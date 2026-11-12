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

## Returns & Transactions report

Builds a client returns and transactions report from CSV inputs using only the
standard library:

```bash
python -m quant_software_factory.reports.returns_transactions \
    data/examples/demo_coop_rg_2026_10 reports/demo_coop_rg_2026_10
```

- Inputs: `opening_positions.csv`, `transactions.csv` and `prices.csv` in the
  input directory. The report definition (account, period, as-of date) is looked
  up by the input directory name, or by `--report-id ID`.
- Outputs: `report.md` (GitHub-flavored Markdown, one section per block),
  `report.json` (numbers as display strings), `narrative.md` and `checks.json`
  (a list of `{name, passed, expected, actual}`).
- Exit codes: `0` when every input, accounting and narrative check passes;
  `1` when any check fails (only `checks.json` is written and stale report
  files are removed); `2` for usage errors such as an unknown report ID.
- All calculations use `decimal.Decimal`; values are rounded only for display,
  to 2 decimals with `ROUND_HALF_UP`. Reruns on the same input are
  byte-identical.

## Development

```bash
ruff check .
ruff format --check .
mypy
pytest
```
