# Business Logic

**Project:** 711-tobacco-promo-analysis  
**Purpose:** Documents all regulatory rules, pricing constraints, promotional mechanics, and simulation parameters baked into the dataset. This is the source of truth for understanding why the data looks the way it does.

---

## Table of Contents

1. [Pricing Architecture](#1-pricing-architecture)
2. [State Excise Tax Modeling](#2-state-excise-tax-modeling)
3. [Minimum Price Law Enforcement](#3-minimum-price-law-enforcement)
4. [Flavor Ban Suppression](#4-flavor-ban-suppression)
5. [Multipack and Coupon Restrictions](#5-multipack-and-coupon-restrictions)
6. [Manufacturer Funding Programs](#6-manufacturer-funding-programs)
7. [Promotional Execution Modeling](#7-promotional-execution-modeling)
8. [Reconciliation Variance Logic](#8-reconciliation-variance-logic)
9. [Price Zone Architecture](#9-price-zone-architecture)
10. [Transaction Volume Distribution](#10-transaction-volume-distribution)

---

## 1. Pricing Architecture

Every transaction price is built from four components:

```
final_price = base_price - promo_discount_applied
base_price  = wholesale_cost + margin + excise_tax_applied
```

**Base price** is set at the store level and varies by price zone. Stores in high-cost zones (Zones 7–8) reflect urban market pricing; stores in low-cost zones (Zones 1–2) reflect price-competitive or rural markets. The spread between Zone 1 and Zone 8 base prices for the same product averages $2.10–$2.80 per pack depending on brand tier.

**Excise tax** is embedded in shelf price (tax-inclusive pricing), consistent with how cigarettes are actually sold at retail. Tax amounts in `fact_transactions.excise_tax_applied` reflect the state rate for that store's state.

**Promo discount** is applied at point of sale and subtracted from base price to produce `final_price`. If no promotion is active, `promo_discount_applied` is 0.00 and `promotion_id` is NULL.

---

## 2. State Excise Tax Modeling

Excise tax rates reflect real 2023–2024 statutory rates for each of the 15 simulated states. Rates are applied on a per-pack basis assuming a standard 20-cigarette pack.

**Tax rate by state (per pack, 20-cigarette standard):**

| State | Rate | Notes |
|---|---|---|
| New York | $4.35 | Highest in simulation; NYC adds additional local tax (not modeled separately) |
| Massachusetts | $3.51 | Combined with minimum price law creates highest effective floor |
| Illinois | $2.98 | Cook County/Chicago surcharge treated as blended state-equivalent rate |
| New Jersey | $2.70 | Coupon ban also applies |
| Pennsylvania | $2.60 | Minimum price law in effect |
| California | $2.87 | Flavored product ban layered on top |
| Washington | $3.025 | Flavored-only ban; menthol still permitted |
| Arizona | $2.00 | No additional restrictions |
| Michigan | $2.00 | Multipack restrictions apply |
| Nevada | $1.80 | Minimal regulatory burden |
| Colorado | $1.94 | Flavored product ban (not menthol) |
| Florida | $1.339 | No minimum price law |
| Texas | $1.41 | Lowest regulatory burden in simulation |
| Tennessee | $0.62 | Among lowest excise rates in US |
| Georgia | $0.37 | Lowest excise rate in simulation |

**Tax calculation in the dataset:**
- `excise_tax_applied` is pulled from `dim_regulation.excise_tax_per_pack` for each transaction's state
- Tax is embedded in `base_price` — it is not a separate line item added at checkout
- The field exists in `fact_transactions` to support tax composition analysis in the dashboard

---

## 3. Minimum Price Law Enforcement

Seven of the 15 states have statutory minimum price laws for cigarettes. These laws set a floor below which retailers cannot legally sell, regardless of promotion depth.

**States with minimum price laws in simulation:**

| State | Floor (per pack) | Tax-Inclusive? |
|---|---|---|
| New York | $10.50 | Yes |
| Massachusetts | $9.00 | Yes |
| New Jersey | $8.00 | Yes |
| Pennsylvania | $7.25 | Yes |
| Michigan | $7.50 | No |
| Colorado | $6.75 | No |
| California | $7.00 | No |

**Enforcement logic:**
- `minimum_price_floor` in `fact_transactions` is populated for every transaction in a minimum-price state
- `min_price_violation_flag` is set to TRUE when `final_price < minimum_price_floor`
- Violations are intentionally included in the dataset at a low rate (~2–4% of transactions in minimum-price states) to simulate real-world execution failures — stores occasionally miscalculate or apply promotions that push price below the floor
- These violations are analytically valuable: they surface in the Regulatory Impact dashboard page and can be filtered for compliance reporting

---

## 4. Flavor Ban Suppression

Four states in the simulation have active flavor bans. Products subject to a ban in a given state are suppressed from transactions in that state — they do not appear as sold, which is the correct representation of a retailer complying with the law.

**Flavor ban states and scope:**

| State | Scope | Menthol Banned? |
|---|---|---|
| Massachusetts | Menthol + Flavored | Yes |
| California | Flavored Only | No (menthol exempt) |
| Washington | Flavored Only | No (menthol exempt) |
| Colorado | Flavored Only | No (menthol exempt) |

**Suppression logic:**
- `dim_product.flavor_ban_eligible` is TRUE for menthol and flavored products
- During transaction generation, the script checks `dim_regulation.flavor_ban` and `flavor_ban_scope` for the store's state
- If a product's flavor classification falls within the ban scope for that state, it is excluded from the eligible product pool for that store
- This produces realistic category mix differences across regulatory tiers — menthol share is lower in ban states, flavored SKUs disappear entirely

---

## 5. Multipack and Coupon Restrictions

**Multipack restrictions (Michigan):**
- Michigan prohibits multipack discount promotions on cigarettes
- Promotions with `dim_promotion.multipack_required = TRUE` are excluded from eligible promotions for Michigan stores
- `dim_product.multipack_eligible` is still populated for all products, but the restriction prevents these promotions from appearing in Michigan transactions

**Coupon bans (New York, New Jersey):**
- New York and New Jersey prohibit manufacturer coupons and scan-based promotional discounts for cigarettes
- Promotions with `dim_promotion.coupon_restricted_states` containing `NY` or `NJ` are suppressed from transactions in those states
- These stores still receive off-invoice funding (price reductions built into wholesale cost) but do not show scan-based promotional transactions
- Effect on the dataset: lower `promo_attach_rate` in NY and NJ compared to unrestricted states, which is analytically visible in the dashboard

---

## 6. Manufacturer Funding Programs

Three funding program types are modeled, reflecting the actual range of manufacturer reimbursement structures used in the US tobacco industry.

### Scan-Based Funding
- Reimbursement is triggered by actual scan data submitted by the retailer
- `scan_required = TRUE` in `dim_promotion`
- Reimbursement is calculated per unit sold and confirmed via scan submission
- Missing or incomplete scan data is the primary source of reconciliation variance for this program type
- Used primarily by Reynolds American (Newport, Camel brands)

### Guaranteed Funding
- Manufacturer commits a fixed reimbursement amount regardless of scan data
- `scan_required = FALSE`
- Simpler execution model, but subject to budget exhaustion if volume runs high
- Used primarily by smaller manufacturers (ITG Brands, Standard General)
- Budget exhaustion is modeled at a higher rate for guaranteed programs because there is no scan-based volume signal to allow mid-period adjustments

### Tiered Funding
- Reimbursement rate varies based on volume thresholds achieved during the promotional period
- Base tier: standard discount rate
- Mid tier: discount rate increases by $0.10–$0.25 per pack at 50% budget utilization
- Top tier: maximum discount rate applied above 80% budget utilization
- Used primarily by Altria (Marlboro)
- Creates more complex reconciliation scenarios: if the volume tier calculation is disputed, the expected vs. actual reimbursement diverges at the tier boundary

---

## 7. Promotional Execution Modeling

Execution failures are baked into the dataset to simulate the real-world reality that store-level promotional compliance is never 100%. Failure modes include:

| Failure Type | Description | Approximate Rate |
|---|---|---|
| Wrong discount applied | Store applied incorrect discount amount | ~3% of promo transactions |
| No discount applied | Promotion was active but discount was not applied at POS | ~2% of promo transactions |
| Discount applied outside promo window | Promotion applied before start date or after end date | ~1% of promo transactions |
| Discount applied to ineligible product | Promo applied to a SKU outside the eligible product set | ~1.5% of promo transactions |
| Missing scan data | Transaction occurred but scan was not submitted | ~4% of scan-required transactions |

**Flags in the dataset:**
- `execution_failure_flag = TRUE` when any of the above conditions are present
- `scan_data_present = FALSE` specifically captures missing scan submissions
- These flags are independent — a transaction can have a scan present but still have an execution failure (e.g., wrong discount applied with scan submitted)

---

## 8. Reconciliation Variance Logic

`recon_variance = actual_reimbursement - expected_reimbursement`

Negative values indicate a shortfall (retailer was reimbursed less than expected). Positive values indicate overpayment (rare, but present).

**Reconciliation flag categories:**

| Flag | Description | Variance Direction |
|---|---|---|
| `CLEAN` | No variance; expected and actual reimbursement match | 0.00 |
| `MISSING_SCAN` | Scan data was not submitted; reimbursement withheld | Negative |
| `WRONG_DISCOUNT` | Discount applied at POS did not match promo terms | Positive or Negative |
| `BUDGET_EXHAUSTED` | Manufacturer budget depleted before period end; reimbursement capped | Negative |
| `PARTIAL_REIMB` | Reimbursement received but below expected amount (disputed claim) | Negative |

**Budget exhaustion modeling:**
- When `dim_promotion.budget_exhausted_flag = TRUE`, transactions after the exhaustion date receive `actual_reimbursement = 0.00` and `recon_flag = BUDGET_EXHAUSTED`
- Exhaustion dates are stochastic — they occur earlier in high-volume periods and for promotions with large discount amounts
- Approximately 8 of the 35 promotions exhaust their budgets before the scheduled end date

---

## 9. Price Zone Architecture

Eight price zones are used to group stores by competitive pricing environment, independent of state geography. A store's price zone is determined by the competitive density and cost-of-living characteristics of its market — not its state.

| Zone | Market Type | Base Price Index | Example Markets |
|---|---|---|---|
| Zone 1 | Rural / Low-cost | 1.00 (baseline) | Small-town Georgia, rural Tennessee |
| Zone 2 | Suburban / Low-cost | 1.04 | Suburban Florida, suburban Texas |
| Zone 3 | Suburban / Mid-cost | 1.08 | Suburban Michigan, suburban Colorado |
| Zone 4 | Mid-market urban | 1.13 | Mid-size city centers |
| Zone 5 | Competitive suburban | 1.18 | High-traffic suburban corridors |
| Zone 6 | Urban / High-cost | 1.24 | Urban California, urban Washington |
| Zone 7 | Dense urban | 1.31 | Chicago, Philadelphia |
| Zone 8 | Premium urban | 1.38 | New York metro, Boston |

**Why zones don't map 1:1 to states:**
A store in Atlanta (Georgia) may be in Zone 4 while a store in rural Georgia is in Zone 1 — even though both are in the same state with the same excise tax. This reflects the real-world reality that 7-Eleven price zone assignments are market-driven, not state-driven. Cross-state zone comparisons in the dashboard surface this intentionally.

---

## 10. Transaction Volume Distribution

23,522 transactions are distributed across 619 stores and 731 days. Volume is not uniform — it reflects realistic seasonal and geographic patterns.

**Seasonality:**
- Q3 (July–September) carries the highest volume (~28% of annual transactions) reflecting summer driving and convenience store traffic peaks
- Q1 (January–March) carries the lowest volume (~22%) post-holiday
- Holidays (July 4th, Memorial Day, Labor Day) show elevated single-day volume

**Store-level distribution:**
- Top 20% of stores by volume account for approximately 45% of total transactions
- Highway and urban stores generate higher per-store volume than suburban stores
- Stores with higher tobacco door counts correlate with higher volume

**Promotional attach rate:**
- Approximately 62% of transactions occur under an active promotion
- Attach rate varies significantly by state: NY and NJ show ~35% (coupon ban effect), while TX, GA, and FL show ~70–75%
- Attach rate also varies by manufacturer: Altria (Marlboro) promotions have the highest attach rate due to program scale and budget depth

---

*For column-level definitions of all fields referenced in this document, see [data_dictionary.md](data_dictionary.md).*
