import pytest
import pandas as pd
from modules.bottleneck_detection import detect_bottlenecks

def test_bottleneck_detection_logic():
    """Verify net accumulation calculations and streak detection."""
    df = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=6),
        "apprehensions": [50, 60, 70, 20, 20, 20],
        "cbp_custody": [30, 40, 50, 20, 20, 20],
        "transfers": [20, 20, 20, 30, 30, 30],
        "hhs_care": [500, 500, 500, 500, 500, 500],
        "discharges": [10, 10, 10, 20, 20, 20]
    })
    
    # Run bottleneck detection with cbp_threshold = 20, min_streak = 3
    results = detect_bottlenecks(df, cbp_threshold=20.0, min_consecutive_obs=3)
    
    # Days 0, 1, 2 have cbp_net = 30, 40, 50 (all > 0)
    # Days 3, 4, 5 have cbp_net = -10, -10, -10
    sustained = results["sustained_events"]
    cbp_streaks = [s for s in sustained if s["stage"] == "CBP Intake Friction"]
    assert len(cbp_streaks) == 1
    assert cbp_streaks[0]["consecutive_obs"] == 3
    assert cbp_streaks[0]["total_net_accumulation"] == 30 + 40 + 50
    
    # Verify severity counts
    counts = results["severity_counts"]
    assert counts["Red"] + counts["Yellow"] + counts["Green"] == 6

def test_empty_dataframe_bottlenecks():
    """Verify safe empty state handling."""
    empty_df = pd.DataFrame()
    res = detect_bottlenecks(empty_df)
    assert res["summary"] == {}
    assert res["sustained_events"] == []
