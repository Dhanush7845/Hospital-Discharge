import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# Professional Executive Theme Constants
COLOR_NAVY = "#1B365D"
COLOR_OCEAN = "#0077B6"
COLOR_CYAN = "#00B4D8"
COLOR_SLATE = "#64748B"
COLOR_GREEN = "#2A9D8F"
COLOR_AMBER = "#F4A261"
COLOR_RED = "#E63946"
COLOR_LIGHT_BG = "#F8FAFC"
COLOR_BORDER = "#E2E8F0"

def get_base_layout(title: str = "", height: int = 420) -> dict:
    """Returns standardized Plotly layout dictionary."""
    return dict(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=14, color=COLOR_NAVY, family="Inter, sans-serif"),
            x=0.01,
            y=0.96
        ),
        margin=dict(l=40, r=40, t=55, b=40),
        height=height,
        paper_bgcolor="white",
        plot_bgcolor="#FAFCFE",
        font=dict(family="Inter, sans-serif", color="#334155", size=12),
        xaxis=dict(
            showgrid=True,
            gridcolor=COLOR_BORDER,
            linecolor=COLOR_BORDER,
            tickfont=dict(size=11, color=COLOR_SLATE)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=COLOR_BORDER,
            linecolor=COLOR_BORDER,
            tickfont=dict(size=11, color=COLOR_SLATE)
        ),
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11)
        )
    )

def plot_cbp_custody_trend(df: pd.DataFrame) -> go.Figure:
    """Plots CBP Custody Stock over time."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["cbp_custody"],
        mode="lines",
        name="Children in CBP Custody (Stock)",
        line=dict(color=COLOR_OCEAN, width=2.5),
        fill="tozeroy",
        fillcolor="rgba(0, 119, 182, 0.08)"
    ))
    fig.update_layout(get_base_layout("1. CBP Custody Population Trend (Daily Stock Snapshot)"))
    fig.update_yaxes(title_text="Children in Custody")
    return fig

def plot_hhs_care_trend(df: pd.DataFrame) -> go.Figure:
    """Plots HHS Care Stock over time."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["hhs_care"],
        mode="lines",
        name="Children in HHS Care (Active Census Stock)",
        line=dict(color=COLOR_NAVY, width=2.5),
        fill="tozeroy",
        fillcolor="rgba(27, 54, 93, 0.08)"
    ))
    fig.update_layout(get_base_layout("2. HHS Shelter Census Trend (Daily Stock Snapshot)"))
    fig.update_yaxes(title_text="Active Census in HHS Care")
    return fig

def plot_intake_vs_transfers(df: pd.DataFrame) -> go.Figure:
    """Plots Daily Apprehensions vs Daily Transfers out of CBP."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["apprehensions"],
        mode="lines",
        name="Apprehensions (Intake Flow)",
        line=dict(color=COLOR_AMBER, width=2)
    ))
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["transfers"],
        mode="lines",
        name="Transfers out of CBP (Outflow)",
        line=dict(color=COLOR_OCEAN, width=2)
    ))
    fig.update_layout(get_base_layout("3. Daily Apprehensions vs. Transfers (Intake vs. Outflow)"))
    fig.update_yaxes(title_text="Daily Children")
    return fig

def plot_transfers_vs_discharges(df: pd.DataFrame) -> go.Figure:
    """Plots HHS Transfers In vs Discharges Out."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["transfers"],
        mode="lines",
        name="Transfers into HHS (Inflow)",
        line=dict(color=COLOR_OCEAN, width=2)
    ))
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["discharges"],
        mode="lines",
        name="Discharges from HHS (Outflow / Placement)",
        line=dict(color=COLOR_GREEN, width=2)
    ))
    fig.update_layout(get_base_layout("4. HHS Transfers In vs. Discharges Out (Inflow vs. Placement)"))
    fig.update_yaxes(title_text="Daily Children")
    return fig

def plot_monthly_discharge_trends(df: pd.DataFrame) -> go.Figure:
    """Plots Monthly Discharge Trends."""
    monthly_df = df.copy()
    if "year_month" not in monthly_df.columns and "date" in monthly_df.columns:
        monthly_df["year_month"] = monthly_df["date"].dt.to_period("M").astype(str)
        
    m_agg = monthly_df.groupby("year_month").agg(
        total_discharges=("discharges", "sum"),
        total_apprehensions=("apprehensions", "sum")
    ).reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=m_agg["year_month"],
        y=m_agg["total_discharges"],
        name="Monthly Discharges",
        marker_color=COLOR_NAVY
    ))
    fig.add_trace(go.Scatter(
        x=m_agg["year_month"],
        y=m_agg["total_apprehensions"],
        mode="lines+markers",
        name="Monthly Intake (Apprehensions)",
        line=dict(color=COLOR_AMBER, width=2)
    ))
    fig.update_layout(get_base_layout("5. Monthly Discharge Trends vs. Monthly Intake Volume"))
    fig.update_yaxes(title_text="Children / Month")
    return fig

def plot_overall_pipeline_performance(df: pd.DataFrame) -> go.Figure:
    """
    Plots Overall Pipeline Performance comparing Cumulative Apprehensions (Intake),
    Transfers, and Discharges (Placements) across time.
    """
    df_calc = df.sort_values("date").copy()
    df_calc["cum_apprehensions"] = df_calc["apprehensions"].cumsum()
    df_calc["cum_transfers"] = df_calc["transfers"].cumsum()
    df_calc["cum_discharges"] = df_calc["discharges"].cumsum()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_calc["date"],
        y=df_calc["cum_apprehensions"],
        mode="lines",
        name="Cumulative Apprehensions (Intake)",
        line=dict(color=COLOR_AMBER, width=2.5)
    ))
    fig.add_trace(go.Scatter(
        x=df_calc["date"],
        y=df_calc["cum_transfers"],
        mode="lines",
        name="Cumulative Transfers out of CBP",
        line=dict(color=COLOR_OCEAN, width=2.5)
    ))
    fig.add_trace(go.Scatter(
        x=df_calc["date"],
        y=df_calc["cum_discharges"],
        mode="lines",
        name="Cumulative Discharges (Community Placements)",
        line=dict(color=COLOR_GREEN, width=3)
    ))
    fig.update_layout(get_base_layout("6. Overall Pipeline Performance (Cumulative Inflow vs. Placement Trajectory)"))
    fig.update_yaxes(title_text="Cumulative Children")
    return fig

def plot_net_accumulation(df: pd.DataFrame, col_name: str, title: str) -> go.Figure:
    """Plots Net Accumulation with color coding for positive (accumulation) vs negative (clearance)."""
    fig = go.Figure()
    colors = [COLOR_RED if v > 0 else COLOR_GREEN for v in df[col_name]]
    fig.add_trace(go.Bar(
        x=df["date"],
        y=df[col_name],
        marker_color=colors,
        name="Net Daily Balance"
    ))
    # Add zero baseline
    fig.add_hline(y=0, line_dash="dash", line_color=COLOR_SLATE, line_width=1)
    
    # Add rolling 7-day average if exists
    rolling_col = f"rolling_7_{col_name}" if f"rolling_7_{col_name}" in df.columns else None
    if rolling_col:
        fig.add_trace(go.Scatter(
            x=df["date"],
            y=df[rolling_col],
            mode="lines",
            name="7-Observation Rolling Avg",
            line=dict(color=COLOR_NAVY, width=2)
        ))
        
    fig.update_layout(get_base_layout(title))
    fig.update_yaxes(title_text="Net Flow (Children/Day)")
    return fig

def plot_efficiency_ratio_trend(
    df: pd.DataFrame,
    ratio_col: str,
    title: str,
    threshold: float = 25.0,
    y_label: str = "Ratio (%)"
) -> go.Figure:
    """Plots efficiency or effectiveness ratio with configurable threshold."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df[ratio_col],
        mode="lines",
        name=title,
        line=dict(color=COLOR_OCEAN, width=1.5),
        opacity=0.75
    ))
    
    # Rolling average overlay
    rolling_col = None
    for c in df.columns:
        if "rolling_7" in c and ratio_col[:8] in c:
            rolling_col = c
            break
            
    if rolling_col in df.columns:
        fig.add_trace(go.Scatter(
            x=df["date"],
            y=df[rolling_col],
            mode="lines",
            name="7-Observation Rolling Avg",
            line=dict(color=COLOR_NAVY, width=2.5)
        ))
        
    fig.add_hline(
        y=threshold,
        line_dash="dot",
        line_color=COLOR_RED,
        annotation_text=f"Benchmark ({threshold}%)",
        annotation_position="bottom right"
    )
    fig.update_layout(get_base_layout(title))
    fig.update_yaxes(title_text=y_label)
    return fig

def plot_pipeline_sankey(df: pd.DataFrame) -> go.Figure:
    """
    Renders an interactive, mass-balanced Sankey diagram.
    Correctly accounts for transitions and the drawdown of pre-existing custody stock
    to guarantee that all active nodes are fully connected without floating boxes.
    """
    total_app = int(df["apprehensions"].sum())
    total_transfers = int(df["transfers"].sum())
    total_discharges = int(df["discharges"].sum())
    
    cbp_diff = total_app - total_transfers
    hhs_diff = total_transfers - total_discharges
    
    nodes = []
    node_colors = []
    node_map = {}
    
    def get_node_id(label, color):
        if label not in node_map:
            node_map[label] = len(nodes)
            nodes.append(label)
            node_colors.append(color)
        return node_map[label]
        
    sources = []
    targets = []
    values = []
    link_colors = []
    
    # Node 1 & 2: Apprehensions -> CBP Custody
    id_app = get_node_id("1. Border Apprehensions (Intake)", COLOR_AMBER)
    id_cbp = get_node_id("2. CBP Custody Processing", COLOR_OCEAN)
    sources.append(id_app); targets.append(id_cbp); values.append(total_app)
    link_colors.append("rgba(244, 162, 97, 0.45)")
    
    # If transfers outpaced new apprehensions, the difference came from prior CBP stock
    if cbp_diff < 0:
        id_prior_cbp = get_node_id("Prior CBP Custody Drawdown", COLOR_SLATE)
        sources.append(id_prior_cbp); targets.append(id_cbp); values.append(abs(cbp_diff))
        link_colors.append("rgba(100, 116, 139, 0.35)")
        
    # Node 2 -> 3: CBP Custody -> HHS Care (Transfers)
    id_hhs = get_node_id("3. Transferred into HHS Care", COLOR_NAVY)
    sources.append(id_cbp); targets.append(id_hhs); values.append(total_transfers)
    link_colors.append("rgba(0, 119, 182, 0.45)")
    
    # If apprehensions outpaced transfers, the excess remained retained in CBP
    if cbp_diff > 0:
        id_cbp_ret = get_node_id("Retained in CBP Custody", COLOR_RED)
        sources.append(id_cbp); targets.append(id_cbp_ret); values.append(cbp_diff)
        link_colors.append("rgba(230, 57, 70, 0.45)")
        
    # If discharges outpaced transfers, the difference came from prior HHS shelter census
    if hhs_diff < 0:
        id_prior_hhs = get_node_id("Prior HHS Shelter Census Drawdown", COLOR_SLATE)
        sources.append(id_prior_hhs); targets.append(id_hhs); values.append(abs(hhs_diff))
        link_colors.append("rgba(100, 116, 139, 0.35)")
        
    # Node 3 -> 4: HHS Care -> Community Discharges
    id_dis = get_node_id("4. Community Discharges (Placement)", COLOR_GREEN)
    sources.append(id_hhs); targets.append(id_dis); values.append(total_discharges)
    link_colors.append("rgba(42, 157, 143, 0.45)")
    
    # If transfers outpaced discharges, the excess remained retained in HHS Care
    if hhs_diff > 0:
        id_hhs_ret = get_node_id("Retained in HHS Care Census", COLOR_RED)
        sources.append(id_hhs); targets.append(id_hhs_ret); values.append(hhs_diff)
        link_colors.append("rgba(230, 57, 70, 0.45)")
        
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=22,
            line=dict(color="#0B2545", width=0.5),
            label=nodes,
            color=node_colors
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors
        )
    )])
    
    fig.update_layout(get_base_layout("Macro-Level Pipeline Movement Flow (Mass-Balanced Sankey)", height=460))
    return fig

def plot_correlation_heatmap(corr_df: pd.DataFrame) -> go.Figure:
    """Plots Correlation Matrix Heatmap."""
    fig = px.imshow(
        corr_df,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1
    )
    fig.update_layout(get_base_layout("Cross-Metric Pearson Correlation Matrix", height=450))
    return fig

def plot_weekday_vs_weekend_bar(comp_df: pd.DataFrame) -> go.Figure:
    """Plots comparative metrics for Weekdays vs Weekends."""
    metrics = ["avg_apprehensions", "avg_transfers", "avg_discharges"]
    labels = ["Intake (Apprehensions)", "Transfers out of CBP", "HHS Discharges"]
    
    fig = go.Figure()
    for m, label in zip(metrics, labels):
        if m in comp_df.columns:
            fig.add_trace(go.Bar(
                x=comp_df["day_type"],
                y=comp_df[m],
                name=label
            ))
            
    fig.update_layout(get_base_layout("Operational Cadence: Weekdays vs. Weekends (Daily Averages)"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Average Children / Day")
    return fig

def plot_outcome_stability_anomalies(df_stability: pd.DataFrame) -> go.Figure:
    """Plots discharge velocity, rolling average, and detected statistical anomalies."""
    fig = go.Figure()
    
    # Daily Discharges
    fig.add_trace(go.Scatter(
        x=df_stability["date"],
        y=df_stability["discharges"],
        mode="lines",
        name="Daily Discharges",
        line=dict(color=COLOR_SLATE, width=1),
        opacity=0.6
    ))
    
    # Rolling Mean
    if "rolling_mean" in df_stability.columns:
        fig.add_trace(go.Scatter(
            x=df_stability["date"],
            y=df_stability["rolling_mean"],
            mode="lines",
            name="14-Obs Rolling Mean",
            line=dict(color=COLOR_NAVY, width=2.5)
        ))
        
    # Upper Bound
    if "upper_bound" in df_stability.columns:
        fig.add_trace(go.Scatter(
            x=df_stability["date"],
            y=df_stability["upper_bound"],
            mode="lines",
            name="+2.5σ Control Bound",
            line=dict(color=COLOR_AMBER, dash="dot", width=1.5)
        ))
        
    # Anomalies Scatter
    anomalies = df_stability[df_stability["is_anomaly"]] if "is_anomaly" in df_stability.columns else pd.DataFrame()
    if not anomalies.empty:
        fig.add_trace(go.Scatter(
            x=anomalies["date"],
            y=anomalies["discharges"],
            mode="markers",
            name="Statistical Anomaly (|Z| ≥ 2.5)",
            marker=dict(color=COLOR_RED, size=9, symbol="diamond")
        ))
        
    fig.update_layout(get_base_layout("Discharge Velocity Stability & Anomaly Control Chart"))
    fig.update_yaxes(title_text="Daily Discharges")
    return fig

def plot_regression_scatter(df: pd.DataFrame, x_col: str, y_col: str, reg_info: dict) -> go.Figure:
    """Plots scatter points with OLS linear trendline."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df[y_col],
        mode="markers",
        name="Observed Days",
        marker=dict(color=COLOR_OCEAN, size=6, opacity=0.7)
    ))
    
    # Trendline
    x_range = np.linspace(df[x_col].min(), df[x_col].max(), 100)
    y_pred = reg_info["slope"] * x_range + reg_info["intercept"]
    fig.add_trace(go.Scatter(
        x=x_range,
        y=y_pred,
        mode="lines",
        name=f"OLS Trend (R² = {reg_info['r_squared']:.3f})",
        line=dict(color=COLOR_RED, width=2.5)
    ))
    
    title = f"{x_col.replace('_', ' ').title()} vs. {y_col.replace('_', ' ').title()}"
    fig.update_layout(get_base_layout(title))
    fig.update_xaxes(title_text=x_col.replace('_', ' ').title())
    fig.update_yaxes(title_text=y_col.replace('_', ' ').title())
    return fig
