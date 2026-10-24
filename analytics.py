"""
analytics.py
KPI calculation, aggregation logic, and Plotly visualization generation
for the Energy & Utility Maintenance Dashboard.
"""

from typing import Any, Dict, List, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Enterprise Theme Palette
CHART_THEME = "plotly_dark"
COLOR_PRIMARY = "#00d2ff"     # Neon Cyan
COLOR_SECONDARY = "#3a7bd5"   # Vibrant Blue
COLOR_ACCENT = "#00f2fe"      # Electric Teal
COLOR_WARN = "#ff9a44"        # Amber Warning
COLOR_DANGER = "#ff4b4b"      # Alert Red
COLOR_SUCCESS = "#00e676"     # Emerald Green
COLOR_PURPLE = "#9d4edd"      # Tech Purple

SYSTEM_COLOR_MAP = {
    "Boiler Plant": "#ff7b00",
    "Air Compressor System": "#00d2ff",
    "Cooling Tower": "#00e676",
    "Water Treatment Plant": "#9d4edd"
}


def calculate_kpis(df: pd.DataFrame, thresholds: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """Calculate key performance indicators from the filtered DataFrame."""
    if df.empty:
        return {
            "total_energy": 0,
            "total_downtime": 0,
            "avg_availability": 0.0,
            "avg_energy_per_unit": 0.0,
            "avg_efficiency_ratio": 0.0,
            "total_maintenance_cost": 0,
            "avg_energy_loss": 0.0,
            "avg_water_per_unit": 0.0,
            "peak_demand_max": 0,
            "total_records": 0,
            "downtime_alert": False,
            "availability_alert": False,
            "energy_loss_alert": False,
            "peak_demand_alert": False,
            "cost_alert": False
        }

    total_energy = float(df["total_energy_kwh"].sum())
    total_downtime = float(df["downtime_hours"].sum())
    avg_availability = float(df["equipment_availability"].mean())
    avg_energy_per_unit = float(df["energy_per_unit_kwh"].mean())
    avg_efficiency_ratio = float(df["energy_efficiency_ratio"].mean())
    total_maintenance_cost = float(df["maintenance_cost"].sum())
    avg_energy_loss = float(df["energy_loss_pct"].mean())
    avg_water_per_unit = float(df["water_per_unit_liters"].mean())
    peak_demand_max = float(df["peak_demand_kw"].max())
    total_records = len(df)

    kpis = {
        "total_energy": total_energy,
        "total_downtime": total_downtime,
        "avg_availability": avg_availability,
        "avg_energy_per_unit": avg_energy_per_unit,
        "avg_efficiency_ratio": avg_efficiency_ratio,
        "total_maintenance_cost": total_maintenance_cost,
        "avg_energy_loss": avg_energy_loss,
        "avg_water_per_unit": avg_water_per_unit,
        "peak_demand_max": peak_demand_max,
        "total_records": total_records,
    }

    if thresholds:
        max_dt = thresholds.get("max_downtime_hours", 25.0)
        min_av = thresholds.get("min_availability_pct", 0.92)
        max_loss = thresholds.get("max_energy_loss_pct", 0.08)
        max_peak = thresholds.get("max_peak_demand_kw", 1050.0)
        max_cost = thresholds.get("max_maintenance_cost", 280000.0)

        # Check breach conditions
        kpis["downtime_alert"] = bool((df["downtime_hours"] > max_dt).any())
        kpis["availability_alert"] = bool((df["equipment_availability"] < min_av).any())
        kpis["energy_loss_alert"] = bool((df["energy_loss_pct"] > max_loss).any())
        kpis["peak_demand_alert"] = bool((df["peak_demand_kw"] > max_peak).any())
        kpis["cost_alert"] = bool((df["maintenance_cost"] > max_cost).any())

    return kpis


def _apply_chart_layout(fig: go.Figure, title: str, x_title: str = "", y_title: str = "") -> go.Figure:
    """Apply unified enterprise dark styling to Plotly figures."""
    fig.update_layout(
        title={
            "text": f"<b>{title}</b>",
            "y": 0.95,
            "x": 0.02,
            "xanchor": "left",
            "yanchor": "top",
            "font": {"size": 15, "color": "#f1f5f9"}
        },
        template="plotly_dark",
        paper_bgcolor="rgba(15, 23, 42, 0.4)",
        plot_bgcolor="rgba(15, 23, 42, 0.2)",
        font={"family": "Inter, Segoe UI, sans-serif", "color": "#94a3b8", "size": 12},
        margin=dict(l=40, r=20, t=50, b=40),
        xaxis=dict(
            title=x_title,
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.07)",
            linecolor="rgba(255, 255, 255, 0.15)",
            tickfont={"size": 11, "color": "#cbd5e1"}
        ),
        yaxis=dict(
            title=y_title,
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.07)",
            linecolor="rgba(255, 255, 255, 0.15)",
            tickfont={"size": 11, "color": "#cbd5e1"}
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font={"size": 11, "color": "#cbd5e1"},
            bgcolor="rgba(0,0,0,0)"
        ),
        hoverlabel=dict(
            bgcolor="#1e293b",
            font_size=12,
            font_family="Inter, Segoe UI, sans-serif"
        )
    )
    return fig


def plot_monthly_energy_trend(df: pd.DataFrame) -> go.Figure:
    """Monthly Energy Consumption Trend Line & Area Chart."""
    if df.empty:
        fig = go.Figure()
        return _apply_chart_layout(fig, "Monthly Energy Consumption Trend (kWh)")

    # Sort chronologically
    sorted_df = df.sort_values(by=["year", "month_num"]).copy()
    sorted_df["Period"] = sorted_df["month"] + " " + sorted_df["year"].astype(str)

    # Group by month/year if multiple systems
    grouped = sorted_df.groupby(["year", "month_num", "month"], as_index=False)["total_energy_kwh"].sum()
    grouped["Period"] = grouped["month"] + " " + grouped["year"].astype(str)

    fig = go.Figure()

    # Total area fill
    fig.add_trace(go.Scatter(
        x=grouped["Period"],
        y=grouped["total_energy_kwh"],
        mode="lines+markers",
        name="Total Energy (kWh)",
        line=dict(color=COLOR_PRIMARY, width=3, shape="spline"),
        marker=dict(size=8, color="#ffffff", line=dict(color=COLOR_PRIMARY, width=2)),
        fill="tozeroy",
        fillcolor="rgba(0, 210, 255, 0.12)"
    ))

    # Add system breakdown if multiple systems present
    systems = sorted_df["utility_system"].unique()
    if len(systems) > 1 and len(df) > len(grouped):
        for system in systems:
            sys_df = sorted_df[sorted_df["utility_system"] == system]
            fig.add_trace(go.Scatter(
                x=sys_df["Period"],
                y=sys_df["total_energy_kwh"],
                mode="lines",
                name=system,
                line=dict(width=1.5, dash="dot", color=SYSTEM_COLOR_MAP.get(system, "#94a3b8")),
                opacity=0.7
            ))

    return _apply_chart_layout(fig, "Monthly Energy Consumption Trend", "Reporting Period", "Total Energy (kWh)")


def plot_energy_by_system(df: pd.DataFrame) -> go.Figure:
    """Energy Consumption Breakdown by Utility System (Donut Chart)."""
    if df.empty:
        fig = go.Figure()
        return _apply_chart_layout(fig, "Energy Share by Utility System")

    sys_energy = df.groupby("utility_system", as_index=False)["total_energy_kwh"].sum()
    colors = [SYSTEM_COLOR_MAP.get(s, "#00d2ff") for s in sys_energy["utility_system"]]

    fig = go.Figure(data=[
        go.Pie(
            labels=sys_energy["utility_system"],
            values=sys_energy["total_energy_kwh"],
            hole=0.55,
            marker=dict(colors=colors, line=dict(color="#0f172a", width=2)),
            textinfo="label+percent",
            hoverinfo="label+value+percent",
            textfont=dict(size=12, color="#ffffff"),
            hovertemplate="<b>%{label}</b><br>Consumption: %{value:,.0f} kWh<br>Share: %{percent}<extra></extra>"
        )
    ])

    fig.update_layout(
        title={
            "text": "<b>Energy Share by Utility System</b>",
            "y": 0.95,
            "x": 0.02,
            "font": {"size": 15, "color": "#f1f5f9"}
        },
        template="plotly_dark",
        paper_bgcolor="rgba(15, 23, 42, 0.4)",
        plot_bgcolor="rgba(15, 23, 42, 0.2)",
        font={"family": "Inter, Segoe UI, sans-serif", "color": "#94a3b8", "size": 12},
        margin=dict(l=20, r=20, t=50, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
    )
    return fig


def plot_downtime_by_system(df: pd.DataFrame, threshold: float = 25.0) -> go.Figure:
    """Utility Downtime by System (Horizontal Bar Chart with Threshold)."""
    if df.empty:
        fig = go.Figure()
        return _apply_chart_layout(fig, "Total Downtime by Utility System (Hours)")

    grouped = df.groupby("utility_system", as_index=False)["downtime_hours"].sum().sort_values(by="downtime_hours")

    colors = [COLOR_DANGER if h > threshold else COLOR_SECONDARY for h in grouped["downtime_hours"]]

    fig = go.Figure(data=[
        go.Bar(
            y=grouped["utility_system"],
            x=grouped["downtime_hours"],
            orientation="h",
            marker=dict(
                color=colors,
                line=dict(color="rgba(255,255,255,0.2)", width=1)
            ),
            text=grouped["downtime_hours"].apply(lambda v: f"{v:.1f} hrs"),
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Downtime: %{x:.1f} Hours<extra></extra>"
        )
    ])

    return _apply_chart_layout(fig, "Downtime by Utility System", "Downtime (Hours)", "")


def plot_maintenance_cost_by_system(df: pd.DataFrame) -> go.Figure:
    """Maintenance Cost Breakdown by Utility System."""
    if df.empty:
        fig = go.Figure()
        return _apply_chart_layout(fig, "Maintenance Cost by System")

    grouped = df.groupby("utility_system", as_index=False)["maintenance_cost"].sum().sort_values(by="maintenance_cost", ascending=False)
    colors = [SYSTEM_COLOR_MAP.get(s, COLOR_PRIMARY) for s in grouped["utility_system"]]

    fig = go.Figure(data=[
        go.Bar(
            x=grouped["utility_system"],
            y=grouped["maintenance_cost"],
            marker=dict(
                color=colors,
                line=dict(color="rgba(255,255,255,0.2)", width=1)
            ),
            text=grouped["maintenance_cost"].apply(lambda v: f"${v:,.0f}"),
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Cost: $%{y:,.0f}<extra></extra>"
        )
    ])

    return _apply_chart_layout(fig, "Total Maintenance Cost by System", "Utility System", "Cost ($)")


def plot_availability_vs_efficiency(df: pd.DataFrame) -> go.Figure:
    """Equipment Availability (%) vs Energy Efficiency Ratio comparison across months."""
    if df.empty:
        fig = go.Figure()
        return _apply_chart_layout(fig, "Availability vs Efficiency Trend")

    sorted_df = df.sort_values(by=["year", "month_num"]).copy()
    grouped = sorted_df.groupby(["year", "month_num", "month"], as_index=False).agg({
        "equipment_availability": "mean",
        "energy_efficiency_ratio": "mean"
    })
    grouped["Period"] = grouped["month"]

    fig = go.Figure()

    # Availability line (percentage 0-100%)
    fig.add_trace(go.Scatter(
        x=grouped["Period"],
        y=grouped["equipment_availability"] * 100.0,
        mode="lines+markers",
        name="Equipment Availability (%)",
        line=dict(color=COLOR_SUCCESS, width=2.5),
        marker=dict(size=7),
        yaxis="y1"
    ))

    # Efficiency ratio line (0-1.0)
    fig.add_trace(go.Scatter(
        x=grouped["Period"],
        y=grouped["energy_efficiency_ratio"],
        mode="lines+markers",
        name="Efficiency Ratio",
        line=dict(color=COLOR_PRIMARY, width=2.5, dash="dash"),
        marker=dict(size=7),
        yaxis="y2"
    ))

    fig.update_layout(
        title={
            "text": "<b>Equipment Availability vs. Energy Efficiency Ratio</b>",
            "y": 0.95,
            "x": 0.02,
            "font": {"size": 15, "color": "#f1f5f9"}
        },
        template="plotly_dark",
        paper_bgcolor="rgba(15, 23, 42, 0.4)",
        plot_bgcolor="rgba(15, 23, 42, 0.2)",
        font={"family": "Inter, Segoe UI, sans-serif", "color": "#94a3b8", "size": 12},
        margin=dict(l=40, r=40, t=50, b=40),
        xaxis=dict(title="Month", gridcolor="rgba(255, 255, 255, 0.07)"),
        yaxis=dict(
            title=dict(text="Availability (%)", font=dict(color=COLOR_SUCCESS)),
            tickfont=dict(color=COLOR_SUCCESS),
            gridcolor="rgba(255, 255, 255, 0.07)",
            range=[75, 105]
        ),
        yaxis2=dict(
            title=dict(text="Efficiency Ratio", font=dict(color=COLOR_PRIMARY)),
            tickfont=dict(color=COLOR_PRIMARY),
            overlaying="y",
            side="right",
            range=[0.5, 1.1]
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def plot_energy_loss_and_water_trend(df: pd.DataFrame) -> go.Figure:
    """Energy Loss (%) and Water Consumption per Unit Produced."""
    if df.empty:
        fig = go.Figure()
        return _apply_chart_layout(fig, "Energy Loss (%) & Water Consumption Trend")

    sorted_df = df.sort_values(by=["year", "month_num"]).copy()
    grouped = sorted_df.groupby(["year", "month_num", "month"], as_index=False).agg({
        "energy_loss_pct": "mean",
        "water_per_unit_liters": "mean"
    })
    grouped["Period"] = grouped["month"]

    fig = go.Figure()

    # Energy Loss bar (pct)
    fig.add_trace(go.Bar(
        x=grouped["Period"],
        y=grouped["energy_loss_pct"] * 100.0,
        name="Energy Loss / Waste (%)",
        marker=dict(color=COLOR_WARN, opacity=0.85),
        yaxis="y1"
    ))

    # Water consumption line
    fig.add_trace(go.Scatter(
        x=grouped["Period"],
        y=grouped["water_per_unit_liters"],
        mode="lines+markers",
        name="Water per Unit (Liters)",
        line=dict(color=COLOR_ACCENT, width=3),
        marker=dict(size=8, color="#ffffff", line=dict(color=COLOR_ACCENT, width=2)),
        yaxis="y2"
    ))

    fig.update_layout(
        title={
            "text": "<b>Energy Loss (%) & Water Consumption (Liters/Unit)</b>",
            "y": 0.95,
            "x": 0.02,
            "font": {"size": 15, "color": "#f1f5f9"}
        },
        template="plotly_dark",
        paper_bgcolor="rgba(15, 23, 42, 0.4)",
        plot_bgcolor="rgba(15, 23, 42, 0.2)",
        font={"family": "Inter, Segoe UI, sans-serif", "color": "#94a3b8", "size": 12},
        margin=dict(l=40, r=40, t=50, b=40),
        xaxis=dict(title="Month", gridcolor="rgba(255, 255, 255, 0.07)"),
        yaxis=dict(
            title=dict(text="Energy Loss (%)", font=dict(color=COLOR_WARN)),
            tickfont=dict(color=COLOR_WARN),
            gridcolor="rgba(255, 255, 255, 0.07)"
        ),
        yaxis2=dict(
            title=dict(text="Water (Liters/Unit)", font=dict(color=COLOR_ACCENT)),
            tickfont=dict(color=COLOR_ACCENT),
            overlaying="y",
            side="right"
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def plot_peak_demand_trend(df: pd.DataFrame, threshold: float = 1050.0) -> go.Figure:
    """Peak Energy Demand (kW) Trend with Warning Threshold Reference Line."""
    if df.empty:
        fig = go.Figure()
        return _apply_chart_layout(fig, "Peak Energy Demand (kW)")

    sorted_df = df.sort_values(by=["year", "month_num"]).copy()
    sorted_df["Period"] = sorted_df["month"]

    fig = go.Figure()

    # Peak demand markers and bars
    fig.add_trace(go.Scatter(
        x=sorted_df["Period"],
        y=sorted_df["peak_demand_kw"],
        mode="lines+markers",
        name="Peak Demand (kW)",
        line=dict(color="#f43f5e", width=3),
        marker=dict(
            size=9,
            color=["#ff0055" if v > threshold else "#f43f5e" for v in sorted_df["peak_demand_kw"]],
            line=dict(color="#ffffff", width=1.5)
        ),
        hovertemplate="<b>%{x}</b><br>Peak Demand: %{y:,.0f} kW<extra></extra>"
    ))

    # Threshold horizontal line
    fig.add_hline(
        y=threshold,
        line_dash="dot",
        line_color="#fbbf24",
        line_width=2,
        annotation_text=f"Warning Threshold ({threshold:.0f} kW)",
        annotation_position="bottom right",
        annotation_font_color="#fbbf24"
    )

    return _apply_chart_layout(fig, "Peak Energy Demand Trend (kW)", "Month", "Peak Demand (kW)")
