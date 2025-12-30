import pandas as pd
import numpy as np

def clean_tt_data(df: pd.DataFrame) -> pd.DataFrame:
    # Standardize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Convert Start Date and End Date to datetime
    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
    df["end_date"] = pd.to_datetime(df["end_date"], errors="coerce")

    # Calculate duration in minutes and hours
    df["duration_minutes"] = (df["end_date"] - df["start_date"]).dt.total_seconds() / 60
    df["duration_hours"] = (df["duration_minutes"] / 60)
    df["duration_days"] = (df["duration_hours"] / 24).round(2)

    # Optional: round duration
    df["duration_minutes"] = df["duration_minutes"].round(2)

    # Tag with month info (based on end_date)
    df["month"] = df["end_date"].dt.to_period("M")
    df["month_str"] = df["month"].astype(str).fillna("Unresolved")
    df["month_name"] = df["end_date"].dt.strftime("%B")
    df["month_year"] = df["end_date"].dt.strftime("%b %Y")

    return df

def clean_db_data(df: pd.DataFrame) -> pd.DataFrame:
    # Clean raw data from DB
    if df.empty:
        return df

    # Match column name
    # DB has 'site_id', graphs expect 'siteid'. I'm lazy to change all of them
    df = df.rename(columns={
        "site_id": "siteid",
        "incident_time": "start_date",
        "resolve_time": "end_date"
    })

    # Date in DB is in string. convert to datetime format
    df["start_date"] = pd.to_datetime(df["start_date"], format="%Y%m%d %H:%M:%S", errors="coerce")
    df["end_date"] = pd.to_datetime(df["end_date"], format="%Y%m%d %H:%M:%S", errors="coerce")

    # Get duration if end_date exist
    df["duration_minutes"] = (df["end_date"] - df["start_date"]).dt.total_seconds() / 60
    df["duration_hours"] = df["duration_minutes"] / 60
    df["duration_days"] = (df["duration_hours"] / 24).round(2)

    # 4. Month tagging
    df["month"] = df["end_date"].dt.to_period("M")
    df["month_str"] = df["month"].astype(str)
    df["month_name"] = df["start_date"].dt.strftime("%B")
    df["month_year"] = df["start_date"].dt.strftime("%b %Y")

    if 'status' not in df.columns:
        df['status'] = np.where(df['end_date'].isna(), 'DOWN', 'UP')
        
    return df