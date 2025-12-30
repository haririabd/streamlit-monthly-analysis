import os
import sqlite3
import pandas as pd
import datetime
from fpdf import FPDF
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()

BASE_DIR = os.getenv("BASE_DIR")
DB_NAME = os.getenv("DB_NAME", "outage_master.db")

if not BASE_DIR:
    raise ValueError("BASE_DIR not set in .env file")

DB_PATH = os.path.join(BASE_DIR, DB_NAME)
OUTPUT_FOLDER = os.path.join(BASE_DIR, "Output")

# Ensure Output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

class PDF(FPDF):
    def header(self):
        # Logo could go here
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Monthly Network Outage Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_monthly_report():
    # 1. Determine "Last Month"
    # If today is Jan 1st, we want the report for December.
    today = datetime.date.today()
    first_of_this_month = today.replace(day=1)
    last_month_end = first_of_this_month - datetime.timedelta(days=1)
    target_month_str = last_month_end.strftime("%Y-%m") # e.g. "2024-12"
    
    print(f"Generating report for period: {target_month_str}")

    # 2. Connect to DB
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM downtime_logs"
    df = pd.read_sql(query, conn)
    conn.close()

    if df.empty:
        print("Database is empty.")
        return

    # 3. Clean & Filter Data
    # Convert dates
    df['end_date'] = pd.to_datetime(df['resolve_time'], format='%Y%m%d %H:%M:%S', errors='coerce')
    df['start_date'] = pd.to_datetime(df['incident_time'], format='%Y%m%d %H:%M:%S', errors='coerce')
    
    # Filter: Only include incidents RESOLVED in the target month
    df['Month'] = df['end_date'].dt.strftime('%Y-%m')
    report_df = df[df['Month'] == target_month_str].copy()

    if report_df.empty:
        print(f"No resolved incidents found for {target_month_str}. No PDF generated.")
        return

    # Calculate Duration
    report_df['duration_hours'] = (report_df['end_date'] - report_df['start_date']).dt.total_seconds() / 3600
    report_df['duration_hours'] = report_df['duration_hours'].round(2)

    # Sort by longest duration
    report_df = report_df.sort_values(by='duration_hours', ascending=False)

    # 4. Generate PDF
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # Summary Metrics
    total_incidents = len(report_df)
    total_downtime = report_df['duration_hours'].sum()
    avg_downtime = report_df['duration_hours'].mean()

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 8, f"Reporting Period: {target_month_str}", 0, 1)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 6, f"Total Incidents Resolved: {total_incidents}", 0, 1)
    pdf.cell(0, 6, f"Total Downtime Hours: {total_downtime:.2f} hrs", 0, 1)
    pdf.cell(0, 6, f"Average Restoration Time: {avg_downtime:.2f} hrs", 0, 1)
    pdf.ln(10)

    # Table Header
    pdf.set_font("Arial", 'B', 9)
    # Adjust column widths: SiteID(40), Start(45), End(45), Dur(20), Status(20)
    pdf.cell(40, 8, "Site ID", 1)
    pdf.cell(45, 8, "Incident Start", 1)
    pdf.cell(45, 8, "Resolved At", 1)
    pdf.cell(30, 8, "Duration (Hrs)", 1)
    pdf.ln()

    # Table Rows
    pdf.set_font("Arial", size=8)
    for index, row in report_df.iterrows():
        # Truncate strings if needed
        site_id = str(row['site_id'])[:20]
        start = str(row['start_date'])
        end = str(row['end_date'])
        dur = f"{row['duration_hours']:.2f}"
        
        pdf.cell(40, 7, site_id, 1)
        pdf.cell(45, 7, start, 1)
        pdf.cell(45, 7, end, 1)
        pdf.cell(30, 7, dur, 1)
        pdf.ln()

    # 5. Save Output
    filename = f"Monthly_Outage_Report_{target_month_str}.pdf"
    output_path = os.path.join(OUTPUT_FOLDER, filename)
    pdf.output(output_path)
    
    print(f"SUCCESS: Report generated at {output_path}")

if __name__ == "__main__":
    generate_monthly_report()