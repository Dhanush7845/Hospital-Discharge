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
    plot_efficiency_ratio_trend, plot_intake_vs_transfers,
    plot_net_accumulation
)
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Transfer Efficiency | UAC Analytics",
    page_icon="⚡",
    layout="wide"
)

inject_custom_css()

df_active = init_session_data(st.session_state)
df = render_sidebar_controls(df_active)

render_header(
    "Transfer Efficiency Analysis: CBP-to-HHS Transit Dynamics",
    "Evaluate the velocity and efficiency of moving unaccompanied children from border patrol custody into HHS shelters."
)

if df.empty:
    st.warning("No data available for the selected filter range.")
    st.stop()

kpis = calculate_core_kpis(df)
df_calc = add_daily_metrics(df)

# Configurable Threshold Slider
te_threshold = st.slider(
    "⚙️ Operational Transfer Efficiency Benchmark Target (%)",
    min_value=5.0,
    max_value=100.0,
    value=25.0,
    step=5.0,
    help="Target benchmark ratio of daily transfers relative to active CBP custody stock."
)

# Core Efficiency KPIs
col_k1, col_k2, col_k3, col_k4 = st.columns(4)
with col_k1:
    st.html(render_kpi_card(
        "Aggregate Transfer Eff.",
        format_percent(kpis["transfer_efficiency"], 2),
        "Total Transfers / CBP Custody-Days"
    ))
with col_k2:
    st.html(render_kpi_card(
        "Mean Daily Efficiency",
        format_percent(kpis["daily_mean_transfer_efficiency"], 2),
        "Average of Daily Ratios"
    ))
with col_k3:
    st.html(render_kpi_card(
        "Transfer-to-Intake Ratio",
        format_percent(kpis["transfer_to_intake_ratio"], 1),
        "Transfers / Apprehensions Flow"
    ))
with col_k4:
    gap_color = "red" if kpis["transfer_gap"] > 0 else "green"
    st.html(render_kpi_card(
        "Gross Transfer Gap",
        f"{kpis['transfer_gap']:,}",
        "Net Inflow Accumulation in CBP"
    ))

# Main Efficiency Chart
st.markdown("### 📈 Longitudinal Transfer Efficiency Ratio Trend")
fig_te = plot_efficiency_ratio_trend(
    df_calc,
    "transfer_efficiency_ratio",
    "Daily Transfer Efficiency Ratio with 7-Observation Rolling Baseline",
    threshold=te_threshold,
    y_label="Transfer Efficiency (%)"
)
st.plotly_chart(fig_te, width="stretch")

# Intake vs Transfers & Transfer Gap
col_g1, col_g2 = st.columns(2)
with col_g1:
    fig_flow = plot_intake_vs_transfers(df)
    st.plotly_chart(fig_flow, width="stretch")
with col_g2:
    fig_gap = plot_net_accumulation(
        df_calc,
        "transfer_gap",
        "Daily Transfer Gap (Apprehensions - Transfers)"
    )
    st.plotly_chart(fig_gap, width="stretch")

# Monthly Aggregation and High/Low Extremes
st.markdown("### 🗓️ Monthly Efficiency Aggregations & Extremes")
monthly_te = df_calc.groupby("year_month").agg(
    total_apprehensions=("apprehensions", "sum"),
    total_transfers=("transfers", "sum"),
    avg_cbp_custody=("cbp_custody", "mean"),
    mean_efficiency=("transfer_efficiency_ratio", "mean")
).reset_index()

col_t1, col_t2 = st.columns([2, 1])
with col_t1:
    fig_month_te = px.bar(
        monthly_te,
        x="year_month",
        y="mean_efficiency",
        title="<b>Monthly Mean Transfer Efficiency Ratio (%)</b>",
        labels={"year_month": "Month", "mean_efficiency": "Mean Efficiency (%)"},
        color="mean_efficiency",
        color_continuous_scale="Blues"
    )
    fig_month_te.update_layout(
        plot_bgcolor="#FAFCFE",
        paper_bgcolor="white",
        height=380,
        margin=dict(l=40, r=40, t=55, b=40)
    )
    st.plotly_chart(fig_month_te, width="stretch")

with col_t2:
    st.markdown("#### Performance Extremes")
    best_day = df_calc.sort_values("transfer_efficiency_ratio", ascending=False).iloc[0]
    worst_day = df_calc.sort_values("transfer_efficiency_ratio", ascending=True).iloc[0]
    
    st.markdown(f"""
    <div class="content-card">
        <div style="font-weight: 600; color: #166534;">🟢 Peak Efficiency Day:</div>
        <div style="font-size: 1.1rem; font-weight: 700; color: #1B365D;">{best_day['date'].strftime('%b %d, %Y')}</div>
        <div style="font-size: 0.85rem; color: #64748B;">Efficiency: <b>{best_day['transfer_efficiency_ratio']:.1f}%</b> ({best_day['transfers']} transferred / {best_day['cbp_custody']} in custody)</div>
    </div>
    <div class="content-card">
        <div style="font-weight: 600; color: #991B1B;">🔴 Lowest Efficiency Day:</div>
        <div style="font-size: 1.1rem; font-weight: 700; color: #1B365D;">{worst_day['date'].strftime('%b %d, %Y')}</div>
        <div style="font-size: 0.85rem; color: #64748B;">Efficiency: <b>{worst_day['transfer_efficiency_ratio']:.1f}%</b> ({worst_day['transfers']} transferred / {worst_day['cbp_custody']} in custody)</div>
    </div>
    """, unsafe_allow_html=True)

render_callout(
    "Transfer Efficiency is defined as (Transfers / CBP Custody) × 100. This metric is a transfer-to-custody-stock "
    "ratio that indicates the turnover velocity of the border holding census on that reporting day. It should not be "
    "interpreted as an individual child's empirical probability of being transferred.",
    "Methodological Foundation"
)
