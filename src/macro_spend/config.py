"""Load and validate the project config (``config.yaml``).

The config is the single source of truth for which series are pulled, the
sample window, and caching behaviour. Keeping a thin typed wrapper around the
raw YAML means the rest of the code never reaches into nested dicts by hand.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Series:
    """A single FRED series reference."""

    id: str
    label: str


@dataclass(frozen=True)
class Config:
    """Typed view over ``config.yaml``."""

    date_start: str
    date_end: str | None
    target: Series
    drivers: list[Series]
    cache_dir: Path
    max_cache_age_days: int
    output_dir: Path
    chart_name: str
    # Stage 2/3 blocks are passed through untouched until those stages land.
    model: dict = field(default_factory=dict)
    scenarios: dict = field(default_factory=dict)

    @property
    def all_series(self) -> list[Series]:
        """Target first, then drivers — the full pull list."""
        return [self.target, *self.drivers]


def load_config(path: str | Path = "config.yaml") -> Config:
    """Parse ``config.yaml`` into a :class:`Config`.

    Raises a clear error if required keys are missing rather than failing
    deep inside the fetch with a ``KeyError``.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path.resolve()}")

    raw = yaml.safe_load(path.read_text()) or {}

    for key in ("date_start", "target", "drivers"):
        if key not in raw:
            raise ValueError(f"config.yaml is missing required key: '{key}'")

    target = Series(id=raw["target"]["id"], label=raw["target"]["label"])
    drivers = [Series(id=d["id"], label=d["label"]) for d in raw["drivers"]]

    data_cfg = raw.get("data", {})
    output_cfg = raw.get("output", {})

    return Config(
        date_start=raw["date_start"],
        date_end=raw.get("date_end"),
        target=target,
        drivers=drivers,
        cache_dir=Path(data_cfg.get("cache_dir", "data")),
        max_cache_age_days=int(data_cfg.get("max_cache_age_days", 7)),
        output_dir=Path(output_cfg.get("dir", "outputs")),
        chart_name=output_cfg.get("chart_name", "example_scenarios.png"),
        model=raw.get("model") or {},
        scenarios=raw.get("scenarios") or {},
    )
