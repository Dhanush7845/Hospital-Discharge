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
    render_callout
)
from modules.data_loader import init_session_data

st.set_page_config(
    page_title="About the Project | UAC Analytics",
    page_icon="📖",
    layout="wide"
)

inject_custom_css()

df_active = init_session_data(st.session_state)
df = render_sidebar_controls(df_active)

render_header(
    "About the Project: Institutional Background & Analytical Architecture",
    "Comprehensive academic documentation, legislative context, system architecture, data dictionary, and methodology."
)

st.markdown("""
<div class="content-card">
    <h3>🏛️ Executive Project Charter</h3>
    <p><b>Project Title:</b> Care Transition Efficiency & Placement Outcome Analytics</p>
    <p>
        <b>Background:</b> The Unaccompanied Alien Children (UAC) Program represents an intricate, multi-agency humanitarian
        care continuum established under the Homeland Security Act of 2002 and the William Wilberforce Trafficking Victims Protection
        Reauthorization Act (TVPRA) of 2008. The pipeline encompasses initial apprehension by U.S. Customs and Border Protection (CBP),
        temporary holding, prompt statutory transfer to the Department of Health and Human Services (HHS) Office of Refugee Resettlement (ORR),
        sheltered residential care, comprehensive medical and legal screening, case management, and safe discharge to thoroughly vetted sponsors.
    </p>
    <p>
        <b>Problem Statement:</b> Traditionally published governmental custody statistics report static, aggregated census counts.
        While these headcounts show immediate population sizes, aggregate custody numbers alone fail to reveal stage-wise transit velocity,
        inter-agency handoff friction, systemic backlog accumulations, weekend operational deceleration, and long-term placement stability.
    </p>
</div>
""", unsafe_allow_html=True)

col_obj1, col_obj2 = st.columns(2)
with col_obj1:
    st.markdown("""
    <div class="content-card">
        <h3>🎯 Primary Analytical Objectives</h3>
        <ul>
            <li><b>Quantify CBP-to-HHS Transition Efficiency:</b> Calculate empirical daily flow-to-stock turnover ratios across border holding facilities.</li>
            <li><b>Evaluate Community Placement Performance:</b> Measure discharge effectiveness indices relative to active HHS residential shelter census.</li>
            <li><b>Identify Custodial Bottlenecks:</b> Detect multi-day accumulation imbalances where inflows systematically outpace release capacity.</li>
            <li><b>Analyze Temporal & Periodicity Patterns:</b> Model operational velocity across weekdays, weekends, months, and quarters.</li>
            <li><b>Assess Outcome Stability:</b> Quantify placement consistency using standardized dispersion metrics and statistical process control charts.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_obj2:
    st.markdown("""
    <div class="content-card">
        <h3>🌟 Secondary Humanitarian & Policy Objectives</h3>
        <ul>
            <li><b>Support Expedited Safe Reunification:</b> Identify operational deceleration factors to minimize unnecessary custodial detention of vulnerable minors.</li>
            <li><b>Optimize Shelter Resource Allocation:</b> Provide early-warning indicators of impending shelter saturation following border intake surges.</li>
            <li><b>Inform Evidence-Based Policy Reforms:</b> Supply objective, reproducible metrics for legislative oversight committees and child welfare advocates.</li>
            <li><b>Bridge Inter-Agency Data Gaps:</b> Provide unified visibility spanning DHS border operations and HHS child welfare systems.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# System Architecture & Tech Stack
st.markdown("### 🏗️ Technical Architecture & Stack")
col_arch1, col_arch2 = st.columns(2)
with col_arch1:
    st.markdown("""
    <div class="content-card">
        <h3>💻 Technology Stack</h3>
        <ul>
            <li><b>Runtime Environment:</b> Python 3.11+</li>
            <li><b>Web Framework:</b> Streamlit (Multi-Page Architecture)</li>
            <li><b>Data Engineering:</b> Pandas 2.2+, NumPy 2.1+</li>
            <li><b>Interactive Visualizations:</b> Plotly Graph Objects & Plotly Express</li>
            <li><b>Statistical & ML Modeling:</b> SciPy, Scikit-learn, Seaborn, Matplotlib</li>
            <li><b>Automated Reporting:</b> ReportLab (Executive PDF Engine), OpenPyXL (Excel Workbooks)</li>
            <li><b>Testing Harness:</b> Pytest</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_arch2:
    st.markdown("""
    <div class="content-card">
        <h3>📂 Modular Project Structure</h3>
        <pre style="font-size: 0.82rem; background-color: #F8FAFC; padding: 0.75rem; border-radius: 6px; border: 1px solid #E2E8F0;">
care-transition-analytics/
├── app.py                      # Main Application Portal
├── requirements.txt            # Python Dependencies
├── README.md                   # Setup & Windows Instructions
├── data/                       # Bundled HHS UAC Archive
├── modules/
│   ├── data_cleaning.py        # Robust Cleaning & Sanitization
│   ├── data_loader.py          # Session State Management
│   ├── kpi_calculations.py    # Zero-Division Guarded Formulas
│   ├── bottleneck_detection.py # Flow Differentials & Persistence
│   ├── trend_analysis.py       # Multi-Scale Periodicity
│   ├── anomaly_detection.py    # Statistical Process Control
│   ├── recommendations.py     # Deterministic Rule Engine
│   ├── visualizations.py       # Plotly Executive Visuals
│   ├── report_generator.py     # ReportLab PDF & OpenPyXL Excel
│   └── utils.py                # Theming, CSS, Safe Operations
└── pages/                      # 12 Specialized Sub-Modules
        </pre>
    </div>
    """, unsafe_allow_html=True)

# Data Dictionary
st.markdown("### 📖 Standardized Data Dictionary")
data_dict_rows = [
    {"Variable Name": "Date", "Field Role": "Temporal Anchor", "Type": "Date (%Y-%m-%d)", "Definition": "Official reporting date of published government operational statistics."},
    {"Variable Name": "Children Apprehended*", "Field Role": "Inflow Movement", "Type": "Integer", "Definition": "Gross daily intake of unaccompanied minors apprehended at border and taken into CBP custody."},
    {"Variable Name": "Children in CBP Custody", "Field Role": "Custody Stock", "Type": "Integer", "Definition": "Static snapshot headcount of children physically in CBP border patrol holding at reporting time."},
    {"Variable Name": "Transferred out of CBP", "Field Role": "Inter-Agency Outflow", "Type": "Integer", "Definition": "Daily movement of children legally transferred from CBP custody to HHS ORR jurisdiction."},
    {"Variable Name": "Children in HHS Care", "Field Role": "Shelter Stock", "Type": "Integer", "Definition": "Static snapshot headcount of active census residing in HHS-funded grantee shelters and foster care."},
    {"Variable Name": "Discharged from HHS Care", "Field Role": "Placement Outflow", "Type": "Integer", "Definition": "Daily volume of children released from HHS shelter custody to verified adult sponsors."}
]
st.dataframe(pd.DataFrame(data_dict_rows), width="stretch")

# KPI Mathematical Formulations
st.markdown("### 📐 Formal Mathematical KPI Definitions")
st.markdown("""
<div class="content-card">
    <ol style="font-size: 0.92rem; color: #334155; line-height: 1.7;">
        <li><b>Transfer Efficiency Ratio (%):</b> <code>(Daily Transfers / CBP Custody Stock) × 100</code> — Measures custodial turnover velocity in border patrol facilities.</li>
        <li><b>Discharge Effectiveness Index (%):</b> <code>(Daily Discharges / HHS Care Stock) × 100</code> — Measures community placement velocity relative to total shelter census.</li>
        <li><b>Transfer-to-Intake Ratio (%):</b> <code>(Total Transfers / Total Apprehended) × 100</code> — Evaluates whether inter-agency handoffs match intake volume.</li>
        <li><b>Overall Pipeline Throughput (%):</b> <code>(Total Discharges / Total Apprehensions) × 100</code> — Assesses macroscopic system balance over a defined evaluation horizon.</li>
        <li><b>CBP Net Inflow Accumulation:</b> <code>Daily Apprehensions - Daily Transfers</code> — Net child retention within border holding.</li>
        <li><b>HHS Net Shelter Accumulation:</b> <code>Daily Transfers - Daily Discharges</code> — Net inventory expansion within residential shelter facilities.</li>
        <li><b>Overall Pipeline Backlog:</b> <code>Daily Apprehensions - Daily Discharges</code> — Net system-wide population growth or drawdown.</li>
        <li><b>Outcome Stability Score:</b> <code>100 / (1 + Coefficient of Variation)</code> — Standardized placement consistency index bounded between 0 and 100.</li>
    </ol>
</div>
""", unsafe_allow_html=True)

# Assumptions & Limitations
st.markdown("### ⚖️ Institutional Assumptions & Analytical Limitations")
st.markdown("""
<div class="content-card">
    <ul>
        <li><b>Movement vs. Stock Separation:</b> Daily apprehensions, transfers, and discharges represent movement flow events. CBP custody and HHS care figures represent static stock snapshots. Summing daily stock snapshots over time produces cumulative custody-days, not unique individual children.</li>
        <li><b>Aggregated vs. Individual-Level Tracking:</b> Public reporting datasets aggregate movements at the agency level. Consequently, calculated ratios describe system-wide throughput rates and must not be interpreted as individualized longitudinal transition probabilities.</li>
        <li><b>Discharge as a Placement Proxy:</b> HHS discharge statistics serve as a quantitative proxy for community placement. Datasets do not record post-release longitudinal outcomes, sponsor relationship category breakdowns (Category 1, 2, or 3), or legal court adjudication results.</li>
        <li><b>Irregular Reporting Cadence:</b> Records reflect business-day reporting cadences. Calendar days without published reports are not zero-activity days; they are unobserved reporting days.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

render_callout(
    "This platform is developed strictly for research, decision support, and policy analysis. "
    "All underlying calculations are deterministic, reproducible, and fully auditable.",
    "Academic Integrity Statement"
)
