"""Build the report dict (report.json) and render it as Markdown (report.md).

Every number in the dict is a display string produced by ``formatting``;
not-applicable cells are ``None`` (JSON ``null``).
"""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Any

from .definitions import (
    BLOCK_IDS,
    BLOCK_TITLES,
    CASH,
    DISCLAIMER,
    PERIOD_RETURN_BASIS,
    SELL,
    TITLE,
    ReportDefinition,
)
from .engine import HUNDRED, EngineResult
from .formatting import fmt_int, fmt_money, fmt_pct

Report = dict[str, Any]
Row = dict[str, str | None]


def _opt_money(value: Decimal | None) -> str | None:
    return None if value is None else fmt_money(value)


def _opt_pct(value: Decimal | None) -> str | None:
    return None if value is None else fmt_pct(value)


def _opt_int(value: int | None) -> str | None:
    return None if value is None else fmt_int(value)


def build_report(definition: ReportDefinition, result: EngineResult) -> Report:
    """Return the report as an ordered dict keyed by ``BLOCK_IDS``.

    The ``narrative`` block is left empty; the caller fills it from this dict.
    """
    header = {
        "title": TITLE,
        "report_id": definition.report_id,
        "client": definition.client,
        "account": definition.account,
        "strategy": definition.strategy,
        "period_start": definition.period_start.isoformat(),
        "period_end": definition.period_end.isoformat(),
        "opening_date": definition.opening_date.isoformat(),
        "as_of_date": definition.as_of_date.isoformat(),
        "currency": definition.currency,
    }

    kpi_summary = {
        "closing_nav": fmt_money(result.closing_nav),
        "total_pnl": fmt_money(result.total_pnl),
        "period_return_pct": fmt_pct(result.period_return_pct),
        "period_return_basis": PERIOD_RETURN_BASIS,
        "realized_capital_gain": fmt_money(result.realized_gain),
        "net_dividends": fmt_money(result.net_dividends),
        "unrealized_pnl": fmt_money(result.closing_unrealized),
    }

    pnl_rows: list[Row] = [
        {
            "instrument": i.instrument,
            "realized_capital_gain": fmt_money(i.realized_gain),
            "net_dividend": fmt_money(i.net_dividends),
            "change_in_unrealized": fmt_money(i.change_in_unrealized),
            "total_pnl": fmt_money(i.total_pnl),
        }
        for i in result.instruments
    ]
    pnl_total: Row = {
        "instrument": "Total",
        "realized_capital_gain": fmt_money(result.realized_gain),
        "net_dividend": fmt_money(result.net_dividends),
        "change_in_unrealized": fmt_money(result.change_in_unrealized),
        "total_pnl": fmt_money(result.total_pnl),
    }

    holding_rows: list[Row] = [
        {
            "instrument": i.instrument,
            "volume": fmt_int(i.closing_volume),
            "average_cost": _opt_money(i.average_cost),
            "cost_value": fmt_money(i.closing_cost),
            "market_price": _opt_money(i.closing_price),
            "market_value": fmt_money(i.closing_market_value),
            "unrealized_pnl": fmt_money(i.closing_unrealized),
            "holding_return_pct": _opt_pct(i.holding_return_pct),
            "weight_pct": fmt_pct(i.weight_pct),
        }
        for i in result.held_instruments
    ]
    holding_rows.append(
        {
            "instrument": CASH,
            "volume": None,
            "average_cost": None,
            "cost_value": fmt_money(result.closing_cash),
            "market_price": None,
            "market_value": fmt_money(result.closing_cash),
            "unrealized_pnl": fmt_money(Decimal(0)),
            "holding_return_pct": None,
            "weight_pct": fmt_pct(result.cash_weight_pct),
        }
    )
    total_cost = sum((i.closing_cost for i in result.held_instruments), Decimal(0))
    holdings_total: Row = {
        "instrument": "Total",
        "volume": None,
        "average_cost": None,
        "cost_value": fmt_money(total_cost + result.closing_cash),
        "market_price": None,
        "market_value": fmt_money(result.closing_nav),
        "unrealized_pnl": fmt_money(result.closing_unrealized),
        "holding_return_pct": None,
        "weight_pct": fmt_pct(HUNDRED if result.closing_nav != 0 else Decimal(0)),
    }

    newest_first = sorted(
        result.transactions,
        key=lambda r: (r.txn.trade_date, r.txn.index),
        reverse=True,
    )
    transaction_rows: list[Row] = [
        {
            "trade_date": r.txn.trade_date.isoformat(),
            "instrument": r.txn.instrument,
            "side": r.txn.side,
            "qty": _opt_int(r.txn.qty),
            "price": _opt_money(r.txn.price),
            "fee": fmt_money(r.txn.fee),
            "tax": fmt_money(r.txn.tax),
            "net_cash_amount": fmt_money(r.net_cash),
            "realized_gain": (
                _opt_money(r.realized_gain) if r.txn.side == SELL else None
            ),
        }
        for r in newest_first
    ]

    expected_nav = result.expected_closing_nav
    closing_nav = result.closing_nav
    reconciliation = {
        "opening_nav": fmt_money(result.opening_nav),
        "deposits": fmt_money(result.deposits),
        "withdrawals": fmt_money(result.withdrawals),
        "total_pnl": fmt_money(result.total_pnl),
        "expected_closing_nav": fmt_money(expected_nav),
        "actual_closing_nav": fmt_money(closing_nav),
        "difference": fmt_money(closing_nav - expected_nav),
    }

    blocks: dict[str, Any] = {
        "header": header,
        "kpi_summary": kpi_summary,
        "pnl_breakdown": {"rows": pnl_rows, "total": pnl_total},
        "holdings": {"rows": holding_rows, "total": holdings_total},
        "transactions": {"rows": transaction_rows},
        "reconciliation": reconciliation,
        "narrative": {"paragraphs": []},
        "disclaimer": {"text": DISCLAIMER},
    }
    return {block_id: blocks[block_id] for block_id in BLOCK_IDS}


def dump_json(obj: object) -> str:
    """Serialize deterministically: fixed key order, LF, trailing newline."""
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def _cell(value: str | None) -> str:
    return "" if value is None else value.replace("|", "\\|")


def _table(
    headers: list[str], rows: list[list[str | None]], numeric: list[bool]
) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---:" if n else "---" for n in numeric) + " |",
    ]
    lines.extend("| " + " | ".join(_cell(v) for v in row) + " |" for row in rows)
    return lines


_PNL_COLUMNS = [
    ("instrument", "Instrument", False),
    ("realized_capital_gain", "Realized capital gain", True),
    ("net_dividend", "Net dividend", True),
    ("change_in_unrealized", "Change in unrealized", True),
    ("total_pnl", "Total P/L", True),
]
_HOLDING_COLUMNS = [
    ("instrument", "Instrument", False),
    ("volume", "Volume", True),
    ("average_cost", "Average cost", True),
    ("cost_value", "Cost value", True),
    ("market_price", "Market price", True),
    ("market_value", "Market value", True),
    ("unrealized_pnl", "Unrealized P/L", True),
    ("holding_return_pct", "Holding return %", True),
    ("weight_pct", "Weight %", True),
]
_TRANSACTION_COLUMNS = [
    ("trade_date", "Date", False),
    ("instrument", "Instrument", False),
    ("side", "Side", False),
    ("qty", "Qty", True),
    ("price", "Price", True),
    ("fee", "Fee", True),
    ("tax", "Tax", True),
    ("net_cash_amount", "Net cash amount", True),
    ("realized_gain", "Realized gain", True),
]


def _rows_table(
    columns: list[tuple[str, str, bool]], rows: list[dict[str, str | None]]
) -> list[str]:
    return _table(
        [label for _, label, _ in columns],
        [[row[key] for key, _, _ in columns] for row in rows],
        [numeric for _, _, numeric in columns],
    )


def _block_lines(report: Report, block_id: str) -> list[str]:
    block = report[block_id]
    if block_id == "header":
        period = f"{block['period_start']} to {block['period_end']}"
        pairs: list[list[str | None]] = [
            ["Client", block["client"]],
            ["Account", block["account"]],
            ["Strategy", block["strategy"]],
            ["Period", period],
            ["Opening date", block["opening_date"]],
            ["As-of date", block["as_of_date"]],
            ["Report ID", block["report_id"]],
            ["Currency", block["currency"]],
        ]
        return _table(["Field", "Value"], pairs, [False, False])
    if block_id == "kpi_summary":
        currency = report["header"]["currency"]
        pairs = [
            [f"Closing NAV ({currency})", block["closing_nav"]],
            [f"Total P/L ({currency})", block["total_pnl"]],
            [
                f"Period return % ({block['period_return_basis']})",
                block["period_return_pct"],
            ],
            [f"Realized capital gain ({currency})", block["realized_capital_gain"]],
            [f"Net dividends ({currency})", block["net_dividends"]],
            [f"Unrealized P/L, closing ({currency})", block["unrealized_pnl"]],
        ]
        return _table(["Metric", "Value"], pairs, [False, True])
    if block_id == "pnl_breakdown":
        return _rows_table(_PNL_COLUMNS, [*block["rows"], block["total"]])
    if block_id == "holdings":
        return _rows_table(_HOLDING_COLUMNS, [*block["rows"], block["total"]])
    if block_id == "transactions":
        return _rows_table(_TRANSACTION_COLUMNS, block["rows"])
    if block_id == "reconciliation":
        currency = report["header"]["currency"]
        labels = [
            ("opening_nav", "Opening NAV"),
            ("deposits", "Deposits"),
            ("withdrawals", "Withdrawals"),
            ("total_pnl", "Total P/L"),
            ("expected_closing_nav", "Expected closing NAV"),
            ("actual_closing_nav", "Actual closing NAV"),
            ("difference", "Difference"),
        ]
        pairs = [[f"{label} ({currency})", block[key]] for key, label in labels]
        return _table(["Item", "Value"], pairs, [False, True])
    if block_id == "narrative":
        lines: list[str] = []
        for index, paragraph in enumerate(block["paragraphs"]):
            if index:
                lines.append("")
            lines.append(paragraph)
        return lines
    if block_id == "disclaimer":
        return [block["text"]]
    raise ValueError(f"unknown block {block_id!r}")


def render_markdown(report: Report) -> str:
    """Render GitHub-flavored Markdown with one ``##`` section per block."""
    lines = [f"# {report['header']['title']}"]
    for block_id in BLOCK_IDS:
        lines.extend(["", f"## {BLOCK_TITLES[block_id]}", ""])
        lines.extend(_block_lines(report, block_id))
    return "\n".join(lines) + "\n"
