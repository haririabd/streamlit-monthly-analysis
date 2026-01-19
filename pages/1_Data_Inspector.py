import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
from utils.data_loader import load_data
from utils.data_cleaner import clean_db_data

load_dotenv()
BASE_DIR = os.getenv("BASE_DIR")
DB_NAME = os.getenv("DB_NAME", "outage_master.db")

if not BASE_DIR:
    st.error("Configuration Error: BASE_DIR not set in .env file")
    st.stop()

DB_PATH = os.path.join(BASE_DIR, DB_NAME)

st.set_page_config(
    page_title="Data Inspector",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Database Inspector")
st.markdown("Use this page to verify if your **Regex** is extracting data correctly from the emails.")

# --- LOAD DATA ---
if os.path.exists(DB_PATH):
    df_raw = load_data()
else:
    st.warning(f"Database not found at {DB_PATH}")
    st.stop()

# --- METRICS ---
col1, col2, col3 = st.columns(3)
col1.metric("Total Records", len(df_raw))
col2.metric("Active Outages (DOWN)", len(df_raw[df_raw['status'] == 'DOWN']))
col3.metric("Resolved Outages (UP)", len(df_raw[df_raw['status'] == 'UP']))

st.divider()

# --- TABS FOR VERIFICATION ---
tab1, tab2 = st.tabs(["📊 Processed Data (Clean)", "🧬 Raw DB Data (Regex Check)"])

with tab1:
    st.info("This is the data **after** types are converted and durations are calculated.")
    
    if not df_raw.empty:
        # Apply the cleaner to a copy so we don't mess up the raw view
        df_clean = clean_db_data(df_raw.copy())
        
        # Search Filter
        search_term = st.text_input("Filter by Site ID:", "")
        if search_term:
            df_clean = df_clean[df_clean['siteid'].str.contains(search_term, case=False, na=False)]

        st.dataframe(
            df_clean, 
            width="stretch",
            height=600,
            column_config={
                "start_date": st.column_config.DatetimeColumn(format="D MMM YYYY, HH:mm"),
                "end_date": st.column_config.DatetimeColumn(format="D MMM YYYY, HH:mm"),
                "duration_hours": st.column_config.NumberColumn(format="%.2f hrs"),
            }
        )
    else:
        st.write("No data available.")

with tab2:
    st.warning("⚠️ This view shows exactly what is inside SQLite. If columns are `None`, your Regex failed.")
    
    st.markdown("""
    **Verification Checklist:**
    - **incident_time**: Is the format strictly `YYYYMMDD HH:MM:SS`?
    - **site_id**: Are there any extra spaces or hidden characters?
    - **status**: Is it correctly correctly marked UP/DOWN?
    """)
    
    # Highlight potential Regex errors (Rows with missing critical data)
    if not df_raw.empty:
        error_rows = df_raw[df_raw['site_id'].isnull() | df_raw['incident_time'].isnull()]
        
        if not error_rows.empty:
            st.error(f"Found {len(error_rows)} rows with extraction errors!")
            st.dataframe(error_rows)
        
        st.subheader("All Raw Records")
        st.dataframe(df_raw, use_container_width=True)