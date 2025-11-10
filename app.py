import streamlit as st
from utils.data_loader import load_excel
from utils.data_cleaner import clean_tt_data
from utils.month_filter import get_month_filters

st.set_page_config(page_title="Excel Streamlit Demo", layout="wide")

st.title("📊 Streamlit Excel Dashboard")

# Load data
df_raw = load_excel()
df_clean = clean_tt_data(df_raw)
df_clean = df_clean.dropna(subset=["end_date"])

filters = get_month_filters(df_clean)

# Filter for current month
df_current = df_clean[df_clean["month"] == filters["current"]]

# Filter for last full month
df_last = df_clean[df_clean["month"] == filters["last"]]

# Comparison: current vs last
df_compare = df_clean[df_clean["month"].isin([filters["current"], filters["last"]])]

# Show preview
st.subheader("Data Preview")
st.dataframe(df_clean.head())

# Example chart
st.subheader("Quick Visualization")
st.bar_chart(df_clean.select_dtypes(include="number"))