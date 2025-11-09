import streamlit as st
from utils.data_loader import load_excel
from utils.data_cleaner import clean_tt_data

st.set_page_config(page_title="Excel Streamlit Demo", layout="wide")

st.title("📊 Streamlit Excel Dashboard")

# Load data
df_raw = load_excel()
df_clean = clean_tt_data(df_raw)

# Show preview
st.subheader("Data Preview")
st.dataframe(df_clean.head())
st.dataframe(df_clean[["start_date", "end_date", "duration_minutes"]].head())

# Example chart
st.subheader("Quick Visualization")
st.bar_chart(df_clean.select_dtypes(include="number"))