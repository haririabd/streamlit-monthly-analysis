import streamlit as st
from utils.data_loader import load_excel

st.set_page_config(page_title="Excel Streamlit Demo", layout="wide")

st.title("📊 Streamlit Excel Dashboard")

# Load data
df = load_excel()

# Show preview
st.subheader("Data Preview")
st.dataframe(df.head())

# Example chart
st.subheader("Quick Visualization")
st.bar_chart(df.select_dtypes(include="number"))