"""Single entry point for the pipeline.

Run end-to-end (as stages land) or individual steps:

    python -m macro_spend fetch            # Stage 1: pull + cache FRED series
    python -m macro_spend fetch --force    # ignore cache, re-pull everything

Future subcommands (model / scenarios / chart / run) are stubbed until their
stages are implemented, so the CLI surface is visible from the start.
"""

from __future__ import annotations

import argparse
import sys

from .config import load_config
from .data import FredError, fetch_all


def _cmd_fetch(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    print(
        f"Fetching {len(cfg.all_series)} series "
        f"({cfg.date_start} → {cfg.date_end or 'latest'}) into '{cfg.cache_dir}/'"
    )
    try:
        frame = fetch_all(cfg, force=args.force)
    except FredError as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        return 1

    print(
        f"\nAligned panel: {frame.shape[0]} rows × {frame.shape[1]} series "
        f"({frame.index.min():%Y-%m} → {frame.index.max():%Y-%m})"
    )
    missing = frame.isna().sum()
    if missing.any():
        print("Missing values per series (expected from frequency alignment):")
        for sid, n in missing.items():
            if n:
                print(f"  {sid}: {n}")
    return 0


def _cmd_not_ready(stage: str):
    def _run(_args: argparse.Namespace) -> int:
        print(f"'{stage}' is not implemented yet — that stage hasn't been built.")
        return 2

    return _run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="macro_spend", description=__doc__)
    parser.add_argument(
        "-c", "--config", default="config.yaml", help="Path to config.yaml"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_fetch = sub.add_parser("fetch", help="Stage 1: pull + cache FRED series")
    p_fetch.add_argument(
        "--force", action="store_true", help="Ignore cache and re-fetch"
    )
    p_fetch.set_defaults(func=_cmd_fetch)

    for name, stage in (
        ("model", "Stage 2 (model)"),
        ("scenarios", "Stage 3 (scenarios)"),
        ("chart", "Stage 4 (chart)"),
        ("run", "full pipeline"),
    ):
        p = sub.add_parser(name, help=f"{stage} — not yet implemented")
        p.set_defaults(func=_cmd_not_ready(name))

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
