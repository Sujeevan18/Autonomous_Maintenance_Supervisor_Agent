"""
Supervisor_main.py

Master Entry Point & Production CLI Launcher for the
Autonomous Maintenance Supervisor Agent.

Purpose
-------
Main entry point for running Supervisor Agent commands and end-to-end workflows:
  - sample    : Generate synthetic sample outputs and run validation
  - real      : Integrate real upstream outputs from RUL, Risk, & Anomaly components
  - train     : Run full multi-model training pipeline and baseline benchmarks
  - infer     : Run decision fusion inference pipeline on processed datasets
  - report    : Build research tables and final markdown report
  - service   : Run FastAPI web server

Usage
-----
    "C:\\Python313\\python.exe" -m app.Supervisor_main --mode sample
    "C:\\Python313\\python.exe" -m app.Supervisor_main --mode train
    "C:\\Python313\\python.exe" -m app.Supervisor_main --mode infer
    "C:\\Python313\\python.exe" -m app.Supervisor_main --mode report
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Final

# Bootstrap Backend/ on sys.path
_CURRENT_FILE: Final[Path] = Path(__file__).resolve()
_BACKEND_ROOT: Final[Path] = _CURRENT_FILE.parent
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.utils.Maintenance_Supervisor.logger import get_logger, section

logger = get_logger()


def run_pipeline_mode(mode: str, extra_args: argparse.Namespace) -> int:
    """Dispatch pipeline execution based on requested mode."""
    mode_clean = mode.strip().lower()
    section(f"SUPERVISOR AGENT MASTER LAUNCHER: {mode_clean.upper()}")
    start_time = time.perf_counter()

    if mode_clean == "sample":
        from app.services.Maintenance_Supervisor.pipeline.run_sample_pipeline import run_sample_pipeline
        res = run_sample_pipeline()

    elif mode_clean == "real":
        from app.services.Maintenance_Supervisor.pipeline.run_real_output_pipeline import run_real_output_pipeline
        res = run_real_output_pipeline(
            rul_path=Path(extra_args.rul_path) if getattr(extra_args, "rul_path", None) else None,
            risk_path=Path(extra_args.risk_path) if getattr(extra_args, "risk_path", None) else None,
            anomaly_path=Path(extra_args.anomaly_path) if getattr(extra_args, "anomaly_path", None) else None,
        )

    elif mode_clean == "train":
        from app.services.Maintenance_Supervisor.pipeline.run_training_pipeline import run_training_pipeline
        res = run_training_pipeline()

    elif mode_clean == "infer":
        from app.services.Maintenance_Supervisor.pipeline.run_inference_pipeline import run_inference_pipeline
        input_path = Path(extra_args.input_path) if getattr(extra_args, "input_path", None) else None
        res = run_inference_pipeline(input_path=input_path)

    elif mode_clean == "report":
        from app.services.Maintenance_Supervisor.reporting.research_table_builder import build_research_tables
        from app.services.Maintenance_Supervisor.reporting.final_report_builder import build_final_research_report
        from app.services.Maintenance_Supervisor.reporting.dashboard_output_builder import build_dashboard_export

        t_res = build_research_tables()
        d_res = build_dashboard_export()
        f_res = build_final_research_report()

        res = {
            "status": "success",
            "research_table": t_res,
            "dashboard_export": d_res,
            "final_report": f_res,
        }

    elif mode_clean == "service":
        try:
            import uvicorn
            port = getattr(extra_args, "port", 8000)
            logger.info("Starting FastAPI server on http://0.0.0.0:%d...", port)
            uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
            return 0
        except ImportError:
            logger.error("uvicorn package is not installed. Install with 'pip install uvicorn'.")
            return 1

    else:
        logger.error("Unknown mode '%s'. Supported modes: sample, real, train, infer, report, service.", mode)
        return 1

    duration = time.perf_counter() - start_time
    logger.info("Master execution completed in %.2fs.", duration)
    section(f"SUPERVISOR AGENT MASTER LAUNCHER COMPLETED ({mode_clean.upper()})")
    print(json.dumps(res, indent=2, default=str))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Autonomous Maintenance Supervisor Agent Master CLI Launcher"
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="sample",
        choices=["sample", "real", "train", "infer", "report", "service"],
        help="Execution mode: sample (default), real, train, infer, report, service",
    )
    parser.add_argument("--port", type=int, default=8000, help="Port for FastAPI web server in service mode (default: 8000)")
    parser.add_argument("--rul_path", type=str, default=None, help="Path to RUL component predictions CSV")
    parser.add_argument("--risk_path", type=str, default=None, help="Path to Risk component predictions CSV")
    parser.add_argument("--anomaly_path", type=str, default=None, help="Path to Anomaly component predictions CSV")
    parser.add_argument("--input_path", type=str, default=None, help="Path to input dataset for inference")

    args = parser.parse_args()
    try:
        return run_pipeline_mode(args.mode, args)
    except Exception as exc:
        logger.error("Master CLI error: %s", exc, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())