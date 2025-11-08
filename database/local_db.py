import sqlite3
import os

LOCAL_DB_PATH = os.path.join(os.getcwd(), "local_cache.db")

def get_local_connection():
    conn = sqlite3.connect(LOCAL_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_local_db():
    """Create local SQLite tables if not exist."""
    conn = get_local_connection()
    cursor = conn.cursor()
    cursor.execute("""
-- This is the required schema for the local SQLite table:
        CREATE TABLE IF NOT EXISTS pending_membership_payments (
            member_id INTEGER,
            months TEXT,
            year TEXT,
            total_amount REAL,
            created_at TEXT,  -- <--- MUST BE PRESENT
            synced INTEGER
        );
        )
    """)
    conn.commit()
    conn.close()
