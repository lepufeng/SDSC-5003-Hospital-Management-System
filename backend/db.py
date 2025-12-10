import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # backend/
PROJECT_ROOT = os.path.dirname(BASE_DIR)              # project root
DB_PATH = os.path.join(PROJECT_ROOT, "hospital.db")


def get_db_connection():
    """Create a SQLite connection with foreign key support enabled."""

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn
