"""
run_training_pipeline.py

Master Supervisor Model Training & Baseline Benchmarking Pipeline Orchestrator.

Purpose
-------
Runs data preprocessing, dataset splitting, multi-model training, baseline benchmarking,
and champion model selection in a single automated workflow.
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

from app.config.supervisor_config import REPORTS_ROOT
from app.services.Maintenance_Supervisor.training.train_supervisor import run_master_training_pipeline
from app.services.Maintenance_Supervisor.evaluation.compare_baselines import run_baseline_comparison
from app.utils.Maintenance_Supervisor.logger import get_logger, section
from app.utils.Maintenance_Supervisor.atomic_writer import atomic_write_json

logger = get_logger()
_REPORT_PATH: Final[Path] = REPORTS_ROOT / "run_training_pipeline_report.json"


def run_training_pipeline() -> dict:
    section("MASTER TRAINING PIPELINE ORCHESTRATOR STARTED")
    start_time = time.perf_counter()

    train_res = run_master_training_pipeline()
    baseline_res = run_baseline_comparison()

    duration = time.perf_counter() - start_time

    report = {
        "status": "success",
        "training_pipeline": train_res,
        "baseline_comparison": baseline_res,
        "duration_seconds": round(duration, 4),
    }

    _REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_json(report, _REPORT_PATH)

    logger.info("Training pipeline orchestrator completed in %.2fs.", duration)
    logger.info("Report written to: %s", _REPORT_PATH)
    section("MASTER TRAINING PIPELINE ORCHESTRATOR COMPLETED")

    return report


def main() -> int:
    try:
        res = run_training_pipeline()
        print(json.dumps(res, indent=2))
        return 0
    except Exception as exc:
        logger.error("Error in run_training_pipeline: %s", exc, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
