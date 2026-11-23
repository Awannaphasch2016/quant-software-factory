# demo_grid_2026_11: mock Reverse Grid account

Every value in this folder is invented. The client, account and instruments
(`DEMO-COOP`, `DEMO-0001`, `AAA`, `BBB`, `CCC`) do not exist. This is the input
for the Grid Trade Performance report.

- Account: `DEMO-0001`, strategy Reverse Grid (GT), inception 2024-02-28
- As-of date: 2026-11-06
- History: one row per instrument at inception, at the last weekday of each
  month, and at the as-of date (35 dates)

## Datasets

| File | Rows | Fields |
| --- | --- | --- |
| `account_info.csv` | 1 | `account_no, client_name, strategy, inception_date, product` (same shape as `demo_coop_rg_2026_10_v2`) |
| `grid_setup.csv` | 3 | `account_no, instrument, display_order, initial_units, initial_cost, commission_rate, expected_trade_units, expected_trade_return_pct` |
| `holdings_daily.csv` | 105 | same fields as `demo_coop_rg_2026_10_v2`; no CASH row |
| `grid_cash.csv` | 105 | `date, account_no, instrument, cash`: cash held in each instrument's grid sleeve |
| `nav_daily.csv` | 35 | `date, account_no, nav, cash, market_value` |
| `transactions.csv` | 26 | same fields as `demo_coop_rg_2026_10_v2`; `side` adds `PORT_ADJUSTED` and `GAIN_ADJUSTMENT` (instrument `CASH`, price 1.00, `qty` is the amount truncated to an integer) |

## Conventions

- `avg_cost` has 4 decimal places; money has 2.
- `cost_value = volume × avg_cost` (to 0.01), `market_value = volume × market_price`,
  `unrealized_pl = market_value − cost_value`.
- `nav_daily.market_value` is the sum of `holdings_daily.market_value`,
  `nav_daily.cash` is the sum of `grid_cash.cash`, and `nav = market_value + cash`,
  on every date.
- `holdings_daily.volume` on any date equals `grid_setup.initial_units` plus BUY
  quantities minus SELL quantities on or before that date.
- `transactions.amount` is signed cash flow: BUY is negative (gross plus fee),
  SELL is gross minus fee, DIVIDEND is quantity × price. Fees are 0.15% of gross,
  rounded to 0.01. SELL rows carry `realized_pl`.
- DIVIDEND quantity is the instrument's volume on the payment date.
- Cash moved between the grid sleeves and the account (`PORT_ADJUSTED`,
  `GAIN_ADJUSTMENT`) is not reconciled against `grid_cash`.

## Key values at 2026-11-06

| Value | Expected |
| --- | ---: |
| NAV | 28,360,974.70 |
| Cash on hand | 249,824.70 |
| Dividend 2026 YTD | 830,000.00 |
| Total cost value (including cash) | 26,473,509.22 |

| Instrument | Volume | Avg cost | Market price | Market value | Sleeve cash |
| --- | ---: | ---: | ---: | ---: | ---: |
| AAA | 500,000 | 16.4127 | 13.90 | 6,950,000.00 | 0.00 |
| BBB | 78,200 | 121.7486 | 138.25 | 10,811,150.00 | 249,824.70 |
| CCC | 180,000 | 47.2033 | 57.50 | 10,350,000.00 | 0.00 |
