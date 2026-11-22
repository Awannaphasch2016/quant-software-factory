# Progress Report: สัปดาห์ 16–23 พ.ย. 2569

- ผู้จัดทำ: Inthanon Ratnavardhana
- ข้อมูล ณ 22 พ.ย. 2569 (ฉบับ 19 พ.ย. ดูได้จาก history ของไฟล์นี้ใน git)
- กำหนดส่งเลื่อนจาก 20 พ.ย. เป็น 23 พ.ย. 2569 เวลา 18:00 น.
- รายละเอียดการออกแบบและหลักฐานอยู่ใน [Software Design](../4-software-design.md) ข้อ 2, 4.4 และ 10 ข้อกำหนดอยู่ใน [SRS](../3-srs.md) ข้อ 3

## 1. สรุป

สัปดาห์นี้ mentor ส่งงานมา 2 ชุด ชุดแรกคือ weekly report วันที่ 15 พ.ย. ที่ขอ Human Iteration 3 รอบ ชุดที่สองคือ feedback วันที่ 19 พ.ย. ที่ให้การออกแบบ architecture สำหรับ Private Data เป็นโจทย์หลัก

- **รอบ Private Data (19 พ.ย.):** โรงงานเขียน executor ที่รันรายงานกับ private database จำลองได้โดยไม่เคยเห็นค่าข้างใน และส่งกลับแค่ผลตรวจ
- **Human Iteration 2 (22 พ.ย.):** deploy Report Agent ซึ่งเป็น Eve agent ตัวเดียว ไว้ใน Team Vercel ของพี่ Anak ผู้ใช้ส่ง Spec ทาง Discord ด้วยคำสั่ง `/ask` แล้วได้รายงานกลับในช่องเดิม ตัว tool เป็นผู้ส่งรายงาน ส่วนโมเดลเห็นแค่สถานะ ไฟล์รายงานที่ได้ใน Discord ตรงกับ `report.md` ใน repo ทุก byte
- **ค่าโมเดลต่อรายงาน:** ประมาณ $0.014 คิดจาก token จริงตามราคาในรายการโมเดล ยังไม่ได้วัดค่า Sandbox และ Function
- **ข้อมูลจริง:** ยังไม่ได้เชื่อม เส้นทางจาก Discord ไปถึง executor ในบริษัทออกแบบไว้แล้ว (Software Design ข้อ 2.9) แต่ยังต้องได้คำตอบเรื่องสิทธิ์และ policy

## 2. สถานะ Human Iteration ตาม weekly report

| Human Iteration | เป้าหมาย | สถานะ | หลักฐาน |
|---|---|---|---|
| 1 | สร้างรายงานจาก Report Spec ด้วยข้อมูลปลอม | มีสิ่งส่งมอบครบแล้ว: <br>- Issue ที่มี Report Spec, PR ที่ merge แล้ว และ Issue ที่ปิดแล้ว (Run #4) <br>- Eve agent ตัวเดียวรับ Spec แล้วได้รายงานที่ตรง Spec <br>- ต้นทุนค่าโมเดลต่อรายงาน (ค่า Sandbox ยังวัดไม่ได้) | Issue #9 → PR #10, PR #19, Software Design ข้อ 10.1 |
| 2 | ใช้งานผ่าน Discord เป็นช่องทางเดียว | ทำงานได้ใน server ทดสอบ ทั้งแบบพิมพ์ Spec และแบบแนบไฟล์ <br>รอ merge PR #19 และยังไม่ได้ทดสอบใน server ของทีม | PR #19, Delivery Document ส่วน C |
| 3 | เชื่อมข้อมูลจริง | ตาม feedback 19 พ.ย. เปลี่ยนเป็นการออกแบบ architecture สำหรับ Private Data <br>- prototype กับ private database จำลอง (Run #5, #6) <br>- ออกแบบเส้นทางจาก Discord ไป executor ในบริษัท (Intended) <br>ยังไม่ได้เชื่อมข้อมูลจริง | Run #5, Run #6, Software Design ข้อ 2.9 |

## 3. งานในสัปดาห์นี้

### 3.1 Agent Run ของโรงงาน

| Run | Spec | Output | เวลาโรงงาน | ต้องอนุมัติกลางทาง | CI |
|---|---|---|---|---|---|
| #5 | Issue #12: private data boundary prototype | PR #13 merge แล้ว (`ab61d91`) | 15 นาที | ไม่ต้อง | run 44481298874 ผ่าน 3.10–3.13, 235 tests |
| #6 | Issue #15: แก้ design gap 3 ข้อจาก PR #13 | PR #16 merge แล้ว (`3a422c5`) | 11 นาที | ไม่ต้อง | run 44529767220 และ 44532003447 ผ่าน 3.10–3.13, 264 tests |

### 3.2 Report Agent (Human Iteration 2)

| วันที่ 22 พ.ย. | ทำอะไร | ผล |
|---|---|---|
| 16:14–16:26 น. | สร้าง project ใน Team ของพี่ Anak, deploy, ส่ง Spec ผ่าน eve channel 2 ครั้ง | รอบแรก Report ID ผิด หลังแก้ รอบที่สองตรงกับ `report.md` ทุก byte |
| 16:51 น. | Discord `/ask` แบบพิมพ์ | 29/29 แต่ตารางขึ้นเป็นข้อความ `\|` ดิบ |
| 16:52 น. | Discord `/ask` แบบแนบไฟล์ | agent เปิดไฟล์ไม่ได้ |
| 17:00 น. | หลังเพิ่ม `read_spec_file` | 29/29 |
| 17:19 น. | หลังให้ tool ส่งรายงานเองและครอบตารางด้วย code block | ไฟล์แนบมี SHA-256 ตรงกับ `report.md` คำตอบของ agent ไม่มีตัวเลข |
| 18:03–18:06 น. | หลัง refactor: Spec ถูก และ Spec ผิด (eve channel) | 29/29 และกรณีบัญชีผิดตอบว่าตัวเช็คไม่ผ่าน 23 ตัว |

## 4. ผลที่แสดงได้ (Demonstrated)

- Research 3 แนวทางที่ mentor ให้ศึกษา พร้อมคำตอบคำถาม 5 ข้อ (Software Design ข้อ 2.2–2.6)
- โรงงานเขียน `SqliteSource`, `make_private_db` และ `private_run` จาก Spec ที่ไม่มีข้อมูลจริง executor รันกับ database ที่คูณตัวเลข 7 เท่าแล้วได้รายงานถูกต้อง ตัวเลข 34 ตัวในรายงานไม่หลุดเข้า `result.json`
- Report Agent สร้างรายงานจาก Spec ที่ส่งทาง Discord ได้โดยไม่ต้องเข้า GitHub (HR-05 กับข้อมูลปลอม)
- รายงานถึงผู้ใช้โดยไม่ผ่านโมเดล (HR-06)
- ผู้ตรวจรันซ้ำได้ตาม [Delivery Document](../5-delivery-document.md) ข้อ 5:
  - ส่วน A และ B รันบนเครื่องของผู้ตรวจ
  - ส่วน C ทำผ่าน Discord โดยเชิญ bot เข้า server ก่อน

## 5. Gap ที่พบและการจัดประเภท

| Gap | ประเภท | การจัดการ |
|---|---|---|
| SRS เดิมไม่มีข้อกำหนดเรื่อง Private Data | Specification | เพิ่มกลุ่ม PD และ AC-07 ใน SRS v1.1 |
| `checks.json` มีตัวเลขจริง ส่งกลับให้ agent ไม่ได้ | Design | ตัวกรอง result (Run #5) |
| ตัวกันเขียนลง repo, leak check กับเลขบัญชีสั้น, layer `"boundary"` | Design | แก้ใน Run #6 |
| leak check ไม่ค้นในชื่อ key ของ JSON และค่าจำนวนเต็ม | Design (ยอมรับไว้ใน Spec ของ Issue #15) | บันทึกเป็นข้อจำกัด |
| Report ID ผิด, เปิดไฟล์แนบไม่ได้, ตารางใน Discord อ่านยาก | Design | แก้ใน PR #19 |
| โมเดลได้รายงานทั้งฉบับแล้วพิมพ์ซ้ำ ตัวเลขจึงผ่านโมเดล | Design (จาก review เทียบกับ feedback 19 พ.ย.) | tool ส่งรายงานเอง (PR #19) |
| ช่อง Data Sources ของ Spec ผูกกับ fixture จึงใช้ Spec เดิมกับข้อมูลจริงไม่ได้ และกฎ standard library ห้าม driver ของ database | Specification | Spec Structure v0.4 (ยังไม่ได้รันกับโรงงาน) |
| schema ยังไม่รองรับฝาก/ถอนหุ้น การถอนกำไร และรูปแบบปันผลของข้อมูลจริง ส่วนวันเริ่มลงทุนยังไม่พบแหล่ง (จากการเทียบกับแผนผังแหล่งข้อมูลของ pipeline ระดับชื่อตาราง) | Specification | แก้ใน Platform Spec รอบถัดไป |

ไม่ได้ลดข้อกำหนดข้อใดเพื่อให้ prototype ผ่าน

## 6. ปัญหาที่ยังเปิดและสิ่งที่รอ

| เรื่อง | ต้องการอะไร | จากใคร |
|---|---|---|
| ทดสอบ Discord ใน server ของทีม | เชิญ bot ด้วยลิงก์ใน Delivery Document ข้อ 3 | mentor |
| ค่า Sandbox และ Function ต่อรายงาน | ดูหน้า Usage ของ Team บน Vercel เพราะ AI Gateway แสดง cost เป็น $0 และ CLI ยังไม่มี billing data | mentor |
| ส่งเนื้อหารายงานลูกค้าเข้า Discord ได้หรือไม่ | ถ้าไม่ได้ Discord จะได้แค่สถานะและลิงก์ภายใน | mentor และฝ่ายที่ดูแล policy |
| executor ในบริษัท | เครื่องสำหรับ self-hosted runner, private repo, บัญชี database แบบอ่านอย่างเดียว | mentor และทีมเจ้าของข้อมูล |
| mapping ชุดข้อมูลไปยังตารางจริง | ยืนยันตารางและคอลัมน์ (เก็บนอก repo) | ผู้ดูแลแผนผังแหล่งข้อมูลของ pipeline |
| Policy เรื่องผู้ให้บริการโมเดล | ยืนยันว่าข้อมูลลูกค้าส่งให้ผู้ให้บริการภายนอกได้หรือไม่ | ฝ่ายที่ดูแล |

## 7. รอบถัดไป

1. ทำ Human Iteration 3 ตาม Software Design ข้อ 2.9 เมื่อได้คำตอบในข้อ 6
2. แก้ schema ใน Platform Spec ให้รองรับข้อมูลจริง (ฝาก/ถอนหุ้น, ปันผล, วันเริ่มลงทุน)
3. ให้ Report ID มาจาก Spec และจำกัดผู้ใช้ `/ask` ตาม role
4. แก้ข้อจำกัดของ leak check
