import sqlite3
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def init_db():
    """Initializes the database with necessary tables."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            day_folder TEXT NOT NULL,
            upload_status TEXT NOT NULL, -- PENDING, UPLOADED, FAILED
            upload_time TIMESTAMP,
            youtube_id TEXT,
            error_message TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {config.DB_PATH}")

def get_connection():
    return sqlite3.connect(config.DB_PATH)

def log_upload(filename, day_folder, status, youtube_id=None, error=None):
    """Logs an upload attempt."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO uploads (filename, day_folder, upload_status, upload_time, youtube_id, error_message)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (filename, day_folder, status, datetime.now(), youtube_id, error))
    conn.commit()
    conn.close()

def get_uploads_today_count():
    """Returns number of successful uploads today."""
    conn = get_connection()
    cursor = conn.cursor()
    # Check for uploads where upload_time is today and status is UPLOADED
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    cursor.execute('''
        SELECT COUNT(*) FROM uploads 
        WHERE upload_status = 'UPLOADED' 
        AND upload_time >= ?
    ''', (today_start,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def is_video_uploaded(filename):
    """Checks if a specific file has already been uploaded."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) FROM uploads 
        WHERE filename = ? AND upload_status = 'UPLOADED'
    ''', (filename,))
    exists = cursor.fetchone()[0] > 0
    conn.close()
    return exists

if __name__ == "__main__":
    init_db()
