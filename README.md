# Macro-Driven Spend Scenario Tool

An interpretable, config-driven tool that models how U.S. consumer spending
responds to macroeconomic drivers and projects it under **base / upside /
downside** scenarios. Built as an FP&A-style scenario & sensitivity analysis —
optimized for a clear, defensible, executive-facing story rather than ML
sophistication.

> **Status:** Stage 1 of 4 complete (repo scaffold + FRED data fetch).
> Modeling, scenarios, and the chart are built in later stages.

## What it does (target end state)

1. Pulls macro time series from [FRED](https://fred.stlouisfed.org/).
2. Fits an interpretable model linking consumer spend to its drivers
   (stationarity-tested first).
3. Projects the target under three user-defined scenarios.
4. Outputs one clean comparison chart plus a short written takeaway.

## Data (FRED)

| Role   | Series     | Description                          |
|--------|------------|--------------------------------------|
| Target | `PCE`      | Personal Consumption Expenditures (real alt: `PCEC96`) |
| Driver | `CPIAUCSL` | CPI — inflation                      |
| Driver | `FEDFUNDS` | Effective federal funds rate         |
| Driver | `UNRATE`   | Unemployment rate                    |
| Driver | `DSPI`     | Disposable personal income           |

All series, the sample window, and (later) scenario assumptions are set in
[`config.yaml`](config.yaml) — the whole pipeline re-runs from there with no
code edits.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .          # or: pip install -r requirements.txt

# FRED API key — required, read from the environment, never hardcoded:
export FRED_API_KEY=your_key_here
```

Get a free key at <https://fred.stlouisfed.org/docs/api/api_key.html>.

## Usage

```bash
# Stage 1 — pull + cache the target and drivers
python -m macro_spend fetch

# ignore the local cache and re-pull everything
python -m macro_spend fetch --force
```

Series are cached as CSVs under `data/` and re-used until they are older than
`max_cache_age_days` (default 7), so repeated runs don't re-hit the API. Cached
data is **not** committed to git.

Later stages add `model`, `scenarios`, `chart`, and `run` subcommands (stubbed
today so the full CLI surface is visible).

## Project structure

```
config.yaml                 # single source of truth (series, window, caching)
src/macro_spend/
  config.py                 # typed loader for config.yaml
  data.py                   # FRED fetch + local caching        (Stage 1 ✓)
  model.py                  # interpretable model + stationarity (Stage 2)
  scenarios.py              # base/upside/downside projection     (Stage 3)
  viz.py                    # the one comparison chart            (Stage 4)
  __main__.py               # CLI entry point
tests/test_data.py          # offline tests for the data layer
data/                       # cached FRED pulls (gitignored)
outputs/                    # one committed example chart (later)
```

## Testing

```bash
pytest        # data-layer tests run fully offline (FRED is mocked)
```

## Analytical guardrails

This project deliberately separates engineering from analytical judgment:

- **Modeling decisions are reviewed, not silently chosen.** Transformations,
  feature set, and model form are proposed with trade-offs and approved before
  implementation.
- **Stationarity first.** These are macro time series; each is tested for
  stationarity and the results reported before any regression, to avoid
  spurious-regression risk. Raw levels are not regressed without justification.

## Built with Claude Code

This repo was developed with Claude Code under a staged, human-in-the-loop
workflow:

- **Claude scaffolded** the repo structure, the config loader, the FRED fetch +
  caching layer, the CLI surface, the offline test suite, and this README.
- **The author directs and reviews** all analytical and modeling decisions —
  model choice, transformations, stationarity handling, and scenario design —
  which Claude proposes with trade-offs rather than picking unilaterally.

Work proceeds in four reviewed stages: (1) scaffold + fetch, (2) model,
(3) scenarios, (4) chart + writeup.
