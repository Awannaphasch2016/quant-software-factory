"""End-to-end CLI tests: outputs, determinism, committed sample, failure path."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from quant_software_factory.reports.returns_transactions import cli
from quant_software_factory.reports.returns_transactions.definitions import BLOCK_IDS

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "data" / "examples" / "demo_coop_rg_2026_10"
COMMITTED_DIR = REPO_ROOT / "reports" / "demo_coop_rg_2026_10"
OUTPUT_FILES = ("report.md", "report.json", "narrative.md", "checks.json")
EXPECTED_HEADINGS = [
    "## Header",
    "## KPI Summary",
    "## P/L Breakdown",
    "## Holdings",
    "## Transactions",
    "## Reconciliation",
    "## Narrative",
    "## Disclaimer",
]


def _run(output_dir: Path) -> int:
    return cli.main([str(FIXTURE_DIR), str(output_dir)])


def test_writes_all_four_files(tmp_path: Path) -> None:
    out = tmp_path / "out"
    assert _run(out) == 0
    for name in OUTPUT_FILES:
        data = (out / name).read_bytes()
        assert data.endswith(b"\n")
        assert not data.endswith(b"\n\n")
        assert b"\r" not in data


def test_report_md_has_eight_blocks_in_order(tmp_path: Path) -> None:
    assert _run(tmp_path) == 0
    text = (tmp_path / "report.md").read_text(encoding="utf-8")
    assert text.startswith("# Returns & Transactions Report\n")
    headings = re.findall(r"^## .*$", text, flags=re.MULTILINE)
    assert headings == EXPECTED_HEADINGS
    assert "| ---: |" in text or "---: |" in text


def test_report_json_keys_are_block_ids(tmp_path: Path) -> None:
    assert _run(tmp_path) == 0
    report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    assert list(report) == list(BLOCK_IDS)
    assert report["disclaimer"]["text"] == (
        "This report is prepared for the named account holder only. It is not an "
        "offer, solicitation, or investment advice. Past performance does not "
        "indicate future results."
    )
    assert report["header"]["title"] == "Returns & Transactions Report"
    assert 2 <= len(report["narrative"]["paragraphs"]) <= 4


def test_transactions_are_newest_first(tmp_path: Path) -> None:
    assert _run(tmp_path) == 0
    report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    rows = report["transactions"]["rows"]
    dates = [row["trade_date"] for row in rows]
    assert dates == sorted(dates, reverse=True)
    assert len(rows) == 5
    for row in rows:
        if row["side"] == "SELL":
            assert row["realized_gain"] is not None
        else:
            assert row["realized_gain"] is None


def test_holdings_sorted_with_cash_last(tmp_path: Path) -> None:
    assert _run(tmp_path) == 0
    report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    names = [row["instrument"] for row in report["holdings"]["rows"]]
    assert names == ["AAA", "BBB", "CASH"]
    assert report["holdings"]["total"]["weight_pct"] == "100.00%"


def test_runs_are_byte_identical(tmp_path: Path) -> None:
    first, second = tmp_path / "a", tmp_path / "b"
    assert _run(first) == 0
    assert _run(second) == 0
    for name in OUTPUT_FILES:
        assert (first / name).read_bytes() == (second / name).read_bytes()
    before = (first / "report.json").read_bytes()
    assert _run(first) == 0
    assert (first / "report.json").read_bytes() == before


def test_committed_sample_matches_fresh_run(tmp_path: Path) -> None:
    assert _run(tmp_path) == 0
    for name in OUTPUT_FILES:
        assert (tmp_path / name).read_bytes() == (COMMITTED_DIR / name).read_bytes()


def test_all_checks_pass_and_identity_difference_is_zero(tmp_path: Path) -> None:
    assert _run(tmp_path) == 0
    checks = json.loads((tmp_path / "checks.json").read_text(encoding="utf-8"))
    assert checks
    for check in checks:
        assert set(check) == {"name", "passed", "expected", "actual"}
        assert check["passed"] is True, check
    names = [check["name"] for check in checks]
    for required in (
        "input.columns.transactions.csv",
        "input.sides",
        "input.sell_volume",
        "input.prices.opening",
        "input.prices.closing",
        "accounting.identity",
        "accounting.weights_sum",
        "accounting.cash_replay",
        "narrative.numbers_in_report",
        "narrative.style",
    ):
        assert required in names
    report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    assert report["reconciliation"]["difference"] == "0.00"


def test_module_entry_point(tmp_path: Path) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "quant_software_factory.reports.returns_transactions",
            str(FIXTURE_DIR),
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "RuntimeWarning" not in completed.stderr
    for name in OUTPUT_FILES:
        assert (tmp_path / name).is_file()


def test_failed_narrative_check_blocks_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert _run(tmp_path) == 0
    assert (tmp_path / "report.md").exists()

    def fake_narrative(report: dict[str, Any]) -> list[str]:
        return [
            "The account earned 1,234.56 THB in the period.",
            "Cash was held throughout.",
        ]

    monkeypatch.setattr(cli, "build_narrative", fake_narrative)
    assert _run(tmp_path) == 1
    assert not (tmp_path / "report.md").exists()
    assert not (tmp_path / "report.json").exists()
    assert not (tmp_path / "narrative.md").exists()
    checks = json.loads((tmp_path / "checks.json").read_text(encoding="utf-8"))
    by_name = {check["name"]: check for check in checks}
    assert by_name["narrative.numbers_in_report"]["passed"] is False
    assert "1,234.56" in by_name["narrative.numbers_in_report"]["actual"]


def test_unknown_report_id_is_a_usage_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = cli.main([str(FIXTURE_DIR), str(tmp_path), "--report-id", "no_such"])
    assert code == 2
    assert "unknown report ID" in capsys.readouterr().err
    assert not (tmp_path / "checks.json").exists()


def test_explicit_report_id(tmp_path: Path) -> None:
    code = cli.main(
        [str(FIXTURE_DIR), str(tmp_path), "--report-id", "demo_coop_rg_2026_10"]
    )
    assert code == 0
