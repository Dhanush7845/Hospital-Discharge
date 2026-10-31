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
from modules.recommendations import generate_system_alerts_and_recommendations

st.set_page_config(
    page_title="Alerts & Recommendations | UAC Analytics",
    page_icon="🚨",
    layout="wide"
)

inject_custom_css()

df_active = init_session_data(st.session_state)
df = render_sidebar_controls(df_active)

render_header(
    "Alert Management & Operational Recommendations",
    "Evidence-based decision-support engine translating pipeline diagnostics into prioritized executive recommendations."
)

if df.empty:
    st.warning("No data available for the selected filter range.")
    st.stop()

# Configurable Trigger Thresholds
with st.expander("⚙️ Adjust Alert Trigger Thresholds", expanded=False):
    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
    with col_t1:
        te_thresh = st.number_input("Low Transfer Eff. (%)", value=25.0, step=5.0)
    with col_t2:
        cbp_thresh = st.number_input("CBP Net Accumulation Thresh", value=20.0, step=5.0)
    with col_t3:
        hhs_thresh = st.number_input("HHS Net Accumulation Thresh", value=30.0, step=5.0)
    with col_t4:
        de_thresh = st.number_input("Low Discharge Eff. (%)", value=2.0, step=0.5)

# Generate Alerts & Recommendations
results = generate_system_alerts_and_recommendations(
    df,
    transfer_eff_threshold=te_thresh,
    cbp_net_threshold=cbp_thresh,
    hhs_net_threshold=hhs_thresh,
    discharge_eff_threshold=de_thresh
)

alerts = results["alerts"]
alert_df = results["alert_df"]

# Severity Summary Cards
col_a1, col_a2, col_a3, col_a4 = st.columns(4)
high_count = len([a for a in alerts if a["severity"] == "High"])
med_count = len([a for a in alerts if a["severity"] == "Medium"])
low_count = len([a for a in alerts if a["severity"] == "Low"])

with col_a1:
    st.html(render_kpi_card("Total Active Alerts", f"{len(alerts)}", "Algorithmic Trigger Flags"))
with col_a2:
    st.html(render_kpi_card("High Priority", f"{high_count}", "Immediate Action Advised"))
with col_a3:
    st.html(render_kpi_card("Medium Priority", f"{med_count}", "Operational Monitoring"))
with col_a4:
    st.html(render_kpi_card("Low / Informational", f"{low_count}", "Cadence Observations"))

# Severity Filter
st.markdown("### 🔍 Filter and Review Active Alerts")
selected_severities = st.multiselect(
    "Filter by Severity Level",
    options=["High", "Medium", "Low"],
    default=["High", "Medium", "Low"]
)

filtered_alerts = [a for a in alerts if a["severity"] in selected_severities]

if not filtered_alerts:
    st.success("No alerts match the chosen severity filter criteria.")
else:
    for a in filtered_alerts:
        sev_color = "red" if a["severity"] == "High" else ("yellow" if a["severity"] == "Medium" else "blue")
        st.markdown(f"""
        <div class="content-card" style="border-left: 5px solid {'#E63946' if a['severity'] == 'High' else ('#E76F51' if a['severity'] == 'Medium' else '#0077B6')};">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <span class="badge badge-{sev_color}">{a['severity']} Priority • {a['category']}</span>
                <span style="font-family: monospace; font-size: 0.8rem; color: #64748B;">{a['id']}</span>
            </div>
            <h3 style="margin-bottom: 0.4rem; color: #1B365D;">{a['title']}</h3>
            <div style="font-size: 0.88rem; color: #0077B6; font-weight: 600; margin-bottom: 0.5rem;">
                Empirical Indicator: {a['metric']}
            </div>
            <p style="font-size: 0.92rem; color: #334155; margin-bottom: 0.75rem; line-height: 1.5;">
                {a['description']}
            </p>
            <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 0.75rem 1rem; border-radius: 6px;">
                <b style="color: #1B365D;">💡 Actionable Recommendation:</b>
                <span style="font-size: 0.9rem; color: #1E293B; margin-left: 0.35rem;">{a['recommendation']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Export Alerts
st.markdown("### 💾 Export Alert Records")
if not alert_df.empty:
    csv_bytes = alert_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Export Alert Records to CSV",
        data=csv_bytes,
        file_name=f"UAC_System_Alerts_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        width="stretch"
    )

render_callout(
    "All diagnostic triggers and recommended interventions are derived entirely from deterministic calculations "
    "on the active reporting dataset. No external generative services or speculative models are used.",
    "System Decision-Support Standards"
)
