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
from modules.kpi_calculations import calculate_core_kpis, add_daily_metrics
from modules.visualizations import (
    plot_pipeline_sankey, plot_intake_vs_transfers,
    plot_transfers_vs_discharges, plot_net_accumulation
)
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Care Pipeline Analysis | UAC Analytics",
    page_icon="🔄",
    layout="wide"
)

inject_custom_css()

df_active = init_session_data(st.session_state)
df = render_sidebar_controls(df_active)

render_header(
    "Care Pipeline Analysis: Multi-Stage Custodial Transitions",
    "Model the longitudinal transition from Border Apprehension & Custody to HHS Sheltering and Final Discharge."
)

if df.empty:
    st.warning("No data available for the selected filter range.")
    st.stop()

kpis = calculate_core_kpis(df)
df_calc = add_daily_metrics(df)

# Aggregation Cadence Selector
cadence = st.radio(
    "Select Aggregation Cadence:",
    options=["Daily Observations", "Weekly Totals", "Monthly Aggregations"],
    horizontal=True
)

if cadence == "Weekly Totals":
    df_plot = df_calc.resample("W-MON", on="date").agg({
        "apprehensions": "sum",
        "transfers": "sum",
        "discharges": "sum",
        "cbp_custody": "mean",
        "hhs_care": "mean",
        "cbp_net_accumulation": "sum",
        "hhs_net_accumulation": "sum",
        "overall_net_accumulation": "sum"
    }).reset_index()
elif cadence == "Monthly Aggregations":
    df_plot = df_calc.resample("ME", on="date").agg({
        "apprehensions": "sum",
        "transfers": "sum",
        "discharges": "sum",
        "cbp_custody": "mean",
        "hhs_care": "mean",
        "cbp_net_accumulation": "sum",
        "hhs_net_accumulation": "sum",
        "overall_net_accumulation": "sum"
    }).reset_index()
else:
    df_plot = df_calc

df_plot = df_plot.fillna(0)

# Pipeline Visuals: Sankey Diagram
st.markdown("### 🔀 Multi-Stage Movement Flow (Sankey Diagram)")
fig_sankey = plot_pipeline_sankey(df)
st.plotly_chart(fig_sankey, width="stretch")

# Volume Comparison by Pipeline Stage
st.markdown("### ⚖️ Stage-Wise Volume Comparison")
col_s1, col_s2, col_s3 = st.columns(3)
with col_s1:
    st.html(render_kpi_card(
        "Stage 1: Border Intake",
        format_number(kpis["total_apprehensions"]),
        f"Avg CBP Custody Stock: {kpis['avg_cbp_custody']:,.1f}"
    ))
with col_s2:
    st.html(render_kpi_card(
        "Stage 2: HHS Transfer",
        format_number(kpis["total_transfers"]),
        f"Transfer Ratio: {kpis['transfer_to_intake_ratio']:.1f}% of intake"
    ))
with col_s3:
    st.html(render_kpi_card(
        "Stage 3: Placement Discharge",
        format_number(kpis["total_discharges"]),
        f"Avg HHS Care Stock: {kpis['avg_hhs_care']:,.1f}"
    ))

# Comparative Charts
col_c1, col_c2 = st.columns(2)
with col_c1:
    fig_stage1 = go.Figure()
    fig_stage1.add_trace(go.Bar(x=df_plot["date"], y=df_plot["apprehensions"], name="Apprehensions", marker_color="#F4A261"))
    fig_stage1.add_trace(go.Bar(x=df_plot["date"], y=df_plot["transfers"], name="Transfers out of CBP", marker_color="#0077B6"))
    fig_stage1.update_layout(
        title=f"<b>Stage 1 to 2: Intake vs. Transfers ({cadence})</b>",
        barmode="group",
        plot_bgcolor="#FAFCFE",
        paper_bgcolor="white",
        height=380,
        margin=dict(l=40, r=40, t=55, b=40)
    )
    st.plotly_chart(fig_stage1, width="stretch")

with col_c2:
    fig_stage2 = go.Figure()
    fig_stage2.add_trace(go.Bar(x=df_plot["date"], y=df_plot["transfers"], name="HHS Inflow (Transfers)", marker_color="#0077B6"))
    fig_stage2.add_trace(go.Bar(x=df_plot["date"], y=df_plot["discharges"], name="HHS Discharges", marker_color="#2A9D8F"))
    fig_stage2.update_layout(
        title=f"<b>Stage 2 to 3: HHS Transfers vs. Discharges ({cadence})</b>",
        barmode="group",
        plot_bgcolor="#FAFCFE",
        paper_bgcolor="white",
        height=380,
        margin=dict(l=40, r=40, t=55, b=40)
    )
    st.plotly_chart(fig_stage2, width="stretch")

# Net Flow Differential Analysis
st.markdown("### 🌊 Net Stage Flow Differentials")
col_n1, col_n2 = st.columns(2)
with col_n1:
    fig_cbp_net = plot_net_accumulation(df_plot, "cbp_net_accumulation", f"CBP Net Accumulation Flow ({cadence})")
    st.plotly_chart(fig_cbp_net, width="stretch")
with col_n2:
    fig_hhs_net = plot_net_accumulation(df_plot, "hhs_net_accumulation", f"HHS Net Accumulation Flow ({cadence})")
    st.plotly_chart(fig_hhs_net, width="stretch")

render_callout(
    "Aggregate pipeline diagrams model system throughput and flow equilibria across government agencies. "
    "Because public data publishes aggregated daily movements rather than individualized case identifiers, "
    "this diagram depicts macroscopic system flow rather than tracked individual child journeys.",
    "Pipeline Modeling Clarification"
)
