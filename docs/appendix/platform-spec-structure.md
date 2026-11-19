# Platform Spec Structure (v0.3)

โครงสร้าง Spec สำหรับสร้างชั้นข้อมูล (data layer) ที่ Report Spec ทุกใบใช้ร่วมกัน ส่งเข้า Software Factory (Foreman) ผ่าน GitHub Issue ที่ติด label `factory` เหมือน Report Spec

- สถานะ: Demonstrated 1 ครั้ง (Issue #7 → PR #8, merge แล้ว commit `9455ea3`) โรงงานทำจบใน session เดียวโดยไม่ต้อง Approve
- ตัวอย่างที่กรอกแล้ว: [`platform-spec.md`](platform-spec.md) (Issue: [#7](https://github.com/Awannaphasch2016/quant-software-factory/issues/7))
- ใช้คู่กับ [`report-spec-structure.md`](report-spec-structure.md)
- ส่วนที่ยังไม่มีข้อมูลมีป้าย `[ต้องการข้อมูล: ...]`

---

## 1. Platform Spec ทำอะไร

| ชนิด | ทำเมื่อ | มีอะไร |
|---|---|---|
| **Platform Spec (ไฟล์นี้)** | ครั้งเดียว หรือเมื่อต้องเพิ่มชุดข้อมูลใหม่ | interface `load(...)`, `DataSource` / `FixtureSource`, schema registry, fixture, ตัวเช็คชั้น A |
| Report Spec | ทุกครั้งที่ต้องการรายงานใหม่ | ดู [`report-spec-structure.md`](report-spec-structure.md) |

ต้องเปิด Platform Spec เมื่อ:
- repo ยังไม่มี data layer (ใน Iteration 1 คือ Issue #7)
- รายงานใหม่ต้องใช้ชุดข้อมูลหรือ field ที่ยังไม่มี เช่น `monthly_business` สำหรับรายงานประจำเดือน หรือ `benchmark_series`, `volatility`, `sharpe` สำหรับ P&L ลูกค้า

Platform Spec ไม่มีรายงาน output มีแค่ `checks.json` ของตัวเช็คชั้น A

## 2. หลักการ

1. ไม่คำนวณตัวเลขใหม่ data layer อ่านค่าที่ pipeline ของทีมคำนวณไว้แล้ว และส่งต่อเป็น string ดิบ ไม่แปลงหรือคำนวณ
2. อ่านข้อมูลผ่าน interface เดียว โค้ดรายงานทุกตัวเรียก `load(...)` เท่านั้น เพื่อให้เปลี่ยนจาก fixture เป็นข้อมูลจริงได้โดยไม่แก้โค้ดรายงาน
3. ไม่ใส่ข้อมูลหรือโครงสร้างระบบภายในใน Issue repo เป็น public ห้ามใส่ข้อมูลลูกค้าจริง, IP, ชื่อ server, ชื่อ database, ชื่อตารางจริง หรือ URL ภายใน ให้ใช้ชื่อกลาง (logical name) ตามข้อ 3 แล้วเก็บ mapping ไปยังของจริงไว้ฝั่งภายใน
4. โรงงานรันกับ fixture เท่านั้น fixture เป็นข้อมูลปลอมที่กรอกไว้ใน Spec และต้อง commit ตามที่ให้ทุกตัวอักษร

## 3. Dataset Catalog (ชื่อกลาง)

ใช้ชื่อกลางใน Spec เสมอ `[ต้องการข้อมูล: รายชื่อคอลัมน์จริงของแต่ละชุด]`

| ชื่อกลาง | เนื้อหา | ระดับข้อมูล | field (ชื่อกลาง) | สถานะ |
|---|---|---|---|---|
| `account_info` | บัญชี ลูกค้า กลยุทธ์ วันเริ่ม | ต่อบัญชี | `account_no`, `client_name`, `strategy`, `inception_date`, `product` | มี fixture บน `main` |
| `nav_daily` | NAV เงินสด มูลค่าพอร์ต รายวัน | ต่อบัญชี ต่อวัน | `date`, `account_no`, `nav`, `cash`, `market_value` | มี fixture บน `main` |
| `holdings_daily` | หุ้นคงเหลือพร้อมทุน มูลค่า และกำไรที่ยังไม่รับรู้ | ต่อบัญชี ต่อหุ้น ต่อวัน | `date`, `account_no`, `instrument`, `volume`, `avg_cost`, `cost_value`, `market_price`, `market_value`, `unrealized_pl` | มี fixture บน `main` |
| `cash_flow` | เงินเข้าออก | ต่อบัญชี ต่อรายการ | `date`, `account_no`, `flow_type` (`DEPOSIT` / `WITHDRAWAL`), `amount` (บวก) | มี fixture บน `main` |
| `transactions` | รายการซื้อขาย ปันผล พร้อมกำไรที่รับรู้ | ต่อรายการ | `date`, `account_no`, `instrument`, `side` (`BUY` / `SELL` / `DIVIDEND`), `qty`, `price`, `fee`, `tax`, `amount`, `realized_pl` | มี fixture บน `main` |
| `performance` | ผลตอบแทนและ P/L ของงวด | ต่อบัญชี ต่อเดือน | `period`, `account_no`, `capital_gain`, `dividend`, `unrealized_change`, `total_pl`, `return_pct` | มี fixture บน `main` |
| `benchmark_series` | ผลตอบแทนของ benchmark | ต่อวัน | `date`, `benchmark`, `value` | ยังไม่มี |
| `grid_nav_vol` | NAV และ volume ของกลยุทธ์ grid | ต่อบัญชี ต่อหุ้น | `initial_units`, `current_units`, `nav_volume`, `gain_volume` | ยังไม่มี |
| `monthly_business` | ตัวเลขรายเดือนของทีม (เช่น AUM, revenue, ค่าธรรมเนียม) | ต่อ product ต่อเดือน | `[ต้องการข้อมูล]` | ยังไม่มี รอยืนยันว่าเป็นรายงานประจำเดือนจริงหรือไม่ |

กติกา:
- ห้ามให้โรงงานคำนวณ field ที่ควรมาจาก pipeline เช่น ถ้า `unrealized_pl` ไม่มีใน fixture ให้ถือเป็นข้อมูลขาด ไม่ใช่ให้คำนวณจาก `market_value − cost_value`
- `volatility` และ `sharpe` ยังไม่อยู่ใน `performance` บน `main`

## 4. Data Access

```python
def load(
    dataset: str, as_of: date, accounts: Sequence[str]
) -> list[dict[str, str]]: ...
```

- คืนค่า string ดิบของแต่ละแถว key เป็นชื่อ field สำหรับบัญชีที่ขอ
- ชุดข้อมูลที่มี `date` คืนแถวที่ `date <= as_of` ส่วน `performance` คืนแถวที่เดือนไม่เกินเดือนของ as-of และ `account_info` คืนทุกแถวของบัญชี
- ชื่อชุดข้อมูลที่ไม่รู้จักให้ raise `KeyError`

| Implementation | ใครทำ | สถานะ |
|---|---|---|
| `DataSource` (`typing.Protocol`) | โรงงาน | Demonstrated (PR #8, `reporting/source.py`) |
| `FixtureSource(root)`: อ่าน `<root>/<dataset>.csv` | โรงงาน | Demonstrated (PR #8) |
| schema registry: กำหนด field และชนิดของแต่ละชุดครั้งเดียว ใช้ทั้งตอนอ่านและตัวเช็ค A3 | โรงงาน | Demonstrated (PR #8, `reporting/schema.py`) |
| `InternalSource`: อ่านจากระบบภายในของทีม | ทีมภายใน (ไม่ทำใน public repo) | Intended `[ต้องการข้อมูล: repo หรือ pipeline ปลายทางที่จะรันโค้ด]` |

## 5. ตัวเช็คชั้น A (ข้อมูล ก่อนทำรายงาน)

| ตัวเช็ค | กติกา | ในโรงงาน (fixture) | ของจริง |
|---|---|---|---|
| A1 ความสด | วันล่าสุดของ `nav_daily` ของบัญชี = วันที่ as-of | Demonstrated (PR #8) | ใช้ตัวเช็คเดิมของ pipeline (Intended) |
| A2 ความครบ | `account_info`, `nav_daily`, `holdings_daily`, `performance` มีข้อมูลของบัญชี; `nav_daily` มีวัน opening และ as-of; `performance` มีเดือน as-of; `transactions` และ `cash_flow` ว่างได้ | Demonstrated (PR #8) | `[ต้องการข้อมูล]` |
| A3 schema | field ครบไม่มีเกิน (ลำดับใดก็ได้), ค่าที่บังคับไม่ว่าง, parse ได้ตามชนิด (`Decimal`, `int`, ISO date, `YYYY-MM`), enum ถูก, ไฟล์ไม่หาย | Demonstrated (PR #8) | เหมือนกัน |
| A4 ตรงกับข้อมูลดิบ | หุ้นคงเหลือตรงกับระบบหลังบ้าน | ข้าม (ไม่มีข้อมูลดิบใน fixture) | ใช้ตัวเช็คเดิมของ pipeline (Intended) |

- ถ้า A3 ไม่ผ่านสำหรับชุดข้อมูลใด ตัวเช็ค A1 และ A2 ที่ต้องใช้ชุดนั้นให้รายงานว่า not run พร้อมเหตุผล ระบุให้ตรงว่าตัวเช็คไหนใช้ชุดไหน (A1 ใช้แค่ `nav_daily`)
- pipeline ของทีมมีตัวเช็คชั้นนี้อยู่แล้วบางส่วน `[ต้องการข้อมูล: แต่ละตัวเช็คอะไรและยอมให้ต่างได้เท่าไร]`
- Report Spec เรียกตัวเช็คชุดนี้ผ่าน `run_checks(...)` ก่อนสร้างรายงาน

## 6. ช่องว่างสำหรับกรอก (คัดลอกส่วนนี้ไปเป็น Issue body)

ดูตัวอย่างที่กรอกครบแล้วใน [`platform-spec.md`](platform-spec.md)

````markdown
Feature: Report data access layer and data checks — precomputed datasets, fixture source

## Background
The Quant team's reports are built from datasets that the team's pipeline has already computed. Report code must never recompute those figures. It reads them, lays them out, and checks them.

This issue adds <the data layer / the datasets <list>>. It adds no report. Its output is a data-check result.

## Report Definition
| Field | Value |
| --- | --- |
| Report type | <used by later Report Specs> |
| Report ID | <snake_case id, also the fixture folder name> |
| Account | <synthetic> |
| Opening date | <YYYY-MM-DD> |
| As-of date | <YYYY-MM-DD> |

## Data Sources
Read data only through this interface:

```python
def load(dataset: str, as_of: date, accounts: Sequence[str]) -> list[dict[str, str]]: ...
```

- Returns the raw string values of each row, keyed by field name, for the given accounts.
- For datasets with a `date` field, returns rows with `date <= as_of`. For `performance`, returns rows whose `period` month is not after the as-of month. `account_info` has no date and returns all rows for the accounts.
- Raises `KeyError` for an unknown dataset name.

Implement `FixtureSource(root: Path)`, which reads `<root>/<dataset>.csv`. Keep the interface (a `typing.Protocol` named `DataSource`) separate from the fixture implementation, so a production source can be added later without touching callers. Do not add a production source.

Commit these fixtures to `data/fixtures/<report_id>/` exactly as given. All values are synthetic.

### <dataset>.csv
Fields: `<field>` (<type>), ...

```csv
<header>
<rows>
```

Define each dataset's fields and types once, in a schema registry in code, and use it for both loading and check A3.

## Data Checks (Layer A)
- A1 freshness: the latest `nav_daily.date` for the account equals the as-of date.
- A2 completeness: <which datasets must have rows, which dates must exist, which datasets may be empty>.
- A3 schema: exact fields in any order with no extras; required values not blank; values parse to their declared types; enum fields contain only the listed values; a missing file fails A3 for that dataset.

If A3 fails for a dataset, the A1 and A2 checks that read that dataset are reported as not run, with the reason.

## Output Contract
- Command: `python -m quant_software_factory.reporting.check_data data/fixtures/<report_id> --account <account> --opening <date> --as-of <date> --out reports/<report_id>`
- Writes `reports/<report_id>/checks.json`: a list of `{"name", "layer", "passed", "expected", "actual"}`, sorted by name, with `layer` set to `"A"`. A check that did not run has `"passed": false` and its reason in `actual`.
- Exit code 0 when all checks pass, 1 when any check fails.
- Two runs on the same input produce a byte-identical `checks.json`.
- Commit the generated `checks.json` for the fixture.

## Expected Values
| Call or check | Expected |
| --- | --- |
| `load("<dataset>", <date>, ["<account>"])` | <n> rows |
| `load("unknown", ...)` | `KeyError` |
| All A1–A3 checks on the fixture | passed, exit code 0 |

## Failing-Input Tests
Each case must make the named check fail and the command exit 1. Build the bad inputs in temporary directories in the tests; do not commit them as fixtures.

| Case | Fails |
| --- | --- |
| <case> | <check> |

Plus one passing case: <datasets that may be empty> contain only the header, and all checks still pass.

## Constraints
- Base branch: `main`.
- Depends on: <#issue or "none">.
- Standard library only. Parse numbers with `decimal.Decimal`, never `float`.
- Put code under `src/quant_software_factory/reporting/`. Do not modify existing modules or tests unless this issue says so.
- Read data only through `load(...)`.
- No server names, IP addresses, database or table names, internal URLs, or credentials anywhere.

## Out of Scope
- Report blocks, `report.json`, `report.md`, narrative
- Report-level number checks
- Any production data source
- Recomputing any figure

## Open Items
- <every [needs data] item in this spec, or "None">

## Acceptance Criteria
- [ ] The pull request targets `main` and the branch is cut from `main`.
- [ ] `DataSource` protocol and `FixtureSource` exist, and all data access goes through `load(...)`.
- [ ] The fixtures are committed exactly as given.
- [ ] Every row in Expected Values is asserted by a test.
- [ ] Every case in Failing-Input Tests has a test, plus the empty-dataset case.
- [ ] The command writes `checks.json` and exits 0 on the fixture; the generated file is committed.
- [ ] Two runs produce a byte-identical `checks.json`.
- [ ] ruff check, ruff format --check, mypy (strict) and pytest pass in CI on Python 3.10–3.13.
- [ ] Submitted as a draft pull request.
- [ ] Independent review finds no unresolved blocking issues.

## Definition of Done
A reviewed, CI-passing draft pull request against `main` with the data access layer, schema registry, Layer A checks, fixtures, tests, a short README section, and the generated `checks.json`.

Do not merge automatically. Human approval is required.
````

ถ้า data layer มีอยู่แล้วและแค่เพิ่มชุดข้อมูล ให้ตัดส่วน interface ออก เขียนแค่ชุดข้อมูลใหม่, schema, fixture, ตัวเช็ค A ที่เพิ่ม และเพิ่ม Constraint "Do not change the behavior of `load(...)` or existing checks."

## 7. Open Items ของ Structure นี้

| # | เรื่อง | ถามใคร |
|---|---|---|
| P1 | รายชื่อคอลัมน์จริงของแต่ละชุดข้อมูล (สำหรับ mapping ภายใน) | เจ้าของ pipeline |
| P2 | ตัวอย่างข้อมูลจริงที่ลบข้อมูลระบุตัวตนแล้ว (เพื่อให้ fixture มีรูปแบบตรงของจริง) | เจ้าของ pipeline |
| P3 | repo หรือ pipeline ปลายทางที่จะรัน `InternalSource` | พี่ Anak |
| P4 | ตัวเช็คชั้น A ที่มีอยู่แล้วเช็คอะไร และความคลาดเคลื่อนที่ยอมรับ | เจ้าของ pipeline |
| P5 | เขียนชื่อตารางจริงใน public repo ได้หรือไม่ (ตอนนี้ถือว่าไม่ได้) | พี่ Anak |

## 8. ผลที่วัดได้และ gap ที่ยังเปิด

| | Issue #7 |
|---|---|
| Classify | ผ่าน ไม่ต้องขอข้อมูลเพิ่ม |
| เวลา label ถึง PR | 12 นาที 34 วินาที ไม่ชนเพดาน token |
| ตัวเช็คชั้น A | 14/14 ผ่าน |
| CI | ผ่าน Python 3.10–3.13 (60 tests) |
| จุดที่โรงงานตัดสินใจเอง | 5 จุด: ชื่อตัวเช็ค, ข้อความใน `expected`/`actual`, แถวที่วันที่อ่านไม่ได้, A3 ไม่ตรวจ `realized_pl` บนแถวที่ไม่ใช่ SELL, A3 ไม่ตรวจว่า `cash_flow.amount` เป็นบวก |

Gap ที่ยังเปิด:

| ประเภท | จุดที่พบ | แนวทาง |
|---|---|---|
| Specification | Spec บอกว่าเมื่อไม่มี `holdings_daily` ให้รายงาน A1 ว่า not run แต่ A1 อ่านแค่ `nav_daily` | แก้แล้วในช่องกรอกข้อ 6 (ให้ระบุตัวเช็คที่อ่านชุดนั้นจริง) |
| Specification | A3 ไม่ตรวจ `realized_pl` บนแถว BUY/DIVIDEND และไม่ตรวจว่า `cash_flow.amount` เป็นบวก | ถ้าต้องการ ให้เพิ่มเป็นกติกาใน A3 ของ Spec ใบถัดไป |
