# Spec Eval Method (แบบ A: ทดสอบ Spec)

วิธีวัดว่า Report Spec Template ใช้งานได้จริงหรือไม่ โดย**ล็อกโรงงานไว้แล้วเปลี่ยน Spec** ตามลำดับความสำคัญสูงสุดของ requirement_1: "พิสูจน์ให้ได้ว่า Spec Structure ที่ออกแบบสามารถใช้งานได้จริง"

- สถานะ: Iteration 1 มี 4 run (Issue #4, #6, #7, #9) สำเร็จถึง Output 3 run (#1, #3, #4)
- แบบ B (ล็อก Spec แล้วปรับ implementer) อยู่นอกขอบเขตรอบนี้ (*Intended*)

## 1. คำถามที่ eval ต้องตอบ

| # | คำถาม | วิธีตอบ |
|---|---|---|
| Q1 | Spec ที่กรอกตาม Template ทำให้โรงงานสร้างรายงานที่ถูกต้องได้ไหม | Expected Values ผ่าน 100% และ Acceptance Criteria ผ่านครบ |
| Q2 | Template ใช้ซ้ำกับรายงานทั้ง 3 ประเภทได้ไหม | รัน Spec อย่างน้อย 1 ใบต่อประเภท |
| Q3 | Section ไหนของ Template จำเป็นจริง | ตัด section ออกทีละส่วนแล้วเทียบ Scorecard (ablation) |
| Q4 | Spec ขนาดเท่าไรที่โรงงานทำจบได้ในรอบเดียว | รัน Spec เล็ก กลาง ใหญ่ แล้วยืนยันกติกาการแตก Spec |

## 2. สิ่งที่ล็อกไว้และสิ่งที่เปลี่ยน

| ล็อกไว้ | เปลี่ยน |
|---|---|
| โรงงาน: Foreman ที่ deploy อยู่ของพี่ Anak | เนื้อหา Spec |
| repo เป้าหมาย: `quant-software-factory` | ประเภทรายงาน |
| Output Contract (report.md, report.json, narrative.md, checks.json) | section ที่ใส่ในบางรอบ (สำหรับ Q3) |
| Grader และ Scorecard | ขนาด Spec (สำหรับ Q4) |

ข้อควรระวัง: ไม่ได้ควบคุมเวอร์ชันของ Foreman เอง ถ้าพี่ Anak deploy ใหม่ระหว่างรอบ ผลอาจเปลี่ยนเพราะโรงงานเปลี่ยน ไม่ใช่เพราะ Spec จึงต้องบันทึกวันเวลาของแต่ละรอบไว้

## 3. Scorecard

### 3.1 Quantitative: ผลลัพธ์

| ID | ตัวชี้วัด | วิธีวัด | เกณฑ์ผ่าน |
|---|---|---|---|
| R1 | Expected Values ที่ผ่าน | รันคำสั่งใน Output Contract บน branch ของ PR แล้วเทียบ `report.json` | 100% |
| R2 | Acceptance Criteria ที่ผ่าน | ไล่ checklist ทีละข้อจาก PR | ครบทุกข้อ |
| R3 | ตัวตรวจใน `checks.json` | อ่านไฟล์ | ผ่านทุกข้อ |
| R4 | CI | GitHub Actions ของ PR | ผ่านทุก Python version |
| R5 | ตัวเลขในข้อความบรรยายตรงกับ JSON | test ใน PR และสุ่มตรวจด้วยมือ | 100% |

### 3.2 Quantitative: กระบวนการ

| ID | ตัวชี้วัด | วิธีวัด | ทิศทางที่ดี |
|---|---|---|---|
| P1 | ผลของ Classifier | คอมเมนต์แรกของ bot | ผ่านโดยไม่โดน `needs_clarification` |
| P2 | จุดที่โรงงานต้องตัดสินใจเอง | นับจากคอมเมนต์ Analysis | น้อยลง |
| P3 | จำนวนรอบที่ reviewer ส่งกลับ | คอมเมนต์ใน Issue (0–2) | น้อยลง |
| P4 | เวลาจากติด label ถึงเปิด PR | timestamp ของ event | สั้นลง (ใช้อ้างอิงเท่านั้น) |
| P5 | ค่าใช้จ่ายต่อ run | ขอจากพี่ Anak (Vercel) | ค่าอ้างอิงของ 1 run ไม่ใช่การคาดการณ์ |

### 3.3 Qualitative

| ID | ตัวชี้วัด | วิธีวัด | เกณฑ์ |
|---|---|---|---|
| Q-a | ความเป็นธรรมชาติของข้อความบรรยาย | rubric 1–5 (ดู Natural Writing Proposal) + นับคำต้องห้าม | ≥ 4 และไม่มีคำต้องห้าม |
| Q-b | ทำตรงขอบเขต | อ่าน diff เทียบกับ Out of Scope | ไม่มีงานเกินหรือขาด |
| Q-c | ความเหมาะสมของการตัดสินใจเองใน P2 | อ่านทีละจุด ว่าจุดนั้นควรเพิ่มเข้า Template ไหม | บันทึกเป็น gap |

## 4. วิธีจัดประเภท gap หลังแต่ละ run

ใช้หลักของพี่ Anak:

- **Specification gap:** Spec ไม่ชัด ไม่ครบ หรือขัดกับ TOR ให้แก้ Template หรือ Example Input
  - ตัวอย่าง: โรงงานต้องตัดสินใจเองในจุดที่ Spec ควรกำหนดไว้ (P2)
- **Design gap:** Spec ชัดแล้ว แต่ผลลัพธ์ยังไม่ผ่าน ให้แก้การออกแบบ เช่น ขนาด Spec, การแตกงาน, หรือขอให้ปรับโรงงาน
- **ห้ามลดเกณฑ์เพื่อให้ผ่าน** เช่น ห้ามลบแถวใน Expected Values ที่ไม่ผ่าน

## 5. แผนการรัน

| Run | Spec | ตอบคำถาม | สถานะ |
|---|---|---|---|
| #1 | `returns_transactions` บัญชีเดียว 1 เดือน (Issue #4) | Q1 | สำเร็จ (PR #5) |
| #2 | `returns_transactions` ด้วย Template v0.2 (ข้อมูลที่คำนวณแล้ว) Issue #6 | Q1, Q4 | ค้างที่ขั้น implement ปิด Issue แล้ว |
| #3 | Platform Spec v0.3: data access + ตัวเช็คชั้น A (Issue #7) | Q4 | สำเร็จ (PR #8 merge แล้ว) |
| #4 | Report Spec v0.3: `returns_transactions` (Issue #9) | Q1, Q4 | สำเร็จ (PR #10 merge แล้ว) |
| #5 | Report Spec `client_pnl` แบบย่อ หลายกลยุทธ์ ใช้ data layer เดิม | Q2 | *Intended* |
| #6 | `monthly_team` (ต้องมีข้อมูล NAV series) | Q2 | *Intended* รอข้อมูล |
| #7 | Spec #4 ที่ตัด Expected Values ออก | Q3 | *Intended* ถามพี่ Anak ก่อน เพราะใช้ quota ของโรงงาน |
| #8 | Spec #4 ที่รวม PDF เข้าไปด้วย (ใหญ่ขึ้น) | Q4 | *Intended* |

## 6. บันทึกผลราย run

### Run #1: Issue #4, `returns_transactions`

- Issue: https://github.com/Awannaphasch2016/quant-software-factory/issues/4
- Spec: [`example-input-returns-demo.md`](example-input-returns-demo.md) (Template v0.1)
- ติด label `factory`: 2026-11-12 03:27 UTC (โดย Josh-Bear)

| ID | ผล | หลักฐาน |
|---|---|---|
| P1 | ✅ ผ่าน: "the spec is complete enough to build as written" และตรวจ Expected Values กับ fixture แล้วว่าทุกแถวถูกต้อง | คอมเมนต์ bot 2026-11-12 03:28:39 UTC |
| P2 | 5 จุด: (1) base branch, (2) รูปแบบ % ใน JSON, (3) ค่าที่ไม่มีเป็น `null`, (4) ข้อมูลหัวรายงานอยู่ในโค้ด, (5) ลบไฟล์เก่าเมื่อตัวตรวจไม่ผ่าน | คอมเมนต์ 03:28:39 และ 03:34:56 UTC |
| P3 | 0 รอบ: reviewer approve รอบแรกโดยไม่มี blocking issue (มีข้อเสนอแนะที่ไม่ block 4 ข้อ) | คอมเมนต์ 03:59:03 UTC และ PR #5 |
| P4 | 31 นาที 45 วินาที (label 03:27:08 → PR 03:58:53) รวมเวลาที่หยุดรออนุมัติ token ประมาณ 11 นาที | timestamp ของ event และ PR |
| P5 | ยังไม่ทราบต้นทุนจริง (อยู่ในบัญชีของพี่ Anak) ที่ทราบคือขั้น implement ใช้ output token ครบเพดาน 100K ต่อ session และต้องให้คนอนุมัติ budget เพิ่ม 1 ครั้ง | คอมเมนต์ 03:43:52 UTC และ 03:54:49 UTC |
| R1 | ✅ 100%: "Every value in your Expected Values table matches exactly" (test 36 กรณี) และตรวจซ้ำด้วยตาเทียบกับ `report.md` แล้ว | PR #5, `reports/demo_coop_rg_2026_10/report.md` |
| R2 | ✅ 13/13 ข้อ (ตามที่ reviewer ติ๊ก) | PR #5 body |
| R3 | ✅ 24/24 checks ผ่าน, difference 0.00 | PR #5, `checks.json` |
| R4 | ✅ GitHub Actions ผ่านทั้ง Python 3.10, 3.11, 3.12 และ 3.13 (122 tests) | CI run 43151748082 |
| R5 | ✅ มี test ตรวจว่าตัวเลขในข้อความบรรยายอยู่ใน JSON | PR #5 |
| Q-a | ยังไม่ได้ให้คะแนน rubric พบ 2 จุดที่ภาษาแข็ง: "a realized capital gain of -3,037.00 THB" (ควรเป็น "a realized loss of 3,037.00 THB") และ "Deposits of" ใช้รูปพหูพจน์ทั้งที่มีรายการเดียว | `narrative.md` และคอมเมนต์ของ reviewer |
| Q-b | ทำตามขอบเขต และเข้มงวดกว่า Spec ในการตรวจ input (เช่น ไม่รับค่าธรรมเนียมบนรายการปันผล) ไม่แตะไฟล์ที่ห้ามแตะ | PR #5 ส่วน Deviations |

**สรุป Run #1:** สำเร็จตั้งแต่ Input ถึง Output (draft PR #5) ตาม Acceptance Criteria ข้อ 3 ของ requirement_1 และ CI บน GitHub ผ่านแล้ว ยังไม่ได้ merge PR #5 (การ merge เป็นการตัดสินใจของคน)

Gap ที่พบแล้ว (ทั้งหมดเป็น specification gap):

| จุดที่พบ | ผลกระทบ | แก้ใน Template v0.2 |
|---|---|---|
| ไม่ได้ระบุ base branch แต่ `main` มีแค่ README โค้ดอยู่บน branch ของ PR #2 | PR ของเราซ้อนอยู่บน PR #2 ถ้า PR #2 ไม่ merge ต้อง rebase | เพิ่มช่อง "Base branch" ใน Constraints |
| ข้อมูลหัวรายงานไม่ได้เป็น input | ใช้กับลูกค้าหรือเดือนอื่นต้องแก้โค้ด ซึ่งขัดกับเป้าหมาย reusable | เพิ่มไฟล์ `report_meta` เป็น input บังคับ |
| ไม่ได้กำหนดรูปแบบตัวเลขใน JSON | โรงงานเลือกเก็บ `%` ไว้ใน string ซึ่งใช้ได้ แต่ควรเป็นมาตรฐานเดียวกันทุกรายงาน | กำหนดรูปแบบใน Output Contract มาตรฐาน |
| ไม่ได้กำหนดค่าว่าง | โรงงานเลือก `null` | กำหนดไว้ใน Output Contract มาตรฐาน |
| "one row per instrument" ไม่ชัดว่ารวมหุ้นที่ขายหมดแล้วไหม | holdings ไม่แสดงหุ้นที่ขายหมด ใน fixture นี้ไม่มีผลเพราะไม่มีหุ้นที่ขายหมด | ระบุใน block `holdings` ว่าแสดงเฉพาะที่ volume ปลายงวด > 0 และเพิ่มกรณีขายหมดใน fixture |
| Writing Rules ไม่ได้กำหนดวิธีเขียนค่าติดลบหรือเอกพจน์/พหูพจน์ | ข้อความถูกต้องแต่ภาษาแข็ง | เพิ่มกติกาใน Natural Writing Proposal เช่น "ขาดทุน X" แทน "กำไร −X" |
| ไม่ได้กำหนดว่าเงินที่อยู่นอกนิยาม (เช่น ค่าธรรมเนียมบนรายการปันผล) ต้องทำอย่างไร | โรงงานเลือกปฏิเสธ input ซึ่งปลอดภัย แต่เป็นการตัดสินใจเอง | ระบุใน Metric Definitions ว่ารายการที่ไม่อยู่ในนิยามต้องถูกปฏิเสธ |

Design gap ที่พบ:

| จุดที่พบ | ผลกระทบ | แนวทาง |
|---|---|---|
| Spec ขนาด 8 block ใช้ output token ครบ 100K ตั้งแต่ขั้น implement | ต้องให้คนอนุมัติกลางทาง ถ้าไม่มีคนอยู่ งานจะค้าง | ลดกติกาการแตก Spec เป็นประมาณ 5–6 block ต่อใบ หรือแยก "คำนวณ" กับ "แสดงผล" เป็น 2 Spec ผลวัดซ้ำอยู่ใน Run #3 และ #4 |

### Run #2: Issue #6, `returns_transactions` ด้วย Template v0.2

- Issue: https://github.com/Awannaphasch2016/quant-software-factory/issues/6
- Spec: [`example-input-v0.2-returns-demo.md`](example-input-v0.2-returns-demo.md) (Template v0.2)
- ก่อนรัน merge PR #2 เข้า `main` แล้ว (commit `e6a0963`) เพื่อให้ Issue แตก branch จาก `main` ได้
- ติด label `factory`: 2026-11-12 09:24:32 UTC (โดย Josh-Bear)

| ID | ผล | หลักฐาน |
|---|---|---|
| P1 | ✅ ผ่าน: "the spec is clear enough to build as written" และยืนยันว่า "the new branch will be cut fresh from `main` and won't build on #5" | คอมเมนต์ 09:26:22 UTC |
| P2 | 5 จุด: (1) รูปแบบวันที่ (2) B4 เทียบกับแถวไหน (3) B8 นับตัวเลขที่เป็นวันที่และจำนวนด้วย โรงงานจึงเลี่ยงวันที่และเขียนจำนวนเป็นคำ (4) B8 กับค่าติดลบที่เขียนเป็น "loss" (5) สถานะของชั้น B เมื่อชั้น A ไม่ผ่าน และคำถามที่ไม่ block 2 ข้อ: A2 fail เมื่อเดือนไม่มีเงินเข้าออก, เงินถอนควรแสดงเป็นค่าลบหรือไม่ | คอมเมนต์ 09:26:22 และ 09:32:07 UTC |
| P3 | ไม่มีผล ยังไม่ถึงขั้น review | |
| P4 | ไม่มีผล ไม่มี PR | |
| P5 | ชนเพดาน output token ที่ 44.9K ต่อ session (Run #1 ชนที่ 100K) ตอบ Approve 2 ครั้ง (12 พ.ย. 09:41:51 UTC และ 13 พ.ย. 06:17 UTC) โรงงานไม่ตอบสนอง ไม่มีคอมเมนต์ ไม่มี branch | คอมเมนต์ 09:39:44 UTC และคอมเมนต์ Approve ทั้งสองครั้ง |
| R1–R5, Q-a, Q-b | ไม่มีผล | |

**สรุป Run #2:** Template v0.2 ผ่าน Classify และ Analysis และแก้ gap เรื่อง base branch ได้ แต่ไม่ถึง Output สาเหตุที่โรงงานหยุดยังไม่ทราบ ต้องให้พี่ Anak ดู log ฝั่ง Vercel

Gap ที่พบใน Run #2:

| ประเภท | จุดที่พบ | แก้ใน v0.3 |
|---|---|---|
| Specification | A2 บังคับให้ทุกชุดข้อมูลมีอย่างน้อย 1 แถว ทำให้เดือนที่ไม่มีเงินเข้าออก fail | ให้ระบุชุดข้อมูลที่ว่างได้ (เช่น `cash_flow`) |
| Specification | Writing Rules ให้เขียนค่าติดลบเป็น "loss" (ค่าบวก) แต่ B8 ต้องการตัวเลขตรงกับ JSON (ค่าลบ) จึงขัดกันเอง | B8 ยอมรับค่าสัมบูรณ์ของตัวเลขที่ JSON เก็บเป็นลบ |
| Specification | B8 ไม่ได้บอกว่าวันที่และจำนวนนับเป็นตัวเลขหรือไม่ | ระบุว่า B8 ตรวจเฉพาะจำนวนเงินและ % |
| Specification | ไม่ได้บอกเครื่องหมายของเงินถอนในตาราง | ระบุใน block `transactions` |
| Design | Spec 6 block + ตัวเช็ค 11 ข้อ ชนเพดาน token ตั้งแต่ต้นขั้น implement | แตก Spec ตามชั้นงาน: data + ชั้น A / รายงาน + ชั้น B / narrative |

### Run #3: Issue #7, Platform Spec v0.3

- Issue: https://github.com/Awannaphasch2016/quant-software-factory/issues/7
- Spec: [`../specs/platform-spec.md`](../specs/platform-spec.md) (Issue: [#7](https://github.com/Awannaphasch2016/quant-software-factory/issues/7))
- ติด label `factory`: 2026-11-13 06:58:00 UTC (โดย Josh-Bear)

| ID | ผล | หลักฐาน |
|---|---|---|
| P1 | ✅ ผ่าน: "clear enough to build as written" และชี้จุดผิดใน Spec 1 จุด (เมื่อไม่มี `holdings_daily` ไม่ต้องรายงาน A1 ว่า not run เพราะ A1 อ่านแค่ `nav_daily`) | คอมเมนต์ 06:59:22 UTC |
| P2 | 5 จุด: (1) ชื่อตัวเช็ค (2) ข้อความใน `expected`/`actual` (3) แถวที่วันที่อ่านไม่ได้ให้เก็บไว้แล้วรายงานใน A3 (4) A3 ไม่ตรวจ `realized_pl` บนแถวที่ไม่ใช่ SELL (5) A3 ไม่ตรวจว่า `cash_flow.amount` เป็นบวก | คอมเมนต์ 06:59:22 และ 07:02:59 UTC |
| P3 | 0 รอบ: reviewer approve โดยไม่มี blocking issue | คอมเมนต์ 07:10:43 UTC |
| P4 | 12 นาที 34 วินาที (label 06:58:00 → PR 07:10:34) ไม่หยุดที่เพดาน token | timestamp ของ event และ PR |
| P5 | ไม่ทราบต้นทุนจริง ไม่ชนเพดาน output token | |
| R1 | ✅ 11/11 แถวมี test | PR #8 |
| R2 | ✅ 10/10 ข้อ (ข้อ CI ผ่านหลังเปิด PR) | PR #8 body, CI run 43383851475 |
| R3 | ✅ 14/14 checks ผ่าน | `reports/demo_coop_rg_2026_10_v2/checks.json` ที่ commit `9455ea3` |
| R4 | ✅ ผ่าน Python 3.10–3.13 (60 tests) และ CI ของ `main` หลัง merge ผ่าน | CI run 43383851475, 43384155137 |
| R5, Q-a | ไม่เกี่ยว ใบนี้ไม่มีข้อความบรรยาย | |
| Q-b | ทำตามขอบเขต ไม่แตะ `risk.py` และ test เดิม | PR #8 |

**สรุป Run #3:** Platform Spec จบได้ใน session เดียวโดยไม่ต้องมีคนอนุมัติกลางทาง merge แล้วเมื่อ 07:13:08 UTC (commit `9455ea3`)

### Run #4: Issue #9, Report Spec v0.3

- Issue: https://github.com/Awannaphasch2016/quant-software-factory/issues/9
- Spec: [`../specs/report-spec.md`](../specs/report-spec.md) (Issue: [#9](https://github.com/Awannaphasch2016/quant-software-factory/issues/9))
- ติด label `factory`: 2026-11-13 07:16:19 UTC (โดย Josh-Bear)

| ID | ผล | หลักฐาน |
|---|---|---|
| P1 | ✅ ผ่าน: "clear enough to build as written" แตก branch จาก `main` และใช้ data layer เดิมโดยไม่แก้ | คอมเมนต์ 07:17:34 UTC |
| P2 | 5 จุด: (1) ช่วงเวลาคิดจากเดือนของ as-of (2) เพิ่มตัวเช็ค B0 เมื่อค่าที่ต้อง map หายไป (3) แยก B7 เป็น 2 ข้อ (4) ไม่เขียนตัวเลข "NAV เปลี่ยนไปเท่าไร" เพราะไม่มีในชุดข้อมูล (5) แก้ test เดิม 2 ตัวให้เทียบเฉพาะผลชั้น A ใน `checks.json` | คอมเมนต์ 07:22:36 UTC และ PR #10 body |
| P3 | 0 รอบ: reviewer approve โดยไม่มี blocking issue | คอมเมนต์ 08:42:00 UTC และ PR #10 |
| P4 | 85 นาที 32 วินาที (label 07:16:19 → PR 08:41:51) ในจำนวนนี้ 66 นาที 24 วินาทีเป็นเวลารอคนอนุมัติ เวลาที่โรงงานทำงานประมาณ 19 นาที | timestamp ของ event และ PR |
| P5 | ชนเพดาน output token 100K ต่อ session หลัง implement เสร็จ (07:32:06 UTC) อนุมัติ 1 ครั้ง (08:38:30 UTC) แล้วทำต่อจนได้ PR | คอมเมนต์ 07:32:06 และ 08:38:30 UTC |
| R1 | ✅ 21/21 แถว ผมรันคำสั่งใน Output Contract เองแล้วเทียบ `report.md` ทีละแถว | `reports/demo_coop_rg_2026_10_v2/report.md` |
| R2 | ✅ 12/12 ข้อ (ข้อ CI ผ่านหลังเปิด PR) | PR #10 body |
| R3 | ✅ 29/29 checks ผ่าน (ชั้น A 14, ชั้น B และการเขียน 15) | `checks.json` |
| R4 | ✅ ผ่าน Python 3.10–3.13 และ CI ของ `main` หลัง merge ผ่าน โรงงานรัน test ในเครื่องตัวเองบน 3.14 อย่างเดียว | CI run 43395249810, 43395497605 |
| R5 | ✅ ตัวเช็ค B8 ผ่าน และข้อความมีวลี "a realized loss of 3,037.00 THB" และ "a deposit of 50,000.00 THB" ตาม Expected Values | `narrative.md`, `checks.json` |
| Q-a | ยังไม่ได้ให้คะแนน rubric ปัญหาค่าติดลบและพหูพจน์จาก Run #1 หายไป แต่ข้อความยังเล่าตามตาราง เช่น ย่อหน้าที่ 3 ไล่ unrealized P/L ทีละหุ้นแล้วบอกยอดรวมซ้ำ | `narrative.md` |
| Q-b | ทำตามขอบเขต ไม่แตะ data layer, fixture, `risk.py` และ `pyproject.toml` | PR #10 body และ diff |
| รันซ้ำ | ✅ ผมรันซ้ำในเครื่อง ทั้ง 4 ไฟล์ตรงกับที่ commit ทุก byte, pytest ผ่าน 149 กรณี | รันเมื่อ 13 พ.ย. ประมาณ 08:45 UTC บน commit `7398e04` |

**สรุป Run #4:** สำเร็จตั้งแต่ Input ถึง Output ตาม Acceptance Criteria ข้อ 3 ของ requirement_1 ด้วย Report Spec 1 ใบ merge แล้วเมื่อ 08:43:45 UTC (commit `4e2129e`)

Gap ที่พบใน Run #3 และ #4:

| ประเภท | จุดที่พบ | แนวทาง |
|---|---|---|
| Specification | Platform Spec ผูก A1 กับ `holdings_daily` ผิด | แก้ใน Platform Spec ถ้าใช้ซ้ำ |
| Specification | Writing Rules สั่งให้พูดถึง "การเปลี่ยนแปลงของ NAV" แต่ไม่มีตัวเลขนี้ในชุดข้อมูล | v0.4: เพิ่ม opening NAV ใน Data Mapping |
| Specification | ไม่ได้บอกว่าช่วงเวลาของรายงานคิดจากอะไร และไม่ได้ตรวจ opening date | v0.4: ระบุใน Report Definition |
| Specification | ตัวเช็ค B0 ไม่มีใน Spec | v0.4: เพิ่มเป็นตัวเช็คมาตรฐาน |
| Design | Report Spec ยังชนเพดาน 100K ก่อนขั้น review | ถามพี่ Anak เรื่องเพดาน หรือลดขนาด Report Spec แล้ววัดซ้ำ |
