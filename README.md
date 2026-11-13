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

## Development

```bash
ruff check .
ruff format --check .
mypy
pytest
```
