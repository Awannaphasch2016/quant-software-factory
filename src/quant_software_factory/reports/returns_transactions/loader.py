"""CSV loading and Layer 1 (input) validation.

``load_inputs`` never raises for bad input data. It returns the parsed inputs
together with the list of input checks. Structural checks (file present,
exact header, every field parses) run first; if any of them fails, the
dependent checks (dates, sides, sell volume, prices) are omitted and the
parsed inputs are ``None``.
"""

from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path

from .checks import Check
from .definitions import (
    ALLOWED_SIDES,
    BUY,
    CASH,
    CASH_FLOW_SIDES,
    DIVIDEND,
    EXPECTED_COLUMNS,
    OPENING_POSITIONS_FILE,
    PRICES_FILE,
    SELL,
    SHARE_SIDES,
    TRANSACTIONS_FILE,
    ReportDefinition,
)

_INT_RE = re.compile(r"-?\d+")
_DECIMAL_RE = re.compile(r"-?\d+(?:\.\d+)?")
_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


class ParseError(Exception):
    """A field in an input CSV could not be parsed."""


@dataclass(frozen=True)
class OpeningPosition:
    instrument: str
    volume: int
    cost_value: Decimal


@dataclass(frozen=True)
class Transaction:
    index: int
    trade_date: date
    instrument: str
    side: str
    qty: int | None
    price: Decimal | None
    fee: Decimal
    tax: Decimal
    amount: Decimal | None


@dataclass(frozen=True)
class Inputs:
    opening_positions: dict[str, OpeningPosition]
    transactions: list[Transaction]
    prices: dict[tuple[date, str], Decimal]

    @property
    def opening_cash(self) -> Decimal:
        position = self.opening_positions.get(CASH)
        return position.cost_value if position is not None else Decimal(0)


def _parse_int(value: str, field: str) -> int:
    if not _INT_RE.fullmatch(value):
        raise ParseError(f"{field} {value!r} is not an integer")
    return int(value)


def _parse_decimal(value: str, field: str) -> Decimal:
    if not _DECIMAL_RE.fullmatch(value):
        raise ParseError(f"{field} {value!r} is not a decimal number")
    return Decimal(value)


def _parse_date(value: str, field: str) -> date:
    if not _DATE_RE.fullmatch(value):
        raise ParseError(f"{field} {value!r} is not a YYYY-MM-DD date")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ParseError(f"{field} {value!r} is not a valid date") from exc


def _non_negative(value: Decimal, field: str) -> Decimal:
    if value < 0:
        raise ParseError(f"{field} must not be negative")
    return value


def _parse_opening(rows: list[dict[str, str]]) -> dict[str, OpeningPosition]:
    positions: dict[str, OpeningPosition] = {}
    for line, row in enumerate(rows, start=2):
        try:
            instrument = row["instrument"]
            if not instrument:
                raise ParseError("instrument is blank")
            if instrument in positions:
                raise ParseError(f"duplicate instrument {instrument!r}")
            volume = _parse_int(row["volume"], "volume")
            if volume < 0:
                raise ParseError("volume must not be negative")
            cost_value = _non_negative(
                _parse_decimal(row["cost_value"], "cost_value"), "cost_value"
            )
        except ParseError as exc:
            raise ParseError(f"line {line}: {exc}") from exc
        positions[instrument] = OpeningPosition(instrument, volume, cost_value)
    return positions


def _parse_transaction(index: int, row: dict[str, str]) -> Transaction:
    side = row["side"]
    instrument = row["instrument"]
    if not instrument:
        raise ParseError("instrument is blank")
    trade_date = _parse_date(row["trade_date"], "trade_date")
    qty = _parse_int(row["qty"], "qty") if row["qty"] else None
    price = _parse_decimal(row["price"], "price") if row["price"] else None
    fee = _non_negative(_parse_decimal(row["fee"], "fee"), "fee")
    tax = _non_negative(_parse_decimal(row["tax"], "tax"), "tax")
    amount = _parse_decimal(row["amount"], "amount") if row["amount"] else None

    if side in SHARE_SIDES:
        if instrument == CASH:
            raise ParseError(f"{side} must not use instrument {CASH}")
        if qty is None or qty <= 0:
            raise ParseError(f"{side} requires a positive qty")
        if price is None or price < 0:
            raise ParseError(f"{side} requires a non-negative price")
        if amount is not None:
            raise ParseError(f"{side} must leave amount blank")
        if side != DIVIDEND and tax != 0:
            raise ParseError("tax applies to dividends only")
        if side == DIVIDEND and fee != 0:
            raise ParseError("DIVIDEND must have a zero fee")
    elif side in CASH_FLOW_SIDES:
        if instrument != CASH:
            raise ParseError(f"{side} must use instrument {CASH}")
        if qty is not None or price is not None:
            raise ParseError(f"{side} must leave qty and price blank")
        if amount is None or amount <= 0:
            raise ParseError(f"{side} requires a positive amount")
        if fee != 0 or tax != 0:
            raise ParseError(f"{side} must have zero fee and tax")
    # Unknown sides are reported by the input.sides check, not here.
    return Transaction(
        index, trade_date, instrument, side, qty, price, fee, tax, amount
    )


def _parse_transactions(rows: list[dict[str, str]]) -> list[Transaction]:
    transactions: list[Transaction] = []
    for index, row in enumerate(rows):
        try:
            transactions.append(_parse_transaction(index, row))
        except ParseError as exc:
            raise ParseError(f"line {index + 2}: {exc}") from exc
    return transactions


def _parse_prices(rows: list[dict[str, str]]) -> dict[tuple[date, str], Decimal]:
    prices: dict[tuple[date, str], Decimal] = {}
    for line, row in enumerate(rows, start=2):
        try:
            price_date = _parse_date(row["date"], "date")
            instrument = row["instrument"]
            if not instrument:
                raise ParseError("instrument is blank")
            key = (price_date, instrument)
            if key in prices:
                raise ParseError(
                    f"duplicate price for {instrument} on {price_date.isoformat()}"
                )
            close = _parse_decimal(row["close"], "close")
            if close < 0:
                raise ParseError("close must not be negative")
        except ParseError as exc:
            raise ParseError(f"line {line}: {exc}") from exc
        prices[key] = close
    return prices


def _read_csv(path: Path) -> tuple[list[str], list[list[str]]]:
    """Return the header and the non-empty data records of a UTF-8 CSV."""
    text = path.read_bytes().decode("utf-8")
    records = list(csv.reader(io.StringIO(text, newline="")))
    if not records:
        return [], []
    return records[0], records[1:]


def _to_dicts(header: list[str], records: list[list[str]]) -> list[dict[str, str]]:
    """Map records to dicts; raises ParseError on a wrong number of fields."""
    rows: list[dict[str, str]] = []
    for line, record in enumerate(records, start=2):
        if not record:
            raise ParseError(f"line {line}: blank line")
        if len(record) != len(header):
            raise ParseError(
                f"line {line}: expected {len(header)} fields, found {len(record)}"
            )
        rows.append(dict(zip(header, record, strict=True)))
    return rows


def replay_sell_violations(
    opening_positions: dict[str, OpeningPosition], transactions: list[Transaction]
) -> tuple[list[str], dict[str, int]]:
    """Replay share volumes chronologically (stable on file order).

    Returns descriptions of SELL rows that exceed the volume held at that
    point, and the closing share volume per instrument.
    """
    volumes: dict[str, int] = {
        name: position.volume
        for name, position in opening_positions.items()
        if name != CASH
    }
    violations: list[str] = []
    for txn in sorted(transactions, key=lambda t: (t.trade_date, t.index)):
        if txn.qty is None:
            continue
        held = volumes.get(txn.instrument, 0)
        if txn.side == BUY:
            volumes[txn.instrument] = held + txn.qty
        elif txn.side == SELL:
            if txn.qty > held:
                violations.append(
                    f"line {txn.index + 2}: SELL {txn.instrument} {txn.qty} "
                    f"exceeds held {held}"
                )
                volumes[txn.instrument] = 0
            else:
                volumes[txn.instrument] = held - txn.qty
    return violations, volumes


def _semantic_checks(inputs: Inputs, definition: ReportDefinition) -> list[Check]:
    checks: list[Check] = []
    start, end = definition.period_start, definition.period_end
    period_text = f"{start.isoformat()} to {end.isoformat()}"

    bad_txn_dates = [
        f"line {t.index + 2}: {t.trade_date.isoformat()}"
        for t in inputs.transactions
        if not start <= t.trade_date <= end
    ]
    checks.append(
        Check(
            "input.dates.transactions",
            not bad_txn_dates,
            f"all trade dates within {period_text}",
            "; ".join(bad_txn_dates) or "ok",
        )
    )

    bad_price_dates = sorted(
        {
            d.isoformat()
            for d, _ in inputs.prices
            if d != definition.opening_date and not start <= d <= end
        }
    )
    checks.append(
        Check(
            "input.dates.prices",
            not bad_price_dates,
            f"all price dates equal {definition.opening_date.isoformat()} "
            f"or fall within {period_text}",
            ", ".join(bad_price_dates) or "ok",
        )
    )

    bad_sides = [
        f"line {t.index + 2}: {t.side!r}"
        for t in inputs.transactions
        if t.side not in ALLOWED_SIDES
    ]
    checks.append(
        Check(
            "input.sides",
            not bad_sides,
            "sides in " + ", ".join(ALLOWED_SIDES),
            "; ".join(bad_sides) or "ok",
        )
    )

    violations, closing_volumes = replay_sell_violations(
        inputs.opening_positions, inputs.transactions
    )
    checks.append(
        Check(
            "input.sell_volume",
            not violations,
            "no SELL exceeds the volume held at that point",
            "; ".join(violations) or "ok",
        )
    )

    opening_held = sorted(
        name
        for name, position in inputs.opening_positions.items()
        if name != CASH and position.volume > 0
    )
    missing_opening = [
        name
        for name in opening_held
        if (definition.opening_date, name) not in inputs.prices
    ]
    checks.append(
        Check(
            "input.prices.opening",
            not missing_opening,
            f"a {definition.opening_date.isoformat()} price for every instrument "
            "held at the opening date",
            "missing: " + ", ".join(missing_opening) if missing_opening else "ok",
        )
    )

    closing_held = sorted(name for name, vol in closing_volumes.items() if vol > 0)
    missing_closing = [
        name
        for name in closing_held
        if (definition.as_of_date, name) not in inputs.prices
    ]
    checks.append(
        Check(
            "input.prices.closing",
            not missing_closing,
            f"a {definition.as_of_date.isoformat()} price for every instrument "
            "held at the as-of date",
            "missing: " + ", ".join(missing_closing) if missing_closing else "ok",
        )
    )
    return checks


def load_inputs(
    input_dir: Path, definition: ReportDefinition
) -> tuple[Inputs | None, list[Check]]:
    """Read the three CSVs and run the Layer 1 input checks."""
    checks: list[Check] = []
    present: list[str] = []
    for name in EXPECTED_COLUMNS:
        exists = (input_dir / name).is_file()
        checks.append(
            Check(
                f"input.files.{name}",
                exists,
                "present",
                "present" if exists else "missing",
            )
        )
        if exists:
            present.append(name)

    raw: dict[str, tuple[list[str], list[list[str]]]] = {}
    for name in present:
        expected = EXPECTED_COLUMNS[name]
        try:
            header, records = _read_csv(input_dir / name)
        except (UnicodeDecodeError, csv.Error) as exc:
            checks.append(
                Check(
                    f"input.columns.{name}",
                    False,
                    ",".join(expected),
                    f"unreadable: {exc}",
                )
            )
            continue
        columns_ok = tuple(header) == expected
        checks.append(
            Check(
                f"input.columns.{name}",
                columns_ok,
                ",".join(expected),
                ",".join(header),
            )
        )
        if columns_ok:
            raw[name] = (header, records)

    parsed_opening: dict[str, OpeningPosition] | None = None
    parsed_transactions: list[Transaction] | None = None
    parsed_prices: dict[tuple[date, str], Decimal] | None = None
    for name, (header, records) in raw.items():
        error = "ok"
        try:
            rows = _to_dicts(header, records)
            if name == OPENING_POSITIONS_FILE:
                parsed_opening = _parse_opening(rows)
            elif name == TRANSACTIONS_FILE:
                parsed_transactions = _parse_transactions(rows)
            elif name == PRICES_FILE:
                parsed_prices = _parse_prices(rows)
        except ParseError as exc:
            error = str(exc)
        checks.append(
            Check(f"input.parse.{name}", error == "ok", "all fields parse", error)
        )

    if (
        parsed_opening is None
        or parsed_transactions is None
        or parsed_prices is None
        or not all(check.passed for check in checks)
    ):
        return None, checks

    inputs = Inputs(parsed_opening, parsed_transactions, parsed_prices)
    checks.extend(_semantic_checks(inputs, definition))
    return inputs, checks
