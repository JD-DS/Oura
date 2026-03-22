"""Persistent storage for imported health data (SQLite)."""

from __future__ import annotations

import sqlite3
from pathlib import Path
import pandas as pd


def _get_db_path(data_dir: str) -> Path:
    """Resolve DB path from DATA_DIR (relative to cwd or absolute)."""
    p = Path(data_dir)
    if not p.is_absolute():
        p = Path.cwd() / p
    p.mkdir(parents=True, exist_ok=True)
    return p / "health_data.db"


def _ensure_lab_results_table(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS lab_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_name TEXT,
            value REAL,
            unit TEXT,
            reference_low REAL,
            reference_high REAL,
            panel_date TEXT,
            source_file TEXT,
            imported_at TEXT
        )
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_lab_panel_date ON lab_results(panel_date)"
    )
    conn.commit()


def get_activity_store(data_dir: str) -> sqlite3.Connection:
    """Get a connection and ensure activity table exists."""
    db_path = _get_db_path(data_dir)
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS activity (
            date TEXT PRIMARY KEY,
            steps REAL,
            calories REAL,
            workouts REAL,
            weight REAL,
            sleep_hours REAL,
            notes TEXT,
            source TEXT,
            imported_at TEXT
        )
    """)
    conn.commit()
    return conn


def save_activity_rows(
    conn: sqlite3.Connection,
    df: pd.DataFrame,
    source: str = "upload",
) -> int:
    """
    Upsert activity rows. Duplicates by date are replaced (incremental update).
    Returns number of rows written.
    """
    if df.empty:
        return 0

    from datetime import UTC, datetime

    now = datetime.now(UTC).isoformat()

    rows = []
    for _, row in df.iterrows():
        rows.append((
            str(row.get("date", "")),
            row.get("steps") if pd.notna(row.get("steps")) else None,
            row.get("calories") if pd.notna(row.get("calories")) else None,
            row.get("workouts") if pd.notna(row.get("workouts")) else None,
            row.get("weight") if pd.notna(row.get("weight")) else None,
            row.get("sleep_hours") if pd.notna(row.get("sleep_hours")) else None,
            str(row.get("notes", "")) if pd.notna(row.get("notes")) else None,
            source,
            now,
        ))

    conn.executemany("""
        INSERT INTO activity (date, steps, calories, workouts, weight, sleep_hours, notes, source, imported_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET
            steps = COALESCE(excluded.steps, steps),
            calories = COALESCE(excluded.calories, calories),
            workouts = COALESCE(excluded.workouts, workouts),
            weight = COALESCE(excluded.weight, weight),
            sleep_hours = COALESCE(excluded.sleep_hours, sleep_hours),
            notes = COALESCE(excluded.notes, notes),
            source = excluded.source,
            imported_at = excluded.imported_at
    """, rows)
    conn.commit()
    return len(rows)


def query_activity(
    data_dir: str,
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    """Query activity table for a date range."""
    db_path = _get_db_path(data_dir)
    if not db_path.exists():
        return pd.DataFrame()

    conn = sqlite3.connect(str(db_path))
    df = pd.read_sql(
        "SELECT * FROM activity WHERE date >= ? AND date <= ? ORDER BY date",
        conn,
        params=(start_date, end_date),
    )
    conn.close()
    return df


def get_lab_store(data_dir: str) -> sqlite3.Connection:
    """Get a connection and ensure lab_results table exists."""
    db_path = _get_db_path(data_dir)
    conn = sqlite3.connect(str(db_path))
    _ensure_lab_results_table(conn)
    return conn


def save_lab_results(
    conn: sqlite3.Connection,
    results: list[dict],
) -> int:
    """Insert lab results. Returns number of rows written."""
    from datetime import UTC, datetime

    if not results:
        return 0
    now = datetime.now(UTC).isoformat()
    rows = [
        (
            r.get("test_name", ""),
            r.get("value"),
            r.get("unit", ""),
            r.get("reference_low"),
            r.get("reference_high"),
            r.get("panel_date", ""),
            r.get("source_file", ""),
            now,
        )
        for r in results
    ]
    conn.executemany(
        """
        INSERT INTO lab_results (test_name, value, unit, reference_low, reference_high, panel_date, source_file, imported_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()
    return len(rows)


def query_lab_results(
    data_dir: str,
    start_date: str,
    end_date: str,
    test_name: str | None = None,
) -> pd.DataFrame:
    """Query lab results for a date range, optionally filtered by test name."""
    db_path = _get_db_path(data_dir)
    if not db_path.exists():
        return pd.DataFrame()

    conn = sqlite3.connect(str(db_path))
    if test_name:
        df = pd.read_sql(
            "SELECT * FROM lab_results WHERE panel_date >= ? AND panel_date <= ? AND test_name = ? ORDER BY panel_date",
            conn,
            params=(start_date, end_date, test_name),
        )
    else:
        df = pd.read_sql(
            "SELECT * FROM lab_results WHERE panel_date >= ? AND panel_date <= ? ORDER BY panel_date, test_name",
            conn,
            params=(start_date, end_date),
        )
    conn.close()
    return df
