# src/nextupcv/database/connection.py
import os
import sqlite3
import tempfile
from contextlib import contextmanager
from pathlib import Path

# Use the system temp directory across OS / Serverless environments
# (On Vercel/Linux this is /tmp/nextupcv.db, which is writable)
TEMP_DIR = Path(tempfile.gettempdir())
DB_PATH = TEMP_DIR / "nextupcv.db"


@contextmanager
def get_db_connection():
    """Context manager for SQLite connections ensuring auto-commit and cleanup."""
    conn = sqlite3.connect(str(DB_PATH), timeout=15.0)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Initializes tables inside the writable SQLite database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS scan_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT,
                raw_resume_text TEXT,
                job_description TEXT,
                match_score INTEGER,
                missing_keyword_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )