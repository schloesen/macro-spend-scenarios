# CLAUDE.md — Macro-Driven Spend Scenario Tool

## Project overview
A small, reusable analytics tool that models how U.S. consumer spending responds to
macroeconomic drivers, and projects it under base / upside / downside scenarios.
This is a portfolio project mirroring FP&A-style scenario & sensitivity analysis.
Keep it **interpretable and executive-facing** — not a heavy ML project.

## What we're building (deliverable)
A config-driven Python tool that:
1. Pulls macro time series from FRED
2. Fits an interpretable model linking consumer spend to its drivers
3. Projects the target under three user-defined scenarios
4. Outputs one clean comparison chart + a short written takeaway

Plus a GitHub-ready repo: clean structure, a README (including a section documenting
the AI-assisted workflow), and one example output committed.

## Data (FRED)
- The API key is in the environment variable `FRED_API_KEY` — **never hardcode it**.
- Cache downloaded series locally (e.g. a `data/` dir); don't re-fetch on every run.
- Series:
  - **Target:** `PCE` (Personal Consumption Expenditures)  *(real alternative: `PCEC96`)*
  - **Drivers:** `CPIAUCSL` (CPI / inflation), `FEDFUNDS` (fed funds rate),
    `UNRATE` (unemployment), `DSPI` (disposable personal income)

## Approach
- Interpretable, explainable model (regression-based). The audience is finance
  stakeholders, so clarity beats sophistication.
- Build it as a **repeatable, config-driven framework**, not a one-off script:
  target series, drivers, and scenario assumptions should all be configurable so the
  whole analysis re-runs with a single command.

## Analytical guardrails (important)
- **I own all analytical and modeling decisions.** Before choosing or changing the
  modeling approach, transformations, or feature set, propose the options with
  trade-offs and wait for my decision. Don't silently pick one.
- **Stationarity first.** These are macro time series. Before fitting any regression,
  test each series for stationarity and report the results. Do **not** regress raw
  levels without addressing non-stationarity — propose differencing/transformations
  and explain why. Explicitly flag any risk of spurious regression.
- Sanity-check scenario outputs for plausibility and tell me if anything looks off.

## Engineering conventions
- Python with a standard scientific stack (pandas, numpy, statsmodels,
  matplotlib or plotly). Keep dependencies minimal.
- Separate modules for data fetching, modeling, scenarios, and visualization, with a
  single entry point (CLI or `main()`) to run end-to-end.
- Write basic tests for the data-loading and scenario logic.
- No secrets in code or git history. Include a `.gitignore`.

## Workflow
- Work in stages and check in with me between each: (1) repo scaffold + FRED fetch,
  (2) model, (3) scenario layer, (4) chart + writeup. Don't build it all at once.
- Briefly explain non-obvious choices as you go.
- Maintain the README, including a short "Built with Claude Code" section noting what
  you scaffolded versus what I directed and reviewed.

## Out of scope (keep it a weekend)
- No black-box/deep ML, no dashboard beyond one clean chart, no deployment.
  Optimize for a clear, defensible, explainable analysis.
