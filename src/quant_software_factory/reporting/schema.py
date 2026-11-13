"""Schema registry for the precomputed report datasets.

``SCHEMAS`` is the single definition of each dataset's fields and types. It is
used by :mod:`.source` to check headers and filter rows, and by the A3 schema
check to validate values.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Literal

Kind = Literal["str", "date", "decimal", "int", "period", "enum"]

DATE_FIELD = "date"
PERIOD_FIELD = "period"
ACCOUNT_FIELD = "account_no"

_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
_PERIOD_RE = re.compile(r"(\d{4})-(0[1-9]|1[0-2])")
_INT_RE = re.compile(r"-?\d+")
_DECIMAL_RE = re.compile(r"-?\d+(\.\d+)?")


@dataclass(frozen=True)
class FieldSpec:
    """Declared name and type of one dataset field.

    Attributes:
        name: Field (column) name.
        kind: Value type.
        choices: Allowed values when ``kind`` is ``"enum"``.
        required: Whether a blank value is an error.
    """

    name: str
    kind: Kind
    choices: tuple[str, ...] = ()
    required: bool = True


def _decimals(*names: str) -> tuple[FieldSpec, ...]:
    return tuple(FieldSpec(n, "decimal") for n in names)


SCHEMAS: dict[str, tuple[FieldSpec, ...]] = {
    "account_info": (
        FieldSpec("account_no", "str"),
        FieldSpec("client_name", "str"),
        FieldSpec("strategy", "str"),
        FieldSpec("inception_date", "date"),
        FieldSpec("product", "str"),
    ),
    "nav_daily": (
        FieldSpec("date", "date"),
        FieldSpec("account_no", "str"),
        *_decimals("nav", "cash", "market_value"),
    ),
    "holdings_daily": (
        FieldSpec("date", "date"),
        FieldSpec("account_no", "str"),
        FieldSpec("instrument", "str"),
        FieldSpec("volume", "int"),
        *_decimals(
            "avg_cost", "cost_value", "market_price", "market_value", "unrealized_pl"
        ),
    ),
    "transactions": (
        FieldSpec("date", "date"),
        FieldSpec("account_no", "str"),
        FieldSpec("instrument", "str"),
        FieldSpec("side", "enum", ("BUY", "SELL", "DIVIDEND")),
        FieldSpec("qty", "int"),
        *_decimals("price", "fee", "tax", "amount"),
        FieldSpec("realized_pl", "decimal", required=False),
    ),
    "cash_flow": (
        FieldSpec("date", "date"),
        FieldSpec("account_no", "str"),
        FieldSpec("flow_type", "enum", ("DEPOSIT", "WITHDRAWAL")),
        FieldSpec("amount", "decimal"),
    ),
    "performance": (
        FieldSpec("period", "period"),
        FieldSpec("account_no", "str"),
        *_decimals(
            "capital_gain", "dividend", "unrealized_change", "total_pl", "return_pct"
        ),
    ),
}


def parse_date(value: str) -> date | None:
    """Parse a strict ``YYYY-MM-DD`` date, or return ``None``."""
    if not _DATE_RE.fullmatch(value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def parse_period(value: str) -> tuple[int, int] | None:
    """Parse a strict ``YYYY-MM`` period into ``(year, month)``, or ``None``."""
    match = _PERIOD_RE.fullmatch(value)
    if match is None:
        return None
    return int(match.group(1)), int(match.group(2))


def parse_decimal(value: str) -> Decimal | None:
    """Parse a plain decimal such as ``-12.50`` (no exponent, NaN or spaces)."""
    if not _DECIMAL_RE.fullmatch(value):
        return None
    try:
        return Decimal(value)
    except InvalidOperation:  # pragma: no cover - guarded by the regex
        return None


def _type_error(spec: FieldSpec, value: str) -> str | None:
    if spec.kind == "str":
        return None
    if spec.kind == "enum":
        if value in spec.choices:
            return None
        return f"not in {'|'.join(spec.choices)}"
    if spec.kind == "date":
        return None if parse_date(value) is not None else "is not an ISO date"
    if spec.kind == "period":
        return None if parse_period(value) is not None else "is not a YYYY-MM period"
    if spec.kind == "int":
        return None if _INT_RE.fullmatch(value) else "is not an int"
    return None if parse_decimal(value) is not None else "is not a decimal"


def _required_for_sell(dataset: str, spec: FieldSpec, row: Mapping[str, str]) -> bool:
    return (
        dataset == "transactions"
        and spec.name == "realized_pl"
        and row.get("side") == "SELL"
    )


def validate_rows(dataset: str, rows: Sequence[Mapping[str, str]]) -> list[str]:
    """Validate row values against the registry entry for ``dataset``.

    Args:
        dataset: Registry key.
        rows: Rows as returned by ``load``.

    Returns:
        Error messages in row order, then field order. Empty when valid.
    """
    errors: list[str] = []
    for index, row in enumerate(rows, start=1):
        for spec in SCHEMAS[dataset]:
            value = row[spec.name]
            if value == "":
                if spec.required:
                    errors.append(f"row {index}: {spec.name} is blank")
                elif _required_for_sell(dataset, spec, row):
                    errors.append(f"row {index}: {spec.name} is required for SELL")
                continue
            problem = _type_error(spec, value)
            if problem is not None:
                errors.append(f"row {index}: {spec.name} '{value}' {problem}")
    return errors
