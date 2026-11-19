# Report Spec v0.3: Returns & Transactions (ใบเดียว ได้รายงาน 1 ฉบับ)

Spec ชนิด **Report Spec** ตาม req 1 ข้อ 1: กรอก 1 ใบ ส่งเข้าโรงงาน แล้วได้รายงานที่ตรงตาม Spec

| ชนิด | ใบ | ทำเมื่อ |
|---|---|---|
| Platform Spec | Issue #7 → PR #8 (merge แล้ว, commit `9455ea3`) | ครั้งเดียว: `DataSource`, `FixtureSource`, schema registry, ตัวเช็คชั้น A |
| **Report Spec** | **ใบนี้** | ทุกรายงานใหม่ ใช้ของจาก Platform Spec |

- รวมงานของใบ B และ C ที่วางแผนไว้เป็นใบเดียว เพราะ data layer มีอยู่บน `main` แล้ว
- แก้ spec gap จาก Run #2 ที่เหลือแล้ว:
  - B8 ตรวจเฉพาะจำนวนเงินและ % และยอมรับค่าสัมบูรณ์ของตัวเลขที่ JSON เก็บเป็นลบ
  - กำหนดเครื่องหมายของเงินถอนในตารางรายการแล้ว
- fixture และตัวเลขเป็นชุดเดิมจาก Issue #6 และ #7 (ข้อมูลปลอม) ไม่ต้อง commit fixture ใหม่
- **สถานะ: เปิดเป็น Issue #9 แล้ว** ได้ PR #10 ที่ merge เข้า `main` เมื่อ 13 พ.ย. 2569 (commit `4e2129e`) ผลอยู่ใน `spec-eval-method.md` Run #4
- ส่วนใต้เส้นคั่นคือ Issue body

---

Feature: Returns & Transactions Report from precomputed data — DEMO-COOP Reverse Grid, October 2026

## Background

The Quant team sends clients a returns and transactions report: capital gains, dividends, and gains or losses on positions still held. Relationship managers use it in client conversations.

The team's pipeline already computes every figure. This report reads those figures, lays them out, checks that they agree with each other, and adds a short narrative. It must not recompute any figure that a dataset provides.

The data layer already exists on `main` (merged from #7): `DataSource`, `FixtureSource`, the schema registry and the Layer A data checks in `quant_software_factory.reporting`. Build on it. Do not change its behavior.

## Report Definition

| Field | Value |
| --- | --- |
| Report type | `returns_transactions` |
| Report ID | `demo_coop_rg_2026_10_v2` |
| Account | `DEMO-0001` |
| Client, strategy, inception | from `account_info` |
| Period | 2026-10 (2026-10-01 to 2026-10-31) |
| Opening date | 2026-09-30 |
| As-of date | 2026-10-30 |
| Currency | THB |
| Language | en |
| Audience | Institutional client, read with a relationship manager |
| Output format | md |

## Data Sources

Use the existing fixtures in `data/fixtures/demo_coop_rg_2026_10_v2/` through `FixtureSource` and `load(...)`. Do not add or change fixtures. Datasets used: `account_info`, `nav_daily`, `holdings_daily`, `transactions`, `cash_flow`, `performance`.

## Data Mapping

| Block | Report field | Dataset.field | Display |
| --- | --- | --- | --- |
| header | Client | `account_info.client_name` | text |
| header | Account | `account_info.account_no` | text |
| header | Strategy | `account_info.strategy` | text |
| header | Inception | `account_info.inception_date` | `DD Mon YYYY` |
| kpi_summary | Net asset value | `nav_daily.nav` at as-of date | money |
| kpi_summary | Cash | `nav_daily.cash` at as-of date | money |
| kpi_summary | Realized capital gain | `performance.capital_gain` | money |
| kpi_summary | Dividends (net) | `performance.dividend` | money |
| kpi_summary | Change in unrealized P/L | `performance.unrealized_change` | money |
| kpi_summary | Total P/L | `performance.total_pl` | money |
| kpi_summary | Period return (simple, on opening NAV) | `performance.return_pct` | pct |
| holdings | Volume, Avg cost, Cost value, Market price, Market value, Unrealized P/L | `holdings_daily.*` at as-of date | int, money |
| holdings | CASH row market value | `nav_daily.cash` at as-of date | money |
| holdings | Total row | sum of the rows above, for display only, checked by B1 and B2 | money |
| transactions | Date, Instrument, Side, Qty, Price, Fee, Tax, Amount, Realized P/L | `transactions.*` | date, text, int, money |
| transactions | Deposit and withdrawal rows | `cash_flow.*`, instrument `CASH`, side = `flow_type`, Amount = `amount` for DEPOSIT and `-amount` for WITHDRAWAL | money |

Formats:
- money: 2 decimals, thousands separators, minus sign for negatives, `-0.00` shown as `0.00`
- pct: 2 decimals followed by `%`
- int: thousands separators
- Use `decimal.Decimal` with ROUND_HALF_UP

If a mapped value is missing, the report fails. Do not derive it from other fields.

## Report Blocks

In this order, one `##` section per block in `report.md`:

1. `header`: title "Returns & Transactions Report", the header fields, period, as-of date, report ID.
2. `kpi_summary`: the seven KPI fields, one row each.
3. `holdings`: one row per instrument in `holdings_daily` at the as-of date, sorted alphabetically, then a CASH row, then a Total row. The Total cost value excludes CASH. The Total market value includes CASH. Instruments fully sold in the period appear only in `transactions`.
4. `transactions`: all rows from `transactions` and `cash_flow` in the period, newest first. Realized P/L is blank except on SELL rows.
5. `narrative`: see Writing Rules.
6. `disclaimer`: fixed text: "This report is prepared for the named account holder only. It is not an offer, solicitation, or investment advice. Past performance does not indicate future results."

## Output Contract

- Command: `python -m quant_software_factory.reporting.returns_transactions data/fixtures/demo_coop_rg_2026_10_v2 reports/demo_coop_rg_2026_10_v2 --account DEMO-0001 --opening 2026-09-30 --as-of 2026-10-30`
- The report ID is the output folder name.
- Writes to the output folder:
  - `report.md`
  - `report.json`: keys are the block IDs; numbers are strings formatted as in the tables; not-applicable values are `null`
  - `narrative.md`
  - `checks.json`: Layer A results from the existing `run_checks(...)` plus the Layer B results, in the same `{name, layer, passed, expected, actual}` format, sorted by name
- If any check fails:
  - exit 1
  - write `checks.json`
  - write no other file, and remove stale `report.md`, `report.json` and `narrative.md`
- Run Layer A first. If it fails, build nothing and report Layer B checks as not run.
- Two runs on the same input give byte-identical `report.json` and `checks.json`.
- This replaces the existing `reports/demo_coop_rg_2026_10_v2/checks.json` with the combined Layer A and Layer B result. Commit all four generated files.

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
| transactions | 2026-10-20 BBB SELL amount / realized | 36,963.00 / -3,037.00 |
| narrative | Sentence about the BBB sale | contains "a realized loss of 3,037.00 THB" |
| narrative | Sentence about the deposit | contains "a deposit of 50,000.00 THB" |
| checks | All Layer A and Layer B checks | passed, exit code 0 |

## Number Checks (Layer B)

- B1 holdings total: sum of holdings `market_value` + cash = `nav_daily.nav` at the as-of date.
- B2 securities value: sum of holdings `market_value` = `nav_daily.market_value` at the as-of date.
- B3 holding rows: on each row, `market_value − cost_value = unrealized_pl`.
- B4 same figure everywhere: NAV and cash in `kpi_summary` equal the CASH row and the Total market value in `holdings`.
- B5 accounting identity: opening `nav` + deposits − withdrawals + `performance.total_pl` = closing `nav`.
- B6 P/L parts: `capital_gain + dividend + unrealized_change = total_pl`.
- B7 realized ties to transactions:
  - sum of SELL `realized_pl` in the period = `performance.capital_gain`
  - sum of DIVIDEND `amount` = `performance.dividend`
- B8 narrative numbers: every money or percent value in `narrative.md` appears in `report.json` with the same formatting, or as the absolute value of a negative value there. Dates, years and counts are not checked by B8.

Tolerance 0.01 per value. Compare unrounded `Decimal` values.

## Writing Rules

- Audience: an institutional client reading with a relationship manager. Plain, professional, calm.
- 2 to 4 short paragraphs, under 180 words.
- Generate the text from `report.json` with code, using fixed sentence templates. Do not call an LLM at runtime.
- Cover, in this order:
  1. the change in net asset value and total P/L for the period
  2. sales and dividends
  3. positions still held
  4. deposits and withdrawals
- Write negative values as losses: "a realized loss of 3,037.00 THB", never "a realized capital gain of -3,037.00 THB".
- Match singular and plural to the count: one deposit is "a deposit of", not "deposits of".
- No two consecutive sentences start with the same word.
- Describe what happened. Do not explain why prices moved.
- No forecasts, recommendations, or investment advice. Do not use "will", "expect", "should", or "recommend".
- Do not use these phrases: "robust", "impressive", "navigate", "it is worth noting", "delve", "in today's".

Writing checks, reported in `checks.json` as Layer B:
- W1: no banned phrase
- W2: no "gain of -"
- W3: no repeated sentence opener
- W4: within the length limits
- W5: no forecast words

A failed writing check fails the report like any other check.

## Constraints

- Base branch: `main`.
- Depends on: #7 (merged).
- Standard library only.
- Put new code under `src/quant_software_factory/reporting/`. Reuse `FixtureSource`, `load(...)`, the schema registry and `run_checks(...)`. Do not change their behavior. Do not modify `risk.py`.
- No hard-coded client, account, strategy or inception values in code.
- No server names, IP addresses, database or table names, internal URLs, or credentials anywhere.

## Out of Scope

- Changing the data layer or fixtures
- Production data sources
- Allocation or weight block, charts, PDF
- Benchmark performance, volatility, Sharpe
- Other report types and multi-account aggregation
- Thai-language output
- LLM-generated text

## Acceptance Criteria

- [ ] The pull request targets `main` and the branch is cut from `main`.
- [ ] The command writes `report.md`, `report.json`, `narrative.md` and `checks.json` for the fixture and exits 0.
- [ ] `report.md` has the 6 blocks in order.
- [ ] Every row in Expected Values is asserted by a test.
- [ ] Each of B1–B8 and W1–W5 has a test with an input that makes it fail.
- [ ] When Layer A fails, no report files are written and Layer B checks are reported as not run.
- [ ] No figure in Data Mapping is computed from other fields. Totals rows are display sums checked by B1 and B2.
- [ ] Data is read only through the existing `load(...)`.
- [ ] Two runs give byte-identical `report.json` and `checks.json`.
- [ ] ruff check, ruff format --check, mypy (strict) and pytest pass in CI on Python 3.10–3.13.
- [ ] Submitted as a draft pull request.
- [ ] Independent review finds no unresolved blocking issues.

## Definition of Done

A reviewed, CI-passing draft pull request against `main` with the report builder, Layer B and writing checks, tests, a README section, and the generated output for `demo_coop_rg_2026_10_v2`.

Do not merge automatically. Human approval is required.
