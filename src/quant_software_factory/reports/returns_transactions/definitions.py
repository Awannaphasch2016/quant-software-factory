"""Static definitions for the Returns & Transactions report."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

REPORT_TYPE = "returns_transactions"
TITLE = "Returns & Transactions Report"
DISCLAIMER = (
    "This report is prepared for the named account holder only. It is not an "
    "offer, solicitation, or investment advice. Past performance does not "
    "indicate future results."
)
PERIOD_RETURN_BASIS = "simple return on opening NAV, not time-weighted"

CASH = "CASH"

BLOCK_IDS: tuple[str, ...] = (
    "header",
    "kpi_summary",
    "pnl_breakdown",
    "holdings",
    "transactions",
    "reconciliation",
    "narrative",
    "disclaimer",
)

BLOCK_TITLES: dict[str, str] = {
    "header": "Header",
    "kpi_summary": "KPI Summary",
    "pnl_breakdown": "P/L Breakdown",
    "holdings": "Holdings",
    "transactions": "Transactions",
    "reconciliation": "Reconciliation",
    "narrative": "Narrative",
    "disclaimer": "Disclaimer",
}

BUY = "BUY"
SELL = "SELL"
DIVIDEND = "DIVIDEND"
DEPOSIT = "DEPOSIT"
WITHDRAWAL = "WITHDRAWAL"
ALLOWED_SIDES: tuple[str, ...] = (BUY, SELL, DIVIDEND, DEPOSIT, WITHDRAWAL)
SHARE_SIDES: tuple[str, ...] = (BUY, SELL, DIVIDEND)
CASH_FLOW_SIDES: tuple[str, ...] = (DEPOSIT, WITHDRAWAL)

OPENING_POSITIONS_FILE = "opening_positions.csv"
TRANSACTIONS_FILE = "transactions.csv"
PRICES_FILE = "prices.csv"

OPENING_POSITIONS_COLUMNS: tuple[str, ...] = ("instrument", "volume", "cost_value")
TRANSACTIONS_COLUMNS: tuple[str, ...] = (
    "trade_date",
    "instrument",
    "side",
    "qty",
    "price",
    "fee",
    "tax",
    "amount",
)
PRICES_COLUMNS: tuple[str, ...] = ("date", "instrument", "close")

EXPECTED_COLUMNS: dict[str, tuple[str, ...]] = {
    OPENING_POSITIONS_FILE: OPENING_POSITIONS_COLUMNS,
    TRANSACTIONS_FILE: TRANSACTIONS_COLUMNS,
    PRICES_FILE: PRICES_COLUMNS,
}


@dataclass(frozen=True)
class ReportDefinition:
    """Metadata for one report instance (account, period, dates)."""

    report_id: str
    client: str
    account: str
    strategy: str
    period_start: date
    period_end: date
    opening_date: date
    as_of_date: date
    currency: str
    language: str


REPORT_DEFINITIONS: dict[str, ReportDefinition] = {
    "demo_coop_rg_2026_10": ReportDefinition(
        report_id="demo_coop_rg_2026_10",
        client="DEMO-COOP",
        account="DEMO-0001",
        strategy="Reverse Grid",
        period_start=date(2026, 10, 1),
        period_end=date(2026, 10, 31),
        opening_date=date(2026, 9, 30),
        as_of_date=date(2026, 10, 30),
        currency="THB",
        language="en",
    ),
}
