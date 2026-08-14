import sqlite3
import logging
from contextlib import contextmanager
from NextUpCV.config import DB_PATH

logger = logging.getLogger(__name__)


@contextmanager
def get_db_connection():
    """
    Thread-safe context manager for local SQLite database connections.
    """
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error encountered: {e}")
        raise e
    finally:
        conn.close()


def init_db():
    """
    Creates scan_logs table schema if it does not already exist.
    """
    schema = """
    CREATE TABLE IF NOT EXISTS scan_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_name TEXT NOT NULL,
        raw_resume_text TEXT NOT NULL,
        job_description TEXT NOT NULL,
        match_score REAL NOT NULL,
        missing_keyword_count INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    with get_db_connection() as conn:
        conn.executescript(schema)
