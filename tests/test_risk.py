"""Tests for quant_software_factory.risk."""

from __future__ import annotations

import math
import random
from collections.abc import Sequence

import pytest

from quant_software_factory.risk import calculate_max_drawdown


def _brute_force_max_drawdown(equity_curve: Sequence[float]) -> float:
    """O(n^2) reference implementation used to cross-check results."""
    worst = 0.0
    for j, value in enumerate(equity_curve):
        peak = max(equity_curve[: j + 1])
        worst = max(worst, (peak - value) / peak)
    return worst


@pytest.mark.parametrize(
    ("equity_curve", "expected"),
    [
        ([100, 120, 90, 110], 0.25),
        ([100, 110, 120], 0.0),
        ([100, 80, 120, 90, 60], 0.5),
        ([100, 100, 100], 0.0),
        ([100], 0.0),
    ],
)
def test_issue_examples(equity_curve: list[float], expected: float) -> None:
    assert calculate_max_drawdown(equity_curve) == pytest.approx(expected)


def test_empty_input_raises_value_error() -> None:
    with pytest.raises(ValueError, match="empty"):
        calculate_max_drawdown([])


@pytest.mark.parametrize(
    "equity_curve",
    [
        [0],
        [-1],
        [100, 0],
        [100, -5],
        [math.nan],
        [100, math.nan, 90],
        [math.inf],
        [100, -math.inf],
        [10**400],
    ],
)
def test_invalid_values_raise_value_error(equity_curve: list[float]) -> None:
    with pytest.raises(ValueError):
        calculate_max_drawdown(equity_curve)


def test_value_error_message_includes_index() -> None:
    with pytest.raises(ValueError, match=r"equity_curve\[2\]"):
        calculate_max_drawdown([100, 90, 0])


@pytest.mark.parametrize(
    "equity_curve",
    [
        [True],
        [100, False],
        ["100"],
        [None],
        "100",
    ],
)
def test_non_numeric_values_raise_type_error(equity_curve: Sequence[object]) -> None:
    with pytest.raises(TypeError):
        calculate_max_drawdown(equity_curve)  # type: ignore[arg-type]


def test_input_is_not_mutated() -> None:
    equity_curve = [100.0, 120.0, 90.0, 110.0]
    snapshot = list(equity_curve)
    calculate_max_drawdown(equity_curve)
    assert equity_curve == snapshot


def test_tuple_input_is_accepted() -> None:
    assert calculate_max_drawdown((100, 120, 90, 110)) == pytest.approx(0.25)


@pytest.mark.parametrize(
    "equity_curve",
    [
        [100, 120, 90, 110],
        [100, 110, 120],
        [100],
    ],
)
def test_returns_builtin_float(equity_curve: list[int]) -> None:
    assert type(calculate_max_drawdown(equity_curve)) is float


def test_random_curves_match_brute_force_reference() -> None:
    rng = random.Random(0)
    for _ in range(200):
        length = rng.randint(1, 30)
        equity_curve = [rng.uniform(0.01, 1000.0) for _ in range(length)]
        result = calculate_max_drawdown(equity_curve)
        assert 0.0 <= result <= 1.0
        assert result == pytest.approx(_brute_force_max_drawdown(equity_curve))


@pytest.mark.parametrize(
    "equity_curve",
    [
        [100, 1e-15],
        [1e308, 5e-324],
    ],
)
def test_extreme_magnitudes_stay_within_unit_interval(
    equity_curve: list[float],
) -> None:
    result = calculate_max_drawdown(equity_curve)
    assert 0.0 <= result <= 1.0
    assert result == pytest.approx(1.0)


def test_extreme_magnitudes_without_drawdown() -> None:
    assert calculate_max_drawdown([5e-324, 1e-300, 1e308]) == 0.0


def test_package_level_import() -> None:
    import quant_software_factory

    assert quant_software_factory.calculate_max_drawdown is calculate_max_drawdown
    assert "calculate_max_drawdown" in quant_software_factory.__all__
