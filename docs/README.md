# Project Documentation: Reporting Spec Structure for Software Factory

เอกสารหลัก 5 ฉบับของโครงการ แต่ละฉบับแสดง version ปัจจุบัน ประวัติ version อยู่ใน Change Log ของแต่ละฉบับ และใน history ของไฟล์ใน git

| # | เอกสาร | Version | Last Updated |
|---|---|---|---|
| 1 | [TOR](1-tor.md) | v1.3 | 22 พ.ย. 2569 |
| 2 | [Project Plan](2-project-plan.md) | v1.5 | 23 พ.ย. 2569 |
| 3 | [SRS](3-srs.md) | v1.5 | 23 พ.ย. 2569 |
| 4 | [Software Design](4-software-design.md) | v1.5 | 23 พ.ย. 2569 |
| 5 | [Delivery Document](5-delivery-document.md) | v1.5 | 23 พ.ย. 2569 |

วิธีทดสอบสิ่งที่ส่งมอบอยู่ใน Delivery Document ข้อ 5 (ส่วน C ทดสอบผ่าน Discord, ส่วน D สร้างรายงาน Grid เป็น PDF)

## เอกสารประกอบ

| โฟลเดอร์ | ไฟล์ | เนื้อหา |
|---|---|---|
| [`spec-structure/`](spec-structure/) | [Report Spec Structure](spec-structure/report-spec-structure.md), [Platform Spec Structure](spec-structure/platform-spec-structure.md) | โครงสร้าง Spec (template) ของรายงาน 1 ฉบับ และของชั้นข้อมูล |
| [`specs/`](specs/) | [Report Spec](specs/report-spec.md) (Issue #9), [Platform Spec](specs/platform-spec.md) (Issue #7), [Spec สำหรับส่งทาง Discord](specs/report-spec-chat-input.md), [Grid Trade Performance](specs/grid-report-spec.md) (Issue #23) | Spec ที่กรอกแล้วและส่งเข้าโรงงานจริง |
| [`evidence/`](evidence/) | [หลักฐาน End-to-End Run](evidence/e2e-run-evidence.md) | Issue #9 → PR #10 พร้อมตารางเทียบ Expected Values |
| [`progress/`](progress/) | [Iteration 1](progress/progress-report-iteration-1.md), [สัปดาห์ 16–23 พ.ย.](progress/progress-report-2026-11-16.md) | Progress Report แต่ละรอบ |
| [`proposals/`](proposals/) | [Natural Writing Proposal](proposals/natural-writing-proposal.md) | ข้อเสนอเรื่องข้อความบรรยาย |
| [`history/`](history/) | Template v0.1–v0.3, ตัวอย่าง Spec v0.1–v0.2, วิธีวัดผล Spec | ฉบับเก่าที่เก็บไว้เทียบ (รวม Report Spec Structure v0.3) |

ข้อมูลทุกไฟล์ในโฟลเดอร์นี้เป็นข้อมูลปลอม (บัญชี DEMO-COOP) และไม่มีชื่อระบบหรือข้อมูลภายใน
