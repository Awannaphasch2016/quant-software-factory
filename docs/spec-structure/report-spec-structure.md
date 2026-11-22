# Report Spec Structure (v0.3)

โครงสร้าง Spec สำหรับส่งงานสร้างรายงานเข้า Software Factory (Foreman) ผ่าน GitHub Issue ที่ติด label `factory` ไฟล์นี้รวม Template v0.2 (โครงหลัก) กับส่วนที่เปลี่ยนใน v0.3 เฉพาะส่วนของรายงาน ส่วนชั้นข้อมูล (Dataset Catalog, `load(...)`, ตัวเช็คชั้น A) อยู่ใน [`platform-spec-structure.md`](platform-spec-structure.md)

- สถานะ:
  - Demonstrated กับรายงาน `returns_transactions` ผ่าน Issue #7 → PR #8 และ Issue #9 → PR #10 (merge แล้วทั้งคู่)
  - `client_pnl` มี preset แต่ยังไม่ได้รัน (Intended)
  - `monthly_team` ยังเป็นโครงเปิด (Intended)
- ตัวอย่างที่กรอกแล้ว: [`../specs/report-spec.md`](../specs/report-spec.md) (Report Spec) และ [`../specs/platform-spec.md`](../specs/platform-spec.md) (Platform Spec) ใน folder เดียวกัน
- ส่วนที่ยังไม่มีข้อมูลมีป้าย `[ต้องการข้อมูล: ...]` ใช้กับโรงงานได้ทันทีด้วย fixture ส่วนการต่อกับข้อมูลจริงเป็นงาน Intended
- ฉบับเดิม (v0.1, v0.2 และส่วนที่เปลี่ยนใน v0.3) เก็บไว้ใน [`../history/`](../history/) เป็นประวัติ

---

## 1. หลักการ

1. ไม่คำนวณตัวเลขใหม่ ตัวเลขทุกช่องในรายงานต้องโยงกลับไปที่ field ในชุดข้อมูลต้นทางได้ (Data Mapping) โค้ดทำได้แค่เลือก จัดรูปแบบ รวมยอดเพื่อแสดงผล และเช็ค
2. ข้อความบรรยายห้ามสร้างหรือแก้ตัวเลข ตัวเลขในข้อความต้องอยู่ใน `report.json`
3. ทุก Spec มีคำตอบที่ถูกไว้ล่วงหน้า (Expected Values) ที่คำนวณจาก fixture
4. ไม่ใส่ข้อมูลหรือโครงสร้างระบบภายในใน Issue repo เป็น public ห้ามใส่ข้อมูลลูกค้าจริง, IP, ชื่อ server, ชื่อ database, ชื่อตารางจริง หรือ URL ภายใน ให้ใช้**ชื่อกลาง (logical name)** ตาม Dataset Catalog ใน [`platform-spec-structure.md`](platform-spec-structure.md) แล้วเก็บ mapping ไปยังของจริงไว้ฝั่งภายใน
5. โรงงานรันกับ fixture เท่านั้น sandbox ของโรงงานเข้าระบบภายในไม่ได้ โค้ดจึงต้องอ่านข้อมูลผ่าน interface ที่เปลี่ยนจาก fixture เป็นของจริงได้โดยไม่แก้ส่วนอื่น

## 2. Spec 2 ชนิด

| ชนิด | ทำเมื่อ | มีอะไร | ตัวอย่าง |
|---|---|---|---|
| Platform Spec | ครั้งเดียว หรือเมื่อเพิ่มชุดข้อมูลใหม่ | interface `load(...)`, `DataSource` / `FixtureSource`, schema registry, fixture, ตัวเช็คชั้น A ดู [`platform-spec-structure.md`](platform-spec-structure.md) | [`../specs/platform-spec.md`](../specs/platform-spec.md) (Issue #7) |
| Report Spec | ทุกครั้งที่ต้องการรายงานใหม่ | Report Definition, Data Mapping, block, Expected Values, ตัวเช็คชั้น B, Writing Rules | [`../specs/report-spec.md`](../specs/report-spec.md) (Issue #9) |

- Report Spec ใช้ data layer จาก Platform Spec ที่ merge แล้ว และห้ามแก้ data layer
- ข้อความบรรยายอยู่ใน Report Spec ใบเดียวกัน Issue #9 ทำทั้งรายงานและข้อความบรรยายจบในใบเดียว โดยต้อง Approve token 1 ครั้ง
- ถ้ารายงานใหม่ต้องใช้ชุดข้อมูลที่ยังไม่มีใน data layer (เช่น `monthly_business`) ให้เปิด Platform Spec เพิ่มชุดข้อมูลนั้นก่อน

## 3. หัวข้อของ Report Spec

| # | หัวข้อ | บังคับ | ใช้ทำอะไร |
|---|---|:-:|---|
| 1 | Background | ✓ | ทำไมต้องมีรายงานนี้ ใครอ่าน data layer มาจาก Issue ไหน |
| 2 | Report Definition | ✓ | ประเภท, report ID, บัญชี, งวด, opening date, as-of date, ภาษา, ผู้อ่าน, Output format |
| 3 | Data Sources | ✓ | ชุดข้อมูลที่ใช้ (ชื่อกลาง) และ fixture ที่มีอยู่แล้ว |
| 4 | Data Mapping | ✓ | ช่องในรายงาน → ชุดข้อมูล.field และรูปแบบการแสดงผล |
| 5 | Report Blocks | ✓ | block ที่ต้องมี เรียงลำดับ พร้อมหมายเหตุของแต่ละ block |
| 6 | Output Contract | ✓ | คำสั่งรัน, ไฟล์, ลำดับการรันตัวเช็ค, กรณีไม่ผ่าน |
| 7 | Expected Values | ✓ | คำตอบที่ถูกจาก fixture |
| 8 | Number Checks | ✓ | ตัวเช็คชั้น B พร้อมสมการ |
| 9 | Writing Rules | ถ้ามี narrative | ผู้อ่าน, ความยาว, ลำดับหัวข้อ, กติกาตัวเลข, ตัวเช็คการเขียน |
| 10 | Constraints | ✓ | base branch, depends on, dependency, ข้อห้ามเรื่องข้อมูลภายใน |
| 11 | Out of Scope | ✓ | สิ่งที่ไม่ต้องทำ |
| 12 | Open Items | ✓ | ป้าย `[ต้องการข้อมูล]` ทั้งหมดใน Spec รวมไว้ที่เดียว ถ้าไม่มีให้เขียน "None" |
| 13 | Acceptance Criteria | ✓ | checklist ที่ reviewer ใช้ |
| 14 | Definition of Done | ✓ | draft PR, ห้าม merge เอง |

หมายเหตุ: Issue #9 ไม่มีหัวข้อ Open Items เพราะไม่มีข้อมูลที่ขาด ฉบับนี้จึงกำหนดให้เขียน "None"

## 4. ขนาดของ Spec

| ถ้า | ทำอย่างไร |
|---|---|
| repo ยังไม่มีโครงโปรเจกต์ (pyproject, CI) | เปิด Spec "project setup" แยกก่อน |
| repo ยังไม่มี data layer | เปิด Platform Spec ก่อน แล้ว merge |
| data layer มีแล้ว | เปิด Report Spec ใบเดียวต่อรายงาน 1 ฉบับ |
| มีรายงานมากกว่า 1 ประเภท | แตกเป็นใบละประเภท |
| Report Spec มีมากกว่า 6 block | แตก block ที่ไม่บังคับออกไปไว้ใบถัดไป |
| แก้คำหรือรูปแบบเล็กน้อย | เล็กเกินไป รวมกับงานอื่น |

ผลที่วัดได้:

| Run | Spec | ผล |
|---|---|---|
| #1 | 8 block รวมการคำนวณ (v0.1) | ชนเพดาน output token 100K กลางขั้น implement |
| #2 | 6 block + ตัวเช็ค 11 ข้อ รวม data layer (v0.2) | ชนเพดาน 44.9K ต้นขั้น implement ไม่ถึง Output |
| #3 | Platform Spec | ไม่ชนเพดาน ได้ PR ใน 12 นาที 34 วินาที |
| #4 | Report Spec 6 block, Expected Values 21 แถว, ตัวเช็คชั้น B และการเขียน 15 ข้อ | ชนเพดาน 100K หลังขั้น implement Approve 1 ครั้งแล้วได้ PR ใน 3 นาที 21 วินาที |

กติกา 6 block ยังไม่พอให้ Report Spec จบใน session เดียว และผลจาก 1 run ยังไม่พอจะตั้งเกณฑ์ใหม่

## 5. ชุดข้อมูลที่ใช้ได้

- ใช้ชุดข้อมูลตาม Dataset Catalog ใน [`platform-spec-structure.md`](platform-spec-structure.md) ข้อ 3 และอ่านผ่าน `load(...)` เท่านั้น
- บน `main` ตอนนี้มี fixture 6 ชุด: `account_info`, `nav_daily`, `holdings_daily`, `cash_flow`, `transactions`, `performance`
- ถ้ารายงานต้องใช้ชุดข้อมูลหรือ field ที่ยังไม่มี ให้เปิด Platform Spec เพิ่มก่อน ห้ามให้ Report Spec คำนวณแทน

## 6. Block Catalog

ทุกตัวเลขใน block มาจาก Data Mapping การรวมยอดเพื่อแสดงแถว Total ทำได้ แต่ต้องมีตัวเช็คว่าตรงกับยอดรวมในชุดข้อมูลต้นทาง

| Block ID | เนื้อหา | ชุดข้อมูลหลัก |
|---|---|---|
| `header` | ชื่อรายงาน, ลูกค้า, บัญชี, กลยุทธ์, งวด, วันที่ as-of, report ID | `account_info` |
| `kpi_summary` | NAV, เงินสด, capital gain, dividend, unrealized P/L, total P/L, return | `nav_daily`, `performance` |
| `allocation` | น้ำหนักตามหลักทรัพย์หรือกลยุทธ์ | `holdings_daily`, `nav_daily` |
| `holdings` | ตารางหุ้นคงเหลือ + แถว CASH + แถว Total | `holdings_daily`, `nav_daily` |
| `realized_by_period` | realized P/L แยกรายปีหรือรายเดือน | `performance` |
| `transactions` | รายการซื้อขาย ปันผล เงินเข้าออก | `transactions`, `cash_flow` |
| `performance` | ผลตอบแทนเทียบ benchmark | `performance`, `benchmark_series` |
| `per_strategy` | ทำ block ย่อยซ้ำต่อกลยุทธ์หรือต่อบัญชี | ตาม block ย่อย |
| `grid_status` | หน่วยตั้งต้น หน่วยปัจจุบัน NAV volume ต่อหุ้น | `grid_nav_vol` |
| `narrative` | ข้อความบรรยายสั้น | `report.json` เท่านั้น |
| `disclaimer` | ข้อความตายตัว | ไม่มี |

## 7. Presets ของรายงาน 3 ประเภท

| Block | 1. รายงานประจำเดือน (`monthly_team`) | 2. P&L ลูกค้า (`client_pnl`) | 3. ผลตอบแทนและรายการลงทุน (`returns_transactions`) |
|---|:-:|:-:|:-:|
| `header` | ✓ | ✓ | ✓ |
| `kpi_summary` | ✓ | ✓ | ✓ |
| `allocation` | `[ต้องการข้อมูล]` | ✓ | ไม่ได้ใช้ใน Issue #9 |
| `holdings` | | ✓ | ✓ |
| `realized_by_period` | | ✓ | |
| `transactions` | | | ✓ |
| `performance` | | ✓ | |
| `per_strategy` | | ✓ | |
| `grid_status` | | | ตัวเลือก (กลยุทธ์ grid) |
| `narrative` | ✓ | ✓ | ✓ |
| `disclaimer` | | ✓ | ✓ |
| ต้นแบบจากรายงานของทีม | `[ต้องการข้อมูล: ยังไม่รู้ว่าเป็นรายงานไหน]` | Program Trading Portfolio | Grid Trade Performance |
| ชุดข้อมูลที่ยังขาด | `monthly_business` | `benchmark_series`, `volatility`, `sharpe` | ไม่มี |
| สถานะ | โครงเปิด (Intended) | มี preset ยังไม่ได้รัน (Intended) | **Demonstrated** (Issue #9 → PR #10) |

หมายเหตุ:
- รายงานแบบ event (เช่น รายงานที่ทำใน Canva) อยู่นอกขอบเขต
- `client_pnl` เต็มรูปแบบมีมากกว่า 6 block ต้องแตกเป็น 2 Report Spec ตามข้อ 4
- Issue #9 ใช้ 6 block: header, kpi_summary, holdings, transactions, narrative, disclaimer

## 8. Output Contract มาตรฐาน

```
reports/<report_id>/
  report.md       ← สำหรับคนอ่าน (หรือ report.pdf ถ้า Output format = pdf)
  report.json     ← ตัวเลขทุกตัว key เป็น block ID
  narrative.md    ← ถ้ามี block narrative
  checks.json     ← ผลตัวเช็คชั้น A และ B: name, layer, passed, expected, actual เรียงตาม name
```

| เรื่อง | มาตรฐาน |
|---|---|
| Report ID | ชื่อ folder ของ output |
| ตัวเลขใน JSON | string ที่จัดรูปแบบแล้ว เหมือนในตาราง เช่น `"792,398.00"`, `"3.83%"` |
| ทศนิยม | จำนวนเงิน 2 ตำแหน่ง, % 2 ตำแหน่ง, ปัดแบบ half-up, ใช้ Decimal |
| ค่าว่าง | `null` ใน JSON และเว้นว่างในตาราง |
| ค่าลบที่เป็นศูนย์ | แสดงเป็น `0.00` |
| การรันซ้ำ | ข้อมูลเดิมต้องได้ `report.json` และ `checks.json` เหมือนเดิมทุกไบต์ |
| ข้อมูลหัวรายงาน | อ่านจาก `account_info` **ห้าม hard-code ในโค้ด** |
| Output format | `md` เป็นค่าเริ่มต้น `pdf` ต้องได้รับอนุมัติ dependency ก่อน |
| ลำดับการรัน | ตัวเช็คชั้น A ก่อน ถ้าไม่ผ่านไม่สร้างรายงาน และรายงานตัวเช็คชั้น B ว่า not run |
| เมื่อเช็คไม่ผ่าน | exit 1, เขียน `checks.json` อย่างเดียว และลบไฟล์รายงานเก่าที่ค้าง |

## 9. Number Checks

ชั้น A (ข้อมูล) อยู่ใน data layer แล้ว รายละเอียดใน [`platform-spec-structure.md`](platform-spec-structure.md) ข้อ 5 Report Spec เรียกผ่าน `run_checks(...)` ก่อนสร้างรายงาน และรวมผลไว้ใน `checks.json`

### ชั้น B: รายงาน (เขียนใน Report Spec)

Report Spec แต่ละใบเลือกตัวเช็คที่ใช้จาก catalog นี้ แล้วตั้งเลข B1, B2, ... ของตัวเองพร้อมสมการ

| ชนิดตัวเช็ค | ตัวอย่าง | ใน Issue #9 |
|---|---|---|
| ค่าที่ map ครบ | ทุกช่องใน Data Mapping มีค่า ถ้าไม่มีให้ไม่ผ่าน ไม่ใช่ crash | B0 (โรงงานเพิ่มเอง) |
| ผลรวมในตาราง = ยอดรวม | Σ `holdings.market_value` + `cash` = `nav` | B1 |
| ผลรวมย่อย = ผลรวมใหญ่ | Σ `holdings.market_value` = `nav_daily.market_value` หรือ Σ NAV รายกลยุทธ์ = NAV ทั้งพอร์ต | B2 |
| ความสอดคล้องในแถว | `market_value − cost_value = unrealized_pl` | B3 |
| ยอดเดียวกันตรงกันทุก block | NAV ใน `kpi_summary` = Total ใน `holdings` | B4 |
| สมการบัญชี | NAV ต้นงวด + เงินเข้า − เงินออก + total P/L = NAV ปลายงวด | B5 |
| ส่วนประกอบ P/L | `capital_gain + dividend + unrealized_change = total_pl` | B6 |
| realized ผูกกับรายการ | Σ `realized_pl` ของ SELL = `capital_gain`, Σ ปันผล = `dividend` | B7 (แยก 2 ข้อ) |
| ตัวเลขในข้อความ | ทุกจำนวนเงินและ % ใน `narrative.md` อยู่ใน `report.json` แบบตรงตัวอักษร หรือเป็นค่าสัมบูรณ์ของค่าลบใน JSON วันที่ ปี และจำนวนนับไม่ตรวจ | B8 |
| น้ำหนักรวม 100% | Σ weight = 100.00% ± 0.01 | ไม่ใช้ |
| ป้ายกำกับตรงกับช่วงเวลา | ยอด YTD ต้องไม่ถูกแสดงด้วยป้าย "since inception" | ไม่ใช้ |

ความคลาดเคลื่อนที่ยอมรับ: ≤ 0.01 ต่อค่า เทียบค่า Decimal ก่อนปัด (R5)

## 10. Writing Rules มาตรฐาน

- ระบุผู้อ่านและน้ำเสียงทุกครั้ง
- กำหนดความยาว (จำนวนย่อหน้าและคำ) และลำดับหัวข้อของข้อความ
- สร้างข้อความจาก `report.json` ด้วยโค้ดและ sentence template ไม่เรียก LLM ตอนรัน (ขั้นต่อไปอยู่ใน Natural Writing Proposal)
- ตัวเลขในข้อความต้องมาจาก `report.json` และใช้รูปแบบเดียวกับตาราง
- ค่าติดลบให้เขียนเป็นความหมาย: "a realized loss of 3,037.00 THB" ไม่ใช่ "a realized capital gain of -3,037.00 THB"
- เอกพจน์/พหูพจน์ต้องตรงกับจำนวนรายการ: "a deposit of" เมื่อมีรายการเดียว
- ประโยคติดกันห้ามขึ้นต้นด้วยคำเดียวกัน
- เล่าสิ่งที่เกิดขึ้น ไม่อธิบายสาเหตุที่ราคาขึ้นลง
- ห้ามคาดการณ์อนาคตหรือให้คำแนะนำการลงทุน
- ห้ามใช้คำในรายการคำต้องห้าม (ดู Natural Writing Proposal)

ตัวเช็คการเขียน รายงานใน `checks.json` เป็นชั้น B และถ้าไม่ผ่านรายงานก็ไม่ผ่าน:

| ID | ตรวจ |
|---|---|
| W1 | ไม่มีคำต้องห้าม |
| W2 | ไม่มี "gain of -" |
| W3 | ประโยคติดกันไม่ขึ้นต้นซ้ำ |
| W4 | ความยาวอยู่ในกรอบ |
| W5 | ไม่มีคำคาดการณ์ ("will", "expect", "should", "recommend") |

## 11. ช่องว่างสำหรับกรอก (คัดลอกส่วนนี้ไปเป็น Issue body)

ดูตัวอย่างที่กรอกครบแล้วใน [`../specs/report-spec.md`](../specs/report-spec.md)

````markdown
Feature: <Report name> from precomputed data — <client>, <period>

## Background
<Who reads this report and what it supports.>

The team's pipeline already computes every figure. This report reads those figures, lays them out, checks that they agree with each other, and adds a short narrative. It must not recompute any figure that a dataset provides.

The data layer already exists on `main` (merged from #<platform spec issue>): `DataSource`, `FixtureSource`, the schema registry and the Layer A data checks. Build on it. Do not change its behavior.

## Report Definition
| Field | Value |
| --- | --- |
| Report type | monthly_team / client_pnl / returns_transactions |
| Report ID | <snake_case id> |
| Account | <synthetic> |
| Client, strategy, inception | from `account_info` |
| Period | <YYYY-MM> (<YYYY-MM-DD> to <YYYY-MM-DD>) |
| Opening date | <YYYY-MM-DD> |
| As-of date | <YYYY-MM-DD> |
| Currency | THB |
| Language | en / th |
| Audience | <client / internal> |
| Output format | md / pdf |

## Data Sources
Use the existing fixtures in `data/fixtures/<report_id>/` through `FixtureSource` and `load(...)`. Do not add or change fixtures. Datasets used: <list>.

## Data Mapping
| Block | Report field | Dataset.field | Display |
| --- | --- | --- | --- |
| <block> | <label> | <dataset.field> | money / pct / int / date / text |

Formats:
- money: 2 decimals, thousands separators, minus sign for negatives, `-0.00` shown as `0.00`
- pct: 2 decimals followed by `%`
- int: thousands separators
- Use `decimal.Decimal` with ROUND_HALF_UP

If a mapped value is missing, the report fails. Do not derive it from other fields.

## Report Blocks
In this order, one `##` section per block in `report.md`:
1. `<block_id>`: <columns, sort order, which rows to include, labels>

## Output Contract
- Command: `<single command>`
- The report ID is the output folder name.
- Writes `report.md`, `report.json` (keys are block IDs; numbers are formatted strings; not-applicable values are `null`), `narrative.md`, `checks.json` (Layer A from `run_checks(...)` plus Layer B, `{name, layer, passed, expected, actual}`, sorted by name).
- If any check fails: exit 1, write `checks.json`, write no other file, and remove stale report files.
- Run Layer A first. If it fails, build nothing and report Layer B checks as not run.
- Two runs on the same input give byte-identical `report.json` and `checks.json`.

## Expected Values
| Block | Field | Expected |
| --- | --- | --- |

## Number Checks (Layer B)
- B1 <name>: <exact equation>
- ...
- B<n> narrative numbers: every money or percent value in `narrative.md` appears in `report.json` with the same formatting, or as the absolute value of a negative value there. Dates, years and counts are not checked.

Tolerance 0.01 per value. Compare unrounded `Decimal` values.

## Writing Rules
- Audience: <...>
- <N> to <M> short paragraphs, under <W> words.
- Generate the text from `report.json` with code, using fixed sentence templates. Do not call an LLM at runtime.
- Cover, in this order: <topics>
- Write negative values as losses. Match singular and plural to the count.
- No two consecutive sentences start with the same word.
- Describe what happened. Do not explain why prices moved.
- No forecasts, recommendations, or investment advice. Do not use "will", "expect", "should", or "recommend".
- Do not use these phrases: <banned list>

Writing checks, reported in `checks.json` as Layer B: W1 no banned phrase, W2 no "gain of -", W3 no repeated sentence opener, W4 within the length limits, W5 no forecast words. A failed writing check fails the report like any other check.

## Constraints
- Base branch: `main`.
- Depends on: #<platform spec issue> (merged).
- Standard library only.
- Put new code under `src/quant_software_factory/reporting/`. Reuse `FixtureSource`, `load(...)`, the schema registry and `run_checks(...)`. Do not change their behavior.
- No hard-coded client, account, strategy or inception values in code.
- No server names, IP addresses, database or table names, internal URLs, or credentials anywhere.

## Out of Scope
- Changing the data layer or fixtures
- Production data sources
- <...>

## Open Items
- <every [needs data] item in this spec, or "None">

## Acceptance Criteria
- [ ] The pull request targets `main` and the branch is cut from `main`.
- [ ] The command writes all output files for the fixture and exits 0.
- [ ] `report.md` has the blocks in order.
- [ ] Every row in Expected Values is asserted by a test.
- [ ] Each Layer B and writing check has a test with an input that makes it fail.
- [ ] When Layer A fails, no report files are written and Layer B checks are reported as not run.
- [ ] No figure in Data Mapping is computed from other fields. Totals rows are display sums checked by a Layer B check.
- [ ] Data is read only through the existing `load(...)`.
- [ ] Two runs give byte-identical `report.json` and `checks.json`.
- [ ] ruff check, ruff format --check, mypy (strict) and pytest pass in CI on Python 3.10–3.13.
- [ ] Submitted as a draft pull request.
- [ ] Independent review finds no unresolved blocking issues.

## Definition of Done
A reviewed, CI-passing draft pull request against `main` with the report builder, Layer B and writing checks, tests, a README section, and the generated output for `<report_id>`.

Do not merge automatically. Human approval is required.
````

## 12. Open Items ของ Structure นี้

Open Items ของชั้นข้อมูล (คอลัมน์จริง, ข้อมูลตัวอย่าง, `InternalSource`, ตัวเช็คชั้น A ของ pipeline, ชื่อตารางใน public repo) อยู่ใน [`platform-spec-structure.md`](platform-spec-structure.md) ข้อ 7

| # | เรื่อง | กระทบ | ถามใคร |
|---|---|---|---|
| R1 | มีโค้ดสร้างรายงาน Program Trading และ Grid อยู่แล้วหรือไม่ จะใช้ของเดิมหรือสร้างใหม่ | ขอบเขต | พี่ Anak |
| R2 | รายงานประจำเดือนของฝ่าย Quant คือรายงานไหน | ข้อ 7 | พี่ Anak |
| R3 | ป้ายกำกับที่ดูไม่ตรงกับตัวเลขในรายงานตัวอย่าง (เช่น "since inception" บนยอด YTD) เป็นบั๊กหรือนิยาม | ข้อ 9 | เจ้าของรายงาน |
| R4 | เพิ่มเพดาน output token ต่อ session ได้หรือไม่ เพื่อให้ Report Spec จบโดยไม่ต้อง Approve | ข้อ 4 | พี่ Anak |
| R5 | ความคลาดเคลื่อน 0.01 ต่อค่า ใช้ได้กับรายงานของทีมหรือไม่ | ข้อ 9 | เจ้าของ pipeline |

## 13. ประวัติเวอร์ชันและ gap ที่ยังเปิด

| เวอร์ชัน | สิ่งที่เปลี่ยน | ทดสอบใน |
|---|---|---|
| v0.1 | Spec ให้โรงงานคำนวณตัวเลขเอง (Metric Definitions) | Run #1: Issue #4 → PR #5 |
| v0.2 | Data Mapping แทนสูตร, ชื่อกลาง, `load(...)`, ตัวเช็ค 2 ชั้น, base branch, Open Items | Run #2: Issue #6 (ไม่ถึง Output) |
| v0.3 | แยก Platform Spec กับ Report Spec, A2 ให้ชุดข้อมูลรายการว่างได้, B8 ตรวจเฉพาะเงินและ % และยอมรับค่าสัมบูรณ์, เครื่องหมายเงินถอน, ลำดับการรันตัวเช็ค, W1–W5 | Run #3 และ #4: Issue #7 → PR #8, Issue #9 → PR #10 |

Gap ที่พบใน Run #4 และยังไม่ได้แก้ (สำหรับ v0.4):

| ประเภท | จุดที่พบ | แนวทาง |
|---|---|---|
| Specification | Writing Rules สั่งให้พูดถึง "การเปลี่ยนแปลงของ NAV" แต่ไม่มีตัวเลขนี้ในชุดข้อมูล | เพิ่ม opening NAV (`nav_daily.nav` ที่ opening date) ใน Data Mapping หรือตัดคำว่า "change" ออก |
| Specification | ไม่ได้บอกว่างวดของรายงานคิดจาก opening date หรือเดือนของ as-of | ระบุใน Report Definition และให้ตรวจว่า opening date คือวันสุดท้ายของเดือนก่อน |
| Specification | ตัวเช็ค "ค่าที่ map ครบ" (B0) ไม่มีใน Spec โรงงานเพิ่มเอง | ใส่ไว้ใน catalog ข้อ 9 แล้ว ต้องเพิ่มเข้าช่องกรอกใน v0.4 |
| Design | Report Spec ยังชนเพดาน 100K ก่อนขั้น review | R4 หรือลดขนาด Report Spec แล้ววัดซ้ำ |
