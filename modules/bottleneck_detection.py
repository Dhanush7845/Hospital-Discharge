import pandas as pd
import numpy as np
from .kpi_calculations import add_daily_metrics

def detect_bottlenecks(
    df: pd.DataFrame,
    cbp_threshold: float = 20.0,
    hhs_threshold: float = 30.0,
    overall_threshold: float = 25.0,
    min_consecutive_obs: int = 3
) -> dict:
    """
    Identifies systemic pipeline friction and accumulation bottlenecks.
    
    Parameters:
    - cbp_threshold: Daily net accumulation (Apprehensions - Transfers) considered elevated.
    - hhs_threshold: Daily net accumulation (Transfers - Discharges) considered elevated.
    - overall_threshold: Daily overall net accumulation (Apprehensions - Discharges).
    - min_consecutive_obs: Minimum consecutive reporting observations to flag sustained bottleneck.
    """
    if df is None or df.empty:
        return {
            "summary": {},
            "bottleneck_records": pd.DataFrame(),
            "sustained_events": [],
            "severity_counts": {"Green": 0, "Yellow": 0, "Red": 0}
        }
        
    df_calc = add_daily_metrics(df)
    
    # Classify each observation into severity
    def assign_severity(row):
        cbp_net = row["cbp_net_accumulation"]
        hhs_net = row["hhs_net_accumulation"]
        overall_net = row["overall_net_accumulation"]
        
        # Red: High concern if either CBP or HHS accumulation exceeds 1.5x threshold or overall net is very high
        if (cbp_net >= cbp_threshold * 1.5) or (hhs_net >= hhs_threshold * 1.5) or (overall_net >= overall_threshold * 1.5):
            return "Red"
        # Yellow: Moderate concern if any metric exceeds basic threshold or transfer efficiency is very low
        elif (cbp_net >= cbp_threshold) or (hhs_net >= hhs_threshold) or (overall_net >= overall_threshold):
            return "Yellow"
        else:
            return "Green"

    df_calc["severity"] = df_calc.apply(assign_severity, axis=1)
    
    # Identify Sustained Imbalances (Consecutive Observations where inflow > outflow)
    sustained_events = []
    
    for stage_name, col_name, thresh in [
        ("CBP Intake Friction", "cbp_net_accumulation", cbp_threshold),
        ("HHS Placement Lag", "hhs_net_accumulation", hhs_threshold),
        ("Total System Accumulation", "overall_net_accumulation", overall_threshold)
    ]:
        current_streak = []
        for idx, row in df_calc.iterrows():
            if row[col_name] > 0:
                current_streak.append(row)
            else:
                if len(current_streak) >= min_consecutive_obs:
                    start_row = current_streak[0]
                    end_row = current_streak[-1]
                    sustained_events.append({
                        "stage": stage_name,
                        "start_date": start_row["date"],
                        "end_date": end_row["date"],
                        "consecutive_obs": len(current_streak),
                        "total_net_accumulation": sum(r[col_name] for r in current_streak),
                        "avg_daily_accumulation": np.mean([r[col_name] for r in current_streak]),
                        "severity": "Red" if len(current_streak) >= min_consecutive_obs + 2 or any(r[col_name] >= thresh * 1.5 for r in current_streak) else "Yellow"
                    })
                current_streak = []
                
        # Check streak at end of dataset
        if len(current_streak) >= min_consecutive_obs:
            start_row = current_streak[0]
            end_row = current_streak[-1]
            sustained_events.append({
                "stage": stage_name,
                "start_date": start_row["date"],
                "end_date": end_row["date"],
                "consecutive_obs": len(current_streak),
                "total_net_accumulation": sum(r[col_name] for r in current_streak),
                "avg_daily_accumulation": np.mean([r[col_name] for r in current_streak]),
                "severity": "Red" if len(current_streak) >= min_consecutive_obs + 2 else "Yellow"
            })

    # Summary statistics
    severity_counts = df_calc["severity"].value_counts().to_dict()
    for col in ["Green", "Yellow", "Red"]:
        severity_counts.setdefault(col, 0)
        
    summary = {
        "max_cbp_net": df_calc["cbp_net_accumulation"].max(),
        "min_cbp_net": df_calc["cbp_net_accumulation"].min(),
        "avg_cbp_net": df_calc["cbp_net_accumulation"].mean(),
        "max_hhs_net": df_calc["hhs_net_accumulation"].max(),
        "min_hhs_net": df_calc["hhs_net_accumulation"].min(),
        "avg_hhs_net": df_calc["hhs_net_accumulation"].mean(),
        "max_overall_net": df_calc["overall_net_accumulation"].max(),
        "min_overall_net": df_calc["overall_net_accumulation"].min(),
        "avg_overall_net": df_calc["overall_net_accumulation"].mean(),
        "total_sustained_events": len(sustained_events),
        "red_alert_days": severity_counts["Red"],
        "yellow_alert_days": severity_counts["Yellow"],
        "green_alert_days": severity_counts["Green"]
    }
    
    return {
        "summary": summary,
        "bottleneck_records": df_calc,
        "sustained_events": sustained_events,
        "severity_counts": severity_counts
    }
