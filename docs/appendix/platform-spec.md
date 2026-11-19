# Platform Spec v0.3: Data access และตัวเช็คชั้นข้อมูล (ทำครั้งเดียว)

ใบแรกจาก 3 ใบที่แตกมาจาก Example Input v0.2 (Issue #6 ที่ปิดไปแล้ว) ตามข้อเสนอ "1 Spec ต่อ 1 ชั้นงาน"

| ใบ | งาน | Depends on |
|---|---|---|
| **A (ใบนี้)** | `load()` + `FixtureSource`, fixture 6 ชุด, ตัวเช็คชั้น A | ไม่มี |
| B | block ของรายงาน, `report.json/md`, ตัวเช็คชั้น B, Expected Values | A |
| C | ข้อความบรรยาย, B8, ตัวเช็คการเขียน | B |

- แก้ spec gap จาก Run #2 ที่เกี่ยวกับชั้นนี้แล้ว: A2 ยอมให้ `transactions` และ `cash_flow` ว่างได้
- fixture เป็นชุดเดียวกับ Issue #6 (ข้อมูลปลอม) ตรวจด้วยสคริปต์แล้วว่าผ่านตัวเช็คทุกข้อ
- ใบนี้ไม่มีรายงาน output มีแค่ `checks.json` จึงควรเล็กพอให้โรงงานจบใน session เดียว
- ใช้ package `quant_software_factory.reporting` เหมือน Issue #6
- **สถานะ: เปิดเป็น Issue #7 แล้ว** ได้ PR #8 ที่ merge เข้า `main` เมื่อ 13 พ.ย. 2569 (commit `9455ea3`) ผลอยู่ใน `spec-eval-method.md` Run #3
- หลังรัน แผนใบ B และ C เปลี่ยนเป็น Report Spec ใบเดียว ([`report-spec.md`](report-spec.md)) ส่วน Issue body ด้านล่างเป็นฉบับที่ส่งจริง จึงยังพูดถึง B และ C
- ส่วนใต้เส้นคั่นคือ Issue body

---

Feature: Report data access layer and data checks (part A of 3) — precomputed datasets, fixture source

## Background

The Quant team's reports are built from datasets that the team's pipeline has already computed. Report code must never recompute those figures. It reads them, lays them out, and checks them.

This work is split into three issues so each one fits in a single factory session:

- A (this issue): read the datasets through one interface and check the data before any report is built.
- B: build the report blocks and the report-level number checks. Depends on A.
- C: write the narrative and the writing checks. Depends on B.

This issue adds no report. Its output is a data-check result.

## Report Definition

| Field | Value |
| --- | --- |
| Report type | `returns_transactions` (used by B and C) |
| Report ID | `demo_coop_rg_2026_10_v2` |
| Account | `DEMO-0001` (synthetic) |
| Opening date | 2026-09-30 |
| As-of date | 2026-10-30 |

## Data Sources

Read data only through this interface:

```python
def load(
    dataset: str, as_of: date, accounts: Sequence[str]
) -> list[dict[str, str]]: ...
```

- Returns the raw string values of each row, keyed by field name, for the given accounts.
- For datasets with a `date` field, returns rows with `date <= as_of`. For `performance`, returns rows whose `period` month is not after the as-of month. `account_info` has no date and returns all rows for the accounts.
- Raises `KeyError` for an unknown dataset name.

Implement `FixtureSource(root: Path)`, which reads `<root>/<dataset>.csv`. Keep the interface (a `typing.Protocol` named `DataSource`) separate from the fixture implementation, so a production source can be added later without touching callers. Do not add a production source.

Commit these fixtures to `data/fixtures/demo_coop_rg_2026_10_v2/` exactly as given. All values are synthetic.

### account_info.csv
Fields: `account_no` (str), `client_name` (str), `strategy` (str), `inception_date` (date), `product` (str).

```csv
account_no,client_name,strategy,inception_date,product
DEMO-0001,DEMO-COOP,Reverse Grid,2024-02-28,AlphaDemo
```

### nav_daily.csv
Fields: `date` (date), `account_no` (str), `nav` (decimal), `cash` (decimal), `market_value` (decimal).

```csv
date,account_no,nav,cash,market_value
2026-09-30,DEMO-0001,715000.00,100000.00,615000.00
2026-10-30,DEMO-0001,792398.00,267398.00,525000.00
```

### holdings_daily.csv
Fields: `date` (date), `account_no` (str), `instrument` (str), `volume` (int), `avg_cost` (decimal), `cost_value` (decimal), `market_price` (decimal), `market_value` (decimal), `unrealized_pl` (decimal).

```csv
date,account_no,instrument,volume,avg_cost,cost_value,market_price,market_value,unrealized_pl
2026-10-30,DEMO-0001,AAA,9000,49.00,441000.00,52.00,468000.00,27000.00
2026-10-30,DEMO-0001,BBB,3000,20.00,60000.00,19.00,57000.00,-3000.00
```

### transactions.csv
Fields: `date` (date), `account_no` (str), `instrument` (str), `side` (`BUY` | `SELL` | `DIVIDEND`), `qty` (int), `price` (decimal), `fee` (decimal), `tax` (decimal), `amount` (decimal, net cash effect, negative for cash out), `realized_pl` (decimal, required for SELL, blank otherwise).

```csv
date,account_no,instrument,side,qty,price,fee,tax,amount,realized_pl
2026-10-05,DEMO-0001,AAA,BUY,2000,43.95,100.00,0.00,-88000.00,
2026-10-12,DEMO-0001,AAA,SELL,3000,55.00,165.00,0.00,164835.00,17835.00
2026-10-15,DEMO-0001,BBB,DIVIDEND,5000,0.80,0.00,400.00,3600.00,
2026-10-20,DEMO-0001,BBB,SELL,2000,18.50,37.00,0.00,36963.00,-3037.00
```

### cash_flow.csv
Fields: `date` (date), `account_no` (str), `flow_type` (`DEPOSIT` | `WITHDRAWAL`), `amount` (decimal, positive).

```csv
date,account_no,flow_type,amount
2026-10-26,DEMO-0001,DEPOSIT,50000.00
```

### performance.csv
Fields: `period` (`YYYY-MM`), `account_no` (str), `capital_gain` (decimal), `dividend` (decimal), `unrealized_change` (decimal), `total_pl` (decimal), `return_pct` (decimal).

```csv
period,account_no,capital_gain,dividend,unrealized_change,total_pl,return_pct
2026-10,DEMO-0001,14798.00,3600.00,9000.00,27398.00,3.83
```

Define each dataset's fields and types once, in a schema registry in code, and use it for both loading and check A3.

## Data Checks (Layer A)

- A1 freshness: the latest `nav_daily.date` for the account equals the as-of date.
- A2 completeness:
  - `account_info`, `nav_daily`, `holdings_daily` and `performance` have at least one row for the account.
  - `nav_daily` has a row for both the opening date and the as-of date.
  - `performance` has a row for the as-of month.
  - `transactions` and `cash_flow` may be empty. A month with no trades or no deposits and withdrawals is valid.
- A3 schema:
  - every file has exactly the listed fields, in any order, with no extras
  - required values are not blank (`realized_pl` is required only for SELL rows)
  - values parse to their declared types (`decimal.Decimal`, `int`, ISO date, `YYYY-MM`)
  - enum fields contain only the listed values
  - a missing file fails A3 for that dataset

If A3 fails for a dataset, A1 and A2 checks that need that dataset are reported as not run, with the reason.

## Output Contract

- Command: `python -m quant_software_factory.reporting.check_data data/fixtures/demo_coop_rg_2026_10_v2 --account DEMO-0001 --opening 2026-09-30 --as-of 2026-10-30 --out reports/demo_coop_rg_2026_10_v2`
- Writes `reports/demo_coop_rg_2026_10_v2/checks.json`: a list of `{"name", "layer", "passed", "expected", "actual"}`, sorted by name, with `layer` set to `"A"`. A check that did not run has `"passed": false` and its reason in `actual`.
- Exit code 0 when all checks pass, 1 when any check fails.
- Two runs on the same input produce a byte-identical `checks.json`.
- Commit the generated `checks.json` for the fixture.

## Expected Values

| Call or check | Expected |
| --- | --- |
| `load("account_info", 2026-10-30, ["DEMO-0001"])` | 1 row |
| `load("nav_daily", 2026-10-30, ["DEMO-0001"])` | 2 rows |
| `load("nav_daily", 2026-09-30, ["DEMO-0001"])` | 1 row |
| `load("holdings_daily", 2026-10-30, ["DEMO-0001"])` | 2 rows |
| `load("transactions", 2026-10-30, ["DEMO-0001"])` | 4 rows |
| `load("transactions", 2026-10-12, ["DEMO-0001"])` | 2 rows |
| `load("cash_flow", 2026-10-30, ["DEMO-0001"])` | 1 row |
| `load("performance", 2026-10-30, ["DEMO-0001"])` | 1 row |
| `load("nav_daily", 2026-10-30, ["OTHER"])` | 0 rows |
| `load("unknown", ...)` | `KeyError` |
| All A1–A3 checks on the fixture | passed, exit code 0 |

## Failing-Input Tests

Each case must make the named check fail and the command exit 1. Build the bad inputs in temporary directories in the tests; do not commit them as fixtures.

| Case | Fails |
| --- | --- |
| Latest `nav_daily` row is 2026-10-29 | A1 |
| `nav_daily` has no 2026-09-30 row | A2 |
| `performance` is header only | A2 |
| `holdings_daily.csv` is missing | A3 (and dependent A1/A2 reported as not run) |
| A column is missing or an extra column is added | A3 |
| `nav` is `79x398.00` | A3 |
| `side` is `TRANSFER` | A3 |
| A SELL row has blank `realized_pl` | A3 |

Plus one passing case: `transactions.csv` and `cash_flow.csv` contain only the header, and all checks still pass.

## Constraints

- Base branch: `main`.
- Depends on: none.
- Standard library only. Parse numbers with `decimal.Decimal`, never `float`.
- Put code under `src/quant_software_factory/reporting/`. Do not modify `risk.py` or existing tests.
- Read data only through `load(...)`.
- No server names, IP addresses, database or table names, internal URLs, or credentials anywhere.

## Out of Scope

- Report blocks, `report.json`, `report.md`, narrative (issues B and C)
- Report-level number checks (issue B)
- Any production data source
- Recomputing any figure

## Acceptance Criteria

- [ ] The pull request targets `main` and the branch is cut from `main`.
- [ ] `DataSource` protocol and `FixtureSource` exist, and all data access goes through `load(...)`.
- [ ] The fixtures are committed exactly as given.
- [ ] Every row in Expected Values is asserted by a test.
- [ ] Every case in Failing-Input Tests has a test, plus the empty `transactions` and `cash_flow` case.
- [ ] The command writes `checks.json` and exits 0 on the fixture; the generated file is committed.
- [ ] Two runs produce a byte-identical `checks.json`.
- [ ] ruff check, ruff format --check, mypy (strict) and pytest pass in CI on Python 3.10–3.13.
- [ ] Submitted as a draft pull request.
- [ ] Independent review finds no unresolved blocking issues.

## Definition of Done

A reviewed, CI-passing draft pull request against `main` with the data access layer, schema registry, Layer A checks, fixtures, tests, a short README section, and the generated `checks.json`.

Do not merge automatically. Human approval is required.
