# Data Dictionary

**Project:** 711-tobacco-promo-analysis  
**Dataset:** `711_cigarette_promo_dataset.xlsx`  
**Last Updated:** 2024  
**Schema Type:** Star schema — one fact table, six dimension tables

---

## Table Index

| Table | Type | Rows | Description |
|---|---|---|---|
| `fact_transactions` | Fact | 23,522 | One row per cigarette transaction |
| `dim_store` | Dimension | 619 | Store attributes, price zones, regulatory region |
| `dim_product` | Dimension | 39 | Brand, manufacturer, pack type, category |
| `dim_manufacturer` | Dimension | 7 | Manufacturer name and funding program type |
| `dim_promotion` | Dimension | 35 | Promotion details, discount type, budget, eligibility |
| `dim_regulation` | Dimension | 15 | State-level tax and regulatory profiles |
| `dim_calendar` | Dimension | 731 | Daily calendar with fiscal periods and holidays |

---

## fact_transactions

The central fact table. Each row represents a single tobacco transaction at the store level. All pricing, discount, and reconciliation fields are captured here. Dimension keys are foreign keys only — no descriptive attributes are stored directly in this table.

| Column | Data Type | Description | Sample Values |
|---|---|---|---|
| `transaction_id` | STRING | Unique transaction identifier | `TXN-00001`, `TXN-23522` |
| `transaction_date` | DATE | Date of transaction | `2023-01-03`, `2024-11-15` |
| `store_id` | STRING | Foreign key → `dim_store` | `STR-0001`, `STR-0619` |
| `product_id` | STRING | Foreign key → `dim_product` | `PRD-01`, `PRD-39` |
| `promotion_id` | STRING | Foreign key → `dim_promotion`; NULL if no active promotion | `PRM-01`, NULL |
| `manufacturer_id` | STRING | Foreign key → `dim_manufacturer` | `MFR-01`, `MFR-07` |
| `regulation_id` | STRING | Foreign key → `dim_regulation` | `REG-CA`, `REG-TX` |
| `calendar_date` | DATE | Foreign key → `dim_calendar` | `2023-01-03` |
| `units_sold` | INTEGER | Number of packs sold in transaction | `1`, `2`, `3` |
| `base_price` | DECIMAL | Pre-discount shelf price per pack | `8.49`, `10.99`, `13.75` |
| `excise_tax_applied` | DECIMAL | State excise tax included in shelf price | `1.01`, `4.35`, `5.85` |
| `promo_discount_applied` | DECIMAL | Per-pack discount applied at point of sale | `0.00`, `0.50`, `1.00` |
| `final_price` | DECIMAL | Price paid by customer after discount | `7.99`, `9.49`, `12.75` |
| `minimum_price_floor` | DECIMAL | State minimum legal price for this product in this state | `8.00`, `11.50`, NULL |
| `min_price_violation_flag` | BOOLEAN | TRUE if `final_price` is below `minimum_price_floor` | `TRUE`, `FALSE` |
| `expected_reimbursement` | DECIMAL | Manufacturer reimbursement expected per promotion terms | `0.00`, `0.50`, `1.00` |
| `actual_reimbursement` | DECIMAL | Reimbursement amount confirmed received | `0.00`, `0.45`, `1.00` |
| `recon_variance` | DECIMAL | `actual_reimbursement` minus `expected_reimbursement`; negative = shortfall | `-0.05`, `0.00`, `0.10` |
| `recon_flag` | STRING | Categorized reason for reconciliation discrepancy | `CLEAN`, `MISSING_SCAN`, `WRONG_DISCOUNT`, `BUDGET_EXHAUSTED`, `PARTIAL_REIMB` |
| `execution_failure_flag` | BOOLEAN | TRUE if promo was not executed correctly at store level | `TRUE`, `FALSE` |
| `scan_data_present` | BOOLEAN | TRUE if scan data was submitted for reimbursement | `TRUE`, `FALSE` |

---

## dim_store

One row per store location. Captures geographic, zone, and regulatory attributes used to segment performance across the dashboard.

| Column | Data Type | Description | Sample Values |
|---|---|---|---|
| `store_id` | STRING | Primary key | `STR-0001`, `STR-0619` |
| `store_name` | STRING | Formatted store identifier | `7-Eleven #0001` |
| `city` | STRING | Store city | `Atlanta`, `Chicago`, `Houston` |
| `state` | STRING | Two-letter state abbreviation | `GA`, `IL`, `TX` |
| `state_full` | STRING | Full state name | `Georgia`, `Illinois`, `Texas` |
| `regulation_id` | STRING | Foreign key → `dim_regulation` | `REG-GA`, `REG-IL` |
| `price_zone` | STRING | Price zone assignment (1–8); zones are market clusters, not geographic | `Zone 1`, `Zone 5`, `Zone 8` |
| `price_zone_id` | INTEGER | Numeric price zone for sorting/filtering | `1`, `5`, `8` |
| `region` | STRING | Broad geographic region | `Southeast`, `Midwest`, `Southwest` |
| `store_open_date` | DATE | Date store entered the simulation | `2023-01-01`, `2023-04-15` |
| `store_type` | STRING | Store format classification | `Urban`, `Suburban`, `Highway` |
| `tobacco_door_count` | INTEGER | Number of tobacco doors (shelf space proxy) | `2`, `3`, `4` |

---

## dim_product

One row per SKU. Covers brand, manufacturer, format, and regulatory classification attributes.

| Column | Data Type | Description | Sample Values |
|---|---|---|---|
| `product_id` | STRING | Primary key | `PRD-01`, `PRD-39` |
| `brand_name` | STRING | Consumer-facing brand name | `Marlboro`, `Newport`, `Camel` |
| `manufacturer_id` | STRING | Foreign key → `dim_manufacturer` | `MFR-01`, `MFR-02` |
| `product_family` | STRING | Brand family grouping | `Marlboro Red`, `Newport Menthol` |
| `pack_type` | STRING | Pack configuration | `King Box`, `King Soft`, `100s Box` |
| `pack_count` | INTEGER | Number of cigarettes per pack | `20`, `25` |
| `carton_eligible` | BOOLEAN | TRUE if product is sold in carton format | `TRUE`, `FALSE` |
| `category` | STRING | Product category | `Cigarette`, `Smokeless`, `Cigar` |
| `flavor` | STRING | Flavor classification | `Regular`, `Menthol`, `Flavored` |
| `flavor_ban_eligible` | BOOLEAN | TRUE if product is subject to state flavor bans | `TRUE`, `FALSE` |
| `multipack_eligible` | BOOLEAN | TRUE if product is eligible for multipack promotions | `TRUE`, `FALSE` |
| `msrp` | DECIMAL | Manufacturer suggested retail price | `8.99`, `11.49`, `14.25` |

---

## dim_manufacturer

One row per tobacco manufacturer. Contains funding program type, which governs how promotional reimbursements are structured.

| Column | Data Type | Description | Sample Values |
|---|---|---|---|
| `manufacturer_id` | STRING | Primary key | `MFR-01`, `MFR-07` |
| `manufacturer_name` | STRING | Full manufacturer name | `Altria`, `Reynolds American`, `ITG Brands` |
| `short_name` | STRING | Abbreviated name used in dashboard labels | `Altria`, `RAI`, `ITG` |
| `funding_program_type` | STRING | Reimbursement model used for this manufacturer's promotions | `Scan-Based`, `Guaranteed`, `Tiered` |
| `primary_brand` | STRING | Manufacturer's highest-volume brand | `Marlboro`, `Newport`, `Winston` |
| `active` | BOOLEAN | TRUE if manufacturer has active promotions in the simulation period | `TRUE`, `FALSE` |

---

## dim_promotion

One row per promotional program. Includes discount terms, eligibility rules, budget parameters, and funding type.

| Column | Data Type | Description | Sample Values |
|---|---|---|---|
| `promotion_id` | STRING | Primary key | `PRM-01`, `PRM-35` |
| `promotion_name` | STRING | Descriptive name of the promotional program | `Marlboro Q1 Pack Discount`, `Newport Summer Scan` |
| `manufacturer_id` | STRING | Foreign key → `dim_manufacturer` | `MFR-01`, `MFR-02` |
| `discount_type` | STRING | Mechanism by which discount is applied | `Off-Invoice`, `Scan`, `Buy-Down` |
| `discount_amount` | DECIMAL | Per-pack discount value | `0.25`, `0.50`, `1.00` |
| `promo_start_date` | DATE | First eligible date for promotion | `2023-01-01`, `2023-07-01` |
| `promo_end_date` | DATE | Last eligible date for promotion | `2023-03-31`, `2023-09-30` |
| `budget_total` | DECIMAL | Total manufacturer funding budget for this promotion | `50000.00`, `125000.00` |
| `budget_utilized` | DECIMAL | Amount of budget drawn down through reimbursement claims | `47832.50`, `118600.00` |
| `budget_utilization_pct` | DECIMAL | `budget_utilized / budget_total` | `0.956`, `0.948` |
| `budget_exhausted_flag` | BOOLEAN | TRUE if budget was fully depleted before promo end date | `TRUE`, `FALSE` |
| `multipack_required` | BOOLEAN | TRUE if discount only applies on multipack purchases | `TRUE`, `FALSE` |
| `flavor_restricted` | BOOLEAN | TRUE if promotion excludes menthol or flavored products | `TRUE`, `FALSE` |
| `coupon_restricted_states` | STRING | Pipe-delimited list of states where coupon promotions are prohibited | `MA|NJ|NY`, NULL |
| `scan_required` | BOOLEAN | TRUE if reimbursement requires scan data submission | `TRUE`, `FALSE` |
| `eligible_states` | STRING | Pipe-delimited list of states where this promotion is valid | `GA|TX|FL|TN`, `ALL` |

---

## dim_regulation

One row per state. Contains excise tax rates, minimum price law parameters, flavor ban status, and other regulatory profile fields. The 15 states were selected to represent the full range of regulatory environments.

| Column | Data Type | Description | Sample Values |
|---|---|---|---|
| `regulation_id` | STRING | Primary key | `REG-NY`, `REG-GA` |
| `state` | STRING | Two-letter state abbreviation | `NY`, `CA`, `TX` |
| `state_full` | STRING | Full state name | `New York`, `California`, `Texas` |
| `excise_tax_per_pack` | DECIMAL | State excise tax in dollars per 20-cigarette pack | `4.35`, `2.87`, `1.41` |
| `minimum_price_law` | BOOLEAN | TRUE if state has a statutory minimum price for cigarettes | `TRUE`, `FALSE` |
| `minimum_price_floor` | DECIMAL | Minimum legal retail price per pack; NULL if no law | `10.50`, `8.00`, NULL |
| `min_price_includes_tax` | BOOLEAN | TRUE if minimum price floor is calculated on a tax-included basis | `TRUE`, `FALSE`, NULL |
| `flavor_ban` | BOOLEAN | TRUE if state or locality has an active flavor ban | `TRUE`, `FALSE` |
| `flavor_ban_scope` | STRING | Products covered by flavor ban; NULL if no ban | `Menthol + Flavored`, `Flavored Only`, NULL |
| `coupon_ban` | BOOLEAN | TRUE if state prohibits cigarette coupons or scan promotions | `TRUE`, `FALSE` |
| `multipack_ban` | BOOLEAN | TRUE if state prohibits multipack discounts | `TRUE`, `FALSE` |
| `regulatory_tier` | STRING | Composite regulatory restrictiveness rating | `High`, `Medium`, `Low` |
| `region` | STRING | Broad geographic region | `Northeast`, `Southeast`, `West` |

**States included in simulation:**

| State | Tier | Key Regulatory Features |
|---|---|---|
| New York | High | $4.35 excise, minimum price law, coupon ban |
| Massachusetts | High | $3.51 excise, minimum price law, flavor ban (menthol + flavored) |
| California | High | $2.87 excise, flavor ban (flavored only) |
| New Jersey | High | $2.70 excise, minimum price law, coupon ban |
| Illinois | Medium | $2.98 excise, Chicago local surcharge applied |
| Michigan | Medium | $2.00 excise, multipack restrictions |
| Pennsylvania | Medium | $2.60 excise, minimum price law |
| Washington | Medium | $3.025 excise, flavor ban (flavored only) |
| Florida | Low-Medium | $1.339 excise, no minimum price law |
| Texas | Low | $1.41 excise, minimal restrictions |
| Georgia | Low | $0.37 excise, no minimum price law |
| Tennessee | Low | $0.62 excise, minimal restrictions |
| Arizona | Low | $2.00 excise, minimal restrictions |
| Nevada | Low | $1.80 excise, minimal restrictions |
| Colorado | Low-Medium | $1.94 excise, flavor ban (flavored only) |

---

## dim_calendar

One row per day across the simulation period (January 1, 2023 – December 31, 2024). Used for time intelligence calculations in Power BI.

| Column | Data Type | Description | Sample Values |
|---|---|---|---|
| `calendar_date` | DATE | Primary key | `2023-01-01`, `2024-12-31` |
| `year` | INTEGER | Calendar year | `2023`, `2024` |
| `quarter` | STRING | Calendar quarter label | `Q1`, `Q2`, `Q3`, `Q4` |
| `quarter_number` | INTEGER | Calendar quarter number | `1`, `2`, `3`, `4` |
| `month_number` | INTEGER | Month number (1–12) | `1`, `6`, `12` |
| `month_name` | STRING | Full month name | `January`, `June`, `December` |
| `month_short` | STRING | Three-letter month abbreviation | `Jan`, `Jun`, `Dec` |
| `week_number` | INTEGER | ISO week number | `1`, `26`, `52` |
| `day_of_week` | STRING | Day name | `Monday`, `Friday` |
| `is_weekend` | BOOLEAN | TRUE if Saturday or Sunday | `TRUE`, `FALSE` |
| `is_holiday` | BOOLEAN | TRUE if federally recognized US holiday | `TRUE`, `FALSE` |
| `holiday_name` | STRING | Holiday name; NULL if not a holiday | `Labor Day`, `Thanksgiving`, NULL |
| `fiscal_year` | INTEGER | Fiscal year (July–June basis) | `2023`, `2024` |
| `fiscal_quarter` | STRING | Fiscal quarter label | `FQ1`, `FQ2`, `FQ3`, `FQ4` |
| `fiscal_period` | INTEGER | Fiscal period number (1–12) | `1`, `6`, `12` |
| `days_in_month` | INTEGER | Total days in the calendar month | `28`, `30`, `31` |
| `is_month_end` | BOOLEAN | TRUE if last day of calendar month | `TRUE`, `FALSE` |
| `is_quarter_end` | BOOLEAN | TRUE if last day of calendar quarter | `TRUE`, `FALSE` |

---

*For business logic governing how these fields were simulated — including tax calculations, minimum price enforcement, flavor ban suppression, and reconciliation variance rules — see [business_logic.md](business_logic.md).*
