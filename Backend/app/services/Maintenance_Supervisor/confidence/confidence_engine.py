"""
confidence_engine.py

Decision Confidence Calculation Engine for the
Autonomous Maintenance Supervisor Agent.

Purpose
-------
Calculates a multi-factor decision confidence score in [0.0, 1.0] for every supervisor
prediction by combining:
1. Model predicted probability margin (max predicted class probability).
2. Upstream prediction quality metrics (RUL uncertainty width, risk confidence, anomaly context confidence).
3. Data quality / drift penalties.

Execution
---------
Run from the Backend/ directory:

    "C:\\Python313\\python.exe" -m app.services.Maintenance_Supervisor.confidence.confidence_engine

Expected outputs
----------------
- reports/Maintenance_Supervisor/confidence_engine_report.json
"""

from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import numpy as np
import pandas as pd

# Bootstrap
_CURRENT_FILE: Final[Path] = Path(__file__).resolve()
_BACKEND_ROOT: Final[Path] = _CURRENT_FILE.parents[4]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.config.supervisor_config import REPORTS_ROOT, PROCESSED_ROOT, SupervisorConfig
from app.utils.Maintenance_Supervisor.logger import get_logger, section
from app.utils.Maintenance_Supervisor.atomic_writer import atomic_write_json

logger = get_logger()
_CFG = SupervisorConfig()

_TEST_PATH: Final[Path] = PROCESSED_ROOT / "splits" / "test.csv"
_REPORT_PATH: Final[Path] = REPORTS_ROOT / "confidence_engine_report.json"


@dataclass
class ConfidenceResult:
    confidence_scores: np.ndarray
    confidence_levels: list[str]  # "low", "medium", "high"
    mean_confidence: float


class SupervisorConfidenceEngine:
    """Calculates decision confidence scores for maintenance decisions."""

    def __init__(self, config: SupervisorConfig | None = None):
        self.cfg = config or _CFG

    def compute_confidence(
        self,
        predicted_probs: np.ndarray,
        df_features: pd.DataFrame,
    ) -> ConfidenceResult:
        # 1. Model certainty (highest class probability)
        max_probs = np.max(predicted_probs, axis=1)

        # 2. Upstream signal quality penalty
        u_width = df_features.get("uncertainty_width", pd.Series(0.0, index=df_features.index)).values
        c_conf = df_features.get("context_confidence", pd.Series(1.0, index=df_features.index)).values
        collapse_flag = df_features.get("confidence_collapse_flag", pd.Series(False, index=df_features.index)).values

        # Penalty calculation
        u_penalty = np.clip(u_width / 50.0, 0.0, 0.3)
        drift_penalty = (1.0 - c_conf) * 0.2
        collapse_penalty = collapse_flag.astype(float) * 0.25

        confidence_scores = np.clip(max_probs - u_penalty - drift_penalty - collapse_penalty, 0.0, 1.0)

        # Categorize confidence level
        confidence_levels = [
            "high" if c >= self.cfg.high_confidence_threshold
            else "medium" if c >= self.cfg.medium_confidence_threshold
            else "low"
            for c in confidence_scores
        ]

        return ConfidenceResult(
            confidence_scores=confidence_scores,
            confidence_levels=confidence_levels,
            mean_confidence=float(np.mean(confidence_scores)),
        )


def run_confidence_engine(input_path: Path | None = None) -> dict:
    input_path = Path(input_path or _TEST_PATH).resolve()

    section("CONFIDENCE ENGINE EVALUATION STARTED")
    start_time = time.perf_counter()

    if not input_path.exists():
        from app.config.supervisor_config import SAMPLE_DATASET_PATH
        input_path = SAMPLE_DATASET_PATH

    df = pd.read_csv(input_path, low_memory=False)

    # Dummy/Uniform probabilities for testing engine standalone
    dummy_probs = np.full((len(df), len(self_classes := _CFG.decision_classes)), 1.0 / len(self_classes))
    dummy_probs[:, 0] = 0.85  # Simulate high model certainty on class 0

    engine = SupervisorConfidenceEngine()
    res = engine.compute_confidence(dummy_probs, df)
    duration = time.perf_counter() - start_time

    report = {
        "status": "success",
        "input_path": str(input_path),
        "samples_evaluated": len(df),
        "mean_confidence": round(res.mean_confidence, 4),
        "high_confidence_count": sum(1 for c in res.confidence_levels if c == "high"),
        "medium_confidence_count": sum(1 for c in res.confidence_levels if c == "medium"),
        "low_confidence_count": sum(1 for c in res.confidence_levels if c == "low"),
        "duration_seconds": round(duration, 4),
    }

    _REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_json(report, _REPORT_PATH)

    logger.info("Mean Confidence: %.4f", res.mean_confidence)
    logger.info("Report written to: %s", _REPORT_PATH)
    section("CONFIDENCE ENGINE EVALUATION COMPLETED")
    return report


def main() -> int:
    try:
        res = run_confidence_engine()
        print(json.dumps(res, indent=2))
        return 0
    except Exception as exc:
        logger.error("Error in confidence_engine: %s", exc, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
