"""Grid Trade Performance report figures built from precomputed datasets.

Usage::

    python -m quant_software_factory.reporting.grid_performance <root> <out> \\
        --account <account> --as-of YYYY-MM-DD --generated-at <timestamp>

Runs the Layer A data checks first, then loads the mapped values, computes every
figure the report prints and runs the Layer B checks (G0-G9). When every check
passes it writes ``checks.json``, ``report.json`` and ``report.pdf`` (drawn by
:mod:`.grid_pdf` from the report) to ``<out>`` and exits 0. When any check fails
it writes only ``checks.json``, removes a stale ``report.json`` and
``report.pdf`` and exits 1. The report ID is the name of ``<out>``.

All data is read through :meth:`DataSource.load`. Figures are computed with
``Decimal`` and rounded (ROUND_HALF_UP) only when formatted for display; every
value in ``report.json`` is a string formatted as the report prints it.
"""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_FLOOR, ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Any

from .checks import CheckResult, run_grid_checks
from .grid_pdf import render_pdf
from .returns_transactions import fmt_long_date
from .schema import GRID_DATASETS, parse_date, parse_decimal
from .source import DatasetError, DataSource, FixtureSource

CASH = "CASH"
NONE = "-"
LOT = 100
TRANSACTION_ROWS = 25
INSTRUMENT_TRANSACTION_ROWS = 7
REPORT_FILE = "report.json"
PDF_FILE = "report.pdf"
CHECKS_FILE = "checks.json"

SIDE_LABELS: dict[str, str] = {
    "BUY": "Buy",
    "SELL": "Sell",
    "DIVIDEND": "Dividend",
    "PORT_ADJUSTED": "Port Adjusted",
    "GAIN_ADJUSTMENT": "Gain Adjustment",
}
ADJUSTMENT_SIDES = ("PORT_ADJUSTED", "GAIN_ADJUSTMENT")

# English month names, independent of the process locale.
_MONTH_NAMES = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)
_GENERATED_AT_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
_HUNDRED = Decimal(100)
_ONE = Decimal(1)

Report = dict[str, Any]


# --- Formatting -------------------------------------------------------------


def _quantize(value: Decimal, places: int) -> Decimal:
    q = value.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)
    return abs(q) if q == 0 else q


def fmt_whole(value: Decimal) -> str:
    """Format a whole amount with thousands separators: ``28,360,975``."""
    return f"{_quantize(value, 0):,.0f}"


def fmt_money(value: Decimal) -> str:
    """Format money or a price: 2 decimals with thousands separators."""
    return f"{_quantize(value, 2):,.2f}"


def fmt_units(value: int) -> str:
    """Format a unit count as an integer with thousands separators."""
    return f"{value:,}"


def fmt_pct(value: Decimal, places: int) -> str:
    """Format a percentage value with ``places`` decimals and a ``%`` sign."""
    return f"{_quantize(value, places):.{places}f}%"


def fmt_plain(value: Decimal, places: int) -> str:
    """Format a plain decimal string (no separators) for drawing charts."""
    return f"{_quantize(value, places):.{places}f}"


def fmt_as_of_label(day: date) -> str:
    """Format the as-of label, for example ``As of 06 November 2026``."""
    return f"As of {day.day:02d} {_MONTH_NAMES[day.month - 1]} {day.year:04d}"


def parse_display(text: str) -> Decimal | None:
    """Parse a formatted number such as ``-1,234.50`` or ``0.9%``."""
    return parse_decimal(text.replace(",", "").removesuffix("%"))


# --- Inputs -----------------------------------------------------------------


@dataclass(frozen=True)
class GridSetup:
    """One grid_setup row."""

    instrument: str
    display_order: int
    initial_units: int
    initial_cost: Decimal
    commission_rate: Decimal
    expected_trade_units: int
    expected_trade_return_pct: Decimal


@dataclass(frozen=True)
class NavRow:
    """One nav_daily row."""

    nav: Decimal
    cash: Decimal
    market_value: Decimal


@dataclass(frozen=True)
class Holding:
    """One holdings_daily row."""

    volume: int
    avg_cost: Decimal
    cost_value: Decimal
    market_price: Decimal
    market_value: Decimal
    unrealized_pl: Decimal


@dataclass(frozen=True)
class Trade:
    """One transactions row up to the as-of date."""

    day: date
    instrument: str
    side: str
    qty: int
    price: Decimal
    amount: Decimal


@dataclass(frozen=True)
class GridInputs:
    """Parsed dataset values for one account and as-of date.

    Attributes:
        dates: History dates: the distinct ``nav_daily`` dates up to the as-of
            date, ascending.
        nav: ``nav_daily`` row per history date.
        setups: ``grid_setup`` rows in display order.
        holdings: ``holdings_daily`` row per ``(instrument, date)``.
        cash: ``grid_cash.cash`` per ``(instrument, date)``.
        trades: ``transactions`` rows in file order.
    """

    account: str
    client: str
    strategy: str
    inception: date
    as_of: date
    generated_at: str
    request_id: str
    dates: tuple[date, ...]
    nav: dict[date, NavRow]
    setups: tuple[GridSetup, ...]
    holdings: dict[tuple[str, date], Holding]
    cash: dict[tuple[str, date], Decimal]
    trades: tuple[Trade, ...]


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

    def integer(self, row: dict[str, str], field: str, where: str) -> int:
        value = parse_decimal(row.get(field, ""))
        if value is None or value != value.to_integral_value():
            self.problems.append(f"{where}: {field} is missing or invalid")
            return 0
        return int(value)

    def day(self, row: dict[str, str], field: str, where: str) -> date | None:
        value = parse_date(row.get(field, ""))
        if value is None:
            self.problems.append(f"{where}: {field} is missing or invalid")
        return value

    def positive(self, value: Decimal | int, what: str) -> None:
        if value <= 0:
            self.problems.append(f"{what} is not positive")


def request_id(account: str, as_of: date) -> str:
    """Return the request ID ``req_<account>_<as-of>``."""
    return f"req_{account}_{as_of.isoformat()}"


def _load_setups(reader: _Reader, rows: list[dict[str, str]]) -> list[GridSetup]:
    setups: list[GridSetup] = []
    seen: set[str] = set()
    if not rows:
        reader.problems.append("grid_setup: no rows")
    for index, row in enumerate(rows, start=1):
        where = f"grid_setup row {index}"
        instrument = reader.text(row, "instrument", where)
        if instrument in seen:
            reader.problems.append(f"{where}: duplicate instrument {instrument}")
        seen.add(instrument)
        setup = GridSetup(
            instrument=instrument,
            display_order=reader.integer(row, "display_order", where),
            initial_units=reader.integer(row, "initial_units", where),
            initial_cost=reader.decimal(row, "initial_cost", where),
            commission_rate=reader.decimal(row, "commission_rate", where),
            expected_trade_units=reader.integer(row, "expected_trade_units", where),
            expected_trade_return_pct=reader.decimal(
                row, "expected_trade_return_pct", where
            ),
        )
        reader.positive(setup.initial_units, f"{where}: initial_units")
        reader.positive(setup.initial_cost, f"{where}: initial_cost")
        if setup.commission_rate < 0:
            reader.problems.append(f"{where}: commission_rate is negative")
        setups.append(setup)
    return sorted(setups, key=lambda s: (s.display_order, s.instrument))


def _instrument_rows(
    reader: _Reader,
    dataset: str,
    rows: list[dict[str, str]],
    instruments: set[str],
    dates: set[date],
) -> list[tuple[tuple[str, date], dict[str, str], str]]:
    """Validate the keys of a per-instrument, per-date dataset."""
    keyed: list[tuple[tuple[str, date], dict[str, str], str]] = []
    seen: set[tuple[str, date]] = set()
    for index, row in enumerate(rows, start=1):
        where = f"{dataset} row {index}"
        day = reader.day(row, "date", where)
        instrument = reader.text(row, "instrument", where)
        if day is None or instrument == "":
            continue
        if instrument not in instruments:
            reader.problems.append(
                f"{where}: instrument {instrument} not in grid_setup"
            )
            continue
        if day not in dates:
            reader.problems.append(f"{where}: date {day.isoformat()} not in nav_daily")
            continue
        key = (instrument, day)
        if key in seen:
            reader.problems.append(
                f"{where}: duplicate row for {instrument} at {day.isoformat()}"
            )
            continue
        seen.add(key)
        keyed.append((key, row, where))
    for instrument in sorted(instruments):
        for day in sorted(dates):
            if (instrument, day) not in seen:
                reader.problems.append(
                    f"{dataset}: no row for {instrument} at {day.isoformat()}"
                )
    return keyed


def load_inputs(
    source: DataSource, account: str, as_of: date, generated_at: str
) -> tuple[GridInputs | None, list[str]]:
    """Load and parse the report inputs for one account.

    Args:
        source: Data source to read through.
        account: Account number.
        as_of: As-of date of the report.
        generated_at: Generation timestamp shown in the header.

    Returns:
        The parsed inputs and an empty list, or ``None`` and the problems found
        (missing, duplicate, invalid or non-positive mapped values). Never
        raises for malformed data.
    """
    reader = _Reader()
    accounts = [account]
    try:
        data = {name: source.load(name, as_of, accounts) for name in GRID_DATASETS}
    except DatasetError as exc:
        return None, [str(exc)]

    info_rows = data["account_info"]
    if len(info_rows) != 1:
        reader.problems.append(f"account_info: expected 1 row, found {len(info_rows)}")
    info = info_rows[0] if len(info_rows) == 1 else {}
    client = reader.text(info, "client_name", "account_info")
    strategy = reader.text(info, "strategy", "account_info")
    account_no = reader.text(info, "account_no", "account_info")
    inception = reader.day(info, "inception_date", "account_info")

    nav: dict[date, NavRow] = {}
    for index, row in enumerate(data["nav_daily"], start=1):
        where = f"nav_daily row {index}"
        day = reader.day(row, "date", where)
        if day is None:
            continue
        if day in nav:
            reader.problems.append(f"{where}: duplicate date {day.isoformat()}")
            continue
        nav[day] = NavRow(
            nav=reader.decimal(row, "nav", where),
            cash=reader.decimal(row, "cash", where),
            market_value=reader.decimal(row, "market_value", where),
        )
    if as_of not in nav:
        reader.problems.append(f"nav_daily at {as_of.isoformat()}: no row")
    else:
        reader.positive(nav[as_of].nav, f"nav_daily at {as_of.isoformat()}: nav")
    dates = set(nav)

    setups = _load_setups(reader, data["grid_setup"])
    instruments = {s.instrument for s in setups if s.instrument}

    holdings: dict[tuple[str, date], Holding] = {}
    for key, row, where in _instrument_rows(
        reader, "holdings_daily", data["holdings_daily"], instruments, dates
    ):
        holding = Holding(
            volume=reader.integer(row, "volume", where),
            avg_cost=reader.decimal(row, "avg_cost", where),
            cost_value=reader.decimal(row, "cost_value", where),
            market_price=reader.decimal(row, "market_price", where),
            market_value=reader.decimal(row, "market_value", where),
            unrealized_pl=reader.decimal(row, "unrealized_pl", where),
        )
        reader.positive(holding.market_price, f"{where}: market_price")
        holdings[key] = holding

    cash: dict[tuple[str, date], Decimal] = {}
    for key, row, where in _instrument_rows(
        reader, "grid_cash", data["grid_cash"], instruments, dates
    ):
        cash[key] = reader.decimal(row, "cash", where)

    trades: list[Trade] = []
    for index, row in enumerate(data["transactions"], start=1):
        where = f"transactions row {index}"
        day = reader.day(row, "date", where)
        trade = Trade(
            day=day or date.min,
            instrument=reader.text(row, "instrument", where),
            side=reader.text(row, "side", where),
            qty=reader.integer(row, "qty", where),
            price=reader.decimal(row, "price", where),
            amount=reader.decimal(row, "amount", where),
        )
        if trade.side and trade.side not in SIDE_LABELS:
            reader.problems.append(f"{where}: side {trade.side} is unknown")
        trades.append(trade)

    if reader.problems or inception is None:
        return None, reader.problems
    return (
        GridInputs(
            account=account_no,
            client=client,
            strategy=strategy,
            inception=inception,
            as_of=as_of,
            generated_at=generated_at,
            request_id=request_id(account, as_of),
            dates=tuple(sorted(dates)),
            nav=nav,
            setups=tuple(setups),
            holdings=holdings,
            cash=cash,
            trades=tuple(trades),
        ),
        [],
    )


# --- Calculations -----------------------------------------------------------


def expected_volume(
    cash: Decimal, market_price: Decimal, commission_rate: Decimal
) -> int:
    """Units the sleeve cash buys at the price plus commission, in whole lots.

    ``cash / (market_price * (1 + commission_rate))`` rounded down to a
    multiple of ``LOT``.
    """
    units = cash / (market_price * (_ONE + commission_rate))
    lots = (units / LOT).to_integral_value(rounding=ROUND_FLOOR)
    return int(lots) * LOT


def change_pct(current: Decimal, initial: Decimal) -> Decimal:
    """Return ``(current / initial - 1) * 100``."""
    return (current / initial - _ONE) * _HUNDRED


def sleeve_cash(inputs: GridInputs, day: date) -> Decimal:
    """Sum of ``grid_cash.cash`` over the instruments on ``day``."""
    return sum((inputs.cash[(s.instrument, day)] for s in inputs.setups), Decimal(0))


@dataclass(frozen=True)
class InstrumentFigures:
    """Unrounded figures of one instrument at the as-of date."""

    setup: GridSetup
    holding: Holding
    cash: Decimal
    expected_volume: int
    nav_volume: int
    gain_volume: int
    current_units_change_pct: Decimal
    cost_change_pct: Decimal
    initial_cost_value: Decimal
    weight: Decimal


def instrument_figures(inputs: GridInputs) -> list[InstrumentFigures]:
    """Compute the as-of figures of every instrument, in display order."""
    nav = inputs.nav[inputs.as_of].nav
    figures: list[InstrumentFigures] = []
    for setup in inputs.setups:
        key = (setup.instrument, inputs.as_of)
        holding = inputs.holdings[key]
        cash = inputs.cash[key]
        expected = expected_volume(cash, holding.market_price, setup.commission_rate)
        nav_volume = holding.volume + expected
        figures.append(
            InstrumentFigures(
                setup=setup,
                holding=holding,
                cash=cash,
                expected_volume=expected,
                nav_volume=nav_volume,
                gain_volume=nav_volume - setup.initial_units,
                current_units_change_pct=change_pct(
                    Decimal(holding.volume), Decimal(setup.initial_units)
                ),
                cost_change_pct=change_pct(holding.avg_cost, setup.initial_cost),
                initial_cost_value=setup.initial_units * setup.initial_cost,
                weight=holding.market_value / nav * _HUNDRED,
            )
        )
    return figures


def weights(inputs: GridInputs) -> list[tuple[str, Decimal]]:
    """Unrounded weight % of each instrument and CASH, in display order."""
    nav = inputs.nav[inputs.as_of].nav
    rows = [(f.setup.instrument, f.weight) for f in instrument_figures(inputs)]
    rows.append((CASH, sleeve_cash(inputs, inputs.as_of) / nav * _HUNDRED))
    return rows


def nav_volume_pct(inputs: GridInputs, setup: GridSetup, day: date) -> Decimal:
    """NAV volume % on ``day`` from that date's holdings and sleeve cash."""
    holding = inputs.holdings[(setup.instrument, day)]
    expected = expected_volume(
        inputs.cash[(setup.instrument, day)],
        holding.market_price,
        setup.commission_rate,
    )
    return change_pct(Decimal(holding.volume + expected), Decimal(setup.initial_units))


def dividend_rows(inputs: GridInputs) -> list[Trade]:
    """DIVIDEND rows dated in the as-of year up to the as-of date."""
    return [
        t
        for t in inputs.trades
        if t.side == "DIVIDEND"
        and t.day.year == inputs.as_of.year
        and t.day <= inputs.as_of
    ]


def ordered_trades(trades: Iterable[Trade]) -> list[Trade]:
    """Newest first; on one date PORT_ADJUSTED, GAIN_ADJUSTMENT, then by ticker."""

    def rank(trade: Trade) -> int:
        if trade.side in ADJUSTMENT_SIDES:
            return ADJUSTMENT_SIDES.index(trade.side)
        return len(ADJUSTMENT_SIDES)

    by_side = sorted(trades, key=lambda t: (rank(t), t.instrument))
    return sorted(by_side, key=lambda t: t.day, reverse=True)


def transaction_row(trade: Trade, with_ticker: bool = True) -> dict[str, str]:
    """Format one transactions row as the report prints it."""
    signed = trade.side in ADJUSTMENT_SIDES
    row = {"trade_date": trade.day.isoformat()}
    if with_ticker:
        row["ticker"] = trade.instrument
    row.update(
        side=SIDE_LABELS.get(trade.side, trade.side),
        qty=fmt_units(trade.qty if signed else abs(trade.qty)),
        price=fmt_money(trade.price),
        amount=fmt_money(trade.amount if signed else abs(trade.amount)),
    )
    return row


# --- Report -----------------------------------------------------------------


def _holding_row(
    ticker: str,
    volume: str,
    cost_value: str,
    avg_cost: str,
    market_price: str,
    market_value: str,
) -> dict[str, str]:
    return {
        "ticker": ticker,
        "volume": volume,
        "cost_value": cost_value,
        "avg_cost": avg_cost,
        "market_price": market_price,
        "market_value": market_value,
    }


def _instrument(
    inputs: GridInputs, f: InstrumentFigures, trades: list[Trade]
) -> dict[str, Any]:
    setup = f.setup
    own = [t for t in trades if t.instrument == setup.instrument]
    history = [inputs.holdings[(setup.instrument, d)] for d in inputs.dates]
    return {
        "ticker": setup.instrument,
        "cards": {
            "initial_units": fmt_units(setup.initial_units),
            "current_units": fmt_units(f.holding.volume),
            "current_units_change_pct": fmt_pct(f.current_units_change_pct, 2),
            "expected_trade_units": fmt_units(setup.expected_trade_units),
            "expected_trade_return_pct": fmt_pct(setup.expected_trade_return_pct, 1),
            "cash": fmt_whole(f.cash),
            "nav_volume": fmt_units(f.nav_volume),
            "gain_volume": fmt_units(f.gain_volume),
            "initial_cost": fmt_money(setup.initial_cost),
            "current_cost": fmt_money(f.holding.avg_cost),
            "cost_change_pct": fmt_pct(f.cost_change_pct, 2),
        },
        "initial_cost_value": fmt_whole(f.initial_cost_value),
        "chart": {
            "dates": [d.isoformat() for d in inputs.dates],
            "avg_cost": [fmt_plain(h.avg_cost, 4) for h in history],
            "market_price": [fmt_plain(h.market_price, 2) for h in history],
            "nav_volume_pct": [
                fmt_plain(nav_volume_pct(inputs, setup, d), 4) for d in inputs.dates
            ],
        },
        "transactions": [
            transaction_row(t, with_ticker=False)
            for t in own[:INSTRUMENT_TRANSACTION_ROWS]
        ],
    }


def build_report(inputs: GridInputs) -> Report:
    """Compute and format every figure of the report.

    Args:
        inputs: Parsed inputs from :func:`load_inputs`.

    Returns:
        A dict with the keys ``header``, ``cards``, ``holdings``,
        ``holdings_total``, ``allocation``, ``summary``, ``transactions`` and
        ``instruments``, in that order. Every leaf value is a string.
    """
    as_of = inputs.as_of
    nav_row = inputs.nav[as_of]
    figures = instrument_figures(inputs)
    cash_total = sleeve_cash(inputs, as_of)
    dividend = sum((t.amount for t in dividend_rows(inputs)), Decimal(0))
    trades = ordered_trades(inputs.trades)

    holdings = [
        _holding_row(
            f.setup.instrument,
            fmt_units(f.holding.volume),
            fmt_money(f.holding.cost_value),
            fmt_money(f.holding.avg_cost),
            fmt_money(f.holding.market_price),
            fmt_money(f.holding.market_value),
        )
        for f in figures
    ]
    holdings.append(
        _holding_row(
            CASH,
            fmt_units(int(cash_total)),
            fmt_money(cash_total),
            fmt_money(_ONE),
            fmt_money(_ONE),
            fmt_money(cash_total),
        )
    )
    total_cost = sum((f.holding.cost_value for f in figures), cash_total)
    total_value = sum((f.holding.market_value for f in figures), cash_total)

    allocation = sorted(weights(inputs), key=lambda item: item[1], reverse=True)

    return {
        "header": {
            "client": inputs.client,
            "account": inputs.account,
            "strategy": inputs.strategy,
            "inception": fmt_long_date(inputs.inception),
            "as_of_label": fmt_as_of_label(as_of),
            "request_id": inputs.request_id,
            "generated_at": inputs.generated_at,
        },
        "cards": {
            "nav": fmt_whole(nav_row.nav),
            "cash_on_hand": fmt_whole(nav_row.cash),
            "dividend_ytd": fmt_whole(dividend),
            "cash_pct": fmt_pct(nav_row.cash / nav_row.nav * _HUNDRED, 1),
        },
        "holdings": holdings,
        "holdings_total": _holding_row(
            NONE, NONE, fmt_money(total_cost), NONE, NONE, fmt_money(total_value)
        ),
        "allocation": [
            {
                "label": label,
                "weight": fmt_pct(weight, 1),
                "weight_raw": fmt_plain(weight, 4),
            }
            for label, weight in allocation
        ],
        "summary": [
            {
                "ticker": f.setup.instrument,
                "avg_cost": fmt_money(f.holding.avg_cost),
                "market_price": fmt_money(f.holding.market_price),
                "initial_units": fmt_units(f.setup.initial_units),
                "current_units": fmt_units(f.holding.volume),
                "cash": fmt_money(f.cash),
                "expected_volume": fmt_units(f.expected_volume),
                "nav_volume": fmt_units(f.nav_volume),
                "gain_volume": fmt_units(f.gain_volume),
            }
            for f in figures
        ],
        "transactions": [transaction_row(t) for t in trades[:TRANSACTION_ROWS]],
        "instruments": [_instrument(inputs, f, trades) for f in figures],
    }


# --- Run and write ----------------------------------------------------------


@dataclass(frozen=True)
class GridRun:
    """Outcome of :func:`run_report`.

    Attributes:
        results: Layer A and Layer B check results, sorted by name.
        report: The built report, or ``None`` when Layer A or G0 failed.
    """

    results: list[CheckResult]
    report: Report | None


def run_report(
    source: DataSource, account: str, as_of: date, generated_at: str
) -> GridRun:
    """Run all checks and build the report.

    Args:
        source: Data source to read through.
        account: Account number.
        as_of: As-of date of the report.
        generated_at: Generation timestamp shown in the header.

    Returns:
        The sorted check results and the report (``None`` if not built).
    """
    # Imported here: grid_checks imports the calculations from this module.
    from .grid_checks import (
        G0_NAME,
        GRID_CHECK_NAMES,
        grid_checks,
        mapped_values_check,
        not_run_results,
    )

    layer_a = run_grid_checks(source, account, as_of)
    report: Report | None = None
    layer_b: list[CheckResult]
    if not all(r.passed for r in layer_a):
        layer_b = not_run_results(GRID_CHECK_NAMES, "not run: Layer A failed")
    else:
        inputs, problems = load_inputs(source, account, as_of, generated_at)
        g0 = mapped_values_check(problems)
        if inputs is None or not g0.passed:
            rest = [n for n in GRID_CHECK_NAMES if n != G0_NAME]
            layer_b = [g0, *not_run_results(rest, f"not run: {G0_NAME} failed")]
        else:
            report = build_report(inputs)
            layer_b = [g0, *grid_checks(inputs, report)]

    results = sorted([*layer_a, *layer_b], key=lambda r: r.name)
    return GridRun(results, report)


def _write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def write_outputs(
    out: Path, results: Sequence[CheckResult], report: Report | None
) -> None:
    """Write ``checks.json`` and, when every check passed, the report files.

    The report files are ``report.json`` and ``report.pdf``. The PDF is drawn
    before anything is written, so a drawing error leaves ``out`` untouched.
    When any check failed or no report was built, a stale ``report.json`` and
    ``report.pdf`` in ``out`` are removed.

    Args:
        out: Output folder; created if missing.
        results: Check results in the order they are written.
        report: The built report, or ``None``.
    """
    pdf: bytes | None = None
    if report is not None and all(r.passed for r in results):
        pdf = render_pdf(report)
    out.mkdir(parents=True, exist_ok=True)
    _write(
        out / CHECKS_FILE, json.dumps([r.to_dict() for r in results], indent=2) + "\n"
    )
    if pdf is not None:
        _write(out / REPORT_FILE, json.dumps(report, indent=2) + "\n")
        (out / PDF_FILE).write_bytes(pdf)
    else:
        (out / REPORT_FILE).unlink(missing_ok=True)
        (out / PDF_FILE).unlink(missing_ok=True)


def _iso_date(value: str) -> date:
    parsed = parse_date(value)
    if parsed is None:
        raise argparse.ArgumentTypeError(f"not an ISO date (YYYY-MM-DD): {value!r}")
    return parsed


def _timestamp(value: str) -> str:
    if not _GENERATED_AT_RE.fullmatch(value):
        raise argparse.ArgumentTypeError(
            f"not a UTC timestamp (YYYY-MM-DDTHH:MM:SSZ): {value!r}"
        )
    return value


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m quant_software_factory.reporting.grid_performance",
        description=(
            "Compute the Grid Trade Performance figures and their checks and "
            "draw the report PDF."
        ),
    )
    parser.add_argument("root", type=Path, help="directory holding <dataset>.csv")
    parser.add_argument("out", type=Path, help="output folder; its name is the ID")
    parser.add_argument("--account", required=True)
    parser.add_argument("--as-of", dest="as_of", required=True, type=_iso_date)
    parser.add_argument(
        "--generated-at", dest="generated_at", required=True, type=_timestamp
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run all checks, build the report and write the output files.

    Args:
        argv: Command line arguments; defaults to ``sys.argv[1:]``.

    Returns:
        0 when every check passes, 1 when any check fails.
    """
    args = _parser().parse_args(argv)
    run = run_report(
        FixtureSource(args.root), args.account, args.as_of, args.generated_at
    )
    write_outputs(args.out, run.results, run.report)
    failed = sum(not r.passed for r in run.results)
    print(f"{len(run.results)} checks, {failed} failed")
    return 0 if failed == 0 and run.report is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
