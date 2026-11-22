# Reporting Spec Structure for Software Factory: TOR

- โครงการ: Reusable Report Spec Structure สำหรับ Software Factory ของฝ่าย Quant
- ผู้จัดทำ: Inthanon Ratnavardhana
- Mentor: Anak Wannaphaschaiyong

| Document Version | Last Updated | Status |
|---|---|---|
| v1.3 | 22 พ.ย. 2569 | Current |

Change Log (ประวัติทุก version ดูได้จาก history ของไฟล์นี้ใน git)

| Version | วันที่ | สิ่งที่เปลี่ยน |
|---|---|---|
| v1.3 | 22 พ.ย. 2569 | เพิ่ม Report Agent (Eve agent ตัวเดียวสำหรับ Discord) ในสิ่งส่งมอบข้อ 4.1 และค่าใช้จ่ายของ agent ในข้อ 5.1 เลื่อนกำหนดส่งสัปดาห์ที่ 2 เป็น 23 พ.ย. 2569 ในข้อ 5.2 |
| v1.2 | 19 พ.ย. 2569 | เพิ่ม Private Data ในเกณฑ์ยอมรับข้อ 4.3 และกำหนดส่งงานสัปดาห์ที่ 2 (20 พ.ย. 2569) ในข้อ 5.2 ตามผลรีวิวเอกสาร |
| v1.1 | 19 พ.ย. 2569 | เพิ่มการทำงานกับ Private Data เป็นวัตถุประสงค์หลักตาม feedback ของ mentor วันที่ 19 พ.ย. 2569 (ข้อ 2.1–2.3, 3.1, 3.3, 5.1) เปลี่ยนช่องทางแชตเป็น Discord และเพิ่ม Delivery Document ในรายการเอกสาร |
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

ข้อมูลที่รายงานใช้เป็นข้อมูลลูกค้าจริงที่เก็บอยู่ใน database ภายในเครือข่ายบริษัท ถ้าจะให้ agent ช่วยงานนี้ได้จริง ต้องออกแบบให้ agent ทำงานกับข้อมูลนี้ได้โดยข้อมูลไม่รั่วออกนอก security boundary (mentor กำหนดเป็นโจทย์หลักเมื่อ 19 พ.ย. 2569)

พี่ Anak มี Software Factory (Eve / Foreman บน Vercel) ที่รับข้อกำหนดจาก GitHub Issue แล้วให้ agents เขียนโค้ด ทดสอบ ตรวจทาน และส่ง draft PR ให้คนตรวจ สิ่งที่ยังขาดคือโครงสร้างของข้อกำหนดที่ใครก็กรอกได้ แล้วโรงงานสร้างรายงานที่ตรงตามข้อกำหนดได้ทุกครั้ง

### 2.2 Project Purpose

ออกแบบโครงสร้าง Spec ที่นำกลับมาใช้ซ้ำได้ ใช้เป็น input ของ Software Factory เพื่อสร้างโค้ดที่ดึงข้อมูล จัดรายงาน และเช็คตัวเลข โดยตัวเลขทุกตัวมาจากข้อมูลต้นทางหรือโค้ดที่ผ่านการทดสอบ ข้อความที่ AI เขียนต้องไม่สร้างหรือแก้ตัวเลข และการ merge กับการส่งรายงานออกยังเป็นการตัดสินใจของคน โดย agent และบริการภายนอกต้องไม่ได้รับข้อมูลลูกค้า

### 2.3 Project Objectives

- ออกแบบ architecture ที่ให้ agent ทำงานกับ Private Data ได้โดยข้อมูลไม่รั่วออกนอก security boundary พร้อมหลักฐานที่ตรวจซ้ำได้ (วัตถุประสงค์หลัก)
- มี Spec Structure ที่รองรับรายงาน 3 ประเภทของฝ่าย Quant และใช้ซ้ำได้โดยไม่ต้องออกแบบใหม่ทุกครั้ง
- พิสูจน์ด้วยการรันจริงว่า Spec ที่กรอกตามโครงสร้างทำให้โรงงานสร้างรายงานที่ตรงตาม Spec ได้ พร้อมหลักฐานที่ตรวจสอบได้
- สั่งงานและรับรายงานผ่าน Discord ได้โดยไม่ต้องเข้าไปจัดการ repository เอง
- มีแนวทางให้ข้อความในรายงานอ่านเป็นธรรมชาติ ไม่เป็น AI slop โดยตัวเลขยังถูกต้อง

## 3. Project Scope

### 3.1 In Scope

- ศึกษาและเปรียบเทียบแนวทางให้ agent ทำงานกับ Private Data (Bring Data to Agent, Bring Agent to Data, แยกการคิดออกจากข้อมูล) และทำ prototype ที่ตรวจซ้ำได้
- ออกแบบและปรับ Spec Structure ผ่านวงรอบ specification, research และ prototype
- รายงาน 3 ประเภท: รายงานประจำเดือนของฝ่าย Quant, รายงานกำไรขาดทุนให้ลูกค้า, รายงานผลตอบแทนและรายการทางการลงทุน (capital gain, dividend, realized และ unrealized gain/loss)
- Spec ตัวอย่างที่กรอกแล้ว และการรันผ่าน Software Factory ตั้งแต่ Issue ถึง draft PR
- การเช็คตัวเลขในรายงาน ทั้งความครบและความสดของข้อมูล และความสอดคล้องกันของตัวเลขในรายงาน
- การเชื่อม Discord เพื่อสั่งสร้างรายงานและรับรายงานกลับ
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
| Private Data | agent และบริการภายนอกไม่ได้รับข้อมูลลูกค้า โค้ดรันกับข้อมูลจริงเฉพาะใน environment ที่บริษัทควบคุม และสิ่งที่ส่งกลับตรวจได้ว่าไม่มีข้อมูลรั่ว |
| ข้อมูล | ไม่มีข้อมูลลูกค้าจริงหรือโครงสร้างระบบภายในใน repository สาธารณะ |
| ช่องทาง | สั่งงานและรับผลผ่านแชตได้จากโทรศัพท์ |
| ภาษา | ข้อความในรายงานเหมาะกับผู้อ่าน ไม่เป็น AI slop |

ข้อกำหนดโดยละเอียดอยู่ใน SRS [2] ไม่กำหนดซ้ำใน TOR

## 4. Deliverables and Acceptance

### 4.1 Software and Spec Deliverables

Spec Structure (Report Spec Template), Spec ตัวอย่าง และผลการรันผ่านโรงงาน อธิบายและอ้างอิงหลักฐานใน Software Design [3] โค้ดที่โรงงานสร้างอยู่ใน repository `quant-software-factory` [4] ไม่ใช่สิ่งส่งมอบแยก

ตั้งแต่ Human Iteration 2 มีสิ่งส่งมอบที่เป็น software ที่ deploy แล้ว คือ Report Agent ที่รับ Spec ทาง Discord และส่งรายงานกลับ ตำแหน่งที่ deploy วิธีใช้ และวิธีทดสอบอยู่ใน Delivery Document

### 4.2 Documentation Deliverables

| เอกสาร | หน้าที่ |
|---|---|
| TOR | เหตุผล วัตถุประสงค์ ขอบเขต ข้อจำกัด และสิ่งส่งมอบ |
| Project Plan | วิธีดำเนินงาน ทรัพยากร และการติดตามความคืบหน้า |
| Software Requirements Specification | ข้อกำหนดและเกณฑ์ยอมรับ |
| Software Design | การออกแบบ ต้นแบบ และหลักฐาน |
| Delivery Document | สิ่งที่ส่งมอบ ที่ deploy การเข้าถึง วิธีใช้ และวิธีทดสอบ |
| Progress Report (รายรอบ, ภาคผนวก) | สิ่งที่ทำ ผลการทดลอง ปัญหาที่เหลือ |

การอ้างอิง ISO เป็นแนวทางสนับสนุน ไม่ใช่การรับรองความสอดคล้องทั้งหมด [6]

### 4.3 Acceptance Criteria

คาดหวังให้มีการออกแบบที่ให้ agent ทำงานกับ Private Data ได้โดยข้อมูลไม่รั่ว พร้อม prototype ที่ผู้ตรวจรันซ้ำได้ (วัตถุประสงค์หลักข้อ 2.3) Spec Structure ที่รองรับรายงาน 3 ประเภท Spec ตัวอย่างอย่างน้อย 1 ใบ การรันผ่านโรงงานที่สำเร็จอย่างน้อย 1 ครั้งพร้อม input และ output ให้ตรวจ การสั่งงานผ่านแชต และข้อเสนอ Natural Writing รายละเอียดเกณฑ์อยู่ใน SRS [2] การผ่านเกณฑ์ของต้นแบบไม่เท่ากับการอ้างว่า design freeze แล้ว

## 5. Constraints and Commitments

### 5.1 Technical and Organizational Constraints

- ใช้ Software Factory ของพี่ Anak (Eve / Foreman บน Vercel, GitHub App `eve-forman`) ไม่ได้ควบคุมการตั้งค่า เวอร์ชัน และ budget ของโรงงานเอง
- Repository `quant-software-factory` เป็นสาธารณะ ห้ามใส่ข้อมูลลูกค้าจริง ชื่อ server ชื่อ database ชื่อตาราง หรือ URL ภายใน ใช้ข้อมูลปลอมและชื่อกลางแทน
- ผู้จัดทำยังไม่มีสิทธิ์เข้าระบบข้อมูลของทีมโดยตรง ข้อมูลที่ใช้ต้องขอผ่านทีม
- ค่าใช้จ่ายของโรงงานและของ Report Agent อยู่ในบัญชีของพี่ Anak การรันแต่ละครั้งต้องคำนึงถึง quota
- ช่องทางแชตใช้ Discord ตามที่ทีม Quant ใช้
- Private Data อยู่ใน database ภายในเครือข่ายบริษัท และตัวโมเดลรันที่ผู้ให้บริการภายนอก การเข้าถึงข้อมูลจริงต้องได้รับอนุมัติจากผู้มีอำนาจก่อน

### 5.2 Timeline and Milestones

| รายการ | กรอบดำเนินงาน |
|---|---|
| เริ่มงาน | 9 พ.ย. 2569 |
| ส่งงานรอบแรก | 13 พ.ย. 2569 เวลา 18:00 น. |
| ส่งงานสัปดาห์ที่ 2 (Human Iteration 3 รอบตาม weekly report และ Private Data ตาม feedback 19 พ.ย. 2569) | เดิม 20 พ.ย. 2569 เลื่อนเป็น 23 พ.ย. 2569 เวลา 18:00 น. |
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
