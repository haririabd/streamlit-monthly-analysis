import os
import shutil
import re
import sqlite3
import datetime
import subprocess
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

BASE_DIR = os.getenv("BASE_DIR")
DB_NAME = os.getenv("DB_NAME", "outage_master.db") # Default
LOG_NAME = os.getenv("LOG_NAME", "process_audit.log")

if not BASE_DIR:
    raise ValueError("BASE_DIR not found. Check your .env file.")

INPUT_FOLDER = os.path.join(BASE_DIR, "Input")
ARCHIVE_FOLDER = os.path.join(BASE_DIR, "Archive")
DB_FILE = os.path.join(BASE_DIR, DB_NAME)
LOG_FILE = os.path.join(BASE_DIR, LOG_NAME)

# Ensure folders exist
os.makedirs(ARCHIVE_FOLDER, exist_ok=True)

def log_message(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}"
    print(entry)
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")

def free_up_space(filepath):
    try:
        # Remove local fie
        subprocess.run(['attrib', '+U', '-P', filepath], check=True, shell=True)
        return True
    except Exception as e:
        log_message(f"WARNING: Could not free up space for {filepath}: {e}")
        return False

def parse_incident_email(text):
    data = {}
    
    # For Site ID
    site_match = re.search(r'SiteID\s*-\s*([A-Z0-9_]+)', text)
    data['site_id'] = site_match.group(1).strip() if site_match else None

    # Incident Time
    start_match = re.search(r'Incident Time\s*[–-]\s*(\d{8}\s+\d{2}:\d{2}:\d{2})', text)
    data['incident_time'] = start_match.group(1).strip() if start_match else None

    # Resolve Time
    end_match = re.search(r'Resolve Time\s*[–-]\s*(\d{8}\s+\d{2}:\d{2}:\d{2})', text)
    data['resolve_time'] = end_match.group(1).strip() if end_match else None

    return data

def update_database(data):
    if not data['site_id'] or not data['incident_time']:
        log_message(f"SKIPPED: Missing SiteID or Time in email.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
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

    cursor.execute('SELECT * FROM downtime_logs WHERE site_id=? AND incident_time=?', 
                   (data['site_id'], data['incident_time']))
    existing = cursor.fetchone()

    status = "UP" if data['resolve_time'] else "DOWN"

    if existing:
        if data['resolve_time']:
            cursor.execute('''
                UPDATE downtime_logs 
                SET resolve_time = ?, status = 'UP', updated_at = CURRENT_TIMESTAMP
                WHERE site_id = ? AND incident_time = ?
            ''', (data['resolve_time'], data['site_id'], data['incident_time']))
            log_message(f"UPDATED: {data['site_id']} is now UP.")
    else:
        cursor.execute('''
            INSERT INTO downtime_logs (site_id, incident_time, resolve_time, status)
            VALUES (?, ?, ?, ?)
        ''', (data['site_id'], data['incident_time'], data['resolve_time'], status))
        log_message(f"INSERTED: {data['site_id']} status {status}.")

    conn.commit()
    conn.close()

def process_batch():
    log_message("--- Batch Run Started ---")
    
    files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".txt")]
    
    if not files:
        log_message("No new files found.")
        return

    for filename in files:
        src_path = os.path.join(INPUT_FOLDER, filename)
        
        try:
            with open(src_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # parse & save data
            cleaned_data = parse_incident_email(content)
            update_database(cleaned_data)
            
            # once processed, move file to archive
            dst_path = os.path.join(ARCHIVE_FOLDER, filename)
            
            # Handle duplicates
            if os.path.exists(dst_path):
                timestamp = int(datetime.datetime.now().timestamp())
                dst_path = os.path.join(ARCHIVE_FOLDER, f"{timestamp}_{filename}")
                
            shutil.move(src_path, dst_path)
            free_up_space(dst_path)

        except Exception as e:
            log_message(f"ERROR processing {filename}: {e}")

if __name__ == "__main__":
    process_batch()