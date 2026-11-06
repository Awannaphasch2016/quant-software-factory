"""Risk metrics for evaluating trading strategies."""

from __future__ import annotations

import math
import numbers
from collections.abc import Sequence


def calculate_max_drawdown(equity_curve: Sequence[float]) -> float:
    """Calculate the maximum drawdown of a portfolio equity curve.

    The drawdown at each point is measured against the highest equity observed
    up to and including that point::

        drawdown_t = (running_peak_t - equity_t) / running_peak_t
        maximum_drawdown = max(drawdown_t)

    The calculation is a single O(n) pass and does not modify ``equity_curve``.

    Args:
        equity_curve: Chronological sequence of portfolio equity values. Every
            value must be a finite, strictly positive real number.

    Returns:
        The maximum drawdown as a fraction in the range ``[0, 1)``. Returns
        ``0.0`` when no drawdown occurs.

    Raises:
        ValueError: If ``equity_curve`` is empty, or contains a value that is
            zero, negative, NaN, infinite, or too large to represent as a float.
        TypeError: If ``equity_curve`` contains a value that is not a real
            number (``bool`` values are rejected as well).
    """
    peak: float | None = None
    max_drawdown = 0.0

    for index, raw in enumerate(equity_curve):
        if isinstance(raw, bool) or not isinstance(raw, numbers.Real):
            raise TypeError(
                f"equity_curve[{index}] must be a real number, got {type(raw).__name__}"
            )
        try:
            value = float(raw)
        except OverflowError:
            raise ValueError(
                f"equity_curve[{index}] is too large to represent as a float"
            ) from None
        if not math.isfinite(value) or value <= 0:
            raise ValueError(
                f"equity_curve[{index}] must be finite and positive, got {raw!r}"
            )

        if peak is None or value > peak:
            peak = value
        else:
            drawdown = (peak - value) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown

    if peak is None:
        raise ValueError("equity_curve must not be empty")

    return max_drawdown
