import os
import sys

# Ensure project root is in sys.path
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import streamlit as st
import pandas as pd
from modules.utils import (
    inject_custom_css, render_header, render_kpi_card, render_kpi_grid, render_callout,
    render_sidebar_controls, format_number, format_percent
)
from modules.data_loader import init_session_data
from modules.kpi_calculations import calculate_core_kpis, add_daily_metrics
from modules.bottleneck_detection import detect_bottlenecks
from modules.visualizations import (
    plot_cbp_custody_trend, plot_hhs_care_trend,
    plot_intake_vs_transfers, plot_transfers_vs_discharges,
    plot_monthly_discharge_trends, plot_overall_pipeline_performance
)

st.set_page_config(
    page_title="Executive Dashboard | UAC Analytics",
    page_icon="🏛️",
    layout="wide"
)

inject_custom_css()

# Retrieve active dataset
df_raw = init_session_data(st.session_state)
df = render_sidebar_controls(df_raw)

render_header(
    "Executive Dashboard: Care Transition Efficiency & Placement",
    "High-level pipeline overview tracking border apprehension, custodial transit, and community discharge."
)

if df.empty:
    st.warning("No data available for the selected filter range. Please expand the date selection.")
    st.stop()

# Calculate Core KPIs
kpis = calculate_core_kpis(df)
bottlenecks = detect_bottlenecks(df)
df_calc = add_daily_metrics(df)

# Render 8 Executive KPI Cards
cards = "".join([
    render_kpi_card("Total Apprehensions", format_number(kpis["total_apprehensions"]), "Gross intake movements"),
    render_kpi_card("Total Transfers", format_number(kpis["total_transfers"]), "Transfers out of CBP to HHS"),
    render_kpi_card("Avg CBP Custody", format_number(kpis["avg_cbp_custody"], 1), "Active holding stock snapshot"),
    render_kpi_card("Avg HHS Care", format_number(kpis["avg_hhs_care"], 1), "Active shelter census snapshot"),
    render_kpi_card("Total HHS Discharges", format_number(kpis["total_discharges"]), "Placements with vetted sponsors"),
    render_kpi_card("Transfer Efficiency", format_percent(kpis["transfer_efficiency"], 2), "(Transfers / CBP Custody) * 100"),
    render_kpi_card("Discharge Effectiveness", format_percent(kpis["discharge_effectiveness"], 2), "(Discharges / HHS Care) * 100"),
    render_kpi_card("Pipeline Throughput", format_percent(kpis["pipeline_throughput"], 1), "(Total Discharges / Total Intake) * 100")
])
st.html(f'<div class="kpi-grid">{cards}</div>')

# Performance Indicators & KPI Comparison Banner
throughput_note = (
    "Net Clearance Phase: Community discharges exceeded intake, drawing down pre-existing shelter census."
    if kpis["pipeline_throughput"] > 100 else
    "Net Inventory Growth Phase: Intake arrivals outpaced community discharges."
)
exec_banner = f"""<div class="content-card">
<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
<div>
<span class="badge badge-{'green' if kpis['overall_backlog_accumulation'] <= 0 else 'red'}">
Overall Pipeline Net Flow: {kpis['overall_backlog_accumulation']:+,} Children
</span>
<span class="badge badge-blue" style="margin-left: 0.4rem;">
Throughput: {kpis['pipeline_throughput']:.1f}%
</span>
<span class="badge badge-blue" style="margin-left: 0.4rem;">
Coverage: {kpis['observation_count']} Reporting Days
</span>
</div>
<div style="font-size: 0.85rem; color: #64748B;">
Reporting Window: <b>{kpis['date_start'].strftime('%b %d, %Y')}</b> to <b>{kpis['date_end'].strftime('%b %d, %Y')}</b>
</div>
</div>
<div style="margin-top: 0.75rem; font-size: 0.92rem; color: #334155; line-height: 1.5;">
<b>Dynamic Performance Assessment:</b> {throughput_note}
Daily transfers averaged <b>{df['transfers'].mean():.1f}</b> children/day against an average CBP holding population of <b>{kpis['avg_cbp_custody']:.1f}</b>.
Daily discharges averaged <b>{df['discharges'].mean():.1f}</b> placements/day against an average active shelter census of <b>{kpis['avg_hhs_care']:,.1f}</b>.
</div>
</div>"""
st.html(exec_banner)

# 6 Mandated Interactive Visualizations
st.markdown("### 📊 1 & 2: Custody Stocks (Census Snapshots)")
col1, col2 = st.columns(2)
with col1:
    fig_cbp = plot_cbp_custody_trend(df)
    st.plotly_chart(fig_cbp, width="stretch")
with col2:
    fig_hhs = plot_hhs_care_trend(df)
    st.plotly_chart(fig_hhs, width="stretch")

st.markdown("### 🔄 3 & 4: Daily Movements & Stage Transitions")
col3, col4 = st.columns(2)
with col3:
    fig_flow1 = plot_intake_vs_transfers(df)
    st.plotly_chart(fig_flow1, width="stretch")
with col4:
    fig_flow2 = plot_transfers_vs_discharges(df)
    st.plotly_chart(fig_flow2, width="stretch")

st.markdown("### 📈 5 & 6: Monthly Placement Trends & Overall Pipeline Performance")
col5, col6 = st.columns(2)
with col5:
    fig_monthly = plot_monthly_discharge_trends(df_calc)
    st.plotly_chart(fig_monthly, width="stretch")
with col6:
    fig_overall = plot_overall_pipeline_performance(df_calc)
    st.plotly_chart(fig_overall, width="stretch")

# Summary of Major Bottlenecks
st.markdown("### ⚠️ Summary of Major System Bottlenecks")
col_bn1, col_bn2, col_bn3 = st.columns(3)
counts = bottlenecks["severity_counts"]

with col_bn1:
    with st.container(border=True):
        st.markdown(f"#### 🟢 Normal Operations: {counts.get('Green', 0):,} Days")
        st.caption("Reporting days where daily inflows and outflows remained in balance within operational tolerances.")

with col_bn2:
    with st.container(border=True):
        st.markdown(f"#### 🟡 Moderate Concern: {counts.get('Yellow', 0):,} Days")
        st.caption("Reporting days with isolated single-stage accumulation (CBP intake friction or HHS shelter expansion).")

with col_bn3:
    with st.container(border=True):
        st.markdown(f"#### 🔴 High Concern: {counts.get('Red', 0):,} Days")
        st.caption("Reporting days with sustained multi-day surge friction or severe transfer clearance deficits.")

# Sustained Bottlenecks Brief
sustained = bottlenecks.get("sustained_events", [])
if sustained:
    st.markdown("#### 🚨 Active Friction Episodes Detected in Selected Scope")
    sust_rows = []
    for s in sustained[:5]:
        sust_rows.append({
            "Stage": s["stage"],
            "Span": f"{s['start_date'].strftime('%b %d, %Y')} to {s['end_date'].strftime('%b %d, %Y')}",
            "Consecutive Days": s["consecutive_obs"],
            "Net Inflow Accumulation": f"+{s['total_net_accumulation']:,} children",
            "Avg Daily Pace": f"+{s['avg_daily_accumulation']:.1f}/day",
            "Severity": s["severity"]
        })
    st.dataframe(pd.DataFrame(sust_rows), width="stretch")

render_callout(
    "Transfer Efficiency and Discharge Effectiveness represent flow-to-stock turnover rates. "
    "Custody levels reflect daily snapshot headcounts and must not be summed across dates. "
    "Pipeline throughput (>100%) indicates that cumulative community discharges exceeded gross new intake, "
    "drawing down children who entered the care continuum prior to the evaluated period.",
    "Executive Governance Notice"
)
