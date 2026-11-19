# Reporting Spec Structure for Software Factory: Delivery Document

- โครงการ: Reusable Report Spec Structure สำหรับ Software Factory ของฝ่าย Quant
- ผู้จัดทำ: Inthanon Ratnavardhana
- แนวทางอ้างอิง: ISO/IEC 29110 ส่วนการส่งมอบ Software Product และ Delivery Instructions (ปรับใช้แบบย่อ ไม่ใช่การรับรองความสอดคล้อง)

| Document Version | Last Updated | Status |
|---|---|---|
| v1.0 | 19 พ.ย. 2569 | Current |

Change Log (ประวัติทุก version ดูได้จาก history ของไฟล์นี้ใน git)

| Version | วันที่ | สิ่งที่เปลี่ยน |
|---|---|---|
| v1.0 | 19 พ.ย. 2569 | ฉบับแรก บันทึกสิ่งที่ส่งมอบได้จริง ณ วันที่นี้ ก่อนเริ่ม Iteration 1 ของสัปดาห์ 16–20 พ.ย. 2569 |

เอกสารนี้บอกว่าส่งมอบอะไร ทำงานอยู่ที่ไหน ต้องมีอะไรก่อนใช้ และทดสอบเองอย่างไร ทุกข้อแสดงสถานะที่เกิดขึ้นจริง ส่วนที่ยังไม่ได้ทำเขียนว่า "ยังไม่ส่งมอบ"

## 1. Delivered Software and Components

| ส่วน | สถานะ | อยู่ที่ |
|---|---|---|
| Data layer: `load(...)`, `FixtureSource`, schema registry, ตัวเช็คชั้น A | ส่งมอบแล้ว | `src/quant_software_factory/reporting/` (PR #8) |
| ตัวสร้างรายงาน Returns & Transactions, ตัวเช็คชั้น B และตัวเช็คการเขียน | ส่งมอบแล้ว | `src/quant_software_factory/reporting/` (PR #10) |
| รายงานตัวอย่างจากข้อมูลปลอม (`report.md`, `report.json`, `narrative.md`, `checks.json`) | ส่งมอบแล้ว | [`reports/demo_coop_rg_2026_10_v2/`](../reports/demo_coop_rg_2026_10_v2/) |
| Report Spec ที่ใช้สร้างรายงาน | ส่งมอบแล้ว | [Issue #9](https://github.com/Awannaphasch2016/quant-software-factory/issues/9), ร่างใน [`appendix/report-spec.md`](appendix/report-spec.md) |
| Spec Structure (Report และ Platform) | ส่งมอบแล้ว | [`appendix/report-spec-structure.md`](appendix/report-spec-structure.md), [`appendix/platform-spec-structure.md`](appendix/platform-spec-structure.md) |
| Report Agent (Eve agent ตัวเดียว) ที่รับ Spec แล้วเปิด PR ที่มีรายงาน | ยังไม่ส่งมอบ | งานของ Iteration 1 |
| รายงานรูปแบบ PDF | ยังไม่ส่งมอบ | งานของ Iteration 1 |
| ตัวเลขต้นทุนต่อรายงาน 1 ฉบับ | ยังไม่ส่งมอบ | งานของ Iteration 1 รอสิทธิ์ดู usage บน Vercel |
| Discord bot | ยังไม่ส่งมอบ | งานของ Iteration 2 |
| การเชื่อมข้อมูลจริง | ยังไม่ส่งมอบ | Iteration 3 รอการอนุมัติเรื่องสิทธิ์และ policy |

Software version ที่ส่งมอบ: commit `4e2129e` บน `main` (merge PR #10 เมื่อ 13 พ.ย. 2569)

## 2. Deployment and Server Information

| เรื่อง | ค่า |
|---|---|
| ที่เก็บโค้ด | GitHub repository สาธารณะ https://github.com/Awannaphasch2016/quant-software-factory |
| การ deploy | ยังไม่มี service ที่ deploy ของเราเอง ตัวสร้างรายงานรันเป็นคำสั่ง Python บนเครื่องผู้ทดสอบ และรันใน GitHub Actions ทุก PR |
| ผู้สร้างโค้ดใน version นี้ | Software Factory (Foreman) ของพี่ Anak บน Vercel ผ่าน GitHub App `eve-forman` ไม่ได้อยู่ในการดูแลของผู้จัดทำ |
| แหล่งข้อมูล | ข้อมูลปลอมใน [`data/fixtures/demo_coop_rg_2026_10_v2/`](../data/fixtures/demo_coop_rg_2026_10_v2/) ไม่มีการเชื่อม database |
| Environment | Development (ข้อมูลปลอม) ยังไม่มี Production |

## 3. Access and Prerequisites

- เปิด repository ได้โดยไม่ต้องมีบัญชี เพราะเป็น public
- เครื่องที่ใช้ทดสอบต้องมี Python 3.10 ขึ้นไป และ `git`
- ไม่ต้องใช้ password, API key หรือสิทธิ์พิเศษใน version นี้

## 4. User Instructions

สร้างรายงานจากข้อมูลปลอมด้วยคำสั่งเดียว (รันที่โฟลเดอร์รากของ repository):

```bash
python -m quant_software_factory.reporting.returns_transactions data/fixtures/demo_coop_rg_2026_10_v2 reports/demo_coop_rg_2026_10_v2 --account DEMO-0001 --opening 2026-09-30 --as-of 2026-10-30
```

- คำสั่งนี้รันตัวเช็คชั้น A (ข้อมูล) ก่อน ถ้าผ่านจึงสร้างรายงานและรันตัวเช็คชั้น B กับตัวเช็คการเขียน
- ผ่านทั้งหมด: เขียน 4 ไฟล์ลงโฟลเดอร์ปลายทาง และจบด้วย exit code 0
- มีตัวเช็คไม่ผ่าน: เขียนแค่ `checks.json` และจบด้วย exit code 1

## 5. Acceptance Test Walkthrough

| ขั้น | ทำอะไร | ผลที่ควรได้ |
|---|---|---|
| 1 | `git clone https://github.com/Awannaphasch2016/quant-software-factory.git` แล้ว `cd quant-software-factory` | ได้โฟลเดอร์ repository |
| 2 | `python -m venv .venv` แล้ว activate จากนั้น `pip install -e .` | ติดตั้งสำเร็จ ไม่มี dependency ภายนอก |
| 3 | รันคำสั่งในข้อ 4 | แสดง `29 checks, 0 failed` และ exit code 0 |
| 4 | เปิด `reports/demo_coop_rg_2026_10_v2/report.md` | มี 6 ส่วนตามลำดับ: Returns & Transactions Report, KPI summary, Holdings, Transactions, Narrative, Disclaimer |
| 5 | ตรวจ KPI summary | Net asset value 792,398.00, Total P/L 27,398.00, Period return 3.83% |
| 6 | ตรวจ Holdings แถว Total | Cost value 501,000.00, Market value 792,398.00, Unrealized P/L 24,000.00 |
| 7 | ตรวจ Narrative | มีวลี "a realized loss of 3,037.00 THB" และ "a deposit of 50,000.00 THB" |
| 8 | `git status --short reports/` | ไม่มีผลลัพธ์ แปลว่ารายงานที่สร้างใหม่ตรงกับที่ commit ไว้ทุก byte |

ค่าที่คาดหวังครบ 21 แถวอยู่ใน Report Spec (Issue #9) และตารางเทียบอยู่ใน [`appendix/e2e-run-evidence.md`](appendix/e2e-run-evidence.md)

## 6. Delivered Version and Known Limitations

- Version ที่ส่งมอบ: commit `4e2129e` ณ 19 พ.ย. 2569
- ข้อจำกัด:
  - ใช้ข้อมูลปลอมทั้งหมด ยังไม่ได้เทียบกับนิยามและ pipeline จริงของทีม
  - รายงานสร้างด้วยคำสั่งบนเครื่องผู้ทดสอบ ยังไม่มี agent ที่รับ Spec แล้วส่งรายงานกลับ และยังไม่มี Discord
  - รายงานเป็น Markdown และ JSON ยังไม่มี PDF
  - ยังไม่ทราบต้นทุนต่อรายงาน 1 ฉบับ
  - ข้อความบรรยายยังไม่มีตัวเลข "NAV เปลี่ยนไปเท่าไร" และยังเล่าซ้ำกับตาราง (ดู [`appendix/natural-writing-proposal.md`](appendix/natural-writing-proposal.md))
