# Reporting Spec Structure for Software Factory: Project Plan

- โครงการ: Reusable Report Spec Structure สำหรับ Software Factory ของฝ่าย Quant
- ผู้จัดทำ: Inthanon Ratnavardhana

| Document Version | Last Updated | Status |
|---|---|---|
| v1.1 | 19 พ.ย. 2569 | Current |

Change Log (ประวัติทุก version ดูได้จาก history ของไฟล์นี้ใน git)

| Version | วันที่ | สิ่งที่เปลี่ยน |
|---|---|---|
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

รอบหนึ่งเสร็จเมื่อครบทั้งสามกิจกรรมและบันทึกผล ไม่จำเป็นต้องผ่านทุกครั้ง หากได้ข้อค้นพบที่ใช้ปรับต่อได้ ความถี่รายสัปดาห์เป็นวิธีเฉพาะโครงการ ไม่ใช่ workflow ที่ ISO บังคับ

### 2.3 Prototype Feasibility Validation

ต้นแบบใช้ตรวจว่า Spec Structure ทำให้โรงงานสร้างรายงานที่ตรง Spec ได้จริง ไม่ใช่แค่สาธิตว่าโรงงานทำงาน แต่ละ run วัดด้วย Scorecard ใน [`appendix/history/spec-eval-method.md`](appendix/history/spec-eval-method.md) [4]:

- ผลลัพธ์: Expected Values ที่ตรง, Acceptance Criteria ของ Issue, `checks.json`, CI
- กระบวนการ: ผล Classify, จำนวนจุดที่โรงงานต้องตัดสินใจเอง, รอบที่ reviewer ส่งกลับ, เวลา, ต้นทุน
- คุณภาพ: ข้อความบรรยายตาม 6 องค์ประกอบของ AI slop, การทำตรงขอบเขต

จำนวนจุดที่โรงงานต้องตัดสินใจเองใช้วัดความชัดของ Spec ทุกจุดคือช่องโหว่ที่ควรแก้ใน Template

ผลผ่านยืนยันเฉพาะสิ่งที่ทดสอบ ใช้ข้อมูลปลอมจึงไม่ยืนยันความถูกต้องกับข้อมูลจริง ผลไม่ผ่านต้องนำไปวิเคราะห์ gap

### 2.4 Gap Classification and Resolution

| ประเภท | ความหมาย | แนวทางแก้ | ตัวอย่างจาก Iteration 1 |
|---|---|---|---|
| Specification gap | Spec ขาด ไม่ชัด ขัดกันเอง หรือสมมติฐานไม่ตรงกับงานจริง | ปรับ Template หรือ Spec แล้วรันใหม่ | Spec ให้คำนวณเองทั้งที่ pipeline คำนวณไว้แล้ว; ไม่ได้ระบุ base branch; Writing Rules ขัดกับตัวเช็ค B8; SRS เดิมไม่มีข้อกำหนดเรื่อง Private Data (เพิ่มกลุ่ม PD ใน v1.1) |
| Design gap | Spec ใช้ได้ แต่วิธีแตกงานหรือขนาดงานทำให้ต้นแบบไปไม่ถึง | ปรับวิธีแตก Spec หรือขนาด แล้วทดสอบซ้ำ | Spec ชนเพดาน token ของโรงงานใน Run #1 และ #2 แก้บางส่วนด้วยการแยก Platform Spec กับ Report Spec (Run #3 จบเอง, Run #4 ต้องอนุมัติ 1 ครั้ง); `checks.json` เดิมมีค่าจริงจึงส่งกลับให้ agent ไม่ได้ (แก้ด้วยตัวกรอง result ใน PR #13) |

ไม่ลดข้อกำหนดเพื่อให้ต้นแบบดูเหมือนผ่าน เช่น ไม่ลบแถวใน Expected Values ที่ไม่ผ่าน และไม่ตัดตัวเช็คออกเพื่อให้ Spec เล็กลง

### 2.5 Iterative Specification and Design Refinement

นำผล Scorecard และ gap กลับไปปรับ Template แต่ละรุ่นเก็บเป็นไฟล์แยก (v0.1, v0.2 และส่วนที่เปลี่ยนใน v0.3 อยู่ใน [`appendix/history/`](appendix/history/)) เพื่อให้ตรวจย้อนได้ว่า run ไหนใช้รุ่นใด ฉบับใช้งานล่าสุดอยู่ใน [`appendix/`](appendix/) เก็บหลักฐานผ่าน GitHub (Issue, PR, CI, commit SHA)

พิจารณาข้อจำกัดที่ไม่ใช่เทคนิคควบคู่ด้วย ได้แก่ สิทธิ์เข้าถึงข้อมูลของทีม, quota และค่าใช้จ่ายของโรงงานที่เป็นของพี่ Anak และการที่ repository เป็นสาธารณะ

### 2.6 Design Freeze Criteria

ใช้หลักฐานพิจารณาร่วมกันสองด้าน:

1. TOR alignment: Spec Structure รองรับรายงาน 3 ประเภท และตอบวัตถุประสงค์ใน TOR
2. Implementation feasibility: Spec ที่กรอกตาม Template ผ่านโรงงานได้จนถึง Output ที่ตรง Spec โดยไม่ต้องมีคนช่วยกลางทาง และทำงานกับข้อมูลจริงได้โดยข้อมูลไม่รั่ว

สถานะ ณ 19 พ.ย. 2569: ยังไม่พร้อม freeze ด้าน 1 พิสูจน์ได้ 1 ประเภท ด้าน 2 boundary ของ Private Data พิสูจน์ได้ในระดับ prototype แต่ยังไม่ได้ทดสอบกับ database และเครือข่ายจริงของบริษัท

## 3. Roles and Resources

### 3.1 Project Roles and Responsibilities

| บทบาท | ผู้รับผิดชอบ | หน้าที่ |
|---|---|---|
| ผู้จัดทำ | Inthanon Ratnavardhana | ออกแบบ Spec, ศึกษา, รันต้นแบบ, ตรวจผล, merge, เอกสาร |
| Mentor และเจ้าของ Software Factory | Anak Wannaphaschaiyong | ให้คำแนะนำ, ดูแลโรงงานและ budget, ตรวจงาน |
| เจ้าของข้อมูลและ pipeline | ทีมในฝ่าย Quant | ให้ข้อมูลเรื่องชุดข้อมูล นิยาม และตัวเช็คที่มีอยู่ |
| Factory agents | Foreman (classifier, analyst, implementer, reviewer) | เครื่องมือดำเนินงาน ไม่ใช่สมาชิกทีม มี review อิสระก่อนส่ง PR |

### 3.2 Tools and Technology

| เครื่องมือ | การใช้งาน |
|---|---|
| GitHub repository `quant-software-factory` | workspace, Issue (Spec), branch, draft PR, ประวัติ |
| GitHub App `eve-forman` | เชื่อม repository กับโรงงาน |
| Foreman บน Vercel | ประสาน agents |
| GitHub Actions | CI: ruff, ruff format, mypy strict, pytest บน Python 3.10–3.13 |
| Claude Code และ `gh` CLI | ร่างเอกสาร, ตรวจ fixture, เปิด Issue, เก็บหลักฐาน |
| Skill `ai-slop-report-review` | ตรวจข้อความบรรยาย |

ไม่ผูกมัดจำนวน agents หรือโมเดลของโรงงาน เพราะเป็นการตั้งค่าของพี่ Anak

### 3.3 Resource Requirements

- ค่าใช้จ่ายของโรงงานอยู่ในบัญชีของพี่ Anak ไม่กำหนดงบในแผน ตัวเลขต่อ run ใน Software Design เป็นจุดอ้างอิง
- ต้องขอสิทธิ์หรือข้อมูลตัวอย่างจากทีมก่อนต่อกับข้อมูลจริง
- การรันแต่ละครั้งใช้ quota ของโรงงาน จึงรันเฉพาะเมื่อ Spec ผ่านการตรวจของผู้ใช้แล้ว

## 4. Progress Monitoring and Control

### 4.1 Lead Measure

ทำ specification, research และ prototype ให้ครบหนึ่งรอบต่อสัปดาห์ พร้อมบันทึก Scorecard, gap และข้อสรุป ทบทวนรายสัปดาห์ว่าเสร็จอะไร พบอะไร ติดอะไร และรอบถัดไปทำอะไร

### 4.2 Scoreboard

| สัปดาห์ | เป้า | รอบที่เสร็จ | หลักฐาน |
|---|---|---|---|
| 16–20 พ.ย. 2569 | 1 | 1 (ณ 19 พ.ย.): Spec กลุ่ม PD → Research 3 แนวทางบน Vercel/Eve, GitHub self-hosted runner, นโยบายผู้ให้บริการโมเดล → Prototype แนวทาง C (Issue #12 → PR #13 merge แล้ว) → gap ใหม่ 3 จุด | Software Design ข้อ 2, SRS ข้อ 3.3, Issue #12, PR #13 |
| 9–13 พ.ย. 2569 | 1 | 3: (1) Template v0.1 → Run #1 สำเร็จ → gap (2) Template v0.2 → Run #2 ค้างที่ implement → gap (3) Template v0.3 → Run #3 และ #4 สำเร็จและ merge แล้ว → gap ใหม่ 3 จุด | Progress Report Iteration 1, Issue #4 → PR #5, Issue #6, Issue #7 → PR #8, Issue #9 → PR #10 |

### 4.3 Progress Indicators

| ตัวชี้วัด | ค่า ณ 19 พ.ย. 2569 |
|---|---|
| รอบที่เสร็จ | 4 (3 รอบในสัปดาห์ 9–13 พ.ย. และ 1 รอบในสัปดาห์ 16–20 พ.ย.) |
| ความไม่แน่นอนที่คลี่คลาย | agent เขียนโค้ดที่อ่าน private database ได้โดยไม่เห็นข้อมูลจริง และ result ที่ส่งกลับไม่มีค่ารั่ว (PR #13); โรงงานรับ Spec ได้จริง; ตัวเลขคำนวณไว้แล้วใน pipeline; base branch แก้ด้วย merge PR #2; Spec ที่ไม่คำนวณใหม่ (Data Mapping) ได้รายงานที่ตรงกับ Spec (Run #4); Report Spec ใช้ data layer จาก Platform Spec ได้โดยไม่ต้องแก้ (Run #3 → #4) |
| ข้อกำหนดที่ตรวจสอบแล้ว | Demonstrated ในระดับ prototype: PD-01 ถึง PD-04, PD-05 และ PD-06 บางส่วน; Demonstrated: HR-01 ถึง HR-04, FR-01, FR-03 ถึง FR-09, NFR-01 ถึง NFR-06, NFR-08 (FR-04 เฉพาะ fixture) ผ่านบางส่วน: FR-02 (1 จาก 3 ประเภท), FR-10 (ดู SRS) |
| ช่องว่างสำคัญที่ยังเปิด | Trusted zone จริงในเครือข่ายบริษัทและสิทธิ์ database แบบอ่านอย่างเดียว, policy เรื่องผู้ให้บริการโมเดล, ตัวกันเขียนลง repo ที่ทำงานเฉพาะการติดตั้งแบบ editable, FR-10 (Report Spec ยังต้องอนุมัติ token 1 ครั้ง), FR-02 (อีก 2 ประเภทรายงาน), HR-05 (ช่องทางแชต), spec gap ใหม่ 3 จุดจาก Run #4, นิยามข้อมูลจริง |
| ความพร้อม freeze | ยังไม่พร้อม (ข้อ 2.6) |

ประเด็นเปิดอาจเพิ่มเมื่อพบปัญหาใหม่ จึงไม่ใช้จำนวนประเด็นที่ลดลงอย่างเดียวแทนความก้าวหน้า

## 5. References

1. TOR: [`1-tor.md`](1-tor.md)
2. SRS: [`3-srs.md`](3-srs.md)
3. Software Design: [`4-software-design.md`](4-software-design.md)
4. Progress Report และ Scorecard: [`appendix/progress-report-iteration-1.md`](appendix/progress-report-iteration-1.md), [`appendix/history/spec-eval-method.md`](appendix/history/spec-eval-method.md); หลักฐานรวม: [`appendix/`](appendix/)
5. Project Plan ของโครงการ AI Harness / Software Factory (Anak Wannaphaschaiyong)
6. ISO/IEC 29110-5-1-2:2025: https://www.iso.org/standard/82669.html
