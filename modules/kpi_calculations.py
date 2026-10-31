import pandas as pd
import numpy as np
from .utils import safe_divide

def calculate_core_kpis(df: pd.DataFrame) -> dict:
    """
    Calculates primary executive and operational KPIs for the care transition pipeline.
    All calculations protect against zero denominators and distinguish between
    snapshot custody stocks and daily movement flows.
    """
    if df is None or df.empty:
        return {
            "total_apprehensions": 0,
            "total_transfers": 0,
            "total_discharges": 0,
            "avg_cbp_custody": 0.0,
            "avg_hhs_care": 0.0,
            "transfer_efficiency": 0.0,
            "daily_mean_transfer_efficiency": 0.0,
            "transfer_to_intake_ratio": 0.0,
            "transfer_gap": 0,
            "discharge_effectiveness": 0.0,
            "daily_mean_discharge_effectiveness": 0.0,
            "discharge_to_transfer_ratio": 0.0,
            "discharge_gap": 0,
            "pipeline_throughput": 0.0,
            "overall_backlog_accumulation": 0,
            "cbp_net_accumulation": 0,
            "hhs_net_accumulation": 0,
            "observation_count": 0,
            "date_start": None,
            "date_end": None,
            "calendar_days": 0
        }

    # Volume Flows (Movements)
    total_apprehensions = int(df["apprehensions"].sum())
    total_transfers = int(df["transfers"].sum())
    total_discharges = int(df["discharges"].sum())
    
    # Custody Stocks (Snapshots)
    avg_cbp_custody = float(df["cbp_custody"].mean())
    avg_hhs_care = float(df["hhs_care"].mean())
    
    # 1. Transfer Efficiency Ratio (%): (Transfers / CBP Custody) * 100
    # On an aggregate reporting period basis: Total Transfers / Summed Custody-Days * 100
    total_cbp_custody_days = float(df["cbp_custody"].sum())
    transfer_efficiency = safe_divide(total_transfers, total_cbp_custody_days) * 100
    
    # Daily mean transfer efficiency (mean of daily transfers / cbp_custody)
    daily_te = df.apply(lambda r: safe_divide(r["transfers"], r["cbp_custody"]) * 100, axis=1)
    daily_mean_transfer_efficiency = float(daily_te.mean())
    
    # Transfer-to-Intake Ratio (%): (Total Transfers / Total Apprehended) * 100
    transfer_to_intake_ratio = safe_divide(total_transfers, total_apprehensions) * 100
    
    # Transfer Gap: Total Apprehensions - Total Transfers
    transfer_gap = total_apprehensions - total_transfers
    
    # 2. Discharge Effectiveness Index (%): (Discharges / HHS Care) * 100
    # Aggregate: Total Discharges / Summed HHS-Care-Days * 100
    total_hhs_care_days = float(df["hhs_care"].sum())
    discharge_effectiveness = safe_divide(total_discharges, total_hhs_care_days) * 100
    
    # Daily mean discharge effectiveness
    daily_de = df.apply(lambda r: safe_divide(r["discharges"], r["hhs_care"]) * 100, axis=1)
    daily_mean_discharge_effectiveness = float(daily_de.mean())
    
    # Discharge-to-Transfer Ratio (%): (Total Discharges / Total Transfers) * 100
    discharge_to_transfer_ratio = safe_divide(total_discharges, total_transfers) * 100
    
    # Discharge Gap: Total Transfers - Total Discharges
    discharge_gap = total_transfers - total_discharges
    
    # 3. Overall Pipeline Throughput (%): (Total Discharges / Total Apprehensions) * 100
    pipeline_throughput = safe_divide(total_discharges, total_apprehensions) * 100
    
    # 4. Net Flow Accumulations
    cbp_net = total_apprehensions - total_transfers
    hhs_net = total_transfers - total_discharges
    overall_backlog = total_apprehensions - total_discharges
    
    # Reporting Dates
    min_date = df["date"].min()
    max_date = df["date"].max()
    cal_days = (max_date - min_date).days + 1 if pd.notna(min_date) and pd.notna(max_date) else 0

    return {
        "total_apprehensions": total_apprehensions,
        "total_transfers": total_transfers,
        "total_discharges": total_discharges,
        "avg_cbp_custody": avg_cbp_custody,
        "avg_hhs_care": avg_hhs_care,
        "transfer_efficiency": transfer_efficiency,
        "daily_mean_transfer_efficiency": daily_mean_transfer_efficiency,
        "transfer_to_intake_ratio": transfer_to_intake_ratio,
        "transfer_gap": transfer_gap,
        "discharge_effectiveness": discharge_effectiveness,
        "daily_mean_discharge_effectiveness": daily_mean_discharge_effectiveness,
        "discharge_to_transfer_ratio": discharge_to_transfer_ratio,
        "discharge_gap": discharge_gap,
        "pipeline_throughput": pipeline_throughput,
        "overall_backlog_accumulation": overall_backlog,
        "cbp_net_accumulation": cbp_net,
        "hhs_net_accumulation": hhs_net,
        "observation_count": len(df),
        "date_start": min_date,
        "date_end": max_date,
        "calendar_days": cal_days
    }

def add_daily_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Appends calculated daily ratio and gap metrics to the dataframe.
    """
    if df is None or df.empty:
        return pd.DataFrame()
        
    df_calc = df.copy()
    
    # Flow differences (Net Accumulations)
    df_calc["cbp_net_accumulation"] = df_calc["apprehensions"] - df_calc["transfers"]
    df_calc["hhs_net_accumulation"] = df_calc["transfers"] - df_calc["discharges"]
    df_calc["overall_net_accumulation"] = df_calc["apprehensions"] - df_calc["discharges"]
    
    # Cumulative Net Accumulations
    df_calc["cum_cbp_net_accumulation"] = df_calc["cbp_net_accumulation"].cumsum()
    df_calc["cum_hhs_net_accumulation"] = df_calc["hhs_net_accumulation"].cumsum()
    df_calc["cum_overall_net_accumulation"] = df_calc["overall_net_accumulation"].cumsum()
    
    # Flow Ratios
    df_calc["transfer_efficiency_ratio"] = df_calc.apply(
        lambda r: safe_divide(r["transfers"], r["cbp_custody"]) * 100, axis=1
    )
    df_calc["transfer_to_intake_ratio"] = df_calc.apply(
        lambda r: safe_divide(r["transfers"], r["apprehensions"]) * 100, axis=1
    )
    df_calc["transfer_gap"] = df_calc["apprehensions"] - df_calc["transfers"]
    
    df_calc["discharge_effectiveness_index"] = df_calc.apply(
        lambda r: safe_divide(r["discharges"], r["hhs_care"]) * 100, axis=1
    )
    df_calc["discharge_to_transfer_ratio"] = df_calc.apply(
        lambda r: safe_divide(r["discharges"], r["transfers"]) * 100, axis=1
    )
    df_calc["discharge_gap"] = df_calc["transfers"] - df_calc["discharges"]
    df_calc["daily_pipeline_throughput"] = df_calc.apply(
        lambda r: safe_divide(r["discharges"], r["apprehensions"]) * 100, axis=1
    )
    
    # Rolling 7-observation averages
    df_calc["rolling_7_apprehensions"] = df_calc["apprehensions"].rolling(window=7, min_periods=1).mean()
    df_calc["rolling_7_transfers"] = df_calc["transfers"].rolling(window=7, min_periods=1).mean()
    df_calc["rolling_7_discharges"] = df_calc["discharges"].rolling(window=7, min_periods=1).mean()
    df_calc["rolling_7_transfer_efficiency"] = df_calc["transfer_efficiency_ratio"].rolling(window=7, min_periods=1).mean()
    df_calc["rolling_7_discharge_effectiveness"] = df_calc["discharge_effectiveness_index"].rolling(window=7, min_periods=1).mean()
    df_calc["rolling_7_overall_net_accumulation"] = df_calc["overall_net_accumulation"].rolling(window=7, min_periods=1).mean()
    
    return df_calc
