# quant-software-factory

Reusable quantitative finance utilities for evaluating trading strategies.

## Installation

```bash
pip install -e .          # library only (no runtime dependencies)
pip install -e ".[dev]"   # plus pytest, ruff and mypy for development
```

## Usage

```python
from quant_software_factory import calculate_max_drawdown

calculate_max_drawdown([100, 120, 90, 110])  # 0.25
calculate_max_drawdown([100, 110, 120])  # 0.0
```

`calculate_max_drawdown` returns the largest decline from a running peak as a
fraction in `[0, 1]` (exactly `1.0` is possible through floating-point rounding
when a value is negligible relative to its peak). It raises `ValueError` for an
empty sequence or for any value that is zero, negative, NaN or infinite, and
`TypeError` for non-numeric values (including `bool` and `Decimal`).

## Development

```bash
ruff check .
ruff format --check .
mypy
pytest
```

## Remote script execution

`calculate_max_drawdown` stays a pure function that returns a float.
`scripts/calculate_max_drawdown.py` is the allowlisted entry point a remote
runner can execute: one JSON object on stdin, one JSON object on stdout.
The operator guide is
[docs/remote-script-execution.md](docs/remote-script-execution.md).
