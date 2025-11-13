import pandas as pd
from datetime import datetime

def get_month_filters(df: pd.DataFrame):
    today = pd.Timestamp.today().normalize()
    current_month = today.to_period("M")
    last_month = (today.replace(day=1) - pd.Timedelta(days=1)).to_period("M")
    prev_month = (today.replace(day=1) - pd.DateOffset(months=2)).to_period("M")

    return {
        "current": current_month,
        "last": last_month,
        "previous": prev_month
    }


