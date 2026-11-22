# quant-software-factory

Reusable quantitative finance utilities for evaluating trading strategies.

| Path | Contents |
| --- | --- |
| `src/quant_software_factory/` | Python library: risk metrics and the report builder (`reporting/`) |
| `tests/` | pytest suite |
| `data/fixtures/` | Mock datasets (no real client data) |
| `reports/` | Reports generated from the fixtures |
| `report-agent/` | eve agent that builds reports from Discord; see its [README](report-agent/README.md) |
| `docs/` | Project documents (TOR, Project Plan, SRS, Software Design, Delivery Document); index in [docs/README.md](docs/README.md) |

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

## Private data boundary prototype

Report code is developed without ever seeing private data. The prototype splits
the work into three zones:

- **Agent zone**: the repository, issues, pull requests and coding agents. It
  holds code, specs, the schema registry and synthetic fixtures only.
- **Trusted zone**: an operator's machine outside the repository working tree.
  The operator runs the repository's code against a private database. The
  database and every private output stay here.
- **Boundary**: the only thing that leaves the trusted zone is a sanitized
  result file with the check names and their pass/fail flags.

In this prototype the private database is a local SQLite file built from
synthetic data. `SqliteSource(path)` implements `DataSource` on it: one TEXT
table per dataset, named as the dataset, opened read-only, with the same
filtering and errors as `FixtureSource`.

Build a database from dataset CSV files (it refuses to overwrite an existing
file). `--scale K` multiplies every money field by `K` (not
`performance.return_pct`, quantities or dates); `--account` and
`--client-name` replace the account number and client name:

```bash
mkdir -p /tmp/private
python -m quant_software_factory.reporting.make_private_db \
    data/fixtures/demo_coop_rg_2026_10_v2 /tmp/private/private.db \
    --scale 3 --account PRIV-0001 --client-name PRIVATE-CLIENT
```

Run the report in the trusted zone:

```bash
python -m quant_software_factory.reporting.private_run \
    --db /tmp/private/private.db --private-out /tmp/private/report \
    --result /tmp/boundary/result.json \
    --account PRIV-0001 --opening 2026-09-30 --as-of 2026-10-30
```

It reads the database only through `SqliteSource` and `load(...)`, runs the
same checks and report builder as `returns_transactions`, and writes
`report.md`, `report.json`, `narrative.md` and `checks.json` to
`--private-out` (the folder name is the report ID). Only `--result` may be
shared:

```json
{
  "status": "passed",
  "checks_total": 29,
  "checks_failed": 0,
  "checks": [{"name": "A1_freshness_nav_daily", "layer": "A", "passed": true}]
}
```

`checks` lists every report check sorted by name with exactly `name`, `layer`
and `passed`. There are no expected or actual values, account, client name,
dates, figures or paths. Before writing the result, a `boundary_leak_check`
rejects text that contains any number with a decimal point or thousands
separator anywhere, or that contains the account ID or the client name as a
whole token (not preceded or followed by a letter, digit or underscore) in one
of its string values (`status` and every check `name` and `layer`). Integer
values such as `checks_total` are not searched for the account ID or client
name, so a short account such as `A1` or `29` does not collide with
`A1_freshness_nav_daily` or `"checks_total": 29`. Text that is not valid JSON
fails the check as `unparseable`. The check's `actual` value names only the
categories found, never the values. `boundary_leak_check` uses layer
`"boundary"` (besides the report layers `"A"` and `"B"`); it appears only in
the private `checks.json` and is never part of the result. A collision can
still happen when the account ID or client name equals a whole check name or
layer (for example account `A`); the run then stops with exit 3 and no result
is written.

Exit codes: 0 when every report check passes; 1 when any report check fails
(the result is still written, with status `"failed"`); 2 when `--private-out`
or `--result` resolves inside a checkout of this repository, including through
a symlink and whatever the install mode (nothing is written); 3 when the leak check fails (no result is
written, an existing one is removed, and the private folder keeps only
`checks.json`).

Design decisions: the private folder is not encrypted. Protecting it (disk
encryption, file permissions, retention) is the trusted zone's
responsibility and out of scope here, as are production data sources and any
network access. `*.db` and `*.sqlite` files are git-ignored; never commit a
private database or private output.

## Development

```bash
ruff check .
ruff format --check .
mypy
pytest
```
