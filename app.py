import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from utils.data_loader import load_excel
from utils.data_cleaner import clean_tt_data
from utils.month_filter import get_month_filters

st.set_page_config(
    page_title="5G Outage Analysis Dashboard",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)

"""
# :material/query_stats: 5G Monthly Outage Analysis

Based on https://github.com/streamlit/demo-stockpeers/
"""

""  # Add some space.

# Load Data
df_raw = load_excel()
df_clean = clean_tt_data(df_raw)
df_clean = df_clean.dropna(subset=["end_date"])

today = datetime.today()
current_period = pd.Period(today, freq="M")
last_period = current_period - 1
current_month_name = datetime.now().strftime("%B %Y")  # e.g., "November"
    
# Filtering data set based on user's month selection
filters = get_month_filters(df_clean)
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
        border=True, height="stretch", vertical_alignment="center"
        )
    
    with col1:
        # Frontend Month Selection
        month_options = sorted(df_clean["month"].dropna().unique(), reverse=True)
        selected_period = st.selectbox("Select a month to view:", month_options)
        df_selected = df_clean[df_clean["month"] == selected_period]
        
        if selected_period == current_period:
            selected_label = "Current Month"
        elif selected_period == last_period:
            selected_label = "Last Month"
        else:
            selected_label = selected_period.strftime("%B %Y")
    
    with col2:
        st.dataframe(df_clean.head())
