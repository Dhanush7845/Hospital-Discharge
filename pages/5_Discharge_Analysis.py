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
    plot_efficiency_ratio_trend, plot_transfers_vs_discharges,
    plot_net_accumulation
)
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Discharge & Placement | UAC Analytics",
    page_icon="🏡",
    layout="wide"
)

inject_custom_css()

df_active = init_session_data(st.session_state)
df = render_sidebar_controls(df_active)

render_header(
    "Discharge & Placement Outcome Analysis",
    "Examine community placement velocity, shelter discharge effectiveness, and custodial exit dynamics."
)

if df.empty:
    st.warning("No data available for the selected filter range.")
    st.stop()

kpis = calculate_core_kpis(df)
df_calc = add_daily_metrics(df)

# Target Benchmark
de_threshold = st.slider(
    "⚙️ Operational Discharge Effectiveness Benchmark Target (%)",
    min_value=0.5,
    max_value=10.0,
    value=2.5,
    step=0.5,
    help="Target benchmark ratio of daily discharges relative to active HHS care shelter census."
)

# Core Placement KPIs
col_k1, col_k2, col_k3, col_k4 = st.columns(4)
with col_k1:
    st.html(render_kpi_card(
        "Total HHS Discharges",
        format_number(kpis["total_discharges"]),
        "Placement with sponsors"
    ))
with col_k2:
    st.html(render_kpi_card(
        "Discharge Effectiveness",
        format_percent(kpis["discharge_effectiveness"], 2),
        "Discharges / HHS Care Stock"
    ))
with col_k3:
    st.html(render_kpi_card(
        "Discharge-to-Transfer",
        format_percent(kpis["discharge_to_transfer_ratio"], 1),
        "Discharges / Inflow Transfers"
    ))
with col_k4:
    st.html(render_kpi_card(
        "Net Discharge Gap",
        f"{kpis['discharge_gap']:,}",
        "Transfers In - Discharges Out"
    ))

# Main Effectiveness Chart
st.markdown("### 📈 Longitudinal Discharge Effectiveness Index Trend")
fig_de = plot_efficiency_ratio_trend(
    df_calc,
    "discharge_effectiveness_index",
    "Daily Discharge Effectiveness Index with 7-Observation Rolling Baseline",
    threshold=de_threshold,
    y_label="Discharge Effectiveness (%)"
)
st.plotly_chart(fig_de, width="stretch")

# HHS Care vs Discharges & Discharge Gap
col_d1, col_d2 = st.columns(2)
with col_d1:
    fig_flow = plot_transfers_vs_discharges(df)
    st.plotly_chart(fig_flow, width="stretch")
with col_d2:
    fig_gap = plot_net_accumulation(
        df_calc,
        "discharge_gap",
        "Daily HHS Net Inflow Accumulation Gap (Transfers - Discharges)"
    )
    st.plotly_chart(fig_gap, width="stretch")

# Monthly Discharges & Extremes
st.markdown("### 🗓️ Monthly Placement Volume & Extremes")
monthly_dis = df_calc.groupby("year_month").agg(
    total_discharges=("discharges", "sum"),
    total_transfers=("transfers", "sum"),
    avg_hhs_care=("hhs_care", "mean"),
    mean_effectiveness=("discharge_effectiveness_index", "mean")
).reset_index()

col_m1, col_m2 = st.columns([2, 1])
with col_m1:
    fig_month_dis = px.bar(
        monthly_dis,
        x="year_month",
        y="total_discharges",
        title="<b>Gross Monthly Discharges (Community Placements)</b>",
        labels={"year_month": "Month", "total_discharges": "Discharges"},
        color="total_discharges",
        color_continuous_scale="Teal"
    )
    fig_month_dis.update_layout(
        plot_bgcolor="#FAFCFE",
        paper_bgcolor="white",
        height=380,
        margin=dict(l=40, r=40, t=55, b=40)
    )
    st.plotly_chart(fig_month_dis, width="stretch")

with col_m2:
    st.markdown("#### Performance Extremes")
    best_dis = df_calc.sort_values("discharges", ascending=False).iloc[0]
    worst_dis = df_calc.sort_values("discharges", ascending=True).iloc[0]
    
    st.markdown(f"""
    <div class="content-card">
        <div style="font-weight: 600; color: #166534;">🟢 Peak Placement Day:</div>
        <div style="font-size: 1.1rem; font-weight: 700; color: #1B365D;">{best_dis['date'].strftime('%b %d, %Y')}</div>
        <div style="font-size: 0.85rem; color: #64748B;">Discharges: <b>{best_dis['discharges']:,} children</b> (HHS Care Census: {best_dis['hhs_care']:,})</div>
    </div>
    <div class="content-card">
        <div style="font-weight: 600; color: #991B1B;">🔴 Lowest Placement Day:</div>
        <div style="font-size: 1.1rem; font-weight: 700; color: #1B365D;">{worst_dis['date'].strftime('%b %d, %Y')}</div>
        <div style="font-size: 0.85rem; color: #64748B;">Discharges: <b>{worst_dis['discharges']:,} children</b> (HHS Care Census: {worst_dis['hhs_care']:,})</div>
    </div>
    """, unsafe_allow_html=True)

render_callout(
    "In accordance with analytical standards, 'HHS discharge' serves as a quantitative placement proxy. "
    "Because public aggregate records do not contain individualized sponsor case identifiers, this analysis does not "
    "claim that every discharge represents a verified permanent reunification without post-release vetting.",
    "Placement Proxy Definition"
)
