"""
run.py
------
Pipeline entry point for the 711-tobacco-promo-analysis dataset.

Usage (from project root):
    python scripts/run.py

What it does:
    1. Calls build_dataset.py to generate all 7 tables
    2. Writes them to data/711_cigarette_promo_dataset.xlsx (one tab per table)
    3. Calls style_excel.py to apply formatting, freeze panes, and tab colors

Output:
    data/711_cigarette_promo_dataset.xlsx
"""

import os
import sys
import time

# Allow imports from the scripts/ directory regardless of working directory
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
from build_dataset import build_all
from style_excel import style_workbook


OUTPUT_DIR  = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "711_cigarette_promo_dataset.xlsx")

# Tab order in the final workbook
TAB_ORDER = [
    "fact_transactions",
    "dim_store",
    "dim_product",
    "dim_manufacturer",
    "dim_promotion",
    "dim_regulation",
    "dim_calendar",
]


def main():
    start = time.time()
    print("=" * 60)
    print("711-tobacco-promo-analysis — dataset pipeline")
    print("=" * 60)

    # ------------------------------------------------------------------ #
    # Step 1: Generate all tables
    # ------------------------------------------------------------------ #
    print("\n[1/3] Generating tables...")
    tables = build_all()

    # ------------------------------------------------------------------ #
    # Step 2: Write to Excel
    # ------------------------------------------------------------------ #
    print(f"\n[2/3] Writing workbook to {OUTPUT_FILE} ...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        for tab_name in TAB_ORDER:
            if tab_name in tables:
                df = tables[tab_name]
                df.to_excel(writer, sheet_name=tab_name, index=False)
                print(f"  ✓ {tab_name}: {len(df):,} rows")

    # ------------------------------------------------------------------ #
    # Step 3: Apply styling
    # ------------------------------------------------------------------ #
    print(f"\n[3/3] Applying formatting...")
    style_workbook(OUTPUT_FILE)

    # ------------------------------------------------------------------ #
    # Summary
    # ------------------------------------------------------------------ #
    elapsed = round(time.time() - start, 1)
    print("\n" + "=" * 60)
    print(f"Done in {elapsed}s")
    print(f"Output: {os.path.abspath(OUTPUT_FILE)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
