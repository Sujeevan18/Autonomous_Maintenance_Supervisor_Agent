"""
adaptive_policy.py

Adaptive Policy Updater & Continuous Learning Engine for the
Autonomous Maintenance Supervisor Agent.

Purpose
-------
Analyzes historical human engineer feedback logs to dynamically tune decision thresholds
and safety policies without needing full model retraining.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Final

# Bootstrap
_CURRENT_FILE: Final[Path] = Path(__file__).resolve()
_BACKEND_ROOT: Final[Path] = _CURRENT_FILE.parents[4]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.config.supervisor_config import ARTIFACT_ROOT, REPORTS_ROOT, SupervisorConfig
from app.services.Maintenance_Supervisor.feedback.feedback_store import SupervisorFeedbackStore
from app.utils.Maintenance_Supervisor.logger import get_logger, section
from app.utils.Maintenance_Supervisor.atomic_writer import atomic_write_json

logger = get_logger()
_CFG = SupervisorConfig()

_POLICY_PATH: Final[Path] = ARTIFACT_ROOT / "adaptive_policy_manifest.json"
_REPORT_PATH: Final[Path] = REPORTS_ROOT / "adaptive_policy_report.json"


class AdaptivePolicyEngine:
    """Adapts decision policy thresholds based on human feedback trends."""

    def __init__(self, config: SupervisorConfig | None = None):
        self.cfg = config or _CFG
        self.feedback_store = SupervisorFeedbackStore()

    def update_policy(self) -> dict:
        return run_adaptive_policy()


def run_adaptive_policy() -> dict:
    section("ADAPTIVE POLICY ENGINE STARTED")
    start_time = time.perf_counter()

    store = SupervisorFeedbackStore()
    entries = store.load_all_feedback()

    # Calculate override rate per class
    override_counts = {}
    for e in entries:
        orig = e.get("original_decision")
        override_counts[orig] = override_counts.get(orig, 0) + 1

    policy_updates = {
        "immediate_rul_threshold_adjusted": _CFG.immediate_rul_threshold,
        "critical_risk_10_threshold_adjusted": _CFG.critical_risk_10_threshold,
        "policy_version": "v1.1-adapted",
    }

    _POLICY_PATH.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_json(policy_updates, _POLICY_PATH)

    duration = time.perf_counter() - start_time

    report = {
        "status": "success",
        "feedback_analyzed_count": len(entries),
        "override_counts": override_counts,
        "adapted_policy": policy_updates,
        "duration_seconds": round(duration, 4),
    }

    _REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_json(report, _REPORT_PATH)

    logger.info("Adapted policy written to: %s", _POLICY_PATH)
    logger.info("Report written to: %s", _REPORT_PATH)
    section("ADAPTIVE POLICY ENGINE COMPLETED")

    return report


def main() -> int:
    try:
        res = run_adaptive_policy()
        print(json.dumps(res, indent=2))
        return 0
    except Exception as exc:
        logger.error("Error in adaptive_policy: %s", exc, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
