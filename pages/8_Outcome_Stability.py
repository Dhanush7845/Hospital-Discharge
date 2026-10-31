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
from modules.anomaly_detection import calculate_outcome_stability
from modules.visualizations import plot_outcome_stability_anomalies
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Outcome Stability | UAC Analytics",
    page_icon="🎯",
    layout="wide"
)

inject_custom_css()

df_active = init_session_data(st.session_state)
df = render_sidebar_controls(df_active)

render_header(
    "Outcome Stability & Anomaly Detection Analysis",
    "Quantify the statistical consistency of HHS community placements and detect operational discharge anomalies."
)

if df.empty:
    st.warning("No data available for the selected filter range.")
    st.stop()

# Configurable Rolling Window
rolling_win = st.slider("⚙️ Rolling Stability Evaluation Window (Observations)", min_value=5, max_value=30, value=14, step=1)

# Run Stability Engine
stability = calculate_outcome_stability(df, rolling_window=rolling_win)
df_stability = stability["df_stability"]
anomalies = stability["anomalies"]

# Scorecard Cards
col_s1, col_s2, col_s3, col_s4 = st.columns(4)
with col_s1:
    st.html(render_kpi_card(
        "Outcome Stability Score",
        f"{stability['stability_score']:.1f} / 100",
        stability["stability_grade"]
    ))
with col_s2:
    st.html(render_kpi_card(
        "Coefficient of Variation (CV)",
        f"{stability['cv']:.2f}",
        "Standard Deviation / Mean"
    ))
with col_s3:
    st.html(render_kpi_card(
        "Mean Daily Discharges",
        f"{stability['mean_discharge']:.1f}",
        f"Std Dev (σ): {stability['std_discharge']:.1f}"
    ))
with col_s4:
    st.html(render_kpi_card(
        "Detected Anomalies",
        f"{len(anomalies):,}",
        "|Z-score| ≥ 2.5 Outliers"
    ))

# Methodology Explanation Box
st.markdown("""
<div class="content-card">
    <h3>📐 Methodological Definition: Outcome Stability Score</h3>
    <p style="font-size: 0.92rem; color: #334155; line-height: 1.5;">
        The <b>Outcome Stability Score</b> is an empirical index evaluating placement consistency across time:
    </p>
    <div style="background-color: #F1F5F9; padding: 0.75rem 1rem; border-radius: 6px; font-family: monospace; font-size: 1.05rem; color: #1B365D; margin-bottom: 0.75rem;">
        Outcome Stability Score = 100 / (1 + Coefficient of Variation)
    </div>
    <p style="font-size: 0.88rem; color: #64748B; margin-bottom: 0;">
        Where <i>Coefficient of Variation (CV) = Standard Deviation (σ) / Mean (μ)</i>.
        A perfectly uniform daily placement velocity produces CV = 0 and Stability Score = 100.
        Higher volatility decreases the score, penalizing unpredictable surges and severe operational drop-offs.
    </p>
</div>
""", unsafe_allow_html=True)

# Anomaly Control Chart
st.markdown("### 📊 Statistical Process Control Chart (Discharge Velocity & Outliers)")
fig_control = plot_outcome_stability_anomalies(df_stability)
st.plotly_chart(fig_control, width="stretch")

# Distribution & Rolling Stability
col_p1, col_p2 = st.columns(2)
with col_p1:
    fig_hist = px.histogram(
        df_stability,
        x="discharges",
        nbins=30,
        marginal="box",
        title="<b>Discharge Velocity Frequency Distribution</b>",
        color_discrete_sequence=["#1B365D"],
        labels={"discharges": "Discharges per Day"}
    )
    fig_hist.update_layout(plot_bgcolor="#FAFCFE", paper_bgcolor="white", height=380)
    st.plotly_chart(fig_hist, width="stretch")

with col_p2:
    fig_roll_stab = px.line(
        df_stability,
        x="date",
        y="rolling_stability_score",
        title=f"<b>Rolling Outcome Stability Score ({rolling_win}-Obs Horizon)</b>",
        labels={"rolling_stability_score": "Stability Score (0-100)", "date": "Reporting Date"},
        color_discrete_sequence=["#0077B6"]
    )
    fig_roll_stab.add_hline(y=60, line_dash="dash", line_color="#2A9D8F", annotation_text="Target Band (≥60)")
    fig_roll_stab.update_layout(plot_bgcolor="#FAFCFE", paper_bgcolor="white", height=380)
    st.plotly_chart(fig_roll_stab, width="stretch")

# Anomalies Table
st.markdown("### 🚨 Detected Statistical Anomaly Audit Log")
if not anomalies.empty:
    display_anom = anomalies[["date", "discharges", "rolling_mean", "z_score", "anomaly_type"]].copy()
    display_anom["date"] = display_anom["date"].dt.strftime("%Y-%m-%d")
    st.dataframe(display_anom.style.format({
        "discharges": "{:,.0f}",
        "rolling_mean": "{:,.1f}",
        "z_score": "{:+.2f}"
    }), width="stretch")
else:
    st.info("No discharge anomalies detected exceeding the 2.5 standard deviation threshold.")

render_callout(
    "Outcome stability metrics measure historical dispersion and consistency across recorded observations. "
    "These statistics are descriptive quality indicators and do not claim predictive forecasting accuracy "
    "without prospective validation against exogenous border policy changes.",
    "Statistical Validation Notice"
)
