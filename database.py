import sqlite3
import datetime
from typing import Optional, Dict, List, Any
import json

DB_NAME = "bug_tracker.db"

def init_db():
    """Initializes the SQLite database and creates the logs table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_hash TEXT UNIQUE NOT NULL,
            filename TEXT NOT NULL,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_size_bytes INTEGER,
            analysis_json TEXT,
            severity TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def get_log_by_hash(file_hash: str) -> Optional[Dict[str, Any]]:
    """Retrieves a log entry by its hash."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM logs WHERE file_hash = ?', (file_hash,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        return dict(row)
    return None

def insert_log(file_hash: str, filename: str, file_size: int, analysis: Dict[str, Any], severity: str):
    """Inserts a new log entry into the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    analysis_json = json.dumps(analysis)
    
    try:
        cursor.execute('''
            INSERT INTO logs (file_hash, filename, file_size_bytes, analysis_json, severity)
            VALUES (?, ?, ?, ?, ?)
        ''', (file_hash, filename, file_size, analysis_json, severity))
        conn.commit()
    except sqlite3.IntegrityError:
        # Should be handled by checking get_log_by_hash first, but safe guard here
        pass
    finally:
        conn.close()

def get_all_logs() -> List[Dict[str, Any]]:
    """Retrieves all logs ordered by upload time descending."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM logs ORDER BY upload_time DESC')
    rows = cursor.fetchall()
    
    conn.close()
    return [dict(row) for row in rows]
