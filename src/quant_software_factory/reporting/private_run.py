"""Run the Returns & Transactions report inside the trusted zone.

Usage::

    python -m quant_software_factory.reporting.private_run --db <db_path> \\
        --private-out <dir> --result <result.json> --account <account> \\
        --opening YYYY-MM-DD --as-of YYYY-MM-DD

Reads the private database only through :class:`SqliteSource` and
:meth:`DataSource.load`, runs the same checks and report builder as
:mod:`.returns_transactions`, and writes ``report.md``, ``report.json``,
``narrative.md`` and ``checks.json`` into ``--private-out``. Only a sanitized
result crosses the boundary into ``--result``: the overall status, the check
counts and each check's name, layer and pass/fail flag.

Exit codes:

- 0: every report check passed; the result is written.
- 1: a report check failed; the result is written with status ``"failed"``.
- 2: ``--private-out`` or ``--result`` is inside the repository working tree
  (or a usage error); nothing is written.
- 3: the boundary leak check failed; no result is written and the failure is
  recorded as ``boundary_leak_check`` in the private ``checks.json`` only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Sequence
from datetime import date
from pathlib import Path
from typing import Any

from .checks import CheckResult
from .returns_transactions import Report, run_report, write_outputs
from .schema import parse_date
from .source import DatasetError
from .sqlite_source import SqliteSource

PROJECT_NAME_LINE = 'name = "quant-software-factory"'
LEAK_CHECK_NAME = "boundary_leak_check"
LEAK_CHECK_LAYER = "boundary"
PASSED = "passed"
FAILED = "failed"
NO_LEAK = "no account id, client name or formatted figure"

# A digit, a decimal point or thousands separator, and a digit: "1.5", "2,377".
_FIGURE_RE = re.compile(r"\d[.,]\d")


def find_repo_root() -> Path | None:
    """Return the directory holding this package's ``pyproject.toml``, if any."""
    here = Path(__file__).resolve().parent
    for directory in (here, *here.parents):
        candidate = directory / "pyproject.toml"
        if candidate.is_file():
            try:
                text = candidate.read_text(encoding="utf-8")
            except OSError:
                continue
            if PROJECT_NAME_LINE in text:
                return directory
    return None


def is_inside(path: Path, root: Path) -> bool:
    """Whether ``path`` resolves to ``root`` or a path below it."""
    resolved = path.resolve()
    base = root.resolve()
    return resolved == base or base in resolved.parents


def build_result(results: Sequence[CheckResult]) -> dict[str, Any]:
    """Build the sanitized result: status, counts and name/layer/passed only."""
    checks = sorted(results, key=lambda r: r.name)
    failed = sum(not r.passed for r in checks)
    return {
        "status": PASSED if failed == 0 else FAILED,
        "checks_total": len(checks),
        "checks_failed": failed,
        "checks": [
            {"name": r.name, "layer": r.layer, "passed": r.passed} for r in checks
        ],
    }


def render_result(results: Sequence[CheckResult]) -> str:
    """Render the sanitized result as JSON text ending with a newline."""
    return json.dumps(build_result(results), indent=2) + "\n"


def leak_check(text: str, account: str, client_names: Sequence[str]) -> CheckResult:
    """Check that ``text`` holds no account id, client name or formatted figure.

    The ``actual`` value names only the categories found, never the values.
    """
    found: list[str] = []
    if account and account in text:
        found.append("account id")
    if any(name and name in text for name in client_names):
        found.append("client name")
    if _FIGURE_RE.search(text):
        found.append("figure")
    actual = "found: " + ", ".join(found) if found else NO_LEAK
    return CheckResult(LEAK_CHECK_NAME, LEAK_CHECK_LAYER, not found, NO_LEAK, actual)


def _client_names(
    source: SqliteSource, report: Report | None, account: str, as_of: date
) -> list[str]:
    if report is not None:
        return [str(report["header"]["client"])]
    try:
        rows = source.load("account_info", as_of, [account])
    except (DatasetError, KeyError):
        return []
    return [row.get("client_name", "") for row in rows]


def _iso_date(value: str) -> date:
    parsed = parse_date(value)
    if parsed is None:
        raise argparse.ArgumentTypeError(f"not an ISO date (YYYY-MM-DD): {value!r}")
    return parsed


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m quant_software_factory.reporting.private_run",
        description=(
            "Build the report from a private database and return only a "
            "sanitized result."
        ),
    )
    parser.add_argument("--db", required=True, type=Path, help="SQLite database")
    parser.add_argument(
        "--private-out",
        dest="private_out",
        required=True,
        type=Path,
        help="private output folder outside the repository; its name is the ID",
    )
    parser.add_argument(
        "--result",
        required=True,
        type=Path,
        help="sanitized result file outside the repository",
    )
    parser.add_argument("--account", required=True)
    parser.add_argument("--opening", required=True, type=_iso_date)
    parser.add_argument("--as-of", dest="as_of", required=True, type=_iso_date)
    return parser


def _write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def main(argv: Sequence[str] | None = None) -> int:
    """Run the report in the trusted zone and write the sanitized result.

    Args:
        argv: Command line arguments; defaults to ``sys.argv[1:]``.

    Returns:
        0 when every report check passes, 1 when any fails, 2 when an output
        path is inside the repository, 3 when the boundary leak check fails.
    """
    args = _parser().parse_args(argv)
    private_out: Path = args.private_out
    result_path: Path = args.result
    root = find_repo_root()
    if root is not None:
        for label, path in (("--private-out", private_out), ("--result", result_path)):
            if is_inside(path, root):
                print(
                    f"error: {label} must be outside the repository working tree",
                    file=sys.stderr,
                )
                return 2

    source = SqliteSource(args.db)
    run = run_report(
        source, args.account, args.opening, args.as_of, private_out.resolve().name
    )
    # Looked up at call time so a test can force a leak.
    result_text = render_result(run.results)
    names = _client_names(source, run.report, args.account, args.as_of)
    leak = leak_check(result_text, args.account, names)
    write_outputs(
        private_out, sorted([*run.results, leak], key=lambda r: r.name), run.report
    )
    if not leak.passed:
        result_path.unlink(missing_ok=True)
        print(
            f"error: boundary leak check failed ({leak.actual}); no result written",
            file=sys.stderr,
        )
        return 3

    result_path.parent.mkdir(parents=True, exist_ok=True)
    _write(result_path, result_text)
    failed = sum(not r.passed for r in run.results)
    print(f"{len(run.results)} checks, {failed} failed")
    return 0 if failed == 0 and run.report is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
