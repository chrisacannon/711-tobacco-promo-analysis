"""
build_dataset.py
----------------
Generates all seven tables for the 711-tobacco-promo-analysis dataset:
    - dim_calendar
    - dim_regulation
    - dim_manufacturer
    - dim_product
    - dim_store
    - dim_promotion
    - dim_calendar

Returns a dict of DataFrames keyed by table name. Called by run.py.
"""

import pandas as pd
import numpy as np
from datetime import date, timedelta

RANDOM_SEED = 42
rng = np.random.default_rng(RANDOM_SEED)


# =============================================================================
# dim_calendar
# =============================================================================

def build_dim_calendar(start="2023-01-01", end="2024-12-31"):
    dates = pd.date_range(start=start, end=end, freq="D")

    us_holidays = {
        date(2023, 1, 1): "New Year's Day",
        date(2023, 1, 16): "Martin Luther King Jr. Day",
        date(2023, 2, 20): "Presidents' Day",
        date(2023, 5, 29): "Memorial Day",
        date(2023, 7, 4): "Independence Day",
        date(2023, 9, 4): "Labor Day",
        date(2023, 11, 23): "Thanksgiving",
        date(2023, 12, 25): "Christmas Day",
        date(2024, 1, 1): "New Year's Day",
        date(2024, 1, 15): "Martin Luther King Jr. Day",
        date(2024, 2, 19): "Presidents' Day",
        date(2024, 5, 27): "Memorial Day",
        date(2024, 7, 4): "Independence Day",
        date(2024, 9, 2): "Labor Day",
        date(2024, 11, 28): "Thanksgiving",
        date(2024, 12, 25): "Christmas Day",
    }

    rows = []
    for d in dates:
        dt = d.date()
        month = d.month
        # Fiscal year: July-June basis
        fiscal_year = d.year if month >= 7 else d.year - 1
        fiscal_month = ((month - 7) % 12) + 1  # July = 1
        fiscal_quarter = f"FQ{(fiscal_month - 1) // 3 + 1}"

        rows.append({
            "calendar_date": dt,
            "year": d.year,
            "quarter": f"Q{d.quarter}",
            "quarter_number": d.quarter,
            "month_number": month,
            "month_name": d.strftime("%B"),
            "month_short": d.strftime("%b"),
            "week_number": int(d.strftime("%V")),
            "day_of_week": d.strftime("%A"),
            "is_weekend": d.weekday() >= 5,
            "is_holiday": dt in us_holidays,
            "holiday_name": us_holidays.get(dt),
            "fiscal_year": fiscal_year,
            "fiscal_quarter": fiscal_quarter,
            "fiscal_period": fiscal_month,
            "days_in_month": pd.Timestamp(dt).days_in_month,
            "is_month_end": d == d + pd.offsets.MonthEnd(0),
            "is_quarter_end": d.month in (3, 6, 9, 12) and (d == d + pd.offsets.MonthEnd(0)),
        })

    return pd.DataFrame(rows)


# =============================================================================
# dim_regulation
# =============================================================================

def build_dim_regulation():
    states = [
        # state, state_full, excise, min_price_law, min_price_floor, min_price_includes_tax,
        # flavor_ban, flavor_ban_scope, coupon_ban, multipack_ban, regulatory_tier, region
        ("NY", "New York",       4.35,  True,  10.50, True,  True,  "Menthol + Flavored", True,  False, "High",       "Northeast"),
        ("MA", "Massachusetts",  3.51,  True,   9.00, True,  True,  "Menthol + Flavored", False, False, "High",       "Northeast"),
        ("CA", "California",     2.87,  False,  None, None,  True,  "Flavored Only",      False, False, "High",       "West"),
        ("NJ", "New Jersey",     2.70,  True,   8.00, True,  False, None,                 True,  False, "High",       "Northeast"),
        ("IL", "Illinois",       2.98,  False,  None, None,  False, None,                 False, False, "Medium",     "Midwest"),
        ("MI", "Michigan",       2.00,  False,  7.50, False, False, None,                 False, True,  "Medium",     "Midwest"),
        ("PA", "Pennsylvania",   2.60,  True,   7.25, True,  False, None,                 False, False, "Medium",     "Northeast"),
        ("WA", "Washington",     3.025, False,  None, None,  True,  "Flavored Only",      False, False, "Medium",     "West"),
        ("FL", "Florida",        1.339, False,  None, None,  False, None,                 False, False, "Low-Medium", "Southeast"),
        ("TX", "Texas",          1.41,  False,  None, None,  False, None,                 False, False, "Low",        "Southwest"),
        ("GA", "Georgia",        0.37,  False,  None, None,  False, None,                 False, False, "Low",        "Southeast"),
        ("TN", "Tennessee",      0.62,  False,  None, None,  False, None,                 False, False, "Low",        "Southeast"),
        ("AZ", "Arizona",        2.00,  False,  None, None,  False, None,                 False, False, "Low",        "Southwest"),
        ("NV", "Nevada",         1.80,  False,  None, None,  False, None,                 False, False, "Low",        "Southwest"),
        ("CO", "Colorado",       1.94,  False,  6.75, False, True,  "Flavored Only",      False, False, "Low-Medium", "West"),
    ]

    rows = []
    for s in states:
        rows.append({
            "regulation_id": f"REG-{s[0]}",
            "state": s[0],
            "state_full": s[1],
            "excise_tax_per_pack": s[2],
            "minimum_price_law": s[3],
            "minimum_price_floor": s[4],
            "min_price_includes_tax": s[5],
            "flavor_ban": s[6],
            "flavor_ban_scope": s[7],
            "coupon_ban": s[8],
            "multipack_ban": s[9],
            "regulatory_tier": s[10],
            "region": s[11],
        })

    return pd.DataFrame(rows)


# =============================================================================
# dim_manufacturer
# =============================================================================

def build_dim_manufacturer():
    data = [
        ("MFR-01", "Altria Group",          "Altria", "Tiered",      "Marlboro", True),
        ("MFR-02", "Reynolds American",      "RAI",    "Scan-Based",  "Newport",  True),
        ("MFR-03", "ITG Brands",             "ITG",    "Guaranteed",  "Winston",  True),
        ("MFR-04", "Standard General",       "StdGen", "Guaranteed",  "Pall Mall",True),
        ("MFR-05", "Vector Group",           "Vector", "Scan-Based",  "Liggett",  True),
        ("MFR-06", "Swisher International",  "Swisher","Scan-Based",  "Swisher",  True),
        ("MFR-07", "General Cigar",          "GenCigar","Guaranteed", "Macanudo", False),
    ]

    return pd.DataFrame(data, columns=[
        "manufacturer_id", "manufacturer_name", "short_name",
        "funding_program_type", "primary_brand", "active"
    ])


# =============================================================================
# dim_product
# =============================================================================

def build_dim_product():
    products = [
        # product_id, brand_name, manufacturer_id, product_family, pack_type, pack_count,
        # carton_eligible, category, flavor, flavor_ban_eligible, multipack_eligible, msrp
        ("PRD-01", "Marlboro",         "MFR-01", "Marlboro Red",       "King Box",  20, True,  "Cigarette", "Regular",  False, True,  8.99),
        ("PRD-02", "Marlboro",         "MFR-01", "Marlboro Red",       "King Soft", 20, True,  "Cigarette", "Regular",  False, True,  8.79),
        ("PRD-03", "Marlboro",         "MFR-01", "Marlboro Gold",      "King Box",  20, True,  "Cigarette", "Regular",  False, True,  8.99),
        ("PRD-04", "Marlboro",         "MFR-01", "Marlboro Menthol",   "King Box",  20, True,  "Cigarette", "Menthol",  True,  True,  8.99),
        ("PRD-05", "Marlboro",         "MFR-01", "Marlboro Black",     "King Box",  20, True,  "Cigarette", "Flavored", True,  True,  9.29),
        ("PRD-06", "Marlboro",         "MFR-01", "Marlboro 72s",       "King Box",  20, False, "Cigarette", "Regular",  False, False, 8.49),
        ("PRD-07", "Newport",          "MFR-02", "Newport Menthol",    "King Box",  20, True,  "Cigarette", "Menthol",  True,  True,  9.49),
        ("PRD-08", "Newport",          "MFR-02", "Newport Menthol",    "King Soft", 20, True,  "Cigarette", "Menthol",  True,  True,  9.29),
        ("PRD-09", "Newport",          "MFR-02", "Newport 100s",       "100s Box",  20, True,  "Cigarette", "Menthol",  True,  True,  9.49),
        ("PRD-10", "Newport",          "MFR-02", "Newport Red",        "King Box",  20, True,  "Cigarette", "Regular",  False, True,  9.49),
        ("PRD-11", "Camel",            "MFR-02", "Camel Blue",         "King Box",  20, True,  "Cigarette", "Regular",  False, True,  8.79),
        ("PRD-12", "Camel",            "MFR-02", "Camel Turkish Gold", "King Box",  20, True,  "Cigarette", "Regular",  False, True,  8.79),
        ("PRD-13", "Camel",            "MFR-02", "Camel Crush",        "King Box",  20, True,  "Cigarette", "Flavored", True,  True,  9.29),
        ("PRD-14", "Camel",            "MFR-02", "Camel Menthol",      "King Box",  20, True,  "Cigarette", "Menthol",  True,  True,  8.99),
        ("PRD-15", "Winston",          "MFR-03", "Winston Red",        "King Box",  20, True,  "Cigarette", "Regular",  False, True,  7.99),
        ("PRD-16", "Winston",          "MFR-03", "Winston Blue",       "King Box",  20, True,  "Cigarette", "Regular",  False, True,  7.99),
        ("PRD-17", "Kool",             "MFR-03", "Kool Menthol",       "King Box",  20, True,  "Cigarette", "Menthol",  True,  True,  8.49),
        ("PRD-18", "Salem",            "MFR-03", "Salem Menthol",      "King Box",  20, True,  "Cigarette", "Menthol",  True,  True,  8.29),
        ("PRD-19", "Pall Mall",        "MFR-04", "Pall Mall Red",      "King Box",  20, True,  "Cigarette", "Regular",  False, True,  7.49),
        ("PRD-20", "Pall Mall",        "MFR-04", "Pall Mall Blue",     "King Box",  20, True,  "Cigarette", "Regular",  False, True,  7.49),
        ("PRD-21", "Pall Mall",        "MFR-04", "Pall Mall Menthol",  "King Box",  20, True,  "Cigarette", "Menthol",  True,  True,  7.49),
        ("PRD-22", "Lucky Strike",     "MFR-04", "Lucky Strike Red",   "King Box",  20, True,  "Cigarette", "Regular",  False, False, 7.99),
        ("PRD-23", "Natural American", "MFR-04", "NAS Light",          "King Box",  20, True,  "Cigarette", "Regular",  False, False, 9.99),
        ("PRD-24", "Liggett Select",   "MFR-05", "Liggett Red",        "King Box",  20, True,  "Cigarette", "Regular",  False, True,  6.99),
        ("PRD-25", "Eagle 20s",        "MFR-05", "Eagle Red",          "King Box",  20, True,  "Cigarette", "Regular",  False, True,  6.49),
        ("PRD-26", "Pyramid",          "MFR-05", "Pyramid Red",        "King Box",  20, True,  "Cigarette", "Regular",  False, True,  6.49),
        ("PRD-27", "Swisher Sweets",   "MFR-06", "Swisher Original",   "Single",     1, False, "Cigar",     "Flavored", True,  False, 1.49),
        ("PRD-28", "Swisher Sweets",   "MFR-06", "Swisher Grape",      "Single",     1, False, "Cigar",     "Flavored", True,  False, 1.49),
        ("PRD-29", "Swisher Sweets",   "MFR-06", "Swisher Peach",      "Single",     1, False, "Cigar",     "Flavored", True,  False, 1.49),
        ("PRD-30", "Black & Mild",     "MFR-06", "Black & Mild Wine",  "Single",     1, False, "Cigar",     "Flavored", True,  False, 1.79),
        ("PRD-31", "Grizzly",          "MFR-02", "Grizzly WG",         "1.2oz Can",  1, False, "Smokeless", "Regular",  False, False, 4.49),
        ("PRD-32", "Grizzly",          "MFR-02", "Grizzly Mint",       "1.2oz Can",  1, False, "Smokeless", "Menthol",  True,  False, 4.49),
        ("PRD-33", "Copenhagen",       "MFR-02", "Copenhagen Long Cut","1.2oz Can",  1, False, "Smokeless", "Regular",  False, False, 5.49),
        ("PRD-34", "Skoal",            "MFR-02", "Skoal Mint",         "1.2oz Can",  1, False, "Smokeless", "Menthol",  True,  False, 5.49),
        ("PRD-35", "Levi Garrett",     "MFR-03", "Levi Garrett Loose", "3oz Pouch",  1, False, "Smokeless", "Regular",  False, False, 4.99),
        ("PRD-36", "Marlboro",         "MFR-01", "Marlboro Snus",      "Pouch Pack", 1, False, "Smokeless", "Regular",  False, False, 4.79),
        ("PRD-37", "Macanudo",         "MFR-07", "Macanudo Cafe",      "Single",     1, False, "Cigar",     "Regular",  False, False, 7.99),
        ("PRD-38", "Macanudo",         "MFR-07", "Macanudo Inspirado", "Single",     1, False, "Cigar",     "Regular",  False, False, 9.99),
        ("PRD-39", "Phillies",         "MFR-06", "Phillies Blunt",     "Single",     1, False, "Cigar",     "Flavored", True,  False, 1.29),
    ]

    return pd.DataFrame(products, columns=[
        "product_id", "brand_name", "manufacturer_id", "product_family",
        "pack_type", "pack_count", "carton_eligible", "category",
        "flavor", "flavor_ban_eligible", "multipack_eligible", "msrp"
    ])


# =============================================================================
# dim_store
# =============================================================================

def build_dim_store(dim_regulation):
    reg = dim_regulation.set_index("state")

    # Store counts per state (total = 619)
    state_store_counts = {
        "TX": 80, "FL": 75, "CA": 65, "IL": 55, "NY": 50,
        "GA": 45, "PA": 45, "TN": 40, "MI": 35, "NJ": 30,
        "AZ": 28, "WA": 25, "NV": 22, "CO": 20, "MA": 24,
    }

    # Zone assignment weights per state
    zone_weights = {
        "GA": [0.30, 0.30, 0.20, 0.15, 0.05, 0.00, 0.00, 0.00],
        "TN": [0.25, 0.30, 0.25, 0.15, 0.05, 0.00, 0.00, 0.00],
        "TX": [0.10, 0.20, 0.25, 0.25, 0.10, 0.05, 0.03, 0.02],
        "FL": [0.10, 0.20, 0.25, 0.25, 0.10, 0.05, 0.03, 0.02],
        "AZ": [0.10, 0.20, 0.25, 0.25, 0.10, 0.05, 0.03, 0.02],
        "NV": [0.05, 0.10, 0.20, 0.30, 0.20, 0.10, 0.03, 0.02],
        "CO": [0.05, 0.15, 0.25, 0.25, 0.15, 0.10, 0.03, 0.02],
        "MI": [0.05, 0.10, 0.20, 0.30, 0.20, 0.10, 0.03, 0.02],
        "WA": [0.02, 0.08, 0.15, 0.25, 0.25, 0.15, 0.07, 0.03],
        "PA": [0.02, 0.08, 0.15, 0.25, 0.25, 0.15, 0.07, 0.03],
        "CA": [0.02, 0.05, 0.10, 0.20, 0.25, 0.20, 0.12, 0.06],
        "IL": [0.02, 0.05, 0.10, 0.20, 0.25, 0.20, 0.12, 0.06],
        "NJ": [0.00, 0.02, 0.08, 0.15, 0.25, 0.25, 0.15, 0.10],
        "MA": [0.00, 0.02, 0.08, 0.15, 0.25, 0.25, 0.15, 0.10],
        "NY": [0.00, 0.00, 0.05, 0.10, 0.20, 0.25, 0.25, 0.15],
    }

    store_types = ["Urban", "Suburban", "Highway"]
    store_type_weights = {
        "Zone 1": [0.05, 0.30, 0.65],
        "Zone 2": [0.10, 0.50, 0.40],
        "Zone 3": [0.15, 0.55, 0.30],
        "Zone 4": [0.30, 0.50, 0.20],
        "Zone 5": [0.40, 0.45, 0.15],
        "Zone 6": [0.60, 0.35, 0.05],
        "Zone 7": [0.75, 0.23, 0.02],
        "Zone 8": [0.90, 0.09, 0.01],
    }

    city_pools = {
        "TX": ["Houston", "Dallas", "San Antonio", "Austin", "Fort Worth", "El Paso", "Arlington", "Plano"],
        "FL": ["Jacksonville", "Miami", "Tampa", "Orlando", "St. Petersburg", "Hialeah", "Tallahassee", "Fort Lauderdale"],
        "CA": ["Los Angeles", "San Diego", "San Jose", "San Francisco", "Fresno", "Sacramento", "Long Beach", "Oakland"],
        "IL": ["Chicago", "Aurora", "Joliet", "Naperville", "Rockford", "Springfield", "Elgin", "Peoria"],
        "NY": ["New York City", "Buffalo", "Rochester", "Yonkers", "Syracuse", "Albany", "New Rochelle", "Mount Vernon"],
        "GA": ["Atlanta", "Augusta", "Columbus", "Macon", "Savannah", "Athens", "Sandy Springs", "Roswell"],
        "PA": ["Philadelphia", "Pittsburgh", "Allentown", "Erie", "Reading", "Scranton", "Bethlehem", "Lancaster"],
        "TN": ["Memphis", "Nashville", "Knoxville", "Chattanooga", "Clarksville", "Murfreesboro", "Jackson", "Franklin"],
        "MI": ["Detroit", "Grand Rapids", "Warren", "Sterling Heights", "Ann Arbor", "Lansing", "Flint", "Dearborn"],
        "NJ": ["Newark", "Jersey City", "Paterson", "Elizabeth", "Trenton", "Camden", "Clifton", "Passaic"],
        "AZ": ["Phoenix", "Tucson", "Mesa", "Chandler", "Glendale", "Scottsdale", "Gilbert", "Tempe"],
        "WA": ["Seattle", "Spokane", "Tacoma", "Vancouver", "Bellevue", "Kent", "Everett", "Renton"],
        "NV": ["Las Vegas", "Henderson", "Reno", "North Las Vegas", "Sparks", "Carson City", "Fernley", "Elko"],
        "CO": ["Denver", "Colorado Springs", "Aurora", "Fort Collins", "Lakewood", "Thornton", "Arvada", "Westminster"],
        "MA": ["Boston", "Worcester", "Springfield", "Cambridge", "Lowell", "Brockton", "Quincy", "Lynn"],
    }

    stores = []
    store_num = 1
    for state, count in state_store_counts.items():
        reg_row = reg.loc[state]
        zones = [f"Zone {i}" for i in range(1, 9)]
        weights = zone_weights[state]
        for _ in range(count):
            zone = rng.choice(zones, p=weights)
            store_type = rng.choice(store_types, p=store_type_weights[zone])
            door_count = rng.choice([2, 3, 4], p=[0.3, 0.5, 0.2])
            open_date = date(2023, 1, 1) if rng.random() > 0.15 else date(2023, int(rng.integers(2, 7)), 1)
            city = rng.choice(city_pools[state])
            stores.append({
                "store_id": f"STR-{store_num:04d}",
                "store_name": f"7-Eleven #{store_num:04d}",
                "city": city,
                "state": state,
                "state_full": reg_row["state_full"],
                "regulation_id": reg_row["regulation_id"],
                "price_zone": zone,
                "price_zone_id": int(zone.split()[-1]),
                "region": reg_row["region"],
                "store_open_date": open_date,
                "store_type": store_type,
                "tobacco_door_count": door_count,
            })
            store_num += 1

    return pd.DataFrame(stores)


# =============================================================================
# dim_promotion
# =============================================================================

def build_dim_promotion():
    promotions = []
    promo_num = 1

    # Format: (name_template, mfr_id, discount_type, discount_amt,
    #          start, end, budget, multipack_required, flavor_restricted,
    #          coupon_restricted_states, scan_required, eligible_states)
    promo_specs = [
        # Altria (Tiered)
        ("Marlboro Q1 Pack Discount",        "MFR-01", "Off-Invoice", 0.50, "2023-01-01", "2023-03-31", 120000, False, False, None,    False, "ALL"),
        ("Marlboro Q2 Summer Promo",         "MFR-01", "Scan",        0.75, "2023-04-01", "2023-06-30", 150000, False, False, "NY|NJ", True,  "ALL"),
        ("Marlboro Q3 Peak Season",          "MFR-01", "Off-Invoice", 1.00, "2023-07-01", "2023-09-30", 180000, False, False, None,    False, "ALL"),
        ("Marlboro Q4 Year-End",             "MFR-01", "Scan",        0.50, "2023-10-01", "2023-12-31", 110000, False, False, "NY|NJ", True,  "ALL"),
        ("Marlboro 2024 Q1 Pack Discount",   "MFR-01", "Off-Invoice", 0.50, "2024-01-01", "2024-03-31", 125000, False, False, None,    False, "ALL"),
        ("Marlboro 2024 Q2 Promo",           "MFR-01", "Scan",        0.75, "2024-04-01", "2024-06-30", 155000, False, False, "NY|NJ", True,  "ALL"),
        ("Marlboro 2024 Q3 Peak",            "MFR-01", "Off-Invoice", 1.00, "2024-07-01", "2024-09-30", 185000, False, False, None,    False, "ALL"),
        ("Marlboro Multipack Q2",            "MFR-01", "Buy-Down",    0.50, "2023-04-01", "2023-06-30",  60000, True,  False, "NY|NJ", False, "TX|FL|GA|TN|AZ|NV|CO"),
        # Reynolds American (Scan-Based)
        ("Newport Q1 Scan Promo",            "MFR-02", "Scan",        0.75, "2023-01-01", "2023-03-31", 100000, False, False, "NY|NJ", True,  "ALL"),
        ("Newport Summer Scan",              "MFR-02", "Scan",        1.00, "2023-06-01", "2023-08-31", 130000, False, False, "NY|NJ", True,  "ALL"),
        ("Newport Q4 Scan",                  "MFR-02", "Scan",        0.75, "2023-10-01", "2023-12-31",  95000, False, False, "NY|NJ", True,  "ALL"),
        ("Newport 2024 H1 Scan",             "MFR-02", "Scan",        0.75, "2024-01-01", "2024-06-30", 200000, False, False, "NY|NJ", True,  "ALL"),
        ("Newport 2024 H2 Scan",             "MFR-02", "Scan",        1.00, "2024-07-01", "2024-12-31", 220000, False, False, "NY|NJ", True,  "ALL"),
        ("Camel Q2 Promo",                   "MFR-02", "Scan",        0.50, "2023-04-01", "2023-06-30",  55000, False, False, "NY|NJ", True,  "ALL"),
        ("Camel Q3 Peak",                    "MFR-02", "Scan",        0.75, "2023-07-01", "2023-09-30",  70000, False, False, "NY|NJ", True,  "ALL"),
        ("Camel 2024 Annual Scan",           "MFR-02", "Scan",        0.50, "2024-01-01", "2024-12-31", 110000, False, False, "NY|NJ", True,  "ALL"),
        ("Grizzly Smokeless Q3",             "MFR-02", "Scan",        0.35, "2023-07-01", "2023-09-30",  30000, False, False, None,    True,  "ALL"),
        # ITG Brands (Guaranteed)
        ("Winston Annual Guaranteed",        "MFR-03", "Off-Invoice", 0.50, "2023-01-01", "2023-12-31",  80000, False, False, None,    False, "ALL"),
        ("Kool Menthol Q2",                  "MFR-03", "Off-Invoice", 0.50, "2023-04-01", "2023-06-30",  25000, False, True,  None,    False, "ALL"),
        ("Salem Q3 Guaranteed",              "MFR-03", "Buy-Down",    0.35, "2023-07-01", "2023-09-30",  18000, False, True,  None,    False, "ALL"),
        ("Winston 2024 Guaranteed",          "MFR-03", "Off-Invoice", 0.50, "2024-01-01", "2024-12-31",  85000, False, False, None,    False, "ALL"),
        ("Kool 2024 Q1",                     "MFR-03", "Off-Invoice", 0.35, "2024-01-01", "2024-03-31",  15000, False, True,  None,    False, "ALL"),
        # Standard General (Guaranteed)
        ("Pall Mall Annual Guaranteed",      "MFR-04", "Off-Invoice", 0.50, "2023-01-01", "2023-12-31",  70000, False, False, None,    False, "ALL"),
        ("Pall Mall Q3 Buy-Down",            "MFR-04", "Buy-Down",    0.75, "2023-07-01", "2023-09-30",  45000, False, False, None,    False, "ALL"),
        ("Pall Mall 2024 Guaranteed",        "MFR-04", "Off-Invoice", 0.50, "2024-01-01", "2024-12-31",  72000, False, False, None,    False, "ALL"),
        ("Lucky Strike Q2",                  "MFR-04", "Off-Invoice", 0.35, "2023-04-01", "2023-06-30",  12000, False, False, None,    False, "TX|FL|GA|TN|AZ|NV"),
        # Vector Group (Scan-Based)
        ("Eagle 20s Annual Scan",            "MFR-05", "Scan",        0.50, "2023-01-01", "2023-12-31",  40000, False, False, "NY|NJ", True,  "ALL"),
        ("Pyramid Q3 Promo",                 "MFR-05", "Scan",        0.35, "2023-07-01", "2023-09-30",  15000, False, False, "NY|NJ", True,  "ALL"),
        ("Eagle 20s 2024 Scan",              "MFR-05", "Scan",        0.50, "2024-01-01", "2024-12-31",  42000, False, False, "NY|NJ", True,  "ALL"),
        # Swisher (Scan-Based)
        ("Swisher Sweets Annual Scan",       "MFR-06", "Scan",        0.25, "2023-01-01", "2023-12-31",  35000, False, True,  None,    True,  "ALL"),
        ("Black & Mild Q3",                  "MFR-06", "Scan",        0.20, "2023-07-01", "2023-09-30",  10000, False, True,  None,    True,  "ALL"),
        ("Swisher 2024 Annual Scan",         "MFR-06", "Scan",        0.25, "2024-01-01", "2024-12-31",  37000, False, True,  None,    True,  "ALL"),
        ("Phillies Q2",                      "MFR-06", "Scan",        0.15, "2023-04-01", "2023-06-30",   8000, False, True,  None,    True,  "ALL"),
        # General Cigar (Guaranteed)
        ("Macanudo Premium Q2",              "MFR-07", "Guaranteed",  0.75, "2023-04-01", "2023-06-30",   9000, False, False, None,    False, "ALL"),
        ("Macanudo 2024 Promo",              "MFR-07", "Guaranteed",  0.75, "2024-04-01", "2024-09-30",  14000, False, False, None,    False, "ALL"),
    ]

    rows = []
    for i, p in enumerate(promo_specs, 1):
        budget = p[8 + 3]  # budget_total
        util_pct = round(rng.uniform(0.72, 0.99), 3)
        exhausted = util_pct > 0.97
        if exhausted:
            util_pct = 1.00

        rows.append({
            "promotion_id": f"PRM-{i:02d}",
            "promotion_name": p[0],
            "manufacturer_id": p[1],
            "discount_type": p[2],
            "discount_amount": p[3],
            "promo_start_date": pd.to_datetime(p[4]).date(),
            "promo_end_date": pd.to_datetime(p[5]).date(),
            "budget_total": p[6],
            "budget_utilized": round(p[6] * util_pct, 2),
            "budget_utilization_pct": util_pct,
            "budget_exhausted_flag": exhausted,
            "multipack_required": p[7],
            "flavor_restricted": p[8],
            "coupon_restricted_states": p[9],
            "scan_required": p[10],
            "eligible_states": p[11],
        })

    return pd.DataFrame(rows)


# =============================================================================
# fact_transactions
# =============================================================================

def build_fact_transactions(dim_store, dim_product, dim_promotion,
                             dim_regulation, dim_calendar, target_rows=23522):
    reg_lookup = dim_regulation.set_index("regulation_id")
    promo_df = dim_promotion.copy()
    product_df = dim_product.copy()

    # Price zone base multipliers
    zone_multipliers = {
        1: 1.00, 2: 1.04, 3: 1.08, 4: 1.13,
        5: 1.18, 6: 1.24, 7: 1.31, 8: 1.38,
    }

    # Seasonality weights by month (index 0 = Jan)
    month_weights = [0.072, 0.068, 0.075, 0.078, 0.085, 0.088,
                     0.095, 0.092, 0.082, 0.080, 0.075, 0.070]
    month_weights = [w / sum(month_weights) for w in month_weights]

    all_dates = dim_calendar["calendar_date"].tolist()
    stores = dim_store.to_dict("records")

    recon_flags = ["CLEAN", "MISSING_SCAN", "WRONG_DISCOUNT", "BUDGET_EXHAUSTED", "PARTIAL_REIMB"]

    transactions = []
    txn_id = 1

    # Sample (store, date) pairs weighted by seasonality
    date_months = [d.month for d in all_dates]
    date_weights = [month_weights[m - 1] for m in date_months]
    date_weights = [w / sum(date_weights) for w in date_weights]

    sampled_dates = rng.choice(all_dates, size=target_rows, p=date_weights, replace=True)
    sampled_store_indices = rng.integers(0, len(stores), size=target_rows)

    for i in range(target_rows):
        txn_date = sampled_dates[i]
        store = stores[sampled_store_indices[i]]
        state = store["state"]
        reg_id = store["regulation_id"]
        reg = reg_lookup.loc[reg_id]
        zone_id = store["price_zone_id"]
        zone_mult = zone_multipliers[zone_id]

        # Eligible products (flavor ban suppression)
        eligible_products = product_df.copy()
        if reg["flavor_ban"]:
            scope = reg["flavor_ban_scope"]
            if scope == "Menthol + Flavored":
                eligible_products = eligible_products[
                    ~eligible_products["flavor"].isin(["Menthol", "Flavored"])
                ]
            elif scope == "Flavored Only":
                eligible_products = eligible_products[
                    eligible_products["flavor"] != "Flavored"
                ]

        if len(eligible_products) == 0:
            eligible_products = product_df  # fallback

        product = eligible_products.sample(1, random_state=int(rng.integers(0, 99999))).iloc[0]
        mfr_id = product["manufacturer_id"]

        # Eligible promotions
        eligible_promos = promo_df[
            (pd.to_datetime(promo_df["promo_start_date"]) <= pd.Timestamp(txn_date)) &
            (pd.to_datetime(promo_df["promo_end_date"]) >= pd.Timestamp(txn_date)) &
            (promo_df["manufacturer_id"] == mfr_id) &
            (~promo_df["budget_exhausted_flag"])
        ]

        # Coupon ban filter
        if reg["coupon_ban"]:
            eligible_promos = eligible_promos[
                eligible_promos["coupon_restricted_states"].isna() |
                ~eligible_promos["coupon_restricted_states"].str.contains(state, na=False)
            ]

        # Multipack ban filter
        if reg["multipack_ban"]:
            eligible_promos = eligible_promos[~eligible_promos["multipack_required"]]

        # State eligibility filter
        eligible_promos = eligible_promos[
            (eligible_promos["eligible_states"] == "ALL") |
            eligible_promos["eligible_states"].str.contains(state, na=False)
        ]

        # Flavor restriction filter
        if product["flavor"] in ["Menthol", "Flavored"]:
            eligible_promos = eligible_promos[~eligible_promos["flavor_restricted"]]

        # Apply promotion
        promo_id = None
        discount = 0.00
        expected_reimb = 0.00
        scan_required = False

        if len(eligible_promos) > 0 and rng.random() < 0.72:
            promo = eligible_promos.sample(1, random_state=int(rng.integers(0, 99999))).iloc[0]
            promo_id = promo["promotion_id"]
            discount = promo["discount_amount"]
            expected_reimb = discount
            scan_required = promo["scan_required"]

        # Pricing
        base_price = round(product["msrp"] * zone_mult + rng.uniform(-0.10, 0.20), 2)
        excise_tax = round(float(reg["excise_tax_per_pack"]), 3)
        final_price = round(base_price - discount, 2)

        # Minimum price enforcement
        min_price_floor = reg["minimum_price_floor"]
        min_price_violation = False
        if pd.notna(min_price_floor) and min_price_floor is not None:
            if rng.random() < 0.025:  # ~2.5% violation rate
                min_price_violation = final_price < float(min_price_floor)
            else:
                if final_price < float(min_price_floor):
                    final_price = float(min_price_floor)

        units = int(rng.choice([1, 2, 3], p=[0.75, 0.18, 0.07]))

        # Reconciliation
        execution_failure = False
        scan_present = True
        actual_reimb = expected_reimb
        recon_flag = "CLEAN"

        if promo_id is not None:
            failure_roll = rng.random()
            if scan_required and rng.random() < 0.04:
                scan_present = False
                actual_reimb = 0.00
                recon_flag = "MISSING_SCAN"
                execution_failure = True
            elif failure_roll < 0.03:
                wrong_discount = round(discount * rng.choice([0.5, 1.5]), 2)
                actual_reimb = wrong_discount
                recon_flag = "WRONG_DISCOUNT"
                execution_failure = True
            elif failure_roll < 0.05:
                actual_reimb = round(expected_reimb * rng.uniform(0.5, 0.9), 2)
                recon_flag = "PARTIAL_REIMB"
            elif failure_roll < 0.06:
                actual_reimb = 0.00
                recon_flag = "BUDGET_EXHAUSTED"
            elif failure_roll < 0.075:
                execution_failure = True

        recon_variance = round(actual_reimb - expected_reimb, 4)

        transactions.append({
            "transaction_id": f"TXN-{txn_id:05d}",
            "transaction_date": txn_date,
            "store_id": store["store_id"],
            "product_id": product["product_id"],
            "promotion_id": promo_id,
            "manufacturer_id": mfr_id,
            "regulation_id": reg_id,
            "calendar_date": txn_date,
            "units_sold": units,
            "base_price": base_price,
            "excise_tax_applied": excise_tax,
            "promo_discount_applied": discount,
            "final_price": final_price,
            "minimum_price_floor": float(min_price_floor) if pd.notna(min_price_floor) and min_price_floor is not None else None,
            "min_price_violation_flag": min_price_violation,
            "expected_reimbursement": round(expected_reimb, 2),
            "actual_reimbursement": round(actual_reimb, 2),
            "recon_variance": recon_variance,
            "recon_flag": recon_flag,
            "execution_failure_flag": execution_failure,
            "scan_data_present": scan_present,
        })
        txn_id += 1

    return pd.DataFrame(transactions)


# =============================================================================
# Main entry point
# =============================================================================

def build_all():
    print("Building dim_calendar...")
    dim_calendar = build_dim_calendar()

    print("Building dim_regulation...")
    dim_regulation = build_dim_regulation()

    print("Building dim_manufacturer...")
    dim_manufacturer = build_dim_manufacturer()

    print("Building dim_product...")
    dim_product = build_dim_product()

    print("Building dim_store...")
    dim_store = build_dim_store(dim_regulation)

    print("Building dim_promotion...")
    dim_promotion = build_dim_promotion()

    print("Building fact_transactions (this may take a moment)...")
    fact_transactions = build_fact_transactions(
        dim_store, dim_product, dim_promotion,
        dim_regulation, dim_calendar
    )

    print(f"  → {len(fact_transactions):,} transactions generated")

    return {
        "fact_transactions": fact_transactions,
        "dim_store": dim_store,
        "dim_product": dim_product,
        "dim_manufacturer": dim_manufacturer,
        "dim_promotion": dim_promotion,
        "dim_regulation": dim_regulation,
        "dim_calendar": dim_calendar,
    }


if __name__ == "__main__":
    tables = build_all()
    for name, df in tables.items():
        print(f"  {name}: {len(df):,} rows, {len(df.columns)} columns")
