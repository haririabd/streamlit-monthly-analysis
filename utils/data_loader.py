import pandas as pd
from pathlib import Path
import streamlit as st

def load_excel(file_name: str = "DNB_Raw TT Data.xlsx") -> pd.DataFrame:
    """Load Excel file from source/ folder."""
    file_path = Path(__file__).resolve().parent.parent / "source" / file_name
    try:
        df = pd.read_excel(file_path, engine="openpyxl")
    except FileNotFoundError:
        st.error(f"Excel file not found at {file_path}")
        return pd.DataFrame()

    return df