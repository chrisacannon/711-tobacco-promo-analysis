"""
style_excel.py
--------------
Applies professional formatting to the 711_cigarette_promo_dataset.xlsx workbook.
Expects a workbook already written by run.py (via build_dataset.py).
Called by run.py after the data has been written to disk.

Formatting applied per sheet:
    - Bold header row with background fill
    - Freeze panes on row 1
    - Auto-fit column widths
    - Number formatting (currency, percentage, boolean)
    - Tab color coding by table type (fact vs. dimension)
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


# Tab colors (hex, no #)
TAB_COLORS = {
    "fact_transactions": "2E4057",   # dark navy — fact table stands out
    "dim_store":         "4A7C59",   # muted green
    "dim_product":       "4A7C59",
    "dim_manufacturer":  "4A7C59",
    "dim_promotion":     "4A7C59",
    "dim_regulation":    "4A7C59",
    "dim_calendar":      "4A7C59",
}

# Header fill colors
HEADER_FILL_FACT = PatternFill(fill_type="solid", fgColor="2E4057")
HEADER_FILL_DIM  = PatternFill(fill_type="solid", fgColor="4A7C59")
HEADER_FONT      = Font(bold=True, color="FFFFFF", size=10)
BODY_FONT        = Font(size=10)

# Thin border for header bottom edge
THIN = Side(style="thin", color="CCCCCC")
HEADER_BORDER = Border(bottom=THIN)

# Column width limits
MIN_WIDTH = 10
MAX_WIDTH = 40


def _auto_width(ws):
    """Set column widths based on max content length, clamped to MIN/MAX."""
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            try:
                val = str(cell.value) if cell.value is not None else ""
                max_len = max(max_len, len(val))
            except Exception:
                pass
        ws.column_dimensions[col_letter].width = max(MIN_WIDTH, min(MAX_WIDTH, max_len + 3))


def _format_header_row(ws, is_fact=False):
    """Bold, colored header row with freeze panes."""
    fill = HEADER_FILL_FACT if is_fact else HEADER_FILL_DIM
    for cell in ws[1]:
        cell.font = HEADER_FONT
        cell.fill = fill
        cell.alignment = Alignment(horizontal="left", vertical="center")
        cell.border = HEADER_BORDER
    ws.freeze_panes = "A2"
    ws.row_dimensions[1].height = 18


def _apply_number_formats(ws, sheet_name):
    """Apply column-level number formats based on known column names."""
    headers = {cell.value: cell.column for cell in ws[1]}

    currency_cols = {
        "base_price", "excise_tax_applied", "promo_discount_applied",
        "final_price", "minimum_price_floor", "expected_reimbursement",
        "actual_reimbursement", "recon_variance", "msrp",
        "discount_amount", "budget_total", "budget_utilized",
        "excise_tax_per_pack",
    }
    pct_cols = {"budget_utilization_pct"}
    int_cols = {"units_sold", "pack_count", "price_zone_id",
                "tobacco_door_count", "fiscal_period", "week_number",
                "month_number", "quarter_number", "days_in_month",
                "year", "fiscal_year"}

    for col_name, col_idx in headers.items():
        col_letter = get_column_letter(col_idx)
        if col_name in currency_cols:
            for row in ws.iter_rows(min_row=2, min_col=col_idx, max_col=col_idx):
                for cell in row:
                    cell.number_format = '"$"#,##0.00'
        elif col_name in pct_cols:
            for row in ws.iter_rows(min_row=2, min_col=col_idx, max_col=col_idx):
                for cell in row:
                    cell.number_format = "0.0%"
        elif col_name in int_cols:
            for row in ws.iter_rows(min_row=2, min_col=col_idx, max_col=col_idx):
                for cell in row:
                    cell.number_format = "0"


def _set_tab_color(ws, sheet_name):
    color = TAB_COLORS.get(sheet_name, "888888")
    ws.sheet_properties.tabColor = color


def _style_body_rows(ws):
    """Apply consistent body font and alternating row shading."""
    alt_fill = PatternFill(fill_type="solid", fgColor="F5F5F5")
    for i, row in enumerate(ws.iter_rows(min_row=2), start=2):
        for cell in row:
            cell.font = BODY_FONT
            cell.alignment = Alignment(horizontal="left", vertical="center")
            if i % 2 == 0:
                if cell.fill.fill_type != "solid" or cell.fill.fgColor.rgb in ("00000000", "FFFFFFFF"):
                    cell.fill = alt_fill
    ws.row_dimensions[1].height = 18


def style_workbook(filepath):
    """
    Load the workbook at `filepath`, apply all formatting, and save in place.
    """
    print(f"Styling workbook: {filepath}")
    wb = openpyxl.load_workbook(filepath)

    # Preferred sheet order
    preferred_order = [
        "fact_transactions",
        "dim_store",
        "dim_product",
        "dim_manufacturer",
        "dim_promotion",
        "dim_regulation",
        "dim_calendar",
    ]
    existing = wb.sheetnames
    ordered = [s for s in preferred_order if s in existing]
    ordered += [s for s in existing if s not in ordered]

    # Reorder sheets
    for i, name in enumerate(ordered):
        wb.move_sheet(name, offset=wb.sheetnames.index(name) - i)

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        is_fact = sheet_name == "fact_transactions"

        print(f"  Formatting sheet: {sheet_name} ({ws.max_row - 1:,} rows)")
        _set_tab_color(ws, sheet_name)
        _format_header_row(ws, is_fact=is_fact)
        _apply_number_formats(ws, sheet_name)
        _auto_width(ws)
        # Skip alternating rows on large fact table for performance
        if not is_fact:
            _style_body_rows(ws)
        else:
            for row in ws.iter_rows(min_row=2):
                for cell in row:
                    cell.font = BODY_FONT
                    cell.alignment = Alignment(horizontal="left", vertical="center")

    wb.save(filepath)
    print(f"Workbook saved: {filepath}")


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "data/711_cigarette_promo_dataset.xlsx"
    style_workbook(path)
