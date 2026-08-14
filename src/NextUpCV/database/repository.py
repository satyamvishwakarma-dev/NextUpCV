from NextUpCV.database.connection import get_db_connection


def save_scan_record(
    file_name: str,
    raw_resume_text: str,
    job_description: str,
    match_score: float,
    missing_keyword_count: int,
) -> int:
    """
    Inserts a scan record into SQLite and returns the auto-incremented row ID.
    """
    query = """
    INSERT INTO scan_logs (
        file_name, raw_resume_text, job_description, match_score, missing_keyword_count
    ) VALUES (?, ?, ?, ?, ?);
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            query,
            (
                file_name,
                raw_resume_text,
                job_description,
                match_score,
                missing_keyword_count,
            ),
        )
        return cursor.lastrowid  # type: ignore


def get_recent_scans(limit: int = 5) -> list[dict]:
    """
    Fetches the most recent scan records for UI rendering.
    """
    query = """
    SELECT file_name, match_score, missing_keyword_count, created_at
    FROM scan_logs
    ORDER BY created_at DESC
    LIMIT ?;
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (limit,))
        return [dict(row) for row in cursor.fetchall()]
