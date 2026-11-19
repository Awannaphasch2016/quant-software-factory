# Report Spec Template (v0.2, โครงเปิด)

โครงสร้าง Spec สำหรับส่งงานสร้างรายงานเข้า Software Factory (Foreman) ผ่าน GitHub Issue ที่ติด label `factory`

- สถานะ: ร่าง ยังไม่ได้รันกับโรงงาน (v0.1 รันแล้ว 1 ครั้งใน Issue #4)
- ต่างจาก v0.1 ตรงที่**ไม่คำนวณตัวเลขเอง** ตัวเลขทุกตัวมาจากชุดข้อมูลที่ pipeline ของทีมคำนวณไว้แล้ว งานของโรงงานคือดึงข้อมูล จัดลงรายงาน และเช็คตัวเลข
- เป็น**โครงเปิด** ส่วนที่ยังไม่มีข้อมูลจะมีป้าย `[ต้องการข้อมูล: ...]` ใช้กับโรงงานได้ทันทีด้วย fixture ส่วนการต่อกับข้อมูลจริงเป็นงาน Intended
- v0.1 เก็บไว้ที่ [`report-spec-template.md`](report-spec-template.md) เป็นหลักฐานของ Run #1 ไม่ได้แก้

---

## 1. หลักการ

1. **ไม่คำนวณตัวเลขใหม่** ตัวเลขทุกช่องในรายงานต้องโยงกลับไปที่ field ในชุดข้อมูลต้นทางได้ (Data Mapping) โค้ดทำได้แค่เลือก จัดรูปแบบ รวมยอดเพื่อแสดงผล และเช็ค
2. **ข้อความบรรยายห้ามสร้างหรือแก้ตัวเลข** ตัวเลขในข้อความต้องอยู่ใน `report.json`
3. **ทุก Spec มีคำตอบที่ถูกไว้ล่วงหน้า** (Expected Values) ที่คำนวณจาก fixture
4. **ไม่ใส่ข้อมูลหรือโครงสร้างระบบภายในใน Issue** repo เป็น public ห้ามใส่ข้อมูลลูกค้าจริง, IP, ชื่อ server, ชื่อ database, ชื่อตารางจริง หรือ URL ภายใน ให้ใช้**ชื่อกลาง (logical name)** ตามข้อ 4 แล้วเก็บ mapping ไปยังของจริงไว้ฝั่งภายใน
5. **โรงงานรันกับ fixture เท่านั้น** sandbox ของโรงงานเข้าระบบภายในไม่ได้ โค้ดจึงต้องอ่านข้อมูลผ่าน interface ที่เปลี่ยนจาก fixture เป็นของจริงได้โดยไม่แก้ส่วนอื่น

## 2. โครงของ Spec

| # | Section | บังคับ | ใช้ทำอะไร | เปลี่ยนจาก v0.1 |
|---|---|:-:|---|---|
| 1 | Background | ✓ | ทำไมต้องมีรายงานนี้ ใครอ่าน | |
| 2 | Report Definition | ✓ | ประเภท, ขอบเขต, วันที่ as-of, ภาษา, ผู้อ่าน, Output format | |
| 3 | Data Sources | ✓ | ชุดข้อมูลที่ใช้ (ชื่อกลาง) และ fixture แบบ inline | เดิมคือ Input Data (ธุรกรรมดิบ) |
| 4 | Data Mapping | ✓ | ช่องในรายงาน → ชุดข้อมูล.field และรูปแบบการแสดงผล | **ใหม่** แทน Metric Definitions |
| 5 | Report Blocks | ✓ | block ที่ต้องมี เรียงลำดับ | |
| 6 | Output Contract | ✓ | ไฟล์, รูปแบบตัวเลข, ค่าว่าง, คำสั่งรัน | เพิ่มรูปแบบตัวเลขและค่าว่าง |
| 7 | Expected Values | ✓ | คำตอบที่ถูกจาก fixture | |
| 8 | Number Checks | ✓ | ตัวเช็ค 2 ชั้น: ข้อมูล และ รายงาน | **เปลี่ยน** จาก Validation Rules |
| 9 | Writing Rules | ถ้ามี narrative | ผู้อ่าน น้ำเสียง กติกาตัวเลข | เพิ่มกติกาค่าติดลบและเอกพจน์/พหูพจน์ |
| 10 | Constraints | ✓ | base branch, depends on, dependency, การเข้าถึงข้อมูล | เพิ่ม base branch และ depends on |
| 11 | Out of Scope | ✓ | สิ่งที่ไม่ต้องทำ | |
| 12 | Open Items | ✓ | ป้าย `[ต้องการข้อมูล]` ทั้งหมดใน Spec รวมไว้ที่เดียว | **ใหม่** |
| 13 | Acceptance Criteria | ✓ | checklist ที่ reviewer ใช้ | |
| 14 | Definition of Done | ✓ | draft PR, ห้าม merge เอง | |

## 3. ขนาดของ Spec

Run #1 (8 block, รวมการคำนวณ) ใช้ output token ครบเพดาน 100K ต่อ session ระหว่างขั้น implement จึงปรับกติกาให้เล็กลง

**1 Spec = 1 ประเภทรายงาน × block ไม่เกิน 5–6 block**

| ถ้า Spec มีลักษณะนี้ | ทำอย่างไร |
|---|---|
| มีรายงานมากกว่า 1 ประเภท | แตกเป็นใบละประเภท |
| ต้องสร้าง data access layer **และ** รายงานในใบเดียว | แตกเป็น (ก) data access + Number Checks ชั้นข้อมูล (ข) รายงาน + Number Checks ชั้นรายงาน โดยใบ (ข) ใส่ `Depends on: #<ก>` |
| block เกิน 6 หรือ Expected Values เกินประมาณ 40 แถว | แตกตาม block |
| repo ยังไม่มีโครงโปรเจกต์ (pyproject, CI) | เปิด Spec "project setup" แยกก่อน |
| แก้คำหรือรูปแบบเล็กน้อย | เล็กเกินไป รวมกับงานอื่น |

## 4. Dataset Catalog (ชื่อกลาง)

ชุดข้อมูลที่ pipeline ของทีมคำนวณไว้แล้ว ใช้ชื่อกลางใน Spec เสมอ mapping ไปยังตารางจริงเก็บไว้ฝั่งภายใน `[ต้องการข้อมูล: รายชื่อคอลัมน์จริงของแต่ละชุด]`

| ชื่อกลาง | เนื้อหา | ระดับข้อมูล | field ที่คาดว่าใช้ (ชื่อกลาง) | สถานะ mapping |
|---|---|---|---|---|
| `account_info` | บัญชี ลูกค้า กลยุทธ์ วันเริ่ม | ต่อบัญชี | `account_no`, `client_name`, `strategy`, `inception_date`, `product` | รอ |
| `nav_daily` | NAV เงินสด มูลค่าพอร์ต รายวัน | ต่อบัญชี ต่อวัน | `date`, `account_no`, `nav`, `cash`, `market_value` | รอ |
| `holdings_daily` | หุ้นคงเหลือพร้อมทุน มูลค่า และกำไรที่ยังไม่รับรู้ | ต่อบัญชี ต่อหุ้น ต่อวัน | `date`, `account_no`, `instrument`, `volume`, `avg_cost`, `cost_value`, `market_price`, `market_value`, `unrealized_pl` | รอ |
| `cash_flow` | เงินเข้าออกและการถอนกำไร | ต่อบัญชี ต่อรายการ | `date`, `account_no`, `flow_type`, `amount` | รอ |
| `transactions` | รายการซื้อขาย ปันผล พร้อมกำไรที่รับรู้ | ต่อรายการ | `date`, `account_no`, `instrument`, `side`, `qty`, `price`, `amount`, `realized_pl` | รอ |
| `performance` | ผลตอบแทนตามช่วงเวลา และ realized แยกรายปี | ต่อบัญชี | `period`, `return_pct`, `volatility`, `sharpe`, `capital_gain`, `dividend` | รอ |
| `benchmark_series` | ผลตอบแทนของ benchmark | ต่อวัน | `date`, `benchmark`, `value` | รอ |
| `grid_nav_vol` | NAV และ volume ของกลยุทธ์ grid | ต่อบัญชี ต่อหุ้น | `initial_units`, `current_units`, `nav_volume`, `gain_volume` | รอ |
| `monthly_business` | ตัวเลขรายเดือนของทีม (เช่น AUM, revenue, ค่าธรรมเนียม) | ต่อ product ต่อเดือน | `[ต้องการข้อมูล]` | รอยืนยันว่าเป็นรายงานประจำเดือนจริงหรือไม่ |

กติกา:
- ถ้า Spec ต้องใช้ field ที่ไม่อยู่ในตารางนี้ ให้เพิ่มแถวใหม่ใน Catalog ก่อน แล้วระบุใน Open Items
- ห้ามให้โรงงานคำนวณ field ที่ควรมาจาก pipeline เช่น ถ้า `unrealized_pl` ไม่มีใน fixture ให้ถือเป็นข้อมูลขาด ไม่ใช่ให้คำนวณจาก `market_value − cost_value`

## 5. Data Access

โค้ดทุกตัวที่โรงงานเขียนต้องอ่านข้อมูลผ่าน interface เดียว

```
load(dataset: str, as_of: date, accounts: list[str]) -> list[row]
```

| Implementation | ใครทำ | สถานะ |
|---|---|---|
| `FixtureSource`: อ่านไฟล์ CSV ใน `data/fixtures/<report_id>/<dataset>.csv` | โรงงาน | ทำได้ทันที |
| `InternalSource`: อ่านจากระบบภายในของทีม | ทีมภายใน (ไม่ทำใน public repo) | Intended `[ต้องการข้อมูล: repo หรือ pipeline ปลายทางที่จะรันโค้ด]` |

ข้อห้าม: โค้ดใน public repo ต้องไม่มีชื่อ server, IP, ชื่อ database, ชื่อตารางจริง หรือ credential

## 6. Block Catalog

ทุกตัวเลขใน block มาจาก Data Mapping การรวมยอด (sum) เพื่อแสดงแถว Total ทำได้ แต่ต้องมี Number Check ว่าตรงกับยอดรวมในชุดข้อมูลต้นทาง (ถ้ามี)

| Block ID | เนื้อหา | ชุดข้อมูลหลัก |
|---|---|---|
| `header` | ชื่อรายงาน, ลูกค้า, บัญชี, กลยุทธ์, วันที่ as-of, report id | `account_info` |
| `kpi_summary` | NAV, capital gain, dividend, unrealized P/L, realized P/L | `nav_daily`, `performance`, `holdings_daily` |
| `allocation` | น้ำหนักตามหลักทรัพย์หรือกลยุทธ์ | `holdings_daily`, `nav_daily` |
| `holdings` | ตารางหุ้นคงเหลือ | `holdings_daily` |
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
| `allocation` | `[ต้องการข้อมูล]` | ✓ | ✓ |
| `holdings` | | ✓ | ✓ |
| `realized_by_period` | | ✓ | |
| `transactions` | | | ✓ |
| `performance` | | ✓ | |
| `per_strategy` | | ✓ | |
| `grid_status` | | | ตัวเลือก (กลยุทธ์ grid) |
| `narrative` | ✓ | ✓ | ✓ |
| `disclaimer` | | ✓ | ✓ |
| ต้นแบบจากรายงานของทีม | `[ต้องการข้อมูล: ยังไม่รู้ว่าเป็นรายงานไหน]` | Program Trading Portfolio | Grid Trade Performance |
| สถานะ | โครงเปิด | พร้อมเขียน Spec | พร้อมเขียน Spec |

หมายเหตุ:
- รายงานแบบ event (เช่น รายงานที่ทำใน Canva) อยู่นอกขอบเขตรอบนี้
- `monthly_team` อาจใช้ชุดข้อมูล `monthly_business` (AUM, revenue, ค่าธรรมเนียมรายเดือนแยก product) แต่ยังไม่ได้ยืนยันกับทีม
- `client_pnl` เต็มรูปแบบมีมากกว่า 6 block ต้องแตกเป็น 2 Spec ตามข้อ 3

## 8. Output Contract มาตรฐาน

```
reports/<report_id>/
  report.md       ← สำหรับคนอ่าน (หรือ report.pdf ถ้า Output format = pdf)
  report.json     ← ตัวเลขทุกตัว key เป็น block ID
  narrative.md    ← ถ้ามี block narrative
  checks.json     ← ผลตัวเช็คทุกข้อ: name, layer, passed, expected, actual
```

| เรื่อง | มาตรฐาน |
|---|---|
| ตัวเลขใน JSON | string ที่จัดรูปแบบแล้ว เหมือนในตาราง เช่น `"792,398.00"`, `"6.12%"` |
| ทศนิยม | จำนวนเงิน 2 ตำแหน่ง, % 2 ตำแหน่ง, ปัดแบบ half-up, ใช้ Decimal |
| ค่าว่าง | `null` ใน JSON และเว้นว่างในตาราง |
| ค่าลบที่เป็นศูนย์ | แสดงเป็น `0.00` |
| การรันซ้ำ | ข้อมูลเดิมต้องได้ `report.json` เหมือนเดิมทุกไบต์ |
| ข้อมูลหัวรายงาน | อ่านจาก `account_info` หรือไฟล์ `report_meta.csv` ใน fixture **ห้าม hard-code ในโค้ด** |
| Output format | `md` เป็นค่าเริ่มต้น `pdf` ต้องได้รับอนุมัติ dependency ก่อน |
| เมื่อเช็คไม่ผ่าน | exit code ≠ 0, เขียน `checks.json`, ไม่เขียนไฟล์รายงาน และลบไฟล์รายงานเก่าที่ค้าง |

## 9. Number Checks (2 ชั้น)

### ชั้น A: ข้อมูล (ก่อนทำรายงาน)

pipeline ของทีมมีตัวเช็คชั้นนี้อยู่แล้วบางส่วน เช่น เช็คความสดของ NAV, เช็คหุ้นคงเหลือเทียบกับข้อมูลดิบของระบบหลังบ้าน และการแจ้งเตือนเมื่อเช็คไม่ผ่าน `[ต้องการข้อมูล: แต่ละตัวเช็คอะไรและยอมให้ต่างได้เท่าไร]`

| ตัวเช็ค | ในโรงงาน (fixture) | ของจริง |
|---|---|---|
| A1 ความสด: วันล่าสุดของ `nav_daily` = วันที่ as-of | เขียนใหม่ | ใช้ตัวเช็คเดิมของ pipeline (Intended) |
| A2 ความครบ: ทุกบัญชีในขอบเขตมีข้อมูลทุกชุดที่ Spec ใช้ | เขียนใหม่ | เขียนใหม่หรือใช้ของเดิม `[ต้องการข้อมูล]` |
| A3 schema: ทุกชุดมี field ตาม Data Mapping และชนิดข้อมูลถูก | เขียนใหม่ | เหมือนกัน |
| A4 ตรงกับข้อมูลดิบ: หุ้นคงเหลือตรงกับระบบหลังบ้าน | ข้าม (ไม่มีข้อมูลดิบใน fixture) | ใช้ตัวเช็คเดิมของ pipeline (Intended) |

### ชั้น B: รายงาน (หลังจัดข้อมูลลงรายงาน)

โรงงานเขียนและ test ได้ทั้งหมดกับ fixture

| ตัวเช็ค | ตัวอย่าง |
|---|---|
| B1 ผลรวมในตาราง = ยอดรวม | Σ `holdings.market_value` + `cash` = `nav` |
| B2 ผลรวมย่อย = ผลรวมใหญ่ | Σ NAV รายกลยุทธ์ = NAV ทั้งพอร์ต |
| B3 น้ำหนักรวม 100% | Σ weight = 100.00% ± 0.01 |
| B4 ยอดเดียวกันตรงกันทุก block | NAV ใน `kpi_summary` = NAV ใน `holdings` |
| B5 สมการบัญชี (ถ้ามีข้อมูลต้นงวด) | NAV ต้นงวด + เงินเข้า − เงินออก + P/L = NAV ปลายงวด |
| B6 ตัวเลขในข้อความ | ทุกตัวเลขใน `narrative.md` อยู่ใน `report.json` |
| B7 ป้ายกำกับตรงกับช่วงเวลา | field ที่เป็นยอด YTD ต้องไม่ถูกแสดงด้วยป้าย "since inception" |

ความคลาดเคลื่อนที่ยอมรับ: ≤ 0.01 ต่อค่า `[ต้องการข้อมูล: ยืนยันกับทีม]`

## 10. Writing Rules มาตรฐาน (ย่อ)

- ระบุผู้อ่านและน้ำเสียงทุกครั้ง
- ตัวเลขในข้อความต้องมาจาก `report.json` และใช้รูปแบบเดียวกับตาราง
- ค่าติดลบให้เขียนเป็นความหมาย: "ขาดทุน 3,037.00" หรือ "a realized loss of 3,037.00" ไม่ใช่ "กำไร −3,037.00"
- เอกพจน์/พหูพจน์ต้องตรงกับจำนวนรายการ
- ห้ามคาดการณ์อนาคตหรือให้คำแนะนำการลงทุน
- ห้ามใช้คำในรายการคำต้องห้าม (ดู Natural Writing Proposal)

## 11. ช่องว่างสำหรับกรอก (คัดลอกส่วนนี้ไปเป็น Issue body)

````markdown
Feature: <Report name> — <scope> as of <YYYY-MM-DD>

## Background
<Who reads this report and what it supports.>

## Report Definition
| Field | Value |
| --- | --- |
| Report type | monthly_team / client_pnl / returns_transactions |
| Report ID | <snake_case id> |
| Client / Account | <synthetic> / <synthetic> |
| Strategy | <name or "all"> |
| As-of date | <YYYY-MM-DD> |
| Period (if any) | <YYYY-MM-DD> to <YYYY-MM-DD> |
| Currency | THB |
| Language | en / th |
| Audience | <client / internal> |
| Output format | md / pdf |

## Data Sources
All numbers come from precomputed datasets. Do not recompute them.
Read data only through `load(dataset, as_of, accounts)`. Implement a fixture-backed source that reads `data/fixtures/<report_id>/<dataset>.csv`.
Commit these fixtures exactly as given. They are synthetic.

### <dataset>.csv
Fields: <logical name (type, meaning)>, ...
```csv
<rows>
```

## Data Mapping
| Block | Report field | Dataset.field | Display format |
| --- | --- | --- | --- |
| <block> | <label> | <dataset.field> | money 2dp / pct 2dp / int / date |
If a mapped field is missing in the data, fail check A3. Do not derive it from other fields.

## Report Blocks
In this order: `<block_id>`, ...
<Per-block notes: columns, sort order, which rows to include, labels.>

## Output Contract
- Command: `<single command>`
- Writes `reports/<report_id>/report.<md|pdf>`, `report.json`, `narrative.md`, `checks.json`.
- Follow the standard rules: formatted strings in JSON, `null` for not applicable, Decimal with ROUND_HALF_UP, byte-identical reruns, no hard-coded report metadata.

## Expected Values
| Block | Field | Expected |
| --- | --- | --- |

## Number Checks
- Layer A (data): A1 freshness, A2 completeness, A3 schema.
- Layer B (report): <list B1–B7 that apply, with the exact equations>.
- Tolerance: 0.01 per value.
Any failed check exits non-zero, writes `checks.json`, and writes no report file.

## Writing Rules
- Audience and tone: <...>
- Numbers only from `report.json`, same formatting as tables.
- Write negative values as losses, match singular and plural to counts.
- No forecasts, recommendations, or investment advice.

## Constraints
- Base branch: <main or branch name>.
- Depends on: <#issue or "none">.
- Allowed new dependencies: <list or "none">.
- No server names, IP addresses, database or table names, internal URLs, or credentials in code or docs.

## Out of Scope
- <...>

## Open Items
- <every [needs data] item in this spec, or "none">

## Acceptance Criteria
- [ ] The command writes all output files for the fixture.
- [ ] Every Expected Values row is asserted by a test.
- [ ] Every Number Check is implemented and has a failing-input test.
- [ ] No number is computed that the Data Mapping says comes from a dataset.
- [ ] Data is read only through `load(...)`.
- [ ] Two runs give a byte-identical `report.json`.
- [ ] Lint, format, type checks, and tests pass in CI.
- [ ] Submitted as a draft pull request.
- [ ] Independent review finds no unresolved blocking issues.

## Definition of Done
A reviewed, CI-passing draft pull request with the implementation, fixtures, tests, and one generated sample report.
Do not merge automatically. Human approval is required.
````

## 12. Open Items ของ Template นี้

| # | เรื่อง | กระทบ | ถามใคร |
|---|---|---|---|
| O1 | รายชื่อคอลัมน์จริงของแต่ละชุดข้อมูล (สำหรับ mapping ภายใน) | ข้อ 4 | เจ้าของ pipeline |
| O2 | ตัวอย่างข้อมูลจริงที่ลบข้อมูลระบุตัวตนแล้ว (เพื่อให้ fixture มีรูปแบบตรงของจริง) | ข้อ 4, fixture | เจ้าของ pipeline |
| O3 | repo หรือ pipeline ปลายทางที่จะรันโค้ด | ข้อ 5 | พี่ Anak |
| O4 | มีโค้ดสร้างรายงาน Program Trading และ Grid อยู่แล้วหรือไม่ จะใช้ของเดิมหรือสร้างใหม่ | ขอบเขต | พี่ Anak |
| O5 | ตัวเช็คชั้น A ที่มีอยู่แล้วเช็คอะไร และความคลาดเคลื่อนที่ยอมรับ | ข้อ 9 | เจ้าของ pipeline |
| O6 | รายงานประจำเดือนของฝ่าย Quant คือรายงานไหน | ข้อ 7 | พี่ Anak |
| O7 | เขียนชื่อตารางจริงใน public repo ได้หรือไม่ (ตอนนี้ถือว่าไม่ได้) | หลักการข้อ 4 | พี่ Anak |
| O8 | ป้ายกำกับที่ดูไม่ตรงกับตัวเลขในรายงานตัวอย่าง (เช่น "since inception" บนยอด YTD) เป็นบั๊กหรือนิยาม | ตัวเช็ค B7 | เจ้าของรายงาน |

## 13. สิ่งที่แก้จาก v0.1 (จาก Run #1)

| Gap จาก Run #1 | แก้ใน v0.2 |
|---|---|
| ไม่ได้ระบุ base branch | Constraints: `Base branch`, `Depends on` |
| ข้อมูลหัวรายงานถูก hard-code ในโค้ด | Output Contract: ห้าม hard-code อ่านจาก `account_info` หรือ `report_meta.csv` |
| ไม่ได้กำหนดรูปแบบตัวเลขใน JSON | Output Contract: string ที่จัดรูปแบบแล้ว |
| ไม่ได้กำหนดค่าว่าง | Output Contract: `null` |
| "one row per instrument" ไม่ชัด | Spec ต้องระบุในหมายเหตุของ block ว่าแถวไหนแสดง (เช่น เฉพาะที่ volume > 0) |
| เงินที่อยู่นอกนิยาม | ไม่เกี่ยวแล้ว เพราะไม่คำนวณเอง แต่ถ้าข้อมูลขาดให้ fail A3 แทนการคำนวณแทน |
| ภาษาแข็งเรื่องค่าติดลบและพหูพจน์ | Writing Rules |
| Spec ใหญ่จนชนเพดาน token | ขนาด Spec: ไม่เกิน 5–6 block และแยก data access ออกจากรายงานได้ |
| (ใหม่) ตัวเลขถูกคำนวณไว้แล้วใน pipeline | Data Mapping แทน Metric Definitions, ห้ามคำนวณใหม่ |
