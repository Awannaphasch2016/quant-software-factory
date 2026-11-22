# Example Input: Returns & Transactions Report (ข้อมูลปลอม)

ตัวอย่าง Spec ที่กรอกตาม Report Spec Template v0.1 แล้ว ประเภท `returns_transactions`

- ข้อมูลทั้งหมดเป็น**ข้อมูลปลอม** (ลูกค้า DEMO-COOP, หุ้น AAA และ BBB) โครงสร้างอิงตัวอย่าง B (Grid Trade Performance) เพราะ repo เป็น public
- Expected Values ทุกค่าคำนวณด้วยมือและตรวจซ้ำแล้ว สมการบัญชีลงตัวพอดี
- Output รอบนี้เป็น Markdown + JSON ไม่ใช่ PDF เพราะ requirement_1 ไม่ได้บังคับรูปแบบไฟล์ (ขอแค่ "รายงานที่ตรงตาม Specification") จึงไม่ต้องเพิ่ม dependency ใน repo และ reviewer อ่านรายงานใน diff ได้ PDF ทำเป็น Spec ใบถัดไป
- **สถานะ: ยังไม่ได้เปิด Issue** รอผู้ใช้ review ก่อน
- ส่วนที่อยู่ใต้เส้นคั่นคือ Issue body ที่จะใช้คัดลอก ทั้งหัวเรื่องและเนื้อหา

---

Feature: Returns & Transactions Report — DEMO-COOP Reverse Grid, October 2026

## Background

The Quant team prepares a returns and transactions report for each client account. Relationship managers use it when they talk with clients about what the account earned in a period: realized capital gains, dividends, and unrealized gains or losses on positions still held.

Today this report is assembled partly by hand. We want code that builds it from position, transaction, and price data, so the numbers are reproducible and checked before anyone sees them.

This issue covers one report type for one account and one month, using synthetic fixture data. It is the first end-to-end test of the team's Report Spec Template.

## Report Definition

| Field | Value |
| --- | --- |
| Report type | `returns_transactions` |
| Report ID | `demo_coop_rg_2026_10` |
| Client / Account | DEMO-COOP / DEMO-0001 (synthetic) |
| Strategy | Reverse Grid |
| Period | 2026-10-01 to 2026-10-31 |
| Opening date (positions and prices) | 2026-09-30 |
| As-of date (closing prices) | 2026-10-30 |
| Currency | THB |
| Language | en |
| Audience | Client (institutional), read together with a relationship manager |
| Output format | md |

## Input Data

Commit these fixtures to `data/examples/demo_coop_rg_2026_10/` exactly as given.

### opening_positions.csv
Columns: `instrument` (str), `volume` (int, shares), `cost_value` (decimal, THB, fees included). Cash is given as `CASH` with `volume` = THB amount and `cost_value` = the same amount.

```csv
instrument,volume,cost_value
AAA,10000,500000.00
BBB,5000,100000.00
CASH,100000,100000.00
```

### transactions.csv
Columns: `trade_date` (YYYY-MM-DD), `instrument` (str), `side` (`BUY` | `SELL` | `DIVIDEND` | `DEPOSIT` | `WITHDRAWAL`), `qty` (int; shares for BUY/SELL/DIVIDEND, blank for cash flows), `price` (decimal; per share, or dividend per share), `fee` (decimal, THB), `tax` (decimal, THB withholding tax, dividends only), `amount` (decimal, THB cash flow for DEPOSIT/WITHDRAWAL, else blank).

```csv
trade_date,instrument,side,qty,price,fee,tax,amount
2026-10-05,AAA,BUY,2000,43.95,100.00,0.00,
2026-10-12,AAA,SELL,3000,55.00,165.00,0.00,
2026-10-15,BBB,DIVIDEND,5000,0.80,0.00,400.00,
2026-10-20,BBB,SELL,2000,18.50,37.00,0.00,
2026-10-26,CASH,DEPOSIT,,,0.00,0.00,50000.00
```

### prices.csv
Columns: `date` (YYYY-MM-DD), `instrument` (str), `close` (decimal, THB).

```csv
date,instrument,close
2026-09-30,AAA,51.00
2026-09-30,BBB,21.00
2026-10-30,AAA,52.00
2026-10-30,BBB,19.00
```

## Metric Definitions

Use these definitions. They match the Report Spec Template defaults.

- Cost method: weighted average cost. Buy fees are added to cost value.
- BUY: cash −= qty × price + fee; cost value += qty × price + fee.
- SELL: realized gain = (qty × price − fee) − (average cost before the sale × qty). Cash += qty × price − fee. Cost value −= average cost × qty.
- DIVIDEND: gross = qty × price; net = gross − tax. Cash += net. Total P/L uses net.
- DEPOSIT / WITHDRAWAL: cash flow only, not P/L.
- Market value = volume × closing price on the as-of date. Cash market value = cash balance.
- Unrealized P/L = market value − cost value.
- NAV = sum of market values including cash.
- Total P/L for the period = realized capital gain + net dividends + (closing unrealized − opening unrealized).
- Accounting identity: opening NAV + deposits − withdrawals + total P/L = closing NAV.
- Period return % = total P/L ÷ opening NAV × 100. This is a simple return on opening NAV, not time-weighted; label it that way in the report.
- Holding return % = unrealized P/L ÷ cost value × 100.
- Weight % = market value ÷ closing NAV × 100.
- Compute with `decimal.Decimal`. Round only for display: money to 2 decimals, percentages to 2 decimals, ROUND_HALF_UP.

## Report Blocks

In this order:

1. `header`: title "Returns & Transactions Report", client, account, strategy, period, as-of date, report ID.
2. `kpi_summary`: closing NAV, total P/L, period return %, realized capital gain, net dividends, unrealized P/L (closing).
3. `pnl_breakdown`: one row per instrument plus a total row. Columns: realized capital gain, net dividend, change in unrealized, total P/L.
4. `holdings`: one row per instrument plus CASH and a total row. Columns: volume, average cost, cost value, market price, market value, unrealized P/L, holding return %, weight %. Sort instruments alphabetically, CASH last.
5. `transactions`: every row from `transactions.csv`, newest first. Columns: date, instrument, side, qty, price, fee, tax, net cash amount, realized gain (SELL only).
6. `reconciliation`: opening NAV, deposits, withdrawals, total P/L, expected closing NAV, actual closing NAV, difference.
7. `narrative`: 2 to 4 short paragraphs for the client. See Writing Rules.
8. `disclaimer`: fixed text: "This report is prepared for the named account holder only. It is not an offer, solicitation, or investment advice. Past performance does not indicate future results."

## Output Contract

- Command: `python -m quant_software_factory.reports.returns_transactions data/examples/demo_coop_rg_2026_10 reports/demo_coop_rg_2026_10`
- Writes to `reports/demo_coop_rg_2026_10/`:
  - `report.md`, GitHub-flavored Markdown with all 8 blocks in order, one `##` section per block, tables for tabular blocks
  - `report.json`, keys are the block IDs above, numbers as strings with display rounding
  - `narrative.md`
  - `checks.json`, a list of `{name, passed, expected, actual}`
- Running the command twice on the same input produces a byte-identical `report.json`.
- Commit the generated `report.md`, `report.json`, `narrative.md`, and `checks.json` for this example.

## Expected Values

| Block | Field | Expected |
| --- | --- | --- |
| pnl_breakdown | AAA realized capital gain | 17,835.00 |
| pnl_breakdown | BBB realized capital gain | -3,037.00 |
| pnl_breakdown | total realized capital gain | 14,798.00 |
| pnl_breakdown | BBB net dividend (gross 4,000.00, tax 400.00) | 3,600.00 |
| pnl_breakdown | AAA change in unrealized | 17,000.00 |
| pnl_breakdown | BBB change in unrealized | -8,000.00 |
| pnl_breakdown | AAA total P/L | 34,835.00 |
| pnl_breakdown | BBB total P/L | -7,437.00 |
| pnl_breakdown | total P/L | 27,398.00 |
| holdings | AAA volume / avg cost / cost value | 9,000 / 49.00 / 441,000.00 |
| holdings | AAA market value / unrealized / return % | 468,000.00 / 27,000.00 / 6.12% |
| holdings | BBB volume / avg cost / cost value | 3,000 / 20.00 / 60,000.00 |
| holdings | BBB market value / unrealized / return % | 57,000.00 / -3,000.00 / -5.00% |
| holdings | CASH | 267,398.00 |
| holdings | weights AAA / BBB / CASH | 59.06% / 7.19% / 33.75% |
| holdings | total market value (closing NAV) | 792,398.00 |
| holdings | total unrealized P/L | 24,000.00 |
| transactions | AAA average cost after 2026-10-05 buy | 49.00 |
| transactions | 2026-10-12 SELL AAA net proceeds | 164,835.00 |
| transactions | 2026-10-20 SELL BBB net proceeds | 36,963.00 |
| kpi_summary | period return % (simple, on opening NAV) | 3.83% |
| reconciliation | opening NAV | 715,000.00 |
| reconciliation | deposits / withdrawals | 50,000.00 / 0.00 |
| reconciliation | expected closing NAV | 792,398.00 |
| reconciliation | difference | 0.00 |

## Validation Rules

- Layer 1, input:
  - every CSV has exactly the columns above
  - all dates fall in the period, or equal the opening date for opening data
  - no SELL exceeds the volume held at that point
  - every held instrument has a price on both the opening date and the as-of date
  - sides come from the allowed set
- Layer 2, accounting:
  - the accounting identity holds within 0.01
  - holdings rows sum to the total row
  - weights sum to 100.00% within 0.01
  - cash in `holdings` equals the cash balance replayed from transactions
  - every number in `narrative.md` appears in `report.json` with the same formatting
- Layer 3, regression: the Expected Values table is the approved reference. Tests must assert every row.
- If any check fails, the command exits non-zero, writes `checks.json`, and does not write `report.md`.

## Writing Rules

- Audience: an institutional client reading with their relationship manager. The tone is plain, professional, and calm.
- Length: 2 to 4 short paragraphs, under 180 words in total.
- Generate narrative text from `report.json` with code, using fixed sentence templates that fill in values. Do not call an LLM at runtime.
- Every number in the text must come from `report.json` and use the same formatting as the tables.
- Describe what happened in the period: what was sold and the result, the dividend received, and how held positions moved. Do not explain why prices moved.
- No forecasts, recommendations, or investment advice.
- Avoid filler and hype, for example "robust", "impressive", "navigate", "in today's dynamic market", "it is worth noting", "delve".
- Do not start two consecutive sentences with the same word.

## Constraints

- No new runtime dependencies. Use the Python standard library only.
- Keep existing modules such as `risk.py` unchanged.
- Fixtures are synthetic. Do not add real client data.
- Existing CI checks must pass on Python 3.10–3.13: ruff check, ruff format --check, mypy (strict), pytest.

## Out of Scope

- Other report types: monthly team report and client P&L report
- Performance block (1M/3M/YTD returns, volatility, Sharpe, benchmark)
- Database or API connections; input is CSV only
- PDF output (planned as a follow-up spec)
- Thai-language output and Thai fonts
- Charts
- Forecasts or expected-return scenarios
- Multi-account or multi-strategy aggregation

## Acceptance Criteria

- [ ] The command in Output Contract generates all four output files for the example input.
- [ ] `report.md` contains all 8 blocks in the specified order.
- [ ] Every row in Expected Values is asserted by an automated test and passes.
- [ ] The accounting identity check passes with a difference of 0.00.
- [ ] Layer 1 checks reject at least these bad inputs, each covered by a test: missing column, SELL larger than holdings, missing closing price, unknown side.
- [ ] A failed check exits non-zero and does not write `report.md`.
- [ ] Every number in `narrative.md` is found in `report.json`, and a test checks this.
- [ ] Two runs on the same input produce a byte-identical `report.json`.
- [ ] Calculations use `decimal.Decimal`, not float.
- [ ] ruff, ruff format, mypy (strict), and pytest pass on Python 3.10–3.13.
- [ ] README has a short section on how to run the report.
- [ ] Changes are submitted as a draft pull request.
- [ ] Independent code review finds no unresolved blocking issues.

## Definition of Done

Produce a reviewed, CI-passing draft pull request containing the implementation, fixtures, tests, README update, and the generated sample output for `demo_coop_rg_2026_10`.

Do not merge automatically. Human approval is required.
