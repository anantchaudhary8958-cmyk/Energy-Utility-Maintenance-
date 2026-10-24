"""
database.py
Database connection, schema management, and CRUD operations for the
Energy & Utility Maintenance Management Dashboard.
Source of truth: SQLite database.
"""

import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

DB_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DB_DIR, "energy_utility.db")

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]
MONTH_MAP = {name: idx + 1 for idx, name in enumerate(MONTH_NAMES)}

DEFAULT_UTILITY_SYSTEMS = [
    "Boiler Plant",
    "Air Compressor System",
    "Cooling Tower",
    "Water Treatment Plant"
]


def get_connection() -> sqlite3.Connection:
    """Return an active connection to the SQLite database with Row factory."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    """Create all required tables and default configurations if not existing."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # Utility Records table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS utility_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER NOT NULL,
                month TEXT NOT NULL,
                month_num INTEGER NOT NULL,
                utility_system TEXT NOT NULL,
                total_energy_kwh REAL NOT NULL,
                energy_per_unit_kwh REAL NOT NULL,
                downtime_hours REAL NOT NULL,
                energy_cost_per_unit REAL NOT NULL,
                peak_demand_kw REAL NOT NULL,
                equipment_availability REAL NOT NULL,
                energy_efficiency_ratio REAL NOT NULL,
                water_per_unit_liters REAL NOT NULL,
                energy_loss_pct REAL NOT NULL,
                maintenance_cost REAL NOT NULL,
                notes TEXT DEFAULT '',
                created_at TEXT DEFAULT (datetime('now', 'localtime')),
                updated_at TEXT DEFAULT (datetime('now', 'localtime')),
                UNIQUE(year, month, utility_system)
            )
        """)

        # Performance and Alert Thresholds table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alert_thresholds (
                id INTEGER PRIMARY KEY,
                max_downtime_hours REAL DEFAULT 25.0,
                min_availability_pct REAL DEFAULT 0.92,
                max_energy_loss_pct REAL DEFAULT 0.08,
                max_peak_demand_kw REAL DEFAULT 1050.0,
                max_maintenance_cost REAL DEFAULT 280000.0,
                updated_at TEXT DEFAULT (datetime('now', 'localtime'))
            )
        """)

        # Maintenance Work Log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS maintenance_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_date TEXT NOT NULL,
                utility_system TEXT NOT NULL,
                issue_description TEXT NOT NULL,
                action_taken TEXT DEFAULT '',
                technician TEXT DEFAULT '',
                cost REAL DEFAULT 0.0,
                status TEXT DEFAULT 'Open',
                priority TEXT DEFAULT 'Medium',
                created_at TEXT DEFAULT (datetime('now', 'localtime'))
            )
        """)

        # Initialize default alert thresholds if empty
        cursor.execute("SELECT COUNT(*) FROM alert_thresholds")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO alert_thresholds (
                    id, max_downtime_hours, min_availability_pct,
                    max_energy_loss_pct, max_peak_demand_kw, max_maintenance_cost
                ) VALUES (1, 25.0, 0.92, 0.08, 1050.0, 280000.0)
            """)

        conn.commit()


def check_duplicate_record(year: int, month: str, utility_system: str, exclude_id: Optional[int] = None) -> bool:
    """Check whether a record already exists for the given year, month, and system."""
    with get_connection() as conn:
        cursor = conn.cursor()
        if exclude_id is not None:
            cursor.execute("""
                SELECT COUNT(*) FROM utility_records
                WHERE year = ? AND month = ? AND utility_system = ? AND id != ?
            """, (year, month, utility_system, exclude_id))
        else:
            cursor.execute("""
                SELECT COUNT(*) FROM utility_records
                WHERE year = ? AND month = ? AND utility_system = ?
            """, (year, month, utility_system))
        return cursor.fetchone()[0] > 0


def add_utility_record(record: Dict[str, Any]) -> int:
    """Insert a single validated utility record into SQLite. Returns new record ID."""
    month_str = record["month"].strip()
    month_num = MONTH_MAP.get(month_str, 1)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO utility_records (
                year, month, month_num, utility_system,
                total_energy_kwh, energy_per_unit_kwh, downtime_hours,
                energy_cost_per_unit, peak_demand_kw, equipment_availability,
                energy_efficiency_ratio, water_per_unit_liters,
                energy_loss_pct, maintenance_cost, notes, updated_at
            ) VALUES (
                ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?,
                ?, ?,
                ?, ?, ?, datetime('now', 'localtime')
            )
        """, (
            int(record["year"]),
            month_str,
            month_num,
            record["utility_system"].strip(),
            float(record["total_energy_kwh"]),
            float(record["energy_per_unit_kwh"]),
            float(record["downtime_hours"]),
            float(record["energy_cost_per_unit"]),
            float(record["peak_demand_kw"]),
            float(record["equipment_availability"]),
            float(record["energy_efficiency_ratio"]),
            float(record["water_per_unit_liters"]),
            float(record["energy_loss_pct"]),
            float(record["maintenance_cost"]),
            record.get("notes", "")
        ))
        conn.commit()
        return cursor.lastrowid


def update_utility_record(record_id: int, record: Dict[str, Any]) -> bool:
    """Update an existing utility record by ID."""
    month_str = record["month"].strip()
    month_num = MONTH_MAP.get(month_str, 1)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE utility_records SET
                year = ?,
                month = ?,
                month_num = ?,
                utility_system = ?,
                total_energy_kwh = ?,
                energy_per_unit_kwh = ?,
                downtime_hours = ?,
                energy_cost_per_unit = ?,
                peak_demand_kw = ?,
                equipment_availability = ?,
                energy_efficiency_ratio = ?,
                water_per_unit_liters = ?,
                energy_loss_pct = ?,
                maintenance_cost = ?,
                notes = ?,
                updated_at = datetime('now', 'localtime')
            WHERE id = ?
        """, (
            int(record["year"]),
            month_str,
            month_num,
            record["utility_system"].strip(),
            float(record["total_energy_kwh"]),
            float(record["energy_per_unit_kwh"]),
            float(record["downtime_hours"]),
            float(record["energy_cost_per_unit"]),
            float(record["peak_demand_kw"]),
            float(record["equipment_availability"]),
            float(record["energy_efficiency_ratio"]),
            float(record["water_per_unit_liters"]),
            float(record["energy_loss_pct"]),
            float(record["maintenance_cost"]),
            record.get("notes", ""),
            record_id
        ))
        conn.commit()
        return cursor.rowcount > 0


def delete_utility_record(record_id: int) -> bool:
    """Delete a utility record by ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM utility_records WHERE id = ?", (record_id,))
        conn.commit()
        return cursor.rowcount > 0


def get_record_by_id(record_id: int) -> Optional[Dict[str, Any]]:
    """Fetch a single record by primary key."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM utility_records WHERE id = ?", (record_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_utility_records(
    year: Optional[int] = None,
    month: Optional[str] = None,
    utility_system: Optional[str] = None,
    search_query: Optional[str] = None
) -> pd.DataFrame:
    """Fetch utility records matching optional filters as a pandas DataFrame."""
    query = "SELECT * FROM utility_records WHERE 1=1"
    params = []

    if year is not None and year != "All":
        query += " AND year = ?"
        params.append(int(year))

    if month is not None and month != "All":
        query += " AND month = ?"
        params.append(month)

    if utility_system is not None and utility_system != "All":
        query += " AND utility_system = ?"
        params.append(utility_system)

    if search_query:
        query += " AND (utility_system LIKE ? OR notes LIKE ? OR month LIKE ?)"
        like_term = f"%{search_query.strip()}%"
        params.extend([like_term, like_term, like_term])

    query += " ORDER BY year DESC, month_num ASC, utility_system ASC"

    with get_connection() as conn:
        df = pd.read_sql_query(query, conn, params=params)
    return df


def get_filter_options() -> Dict[str, List[Any]]:
    """Retrieve distinct existing values for year, month, and systems for filter dropdowns."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT year FROM utility_records ORDER BY year DESC")
        years = [row[0] for row in cursor.fetchall()]
        if not years:
            years = [datetime.now().year]

        cursor.execute("SELECT DISTINCT month, month_num FROM utility_records ORDER BY month_num ASC")
        months = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT utility_system FROM utility_records ORDER BY utility_system ASC")
        systems = [row[0] for row in cursor.fetchall()]
        if not systems:
            systems = DEFAULT_UTILITY_SYSTEMS

    return {
        "years": years,
        "months": months,
        "systems": systems
    }


def get_thresholds() -> Dict[str, float]:
    """Retrieve current warning alert thresholds."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM alert_thresholds WHERE id = 1")
        row = cursor.fetchone()
        if row:
            return dict(row)
        return {
            "max_downtime_hours": 25.0,
            "min_availability_pct": 0.92,
            "max_energy_loss_pct": 0.08,
            "max_peak_demand_kw": 1050.0,
            "max_maintenance_cost": 280000.0
        }


def update_thresholds(thresholds: Dict[str, float]):
    """Update current warning alert thresholds."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE alert_thresholds SET
                max_downtime_hours = ?,
                min_availability_pct = ?,
                max_energy_loss_pct = ?,
                max_peak_demand_kw = ?,
                max_maintenance_cost = ?,
                updated_at = datetime('now', 'localtime')
            WHERE id = 1
        """, (
            float(thresholds.get("max_downtime_hours", 25.0)),
            float(thresholds.get("min_availability_pct", 0.92)),
            float(thresholds.get("max_energy_loss_pct", 0.08)),
            float(thresholds.get("max_peak_demand_kw", 1050.0)),
            float(thresholds.get("max_maintenance_cost", 280000.0))
        ))
        conn.commit()


def get_maintenance_logs(system_filter: Optional[str] = None) -> pd.DataFrame:
    """Fetch maintenance activity logs."""
    query = "SELECT * FROM maintenance_logs WHERE 1=1"
    params = []
    if system_filter and system_filter != "All":
        query += " AND utility_system = ?"
        params.append(system_filter)
    query += " ORDER BY log_date DESC, id DESC"

    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=params)


def add_maintenance_log(data: Dict[str, Any]) -> int:
    """Add a new maintenance log entry."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO maintenance_logs (
                log_date, utility_system, issue_description,
                action_taken, technician, cost, status, priority
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["log_date"],
            data["utility_system"],
            data["issue_description"],
            data.get("action_taken", ""),
            data.get("technician", ""),
            float(data.get("cost", 0.0)),
            data.get("status", "Open"),
            data.get("priority", "Medium")
        ))
        conn.commit()
        return cursor.lastrowid


def update_maintenance_log_status(log_id: int, status: str):
    """Quick update of status for maintenance log item."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE maintenance_logs SET status = ? WHERE id = ?", (status, log_id))
        conn.commit()


def delete_maintenance_log(log_id: int):
    """Delete a maintenance log entry."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM maintenance_logs WHERE id = ?", (log_id,))
        conn.commit()


def seed_default_data_from_excel_if_empty(excel_path: Optional[str] = None):
    """
    Seed initial 12 records from the workbook DATASET sheet if the database is newly initialized.
    Default reporting year is set to 2026.
    """
    if excel_path is None:
        excel_path = os.path.join(DB_DIR, "Energy & Utility Maintenance Dashboard.xlsx")

    if not os.path.exists(excel_path):
        return

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM utility_records")
        if cursor.fetchone()[0] > 0:
            return  # Already has data

    try:
        df = pd.read_excel(excel_path, sheet_name="DATASET")
        required_cols = [
            "Month", "Utility System", "Total Energy Consumption (kWh)",
            "Energy Consumption per Unit of Production (kWh)", "Utility Downtime (Hours)",
            "Energy Cost per Unit Produced", "Peak Energy Demand (kW)",
            "Utility Equipment Availability (%)", "Energy Efficiency Ratio",
            "Water Consumption per Unit Produced (Liters)", "Energy Loss / Waste (%)",
            "Maintenance Cost of Utility Systems"
        ]
        if not all(col in df.columns for col in required_cols):
            return

        with get_connection() as conn:
            cursor = conn.cursor()
            for _, row in df.iterrows():
                month = str(row["Month"]).strip()
                month_num = MONTH_MAP.get(month, 1)
                system = str(row["Utility System"]).strip()
                
                # Check availability & energy loss formatting
                avail = float(row["Utility Equipment Availability (%)"])
                if avail > 1.0:
                    avail = avail / 100.0  # normalize to 0-1
                
                loss = float(row["Energy Loss / Waste (%)"])
                if loss > 1.0:
                    loss = loss / 100.0  # normalize to 0-1

                cursor.execute("""
                    INSERT OR IGNORE INTO utility_records (
                        year, month, month_num, utility_system,
                        total_energy_kwh, energy_per_unit_kwh, downtime_hours,
                        energy_cost_per_unit, peak_demand_kw, equipment_availability,
                        energy_efficiency_ratio, water_per_unit_liters,
                        energy_loss_pct, maintenance_cost, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    2026,
                    month,
                    month_num,
                    system,
                    float(row["Total Energy Consumption (kWh)"]),
                    float(row["Energy Consumption per Unit of Production (kWh)"]),
                    float(row["Utility Downtime (Hours)"]),
                    float(row["Energy Cost per Unit Produced"]),
                    float(row["Peak Energy Demand (kW)"]),
                    avail,
                    float(row["Energy Efficiency Ratio"]),
                    float(row["Water Consumption per Unit Produced (Liters)"]),
                    loss,
                    float(row["Maintenance Cost of Utility Systems"]),
                    "Initial migration from Excel DATASET"
                ))
            conn.commit()
    except Exception as e:
        print(f"Notice: Auto-seeding encountered: {e}")
