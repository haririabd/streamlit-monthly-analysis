import pandas as pd

def clean_tt_data(df: pd.DataFrame) -> pd.DataFrame:
    # Standardize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Convert Start Date and End Date to datetime
    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
    df["end_date"] = pd.to_datetime(df["end_date"], errors="coerce")

    # Calculate duration in minutes
    df["duration_minutes"] = (df["end_date"] - df["start_date"]).dt.total_seconds() / 60

    # Optional: round duration
    df["duration_minutes"] = df["duration_minutes"].round(2)

    return df