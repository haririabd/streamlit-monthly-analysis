import sqlite3
import pandas as pd
import os
import datetime
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = os.getenv("BASE_DIR")
DB_NAME = os.getenv("DB_NAME", "outage_master.db")

if not BASE_DIR:
    st.error("Configuration Error: BASE_DIR not set in .env file")
    st.stop()

DB_PATH = os.path.join(BASE_DIR, DB_NAME)
EXCEL_PATH = r"" # Update this!

# COLUMN MAPPING
# Key = Your DB Column Name (Keep these as is)
# Value = Your Excel Header Name (Change these to match your Excel file)
COL_MAP = {
    'site_id': 'Site ID',          # e.g. 'Site_ID' or 'SiteName'
    'start_time': 'Time Down',     # e.g. 'Incident Start'
    'end_time': 'Time Up'          # e.g. 'Incident End'
}

def format_date_for_db(dt_obj):
    """
    Converts Excel Timestamp to the specific string format used by your Email Parser.
    Format: YYYYMMDD HH:MM:SS (e.g., 20251229 16:00:00)
    """
    if pd.isnull(dt_obj):
        return None
    try:
        # Ensure it's a datetime object
        dt_obj = pd.to_datetime(dt_obj)
        return dt_obj.strftime("%Y%m%d %H:%M:%S")
    except:
        return None

def migrate_data():
    if not os.path.exists(EXCEL_PATH):
        print(f"Error: Excel file not found at {EXCEL_PATH}")
        return

    print("Reading Excel file...")
    df = pd.read_excel(EXCEL_PATH)
    
    # 1. Rename columns to generic names
    df = df.rename(columns={
        COL_MAP['site_id']: 'site_id',
        COL_MAP['start_time']: 'start_time',
        COL_MAP['end_time']: 'end_time'
    })

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Ensure table exists (in case you run this before the processor)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS downtime_logs (
            site_id TEXT,
            incident_time TEXT,
            resolve_time TEXT,
            status TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (site_id, incident_time)
        )
    ''')

    count_inserted = 0
    count_skipped = 0

    print("Starting migration...")
    
    for index, row in df.iterrows():
        site_id = str(row['site_id']).strip()
        
        # Convert Dates
        incident_time = format_date_for_db(row['start_time'])
        resolve_time = format_date_for_db(row['end_time'])
        
        # Skip bad rows
        if not incident_time or site_id == 'nan':
            count_skipped += 1
            continue

        # Determine Status
        status = "UP" if resolve_time else "DOWN"

        # SQL Injection Safe Insert
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO downtime_logs (site_id, incident_time, resolve_time, status)
                VALUES (?, ?, ?, ?)
            ''', (site_id, incident_time, resolve_time, status))
            count_inserted += 1
        except Exception as e:
            print(f"Error on row {index}: {e}")

    conn.commit()
    conn.close()
    
    print("--- Migration Complete ---")
    print(f"Successfully Migrated: {count_inserted} rows")
    print(f"Skipped (Invalid Data): {count_skipped} rows")

if __name__ == "__main__":
    migrate_data()