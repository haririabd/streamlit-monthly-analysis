import streamlit as st
import pandas as pd
from datetime import datetime
from utils.data_loader import load_excel
from utils.data_cleaner import clean_tt_data
from utils.month_filter import get_month_filters
from utils.graph import plot_top10_sites_by_downtime

st.set_page_config(page_title="Excel Streamlit Demo", layout="wide")
st.title("📊 Streamlit Excel Dashboard")

current_month_name = datetime.now().strftime("%B %Y")  # e.g., "November"

# Load data
df_raw = load_excel()
df_clean = clean_tt_data(df_raw)
df_clean = df_clean.dropna(subset=["end_date"])

# Get unique month options from the data
month_options = sorted(df_clean["month"].dropna().unique(), reverse=True)
selected_period = st.selectbox("Select a month to view:", month_options)
df_selected = df_clean[df_clean["month"] == selected_period]

today = datetime.today()
current_period = pd.Period(today, freq="M")
last_period = current_period - 1

if selected_period == current_period:
    selected_label = "Current Month"
elif selected_period == last_period:
    selected_label = "Last Month"
else:
    selected_label = selected_period.strftime("%B %Y")

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
# st.subheader(f"Current Month View: {current_month_name}")
# col1, col2 = st.columns(2)
# with col1:
#     st.pyplot(plot_top10_sites_by_downtime(df_current))
# with col2:
#     pass
with st.container():
    col1, col2 = st.columns([2, 1])  # wider chart, narrower table

    with col1:
        st.subheader(f"Top 10 Highest Downtime for {selected_label}")
        st.pyplot(plot_top10_sites_by_downtime(df_selected))

    with col2:
        st.subheader("Downtime Table")
        # st.dataframe(build_downtime_table(df_selected))  # custom function

# with st.container():
#     col1, col2 = st.columns(2)

#     with col1:
#         st.subheader("Top 5 Repeated Sites by Month")
#         st.pyplot(plot_repeated_sites_comparison(df_current, df_last))

#     with col2:
#         st.subheader(f"Top 5 Most Repeated Sites for {selected_label}")
#         st.pyplot(plot_top_repeated_sites(df_selected))

