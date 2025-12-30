import os
import sqlite3
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

def load_data(db_path: str) -> pd.DataFrame:
    # Load data from DB
    if not os.path.exists(db_path):
        st.error(f"Database not found at: {db_path}. Please check your .env path or run the processor script.")
        return pd.DataFrame()

    try:
        conn = sqlite3.connect(db_path)
        # Select all columns
        query = "SELECT * FROM downtime_logs"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error loading database: {e}")
        return pd.DataFrame()