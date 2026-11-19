# Progress Report: Iteration 1

- ขอบเขต: requirement_1 (Reusable Spec Template สำหรับ Software Factory)
- ช่วงเวลา: 9 ถึง 13 พฤศจิกายน 2569
- สถานะ ณ 13 พ.ย. 2569: ครบ 3 รอบของ Specification, Research และ Prototype (Template v0.1, v0.2 และ v0.3) รอบ v0.2 ไม่ถึง Output แต่บันทึกผลและนำไปแก้ใน v0.3 แล้ว
- ไม่รวมเรื่องการเชื่อม Grokbot หรือ Slack (Acceptance Criteria ข้อ 5) ซึ่งยังไม่ได้เริ่มและจะรายงานแยก

## 1. สรุป

ผมออกแบบโครงสร้าง Spec สำหรับรายงาน 3 ประเภท และทดลองกับโรงงาน (Foreman) ใน `quant-software-factory` 4 run ด้วยรายงานผลตอบแทนและรายการลงทุนของบัญชีปลอม DEMO-COOP ทุก run ใช้ข้อมูลปลอมชุดเดียวกันและตัวเลขเดียวกัน

| Run | Template | Spec | ผล |
|---|---|---|---|
| #1 | v0.1 (คำนวณเอง) | Issue #4 | draft PR #5 ตัวเลขตรงทุกค่า CI ผ่าน ไม่ได้ merge เพราะใช้แนวทางคำนวณเอง |
| #2 | v0.2 (Data Mapping) | Issue #6 | หยุดที่เพดาน token ต้นขั้น implement ไม่ทำงานต่อหลังอนุมัติ 2 ครั้ง ปิด Issue แล้ว |
| #3 | v0.3 Platform Spec | Issue #7 | PR #8 จบเองโดยไม่ต้องอนุมัติกลางทาง CI ผ่าน merge แล้ว |
| #4 | v0.3 Report Spec | Issue #9 | PR #10 ตัวเลขตรงทุกค่า ตัวเช็ค 29/29 CI ผ่าน merge แล้ว ต้องอนุมัติ token 1 ครั้ง |

หลัง Run #1 ผมได้ข้อมูลจากทีมว่า pipeline คำนวณตัวเลขไว้ให้แล้ว งานจริงคือดึงข้อมูลมาทำรายงานและเช็คตัวเลข จึงเปลี่ยน Template เป็น v0.2 ที่ใช้ Data Mapping แทนสูตร Run #2 ชี้ว่า Spec ใหญ่เกินไปสำหรับ session เดียว และมีจุดที่ Spec ขัดกันเอง v0.3 จึงแยก Spec เป็น 2 ชนิด คือ Platform Spec (ทำครั้งเดียว) และ Report Spec (กรอก 1 ใบได้รายงาน 1 ฉบับ)

Run #4 เป็นหลักฐานหลักของ Acceptance Criteria ข้อ 3 เพราะตรงกับโจทย์ที่สุด คือกรอก Report Spec 1 ใบตาม Template v0.3 แล้วได้รายงานที่ตรงกับ Spec และ merge เข้า `main` แล้ว

## 2. สิ่งที่ทำ

| งาน | ผลลัพธ์ | ไฟล์ / หลักฐาน |
|---|---|---|
| ศึกษาการทำงานของ Foreman จาก Issue #1, PR #2 และโค้ดใน `eve-software-factory-template` | รู้ลำดับสถานี (classify, plan, implement, review, PR) เงื่อนไขการติด label, เพดาน token และโมเดล (ตามค่าใน template ตั้งไว้ที่ Claude Opus 5.5 ทุกสถานี ส่วนตัวที่ deploy อยู่ยังไม่ได้ยืนยัน) | ยังไม่ได้เขียนเป็นเอกสารแยก |
| เทียบรายงานตัวอย่างของทีม 3 ฉบับ | แตกเป็น block มาตรฐาน และ preset ของรายงาน 3 ประเภท | [`history/report-spec-template.md`](history/report-spec-template.md) ภาคผนวก A |
| Report Spec Template v0.1 | โครง Spec 13 หัวข้อ, กติกาการแตก Spec, นิยามตัวเลข, Output Contract, ตัวตรวจ 3 ชั้น | [`history/report-spec-template.md`](history/report-spec-template.md) |
| Example Input v0.1 | Spec ของรายงานผลตอบแทนและรายการลงทุน บัญชีปลอม DEMO-COOP เดือน ต.ค. 2569 ค่าคาดหวัง 25 แถว | [`history/example-input-returns-demo.md`](history/example-input-returns-demo.md), Issue #4 |
| Run #1 | Issue #4 ถึง draft PR #5 | ข้อ 3 |
| อ่านเอกสารแหล่งข้อมูลของทีม | ตัวเลขในรายงานลูกค้ามาจากชุดข้อมูลที่ pipeline คำนวณไว้แล้ว และ pipeline มีตัวเช็คข้อมูลบางส่วนอยู่แล้ว | เอกสารภายใน ไม่ได้นำขึ้น repo |
| Report Spec Template v0.2 (โครงเปิด) | Data Mapping แทนสูตร, ชื่อกลางแทนชื่อระบบภายใน, interface `load(...)`, ตัวเช็ค 2 ชั้น, หัวข้อ Open Items | [`history/report-spec-template-v0.2.md`](history/report-spec-template-v0.2.md) |
| Merge PR #2 เข้า `main` | `main` มีโครง repo (pyproject, CI) ให้ Issue ต่อจากนี้แตก branch จาก `main` ได้ | commit `e6a0963`, 12 พ.ย. 09:15 UTC |
| Example Input v0.2 | รายงานเดิม ตัวเลขชุดเดิม แต่ input เป็นชุดข้อมูลที่คำนวณแล้ว 6 ชุด, 6 block, ตัวเช็ค 11 ข้อ | [`history/example-input-v0.2-returns-demo.md`](history/example-input-v0.2-returns-demo.md), Issue #6 |
| Run #2 | Issue #6 ผ่าน Classify และ Analysis แล้วหยุด ปิด Issue เป็น not planned เมื่อ 13 พ.ย. 06:48 UTC | ข้อ 4 |
| Report Spec Template v0.3 | แยก Platform Spec กับ Report Spec และแก้ spec gap 4 จุดจาก Run #2 | [`history/report-spec-template-v0.3.md`](history/report-spec-template-v0.3.md) |
| Platform Spec v0.3 | data access, schema registry, fixture 6 ชุด, ตัวเช็คชั้น A 14 ข้อ | [`platform-spec.md`](platform-spec.md), Issue #7 |
| Run #3 | Issue #7 ถึง PR #8 แล้ว merge | ข้อ 5 |
| Report Spec v0.3 | รายงาน 6 block, Expected Values 21 แถว, ตัวเช็คชั้น B และการเขียน | [`report-spec.md`](report-spec.md), Issue #9 |
| Run #4 | Issue #9 ถึง PR #10 แล้ว merge | ข้อ 5 |
| วิธีวัดผล Spec | Scorecard ด้านผลลัพธ์ กระบวนการ และคุณภาพ พร้อมผลของทั้ง 4 run | [`history/spec-eval-method.md`](history/spec-eval-method.md) |
| Skill ตรวจ AI slop | 6 องค์ประกอบจากทอล์กที่พี่ Anak แนบ + กติกาเฉพาะรายงานของฝ่าย Quant | skill `ai-slop-report-review` (อยู่ในเครื่องผู้จัดทำ ไม่ได้อยู่ใน repo) |
| Natural Writing Proposal | ข้อเสนอ 3 ชั้น (Spec, Writing Guidelines, ตรวจ Output) พร้อมผลตรวจข้อความจาก Run #1 และ Run #4 และฉบับแก้ | [`natural-writing-proposal.md`](natural-writing-proposal.md) |

ข้อมูลใน Spec ทุกใบเป็นข้อมูลปลอม และไม่มีชื่อระบบภายใน เพราะ `quant-software-factory` เป็น public repo รายงานตัวอย่างของทีมใช้แค่ดูโครงสร้าง

## 3. ผลการทดลอง: Run #1 (Template v0.1)

### Input และ Output

| | ที่อยู่ |
|---|---|
| Input (Spec) | Issue #4: https://github.com/Awannaphasch2016/quant-software-factory/issues/4 |
| Output (draft PR) | PR #5: https://github.com/Awannaphasch2016/quant-software-factory/pull/5 |
| รายงานที่ได้ | `reports/demo_coop_rg_2026_10/report.md` บน branch `feat/returns-transactions-report-issue-4` |
| Commit ล่าสุดของ PR | `fcdbeea086414dd91da7303272064169f0207d11` |
| CI | GitHub Actions run 43151748082 ผ่าน |

### ลำดับเหตุการณ์

ติด label เมื่อ 12 พ.ย. 03:27:08 UTC และได้ draft PR เมื่อ 03:58:53 UTC รวม 31 นาที 45 วินาที ในจำนวนนี้ประมาณ 11 นาทีเป็นช่วงที่โรงงานหยุดที่เพดาน output token 100K และรอผมตอบ `@eve-forman Approve` เวลาของแต่ละขั้นอยู่ใน Design Prototype ข้อ 4.1 และหลักฐานอยู่ในข้อ 6 ของเอกสารเดียวกัน

### ผลตาม Scorecard

| ตัวชี้วัด | ผล |
|---|---|
| ค่าคาดหวังใน Spec ที่ตรง | ทุกค่า (test 36 กรณี) ผมเปิด `report.md` ตรวจซ้ำแล้ว เช่น NAV ปลายงวด 792,398.00 และ P/L รวม 27,398.00 |
| Acceptance Criteria ของ Issue | 13 จาก 13 ข้อ ตามที่ reviewer ติ๊กใน PR |
| ตัวตรวจขณะรัน (`checks.json`) | 24 จาก 24 ข้อ ผลต่างจากการกระทบยอด 0.00 |
| CI | ผ่าน Python 3.10, 3.11, 3.12 และ 3.13 |
| ผล Classify | ผ่านโดยไม่ต้องขอข้อมูลเพิ่ม |
| จุดที่โรงงานต้องตัดสินใจเอง | 5 จุด (base branch, รูปแบบ %, ค่าว่าง, ข้อมูลหัวรายงานในโค้ด, การลบไฟล์เก่า) อีก 2 จุดในข้อ 7 มาจากข้อเสนอของ reviewer |
| รอบที่ reviewer ส่งกลับ | 0 |

ไม่ได้ merge PR #5 เพราะ Run #1 ใช้แนวทางคำนวณเอง ซึ่งไม่ตรงกับข้อสรุปใหม่ที่ว่าตัวเลขคำนวณไว้แล้ว เก็บ PR ไว้เป็นหลักฐาน

## 4. ผลการทดลอง: Run #2 (Template v0.2)

| | ที่อยู่ |
|---|---|
| Input (Spec) | Issue #6: https://github.com/Awannaphasch2016/quant-software-factory/issues/6 |
| Output | ไม่มี PR |

| เวลา (UTC) | เหตุการณ์ |
|---|---|
| 12 พ.ย. 09:24:32 | ติด label `factory` |
| 12 พ.ย. 09:26:22 | Classify ผ่าน: "the spec is clear enough to build as written" และระบุว่าจะแตก branch ใหม่จาก `main` ไม่ต่อจาก PR #5 |
| 12 พ.ย. 09:32:07 | Analysis เสร็จ: แผนแยก module ตาม Spec, ตัวเช็คครบ 11 ข้อ และทุกข้อมี test ที่ทำให้ไม่ผ่าน |
| 12 พ.ย. 09:39:44 | หยุดที่เพดาน output token 44.9K ต่อ session |
| 12 พ.ย. 09:41:51 | ผมตอบ `@eve-forman Approve` |
| 13 พ.ย. 06:17 | ผมตอบ `@eve-forman Approve` ครั้งที่ 2 |
| 13 พ.ย. 06:48:48 | ไม่มีคอมเมนต์ใหม่ ไม่มี branch ไม่มี PR จึงปิด Issue เป็น not planned แล้วแตกเป็น Spec ใหม่ (ข้อ 5) |

สิ่งที่ Run #2 แสดงได้:

- Template v0.2 ผ่าน Classify และ Analysis โดยไม่ต้องขอข้อมูลเพิ่ม
- spec gap เรื่อง base branch จาก Run #1 แก้ได้จริง โรงงานแตก branch จาก `main` ตามที่ Spec สั่ง
- โรงงานยังต้องตัดสินใจเอง 5 จุด และถามกลับ 2 ข้อ (ดูข้อ 7) ส่วนใหญ่เป็นจุดที่ Spec เขียนไม่ชัด และมี 1 จุดที่ Spec ขัดกันเอง (Writing Rules กับ B8)

สิ่งที่ Run #2 แสดงไม่ได้: ผลลัพธ์ของโค้ด, ตัวเลขในรายงาน, review และ CI สาเหตุที่โรงงานไม่ตอบหลังอนุมัติยังไม่ทราบ ใน Run #1 และ Run #4 โรงงานทำงานต่อหลังอนุมัติและได้ PR ภายในประมาณ 4 นาที จึงต้องให้พี่ Anak ดู log ฝั่ง Vercel

## 5. ผลการทดลอง: Run #3 และ Run #4 (Template v0.3)

v0.3 แยก Spec เป็น 2 ชนิด (รายละเอียดใน [`report-spec-structure.md`](report-spec-structure.md) ข้อ 2 และ [`platform-spec-structure.md`](platform-spec-structure.md))

- Platform Spec ทำครั้งเดียว: interface `load(...)`, fixture และตัวเช็คชั้น A
- Report Spec กรอกใบเดียวต่อรายงาน 1 ฉบับ และใช้ data layer ที่ merge แล้ว

### Input และ Output

| | Run #3 (Platform Spec) | Run #4 (Report Spec) |
|---|---|---|
| Input (Spec) | Issue #7: https://github.com/Awannaphasch2016/quant-software-factory/issues/7 | Issue #9: https://github.com/Awannaphasch2016/quant-software-factory/issues/9 |
| Output (PR) | PR #8: https://github.com/Awannaphasch2016/quant-software-factory/pull/8 | PR #10: https://github.com/Awannaphasch2016/quant-software-factory/pull/10 |
| Commit ของ PR | `3384bbcfc9a5237022e830ea888cc547c4858942` | `7398e040003d139f67d33d8df1f918b34e9f259a` |
| CI ของ PR | run 43383851475 ผ่าน 3.10–3.13 | run 43395249810 ผ่าน 3.10–3.13 |
| Merge เข้า `main` | 13 พ.ย. 07:13:08 UTC, commit `9455ea3` | 13 พ.ย. 08:43:45 UTC, commit `4e2129e` |
| CI ของ `main` หลัง merge | run 43384155137 ผ่าน | run 43395497605 ผ่าน |
| Output ที่ได้ | `reports/demo_coop_rg_2026_10_v2/checks.json` (ตัวเช็คชั้น A 14 ข้อ) | `reports/demo_coop_rg_2026_10_v2/` ครบ 4 ไฟล์: `report.md`, `report.json`, `narrative.md`, `checks.json` (สำเนาอยู่ใน [`../../reports/demo_coop_rg_2026_10_v2/`](../../reports/demo_coop_rg_2026_10_v2/)) |

### ลำดับเหตุการณ์ (13 พ.ย., UTC)

| | Run #3 | Run #4 |
|---|---|---|
| ติด label | 06:58:00 | 07:16:19 |
| Classify | 06:59:22 | 07:17:34 |
| Analysis | 07:02:59 | 07:22:36 |
| Implement push | 07:07:22 | 07:31:55 |
| หยุดที่เพดาน token | ไม่หยุด | 07:32:06 (100K ต่อ session) ก่อนขั้น review |
| ผมตอบ Approve | ไม่ต้อง | 08:38:30 |
| เปิด PR | 07:10:34 | 08:41:51 |
| รวม | 12 นาที 34 วินาที | 85 นาที 32 วินาที ในจำนวนนี้ 66 นาที 24 วินาทีเป็นเวลารอคนอนุมัติ เวลาที่โรงงานทำงานประมาณ 19 นาที |

### ผลตาม Scorecard

| ตัวชี้วัด | Run #3 | Run #4 |
|---|---|---|
| ค่าคาดหวังใน Spec ที่ตรง | ทุกแถว (11 แถว) ตามที่ reviewer ยืนยัน | ทุกแถว (21 แถว) ผมรันคำสั่งใน Spec เองแล้วเทียบ `report.md` ทีละแถว |
| Acceptance Criteria ของ Issue | 10 จาก 10 ข้อ | 12 จาก 12 ข้อ |
| ตัวเช็คใน `checks.json` | 14/14 | 29/29 (ชั้น A 14 และชั้น B กับการเขียน 15) |
| รันซ้ำได้ผลเหมือนเดิม | ไฟล์ตรงกันทุก byte ตามที่โรงงานรายงาน | ผมรันซ้ำในเครื่องเองแล้ว ทั้ง 4 ไฟล์ตรงกับที่ commit ทุก byte และ pytest ผ่าน 149 กรณี |
| ผล Classify | ผ่านโดยไม่ต้องขอข้อมูลเพิ่ม และจับจุดผิดใน Spec ได้ 1 จุด (Spec บอกว่าเมื่อไม่มี `holdings_daily` ให้รายงาน A1 ว่า not run แต่ A1 อ่านแค่ `nav_daily`) | ผ่านโดยไม่ต้องขอข้อมูลเพิ่ม |
| จุดที่โรงงานต้องตัดสินใจเอง | 5 จุด (ชื่อตัวเช็ค, ข้อความใน `expected` และ `actual`, แถวที่วันที่อ่านไม่ได้, A3 ไม่ตรวจ `realized_pl` บนแถวที่ไม่ใช่ SELL, A3 ไม่ตรวจว่า `cash_flow.amount` เป็นบวก) | 5 จุด (ช่วงเวลาคิดจากเดือนของ as-of, เพิ่มตัวเช็ค B0, แยก B7 เป็น 2 ข้อ, ไม่เขียนตัวเลข "NAV เปลี่ยนไปเท่าไร", แก้ test เดิม 2 ตัวให้เทียบเฉพาะผลชั้น A) |
| รอบที่ reviewer ส่งกลับ | 0 | 0 |

ข้อความบรรยายของ Run #4 (ตัดมาบางส่วน) แก้ปัญหาภาษาจาก Run #1 ได้ทั้ง 2 จุด:

> During the period the account made 2 sales: AAA on 12 Oct 2026 with a realized gain of 17,835.00 THB and BBB on 20 Oct 2026 with a realized loss of 3,037.00 THB. ...
>
> The account received a deposit of 50,000.00 THB on 26 Oct 2026. No withdrawals were made in the period.

สิ่งที่ Run #3 และ #4 แสดงได้:

- Spec 1 ใบตาม Template v0.3 ได้รายงานที่ตรงกับ Spec ตั้งแต่ input ถึง output และผ่านการตรวจของคน (merge แล้ว)
- spec gap 3 จาก 4 จุดของ Run #2 แก้ได้จริง ส่วนเรื่องเครื่องหมายเงินถอนมีโค้ดและ test แล้ว แต่ fixture ไม่มีรายการถอน
- Platform Spec จบได้เองโดยไม่ต้องมีคนกดอนุมัติกลางทาง

สิ่งที่ยังแสดงไม่ได้:

- Report Spec ยังจบเองไม่ได้ (ดู Design gap ในข้อ 7)
- ยังพิสูจน์กับรายงานแค่ประเภทเดียว

## 6. สถานะตาม Acceptance Criteria ของ requirement_1

| ข้อ | งาน | สถานะ | หลักฐาน |
|---|---|---|---|
| 1 | Reusable Spec Template | Demonstrated กับรายงาน 1 ประเภท (v0.1 ใน Run #1, v0.3 ใน Run #3 และ #4) อีก 2 ประเภทเป็น Intended (มี preset แต่ยังไม่ได้รัน) | [`report-spec-structure.md`](report-spec-structure.md) และ [`platform-spec-structure.md`](platform-spec-structure.md), ประวัติ: [`history/report-spec-template.md`](history/report-spec-template.md), [`history/report-spec-template-v0.2.md`](history/report-spec-template-v0.2.md), [`history/report-spec-template-v0.3.md`](history/report-spec-template-v0.3.md) |
| 2 | Example Input | Demonstrated (v0.1, v0.2 และ v0.3) | [`history/example-input-returns-demo.md`](history/example-input-returns-demo.md), [`history/example-input-v0.2-returns-demo.md`](history/example-input-v0.2-returns-demo.md), [`platform-spec.md`](platform-spec.md), [`report-spec.md`](report-spec.md) |
| 3 | Successful End-to-End Run | Demonstrated 2 ครั้ง: Run #1 (v0.1) และ Run #4 (v0.3, merge แล้ว) | Issue #4 → PR #5, CI run 43151748082; Issue #9 → PR #10, CI run 43395249810, commit `4e2129e`; ตารางเทียบ [`e2e-run-evidence.md`](e2e-run-evidence.md), ไฟล์ output ใน [`../../reports/demo_coop_rg_2026_10_v2/`](../../reports/demo_coop_rg_2026_10_v2/) |
| 4 | Progress Report | เอกสารนี้ | |
| 5 | Grokbot / Slack | ยังไม่เริ่ม (อยู่นอกรายงานนี้) | |
| 6 | Natural Writing Proposal | ข้อเสนอเสร็จแล้ว ส่วนที่ทดลองได้คือ template ในโค้ดพร้อมกติกาค่าติดลบ เอกพจน์/พหูพจน์ และตัวเช็ค W1–W5 (Run #4) ส่วน narrative facts และ LLM judge เป็น Intended | [`natural-writing-proposal.md`](natural-writing-proposal.md), สรุปในข้อ 8 |

## 7. ปัญหาที่พบ

### Specification gap

| Run | จุดที่พบ | สถานะ |
|---|---|---|
| 1 | ไม่ได้ระบุ base branch ทั้งที่ `main` มีแค่ README | แก้แล้ว: v0.2 มีช่อง Base branch และ merge PR #2 แล้ว Run #2–#4 ยืนยันว่าได้ผล |
| 1 | ข้อมูลหัวรายงานไม่ได้เป็น input โรงงานจึงเขียนไว้ในโค้ด | แก้แล้ว: อ่านจาก `account_info` Run #4 ยืนยันว่าไม่มีค่า hard-code ในโค้ด |
| 1 | ไม่ได้กำหนดรูปแบบตัวเลขใน JSON และค่าว่าง | แก้แล้ว: Run #4 ใช้ string ที่จัดรูปแบบแล้วและ `null` ตาม Spec |
| 1 | "one row per instrument" ไม่ชัดว่ารวมหุ้นที่ขายหมดหรือไม่ | แก้แล้ว: ระบุว่าแสดงเฉพาะที่ยังถือ |
| 1 | Writing Rules ไม่ได้กำหนดวิธีเขียนค่าติดลบและเอกพจน์/พหูพจน์ | แก้แล้ว: Run #4 ยืนยัน |
| 1 | Spec ให้คำนวณตัวเลขเอง ซึ่งไม่ตรงกับงานจริงของทีม | แก้แล้ว: Data Mapping แทนสูตร |
| 2 | ตัวเช็ค A2 บังคับให้ทุกชุดข้อมูลมีอย่างน้อย 1 แถว เดือนที่ไม่มีเงินเข้าออกจึง fail | แก้แล้วใน v0.3: Run #3 มี test กรณีว่างแล้วผ่าน |
| 2 | Writing Rules ให้เขียนค่าติดลบเป็น "loss" (ค่าบวก) แต่ B8 ต้องการตัวเลขตรงกับ JSON (ค่าลบ) จึงขัดกันเอง | แก้แล้วใน v0.3: Run #4 ยืนยัน |
| 2 | B8 ไม่ได้บอกว่าวันที่และจำนวนนับเป็นตัวเลขที่ต้องตรวจหรือไม่ | แก้แล้วใน v0.3: Run #4 ยืนยัน |
| 2 | ไม่ได้บอกเครื่องหมายของเงินถอนในตาราง | แก้แล้วใน v0.3 แต่ fixture ไม่มีรายการถอน |
| 3 | Spec บอกว่าเมื่อไม่มี `holdings_daily` ให้รายงาน A1 ว่า not run แต่ A1 อ่านแค่ `nav_daily` | โรงงานจับได้ตอน Classify และทำถูก ต้องแก้ใน Platform Spec ถ้าใช้ซ้ำ |
| 4 | Writing Rules สั่งให้พูดถึง "การเปลี่ยนแปลงของ NAV" แต่ตัวเลขนี้ไม่มีในชุดข้อมูล | รอแก้ใน v0.4: เพิ่ม opening NAV ใน Data Mapping |
| 4 | ไม่ได้บอกว่าช่วงเวลาของรายงานคิดจาก opening date หรือเดือนของ as-of ถ้าใส่ opening date ผิด B5 จะแจ้งว่าตัวเลขไม่ตรง แทนการแจ้งว่าใส่วันที่ผิด | รอแก้ใน v0.4 |
| 4 | ตัวเช็ค B0 (ค่าที่ต้อง map หายไป) ไม่มีใน Spec โรงงานเพิ่มเอง | รอแก้ใน v0.4: เพิ่มเป็นตัวเช็คมาตรฐาน |

### Design gap

| จุดที่พบ | ผลกระทบ | แนวทาง |
|---|---|---|
| Spec ขนาด 8 block (Run #1) และ 6 block กับตัวเช็ค 11 ข้อ (Run #2) ชนเพดาน output token | ต้องมีคนกดอนุมัติกลางทาง ถ้าไม่มีคนตอบงานจะค้าง | แก้บางส่วนใน v0.3: Platform Spec จบเอง ส่วน Report Spec ดูแถวสุดท้าย |
| เพดานของ Run #2 (44.9K) ต่ำกว่ารอบอื่น (100K) และหลังอนุมัติโรงงานไม่ทำงานต่อ | Run #2 ไม่ถึง Output | ต้องถามพี่ Anak เรื่อง budget และ log ฝั่ง Vercel |
| Report Spec ที่มีรายงาน ข้อความบรรยาย และตัวเช็ค 15 ข้อ ใช้ token เกิน 1 session | การสั่งงานผ่านแชต (ข้อ 5) จะต้องมีคนตอบอนุมัติในแชตด้วย | ถามพี่ Anak ว่าเพิ่มเพดานได้หรือไม่ หรือลดขนาด Report Spec แล้ววัดซ้ำ |

การแตก Spec มีข้อเสีย คือต้องเขียน Spec หลายใบ ต้อง merge ตามลำดับ และทุกใบมีค่าใช้จ่ายคงที่ของ classify, plan และ review แต่ Platform Spec ทำครั้งเดียว รายงานใหม่ต่อจากนี้จึงต้องเขียนแค่ Report Spec

## 8. Natural Writing Proposal (สรุปจาก [`natural-writing-proposal.md`](natural-writing-proposal.md))

หลักที่คุมทุกข้อ: ตัวเลขในข้อความต้องมาจาก `report.json` และใช้รูปแบบเดียวกับตาราง ข้อความห้ามสร้างหรือแก้ตัวเลข การทำให้อ่านเป็นธรรมชาติจึงทำได้แค่กับการเลือกเรื่องที่จะเล่า ลำดับ และถ้อยคำ

### แนวทางที่เสนอ

| ชั้น | แนวทาง | สถานะ |
|---|---|---|
| 1. การออกแบบ Spec | Writing Rules ทุกข้อต้องตรวจได้; ระบุผู้อ่านและสิ่งที่ผู้อ่านต้องรู้; เรียงหัวข้อของข้อความตามสิ่งที่ผู้อ่านต้องรู้ ไม่ใช่ตามลำดับตาราง; ให้โค้ดคำนวณ "narrative facts" (เช่น หุ้นที่ให้ P/L มากที่สุด) ลงใน JSON; ใส่ตัวอย่างที่ดีและไม่ดีใน Spec | กติกาที่ตรวจได้: Demonstrated (Run #4) ส่วนที่เหลือ: Intended |
| 2. Writing Guidelines | ค่าติดลบเขียนเป็นขาดทุน; เอกพจน์/พหูพจน์ตรงกับจำนวน; ป้ายช่วงเวลาตรงกับตัวเลข; ไม่ทวนตัวเลขที่ตารางมีแล้ว; ไม่ใช้ศัพท์ภายใน เช่น "as-of date"; ไม่อธิบายสาเหตุ; ห้ามคาดการณ์ | ค่าติดลบ เอกพจน์ และห้ามคาดการณ์: Demonstrated (Run #4) ส่วนที่เหลือ: Intended และยังไม่ได้ยืนยันกับทีม |
| 3. การตรวจ Output | ตัวเช็คอัตโนมัติก่อน (ตัวเลขในข้อความ B8 และ W1–W5) แล้วใช้ LLM judge 2 ค่ายขึ้นไปกับเรื่องที่โค้ดตรวจไม่ได้ ไม่เกิน 3 รอบ แล้วคนอนุมัติขั้นสุดท้าย | ตัวเช็คอัตโนมัติ: Demonstrated (Run #4) LLM judge: Intended |

วิธีสร้างข้อความเสนอให้ขยับเป็นขั้น และขยับต่อเมื่อตัวเช็คของขั้นก่อนครบแล้วเท่านั้น:
1. template ในโค้ด (Demonstrated)
2. template หลายแบบ + narrative facts (Demonstrated บางส่วน)
3. LLM เขียนจาก JSON แล้วต้องผ่านตัวเช็คตัวเลข (Intended)
4. หลายร่างแล้วรวมร่าง (Intended)

### ผลทดลอง

ผมตรวจข้อความบรรยายของ Run #1 และ Run #4 ด้วย skill `ai-slop-report-review` ซึ่งใช้ 6 องค์ประกอบจากทอล์กที่พี่ Anak แนบไว้ (1 = สะอาด, 4 = แทรกทั่วทั้งฉบับ)

| องค์ประกอบ | Run #1 | Run #4 |
|---|:-:|:-:|
| 1. คำเฝือ | 1 | 1 |
| 2. กว้างเกินไป | 1 | 1 |
| 3. พูดแต่ไม่ได้บอกอะไร | 1 | 2 |
| 4. ซ้ำ | 3 | 3 |
| 5. Hallucination | 1 | 1 |
| 6. น้ำเสียง | 3 | 2 |

- Run #4 แก้น้ำเสียงได้จริง: "a realized capital gain of -3,037.00 THB" กลายเป็น "a realized loss of 3,037.00 THB" และ "Deposits of" กลายเป็น "a deposit of"
- การซ้ำไม่ดีขึ้น ตัวเลขทั้ง 12 ตัวในข้อความมีในตารางแล้ว และวลีบอกช่วงเวลา ("for the period", "in the period", "During the period") ใช้รวม 5 ครั้ง สาเหตุอยู่ที่ Spec: Writing Rules สั่งลำดับหัวข้อตามลำดับตาราง และไม่มีข้อไหนสั่งให้บอกว่า P/L รวมมาจากส่วนไหน
- ผมเขียนฉบับแก้ด้วยมือโดยใช้ตัวเลขเดิม เริ่มจาก P/L รวมแล้วแยกเป็นส่วนประกอบ ผลคือผ่านตัวเช็ค B8, W3, W4 และ W5 และยาว 137 คำ ฉบับแก้นี้ยังสร้างด้วย template ในโค้ดได้ จึงแก้ได้ที่ Writing Rules ไม่ต้องใช้ LLM (ข้อความเต็มอยู่ใน [`natural-writing-proposal.md`](natural-writing-proposal.md) ข้อ 3.2)

ตัวอย่างย่อหน้าที่ 2 ของฉบับแก้:

> That gain came from three sources: realized gains of 14,798.00 THB, net dividends of 3,600.00 THB, and an increase of 9,000.00 THB in unrealized P/L.

ข้อจำกัด: คะแนนเป็นการตรวจของผมกับ skill ยังไม่มี judge อิสระหรือคนในทีมตรวจซ้ำ และฉบับแก้ยังไม่ได้ให้โรงงานสร้างจาก Writing Rules ใหม่

## 9. ค่าใช้จ่ายต่อ run (ค่าประมาณ)

ยังไม่มีตัวเลขจริง ค่าใช้จ่ายอยู่ในบัญชี Vercel ของพี่ Anak ตัวเลขด้านล่างเทียบจากต้นทุนของ Issue #1 ที่พี่ Anak วัดไว้ใน Design Prototype (ประมาณ $2.30 ต่อรอบ, output 46.6K tokens, โค้ด +320 บรรทัด) โดยใช้อัตราส่วน output token และอัตรา 33.5 บาทต่อดอลลาร์ ใช้เป็นจุดอ้างอิงของ 1 run ไม่ใช่การคาดการณ์

| Run | ข้อมูลที่รู้ | ประมาณ |
|---|---|---|
| Issue #1 (อ้างอิง) | วัดแล้ว | ~$2.30 ≈ 77 บาท |
| Run #1 | output ชนเพดาน 100K แล้วทำต่ออีกเล็กน้อย, โค้ด +3,077 บรรทัด | ~$4–6 ≈ 135–200 บาท |
| Run #2 | ชนเพดานที่ 44.9K ไม่ถึง Output | ประมาณไม่ได้ |
| Run #3 | ไม่ชนเพดาน ไม่ทราบจำนวน output token, โค้ด +879 บรรทัด | ประมาณไม่ได้ |
| Run #4 | output ชนเพดาน 100K แล้วทำต่ออีกเล็กน้อย, โค้ด +2,012 บรรทัด | ~$4–6 ≈ 135–200 บาท (เทียบกับ Run #1) |

การประมาณนี้หยาบ เพราะต้นทุนส่วนใหญ่ของ Issue #1 มาจาก cache read ซึ่งขึ้นกับจำนวนรอบที่ agent ทำงาน ไม่ได้ขึ้นกับ output อย่างเดียว

## 10. เรื่องที่ยังเหลือ

1. ยังไม่มีนิยามและชื่อคอลัมน์จริงของชุดข้อมูล ตัวอย่างข้อมูลที่ลบตัวตนแล้ว และข้อมูลว่า repo หรือ pipeline ใดจะรันโค้ด Template จึงใช้ชื่อกลาง และรวมสิ่งที่ขาดไว้ใน Open Items 8 ข้อ (Template v0.2 ข้อ 12)
2. รายงานประจำเดือนของฝ่าย Quant คือรายงานไหนยังไม่ชัด รายงานที่ทำใน Canva เป็นรายงานเฉพาะ event จึงอยู่นอกขอบเขต preset `monthly_team` ยังเป็นโครงเปิด
3. รายงานตัวอย่างของทีมมีป้ายกำกับบางจุดที่ไม่ตรงกับตัวเลข เช่น ป้าย "since inception" บนตัวเลขที่ตรงกับยอด YTD ยังไม่รู้ว่าเป็นบั๊กหรือนิยามที่ตั้งใจ
4. สาเหตุที่ Run #2 ค้างหลังอนุมัติยังไม่ทราบ ต้องให้พี่ Anak ดู log และ budget
5. การใช้ซ้ำพิสูจน์ได้แค่รายงานประเภทเดียว
6. Output รอบนี้เป็น Markdown และ JSON ไม่ใช่ PDF เพราะ requirement_1 ไม่ได้บังคับรูปแบบ และ PDF ต้องเพิ่ม dependency
7. ยังไม่ทราบค่าใช้จ่ายจริงต่อ run
8. PR #3 (CI ไม่ผ่านบน Python 3.10 และ 3.11) และ PR #5 ยังเปิดค้าง ไม่ได้แตะในรอบนี้
9. spec gap ใหม่ 3 จุดจาก Run #4 (ข้อ 7) ยังไม่ได้แก้

## 11. แผนรอบถัดไป

| งาน | เหตุผล |
|---|---|
| Template v0.4: แก้ spec gap 3 จุดจาก Run #4 | ลดจุดที่โรงงานต้องเดา |
| Report Spec ของรายงาน P&L ลูกค้า โดยใช้ data layer เดิม | พิสูจน์การใช้ซ้ำกับรายงานอีกประเภท และวัดว่าเขียนแค่ Report Spec ก็พอจริงหรือไม่ |
| ถามพี่ Anak เรื่องเพดาน token, log ของ Run #2 และค่าใช้จ่ายจริง | ปิดเรื่องที่ค้างในข้อ 10 และหาทางให้ Report Spec จบโดยไม่ต้องอนุมัติ |
| แก้ลำดับหัวข้อใน Writing Rules ตามฉบับแก้ในข้อ 8 แล้วทำ Natural Writing ขั้นที่ 2 (narrative facts) | แก้ปัญหาข้อความที่ยังเล่าตามตาราง (องค์ประกอบ 4) และวัดคะแนนเทียบกับ Run #4 |
| เริ่มเรื่อง Grokbot หรือ Slack | Acceptance Criteria ข้อ 5 |

## ภาคผนวก: ไฟล์ในรอบนี้

| ไฟล์ | เนื้อหา |
|---|---|
| [`history/report-spec-template.md`](history/report-spec-template.md) | Report Spec Template v0.1 (ใช้ใน Run #1) |
| [`history/report-spec-template-v0.2.md`](history/report-spec-template-v0.2.md) | Report Spec Template v0.2 แบบโครงเปิด |
| [`history/report-spec-template-v0.3.md`](history/report-spec-template-v0.3.md) | ส่วนที่เปลี่ยนใน v0.3 (Platform Spec และ Report Spec) |
| [`report-spec-structure.md`](report-spec-structure.md) | Report Spec Structure v0.3 (รวม v0.2 กับส่วนที่เปลี่ยนใน v0.3 เฉพาะส่วนรายงาน) |
| [`platform-spec-structure.md`](platform-spec-structure.md) | Platform Spec Structure v0.3 (ชั้นข้อมูลและตัวเช็คชั้น A) |
| [`history/example-input-returns-demo.md`](history/example-input-returns-demo.md) | Spec ที่ใช้เปิด Issue #4 |
| [`history/example-input-v0.2-returns-demo.md`](history/example-input-v0.2-returns-demo.md) | Spec ที่ใช้เปิด Issue #6 |
| [`platform-spec.md`](platform-spec.md) | Platform Spec ที่ใช้เปิด Issue #7 |
| [`report-spec.md`](report-spec.md) | Report Spec ที่ใช้เปิด Issue #9 |
| [Issue #7](https://github.com/Awannaphasch2016/quant-software-factory/issues/7), [Issue #9](https://github.com/Awannaphasch2016/quant-software-factory/issues/9) | Spec ที่ส่งจริงบน GitHub |
| [`e2e-run-evidence.md`](e2e-run-evidence.md), [`../../reports/demo_coop_rg_2026_10_v2/`](../../reports/demo_coop_rg_2026_10_v2/) | หลักฐาน End-to-End Run: ตารางเทียบ Expected Values 21 แถว และไฟล์ output 4 ไฟล์จาก commit `4e2129e` |
| `history/issue-a-project-setup.md` | Spec สร้างโครง repo (ไม่ได้ใช้ เพราะ merge PR #2 แทน) |
| [`history/spec-eval-method.md`](history/spec-eval-method.md) | วิธีวัดผล Spec และ Scorecard ของ Run #1 ถึง #4 |
| [`natural-writing-proposal.md`](natural-writing-proposal.md) | Natural Writing Proposal |
| skill `ai-slop-report-review` (อยู่ในเครื่องผู้จัดทำ ไม่ได้อยู่ใน repo) | Skill ตรวจ AI slop ฉบับฝ่าย Quant |
| [`progress-report-iteration-1.md`](progress-report-iteration-1.md) | รายงานนี้ |
