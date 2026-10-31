import pytest
import pandas as pd
import numpy as np
import os
from modules.data_cleaning import clean_dataset, validate_dataset
from modules.data_loader import get_default_dataset_path, load_csv

def test_clean_default_dataset():
    """Verify that cleaning the bundled CSV preserves exactly 720 valid observations."""
    csv_path = get_default_dataset_path()
    assert os.path.exists(csv_path), f"Default CSV not found at {csv_path}"
    
    cleaned_df = load_csv(csv_path)
    assert len(cleaned_df) == 720, f"Expected 720 records, got {len(cleaned_df)}"
    
    # Check required columns
    expected_cols = ["date", "apprehensions", "cbp_custody", "transfers", "hhs_care", "discharges"]
    for c in expected_cols:
        assert c in cleaned_df.columns, f"Missing column {c}"
        
    # Check chronological ordering
    assert cleaned_df["date"].is_monotonic_increasing, "Cleaned dataset must be sorted chronologically"
    
    # Check date range: Jan 12, 2023 to Dec 21, 2025
    assert cleaned_df["date"].min() == pd.Timestamp("2023-01-12")
    assert cleaned_df["date"].max() == pd.Timestamp("2025-12-21")
    
    # Check no nulls in numeric fields
    for c in ["apprehensions", "cbp_custody", "transfers", "hhs_care", "discharges"]:
        assert cleaned_df[c].isna().sum() == 0, f"Column {c} contains nulls"

def test_clean_empty_rows_and_commas():
    """Verify handling of empty rows and comma-separated numbers."""
    raw_data = {
        "Date": ["December 21, 2025", None, "December 18, 2025", ""],
        "Children apprehended and placed in CBP custody*": ["6", None, "11", ""],
        "Children in CBP custody": ["18", None, "50", ""],
        "Children transferred out of CBP custody": ["11", None, "6", ""],
        "Children in HHS Care": ['"2,484"', None, '"2,472"', ""],
        "Children discharged from HHS Care": ["14", None, "16", ""]
    }
    df = pd.DataFrame(raw_data)
    cleaned = clean_dataset(df)
    
    assert len(cleaned) == 2, f"Expected 2 rows after dropping empties, got {len(cleaned)}"
    assert cleaned.iloc[0]["hhs_care"] == 2472  # 2025-12-18 is earlier than 2025-12-21
    assert cleaned.iloc[1]["hhs_care"] == 2484

def test_validate_dataset_diagnostics():
    """Verify validation diagnostics on good vs corrupted data."""
    valid_df = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=5),
        "apprehensions": [10, 20, 30, 40, 50],
        "cbp_custody": [15, 25, 35, 45, 55],
        "transfers": [8, 18, 28, 38, 48],
        "hhs_care": [100, 110, 120, 130, 140],
        "discharges": [7, 17, 27, 37, 47]
    })
    diag = validate_dataset(valid_df)
    assert diag["is_valid"] is True
    assert diag["row_count"] == 5
    assert len(diag["errors"]) == 0
    
    # Missing column
    invalid_df = valid_df.drop(columns=["apprehensions"])
    diag_invalid = validate_dataset(invalid_df)
    assert diag_invalid["is_valid"] is False
    assert len(diag_invalid["errors"]) > 0
