"""
rl_environment.py

Sequential Markov Decision Process (MDP) Maintenance Environment for the
Autonomous Maintenance Supervisor Agent.

Purpose
-------
Provides a gym-compatible sequential environment (`TurbofanMaintenanceEnv`) that simulates
engine degradation trajectories based on multivariate sensor outputs, multi-horizon failure
risks, RUL estimates, and anomaly scores.

Key Components
--------------
1. State Space: Unified machine health state vector (features derived from RUL, Risk, & Anomaly agents).
2. Action Space: Discrete(5)
    0: continue_operation
    1: monitor_closely
    2: schedule_inspection
    3: schedule_maintenance
    4: immediate_maintenance
3. Reward Function: Multi-objective cost-aware trade-off function balancing downtime, maintenance costs,
   and catastrophic failure prevention.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Final

import numpy as np
import pandas as pd

# Bootstrap
_CURRENT_FILE: Final[Path] = Path(__file__).resolve()
_BACKEND_ROOT: Final[Path] = _CURRENT_FILE.parents[4]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.config.supervisor_config import (
    DECISION_CLASSES,
    SupervisorConfig,
)
from app.utils.Maintenance_Supervisor.logger import get_logger

logger = get_logger()
_CFG = SupervisorConfig()


class TurbofanMaintenanceEnv:
    """
    Sequential MDP Environment simulating industrial engine degradation cycles
    for reinforcement learning policy optimization.
    """

    def __init__(
        self,
        df_episodes: pd.DataFrame,
        feature_columns: list[str] | None = None,
        config: SupervisorConfig | None = None,
    ):
        self.cfg = config or _CFG
        self.df_raw = df_episodes.copy()

        # Group dataset by engine trajectory
        self.engine_col = self.cfg.engine_id_column if self.cfg.engine_id_column in df_episodes.columns else "engine_id"
        self.cycle_col = self.cfg.cycle_column if self.cfg.cycle_column in df_episodes.columns else "cycle"

        if self.engine_col not in self.df_raw.columns:
            self.df_raw[self.engine_col] = 1

        self.engine_ids = sorted(self.df_raw[self.engine_col].unique())
        self.episodes: dict[Any, pd.DataFrame] = {
            eng_id: group.sort_values(self.cycle_col).reset_index(drop=True)
            for eng_id, group in self.df_raw.groupby(self.engine_col)
        }

        # Determine state feature columns
        if feature_columns:
            self.feature_cols = [c for c in feature_columns if c in self.df_raw.columns]
        else:
            self.feature_cols = [
                c for c in self.cfg.all_model_features if c in self.df_raw.columns
            ]
            if not self.feature_cols:
                self.feature_cols = list(self.df_raw.select_dtypes(include=[np.number]).columns)

        self.state_dim = len(self.feature_cols)
        self.action_dim = len(DECISION_CLASSES)  # 5 actions

        self.current_engine_idx = 0
        self.current_step = 0
        self.current_trajectory: pd.DataFrame | None = None
        self.max_steps = 0

    def reset(self, engine_id: Any | None = None) -> np.ndarray:
        """Reset environment to the beginning of a trajectory."""
        if engine_id is not None and engine_id in self.episodes:
            self.current_trajectory = self.episodes[engine_id]
        else:
            eng_id = np.random.choice(self.engine_ids)
            self.current_trajectory = self.episodes[eng_id]

        self.current_step = 0
        self.max_steps = len(self.current_trajectory)
        return self._get_state()

    def _get_state(self) -> np.ndarray:
        """Extract state feature vector for the current step."""
        if self.current_trajectory is None or self.current_step >= self.max_steps:
            return np.zeros(self.state_dim, dtype=np.float32)

        row = self.current_trajectory.iloc[self.current_step]
        state = row[self.feature_cols].apply(pd.to_numeric, errors="coerce").fillna(0.0).values
        return state.astype(np.float32)

    def step(self, action: int) -> tuple[np.ndarray, float, bool, dict]:
        """
        Execute maintenance action step.

        Actions
        -------
        0: continue_operation
        1: monitor_closely
        2: schedule_inspection
        3: schedule_maintenance
        4: immediate_maintenance
        """
        if self.current_trajectory is None or self.current_step >= self.max_steps:
            return np.zeros(self.state_dim, dtype=np.float32), 0.0, True, {}

        row = self.current_trajectory.iloc[self.current_step]
        predicted_rul = float(row.get("predicted_rul", row.get("RUL", self.max_steps - self.current_step)))
        risk_10 = float(row.get("risk_10", row.get("failure_risk", 0.0)))
        anomaly_score = float(row.get("anomaly_score", 0.0))

        reward = 0.0
        done = False
        info = {
            "action_name": DECISION_CLASSES[action],
            "step": self.current_step,
            "predicted_rul": predicted_rul,
            "risk_10": risk_10,
        }

        # ---------------------------------------------------------------------
        # Action Dynamics & Multi-Objective Reward Calculation
        # ---------------------------------------------------------------------

        if action == 0:  # continue_operation
            reward -= self.cfg.cost_continue_operation
            if predicted_rul <= 1.0 or self.current_step >= self.max_steps - 1:
                reward -= self.cfg.cost_unplanned_failure
                done = True
                info["event"] = "unplanned_catastrophic_failure"
            elif risk_10 > 0.85:
                reward -= 500.0

        elif action == 1:  # monitor_closely
            reward -= self.cfg.cost_monitoring
            if predicted_rul <= 1.0 or self.current_step >= self.max_steps - 1:
                reward -= self.cfg.cost_unplanned_failure
                done = True
                info["event"] = "unplanned_failure_during_monitoring"

        elif action == 2:  # schedule_inspection
            reward -= self.cfg.cost_inspection
            if predicted_rul <= 1.0 or self.current_step >= self.max_steps - 1:
                reward -= self.cfg.cost_unplanned_failure
                done = True
                info["event"] = "unplanned_failure_during_inspection"

        elif action == 3:  # schedule_maintenance
            reward -= self.cfg.cost_scheduled_maintenance
            done = True
            info["event"] = "successful_scheduled_maintenance"
            if predicted_rul > 60.0:
                reward -= (predicted_rul - 60.0) * 10.0
            else:
                reward += 200.0

        elif action == 4:  # immediate_maintenance
            reward -= self.cfg.cost_immediate_maintenance
            done = True
            info["event"] = "emergency_shutdown_executed"
            if predicted_rul < 15.0 or risk_10 > 0.70:
                reward += 300.0
            else:
                reward -= 400.0

        self.current_step += 1
        if self.current_step >= self.max_steps:
            done = True

        next_state = self._get_state()
        return next_state, float(reward), done, info
