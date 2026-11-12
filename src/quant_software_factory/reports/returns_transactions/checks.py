"""Check records and Layer 2 (accounting and narrative) checks."""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from .definitions import BUY, DEPOSIT, DIVIDEND, SELL, WITHDRAWAL
from .formatting import fmt_money, fmt_pct
from .narrative import (
    NUMBER_RE,
    banned_phrases_in,
    repeated_openers,
    split_paragraphs,
    word_count,
)

if TYPE_CHECKING:
    from .engine import EngineResult
    from .loader import Transaction

TOLERANCE = Decimal("0.01")
MIN_PARAGRAPHS = 2
MAX_PARAGRAPHS = 4
MAX_WORDS = 180


@dataclass(frozen=True)
class Check:
    """One validation result, serialized into checks.json."""

    name: str
    passed: bool
    expected: str
    actual: str

    def to_json(self) -> dict[str, str | bool]:
        return {
            "name": self.name,
            "passed": self.passed,
            "expected": self.expected,
            "actual": self.actual,
        }


def replay_cash(opening_cash: Decimal, transactions: list[Transaction]) -> Decimal:
    """Recompute the closing cash balance straight from the transaction rows.

    This is deliberately independent of the engine's position replay.
    """
    cash = opening_cash
    for txn in transactions:
        qty = Decimal(txn.qty) if txn.qty is not None else Decimal(0)
        price = txn.price if txn.price is not None else Decimal(0)
        amount = txn.amount if txn.amount is not None else Decimal(0)
        if txn.side == BUY:
            cash -= qty * price + txn.fee
        elif txn.side == SELL:
            cash += qty * price - txn.fee
        elif txn.side == DIVIDEND:
            cash += qty * price - txn.tax
        elif txn.side == DEPOSIT:
            cash += amount
        elif txn.side == WITHDRAWAL:
            cash -= amount
    return cash


def accounting_checks(
    result: EngineResult, transactions: list[Transaction]
) -> list[Check]:
    """Accounting identity, holdings totals, weights and cash replay."""
    checks: list[Check] = []

    expected_nav = result.expected_closing_nav
    closing_nav = result.closing_nav
    checks.append(
        Check(
            "accounting.identity",
            abs(closing_nav - expected_nav) <= TOLERANCE,
            fmt_money(expected_nav),
            fmt_money(closing_nav),
        )
    )

    held = result.held_instruments
    row_values: dict[str, list[Decimal]] = {
        "cost_value": [i.closing_cost for i in held] + [result.closing_cash],
        "market_value": [i.closing_market_value for i in held] + [result.closing_cash],
        "unrealized_pnl": [i.closing_unrealized for i in held] + [Decimal(0)],
        "weight_pct": [i.weight_pct for i in held] + [result.cash_weight_pct],
    }
    totals: dict[str, Decimal] = {
        "cost_value": sum((i.closing_cost for i in held), result.closing_cash),
        "market_value": closing_nav,
        "unrealized_pnl": result.closing_unrealized,
        "weight_pct": Decimal(100) if closing_nav != 0 else Decimal(0),
    }
    for column, values in row_values.items():
        fmt = fmt_pct if column == "weight_pct" else fmt_money
        row_sum = sum(values, Decimal(0))
        checks.append(
            Check(
                f"accounting.holdings_total.{column}",
                abs(row_sum - totals[column]) <= TOLERANCE,
                fmt(totals[column]),
                fmt(row_sum),
            )
        )

    weight_sum = sum(row_values["weight_pct"], Decimal(0))
    checks.append(
        Check(
            "accounting.weights_sum",
            abs(weight_sum - Decimal(100)) <= TOLERANCE,
            fmt_pct(Decimal(100)),
            fmt_pct(weight_sum),
        )
    )

    replayed = replay_cash(result.opening_cash, transactions)
    checks.append(
        Check(
            "accounting.cash_replay",
            abs(result.closing_cash - replayed) <= TOLERANCE,
            fmt_money(replayed),
            fmt_money(result.closing_cash),
        )
    )
    return checks


def _string_leaves(value: Any) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _string_leaves(item)
    elif isinstance(value, list):
        for item in value:
            yield from _string_leaves(item)


def report_values(report: dict[str, Any]) -> set[str]:
    """String leaves of the report, excluding the narrative block itself."""
    return {
        leaf
        for block_id, block in report.items()
        if block_id != "narrative"
        for leaf in _string_leaves(block)
    }


def untraceable_numbers(narrative_text: str, report: dict[str, Any]) -> list[str]:
    """Numbers in the narrative not found verbatim in report.json.

    Digits not covered by a NUMBER_RE token (dates, years, unformatted
    numbers) are reported too.
    """
    values = report_values(report)
    missing = [t for t in NUMBER_RE.findall(narrative_text) if t not in values]
    leftover = re.findall(r"\S*\d\S*", NUMBER_RE.sub(" ", narrative_text))
    return missing + [f"stray digits in {s!r}" for s in leftover]


def narrative_checks(narrative_text: str, report: dict[str, Any]) -> list[Check]:
    """Number traceability and writing-style checks for the narrative."""
    missing = untraceable_numbers(narrative_text, report)
    checks = [
        Check(
            "narrative.numbers_in_report",
            not missing,
            "every number in narrative.md appears in report.json",
            "; ".join(missing),
        )
    ]

    paragraphs = len(split_paragraphs(narrative_text))
    words = word_count(narrative_text)
    banned = banned_phrases_in(narrative_text)
    repeats = repeated_openers(narrative_text)
    problems: list[str] = []
    if not MIN_PARAGRAPHS <= paragraphs <= MAX_PARAGRAPHS:
        problems.append(f"{paragraphs} paragraphs")
    if words >= MAX_WORDS:
        problems.append(f"{words} words")
    if banned:
        problems.append("banned phrases: " + ", ".join(banned))
    if repeats:
        problems.append("repeated sentence openers: " + ", ".join(repeats))
    checks.append(
        Check(
            "narrative.style",
            not problems,
            f"{MIN_PARAGRAPHS} to {MAX_PARAGRAPHS} paragraphs, under {MAX_WORDS} "
            "words, no banned phrases, no repeated sentence openers",
            "; ".join(problems) or f"{paragraphs} paragraphs, {words} words",
        )
    )
    return checks
