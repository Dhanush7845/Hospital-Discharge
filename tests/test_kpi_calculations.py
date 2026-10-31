import pytest
import pandas as pd
import numpy as np
from modules.kpi_calculations import calculate_core_kpis, add_daily_metrics
from modules.utils import safe_divide
from modules.anomaly_detection import calculate_outcome_stability

def test_safe_divide():
    """Verify zero-division and edge cases are safely handled."""
    assert safe_divide(10, 2) == 5.0
    assert safe_divide(10, 0) == 0.0
    assert safe_divide(10, None) == 0.0
    assert safe_divide(None, 10) == 0.0
    assert safe_divide(0, 0, default=-1.0) == -1.0
    assert safe_divide(np.nan, 5) == 0.0
    assert safe_divide(5, np.nan) == 0.0

def test_core_kpis_calculation():
    """Verify primary KPI formula outputs against hand-calculated values."""
    df = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=2),
        "apprehensions": [100, 200],  # total = 300
        "cbp_custody": [50, 150],     # avg = 100, sum = 200
        "transfers": [80, 160],       # total = 240
        "hhs_care": [1000, 2000],     # avg = 1500, sum = 3000
        "discharges": [70, 110]       # total = 180
    })
    
    kpis = calculate_core_kpis(df)
    
    assert kpis["total_apprehensions"] == 300
    assert kpis["total_transfers"] == 240
    assert kpis["total_discharges"] == 180
    assert kpis["avg_cbp_custody"] == 100.0
    assert kpis["avg_hhs_care"] == 1500.0
    
    # Transfer Efficiency: (240 / 200) * 100 = 120.0%
    assert pytest.approx(kpis["transfer_efficiency"], 0.01) == 120.0
    
    # Discharge Effectiveness: (180 / 3000) * 100 = 6.0%
    assert pytest.approx(kpis["discharge_effectiveness"], 0.01) == 6.0
    
    # Pipeline Throughput: (180 / 300) * 100 = 60.0%
    assert pytest.approx(kpis["pipeline_throughput"], 0.01) == 60.0
    
    # Backlog Accumulation: 300 - 180 = 120
    assert kpis["overall_backlog_accumulation"] == 120

def test_outcome_stability_score():
    """Verify Outcome Stability Score = 100 / (1 + CV)."""
    # When discharges are constant: mean=50, std=0 -> CV=0 -> Score = 100 / (1 + 0) = 100
    df_const = pd.DataFrame({
        "discharges": [50, 50, 50, 50, 50]
    })
    res_const = calculate_outcome_stability(df_const)
    assert pytest.approx(res_const["stability_score"], 0.01) == 100.0
    assert res_const["cv"] == 0.0
    
    # When CV is positive
    df_var = pd.DataFrame({
        "discharges": [10, 20, 30, 40, 50]
    })
    res_var = calculate_outcome_stability(df_var)
    expected_cv = np.std([10, 20, 30, 40, 50], ddof=1) / np.mean([10, 20, 30, 40, 50])
    expected_score = 100.0 / (1.0 + expected_cv)
    assert pytest.approx(res_var["stability_score"], 0.01) == expected_score
