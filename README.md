# Lightweight Automated Streamlit Outage Analysis Dashboard

A lightweight, automated pipeline for tracking site outages and generating monthly downtime reports.
Designed to ingest vendor email notifications, parse unstructured data, and visualize network availability metrics via Streamlit

Repository files:
- `app.py`: Main dashboard interface.
- `outage_processor.py`: Backend batch script that parses raw email text into structured data.
- `outage_reporter.py`: Headless script for generating PDF reports via Task Scheduler.
- `outage_master.db`: SQLite database storing the incident history (auto-generated).
- `requirements.txt`: Project dependencies.
- `utils/`: Helper modules for data loading, cleaning, and graphing.

## Architecture
This tool implements a **Hybrid Automation Architecture**:
1.  **Ingestion:** Automation flow saves raw vendor notifications to a local `Input` directory.
2.  **Processing:** `outage_processor.py` scans for new files, applies Regex extraction, and upserts data into `outage_master.db`.
3.  **Visualization:** Streamlit reads the local database to display live outage statistics.

## Setup & Configuration
1.  **Database Path:** Configure the `DB_PATH` variable in `app.py` and `outage_processor.py` to point to your shared data directory.
2.  **Regex Patterns:** If adapting for a new vendor, update the regex logic in `outage_processor.py` -> `parse_incident_email()`.

Quick overview
- Two Streamlit apps:
  - [app.py](app.py) — main dashboard using Altair charts and tables.
  - [streamlit_app.py](streamlit_app.py) — alternate version using Matplotlib charts.
- Data pipeline helpers:
  - Data loader: [`utils.data_loader.load_excel`](utils/data_loader.py)
  - Cleaning: [`utils.data_cleaner.clean_tt_data`](utils/data_cleaner.py)
  - Month selection: [`utils.month_filter.get_month_filters`](utils/month_filter.py)
- Visualization helpers:
  - Matplotlib-based: [`utils.graph.plot_top10_sites_by_downtime`](utils/graph.py), [`utils.graph.build_downtime_table`](utils/graph.py), [`utils.graph.plot_top_repeated_sites`](utils/graph.py)
  - Altair-based: [`utils.graph_altair.plot_top10_sites_by_downtime_altair`](utils/graph_altair.py), [`utils.graph_altair.build_downtime_table`](utils/graph_altair.py), [`utils.graph_altair.plot_top_repeated_sites_bar`](utils/graph_altair.py), [`utils.graph_altair.plot_repeated_sites_comparison`](utils/graph_altair.py)

Requirements
- See [requirements.txt](requirements.txt)
  - streamlit
  - pandas
  - openpyxl (Excel)
  - altair

How it expects your data
- Default Excel file: source/sourcefile.xlsx (loaded by [`utils.data_loader.load_excel`](utils/data_loader.py))
- Data is cleaned and normalized by [`utils.data_cleaner.clean_tt_data`](utils/data_cleaner.py). The cleaner will:
  - normalizes column names (lowercase + underscores),
  - converts start/end dates to datetimes,
  - computes durations (minutes/hours/days),
  - attaches month fields (period, string, name, month_year).

Run (local)
1. Create venv and install deps:
```bash
python -m venv venv

# On Windows
venv/Scripts/activate

# On macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```
2. Initialize the database by running the processor once:
```bash
python outage_processor.py
```
3. Launch dashboard

- Altair dashboard
```bash
streamlit run app.py
```

### Configuration & theme

Streamlit theme is configured in ```.streamlit/config.toml.```

### Notes

- The loader function ```utils.data_loader.load_excel``` looks in the ```source/``` directory, add the Excel source file there.
- Month fields are pandas Period objects — filters use ```utils.month_filter.get_month_filters```