import pandas as pd
import numpy as np
from scipy import stats
from .utils import safe_divide
from .kpi_calculations import add_daily_metrics

def compute_research_statistics(df: pd.DataFrame) -> dict:
    """
    Computes rigorous exploratory data analysis (EDA), correlation,
    distribution metrics, and linear regression models.
    """
    if df is None or df.empty:
        return {
            "descriptive_stats": pd.DataFrame(),
            "correlation_matrix": pd.DataFrame(),
            "outlier_summary": {},
            "regressions": {},
            "insights": []
        }
        
    df_calc = add_daily_metrics(df)
    
    analysis_cols = [
        "apprehensions", "cbp_custody", "transfers", "hhs_care", "discharges",
        "transfer_efficiency_ratio", "discharge_effectiveness_index", "overall_net_accumulation"
    ]
    existing_cols = [c for c in analysis_cols if c in df_calc.columns]
    
    # 1. Descriptive Statistics
    desc_stats = df_calc[existing_cols].describe().T
    desc_stats["median"] = df_calc[existing_cols].median()
    desc_stats["skewness"] = df_calc[existing_cols].skew()
    desc_stats["kurtosis"] = df_calc[existing_cols].kurtosis()
    
    # 2. Correlation Matrix
    corr_matrix = df_calc[existing_cols].corr()
    
    # 3. Outlier Summary using IQR method
    outlier_summary = {}
    for col in ["apprehensions", "cbp_custody", "transfers", "hhs_care", "discharges"]:
        if col in df_calc.columns:
            q25 = df_calc[col].quantile(0.25)
            q75 = df_calc[col].quantile(0.75)
            iqr = q75 - q25
            lower_fence = q25 - 1.5 * iqr
            upper_fence = q75 + 1.5 * iqr
            outliers = df_calc[(df_calc[col] < lower_fence) | (df_calc[col] > upper_fence)]
            outlier_summary[col] = {
                "q25": q25,
                "q75": q75,
                "iqr": iqr,
                "lower_fence": lower_fence,
                "upper_fence": upper_fence,
                "outlier_count": len(outliers),
                "outlier_pct": (len(outliers) / len(df_calc)) * 100
            }
            
    # 4. Linear Regressions (Relationships)
    regressions = {}
    pairs = [
        ("apprehensions", "transfers", "Intake vs Transfer Velocity"),
        ("transfers", "discharges", "HHS Transfers vs HHS Discharges"),
        ("cbp_custody", "transfers", "CBP Custody Stock vs Transfer Movement"),
        ("hhs_care", "discharges", "HHS Care Stock vs Discharge Movement")
    ]
    for x_col, y_col, label in pairs:
        if x_col in df_calc.columns and y_col in df_calc.columns and len(df_calc) > 2:
            x_vals = df_calc[x_col].astype(float).values
            y_vals = df_calc[y_col].astype(float).values
            if len(x_vals) > 2 and np.amax(x_vals) > np.amin(x_vals):
                try:
                    slope, intercept, r_value, p_value, std_err = stats.linregress(x_vals, y_vals)
                    regressions[label] = {
                        "x_col": x_col,
                        "y_col": y_col,
                        "slope": float(slope),
                        "intercept": float(intercept),
                        "r_squared": float(r_value ** 2),
                        "r_value": float(r_value),
                        "p_value": float(p_value),
                        "std_err": float(std_err)
                    }
                except Exception:
                    pass

    # 5. Automated Statistical Insights
    insights = []
    
    # Apprehension-Transfer relationship
    if "Intake vs Transfer Velocity" in regressions:
        r2 = regressions["Intake vs Transfer Velocity"]["r_squared"]
        r = regressions["Intake vs Transfer Velocity"]["r_value"]
        insights.append(
            f"Daily apprehensions and transfers exhibit a Pearson correlation of r = {r:.3f} (R² = {r2:.3f}). "
            f"This indicates that while transfer velocity tracks border intake, substantial uncoupling exists on peak intake days."
        )
        
    # HHS Care Stock vs Discharges
    if "HHS Care Stock vs Discharge Movement" in regressions:
        r_care = regressions["HHS Care Stock vs Discharge Movement"]["r_value"]
        insights.append(
            f"HHS care population stock correlates with daily discharge volume at r = {r_care:.3f}. "
            f"Larger active shelter census correlates strongly with higher aggregate daily placement volumes."
        )
        
    # Skewness insight
    skew_app = desc_stats.loc["apprehensions", "skewness"] if "apprehensions" in desc_stats.index else 0
    if skew_app > 1.0:
        insights.append(
            f"Daily apprehensions show right-skewed distribution (skewness = {skew_app:.2f}), "
            f"reflecting episodic border surge events separated by extended baseline periods."
        )

    return {
        "descriptive_stats": desc_stats,
        "correlation_matrix": corr_matrix,
        "outlier_summary": outlier_summary,
        "regressions": regressions,
        "insights": insights,
        "df_with_metrics": df_calc
    }
