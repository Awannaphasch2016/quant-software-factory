"""Tests for the Returns & Transactions report, Layer B and writing checks."""

from __future__ import annotations

import copy
import json
import re
import shutil
import subprocess
import sys
from collections.abc import Sequence
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from quant_software_factory.reporting import FixtureSource
from quant_software_factory.reporting.narrative import generate_narrative
from quant_software_factory.reporting.report_checks import (
    LAYER_B_CHECK_NAMES,
    narrative_checks,
    same_figure_check,
)
from quant_software_factory.reporting.returns_transactions import (
    DISCLAIMER,
    Report,
    build_report,
    fmt_int,
    fmt_long_date,
    fmt_money,
    fmt_pct,
    load_inputs,
    main,
)

REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "data" / "fixtures" / "demo_coop_rg_2026_10_v2"
REPORT_ID = "demo_coop_rg_2026_10_v2"
COMMITTED = REPO / "reports" / REPORT_ID
PACKAGE = REPO / "src" / "quant_software_factory" / "reporting"
ACCOUNT = "DEMO-0001"
OPENING = date(2026, 9, 30)
AS_OF = date(2026, 10, 30)
OPTIONS = ["--account", ACCOUNT, "--opening", "2026-09-30", "--as-of", "2026-10-30"]
FILES = ["checks.json", "narrative.md", "report.json", "report.md"]
LAYER_A_COUNT = 14
ACCOUNT_ROW = "DEMO-0001,DEMO-COOP,Reverse Grid,2024-02-28,AlphaDemo\n"


def _run(root: Path, out: Path) -> tuple[int, dict[str, dict[str, Any]]]:
    rc = main([str(root), str(out), *OPTIONS])
    results: list[dict[str, Any]] = json.loads(
        (out / "checks.json").read_text(encoding="utf-8")
    )
    return rc, {r["name"]: r for r in results}


def _copy_fixture(tmp_path: Path) -> Path:
    root = tmp_path / "data"
    shutil.copytree(FIXTURE, root)
    return root


def _edit(path: Path, edits: list[tuple[str, str]]) -> None:
    text = path.read_text(encoding="utf-8")
    for old, new in edits:
        assert old in text, old
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")


def _names(out: Path) -> list[str]:
    return sorted(p.name for p in out.iterdir())


def _fixture_report() -> Report:
    inputs, problems = load_inputs(FixtureSource(FIXTURE), ACCOUNT, OPENING, AS_OF)
    assert inputs is not None, problems
    report = build_report(inputs, REPORT_ID)
    report["narrative"] = generate_narrative(report)
    return report


@pytest.fixture(scope="module")
def out_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("run") / REPORT_ID
    assert main([str(FIXTURE), str(out), *OPTIONS]) == 0
    return out


@pytest.fixture(scope="module")
def report(out_dir: Path) -> Report:
    data: Report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
    return data


def test_fixture_passes_and_writes_four_files(out_dir: Path) -> None:
    assert _names(out_dir) == FILES
    results = json.loads((out_dir / "checks.json").read_text(encoding="utf-8"))
    names = [r["name"] for r in results]
    assert names == sorted(names)
    assert len(names) == LAYER_A_COUNT + len(LAYER_B_CHECK_NAMES)
    assert [n for n in names if not n.startswith("A")] == list(LAYER_B_CHECK_NAMES)
    for r in results:
        assert list(r) == ["name", "layer", "passed", "expected", "actual"]
        assert r["passed"] is True
        assert r["layer"] == ("A" if r["name"].startswith("A") else "B")


def _get(report: Report, path: Sequence[str]) -> Any:
    value: Any = report
    for key in path:
        if isinstance(value, list):
            value = next(row for row in value if row["instrument"] == key)
        else:
            value = value[key]
    return value


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        (("header", "client"), "DEMO-COOP"),
        (("header", "account"), "DEMO-0001"),
        (("header", "strategy"), "Reverse Grid"),
        (("header", "inception"), "28 Feb 2024"),
        (("header", "period_start"), "2026-10-01"),
        (("header", "period_end"), "2026-10-31"),
        (("header", "as_of"), "2026-10-30"),
        (("header", "currency"), "THB"),
        (("header", "report_id"), REPORT_ID),
        (("kpi_summary", "net_asset_value"), "792,398.00"),
        (("kpi_summary", "cash"), "267,398.00"),
        (("kpi_summary", "realized_capital_gain"), "14,798.00"),
        (("kpi_summary", "dividends_net"), "3,600.00"),
        (("kpi_summary", "change_in_unrealized_pl"), "9,000.00"),
        (("kpi_summary", "total_pl"), "27,398.00"),
        (("kpi_summary", "period_return"), "3.83%"),
        (("holdings", "AAA", "volume"), "9,000"),
        (("holdings", "AAA", "avg_cost"), "49.00"),
        (("holdings", "AAA", "cost_value"), "441,000.00"),
        (("holdings", "AAA", "market_price"), "52.00"),
        (("holdings", "AAA", "market_value"), "468,000.00"),
        (("holdings", "AAA", "unrealized_pl"), "27,000.00"),
        (("holdings", "BBB", "volume"), "3,000"),
        (("holdings", "BBB", "avg_cost"), "20.00"),
        (("holdings", "BBB", "cost_value"), "60,000.00"),
        (("holdings", "BBB", "market_price"), "19.00"),
        (("holdings", "BBB", "market_value"), "57,000.00"),
        (("holdings", "BBB", "unrealized_pl"), "-3,000.00"),
        (("holdings", "CASH", "market_value"), "267,398.00"),
        (("holdings", "CASH", "cost_value"), None),
        (("holdings", "Total", "cost_value"), "501,000.00"),
        (("holdings", "Total", "market_value"), "792,398.00"),
        (("holdings", "Total", "unrealized_pl"), "24,000.00"),
        (("holdings", "Total", "volume"), None),
        (("disclaimer",), DISCLAIMER),
    ],
)
def test_expected_values(report: Report, path: Sequence[str], expected: Any) -> None:
    assert _get(report, path) == expected


def test_report_structure(report: Report) -> None:
    assert list(report) == [
        "header",
        "kpi_summary",
        "holdings",
        "transactions",
        "narrative",
        "disclaimer",
    ]
    assert [r["instrument"] for r in report["holdings"]] == [
        "AAA",
        "BBB",
        "CASH",
        "Total",
    ]
    assert report["disclaimer"] == (
        "This report is prepared for the named account holder only. It is not an "
        "offer, solicitation, or investment advice. Past performance does not "
        "indicate future results."
    )


def test_transactions_block(report: Report) -> None:
    rows = report["transactions"]
    assert len(rows) == 5
    first = rows[0]
    assert (first["date"], first["instrument"], first["side"], first["amount"]) == (
        "2026-10-26",
        "CASH",
        "DEPOSIT",
        "50,000.00",
    )
    assert [r["date"] for r in rows] == sorted((r["date"] for r in rows), reverse=True)
    sale = next(r for r in rows if r["date"] == "2026-10-20")
    assert (sale["instrument"], sale["side"]) == ("BBB", "SELL")
    assert (sale["amount"], sale["realized_pl"]) == ("36,963.00", "-3,037.00")
    for row in rows:
        assert (row["realized_pl"] is None) == (row["side"] != "SELL")


def test_narrative_text(out_dir: Path, report: Report) -> None:
    text = (out_dir / "narrative.md").read_text(encoding="utf-8")
    assert "a realized loss of 3,037.00 THB" in text
    assert "a deposit of 50,000.00 THB" in text
    assert "gain of -" not in text
    assert "deposits of" not in text
    assert text == "\n\n".join(report["narrative"]) + "\n"
    assert 2 <= len(report["narrative"]) <= 4
    assert len(text.split()) < 180


def test_markdown_blocks_in_order(out_dir: Path) -> None:
    text = (out_dir / "report.md").read_text(encoding="utf-8")
    headings = [line for line in text.splitlines() if line.startswith("## ")]
    assert headings == [
        "## Returns & Transactions Report",
        "## KPI summary",
        "## Holdings",
        "## Transactions",
        "## Narrative",
        "## Disclaimer",
    ]
    assert text.rstrip("\n").endswith(DISCLAIMER)


def test_deterministic_and_matches_committed(tmp_path: Path, out_dir: Path) -> None:
    second = tmp_path / REPORT_ID
    assert _run(FIXTURE, second)[0] == 0
    for name in FILES:
        data = (out_dir / name).read_bytes()
        assert data == (second / name).read_bytes(), name
        assert data == (COMMITTED / name).read_bytes(), name


def _stale(out: Path) -> None:
    out.mkdir(parents=True)
    for name in [*FILES, "keep.txt"]:
        (out / name).write_text("stale\n", encoding="utf-8")


@pytest.mark.parametrize(
    ("file_name", "edits", "failing_check"),
    [
        (
            "account_info.csv",
            [("AlphaDemo\n", "AlphaDemo\nDEMO-0001,DEMO-COOP,X,2024-02-28,X\n")],
            "B0_mapped_values",
        ),
        ("nav_daily.csv", [("792398.00,267398.00", "792399.00,267398.00")], "B1"),
        ("nav_daily.csv", [("267398.00,525000.00", "267398.00,525001.00")], "B2"),
        ("holdings_daily.csv", [("468000.00,27000.00", "468000.00,27001.00")], "B3"),
        ("nav_daily.csv", [("715000.00", "715001.00")], "B5"),
        ("performance.csv", [("9000.00,27398.00", "9001.00,27398.00")], "B6"),
        (
            "transactions.csv",
            [("164835.00,17835.00", "164835.00,17836.00")],
            "B7_realized_capital_gain",
        ),
        ("transactions.csv", [("400.00,3600.00", "400.00,3601.00")], "B7_dividends"),
    ],
)
def test_number_check_failures(
    tmp_path: Path, file_name: str, edits: list[tuple[str, str]], failing_check: str
) -> None:
    root = _copy_fixture(tmp_path)
    _edit(root / file_name, edits)
    out = tmp_path / "out"
    _stale(out)
    rc, checks = _run(root, out)
    assert rc == 1
    assert all(r["passed"] for n, r in checks.items() if n.startswith("A"))
    failed = [n for n, r in checks.items() if not r["passed"]]
    assert any(n.startswith(failing_check) for n in failed), failed
    assert _names(out) == ["checks.json", "keep.txt"]


def test_b0_failure_marks_other_checks_not_run(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    _edit(root / "account_info.csv", [("AlphaDemo\n", "AlphaDemo\n" + ACCOUNT_ROW)])
    rc, checks = _run(root, tmp_path / "out")
    assert rc == 1
    assert checks["B0_mapped_values"]["actual"] == (
        "account_info: expected 1 row, found 2"
    )
    for name in LAYER_B_CHECK_NAMES[1:]:
        assert checks[name]["passed"] is False
        assert checks[name]["actual"] == "not run: B0_mapped_values failed"


def test_tolerance_allows_one_cent(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    _edit(root / "nav_daily.csv", [("525000.00", "525000.01")])
    rc, checks = _run(root, tmp_path / "out")
    assert rc == 0
    assert checks["B2_securities_value"]["actual"] == "525000.00 vs 525000.01"


def test_layer_a_failure_builds_nothing(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    (root / "holdings_daily.csv").unlink()
    out = tmp_path / "out"
    _stale(out)
    rc, checks = _run(root, out)
    assert rc == 1
    assert checks["A3_schema_holdings_daily"]["passed"] is False
    assert _names(out) == ["checks.json", "keep.txt"]
    for name in LAYER_B_CHECK_NAMES:
        assert checks[name]["layer"] == "B"
        assert checks[name]["passed"] is False
        assert checks[name]["actual"] == "not run: Layer A failed"


@pytest.mark.parametrize(
    "target", ["kpi_cash", "kpi_nav", "cash_row", "total_row", "missing_row"]
)
def test_b4_same_figure_fails(target: str) -> None:
    report = _fixture_report()
    assert same_figure_check(report).passed is True
    changed = copy.deepcopy(report)
    if target == "kpi_cash":
        changed["kpi_summary"]["cash"] = "267,399.00"
    elif target == "kpi_nav":
        changed["kpi_summary"]["net_asset_value"] = "792,398.02"
    elif target == "cash_row":
        _get(changed, ("holdings", "CASH"))["market_value"] = "1.00"
    elif target == "total_row":
        _get(changed, ("holdings", "Total"))["market_value"] = "1.00"
    else:
        changed["holdings"] = changed["holdings"][:2]
    result = same_figure_check(changed)
    assert result.passed is False
    assert result.layer == "B"


GOOD = [
    "Net asset value was 792,398.00 THB on 30 Oct 2026.",
    "The account received a deposit of 50,000.00 THB. Cash was 267,398.00 THB.",
]


def _narrative_results(paragraphs: list[str]) -> dict[str, bool]:
    return {r.name: r.passed for r in narrative_checks(paragraphs, _fixture_report())}


def test_good_narrative_passes() -> None:
    assert all(_narrative_results(GOOD).values())
    loss = ["Sales gave a realized loss of 3,037.00 THB.", "Return was 3.83%."]
    assert _narrative_results(loss)["B8_narrative_numbers"] is True


@pytest.mark.parametrize(
    ("paragraphs", "failing_check"),
    [
        ([GOOD[0].replace("792,398.00", "1,234.56"), GOOD[1]], "B8_narrative_numbers"),
        ([GOOD[0] + " Return was 1234.56%.", GOOD[1]], "B8_narrative_numbers"),
        ([GOOD[0], GOOD[1].replace("a deposit", "a robust deposit")], "W1"),
        ([GOOD[0], "In today's market cash was 267,398.00 THB."], "W1"),
        ([GOOD[0], "Sales gave a gain of -3,037.00 THB."], "W2_no_negative_gain"),
        (["The NAV was 792,398.00 THB. The cash was 267,398.00 THB.", GOOD[1]], "W3"),
        (["Net asset value was 792,398.00 THB.", "Net cash was 267,398.00 THB."], "W3"),
        ([GOOD[0]], "W4_length"),
        ([*GOOD, *GOOD, GOOD[0]], "W4_length"),
        ([GOOD[0], "Cash " * 180], "W4_length"),
        ([GOOD[0], "Net asset value will rise."], "W5_forecast_words"),
        ([GOOD[0], "We recommend a review."], "W5_forecast_words"),
    ],
)
def test_narrative_check_failures(paragraphs: list[str], failing_check: str) -> None:
    results = _narrative_results(paragraphs)
    failed = [name for name, passed in results.items() if not passed]
    assert any(name.startswith(failing_check) for name in failed), failed


def _flow(day: str, side: str, amount: str) -> dict[str, str | None]:
    return {
        "date": day,
        "instrument": "CASH",
        "side": side,
        "qty": None,
        "price": None,
        "fee": None,
        "tax": None,
        "amount": amount,
        "realized_pl": None,
    }


def _variant(name: str) -> Report:
    report = _fixture_report()
    report["narrative"] = []
    if name == "empty":
        report["transactions"] = []
    elif name == "flows":
        report["transactions"] = [
            _flow("2026-10-16", "WITHDRAWAL", "-5,000.00"),
            _flow("2026-10-09", "DEPOSIT", "20,000.00"),
            _flow("2026-10-02", "DEPOSIT", "10,000.00"),
        ]
    elif name == "many":
        report["holdings"] = report["holdings"][1:]
        report["transactions"] = [
            _flow("2026-10-29", "WITHDRAWAL", "-2,000.00"),
            _flow("2026-10-28", "WITHDRAWAL", "-1,000.00"),
            *[_flow(f"2026-10-0{d}", "DEPOSIT", "100.00") for d in (3, 2, 1)],
        ]
    elif name == "losses":
        kpi = report["kpi_summary"]
        kpi.update(
            total_pl="-1,000.00",
            period_return="-0.14%",
            realized_capital_gain="-500.00",
            change_in_unrealized_pl="-200.00",
        )
        report["holdings"] = report["holdings"][2:]
        report["transactions"] = [
            _flow("2026-10-25", "WITHDRAWAL", "-5,000.00"),
            *[r for r in report["transactions"] if r["date"] == "2026-10-20"],
        ]
    return report


@pytest.mark.parametrize(
    ("name", "phrases"),
    [
        (
            "empty",
            [
                "There were no sales in the period.",
                "No dividends were received in the period.",
                "There were no deposits or withdrawals in the period.",
            ],
        ),
        (
            "flows",
            [
                "deposits of 10,000.00 THB on 02 Oct 2026 and 20,000.00 THB on "
                "09 Oct 2026",
                "A withdrawal of 5,000.00 THB was made on 16 Oct 2026.",
            ],
        ),
        (
            "many",
            [
                "held one position: BBB with an unrealized loss of 3,000.00 THB.",
                "Unrealized P/L on this position was a gain of 24,000.00 THB",
                "The account received 3 deposits.",
                "Withdrawals were 1,000.00 THB on 28 Oct 2026 and 2,000.00 THB on "
                "29 Oct 2026.",
            ],
        ),
        (
            "losses",
            [
                "a loss of 1,000.00 THB, a negative simple return of 0.14%",
                "made one sale: BBB on 20 Oct 2026 with a realized loss of 3,037.00",
                "Realized capital result for the period was a loss of 500.00 THB.",
                "held no securities positions",
                "unrealized P/L for the period was a loss of 200.00 THB",
                "No deposits were made in the period.",
                "A withdrawal of 5,000.00 THB was made on 25 Oct 2026.",
            ],
        ),
    ],
)
def test_narrative_variants(name: str, phrases: list[str]) -> None:
    report = _variant(name)
    paragraphs = generate_narrative(report)
    text = " ".join(paragraphs)
    for phrase in phrases:
        assert phrase in text
    results = narrative_checks(paragraphs, report)
    assert all(r.passed for r in results), [r for r in results if not r.passed]


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (fmt_money(Decimal("-0.004")), "0.00"),
        (fmt_money(Decimal("-0.005")), "-0.01"),
        (fmt_money(Decimal("1234.565")), "1,234.57"),
        (fmt_money(Decimal("-3037")), "-3,037.00"),
        (fmt_money(Decimal("1234567.8")), "1,234,567.80"),
        (fmt_pct(Decimal("3.825")), "3.83%"),
        (fmt_pct(Decimal("-0.001")), "0.00%"),
        (fmt_int(9000), "9,000"),
        (fmt_long_date(date(2024, 2, 28)), "28 Feb 2024"),
        (fmt_long_date(date(2026, 10, 1)), "01 Oct 2026"),
    ],
)
def test_formatting(value: str, expected: str) -> None:
    assert value == expected


class _SpySource:
    def __init__(self) -> None:
        self.inner = FixtureSource(FIXTURE)
        self.calls: list[str] = []

    def load(
        self, dataset: str, as_of: date, accounts: Sequence[str]
    ) -> list[dict[str, str]]:
        self.calls.append(dataset)
        return self.inner.load(dataset, as_of, accounts)


def test_inputs_read_only_through_load() -> None:
    spy = _SpySource()
    inputs, problems = load_inputs(spy, ACCOUNT, OPENING, AS_OF)
    assert inputs is not None and problems == []
    assert sorted(spy.calls) == sorted(
        [
            "account_info",
            "cash_flow",
            "holdings_daily",
            "nav_daily",
            "performance",
            "transactions",
        ]
    )


@pytest.mark.parametrize(
    "module", ["returns_transactions.py", "report_checks.py", "narrative.py"]
)
def test_no_hard_coded_client_values(module: str) -> None:
    text = (PACKAGE / module).read_text(encoding="utf-8")
    for value in ("DEMO-COOP", "DEMO-0001", "Reverse Grid", "2024-02-28"):
        assert value not in text
    assert not re.search(r"\d+\.\d+\.\d+\.\d+|https?://", text)


def test_module_entrypoint(tmp_path: Path) -> None:
    out = tmp_path / REPORT_ID
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "quant_software_factory.reporting.returns_transactions",
            str(FIXTURE),
            str(out),
            *OPTIONS,
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout == "29 checks, 0 failed\n"
    for name in FILES:
        assert (out / name).read_bytes() == (COMMITTED / name).read_bytes(), name
