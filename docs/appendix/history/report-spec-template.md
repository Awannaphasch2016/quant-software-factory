# Report Spec Template (v0.1)

โครงสร้าง Spec ที่นำกลับมาใช้ซ้ำได้ สำหรับส่งงานสร้างรายงานเข้า Software Factory (Foreman / Eve)
ผ่าน GitHub Issue ที่ติด label `factory`

- สถานะ: ร่างรอบแรก (Iteration 1) ยังไม่ผ่านการทดลองรัน
- รองรับรายงาน 3 ประเภทตาม requirement_1 ข้อ 2
- เนื้อหา Issue เขียนเป็นภาษาอังกฤษ เพราะ agent ทุกสถานีใน factory อ่าน และ Issue #1 ที่รันผ่านแล้วก็เป็นภาษาอังกฤษ ส่วนคำอธิบายในเอกสารนี้เขียนเป็นภาษาไทย

---

## 1. หลักการออกแบบ

1. **Spec บอกว่าต้องได้อะไร ไม่ได้บอกว่าต้องเขียนโค้ดอย่างไร** factory ตัดสินใจเรื่อง design เอง ยกเว้นข้อจำกัดที่ระบุไว้ เช่น dependency หรือที่เก็บไฟล์
2. **โค้ดคำนวณตัวเลขทุกตัว** ข้อความบรรยายห้ามสร้างหรือแก้ตัวเลข ตัวเลขทุกตัวในข้อความต้องมาจาก `report.json`
3. **ทุก Spec ต้องมีคำตอบที่ถูกไว้ล่วงหน้า** (ตาราง Expected Values) ให้ reviewer และ test ตรวจได้ ไม่ใช่แค่ "ดูสมเหตุสมผล"
4. **รายงาน = ชุดของ block มาตรฐาน** รายงานแต่ละประเภทเป็นแค่ preset ของ block (ดูข้อ 4 และ 5) block เดียวกันมีนิยามตัวเลขเดียวกันในทุกรายงาน
5. **ไม่ใส่ข้อมูลลูกค้าจริงใน Issue** เพราะ repo เป็น public ให้ใช้ข้อมูลปลอมที่มีโครงสร้างเหมือนของจริง ข้อมูลจริงรันในขั้น "รันรายงานจริง" นอก factory

## 2. โครงของ Spec (ทุกประเภทใช้ร่วมกัน)

| # | Section | บังคับ | ใช้ทำอะไร | ใครอ่าน |
|---|---|:-:|---|---|
| 1 | Background | ✓ | ทำไมต้องมีรายงานนี้ ใครอ่าน | classifier, planner |
| 2 | Report Definition | ✓ | ประเภท, ขอบเขต (บัญชี, กลยุทธ์, ช่วงเวลา, วันที่ as-of), ภาษา, ผู้อ่าน | ทุกสถานี |
| 3 | Input Data | ✓ | ชื่อไฟล์, คอลัมน์, ชนิดข้อมูล และตัวอย่างข้อมูล (fixture) แบบ inline | implementer |
| 4 | Metric Definitions | ✓ | สูตรและนิยามของตัวเลขทุกตัว รวมถึงวิธีคิดต้นทุนและการปัดเศษ | implementer, reviewer |
| 5 | Report Blocks | ✓ | block ที่ต้องมีในรายงาน เรียงตามลำดับ | implementer |
| 6 | Output Contract | ✓ | ไฟล์ที่ต้องได้, รูปแบบ (md/pdf), ตำแหน่งไฟล์, คำสั่งรัน | implementer, reviewer |
| 7 | Expected Values | ✓ | คำตอบที่ถูกของ fixture (golden) | reviewer, tests |
| 8 | Validation Rules | ✓ | ตัวตรวจอัตโนมัติ 3 ชั้น | implementer, reviewer |
| 9 | Writing Rules | ✓ ถ้ามีข้อความบรรยาย | น้ำเสียง, ผู้อ่าน, คำต้องห้าม, กติกาตัวเลข | implementer |
| 10 | Constraints | ✓ | dependency ที่อนุญาต, สิ่งที่ห้ามแตะ | ทุกสถานี |
| 11 | Out of Scope | ✓ | สิ่งที่ไม่ต้องทำ | classifier, reviewer |
| 12 | Acceptance Criteria | ✓ | checklist ที่ reviewer ใช้ตัดสิน | reviewer |
| 13 | Definition of Done | ✓ | ผลลัพธ์สุดท้าย (draft PR, ห้าม merge เอง) | ทุกสถานี |

Section 1, 7, 12 และ 13 ใช้รูปแบบเดียวกับ Issue #1 ที่ Foreman รันสำเร็จแล้ว (Background, Expected Behavior, Acceptance Criteria, Definition of Done) ส่วนที่เหลือเพิ่มเข้ามาเพราะงานรายงานต้องการนิยามข้อมูลและตัวเลขที่ชัดกว่างานฟังก์ชันเดียว

## 3. ขนาดของ Spec: เมื่อไรควรแตก

Foreman จำกัด output ไว้ราว 100k tokens ต่อ session และ reviewer ส่งกลับให้แก้ได้ไม่เกิน 2 รอบ Spec ใบเดียวจึงควรเป็นงานที่ทำจบได้ในรอบเดียว

**1 Spec = 1 ประเภทรายงาน × 1 ชุดข้อมูล × block ไม่เกิน ~8 block**

| ถ้า Spec มีลักษณะนี้ | ทำอย่างไร |
|---|---|
| มีรายงานมากกว่า 1 ประเภท | แตกเป็นใบละประเภท |
| ต้องเชื่อมแหล่งข้อมูลใหม่ (database, API) **และ** สร้างรายงานในใบเดียวกัน | แตกเป็น (ก) data loader + validation (ข) คำนวณ + รายงาน |
| Expected Values มากกว่า ~40 แถว หรือ fixture ยาวเกิน ~100 แถว | ลด fixture หรือแตกตาม block |
| ต้องใช้ข้อมูล time series (ผลตอบแทน 1M/3M, Volatility, Sharpe) ร่วมกับ block อื่นจำนวนมาก | แยกเป็น Spec ของ block performance |
| เพิ่มตัวชี้วัด 1 ตัวในรายงานที่มีอยู่แล้ว | ใบเดียวพอ แต่ต้องมี Expected Values ของตัวใหม่ |
| แก้คำหรือรูปแบบเล็กน้อย | **เล็กเกินไป** รวมกับงานอื่นในรายงานเดียวกัน หรือแก้เองโดยไม่ผ่าน factory |

## 4. Block Catalog (block มาตรฐาน)

ได้มาจากการแตกรายงานตัวอย่างของทีม 3 ฉบับ (ดูภาคผนวก A)

| Block ID | เนื้อหา | ตัวเลขหลัก (นิยามดูข้อ 6) |
|---|---|---|
| `header` | ชื่อรายงาน, ลูกค้า, บัญชี, กลยุทธ์, วันที่ as-of, ช่วงเวลา, request id | – |
| `kpi_summary` | การ์ดตัวเลขสำคัญ | NAV, capital invested, realized P/L, dividend, unrealized P/L, return % |
| `allocation` | น้ำหนักพอร์ตตามหลักทรัพย์หรือกลยุทธ์ (ตารางหรือ pie) | weight % |
| `holdings` | ตารางหลักทรัพย์ที่ถือ | volume, avg cost, cost value, market price, market value, unrealized P/L, return % |
| `pnl_breakdown` | แยกกำไรขาดทุนของงวด | realized capital gain, dividend, change in unrealized, total P/L |
| `realized_by_period` | realized P/L แยกรายเดือนหรือรายปี | capital gain, dividend, total |
| `transactions` | รายการซื้อขาย ปันผล เงินเข้าออก | date, instrument, side, qty, price, fee, amount, realized P/L |
| `performance` | ผลตอบแทนเทียบ benchmark | return 1M/3M/YTD/since inception, volatility, Sharpe (**ต้องมี NAV series**) |
| `per_strategy` | ทำ block ย่อยซ้ำทีละกลยุทธ์หรือทีละบัญชี | ตาม block ย่อยที่เลือก |
| `reconciliation` | ตารางกระทบยอดตามสมการบัญชี | opening NAV, flows, P/L, closing NAV, difference |
| `narrative` | ข้อความบรรยายสั้น | ห้ามมีตัวเลขที่ไม่อยู่ใน JSON |
| `disclaimer` | ข้อความข้อจำกัดความรับผิดชอบ (ข้อความตายตัว) | – |

## 5. Presets ของรายงาน 3 ประเภท

| Block | 1. รายงานประจำเดือน (`monthly_team`) | 2. P&L ลูกค้า (`client_pnl`) | 3. ผลตอบแทนและรายการลงทุน (`returns_transactions`) |
|---|:-:|:-:|:-:|
| `header` | ✓ | ✓ | ✓ |
| `kpi_summary` | ✓ | ✓ | ✓ |
| `allocation` | ✓ (ตามกลยุทธ์) | ✓ | ✓ |
| `holdings` | – | ✓ | ✓ |
| `pnl_breakdown` | – | ✓ | ✓ |
| `realized_by_period` | ✓ รายเดือน | ✓ รายปี | ตัวเลือก |
| `transactions` | – | ✓ | ✓ |
| `performance` | ✓ | ✓ | – |
| `per_strategy` | ✓ | ✓ | – |
| `reconciliation` | ✓ | ✓ | ✓ |
| `narrative` | ✓ (ภายในทีม) | ✓ (ลูกค้า) | ✓ (ลูกค้า) |
| `disclaimer` | – | ✓ | ✓ |
| ผู้อ่านหลัก | ทีม Quant / ผู้บริหาร | ลูกค้า | ลูกค้า (ใช้ประกอบการคุย) |
| ระดับความเสี่ยง (จากรายงาน Software Factory หัวข้อ 5) | ต่ำถึงกลาง | สูง | สูง |

ข้อมูลขาเข้าที่ต้องมีตาม block:

| ข้อมูล | ใช้กับ block |
|---|---|
| `opening_positions` (ยอดยกมาต้นงวด) | holdings, pnl_breakdown, reconciliation |
| `transactions` (buy/sell/dividend/deposit/withdrawal) | transactions, pnl_breakdown, realized_by_period, reconciliation |
| `prices` (ราคาต้นงวดและปลายงวด) | holdings, allocation, pnl_breakdown |
| `nav_series` (NAV รายวัน) และ `benchmark_series` | performance |
| `strategy_map` (บัญชี → กลยุทธ์) | per_strategy, allocation ตามกลยุทธ์ |

## 6. นิยามตัวเลขมาตรฐาน (ค่าเริ่มต้น)

ใช้ค่าเหล่านี้ถ้า Spec ไม่ได้ระบุเป็นอย่างอื่น ถ้าจะเปลี่ยน ต้องเขียนไว้ใน Section 4 ของ Spec

| ตัวเลข | นิยาม |
|---|---|
| วิธีคิดต้นทุน | **Weighted average cost** ค่าธรรมเนียมซื้อรวมเข้าต้นทุน |
| Realized capital gain (ต่อรายการขาย) | (qty × price − fee) − (avg cost ก่อนขาย × qty) |
| Dividend | บันทึกยอด gross, ภาษีหัก ณ ที่จ่าย และ net โดยใช้ **net** ในการคำนวณ P/L |
| Cost value | volume × avg cost |
| Market value | volume × ราคาปลายงวด (เงินสดใช้ราคา 1.00) |
| Unrealized P/L | market value − cost value |
| NAV | Σ market value ของหลักทรัพย์ + เงินสด |
| Total P/L ของงวด | realized capital gain + dividend (net) + (unrealized ปลายงวด − unrealized ต้นงวด) |
| สมการบัญชี | NAV ต้นงวด + เงินเข้า − เงินออก + Total P/L = NAV ปลายงวด |
| Weight % | market value / NAV × 100 |
| การปัดเศษ | คำนวณเต็มความละเอียด (Decimal) แล้วปัดเฉพาะตอนแสดงผล: จำนวนเงิน 2 ตำแหน่ง, % 2 ตำแหน่ง, ปัดแบบ half-up |
| ความคลาดเคลื่อนที่ยอมรับ | ≤ 0.01 ต่อค่า |

## 7. Output Contract มาตรฐาน

```
reports/<report_id>/
  report.md       ← สำหรับคนอ่าน (หรือ report.pdf ตามช่อง Output format)
  report.json     ← ตัวเลขทุกตัว จัดกลุ่มตาม block ID (reviewer อ่าน PDF ใน diff ไม่ได้)
  narrative.md    ← ข้อความบรรยาย (ถ้ามี block narrative)
  checks.json     ← ผลตัวตรวจทุกข้อ: name, passed, expected, actual
```

- ต้องสร้างได้ด้วยคำสั่งเดียวที่ระบุไว้ใน Spec และรันซ้ำกับข้อมูลเดิมต้องได้ `report.json` เหมือนเดิมทุกไบต์
- `report.json` ใช้ key เป็น block ID จากข้อ 4
- **Output format** มี 2 แบบ:
  - `md` (ค่าเริ่มต้น): ไม่ต้องเพิ่ม dependency, GitHub แสดงผลใน PR และบนมือถือได้, reviewer อ่านใน diff ได้
  - `pdf`: ต้องระบุ library ที่อนุญาตไว้ใน Constraints เพราะ repo ไม่มี runtime dependency และต้องได้รับอนุมัติจากเจ้าของ repo ก่อน
- requirement_1 ไม่ได้บังคับรูปแบบไฟล์ จึงเริ่มที่ `md` แล้วทำ `pdf` เป็น Spec แยก

## 8. Validation Rules (ตัวตรวจ 3 ชั้น)

| ชั้น | ตรวจอะไร | ใน factory รอบนี้ |
|---|---|---|
| 1. ข้อมูลขาเข้า | schema, ห้ามว่าง, วันที่อยู่ในงวด, ไม่มีขายเกินจำนวนที่ถือ, ราคามีครบทุกหลักทรัพย์ | ✓ |
| 2. เงื่อนไขทางบัญชี | สมการบัญชี, ผลรวมของ holdings = ยอดรวม, weight รวม = 100%, ตัวเลขในข้อความตรงกับ JSON | ✓ |
| 3. เทียบกับรายงานที่อนุมัติแล้ว | สร้างรายงานย้อนหลังแล้ว diff กับฉบับที่อนุมัติ | ใช้ Expected Values แทน จนกว่าจะมีข้อมูลดิบของรายงานจริง |

ถ้าตัวตรวจข้อใดไม่ผ่าน คำสั่งต้องจบด้วย exit code ≠ 0 และต้องไม่สร้างไฟล์รายงาน (`report.md` หรือ `report.pdf`)

## 9. Writing Rules มาตรฐาน (ย่อ)

รายละเอียดอยู่ใน Natural Writing Proposal

- ระบุผู้อ่านและน้ำเสียงใน Spec ทุกครั้ง เช่น ลูกค้าสถาบันใช้ภาษาทางการแต่ไม่แข็ง
- ตัวเลขในข้อความต้องดึงจาก `report.json` เท่านั้น และต้องเขียนรูปแบบเดียวกับในตาราง
- ห้ามคาดการณ์อนาคตหรือให้คำแนะนำการลงทุน (อยู่นอกขอบเขตของ factory)
- ห้ามใช้วลีที่อยู่ในรายการคำต้องห้าม (เริ่มจาก `agent/skills/writing-quality/references/ai-phrases-to-avoid.md` ใน eve-software-factory-template)

## 10. ช่องว่างสำหรับกรอก (คัดลอกส่วนนี้ไปเป็น Issue body)

````markdown
Feature: <Report name> — <scope> as of <YYYY-MM-DD>

## Background
<Who reads this report, why it exists, what decision or conversation it supports.>

## Report Definition
| Field | Value |
| --- | --- |
| Report type | monthly_team / client_pnl / returns_transactions |
| Report ID | <snake_case id, used as output folder> |
| Client / Account | <synthetic name> / <synthetic account> |
| Strategy | <name or "all"> |
| Period | <YYYY-MM-DD> to <YYYY-MM-DD> |
| As-of date | <YYYY-MM-DD> |
| Currency | THB |
| Language | en / th |
| Audience | <client / internal> |
| Output format | md / pdf |

## Input Data
Commit these fixtures to `<path>` exactly as given.

### <file_name>.csv
Columns: <name (type, meaning)>, ...
```csv
<rows>
```

## Metric Definitions
Use the defaults in the Report Spec Template §6 unless overridden here:
- <overrides, or "No overrides.">

## Report Blocks
In this order: `<block_id>`, `<block_id>`, ...
<Per-block notes: columns, sort order, labels.>

## Output Contract
- Command: `<single command>`
- Writes `reports/<report_id>/report.<md|pdf>`, `report.json`, `narrative.md`, `checks.json`.
- `report.json` keys are block IDs.

## Expected Values
| Block | Field | Expected |
| --- | --- | --- |
| <block> | <field> | <value> |

## Validation Rules
- Layer 1 (input): <rules>
- Layer 2 (accounting): <rules>
- Layer 3 (regression): Expected Values above are the approved reference.
Any failed check exits non-zero and produces no report file.

## Writing Rules
- Audience and tone: <...>
- Every number in narrative text must appear in `report.json`, formatted the same way.
- No forecasts, recommendations, or investment advice.
- <length limit, banned phrases>

## Constraints
- Allowed new dependencies: <list or "none"; output format pdf needs an approved PDF library here>
- <Do not touch / keep existing modules unchanged.>

## Out of Scope
- <...>

## Acceptance Criteria
- [ ] <...>

## Definition of Done
Produce a reviewed, CI-passing draft pull request containing the implementation, fixtures, tests, and one generated sample report.
Do not merge automatically. Human approval is required.
````

---

## ภาคผนวก A: ที่มาของ Block Catalog

แตกรายงานตัวอย่างของทีม 3 ฉบับ (ไม่ระบุชื่อลูกค้า เพราะเป็นข้อมูลจริง) เป็น block แล้ววางเทียบกัน

| Block | ตัวอย่าง A: Program Trading Portfolio (หลายกลยุทธ์, สร้างจากระบบ) | ตัวอย่าง B: Grid Trade Performance (กลยุทธ์เดียว, สร้างจากระบบ) | ตัวอย่าง C: Performance Report (ภาษาไทย, ทำใน Canva) |
|---|:-:|:-:|:-:|
| header | ✓ | ✓ | ✓ |
| kpi_summary | ✓ | ✓ | ✓ |
| realized_by_period | ✓ รายปี | – | ✓ รายเดือน |
| performance | ✓ 1M/3M/YTD/SI, vol, Sharpe | – | ✓ 3M/6M/SI |
| allocation | ✓ | ✓ | ✓ ตามกลยุทธ์ |
| holdings | ✓ | ✓ | – |
| transactions | ✓ | ✓ | – |
| per_strategy | ✓ 10 กลยุทธ์ | ✓ รายหุ้น | ✓ 2 บัญชี |
| กรณีขายทั้งพอร์ต / ผลตอบแทนที่คาดหวัง | – | – | ✓ |
| disclaimer | ✓ | ✓ | – |

ข้อสังเกตที่นำมาใช้ในการออกแบบ:
- ยอดรวมในตัวอย่าง A กระทบกันได้ภายในฉบับ (ผลรวมของ unrealized และ NAV รายกลยุทธ์เท่ากับยอดรวมทั้งพอร์ต ต่างกันไม่เกิน 0.01) จึงใช้เป็นต้นแบบของตัวตรวจชั้นที่ 2 ได้
- พบป้ายกำกับที่อาจไม่ตรงกับตัวเลข เช่น ป้าย "since inception" อยู่บนตัวเลขที่ตรงกับยอด YTD จึงกำหนดให้ทุก Spec ต้องมี Metric Definitions ที่ชัด (รอยืนยันกับทีมว่าเป็นบั๊กหรือนิยามที่ตั้งใจ)
- "กรณีขายทั้งพอร์ต / ผลตอบแทนที่คาดหวัง" ในตัวอย่าง C เป็นการคาดการณ์ จึงอยู่นอกขอบเขตของ factory ตามรายงาน Software Factory หัวข้อ 5 และยังไม่ใส่ใน Block Catalog
