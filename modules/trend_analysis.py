import pandas as pd
import numpy as np
from .utils import safe_divide
from .kpi_calculations import add_daily_metrics

def analyze_temporal_trends(df: pd.DataFrame) -> dict:
    """
    Performs multi-frequency temporal aggregation and periodicity analysis:
    - Daily, Weekly, Monthly, Quarterly, Yearly summaries.
    - Weekday vs Weekend performance differences.
    - Month-over-Month changes.
    - Rolling metrics.
    Note: Calculations aggregate observed reporting days only and never treat
    unobserved calendar dates as zero.
    """
    if df is None or df.empty:
        return {
            "monthly": pd.DataFrame(),
            "quarterly": pd.DataFrame(),
            "yearly": pd.DataFrame(),
            "weekday_vs_weekend": pd.DataFrame(),
            "day_of_week_breakdown": pd.DataFrame(),
            "mom_changes": pd.DataFrame()
        }
        
    df_calc = add_daily_metrics(df)
    
    # 1. Monthly Aggregation
    monthly = df_calc.groupby("year_month").agg(
        obs_count=("date", "count"),
        total_apprehensions=("apprehensions", "sum"),
        total_transfers=("transfers", "sum"),
        total_discharges=("discharges", "sum"),
        avg_cbp_custody=("cbp_custody", "mean"),
        avg_hhs_care=("hhs_care", "mean"),
        cbp_net_accumulation=("cbp_net_accumulation", "sum"),
        hhs_net_accumulation=("hhs_net_accumulation", "sum"),
        overall_net_accumulation=("overall_net_accumulation", "sum"),
        mean_transfer_efficiency=("transfer_efficiency_ratio", "mean"),
        mean_discharge_effectiveness=("discharge_effectiveness_index", "mean")
    ).reset_index()
    
    # Ratios on aggregated monthly totals
    monthly["monthly_transfer_efficiency"] = monthly.apply(
        lambda r: safe_divide(r["total_transfers"], r["avg_cbp_custody"] * r["obs_count"]) * 100, axis=1
    )
    monthly["monthly_discharge_effectiveness"] = monthly.apply(
        lambda r: safe_divide(r["total_discharges"], r["avg_hhs_care"] * r["obs_count"]) * 100, axis=1
    )
    monthly["monthly_pipeline_throughput"] = monthly.apply(
        lambda r: safe_divide(r["total_discharges"], r["total_apprehensions"]) * 100, axis=1
    )
    
    # Month-over-Month (MoM) Growth Rates
    monthly["apprehensions_mom_pct"] = monthly["total_apprehensions"].pct_change() * 100
    monthly["transfers_mom_pct"] = monthly["total_transfers"].pct_change() * 100
    monthly["discharges_mom_pct"] = monthly["total_discharges"].pct_change() * 100
    
    # 2. Quarterly Aggregation
    quarterly = df_calc.groupby("quarter").agg(
        obs_count=("date", "count"),
        total_apprehensions=("apprehensions", "sum"),
        total_transfers=("transfers", "sum"),
        total_discharges=("discharges", "sum"),
        avg_cbp_custody=("cbp_custody", "mean"),
        avg_hhs_care=("hhs_care", "mean"),
        cbp_net_accumulation=("cbp_net_accumulation", "sum"),
        hhs_net_accumulation=("hhs_net_accumulation", "sum"),
        overall_net_accumulation=("overall_net_accumulation", "sum")
    ).reset_index()
    
    quarterly["pipeline_throughput"] = quarterly.apply(
        lambda r: safe_divide(r["total_discharges"], r["total_apprehensions"]) * 100, axis=1
    )
    
    # 3. Yearly Aggregation
    yearly = df_calc.groupby("year").agg(
        obs_count=("date", "count"),
        total_apprehensions=("apprehensions", "sum"),
        total_transfers=("transfers", "sum"),
        total_discharges=("discharges", "sum"),
        avg_cbp_custody=("cbp_custody", "mean"),
        avg_hhs_care=("hhs_care", "mean"),
        cbp_net_accumulation=("cbp_net_accumulation", "sum"),
        hhs_net_accumulation=("hhs_net_accumulation", "sum"),
        overall_net_accumulation=("overall_net_accumulation", "sum")
    ).reset_index()
    
    yearly["pipeline_throughput"] = yearly.apply(
        lambda r: safe_divide(r["total_discharges"], r["total_apprehensions"]) * 100, axis=1
    )
    
    # 4. Weekday vs Weekend Comparison
    df_calc["day_type"] = df_calc["is_weekend"].apply(lambda x: "Weekend (Sat-Sun)" if x else "Weekday (Mon-Fri)")
    weekday_vs_weekend = df_calc.groupby("day_type").agg(
        obs_count=("date", "count"),
        avg_apprehensions=("apprehensions", "mean"),
        avg_transfers=("transfers", "mean"),
        avg_discharges=("discharges", "mean"),
        avg_cbp_custody=("cbp_custody", "mean"),
        avg_hhs_care=("hhs_care", "mean"),
        avg_transfer_efficiency=("transfer_efficiency_ratio", "mean"),
        avg_discharge_effectiveness=("discharge_effectiveness_index", "mean"),
        avg_overall_net=("overall_net_accumulation", "mean")
    ).reset_index()
    
    # 5. Day of Week Breakdown
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_breakdown = df_calc.groupby("day_name").agg(
        obs_count=("date", "count"),
        avg_apprehensions=("apprehensions", "mean"),
        avg_transfers=("transfers", "mean"),
        avg_discharges=("discharges", "mean"),
        avg_cbp_custody=("cbp_custody", "mean"),
        avg_hhs_care=("hhs_care", "mean"),
        avg_transfer_efficiency=("transfer_efficiency_ratio", "mean"),
        avg_discharge_effectiveness=("discharge_effectiveness_index", "mean")
    ).reindex(day_order).dropna(how='all').reset_index()

    return {
        "monthly": monthly,
        "quarterly": quarterly,
        "yearly": yearly,
        "weekday_vs_weekend": weekday_vs_weekend,
        "day_of_week_breakdown": day_breakdown,
        "daily_with_metrics": df_calc
    }
