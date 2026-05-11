# Dashboard Guide

**Project:** 711-tobacco-promo-analysis  
**Tool:** Power BI Desktop  
**Pages:** 5  
**Screenshots:** `/images/` folder

This document describes each dashboard page — the business question it answers, the visuals it contains, and the DAX measures powering it. Since the `.pbix` file is not published, this guide is the primary reference for understanding what was built and why.

---

## Page 1: Executive Summary

**Business question:** How is the overall business performing, and where are the headline risks?

This is the entry point for a hiring manager or executive. It provides top-line KPIs, volume trend, and revenue decomposition without requiring any navigation.

![Executive Summary Dashboard](../images/dashboard_executive_summary.png)

### Visuals

| Visual | Type | Description |
|---|---|---|
| Total Revenue | KPI card | Sum of `final_price × units_sold` across all transactions; YTD with prior year comparison |
| Total Units Sold | KPI card | Sum of `units_sold`; YTD with prior year comparison |
| Promo Attach Rate | KPI card | % of transactions with an active promotion; highlights coupon-ban state effect |
| Recon Variance (Net) | KPI card | Sum of `recon_variance`; negative value = net shortfall vs. expected reimbursement |
| Monthly Volume Trend | Line chart | Units sold by month, 2023 vs. 2024 overlay; seasonality and YoY comparison |
| Revenue by Regulatory Region | Bar chart | Total revenue grouped by `dim_regulation.regulatory_tier` (High / Medium / Low) |
| Revenue by Manufacturer | Donut chart | Revenue share by manufacturer; shows Altria/RAI market concentration |
| Execution Failure Rate | KPI card | % of transactions with `execution_failure_flag = TRUE` |

### Key DAX Measures

```dax
Total Revenue = 
SUMX(
    fact_transactions,
    fact_transactions[final_price] * fact_transactions[units_sold]
)

Promo Attach Rate = 
DIVIDE(
    COUNTROWS(FILTER(fact_transactions, NOT ISBLANK(fact_transactions[promotion_id]))),
    COUNTROWS(fact_transactions)
)

Recon Variance Net = 
SUM(fact_transactions[recon_variance])

Execution Failure Rate = 
DIVIDE(
    COUNTROWS(FILTER(fact_transactions, fact_transactions[execution_failure_flag] = TRUE())),
    COUNTROWS(fact_transactions)
)

Revenue YoY Change = 
VAR CurrentYear = [Total Revenue]
VAR PriorYear = CALCULATE([Total Revenue], SAMEPERIODLASTYEAR(dim_calendar[calendar_date]))
RETURN DIVIDE(CurrentYear - PriorYear, PriorYear)
```

---

## Page 2: Promo Reconciliation

**Business question:** Where is the promotional reimbursement process breaking down, and how much money is at risk?

This is the most operationally focused page. It answers the questions a pricing analyst would ask after month-end close: how much did we expect, how much did we get, and what caused the gap?

![Promo Reconciliation Dashboard](../images/dashboard_promo_reconciliation.png)

### Visuals

| Visual | Type | Description |
|---|---|---|
| Expected vs. Actual Reimbursement | Clustered bar | Side-by-side comparison by manufacturer; gap = reconciliation shortfall |
| Recon Flag Breakdown | Stacked bar | Transaction count by `recon_flag` category; shows failure mode distribution |
| Variance Over Time | Line chart | Net `recon_variance` by month; surfaces budget exhaustion timing |
| Top 10 Stores by Variance | Table | Stores with highest cumulative negative variance; execution risk signals |
| Scan Data Missing Rate | KPI card | % of scan-required transactions with `scan_data_present = FALSE` |
| Budget Exhaustion Events | Table | Promotions where `budget_exhausted_flag = TRUE`, with exhaustion date and remaining period |

### Key DAX Measures

```dax
Expected Reimbursement Total = 
SUM(fact_transactions[expected_reimbursement])

Actual Reimbursement Total = 
SUM(fact_transactions[actual_reimbursement])

Recon Shortfall = 
[Expected Reimbursement Total] - [Actual Reimbursement Total]

Shortfall Rate = 
DIVIDE([Recon Shortfall], [Expected Reimbursement Total])

Missing Scan Rate = 
DIVIDE(
    COUNTROWS(
        FILTER(fact_transactions,
            fact_transactions[scan_data_present] = FALSE()
            && NOT ISBLANK(fact_transactions[promotion_id])
        )
    ),
    COUNTROWS(FILTER(fact_transactions, NOT ISBLANK(fact_transactions[promotion_id])))
)

Transactions by Recon Flag = 
CALCULATE(
    COUNTROWS(fact_transactions),
    ALLEXCEPT(fact_transactions, fact_transactions[recon_flag])
)
```

---

## Page 3: Manufacturer Funding

**Business question:** Which manufacturers and funding programs are performing, and how is budget being utilized?

This page is designed for the manufacturer account management side of the business — tracking how promotional dollars are being deployed and where program performance is strong or weak.

![Manufacturer Funding Dashboard](../images/dashboard_manufacturer_funding.png)

### Visuals

| Visual | Type | Description |
|---|---|---|
| Budget Utilization by Manufacturer | Bar chart | `budget_utilization_pct` by manufacturer; 100% = budget exhausted |
| Funding Program Type Comparison | Clustered bar | Recon shortfall rate by funding program type (Scan-Based / Guaranteed / Tiered) |
| Promotion-Level Tracker | Matrix table | One row per promotion: budget, utilized, utilization %, exhausted flag, recon variance |
| Revenue per Promo Dollar | KPI card | Total revenue generated per $1 of manufacturer funding |
| Active Promotions Timeline | Gantt-style bar | Promotion date ranges with budget exhaustion events marked |
| Manufacturer Attach Rate | Bar chart | Promo attach rate by manufacturer; shows promotional coverage depth |

### Key DAX Measures

```dax
Budget Utilization Pct = 
DIVIDE(
    SUM(dim_promotion[budget_utilized]),
    SUM(dim_promotion[budget_total])
)

Revenue per Promo Dollar = 
DIVIDE(
    [Total Revenue],
    [Actual Reimbursement Total]
)

Promotions Exhausted = 
CALCULATE(
    COUNTROWS(dim_promotion),
    dim_promotion[budget_exhausted_flag] = TRUE()
)

Attach Rate by Manufacturer = 
CALCULATE(
    [Promo Attach Rate],
    ALLEXCEPT(fact_transactions, fact_transactions[manufacturer_id])
)

Funding Program Shortfall Rate = 
CALCULATE(
    [Shortfall Rate],
    ALLEXCEPT(dim_promotion, dim_promotion[discount_type])
)
```

---

## Page 4: Store Performance

**Business question:** Which stores are driving volume, and how does performance vary across price zones and geographies?

This page supports field operations and zone management. It surfaces which stores are over- or under-performing relative to their zone peers and where execution quality is weakest.

![Store Performance Dashboard](../images/dashboard_store_performance.png)

### Visuals

| Visual | Type | Description |
|---|---|---|
| Geographic Volume Map | Filled map | Units sold by state; color intensity = volume |
| Top 20 Stores by Revenue | Bar chart | Horizontal bar; store name + city label |
| Price Zone Revenue Comparison | Clustered bar | Revenue by price zone; illustrates zone pricing premium effect |
| Volume vs. Attach Rate Scatter | Scatter plot | One dot per store; X = units sold, Y = promo attach rate; outliers = execution issues |
| Execution Failure by Store Type | Bar chart | Failure rate segmented by `store_type` (Urban / Suburban / Highway) |
| Store Performance Table | Table | Filterable by state/zone; columns: revenue, units, attach rate, failure rate, recon variance |

### Key DAX Measures

```dax
Store Revenue = 
CALCULATE(
    [Total Revenue],
    ALLEXCEPT(dim_store, dim_store[store_id])
)

Zone Average Revenue = 
CALCULATE(
    AVERAGEX(
        VALUES(dim_store[store_id]),
        [Store Revenue]
    ),
    ALLEXCEPT(dim_store, dim_store[price_zone])
)

Store vs Zone Index = 
DIVIDE([Store Revenue], [Zone Average Revenue])

Execution Failure Rate by Store = 
CALCULATE(
    [Execution Failure Rate],
    ALLEXCEPT(dim_store, dim_store[store_id])
)
```

---

## Page 5: Regulatory Impact

**Business question:** How do state-level regulatory environments affect pricing, promotional eligibility, and revenue performance?

This is the most analytically distinctive page in the dashboard — it's what makes this project interesting to a pricing or regulatory analyst. It connects compliance data to business outcomes.

![Regulatory Impact Dashboard](../images/dashboard_regulatory_impact.png)

### Visuals

| Visual | Type | Description |
|---|---|---|
| Average Price by State | Bar chart | `avg(final_price)` by state; sorted descending; excise tax contribution visible via tooltip |
| Tax Composition Stack | 100% stacked bar | For each state: excise tax as % of shelf price vs. non-tax price component |
| Regulatory Profile Matrix | Matrix table | States as rows; regulatory features as columns (min price law, flavor ban, coupon ban, multipack ban); TRUE/FALSE values color-coded |
| Attach Rate by Regulatory Tier | Bar chart | Promo attach rate for High / Medium / Low regulatory tiers; coupon ban states suppress attach rate visibly |
| Minimum Price Violation Tracker | KPI card + table | Count and rate of `min_price_violation_flag = TRUE`; table shows violations by state and store |
| Flavor Ban Impact | Clustered bar | Menthol and flavored product share in ban vs. non-ban states; side-by-side comparison |

### Key DAX Measures

```dax
Avg Final Price = 
AVERAGE(fact_transactions[final_price])

Excise Tax Share = 
DIVIDE(
    AVERAGE(fact_transactions[excise_tax_applied]),
    AVERAGE(fact_transactions[final_price])
)

Min Price Violation Rate = 
DIVIDE(
    COUNTROWS(FILTER(fact_transactions, fact_transactions[min_price_violation_flag] = TRUE())),
    COUNTROWS(fact_transactions)
)

Attach Rate by Tier = 
CALCULATE(
    [Promo Attach Rate],
    ALLEXCEPT(dim_regulation, dim_regulation[regulatory_tier])
)

Menthol Share = 
DIVIDE(
    CALCULATE(
        SUM(fact_transactions[units_sold]),
        dim_product[flavor] = "Menthol"
    ),
    SUM(fact_transactions[units_sold])
)

Flavored Product Share = 
DIVIDE(
    CALCULATE(
        SUM(fact_transactions[units_sold]),
        dim_product[flavor] = "Flavored"
    ),
    SUM(fact_transactions[units_sold])
)
```

---

## Using This Dashboard for Interviews

The five pages are designed to answer interview questions in sequence:

- **"Walk me through the project"** → Executive Summary gives you the overview
- **"How did you handle complexity in the data?"** → Business logic is in the dataset; Promo Reconciliation shows it analytically
- **"How would you present this to a non-technical stakeholder?"** → Executive Summary and Regulatory Impact were built for that audience
- **"Show me a DAX measure you're proud of"** → The `Revenue YoY Change`, `Store vs Zone Index`, or `Funding Program Shortfall Rate` measures all show deliberate design thinking

---

*For field definitions of all columns referenced in this guide, see [data_dictionary.md](data_dictionary.md).*  
*For the simulation rules behind the data, see [business_logic.md](business_logic.md).*
