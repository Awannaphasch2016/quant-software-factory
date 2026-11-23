"""Tests for the Grid Trade Performance figures and checks (#27, part 2 of #23)."""

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

from quant_software_factory.reporting import FixtureSource, SqliteSource
from quant_software_factory.reporting.grid_checks import (
    GRID_CHECK_NAMES,
    dividend_check,
    nav_volume_check,
    same_figure_check,
    transaction_rows_check,
)
from quant_software_factory.reporting.grid_performance import (
    GridInputs,
    Report,
    build_report,
    expected_volume,
    fmt_as_of_label,
    fmt_money,
    fmt_pct,
    fmt_plain,
    fmt_units,
    fmt_whole,
    load_inputs,
    main,
    run_report,
    write_outputs,
)
from quant_software_factory.reporting.make_private_db import read_csv, write_db
from quant_software_factory.reporting.schema import GRID_DATASETS

REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "data" / "fixtures" / "demo_grid_2026_11"
REPORT_ID = "demo_grid_2026_11"
COMMITTED = REPO / "reports" / REPORT_ID
PACKAGE = REPO / "src" / "quant_software_factory" / "reporting"
ACCOUNT = "DEMO-0001"
AS_OF = date(2026, 11, 6)
GENERATED_AT = "2026-11-06T18:00:00Z"
OPTIONS = [
    "--account",
    ACCOUNT,
    "--as-of",
    "2026-11-06",
    "--generated-at",
    GENERATED_AT,
]
FILES = ["checks.json", "report.json", "report.pdf"]
LAYER_A_NAMES = [
    "A2_account_info_has_rows",
    "A2_grid_cash_as_of_date",
    "A2_grid_cash_unique_rows",
    "A2_grid_setup_has_rows",
    "A2_holdings_daily_as_of_date",
    "A2_holdings_daily_unique_rows",
    "A2_nav_daily_as_of_date",
    "A3_schema_account_info",
    "A3_schema_grid_cash",
    "A3_schema_grid_setup",
    "A3_schema_holdings_daily",
    "A3_schema_nav_daily",
    "A3_schema_transactions",
]
G_NAMES = [
    "G0_mapped_values",
    "G1_nav",
    "G2_holding_rows",
    "G3_same_figure",
    "G4_units",
    "G5_weights",
    "G6_nav_volume",
    "G7_dividend_ytd",
    "G8_transaction_rows",
    "G9_chart_series",
]


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


def _stale(out: Path) -> None:
    out.mkdir(parents=True)
    for name in [*FILES, "keep.txt"]:
        (out / name).write_text("stale\n", encoding="utf-8")


def _inputs() -> GridInputs:
    inputs, problems = load_inputs(FixtureSource(FIXTURE), ACCOUNT, AS_OF, GENERATED_AT)
    assert inputs is not None, problems
    return inputs


def _strings_only(value: Any) -> bool:
    if isinstance(value, dict):
        return all(_strings_only(v) for v in value.values())
    if isinstance(value, list):
        return all(_strings_only(v) for v in value)
    return isinstance(value, str)


@pytest.fixture(scope="module")
def out_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("run") / REPORT_ID
    assert main([str(FIXTURE), str(out), *OPTIONS]) == 0
    return out


@pytest.fixture(scope="module")
def report(out_dir: Path) -> Report:
    data: Report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
    return data


def test_fixture_passes_and_writes_three_files(out_dir: Path) -> None:
    assert _names(out_dir) == FILES
    results = json.loads((out_dir / "checks.json").read_text(encoding="utf-8"))
    names = [r["name"] for r in results]
    assert names == sorted(names)
    assert names == LAYER_A_NAMES + G_NAMES
    assert list(GRID_CHECK_NAMES) == G_NAMES
    for r in results:
        assert list(r) == ["name", "layer", "passed", "expected", "actual"]
        assert r["passed"] is True
        assert r["layer"] == ("A" if r["name"].startswith("A") else "B")


def test_deterministic_and_matches_committed(tmp_path: Path, out_dir: Path) -> None:
    second = tmp_path / REPORT_ID
    assert _run(FIXTURE, second)[0] == 0
    for name in FILES:
        data = (out_dir / name).read_bytes()
        assert data == (second / name).read_bytes(), name
        assert data == (COMMITTED / name).read_bytes(), name
        if name.endswith(".json"):
            assert data.endswith(b"\n") and b"\r" not in data


def test_sqlite_source_gives_identical_report(tmp_path: Path, out_dir: Path) -> None:
    db = tmp_path / "grid.db"
    write_db(db, {dataset: read_csv(FIXTURE, dataset) for dataset in GRID_DATASETS})
    run = run_report(SqliteSource(db), ACCOUNT, AS_OF, GENERATED_AT)
    assert all(r.passed for r in run.results)
    assert run.report is not None
    out = tmp_path / REPORT_ID
    write_outputs(out, run.results, run.report)
    assert _names(out) == FILES
    for name in FILES:
        assert (out / name).read_bytes() == (out_dir / name).read_bytes(), name


def _row(rows: list[dict[str, Any]], ticker: str) -> dict[str, Any]:
    return next(r for r in rows if r["ticker"] == ticker)


def _instrument(report: Report, ticker: str) -> dict[str, Any]:
    return _row(report["instruments"], ticker)


def test_report_structure(report: Report) -> None:
    assert list(report) == [
        "header",
        "cards",
        "holdings",
        "holdings_total",
        "allocation",
        "summary",
        "transactions",
        "instruments",
    ]
    assert _strings_only(report)
    assert list(report["header"]) == [
        "client",
        "account",
        "strategy",
        "inception",
        "as_of_label",
        "request_id",
        "generated_at",
    ]
    assert list(report["cards"]) == ["nav", "cash_on_hand", "dividend_ytd", "cash_pct"]
    holding_keys = [
        "ticker",
        "volume",
        "cost_value",
        "avg_cost",
        "market_price",
        "market_value",
    ]
    assert [r["ticker"] for r in report["holdings"]] == ["AAA", "BBB", "CCC", "CASH"]
    for row in report["holdings"]:
        assert list(row) == holding_keys
    assert list(report["holdings_total"]) == holding_keys
    for key in ("ticker", "volume", "avg_cost", "market_price"):
        assert report["holdings_total"][key] == "-"
    for row in report["allocation"]:
        assert list(row) == ["label", "weight", "weight_raw"]
    assert [r["ticker"] for r in report["summary"]] == ["AAA", "BBB", "CCC"]
    for row in report["summary"]:
        assert list(row) == [
            "ticker",
            "avg_cost",
            "market_price",
            "initial_units",
            "current_units",
            "cash",
            "expected_volume",
            "nav_volume",
            "gain_volume",
        ]
    for row in report["transactions"]:
        assert list(row) == ["trade_date", "ticker", "side", "qty", "price", "amount"]
    assert [i["ticker"] for i in report["instruments"]] == ["AAA", "BBB", "CCC"]
    for item in report["instruments"]:
        assert list(item) == [
            "ticker",
            "cards",
            "initial_cost_value",
            "chart",
            "transactions",
        ]
        assert list(item["cards"]) == [
            "initial_units",
            "current_units",
            "current_units_change_pct",
            "expected_trade_units",
            "expected_trade_return_pct",
            "cash",
            "nav_volume",
            "gain_volume",
            "initial_cost",
            "current_cost",
            "cost_change_pct",
        ]
        assert list(item["chart"]) == [
            "dates",
            "avg_cost",
            "market_price",
            "nav_volume_pct",
        ]
        for row in item["transactions"]:
            assert list(row) == ["trade_date", "side", "qty", "price", "amount"]


def test_expected_header(report: Report) -> None:
    header = report["header"]
    assert (
        header["client"],
        header["account"],
        header["strategy"],
        header["inception"],
    ) == ("DEMO-COOP", "DEMO-0001", "Reverse Grid (GT)", "28 Feb 2024")
    assert header["as_of_label"] == "As of 06 November 2026"
    assert header["request_id"] == "req_DEMO-0001_2026-11-06"
    assert header["generated_at"] == GENERATED_AT


def test_expected_cards(report: Report) -> None:
    assert report["cards"] == {
        "nav": "28,360,975",
        "cash_on_hand": "249,825",
        "dividend_ytd": "830,000",
        "cash_pct": "0.9%",
    }


@pytest.mark.parametrize(
    ("ticker", "expected"),
    [
        ("AAA", ["500,000", "8,206,350.00", "16.41", "13.90", "6,950,000.00"]),
        ("BBB", ["78,200", "9,520,740.52", "121.75", "138.25", "10,811,150.00"]),
        ("CCC", ["180,000", "8,496,594.00", "47.20", "57.50", "10,350,000.00"]),
    ],
)
def test_expected_holdings(report: Report, ticker: str, expected: list[str]) -> None:
    row = _row(report["holdings"], ticker)
    keys = ["volume", "cost_value", "avg_cost", "market_price", "market_value"]
    assert [row[k] for k in keys] == expected


def test_expected_cash_row_and_total(report: Report) -> None:
    cash = _row(report["holdings"], "CASH")
    assert (cash["volume"], cash["cost_value"], cash["market_value"]) == (
        "249,824",
        "249,824.70",
        "249,824.70",
    )
    assert (cash["avg_cost"], cash["market_price"]) == ("1.00", "1.00")
    total = report["holdings_total"]
    assert (total["cost_value"], total["market_value"]) == (
        "26,473,509.22",
        "28,360,974.70",
    )


def test_expected_allocation(report: Report) -> None:
    assert [(r["label"], r["weight"]) for r in report["allocation"]] == [
        ("BBB", "38.1%"),
        ("CCC", "36.5%"),
        ("AAA", "24.5%"),
        ("CASH", "0.9%"),
    ]
    assert [r["weight_raw"] for r in report["allocation"]] == [
        "38.1198",
        "36.4938",
        "24.5055",
        "0.8809",
    ]


@pytest.mark.parametrize(
    ("ticker", "expected"),
    [
        ("AAA", ["500,000", "500,000", "0.00", "0", "500,000", "0"]),
        ("BBB", ["80,000", "78,200", "249,824.70", "1,800", "80,000", "0"]),
        ("CCC", ["300,000", "180,000", "0.00", "0", "180,000", "-120,000"]),
    ],
)
def test_expected_summary(report: Report, ticker: str, expected: list[str]) -> None:
    row = _row(report["summary"], ticker)
    keys = [
        "initial_units",
        "current_units",
        "cash",
        "expected_volume",
        "nav_volume",
        "gain_volume",
    ]
    assert [row[k] for k in keys] == expected


def test_expected_transactions(report: Report) -> None:
    rows = report["transactions"]
    assert len(rows) == 25
    assert rows[0] == {
        "trade_date": "2026-10-20",
        "ticker": "BBB",
        "side": "Sell",
        "qty": "1,800",
        "price": "139.00",
        "amount": "249,824.70",
    }
    adjustments = [r for r in rows if r["ticker"] == "CASH"]
    assert [list(r.values()) for r in adjustments] == [
        ["2026-03-25", "CASH", "Port Adjusted", "-2,950,000", "1.00", "-2,950,000.00"],
        ["2026-03-25", "CASH", "Gain Adjustment", "18,420", "1.00", "18,420.35"],
    ]
    dates = [r["trade_date"] for r in rows]
    assert dates == sorted(dates, reverse=True)
    # The oldest row (2024-05-14 AAA Sell) is the 26th and is left out.
    assert rows[-1]["trade_date"] == "2024-07-22"
    assert {r["side"] for r in rows} == {
        "Buy",
        "Sell",
        "Dividend",
        "Port Adjusted",
        "Gain Adjustment",
    }
    for row in rows:
        if row["side"] in ("Buy", "Sell", "Dividend"):
            assert not row["amount"].startswith("-")


@pytest.mark.parametrize(
    ("ticker", "expected"),
    [
        (
            "AAA",
            {
                "current_units_change_pct": "0.00%",
                "initial_cost": "24.80",
                "current_cost": "16.41",
                "cost_change_pct": "-33.82%",
            },
        ),
        (
            "BBB",
            {
                "current_units_change_pct": "-2.25%",
                "cash": "249,825",
                "cost_change_pct": "-24.14%",
            },
        ),
        (
            "CCC",
            {
                "current_units_change_pct": "-40.00%",
                "gain_volume": "-120,000",
                "cost_change_pct": "-30.99%",
            },
        ),
    ],
)
def test_expected_instrument_cards(
    report: Report, ticker: str, expected: dict[str, str]
) -> None:
    cards = _instrument(report, ticker)["cards"]
    assert {k: cards[k] for k in expected} == expected


@pytest.mark.parametrize(
    ("ticker", "expected"),
    [("AAA", "12,400,000"), ("BBB", "12,840,000"), ("CCC", "20,520,000")],
)
def test_expected_initial_cost_value(
    report: Report, ticker: str, expected: str
) -> None:
    assert _instrument(report, ticker)["initial_cost_value"] == expected


@pytest.mark.parametrize("ticker", ["AAA", "BBB", "CCC"])
def test_expected_chart(report: Report, ticker: str) -> None:
    chart = _instrument(report, ticker)["chart"]
    assert len(chart["dates"]) == 35
    assert (chart["dates"][0], chart["dates"][-1]) == ("2024-02-28", "2026-11-06")
    for series in ("avg_cost", "market_price", "nav_volume_pct"):
        assert len(chart[series]) == 35
    assert chart["nav_volume_pct"][0] == "0.0000"
    assert re.fullmatch(r"-?\d+\.\d{4}", chart["avg_cost"][0])
    assert re.fullmatch(r"-?\d+\.\d{2}", chart["market_price"][0])


def test_chart_values(report: Report) -> None:
    aaa = _instrument(report, "AAA")["chart"]
    assert aaa["avg_cost"][-1] == "16.4127"
    assert aaa["market_price"][-1] == "13.90"
    assert aaa["nav_volume_pct"][aaa["dates"].index("2024-05-31")] == "-4.0000"
    ccc = _instrument(report, "CCC")["chart"]
    assert ccc["nav_volume_pct"][-1] == "-40.0000"
    assert "-13.3333" in ccc["nav_volume_pct"]


def test_instrument_transactions(report: Report) -> None:
    counts = {i["ticker"]: len(i["transactions"]) for i in report["instruments"]}
    assert counts == {"AAA": 7, "BBB": 7, "CCC": 6}
    bbb = _instrument(report, "BBB")["transactions"]
    assert bbb[0] == {
        "trade_date": "2026-10-20",
        "side": "Sell",
        "qty": "1,800",
        "price": "139.00",
        "amount": "249,824.70",
    }
    for item in report["instruments"]:
        dates = [r["trade_date"] for r in item["transactions"]]
        assert dates == sorted(dates, reverse=True)


@pytest.mark.parametrize(
    ("file_name", "edits", "failing_check"),
    [
        (
            "nav_daily.csv",
            [("2024-02-29,DEMO-0001,46397200.00", "2024-02-29,DEMO-0001,46397201.00")],
            "G1_nav",
        ),
        (
            "holdings_daily.csv",
            [("25.40,12700000.00,300000.00", "25.40,12700000.00,300001.00")],
            "G2_holding_rows",
        ),
        (
            "nav_daily.csv",
            [
                (
                    "28360974.70,249824.70,28111150.00",
                    "28360974.70,249825.70,28111150.00",
                )
            ],
            "G3_same_figure",
        ),
        (
            "transactions.csv",
            [
                (
                    "2024-05-14,DEMO-0001,AAA,SELL,20000",
                    "2024-05-14,DEMO-0001,AAA,SELL,20001",
                )
            ],
            "G4_units",
        ),
        (
            "nav_daily.csv",
            [
                (
                    "2026-11-06,DEMO-0001,28360974.70,",
                    "2026-11-06,DEMO-0001,28460974.70,",
                )
            ],
            "G5_weights",
        ),
        (
            "account_info.csv",
            [("Reverse Grid (GT),2024-02-28", "Reverse Grid (GT),2024-02-27")],
            "G9_chart_series",
        ),
    ],
)
def test_broken_fixture_fails(
    tmp_path: Path, file_name: str, edits: list[tuple[str, str]], failing_check: str
) -> None:
    root = _copy_fixture(tmp_path)
    _edit(root / file_name, edits)
    out = tmp_path / "out"
    _stale(out)
    rc, checks = _run(root, out)
    assert rc == 1
    assert all(r["passed"] for n, r in checks.items() if n.startswith("A"))
    assert checks["G0_mapped_values"]["passed"] is True
    assert checks[failing_check]["passed"] is False
    assert checks[failing_check]["layer"] == "B"
    assert _names(out) == ["checks.json", "keep.txt"]


def test_tolerance_allows_one_cent(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    _edit(
        root / "nav_daily.csv",
        [("2024-02-29,DEMO-0001,46397200.00", "2024-02-29,DEMO-0001,46397200.01")],
    )
    rc, checks = _run(root, tmp_path / "out")
    assert rc == 0
    assert checks["G1_nav"]["passed"] is True


def _fixture_report() -> tuple[GridInputs, Report]:
    inputs = _inputs()
    return inputs, build_report(inputs)


def test_g6_fails_on_altered_report() -> None:
    _, report = _fixture_report()
    assert nav_volume_check(report).passed is True
    for alter in ("summary", "cards"):
        changed = copy.deepcopy(report)
        if alter == "summary":
            _row(changed["summary"], "BBB")["nav_volume"] = "80,100"
        else:
            _instrument(changed, "BBB")["cards"]["gain_volume"] = "100"
        result = nav_volume_check(changed)
        assert result.passed is False
        assert result.name == "G6_nav_volume"


def test_g7_fails_on_altered_report() -> None:
    inputs, report = _fixture_report()
    assert dividend_check(inputs, report).passed is True
    changed = copy.deepcopy(report)
    changed["cards"]["dividend_ytd"] = "830,001"
    result = dividend_check(inputs, changed)
    assert result.passed is False
    assert result.actual == "830,001 vs 830,000 from 3 row(s)"


@pytest.mark.parametrize("alter", ["drop_row", "amount", "instrument_rows", "extra"])
def test_g8_fails_on_altered_report(alter: str) -> None:
    inputs, report = _fixture_report()
    assert transaction_rows_check(inputs, report).passed is True
    changed = copy.deepcopy(report)
    if alter == "drop_row":
        changed["transactions"].pop()
    elif alter == "amount":
        changed["transactions"][3]["amount"] = "1.00"
    elif alter == "instrument_rows":
        aaa = _instrument(changed, "AAA")
        aaa["transactions"] = aaa["transactions"][:6]
    else:
        ccc = _instrument(changed, "CCC")
        ccc["transactions"].append(dict(ccc["transactions"][0]))
    result = transaction_rows_check(inputs, changed)
    assert result.passed is False
    assert result.name == "G8_transaction_rows"


@pytest.mark.parametrize("alter", ["summary_units", "nav_card", "cash_row"])
def test_g3_fails_on_altered_report(alter: str) -> None:
    _, report = _fixture_report()
    assert same_figure_check(report).passed is True
    changed = copy.deepcopy(report)
    if alter == "summary_units":
        _row(changed["summary"], "CCC")["current_units"] = "180,001"
    elif alter == "nav_card":
        changed["cards"]["nav"] = "28,360,976"
    else:
        _row(changed["holdings"], "CASH")["market_value"] = "249,826.70"
    assert same_figure_check(changed).passed is False


@pytest.mark.parametrize(
    ("file_name", "edits", "problem"),
    [
        (
            "account_info.csv",
            [("AlphaDemo\n", "AlphaDemo\nDEMO-0001,DEMO-COOP,X,2024-02-28,X\n")],
            "account_info: expected 1 row, found 2",
        ),
        (
            "holdings_daily.csv",
            [("2024-03-29,DEMO-0001,BBB,", "2024-03-28,DEMO-0001,BBB,")],
            "holdings_daily: no row for BBB at 2024-03-29",
        ),
        (
            "grid_cash.csv",
            [("2024-02-29,DEMO-0001,CCC,0.00\n", "")],
            "grid_cash: no row for CCC at 2024-02-29",
        ),
        (
            "grid_setup.csv",
            [("DEMO-0001,AAA,1,500000,", "DEMO-0001,AAA,1,0,")],
            "grid_setup row 1: initial_units is not positive",
        ),
        (
            "grid_setup.csv",
            [("1,500000,24.8000,", "1,500000,0.0000,")],
            "grid_setup row 1: initial_cost is not positive",
        ),
        (
            "holdings_daily.csv",
            [
                (
                    "2024-02-28,DEMO-0001,AAA,500000,24.8000,12400000.00,25.40,",
                    "2024-02-28,DEMO-0001,AAA,500000,24.8000,12400000.00,0.00,",
                )
            ],
            "holdings_daily row 1: market_price is not positive",
        ),
        (
            "nav_daily.csv",
            [("2026-11-06,DEMO-0001,28360974.70,", "2026-11-06,DEMO-0001,0.00,")],
            "nav_daily at 2026-11-06: nav is not positive",
        ),
    ],
)
def test_g0_fails_cleanly(
    tmp_path: Path, file_name: str, edits: list[tuple[str, str]], problem: str
) -> None:
    root = _copy_fixture(tmp_path)
    _edit(root / file_name, edits)
    out = tmp_path / "out"
    _stale(out)
    rc, checks = _run(root, out)
    assert rc == 1
    assert all(r["passed"] for n, r in checks.items() if n.startswith("A"))
    g0 = checks["G0_mapped_values"]
    assert g0["passed"] is False
    assert problem in g0["actual"]
    for name in G_NAMES[1:]:
        assert checks[name]["passed"] is False
        assert checks[name]["actual"] == "not run: G0_mapped_values failed"
    assert _names(out) == ["checks.json", "keep.txt"]


def test_unparseable_value_fails_g0_without_traceback() -> None:
    class _Broken:
        def __init__(self) -> None:
            self.inner = FixtureSource(FIXTURE)

        def load(
            self, dataset: str, as_of: date, accounts: Sequence[str]
        ) -> list[dict[str, str]]:
            rows = self.inner.load(dataset, as_of, accounts)
            if dataset == "grid_cash":
                rows[0] = {**rows[0], "cash": "abc"}
            return rows

    inputs, problems = load_inputs(_Broken(), ACCOUNT, AS_OF, GENERATED_AT)
    assert inputs is None
    assert problems == ["grid_cash row 1: cash is missing or invalid"]


def test_layer_a_failure_builds_nothing(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    (root / "grid_cash.csv").unlink()
    out = tmp_path / "out"
    _stale(out)
    rc, checks = _run(root, out)
    assert rc == 1
    assert checks["A3_schema_grid_cash"]["passed"] is False
    assert checks["A3_schema_grid_cash"]["actual"] == "grid_cash.csv not found"
    for name in ("A2_grid_cash_as_of_date", "A2_grid_cash_unique_rows"):
        assert checks[name]["actual"] == "not run: A3_schema_grid_cash failed"
    for name in G_NAMES:
        assert checks[name]["layer"] == "B"
        assert checks[name]["passed"] is False
        assert checks[name]["actual"] == "not run: Layer A failed"
    assert _names(out) == ["checks.json", "keep.txt"]


@pytest.mark.parametrize(
    ("file_name", "edits", "failing_check"),
    [
        (
            "grid_cash.csv",
            [("2026-11-06,DEMO-0001,CCC,0.00\n", "")],
            "A2_grid_cash_as_of_date",
        ),
        (
            "holdings_daily.csv",
            [("2026-11-06,DEMO-0001,CCC,", "2026-11-05,DEMO-0001,CCC,")],
            "A2_holdings_daily_as_of_date",
        ),
        (
            "grid_cash.csv",
            [
                (
                    "2026-11-06,DEMO-0001,CCC,0.00\n",
                    "2026-11-06,DEMO-0001,CCC,0.00\n" * 2,
                )
            ],
            "A2_grid_cash_unique_rows",
        ),
        (
            "nav_daily.csv",
            [("2026-11-06,DEMO-0001,", "2026-11-05,DEMO-0001,")],
            "A2_nav_daily_as_of_date",
        ),
        (
            "grid_setup.csv",
            [("DEMO-0001,AAA,1,500000,", "DEMO-0001,AAA,x,500000,")],
            "A3_schema_grid_setup",
        ),
    ],
)
def test_layer_a_check_failures(
    tmp_path: Path, file_name: str, edits: list[tuple[str, str]], failing_check: str
) -> None:
    root = _copy_fixture(tmp_path)
    _edit(root / file_name, edits)
    rc, checks = _run(root, tmp_path / "out")
    assert rc == 1
    assert checks[failing_check]["passed"] is False
    assert checks["G1_nav"]["actual"] == "not run: Layer A failed"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (fmt_whole(Decimal("28360974.70")), "28,360,975"),
        (fmt_whole(Decimal("249824.50")), "249,825"),
        (fmt_whole(Decimal("-0.4")), "0"),
        (fmt_whole(Decimal("-120000")), "-120,000"),
        (fmt_money(Decimal("-0.004")), "0.00"),
        (fmt_money(Decimal("1234.565")), "1,234.57"),
        (fmt_money(Decimal("-2950000")), "-2,950,000.00"),
        (fmt_units(-120000), "-120,000"),
        (fmt_units(0), "0"),
        (fmt_pct(Decimal("0.88086"), 1), "0.9%"),
        (fmt_pct(Decimal("-0.04"), 1), "0.0%"),
        (fmt_pct(Decimal("-33.8185"), 2), "-33.82%"),
        (fmt_plain(Decimal("-13.33333"), 4), "-13.3333"),
        (fmt_plain(Decimal("-0.00001"), 4), "0.0000"),
        (fmt_plain(Decimal("38.11975"), 4), "38.1198"),
        (fmt_as_of_label(date(2026, 11, 6)), "As of 06 November 2026"),
        (fmt_as_of_label(date(2024, 2, 1)), "As of 01 February 2024"),
    ],
)
def test_formatting(value: str, expected: str) -> None:
    assert value == expected


@pytest.mark.parametrize(
    ("cash", "price", "expected"),
    [
        (Decimal("249824.70"), Decimal("138.25"), 1800),
        (Decimal("0.00"), Decimal("13.90"), 0),
        (Decimal("13.00"), Decimal("13.90"), 0),
        (Decimal("13920.85"), Decimal("13.90"), 1000),
        (Decimal("13920.84"), Decimal("13.90"), 900),
    ],
)
def test_expected_volume(cash: Decimal, price: Decimal, expected: int) -> None:
    result = expected_volume(cash, price, Decimal("0.0015"))
    assert result == expected
    assert isinstance(result, int)
    assert str(result) == str(expected)


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
    run = run_report(spy, ACCOUNT, AS_OF, GENERATED_AT)
    assert run.report is not None
    assert set(spy.calls) == set(GRID_DATASETS)


@pytest.mark.parametrize(
    "module", ["grid_performance.py", "grid_checks.py", "grid_pdf.py"]
)
def test_no_hard_coded_client_values(module: str) -> None:
    text = (PACKAGE / module).read_text(encoding="utf-8")
    values = ["DEMO-COOP", "DEMO-0001", "2024-02-28", "28 Feb 2024"]
    if module != "grid_pdf.py":
        # The PDF prints "Reverse Grid Trading" as its title.
        values.append("Reverse Grid")
    for value in values:
        assert value not in text
    assert not re.search(r"\d+\.\d+\.\d+\.\d+|https?://", text)


def test_pdf_module_computes_nothing() -> None:
    text = (PACKAGE / "grid_pdf.py").read_text(encoding="utf-8")
    for name in ("Decimal", "parse_display", "grid_performance", "grid_checks"):
        assert name not in text


def test_rejects_bad_generated_at(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main([str(FIXTURE), "unused", *OPTIONS[:4], "--generated-at", "yesterday"])
    assert exc.value.code == 2
    assert "--generated-at" in capsys.readouterr().err


def test_module_entrypoint(tmp_path: Path) -> None:
    out = tmp_path / REPORT_ID
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "quant_software_factory.reporting.grid_performance",
            str(FIXTURE),
            str(out),
            *OPTIONS,
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout == "23 checks, 0 failed\n"
    for name in FILES:
        assert (out / name).read_bytes() == (COMMITTED / name).read_bytes(), name
