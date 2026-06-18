"""Scenario layer — STAGE 3 (not yet implemented).

Projects the target under base / upside / downside driver assumptions defined
in ``config.yaml``. Left unimplemented until the model exists, because the form
of a scenario (level path vs. shock to a differenced/transformed driver)
depends on the Stage-2 modeling choice.
"""

from __future__ import annotations

import pandas as pd


def project(model: object, cfg) -> pd.DataFrame:  # pragma: no cover
    """Planned Stage-3 entry point: return target paths per scenario."""
    raise NotImplementedError("Scenario projection is Stage 3 — not started.")
