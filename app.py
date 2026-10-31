import os
import sys

# Ensure root directory is in sys.path
_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import streamlit as st
import pandas as pd
from modules.utils import (
    inject_custom_css, render_header, render_kpi_card, render_kpi_grid,
    render_sidebar_controls, render_callout, format_number, format_percent
)
from modules.data_loader import init_session_data
from modules.kpi_calculations import calculate_core_kpis, add_daily_metrics
from modules.bottleneck_detection import detect_bottlenecks
from modules.visualizations import (
    plot_cbp_custody_trend, plot_hhs_care_trend,
    plot_pipeline_sankey
)

st.set_page_config(
    page_title="Care Transition Analytics | UAC Program",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_custom_css()

# Initialize active dataset
df_active = init_session_data(st.session_state)
df = render_sidebar_controls(df_active)

render_header(
    "Care Transition Efficiency & Placement Outcome Analytics",
    "Comprehensive Decision-Support & Operational Intelligence Platform for the U.S. Unaccompanied Children Program"
)

if df.empty:
    st.error("No dataset available. Please verify the bundled dataset or upload records in Dataset Explorer.")
    st.stop()

kpis = calculate_core_kpis(df)
bottlenecks = detect_bottlenecks(df)

# System Status Banner
status_banner = f"""<div class="content-card" style="background: linear-gradient(90deg, #FFFFFF 0%, #F8FAFC 100%); border-left: 5px solid #0077B6;">
<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
<div>
<span class="badge badge-blue">System Active &amp; Operational</span>
<span class="badge badge-green" style="margin-left: 0.4rem;">{kpis['observation_count']:,} Reporting Observations</span>
<span class="badge badge-blue" style="margin-left: 0.4rem;">Source: {st.session_state.get('dataset_source', 'Default Archive')}</span>
</div>
<div style="font-size: 0.85rem; color: #64748B;">
Reporting Archive: <b>{kpis['date_start'].strftime('%b %d, %Y')}</b> to <b>{kpis['date_end'].strftime('%b %d, %Y')}</b>
</div>
</div>
<div style="margin-top: 0.75rem; font-size: 0.95rem; color: #334155; line-height: 1.5;">
Welcome to the <b>Care Transition Efficiency &amp; Placement Outcome Analytics</b> system.
This enterprise portal models multi-stage transitions across U.S. Customs and Border Protection (CBP)
and Department of Health and Human Services (HHS) care, providing empirical throughput metrics,
bottleneck detection, and policy reporting.
</div>
</div>"""
st.html(status_banner)

# Executive Snapshot KPIs
st.markdown("### 🏛️ Executive Pipeline Scorecard")
cards = "".join([
    render_kpi_card("Total Apprehensions", format_number(kpis["total_apprehensions"]), "Gross border intake movements"),
    render_kpi_card("Total Transfers", format_number(kpis["total_transfers"]), "Movement from CBP to HHS care"),
    render_kpi_card("Average CBP Custody", format_number(kpis["avg_cbp_custody"], 1), "Daily active holding census"),
    render_kpi_card("Average HHS Care", format_number(kpis["avg_hhs_care"], 1), "Daily residential shelter census"),
    render_kpi_card("Total Discharges", format_number(kpis["total_discharges"]), "Community sponsor placements"),
    render_kpi_card("Transfer Efficiency", format_percent(kpis["transfer_efficiency"], 2), "(Transfers / CBP Custody) * 100"),
    render_kpi_card("Discharge Effectiveness", format_percent(kpis["discharge_effectiveness"], 2), "(Discharges / HHS Care) * 100"),
    render_kpi_card("Pipeline Throughput", format_percent(kpis["pipeline_throughput"], 1), "(Total Discharges / Total Intake) * 100")
])
st.html(f'<div class="kpi-grid">{cards}</div>')

# Pipeline Flow Visual
st.markdown("### 🔀 Macro-Level Pipeline Movement (Sankey Flow)")
fig_sankey = plot_pipeline_sankey(df)
st.plotly_chart(fig_sankey, width="stretch")

# Navigation Cards to 12 Specialized Pages using st.page_link
st.markdown("### 📑 Platform Navigation Hub (12 Specialized Modules)")
col_nav1, col_nav2, col_nav3 = st.columns(3)

with col_nav1:
    with st.container(border=True):
        st.markdown("#### 1. Executive Dashboard")
        st.caption("High-level overview of core pipeline metrics, dual custody stocks, and net balances.")
        st.page_link("pages/1_Executive_Dashboard.py", label="Open Dashboard", icon="📊")
        
    with st.container(border=True):
        st.markdown("#### 4. Transfer Efficiency")
        st.caption("Evaluate CBP-to-HHS movement velocity, transfer ratios, and holding turnover.")
        st.page_link("pages/4_Transfer_Efficiency.py", label="Open Transfer Efficiency", icon="⚡")
        
    with st.container(border=True):
        st.markdown("#### 7. Temporal & Trend Analysis")
        st.caption("Analyze daily, monthly, quarterly, and weekday vs. weekend operating cadences.")
        st.page_link("pages/7_Temporal_Analysis.py", label="Open Temporal Analysis", icon="📅")
        
    with st.container(border=True):
        st.markdown("#### 10. Research Insights")
        st.caption("Econometric modeling, correlation heatmaps, OLS regressions, and distributions.")
        st.page_link("pages/10_Research_Insights.py", label="Open Research Insights", icon="🔬")

with col_nav2:
    with st.container(border=True):
        st.markdown("#### 2. Dataset Explorer")
        st.caption("Upload custom CSV/Excel files, audit data quality, filter columns, and export data.")
        st.page_link("pages/2_Dataset_Explorer.py", label="Open Dataset Explorer", icon="📂")
        
    with st.container(border=True):
        st.markdown("#### 5. Discharge & Placement")
        st.caption("Examine HHS shelter exit effectiveness, discharge gaps, and placement proxies.")
        st.page_link("pages/5_Discharge_Analysis.py", label="Open Discharge Analysis", icon="🏡")
        
    with st.container(border=True):
        st.markdown("#### 8. Outcome Stability")
        st.caption("Measure placement consistency using Coefficient of Variation and anomaly detection.")
        st.page_link("pages/8_Outcome_Stability.py", label="Open Outcome Stability", icon="🎯")
        
    with st.container(border=True):
        st.markdown("#### 11. Reports & Downloads")
        st.caption("Download official Executive PDF briefings, formatted Excel books, and CSV files.")
        st.page_link("pages/11_Reports_Downloads.py", label="Open Reports & Downloads", icon="📑")

with col_nav3:
    with st.container(border=True):
        st.markdown("#### 3. Care Pipeline Analysis")
        st.caption("Interactive Sankey flow visualization, stage comparisons, and net flow balances.")
        st.page_link("pages/3_Care_Pipeline.py", label="Open Care Pipeline", icon="🔄")
        
    with st.container(border=True):
        st.markdown("#### 6. Bottleneck Detection")
        st.caption("Identify intake accumulation surges, shelter saturation, and multi-day friction streaks.")
        st.page_link("pages/6_Bottleneck_Detection.py", label="Open Bottleneck Detection", icon="⚠️")
        
    with st.container(border=True):
        st.markdown("#### 9. Alerts & Recommendations")
        st.caption("Review prioritized, deterministic recommendations derived from operational alerts.")
        st.page_link("pages/9_Alerts_Recommendations.py", label="Open Alerts & Recommendations", icon="🚨")
        
    with st.container(border=True):
        st.markdown("#### 12. About the Project")
        st.caption("Legislative background, primary objectives, data dictionary, formulas, and limitations.")
        st.page_link("pages/12_About_Project.py", label="Open About Project", icon="📖")

render_callout(
    "All analytical modules update dynamically when the global date filter in the sidebar is modified. "
    "Select any page from the sidebar navigation or click the links above.",
    "User Navigation Guidance"
)
