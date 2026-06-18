"""Visualization layer — STAGE 4 (not yet implemented).

Produces the single executive-facing comparison chart of the target under each
scenario. Implemented once scenarios exist (Stage 3).
"""

from __future__ import annotations

import pandas as pd


def plot_scenarios(paths: pd.DataFrame, cfg) -> str:  # pragma: no cover
    """Planned Stage-4 entry point: write the comparison chart, return its path."""
    raise NotImplementedError("Charting is Stage 4 — not started.")
