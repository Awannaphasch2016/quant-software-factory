# Reporting Spec Structure for Software Factory: Delivery Document

- โครงการ: Reusable Report Spec Structure สำหรับ Software Factory ของฝ่าย Quant
- ผู้จัดทำ: Inthanon Ratnavardhana
- แนวทางอ้างอิง: ISO/IEC 29110 ส่วนการส่งมอบ Software Product และ Delivery Instructions (ปรับใช้แบบย่อ ไม่ใช่การรับรองความสอดคล้อง)

| Document Version | Last Updated | Status |
|---|---|---|
| v1.3 | 19 พ.ย. 2569 | Current |

Change Log (ประวัติทุก version ดูได้จาก history ของไฟล์นี้ใน git)

| Version | วันที่ | สิ่งที่เปลี่ยน |
|---|---|---|
| v1.3 | 19 พ.ย. 2569 | เปลี่ยนคำว่า "ค่าจริง" ในส่วน B เป็นค่าจาก private database เพราะเป็นข้อมูลปลอมที่คูณและเปลี่ยนชื่อ |
| v1.2 | 19 พ.ย. 2569 | ปรับ version ที่ส่งมอบเป็น `3a422c5` (PR #16 แก้ตัวกันเขียนลง repo และ leak check) เอาเงื่อนไขติดตั้งแบบ editable ออก และปรับข้อจำกัด |
| v1.1 | 19 พ.ย. 2569 | เพิ่ม prototype Private Data boundary (PR #13): ส่วนประกอบใหม่ 3 ตัว, วิธีใช้ และ Acceptance Test Walkthrough ส่วน B ปรับ version ที่ส่งมอบและข้อจำกัด |
| v1.0 | 19 พ.ย. 2569 | ฉบับแรก บันทึกสิ่งที่ส่งมอบได้จริง ณ วันที่นี้ ก่อนเริ่ม Iteration 1 ของสัปดาห์ 16–20 พ.ย. 2569 |

เอกสารนี้บอกว่าส่งมอบอะไร ทำงานอยู่ที่ไหน ต้องมีอะไรก่อนใช้ และทดสอบเองอย่างไร ทุกข้อแสดงสถานะที่เกิดขึ้นจริง ส่วนที่ยังไม่ได้ทำเขียนว่า "ยังไม่ส่งมอบ"

## 1. Delivered Software and Components

| ส่วน | สถานะ | อยู่ที่ |
|---|---|---|
| Data layer: `load(...)`, `FixtureSource`, schema registry, ตัวเช็คชั้น A | ส่งมอบแล้ว | `src/quant_software_factory/reporting/` (PR #8) |
| ตัวสร้างรายงาน Returns & Transactions, ตัวเช็คชั้น B และตัวเช็คการเขียน | ส่งมอบแล้ว | `src/quant_software_factory/reporting/` (PR #10) |
| รายงานตัวอย่างจากข้อมูลปลอม | ส่งมอบแล้ว | [`reports/demo_coop_rg_2026_10_v2/`](../reports/demo_coop_rg_2026_10_v2/) |
| **`SqliteSource`**: อ่าน private database ผ่าน `load(...)` เดิม แบบอ่านอย่างเดียว | ส่งมอบแล้ว (prototype) | `reporting/sqlite_source.py` (PR #13) |
| **`make_private_db`**: สร้าง private database จาก CSV คูณตัวเลขเงินและเปลี่ยนเลขบัญชีกับชื่อลูกค้าได้ | ส่งมอบแล้ว (prototype) | `reporting/make_private_db.py` (PR #13) |
| **`private_run`**: executor ใน trusted zone เขียนรายงานเต็มนอก repo และส่งกลับแค่ result ที่ผ่าน leak check | ส่งมอบแล้ว (prototype) | `reporting/private_run.py` (PR #13, แก้ใน PR #16) |
| Report Spec และ Spec ของ prototype | ส่งมอบแล้ว | [Issue #9](https://github.com/Awannaphasch2016/quant-software-factory/issues/9), [Issue #12](https://github.com/Awannaphasch2016/quant-software-factory/issues/12) |
| Spec Structure (Report และ Platform) | ส่งมอบแล้ว | [`appendix/report-spec-structure.md`](appendix/report-spec-structure.md), [`appendix/platform-spec-structure.md`](appendix/platform-spec-structure.md) |
| Trusted zone จริงในเครือข่ายบริษัทและ database จริง | ยังไม่ส่งมอบ | รอการอนุมัติเรื่องสิทธิ์และ policy |
| Report Agent (Eve agent ตัวเดียว) | ยังไม่ส่งมอบ | รอสิทธิ์ deploy บน Vercel |
| รายงานรูปแบบ PDF | ยังไม่ส่งมอบ | |
| ตัวเลขต้นทุนต่อรายงาน 1 ฉบับ | ยังไม่ส่งมอบ | รอตัวเลข usage จาก Vercel |
| Discord bot | ยังไม่ส่งมอบ | |

Software version ที่ส่งมอบ: commit `3a422c5` บน `main` (merge PR #16 เมื่อ 19 พ.ย. 2569)

## 2. Deployment and Server Information

| เรื่อง | ค่า |
|---|---|
| ที่เก็บโค้ด | GitHub repository สาธารณะ https://github.com/Awannaphasch2016/quant-software-factory |
| การ deploy | ยังไม่มี service ที่ deploy ทุกส่วนรันเป็นคำสั่ง Python บนเครื่องผู้ทดสอบ และรันใน GitHub Actions ทุก PR |
| ผู้เขียนโค้ด (โซน Agent) | Software Factory (Foreman) ของพี่ Anak บน Vercel ผ่าน GitHub App `eve-forman` เห็นแค่ Spec, schema และข้อมูลปลอม |
| Trusted zone ใน prototype | โฟลเดอร์บนเครื่องผู้ทดสอบที่อยู่นอก repository แทนเครื่องในเครือข่ายบริษัท |
| แหล่งข้อมูล | ข้อมูลปลอมใน [`data/fixtures/demo_coop_rg_2026_10_v2/`](../data/fixtures/demo_coop_rg_2026_10_v2/) และ private database (SQLite) ที่ผู้ทดสอบสร้างเอง ไม่มีการเชื่อม database ของบริษัท |
| Environment | Development ยังไม่มี Production |

## 3. Access and Prerequisites

- เปิด repository ได้โดยไม่ต้องมีบัญชี เพราะเป็น public
- เครื่องที่ใช้ทดสอบต้องมี Python 3.10 ขึ้นไป และ `git`
- ติดตั้งด้วย `pip install -e .` ตาม walkthrough ตั้งแต่ PR #16 ติดตั้งแบบปกติ (`pip install .`) ก็ได้ ตัวกันเขียน output ลงใน repo ทำงานทั้งสองแบบ
- ไม่ต้องใช้ password, API key หรือสิทธิ์พิเศษ

## 4. User Instructions

### 4.1 สร้างรายงานจากข้อมูลปลอม

รันที่โฟลเดอร์รากของ repository:

```bash
python -m quant_software_factory.reporting.returns_transactions data/fixtures/demo_coop_rg_2026_10_v2 reports/demo_coop_rg_2026_10_v2 --account DEMO-0001 --opening 2026-09-30 --as-of 2026-10-30
```

ผ่านทั้งหมด: เขียน 4 ไฟล์และจบด้วย exit code 0 มีตัวเช็คไม่ผ่าน: เขียนแค่ `checks.json` และจบด้วย exit code 1

### 4.2 รันรายงานใน trusted zone (prototype Private Data)

1. สร้าง private database จาก CSV (ทำใน trusted zone):

```bash
python -m quant_software_factory.reporting.make_private_db <csv_dir> <db_path> --scale <K> --account <ID> --client-name "<NAME>"
```

2. รัน executor:

```bash
python -m quant_software_factory.reporting.private_run --db <db_path> --private-out <โฟลเดอร์ปิด> --result <result.json> --account <ID> --opening <YYYY-MM-DD> --as-of <YYYY-MM-DD>
```

- รายงานเต็มอยู่ใน `--private-out` เท่านั้น
- `--result` เป็นไฟล์เดียวที่ส่งกลับไปโซน Agent ได้ มีแค่ `status`, `checks_total`, `checks_failed` และรายชื่อตัวเช็คพร้อมผ่าน/ไม่ผ่าน
- exit code: 0 ผ่าน, 1 มีตัวเช็คไม่ผ่าน, 2 โฟลเดอร์ output อยู่ใน repo, 3 leak check พบค่าจาก private data

## 5. Acceptance Test Walkthrough

### ส่วน A: รายงานจากข้อมูลปลอม

| ขั้น | ทำอะไร | ผลที่ควรได้ |
|---|---|---|
| A1 | `git clone https://github.com/Awannaphasch2016/quant-software-factory.git` แล้ว `cd quant-software-factory` | ได้โฟลเดอร์ repository |
| A2 | `python -m venv .venv` แล้ว activate จากนั้น `pip install -e .` | ติดตั้งสำเร็จ ไม่มี dependency ภายนอก |
| A3 | รันคำสั่งในข้อ 4.1 | แสดง `29 checks, 0 failed` และ exit code 0 |
| A4 | เปิด `reports/demo_coop_rg_2026_10_v2/report.md` | มี 6 ส่วนตามลำดับ: Returns & Transactions Report, KPI summary, Holdings, Transactions, Narrative, Disclaimer |
| A5 | ตรวจ KPI summary | Net asset value 792,398.00, Total P/L 27,398.00, Period return 3.83% |
| A6 | `git status --short reports/` | ไม่มีผลลัพธ์ แปลว่ารายงานที่สร้างใหม่ตรงกับที่ commit ไว้ทุก byte |

### ส่วน B: Private Data boundary

ใช้ค่าที่ไม่มีอยู่ใน repository เพื่อดูว่าค่าเหล่านี้ไม่ข้ามเส้น ตัวอย่างนี้คูณตัวเลขเงิน 7 เท่า ใช้เลขบัญชี `ZX-9931` และชื่อลูกค้า `SECRET HOLDINGS CO` (เปลี่ยนเป็นค่าอื่นได้)

| ขั้น | ทำอะไร | ผลที่ควรได้ |
|---|---|---|
| B1 | `mkdir -p ~/qsf-trusted ~/qsf-agent` | ได้โฟลเดอร์ trusted zone และโฟลเดอร์ที่แทนโซน Agent ทั้งสองอยู่นอก repo |
| B2 | `python -m quant_software_factory.reporting.make_private_db data/fixtures/demo_coop_rg_2026_10_v2 ~/qsf-trusted/private.db --scale 7 --account ZX-9931 --client-name "SECRET HOLDINGS CO"` | แสดง `wrote 6 tables to ...` |
| B3 | `python -m quant_software_factory.reporting.private_run --db ~/qsf-trusted/private.db --private-out ~/qsf-trusted/out --result ~/qsf-agent/result.json --account ZX-9931 --opening 2026-09-30 --as-of 2026-10-30` | แสดง `29 checks, 0 failed` และ exit code 0 |
| B4 | เปิด `~/qsf-trusted/out/report.md` | รายงานเต็มที่มีค่าจาก private database: Client SECRET HOLDINGS CO, Account ZX-9931, Net asset value 5,546,786.00, Total P/L 191,786.00, Period return 3.83% |
| B5 | เปิด `~/qsf-agent/result.json` | มีแค่ `status: "passed"`, `checks_total: 29`, `checks_failed: 0` และรายการตัวเช็คที่มี `name`, `layer`, `passed` ไม่มีตัวเลขเงิน เลขบัญชี หรือชื่อลูกค้า |
| B6 | `grep -c -e "ZX-9931" -e "SECRET" -e "5,546,786" ~/qsf-agent/result.json` | `0` |
| B7 | `python -m quant_software_factory.reporting.private_run --db ~/qsf-trusted/private.db --private-out ./leak-out --result ~/qsf-agent/r2.json --account ZX-9931 --opening 2026-09-30 --as-of 2026-10-30` | แสดง `error: --private-out must be outside the repository working tree` exit code 2 และไม่มีโฟลเดอร์ `leak-out` |
| B8 | `git status --short` | ไม่มีผลลัพธ์ ไม่มี database หรือรายงานจริงเข้า repository |

สิ่งที่ส่วน B แสดง: โค้ดที่โรงงานเขียนโดยไม่เคยเห็นค่าเหล่านี้ อ่าน private database และสร้างรายงานที่ถูกต้องได้ ค่าจาก private database (ซึ่งเป็นข้อมูลปลอมที่คูณ 7 เท่าและเปลี่ยนชื่อ ไม่ใช่ข้อมูลลูกค้า) อยู่แค่ใน `~/qsf-trusted/` ส่วนสิ่งที่ข้ามไป `~/qsf-agent/` มีแค่ผลตรวจ

## 6. Delivered Version and Known Limitations

- Version ที่ส่งมอบ: commit `3a422c5` ณ 19 พ.ย. 2569
- ข้อจำกัด:
  - trusted zone ใน prototype คือเครื่องผู้ทดสอบ และ private database เป็น SQLite จากข้อมูลปลอม ยังไม่ได้ทดสอบกับ database, เครือข่าย และสิทธิ์จริงของบริษัท
  - leak check ไม่ค้นในชื่อ key ของ JSON และในค่าจำนวนเต็ม และยังหยุดด้วย exit 3 ถ้าเลขบัญชีหรือชื่อลูกค้าตรงกับชื่อตัวเช็คหรือ layer ทั้งคำ เช่น `A` (Software Design ข้อ 2.7)
  - โซน Agent ยังเป็น Foreman ไม่ใช่ Eve agent ตัวเดียว
  - ยังไม่มี Discord, PDF และตัวเลขต้นทุนต่อรายงาน
  - ข้อความบรรยายยังไม่มีตัวเลข "NAV เปลี่ยนไปเท่าไร" และยังเล่าซ้ำกับตาราง (ดู [`appendix/natural-writing-proposal.md`](appendix/natural-writing-proposal.md))
