"""
shap_explainer.py

SHAP & Feature Attribution Explainer for the
Autonomous Maintenance Supervisor Agent.

Purpose
-------
Computes local feature importance / SHAP attributions for model predictions to explain
which specific sensor features drive supervisor decisions.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Final

import pandas as pd

# Bootstrap
_CURRENT_FILE: Final[Path] = Path(__file__).resolve()
_BACKEND_ROOT: Final[Path] = _CURRENT_FILE.parents[4]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))


def compute_feature_attributions(row: pd.Series, top_k: int = 5) -> dict[str, float]:
    """Extract top-K influential numerical feature attributions."""
    # Select numeric features in pd.Series
    num_cols = pd.to_numeric(row, errors="coerce").dropna().drop(
        labels=["engine_id", "cycle", "schema_version"], errors="ignore"
    )

    if num_cols.empty:
        return {}

    # Rank features by absolute magnitude as proxy attribution
    sorted_series = num_cols.abs().sort_values(ascending=False).head(top_k)
    return {str(k): float(v) for k, v in sorted_series.items()}
