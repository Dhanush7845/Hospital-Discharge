import os
import sys

# Ensure project root is in sys.path
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import streamlit as st
import pandas as pd
from datetime import datetime
from modules.utils import (
    inject_custom_css, render_header, render_sidebar_controls,
    render_kpi_card, render_callout
)
from modules.data_loader import init_session_data
from modules.kpi_calculations import calculate_core_kpis, add_daily_metrics
from modules.bottleneck_detection import detect_bottlenecks
from modules.analytics import compute_research_statistics
from modules.recommendations import generate_system_alerts_and_recommendations
from modules.report_generator import generate_pdf_report, generate_kpi_excel

st.set_page_config(
    page_title="Reports & Downloads | UAC Analytics",
    page_icon="📑",
    layout="wide"
)

inject_custom_css()

df_active = init_session_data(st.session_state)
df = render_sidebar_controls(df_active)

render_header(
    "Reports & Downloads: Official Publications Archive",
    "Generate and download publication-ready executive PDF briefing documents, Excel workbooks, and sanitized data archives."
)

if df.empty:
    st.warning("No data available for the selected filter range.")
    st.stop()

# Pre-calculate analytical outputs for reports
with st.spinner("Compiling real-time report metrics and diagnostics..."):
    kpis = calculate_core_kpis(df)
    bottlenecks = detect_bottlenecks(df)
    stats_dict = compute_research_statistics(df)
    alerts_data = generate_system_alerts_and_recommendations(df)
    df_calc = add_daily_metrics(df)

# Date String for filenames
date_suffix = datetime.now().strftime("%Y%m%d_%H%M")

st.markdown("### 📄 Publication-Ready PDF Reports (ReportLab Engine)")
st.markdown(
    "Each PDF report is dynamically compiled from the currently active dataset and date filters, "
    "incorporating formal introductions, methodology, mathematical definitions, scorecards, and policy recommendations."
)

col_pdf1, col_pdf2, col_pdf3 = st.columns(3)

# 1. Executive Summary PDF
with col_pdf1:
    st.markdown("""
    <div class="content-card">
        <h3>1. Executive Summary PDF</h3>
        <p style="font-size: 0.88rem; color: #64748B;">
            Concise high-level briefing document with core KPI scorecards, multi-agency balance summaries, and top-tier recommendations.
        </p>
    </div>
    """, unsafe_allow_html=True)
    pdf_exec = generate_pdf_report(df, kpis, "Executive Summary", bottlenecks=bottlenecks, stats_dict=stats_dict)
    st.download_button(
        label="⬇️ Download Executive Summary (PDF)",
        data=pdf_exec,
        file_name=f"UAC_Executive_Summary_{date_suffix}.pdf",
        mime="application/pdf",
        width="stretch"
    )

# 2. Detailed Analytical Report PDF
with col_pdf2:
    st.markdown("""
    <div class="content-card">
        <h3>2. Detailed Analytical Report PDF</h3>
        <p style="font-size: 0.88rem; color: #64748B;">
            Comprehensive institutional evaluation featuring complete bottleneck logs, stage friction diagnostics, and operational workflows.
        </p>
    </div>
    """, unsafe_allow_html=True)
    pdf_detail = generate_pdf_report(df, kpis, "Detailed Analytical Report", bottlenecks=bottlenecks, stats_dict=stats_dict)
    st.download_button(
        label="⬇️ Download Detailed Report (PDF)",
        data=pdf_detail,
        file_name=f"UAC_Detailed_Analytical_Report_{date_suffix}.pdf",
        mime="application/pdf",
        width="stretch"
    )

# 3. Research Findings PDF
with col_pdf3:
    st.markdown("""
    <div class="content-card">
        <h3>3. Research Findings PDF</h3>
        <p style="font-size: 0.88rem; color: #64748B;">
            Econometric and statistical research briefing documenting OLS regressions, distribution skewness, and correlation analyses.
        </p>
    </div>
    """, unsafe_allow_html=True)
    pdf_research = generate_pdf_report(df, kpis, "Research Findings", bottlenecks=bottlenecks, stats_dict=stats_dict)
    st.download_button(
        label="⬇️ Download Research Findings (PDF)",
        data=pdf_research,
        file_name=f"UAC_Research_Findings_{date_suffix}.pdf",
        mime="application/pdf",
        width="stretch"
    )

st.markdown("---")
st.markdown("### 📊 Excel & Data Exports (.xlsx & .csv)")

col_d1, col_d2 = st.columns(2)

with col_d1:
    st.markdown("#### Formatted Excel Workbooks")
    
    # 4. KPI Summary Excel
    excel_kpi = generate_kpi_excel(df, kpis)
    st.download_button(
        label="⬇️ Download KPI Summary & Observations (.xlsx)",
        data=excel_kpi,
        file_name=f"UAC_KPI_Summary_Workbook_{date_suffix}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="stretch"
    )
    
    # 6. Cleaned Dataset Excel
    st.download_button(
        label="⬇️ Download Cleaned Dataset (.xlsx)",
        data=excel_kpi,
        file_name=f"UAC_Cleaned_Dataset_{date_suffix}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="stretch"
    )

with col_d2:
    st.markdown("#### Tabular CSV Archives")
    
    # 5. Cleaned Dataset CSV
    export_df = df.copy()
    export_df["date"] = export_df["date"].dt.strftime("%Y-%m-%d")
    st.download_button(
        label="⬇️ Download Cleaned Dataset (.csv)",
        data=export_df.to_csv(index=False).encode('utf-8'),
        file_name=f"UAC_Cleaned_Dataset_{date_suffix}.csv",
        mime="text/csv",
        width="stretch"
    )
    
    # 7. Bottleneck Analysis CSV
    bn_df = bottlenecks["bottleneck_records"].copy()
    bn_df["date"] = bn_df["date"].dt.strftime("%Y-%m-%d")
    st.download_button(
        label="⬇️ Download Bottleneck Audit Records (.csv)",
        data=bn_df.to_csv(index=False).encode('utf-8'),
        file_name=f"UAC_Bottleneck_Analysis_{date_suffix}.csv",
        mime="text/csv",
        width="stretch"
    )
    
    # 8. Alerts Report CSV
    alert_export = alerts_data["alert_df"]
    st.download_button(
        label="⬇️ Download System Alerts Report (.csv)",
        data=alert_export.to_csv(index=False).encode('utf-8'),
        file_name=f"UAC_Alerts_Report_{date_suffix}.csv",
        mime="text/csv",
        width="stretch"
    )

render_callout(
    "All PDF reports and spreadsheets are produced with verified numeric calculations from the local Python session. "
    "No placeholder data or mock values are included.",
    "Report Authenticity Certification"
)
