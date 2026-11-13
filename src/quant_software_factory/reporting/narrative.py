"""Template narrative for the Returns & Transactions report.

The text is built from the formatted strings in the report dict with fixed
sentence templates. No figure is computed here: every amount is copied from the
report, and a negative amount is written as a loss using its absolute value.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from .returns_transactions import CASH, TOTAL, Report, fmt_long_date
from .schema import parse_date

# Lists longer than this are summarised by count only, to keep the text short.
MAX_LISTED = 2


def _long(iso: str) -> str:
    day = parse_date(iso)
    return iso if day is None else fmt_long_date(day)


def _abs(value: str) -> str:
    return value.removeprefix("-")


def _signed(value: str, currency: str, gain: str = "gain", loss: str = "loss") -> str:
    """Return ``"a gain of X THB"`` or, for a negative value, ``"a loss of X THB"``."""
    word = loss if value.startswith("-") else gain
    article = "an" if word[0] in "aeiou" else "a"
    return f"{article} {word} of {_abs(value)} {currency}"


def _join(items: Sequence[str]) -> str:
    if len(items) <= 2:
        return " and ".join(items)
    return ", ".join(items[:-1]) + ", and " + items[-1]


def _count(n: int, singular: str, plural: str) -> str:
    return f"one {singular}" if n == 1 else f"{n} {plural}"


def _performance(report: Report, currency: str) -> str:
    kpi = report["kpi_summary"]
    as_of = _long(report["header"]["as_of"])
    ret = kpi["period_return"]
    if ret.startswith("-"):
        return_text = f"a negative simple return of {_abs(ret)}"
    else:
        return_text = f"a simple return of {ret}"
    return (
        f"Net asset value was {kpi['net_asset_value']} {currency} on {as_of}. "
        f"Total P/L for the period was {_signed(kpi['total_pl'], currency)}, "
        f"{return_text} on opening net asset value."
    )


def _sales_and_dividends(
    report: Report, rows: list[dict[str, Any]], currency: str
) -> str:
    kpi = report["kpi_summary"]
    sales = [r for r in rows if r["side"] == "SELL"]
    dividends = [r for r in rows if r["side"] == "DIVIDEND"]
    sentences: list[str] = []
    if not sales:
        sentences.append("There were no sales in the period.")
    else:
        text = (
            f"During the period the account made {_count(len(sales), 'sale', 'sales')}"
        )
        if len(sales) <= MAX_LISTED:
            items = [
                f"{r['instrument']} on {_long(r['date'])} with "
                + _signed(r["realized_pl"], currency, "realized gain", "realized loss")
                for r in sales
            ]
            text += ": " + _join(items)
        sentences.append(text + ".")
    realized = kpi["realized_capital_gain"]
    if realized.startswith("-"):
        sentences.append(
            f"Realized capital result for the period was {_signed(realized, currency)}."
        )
    else:
        sentences.append(
            f"Realized capital gain for the period was {realized} {currency}."
        )
    if not dividends:
        sentences.append("No dividends were received in the period.")
    else:
        sentences.append(
            f"Net dividends of {kpi['dividends_net']} {currency} were received "
            f"from {_count(len(dividends), 'payment', 'payments')}."
        )
    return " ".join(sentences)


def _positions(report: Report, currency: str) -> str:
    rows = report["holdings"]
    held = [r for r in rows if r["instrument"] not in (CASH, TOTAL)]
    total = next((r for r in rows if r["instrument"] == TOTAL), None)
    change = _signed(report["kpi_summary"]["change_in_unrealized_pl"], currency)
    if not held or total is None:
        return (
            "At the as-of date the account held no securities positions. "
            f"Change in unrealized P/L for the period was {change}."
        )
    text = (
        "At the as-of date the account held "
        f"{_count(len(held), 'position', 'positions')}"
    )
    if len(held) <= MAX_LISTED:
        items = [
            f"{r['instrument']} with "
            + _signed(
                r["unrealized_pl"], currency, "unrealized gain", "unrealized loss"
            )
            for r in held
        ]
        text += ": " + _join(items)
    these = "this position" if len(held) == 1 else "these positions"
    return (
        f"{text}. Unrealized P/L on {these} was "
        f"{_signed(total['unrealized_pl'], currency)}, and the change in "
        f"unrealized P/L for the period was {change}."
    )


def _flow_items(rows: list[dict[str, Any]], currency: str) -> str:
    return _join(
        [f"{_abs(r['amount'])} {currency} on {_long(r['date'])}" for r in rows]
    )


def _flows(rows: list[dict[str, Any]], currency: str) -> str:
    cash = [r for r in rows if r["instrument"] == CASH]
    deposits = [r for r in cash if r["side"] == "DEPOSIT"]
    withdrawals = [r for r in cash if r["side"] == "WITHDRAWAL"]
    if not deposits and not withdrawals:
        return "There were no deposits or withdrawals in the period."
    sentences: list[str] = []
    if not deposits:
        sentences.append("No deposits were made in the period.")
    elif len(deposits) == 1:
        sentences.append(
            f"The account received a deposit of {_flow_items(deposits, currency)}."
        )
    elif len(deposits) <= MAX_LISTED:
        sentences.append(
            f"The account received deposits of {_flow_items(deposits, currency)}."
        )
    else:
        sentences.append(f"The account received {len(deposits)} deposits.")
    if not withdrawals:
        sentences.append("No withdrawals were made in the period.")
    elif len(withdrawals) == 1:
        only = withdrawals[0]
        sentences.append(
            f"A withdrawal of {_abs(only['amount'])} {currency} was made on "
            f"{_long(only['date'])}."
        )
    elif len(withdrawals) <= MAX_LISTED:
        sentences.append(f"Withdrawals were {_flow_items(withdrawals, currency)}.")
    else:
        sentences.append(f"Withdrawals were made {len(withdrawals)} times.")
    return " ".join(sentences)


def generate_narrative(report: Report) -> list[str]:
    """Write the narrative paragraphs for a built report.

    Paragraphs, in order: net asset value and total P/L; sales and dividends;
    positions still held; deposits and withdrawals.

    Args:
        report: Report dict from ``build_report`` (the narrative block is not
            read).

    Returns:
        Four paragraphs of plain text.
    """
    currency = report["header"]["currency"]
    rows: list[dict[str, Any]] = report["transactions"]
    # Report rows are newest first; the narrative lists events in date order.
    chronological = list(reversed(rows))
    return [
        _performance(report, currency),
        _sales_and_dividends(report, chronological, currency),
        _positions(report, currency),
        _flows(chronological, currency),
    ]
