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
            insta_id TEXT,
            insta_status TEXT,
            error_message TEXT
        )
    ''')
    
    # Simple migration for existing DB
    try:
        cursor.execute("ALTER TABLE uploads ADD COLUMN insta_id TEXT")
        cursor.execute("ALTER TABLE uploads ADD COLUMN insta_status TEXT")
    except:
        pass
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {config.DB_PATH}")

def get_connection():
    return sqlite3.connect(config.DB_PATH)

def log_upload(filename, day_folder, yt_status, yt_id=None, insta_status=None, insta_id=None, error=None):
    """Logs upload attempts for both YouTube and Instagram."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO uploads (filename, day_folder, upload_status, upload_time, youtube_id, insta_status, insta_id, error_message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (filename, day_folder, yt_status, datetime.now(), yt_id, insta_status, insta_id, error))
    conn.commit()
    conn.close()

def get_uploads_today_count():
    """Returns number of successful uploads today (checking YouTube as primary indicator)."""
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
