# Progress Report: สัปดาห์ 16–20 พ.ย. 2569

- ผู้จัดทำ: Inthanon Ratnavardhana
- ข้อมูล ณ 19 พ.ย. 2569
- รายละเอียดการออกแบบและหลักฐานอยู่ใน [Software Design](../4-software-design.md) ข้อ 2 ข้อกำหนดอยู่ใน [SRS](../3-srs.md) ข้อ 3.3

## 1. สรุป

สัปดาห์นี้ mentor ส่งงาน 2 ชุด ชุดแรกเป็น weekly report (15 พ.ย.) ที่ขอ Human Iteration 3 รอบ ชุดที่สองเป็น feedback 19 พ.ย. ที่กำหนดให้การออกแบบ architecture สำหรับ Private Data เป็นโจทย์หลัก งานที่เสร็จคือรอบ Private Data ซึ่งใช้ Agent Run 2 ครั้ง (Run #5 และ #6) โรงงานเขียน executor ที่รันรายงานกับ private database จำลองได้ โดยไม่เคยเห็นค่าใน database นั้น และส่งกลับแค่ผลตรวจที่ไม่มีตัวเลข เลขบัญชี หรือชื่อลูกค้า ส่วน Discord, Eve agent ตัวเดียว และต้นทุนต่อรายงาน ยังทำไม่ได้เพราะรอสิทธิ์

## 2. สถานะ Human Iteration ตาม weekly report

| Human Iteration | เป้าหมาย | สถานะ | หลักฐาน |
|---|---|---|---|
| 1 | สร้างรายงานจาก Report Spec ด้วยข้อมูลปลอม | สิ่งส่งมอบส่วนใหญ่มีแล้วจากสัปดาห์ก่อน: Issue ที่มี Report Spec, รายงานตรง Spec, PR ที่ merge แล้วและ Issue ปิดแล้ว, Delivery Document ส่วน A ที่ยังขาดคือการรันด้วย Eve agent ตัวเดียว (ใช้ Foreman) และต้นทุนต่อรายงาน รอ mentor ยืนยันว่านับรอบนี้ได้หรือไม่ | Issue #9 → PR #10 (Run #4) |
| 2 | ใช้งานผ่าน Discord | ยังไม่เริ่ม | รอ Discord server และสิทธิ์ Vercel |
| 3 | เชื่อมข้อมูลจริง | เปลี่ยนเป็นการออกแบบ architecture สำหรับ Private Data ตาม feedback 19 พ.ย. ทำ prototype กับ private database จำลองแล้ว ยังไม่ได้เชื่อมข้อมูลจริง | Run #5, Run #6 (ข้อ 3) |

## 3. Agent Run ในสัปดาห์นี้

| Run | Spec | Output | เวลาโรงงาน | ต้องอนุมัติกลางทาง | CI |
|---|---|---|---|---|---|
| #5 | Issue #12: private data boundary prototype | PR #13 merge แล้ว (`ab61d91`) | 15 นาที | ไม่ต้อง | run 44481298874 ผ่าน 3.10–3.13, 235 tests |
| #6 | Issue #15: แก้ design gap 3 ข้อจาก PR #13 | PR #16 merge แล้ว (`3a422c5`) | 11 นาที | ไม่ต้อง | run 44529767220 และ 44532003447 ผ่าน 3.10–3.13, 264 tests |

ทั้งสองรอบ reviewer ของโรงงานอนุมัติรอบแรก และไม่ชนเพดาน token ต่างจาก Report Spec ใน Run #4 ที่ต้องอนุมัติ 1 ครั้ง

## 4. ผลที่แสดงได้ (Demonstrated)

- Research 3 แนวทางที่ mentor ให้ศึกษา (Bring Data to Agent, Bring Agent to Data, แยกการคิดออกจากข้อมูล) บน Vercel/Eve, GitHub private repo กับ self-hosted runner และนโยบายของผู้ให้บริการโมเดล พร้อมคำตอบคำถาม 5 ข้อ (Software Design ข้อ 2.2–2.6)
- โรงงานเขียน `SqliteSource`, `make_private_db` และ `private_run` จาก Spec ที่ไม่มีข้อมูลจริง executor รันกับ database ที่คูณตัวเลข 7 เท่าและเปลี่ยนเลขบัญชีกับชื่อลูกค้า ได้รายงานถูกต้อง ตัวเลข 34 ตัวในรายงานเต็มไม่หลุดเข้า `result.json` เลย
- ปฏิเสธการเขียน output ลงใน repository (exit 2) ได้ทุกวิธีติดตั้ง ตั้งแต่ PR #16
- ผู้ตรวจรันซ้ำเองได้ตาม [Delivery Document](../5-delivery-document.md) ข้อ 5 ส่วน B ผู้จัดทำรันซ้ำใน clone ใหม่ของ `3a422c5` แล้วได้ผลตรงทุกขั้น

## 5. Gap ที่พบและการจัดประเภท

| Gap | ประเภท | การจัดการ |
|---|---|---|
| SRS เดิมไม่มีข้อกำหนดเรื่อง Private Data | Specification | เพิ่มกลุ่ม PD-01 ถึง PD-06 และ AC-07 ใน SRS v1.1 |
| `checks.json` เก็บค่า `expected` และ `actual` ซึ่งเป็นตัวเลขจริง จึงส่งกลับให้ agent ไม่ได้ | Design | เพิ่มตัวกรองที่สร้าง result จากชื่อตัวเช็คและผ่าน/ไม่ผ่านเท่านั้น (Run #5) |
| ตัวกันเขียนลง repo ทำงานเฉพาะการติดตั้งแบบ editable, leak check หยุดโดยไม่จำเป็นเมื่อเลขบัญชีสั้น, layer `"boundary"` ไม่ได้กำหนดไว้ | Design | แก้ใน Run #6 |
| leak check ไม่ค้นในชื่อ key ของ JSON และค่าจำนวนเต็ม | Design (ยอมรับไว้ใน Spec ของ Issue #15) | บันทึกเป็นข้อจำกัด แก้รอบหน้า |

ไม่ได้ลดข้อกำหนดข้อใดเพื่อให้ prototype ผ่าน

## 6. ปัญหาที่ยังเปิดและสิ่งที่รอ

| เรื่อง | ต้องการอะไร | จากใคร |
|---|---|---|
| Eve agent ตัวเดียวและต้นทุนต่อรายงาน | เข้า Team ของโรงงานบน Vercel ณ 19 พ.ย. บัญชีของผู้จัดทำยังไม่เห็น Team และไม่มีคำเชิญค้างอยู่ | mentor |
| Human Iteration 2 (Discord) | Discord server ของทีม และสิทธิ์ติดตั้ง bot | mentor |
| Human Iteration 1 | ยืนยันว่า Run #4 (PR #10) นับเป็นรอบนี้ได้หรือไม่ | mentor |
| Trusted zone จริง | เครื่องในเครือข่ายบริษัท สิทธิ์ database แบบอ่านอย่างเดียว และการอนุมัติให้ใช้ข้อมูลจริง | mentor และทีมเจ้าของข้อมูล |
| Policy เรื่องผู้ให้บริการโมเดล | ยืนยันว่าข้อมูลลูกค้าส่งให้ผู้ให้บริการภายนอกได้หรือไม่ | ฝ่ายที่ดูแล |

## 7. รอบถัดไป

1. เมื่อได้สิทธิ์ Vercel: deploy Eve agent ตัวเดียว รัน Report Spec เดิม และวัดต้นทุนต่อรายงาน
2. เมื่อได้ Discord server: ทำ Human Iteration 2 ให้สั่งงานและรับสถานะผ่าน Discord โดยรายงานที่มีข้อมูลจริงไม่ออกนอก Trusted zone
3. แก้ข้อจำกัดของ leak check (ค้นใน key และตรวจว่า result มีแค่ key ที่กำหนด)
