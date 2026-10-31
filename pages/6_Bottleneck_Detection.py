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
    render_kpi_card, render_callout, format_number
)
from modules.data_loader import init_session_data
from modules.bottleneck_detection import detect_bottlenecks
from modules.visualizations import plot_net_accumulation
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Bottleneck & Backlog | UAC Analytics",
    page_icon="⚠️",
    layout="wide"
)

inject_custom_css()

df_active = init_session_data(st.session_state)
df = render_sidebar_controls(df_active)

render_header(
    "Bottleneck & Backlog Detection Architecture",
    "Identify custodial friction, sustained stage imbalances, and multi-day accumulation pressures across the pipeline."
)

if df.empty:
    st.warning("No data available for the selected filter range.")
    st.stop()

# Threshold Configuration in an expandable panel
with st.expander("⚙️ Configure Bottleneck Alert & Persistence Parameters", expanded=False):
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    with col_p1:
        cbp_thresh = st.number_input("CBP Net Thresh (Appr - Trans)", value=20.0, step=5.0)
    with col_p2:
        hhs_thresh = st.number_input("HHS Net Thresh (Trans - Disch)", value=30.0, step=5.0)
    with col_p3:
        overall_thresh = st.number_input("Overall Net Thresh (Appr - Disch)", value=25.0, step=5.0)
    with col_p4:
        min_streak = st.number_input("Min Consecutive Obs Streak", min_value=2, max_value=10, value=3)

# Run Bottleneck Engine
bn_results = detect_bottlenecks(
    df,
    cbp_threshold=cbp_thresh,
    hhs_threshold=hhs_thresh,
    overall_threshold=overall_thresh,
    min_consecutive_obs=min_streak
)
summary = bn_results["summary"]
df_bn = bn_results["bottleneck_records"]
sustained_events = bn_results["sustained_events"]
counts = bn_results["severity_counts"]

# Severity KPI Summary
col_b1, col_b2, col_b3, col_b4 = st.columns(4)
with col_b1:
    st.html(render_kpi_card(
        "Normal Days (Green)",
        f"{counts.get('Green', 0):,}",
        "Flow within normal operating bands"
    ))
with col_b2:
    st.html(render_kpi_card(
        "Moderate Days (Yellow)",
        f"{counts.get('Yellow', 0):,}",
        "Single-stage elevated accumulation"
    ))
with col_b3:
    st.html(render_kpi_card(
        "High Concern Days (Red)",
        f"{counts.get('Red', 0):,}",
        "Severe friction / sustained surge"
    ))
with col_b4:
    st.html(render_kpi_card(
        "Sustained Episodes",
        f"{len(sustained_events):,}",
        f"Streaks ≥ {min_streak} consecutive observations"
    ))

# Main Net Accumulation Charts
st.markdown("### 📊 Net Accumulation Flow Balances")
tab_cbp, tab_hhs, tab_ovr = st.tabs([
    "CBP Net Intake Accumulation",
    "HHS Net Shelter Accumulation",
    "Overall Pipeline Net Accumulation"
])

with tab_cbp:
    fig_cbp = plot_net_accumulation(
        df_bn,
        "cbp_net_accumulation",
        "CBP Daily Net Inflow Accumulation (Apprehensions - Transfers)"
    )
    st.plotly_chart(fig_cbp, width="stretch")
    st.caption("Positive (Red) bars indicate border intake exceeded transfers. Negative (Green) bars indicate CBP clearance.")

with tab_hhs:
    fig_hhs = plot_net_accumulation(
        df_bn,
        "hhs_net_accumulation",
        "HHS Daily Net Shelter Accumulation (Transfers - Discharges)"
    )
    st.plotly_chart(fig_hhs, width="stretch")
    st.caption("Positive (Red) bars indicate shelter census growth. Negative (Green) bars indicate community placement exceeded transfers.")

with tab_ovr:
    fig_ovr = plot_net_accumulation(
        df_bn,
        "overall_net_accumulation",
        "Total Pipeline Net Accumulation (Apprehensions - Discharges)"
    )
    st.plotly_chart(fig_ovr, width="stretch")
    st.caption("System-wide flow differential: intake arrivals vs community placements.")

# Sustained Imbalance Identification Table
st.markdown("### 🚨 Sustained Pipeline Friction Episodes")
if sustained_events:
    event_rows = []
    for e in sustained_events:
        event_rows.append({
            "Stage / Bottleneck Category": e["stage"],
            "Start Date": e["start_date"].strftime("%Y-%m-%d"),
            "End Date": e["end_date"].strftime("%Y-%m-%d"),
            "Consecutive Obs": e["consecutive_obs"],
            "Total Accumulated": f"+{e['total_net_accumulation']:,} children",
            "Avg Daily Accumulation": f"+{e['avg_daily_accumulation']:.1f}/day",
            "Alert Severity": e["severity"]
        })
    st.dataframe(pd.DataFrame(event_rows), width="stretch")
else:
    st.info("No sustained imbalance episodes detected matching the current streak threshold.")

# Detailed Bottleneck Observation Table with Filtering
st.markdown("### 📋 Daily Observation Bottleneck Audit Table")
col_f1, col_f2 = st.columns([2, 1])
with col_f1:
    severity_filter = st.multiselect(
        "Filter by Severity",
        options=["Red", "Yellow", "Green"],
        default=["Red", "Yellow"]
    )
with col_f2:
    table_rows = st.number_input("Max Display Rows", min_value=10, max_value=len(df_bn), value=25, step=5)

filtered_table = df_bn[df_bn["severity"].isin(severity_filter)].copy()
display_cols = [
    "date", "severity", "apprehensions", "cbp_custody", "transfers", "cbp_net_accumulation",
    "hhs_care", "discharges", "hhs_net_accumulation", "overall_net_accumulation"
]
display_table = filtered_table[display_cols].sort_values("overall_net_accumulation", ascending=False).head(table_rows)
if not display_table.empty and "date" in display_table.columns:
    display_table["date"] = display_table["date"].dt.strftime("%Y-%m-%d")

st.dataframe(display_table, width="stretch")

render_callout(
    "Flow balances (Apprehensions - Transfers and Transfers - Discharges) are analytical net movement estimates, "
    "not literal snapshot counts of physical children in custody. For actual physical headcounts, always refer to the "
    "dedicated custody stock columns ('cbp_custody' and 'hhs_care'). Consecutive observation persistence calculates "
    "uninterrupted reporting day runs without inferring zero values on weekends or non-reporting dates.",
    "Critical Governance Clarification"
)
