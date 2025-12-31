import os
import pandas as pd
import datetime
from fpdf import FPDF
from dotenv import load_dotenv

# Import the shared loader
from utils.data_loader import load_data 

# --- CONFIGURATION ---
load_dotenv()
BASE_DIR = os.getenv("BASE_DIR")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "Output")
DATA_SOURCE = os.getenv("DATA_SOURCE", "db").upper()

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Monthly Network Outage Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_monthly_report():
    today = datetime.date.today()
    # Calculate previous month
    first_of_this_month = today.replace(day=1)
    last_month_end = first_of_this_month - datetime.timedelta(days=1)
    target_month_str = last_month_end.strftime("%Y-%m")
    
    # target_month_str = "2024-12" # Uncomment to force test specific month

    print(f"📊 Generating report for: {target_month_str} (Source: {DATA_SOURCE})")

    # --- THE CLEAN LOAD ---
    try:
        df = load_data() # Uses utils/data_loader.py logic
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        return
    # ----------------------

    if df.empty:
        print("⚠️ Data loaded but empty.")
        return

    # Clean Dates
    df['end_date'] = pd.to_datetime(df['resolve_time'], errors='coerce')
    df['start_date'] = pd.to_datetime(df['incident_time'], errors='coerce')
    
    # Filter for Month
    df['Month'] = df['end_date'].dt.strftime('%Y-%m')
    report_df = df[df['Month'] == target_month_str].copy()

    if report_df.empty:
        print(f"ℹ️ No resolved incidents found for {target_month_str}.")
        return

    # Calculations
    report_df['duration_hours'] = (report_df['end_date'] - report_df['start_date']).dt.total_seconds() / 3600
    report_df['duration_hours'] = report_df['duration_hours'].round(2)
    report_df = report_df.sort_values(by='duration_hours', ascending=False)

    # Generate PDF
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # Metrics
    total_incidents = len(report_df)
    total_downtime = report_df['duration_hours'].sum()
    avg_downtime = report_df['duration_hours'].mean()

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 8, f"Reporting Period: {target_month_str}", 0, 1)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 6, f"Source: {DATA_SOURCE}", 0, 1)
    pdf.cell(0, 6, f"Total Incidents: {total_incidents}", 0, 1)
    pdf.cell(0, 6, f"Total Downtime: {total_downtime:.2f} hrs", 0, 1)
    pdf.ln(10)

    # Table
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(40, 8, "Site ID", 1)
    pdf.cell(45, 8, "Incident Start", 1)
    pdf.cell(45, 8, "Resolved At", 1)
    pdf.cell(30, 8, "Duration (H)", 1)
    pdf.ln()

    pdf.set_font("Arial", size=8)
    for _, row in report_df.iterrows():
        site_id = str(row.get('site_id', 'Unknown'))[:20]
        start = str(row['start_date'])[:19]
        end = str(row['end_date'])[:19]
        dur = f"{row['duration_hours']:.2f}"
        
        pdf.cell(40, 7, site_id, 1)
        pdf.cell(45, 7, start, 1)
        pdf.cell(45, 7, end, 1)
        pdf.cell(30, 7, dur, 1)
        pdf.ln()

    filename = f"Monthly_Outage_Report_{target_month_str}.pdf"
    output_path = os.path.join(OUTPUT_FOLDER, filename)
    pdf.output(output_path)
    print(f"✅ SUCCESS: Report generated at {output_path}")

if __name__ == "__main__":
    generate_monthly_report()