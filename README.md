# Care Transition Efficiency & Placement Outcome Analytics

An institutional, evidence-based data analytics and operational intelligence platform for the **U.S. Unaccompanied Alien Children (UAC) Program**, modeling the multi-stage care continuum spanning Customs and Border Protection (CBP) apprehension, custodial holding, Office of Refugee Resettlement (HHS/ORR) care, and safe community discharge to vetted sponsors.

---

## 🌟 Executive Summary & Key Capabilities

- **End-to-End Pipeline Modeling:** Analyzes transition efficiency between border holding facilities and HHS residential shelters.
- **Custody Stock vs. Movement Flow Disaggregation:** Distinguishes between daily static custody headcounts (stocks) and daily transition volumes (flows).
- **Algorithmic Bottleneck & Backlog Detection:** Calculates CBP, HHS, and overall net accumulations and persistence streaks to identify friction points.
- **Empirical Outcome Stability Scoring:** Evaluates placement velocity consistency using the formula:
  $$\text{Outcome Stability Score} = \frac{100}{1 + \text{Coefficient of Variation}}$$
- **Automated Publication-Ready Reporting:** Generates downloadable Executive PDF briefing documents (via ReportLab) and formatted multi-tab Excel workbooks (via OpenPyXL).
- **Dynamic Government-Level UI:** Streamlit multi-page interface styled with a navy blue, white, and slate enterprise theme, responsive KPI cards, and Plotly visualizations.

---

## 🏗️ Project Architecture

```
care-transition-analytics/
│
├── app.py                      # Main Application Portal & Hub
├── requirements.txt            # Project Dependencies
├── README.md                   # System Documentation & Runbook
├── .gitignore                  # Git Ignore Specifications
│
├── data/
│   └── HHS_Unaccompanied_Alien_Children_Program.csv  # 720 Valid Observations (2023-2025)
│
├── modules/
│   ├── __init__.py
│   ├── utils.py                # Theming, CSS Injection, Safe Math
│   ├── data_cleaning.py        # Sanitization, Formatting, Validation
│   ├── data_loader.py          # Session State & Dataset Management
│   ├── kpi_calculations.py    # Zero-Division Guarded KPI Formulations
│   ├── bottleneck_detection.py # Net Accumulation & Persistence Streaks
│   ├── trend_analysis.py       # Multi-Horizon Temporal Aggregations
│   ├── anomaly_detection.py    # Statistical Process Control & Z-Score Anomaly Engine
│   ├── recommendations.py     # Deterministic Rule Engine for Actionable Alerts
│   ├── visualizations.py       # Plotly Graph Objects & Express Visuals
│   ├── report_generator.py     # ReportLab PDF & OpenPyXL Excel Generator
│   └── analytics.py            # OLS Regressions, Correlation & Outlier Audits
│
├── pages/
│   ├── 1_Executive_Dashboard.py   # Overview Scorecard & Core Charts
│   ├── 2_Dataset_Explorer.py       # Upload, Audit, Filter & Export Data
│   ├── 3_Care_Pipeline.py          # Sankey Movement Diagram & Stage Balances
│   ├── 4_Transfer_Efficiency.py    # CBP-to-HHS Transit Ratios
│   ├── 5_Discharge_Analysis.py     # Shelter Exit Velocity & Placement Proxies
│   ├── 6_Bottleneck_Detection.py   # Net Flow Imbalances & Persistence Logs
│   ├── 7_Temporal_Analysis.py      # Daily, Weekly, Monthly, & Weekend Cadence
│   ├── 8_Outcome_Stability.py      # Coefficient of Variation & Anomaly Charts
│   ├── 9_Alerts_Recommendations.py # Prioritized Policy Decision-Support
│   ├── 10_Research_Insights.py     # Econometrics, OLS Regressions & Heatmaps
│   ├── 11_Reports_Downloads.py     # PDF Briefings & Excel/CSV Downloads
│   └── 12_About_Project.py         # Institutional Background & Data Dictionary
│
└── tests/
    ├── __init__.py
    ├── test_data_cleaning.py       # Preserves All 720 Rows, Cleans Commas & Asterisks
    ├── test_kpi_calculations.py    # Zero-Division Guarding & Math Verification
    ├── test_bottlenecks.py         # Imbalance Streaks & Severity Classification
    └── test_reports.py             # Binary PDF & Excel Generation Verification
```

---

## 💻 Windows Execution & Setup Guide

### 1. Prerequisites
- Python 3.11+ installed.
- PowerShell or Command Prompt.

### 2. Navigate to Project Directory
```powershell
cd C:\Users\User\.gemini\antigravity\scratch\care-transition-analytics
```

### 3. Create & Activate Virtual Environment
```powershell
python -m venv venv
venv\Scripts\activate
```

### 4. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 5. Launch Application
```powershell
streamlit run app.py
```
The application will open automatically in your browser at `http://localhost:8501`.

---

## 🧪 Automated Testing & Code Compilation

Run the full automated unit test suite:
```powershell
python -m pytest -q
```

Verify that all Python modules compile without syntax errors:
```powershell
python -m compileall -q .
```

---

## 📖 Standardized Data Dictionary

| Column Name | Type | Description | Role |
| :--- | :--- | :--- | :--- |
| **Date** | Date | Official reporting date of published government operational statistics. | Temporal Anchor |
| **Children Apprehended\*** | Integer | Gross daily intake of unaccompanied minors placed in CBP custody. | Movement Inflow |
| **Children in CBP Custody** | Integer | Headcount snapshot of children in CBP holding at time of reporting. | Custody Stock |
| **Transferred out of CBP** | Integer | Daily volume of children legally transferred from CBP to HHS ORR care. | Movement Outflow |
| **Children in HHS Care** | Integer | Headcount snapshot of children residing in HHS shelters or foster homes. | Custody Stock |
| **Discharged from HHS Care**| Integer | Daily volume of children released to vetted family or community sponsors.| Movement Outflow |

---

## 📐 Analytical Methodology & KPI Definitions

1. **Transfer Efficiency Ratio (%):**
   $$\text{Transfer Efficiency} = \left(\frac{\text{Daily Transfers}}{\text{Children in CBP Custody}}\right) \times 100$$
2. **Discharge Effectiveness Index (%):**
   $$\text{Discharge Effectiveness} = \left(\frac{\text{Daily Discharges}}{\text{Children in HHS Care}}\right) \times 100$$
3. **Pipeline Throughput Ratio (%):**
   $$\text{Pipeline Throughput} = \left(\frac{\text{Total Discharges}}{\text{Total Apprehensions}}\right) \times 100$$
4. **CBP Net Accumulation:**
   $$\text{CBP Net Accumulation} = \text{Daily Apprehensions} - \text{Daily Transfers}$$
5. **HHS Net Accumulation:**
   $$\text{HHS Net Accumulation} = \text{Daily Transfers} - \text{Daily Discharges}$$
6. **Overall Net Pipeline Backlog:**
   $$\text{Overall Backlog} = \text{Daily Apprehensions} - \text{Daily Discharges}$$
7. **Outcome Stability Score:**
   $$\text{Outcome Stability Score} = \frac{100}{1 + \text{Coefficient of Variation}}$$
   *(Where Coefficient of Variation $CV = \frac{\sigma}{\mu}$).*

---

## ⚖️ Analytical Assumptions & Governance Limitations

- **Stock vs. Flow Segregation:** Daily custody figures are static snapshots and are never summed across days to represent unique children.
- **System-Level Proxies:** Public datasets report aggregate movements; ratios describe system turnover rates, not individual tracking probabilities.
- **Discharge Placement Proxy:** HHS discharge numbers serve as a quantitative placement proxy. Individual post-release outcomes cannot be verified without case-level longitudinal datasets.
- **Irregular Reporting Distribution:** Unobserved weekend or holiday dates are treated as non-reporting intervals, never as zero-activity days.
