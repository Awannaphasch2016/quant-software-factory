"""Template-based client narrative built only from report.json strings.

The narrative contains no dates, years, or other digits apart from values
copied verbatim from the report dict, so every number can be traced back to
report.json. Signed values are written as they appear in the tables.
"""

from __future__ import annotations

import re
from typing import Any

from .definitions import CASH, DIVIDEND, SELL

BANNED_PHRASES: tuple[str, ...] = (
    "robust",
    "impressive",
    "navigate",
    "in today's dynamic market",
    "it is worth noting",
    "delve",
    "recommend",
    "forecast",
    "expect",
    "should",
    "will",
)

NUMBER_RE = re.compile(r"(?<![\w.,-])-?\d{1,3}(?:,\d{3})*(?:\.\d+)?%?")

_SELL_OPENERS: tuple[str, ...] = (
    "The account sold",
    "It also sold",
    "In addition, the account sold",
)


def split_paragraphs(text: str) -> list[str]:
    """Split text into paragraphs separated by blank lines."""
    return [p.strip() for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]


def split_sentences(paragraph: str) -> list[str]:
    """Split a paragraph into sentences on ``.``, ``!`` or ``?`` plus space."""
    stripped = paragraph.strip()
    if not stripped:
        return []
    return re.split(r"(?<=[.!?])\s+", stripped)


def first_word(sentence: str) -> str:
    """Return the first word of a sentence, casefolded (empty if none)."""
    match = re.match(r"\s*([A-Za-z0-9'/-]+)", sentence)
    return match.group(1).casefold() if match else ""


def word_count(text: str) -> int:
    """Count whitespace-separated words."""
    return len(text.split())


def banned_phrases_in(text: str) -> list[str]:
    """Return the banned phrases found in text (case-insensitive, whole words)."""
    folded = text.casefold()
    return [
        phrase
        for phrase in BANNED_PHRASES
        if re.search(r"\b" + re.escape(phrase) + r"\b", folded)
    ]


def repeated_openers(text: str) -> list[str]:
    """Return first words shared by two consecutive sentences."""
    sentences = [s for p in split_paragraphs(text) for s in split_sentences(p)]
    words = [first_word(s) for s in sentences]
    return [a for a, b in zip(words, words[1:], strict=False) if a and a == b]


def _cash_flow_sentence(deposits: str, withdrawals: str, currency: str) -> str:
    no_deposits = deposits == "0.00"
    no_withdrawals = withdrawals == "0.00"
    if no_deposits and no_withdrawals:
        return "There were no deposits or withdrawals."
    if no_withdrawals:
        return (
            f"Deposits of {deposits} {currency} were added and no withdrawals "
            "were made."
        )
    if no_deposits:
        return (
            f"Withdrawals of {withdrawals} {currency} were made and no deposits "
            "were added."
        )
    return (
        f"Deposits of {deposits} {currency} were added and withdrawals of "
        f"{withdrawals} {currency} were made."
    )


def build_narrative(report: dict[str, Any]) -> list[str]:
    """Return 2 to 4 short paragraphs describing the period."""
    currency = report["header"]["currency"]
    kpi = report["kpi_summary"]
    recon = report["reconciliation"]

    cash_flows = _cash_flow_sentence(recon["deposits"], recon["withdrawals"], currency)
    overview = (
        f"During the period, the account's net asset value moved from "
        f"{recon['opening_nav']} {currency} to {recon['actual_closing_nav']} "
        f"{currency}. Total profit and loss was {kpi['total_pnl']} {currency}, a "
        f"simple period return of {kpi['period_return_pct']} on opening net asset "
        f"value. {cash_flows}"
    )

    chronological = list(reversed(report["transactions"]["rows"]))
    activity: list[str] = []
    sells = [row for row in chronological if row["side"] == SELL]
    for index, row in enumerate(sells):
        opener = _SELL_OPENERS[index % len(_SELL_OPENERS)]
        activity.append(
            f"{opener} {row['qty']} {row['instrument']} shares for net proceeds of "
            f"{row['net_cash_amount']} {currency} and a realized capital gain of "
            f"{row['realized_gain']} {currency}."
        )
    dividends = [row for row in chronological if row["side"] == DIVIDEND]
    for index, row in enumerate(dividends):
        if index % 2 == 0:
            activity.append(
                f"{row['instrument']} paid a net dividend of {row['net_cash_amount']} "
                f"{currency} after withholding tax of {row['tax']} {currency}."
            )
        else:
            activity.append(
                f"A further net dividend of {row['net_cash_amount']} {currency} was "
                f"received from {row['instrument']}, after withholding tax of "
                f"{row['tax']} {currency}."
            )
    if not activity:
        activity.append("No shares were sold and no dividends were received.")

    holdings = report["holdings"]["rows"]
    positions: list[str] = []
    for row in holdings:
        if row["instrument"] == CASH:
            continue
        sentence = (
            f"{row['instrument']} showed unrealized P/L of {row['unrealized_pnl']} "
            f"{currency}"
        )
        if row["holding_return_pct"] is not None:
            sentence += f", a holding return of {row['holding_return_pct']}"
        positions.append(sentence + ".")
    cash_row = next(row for row in holdings if row["instrument"] == CASH)
    if positions:
        positions[0] = "At the end of the period, " + positions[0]
        positions.append(
            f"Cash stood at {cash_row['market_value']} {currency}, or "
            f"{cash_row['weight_pct']} of net asset value."
        )
    else:
        positions.append(
            f"At the end of the period, the account held only cash of "
            f"{cash_row['market_value']} {currency}."
        )

    return [overview, " ".join(activity), " ".join(positions)]


def render_narrative(paragraphs: list[str]) -> str:
    """Join paragraphs for narrative.md with a single trailing newline."""
    return "\n\n".join(paragraphs) + "\n"
