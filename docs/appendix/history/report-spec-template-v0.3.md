# Report Spec Template v0.3 (ส่วนที่เปลี่ยนจาก v0.2)

เอกสารนี้บอกเฉพาะส่วนที่เปลี่ยนจาก [`report-spec-template-v0.2.md`](report-spec-template-v0.2.md) ส่วนที่ไม่ได้พูดถึงให้ใช้ตาม v0.2 ได้เลย ได้แก่ หลักการ, Dataset Catalog, Block Catalog, Presets, Output Contract มาตรฐาน และ Open Items O1–O8

- สถานะ: Demonstrated กับรายงานประเภท `returns_transactions` 1 ประเภท ผ่าน Spec 2 ใบ
  - Issue #7 → PR #8 merge แล้ว commit `9455ea3`
  - Issue #9 → PR #10 merge แล้ว commit `4e2129e`
- Spec ที่ใช้รันจริง (เป็นตัวอย่างการกรอก v0.3):
  - [`../platform-spec.md`](../platform-spec.md) (Platform Spec, Issue: [#7](https://github.com/Awannaphasch2016/quant-software-factory/issues/7))
  - [`../report-spec.md`](../report-spec.md) (Report Spec, Issue: [#9](https://github.com/Awannaphasch2016/quant-software-factory/issues/9))
- อีก 2 ประเภท (`client_pnl`, `monthly_team`) ยังเป็น Intended

## 1. Spec มี 2 ชนิด

v0.2 แตก Spec ตามชั้นงาน (ข้อมูล, รายงาน, ข้อความบรรยาย) ทำให้ "กรอก Spec 1 ใบได้รายงาน 1 ฉบับ" ตาม requirement_1 ไม่เป็นจริง v0.3 จึงแยกชนิดของ Spec แทน

| ชนิด | ทำเมื่อ | มีอะไร | ตัวอย่าง |
|---|---|---|---|
| Platform Spec | ครั้งเดียว หรือเมื่อเพิ่มแหล่งข้อมูลใหม่ | interface `load(...)`, `DataSource` / `FixtureSource`, schema registry, fixture, ตัวเช็คชั้น A | Issue #7 |
| Report Spec | ทุกครั้งที่ต้องการรายงานใหม่ | Report Definition, Data Mapping, block, Expected Values, ตัวเช็คชั้น B, Writing Rules | Issue #9 |

- Report Spec ต้องใช้ของจาก Platform Spec ที่ merge แล้ว และห้ามแก้ data layer (ระบุใน Constraints และ Out of Scope)
- ข้อความบรรยายอยู่ใน Report Spec ใบเดียวกัน ไม่แยกเป็นใบที่ 3 ตามที่วางแผนไว้ใน v0.2 เพราะ Issue #9 ทำทั้งรายงานและข้อความบรรยายจบใน Spec ใบเดียว โดยต้อง Approve 1 ครั้ง

## 2. กติกาขนาด

| ถ้า | ทำอย่างไร |
|---|---|
| repo ยังไม่มี data layer | เปิด Platform Spec ก่อน แล้ว merge |
| data layer มีแล้ว | เปิด Report Spec ใบเดียวต่อรายงาน 1 ฉบับ |
| Report Spec มีมากกว่า 6 block | แตก block ที่ไม่บังคับออกไปไว้ใบถัดไป (กติกาเดิมของ v0.2) |

ผลที่วัดได้:
- Platform Spec (Issue #7) ไม่ชนเพดาน output token ได้ PR ใน 12 นาที 34 วินาที
- Report Spec (Issue #9, 6 block, Expected Values 21 แถว, ตัวเช็คชั้น B และการเขียน 15 ข้อ) ชนเพดาน 100K หลังขั้น implement เสร็จ หลัง Approve 1 ครั้งได้ PR ใน 3 นาที 21 วินาที
- กติกา 6 block ของ v0.2 จึงยังไม่พอให้ Report Spec จบใน session เดียว และผลจาก 1 run ยังไม่พอจะตั้งเกณฑ์ใหม่ ดูข้อ 5

## 3. สิ่งที่แก้จาก v0.2 (จาก Run #2)

| Gap จาก Run #2 | แก้ใน v0.3 | ยืนยันด้วยผลรัน |
|---|---|---|
| A2 บังคับให้ทุกชุดข้อมูลมีอย่างน้อย 1 แถว | ระบุชุดข้อมูลที่ว่างได้ (`transactions`, `cash_flow`) | ✅ Issue #7 มี test กรณีว่างแล้วผ่าน |
| Writing Rules ให้เขียนค่าติดลบเป็น "loss" แต่ B8 ต้องการเลขตรงกับ JSON | B8 ยอมรับค่าสัมบูรณ์ของค่าที่ JSON เก็บเป็นลบ | ✅ Issue #9: "a realized loss of 3,037.00 THB" ผ่าน B8 |
| B8 ไม่บอกว่าวันที่และจำนวนนับต้องตรวจหรือไม่ | B8 ตรวจเฉพาะจำนวนเงินและ % | ✅ Issue #9 ข้อความมีวันที่และจำนวนรายการได้ตามปกติ |
| ไม่ได้บอกเครื่องหมายของเงินถอน | Data Mapping: Amount = `-amount` สำหรับ WITHDRAWAL | ⚠️ เขียนเป็นโค้ดและ test แล้ว แต่ fixture ไม่มีรายการถอน |
| Spec ใหญ่ชนเพดานตั้งแต่ต้นขั้น implement | Platform Spec + Report Spec | ✅ บางส่วน (ดูข้อ 2) |

## 4. สิ่งที่เปลี่ยนในช่องกรอกของ Report Spec

เปลี่ยนหรือเพิ่มจากช่องกรอกของ v0.2 ข้อ 11:

- Background: บอกว่า data layer มีอยู่แล้วจาก Issue ไหน และห้ามเปลี่ยนพฤติกรรม
- Data Mapping: เปลี่ยนจาก "fail check A3" ใน v0.2 เป็น "If a mapped value is missing, the report fails. Do not derive it from other fields." เพราะ A3 ตรวจแค่ schema ไม่ได้ตรวจว่าแถวที่รายงานต้องใช้มีอยู่จริง
- Output Contract:
  - ลำดับการรัน: ตัวเช็คชั้น A ก่อน ถ้าไม่ผ่านไม่สร้างรายงาน และรายงานตัวเช็คชั้น B ว่า not run
  - `checks.json` รวมผลชั้น A และชั้น B ในรูปแบบเดียวกัน
- Writing Rules: ลำดับหัวข้อของข้อความ และตัวเช็คการเขียน W1–W5 ที่รายงานใน `checks.json`

## 5. Gap ใหม่จาก Issue #9 (ยังไม่ได้แก้)

| ประเภท | จุดที่พบ | แนวทางสำหรับ v0.4 |
|---|---|---|
| Specification | Writing Rules ข้อ 1 สั่งให้พูดถึง "การเปลี่ยนแปลงของ NAV" แต่ตัวเลขนี้ไม่มีในชุดข้อมูล โรงงานจึงไม่เขียนตัวเลขนี้ เพราะจะผิดหลักห้ามคำนวณใหม่ | เพิ่ม opening NAV (`nav_daily.nav` ที่ opening date) ใน Data Mapping เพื่อให้เขียน "จาก X เป็น Y" ได้ หรือตัดคำว่า "change" ออกจาก Writing Rules |
| Specification | Spec ไม่ได้บอกว่าช่วงเวลาของรายงานคิดจาก opening date หรือเดือนของ as-of โรงงานเลือกเดือนของ as-of | ระบุใน Report Definition ว่า period มาจากไหน และให้ตรวจว่า opening date คือวันสุดท้ายของเดือนก่อน |
| Specification | ตัวเช็ค B0 (ค่าที่ต้อง map หายไป) โรงงานเพิ่มเอง | เพิ่ม B0 เป็นตัวเช็คมาตรฐานของชั้น B |
| Design | Report Spec ขนาดนี้ยังชนเพดาน 100K ก่อนขั้น review | ถามพี่ Anak ว่าเพิ่มเพดานต่อ session ได้หรือไม่ หรือลดขนาด Report Spec (เช่น แยก block ที่ไม่บังคับ) แล้ววัดซ้ำ |
