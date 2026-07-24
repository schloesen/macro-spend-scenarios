"""Fetch macro time series from FRED, with a local cache.

Design notes
------------
* The API key is read from the ``FRED_API_KEY`` environment variable. It is
  never written to disk or logged.
* Each series is cached as a CSV under ``cache_dir`` (``data/`` by default).
  A series is re-fetched only if its cache is missing or older than
  ``max_cache_age_days``; otherwise the local copy is used. Pass
  ``force=True`` to bypass the cache.
* We hit the FRED REST endpoint directly with ``requests`` rather than pulling
  in a wrapper library, to keep dependencies minimal and the request explicit.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

import pandas as pd
import requests

from .config import Config, Series

FRED_URL = "https://api.stlouisfed.org/fred/series/observations"
_ENV_KEY = "FRED_API_KEY"


class FredError(RuntimeError):
    """Raised for any problem fetching from FRED."""


def get_api_key() -> str:
    """Return the FRED API key from the environment or raise a clear error."""
    key = os.environ.get(_ENV_KEY)
    if not key:
        raise FredError(
            f"Environment variable {_ENV_KEY} is not set. "
            "Export your FRED API key, e.g.\n"
            f"    export {_ENV_KEY}=your_key_here"
        )
    return key


def _cache_path(cache_dir: Path, series_id: str) -> Path:
    return cache_dir / f"{series_id}.csv"


def _cache_is_fresh(path: Path, max_age_days: int) -> bool:
    if not path.exists():
        return False
    age_seconds = time.time() - path.stat().st_mtime
    return age_seconds <= max_age_days * 86_400


def _parse_observations(payload: dict, series_id: str) -> pd.Series:
    """Turn a FRED observations JSON payload into a float Series indexed by date."""
    obs = payload.get("observations")
    if obs is None:
        raise FredError(f"Unexpected FRED response for {series_id}: {payload}")

    frame = pd.DataFrame(obs)
    if frame.empty:
        raise FredError(f"FRED returned no observations for {series_id}.")

    dates = pd.to_datetime(frame["date"])
    # FRED encodes missing values as ".".
    values = pd.to_numeric(frame["value"], errors="coerce")
    series = pd.Series(values.values, index=dates, name=series_id)
    return series


def fetch_series(
    series: Series,
    cfg: Config,
    *,
    api_key: str | None = None,
    force: bool = False,
) -> pd.Series:
    """Fetch one series, using the cache when fresh.

    Returns a float :class:`pandas.Series` named after the series id and
    indexed by observation date.
    """
    cfg.cache_dir.mkdir(parents=True, exist_ok=True)
    path = _cache_path(cfg.cache_dir, series.id)

    if not force and _cache_is_fresh(path, cfg.max_cache_age_days):
        cached = pd.read_csv(path, index_col=0, parse_dates=True).iloc[:, 0]
        cached.name = series.id
        return cached

    api_key = api_key or get_api_key()
    params = {
        "series_id": series.id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": cfg.date_start,
    }
    if cfg.date_end:
        params["observation_end"] = cfg.date_end

    try:
        resp = requests.get(FRED_URL, params=params, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as exc:  # network / HTTP error
        # Fall back to a stale cache rather than hard-failing the run.
        if path.exists():
            cached = pd.read_csv(path, index_col=0, parse_dates=True).iloc[:, 0]
            cached.name = series.id
            return cached
        raise FredError(f"Failed to fetch {series.id} from FRED: {exc}") from exc

    data = _parse_observations(resp.json(), series.id)
    data.to_csv(path)
    return data


def fetch_all(
    cfg: Config, *, force: bool = False, verbose: bool = True
) -> pd.DataFrame:
    """Fetch the target and all drivers and align them into one DataFrame.

    Each series keeps its native frequency on its own index; they are joined on
    date with an outer join, so monthly series line up and any frequency
    mismatch surfaces as NaNs rather than being silently dropped.
    """
    api_key = get_api_key()  # fail fast once, before any network calls
    columns: dict[str, pd.Series] = {}

    for s in cfg.all_series:
        # Determine the source BEFORE fetching — fetch_series writes the cache,
        # so checking freshness afterwards would always report "cache".
        from_cache = not force and _cache_is_fresh(
            _cache_path(cfg.cache_dir, s.id), cfg.max_cache_age_days
        )
        data = fetch_series(s, cfg, api_key=api_key, force=force)
        columns[s.id] = data
        if verbose:
            n_missing = int(data.isna().sum())
            gap = f"  {n_missing} missing" if n_missing else ""
            print(
                f"  {s.id:<10} {len(data):>5} obs  "
                f"[{data.index.min():%Y-%m} → {data.index.max():%Y-%m}]  "
                f"({'cache' if from_cache else 'FRED'}){gap}"
            )

    frame = pd.concat(columns.values(), axis=1, keys=columns.keys())
    frame = frame.sort_index()
    frame.index.name = "date"
    return frame
