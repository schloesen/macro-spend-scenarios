"""Tests for the data-loading layer.

These are offline by design: we never call FRED in tests. The HTTP boundary is
monkeypatched so caching, parsing, and alignment logic are exercised
deterministically.
"""

from __future__ import annotations

import json

import pandas as pd
import pytest

from macro_spend import data
from macro_spend.config import Config, Series


@pytest.fixture
def cfg(tmp_path) -> Config:
    return Config(
        date_start="2000-01-01",
        date_end=None,
        target=Series(id="PCE", label="Personal Consumption Expenditures"),
        drivers=[Series(id="UNRATE", label="Unemployment Rate")],
        cache_dir=tmp_path / "data",
        max_cache_age_days=7,
        output_dir=tmp_path / "outputs",
        chart_name="example.png",
    )


def _fake_payload(dates_values):
    return {
        "observations": [
            {"date": d, "value": v} for d, v in dates_values
        ]
    }


def test_get_api_key_missing(monkeypatch):
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    with pytest.raises(data.FredError):
        data.get_api_key()


def test_parse_observations_handles_missing_dots():
    payload = _fake_payload([("2000-01-01", "100.0"), ("2000-02-01", ".")])
    s = data._parse_observations(payload, "PCE")
    assert s.name == "PCE"
    assert s.iloc[0] == 100.0
    assert pd.isna(s.iloc[1])  # "." -> NaN
    assert isinstance(s.index, pd.DatetimeIndex)


def test_parse_observations_empty_raises():
    with pytest.raises(data.FredError):
        data._parse_observations({"observations": []}, "PCE")


def test_fetch_series_writes_and_reads_cache(cfg, monkeypatch):
    calls = {"n": 0}

    class FakeResp:
        def raise_for_status(self):
            pass

        def json(self):
            return _fake_payload([("2000-01-01", "100.0"), ("2000-02-01", "101.0")])

    def fake_get(url, params, timeout):
        calls["n"] += 1
        return FakeResp()

    monkeypatch.setattr(data.requests, "get", fake_get)

    series = cfg.target
    first = data.fetch_series(series, cfg, api_key="dummy")
    assert calls["n"] == 1
    assert (cfg.cache_dir / "PCE.csv").exists()
    assert first.iloc[0] == 100.0

    # Second call should hit the fresh cache, not the network.
    second = data.fetch_series(series, cfg, api_key="dummy")
    assert calls["n"] == 1
    pd.testing.assert_series_equal(first, second)


def test_fetch_series_force_bypasses_cache(cfg, monkeypatch):
    calls = {"n": 0}

    class FakeResp:
        def raise_for_status(self):
            pass

        def json(self):
            return _fake_payload([("2000-01-01", "100.0")])

    def fake_get(url, params, timeout):
        calls["n"] += 1
        return FakeResp()

    monkeypatch.setattr(data.requests, "get", fake_get)
    data.fetch_series(cfg.target, cfg, api_key="dummy")
    data.fetch_series(cfg.target, cfg, api_key="dummy", force=True)
    assert calls["n"] == 2


def test_fetch_all_aligns_series(cfg, monkeypatch):
    payloads = {
        "PCE": _fake_payload([("2000-01-01", "100"), ("2000-02-01", "101")]),
        "UNRATE": _fake_payload([("2000-01-01", "4.0"), ("2000-02-01", "4.1")]),
    }

    class FakeResp:
        def __init__(self, sid):
            self._sid = sid

        def raise_for_status(self):
            pass

        def json(self):
            return payloads[self._sid]

    def fake_get(url, params, timeout):
        return FakeResp(params["series_id"])

    monkeypatch.setenv("FRED_API_KEY", "dummy")
    monkeypatch.setattr(data.requests, "get", fake_get)

    frame = data.fetch_all(cfg, verbose=False)
    assert list(frame.columns) == ["PCE", "UNRATE"]
    assert frame.shape == (2, 2)
    assert frame.index.name == "date"
    assert frame.loc["2000-01-01", "PCE"] == 100.0
