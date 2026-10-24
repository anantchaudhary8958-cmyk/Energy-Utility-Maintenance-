"""
import_export.py
Module for Excel data migration, CSV export, and styled Excel report generation
for the Energy & Utility Maintenance Management Dashboard.
"""

import io
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
import pandas as pd

from database import add_utility_record, check_duplicate_record, get_connection, update_utility_record
from validation import validate_record_input

EXCEL_COLUMN_MAP = {
    "Month": "month",
    "Utility System": "utility_system",
    "Total Energy Consumption (kWh)": "total_energy_kwh",
    "Energy Consumption per Unit of Production (kWh)": "energy_per_unit_kwh",
    "Utility Downtime (Hours)": "downtime_hours",
    "Energy Cost per Unit Produced": "energy_cost_per_unit",
    "Peak Energy Demand (kW)": "peak_demand_kw",
    "Utility Equipment Availability (%)": "equipment_availability",
    "Energy Efficiency Ratio": "energy_efficiency_ratio",
    "Water Consumption per Unit Produced (Liters)": "water_per_unit_liters",
    "Energy Loss / Waste (%)": "energy_loss_pct",
    "Maintenance Cost of Utility Systems": "maintenance_cost"
}

REVERSE_DISPLAY_MAP = {
    "id": "Record ID",
    "year": "Reporting Year",
    "month": "Month",
    "utility_system": "Utility System",
    "total_energy_kwh": "Total Energy Consumption (kWh)",
    "energy_per_unit_kwh": "Energy Consumption / Unit (kWh)",
    "downtime_hours": "Utility Downtime (Hours)",
    "energy_cost_per_unit": "Energy Cost / Unit Produced ($)",
    "peak_demand_kw": "Peak Energy Demand (kW)",
    "equipment_availability": "Equipment Availability (%)",
    "energy_efficiency_ratio": "Energy Efficiency Ratio",
    "water_per_unit_liters": "Water Consumption / Unit (Liters)",
    "energy_loss_pct": "Energy Loss / Waste (%)",
    "maintenance_cost": "Maintenance Cost ($)",
    "notes": "Notes",
    "created_at": "Created At",
    "updated_at": "Updated At"
}


def parse_and_validate_excel(
    file_source: Any,
    target_year: int = 2026,
    sheet_name: str = "DATASET"
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], pd.DataFrame]:
    """
    Parse uploaded or local Excel workbook, mapping the DATASET sheet to database structure.

    Returns:
        (valid_records, invalid_records, preview_dataframe)
    """
    valid_records = []
    invalid_records = []

    try:
        df = pd.read_excel(file_source, sheet_name=sheet_name)
    except Exception as e:
        # If sheet DATASET not found, try reading first sheet
        try:
            df = pd.read_excel(file_source, sheet_name=0)
        except Exception as e2:
            raise ValueError(f"Could not read Excel file: {e2}")

    preview_df = df.copy()

    for idx, row in df.iterrows():
        row_num = idx + 2  # Excel 1-indexed header is row 1
        raw_dict = {}

        for excel_col, db_col in EXCEL_COLUMN_MAP.items():
            if excel_col in df.columns:
                raw_dict[db_col] = row[excel_col]

        raw_dict["year"] = target_year
        raw_dict["notes"] = f"Imported from Excel row {row_num}"

        is_valid, errors, cleaned = validate_record_input(raw_dict, allow_duplicate=True)

        if is_valid:
            valid_records.append(cleaned)
        else:
            invalid_records.append({
                "row_number": row_num,
                "month": raw_dict.get("month", "Unknown"),
                "system": raw_dict.get("utility_system", "Unknown"),
                "errors": errors
            })

    return valid_records, invalid_records, preview_df


def import_parsed_records(records: List[Dict[str, Any]], overwrite: bool = False) -> Dict[str, int]:
    """
    Import list of validated records into SQLite.
    If overwrite is True, updates existing record for the same year/month/system.
    """
    counts = {"imported": 0, "updated": 0, "skipped": 0}

    with get_connection() as conn:
        cursor = conn.cursor()
        for rec in records:
            cursor.execute("""
                SELECT id FROM utility_records
                WHERE year = ? AND month = ? AND utility_system = ?
            """, (rec["year"], rec["month"], rec["utility_system"]))
            existing = cursor.fetchone()

            if existing:
                if overwrite:
                    update_utility_record(existing["id"], rec)
                    counts["updated"] += 1
                else:
                    counts["skipped"] += 1
            else:
                add_utility_record(rec)
                counts["imported"] += 1

    return counts


def export_to_csv(df: pd.DataFrame) -> bytes:
    """Export filtered DataFrame to UTF-8 CSV bytes."""
    export_df = df.copy()
    if "month_num" in export_df.columns:
        export_df = export_df.drop(columns=["month_num"])

    # Format percentages for presentation
    if "equipment_availability" in export_df.columns:
        export_df["equipment_availability"] = (export_df["equipment_availability"] * 100).round(2).astype(str) + "%"
    if "energy_loss_pct" in export_df.columns:
        export_df["energy_loss_pct"] = (export_df["energy_loss_pct"] * 100).round(2).astype(str) + "%"

    # Rename columns to user-friendly titles
    export_df = export_df.rename(columns=REVERSE_DISPLAY_MAP)
    return export_df.to_csv(index=False).encode("utf-8")


def export_to_excel(
    df: pd.DataFrame,
    filters_desc: Dict[str, Any],
    kpis: Dict[str, Any]
) -> bytes:
    """
    Generate an executive-ready, beautifully styled multi-tab Excel workbook
    containing Executive Summary, Filtered Utility Records, and Threshold Status.
    """
    output = io.BytesIO()
    wb = openpyxl.Workbook()

    # Style definitions
    font_title = Font(name="Calibri", size=16, bold=True, color="1E3A8A")
    font_subtitle = Font(name="Calibri", size=11, italic=True, color="475569")
    font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    font_bold = Font(name="Calibri", size=11, bold=True)
    font_regular = Font(name="Calibri", size=11)

    fill_primary = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")  # Navy
    fill_accent = PatternFill(start_color="0284C7", end_color="0284C7", fill_type="solid")   # Sky Blue
    fill_light = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")

    thin_border = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="thin", color="CBD5E1")
    )

    # -------------------------------------------------------------
    # SHEET 1: Executive Summary & KPIs
    # -------------------------------------------------------------
    ws_summary = wb.active
    ws_summary.title = "Executive Summary"
    ws_summary.views.sheetView[0].showGridLines = True

    # Title Banner
    ws_summary.cell(row=2, column=2, value="ENERGY & UTILITY PERFORMANCE REPORT").font = font_title
    ws_summary.cell(row=3, column=2, value=f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}").font = font_subtitle

    # Applied Filters Box
    ws_summary.cell(row=5, column=2, value="Report Filter Criteria").font = font_bold
    ws_summary.cell(row=6, column=2, value="Year Filter:").font = font_regular
    ws_summary.cell(row=6, column=3, value=str(filters_desc.get("year", "All"))).font = font_bold
    ws_summary.cell(row=7, column=2, value="Month Filter:").font = font_regular
    ws_summary.cell(row=7, column=3, value=str(filters_desc.get("month", "All"))).font = font_bold
    ws_summary.cell(row=8, column=2, value="Utility System Filter:").font = font_regular
    ws_summary.cell(row=8, column=3, value=str(filters_desc.get("utility_system", "All"))).font = font_bold

    # KPI Table Header
    ws_summary.cell(row=10, column=2, value="Key Performance Indicator (KPI)").font = font_header
    ws_summary.cell(row=10, column=2).fill = fill_primary
    ws_summary.cell(row=10, column=3, value="Aggregated Value").font = font_header
    ws_summary.cell(row=10, column=3).fill = fill_primary
    ws_summary.cell(row=10, column=4, value="Standard Unit").font = font_header
    ws_summary.cell(row=10, column=4).fill = fill_primary

    kpi_rows = [
        ("Total Energy Consumption", f"{kpis.get('total_energy', 0):,.0f}", "kWh"),
        ("Total Utility Downtime", f"{kpis.get('total_downtime', 0):,.1f}", "Hours"),
        ("Average Equipment Availability", f"{kpis.get('avg_availability', 0) * 100:.1f}%", "Percentage"),
        ("Average Energy per Unit of Production", f"{kpis.get('avg_energy_per_unit', 0):.2f}", "kWh/Unit"),
        ("Average Energy Efficiency Ratio", f"{kpis.get('avg_efficiency_ratio', 0):.2f}", "Ratio (0.0 - 1.0)"),
        ("Total Maintenance Cost", f"${kpis.get('total_maintenance_cost', 0):,.0f}", "USD ($)"),
        ("Average Energy Loss / Waste", f"{kpis.get('avg_energy_loss', 0) * 100:.1f}%", "Percentage"),
        ("Average Water Consumption per Unit", f"{kpis.get('avg_water_per_unit', 0):.1f}", "Liters/Unit"),
        ("Max Peak Energy Demand Recorded", f"{kpis.get('peak_demand_max', 0):,.0f}", "kW"),
        ("Total Monthly Records Evaluated", f"{kpis.get('total_records', 0)}", "Records Count")
    ]

    for idx, (kpi_name, kpi_val, unit) in enumerate(kpi_rows, start=11):
        cell_kpi = ws_summary.cell(row=idx, column=2, value=kpi_name)
        cell_val = ws_summary.cell(row=idx, column=3, value=kpi_val)
        cell_unit = ws_summary.cell(row=idx, column=4, value=unit)

        cell_kpi.font = font_regular
        cell_val.font = font_bold
        cell_unit.font = font_regular

        cell_val.alignment = Alignment(horizontal="right")
        cell_unit.alignment = Alignment(horizontal="center")

        for c in [cell_kpi, cell_val, cell_unit]:
            c.border = thin_border
            if idx % 2 == 0:
                c.fill = fill_light

    ws_summary.column_dimensions["B"].width = 38
    ws_summary.column_dimensions["C"].width = 24
    ws_summary.column_dimensions["D"].width = 20

    # -------------------------------------------------------------
    # SHEET 2: Filtered Utility Records
    # -------------------------------------------------------------
    ws_data = wb.create_sheet(title="Utility Records")
    ws_data.views.sheetView[0].showGridLines = True

    export_df = df.copy()
    if "month_num" in export_df.columns:
        export_df = export_df.drop(columns=["month_num"])

    cols = [c for c in export_df.columns if c in REVERSE_DISPLAY_MAP]
    headers = [REVERSE_DISPLAY_MAP[c] for c in cols]

    for col_idx, header in enumerate(headers, start=1):
        cell = ws_data.cell(row=1, column=col_idx, value=header)
        cell.font = font_header
        cell.fill = fill_accent
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for row_idx, row in export_df.iterrows():
        excel_row = row_idx + 2
        for col_idx, col_name in enumerate(cols, start=1):
            val = row[col_name]
            cell = ws_data.cell(row=excel_row, column=col_idx)

            if col_name in ["equipment_availability", "energy_loss_pct"] and pd.notnull(val):
                cell.value = float(val)
                cell.number_format = "0.0%"
            elif col_name in ["total_energy_kwh", "peak_demand_kw"] and pd.notnull(val):
                cell.value = float(val)
                cell.number_format = "#,##0"
            elif col_name in ["maintenance_cost", "energy_cost_per_unit"] and pd.notnull(val):
                cell.value = float(val)
                cell.number_format = "$#,##0.00"
            elif col_name in ["downtime_hours", "energy_per_unit_kwh", "energy_efficiency_ratio", "water_per_unit_liters"] and pd.notnull(val):
                cell.value = float(val)
                cell.number_format = "0.00"
            else:
                cell.value = str(val) if pd.notnull(val) else ""

            cell.font = font_regular
            cell.border = thin_border
            if excel_row % 2 == 1:
                cell.fill = fill_light

    for col_idx in range(1, len(headers) + 1):
        col_letter = get_column_letter(col_idx)
        ws_data.column_dimensions[col_letter].width = 20

    wb.save(output)
    output.seek(0)
    return output.getvalue()
