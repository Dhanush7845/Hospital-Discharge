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
from modules.analytics import compute_research_statistics
from modules.visualizations import (
    plot_correlation_heatmap, plot_regression_scatter
)
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Research & Statistical Insights | UAC Analytics",
    page_icon="🔬",
    layout="wide"
)

inject_custom_css()

df_active = init_session_data(st.session_state)
df = render_sidebar_controls(df_active)

render_header(
    "Research & Statistical Insights: Empirical Econometrics",
    "Exploratory data analysis, multi-stage correlation modeling, distribution diagnostics, and linear regressions."
)

if df.empty:
    st.warning("No data available for the selected filter range.")
    st.stop()

# Compute Research Stats
stats_results = compute_research_statistics(df)
desc_stats = stats_results["descriptive_stats"]
corr_matrix = stats_results["correlation_matrix"]
outliers = stats_results["outlier_summary"]
regressions = stats_results["regressions"]
insights = stats_results["insights"]
df_calc = stats_results["df_with_metrics"]

tab_desc, tab_corr, tab_reg, tab_dist = st.tabs([
    "📋 Descriptive Statistics & Outliers",
    "🌡️ Correlation Matrix & Heatmap",
    "📉 Regression & Relationship Modeling",
    "📊 Probability Distributions & Boxplots"
])

# ----------------- TAB 1: DESCRIPTIVE -----------------
with tab_desc:
    st.markdown("### 📋 Extended Parametric & Non-Parametric Statistics")
    st.dataframe(desc_stats.style.format("{:,.2f}"), width="stretch")
    
    st.markdown("### 🔍 Outlier Audit Summary (IQR 1.5× Rule)")
    outlier_rows = []
    for col, o_info in outliers.items():
        outlier_rows.append({
            "Pipeline Metric": col.replace('_', ' ').title(),
            "Q25 (1st Quartile)": f"{o_info['q25']:,.1f}",
            "Q75 (3rd Quartile)": f"{o_info['q75']:,.1f}",
            "IQR": f"{o_info['iqr']:,.1f}",
            "Lower Fence": f"{o_info['lower_fence']:,.1f}",
            "Upper Fence": f"{o_info['upper_fence']:,.1f}",
            "Outlier Count": f"{o_info['outlier_count']:,} days",
            "Outlier Share": f"{o_info['outlier_pct']:.1f}%"
        })
    st.dataframe(pd.DataFrame(outlier_rows), width="stretch")

# ----------------- TAB 2: CORRELATION -----------------
with tab_corr:
    st.markdown("### 🌡️ Cross-Metric Pearson Correlation Heatmap")
    fig_corr = plot_correlation_heatmap(corr_matrix)
    st.plotly_chart(fig_corr, width="stretch")
    
    # Correlation vs Causation Box
    st.markdown("""
    <div class="content-card">
        <h3>⚠️ Critical Methodological Principle: Correlation vs. Causation</h3>
        <p style="font-size: 0.92rem; color: #334155; line-height: 1.5; margin-bottom: 0;">
            A strong positive correlation between CBP Custody and HHS Care census does <b>not</b> indicate that CBP custody directly causes HHS shelter growth.
            Rather, both are driven by an underlying exogenous common cause: border apprehension surge events.
            Furthermore, daily transfers lag apprehensions due to legal mandates (such as the 72-hour TVPRA requirement) and physical bed availability.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ----------------- TAB 3: REGRESSIONS -----------------
with tab_reg:
    st.markdown("### 📉 Empirical Relationship Modeling (Ordinary Least Squares)")
    reg_names = list(regressions.keys())
    if reg_names:
        selected_reg = st.selectbox("Select Relationship Pair to Model:", options=reg_names)
        reg_info = regressions[selected_reg]
        
        col_r1, col_r2 = st.columns([2, 1])
        with col_r1:
            fig_scatter = plot_regression_scatter(df_calc, reg_info["x_col"], reg_info["y_col"], reg_info)
            st.plotly_chart(fig_scatter, width="stretch")
            
        with col_r2:
            st.markdown(f"#### Model Diagnostics: {selected_reg}")
            st.markdown(f"""
            <div class="content-card">
                <div style="font-size: 0.85rem; color: #64748B;">Dependent Variable (Y): <b>{reg_info['y_col']}</b></div>
                <div style="font-size: 0.85rem; color: #64748B;">Independent Variable (X): <b>{reg_info['x_col']}</b></div>
                <hr style="margin: 0.5rem 0; border-color: #E2E8F0;">
                <div style="font-size: 1.1rem; font-weight: 700; color: #1B365D;">R² = {reg_info['r_squared']:.4f}</div>
                <div style="font-size: 0.88rem; color: #334155;">Correlation (r): <b>{reg_info['r_value']:.4f}</b></div>
                <div style="font-size: 0.88rem; color: #334155;">Slope (β₁): <b>{reg_info['slope']:.4f}</b></div>
                <div style="font-size: 0.88rem; color: #334155;">Intercept (β₀): <b>{reg_info['intercept']:.2f}</b></div>
                <div style="font-size: 0.88rem; color: #334155;">p-value: <b>{reg_info['p_value']:.4e}</b></div>
                <div style="font-size: 0.88rem; color: #334155;">Standard Error: <b>{reg_info['std_err']:.4f}</b></div>
            </div>
            """, unsafe_allow_html=True)
            
    # Automated Observations
    st.markdown("#### Automated Statistical Observations")
    for ins in insights:
        st.markdown(f"• {ins}")

# ----------------- TAB 4: DISTRIBUTIONS -----------------
with tab_dist:
    st.markdown("### 📊 Distribution Shapes and Multimodality")
    col_dist1, col_dist2 = st.columns(2)
    with col_dist1:
        fig_box_stock = px.box(
            df_calc[["cbp_custody", "hhs_care"]],
            title="<b>Custodial Stock Distributions (Log-Scaled Census)</b>",
            log_y=True,
            color_discrete_sequence=["#1B365D", "#0077B6"]
        )
        fig_box_stock.update_layout(plot_bgcolor="#FAFCFE", paper_bgcolor="white", height=380)
        st.plotly_chart(fig_box_stock, width="stretch")
        
    with col_dist2:
        fig_box_flows = px.box(
            df_calc[["apprehensions", "transfers", "discharges"]],
            title="<b>Daily Flow Movement Distributions</b>",
            color_discrete_sequence=["#F4A261", "#0077B6", "#2A9D8F"]
        )
        fig_box_flows.update_layout(plot_bgcolor="#FAFCFE", paper_bgcolor="white", height=380)
        st.plotly_chart(fig_box_flows, width="stretch")

render_callout(
    "All regression models are ordinary least squares (OLS) estimations on the active date filter. "
    "Calculations protect against numerical singularities and report p-values alongside standard errors.",
    "Statistical Governance"
)
