"""Command line entry point that runs the Layer A data checks.

Usage::

    python -m quant_software_factory.reporting.check_data <root> \\
        --account <account> --opening YYYY-MM-DD --as-of YYYY-MM-DD --out <dir>

Writes ``<dir>/checks.json`` and exits 0 when every check passes, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from datetime import date
from pathlib import Path

from .checks import run_checks
from .schema import parse_date
from .source import FixtureSource


def _iso_date(value: str) -> date:
    parsed = parse_date(value)
    if parsed is None:
        raise argparse.ArgumentTypeError(f"not an ISO date (YYYY-MM-DD): {value!r}")
    return parsed


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m quant_software_factory.reporting.check_data",
        description="Run Layer A data checks and write checks.json.",
    )
    parser.add_argument("root", type=Path, help="directory holding <dataset>.csv")
    parser.add_argument("--account", required=True)
    parser.add_argument("--opening", required=True, type=_iso_date)
    parser.add_argument("--as-of", dest="as_of", required=True, type=_iso_date)
    parser.add_argument("--out", required=True, type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the checks and write ``checks.json``.

    Args:
        argv: Command line arguments; defaults to ``sys.argv[1:]``.

    Returns:
        0 when all checks pass, 1 when any check fails.
    """
    args = _parser().parse_args(argv)
    results = run_checks(
        FixtureSource(args.root), args.account, args.opening, args.as_of
    )
    text = json.dumps([r.to_dict() for r in results], indent=2) + "\n"
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=True)
    (out / "checks.json").write_text(text, encoding="utf-8", newline="\n")
    failed = sum(not r.passed for r in results)
    print(f"{len(results)} checks, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
