import pandas as pd
from pathlib import Path

def load_excel(file_name: str = "DNB_Raw TT Data.xlsx") -> pd.DataFrame:
    """Load Excel file from source/ folder."""
    file_path = Path(__file__).resolve().parent.parent / "source" / file_name
    df = pd.read_excel(file_path, engine="openpyxl")
    return df