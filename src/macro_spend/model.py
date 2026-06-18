"""Modeling layer — STAGE 2 (not yet implemented).

Per the project guardrails, the modeling approach is owned by the user:
transformations, stationarity handling, and feature selection are decisions to
be proposed-with-trade-offs and approved, not chosen silently here.

This module currently only exposes the stationarity diagnostics that Stage 2
will build on, so we can *report* before we *fit*. The regression itself is
intentionally left unimplemented until the approach is agreed.
"""

from __future__ import annotations

import pandas as pd


def stationarity_report(frame: pd.DataFrame) -> pd.DataFrame:  # pragma: no cover
    """Planned Stage-2 entry point: ADF/KPSS tests per series.

    Returns a tidy table (series, test statistic, p-value, verdict) so we can
    decide differencing/transformations before any regression. Not yet wired
    up — placeholder to keep the module boundary explicit.
    """
    raise NotImplementedError(
        "Stationarity testing is Stage 2 — pending the modeling-approach decision."
    )


def fit(frame: pd.DataFrame, cfg) -> object:  # pragma: no cover
    """Planned Stage-2 entry point: fit the interpretable spend model."""
    raise NotImplementedError("Modeling is Stage 2 — not started.")
