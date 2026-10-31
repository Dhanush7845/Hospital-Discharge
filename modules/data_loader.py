import os
import pandas as pd
from .data_cleaning import clean_dataset, validate_dataset

DEFAULT_DATASET_NAME = "HHS_Unaccompanied_Alien_Children_Program.csv"

def get_default_dataset_path() -> str:
    """Returns absolute path to the bundled default dataset."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    return os.path.join(project_root, "data", DEFAULT_DATASET_NAME)

def load_csv(filepath_or_buffer) -> pd.DataFrame:
    """Loads and cleans CSV data."""
    raw_df = pd.read_csv(filepath_or_buffer)
    return clean_dataset(raw_df)

def load_excel(filepath_or_buffer) -> pd.DataFrame:
    """Loads and cleans Excel data."""
    raw_df = pd.read_excel(filepath_or_buffer)
    return clean_dataset(raw_df)

def init_session_data(st_state) -> pd.DataFrame:
    """Initializes or retrieves the active dataset in Streamlit session state."""
    if "active_data" not in st_state or st_state["active_data"] is None or st_state["active_data"].empty:
        default_path = get_default_dataset_path()
        if os.path.exists(default_path):
            cleaned = load_csv(default_path)
            st_state["active_data"] = cleaned
            st_state["dataset_source"] = "Default HHS Dataset (720 Records)"
            st_state["raw_active_data"] = cleaned.copy()
        else:
            st_state["active_data"] = pd.DataFrame()
            st_state["dataset_source"] = "No Dataset Loaded"
            st_state["raw_active_data"] = pd.DataFrame()
            
    return st_state["active_data"]

def set_active_data(st_state, df: pd.DataFrame, source_name: str = "Uploaded Dataset"):
    """Replaces the active dataset in session state."""
    st_state["active_data"] = df
    st_state["dataset_source"] = source_name
    st_state["raw_active_data"] = df.copy()

def reset_to_default(st_state):
    """Restores the bundled default dataset."""
    default_path = get_default_dataset_path()
    if os.path.exists(default_path):
        cleaned = load_csv(default_path)
        st_state["active_data"] = cleaned
        st_state["dataset_source"] = "Default HHS Dataset (720 Records)"
        st_state["raw_active_data"] = cleaned.copy()
