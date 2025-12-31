import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime

# Utils
from utils.data_loader import load_data
from utils.data_cleaner import clean_tt_data, clean_db_data
from utils.month_filter import get_month_filters

# Function in graph
from utils.graph_altair import (
    build_downtime_table,
    plot_top10_sites_by_downtime_altair,
    plot_top_repeated_sites_bar,
    plot_repeated_sites_comparison
)

load_dotenv()

# For seamless Data Source switch
DATA_SOURCE = os.getenv("DATA_SOURCE", "db").lower()
EXCEL_FILENAME = os.getenv("EXCEL_FILENAME", "sourcefile.xlsx")

BASE_DIR = os.getenv("BASE_DIR")
DB_NAME = os.getenv("DB_NAME", "outage_master.db")

if not BASE_DIR:
    st.error("Configuration Error: BASE_DIR not set in .env file")
    st.stop()

DB_PATH = os.path.join(BASE_DIR, DB_NAME)

st.set_page_config(
    page_title="5G Outage Analysis Dashboard",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)

if DATA_SOURCE == 'excel':
    st.warning(
        f"⚠️ **TEST MODE:** Displaying historical data from Excel"
    )
# ---------------------------------
"""
# :material/query_stats: 5G Monthly Outage Analysis

Based on https://github.com/streamlit/demo-stockpeers/
"""

""
try:
    df_raw = load_data()
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()

df_clean = clean_db_data(df_raw)
df_clean = df_clean.dropna(subset=["end_date"])

if df_clean.empty:
    st.warning("No data found in database. Waiting for processor to run...")
    st.stop()
    
# Filter data based on user's month selection
filters = get_month_filters(df_clean)
today = datetime.today()
current_period = pd.Period(today, freq="M")
current_month_name = datetime.now().strftime("%B %Y")  # e.g., "November"

df_current = df_clean[df_clean["month"] == filters["current"]] # Filter for current month
df_last = df_clean[df_clean["month"] == filters["last"]] # Filter for last full month
df_compare = df_clean[df_clean["month"].isin([filters["current"], filters["last"]])] # Comparison: current vs last

with st.container():
    cols = st.columns([1, 3])
    
    col1 = cols[0].container(
        border=True, height="stretch", vertical_alignment="center"
        )
    col2 = cols[1].container(
        border=True, height="stretch", vertical_alignment="center"
        )
    col3 = cols[0].container(
        border=False, height="stretch", vertical_alignment="center"
        )
    
    with col1:
        # Frontend Month Selection
        month_options = sorted(df_clean["month"].dropna().unique(), reverse=True)
        selected_period = st.selectbox("Select a month to view:", month_options)
        previous_period = selected_period - 1  # subtract one month
        df_selected = df_clean[df_clean["month"] == selected_period] # subset of df_clean, contains only the selected month
        
        if selected_period == current_period:
            selected_label = "Current Month"
        elif selected_period == previous_period:
            selected_label = "Last Month"
        else:
            selected_label = selected_period.strftime("%B %Y")
    
    with col2:
        st.altair_chart(plot_top10_sites_by_downtime_altair(df_selected, selected_period), width="stretch")
        
    with col3:
        st.dataframe(build_downtime_table(df_selected))

with st.container():
    cols = st.columns([1, 1])
    col1 = cols[0].container(
        border=True, height="stretch", vertical_alignment="center"
        )
    col2 = cols[1].container(
        border=True, height="stretch", vertical_alignment="center"
        )
    
    with col1:
        st.altair_chart(plot_repeated_sites_comparison(df_clean, selected_period, previous_period), width="stretch")
    with col2:
        st.altair_chart(plot_top_repeated_sites_bar(df_selected, selected_period), width="stretch")
