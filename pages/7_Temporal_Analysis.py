import os
import sys

# Ensure project root is in sys.path
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import streamlit as st
import pandas as pd
from modules.utils import (
    inject_custom_css, render_header, render_sidebar_controls,
    render_kpi_card, render_callout, format_number, format_percent
)
from modules.data_loader import init_session_data
from modules.trend_analysis import analyze_temporal_trends
from modules.visualizations import plot_weekday_vs_weekend_bar
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Temporal & Trend Analysis | UAC Analytics",
    page_icon="📅",
    layout="wide"
)

inject_custom_css()

df_active = init_session_data(st.session_state)
df = render_sidebar_controls(df_active)

render_header(
    "Temporal & Trend Analysis: Multi-Horizon Periodicity",
    "Analyze time-series dynamics across daily, weekly, monthly, quarterly, and weekday/weekend operating horizons."
)

if df.empty:
    st.warning("No data available for the selected filter range.")
    st.stop()

# Compute Temporal Analytics
trends = analyze_temporal_trends(df)
df_calc = trends["daily_with_metrics"]
monthly = trends["monthly"]
quarterly = trends["quarterly"]
yearly = trends["yearly"]
w_comp = trends["weekday_vs_weekend"]
day_comp = trends["day_of_week_breakdown"]

# Tabs for multi-scale analysis
tab_month, tab_week, tab_quarter, tab_year, tab_rolling = st.tabs([
    "🗓️ Monthly & MoM Dynamics",
    "🏢 Weekday vs. Weekend Cadence",
    "📊 Quarterly Aggregations",
    "🏛️ Yearly Macro Comparisons",
    "🌊 Rolling Averages & Smoothing"
])

# ----------------- TAB 1: MONTHLY -----------------
with tab_month:
    st.markdown("### 📈 Monthly Intake vs. Placement Totals")
    if not monthly.empty:
        fig_m = go.Figure()
        fig_m.add_trace(go.Bar(x=monthly["year_month"], y=monthly["total_apprehensions"], name="Apprehensions (Intake)", marker_color="#F4A261"))
        fig_m.add_trace(go.Bar(x=monthly["year_month"], y=monthly["total_transfers"], name="Transfers out of CBP", marker_color="#0077B6"))
        fig_m.add_trace(go.Bar(x=monthly["year_month"], y=monthly["total_discharges"], name="HHS Discharges", marker_color="#2A9D8F"))
        fig_m.update_layout(
            barmode="group",
            plot_bgcolor="#FAFCFE",
            paper_bgcolor="white",
            height=400,
            margin=dict(l=40, r=40, t=55, b=40),
            title="<b>Monthly Gross Flow Volumes</b>"
        )
        st.plotly_chart(fig_m, width="stretch")
        
        st.markdown("#### Month-over-Month (MoM) Growth (%)")
        fig_mom = go.Figure()
        fig_mom.add_trace(go.Scatter(x=monthly["year_month"], y=monthly["apprehensions_mom_pct"], mode="lines+markers", name="Apprehensions MoM %", line=dict(color="#F4A261", width=2)))
        fig_mom.add_trace(go.Scatter(x=monthly["year_month"], y=monthly["discharges_mom_pct"], mode="lines+markers", name="Discharges MoM %", line=dict(color="#2A9D8F", width=2)))
        fig_mom.add_hline(y=0, line_dash="dash", line_color="#94A3B8")
        fig_mom.update_layout(
            plot_bgcolor="#FAFCFE",
            paper_bgcolor="white",
            height=350,
            margin=dict(l=40, r=40, t=55, b=40),
            title="<b>Month-over-Month Flow Growth Rates (%)</b>"
        )
        st.plotly_chart(fig_mom, width="stretch")
        
        st.dataframe(monthly[[
            "year_month", "obs_count", "total_apprehensions", "total_transfers", "total_discharges",
            "avg_cbp_custody", "avg_hhs_care", "monthly_pipeline_throughput"
        ]].style.format({
            "total_apprehensions": "{:,.0f}",
            "total_transfers": "{:,.0f}",
            "total_discharges": "{:,.0f}",
            "avg_cbp_custody": "{:,.1f}",
            "avg_hhs_care": "{:,.1f}",
            "monthly_pipeline_throughput": "{:.1f}%"
        }), width="stretch")

# ----------------- TAB 2: WEEKDAY VS WEEKEND -----------------
with tab_week:
    st.markdown("### 🏢 Operational Cadence: Weekdays vs. Weekends")
    fig_w_bar = plot_weekday_vs_weekend_bar(w_comp)
    st.plotly_chart(fig_w_bar, width="stretch")
    
    st.markdown("#### Day-of-Week Detailed Averages")
    st.dataframe(day_comp.style.format({
        "avg_apprehensions": "{:,.1f}",
        "avg_transfers": "{:,.1f}",
        "avg_discharges": "{:,.1f}",
        "avg_cbp_custody": "{:,.1f}",
        "avg_hhs_care": "{:,.1f}",
        "avg_transfer_efficiency": "{:.2f}%",
        "avg_discharge_effectiveness": "{:.2f}%"
    }), width="stretch")

# ----------------- TAB 3: QUARTERLY -----------------
with tab_quarter:
    st.markdown("### 📊 Quarterly Aggregations & Seasonal Patterns")
    if not quarterly.empty:
        fig_q = px.bar(
            quarterly,
            x="quarter",
            y=["total_apprehensions", "total_transfers", "total_discharges"],
            barmode="group",
            title="<b>Quarterly Pipeline Movements</b>",
            color_discrete_map={
                "total_apprehensions": "#F4A261",
                "total_transfers": "#0077B6",
                "total_discharges": "#2A9D8F"
            }
        )
        fig_q.update_layout(plot_bgcolor="#FAFCFE", paper_bgcolor="white", height=380)
        st.plotly_chart(fig_q, width="stretch")
        st.dataframe(quarterly, width="stretch")

# ----------------- TAB 4: YEARLY -----------------
with tab_year:
    st.markdown("### 🏛️ Yearly Comparisons")
    if not yearly.empty:
        st.dataframe(yearly.style.format({
            "total_apprehensions": "{:,.0f}",
            "total_transfers": "{:,.0f}",
            "total_discharges": "{:,.0f}",
            "avg_cbp_custody": "{:,.1f}",
            "avg_hhs_care": "{:,.1f}",
            "pipeline_throughput": "{:.1f}%"
        }), width="stretch")

# ----------------- TAB 5: ROLLING AVERAGES -----------------
with tab_rolling:
    st.markdown("### 🌊 Multi-Period Rolling Averages")
    window_choice = st.selectbox("Select Rolling Window Size (Observations)", options=[7, 14, 30], index=0)
    
    df_calc[f"roll_app_{window_choice}"] = df_calc["apprehensions"].rolling(window=window_choice, min_periods=2).mean()
    df_calc[f"roll_dis_{window_choice}"] = df_calc["discharges"].rolling(window=window_choice, min_periods=2).mean()
    
    fig_roll = go.Figure()
    fig_roll.add_trace(go.Scatter(x=df_calc["date"], y=df_calc["apprehensions"], mode="markers", name="Daily Intake", opacity=0.3, marker=dict(color="#F4A261", size=4)))
    fig_roll.add_trace(go.Scatter(x=df_calc["date"], y=df_calc[f"roll_app_{window_choice}"], mode="lines", name=f"{window_choice}-Obs Rolling Intake", line=dict(color="#E76F51", width=2.5)))
    fig_roll.add_trace(go.Scatter(x=df_calc["date"], y=df_calc["discharges"], mode="markers", name="Daily Discharges", opacity=0.3, marker=dict(color="#2A9D8F", size=4)))
    fig_roll.add_trace(go.Scatter(x=df_calc["date"], y=df_calc[f"roll_dis_{window_choice}"], mode="lines", name=f"{window_choice}-Obs Rolling Discharges", line=dict(color="#1B365D", width=2.5)))
    fig_roll.update_layout(
        plot_bgcolor="#FAFCFE",
        paper_bgcolor="white",
        height=420,
        title=f"<b>Longitudinal Rolling Trendlines ({window_choice} Observations)</b>"
    )
    st.plotly_chart(fig_roll, width="stretch")

render_callout(
    "UAC reporting dates follow an irregular calendar distribution (predominantly business days, excluding federal holidays). "
    "All temporal aggregation models calculate totals and means across empirical reporting observations only, "
    "explicitly preventing unobserved calendar dates from being falsely computed as zero values.",
    "Temporal Aggregation Integrity Rule"
)
