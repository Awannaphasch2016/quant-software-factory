"""Decimal accounting engine: replays transactions with weighted-average cost.

All arithmetic uses ``decimal.Decimal``; nothing is rounded here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from .definitions import (
    BUY,
    CASH,
    DEPOSIT,
    DIVIDEND,
    SELL,
    WITHDRAWAL,
    ReportDefinition,
)
from .loader import Inputs, Transaction

ZERO = Decimal(0)
HUNDRED = Decimal(100)


@dataclass(frozen=True)
class TransactionResult:
    """Outcome of one transaction row."""

    txn: Transaction
    net_cash: Decimal
    realized_gain: Decimal | None = None
    avg_cost_after: Decimal | None = None
    gross_dividend: Decimal | None = None


@dataclass
class InstrumentResult:
    """Per-instrument figures for the period."""

    instrument: str
    opening_volume: int
    opening_cost: Decimal
    opening_price: Decimal | None
    closing_volume: int = 0
    closing_cost: Decimal = ZERO
    closing_price: Decimal | None = None
    realized_gain: Decimal = ZERO
    net_dividends: Decimal = ZERO
    weight_pct: Decimal = ZERO

    @property
    def opening_market_value(self) -> Decimal:
        if self.opening_volume == 0 or self.opening_price is None:
            return ZERO
        return self.opening_volume * self.opening_price

    @property
    def opening_unrealized(self) -> Decimal:
        return self.opening_market_value - self.opening_cost

    @property
    def closing_market_value(self) -> Decimal:
        if self.closing_volume == 0 or self.closing_price is None:
            return ZERO
        return self.closing_volume * self.closing_price

    @property
    def closing_unrealized(self) -> Decimal:
        return self.closing_market_value - self.closing_cost

    @property
    def change_in_unrealized(self) -> Decimal:
        return self.closing_unrealized - self.opening_unrealized

    @property
    def total_pnl(self) -> Decimal:
        return self.realized_gain + self.net_dividends + self.change_in_unrealized

    @property
    def average_cost(self) -> Decimal | None:
        if self.closing_volume == 0:
            return None
        return self.closing_cost / self.closing_volume

    @property
    def holding_return_pct(self) -> Decimal | None:
        if self.closing_cost == 0:
            return None
        return self.closing_unrealized / self.closing_cost * HUNDRED


@dataclass
class EngineResult:
    """Account-level figures for the period."""

    instruments: list[InstrumentResult]
    transactions: list[TransactionResult]
    opening_cash: Decimal
    closing_cash: Decimal
    deposits: Decimal
    withdrawals: Decimal
    cash_weight_pct: Decimal = ZERO
    by_instrument: dict[str, InstrumentResult] = field(default_factory=dict)

    @property
    def held_instruments(self) -> list[InstrumentResult]:
        return [i for i in self.instruments if i.closing_volume > 0]

    @property
    def opening_nav(self) -> Decimal:
        return sum(
            (i.opening_market_value for i in self.instruments), self.opening_cash
        )

    @property
    def closing_nav(self) -> Decimal:
        return sum(
            (i.closing_market_value for i in self.instruments), self.closing_cash
        )

    @property
    def realized_gain(self) -> Decimal:
        return sum((i.realized_gain for i in self.instruments), ZERO)

    @property
    def net_dividends(self) -> Decimal:
        return sum((i.net_dividends for i in self.instruments), ZERO)

    @property
    def change_in_unrealized(self) -> Decimal:
        return sum((i.change_in_unrealized for i in self.instruments), ZERO)

    @property
    def closing_unrealized(self) -> Decimal:
        return sum((i.closing_unrealized for i in self.instruments), ZERO)

    @property
    def total_pnl(self) -> Decimal:
        return self.realized_gain + self.net_dividends + self.change_in_unrealized

    @property
    def expected_closing_nav(self) -> Decimal:
        return self.opening_nav + self.deposits - self.withdrawals + self.total_pnl

    @property
    def period_return_pct(self) -> Decimal:
        opening_nav = self.opening_nav
        if opening_nav == 0:
            return ZERO
        return self.total_pnl / opening_nav * HUNDRED


def run_engine(inputs: Inputs, definition: ReportDefinition) -> EngineResult:
    """Replay the transactions and value positions. Inputs must pass Layer 1."""
    names = {name for name in inputs.opening_positions if name != CASH}
    names.update(t.instrument for t in inputs.transactions if t.instrument != CASH)

    by_instrument: dict[str, InstrumentResult] = {}
    for name in sorted(names):
        position = inputs.opening_positions.get(name)
        by_instrument[name] = InstrumentResult(
            instrument=name,
            opening_volume=position.volume if position is not None else 0,
            opening_cost=position.cost_value if position is not None else ZERO,
            opening_price=inputs.prices.get((definition.opening_date, name)),
        )

    volume = {name: r.opening_volume for name, r in by_instrument.items()}
    cost = {name: r.opening_cost for name, r in by_instrument.items()}
    cash = inputs.opening_cash
    deposits = ZERO
    withdrawals = ZERO
    results: dict[int, TransactionResult] = {}

    for txn in sorted(inputs.transactions, key=lambda t: (t.trade_date, t.index)):
        name = txn.instrument
        if txn.side == BUY:
            assert txn.qty is not None and txn.price is not None
            gross = txn.qty * txn.price + txn.fee
            cash -= gross
            cost[name] += gross
            volume[name] += txn.qty
            results[txn.index] = TransactionResult(
                txn, -gross, avg_cost_after=cost[name] / volume[name]
            )
        elif txn.side == SELL:
            assert txn.qty is not None and txn.price is not None
            avg_before = cost[name] / volume[name]
            proceeds = txn.qty * txn.price - txn.fee
            realized = proceeds - avg_before * txn.qty
            cash += proceeds
            volume[name] -= txn.qty
            cost[name] = (
                ZERO if volume[name] == 0 else cost[name] - avg_before * txn.qty
            )
            by_instrument[name].realized_gain += realized
            avg_after = cost[name] / volume[name] if volume[name] else None
            results[txn.index] = TransactionResult(
                txn, proceeds, realized_gain=realized, avg_cost_after=avg_after
            )
        elif txn.side == DIVIDEND:
            assert txn.qty is not None and txn.price is not None
            gross = txn.qty * txn.price
            net = gross - txn.tax
            cash += net
            by_instrument[name].net_dividends += net
            results[txn.index] = TransactionResult(txn, net, gross_dividend=gross)
        elif txn.side == DEPOSIT:
            assert txn.amount is not None
            cash += txn.amount
            deposits += txn.amount
            results[txn.index] = TransactionResult(txn, txn.amount)
        elif txn.side == WITHDRAWAL:
            assert txn.amount is not None
            cash -= txn.amount
            withdrawals += txn.amount
            results[txn.index] = TransactionResult(txn, -txn.amount)
        else:  # pragma: no cover - rejected by the input.sides check
            raise ValueError(f"unsupported side {txn.side!r}")

    for name, result in by_instrument.items():
        result.closing_volume = volume[name]
        result.closing_cost = cost[name]
        result.closing_price = inputs.prices.get((definition.as_of_date, name))

    engine_result = EngineResult(
        instruments=list(by_instrument.values()),
        transactions=[results[t.index] for t in inputs.transactions],
        opening_cash=inputs.opening_cash,
        closing_cash=cash,
        deposits=deposits,
        withdrawals=withdrawals,
        by_instrument=by_instrument,
    )
    closing_nav = engine_result.closing_nav
    if closing_nav != 0:
        for result in by_instrument.values():
            result.weight_pct = result.closing_market_value / closing_nav * HUNDRED
        engine_result.cash_weight_pct = cash / closing_nav * HUNDRED
    return engine_result
