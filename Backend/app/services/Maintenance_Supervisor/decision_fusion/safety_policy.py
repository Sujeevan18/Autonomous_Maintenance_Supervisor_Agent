"""
safety_policy.py

Safety Policy & Hard Risk Guardrails for the
Autonomous Maintenance Supervisor Agent.

Purpose
-------
Enforces non-negotiable safety guardrails and policy overrides on candidate ML model
decisions before final decision emission.

Safety Rules (Fail-Safe Overrides):
-----------------------------------
1. Critical RUL Override: If predicted_rul <= 10.0 -> OVERRIDE to "immediate_maintenance".
2. Critical Risk Override: If risk_10 >= 0.82 -> OVERRIDE to "immediate_maintenance".
3. Critical Anomaly Override: If anomaly_severity == "critical" -> OVERRIDE to "immediate_maintenance".
4. High Risk Override: If risk_30 >= 0.72 -> ENSURE AT LEAST "schedule_maintenance".
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

from app.config.supervisor_config import (
    DECISION_TO_SEVERITY,
    SEVERITY_TO_DECISION,
    SupervisorConfig,
)
from app.utils.Maintenance_Supervisor.logger import get_logger

logger = get_logger()
_CFG = SupervisorConfig()


@dataclass
class PolicyOverrideResult:
    final_decisions: np.ndarray
    override_flags: np.ndarray
    override_reasons: list[str]
    total_overrides: int


class SupervisorSafetyPolicy:
    """Enforces safety guardrails over candidate model decisions."""

    def __init__(self, config: SupervisorConfig | None = None):
        self.cfg = config or _CFG

    def apply_policy_overrides(
        self,
        candidate_decisions: np.ndarray | list[str],
        df_features: pd.DataFrame,
    ) -> PolicyOverrideResult:
        decisions_arr = np.array([str(d).strip().lower() for d in candidate_decisions])
        n_samples = len(decisions_arr)

        rul = df_features.get("predicted_rul", pd.Series(999.0, index=df_features.index)).values
        r10 = df_features.get("risk_10", pd.Series(0.0, index=df_features.index)).values
        r30 = df_features.get("risk_30", pd.Series(0.0, index=df_features.index)).values
        anom_sev = df_features.get("anomaly_severity", pd.Series("none", index=df_features.index)).astype(str).str.lower().values

        final_decisions = decisions_arr.copy()
        override_flags = np.zeros(n_samples, dtype=bool)
        override_reasons = ["None"] * n_samples

        for i in range(n_samples):
            curr_sev = DECISION_TO_SEVERITY.get(final_decisions[i], 0)
            target_sev = curr_sev
            reasons = []

            # Rule 1: Critical RUL
            if rul[i] <= self.cfg.immediate_rul_threshold:
                if target_sev < 4:
                    target_sev = 4
                    reasons.append(f"RUL <= {self.cfg.immediate_rul_threshold}")

            # Rule 2: Critical Risk 10
            if r10[i] >= self.cfg.critical_risk_10_threshold:
                if target_sev < 4:
                    target_sev = 4
                    reasons.append(f"Risk_10 >= {self.cfg.critical_risk_10_threshold}")

            # Rule 3: Critical Anomaly
            if anom_sev[i] == "critical":
                if target_sev < 4:
                    target_sev = 4
                    reasons.append("Critical Anomaly Severity")

            # Rule 4: High Risk 30 -> Schedule Maintenance
            if r30[i] >= self.cfg.maintenance_risk_30_threshold:
                if target_sev < 3:
                    target_sev = 3
                    reasons.append(f"Risk_30 >= {self.cfg.maintenance_risk_30_threshold}")

            if target_sev != curr_sev:
                final_decisions[i] = SEVERITY_TO_DECISION.get(target_sev, "immediate_maintenance")
                override_flags[i] = True
                override_reasons[i] = "; ".join(reasons)

        return PolicyOverrideResult(
            final_decisions=final_decisions,
            override_flags=override_flags,
            override_reasons=override_reasons,
            total_overrides=int(np.sum(override_flags)),
        )
