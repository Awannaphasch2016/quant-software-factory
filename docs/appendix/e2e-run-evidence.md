# หลักฐาน Successful End-to-End Run (requirement_1 ข้อ 3)

Report Spec 1 ใบที่กรอกตาม [`report-spec-structure.md`](report-spec-structure.md) ส่งเข้า Software Factory แล้วได้รายงานที่ตรงตาม Spec ทุกค่า

## 1. Input และ Output

| | ไฟล์ใน repo | ต้นฉบับ |
|---|---|---|
| Input (Report Spec) | [Issue #9](https://github.com/Awannaphasch2016/quant-software-factory/issues/9) (ร่าง: [`report-spec.md`](report-spec.md)) | Issue #9: https://github.com/Awannaphasch2016/quant-software-factory/issues/9 |
| Output (PR) | | PR #10: https://github.com/Awannaphasch2016/quant-software-factory/pull/10 (merge แล้ว commit `4e2129e`) |
| รายงาน | [`../../reports/demo_coop_rg_2026_10_v2/report.md`](../../reports/demo_coop_rg_2026_10_v2/report.md) | https://github.com/Awannaphasch2016/quant-software-factory/blob/main/reports/demo_coop_rg_2026_10_v2/report.md |
| ตัวเลขทุกตัว | [`../../reports/demo_coop_rg_2026_10_v2/report.json`](../../reports/demo_coop_rg_2026_10_v2/report.json) | `reports/demo_coop_rg_2026_10_v2/report.json` บน `main` |
| ข้อความบรรยาย | [`../../reports/demo_coop_rg_2026_10_v2/narrative.md`](../../reports/demo_coop_rg_2026_10_v2/narrative.md) | `reports/demo_coop_rg_2026_10_v2/narrative.md` บน `main` |
| ผลตัวเช็ค | [`../../reports/demo_coop_rg_2026_10_v2/checks.json`](../../reports/demo_coop_rg_2026_10_v2/checks.json) | `reports/demo_coop_rg_2026_10_v2/checks.json` บน `main` |
| CI | | run 43395249810 ผ่าน Python 3.10–3.13: https://github.com/Awannaphasch2016/quant-software-factory/actions/runs/43395249810 |

ไฟล์ output อยู่ใน [`reports/demo_coop_rg_2026_10_v2/`](../../reports/demo_coop_rg_2026_10_v2/) บน `main` (merge commit `4e2129e`) ข้อมูลทั้งหมดเป็นข้อมูลปลอม (บัญชี DEMO-COOP)

Platform Spec ที่สร้าง data layer ให้รายงานนี้คือ Issue #7 → PR #8 ([Issue #7](https://github.com/Awannaphasch2016/quant-software-factory/issues/7), [`platform-spec.md`](platform-spec.md))

## 2. ลำดับเหตุการณ์ (13 พ.ย. 2569, UTC)

| เวลา | เหตุการณ์ |
|---|---|
| 07:16:19 | ติด label `factory` |
| 07:17:34 | Classify ผ่าน: "clear enough to build as written" |
| 07:22:36 | Analysis เสร็จ |
| 07:31:55 | Implement push แล้ว ตัวเช็ค 29 ข้อผ่าน |
| 07:32:06 | หยุดที่เพดาน output token 100K ต่อ session |
| 08:38:30 | ผู้ใช้ตอบ `@eve-forman Approve` |
| 08:41:51 | Review อนุมัติโดยไม่มี blocking issue แล้วเปิด draft PR #10 |
| 08:43:45 | คน merge PR #10 เข้า `main` |

## 3. Expected Values ใน Spec เทียบกับ Output

ค่า "ได้จริง" อ่านจาก [`../../reports/demo_coop_rg_2026_10_v2/report.json`](../../reports/demo_coop_rg_2026_10_v2/report.json), [`../../reports/demo_coop_rg_2026_10_v2/narrative.md`](../../reports/demo_coop_rg_2026_10_v2/narrative.md) และ [`../../reports/demo_coop_rg_2026_10_v2/checks.json`](../../reports/demo_coop_rg_2026_10_v2/checks.json) ด้วยสคริปต์ แล้วเทียบแบบตรงตัวอักษร

| # | Block | Field | Expected (จาก Spec) | ได้จริง | ผล |
|---|---|---|---|---|:-:|
| 1 | header | Client / Account / Strategy | DEMO-COOP / DEMO-0001 / Reverse Grid | DEMO-COOP / DEMO-0001 / Reverse Grid | ✅ |
| 2 | header | Inception | 28 Feb 2024 | 28 Feb 2024 | ✅ |
| 3 | kpi_summary | Net asset value | 792,398.00 | 792,398.00 | ✅ |
| 4 | kpi_summary | Cash | 267,398.00 | 267,398.00 | ✅ |
| 5 | kpi_summary | Realized capital gain | 14,798.00 | 14,798.00 | ✅ |
| 6 | kpi_summary | Dividends (net) | 3,600.00 | 3,600.00 | ✅ |
| 7 | kpi_summary | Change in unrealized P/L | 9,000.00 | 9,000.00 | ✅ |
| 8 | kpi_summary | Total P/L | 27,398.00 | 27,398.00 | ✅ |
| 9 | kpi_summary | Period return | 3.83% | 3.83% | ✅ |
| 10 | holdings | AAA volume / avg cost / cost value | 9,000 / 49.00 / 441,000.00 | 9,000 / 49.00 / 441,000.00 | ✅ |
| 11 | holdings | AAA market price / market value / unrealized | 52.00 / 468,000.00 / 27,000.00 | 52.00 / 468,000.00 / 27,000.00 | ✅ |
| 12 | holdings | BBB volume / avg cost / cost value | 3,000 / 20.00 / 60,000.00 | 3,000 / 20.00 / 60,000.00 | ✅ |
| 13 | holdings | BBB market price / market value / unrealized | 19.00 / 57,000.00 / -3,000.00 | 19.00 / 57,000.00 / -3,000.00 | ✅ |
| 14 | holdings | CASH market value | 267,398.00 | 267,398.00 | ✅ |
| 15 | holdings | Total cost value / market value / unrealized | 501,000.00 / 792,398.00 / 24,000.00 | 501,000.00 / 792,398.00 / 24,000.00 | ✅ |
| 16 | transactions | Row count | 5 | 5 | ✅ |
| 17 | transactions | First row (newest) | 2026-10-26, CASH, DEPOSIT, 50,000.00 | 2026-10-26, CASH, DEPOSIT, 50,000.00 | ✅ |
| 18 | transactions | 2026-10-20 BBB SELL amount / realized | 36,963.00 / -3,037.00 | 36,963.00 / -3,037.00 | ✅ |
| 19 | narrative | Sentence about the BBB sale | contains "a realized loss of 3,037.00 THB" | พบ | ✅ |
| 20 | narrative | Sentence about the deposit | contains "a deposit of 50,000.00 THB" | พบ | ✅ |
| 21 | checks | All Layer A and Layer B checks | passed, exit code 0 | 29/29 passed, exit 0 | ✅ |

ผล: 21 จาก 21 แถว

## 4. ส่วนอื่นของ Spec ที่ตรวจแล้ว

| ข้อกำหนดใน Spec | ผล | หลักฐาน |
|---|---|---|
| `report.md` มี 6 block ตามลำดับ | ✅ Returns & Transactions Report (header), KPI summary, Holdings, Transactions, Narrative, Disclaimer | [`../../reports/demo_coop_rg_2026_10_v2/report.md`](../../reports/demo_coop_rg_2026_10_v2/report.md) |
| Disclaimer ตรงตามข้อความที่กำหนด | ✅ ตรงทุกคำ | [`../../reports/demo_coop_rg_2026_10_v2/report.md`](../../reports/demo_coop_rg_2026_10_v2/report.md) |
| ตัวเช็คชั้น A 14 ข้อ และชั้น B กับการเขียน 15 ข้อ (B0–B8, W1–W5) | ✅ ผ่านทั้ง 29 ข้อ | [`../../reports/demo_coop_rg_2026_10_v2/checks.json`](../../reports/demo_coop_rg_2026_10_v2/checks.json) |
| ข้อความบรรยาย 2–4 ย่อหน้า ไม่เกิน 180 คำ | ✅ 4 ย่อหน้า 154 คำ (ตัวเช็ค W4) | [`../../reports/demo_coop_rg_2026_10_v2/narrative.md`](../../reports/demo_coop_rg_2026_10_v2/narrative.md) |
| รันซ้ำได้ไฟล์เหมือนเดิมทุก byte | ✅ ผู้จัดทำรันคำสั่งใน Spec ซ้ำบน commit `7398e04` แล้วได้ 4 ไฟล์ตรงกับที่ commit | รันเมื่อ 13 พ.ย. 2569 ประมาณ 08:45 UTC |
| ไม่มีค่าลูกค้าหรือบัญชีเขียนตายตัวในโค้ด | ✅ ค้นในโค้ดแล้วไม่พบ | `src/quant_software_factory/reporting/` บน `main` |
| ruff, ruff format, mypy strict, pytest ผ่านบน Python 3.10–3.13 | ✅ | CI run 43395249810 และ CI ของ `main` run 43395497605 |
| Acceptance Criteria ของ Issue | ✅ 12/12 ข้อ | PR #10 body |

คำสั่งที่ใช้รันซ้ำ (ใน repo `quant-software-factory`):

```bash
python -m quant_software_factory.reporting.returns_transactions data/fixtures/demo_coop_rg_2026_10_v2 reports/demo_coop_rg_2026_10_v2 --account DEMO-0001 --opening 2026-09-30 --as-of 2026-10-30
```

## 5. ข้อจำกัด

- พิสูจน์กับรายงาน 1 ประเภท (`returns_transactions`) และข้อมูลปลอม ไม่ได้ยืนยันว่าตัวเลขตรงกับนิยามของทีม หรือพร้อมใช้กับข้อมูลจริง
- โรงงานหยุดที่เพดาน token 1 ครั้ง ต้องมีคนตอบ Approve ก่อนจะได้ PR
- ข้อความบรรยายยังไม่พูดถึงตัวเลข "NAV เปลี่ยนไปเท่าไร" ตามที่ Writing Rules ขอ เพราะไม่มีตัวเลขนี้ในชุดข้อมูล โรงงานเลือกไม่คำนวณเองตามหลักห้ามคำนวณใหม่ บันทึกเป็น spec gap ใน [`report-spec-structure.md`](report-spec-structure.md) ข้อ 13
