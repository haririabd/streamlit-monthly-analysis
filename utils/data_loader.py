import pandas as pd
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.getenv("BASE_DIR")
DB_NAME = os.getenv("DB_NAME", "outage_master.db")
DATA_SOURCE = os.getenv("DATA_SOURCE", "db").lower()
EXCEL_FILENAME = os.getenv("EXCEL_FILENAME", "sourcefile.xlsx")

# Define path
if BASE_DIR:
    DB_PATH = os.path.join(BASE_DIR, DB_NAME)
else:
    DB_PATH = None

# Get the project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCEL_PATH_LOCAL = os.path.join(PROJECT_ROOT, "source", EXCEL_FILENAME)
EXCEL_PATH_CLOUD = os.path.join(BASE_DIR, "source", EXCEL_FILENAME) if BASE_DIR else None

# Excel Mapping (Moved here so it's shared)
COL_MAP = {
    "SiteID": "site_id",
    "Start Date": "incident_time", 
    "End Date": "resolve_time"
}

def load_data() -> pd.DataFrame:
    if DATA_SOURCE == 'excel':
        return _load_from_excel()
    else:
        return _load_from_db()

def _load_from_db() -> pd.DataFrame:
    if not DB_PATH or not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at: {DB_PATH}")

    try:
        conn = sqlite3.connect(DB_PATH)
        query = "SELECT * FROM downtime_logs"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        raise Exception(f"Error reading Database: {e}")

def _load_from_excel() -> pd.DataFrame:
    # Try Local source/ first, then Cloud source/
    path_to_use = EXCEL_PATH_LOCAL
    if not os.path.exists(path_to_use):
        if EXCEL_PATH_CLOUD and os.path.exists(EXCEL_PATH_CLOUD):
            path_to_use = EXCEL_PATH_CLOUD
        else:
            raise FileNotFoundError(f"Excel file not found at local ({EXCEL_PATH_LOCAL}) or cloud ({EXCEL_PATH_CLOUD})")

    try:
        df = pd.read_excel(path_to_use)
        
        # Normalize Headers
        rename_map = {k: v for k, v in COL_MAP.items() if k in df.columns}
        df = df.rename(columns=rename_map)
        
        # Validation
        required = ['site_id', 'incident_time', 'resolve_time']
        missing = [col for col in required if col not in df.columns]
        if missing:
             raise ValueError(f"Excel missing required columns: {missing}")
             
        return df
    except Exception as e:
        raise Exception(f"Error reading Excel: {e}")