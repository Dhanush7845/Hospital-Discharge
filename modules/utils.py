import os
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Color Palette: Navy Blue, Slate, White, Light Grey, Accents
COLORS = {
    "primary": "#1B365D",       # Deep Navy
    "secondary": "#0077B6",     # Ocean Blue
    "accent": "#00B4D8",        # Bright Blue
    "dark_bg": "#0B2545",       # Midnight Navy
    "card_bg": "#FFFFFF",       # Card White
    "page_bg": "#F4F6F9",       # Light Grey
    "border": "#E2E8F0",        # Light Border
    "text_dark": "#1E293B",     # Slate Dark
    "text_muted": "#64748B",    # Slate Muted
    "success": "#2A9D8F",       # Teal Green
    "warning": "#E76F51",       # Muted Coral/Orange
    "danger": "#E63946",        # Crimson Red
    "info": "#457B9D"           # Slate Blue
}

def inject_custom_css():
    """Injects high-quality government/enterprise CSS theme into Streamlit."""
    css = f"""
    <style>
    /* Global Styles */
    .stApp {{
        background-color: #F8FAFC;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #1E293B;
    }}
    
    /* Top Header Bar */
    .top-header-banner {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['dark_bg']} 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(11, 37, 69, 0.12);
        border-left: 6px solid {COLORS['accent']};
    }}
    .top-header-banner h1 {{
        color: #FFFFFF !important;
        font-size: 1.75rem;
        font-weight: 700;
        margin: 0;
        padding: 0;
        letter-spacing: -0.02em;
    }}
    .top-header-banner p {{
        color: #CBD5E1;
        font-size: 0.95rem;
        margin-top: 0.4rem;
        margin-bottom: 0;
    }}
    
    /* Metric / KPI Cards */
    .kpi-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 0.9rem;
        margin-bottom: 1.5rem;
    }}
    .kpi-card {{
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 1rem 1.15rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}
    .kpi-card:hover {{
        box-shadow: 0 4px 12px rgba(27, 54, 93, 0.08);
        border-color: #CBD5E1;
    }}
    .kpi-label {{
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        color: #64748B;
        letter-spacing: 0.04em;
        margin-bottom: 0.35rem;
    }}
    .kpi-value {{
        font-size: 1.55rem;
        font-weight: 700;
        color: {COLORS['primary']};
        line-height: 1.2;
    }}
    .kpi-subtext {{
        font-size: 0.75rem;
        color: #94A3B8;
        margin-top: 0.35rem;
    }}

    /* Card Panels */
    .content-card {{
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 1.25rem 1.4rem;
        border: 1px solid #E2E8F0;
        margin-bottom: 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}
    .content-card h3 {{
        color: {COLORS['primary']};
        font-size: 1.15rem;
        font-weight: 600;
        margin-top: 0;
        margin-bottom: 0.75rem;
        border-bottom: 1px solid #F1F5F9;
        padding-bottom: 0.5rem;
    }}

    /* Badges */
    .badge {{
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }}
    .badge-green {{
        background-color: #DCFCE7;
        color: #166534;
        border: 1px solid #BBF7D0;
    }}
    .badge-yellow {{
        background-color: #FEF9C3;
        color: #854D0E;
        border: 1px solid #FEF08A;
    }}
    .badge-red {{
        background-color: #FEE2E2;
        color: #991B1B;
        border: 1px solid #FECACA;
    }}
    .badge-blue {{
        background-color: #E0F2FE;
        color: #075985;
        border: 1px solid #BAE6FD;
    }}

    /* Analytical Note Callout */
    .analytical-callout {{
        background-color: #F8FAFC;
        border-left: 4px solid {COLORS['secondary']};
        padding: 0.9rem 1.2rem;
        border-radius: 0 6px 6px 0;
        margin: 1rem 0;
        font-size: 0.88rem;
        color: #334155;
        border-top: 1px solid #E2E8F0;
        border-right: 1px solid #E2E8F0;
        border-bottom: 1px solid #E2E8F0;
    }}
    .analytical-callout strong {{
        color: {COLORS['primary']};
    }}

    /* Streamlit Sidebar Customization */
    section[data-testid="stSidebar"] {{
        background-color: #0F172A;
    }}
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {{
        color: #E2E8F0 !important;
    }}
    section[data-testid="stSidebar"] hr {{
        border-color: #334155 !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def render_header(title: str, subtitle: str = ""):
    """Renders standard executive header banner using st.html."""
    sub = f'<p>{subtitle}</p>' if subtitle else ''
    st.html(f'<div class="top-header-banner"><h1>{title}</h1>{sub}</div>')

def render_kpi_card(label: str, value: str, subtext: str = "", delta_color: str = ""):
    """Generates clean HTML string for a KPI card with zero leading indentation."""
    sub = f'<div class="kpi-subtext">{subtext}</div>' if subtext else ''
    return f'<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div>{sub}</div>'

def render_kpi_grid(cards_html: str):
    """Renders a grid container for KPI cards without markdown indentation issues."""
    st.html(f'<div class="kpi-grid">{cards_html}</div>')

def render_callout(text: str, title: str = "Analytical Clarification & Methodology"):
    """Displays standard analytical disclaimer/clarification box using st.html."""
    st.html(f'<div class="analytical-callout"><strong>{title}:</strong> {text}</div>')

def safe_divide(numerator, denominator, default=0.0):
    """Safely performs division guarding against zero or NaN."""
    try:
        if denominator is None or pd.isna(denominator) or denominator == 0:
            return default
        if numerator is None or pd.isna(numerator):
            return default
        res = float(numerator) / float(denominator)
        if np.isnan(res) or np.isinf(res):
            return default
        return res
    except (ZeroDivisionError, ValueError, TypeError):
        return default

def format_number(val, decimals=0):
    """Formats numeric values with comma separators."""
    if val is None or pd.isna(val):
        return "N/A"
    try:
        if decimals == 0:
            return f"{int(round(float(val))):,}"
        return f"{float(val):,.{decimals}f}"
    except (ValueError, TypeError):
        return str(val)

def format_percent(val, decimals=1):
    """Formats ratio as percentage."""
    if val is None or pd.isna(val):
        return "N/A"
    try:
        return f"{float(val):.{decimals}f}%"
    except (ValueError, TypeError):
        return str(val)

def render_sidebar_controls(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renders common sidebar metadata, global date filter, and dataset reset button.
    Returns filtered dataframe.
    """
    st.sidebar.markdown("### 🏛️ Program Analytics")
    source_name = st.session_state.get("dataset_source", "HHS UAC Program Archive")
    st.sidebar.caption(f"**Active Source:** {source_name}")
    st.sidebar.caption(f"**Total Records:** {len(df):,} valid observations")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("#### 📅 Temporal Scope Filter")
    
    if df.empty or "date" not in df.columns:
        return df
        
    min_date = df["date"].min().date()
    max_date = df["date"].max().date()
    
    # Store or retrieve selected date range
    default_range = [min_date, max_date]
    selected_range = st.sidebar.date_input(
        "Select Date Range",
        value=default_range,
        min_value=min_date,
        max_value=max_date,
        key="global_date_filter"
    )
    
    if isinstance(selected_range, (list, tuple)) and len(selected_range) == 2:
        start_d, end_d = selected_range
        filtered_df = df[(df["date"].dt.date >= start_d) & (df["date"].dt.date <= end_d)].copy()
    else:
        filtered_df = df.copy()
        
    st.sidebar.caption(f"**Filtered Records:** {len(filtered_df):,} days")
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Reset to Default Dataset", width="stretch"):
        from .data_loader import reset_to_default
        reset_to_default(st.session_state)
        st.sidebar.success("Reset to default dataset (720 records).")
        st.rerun()
        
    return filtered_df
