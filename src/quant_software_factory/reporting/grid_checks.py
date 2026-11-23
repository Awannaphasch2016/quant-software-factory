"""Layer B checks (G0-G9) of the Grid Trade Performance report.

G1, G2, G4 and G5 compare unrounded ``Decimal`` values from the datasets; G3,
G6, G7, G8 and G9 check the built report against the inputs or against itself.
All results use the ``CheckResult`` format of the Layer A checks with layer
``"B"``.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Sequence
from decimal import Decimal
from typing import Any

from .checks import CheckResult
from .grid_performance import (
    CASH,
    INSTRUMENT_TRANSACTION_ROWS,
    TRANSACTION_ROWS,
    GridInputs,
    Report,
    dividend_rows,
    fmt_whole,
    parse_display,
    sleeve_cash,
    transaction_row,
    weights,
)

LAYER = "B"
TOLERANCE = Decimal("0.01")
OK = "ok"

G0_NAME = "G0_mapped_values"

_EXPECTED: dict[str, str] = {
    G0_NAME: "every mapped value present exactly once and valid",
    "G1_nav": (
        "sum of holdings market_value + sum of grid_cash = nav_daily.nav and "
        "sum of grid_cash = nav_daily.cash on every date"
    ),
    "G2_holding_rows": (
        "cost_value = volume x avg_cost, market_value = volume x market_price, "
        "unrealized_pl = market_value - cost_value on every row"
    ),
    "G3_same_figure": (
        "NAV card = holdings_total market_value; cash card = CASH row; "
        "holdings, summary and instruments agree"
    ),
    "G4_units": "initial_units + BUY - SELL qty to each date = volume on that date",
    "G5_weights": "instrument and CASH weights sum to 100",
    "G6_nav_volume": (
        "nav_volume = current_units + expected_volume; "
        "gain_volume = nav_volume - initial_units"
    ),
    "G7_dividend_ytd": "dividend_ytd card = sum of DIVIDEND amount in the as-of year",
    "G8_transaction_rows": (
        f"{TRANSACTION_ROWS} rows overall and {INSTRUMENT_TRANSACTION_ROWS} per "
        "instrument (or all if fewer); every row exists in transactions"
    ),
    "G9_chart_series": "one point per history date, from inception to as-of",
}

GRID_CHECK_NAMES: tuple[str, ...] = tuple(sorted(_EXPECTED))

_SUMMARY_TO_CARDS = (
    ("initial_units", "initial_units"),
    ("current_units", "current_units"),
    ("nav_volume", "nav_volume"),
    ("gain_volume", "gain_volume"),
    ("avg_cost", "current_cost"),
)
_SUMMARY_TO_HOLDINGS = (
    ("current_units", "volume"),
    ("avg_cost", "avg_cost"),
    ("market_price", "market_price"),
)


def _result(name: str, passed: bool, actual: str) -> CheckResult:
    return CheckResult(name, LAYER, passed, _EXPECTED[name], actual)


def _errors_result(name: str, errors: Sequence[str], ok: str = OK) -> CheckResult:
    return _result(name, not errors, "; ".join(errors) if errors else ok)


def not_run_results(names: Iterable[str], reason: str) -> list[CheckResult]:
    """Return failed results for checks that could not run."""
    return [CheckResult(n, LAYER, False, _EXPECTED[n], reason) for n in names]


def mapped_values_check(problems: Sequence[str]) -> CheckResult:
    """G0: report the problems found while loading the mapped values."""
    return _errors_result(G0_NAME, problems)


def _close(a: Decimal, b: Decimal) -> bool:
    return abs(a - b) <= TOLERANCE


def nav_check(inputs: GridInputs) -> CheckResult:
    """G1: holdings plus sleeve cash equal NAV, sleeve cash equals NAV cash."""
    errors: list[str] = []
    for day in inputs.dates:
        row = inputs.nav[day]
        cash = sleeve_cash(inputs, day)
        value = sum(
            (inputs.holdings[(s.instrument, day)].market_value for s in inputs.setups),
            Decimal(0),
        )
        if not _close(value + cash, row.nav):
            errors.append(f"{day.isoformat()} nav: {value + cash} vs {row.nav}")
        if not _close(cash, row.cash):
            errors.append(f"{day.isoformat()} cash: {cash} vs {row.cash}")
    return _errors_result("G1_nav", errors, f"{len(inputs.dates)} dates ok")


def holding_rows_check(inputs: GridInputs) -> CheckResult:
    """G2: the identities of every holdings_daily row."""
    errors: list[str] = []
    for (instrument, day), h in sorted(inputs.holdings.items()):
        where = f"{day.isoformat()} {instrument}"
        cost = h.volume * h.avg_cost
        value = h.volume * h.market_price
        if not _close(cost, h.cost_value):
            errors.append(f"{where} cost_value: {cost} vs {h.cost_value}")
        if not _close(value, h.market_value):
            errors.append(f"{where} market_value: {value} vs {h.market_value}")
        if not _close(h.market_value - h.cost_value, h.unrealized_pl):
            errors.append(
                f"{where} unrealized_pl: {h.market_value - h.cost_value} "
                f"vs {h.unrealized_pl}"
            )
    return _errors_result("G2_holding_rows", errors, f"{len(inputs.holdings)} rows ok")


def _by_ticker(rows: Any) -> dict[str, dict[str, Any]]:
    found: dict[str, dict[str, Any]] = {}
    if isinstance(rows, list):
        for row in rows:
            if isinstance(row, dict) and isinstance(row.get("ticker"), str):
                found.setdefault(row["ticker"], row)
    return found


def _same_whole(card: Any, precise: Any) -> bool:
    if not isinstance(card, str) or not isinstance(precise, str):
        return False
    value = parse_display(precise)
    return value is not None and fmt_whole(value) == card


def same_figure_check(report: Report) -> CheckResult:
    """G3: the same figure has the same value wherever the report prints it.

    The NAV and cash cards are whole amounts; they are compared with the
    holdings values rounded the same way.
    """
    name = "G3_same_figure"
    errors: list[str] = []
    cards = report.get("cards", {})
    total = report.get("holdings_total", {})
    holdings = _by_ticker(report.get("holdings"))
    summary = _by_ticker(report.get("summary"))
    instruments = _by_ticker(report.get("instruments"))
    cash_row = holdings.get(CASH, {})

    if not _same_whole(cards.get("nav"), total.get("market_value")):
        errors.append(
            f"nav card {cards.get('nav')} vs holdings_total {total.get('market_value')}"
        )
    if not _same_whole(cards.get("cash_on_hand"), cash_row.get("market_value")):
        errors.append(
            f"cash card {cards.get('cash_on_hand')} vs CASH row "
            f"{cash_row.get('market_value')}"
        )
    tickers = [t for t in holdings if t != CASH]
    if tickers != list(summary) or tickers != list(instruments):
        errors.append(
            f"tickers: holdings {tickers}, summary {list(summary)}, "
            f"instruments {list(instruments)}"
        )
    for ticker, row in summary.items():
        card = instruments.get(ticker, {}).get("cards", {})
        holding = holdings.get(ticker, {})
        for left, right in _SUMMARY_TO_CARDS:
            if row.get(left) != card.get(right):
                errors.append(
                    f"{ticker} {left} {row.get(left)} vs cards {card.get(right)}"
                )
        if not _same_whole(card.get("cash"), row.get("cash")):
            errors.append(
                f"{ticker} cash {row.get('cash')} vs cards {card.get('cash')}"
            )
        for left, right in _SUMMARY_TO_HOLDINGS:
            if row.get(left) != holding.get(right):
                errors.append(
                    f"{ticker} {left} {row.get(left)} vs holdings {holding.get(right)}"
                )
    return _errors_result(name, errors)


def units_check(inputs: GridInputs) -> CheckResult:
    """G4: initial units plus BUY minus SELL quantities equal each volume."""
    errors: list[str] = []
    for setup in inputs.setups:
        for day in inputs.dates:
            units = setup.initial_units
            for t in inputs.trades:
                if t.instrument != setup.instrument or t.day > day:
                    continue
                if t.side == "BUY":
                    units += t.qty
                elif t.side == "SELL":
                    units -= t.qty
            volume = inputs.holdings[(setup.instrument, day)].volume
            if units != volume:
                errors.append(
                    f"{day.isoformat()} {setup.instrument}: {units} vs {volume}"
                )
    count = len(inputs.setups) * len(inputs.dates)
    return _errors_result("G4_units", errors, f"{count} rows ok")


def weights_check(inputs: GridInputs) -> CheckResult:
    """G5: the unrounded weights of the instruments and CASH sum to 100."""
    total = sum((w for _, w in weights(inputs)), Decimal(0))
    shown = total.quantize(Decimal("0.0001"))
    return _result("G5_weights", _close(total, Decimal(100)), f"{shown} vs 100")


def _units(value: Any) -> Decimal | None:
    return parse_display(value) if isinstance(value, str) else None


def nav_volume_check(report: Report) -> CheckResult:
    """G6: NAV volume and gain volume in the summary and instrument cards."""
    errors: list[str] = []
    for ticker, row in _by_ticker(report.get("summary")).items():
        current = _units(row.get("current_units"))
        expected = _units(row.get("expected_volume"))
        nav = _units(row.get("nav_volume"))
        initial = _units(row.get("initial_units"))
        gain = _units(row.get("gain_volume"))
        if None in (current, expected, nav, initial, gain):
            errors.append(f"summary {ticker}: unparseable value")
            continue
        assert current is not None and expected is not None
        assert nav is not None and initial is not None and gain is not None
        if current + expected != nav:
            errors.append(f"summary {ticker} nav_volume: {current + expected} vs {nav}")
        if nav - initial != gain:
            errors.append(f"summary {ticker} gain_volume: {nav - initial} vs {gain}")
    for ticker, item in _by_ticker(report.get("instruments")).items():
        cards = item.get("cards", {})
        nav = _units(cards.get("nav_volume"))
        initial = _units(cards.get("initial_units"))
        gain = _units(cards.get("gain_volume"))
        if nav is None or initial is None or gain is None:
            errors.append(f"instruments {ticker}: unparseable value")
        elif nav - initial != gain:
            errors.append(
                f"instruments {ticker} gain_volume: {nav - initial} vs {gain}"
            )
    return _errors_result("G6_nav_volume", errors)


def dividend_check(inputs: GridInputs, report: Report) -> CheckResult:
    """G7: the dividend card equals the sum of the DIVIDEND rows it counts."""
    rows = dividend_rows(inputs)
    total = fmt_whole(sum((t.amount for t in rows), Decimal(0)))
    card = report.get("cards", {}).get("dividend_ytd")
    return _result(
        "G7_dividend_ytd",
        card == total,
        f"{card} vs {total} from {len(rows)} row(s)",
    )


def _key(row: Any, fields: Sequence[str]) -> tuple[Any, ...]:
    if not isinstance(row, dict):
        return (row,)
    return tuple(row.get(f) for f in fields)


def _missing_rows(
    rows: Any, available: Counter[tuple[Any, ...]], fields: Sequence[str]
) -> list[str]:
    left = Counter(available)
    missing: list[str] = []
    for row in rows if isinstance(rows, list) else []:
        key = _key(row, fields)
        if left[key] > 0:
            left[key] -= 1
        else:
            missing.append(", ".join(str(v) for v in key))
    return missing


def transaction_rows_check(inputs: GridInputs, report: Report) -> CheckResult:
    """G8: row counts of the transaction tables and every row exists."""
    errors: list[str] = []
    formatted = [transaction_row(t) for t in inputs.trades]
    fields = list(formatted[0]) if formatted else ["trade_date", "ticker"]
    available = Counter(_key(r, fields) for r in formatted)

    rows = report.get("transactions")
    count = len(rows) if isinstance(rows, list) else 0
    want = min(TRANSACTION_ROWS, len(formatted))
    if count != want:
        errors.append(f"transactions: {count} rows vs {want}")
    errors += [
        f"transactions row not found: {m}"
        for m in _missing_rows(rows, available, fields)
    ]

    for ticker, item in _by_ticker(report.get("instruments")).items():
        own = item.get("transactions")
        tagged = (
            [{**r, "ticker": ticker} if isinstance(r, dict) else r for r in own]
            if isinstance(own, list)
            else []
        )
        have = sum(1 for t in inputs.trades if t.instrument == ticker)
        want = min(INSTRUMENT_TRANSACTION_ROWS, have)
        if len(tagged) != want:
            errors.append(f"{ticker} transactions: {len(tagged)} rows vs {want}")
        errors += [
            f"{ticker} transactions row not found: {m}"
            for m in _missing_rows(tagged, available, fields)
        ]
    return _errors_result("G8_transaction_rows", errors)


def chart_series_check(inputs: GridInputs, report: Report) -> CheckResult:
    """G9: every chart has one point per history date, inception to as-of."""
    errors: list[str] = []
    history = [d.isoformat() for d in inputs.dates]
    inception = inputs.inception.isoformat()
    as_of = inputs.as_of.isoformat()
    if not history or history[0] != inception:
        errors.append(f"first history date {history[:1]} vs inception {inception}")
    if not history or history[-1] != as_of:
        errors.append(f"last history date {history[-1:]} vs as-of {as_of}")
    instruments = _by_ticker(report.get("instruments"))
    expected_tickers = [s.instrument for s in inputs.setups]
    if list(instruments) != expected_tickers:
        errors.append(f"instruments {list(instruments)} vs {expected_tickers}")
    for ticker, item in instruments.items():
        chart = item.get("chart", {})
        dates = chart.get("dates")
        if dates != history:
            errors.append(
                f"{ticker} dates do not match the {len(history)} history dates"
            )
        for series in ("avg_cost", "market_price", "nav_volume_pct"):
            values = chart.get(series)
            if not isinstance(values, list) or len(values) != len(history):
                errors.append(f"{ticker} {series}: not {len(history)} points")
    ok = f"{len(history)} points per instrument, {inception} to {as_of}"
    return _errors_result("G9_chart_series", errors, ok)


def grid_checks(inputs: GridInputs, report: Report) -> list[CheckResult]:
    """Run G1-G9 on the parsed inputs and the built report.

    Args:
        inputs: Parsed inputs the report was built from.
        report: Report dict from ``build_report``.

    Returns:
        One result per check, in name order.
    """
    return [
        nav_check(inputs),
        holding_rows_check(inputs),
        same_figure_check(report),
        units_check(inputs),
        weights_check(inputs),
        nav_volume_check(report),
        dividend_check(inputs, report),
        transaction_rows_check(inputs, report),
        chart_series_check(inputs, report),
    ]
