# Example Input v0.2: Returns & Transactions Report (ข้อมูลปลอม)

Spec ตัวอย่างที่กรอกตาม Report Spec Template v0.2 ประเภท `returns_transactions` ใช้สำหรับ Run #2

- **เปลี่ยนจาก Run #1 อย่างเดียวคือโครง Spec** (v0.1 → v0.2) ประเภทรายงานและตัวเลขยังเป็นชุดเดิม (DEMO-COOP, ต.ค. 2026) เพื่อให้เทียบผลกับ Run #1 ได้ตรงๆ
- fixture เปลี่ยนจาก "ธุรกรรมดิบที่ต้องคำนวณ" เป็น "**ชุดข้อมูลที่คำนวณไว้แล้ว**" ตามข้อสรุปว่า pipeline ของทีมคำนวณตัวเลขให้ งานของโรงงานคือดึงข้อมูล จัดลงรายงาน และเช็คตัวเลข
- ชื่อชุดข้อมูลและ field ใช้ชื่อกลางจาก Dataset Catalog ไม่มีชื่อระบบภายใน
- ใช้ package `quant_software_factory.reporting` และ report id `demo_coop_rg_2026_10_v2` เพื่อไม่ให้ชนกับไฟล์ของ PR #5 ที่ยังเปิดอยู่
- block มี 6 ตัวตามกติกาขนาดใหม่ (ตัด `allocation` ออก เพราะน้ำหนักพอร์ตยังไม่รู้ว่ามีในชุดข้อมูลจริงหรือไม่)
- **สถานะ: ยังไม่ได้เปิด Issue** รอผู้ใช้ตรวจก่อน
- ส่วนที่อยู่ใต้เส้นคั่นคือ Issue body ที่จะคัดลอกไปใช้

---

Feature: Returns & Transactions Report from precomputed data — DEMO-COOP Reverse Grid, October 2026

## Background

The Quant team sends clients a returns and transactions report: capital gains, dividends, and unrealized gains or losses on positions still held. Relationship managers use it in client conversations.

The team's data pipeline already computes every figure and stores it in precomputed datasets. This report must not recompute anything. Its job is to read those datasets, lay the figures out in the report, and check that the figures agree with each other before anyone sees the report.

This issue covers one account and one month, using synthetic fixtures. Production data access is out of scope; it will be plugged in later behind the same interface.

## Report Definition

| Field | Value |
| --- | --- |
| Report type | `returns_transactions` |
| Report ID | `demo_coop_rg_2026_10_v2` |
| Client / Account | from `account_info` (fixture: DEMO-COOP / DEMO-0001, synthetic) |
| Strategy | from `account_info` |
| Period | 2026-10-01 to 2026-10-31 |
| Opening date | 2026-09-30 |
| As-of date | 2026-10-30 |
| Currency | THB |
| Language | en |
| Audience | Institutional client, read with a relationship manager |
| Output format | md |

## Data Sources

All numbers come from precomputed datasets. Do not recompute them.

Read data only through one interface:

```python
load(dataset: str, as_of: date, accounts: list[str]) -> list[dict[str, str]]
```

Implement `FixtureSource`, which reads `data/fixtures/demo_coop_rg_2026_10_v2/<dataset>.csv`. Keep the interface small so a production source can replace it later without changing report code.

Commit these fixtures exactly as given. All values are synthetic.

### account_info.csv
Fields: `account_no` (str), `client_name` (str), `strategy` (str), `inception_date` (date), `product` (str).

```csv
account_no,client_name,strategy,inception_date,product
DEMO-0001,DEMO-COOP,Reverse Grid,2024-02-28,AlphaDemo
```

### nav_daily.csv
Fields: `date` (date), `account_no` (str), `nav` (decimal), `cash` (decimal), `market_value` (decimal, securities only).

```csv
date,account_no,nav,cash,market_value
2026-09-30,DEMO-0001,715000.00,100000.00,615000.00
2026-10-30,DEMO-0001,792398.00,267398.00,525000.00
```

### holdings_daily.csv
Fields: `date` (date), `account_no` (str), `instrument` (str), `volume` (int), `avg_cost` (decimal), `cost_value` (decimal), `market_price` (decimal), `market_value` (decimal), `unrealized_pl` (decimal). Rows exist only for instruments still held.

```csv
date,account_no,instrument,volume,avg_cost,cost_value,market_price,market_value,unrealized_pl
2026-10-30,DEMO-0001,AAA,9000,49.00,441000.00,52.00,468000.00,27000.00
2026-10-30,DEMO-0001,BBB,3000,20.00,60000.00,19.00,57000.00,-3000.00
```

### transactions.csv
Fields: `date` (date), `account_no` (str), `instrument` (str), `side` (`BUY` | `SELL` | `DIVIDEND`), `qty` (int), `price` (decimal), `fee` (decimal), `tax` (decimal), `amount` (decimal, net cash effect, negative for cash out), `realized_pl` (decimal, SELL only, blank otherwise).

```csv
date,account_no,instrument,side,qty,price,fee,tax,amount,realized_pl
2026-10-05,DEMO-0001,AAA,BUY,2000,43.95,100.00,0.00,-88000.00,
2026-10-12,DEMO-0001,AAA,SELL,3000,55.00,165.00,0.00,164835.00,17835.00
2026-10-15,DEMO-0001,BBB,DIVIDEND,5000,0.80,0.00,400.00,3600.00,
2026-10-20,DEMO-0001,BBB,SELL,2000,18.50,37.00,0.00,36963.00,-3037.00
```

### cash_flow.csv
Fields: `date` (date), `account_no` (str), `flow_type` (`DEPOSIT` | `WITHDRAWAL`), `amount` (decimal, always positive).

```csv
date,account_no,flow_type,amount
2026-10-26,DEMO-0001,DEPOSIT,50000.00
```

### performance.csv
Fields: `period` (YYYY-MM), `account_no` (str), `capital_gain` (decimal, realized), `dividend` (decimal, net), `unrealized_change` (decimal), `total_pl` (decimal), `return_pct` (decimal, simple return on opening NAV, in percent).

```csv
period,account_no,capital_gain,dividend,unrealized_change,total_pl,return_pct
2026-10,DEMO-0001,14798.00,3600.00,9000.00,27398.00,3.83
```

## Data Mapping

| Block | Report field | Dataset.field | Display format |
| --- | --- | --- | --- |
| header | Client | `account_info.client_name` | text |
| header | Account | `account_info.account_no` | text |
| header | Strategy | `account_info.strategy` | text |
| header | Inception | `account_info.inception_date` | date `DD Mon YYYY` |
| kpi_summary | Net asset value | `nav_daily.nav` at as-of date | money |
| kpi_summary | Cash | `nav_daily.cash` at as-of date | money |
| kpi_summary | Realized capital gain | `performance.capital_gain` | money |
| kpi_summary | Dividends (net) | `performance.dividend` | money |
| kpi_summary | Change in unrealized P/L | `performance.unrealized_change` | money |
| kpi_summary | Total P/L | `performance.total_pl` | money |
| kpi_summary | Period return (simple, on opening NAV) | `performance.return_pct` | pct |
| holdings | Volume, Avg cost, Cost value, Market price, Market value, Unrealized P/L | `holdings_daily.*` at as-of date | int, money |
| holdings | CASH row, Market value | `nav_daily.cash` at as-of date | money |
| holdings | Total row | sum of rows above, for display only, checked by B1 | money |
| transactions | Date, Instrument, Side, Qty, Price, Fee, Tax, Amount, Realized P/L | `transactions.*` | date, text, int, money |
| transactions | Deposits and withdrawals | `cash_flow.*` shown as extra rows with instrument `CASH` | money |

Display formats: money is 2 decimals with thousands separators; pct is 2 decimals with `%`; int has thousands separators.

If a mapped field is missing or blank where a value is required, fail check A3. Do not derive it from other fields. For example, do not compute `unrealized_pl` as `market_value − cost_value`.

## Report Blocks

In this order:

1. `header`: title "Returns & Transactions Report", fields from Data Mapping, period, as-of date, report ID.
2. `kpi_summary`: the seven KPI fields from Data Mapping.
3. `holdings`: one row per instrument in `holdings_daily` at the as-of date, sorted alphabetically, then a CASH row, then a Total row. Instruments fully sold during the period do not appear here; they appear in `transactions`.
4. `transactions`: all rows from `transactions` and `cash_flow` in the period, newest first.
5. `narrative`: 2 to 4 short paragraphs. See Writing Rules.
6. `disclaimer`: fixed text: "This report is prepared for the named account holder only. It is not an offer, solicitation, or investment advice. Past performance does not indicate future results."

## Output Contract

- Command: `python -m quant_software_factory.reporting.returns_transactions data/fixtures/demo_coop_rg_2026_10_v2 reports/demo_coop_rg_2026_10_v2 --as-of 2026-10-30 --period 2026-10`
- Writes to `reports/demo_coop_rg_2026_10_v2/`: `report.md`, `report.json`, `narrative.md`, `checks.json`.
- `report.json` keys are the block IDs. Numbers are strings formatted exactly as in the tables. Not-applicable values are `null`.
- Decimal arithmetic only, ROUND_HALF_UP, for display formatting and checks.
- Two runs on the same input produce a byte-identical `report.json`.
- No report metadata is hard-coded. Client, account, strategy and inception come from `account_info`.
- Commit the generated output files for this example.

## Expected Values

| Block | Field | Expected |
| --- | --- | --- |
| header | Client / Account / Strategy | DEMO-COOP / DEMO-0001 / Reverse Grid |
| header | Inception | 28 Feb 2024 |
| kpi_summary | Net asset value | 792,398.00 |
| kpi_summary | Cash | 267,398.00 |
| kpi_summary | Realized capital gain | 14,798.00 |
| kpi_summary | Dividends (net) | 3,600.00 |
| kpi_summary | Change in unrealized P/L | 9,000.00 |
| kpi_summary | Total P/L | 27,398.00 |
| kpi_summary | Period return | 3.83% |
| holdings | AAA volume / avg cost / cost value | 9,000 / 49.00 / 441,000.00 |
| holdings | AAA market price / market value / unrealized | 52.00 / 468,000.00 / 27,000.00 |
| holdings | BBB volume / avg cost / cost value | 3,000 / 20.00 / 60,000.00 |
| holdings | BBB market price / market value / unrealized | 19.00 / 57,000.00 / -3,000.00 |
| holdings | CASH market value | 267,398.00 |
| holdings | Total cost value / market value / unrealized | 501,000.00 / 792,398.00 / 24,000.00 |
| transactions | Row count | 5 |
| transactions | First row (newest) | 2026-10-26, CASH, DEPOSIT, 50,000.00 |
| checks | All checks | passed |

The Total cost value (501,000.00) excludes CASH. The Total market value includes CASH.

## Number Checks

Layer A, data:
- A1 freshness: the latest `nav_daily.date` equals the as-of date.
- A2 completeness: every dataset in Data Sources has at least one row for the account, and `nav_daily` has rows for both the opening date and the as-of date.
- A3 schema: every dataset has exactly the fields listed, required values are present, and values parse to their declared types.

Layer B, report:
- B1 holdings total: sum of holdings `market_value` + cash = `nav_daily.nav` at the as-of date.
- B2 securities value: sum of holdings `market_value` = `nav_daily.market_value` at the as-of date.
- B3 holding rows: for each row, `market_value − cost_value = unrealized_pl`.
- B4 same figure everywhere: NAV and cash in `kpi_summary` equal the values in `holdings`.
- B5 accounting identity: opening `nav` + deposits − withdrawals + `performance.total_pl` = closing `nav`.
- B6 P/L parts: `capital_gain + dividend + unrealized_change = total_pl`.
- B7 realized ties to transactions: sum of SELL `realized_pl` in the period = `performance.capital_gain`, and sum of DIVIDEND `amount` = `performance.dividend`.
- B8 narrative numbers: every number in `narrative.md` appears in `report.json` with the same formatting.

Tolerance: 0.01 per value. Any failed check exits non-zero, writes `checks.json` with `name`, `layer`, `passed`, `expected`, `actual` for every check, writes no report files, and removes stale report files from an earlier run.

## Writing Rules

- Audience: an institutional client reading with their relationship manager. Plain, professional, calm.
- 2 to 4 short paragraphs, under 180 words in total.
- Generate the text from `report.json` with code, using fixed sentence templates. Do not call an LLM at runtime.
- Every number in the text comes from `report.json`, formatted the same way.
- Write negative values as losses: "a realized loss of 3,037.00 THB", not "a realized capital gain of -3,037.00 THB".
- Match singular and plural to the count: one deposit is "a deposit of", not "deposits of".
- Describe what happened in the period. Do not explain why prices moved.
- No forecasts, recommendations, or investment advice.
- Avoid filler and hype such as "robust", "impressive", "navigate", "it is worth noting", "delve".

## Constraints

- Base branch: `main`.
- Depends on: none.
- No new runtime dependencies. Standard library only.
- Put new code under `src/quant_software_factory/reporting/`. Do not modify `risk.py` or existing tests.
- No server names, IP addresses, database or table names, internal URLs, or credentials in code, fixtures or docs.

## Out of Scope

- Production data access (only `FixtureSource` is built)
- Recomputing any figure that a dataset provides
- Allocation or weight block, charts, PDF output
- Performance against a benchmark, volatility, Sharpe
- Other report types and multi-account aggregation
- Thai-language output

## Open Items

- Real column names for each dataset are not mapped yet; this spec uses logical names only.
- Whether the production datasets include weight per holding is unknown, so the allocation block is left out.
- The checks the team's pipeline already runs on the source data are not reused here; Layer A is reimplemented against fixtures.

## Acceptance Criteria

- [ ] The pull request targets `main` and the branch is cut from `main`.
- [ ] The command in Output Contract writes all four output files for the fixture.
- [ ] `report.md` contains the 6 blocks in the specified order.
- [ ] Every row in Expected Values is asserted by an automated test.
- [ ] Every check A1–A3 and B1–B8 is implemented, and each has a test with an input that makes it fail.
- [ ] No figure listed in Data Mapping is computed from other fields; a test or review note confirms this.
- [ ] Data is read only through `load(...)`.
- [ ] Client, account, strategy and inception come from `account_info`, not from code.
- [ ] Two runs produce a byte-identical `report.json`.
- [ ] The narrative follows Writing Rules, including the loss wording and singular/plural rule, and a test checks the BBB sale sentence.
- [ ] ruff check, ruff format --check, mypy (strict) and pytest pass in CI on Python 3.10–3.13.
- [ ] Submitted as a draft pull request.
- [ ] Independent review finds no unresolved blocking issues.

## Definition of Done

A reviewed, CI-passing draft pull request against `main` with the implementation, fixtures, tests, README section, and the generated sample output for `demo_coop_rg_2026_10_v2`.

Do not merge automatically. Human approval is required.
