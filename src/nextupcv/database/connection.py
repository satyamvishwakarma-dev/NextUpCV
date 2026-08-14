# src/nextupcv/database/connection.py
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

# On Vercel / serverless, write to /tmp. Locally, use the project data folder or /tmp.
if os.environ.get("VERCEL") or os.path.exists("/tmp"):
    DB_PATH = Path("/tmp/nextupcv.db")
else:
    DB_PATH = Path(__file__).resolve().parent.parent.parent.parent / "nextupcv.db"

# Ensure parent directory exists
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


@contextmanager
def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH), timeout=10.0)
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
    """Initializes tables in the SQLite database."""
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