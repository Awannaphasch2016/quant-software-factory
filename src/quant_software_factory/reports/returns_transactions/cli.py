"""Command-line entry point for the Returns & Transactions report.

Exit codes: 0 when every check passes and all outputs are written, 1 when any
check fails (only checks.json is written, stale report outputs are removed),
2 for usage errors such as an unknown report ID.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from .checks import Check, accounting_checks, narrative_checks
from .definitions import REPORT_DEFINITIONS
from .engine import run_engine
from .loader import load_inputs
from .narrative import build_narrative, render_narrative
from .report import build_report, dump_json, render_markdown

REPORT_MD = "report.md"
REPORT_JSON = "report.json"
NARRATIVE_MD = "narrative.md"
CHECKS_JSON = "checks.json"


def _write(path: Path, text: str) -> None:
    path.write_bytes(text.encode("utf-8"))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m quant_software_factory.reports.returns_transactions",
        description="Build the Returns & Transactions report from CSV inputs.",
    )
    parser.add_argument("input_dir", type=Path, help="directory with the input CSVs")
    parser.add_argument("output_dir", type=Path, help="directory for the outputs")
    parser.add_argument(
        "--report-id",
        default=None,
        help="report definition to use (default: the input directory name)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    input_dir: Path = args.input_dir
    output_dir: Path = args.output_dir
    report_id: str = args.report_id or input_dir.resolve().name

    definition = REPORT_DEFINITIONS.get(report_id)
    if definition is None:
        known = ", ".join(sorted(REPORT_DEFINITIONS))
        print(
            f"error: unknown report ID {report_id!r} (known: {known})",
            file=sys.stderr,
        )
        return 2

    inputs, checks = load_inputs(input_dir, definition)
    outputs: dict[str, str] = {}
    if inputs is not None and all(check.passed for check in checks):
        result = run_engine(inputs, definition)
        report = build_report(definition, result)
        paragraphs = build_narrative(report)
        report["narrative"] = {"paragraphs": paragraphs}
        narrative_text = render_narrative(paragraphs)
        checks.extend(accounting_checks(result, inputs.transactions))
        checks.extend(narrative_checks(narrative_text, report))
        outputs = {
            REPORT_JSON: dump_json(report),
            NARRATIVE_MD: narrative_text,
            REPORT_MD: render_markdown(report),
        }

    output_dir.mkdir(parents=True, exist_ok=True)
    _write(output_dir / CHECKS_JSON, dump_json([c.to_json() for c in checks]))

    failed: list[Check] = [check for check in checks if not check.passed]
    if failed or not outputs:
        for name in (REPORT_MD, REPORT_JSON, NARRATIVE_MD):
            (output_dir / name).unlink(missing_ok=True)
        for check in failed:
            print(
                f"FAILED {check.name}: expected {check.expected}; "
                f"actual {check.actual}",
                file=sys.stderr,
            )
        return 1

    for name, text in outputs.items():
        _write(output_dir / name, text)
    print(f"{len(checks)} checks passed; wrote {len(outputs) + 1} files")
    return 0
