"""Display formatting shared by report.json, report.md and narrative.md.

Values are computed with full ``Decimal`` precision and rounded only here,
to two decimals with ``ROUND_HALF_UP``.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")
ZERO_DISPLAY = Decimal("0.00")


def round_display(value: Decimal) -> Decimal:
    """Round to two decimals, half up, and turn ``-0.00`` into ``0.00``."""
    quantized = value.quantize(CENT, rounding=ROUND_HALF_UP)
    return quantized if quantized != 0 else ZERO_DISPLAY


def fmt_money(value: Decimal) -> str:
    """Format a THB amount or price, e.g. ``17,835.00`` or ``-3,037.00``."""
    return f"{round_display(value):,.2f}"


def fmt_pct(value: Decimal) -> str:
    """Format a percentage already expressed in percent, e.g. ``6.12%``."""
    return f"{round_display(value):,.2f}%"


def fmt_int(value: int) -> str:
    """Format a share count with thousands separators, e.g. ``9,000``."""
    return f"{value:,}"
