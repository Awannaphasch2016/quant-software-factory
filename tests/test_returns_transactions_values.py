"""Layer 3 regression: every row of the issue's Expected Values table."""

from __future__ import annotations

from collections.abc import Callable
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from quant_software_factory.reports.returns_transactions.definitions import (
    PERIOD_RETURN_BASIS,
    REPORT_DEFINITIONS,
)
from quant_software_factory.reports.returns_transactions.engine import (
    EngineResult,
    run_engine,
)
from quant_software_factory.reports.returns_transactions.formatting import fmt_money
from quant_software_factory.reports.returns_transactions.loader import load_inputs
from quant_software_factory.reports.returns_transactions.report import build_report

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "data" / "examples" / "demo_coop_rg_2026_10"
DEFINITION = REPORT_DEFINITIONS["demo_coop_rg_2026_10"]

Report = dict[str, Any]


def _engine() -> EngineResult:
    inputs, checks = load_inputs(FIXTURE_DIR, DEFINITION)
    assert inputs is not None
    assert all(check.passed for check in checks)
    return run_engine(inputs, DEFINITION)


@pytest.fixture(scope="module")
def result() -> EngineResult:
    return _engine()


@pytest.fixture(scope="module")
def report(result: EngineResult) -> Report:
    return build_report(DEFINITION, result)


def _pnl(instrument: str, column: str) -> Callable[[Report], str]:
    def get(report: Report) -> str:
        if instrument == "Total":
            value: str = report["pnl_breakdown"]["total"][column]
            return value
        rows = report["pnl_breakdown"]["rows"]
        row = next(r for r in rows if r["instrument"] == instrument)
        found: str = row[column]
        return found

    return get


def _holding(instrument: str, column: str) -> Callable[[Report], str]:
    def get(report: Report) -> str:
        if instrument == "Total":
            value: str = report["holdings"]["total"][column]
            return value
        rows = report["holdings"]["rows"]
        row = next(r for r in rows if r["instrument"] == instrument)
        found: str = row[column]
        return found

    return get


def _txn(trade_date: str, instrument: str, column: str) -> Callable[[Report], str]:
    def get(report: Report) -> str:
        rows = report["transactions"]["rows"]
        row = next(
            r
            for r in rows
            if r["trade_date"] == trade_date and r["instrument"] == instrument
        )
        found: str = row[column]
        return found

    return get


def _field(block: str, key: str) -> Callable[[Report], str]:
    def get(report: Report) -> str:
        value: str = report[block][key]
        return value

    return get


EXPECTED_VALUES: list[tuple[str, Callable[[Report], str], str]] = [
    ("pnl AAA realized", _pnl("AAA", "realized_capital_gain"), "17,835.00"),
    ("pnl BBB realized", _pnl("BBB", "realized_capital_gain"), "-3,037.00"),
    ("pnl total realized", _pnl("Total", "realized_capital_gain"), "14,798.00"),
    ("pnl BBB net dividend", _pnl("BBB", "net_dividend"), "3,600.00"),
    ("pnl AAA change unrealized", _pnl("AAA", "change_in_unrealized"), "17,000.00"),
    ("pnl BBB change unrealized", _pnl("BBB", "change_in_unrealized"), "-8,000.00"),
    ("pnl AAA total", _pnl("AAA", "total_pnl"), "34,835.00"),
    ("pnl BBB total", _pnl("BBB", "total_pnl"), "-7,437.00"),
    ("pnl total", _pnl("Total", "total_pnl"), "27,398.00"),
    ("holdings AAA volume", _holding("AAA", "volume"), "9,000"),
    ("holdings AAA avg cost", _holding("AAA", "average_cost"), "49.00"),
    ("holdings AAA cost value", _holding("AAA", "cost_value"), "441,000.00"),
    ("holdings AAA market value", _holding("AAA", "market_value"), "468,000.00"),
    ("holdings AAA unrealized", _holding("AAA", "unrealized_pnl"), "27,000.00"),
    ("holdings AAA return", _holding("AAA", "holding_return_pct"), "6.12%"),
    ("holdings BBB volume", _holding("BBB", "volume"), "3,000"),
    ("holdings BBB avg cost", _holding("BBB", "average_cost"), "20.00"),
    ("holdings BBB cost value", _holding("BBB", "cost_value"), "60,000.00"),
    ("holdings BBB market value", _holding("BBB", "market_value"), "57,000.00"),
    ("holdings BBB unrealized", _holding("BBB", "unrealized_pnl"), "-3,000.00"),
    ("holdings BBB return", _holding("BBB", "holding_return_pct"), "-5.00%"),
    ("holdings CASH market value", _holding("CASH", "market_value"), "267,398.00"),
    ("holdings AAA weight", _holding("AAA", "weight_pct"), "59.06%"),
    ("holdings BBB weight", _holding("BBB", "weight_pct"), "7.19%"),
    ("holdings CASH weight", _holding("CASH", "weight_pct"), "33.75%"),
    ("holdings total market value", _holding("Total", "market_value"), "792,398.00"),
    ("kpi closing NAV", _field("kpi_summary", "closing_nav"), "792,398.00"),
    ("holdings total unrealized", _holding("Total", "unrealized_pnl"), "24,000.00"),
    (
        "txn AAA SELL net proceeds",
        _txn("2026-10-12", "AAA", "net_cash_amount"),
        "164,835.00",
    ),
    (
        "txn BBB SELL net proceeds",
        _txn("2026-10-20", "BBB", "net_cash_amount"),
        "36,963.00",
    ),
    ("kpi period return", _field("kpi_summary", "period_return_pct"), "3.83%"),
    ("recon opening NAV", _field("reconciliation", "opening_nav"), "715,000.00"),
    ("recon deposits", _field("reconciliation", "deposits"), "50,000.00"),
    ("recon withdrawals", _field("reconciliation", "withdrawals"), "0.00"),
    (
        "recon expected closing NAV",
        _field("reconciliation", "expected_closing_nav"),
        "792,398.00",
    ),
    ("recon difference", _field("reconciliation", "difference"), "0.00"),
]


@pytest.mark.parametrize(
    ("accessor", "expected"),
    [
        pytest.param(accessor, expected, id=name)
        for name, accessor, expected in EXPECTED_VALUES
    ],
)
def test_expected_value(
    report: Report, accessor: Callable[[Report], str], expected: str
) -> None:
    assert accessor(report) == expected


def test_aaa_average_cost_after_buy(result: EngineResult) -> None:
    buy = next(
        r
        for r in result.transactions
        if r.txn.side == "BUY" and r.txn.trade_date.isoformat() == "2026-10-05"
    )
    assert buy.avg_cost_after is not None
    assert fmt_money(buy.avg_cost_after) == "49.00"


def test_bbb_dividend_gross_and_tax(result: EngineResult) -> None:
    dividend = next(r for r in result.transactions if r.txn.side == "DIVIDEND")
    assert dividend.gross_dividend is not None
    assert fmt_money(dividend.gross_dividend) == "4,000.00"
    assert fmt_money(dividend.txn.tax) == "400.00"
    assert fmt_money(dividend.net_cash) == "3,600.00"


def test_period_return_is_labelled_simple_not_time_weighted(report: Report) -> None:
    basis = report["kpi_summary"]["period_return_basis"]
    assert basis == PERIOD_RETURN_BASIS
    assert "simple" in basis
    assert "opening NAV" in basis
    assert "not time-weighted" in basis


def test_engine_values_are_decimal(result: EngineResult) -> None:
    values = [
        result.closing_nav,
        result.opening_nav,
        result.total_pnl,
        result.period_return_pct,
        result.closing_cash,
    ]
    for instrument in result.instruments:
        values.extend(
            [instrument.closing_cost, instrument.realized_gain, instrument.weight_pct]
        )
    assert all(type(value) is Decimal for value in values)
    assert result.closing_nav == Decimal("792398.00")
    assert result.expected_closing_nav == result.closing_nav


def test_reports_source_has_no_float() -> None:
    package = (
        REPO_ROOT
        / "src"
        / "quant_software_factory"
        / "reports"
        / "returns_transactions"
    )
    for path in sorted(package.glob("*.py")):
        assert "float" not in path.read_text(encoding="utf-8"), path.name
