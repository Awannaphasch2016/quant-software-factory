# Reporting Spec Structure for Software Factory: Project Plan

- โครงการ: Reusable Report Spec Structure สำหรับ Software Factory ของฝ่าย Quant
- ผู้จัดทำ: Inthanon Ratnavardhana

| Document Version | Last Updated | Status |
|---|---|---|
| v1.7 | 23 พ.ย. 2569 | Current |

Change Log (ประวัติทุก version ดูได้จาก history ของไฟล์นี้ใน git)

| Version | วันที่ | สิ่งที่เปลี่ยน |
|---|---|---|
| v1.7 | 23 พ.ย. 2569 | ผล review เอกสารและข้อ 5 ของ mentor: แยก Human Iteration (Deliverable) ออกจาก Agent Run ใน Scoreboard และ Progress Indicators ปรับนิยามในข้อ 2.2 สถานะ freeze ณ 23 พ.ย. เพิ่ม gap จากรายงาน Grid ในข้อ 2.4 และย่อตัวชี้วัดที่ซ้ำกับ SRS |
| v1.6 | 23 พ.ย. 2569 | รายงาน Grid สั่งผ่าน Discord ได้แล้ว (PR #35) เอาออกจากช่องว่างที่ยังเปิด |
| v1.5 | 23 พ.ย. 2569 | ปรับ Scoreboard และ Progress Indicators ณ 23 พ.ย.: เพิ่มรอบรายงาน Grid Trade Performance (Issue #23 → Run #7–#10) ที่ทำตาม feedback ต่อ PR #5 แก้สถานะ PR #19 เป็น merge แล้ว และเพิ่ม gap เรื่องขนาดงานต่อ Issue ของโรงงาน |
| v1.4 | 22 พ.ย. 2569 | ปรับ Scoreboard และ Progress Indicators ณ 22 พ.ย. (Human Iteration 2: Report Agent และ Discord) เพิ่มตัวอย่าง gap จากรอบนี้ เพิ่มเครื่องมือ (Vercel, Discord) และบทบาท Report Agent แก้ลิงก์ตามโครงสร้าง `docs/` ใหม่ |
| v1.3 | 19 พ.ย. 2569 | ใช้คำ Human Iteration และ Agent Run ตาม weekly report (ข้อ 2.2) ปรับ Scoreboard สัปดาห์ 16–20 พ.ย. ให้แสดงสถานะ Human Iteration 1–3 เพิ่มลิงก์ Progress Report สัปดาห์ 16–20 พ.ย. |
| v1.2 | 19 พ.ย. 2569 | เพิ่มการแก้ design gap ของ prototype (Issue #15 → PR #16) ใน Scoreboard และ Progress Indicators |
| v1.1 | 19 พ.ย. 2569 | เพิ่มรอบสัปดาห์ 16–20 พ.ย. 2569 (Private Data) ใน Scoreboard และ Progress Indicators เพิ่มตัวอย่าง gap จากรอบนี้ ปรับ design freeze และเพิ่มเอกสาร 5 ฉบับใน `docs/` |
| v1.0 | 19 พ.ย. 2569 | ย้ายเข้า `docs/` ใน repo จากฉบับที่ส่งเมื่อ 13 พ.ย. 2569 เนื้อหาเดิม เพิ่มหัว version แก้ลิงก์ และเรียกเอกสารฉบับที่ 4 ว่า Software Design |

## สารบัญ

1. Document Information
2. Development Methodology
3. Roles and Resources
4. Progress Monitoring and Control
5. References

## 1. Document Information

### 1.1 Document Identification

Project Plan อธิบายวิธีดำเนินงานให้สอดคล้องกับ TOR [1] ใช้วงรอบ specification, research และ prototype พร้อมหลักฐานเพื่อลดความไม่แน่นอน ใช้ Project Plan ของโครงการ AI Harness / Software Factory ของพี่ Anak เป็นแม่แบบ [5] ไม่สร้างประวัติการอนุมัติหรือผลการดำเนินงานย้อนหลัง

### 1.2 References

ข้อกำหนดอยู่ใน SRS [2] การออกแบบและหลักฐานอยู่ใน Software Design [3] ผลรายรอบอยู่ใน Progress Report [4] ปรับใช้ ISO/IEC 29110-5-1-2:2025 โดยเฉพาะ WP.10 Project Plan และ WP.16 Software Design เป็นแนวทาง ไม่ใช่การรับรองความสอดคล้องทั้งหมด [6]

## 2. Development Methodology

### 2.1 Development Lifecycle

ใช้ iterative, prototype-driven development เริ่มจากโครงสร้าง Spec เบื้องต้น แล้วปรับจากผลการรันกับโรงงานจริง ลำดับการอ่าน TOR, Project Plan, SRS, Software Design ไม่ได้บังคับให้ทำแบบ waterfall

ช่วงงานเริ่ม 9 พ.ย. 2569 จังหวะทำงานหนึ่งรอบต่อสัปดาห์ สิ้นสุดช่วงฝึกงาน 30 พ.ย. 2569 ความพร้อม design freeze พิจารณาจากหลักฐาน ไม่กำหนดวันหรือจำนวนรอบตายตัว

### 2.2 Specification–Research–Prototype Cycle

| กิจกรรม | ข้อมูลเข้าและงาน | ผลที่ต้องบันทึก |
|---|---|---|
| Specification | TOR, requirement_1, ผลจากรอบก่อน; ร่างหรือปรับ Template และ Spec ตัวอย่าง | Template, Spec ตัวอย่าง, คำถามที่ต้องตรวจ |
| Research | การทำงานของโรงงาน, รายงานตัวอย่างของทีม, แหล่งข้อมูลของทีม, เรื่อง AI slop | ทางเลือก ข้อจำกัด และเหตุผลที่เลือกทดสอบ |
| Prototype | เปิด Issue ตาม Spec ให้โรงงานรัน แล้วตรวจ Output เทียบ Expected Values | Scorecard, gap, ข้อสรุป และสิ่งที่จะปรับรอบหน้า |

คำที่ใช้ในเอกสารนี้ตาม weekly report ของ mentor: **Human Iteration** (เรียกสั้นว่า "รอบ") คือรอบงานที่ผู้จัดทำวางแผน ตัดสินใจ และตรวจผลเอง มีเป้าหมายและสิ่งส่งมอบชัดเจน **Agent Run** (Run #1, #2, ...) คือการสั่งโรงงานทำงาน 1 ครั้งจาก Issue 1 ใบ การสั่ง Report Agent ระหว่างทดสอบก็เป็นการใช้ agent ภายในรอบเช่นกัน Human Iteration หนึ่งรอบมีได้หลาย Agent Run และวัดความสำเร็จจาก Deliverable ไม่ใช่จำนวน Run "Iteration 1" ในเอกสารสัปดาห์ 9–13 พ.ย. หมายถึงงานทั้งสัปดาห์นั้น ส่วน Human Iteration 1–3 ของสัปดาห์ 16–23 พ.ย. เป็นรอบตาม weekly report

รอบหนึ่งเสร็จเมื่อครบทั้งสามกิจกรรมและบันทึกผล ไม่จำเป็นต้องผ่านทุกครั้ง หากได้ข้อค้นพบที่ใช้ปรับต่อได้ ความถี่รายสัปดาห์เป็นวิธีเฉพาะโครงการ ไม่ใช่ workflow ที่ ISO บังคับ

### 2.3 Prototype Feasibility Validation

ต้นแบบใช้ตรวจว่า Spec Structure ทำให้โรงงานสร้างรายงานที่ตรง Spec ได้จริง ไม่ใช่แค่สาธิตว่าโรงงานทำงาน แต่ละ run วัดด้วย Scorecard ใน [`history/spec-eval-method.md`](history/spec-eval-method.md) [4]:

- ผลลัพธ์: Expected Values ที่ตรง, Acceptance Criteria ของ Issue, `checks.json`, CI
- กระบวนการ: ผล Classify, จำนวนจุดที่โรงงานต้องตัดสินใจเอง, รอบที่ reviewer ส่งกลับ, เวลา, ต้นทุน
- คุณภาพ: ข้อความบรรยายตาม 6 องค์ประกอบของ AI slop, การทำตรงขอบเขต

จำนวนจุดที่โรงงานต้องตัดสินใจเองใช้วัดความชัดของ Spec ทุกจุดคือช่องโหว่ที่ควรแก้ใน Template

ผลผ่านยืนยันเฉพาะสิ่งที่ทดสอบ ใช้ข้อมูลปลอมจึงไม่ยืนยันความถูกต้องกับข้อมูลจริง ผลไม่ผ่านต้องนำไปวิเคราะห์ gap

### 2.4 Gap Classification and Resolution

| ประเภท | ความหมาย | แนวทางแก้ | ตัวอย่างที่พบ |
|---|---|---|---|
| Specification gap | Spec ขาด ไม่ชัด ขัดกันเอง หรือสมมติฐานไม่ตรงกับงานจริง | ปรับ Template หรือ Spec แล้วรันใหม่ | Spec ให้คำนวณเองทั้งที่ pipeline คำนวณไว้แล้ว; ไม่ได้ระบุ base branch; Writing Rules ขัดกับตัวเช็ค B8; SRS เดิมไม่มีข้อกำหนดเรื่อง Private Data (เพิ่มกลุ่ม PD ใน v1.1); ช่อง Data Sources ผูกกับ fixture จึงใช้ Spec เดิมกับข้อมูลจริงไม่ได้ (แก้ใน Spec Structure v0.4); Spec Structure ไม่รองรับ layout ของ PDF และสูตรที่คำนวณต่อจากข้อมูล Spec ของรายงาน Grid จึงเขียนหัวข้อเอง และรายงานนี้คำนวณค่าบางตัวเองซึ่งอาจซ้ำกับ pipeline (SRS FR-01, FR-03) |
| Design gap | Spec ใช้ได้ แต่วิธีแตกงานหรือขนาดงานทำให้ต้นแบบไปไม่ถึง | ปรับวิธีแตก Spec หรือขนาด แล้วทดสอบซ้ำ | Spec ชนเพดาน token ของโรงงานใน Run #1 และ #2 แก้บางส่วนด้วยการแยก Platform Spec กับ Report Spec (Run #3 จบเอง, Run #4 ต้องอนุมัติ 1 ครั้ง); `checks.json` เดิมมีค่าจริงจึงส่งกลับให้ agent ไม่ได้ (แก้ด้วยตัวกรอง result ใน PR #13); Report Agent ส่งรายงานให้โมเดลพิมพ์ซ้ำ และเปิดไฟล์ Spec ที่แนบไม่ได้ (แก้ใน PR #19); Spec ของรายงาน Grid ทั้งฉบับเกิน budget ต่อ session ของโรงงาน (แตกเป็น 4 Issue); PR #28 มีคำว่า "do not close #23" ทำให้ GitHub ปิด #23 ก่อนเวลา (เปิดใหม่และเลี่ยงคำนี้) |

ไม่ลดข้อกำหนดเพื่อให้ต้นแบบดูเหมือนผ่าน เช่น ไม่ลบแถวใน Expected Values ที่ไม่ผ่าน และไม่ตัดตัวเช็คออกเพื่อให้ Spec เล็กลง

### 2.5 Iterative Specification and Design Refinement

นำผล Scorecard และ gap กลับไปปรับ Template แต่ละรุ่นเก็บเป็นไฟล์แยก (v0.1–v0.3 อยู่ใน [`history/`](history/)) เพื่อให้ตรวจย้อนได้ว่า run ไหนใช้รุ่นใด ฉบับใช้งานล่าสุด (v0.4) อยู่ใน [`spec-structure/`](spec-structure/) เก็บหลักฐานผ่าน GitHub (Issue, PR, CI, commit SHA)

พิจารณาข้อจำกัดที่ไม่ใช่เทคนิคควบคู่ด้วย ได้แก่ สิทธิ์เข้าถึงข้อมูลของทีม, quota และค่าใช้จ่ายของโรงงานที่เป็นของพี่ Anak และการที่ repository เป็นสาธารณะ

### 2.6 Design Freeze Criteria

ใช้หลักฐานพิจารณาร่วมกันสองด้าน:

1. TOR alignment: Spec Structure รองรับรายงาน 3 ประเภท และตอบวัตถุประสงค์ใน TOR
2. Implementation feasibility: Spec ที่กรอกตาม Template ผ่านโรงงานได้จนถึง Output ที่ตรง Spec โดยไม่ต้องมีคนช่วยกลางทาง และทำงานกับข้อมูลจริงได้โดยข้อมูลไม่รั่ว

สถานะ ณ 23 พ.ย. 2569: ยังไม่พร้อม freeze ด้าน 1 พิสูจน์ได้ 1 ประเภท (รวมรายงาน Grid ที่เป็นรูปแบบของทีม) และ Spec Structure ยังไม่รองรับรายงาน PDF ด้าน 2 boundary ของ Private Data พิสูจน์ได้ในระดับ prototype Report Agent ส่งรายงานทั้ง Markdown และ PDF ผ่าน Discord ได้โดยโมเดลไม่เห็นตัวเลข และ Spec ใหญ่ต้องแตกเป็นหลาย Issue แต่ทั้งหมดยังใช้ข้อมูลปลอม ยังไม่ได้ทดสอบกับ database และเครือข่ายจริงของบริษัท

## 3. Roles and Resources

### 3.1 Project Roles and Responsibilities

| บทบาท | ผู้รับผิดชอบ | หน้าที่ |
|---|---|---|
| ผู้จัดทำ | Inthanon Ratnavardhana | ออกแบบ Spec, ศึกษา, รันต้นแบบ, ตรวจผล, merge, เอกสาร |
| Mentor และเจ้าของ Software Factory | Anak Wannaphaschaiyong | ให้คำแนะนำ, ดูแลโรงงานและ budget, ตรวจงาน |
| เจ้าของข้อมูลและ pipeline | ทีมในฝ่าย Quant | ให้ข้อมูลเรื่องชุดข้อมูล นิยาม และตัวเช็คที่มีอยู่ |
| Factory agents | Foreman (classifier, analyst, implementer, reviewer) | เครื่องมือดำเนินงาน ไม่ใช่สมาชิกทีม มี review อิสระก่อนส่ง PR |
| Report Agent | Eve agent ตัวเดียวใน `report-agent/` | รับ Spec ทาง Discord แล้วรันโค้ดรายงานที่ merge แล้ว ไม่เขียนโค้ด |

### 3.2 Tools and Technology

| เครื่องมือ | การใช้งาน |
|---|---|
| GitHub repository `quant-software-factory` | workspace, Issue (Spec), branch, draft PR, ประวัติ |
| GitHub App `eve-forman` | เชื่อม repository กับโรงงาน |
| Foreman บน Vercel | ประสาน agents |
| GitHub Actions | CI: ruff, ruff format, mypy strict, pytest บน Python 3.10–3.13 และ typecheck กับ test ของ `report-agent/` บน Node 26 |
| Vercel (Team ของพี่ Anak) | deploy Report Agent, Vercel Sandbox, AI Gateway (log token ที่ใช้คิดต้นทุน), Vercel Connect (token ของ Discord bot) |
| Discord | ช่องทางเดียวที่ผู้ใช้สั่งงาน Report Agent (คำสั่ง `/ask`) |
| Claude Code และ `gh` CLI | ร่างเอกสาร, ตรวจ fixture, เปิด Issue, เก็บหลักฐาน |
| Skill `ai-slop-report-review` | ตรวจข้อความบรรยาย |

ไม่ผูกมัดจำนวน agents หรือโมเดลของโรงงาน เพราะเป็นการตั้งค่าของพี่ Anak

### 3.3 Resource Requirements

- ค่าใช้จ่ายของโรงงานและของ Report Agent อยู่ในบัญชีของพี่ Anak ไม่กำหนดงบในแผน ตัวเลขต่อ run และต่อรายงานใน Software Design ข้อ 10 เป็นจุดอ้างอิง ผู้จัดทำขออนุญาตก่อน deploy หรือสร้าง resource ทุกครั้ง
- ต้องขอสิทธิ์หรือข้อมูลตัวอย่างจากทีมก่อนต่อกับข้อมูลจริง
- การรันแต่ละครั้งใช้ quota ของโรงงาน จึงรันเฉพาะเมื่อ Spec ผ่านการตรวจของผู้ใช้แล้ว

## 4. Progress Monitoring and Control

### 4.1 Lead Measure

ทำ specification, research และ prototype ให้ครบหนึ่งรอบต่อสัปดาห์ พร้อมบันทึก Scorecard, gap และข้อสรุป ทบทวนรายสัปดาห์ว่าเสร็จอะไร พบอะไร ติดอะไร และรอบถัดไปทำอะไร

### 4.2 Scoreboard

| สัปดาห์ | เป้า | Human Iteration ที่เสร็จ (Deliverable) | Agent Run ภายในรอบ | หลักฐาน |
|---|---|---|---|---|
| 16–23 พ.ย. 2569 (กำหนดส่งเลื่อนเป็น 23 พ.ย. 18:00) | 3 ตาม weekly report | 4 รอบ: <br>(1) HI1: Issue ที่มี Spec → PR ที่มีรายงานจากข้อมูลปลอม → merge → ปิด Issue และ Eve agent ตัวเดียวสร้างรายงานที่ตรง `report.md` ทุก byte พร้อมค่าโมเดลต่อรายงาน <br>(2) HI2: สั่ง `/ask` ใน Discord แล้วได้รายงานกลับ (ทดสอบใน server ทดสอบ ยังไม่ได้ทดสอบใน server ของทีม) <br>(3) Private Data แทน HI3 ตาม feedback 19 พ.ย.: prototype ที่ข้อมูลไม่รั่ว และแบบเส้นทางไป executor ในบริษัท (ยังไม่ได้เชื่อมข้อมูลจริง) <br>(4) รายงาน Grid ตามรูปแบบของทีม (feedback ต่อ PR #5): Issue #23 → PDF 5 หน้า → merge → ปิด #23 และสั่งผ่าน Discord ได้ | HI1: Run #4 (จาก Iteration 1) และการรัน Report Agent บน Vercel <br>HI2: การรัน Report Agent ระหว่างแก้ 3 ปัญหา <br>Private Data: Run #5, #6 <br>รายงาน Grid: Run #7–#10 (Issue #23 ค้าง 1 ครั้ง) | PR #10, #13, #16, #19, #26, #28, #30, #32, #35, Software Design ข้อ 2, 4.4, 5.5, 10, [Progress Report 16–23 พ.ย.](progress/progress-report-2026-11-16.md) |
| 9–13 พ.ย. 2569 | 1 | 3 รอบ ทุกรอบมี Deliverable คือ Template รุ่นใหม่ + Spec ที่กรอก + ผลรันพร้อม gap: <br>(1) Template v0.1 → รายงานตรง Expected Values (สำเร็จ) <br>(2) Template v0.2 → ค้างที่ implement (บันทึก gap) <br>(3) Template v0.3 → data layer และรายงานที่ merge แล้ว | (1) Run #1 <br>(2) Run #2 <br>(3) Run #3, #4 | Progress Report Iteration 1, Issue #4 → PR #5, Issue #6, Issue #7 → PR #8, Issue #9 → PR #10 |

### 4.3 Progress Indicators

| ตัวชี้วัด | ค่า ณ 23 พ.ย. 2569 |
|---|---|
| Human Iteration ที่เสร็จ | 7 รอบ (3 รอบในสัปดาห์ 9–13 พ.ย. และ 4 รอบในสัปดาห์ 16–23 พ.ย.) นับจาก Deliverable ในข้อ 4.2 ไม่ได้นับจาก Agent Run (ทั้งหมด 10 Run ของโรงงาน) |
| ความไม่แน่นอนที่คลี่คลาย | โรงงานสร้างรายงาน PDF ตามรูปแบบของทีมได้จาก Spec โดยโค้ดคำนวณทุกค่าก่อนวาด และสร้างซ้ำได้ตรงทุกไบต์ (PR #32); Spec ใหญ่ต้องแตกเป็น Issue ที่จบใน session เดียว (Run #7–#10); Eve agent ตัวเดียวรันโค้ดรายงานใน Vercel Sandbox ได้และส่งรายงานเข้า Discord โดยโมเดลไม่เห็นตัวเลข ค่าโมเดลประมาณ $0.014 ต่อรายงาน (PR #19); agent เขียนโค้ดที่อ่าน private database ได้โดยไม่เห็นข้อมูลจริง และ result ที่ส่งกลับไม่มีค่ารั่ว (PR #13); ตัวกันเขียนลง repo ใช้ได้ทุกวิธีติดตั้ง และเลขบัญชีสั้นไม่ทำให้ leak check หยุดโดยไม่จำเป็น (PR #16); โรงงานรับ Spec ได้จริง; ตัวเลขคำนวณไว้แล้วใน pipeline; base branch แก้ด้วย merge PR #2; Spec ที่ไม่คำนวณใหม่ (Data Mapping) ได้รายงานที่ตรงกับ Spec (Run #4); Report Spec ใช้ data layer จาก Platform Spec ได้โดยไม่ต้องแก้ (Run #3 → #4) |
| ข้อกำหนดที่ตรวจสอบแล้ว | สถานะรายข้อดูใน SRS ข้อ 3–5 สรุป: กลุ่ม PD Demonstrated ระดับ prototype, HR-05 และ HR-06 Demonstrated กับข้อมูลปลอม, FR-01 มี gap จากรายงาน Grid, FR-02 ได้ 1 จาก 3 ประเภท, FR-10 ผ่านบางส่วน |
| ช่องว่างสำคัญที่ยังเปิด | Spec Structure ยังไม่รองรับ layout ของ PDF, สูตรของรายงาน Grid (Expected Volume, NAV Vol, Cost Change %) ยังไม่ได้ยืนยันกับทีม Quant, โรงงานไม่ทำต่อหลัง approve เมื่อชน token guardrail (#23, #27), ทดสอบ Discord ใน server ของทีม, ค่า Sandbox และ Function ต่อรายงาน (AI Gateway แสดง $0 และยังไม่มี billing data), เส้นทางจาก Discord ไป executor ในบริษัท (Software Design ข้อ 2.9) และ policy เรื่องส่งรายงานเข้า Discord, Trusted zone จริงในเครือข่ายบริษัทและสิทธิ์ database แบบอ่านอย่างเดียว, policy เรื่องผู้ให้บริการโมเดล, leak check ที่ไม่ค้นในชื่อ key และค่าจำนวนเต็ม, FR-10 (Report Spec ยังต้องอนุมัติ token 1 ครั้ง), FR-02 (อีก 2 ประเภทรายงาน), HR-05 กับข้อมูลจริง, schema ที่ยังไม่รองรับฝาก/ถอนหุ้นและรูปแบบปันผลของข้อมูลจริง, spec gap 3 จุดจาก Run #4, นิยามข้อมูลจริง |
| ความพร้อม freeze | ยังไม่พร้อม (ข้อ 2.6) |

ประเด็นเปิดอาจเพิ่มเมื่อพบปัญหาใหม่ จึงไม่ใช้จำนวนประเด็นที่ลดลงอย่างเดียวแทนความก้าวหน้า

## 5. References

1. TOR: [`1-tor.md`](1-tor.md)
2. SRS: [`3-srs.md`](3-srs.md)
3. Software Design: [`4-software-design.md`](4-software-design.md)
4. Progress Report และ Scorecard: [`progress/progress-report-iteration-1.md`](progress/progress-report-iteration-1.md), [`progress/progress-report-2026-11-16.md`](progress/progress-report-2026-11-16.md), [`history/spec-eval-method.md`](history/spec-eval-method.md); หลักฐานรวม: [`README.md`](README.md)
5. Project Plan ของโครงการ AI Harness / Software Factory (Anak Wannaphaschaiyong)
6. ISO/IEC 29110-5-1-2:2025: https://www.iso.org/standard/82669.html
