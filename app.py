"""
app.py
Energy & Utility Maintenance Management Dashboard
Built with Streamlit, SQLite, Pandas, Plotly, and OpenPyXL.
"""

from datetime import datetime
import pandas as pd
import streamlit as st

import analytics
import database
import import_export
import validation

# -----------------------------------------------------------------------------
# 1. Page Configuration & Custom CSS (Glassmorphism & Industrial Dark Theme)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="EnergiX | Utility & Maintenance Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
  --bg: #080d18;
  --surface: rgba(17, 27, 46, .82);
  --surface-strong: #111c30;
  --line: rgba(148, 163, 184, .17);
  --muted: #94a3b8;
  --text: #edf4ff;
  --cyan: #22d3ee;
  --blue: #60a5fa;
  --green: #34d399;
  --red: #fb7185;
}
html, body, [class*="css"], [data-testid="stMarkdownContainer"] {
  font-family: 'DM Sans', 'Segoe UI', sans-serif;
}
.stApp {
  color: var(--text);
  background:
    radial-gradient(ellipse at 8% 0%, rgba(14, 116, 144, .16), transparent 34%),
    radial-gradient(ellipse at 95% 12%, rgba(37, 99, 235, .12), transparent 30%),
    linear-gradient(145deg, #080d18 0%, #0b1220 48%, #080d18 100%);
}
.block-container { padding-top: 1.55rem; padding-bottom: 3rem; max-width: 1600px; }
h1, h2, h3, h4 { font-family: 'Manrope', sans-serif !important; letter-spacing: -.025em; color: #f8fafc; }
h2 { margin-top: .35rem; }
p, li { color: #cbd5e1; }
small, .stCaption { color: var(--muted) !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0b1424 0%, #09101d 100%) !important;
  border-right: 1px solid var(--line);
}
section[data-testid="stSidebar"] > div { padding-top: 1.4rem; }
section[data-testid="stSidebar"] [data-testid="stRadio"] > div { gap: .38rem; }
section[data-testid="stSidebar"] [data-testid="stRadio"] label {
  border: 1px solid transparent; border-radius: 10px; padding: .45rem .65rem;
  transition: all .18s ease;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
  background: rgba(34, 211, 238, .07); border-color: rgba(34, 211, 238, .18);
}
section[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
  background: rgba(15, 23, 42, .9); border-color: var(--line); border-radius: 9px;
}

/* Hero and KPI cards */
.hero-banner {
  position: relative; overflow: hidden; isolation: isolate;
  background: linear-gradient(115deg, rgba(15, 35, 58, .96), rgba(13, 28, 49, .88) 58%, rgba(14, 45, 65, .76));
  border: 1px solid rgba(34, 211, 238, .22); border-radius: 18px;
  padding: 26px 30px; margin: 0 0 22px;
  box-shadow: 0 18px 50px rgba(0,0,0,.18);
}
.hero-banner:after {
  content: ''; position: absolute; z-index: -1; width: 260px; height: 260px;
  right: -80px; top: -145px; border-radius: 50%;
  border: 1px solid rgba(34,211,238,.2);
  box-shadow: 0 0 0 28px rgba(34,211,238,.025), 0 0 0 58px rgba(34,211,238,.02);
}
.hero-title { font-family: 'Manrope', sans-serif; font-size: clamp(1.5rem, 2.3vw, 2.05rem); font-weight: 800; color: #f8fafc; margin: 0; letter-spacing: -.045em; }
.hero-subtitle { font-size: .94rem; color: #a9bbd1; margin: .55rem 0 0; max-width: 900px; line-height: 1.65; }
.kpi-card {
  min-height: 136px; position: relative; overflow: hidden;
  background: linear-gradient(145deg, rgba(23, 37, 60, .92), rgba(13, 23, 40, .95));
  border: 1px solid var(--line); border-radius: 15px; padding: 19px 20px;
  margin-bottom: 12px; box-shadow: 0 10px 28px rgba(0,0,0,.14);
  transition: transform .2s ease, border-color .2s ease, box-shadow .2s ease;
}
.kpi-card:before { content: ''; position: absolute; left: 0; top: 18px; bottom: 18px; width: 3px; background: linear-gradient(180deg, var(--cyan), var(--blue)); border-radius: 0 4px 4px 0; }
.kpi-card:hover { transform: translateY(-3px); border-color: rgba(34,211,238,.38); box-shadow: 0 16px 35px rgba(0,0,0,.23); }
.kpi-title { font-size: .73rem; font-weight: 700; text-transform: uppercase; letter-spacing: .075em; color: #9fb0c7; margin-bottom: 10px; }
.kpi-value { font-family: 'Manrope', sans-serif; font-size: clamp(1.35rem, 1.9vw, 1.8rem); font-weight: 800; color: #f8fafc; line-height: 1.2; letter-spacing: -.04em; overflow-wrap: anywhere; }
.kpi-unit { font-size: .78rem; font-weight: 600; color: #8da2bb; margin-left: 5px; letter-spacing: 0; }
.kpi-badge { display: inline-block; padding: 4px 9px; font-size: .69rem; font-weight: 700; border-radius: 999px; margin-top: 12px; }
.badge-good { background: rgba(52,211,153,.10); color: #6ee7b7; border: 1px solid rgba(52,211,153,.22); }
.badge-alert { background: rgba(251,113,133,.10); color: #fda4af; border: 1px solid rgba(251,113,133,.24); }
.badge-info { background: rgba(34,211,238,.10); color: #67e8f9; border: 1px solid rgba(34,211,238,.22); }
.alert-strip { background: linear-gradient(90deg, rgba(127,29,29,.24), rgba(127,29,29,.06)); border: 1px solid rgba(251,113,133,.22); border-left: 4px solid #fb7185; border-radius: 11px; padding: 13px 17px; margin-bottom: 17px; color: #fecdd3; font-size: .9rem; }

/* Native Streamlit controls */
.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button {
  border-radius: 9px !important; font-weight: 700 !important; min-height: 2.55rem;
  transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease !important;
}
.stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] > button[kind="primary"] {
  border: 1px solid rgba(34,211,238,.35) !important;
  background: linear-gradient(110deg, #0891b2, #2563eb) !important;
  color: white !important; box-shadow: 0 5px 18px rgba(8,145,178,.16);
}
.stButton > button:hover, .stDownloadButton > button:hover { transform: translateY(-1px); border-color: rgba(34,211,238,.45) !important; }
input, textarea { border-radius: 9px !important; }
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, div[data-baseweb="textarea"] {
  border-radius: 9px !important; border-color: rgba(148,163,184,.24) !important;
}
[data-testid="stForm"], [data-testid="stExpander"], div[data-testid="stDataFrame"], div[data-testid="stTable"] {
  border: 1px solid var(--line); border-radius: 13px; overflow: hidden;
}
[data-testid="stTabs"] button { font-weight: 700; }
[data-testid="stTabs"] button[aria-selected="true"] { color: #67e8f9 !important; }
hr { border-color: rgba(148,163,184,.15) !important; }
div[data-testid="stAlert"] { border-radius: 11px; }
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
@media (max-width: 800px) {
  .block-container { padding-left: 1rem; padding-right: 1rem; }
  .hero-banner { padding: 21px 20px; }
  .kpi-card { padding: 16px; }
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Compact application identity bar
st.markdown(
    f"""
    <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;
                padding:0 2px 16px;border-bottom:1px solid rgba(148,163,184,.12);margin-bottom:18px;">
      <div style="display:flex;align-items:center;gap:10px;">
        <div style="width:34px;height:34px;border-radius:10px;display:flex;align-items:center;
                    justify-content:center;background:linear-gradient(135deg,#0891b2,#2563eb);
                    box-shadow:0 5px 18px rgba(8,145,178,.22);font-size:18px;">⚡</div>
        <div>
          <div style="font-family:Manrope,sans-serif;font-weight:800;font-size:1rem;color:#f1f5f9;letter-spacing:-.03em;">ENERGIX <span style="color:#67e8f9;">/</span> OPERATIONS INTELLIGENCE</div>
          <div style="font-size:.72rem;color:#8498b2;letter-spacing:.04em;">ENERGY • UTILITIES • MAINTENANCE</div>
        </div>
      </div>
      <div style="text-align:right;font-size:.76rem;color:#9fb0c7;white-space:nowrap;">
        <span style="color:#34d399;">●</span> LOCAL DATABASE READY<br>
        <span style="color:#64748b;">{datetime.now().strftime('%d %b %Y  •  %H:%M')}</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)


# -----------------------------------------------------------------------------
# 2. Database Initialization & Auto-Seeding
# -----------------------------------------------------------------------------
@st.cache_resource
def init_application():
    """Ensure database schema is created and seed initial Excel dataset if empty."""
    database.create_tables()
    database.seed_default_data_from_excel_if_empty()
    return True

init_application()


# -----------------------------------------------------------------------------
# 3. Sidebar Navigation & Global Filters
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
            <div style="background: linear-gradient(135deg, #00d2ff, #0072ff); width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; box-shadow: 0 4px 15px rgba(0, 210, 255, 0.35);">
                ⚡
            </div>
            <div>
                <h3 style="margin: 0; font-size: 1.25rem; font-weight: 800; color: #ffffff;">EnergiX</h3>
                <p style="margin: 0; font-size: 0.72rem; color: #00d2ff; letter-spacing: 0.08em; text-transform: uppercase; font-weight: 600;">Utility & Maintenance</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    page_selection = st.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "➕ Add Record",
            "📋 Manage Records",
            "📥 Import Data",
            "📑 Reports & Export",
            "⚙️ Thresholds & Maintenance"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("<h4 style='color: #cbd5e1; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em;'>Global Filters</h4>", unsafe_allow_html=True)

    filter_opts = database.get_filter_options()

    year_options = ["All"] + [str(y) for y in sorted(filter_opts["years"], reverse=True)]
    selected_year = st.selectbox("Reporting Year", year_options, index=0)

    month_options = ["All"] + filter_opts["months"]
    selected_month = st.selectbox("Reporting Month", month_options, index=0)

    system_options = ["All"] + filter_opts["systems"]
    selected_system = st.selectbox("Utility System", system_options, index=0)

    # Active filter descriptor
    active_filters = {
        "year": None if selected_year == "All" else int(selected_year),
        "month": None if selected_month == "All" else selected_month,
        "utility_system": None if selected_system == "All" else selected_system,
    }

    st.markdown("---")
    thresholds = database.get_thresholds()
    st.markdown(f"""
        <div style="font-size: 0.75rem; color: #64748b; line-height: 1.5;">
            <b>Storage:</b> SQLite Persistent DB<br>
            <b>Source of Truth:</b> <code>energy_utility.db</code><br>
            <b>Threshold Max Downtime:</b> {thresholds.get('max_downtime_hours', 25):.0f} hrs<br>
            <b>Threshold Min Availability:</b> {thresholds.get('min_availability_pct', 0.92)*100:.0f}%
        </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 4. Helper Function: Render Metric Card
# -----------------------------------------------------------------------------
def render_kpi_card(title: str, value_str: str, unit: str, badge_text: str, badge_type: str = "good"):
    badge_class = f"badge-{badge_type}"
    return f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value_str}<span class="kpi-unit">{unit}</span></div>
            <span class="kpi-badge {badge_class}">{badge_text}</span>
        </div>
    """


# -----------------------------------------------------------------------------
# PAGE 1: 📊 Executive Dashboard
# -----------------------------------------------------------------------------
if page_selection == "📊 Dashboard":
    records_df = database.get_utility_records(
        year=active_filters["year"],
        month=active_filters["month"],
        utility_system=active_filters["utility_system"]
    )
    kpis = analytics.calculate_kpis(records_df, thresholds)

    # Hero Banner
    filter_tag = f"Showing: Year: {selected_year} | Month: {selected_month} | System: {selected_system}"
    st.markdown(f"""
        <div class="hero-banner">
            <h1 class="hero-title">Energy & Utility Performance Dashboard</h1>
            <p class="hero-subtitle">Continuous monitoring of plant utility consumption, equipment availability, downtime, and maintenance expenditure. • <span style="color: #00d2ff; font-weight: 600;">{filter_tag}</span></p>
        </div>
    """, unsafe_allow_html=True)

    # Breach alert if any metrics exceed thresholds
    breaches = []
    if kpis.get("downtime_alert"):
        breaches.append(f"Utility downtime exceeded threshold ({thresholds['max_downtime_hours']:.0f} hrs)")
    if kpis.get("availability_alert"):
        breaches.append(f"Equipment availability fell below {thresholds['min_availability_pct']*100:.0f}%")
    if kpis.get("energy_loss_alert"):
        breaches.append(f"Energy loss exceeded {thresholds['max_energy_loss_pct']*100:.0f}% target")
    if kpis.get("peak_demand_alert"):
        breaches.append(f"Peak demand surpassed threshold ({thresholds['max_peak_demand_kw']:.0f} kW)")
    if kpis.get("cost_alert"):
        breaches.append(f"Monthly maintenance cost exceeded ${thresholds['max_maintenance_cost']:,.0f}")

    if breaches:
        breach_text = " &bull; ".join(breaches)
        st.markdown(f"""
            <div class="alert-strip">
                <span style="font-size: 1.2rem;">⚠️</span>
                <div><b>Operational Alert Detected:</b> {breach_text}</div>
            </div>
        """, unsafe_allow_html=True)

    if records_df.empty:
        st.warning("No records match the current filter selection. Adjust filters in the sidebar or add new records.")
    else:
        # Row 1: Top 4 Primary KPIs
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(render_kpi_card(
                "Total Energy Consumption",
                f"{kpis['total_energy']:,.0f}",
                "kWh",
                f"{kpis['total_records']} Records Aggregated",
                "info"
            ), unsafe_allow_html=True)
        with c2:
            dt_badge = "Alert: High" if kpis.get("downtime_alert") else "Normal Range"
            dt_type = "alert" if kpis.get("downtime_alert") else "good"
            st.markdown(render_kpi_card(
                "Total Utility Downtime",
                f"{kpis['total_downtime']:.1f}",
                "Hours",
                dt_badge,
                dt_type
            ), unsafe_allow_html=True)
        with c3:
            av_val = kpis["avg_availability"] * 100.0
            av_badge = "Target Met (>92%)" if av_val >= (thresholds["min_availability_pct"]*100) else "Below Target"
            av_type = "good" if av_val >= (thresholds["min_availability_pct"]*100) else "alert"
            st.markdown(render_kpi_card(
                "Avg Equipment Availability",
                f"{av_val:.1f}",
                "%",
                av_badge,
                av_type
            ), unsafe_allow_html=True)
        with c4:
            st.markdown(render_kpi_card(
                "Total Maintenance Cost",
                f"${kpis['total_maintenance_cost']:,.0f}",
                "USD",
                "Utility Systems Budget",
                "info"
            ), unsafe_allow_html=True)

        # Row 2: Secondary KPIs
        c5, c6, c7, c8 = st.columns(4)
        with c5:
            st.markdown(render_kpi_card(
                "Avg Energy / Unit Produced",
                f"{kpis['avg_energy_per_unit']:.2f}",
                "kWh/Unit",
                "Specific Intensity",
                "info"
            ), unsafe_allow_html=True)
        with c6:
            st.markdown(render_kpi_card(
                "Avg Energy Efficiency Ratio",
                f"{kpis['avg_efficiency_ratio']:.2f}",
                "Ratio",
                "Operational Index",
                "good"
            ), unsafe_allow_html=True)
        with c7:
            loss_val = kpis["avg_energy_loss"] * 100.0
            loss_badge = "Waste in Control" if loss_val <= (thresholds["max_energy_loss_pct"]*100) else "High Energy Waste"
            loss_type = "good" if loss_val <= (thresholds["max_energy_loss_pct"]*100) else "alert"
            st.markdown(render_kpi_card(
                "Avg Energy Loss / Waste",
                f"{loss_val:.1f}",
                "%",
                loss_badge,
                loss_type
            ), unsafe_allow_html=True)
        with c8:
            st.markdown(render_kpi_card(
                "Peak Demand (Max kW)",
                f"{kpis['peak_demand_max']:,.0f}",
                "kW",
                f"Cap: {thresholds['max_peak_demand_kw']:.0f} kW",
                "alert" if kpis.get("peak_demand_alert") else "good"
            ), unsafe_allow_html=True)

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        # Charts Section - Row 1
        col_chart1, col_chart2 = st.columns([1.6, 1.0])
        with col_chart1:
            fig_trend = analytics.plot_monthly_energy_trend(records_df)
            st.plotly_chart(fig_trend, use_container_width=True)
        with col_chart2:
            fig_pie = analytics.plot_energy_by_system(records_df)
            st.plotly_chart(fig_pie, use_container_width=True)

        # Charts Section - Row 2
        col_chart3, col_chart4 = st.columns(2)
        with col_chart3:
            fig_dt = analytics.plot_downtime_by_system(records_df, threshold=thresholds["max_downtime_hours"])
            st.plotly_chart(fig_dt, use_container_width=True)
        with col_chart4:
            fig_maint = analytics.plot_maintenance_cost_by_system(records_df)
            st.plotly_chart(fig_maint, use_container_width=True)

        # Charts Section - Row 3
        col_chart5, col_chart6 = st.columns(2)
        with col_chart5:
            fig_avail = analytics.plot_availability_vs_efficiency(records_df)
            st.plotly_chart(fig_avail, use_container_width=True)
        with col_chart6:
            fig_loss = analytics.plot_energy_loss_and_water_trend(records_df)
            st.plotly_chart(fig_loss, use_container_width=True)

        # Charts Section - Row 4
        st.plotly_chart(analytics.plot_peak_demand_trend(records_df, threshold=thresholds["max_peak_demand_kw"]), use_container_width=True)

        # Quick Data Preview
        with st.expander("🔍 View Raw Filtered Records Table", expanded=False):
            display_df = records_df.copy()
            if "month_num" in display_df.columns:
                display_df = display_df.drop(columns=["month_num"])
            st.dataframe(display_df, use_container_width=True)


# -----------------------------------------------------------------------------
# PAGE 2: ➕ Add Utility Record
# -----------------------------------------------------------------------------
elif page_selection == "➕ Add Record":
    st.markdown("""
        <div class="hero-banner">
            <h1 class="hero-title">Add Monthly Utility Record</h1>
            <p class="hero-subtitle">Input utility meter readings, downtime, and maintenance cost metrics directly into the persistent SQLite database.</p>
        </div>
    """, unsafe_allow_html=True)

    with st.form("add_record_form", clear_on_submit=False):
        st.markdown("<h3 style='color: #00d2ff; font-size: 1.1rem; margin-bottom: 12px;'>1. Reporting Period & System Identification</h3>", unsafe_allow_html=True)
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            form_year = st.number_input("Reporting Year", min_value=2000, max_value=2100, value=datetime.now().year, step=1)
        with col_f2:
            curr_month_idx = datetime.now().month - 1
            form_month = st.selectbox("Reporting Month", database.MONTH_NAMES, index=curr_month_idx)
        with col_f3:
            existing_systems = filter_opts["systems"]
            form_system = st.selectbox("Utility System", existing_systems)

        st.markdown("<h3 style='color: #00d2ff; font-size: 1.1rem; margin-top: 20px; margin-bottom: 12px;'>2. Energy & Demand Metrics</h3>", unsafe_allow_html=True)
        col_e1, col_e2, col_e3, col_e4 = st.columns(4)
        with col_e1:
            form_total_energy = st.number_input("Total Energy Consumption (kWh)", min_value=0.0, value=520000.0, step=1000.0)
        with col_e2:
            form_energy_per_unit = st.number_input("Energy per Unit Produced (kWh)", min_value=0.0, value=4.80, step=0.05, format="%.2f")
        with col_e3:
            form_peak_demand = st.number_input("Peak Energy Demand (kW)", min_value=0.0, value=920.0, step=10.0)
        with col_e4:
            form_energy_cost_unit = st.number_input("Energy Cost per Unit Produced ($)", min_value=0.0, value=3.20, step=0.05, format="%.2f")

        st.markdown("<h3 style='color: #00d2ff; font-size: 1.1rem; margin-top: 20px; margin-bottom: 12px;'>3. Reliability & Operational Efficiency</h3>", unsafe_allow_html=True)
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            form_downtime = st.number_input("Utility Downtime (Hours)", min_value=0.0, max_value=744.0, value=18.0, step=0.5)
        with col_r2:
            form_availability = st.number_input("Utility Equipment Availability (0.00 - 1.00 or %)", min_value=0.0, max_value=100.0, value=0.95, step=0.01, format="%.2f", help="e.g. 0.95 or 95.0 for 95%")
        with col_r3:
            form_efficiency = st.number_input("Energy Efficiency Ratio", min_value=0.0, max_value=10.0, value=0.88, step=0.01, format="%.2f")

        st.markdown("<h3 style='color: #00d2ff; font-size: 1.1rem; margin-top: 20px; margin-bottom: 12px;'>4. Water, Energy Loss & Maintenance Cost</h3>", unsafe_allow_html=True)
        col_w1, col_w2, col_w3 = st.columns(3)
        with col_w1:
            form_water_unit = st.number_input("Water Consumption per Unit (Liters)", min_value=0.0, value=42.0, step=1.0)
        with col_w2:
            form_energy_loss = st.number_input("Energy Loss / Waste (0.00 - 1.00 or %)", min_value=0.0, max_value=100.0, value=0.06, step=0.01, format="%.2f", help="e.g. 0.06 or 6.0 for 6%")
        with col_w3:
            form_maintenance_cost = st.number_input("Maintenance Cost of Utility System ($)", min_value=0.0, value=240000.0, step=5000.0)

        form_notes = st.text_input("Operational Notes / Log", placeholder="e.g. Routine quarterly maintenance and sensor calibration performed")

        submit_btn = st.form_submit_button("💾 Save Record to Database", use_container_width=True, type="primary")

    if submit_btn:
        payload = {
            "year": form_year,
            "month": form_month,
            "utility_system": form_system,
            "total_energy_kwh": form_total_energy,
            "energy_per_unit_kwh": form_energy_per_unit,
            "downtime_hours": form_downtime,
            "energy_cost_per_unit": form_energy_cost_unit,
            "peak_demand_kw": form_peak_demand,
            "equipment_availability": form_availability,
            "energy_efficiency_ratio": form_efficiency,
            "water_per_unit_liters": form_water_unit,
            "energy_loss_pct": form_energy_loss,
            "maintenance_cost": form_maintenance_cost,
            "notes": form_notes
        }

        is_valid, error_list, cleaned_data = validation.validate_record_input(payload)

        if not is_valid:
            for err in error_list:
                st.error(f"❌ {err}")
        else:
            try:
                new_id = database.add_utility_record(cleaned_data)
                st.success(f"✅ Record successfully saved! (ID: {new_id} — {form_system} for {form_month} {form_year})")
                st.balloons()
            except Exception as e:
                st.error(f"Database error during insert: {e}")


# -----------------------------------------------------------------------------
# PAGE 3: 📋 Manage Records (Search, Edit, Delete)
# -----------------------------------------------------------------------------
elif page_selection == "📋 Manage Records":
    st.markdown("""
        <div class="hero-banner">
            <h1 class="hero-title">Manage Utility Records</h1>
            <p class="hero-subtitle">Search, inspect, update, or remove monthly utility records stored in SQLite.</p>
        </div>
    """, unsafe_allow_html=True)

    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        search_query = st.text_input("🔍 Search records by system, month, or notes...", "")
    with col_s2:
        st.write("")
        st.write("")
        refresh_btn = st.button("🔄 Refresh Data", use_container_width=True)

    records_df = database.get_utility_records(
        year=active_filters["year"],
        month=active_filters["month"],
        utility_system=active_filters["utility_system"],
        search_query=search_query
    )

    st.markdown(f"**Found {len(records_df)} matching record(s)**")

    if records_df.empty:
        st.info("No records match your criteria. Try adjusting the search or filters.")
    else:
        # Display table with readable headers
        preview_table = records_df.copy()
        if "month_num" in preview_table.columns:
            preview_table = preview_table.drop(columns=["month_num"])
        
        # Display formatted percentages and currencies
        display_view = preview_table.copy()
        display_view["equipment_availability"] = (display_view["equipment_availability"] * 100).round(1).astype(str) + "%"
        display_view["energy_loss_pct"] = (display_view["energy_loss_pct"] * 100).round(1).astype(str) + "%"
        display_view["maintenance_cost"] = "$" + display_view["maintenance_cost"].map("{:,.0f}".format)
        display_view["total_energy_kwh"] = display_view["total_energy_kwh"].map("{:,.0f}".format)

        st.dataframe(display_view, use_container_width=True, height=350)

        st.markdown("---")
        st.markdown("### ✏️ Edit or 🗑️ Delete a Record")

        # Select record by ID
        record_options = [
            f"ID {row['id']} — {row['year']} {row['month']} | {row['utility_system']} (Energy: {row['total_energy_kwh']:,.0f} kWh)"
            for _, row in records_df.iterrows()
        ]
        selected_record_str = st.selectbox("Select record to edit or delete:", record_options)
        selected_id = int(selected_record_str.split(" ")[1])
        record_to_edit = database.get_record_by_id(selected_id)

        if record_to_edit:
            tab_edit, tab_delete = st.tabs(["✏️ Edit Record Details", "🗑️ Delete Record Confirmation"])

            with tab_edit:
                with st.form(f"edit_form_{selected_id}"):
                    ce1, ce2, ce3 = st.columns(3)
                    with ce1:
                        edit_year = st.number_input("Year", min_value=2000, max_value=2100, value=int(record_to_edit["year"]))
                    with ce2:
                        edit_month_idx = database.MONTH_NAMES.index(record_to_edit["month"]) if record_to_edit["month"] in database.MONTH_NAMES else 0
                        edit_month = st.selectbox("Month", database.MONTH_NAMES, index=edit_month_idx)
                    with ce3:
                        sys_idx = filter_opts["systems"].index(record_to_edit["utility_system"]) if record_to_edit["utility_system"] in filter_opts["systems"] else 0
                        edit_system = st.selectbox("Utility System", filter_opts["systems"], index=sys_idx)

                    ce4, ce5, ce6, ce7 = st.columns(4)
                    with ce4:
                        edit_energy = st.number_input("Total Energy (kWh)", value=float(record_to_edit["total_energy_kwh"]))
                    with ce5:
                        edit_energy_unit = st.number_input("Energy / Unit (kWh)", value=float(record_to_edit["energy_per_unit_kwh"]))
                    with ce6:
                        edit_downtime = st.number_input("Downtime (Hours)", value=float(record_to_edit["downtime_hours"]))
                    with ce7:
                        edit_cost_unit = st.number_input("Cost / Unit ($)", value=float(record_to_edit["energy_cost_per_unit"]))

                    ce8, ce9, ce10, ce11 = st.columns(4)
                    with ce8:
                        edit_peak = st.number_input("Peak Demand (kW)", value=float(record_to_edit["peak_demand_kw"]))
                    with ce9:
                        edit_avail = st.number_input("Availability (0-1 or %)", value=float(record_to_edit["equipment_availability"]))
                    with ce10:
                        edit_eff = st.number_input("Efficiency Ratio", value=float(record_to_edit["energy_efficiency_ratio"]))
                    with ce11:
                        edit_water = st.number_input("Water / Unit (Liters)", value=float(record_to_edit["water_per_unit_liters"]))

                    ce12, ce13 = st.columns(2)
                    with ce12:
                        edit_loss = st.number_input("Energy Loss / Waste (0-1 or %)", value=float(record_to_edit["energy_loss_pct"]))
                    with ce13:
                        edit_maint = st.number_input("Maintenance Cost ($)", value=float(record_to_edit["maintenance_cost"]))

                    edit_notes = st.text_input("Operational Notes", value=str(record_to_edit.get("notes", "")))

                    update_btn = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)

                if update_btn:
                    upd_payload = {
                        "year": edit_year,
                        "month": edit_month,
                        "utility_system": edit_system,
                        "total_energy_kwh": edit_energy,
                        "energy_per_unit_kwh": edit_energy_unit,
                        "downtime_hours": edit_downtime,
                        "energy_cost_per_unit": edit_cost_unit,
                        "peak_demand_kw": edit_peak,
                        "equipment_availability": edit_avail,
                        "energy_efficiency_ratio": edit_eff,
                        "water_per_unit_liters": edit_water,
                        "energy_loss_pct": edit_loss,
                        "maintenance_cost": edit_maint,
                        "notes": edit_notes
                    }
                    is_valid, err_list, cleaned = validation.validate_record_input(upd_payload, exclude_id=selected_id)
                    if not is_valid:
                        for e in err_list:
                            st.error(f"❌ {e}")
                    else:
                        success = database.update_utility_record(selected_id, cleaned)
                        if success:
                            st.success(f"✅ Record #{selected_id} updated successfully!")
                            st.rerun()

            with tab_delete:
                st.error(f"⚠️ You are about to permanently delete Record #{selected_id} ({record_to_edit['month']} {record_to_edit['year']} - {record_to_edit['utility_system']}).")
                confirm_check = st.checkbox(f"Yes, I confirm I want to permanently delete record #{selected_id}")
                if st.button("🗑️ Permanently Delete Record", type="primary", disabled=not confirm_check):
                    if database.delete_utility_record(selected_id):
                        st.success(f"Record #{selected_id} deleted successfully.")
                        st.rerun()


# -----------------------------------------------------------------------------
# PAGE 4: 📥 Import Data (Excel Migration)
# -----------------------------------------------------------------------------
elif page_selection == "📥 Import Data":
    st.markdown("""
        <div class="hero-banner">
            <h1 class="hero-title">Excel Data Migration & Import</h1>
            <p class="hero-subtitle">Ingest monthly utility datasets from Excel workbooks directly into the SQLite database with automatic validation and duplicate prevention.</p>
        </div>
    """, unsafe_allow_html=True)

    tab_upload, tab_default = st.tabs(["📤 Upload Custom Excel File", "📁 Re-Import Seed Excel Dataset"])

    with tab_upload:
        st.markdown("Upload any Excel workbook containing a **`DATASET`** sheet with standard utility columns:")
        uploaded_file = st.file_uploader("Choose Excel (.xlsx) file", type=["xlsx", "xls"])
        import_target_year = st.number_input("Assign Reporting Year for Imported Records", min_value=2000, max_value=2100, value=2026, step=1)
        overwrite_choice = st.checkbox("Overwrite existing records if same Year, Month, and Utility System already exist", value=False)

        if uploaded_file is not None:
            try:
                valid_recs, invalid_recs, preview_df = import_export.parse_and_validate_excel(uploaded_file, target_year=import_target_year)
                
                st.markdown(f"### 🔍 Ingestion Preview ({len(preview_df)} rows detected)")
                st.dataframe(preview_df.head(10), use_container_width=True)

                col_stat1, col_stat2 = st.columns(2)
                with col_stat1:
                    st.success(f"✅ Valid Records Ready for Import: **{len(valid_recs)}**")
                with col_stat2:
                    if invalid_recs:
                        st.error(f"❌ Invalid / Malformed Records: **{len(invalid_recs)}**")
                    else:
                        st.info("No invalid rows detected.")

                if invalid_recs:
                    with st.expander("View Invalid Row Errors"):
                        for inv in invalid_recs:
                            st.write(f"Row {inv['row_number']} ({inv['month']} - {inv['system']}): {', '.join(inv['errors'])}")

                if len(valid_recs) > 0:
                    if st.button("🚀 Execute Database Import", type="primary", use_container_width=True):
                        results = import_export.import_parsed_records(valid_recs, overwrite=overwrite_choice)
                        st.success(f"🎉 Import Completed! Added: {results['imported']} new records | Updated: {results['updated']} existing | Skipped: {results['skipped']} duplicates.")
                        st.balloons()
            except Exception as e:
                st.error(f"Error parsing workbook: {e}")

    with tab_default:
        st.markdown("""
            **Local Source Workbook:** `data/Energy & Utility Maintenance Dashboard.xlsx`  
            You can re-import or update all 12 baseline monthly utility records into SQLite with one click.
        """)
        reimport_overwrite = st.checkbox("Overwrite existing records during baseline reload", value=True)
        if st.button("🔄 Reload Baseline Dataset from Local Excel", type="secondary"):
            excel_path = "data/Energy & Utility Maintenance Dashboard.xlsx"
            valid_recs, invalid_recs, _ = import_export.parse_and_validate_excel(excel_path, target_year=2026)
            res = import_export.import_parsed_records(valid_recs, overwrite=reimport_overwrite)
            st.success(f"Baseline reload completed! Imported: {res['imported']} | Updated: {res['updated']} | Skipped: {res['skipped']}")


# -----------------------------------------------------------------------------
# PAGE 5: 📑 Reports & Export
# -----------------------------------------------------------------------------
elif page_selection == "📑 Reports & Export":
    st.markdown("""
        <div class="hero-banner">
            <h1 class="hero-title">Reports & Data Export</h1>
            <p class="hero-subtitle">Generate presentation-ready reports and download clean datasets in Excel (.xlsx) and CSV formats.</p>
        </div>
    """, unsafe_allow_html=True)

    records_df = database.get_utility_records(
        year=active_filters["year"],
        month=active_filters["month"],
        utility_system=active_filters["utility_system"]
    )
    kpis = analytics.calculate_kpis(records_df, thresholds)

    col_meta1, col_meta2 = st.columns([2, 1])
    with col_meta1:
        st.markdown(f"""
            <div class="form-card">
                <h3 style="color: #00d2ff; margin-top: 0;">Executive Summary & Filter Metadata</h3>
                <p><b>Report Generation Date:</b> {datetime.now().strftime('%B %d, %Y - %H:%M:%S')}</p>
                <p><b>Selected Year:</b> {selected_year} &nbsp;|&nbsp; <b>Selected Month:</b> {selected_month} &nbsp;|&nbsp; <b>Utility System:</b> {selected_system}</p>
                <p><b>Total Records Included:</b> {len(records_df)}</p>
                <p style="color: #94a3b8; font-size: 0.88rem;">Exports include all active metrics with explicit engineering units and executive KPI aggregations.</p>
            </div>
        """, unsafe_allow_html=True)

    with col_meta2:
        st.markdown("<div class='form-card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #00d2ff; margin-top: 0;'>Quick Downloads</h3>", unsafe_allow_html=True)

        if not records_df.empty:
            excel_data = import_export.export_to_excel(records_df, active_filters, kpis)
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M")
            st.download_button(
                label="📊 Download Styled Excel Report (.xlsx)",
                data=excel_data,
                file_name=f"Utility_Report_{timestamp_str}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

            csv_data = import_export.export_to_csv(records_df)
            st.download_button(
                label="📄 Download Clean CSV Dataset (.csv)",
                data=csv_data,
                file_name=f"Utility_Data_{timestamp_str}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.warning("No records to export. Clear filters.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 📋 Executive Summary Table Preview")
    summary_preview_data = [
        {"KPI Metric": "Total Energy Consumption", "Value": f"{kpis['total_energy']:,.0f}", "Unit": "kWh"},
        {"KPI Metric": "Total Utility Downtime", "Value": f"{kpis['total_downtime']:.1f}", "Unit": "Hours"},
        {"KPI Metric": "Average Equipment Availability", "Value": f"{kpis['avg_availability']*100:.1f}%", "Unit": "Percentage"},
        {"KPI Metric": "Average Energy / Production Unit", "Value": f"{kpis['avg_energy_per_unit']:.2f}", "Unit": "kWh/Unit"},
        {"KPI Metric": "Average Energy Efficiency Ratio", "Value": f"{kpis['avg_efficiency_ratio']:.2f}", "Unit": "Ratio"},
        {"KPI Metric": "Total Maintenance Cost", "Value": f"${kpis['total_maintenance_cost']:,.0f}", "Unit": "USD ($)"},
        {"KPI Metric": "Average Energy Loss / Waste", "Value": f"{kpis['avg_energy_loss']*100:.1f}%", "Unit": "Percentage"},
        {"KPI Metric": "Average Water Consumption", "Value": f"{kpis['avg_water_per_unit']:.1f}", "Unit": "Liters/Unit"},
        {"KPI Metric": "Peak Energy Demand (Max)", "Value": f"{kpis['peak_demand_max']:,.0f}", "Unit": "kW"}
    ]
    st.table(pd.DataFrame(summary_preview_data))


# -----------------------------------------------------------------------------
# PAGE 6: ⚙️ Thresholds & Maintenance Log
# -----------------------------------------------------------------------------
elif page_selection == "⚙️ Thresholds & Maintenance":
    st.markdown("""
        <div class="hero-banner">
            <h1 class="hero-title">Alert Thresholds & Maintenance Work Orders</h1>
            <p class="hero-subtitle">Configure engineering alarm limits and log preventive or corrective maintenance tasks.</p>
        </div>
    """, unsafe_allow_html=True)

    tab_thresh, tab_maint = st.tabs(["⚙️ Configure Alert Thresholds", "🛠️ Maintenance Activity Logs"])

    with tab_thresh:
        st.markdown("### Operating Warning Thresholds")
        st.markdown("When monthly utility metrics exceed these thresholds, the dashboard highlights them in warning red.")

        current_thresh = database.get_thresholds()

        with st.form("thresholds_form"):
            ct1, ct2 = st.columns(2)
            with ct1:
                new_max_dt = st.number_input("Max Allowable Utility Downtime (Hours)", min_value=0.0, value=float(current_thresh.get("max_downtime_hours", 25.0)), step=1.0)
                new_min_avail = st.number_input("Min Required Equipment Availability (%)", min_value=0.0, max_value=100.0, value=float(current_thresh.get("min_availability_pct", 0.92)*100), step=1.0)
                new_max_loss = st.number_input("Max Acceptable Energy Loss / Waste (%)", min_value=0.0, max_value=100.0, value=float(current_thresh.get("max_energy_loss_pct", 0.08)*100), step=0.5)
            with ct2:
                new_max_peak = st.number_input("Max Peak Demand Limit (kW)", min_value=0.0, value=float(current_thresh.get("max_peak_demand_kw", 1050.0)), step=10.0)
                new_max_cost = st.number_input("Monthly Maintenance Cost Alert ($)", min_value=0.0, value=float(current_thresh.get("max_maintenance_cost", 280000.0)), step=5000.0)

            save_thresh_btn = st.form_submit_button("💾 Save Alert Thresholds", type="primary")

        if save_thresh_btn:
            database.update_thresholds({
                "max_downtime_hours": new_max_dt,
                "min_availability_pct": new_min_avail / 100.0,
                "max_energy_loss_pct": new_max_loss / 100.0,
                "max_peak_demand_kw": new_max_peak,
                "max_maintenance_cost": new_max_cost
            })
            st.success("✅ Threshold settings updated successfully!")
            st.rerun()

    with tab_maint:
        st.markdown("### 🛠️ Log New Maintenance Work Order")
        with st.form("new_maint_form"):
            cm1, cm2, cm3 = st.columns(3)
            with cm1:
                m_date = st.date_input("Work Date", value=datetime.now())
            with cm2:
                m_system = st.selectbox("Utility System", filter_opts["systems"])
            with cm3:
                m_priority = st.selectbox("Priority Level", ["Low", "Medium", "High", "Critical"], index=1)

            m_issue = st.text_input("Issue / Maintenance Description *", placeholder="e.g. Steam leak detected at secondary valve manifold")
            
            cm4, cm5, cm6 = st.columns(3)
            with cm4:
                m_action = st.text_input("Action Taken", placeholder="e.g. Replaced gasket and torqued flange bolts")
            with cm5:
                m_tech = st.text_input("Technician / Team", placeholder="e.g. J. Miller (Mechanical Dept)")
            with cm6:
                m_cost = st.number_input("Incurred Cost ($)", min_value=0.0, value=1500.0, step=100.0)

            m_status = st.selectbox("Task Status", ["Open", "In Progress", "Resolved"], index=0)

            m_submit = st.form_submit_button("📝 Add Maintenance Log", type="primary")

        if m_submit:
            if not m_issue.strip():
                st.error("Please enter an issue description.")
            else:
                database.add_maintenance_log({
                    "log_date": str(m_date),
                    "utility_system": m_system,
                    "issue_description": m_issue,
                    "action_taken": m_action,
                    "technician": m_tech,
                    "cost": m_cost,
                    "status": m_status,
                    "priority": m_priority
                })
                st.success("✅ Maintenance work order logged successfully!")
                st.rerun()

        st.markdown("---")
        st.markdown("### 📋 Maintenance Activity History")
        logs_df = database.get_maintenance_logs()
        if logs_df.empty:
            st.info("No maintenance activity logged yet.")
        else:
            st.dataframe(logs_df, use_container_width=True)
