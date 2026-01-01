import pandas as pd
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
BASE_DIR = os.getenv("BASE_DIR", ".")
DB_NAME = os.getenv("DB_NAME", "outage_master.db")
DATA_SOURCE = os.getenv("DATA_SOURCE", "db").lower().strip()
EXCEL_FILENAME = os.getenv("EXCEL_FILENAME", "sourcefile.xlsx")

# Define DB path
if BASE_DIR:
    DB_PATH = os.path.join(BASE_DIR, DB_NAME)
else:
    DB_PATH = None

# Define Excel Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_PATH = os.path.join(PROJECT_ROOT, "sample_source", EXCEL_FILENAME)
EXCEL_PATH_LOCAL = os.path.join(PROJECT_ROOT, "source", EXCEL_FILENAME)
EXCEL_PATH_CLOUD = os.path.join(BASE_DIR, "source", EXCEL_FILENAME) if BASE_DIR else None

# Column Mapping
COL_MAP = {
    "SiteID": "site_id",
    "Start Date": "incident_time", 
    "End Date": "resolve_time"
}

def load_data() -> pd.DataFrame:
    print(f"🔄 Data Source Selected: {DATA_SOURCE.upper()}")

    if DATA_SOURCE in ["sample", "excel"]:
        target_path = None
        
        # 1. Determine Preferred Path
        if DATA_SOURCE == "sample":
            target_path = SAMPLE_PATH
        else:
            target_path = EXCEL_PATH_LOCAL
            
        # 2. Check if Preferred Path Exists
        if not os.path.exists(target_path):
            print(f"⚠️ File not found at {target_path}, checking cloud path...")
            
            # 3. Try Fallback (Cloud Path)
            if EXCEL_PATH_CLOUD and os.path.exists(EXCEL_PATH_CLOUD):
                target_path = EXCEL_PATH_CLOUD
            else:
                # 4. If both fail, RAISE ERROR
                raise FileNotFoundError(
                    f"❌ Could not find valid Excel file for mode '{DATA_SOURCE}'.\n"
                    f"Checked Local: {EXCEL_PATH_LOCAL}\n"
                    f"Checked Cloud: {EXCEL_PATH_CLOUD}"
                )

        print(f"📂 Loading file: {target_path}")
        return _load_from_excel(target_path)

    elif DATA_SOURCE == 'db':
        return _load_from_db()
    else:
        raise ValueError(f"Unknown DATA_SOURCE: {DATA_SOURCE}")

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

def _load_from_excel(path_to_use: str) -> pd.DataFrame:
    try:
        # 1. Try reading as Excel first (Standard for your Source Data)
        try:
            df = pd.read_excel(path_to_use)
        except Exception:
            print(f"⚠️ read_excel failed. Trying read_csv for: {path_to_use}")
            df = pd.read_csv(path_to_use)
        
        # 2. Normalize Headers
        rename_map = {k: v for k, v in COL_MAP.items() if k in df.columns}
        df = df.rename(columns=rename_map)
        
        # 3. Validation
        required = ['site_id', 'incident_time', 'resolve_time']
        missing = [col for col in required if col not in df.columns]
        if missing:
             raise ValueError(f"File missing required columns: {missing}")
             
        return df
    except Exception as e:
        raise Exception(f"Error reading File: {e}")