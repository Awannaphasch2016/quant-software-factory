# Reporting Spec Structure for Software Factory: Requirements Specification

- โครงการ: Reusable Report Spec Structure สำหรับ Software Factory ของฝ่าย Quant
- ผู้จัดทำ: Inthanon Ratnavardhana
- มาตรฐานอ้างอิง: ISO/IEC/IEEE 29148:2018 (ปรับใช้แบบย่อ ไม่ใช่การรับรองความสอดคล้องทั้งหมด)

| Document Version | Last Updated | Status |
|---|---|---|
| v1.2 | 19 พ.ย. 2569 | Current |

Change Log (ประวัติทุก version ดูได้จาก history ของไฟล์นี้ใน git)

| Version | วันที่ | สิ่งที่เปลี่ยน |
|---|---|---|
| v1.2 | 19 พ.ย. 2569 | ปรับสถานะ PD-04 และ PD-05 หลังแก้ design gap ด้วย Issue #15 → PR #16 เพิ่มลิงก์อ้างอิง |
| v1.1 | 19 พ.ย. 2569 | เพิ่มข้อ 3.3 กลุ่ม PD (Private Data) และ AC-07 ตาม feedback 19 พ.ย. 2569 เปลี่ยนช่องทางแชตใน HR-05 และ AC-05 เป็น Discord เพิ่มคำศัพท์ Agent zone, Trusted zone และสมมติฐานเรื่อง Private Data |
| v1.0 | 19 พ.ย. 2569 | ย้ายเข้า `docs/` ใน repo จากฉบับที่ส่งเมื่อ 13 พ.ย. 2569 เนื้อหาเดิม เพิ่มหัว version แก้ลิงก์ และเรียกเอกสารฉบับที่ 4 ว่า Software Design |

## สารบัญ

1. Introduction
2. Scope
3. Functional Requirements
4. Nonfunctional Requirements
5. Acceptance Criteria
6. Constraints, Assumptions and References

## 1. Introduction

เอกสารนี้ขยายข้อกำหนดระดับสูงใน TOR [1] เป็นข้อกำหนดที่ตรวจได้ของ Report Spec Structure และการใช้งานกับ Software Factory ข้อกำหนดกลุ่ม HR ว่าด้วยการเชื่อมกับ harness และโรงงาน กลุ่ม FR ว่าด้วยตัวโครงสร้าง Spec และผลลัพธ์ที่โรงงานต้องสร้าง การออกแบบและหลักฐานอยู่ใน Software Design [2] ทุกข้อมีสถานะ Demonstrated หรือ Intended ตามหลักฐานที่มี

ตั้งแต่ v1.1 การทำงานกับ Private Data โดยข้อมูลไม่รั่วเป็น Core Requirement ของโครงการ (กลุ่ม PD ข้อ 3.3) ข้อกำหนดกลุ่มอื่นต้องไม่ขัดกับกลุ่มนี้

## 2. Scope

### 2.1 คำศัพท์

| คำศัพท์ | ความหมาย |
|---|---|
| Spec | ข้อกำหนดของงาน 1 งาน เขียนเป็น GitHub Issue body |
| Platform Spec | Spec ที่สร้างชั้นข้อมูล (`load(...)`, fixture, ตัวเช็คชั้น A) ทำครั้งเดียว หรือเมื่อเพิ่มชุดข้อมูลใหม่ |
| Report Spec | Spec ของรายงาน 1 ฉบับ ใช้ชั้นข้อมูลจาก Platform Spec |
| Spec Structure | แบบฟอร์มของ Spec ที่ใช้ซ้ำได้ มี 2 ไฟล์ คือ Report Spec Structure และ Platform Spec Structure (รุ่นก่อน v0.3 เรียกว่า Report Spec Template) |
| Block | ส่วนมาตรฐานของรายงาน เช่น `header`, `holdings`, `transactions` |
| Preset | ชุดของ block ที่กำหนดไว้สำหรับรายงานแต่ละประเภท |
| Dataset / ชื่อกลาง | ชุดข้อมูลที่ pipeline ของทีมคำนวณไว้แล้ว อ้างถึงด้วยชื่อกลาง (logical name) แทนชื่อระบบจริง |
| Data Mapping | ตารางที่บอกว่าช่องในรายงานมาจาก dataset และ field ใด |
| Fixture | ข้อมูลปลอมที่ใช้ในโรงงานแทนข้อมูลจริง |
| Expected Values | คำตอบที่ถูกของ fixture ที่ใช้ตรวจผล |
| Number Checks | ตัวเช็คตัวเลข ชั้น A (ข้อมูล) และชั้น B (รายงาน) |
| Foreman / eve-forman[bot] | Software Factory ของพี่ Anak และบัญชี bot ที่รายงานผลใน Issue |
| Demonstrated / Intended | มีหลักฐานแล้ว / เป็นข้อกำหนดหรือทิศทางที่ยังไม่มีหลักฐาน |
| Private Data | ข้อมูลลูกค้าและข้อมูลลับของบริษัท รวมตัวเลขในรายงาน เลขบัญชี และชื่อลูกค้า |
| Agent zone | ส่วนที่ agent และบริการภายนอก (รวมผู้ให้บริการโมเดล) ทำงาน ต้องไม่ได้รับ Private Data |
| Trusted zone | environment ที่บริษัทควบคุมและเก็บ Private Data โค้ดที่ agent เขียนรันกับข้อมูลจริงได้ที่นี่เท่านั้น |
| Result | ไฟล์เดียวที่ส่งจาก Trusted zone กลับไป Agent zone มีแค่ชื่อตัวเช็คและผ่าน/ไม่ผ่าน |

### 2.2 ประเภทรายงานที่ต้องรองรับ

| Preset | รายงาน | สถานะ |
|---|---|---|
| `returns_transactions` | ผลตอบแทนและรายการทางการลงทุน | ใช้ใน Run #1, #2 และ #4 |
| `client_pnl` | กำไรขาดทุนให้ลูกค้า | มี preset ยังไม่ได้รัน |
| `monthly_team` | รายงานประจำเดือนของฝ่าย Quant | โครงเปิด ยังไม่รู้ว่าต้นแบบคือรายงานใด |

### 2.3 Use case

ผู้ใช้กรอก Spec ตาม Template แล้วเปิด GitHub Issue และติด label `factory` (หรือส่งผ่านแชตในอนาคต) โรงงานจัดประเภท วางแผน เขียนโค้ด ตรวจทาน และเปิด draft PR ที่มีโค้ด fixture test และรายงานตัวอย่าง ผู้ใช้ตรวจ PR แล้วตัดสินใจ merge หลัง merge แล้วโค้ดนั้นใช้สร้างรายงานจากข้อมูลจริงได้ทุกรอบ โดยต่อกับระบบข้อมูลของทีมผ่าน interface เดียวกัน

## 3. Functional Requirements

### 3.1 ระดับ Harness และ Factory

| ID | ข้อกำหนด | สถานะ |
|---|---|---|
| HR-01 | Spec ต้องส่งเข้าโรงงานได้ด้วย GitHub Issue ที่ติด label `factory` | Demonstrated (Issue #4, #6, #7, #9) |
| HR-02 | ผู้ติด label ต้องเป็นบัญชีคนที่มีสิทธิ์ triage ขึ้นไป บัญชีชนิด Bot จะถูกโรงงานข้าม | Demonstrated เฉพาะกรณีบัญชีคน (Josh-Bear, Issue #4, #6, #7, #9) ส่วนกรณีบัญชี Bot มาจากโค้ดใน template ยังไม่ได้ทดสอบ |
| HR-03 | Output ของโรงงานต้องเป็น draft PR การ merge เป็นของคน | Demonstrated (PR #5, #8, #10 เป็น draft และคนเป็นผู้ merge PR #2, #8, #10) |
| HR-04 | Spec ต้องระบุ base branch และ Issue ที่ต้องทำก่อน (`Depends on`) ได้ | Demonstrated (Issue #6, #7, #9 แตก branch จาก `main` ตาม Spec และ Issue #9 ใช้ data layer จาก #7 ที่ merge แล้ว) |
| HR-05 | ต้องสั่งงานและรับรายงานกลับผ่านช่องทางแชต (Discord ตามที่ทีม Quant ใช้) โดยไม่ต้องเข้า repository และช่องทางแชตต้องไม่ส่ง Private Data ออกนอก Trusted zone | Intended |

### 3.2 ระดับ Spec Structure

| ID | ข้อกำหนด | สถานะ |
|---|---|---|
| FR-01 | Template ต้องมีหัวข้อตายตัวที่ทุก Spec ใช้: Background, Report Definition, Data Sources, Data Mapping, Report Blocks, Output Contract, Expected Values, Number Checks, Writing Rules, Constraints, Out of Scope, Open Items, Acceptance Criteria, Definition of Done | Demonstrated v0.1 (Run #1) และ v0.3 (Run #4) ส่วน v0.2 ผ่านแค่ Classify (Run #2) Report Spec ของ Run #4 ไม่มีหัวข้อ Open Items เพราะไม่มีสิ่งที่ขาด (ดู FR-09) |
| FR-02 | Template ต้องรองรับรายงาน 3 ประเภทด้วย preset ของ block มาตรฐาน | Demonstrated 1 ประเภท, Intended 2 ประเภท |
| FR-03 | ตัวเลขทุกช่องในรายงานต้องมี Data Mapping ไปยัง dataset.field และโค้ดต้องไม่คำนวณ field ที่ dataset ให้มา | Demonstrated (Run #4: ตามที่ reviewer ตรวจใน PR #10 โค้ดมีการคำนวณแค่ยอดรวมในแถว Total เพื่อแสดงผล ซึ่ง B1 และ B2 ตรวจ และกลับเครื่องหมายเงินถอน) |
| FR-04 | โค้ดต้องอ่านข้อมูลผ่าน interface เดียว `load(dataset, as_of, accounts)` ที่เปลี่ยนจาก fixture เป็นข้อมูลจริงได้ | Demonstrated กับ fixture (Run #3 สร้าง `DataSource` และ `FixtureSource`, Run #4 มี test ยืนยันว่าอ่านผ่าน `load(...)` เท่านั้น) การต่อกับข้อมูลจริงเป็น Intended |
| FR-05 | ทุก Spec ต้องมี Expected Values ที่คำนวณจาก fixture และ test ต้องตรวจทุกแถว | Demonstrated (Run #1: 36 กรณี, Run #3: 11 แถว, Run #4: 21 แถว) |
| FR-06 | Output ต้องเป็น `report.md` (หรือ pdf ถ้าอนุมัติ dependency), `report.json`, `narrative.md`, `checks.json` ตามกติการูปแบบตัวเลขและค่าว่างใน Template | Demonstrated (Run #1 และ #4, รูปแบบ md) |
| FR-07 | Number Checks ชั้น A ต้องตรวจความสด ความครบ และ schema ของข้อมูล ชั้น B ต้องตรวจความสอดคล้องของตัวเลขในรายงาน ถ้าไม่ผ่านต้องไม่สร้างไฟล์รายงาน | Demonstrated (Run #4: ชั้น A 14 และชั้น B 15 ผ่าน, ทุกตัวเช็คมี test ที่ทำให้ไม่ผ่าน, ชั้น A ไม่ผ่านแล้วไม่สร้างไฟล์รายงาน) |
| FR-08 | Writing Rules ต้องตรวจได้ และตัวเลขในข้อความต้องอยู่ใน `report.json` | Demonstrated (Run #4: ตัวเช็ค B8 และ W1–W5 อยู่ใน `checks.json`) แต่ตัวเช็คอัตโนมัติยังจับปัญหาข้อความที่เล่าตามตารางไม่ได้ |
| FR-09 | Spec ต้องมีหัวข้อ Open Items ที่รวมสิ่งที่ยังไม่มีข้อมูล | Demonstrated (Example v0.2) Report Spec ของ Run #4 ไม่มีหัวข้อนี้เพราะไม่มีสิ่งที่ขาด Spec Structure v0.3 จึงบังคับให้เขียน "None" แล้ว ([`appendix/report-spec-structure.md`](appendix/report-spec-structure.md) ข้อ 3) แต่ยังไม่ได้ทดสอบกับโรงงาน |
| FR-10 | Spec 1 ใบต้องมีขนาดที่โรงงานทำจบได้ใน 1 session ตามกติกาการแตก Spec | ผ่านบางส่วน: Platform Spec จบใน 1 session (Run #3) ส่วน Report Spec ชนเพดานหลังขั้น implement และต้องอนุมัติ 1 ครั้ง (Run #4) Run #1 และ #2 ไม่ผ่าน |

### 3.3 ระดับ Private Data (Core Requirement ตั้งแต่ v1.1)

| ID | ข้อกำหนด | สถานะ |
|---|---|---|
| PD-01 | Agent และบริการภายนอก (รวมผู้ให้บริการโมเดล) ต้องไม่ได้รับ Private Data | Demonstrated ใน prototype (Issue #12 → PR #13: โรงงานเขียนโค้ดจาก Spec, schema และข้อมูลปลอมเท่านั้น) |
| PD-02 | โค้ดที่ agent เขียนต้องรันกับข้อมูลจริงใน Trusted zone เท่านั้น ด้วยสิทธิ์อ่านอย่างเดียว | Demonstrated ใน prototype (`SqliteSource` เปิดแบบอ่านอย่างเดียว, SHA-256 ของ database เท่าเดิมหลังรัน) Trusted zone จริงในเครือข่ายบริษัทเป็น Intended |
| PD-03 | สิ่งที่ส่งกลับจาก Trusted zone มีได้แค่ชื่อตัวเช็ค ผ่าน/ไม่ผ่าน และจำนวนรวม ไม่มีตัวเลข ชื่อ หรือเลขบัญชี | Demonstrated ใน prototype (`result.json` มี 4 key และไม่มีค่าจาก private database) |
| PD-04 | ต้องมี leak check ที่หยุดการส่งกลับถ้าพบค่าจาก Private Data | Demonstrated ใน prototype (exit 3 เมื่อพบตัวเลข เลขบัญชี หรือชื่อลูกค้า มี test; PR #16 เปลี่ยนเป็นจับเลขบัญชีและชื่อแบบทั้งคำ เลขบัญชีสั้นจึงไม่หยุดโดยไม่จำเป็น) ข้อจำกัดที่เหลือดู Software Design ข้อ 2.7 |
| PD-05 | รายงานที่มี Private Data ต้องเก็บใน Trusted zone เท่านั้น ห้าม commit เข้า repository | Demonstrated บางส่วน (ปฏิเสธ output ใน repo exit 2 ไม่ว่าจะติดตั้งแบบใด ตั้งแต่ PR #16) การกำหนดสิทธิ์ผู้อ่านเป็น Intended |
| PD-06 | repository เก็บได้แค่โค้ด schema และข้อมูลปลอม และต้องมีกลไกกัน commit ข้อมูลจริง | Demonstrated บางส่วน (`.gitignore` สำหรับ `*.db` และ `*.sqlite`) secret scanning และ push protection เป็น Intended |

การออกแบบที่ตอบกลุ่มนี้อยู่ใน Software Design ข้อ 2

## 4. Nonfunctional Requirements

| ID | ข้อกำหนด | สถานะ |
|---|---|---|
| NFR-01 | รันซ้ำกับข้อมูลเดิมต้องได้ `report.json` เหมือนเดิมทุกไบต์ | Demonstrated (Run #1 และ #4 ผู้จัดทำรันซ้ำเองใน Run #4 แล้วได้ไฟล์ตรงกับที่ commit) |
| NFR-02 | คำนวณและจัดรูปแบบด้วย Decimal ปัดแบบ half-up ความคลาดเคลื่อนไม่เกิน 0.01 ต่อค่า | Demonstrated (Run #1 และ #4) |
| NFR-03 | ไม่มีข้อมูลลูกค้าจริง ชื่อ server ชื่อ database ชื่อตาราง URL ภายใน หรือ credential ใน Issue โค้ด หรือเอกสารบน repository สาธารณะ | Demonstrated (ตรวจ Issue #4, #6, #7, #9 และเอกสารแล้ว) |
| NFR-04 | CI ผ่านบน Python 3.10 ถึง 3.13 (ruff, ruff format, mypy strict, pytest) | Demonstrated (Run #1 CI run 43151748082, Run #3 CI run 43383851475, Run #4 CI run 43395249810) |
| NFR-05 | ทุกข้ออ้างตรวจย้อนกลับได้ด้วยลิงก์ GitHub หรือ commit SHA | Demonstrated |
| NFR-06 | ไม่เพิ่ม runtime dependency ถ้า Spec ไม่อนุญาต | Demonstrated (Run #1, #3, #4: `pyproject.toml` ไม่เปลี่ยนใน #3 และ #4) |
| NFR-07 | ต้นทุนต่อรอบวัดได้และใช้เป็นจุดอ้างอิง | Intended (ยังไม่มีตัวเลขจริงจาก Vercel) |
| NFR-08 | ข้อความบรรยายไม่มีการคาดการณ์หรือคำแนะนำการลงทุน | Demonstrated (Run #1 และ #4 ตัวเช็ค W5) |

## 5. Acceptance Criteria

AC ระดับระบบ AC-01 ถึง AC-06 ตรงกับ Acceptance Criteria ของ requirement_1 และ AC-07 มาจาก feedback วันที่ 19 พ.ย. 2569

| ID | เกณฑ์ | อ้าง | สถานะ |
|---|---|---|---|
| AC-01 | มี Reusable Spec Template ที่รองรับรายงาน 3 ประเภท | FR-01, FR-02 | Demonstrated กับ 1 ประเภท |
| AC-02 | มี Spec ตัวอย่างที่กรอกแล้วอย่างน้อย 1 ใบ | FR-01, FR-05, FR-09 | Demonstrated (4 ใบ: v0.1, v0.2, Platform Spec v0.3, Report Spec v0.3) |
| AC-03 | มีการรันผ่านโรงงานสำเร็จอย่างน้อย 1 ครั้ง: Issue เชื่อมกับ draft PR, Output ตรง Expected Values ทุกค่า, CI ผ่าน, reviewer ไม่เหลือ blocking issue | HR-01, HR-03, FR-05, FR-06, FR-07, NFR-04 | Demonstrated 2 ครั้ง (Issue #4 → PR #5 และ Issue #9 → PR #10 ที่ merge แล้ว) |
| AC-04 | มี Progress Report | | Demonstrated |
| AC-05 | สั่งงานผ่าน Discord ได้ | HR-05 | Intended |
| AC-06 | มีข้อเสนอ Natural Writing ครอบคลุม Spec, Writing Guidelines และการตรวจ Output | FR-08 | Demonstrated (เอกสารข้อเสนอ, กติกาที่ตรวจได้และตัวเช็ค W1–W5 ใน Run #4, ผลตรวจข้อความ Run #1 และ #4 ด้วย skill พร้อมฉบับแก้) ส่วน narrative facts และ LLM judge เป็น Intended |
| AC-07 | Agent ทำงานกับ Private Data ได้โดยข้อมูลไม่รั่วออกนอก Trusted zone มีหลักฐานที่ผู้ตรวจรันซ้ำได้ | PD-01 ถึง PD-06 | Demonstrated ระดับ prototype ด้วย private database จำลอง (Issue #12 → PR #13) ยังไม่ได้ทดสอบกับ database และเครือข่ายจริงของบริษัท |

การผ่าน AC-03 หมายถึงโครงสร้าง Spec ทำงานกับโรงงานได้กับรายงาน 1 ประเภทและข้อมูลปลอม ไม่ได้ยืนยันว่าตัวเลขตรงกับนิยามของทีม หรือพร้อมใช้กับข้อมูลจริง

## 6. Constraints, Assumptions and References

### 6.1 ข้อจำกัด

- พึ่ง GitHub, Software Factory ของพี่ Anak บน Vercel และ budget ของโรงงาน
- Repository เป็นสาธารณะ (NFR-03)
- เพดาน output token ของโรงงานต่อ session (100K ใน Run #1 และ #4, 44.9K ใน Run #2) ไม่ได้อยู่ในการควบคุมของผู้จัดทำ

### 6.2 สมมติฐาน

- ตัวเลขในรายงานลูกค้าคำนวณไว้แล้วในชุดข้อมูลของ pipeline (ข้อมูลจากทีม 12 พ.ย. 2569)
- Dataset Catalog ([`appendix/platform-spec-structure.md`](appendix/platform-spec-structure.md) ข้อ 3) ครอบคลุมชุดข้อมูลที่รายงาน 2 ประเภทแรกใช้ ชื่อคอลัมน์จริงยังไม่ได้ map
- นิยามตัวเลขใน fixture (average cost, ปันผลแบบ net) เป็นค่าสมมติ ยังไม่ได้ยืนยันกับทีม
- Foreman ยังชี้ไปที่ repository `quant-software-factory`
- Private Data อยู่ใน database บน server ภายในเครือข่ายบริษัท และตัวโมเดลรันที่ผู้ให้บริการภายนอก ข้อมูลใดที่อยู่ใน prompt จึงถือว่าออกนอกบริษัท (ข้อมูลจากทีม และ feedback 19 พ.ย. 2569)
- ยังไม่ได้ยืนยัน policy ของบริษัทเรื่องการส่งข้อมูลให้ผู้ให้บริการโมเดล จึงออกแบบให้ไม่ต้องส่ง

### 6.3 References

| รายการ | ลิงก์ |
|---|---|
| TOR | [`1-tor.md`](1-tor.md) |
| Software Design | [`4-software-design.md`](4-software-design.md) |
| Repository | https://github.com/Awannaphasch2016/quant-software-factory |
| Issue #4 (Run #1) | https://github.com/Awannaphasch2016/quant-software-factory/issues/4 |
| PR #5 (Run #1) | https://github.com/Awannaphasch2016/quant-software-factory/pull/5 |
| CI ของ PR #5 | https://github.com/Awannaphasch2016/quant-software-factory/actions/runs/43151748082 |
| Issue #6 (Run #2) | https://github.com/Awannaphasch2016/quant-software-factory/issues/6 |
| Issue #7 → PR #8 (Run #3) | https://github.com/Awannaphasch2016/quant-software-factory/issues/7, https://github.com/Awannaphasch2016/quant-software-factory/pull/8 |
| Issue #9 → PR #10 (Run #4) | https://github.com/Awannaphasch2016/quant-software-factory/issues/9, https://github.com/Awannaphasch2016/quant-software-factory/pull/10 |
| Issue #12 → PR #13 (prototype Private Data) | https://github.com/Awannaphasch2016/quant-software-factory/issues/12, https://github.com/Awannaphasch2016/quant-software-factory/pull/13 |
| Issue #15 → PR #16 (แก้ design gap ของ prototype) | https://github.com/Awannaphasch2016/quant-software-factory/issues/15, https://github.com/Awannaphasch2016/quant-software-factory/pull/16 |
| CI ของ PR #10 | https://github.com/Awannaphasch2016/quant-software-factory/actions/runs/43395249810 |
| Spec Structure v0.3 | [`appendix/report-spec-structure.md`](appendix/report-spec-structure.md), [`appendix/platform-spec-structure.md`](appendix/platform-spec-structure.md) |
| หลักฐาน End-to-End Run | [`appendix/e2e-run-evidence.md`](appendix/e2e-run-evidence.md), [`../reports/demo_coop_rg_2026_10_v2/`](../reports/demo_coop_rg_2026_10_v2/) |
| Template v0.1 / v0.2 / v0.3 (ประวัติ) | [`appendix/history/report-spec-template.md`](appendix/history/report-spec-template.md), [`appendix/history/report-spec-template-v0.2.md`](appendix/history/report-spec-template-v0.2.md), [`appendix/history/report-spec-template-v0.3.md`](appendix/history/report-spec-template-v0.3.md) |
