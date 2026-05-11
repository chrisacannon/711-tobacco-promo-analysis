# 711-tobacco-promo-analysis

An end-to-end data project simulating cigarette and tobacco promotional execution across a 7-Eleven-style convenience store network. Built to demonstrate pricing analytics, promotional reconciliation, and business intelligence skills in the context of a real-world retail pricing environment.

---

## Project Overview

Cigarette and tobacco pricing is one of the more analytically demanding environments in retail. A single promotional program touches state-level excise taxes, minimum price laws, flavor bans, manufacturer funding programs, price zone architecture, and store-level execution compliance — simultaneously. This project models that complexity from the ground up.

The dataset simulates two years of cigarette transactions (2023–2024) across 619 stores in 15 states, with manufacturer promotions, regulatory constraints, and reconciliation variance baked into every layer. A five-page Power BI dashboard sits on top of it, built to answer the questions a pricing analyst would actually ask.

---

## What This Project Covers

- **Star schema data modeling** — fact and dimension tables designed for direct import into Power BI
- **State-level regulatory simulation** — real excise tax rates, minimum price law enforcement, flavor bans, multipack restrictions, and coupon limitations by state
- **Manufacturer funding programs** — scan-based, guaranteed, and tiered funding models with realistic budget utilization and reconciliation variance
- **Price zone architecture** — 8 price zones reflecting competitive market clustering independent of state geography
- **Promotional execution modeling** — execution failures, wrong discounts applied, missing scan data, budget exhaustion, and reimbursement discrepancies
- **Power BI dashboard** — 5 report pages covering executive summary, promo reconciliation, manufacturer funding, store performance, and regulatory impact

---

## Repository Structure

```
711-tobacco-promo-analysis/
│
├── README.md
├── data/
│   └── 711_cigarette_promo_dataset.xlsx   # Full dataset (7 tabs)
├── scripts/
│   ├── build_dataset.py                   # Dimension + fact table generation
│   ├── style_excel.py                     # Excel formatting and styling
│   └── run.py                             # Pipeline runner
├── docs/
│   ├── data_dictionary.md                 # All tables, columns, values documented
│   ├── business_logic.md                  # Regulatory and promo rules baked into simulation
│   ├── project_structure.md               # Schema diagram and relationship map
│   └── dashboard_guide.md                 # Power BI page descriptions and DAX measures
└── images/
    └── [Power BI dashboard screenshots]
```

---

## Dataset Summary

| Table | Rows | Description |
|---|---|---|
| `fact_transactions` | 23,522 | One row per cigarette transaction |
| `dim_store` | 619 | Store attributes, price zones, regulatory region |
| `dim_product` | 39 | Brand, manufacturer, pack type, category |
| `dim_manufacturer` | 7 | Manufacturer name and funding program type |
| `dim_promotion` | 35 | Promotion details, discount type, budget, eligibility |
| `dim_regulation` | 15 | State-level tax and regulatory profiles |
| `dim_calendar` | 731 | Daily calendar with fiscal periods and holidays |

---

## Dashboard Pages

| Page | Focus |
|---|---|
| Executive Summary | KPIs, monthly volume trend, revenue by regulatory region |
| Promo Reconciliation | Execution failures, recon flag breakdown, expected vs. actual reimbursement |
| Manufacturer Funding | Budget utilization, funding program performance, promotion-level tracker |
| Store Performance | Geographic volume map, top stores, price zone analysis, volume vs. attach rate |
| Regulatory Impact | Price by state, tax composition stack, regulatory profile matrix, attach rate by region |

Screenshots of each page are in the `/images` folder.

---

## How to Run the Scripts

**Requirements:**
```
python 3.8+
pandas
numpy
openpyxl
```

**Install dependencies:**
```bash
pip install pandas numpy openpyxl
```

**Generate the dataset:**
```bash
python scripts/run.py
```

Output will be written to `data/711_cigarette_promo_dataset.xlsx`.

---

## Key Design Decisions

**Why a star schema?**
The dataset is designed to load directly into Power BI with clean relationships. The fact table contains foreign keys only — all descriptive attributes live in dimension tables. This mirrors how a real retail pricing data model would be structured.

**Why simulate reconciliation variance?**
Manufacturer reimbursement reconciliation is one of the most operationally complex parts of tobacco pricing. Modeling it with realistic failure modes — missing scans, wrong discounts, budget exhaustion — makes the dataset analytically interesting rather than just structurally correct.

**Why 15 states?**
The states were selected to represent the full range of regulatory environments — from high-tax, high-restriction markets like New York and Massachusetts to low-tax, permissive markets like Georgia and Tennessee. This creates meaningful variation in pricing, promo eligibility, and attach rates across the dataset.

---

## Author

**Chris Cannon**
[github.com/chrisacannon](https://github.com/chrisacannon) | [chrisacannon@gmail.com](mailto:chrisacannon@gmail.com)
