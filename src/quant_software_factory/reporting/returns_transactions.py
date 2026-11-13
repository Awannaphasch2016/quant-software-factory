"""Returns & Transactions report built from precomputed datasets.

Usage::

    python -m quant_software_factory.reporting.returns_transactions <root> <out> \\
        --account <account> --opening YYYY-MM-DD --as-of YYYY-MM-DD

Runs the Layer A data checks first, then builds the report, its narrative and the
Layer B number and writing checks. When every check passes it writes
``report.md``, ``report.json``, ``narrative.md`` and ``checks.json`` to ``<out>``
and exits 0. When any check fails it writes only ``checks.json``, removes stale
report files and exits 1. The report ID is the name of ``<out>``.

All data is read through :meth:`DataSource.load`. Every figure comes from a
dataset field; the only arithmetic is the display Total row of the holdings
block and the sign of withdrawal amounts.
"""

from __future__ import annotations

import argparse
import calendar
import json
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Any

from .checks import CheckResult, run_checks
from .schema import PERIOD_FIELD, parse_date, parse_decimal, parse_period
from .source import DatasetError, DataSource, FixtureSource

TITLE = "Returns & Transactions Report"
CURRENCY = "THB"
DISCLAIMER = (
    "This report is prepared for the named account holder only. It is not an "
    "offer, solicitation, or investment advice. Past performance does not "
    "indicate future results."
)
CASH = "CASH"
TOTAL = "Total"
OUTPUT_FILES = ("report.md", "report.json", "narrative.md")
CHECKS_FILE = "checks.json"

_CENT = Decimal("0.01")
_MONTHS = (
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
)

Report = dict[str, Any]


def _quantize(value: Decimal) -> Decimal:
    q = value.quantize(_CENT, rounding=ROUND_HALF_UP)
    return abs(q) if q == 0 else q


def fmt_money(value: Decimal) -> str:
    """Format money: 2 decimals, thousands separators, ``-0.00`` as ``0.00``."""
    return f"{_quantize(value):,.2f}"


def fmt_pct(value: Decimal) -> str:
    """Format a percentage value such as ``3.83`` as ``3.83%``."""
    return f"{_quantize(value):.2f}%"


def fmt_int(value: int) -> str:
    """Format an integer with thousands separators."""
    return f"{value:,}"


def fmt_long_date(day: date) -> str:
    """Format a date as ``DD Mon YYYY`` with English month names."""
    return f"{day.day:02d} {_MONTHS[day.month - 1]} {day.year:04d}"


def parse_amount(text: str) -> Decimal | None:
    """Parse a formatted money or percent string back to a ``Decimal``."""
    return parse_decimal(text.replace(",", "").removesuffix("%"))


@dataclass(frozen=True)
class Holding:
    """One holdings_daily row at the as-of date."""

    instrument: str
    volume: int
    avg_cost: Decimal
    cost_value: Decimal
    market_price: Decimal
    market_value: Decimal
    unrealized_pl: Decimal


@dataclass(frozen=True)
class Trade:
    """One transactions row in the period."""

    day: date
    instrument: str
    side: str
    qty: int
    price: Decimal
    fee: Decimal
    tax: Decimal
    amount: Decimal
    realized_pl: Decimal | None


@dataclass(frozen=True)
class CashFlow:
    """One cash_flow row in the period."""

    day: date
    flow_type: str
    amount: Decimal


@dataclass(frozen=True)
class ReportInputs:
    """Parsed dataset values for one account, opening date and as-of date."""

    account: str
    client: str
    strategy: str
    inception: date
    opening: date
    as_of: date
    period_start: date
    period_end: date
    opening_nav: Decimal
    nav: Decimal
    cash: Decimal
    securities_value: Decimal
    capital_gain: Decimal
    dividend: Decimal
    unrealized_change: Decimal
    total_pl: Decimal
    return_pct: Decimal
    holdings: tuple[Holding, ...]
    trades: tuple[Trade, ...]
    cash_flows: tuple[CashFlow, ...]


class _Reader:
    """Parses raw string fields and records problems instead of raising."""

    def __init__(self) -> None:
        self.problems: list[str] = []

    def text(self, row: dict[str, str], field: str, where: str) -> str:
        value = row.get(field, "")
        if value == "":
            self.problems.append(f"{where}: {field} is missing")
        return value

    def decimal(self, row: dict[str, str], field: str, where: str) -> Decimal:
        value = parse_decimal(row.get(field, ""))
        if value is None:
            self.problems.append(f"{where}: {field} is missing or invalid")
            return Decimal(0)
        return value

    def optional_decimal(
        self, row: dict[str, str], field: str, where: str
    ) -> Decimal | None:
        if row.get(field, "") == "":
            return None
        return self.decimal(row, field, where)

    def integer(self, row: dict[str, str], field: str, where: str) -> int:
        value = parse_decimal(row.get(field, ""))
        if value is None or value != value.to_integral_value():
            self.problems.append(f"{where}: {field} is missing or invalid")
            return 0
        return int(value)

    def day(self, row: dict[str, str], field: str, where: str) -> date:
        value = parse_date(row.get(field, ""))
        if value is None:
            self.problems.append(f"{where}: {field} is missing or invalid")
            return date.min
        return value

    def single(self, rows: list[dict[str, str]], what: str) -> dict[str, str] | None:
        if len(rows) != 1:
            self.problems.append(f"{what}: expected 1 row, found {len(rows)}")
            return None
        return rows[0]


def _rows_on(rows: list[dict[str, str]], day: date) -> list[dict[str, str]]:
    return [r for r in rows if parse_date(r.get("date", "")) == day]


def load_inputs(
    source: DataSource, account: str, opening: date, as_of: date
) -> tuple[ReportInputs | None, list[str]]:
    """Load and parse the report inputs for one account.

    The period is the calendar month of ``as_of``. Transactions and cash flows
    are the rows from the first day of that month up to ``as_of``.

    Args:
        source: Data source to read through.
        account: Account number, for example ``"<account>"``.
        opening: Opening date of the period.
        as_of: As-of date of the report.

    Returns:
        The parsed inputs and an empty list, or ``None`` and the problems found
        (missing, duplicate or invalid mapped values). Nothing is derived to
        fill a missing value.
    """
    reader = _Reader()
    accounts = [account]
    try:
        data = {
            name: source.load(name, as_of, accounts)
            for name in (
                "account_info",
                "nav_daily",
                "holdings_daily",
                "transactions",
                "cash_flow",
                "performance",
            )
        }
    except DatasetError as exc:
        return None, [str(exc)]

    period_start = as_of.replace(day=1)
    period_end = as_of.replace(day=calendar.monthrange(as_of.year, as_of.month)[1])
    month = (as_of.year, as_of.month)

    info = reader.single(data["account_info"], "account_info")
    nav_open = reader.single(
        _rows_on(data["nav_daily"], opening), f"nav_daily at {opening.isoformat()}"
    )
    nav_close = reader.single(
        _rows_on(data["nav_daily"], as_of), f"nav_daily at {as_of.isoformat()}"
    )
    perf = reader.single(
        [r for r in data["performance"] if parse_period(r[PERIOD_FIELD]) == month],
        f"performance for {month[0]:04d}-{month[1]:02d}",
    )

    holdings: list[Holding] = []
    seen: set[str] = set()
    holding_rows = _rows_on(data["holdings_daily"], as_of)
    if not holding_rows:
        reader.problems.append(f"holdings_daily at {as_of.isoformat()}: no rows")
    for index, row in enumerate(holding_rows, start=1):
        where = f"holdings_daily row {index}"
        instrument = reader.text(row, "instrument", where)
        if instrument in seen:
            reader.problems.append(f"{where}: duplicate instrument {instrument}")
        seen.add(instrument)
        holdings.append(
            Holding(
                instrument=instrument,
                volume=reader.integer(row, "volume", where),
                avg_cost=reader.decimal(row, "avg_cost", where),
                cost_value=reader.decimal(row, "cost_value", where),
                market_price=reader.decimal(row, "market_price", where),
                market_value=reader.decimal(row, "market_value", where),
                unrealized_pl=reader.decimal(row, "unrealized_pl", where),
            )
        )

    trades: list[Trade] = []
    for index, row in enumerate(data["transactions"], start=1):
        where = f"transactions row {index}"
        day = reader.day(row, "date", where)
        if day < period_start:
            continue
        side = reader.text(row, "side", where)
        realized = reader.optional_decimal(row, "realized_pl", where)
        if side == "SELL" and realized is None:
            reader.problems.append(f"{where}: realized_pl is missing")
        trades.append(
            Trade(
                day=day,
                instrument=reader.text(row, "instrument", where),
                side=side,
                qty=reader.integer(row, "qty", where),
                price=reader.decimal(row, "price", where),
                fee=reader.decimal(row, "fee", where),
                tax=reader.decimal(row, "tax", where),
                amount=reader.decimal(row, "amount", where),
                realized_pl=realized,
            )
        )

    flows: list[CashFlow] = []
    for index, row in enumerate(data["cash_flow"], start=1):
        where = f"cash_flow row {index}"
        day = reader.day(row, "date", where)
        if day < period_start:
            continue
        flows.append(
            CashFlow(
                day=day,
                flow_type=reader.text(row, "flow_type", where),
                amount=reader.decimal(row, "amount", where),
            )
        )

    if info is None or nav_open is None or nav_close is None or perf is None:
        return None, reader.problems
    inputs = ReportInputs(
        account=reader.text(info, "account_no", "account_info"),
        client=reader.text(info, "client_name", "account_info"),
        strategy=reader.text(info, "strategy", "account_info"),
        inception=reader.day(info, "inception_date", "account_info"),
        opening=opening,
        as_of=as_of,
        period_start=period_start,
        period_end=period_end,
        opening_nav=reader.decimal(nav_open, "nav", "nav_daily opening"),
        nav=reader.decimal(nav_close, "nav", "nav_daily as-of"),
        cash=reader.decimal(nav_close, "cash", "nav_daily as-of"),
        securities_value=reader.decimal(nav_close, "market_value", "nav_daily as-of"),
        capital_gain=reader.decimal(perf, "capital_gain", "performance"),
        dividend=reader.decimal(perf, "dividend", "performance"),
        unrealized_change=reader.decimal(perf, "unrealized_change", "performance"),
        total_pl=reader.decimal(perf, "total_pl", "performance"),
        return_pct=reader.decimal(perf, "return_pct", "performance"),
        holdings=tuple(holdings),
        trades=tuple(trades),
        cash_flows=tuple(flows),
    )
    if reader.problems:
        return None, reader.problems
    return inputs, []


def _holding_row(
    instrument: str,
    volume: str | None,
    avg_cost: str | None,
    cost_value: str | None,
    market_price: str | None,
    market_value: str | None,
    unrealized_pl: str | None,
) -> dict[str, str | None]:
    return {
        "instrument": instrument,
        "volume": volume,
        "avg_cost": avg_cost,
        "cost_value": cost_value,
        "market_price": market_price,
        "market_value": market_value,
        "unrealized_pl": unrealized_pl,
    }


def _transaction_rows(inputs: ReportInputs) -> list[dict[str, str | None]]:
    keyed: list[tuple[date, dict[str, str | None]]] = []
    for t in inputs.trades:
        realized = t.realized_pl if t.side == "SELL" else None
        keyed.append(
            (
                t.day,
                {
                    "date": t.day.isoformat(),
                    "instrument": t.instrument,
                    "side": t.side,
                    "qty": fmt_int(t.qty),
                    "price": fmt_money(t.price),
                    "fee": fmt_money(t.fee),
                    "tax": fmt_money(t.tax),
                    "amount": fmt_money(t.amount),
                    "realized_pl": None if realized is None else fmt_money(realized),
                },
            )
        )
    for f in inputs.cash_flows:
        amount = -f.amount if f.flow_type == "WITHDRAWAL" else f.amount
        keyed.append(
            (
                f.day,
                {
                    "date": f.day.isoformat(),
                    "instrument": CASH,
                    "side": f.flow_type,
                    "qty": None,
                    "price": None,
                    "fee": None,
                    "tax": None,
                    "amount": fmt_money(amount),
                    "realized_pl": None,
                },
            )
        )
    # Stable sort: equal dates keep transactions before cash flows, file order.
    keyed.sort(key=lambda item: item[0], reverse=True)
    return [row for _, row in keyed]


def build_report(inputs: ReportInputs, report_id: str) -> Report:
    """Map the inputs into the report blocks.

    Values are formatted strings; values that do not apply are ``None``. The
    narrative block is left empty for :func:`main` to fill in.

    Args:
        inputs: Parsed inputs from :func:`load_inputs`.
        report_id: Report ID shown in the header.

    Returns:
        A dict with the keys ``header``, ``kpi_summary``, ``holdings``,
        ``transactions``, ``narrative`` and ``disclaimer``, in that order.
    """
    holdings = sorted(inputs.holdings, key=lambda h: h.instrument)
    rows = [
        _holding_row(
            h.instrument,
            fmt_int(h.volume),
            fmt_money(h.avg_cost),
            fmt_money(h.cost_value),
            fmt_money(h.market_price),
            fmt_money(h.market_value),
            fmt_money(h.unrealized_pl),
        )
        for h in holdings
    ]
    rows.append(
        _holding_row(CASH, None, None, None, None, fmt_money(inputs.cash), None)
    )
    # Display-only Total row; B1 and B2 check it against nav_daily.
    rows.append(
        _holding_row(
            TOTAL,
            None,
            None,
            fmt_money(sum((h.cost_value for h in holdings), Decimal(0))),
            None,
            fmt_money(
                sum((h.market_value for h in holdings), Decimal(0)) + inputs.cash
            ),
            fmt_money(sum((h.unrealized_pl for h in holdings), Decimal(0))),
        )
    )
    return {
        "header": {
            "title": TITLE,
            "client": inputs.client,
            "account": inputs.account,
            "strategy": inputs.strategy,
            "inception": fmt_long_date(inputs.inception),
            "period": f"{inputs.as_of.year:04d}-{inputs.as_of.month:02d}",
            "period_start": inputs.period_start.isoformat(),
            "period_end": inputs.period_end.isoformat(),
            "opening_date": inputs.opening.isoformat(),
            "as_of": inputs.as_of.isoformat(),
            "currency": CURRENCY,
            "report_id": report_id,
        },
        "kpi_summary": {
            "net_asset_value": fmt_money(inputs.nav),
            "cash": fmt_money(inputs.cash),
            "realized_capital_gain": fmt_money(inputs.capital_gain),
            "dividends_net": fmt_money(inputs.dividend),
            "change_in_unrealized_pl": fmt_money(inputs.unrealized_change),
            "total_pl": fmt_money(inputs.total_pl),
            "period_return": fmt_pct(inputs.return_pct),
        },
        "holdings": rows,
        "transactions": _transaction_rows(inputs),
        "narrative": [],
        "disclaimer": DISCLAIMER,
    }


_HEADER_LABELS = (
    ("Client", "client"),
    ("Account", "account"),
    ("Strategy", "strategy"),
    ("Inception", "inception"),
    ("Period", "period"),
    ("Period start", "period_start"),
    ("Period end", "period_end"),
    ("Opening date", "opening_date"),
    ("As-of date", "as_of"),
    ("Currency", "currency"),
    ("Report ID", "report_id"),
)
_KPI_LABELS = (
    ("Net asset value", "net_asset_value"),
    ("Cash", "cash"),
    ("Realized capital gain", "realized_capital_gain"),
    ("Dividends (net)", "dividends_net"),
    ("Change in unrealized P/L", "change_in_unrealized_pl"),
    ("Total P/L", "total_pl"),
    ("Period return (simple, on opening NAV)", "period_return"),
)
_HOLDING_COLUMNS = (
    ("Instrument", "instrument", False),
    ("Volume", "volume", True),
    ("Avg cost", "avg_cost", True),
    ("Cost value", "cost_value", True),
    ("Market price", "market_price", True),
    ("Market value", "market_value", True),
    ("Unrealized P/L", "unrealized_pl", True),
)
_TRANSACTION_COLUMNS = (
    ("Date", "date", False),
    ("Instrument", "instrument", False),
    ("Side", "side", False),
    ("Qty", "qty", True),
    ("Price", "price", True),
    ("Fee", "fee", True),
    ("Tax", "tax", True),
    ("Amount", "amount", True),
    ("Realized P/L", "realized_pl", True),
)


def _cell(value: object) -> str:
    return "" if value is None else str(value).replace("|", "\\|")


def _table(
    columns: Sequence[tuple[str, str, bool]], rows: Sequence[dict[str, Any]]
) -> list[str]:
    lines = [
        "| " + " | ".join(label for label, _, _ in columns) + " |",
        "| " + " | ".join("---:" if num else "---" for _, _, num in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_cell(row[key]) for _, key, _ in columns) + " |")
    return lines


def render_markdown(report: Report) -> str:
    """Render the report as Markdown with one ``##`` section per block."""
    header = report["header"]
    kpi = report["kpi_summary"]
    lines = [f"## {header['title']}", ""]
    lines += _table(
        (("Field", "label", False), ("Value", "value", False)),
        [{"label": label, "value": header[key]} for label, key in _HEADER_LABELS],
    )
    lines += ["", "## KPI summary", ""]
    lines += _table(
        (("KPI", "label", False), (f"Value ({header['currency']})", "value", True)),
        [{"label": label, "value": kpi[key]} for label, key in _KPI_LABELS],
    )
    lines += ["", "## Holdings", ""]
    lines += _table(_HOLDING_COLUMNS, report["holdings"])
    lines += ["", "## Transactions", ""]
    if report["transactions"]:
        lines += _table(_TRANSACTION_COLUMNS, report["transactions"])
    else:
        lines.append("No transactions in the period.")
    lines += ["", "## Narrative", ""]
    for paragraph in report["narrative"]:
        lines += [paragraph, ""]
    lines += ["## Disclaimer", "", report["disclaimer"]]
    return "\n".join(lines) + "\n"


def render_narrative(paragraphs: Sequence[str]) -> str:
    """Join narrative paragraphs with blank lines, ending with a newline."""
    return "\n\n".join(paragraphs) + "\n"


def _iso_date(value: str) -> date:
    parsed = parse_date(value)
    if parsed is None:
        raise argparse.ArgumentTypeError(f"not an ISO date (YYYY-MM-DD): {value!r}")
    return parsed


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m quant_software_factory.reporting.returns_transactions",
        description="Build the Returns & Transactions report and its checks.",
    )
    parser.add_argument("root", type=Path, help="directory holding <dataset>.csv")
    parser.add_argument("out", type=Path, help="output folder; its name is the ID")
    parser.add_argument("--account", required=True)
    parser.add_argument("--opening", required=True, type=_iso_date)
    parser.add_argument("--as-of", dest="as_of", required=True, type=_iso_date)
    return parser


def _write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def main(argv: Sequence[str] | None = None) -> int:
    """Run all checks, build the report and write the output files.

    Args:
        argv: Command line arguments; defaults to ``sys.argv[1:]``.

    Returns:
        0 when every check passes, 1 when any check fails.
    """
    # Imported here: both modules import formatting helpers from this module.
    from .narrative import generate_narrative
    from .report_checks import (
        B0_NAME,
        LAYER_B_CHECK_NAMES,
        mapped_values_check,
        narrative_checks,
        not_run_results,
        number_checks,
    )

    args = _parser().parse_args(argv)
    out: Path = args.out
    source = FixtureSource(args.root)
    layer_a = run_checks(source, args.account, args.opening, args.as_of)
    report: Report | None = None
    layer_b: list[CheckResult]
    if not all(r.passed for r in layer_a):
        layer_b = not_run_results(LAYER_B_CHECK_NAMES, "not run: Layer A failed")
    else:
        inputs, problems = load_inputs(source, args.account, args.opening, args.as_of)
        b0 = mapped_values_check(problems)
        if inputs is None or not b0.passed:
            rest = [n for n in LAYER_B_CHECK_NAMES if n != B0_NAME]
            layer_b = [b0, *not_run_results(rest, f"not run: {B0_NAME} failed")]
        else:
            report = build_report(inputs, out.resolve().name)
            paragraphs = generate_narrative(report)
            report["narrative"] = paragraphs
            layer_b = [
                b0,
                *number_checks(inputs, report),
                *narrative_checks(paragraphs, report),
            ]

    results = sorted([*layer_a, *layer_b], key=lambda r: r.name)
    out.mkdir(parents=True, exist_ok=True)
    _write(
        out / CHECKS_FILE, json.dumps([r.to_dict() for r in results], indent=2) + "\n"
    )
    failed = sum(not r.passed for r in results)
    if failed == 0 and report is not None:
        _write(out / "report.json", json.dumps(report, indent=2) + "\n")
        _write(out / "report.md", render_markdown(report))
        _write(out / "narrative.md", render_narrative(report["narrative"]))
    else:
        for name in OUTPUT_FILES:
            (out / name).unlink(missing_ok=True)
    print(f"{len(results)} checks, {failed} failed")
    return 0 if failed == 0 and report is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
