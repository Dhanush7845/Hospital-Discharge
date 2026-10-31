import pandas as pd
import numpy as np

# Column mapping from raw dataset to standardized names
COLUMN_MAPPING = {
    "date": "date",
    "children apprehended and placed in cbp custody*": "apprehensions",
    "children apprehended and placed in cbp custody": "apprehensions",
    "children in cbp custody": "cbp_custody",
    "children transferred out of cbp custody": "transfers",
    "children in hhs care": "hhs_care",
    "children discharged from hhs care": "discharges"
}

# Display labels for UI and reports
COLUMN_LABELS = {
    "date": "Reporting Date",
    "apprehensions": "Children Apprehended (Intake)",
    "cbp_custody": "Children in CBP Custody (Stock)",
    "transfers": "Children Transferred out of CBP (Movement)",
    "hhs_care": "Children in HHS Care (Stock)",
    "discharges": "Children Discharged from HHS (Movement)"
}

def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans raw UAC dataset according to analytical requirements:
    1. Removes completely empty rows.
    2. Standardizes column names (handles asterisks).
    3. Converts comma-separated number strings to numeric integers/floats.
    4. Parses dates into datetime objects.
    5. Sorts observations chronologically.
    6. Computes reporting interval (days since previous report).
    7. Adds temporal metadata (year, month, weekday, etc.).
    Preserves all valid reporting records.
    """
    if df is None or df.empty:
        return pd.DataFrame()
    
    cleaned = df.copy()
    
    # 1. Drop completely empty rows
    cleaned = cleaned.dropna(how='all')
    
    # Also drop rows where all values are empty strings or commas only
    cleaned = cleaned[~cleaned.apply(lambda row: row.astype(str).str.strip().str.replace(',', '', regex=False).eq('').all(), axis=1)]
    
    # 2. Standardize column names
    col_rename = {}
    for col in cleaned.columns:
        norm_col = str(col).strip().lower()
        if norm_col in COLUMN_MAPPING:
            col_rename[col] = COLUMN_MAPPING[norm_col]
        else:
            # Fuzzy check
            for raw_pattern, std_name in COLUMN_MAPPING.items():
                if raw_pattern.rstrip('*') in norm_col:
                    col_rename[col] = std_name
                    break
    
    cleaned = cleaned.rename(columns=col_rename)
    
    # 3. Clean numeric columns
    numeric_cols = ["apprehensions", "cbp_custody", "transfers", "hhs_care", "discharges"]
    for col in numeric_cols:
        if col in cleaned.columns:
            cleaned[col] = (
                cleaned[col]
                .astype(str)
                .str.replace(',', '', regex=False)
                .str.replace('"', '', regex=False)
                .str.replace("'", '', regex=False)
                .str.replace('$', '', regex=False)
                .str.strip()
            )
            cleaned[col] = pd.to_numeric(cleaned[col], errors='coerce')
    
    # Drop rows where date is missing or all numeric columns are NaN
    if 'date' in cleaned.columns:
        cleaned = cleaned.dropna(subset=['date'])
        # 4. Parse Dates
        cleaned['date'] = pd.to_datetime(cleaned['date'], format='%B %d, %Y', errors='coerce')
        # Fallback parsing for ISO or other formats if any NaT
        if cleaned['date'].isna().any():
            fallback_dates = pd.to_datetime(df.loc[cleaned.index, df.columns[0]], errors='coerce')
            cleaned['date'] = cleaned['date'].fillna(fallback_dates)
            
        cleaned = cleaned.dropna(subset=['date'])
        
        # 5. Sort chronologically
        cleaned = cleaned.sort_values('date').reset_index(drop=True)
        
        # 6. Add reporting interval & temporal attributes
        cleaned['days_since_prev_report'] = cleaned['date'].diff().dt.days
        cleaned['year'] = cleaned['date'].dt.year
        cleaned['month'] = cleaned['date'].dt.month
        cleaned['month_name'] = cleaned['date'].dt.strftime('%B')
        cleaned['year_month'] = cleaned['date'].dt.to_period('M').astype(str)
        cleaned['quarter'] = cleaned['date'].dt.to_period('Q').astype(str)
        cleaned['day_of_week'] = cleaned['date'].dt.dayofweek
        cleaned['day_name'] = cleaned['date'].dt.day_name()
        cleaned['is_weekend'] = cleaned['day_of_week'].isin([5, 6])
    
    # Fill remaining numeric NaNs with 0 if any (or keep valid)
    for col in numeric_cols:
        if col in cleaned.columns:
            cleaned[col] = cleaned[col].fillna(0).astype(int)
            
    return cleaned

def validate_dataset(df: pd.DataFrame) -> dict:
    """
    Validates a cleaned dataframe and returns diagnostics.
    """
    diagnostics = {
        "is_valid": True,
        "row_count": len(df),
        "errors": [],
        "warnings": [],
        "date_min": None,
        "date_max": None,
        "has_duplicates": False
    }
    
    required_cols = ["date", "apprehensions", "cbp_custody", "transfers", "hhs_care", "discharges"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        diagnostics["is_valid"] = False
        diagnostics["errors"].append(f"Missing required columns: {', '.join(missing)}")
        return diagnostics
        
    if df.empty:
        diagnostics["is_valid"] = False
        diagnostics["errors"].append("Dataset contains 0 valid observations.")
        return diagnostics
        
    diagnostics["date_min"] = df['date'].min()
    diagnostics["date_max"] = df['date'].max()
    
    # Check date duplicates
    dup_count = df['date'].duplicated().sum()
    if dup_count > 0:
        diagnostics["has_duplicates"] = True
        diagnostics["warnings"].append(f"Found {dup_count} duplicate reporting dates.")
        
    # Check negative values
    for col in ["apprehensions", "cbp_custody", "transfers", "hhs_care", "discharges"]:
        neg_count = (df[col] < 0).sum()
        if neg_count > 0:
            diagnostics["warnings"].append(f"Column '{col}' has {neg_count} negative entries.")
            
    return diagnostics
