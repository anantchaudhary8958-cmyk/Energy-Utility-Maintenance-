# EnergiX — Energy & Utility Maintenance Management Dashboard

A modern, database-backed enterprise web application built with **Streamlit**, **SQLite**, **Pandas**, **Plotly**, and **openpyxl**. It replaces fragile, manual Excel spreadsheets with a persistent, validated, and interactive command center for plant utilities and maintenance engineering.

---

## 1. Project Overview & Problem Solved

Traditional utility tracking frequently relies on manual spreadsheets (such as `Energy & Utility Maintenance Dashboard.xlsx`), which suffer from:
- Accidental formula deletions or row overwrites.
- Lack of centralized validation for negative numbers, out-of-range availability, or duplicate reporting periods.
- Inability to perform dynamic filtering across years, months, and systems without maintaining manual pivot tables.
- Difficulty collaborating across mechanical, electrical, and facility maintenance teams.

**EnergiX** converts this workflow into an **SQLite database-backed web application**:
- **SQLite is the source of truth**: all additions, edits, and deletions are permanently stored and queried using parameterized SQL.
- **Excel is an optional import/export format**: easily migrate legacy sheets and generate executive-ready styled `.xlsx` reports on demand.

---

## 2. Key Metrics Tracked

The application faithfully captures and models all 12 baseline parameters from the original industrial dataset:

| Metric | Stored Unit | Description |
|---|---|---|
| **Month & Year** | Period | Reporting time period (supports multi-year analysis) |
| **Utility System** | Text | Boiler Plant, Air Compressor, Cooling Tower, Water Treatment |
| **Total Energy Consumption** | kWh | Gross electrical & thermal energy consumed |
| **Energy Consumption / Unit** | kWh/Unit | Specific energy consumption intensity per production unit |
| **Utility Downtime** | Hours | Unplanned and planned downtime hours |
| **Energy Cost per Unit Produced** | $ / Unit | Unit financial cost for energy |
| **Peak Energy Demand** | kW | Maximum power draw recorded |
| **Equipment Availability** | % (0.0–1.0) | System uptime availability ratio |
| **Energy Efficiency Ratio** | Index (0–1.0) | Operational efficiency score |
| **Water Consumption / Unit** | Liters/Unit | Specific water usage per production output |
| **Energy Loss / Waste** | % (0.0–1.0) | Energy dissipated as waste heat, leaks, or idling |
| **Maintenance Cost** | $ | Total spare parts, labor, and servicing expenditures |

---

## 3. Technology Stack

- **Application Logic & UI**: Python 3.13, Streamlit
- **Persistence & Storage**: SQLite (`data/energy_utility.db`) with parameterized queries and transaction safety
- **Data Analytics & Transformations**: Pandas, NumPy
- **Interactive Visualizations**: Plotly (custom dark glassmorphism theme with neon accents)
- **Report & Excel Engine**: openpyxl (styled executive multi-tab workbooks with formatted headers, borders, number formats)

---

## 4. Project Structure

```text
Energy & Utility Maintenance/
├── app.py                      # Streamlit application UI, routing, and glassmorphic styling
├── database.py                 # SQLite connection, schema, CRUD, auto-seeder, maintenance logs
├── analytics.py                # KPI formulas, data aggregations, Plotly charts
├── validation.py               # Input validation, sanitization, and duplicate checking
├── import_export.py            # Excel DATASET ingestion, CSV export, styled Excel workbook export
├── requirements.txt            # Dependency definitions
├── README.md                   # Complete architectural and operational documentation
├── .gitignore                  # Git ignore rules for virtual environments, DB journals, caches
└── data/
    ├── energy_utility.db       # Primary SQLite persistent database
    └── Energy & Utility Maintenance Dashboard.xlsx   # Legacy source dataset
```

---

## 5. Application Features & Modules

### 📊 1. Executive Dashboard
- **Glassmorphic Hero KPI Cards**: Total Energy, Total Downtime, Average Availability, Total Maintenance Cost, Energy per Unit, Efficiency Ratio, Energy Waste %, and Peak Demand.
- **Dynamic Breach Strip**: Alerts operators if any metric exceeds configured safety thresholds.
- **Plotly Visualizations**:
  - *Monthly Energy Consumption Trend* with area fill and multi-system spline breakdown.
  - *Energy Share by Utility System* (interactive donut chart).
  - *Utility Downtime by System* with red alert bars for excessive outage.
  - *Maintenance Cost Breakdown* across equipment.
  - *Equipment Availability vs. Energy Efficiency Ratio* (dual-axis comparison).
  - *Energy Loss & Water Consumption Trends*.
  - *Peak Demand Trend* with customizable warning threshold reference line.

### ➕ 2. Add Utility Record
- Comprehensive input form categorized into logical engineering sections:
  1. Period & System Identification
  2. Energy & Demand Metrics
  3. Reliability & Operational Efficiency
  4. Water, Energy Loss & Maintenance Cost
- Validation guards preventing negative numbers, impossible hours (>744 hrs/month), and duplicate periods.

### 📋 3. Manage & Search Records
- Live full-text search across utility systems, months, and notes.
- In-place **Record Editor** with automatic validation before saving changes.
- Safe **Record Deletion** requiring affirmative checkbox confirmation to prevent accidental data loss.

### 📥 4. Excel Migration & Ingestion
- Upload external `.xlsx` files containing a `DATASET` sheet.
- Live pre-flight preview of valid and invalid rows with error diagnostics.
- Conflict resolution: choose between "Skip Duplicates" or "Overwrite Existing".
- 1-Click baseline dataset reloader.

### 📑 5. Reports & Data Export
- Filter-aware report generator with metadata timestamping.
- **Download Styled Excel Report (`.xlsx`)**: multi-tab workbook with Executive Summary sheet and styled Data sheet.
- **Download Clean CSV (`.csv`)** for downstream BI tools (Power BI, Tableau).

### ⚙️ 6. Alert Thresholds & Maintenance Work Orders
- Configurable engineering alarm thresholds for Downtime, Availability, Energy Loss, Peak Demand, and Maintenance Cost.
- Digital Maintenance Work Order logger for logging mechanical/electrical issues, actions taken, technician assigned, cost, priority, and status.

---

## 6. Local Quickstart Guide

### Step 1: Clone or Navigate to the Project Folder
```bash
cd "c:\Users\kumar\OneDrive\Desktop\Energy & Utility Maintenance"
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Streamlit Application
```bash
streamlit run app.py
```

The web dashboard will automatically open in your default browser at:  
👉 **`http://localhost:8501`**

---

## 7. Quality Assurance & Testing

Run unit and integrity tests on database operations, validation rules, and export routines:

```bash
# Verify SQLite table creation and auto-seeding
python -c "import database; database.create_tables(); print('Total Records:', len(database.get_utility_records()))"

# Verify validation engine
python -c "import validation; print(validation.validate_record_input({'year': 2026, 'month': 'January', 'utility_system': 'Boiler Plant'}))"
```

---

## 8. Deployment Considerations

- For local deployment, SQLite provides high performance, zero-configuration persistence.
- When deploying to production cloud platforms (e.g., Streamlit Community Cloud, AWS, GCP, Azure), mount a persistent volume for `data/energy_utility.db` or connect `database.py` to PostgreSQL / MySQL by updating the database adapter.
