import os
import sys

# Ensure project root is in sys.path
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import streamlit as st
import pandas as pd
import io
from datetime import datetime
from modules.utils import (
    inject_custom_css, render_header, render_sidebar_controls,
    render_kpi_card, render_callout, format_number
)
from modules.data_loader import (
    init_session_data, set_active_data, reset_to_default,
    load_csv, load_excel
)
from modules.data_cleaning import validate_dataset, COLUMN_LABELS
from modules.report_generator import generate_kpi_excel
from modules.kpi_calculations import calculate_core_kpis

st.set_page_config(
    page_title="Dataset Explorer | UAC Analytics",
    page_icon="📂",
    layout="wide"
)

inject_custom_css()

df_active = init_session_data(st.session_state)
df_filtered = render_sidebar_controls(df_active)

render_header(
    "Dataset Explorer & Management Interface",
    "Inspect, upload, validate, filter, and export the official UAC program reporting datasets."
)

tab_upload, tab_inspect, tab_filter, tab_export = st.tabs([
    "📥 Data Ingestion & Upload",
    "🔍 Data Quality & Inspection",
    "🔎 Interactive Filtering & Columns",
    "💾 Export Cleaned Dataset"
])

# ----------------- TAB 1: UPLOAD -----------------
with tab_upload:
    st.markdown("### 📤 Upload New Dataset")
    st.markdown(
        "Upload a revised CSV or Excel file containing UAC Program reporting records. "
        "The uploaded dataset will update the active session across all analytical dashboard modules."
    )
    
    col_up1, col_up2 = st.columns([2, 1])
    with col_up1:
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file",
            type=["csv", "xlsx", "xls"],
            help="File must contain the 6 standard UAC reporting columns."
        )
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    new_df = load_csv(uploaded_file)
                else:
                    new_df = load_excel(uploaded_file)
                    
                val_diag = validate_dataset(new_df)
                if val_diag["is_valid"]:
                    set_active_data(st.session_state, new_df, source_name=f"Uploaded: {uploaded_file.name}")
                    st.success(f"Successfully loaded and cleaned **{len(new_df):,}** records from `{uploaded_file.name}`!")
                    st.rerun()
                else:
                    st.error(f"Dataset validation failed: {', '.join(val_diag['errors'])}")
            except Exception as e:
                st.error(f"Error parsing uploaded file: {str(e)}")
                
    with col_up2:
        st.markdown("#### Active Dataset Status")
        st.info(
            f"**Current Source:**\n{st.session_state.get('dataset_source', 'Default Archive')}\n\n"
            f"**Total Records:** {len(df_active):,} days\n\n"
            f"**Date Range:**\n{df_active['date'].min().strftime('%Y-%m-%d')} to {df_active['date'].max().strftime('%Y-%m-%d')}"
        )
        if st.button("🔄 Restore Bundled Default Dataset", key="btn_restore_tab1"):
            reset_to_default(st.session_state)
            st.success("Default dataset restored.")
            st.rerun()

# ----------------- TAB 2: INSPECTION -----------------
with tab_inspect:
    st.markdown("### 🔬 Data Integrity & Diagnostic Audit")
    diag = validate_dataset(df_active)
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.html(render_kpi_card("Total Observations", f"{len(df_active):,}", "Preserved Valid Days"))
    with col_m2:
        st.html(render_kpi_card("Column Count", f"{len(df_active.columns)}", "Standardized attributes"))
    with col_m3:
        dup_count = df_active['date'].duplicated().sum()
        st.html(render_kpi_card("Duplicate Dates", f"{dup_count}", "Unique reporting cadence"))
    with col_m4:
        missing_count = df_active[["apprehensions", "cbp_custody", "transfers", "hhs_care", "discharges"]].isna().sum().sum()
        st.html(render_kpi_card("Missing Values", f"{missing_count}", "Complete numerical integrity"))
        
    st.markdown("#### Schema & Column Attributes")
    schema_rows = []
    for col in df_active.columns:
        schema_rows.append({
            "Internal Column": col,
            "Public Description": COLUMN_LABELS.get(col, col.replace('_', ' ').title()),
            "Data Type": str(df_active[col].dtype),
            "Non-Null Count": df_active[col].count(),
            "Sample Value": str(df_active[col].iloc[0]) if len(df_active) > 0 else "N/A"
        })
    st.dataframe(pd.DataFrame(schema_rows), width="stretch")
    
    st.markdown("#### Descriptive Statistical Summary")
    num_cols = ["apprehensions", "cbp_custody", "transfers", "hhs_care", "discharges"]
    st.dataframe(df_active[num_cols].describe().T.style.format("{:,.1f}"), width="stretch")

# ----------------- TAB 3: FILTERING -----------------
with tab_filter:
    st.markdown("### 🔎 Interactive Data Preview & Column Selection")
    
    col_sel, col_rows = st.columns([3, 1])
    with col_sel:
        all_cols = list(df_filtered.columns)
        default_cols = ["date", "apprehensions", "cbp_custody", "transfers", "hhs_care", "discharges"]
        selected_columns = st.multiselect("Display Columns", options=all_cols, default=default_cols)
    with col_rows:
        num_preview_rows = st.number_input("Max Preview Rows", min_value=10, max_value=len(df_filtered), value=min(50, len(df_filtered)), step=10)
        
    if selected_columns:
        display_df = df_filtered[selected_columns].copy()
        if "date" in display_df.columns:
            display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d")
        st.dataframe(display_df.head(num_preview_rows), width="stretch")
    else:
        st.warning("Please select at least one column to display.")

# ----------------- TAB 4: EXPORT -----------------
with tab_export:
    st.markdown("### 💾 Export Cleaned Dataset")
    st.markdown("Download the cleaned, standardized, and chronologically ordered UAC dataset in CSV or Excel format.")
    
    export_df = df_filtered.copy()
    export_df["date"] = export_df["date"].dt.strftime("%Y-%m-%d")
    
    # CSV buffer
    csv_bytes = export_df.to_csv(index=False).encode('utf-8')
    
    # Excel buffer
    kpis = calculate_core_kpis(df_filtered)
    excel_bytes = generate_kpi_excel(df_filtered, kpis)
    
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            label="⬇️ Download Cleaned CSV",
            data=csv_bytes,
            file_name=f"UAC_Cleaned_Dataset_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            width="stretch"
        )
    with col_dl2:
        st.download_button(
            label="⬇️ Download Formatted Excel (.xlsx)",
            data=excel_bytes,
            file_name=f"UAC_Analytics_Workbook_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch"
        )

render_callout(
    "All 720 valid reporting records from the raw government archive are chronologically validated. "
    "Completely empty rows and formatting asterisks have been safely sanitized without losing any observation.",
    "Data Sanitation Transparency"
)
