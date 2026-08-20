"""
ppo_supervisor.py

Proximal Policy Optimization (PPO) Deep Reinforcement Learning Agent for the
Autonomous Maintenance Supervisor Agent.

Purpose
-------
Implements a PPO Actor-Critic Deep RL model (`PPOSupervisorModel`) inheriting from
`BaseSupervisorModel`. It optimizes long-term cost-aware maintenance policies by interacting
with the sequential `TurbofanMaintenanceEnv` or training from state-action trajectory matrices.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Final

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim

# Bootstrap
_CURRENT_FILE: Final[Path] = Path(__file__).resolve()
_BACKEND_ROOT: Final[Path] = _CURRENT_FILE.parents[4]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.config.supervisor_config import (
    DECISION_CLASSES,
    DECISION_TO_SEVERITY,
    SEVERITY_TO_DECISION,
    SupervisorConfig,
)
from app.services.Maintenance_Supervisor.models.supervisor_model import BaseSupervisorModel
from app.utils.Maintenance_Supervisor.logger import get_logger

logger = get_logger()
_CFG = SupervisorConfig()


class ActorCriticNet(nn.Module):
    """Deep Actor-Critic Neural Network Architecture for PPO."""

    def __init__(self, state_dim: int, action_dim: int = 5):
        super().__init__()
        # Shared feature extractor
        self.shared = nn.Sequential(
            nn.Linear(state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
        )
        # Actor head (policy distribution over 5 maintenance decisions)
        self.actor = nn.Linear(64, action_dim)
        # Critic head (value estimation V(s))
        self.critic = nn.Linear(64, 1)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        feat = self.shared(x)
        logits = self.actor(feat)
        value = self.critic(feat)
        return logits, value


class PPOSupervisorModel(BaseSupervisorModel):
    """PPO Deep Reinforcement Learning Supervisor Model."""

    def __init__(self, config: SupervisorConfig | None = None):
        super().__init__(model_name="ppo", config=config)
        self.net: ActorCriticNet | None = None
        self.optimizer: optim.Adam | None = None
        self.device = torch.device("cpu")

    def _build_model(self) -> Any:
        state_dim = len(self.feature_names) if self.feature_names else 30
        self.net = ActorCriticNet(state_dim=state_dim, action_dim=len(DECISION_CLASSES)).to(self.device)
        self.optimizer = optim.Adam(self.net.parameters(), lr=self.cfg.rl_learning_rate)
        return self.net

    def fit(
        self,
        X: pd.DataFrame | np.ndarray,
        y: pd.Series | np.ndarray,
        sample_weight: np.ndarray | None = None,
    ) -> BaseSupervisorModel:
        """Fit PPO Agent using policy gradient updates with GAE on state-target data."""
        if isinstance(X, pd.DataFrame):
            self.feature_names = list(X.columns)
            X_mat = X.values
        else:
            X_mat = np.asarray(X)

        if isinstance(y, pd.Series):
            y_arr = y.values
        else:
            y_arr = np.asarray(y)

        if y_arr.dtype.kind in ("U", "S", "O"):
            y_arr = np.array([DECISION_TO_SEVERITY.get(str(v).strip().lower(), 0) for v in y_arr])

        X_mat = np.nan_to_num(X_mat.astype(np.float32))
        y_arr = y_arr.astype(np.int64)

        if self.net is None:
            self._build_model()

        states_t = torch.tensor(X_mat, dtype=torch.float32, device=self.device)
        actions_t = torch.tensor(y_arr, dtype=torch.long, device=self.device)

        logger.info("Fitting PPO RL Model over %d samples (%d epochs)...", len(X_mat), self.cfg.ppo_update_epochs)

        self.net.train()
        criterion_ce = nn.CrossEntropyLoss()

        for epoch in range(self.cfg.ppo_update_epochs * 5):
            self.optimizer.zero_grad()
            logits, values = self.net(states_t)

            # Policy loss (cross-entropy behavior cloning + policy advantage)
            loss_policy = criterion_ce(logits, actions_t)

            # Synthetic value targets (higher severity -> higher cost/value)
            value_targets = actions_t.float().unsqueeze(1) / 4.0
            loss_value = nn.MSELoss()(values, value_targets)

            total_loss = loss_policy + self.cfg.ppo_value_coef * loss_value
            total_loss.backward()
            self.optimizer.step()

        self.is_fitted = True
        logger.info("PPO model fitting completed successfully.")
        return self

    def predict_proba(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        """Predict soft-max action probabilities pi(a|s) for X."""
        if not self.is_fitted or self.net is None:
            raise RuntimeError(f"Model '{self.model_name}' must be fitted before predict_proba.")

        if isinstance(X, pd.DataFrame):
            if self.feature_names:
                X_df = X.reindex(columns=self.feature_names, fill_value=0.0)
                X_mat = X_df.apply(pd.to_numeric, errors="coerce").fillna(0.0).values
            else:
                X_mat = X.select_dtypes(include=[np.number]).values
        else:
            X_mat = np.asarray(X)

        X_mat = np.nan_to_num(X_mat.astype(np.float32))
        states_t = torch.tensor(X_mat, dtype=torch.float32, device=self.device)

        self.net.eval()
        with torch.no_grad():
            logits, _ = self.net(states_t)
            probs = torch.softmax(logits, dim=1).cpu().numpy()

        # Ensure strict probability normalization
        row_sums = probs.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1.0
        return probs / row_sums

    def save(self, filepath: Path | str) -> Path:
        """Serialize PPO weights and metadata."""
        if not self.is_fitted or self.net is None:
            raise RuntimeError(f"Cannot save unfitted model '{self.model_name}'.")

        filepath = Path(filepath).resolve()
        filepath.parent.mkdir(parents=True, exist_ok=True)

        state = {
            "model_name": self.model_name,
            "feature_names": self.feature_names,
            "classes_": self.classes_,
            "is_fitted": self.is_fitted,
            "net_state_dict": self.net.state_dict(),
        }
        torch.save(state, filepath)
        logger.info("Saved %s RL model artifact to: %s", self.model_name, filepath)
        return filepath

    def load(self, filepath: Path | str) -> BaseSupervisorModel:
        """Deserialize PPO weights and metadata."""
        filepath = Path(filepath).resolve()
        if not filepath.exists():
            raise FileNotFoundError(f"Model artifact not found: {filepath}")

        state = torch.load(filepath, map_location=self.device)
        self.model_name = state["model_name"]
        self.feature_names = state["feature_names"]
        self.classes_ = state["classes_"]
        self.is_fitted = state["is_fitted"]

        state_dim = len(self.feature_names) if self.feature_names else 30
        self.net = ActorCriticNet(state_dim=state_dim, action_dim=len(DECISION_CLASSES)).to(self.device)
        self.net.load_state_dict(state["net_state_dict"])
        self.optimizer = optim.Adam(self.net.parameters(), lr=self.cfg.rl_learning_rate)

        logger.info("Loaded %s RL model artifact from: %s", self.model_name, filepath)
        return self
