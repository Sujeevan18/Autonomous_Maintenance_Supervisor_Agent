"""
supervisor_explainer.py

Unified Explainability & Reasoning Engine for the
Autonomous Maintenance Supervisor Agent.

Purpose
-------
Orchestrates multi-level decision explainability combining:
1. Feature attribution (SHAP values or feature importance).
2. Rule-based natural language template narratives.
3. Upstream contributor breakdown (RUL vs Risk vs Anomaly contribution percentages).

Execution
---------
Run from the Backend/ directory:

    "C:\\Python313\\python.exe" -m app.services.Maintenance_Supervisor.explanation.supervisor_explainer

Expected outputs
----------------
- reports/Maintenance_Supervisor/supervisor_explainer_report.json
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

from app.config.supervisor_config import REPORTS_ROOT, PROCESSED_ROOT
from app.services.Maintenance_Supervisor.explanation.template_explainer import generate_decision_narrative
from app.services.Maintenance_Supervisor.explanation.shap_explainer import compute_feature_attributions
from app.utils.Maintenance_Supervisor.logger import get_logger, section
from app.utils.Maintenance_Supervisor.atomic_writer import atomic_write_json

logger = get_logger()

_TEST_PATH: Final[Path] = PROCESSED_ROOT / "splits" / "test.csv"
_REPORT_PATH: Final[Path] = REPORTS_ROOT / "supervisor_explainer_report.json"


@dataclass
class ExplanationResult:
    sample_id: int
    decision: str
    explanation_narrative: str
    top_feature_attributions: dict[str, float]
    upstream_contributions: dict[str, float]


class SupervisorExplainer:
    """Master Decision Explainer."""

    def explain_sample(self, row: pd.Series, decision: str) -> ExplanationResult:
        narrative = generate_decision_narrative(row, decision)
        attributions = compute_feature_attributions(row)

        # Estimate upstream contributor share
        rul_val = float(row.get("predicted_rul", 100.0))
        risk_val = float(row.get("risk_30", 0.0))
        anom_val = float(row.get("anomaly_score", 0.0))

        s_rul = max(0.0, 1.0 - (rul_val / 150.0))
        s_risk = risk_val
        s_anom = anom_val
        total_s = s_rul + s_risk + s_anom + 1e-6

        upstream = {
            "rul_contribution_pct": round(100.0 * s_rul / total_s, 2),
            "risk_contribution_pct": round(100.0 * s_risk / total_s, 2),
            "anomaly_contribution_pct": round(100.0 * s_anom / total_s, 2),
        }

        return ExplanationResult(
            sample_id=int(row.get("cycle", 0)),
            decision=decision,
            explanation_narrative=narrative,
            top_feature_attributions=attributions,
            upstream_contributions=upstream,
        )


def run_supervisor_explainer(input_path: Path | None = None) -> dict:
    input_path = Path(input_path or _TEST_PATH).resolve()

    section("SUPERVISOR EXPLAINABILITY ENGINE STARTED")
    start_time = time.perf_counter()

    if not input_path.exists():
        from app.config.supervisor_config import SAMPLE_DATASET_PATH
        input_path = SAMPLE_DATASET_PATH

    df = pd.read_csv(input_path, low_memory=False)
    explainer = SupervisorExplainer()

    sample_explanations = []
    for idx in range(min(5, len(df))):
        row = df.iloc[idx]
        res = explainer.explain_sample(row, decision=str(row.get("final_decision", "immediate_maintenance")))
        sample_explanations.append({
            "sample_index": idx,
            "decision": res.decision,
            "narrative": res.explanation_narrative,
            "upstream_contributions": res.upstream_contributions,
            "top_attributions": res.top_feature_attributions,
        })

    duration = time.perf_counter() - start_time

    report = {
        "status": "success",
        "input_path": str(input_path),
        "sample_explanations": sample_explanations,
        "duration_seconds": round(duration, 4),
    }

    _REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_json(report, _REPORT_PATH)

    logger.info("Generated explanations for sample rows.")
    logger.info("Report written to: %s", _REPORT_PATH)
    section("SUPERVISOR EXPLAINABILITY ENGINE COMPLETED")

    return report


def main() -> int:
    try:
        res = run_supervisor_explainer()
        print(json.dumps(res, indent=2))
        return 0
    except Exception as exc:
        logger.error("Error in supervisor_explainer: %s", exc, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
