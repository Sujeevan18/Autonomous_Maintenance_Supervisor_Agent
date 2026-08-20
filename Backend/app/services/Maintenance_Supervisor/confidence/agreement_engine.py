"""
agreement_engine.py

Multi-Agent Consensus & Conflict Detection Engine for the
Autonomous Maintenance Supervisor Agent.

Purpose
-------
Quantifies agreement and measures decision conflict across independent upstream
components (RUL, Failure Risk, and Anomaly Monitoring).

It calculates:
1. `agreement_score`: Degree of alignment between RUL, Risk, and Anomaly signals in [0.0, 1.0].
2. `conflict_score`: Degree of contradiction across upstream agent outputs.
3. `high_conflict_flag`: Boolean flag indicating severe inter-agent disagreement.
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
_REPORT_PATH: Final[Path] = REPORTS_ROOT / "agreement_engine_report.json"


@dataclass
class AgreementResult:
    agreement_scores: np.ndarray
    conflict_scores: np.ndarray
    high_conflict_flags: np.ndarray
    mean_agreement: float
    mean_conflict: float


class SupervisorAgreementEngine:
    """Computes inter-agent agreement and conflict metrics."""

    def __init__(self, config: SupervisorConfig | None = None):
        self.cfg = config or _CFG

    def compute_agreement(self, df_features: pd.DataFrame) -> AgreementResult:
        rul = df_features.get("predicted_rul", pd.Series(100.0, index=df_features.index)).values
        r30 = df_features.get("risk_30", pd.Series(0.0, index=df_features.index)).values
        anom = df_features.get("anomaly_score", pd.Series(0.0, index=df_features.index)).values

        # Normalize signals to severity range [0.0, 1.0]
        rul_norm = np.clip(1.0 - (rul / 150.0), 0.0, 1.0)
        risk_norm = np.clip(r30, 0.0, 1.0)
        anom_norm = np.clip(anom, 0.0, 1.0)

        # Standard deviation across signals per sample
        stacked = np.column_stack([rul_norm, risk_norm, anom_norm])
        std_devs = np.std(stacked, axis=1)

        # Scale conflict to [0.0, 1.0]
        conflict_scores = np.clip(std_devs * 2.0, 0.0, 1.0)
        agreement_scores = np.clip(1.0 - conflict_scores, 0.0, 1.0)

        high_conflict_flags = conflict_scores >= self.cfg.high_conflict_threshold

        return AgreementResult(
            agreement_scores=agreement_scores,
            conflict_scores=conflict_scores,
            high_conflict_flags=high_conflict_flags,
            mean_agreement=float(np.mean(agreement_scores)),
            mean_conflict=float(np.mean(conflict_scores)),
        )


def run_agreement_engine(input_path: Path | None = None) -> dict:
    input_path = Path(input_path or _TEST_PATH).resolve()

    section("AGREEMENT ENGINE EVALUATION STARTED")
    start_time = time.perf_counter()

    if not input_path.exists():
        from app.config.supervisor_config import SAMPLE_DATASET_PATH
        input_path = SAMPLE_DATASET_PATH

    df = pd.read_csv(input_path, low_memory=False)

    engine = SupervisorAgreementEngine()
    res = engine.compute_agreement(df)
    duration = time.perf_counter() - start_time

    report = {
        "status": "success",
        "input_path": str(input_path),
        "samples_evaluated": len(df),
        "mean_agreement": round(res.mean_agreement, 4),
        "mean_conflict": round(res.mean_conflict, 4),
        "high_conflict_count": int(np.sum(res.high_conflict_flags)),
        "duration_seconds": round(duration, 4),
    }

    _REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_json(report, _REPORT_PATH)

    logger.info("Mean Agreement: %.4f | Mean Conflict: %.4f", res.mean_agreement, res.mean_conflict)
    logger.info("High Conflict Samples: %d", report["high_conflict_count"])
    logger.info("Report written to: %s", _REPORT_PATH)
    section("AGREEMENT ENGINE EVALUATION COMPLETED")
    return report


def main() -> int:
    try:
        res = run_agreement_engine()
        print(json.dumps(res, indent=2))
        return 0
    except Exception as exc:
        logger.error("Error in agreement_engine: %s", exc, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
