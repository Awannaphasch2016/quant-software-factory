# Report Spec สำหรับส่งทาง Discord

ไฟล์นี้คือส่วน Report Definition และ Data Sources ของ [Report Spec ที่ส่งเป็น Issue #9](report-spec.md) ใช้แนบในคำสั่ง `/ask` ของ Discord (Delivery Document ส่วน C) ข้อความใต้เส้นคั่นตรงกับไฟล์ที่แนบทดสอบใน Discord เมื่อ 22 พ.ย. 2569 ซึ่งได้ผล 29/29

---

Feature: Returns & Transactions Report from precomputed data — DEMO-COOP Reverse Grid, October 2026

## Background

The Quant team sends clients a returns and transactions report: capital gains, dividends, and gains or losses on positions still held. Relationship managers use it in client conversations.

The team's pipeline already computes every figure. This report reads those figures, lays them out, checks that they agree with each other, and adds a short narrative. It must not recompute any figure that a dataset provides.

The data layer already exists on `main` (merged from #7): `DataSource`, `FixtureSource`, the schema registry and the Layer A data checks in `quant_software_factory.reporting`. Build on it. Do not change its behavior.

## Report Definition

| Field | Value |
| --- | --- |
| Report type | `returns_transactions` |
| Report ID | `demo_coop_rg_2026_10_v2` |
| Account | `DEMO-0001` |
| Client, strategy, inception | from `account_info` |
| Period | 2026-10 (2026-10-01 to 2026-10-31) |
| Opening date | 2026-09-30 |
| As-of date | 2026-10-30 |
| Currency | THB |
| Language | en |
| Audience | Institutional client, read with a relationship manager |
| Output format | md |

## Data Sources

Use the existing fixtures in `data/fixtures/demo_coop_rg_2026_10_v2/` through `FixtureSource` and `load(...)`. Do not add or change fixtures. Datasets used: `account_info`, `nav_daily`, `holdings_daily`, `transactions`, `cash_flow`, `performance`.

