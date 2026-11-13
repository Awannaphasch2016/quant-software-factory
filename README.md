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

## Report data checks

Reports are built from datasets the pipeline has already computed. Report code
reads them only through `DataSource.load(dataset, as_of, accounts)`, a
`typing.Protocol` in `quant_software_factory.reporting`. `FixtureSource(root)`
implements it by reading `<root>/<dataset>.csv`; the fields and types of each
dataset are defined once in `reporting.schema.SCHEMAS`.

Run the Layer A data checks (A1 freshness, A2 completeness, A3 schema):

```bash
python -m quant_software_factory.reporting.check_data \
    data/fixtures/demo_coop_rg_2026_10_v2 --account DEMO-0001 \
    --opening 2026-09-30 --as-of 2026-10-30 --out reports/demo_coop_rg_2026_10_v2
```

This writes `checks.json` to the `--out` directory: a list of
`{"name", "layer", "passed", "expected", "actual"}` objects sorted by name.
A check that could not run because its dataset failed A3 has `"passed": false`
and the reason in `actual`. The exit code is 0 when all checks pass and 1
otherwise. The output is deterministic: two runs on the same input produce
byte-identical files.

## Returns & Transactions report

Build the report for one account from the precomputed datasets:

```bash
python -m quant_software_factory.reporting.returns_transactions \
    data/fixtures/demo_coop_rg_2026_10_v2 reports/demo_coop_rg_2026_10_v2 \
    --account DEMO-0001 --opening 2026-09-30 --as-of 2026-10-30
```

The report ID is the output folder name. The period is the calendar month of
the as-of date; transactions and cash flows are the rows from the first day of
that month up to the as-of date. Every figure is read through `load(...)` and
shown as the dataset provides it; the holdings Total row is a display sum and
withdrawals are shown as negative amounts. Money uses 2 decimals and thousands
separators (`Decimal`, ROUND_HALF_UP); values that do not apply are `null`.

The command runs the Layer A data checks first. If they pass, it builds the
report and runs the Layer B checks (layer `"B"`, tolerance 0.01):

- B0 every mapped value is present exactly once; B1 holdings market value plus
  cash equals NAV; B2 holdings market value equals securities value; B3
  market value minus cost equals unrealized P/L on each row; B4 KPI NAV and
  cash equal the holdings Total and CASH rows; B5 opening NAV plus deposits
  minus withdrawals plus total P/L equals closing NAV; B6 P/L parts add up to
  total P/L; B7 SELL realized P/L and DIVIDEND amounts tie to `performance`;
  B8 every money or percent value in the narrative appears in `report.json`.
- W1 no banned phrase; W2 no "gain of -"; W3 no two consecutive sentences
  start with the same word; W4 2 to 4 paragraphs and under 180 words; W5 no
  forecast or recommendation words.

The narrative is generated from `report.json` with fixed sentence templates.

When every check passes, the command writes `report.md`, `report.json`,
`narrative.md` and `checks.json` (Layer A and B results sorted by name) and
exits 0. When any check fails, it writes only `checks.json`, removes stale
`report.md`, `report.json` and `narrative.md`, and exits 1. If Layer A fails,
nothing is built and the Layer B checks are reported as `"not run: Layer A
failed"`. Two runs on the same input produce byte-identical files.

## Development

```bash
ruff check .
ruff format --check .
mypy
pytest
```
