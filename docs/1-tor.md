# Reporting Spec Structure for Software Factory: TOR

- โครงการ: Reusable Report Spec Structure สำหรับ Software Factory ของฝ่าย Quant
- ผู้จัดทำ: Inthanon Ratnavardhana
- Mentor: Anak Wannaphaschaiyong

| Document Version | Last Updated | Status |
|---|---|---|
| v1.0 | 19 พ.ย. 2569 | Current |

Change Log (ประวัติทุก version ดูได้จาก history ของไฟล์นี้ใน git)

| Version | วันที่ | สิ่งที่เปลี่ยน |
|---|---|---|
| v1.0 | 19 พ.ย. 2569 | ย้ายเข้า `docs/` ใน repo จากฉบับที่ส่งเมื่อ 13 พ.ย. 2569 เนื้อหาเดิม เพิ่มหัว version แก้ลิงก์ และเรียกเอกสารฉบับที่ 4 ว่า Software Design |

## สารบัญ

1. Document Information
2. Project Background and Objectives
3. Project Scope
4. Deliverables and Acceptance
5. Constraints and Commitments
6. References

## 1. Document Information

### 1.1 Document Identification

TOR นี้กำหนดเหตุผล วัตถุประสงค์ ขอบเขต และสิ่งส่งมอบของงานออกแบบโครงสร้าง Spec สำหรับสร้างรายงานผ่าน Software Factory ตลอดช่วงฝึกงาน ใช้ TOR ของโครงการ AI Harness / Software Factory ของพี่ Anak เป็นแม่แบบ [5] เขียนจากมุมมองเมื่อเริ่มงาน ผลจากต้นแบบรอบแรกอยู่ใน Software Design ไม่ได้ใช้เป็นหลักฐานว่าเคยตัดสินใจหรืออนุมัติไว้ก่อน

### 1.2 References

Project Plan, SRS และ Software Design เป็นเอกสารปลายทางที่ขยายวิธีทำงาน ข้อกำหนด และการออกแบบ [1][2][3] รายการอ้างอิงอยู่ท้ายเอกสาร

## 2. Project Background and Objectives

### 2.1 Project Background

งานรายงานของฝ่าย Quant ใช้เวลามาก เวลาส่วนใหญ่หมดไปกับการดึงข้อมูล จัดลงรายงาน และตรวจทาน ซึ่งวนซ้ำทุกรอบรายงาน ตัวเลขในรายงานลูกค้าคำนวณไว้แล้วโดย pipeline ของทีม (ยืนยันกับทีมระหว่าง Iteration 1) แต่การจัดรายงานและการเช็คตัวเลขยังทำซ้ำด้วยมือ

พี่ Anak มี Software Factory (Eve / Foreman บน Vercel) ที่รับข้อกำหนดจาก GitHub Issue แล้วให้ agents เขียนโค้ด ทดสอบ ตรวจทาน และส่ง draft PR ให้คนตรวจ สิ่งที่ยังขาดคือโครงสร้างของข้อกำหนดที่ใครก็กรอกได้ แล้วโรงงานสร้างรายงานที่ตรงตามข้อกำหนดได้ทุกครั้ง

### 2.2 Project Purpose

ออกแบบโครงสร้าง Spec ที่นำกลับมาใช้ซ้ำได้ ใช้เป็น input ของ Software Factory เพื่อสร้างโค้ดที่ดึงข้อมูล จัดรายงาน และเช็คตัวเลข โดยตัวเลขทุกตัวมาจากข้อมูลต้นทางหรือโค้ดที่ผ่านการทดสอบ ข้อความที่ AI เขียนต้องไม่สร้างหรือแก้ตัวเลข และการ merge กับการส่งรายงานออกยังเป็นการตัดสินใจของคน

### 2.3 Project Objectives

- มี Spec Structure ที่รองรับรายงาน 3 ประเภทของฝ่าย Quant และใช้ซ้ำได้โดยไม่ต้องออกแบบใหม่ทุกครั้ง
- พิสูจน์ด้วยการรันจริงว่า Spec ที่กรอกตามโครงสร้างทำให้โรงงานสร้างรายงานที่ตรงตาม Spec ได้ พร้อมหลักฐานที่ตรวจสอบได้
- สั่งงานโรงงานผ่านช่องทางแชต (Grokbot หรือ Slack) ได้โดยไม่ต้องเข้าไปจัดการ repository เอง
- มีแนวทางให้ข้อความในรายงานอ่านเป็นธรรมชาติ ไม่เป็น AI slop โดยตัวเลขยังถูกต้อง

## 3. Project Scope

### 3.1 In Scope

- ออกแบบและปรับ Spec Structure ผ่านวงรอบ specification, research และ prototype
- รายงาน 3 ประเภท: รายงานประจำเดือนของฝ่าย Quant, รายงานกำไรขาดทุนให้ลูกค้า, รายงานผลตอบแทนและรายการทางการลงทุน (capital gain, dividend, realized และ unrealized gain/loss)
- Spec ตัวอย่างที่กรอกแล้ว และการรันผ่าน Software Factory ตั้งแต่ Issue ถึง draft PR
- การเช็คตัวเลขในรายงาน ทั้งความครบและความสดของข้อมูล และความสอดคล้องกันของตัวเลขในรายงาน
- การเชื่อมช่องทางแชตเพื่อส่ง Spec เข้าโรงงานและรับรายงานกลับ
- ข้อเสนอเรื่อง Natural Writing
- การวัดผลของ Spec แต่ละรอบ และการบันทึกต้นทุนอ้างอิงต่อรอบเท่าที่ข้อมูลมี

### 3.2 Out of Scope

- การสร้าง Software Factory ใหม่ (ใช้ของพี่ Anak)
- การคำนวณตัวเลขใหม่แทน pipeline ของทีม
- การ merge, deploy และการส่งรายงานถึงลูกค้า ซึ่งเป็นการตัดสินใจของคน
- ข้อเสนอแนะหรือการคาดการณ์การลงทุนในรายงานลูกค้า
- backtest และการเฝ้าดู pipeline (เลื่อนไปรอบหลัง)
- รายงานเฉพาะ event ที่ทำนอกระบบ

### 3.3 High-Level Requirements

| กลุ่ม | ความคาดหวังระดับสูง |
|---|---|
| Spec | โครงสร้างเดียวรองรับรายงาน 3 ประเภท กรอกได้โดยคนที่ไม่ได้ออกแบบ และตรวจผลได้จาก Spec เอง |
| Factory | Spec ที่กรอกแล้วส่งเข้าโรงงานได้ และได้ draft PR ที่มีโค้ด ข้อมูลทดสอบ และรายงานตัวอย่าง |
| ความถูกต้อง | ตัวเลขทุกตัวโยงกลับข้อมูลต้นทางได้ และมีตัวเช็คอัตโนมัติก่อนถึงคน |
| ข้อมูล | ไม่มีข้อมูลลูกค้าจริงหรือโครงสร้างระบบภายในใน repository สาธารณะ |
| ช่องทาง | สั่งงานและรับผลผ่านแชตได้จากโทรศัพท์ |
| ภาษา | ข้อความในรายงานเหมาะกับผู้อ่าน ไม่เป็น AI slop |

ข้อกำหนดโดยละเอียดอยู่ใน SRS [2] ไม่กำหนดซ้ำใน TOR

## 4. Deliverables and Acceptance

### 4.1 Software and Spec Deliverables

Spec Structure (Report Spec Template), Spec ตัวอย่าง และผลการรันผ่านโรงงาน อธิบายและอ้างอิงหลักฐานใน Software Design [3] โค้ดที่โรงงานสร้างอยู่ใน repository `quant-software-factory` [4] ไม่ใช่สิ่งส่งมอบแยก

### 4.2 Documentation Deliverables

| เอกสาร | หน้าที่ |
|---|---|
| TOR | เหตุผล วัตถุประสงค์ ขอบเขต ข้อจำกัด และสิ่งส่งมอบ |
| Project Plan | วิธีดำเนินงาน ทรัพยากร และการติดตามความคืบหน้า |
| Software Requirements Specification | ข้อกำหนดและเกณฑ์ยอมรับ |
| Software Design | การออกแบบ ต้นแบบ และหลักฐาน |
| Progress Report (รายรอบ) | สิ่งที่ทำ ผลการทดลอง ปัญหาที่เหลือ |

การอ้างอิง ISO เป็นแนวทางสนับสนุน ไม่ใช่การรับรองความสอดคล้องทั้งหมด [6]

### 4.3 Acceptance Criteria

คาดหวังให้มี Spec Structure ที่รองรับรายงาน 3 ประเภท Spec ตัวอย่างอย่างน้อย 1 ใบ การรันผ่านโรงงานที่สำเร็จอย่างน้อย 1 ครั้งพร้อม input และ output ให้ตรวจ การสั่งงานผ่านแชต และข้อเสนอ Natural Writing รายละเอียดเกณฑ์อยู่ใน SRS [2] การผ่านเกณฑ์ของต้นแบบไม่เท่ากับการอ้างว่า design freeze แล้ว

## 5. Constraints and Commitments

### 5.1 Technical and Organizational Constraints

- ใช้ Software Factory ของพี่ Anak (Eve / Foreman บน Vercel, GitHub App `eve-forman`) ไม่ได้ควบคุมการตั้งค่า เวอร์ชัน และ budget ของโรงงานเอง
- Repository `quant-software-factory` เป็นสาธารณะ ห้ามใส่ข้อมูลลูกค้าจริง ชื่อ server ชื่อ database ชื่อตาราง หรือ URL ภายใน ใช้ข้อมูลปลอมและชื่อกลางแทน
- ผู้จัดทำยังไม่มีสิทธิ์เข้าระบบข้อมูลของทีมโดยตรง ข้อมูลที่ใช้ต้องขอผ่านทีม
- ค่าใช้จ่ายของโรงงานอยู่ในบัญชีของพี่ Anak การรันแต่ละครั้งต้องคำนึงถึง quota
- Subscription ของ Grokbot ยังไม่ทราบ ถ้าไม่มีให้ใช้ Slack แทนตาม requirement

### 5.2 Timeline and Milestones

| รายการ | กรอบดำเนินงาน |
|---|---|
| เริ่มงาน | 9 พ.ย. 2569 |
| ส่งงานรอบแรก | 13 พ.ย. 2569 เวลา 18:00 น. |
| สิ้นสุดช่วงฝึกงาน | 30 พ.ย. 2569 |
| จังหวะดำเนินงาน | specification, research และ prototype หนึ่งรอบต่อสัปดาห์ |
| Design freeze | พิจารณาจากหลักฐาน ไม่กำหนดวันหรือจำนวนรอบตายตัว |

### 5.3 Responsibilities and Dependencies

- ผู้จัดทำรับผิดชอบการออกแบบ Spec การศึกษา การรันต้นแบบ เอกสาร และการติดตามผล
- พี่ Anak เป็น mentor และเจ้าของ Software Factory
- ทีมเจ้าของ pipeline เป็นผู้ให้ข้อมูลเรื่องชุดข้อมูล นิยาม และตัวเช็คที่มีอยู่
- Factory agents เป็นเครื่องมือ ไม่ใช่บุคลากรเพิ่ม
- งานพึ่งพา GitHub, Software Factory บน Vercel และข้อมูลจากทีม

## 6. References

1. Project Plan: [`2-project-plan.md`](2-project-plan.md)
2. Software Requirements Specification: [`3-srs.md`](3-srs.md)
3. Software Design: [`4-software-design.md`](4-software-design.md)
4. Repository: https://github.com/Awannaphasch2016/quant-software-factory
5. TOR ของโครงการ AI Harness / Software Factory (Anak Wannaphaschaiyong)
6. ISO/IEC 29110-5-1-2:2025: https://www.iso.org/standard/82669.html
