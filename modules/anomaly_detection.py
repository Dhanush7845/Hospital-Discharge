import pandas as pd
import numpy as np
from .utils import safe_divide

def calculate_outcome_stability(df: pd.DataFrame, rolling_window: int = 14) -> dict:
    """
    Evaluates placement & discharge consistency and detects statistical anomalies.
    
    Metrics:
    - Mean discharge volume
    - Standard deviation
    - Variance
    - Coefficient of Variation (CV = SD / Mean)
    - Outcome Stability Score = 100 / (1 + CV)
    - Anomaly detection using Z-score (outliers: |Z| > 2.5) and IQR bounds.
    """
    if df is None or df.empty or "discharges" not in df.columns:
        return {
            "mean_discharge": 0.0,
            "std_discharge": 0.0,
            "variance_discharge": 0.0,
            "cv": 0.0,
            "stability_score": 0.0,
            "stability_grade": "N/A",
            "anomalies": pd.DataFrame(),
            "df_stability": pd.DataFrame()
        }
        
    df_calc = df.copy()
    discharges = df_calc["discharges"].astype(float)
    
    mean_val = float(discharges.mean())
    std_val = float(discharges.std()) if len(discharges) > 1 else 0.0
    var_val = float(discharges.var()) if len(discharges) > 1 else 0.0
    
    # Coefficient of Variation: CV = SD / Mean
    cv = safe_divide(std_val, mean_val, default=0.0)
    
    # Outcome Stability Score: 100 / (1 + CV)
    stability_score = safe_divide(100.0, 1.0 + cv, default=0.0)
    
    # Qualitative Grade
    if stability_score >= 80:
        grade = "High Stability (Highly Consistent Placement Velocity)"
    elif stability_score >= 60:
        grade = "Moderate Stability (Expected Seasonal Variations)"
    elif stability_score >= 40:
        grade = "Elevated Volatility (Noticeable Operational Fluctuations)"
    else:
        grade = "High Volatility (Severe Placement Velocity Swings)"
        
    # Rolling calculations
    df_calc["rolling_mean"] = discharges.rolling(window=rolling_window, min_periods=3).mean()
    df_calc["rolling_std"] = discharges.rolling(window=rolling_window, min_periods=3).std().fillna(0)
    df_calc["rolling_cv"] = df_calc.apply(lambda r: safe_divide(r["rolling_std"], r["rolling_mean"]), axis=1)
    df_calc["rolling_stability_score"] = df_calc["rolling_cv"].apply(lambda cv_val: safe_divide(100.0, 1.0 + cv_val))
    
    # Statistical Anomaly Detection (Z-score & Rolling IQR)
    if std_val > 0:
        df_calc["z_score"] = (discharges - mean_val) / std_val
    else:
        df_calc["z_score"] = 0.0
        
    # Upper and lower thresholds based on 2.5 standard deviations
    df_calc["upper_bound"] = mean_val + 2.5 * std_val
    df_calc["lower_bound"] = np.maximum(0, mean_val - 2.5 * std_val)
    
    df_calc["is_anomaly"] = (df_calc["z_score"].abs() >= 2.5)
    df_calc["anomaly_type"] = "Normal"
    df_calc.loc[df_calc["z_score"] >= 2.5, "anomaly_type"] = "Surge Outlier (High Placement Spike)"
    df_calc.loc[df_calc["z_score"] <= -2.5, "anomaly_type"] = "Plunge Outlier (Sharp Placement Drop)"
    
    anomalies = df_calc[df_calc["is_anomaly"]].copy()
    
    return {
        "mean_discharge": mean_val,
        "std_discharge": std_val,
        "variance_discharge": var_val,
        "cv": cv,
        "stability_score": stability_score,
        "stability_grade": grade,
        "anomalies": anomalies,
        "df_stability": df_calc
    }
