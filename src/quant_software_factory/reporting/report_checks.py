"""Layer B number checks (B0-B8) and writing checks (W1-W5) for the report.

Number checks compare unrounded ``Decimal`` values from the datasets, except
B4, which compares the built report blocks with each other. All results use the
``CheckResult`` format of the Layer A checks with layer ``"B"``.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator, Sequence
from decimal import Decimal
from typing import Any

from .checks import CheckResult
from .returns_transactions import CASH, TOTAL, Report, ReportInputs, parse_amount

LAYER = "B"
TOLERANCE = Decimal("0.01")
OK = "ok"

B0_NAME = "B0_mapped_values"

_EXPECTED: dict[str, str] = {
    B0_NAME: "every mapped value present exactly once",
    "B1_holdings_total": "sum of holdings market_value + cash = nav_daily.nav",
    "B2_securities_value": "sum of holdings market_value = nav_daily.market_value",
    "B3_holding_rows": "market_value - cost_value = unrealized_pl on every row",
    "B4_same_figure": (
        "kpi net_asset_value = holdings Total market_value; "
        "kpi cash = holdings CASH market_value"
    ),
    "B5_accounting_identity": (
        "opening nav + deposits - withdrawals + total_pl = closing nav"
    ),
    "B6_pl_parts": "capital_gain + dividend + unrealized_change = total_pl",
    "B7_realized_capital_gain": ("sum of SELL realized_pl = performance.capital_gain"),
    "B7_dividends": "sum of DIVIDEND amount = performance.dividend",
    "B8_narrative_numbers": "every money or percent value appears in report.json",
    "W1_banned_phrases": "no banned phrase",
    "W2_no_negative_gain": "no 'gain of -'",
    "W3_sentence_openers": "no two consecutive sentences start with the same word",
    "W4_length": "2-4 paragraphs, under 180 words",
    "W5_forecast_words": "no forecast or recommendation words",
}

LAYER_B_CHECK_NAMES: tuple[str, ...] = tuple(sorted(_EXPECTED))

BANNED_PHRASES = (
    "robust",
    "impressive",
    "navigate",
    "it is worth noting",
    "delve",
    "in today's",
)
MIN_PARAGRAPHS = 2
MAX_PARAGRAPHS = 4
MAX_WORDS = 180  # exclusive

_NUMBER_RE = re.compile(r"(?<![\d.,])-?\d[\d,]*\.\d+%?")
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_WORD_RE = re.compile(r"[A-Za-z0-9']+")
_FORECAST_RE = re.compile(r"\b(will|expect\w*|should|recommend\w*)\b", re.IGNORECASE)


def _result(name: str, passed: bool, actual: str) -> CheckResult:
    return CheckResult(name, LAYER, passed, _EXPECTED[name], actual)


def not_run_results(names: Iterable[str], reason: str) -> list[CheckResult]:
    """Return failed results for checks that could not run."""
    return [CheckResult(n, LAYER, False, _EXPECTED[n], reason) for n in names]


def mapped_values_check(problems: Sequence[str]) -> CheckResult:
    """B0: report the problems found while loading the mapped values."""
    return _result(B0_NAME, not problems, "; ".join(problems) if problems else OK)


def _close(a: Decimal, b: Decimal) -> bool:
    return abs(a - b) <= TOLERANCE


def _compare(name: str, left: Decimal, right: Decimal) -> CheckResult:
    return _result(name, _close(left, right), f"{left} vs {right}")


def _total(values: Iterable[Decimal]) -> Decimal:
    return sum(values, Decimal(0))


def number_checks(inputs: ReportInputs, report: Report) -> list[CheckResult]:
    """Run B1-B7 on the parsed inputs and B4 on the built report.

    Args:
        inputs: Parsed inputs the report was built from.
        report: Report dict from ``build_report``.

    Returns:
        One result per check, in name order.
    """
    securities = _total(h.market_value for h in inputs.holdings)
    row_errors = [
        f"{h.instrument}: {h.market_value - h.cost_value} vs {h.unrealized_pl}"
        for h in inputs.holdings
        if not _close(h.market_value - h.cost_value, h.unrealized_pl)
    ]
    deposits = _total(f.amount for f in inputs.cash_flows if f.flow_type == "DEPOSIT")
    withdrawals = _total(
        f.amount for f in inputs.cash_flows if f.flow_type == "WITHDRAWAL"
    )
    realized = _total(
        t.realized_pl
        for t in inputs.trades
        if t.side == "SELL" and t.realized_pl is not None
    )
    dividends = _total(t.amount for t in inputs.trades if t.side == "DIVIDEND")
    return [
        _compare("B1_holdings_total", securities + inputs.cash, inputs.nav),
        _compare("B2_securities_value", securities, inputs.securities_value),
        _result("B3_holding_rows", not row_errors, "; ".join(row_errors) or OK),
        same_figure_check(report),
        _compare(
            "B5_accounting_identity",
            inputs.opening_nav + deposits - withdrawals + inputs.total_pl,
            inputs.nav,
        ),
        _compare(
            "B6_pl_parts",
            inputs.capital_gain + inputs.dividend + inputs.unrealized_change,
            inputs.total_pl,
        ),
        _compare("B7_dividends", dividends, inputs.dividend),
        _compare("B7_realized_capital_gain", realized, inputs.capital_gain),
    ]


def _holding_value(report: Report, instrument: str) -> str | None:
    for row in report["holdings"]:
        if row["instrument"] == instrument:
            value: str | None = row["market_value"]
            return value
    return None


def same_figure_check(report: Report) -> CheckResult:
    """B4: NAV and cash in kpi_summary match the holdings Total and CASH rows."""
    name = "B4_same_figure"
    kpi = report["kpi_summary"]
    pairs = [
        ("net_asset_value", kpi["net_asset_value"], _holding_value(report, TOTAL)),
        ("cash", kpi["cash"], _holding_value(report, CASH)),
    ]
    parts: list[str] = []
    passed = True
    for label, left_text, right_text in pairs:
        left = parse_amount(left_text or "")
        right = parse_amount(right_text or "")
        if left is None or right is None or not _close(left, right):
            passed = False
        parts.append(f"{label} {left_text} vs {right_text}")
    return _result(name, passed, "; ".join(parts))


def _strings(value: Any) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)


def _sentences(paragraphs: Sequence[str]) -> list[str]:
    return [
        s for p in paragraphs for s in _SENTENCE_SPLIT_RE.split(p.strip()) if s.strip()
    ]


def _first_word(sentence: str) -> str:
    match = _WORD_RE.search(sentence)
    return match.group(0).lower() if match else ""


def narrative_checks(paragraphs: Sequence[str], report: Report) -> list[CheckResult]:
    """Run B8 and W1-W5 on the narrative paragraphs.

    Args:
        paragraphs: Narrative paragraphs.
        report: Report dict; its ``narrative`` block is ignored by B8.

    Returns:
        One result per check, in name order.
    """
    text = "\n\n".join(paragraphs)
    lowered = text.lower()

    allowed: set[str] = set()
    for key, block in report.items():
        if key == "narrative":
            continue
        for value in _strings(block):
            allowed.add(value)
            if value.startswith("-"):
                allowed.add(value[1:])
    unknown = [t for t in _NUMBER_RE.findall(text) if t not in allowed]
    b8_actual = "not in report.json: " + ", ".join(unknown) if unknown else OK

    banned = [p for p in BANNED_PHRASES if p in lowered]

    openers = [_first_word(s) for s in _sentences(paragraphs)]
    repeated = sorted({a for a, b in zip(openers, openers[1:], strict=False) if a == b})

    words = len(text.split())
    count = len(paragraphs)
    length_ok = MIN_PARAGRAPHS <= count <= MAX_PARAGRAPHS and words < MAX_WORDS

    forecast = sorted({m.lower() for m in _FORECAST_RE.findall(text)})

    return [
        _result("B8_narrative_numbers", not unknown, b8_actual),
        _result(
            "W1_banned_phrases",
            not banned,
            "found: " + ", ".join(banned) if banned else OK,
        ),
        _result(
            "W2_no_negative_gain",
            "gain of -" not in lowered,
            "found: 'gain of -'" if "gain of -" in lowered else OK,
        ),
        _result(
            "W3_sentence_openers",
            not repeated,
            "repeated: " + ", ".join(repeated) if repeated else OK,
        ),
        _result("W4_length", length_ok, f"{count} paragraphs, {words} words"),
        _result(
            "W5_forecast_words",
            not forecast,
            "found: " + ", ".join(forecast) if forecast else OK,
        ),
    ]
