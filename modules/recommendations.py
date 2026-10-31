import pandas as pd
import numpy as np
from .kpi_calculations import calculate_core_kpis, add_daily_metrics
from .bottleneck_detection import detect_bottlenecks
from .anomaly_detection import calculate_outcome_stability

def generate_system_alerts_and_recommendations(
    df: pd.DataFrame,
    transfer_eff_threshold: float = 25.0,
    cbp_net_threshold: float = 20.0,
    hhs_net_threshold: float = 30.0,
    discharge_eff_threshold: float = 2.0
) -> dict:
    """
    Generates actionable, evidence-based alerts and operational recommendations
    derived directly from the empirical pipeline metrics.
    """
    if df is None or df.empty:
        return {
            "alerts": [],
            "recommendations": [],
            "alert_df": pd.DataFrame()
        }
        
    kpis = calculate_core_kpis(df)
    bottlenecks = detect_bottlenecks(df, cbp_threshold=cbp_net_threshold, hhs_threshold=hhs_net_threshold)
    stability = calculate_outcome_stability(df)
    df_calc = add_daily_metrics(df)
    
    alerts = []
    
    # Alert 1: Overall Backlog Accumulation
    if kpis["overall_backlog_accumulation"] > 100:
        alerts.append({
            "id": "ALT-001",
            "category": "Pipeline Throughput",
            "severity": "High",
            "title": f"Systemic Intake Exceeds Placements (+{kpis['overall_backlog_accumulation']:,} Children)",
            "metric": f"Throughput: {kpis['pipeline_throughput']:.1f}%",
            "description": (
                f"Across the observed period, total apprehensions ({kpis['total_apprehensions']:,}) "
                f"exceeded total HHS discharges ({kpis['total_discharges']:,}) by "
                f"{kpis['overall_backlog_accumulation']:,} children, driving custody inventory growth."
            ),
            "recommendation": (
                "Conduct comprehensive placement capacity review across HHS shelter network; "
                "accelerate family reunification sponsorship vetting workflows to match intake velocity."
            )
        })
    elif kpis["overall_backlog_accumulation"] < -100:
        alerts.append({
            "id": "ALT-001-INFO",
            "category": "Pipeline Throughput",
            "severity": "Low",
            "title": f"Net System De-accumulation ({kpis['overall_backlog_accumulation']:,} Children)",
            "metric": f"Throughput: {kpis['pipeline_throughput']:.1f}%",
            "description": (
                f"Total HHS discharges ({kpis['total_discharges']:,}) exceeded total apprehensions "
                f"({kpis['total_apprehensions']:,}), indicating a drawdown of overall care population."
            ),
            "recommendation": "Maintain standard operational post-release monitoring protocols."
        })
        
    # Alert 2: Transfer Efficiency Friction
    low_te_days = (df_calc["transfer_efficiency_ratio"] < transfer_eff_threshold).sum()
    pct_low_te = (low_te_days / len(df_calc)) * 100
    if pct_low_te >= 25.0:
        alerts.append({
            "id": "ALT-002",
            "category": "CBP-to-HHS Transition",
            "severity": "High" if pct_low_te >= 50 else "Medium",
            "title": f"Low Daily Transfer Velocity ({low_te_days} of {len(df_calc)} Days < {transfer_eff_threshold:.0f}%)",
            "metric": f"Mean Daily TE: {kpis['daily_mean_transfer_efficiency']:.1f}%",
            "description": (
                f"In {pct_low_te:.1f}% of observed reporting days, daily transfers represented "
                f"less than {transfer_eff_threshold:.0f}% of children in active CBP custody."
            ),
            "recommendation": (
                "Review inter-agency transport scheduling, medical clearance turnaround, "
                "and HHS intake facility bed availability to minimize time spent in border facilities."
            )
        })

    # Alert 3: Sustained CBP Net Accumulation
    sustained_cbp = [e for e in bottlenecks["sustained_events"] if e["stage"] == "CBP Intake Friction"]
    if sustained_cbp:
        max_streak = max(e["consecutive_obs"] for e in sustained_cbp)
        alerts.append({
            "id": "ALT-003",
            "category": "Border Holding Backlog",
            "severity": "High" if max_streak >= 5 else "Medium",
            "title": f"Sustained CBP Intake Surges Detected ({len(sustained_cbp)} Episodes)",
            "metric": f"Longest Friction Streak: {max_streak} consecutive observations",
            "description": (
                f"Identified {len(sustained_cbp)} sustained periods where CBP intake consecutively "
                f"outpaced transfers out of custody. Longest episode persisted for {max_streak} reporting days."
            ),
            "recommendation": (
                "Establish dynamic escalation triggers to dispatch mobile intake processing teams "
                "when intake outpaces transfers for 3 consecutive reporting days."
            )
        })

    # Alert 4: HHS Placement Lag (Shelter Saturation)
    sustained_hhs = [e for e in bottlenecks["sustained_events"] if e["stage"] == "HHS Placement Lag"]
    if sustained_hhs:
        alerts.append({
            "id": "ALT-004",
            "category": "HHS Shelter Accumulation",
            "severity": "Medium",
            "title": f"HHS Inflow Outpaces Discharges ({len(sustained_hhs)} Episodes)",
            "metric": f"Total HHS Net Growth: +{kpis['hhs_net_accumulation']:,}",
            "description": (
                f"Transfers into HHS care exceeded community discharges in {len(sustained_hhs)} sustained episodes, "
                f"increasing length of stay in grantee facilities."
            ),
            "recommendation": (
                "Expand case management staff allocations and streamline fingerprint background "
                "checks for Category 1 (parent/legal guardian) sponsors."
            )
        })

    # Alert 5: Weekend Placement Deceleration
    df_calc["day_type"] = df_calc["is_weekend"].apply(lambda x: "Weekend" if x else "Weekday")
    w_comp = df_calc.groupby("day_type")["discharges"].mean().to_dict()
    weekday_avg = w_comp.get("Weekday", 0)
    weekend_avg = w_comp.get("Weekend", 0)
    if weekday_avg > 0 and weekend_avg < weekday_avg * 0.7:
        drop_pct = ((weekday_avg - weekend_avg) / weekday_avg) * 100
        alerts.append({
            "id": "ALT-005",
            "category": "Operational Cadence",
            "severity": "Low",
            "title": f"Weekend Placement Drop-off ({drop_pct:.1f}% Lower Discharge Velocity)",
            "metric": f"Weekday: {weekday_avg:.1f}/day vs Weekend: {weekend_avg:.1f}/day",
            "description": (
                f"HHS discharges average {weekend_avg:.1f} per weekend reporting day compared to "
                f"{weekday_avg:.1f} on weekdays, creating Monday intake bottlenecks."
            ),
            "recommendation": (
                "Implement weekend case management and travel coordination shifts to prevent "
                "avoidable custodial retention over weekends."
            )
        })

    # Alert 6: Outcome Stability & Outlier Spikes
    if stability["stability_score"] < 50.0:
        alerts.append({
            "id": "ALT-006",
            "category": "Outcome Stability",
            "severity": "Medium",
            "title": f"Elevated Discharge Volatility (Score: {stability['stability_score']:.1f}/100)",
            "metric": f"CV: {stability['cv']:.2f}",
            "description": (
                f"Discharge velocity demonstrates high statistical variation (standard deviation: "
                f"{stability['std_discharge']:.1f} vs mean: {stability['mean_discharge']:.1f})."
            ),
            "recommendation": (
                "Standardize weekly placement quota planning and audit grantee facilities showing "
                "intermittent batch-processing discharge patterns."
            )
        })
        
    # Convert alerts to DataFrame for easy filtering and export
    alert_df = pd.DataFrame(alerts) if alerts else pd.DataFrame(columns=[
        "id", "category", "severity", "title", "metric", "description", "recommendation"
    ])
    
    return {
        "alerts": alerts,
        "recommendations": [a["recommendation"] for a in alerts],
        "alert_df": alert_df
    }
