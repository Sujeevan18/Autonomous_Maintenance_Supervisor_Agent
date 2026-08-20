"""
decision_fusion_engine.py

Master Decision Fusion & Policy Enforcement Engine for the
Autonomous Maintenance Supervisor Agent.

Purpose
-------
Integrates the champion ML model predictions, safety policy guardrails, confidence &
uncertainty estimators, and action/priority mappers into a single, unified decision
fusion pipeline.

Output Structure per Sample:
----------------------------
- `final_decision`: Final safety-checked maintenance decision class
- `priority`: Operational priority ("Low", "Medium", "High", "Critical")
- `maintenance_urgency`: Time horizon recommendation
- `recommended_action`: Human-readable engineering directive
- `confidence_score`: Multi-factor confidence in [0.0, 1.0]
- `confidence_level`: "low", "medium", or "high"
- `entropy_score`: Normalized prediction uncertainty
- `conflict_score`: Inter-agent disagreement score
- `requires_human_review`: Mandatory human review boolean flag
- `override_applied`: Boolean indicating if safety policy overrode ML prediction

Execution
---------
Run from the Backend/ directory:

    "C:\\Python313\\python.exe" -m app.services.Maintenance_Supervisor.decision_fusion.decision_fusion_engine

Expected outputs
----------------
- reports/Maintenance_Supervisor/decision_fusion_report.json
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

from app.config.supervisor_config import REPORTS_ROOT, PROCESSED_ROOT, ARTIFACT_ROOT, SupervisorConfig
from app.services.Maintenance_Supervisor.models.model_registry import load_model
from app.services.Maintenance_Supervisor.decision_fusion.safety_policy import SupervisorSafetyPolicy
from app.services.Maintenance_Supervisor.decision_fusion.urgency_mapper import map_priorities_and_urgencies
from app.services.Maintenance_Supervisor.decision_fusion.action_mapper import map_action_recommendations
from app.services.Maintenance_Supervisor.confidence.confidence_engine import SupervisorConfidenceEngine
from app.services.Maintenance_Supervisor.confidence.uncertainty_engine import SupervisorUncertaintyEngine
from app.services.Maintenance_Supervisor.confidence.agreement_engine import SupervisorAgreementEngine
from app.services.Maintenance_Supervisor.confidence.human_review_engine import HumanReviewEngine
from app.utils.Maintenance_Supervisor.logger import get_logger, section
from app.utils.Maintenance_Supervisor.atomic_writer import atomic_write_json

logger = get_logger()
_CFG = SupervisorConfig()

_TEST_PATH: Final[Path] = PROCESSED_ROOT / "splits" / "test.csv"
_CHAMPION_MANIFEST: Final[Path] = ARTIFACT_ROOT / "champion_model_manifest.json"
_REPORT_PATH: Final[Path] = REPORTS_ROOT / "decision_fusion_report.json"


class DecisionFusionEngine:
    """Master Multi-Agent Decision Fusion Engine."""

    def __init__(self, model_path: Path | str | None = None, config: SupervisorConfig | None = None):
        self.cfg = config or _CFG
        self.safety_policy = SupervisorSafetyPolicy(self.cfg)
        self.confidence_engine = SupervisorConfidenceEngine(self.cfg)
        self.uncertainty_engine = SupervisorUncertaintyEngine(self.cfg)
        self.agreement_engine = SupervisorAgreementEngine(self.cfg)
        self.human_review_engine = HumanReviewEngine(self.cfg)

        if model_path is None and _CHAMPION_MANIFEST.exists():
            with open(_CHAMPION_MANIFEST, "r", encoding="utf-8") as f:
                champ_data = json.load(f)
                model_path = champ_data.get("champion_model_path")

        if model_path and Path(model_path).exists():
            self.model = load_model(model_path)
        else:
            self.model = None
            logger.warning("No champion model found for decision fusion engine. Using fallback logic.")

    def fuse_decisions(self, df_features: pd.DataFrame) -> pd.DataFrame:
        """Run end-to-end decision fusion across features."""
        # 1. Candidate ML Predictions
        if self.model and self.model.is_fitted:
            # Use selected features if model has them
            feature_cols = self.model.feature_names if self.model.feature_names else df_features.select_dtypes(include=[np.number]).columns
            # Ensure all required model features exist in input dataframe and are numeric
            X_df = df_features.reindex(columns=feature_cols, fill_value=0.0)
            X_mat = X_df.apply(pd.to_numeric, errors="coerce").fillna(0.0)
            raw_preds = self.model.predict(X_mat)
            probs = self.model.predict_proba(X_mat)
        else:
            # Rule-based fallback if ML model is unavailable
            from app.services.Maintenance_Supervisor.baselines.rule_based_supervisor import RuleBasedSupervisorModel
            rb_model = RuleBasedSupervisorModel(self.cfg)
            raw_preds = rb_model.predict(df_features).values
            probs = np.full((len(df_features), len(self.cfg.decision_classes)), 1.0 / len(self.cfg.decision_classes))

        # 2. Safety Policy Overrides
        policy_res = self.safety_policy.apply_policy_overrides(raw_preds, df_features)

        # 3. Confidence & Uncertainty Metrics
        conf_res = self.confidence_engine.compute_confidence(probs, df_features)
        unc_res = self.uncertainty_engine.compute_uncertainty(probs)
        agree_res = self.agreement_engine.compute_agreement(df_features)

        # 4. Human Review Flagging
        review_res = self.human_review_engine.evaluate_human_review(
            policy_res.final_decisions,
            conf_res.confidence_scores,
            unc_res.entropy_scores,
            agree_res.conflict_scores,
            df_features,
        )

        # 5. Operational Priority, Urgency & Action Directives
        priorities, urgencies = map_priorities_and_urgencies(policy_res.final_decisions)
        actions = map_action_recommendations(policy_res.final_decisions)

        # Build fused result DataFrame
        fused_df = df_features.copy()
        fused_df["raw_model_decision"] = raw_preds
        fused_df["final_decision"] = policy_res.final_decisions
        fused_df["override_applied"] = policy_res.override_flags
        fused_df["override_reason"] = policy_res.override_reasons
        fused_df["priority"] = priorities
        fused_df["maintenance_urgency"] = urgencies
        fused_df["recommended_action"] = actions
        fused_df["confidence_score"] = conf_res.confidence_scores
        fused_df["confidence_level"] = conf_res.confidence_levels
        fused_df["entropy_score"] = unc_res.entropy_scores
        fused_df["conflict_score"] = agree_res.conflict_scores
        fused_df["requires_human_review"] = review_res.requires_review_flags
        fused_df["review_reason"] = review_res.review_reasons

        return fused_df


def run_decision_fusion(input_path: Path | None = None) -> dict:
    input_path = Path(input_path or _TEST_PATH).resolve()

    section("DECISION FUSION ENGINE STARTED")
    start_time = time.perf_counter()

    if not input_path.exists():
        from app.config.supervisor_config import SAMPLE_DATASET_PATH
        input_path = SAMPLE_DATASET_PATH

    df = pd.read_csv(input_path, low_memory=False)

    engine = DecisionFusionEngine()
    fused_df = engine.fuse_decisions(df)

    duration = time.perf_counter() - start_time

    overrides = int(fused_df["override_applied"].sum())
    reviews = int(fused_df["requires_human_review"].sum())
    mean_conf = float(fused_df["confidence_score"].mean())

    report = {
        "status": "success",
        "input_path": str(input_path),
        "total_samples": len(fused_df),
        "overrides_applied": overrides,
        "human_reviews_required": reviews,
        "mean_confidence": round(mean_conf, 4),
        "decisions_distribution": fused_df["final_decision"].value_counts().to_dict(),
        "duration_seconds": round(duration, 4),
    }

    _REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_json(report, _REPORT_PATH)

    logger.info("Fused Decisions: %s", report["decisions_distribution"])
    logger.info("Overrides Applied: %d | Reviews Required: %d", overrides, reviews)
    logger.info("Report written to: %s", _REPORT_PATH)
    section("DECISION FUSION ENGINE COMPLETED")

    return report


def main() -> int:
    try:
        res = run_decision_fusion()
        print(json.dumps(res, indent=2))
        return 0
    except Exception as exc:
        logger.error("Error in decision_fusion_engine: %s", exc, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
