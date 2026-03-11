"""Parse Excel/CSV files into normalized activity rows."""

from __future__ import annotations

import io
from datetime import datetime
from pathlib import Path

import pandas as pd


# Column aliases: canonical_name -> list of accepted names
COLUMN_ALIASES = {
    "date": ["date", "day", "Day", "Date", "date_time"],
    "steps": ["steps", "Steps", "step_count"],
    "calories": ["calories", "Calories", "cal", "kcal"],
    "workouts": ["workouts", "Workouts", "workout_min", "exercise", "exercise_min"],
    "weight": ["weight", "Weight", "weight_kg"],
    "sleep_hours": ["sleep_hours", "sleep", "Sleep", "hours_slept"],
    "notes": ["notes", "Notes", "memo"],
}

DATE_FORMATS = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"]


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map aliased columns to canonical names."""
    out = pd.DataFrame()
    for canon, aliases in COLUMN_ALIASES.items():
        for a in aliases:
            if a in df.columns:
                out[canon] = df[a]
                break
    return out


def _parse_date(val) -> str | None:
    """Parse various date representations to YYYY-MM-DD."""
    if pd.isna(val):
        return None
    if isinstance(val, datetime):
        return val.strftime("%Y-%m-%d")
    if isinstance(val, (int, float)):
        try:
            # Interpret numeric values as Excel serial dates (days since 1899-12-30)
            return pd.to_datetime(val, origin="1899-12-30", unit="D").strftime("%Y-%m-%d")
        except Exception:
            return None
    s = str(val).strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    try:
        return pd.to_datetime(s).strftime("%Y-%m-%d")
    except Exception:
        return None


def parse_excel(
    file_or_bytes: bytes | str | Path,
    filename: str | None = None,
) -> tuple[pd.DataFrame, list[str]]:
    """
    Parse Excel or CSV into normalized activity rows.
    Returns (DataFrame with canonical columns, list of validation errors).
    """
    errors: list[str] = []
    df: pd.DataFrame

    if isinstance(file_or_bytes, (str, Path)):
        path = Path(file_or_bytes)
        if not path.exists():
            return pd.DataFrame(), [f"File not found: {path}"]
        if path.suffix.lower() in (".csv", ".txt"):
            df = pd.read_csv(path)
        else:
            df = pd.read_excel(path, engine="openpyxl")
    elif isinstance(file_or_bytes, bytes):
        buf = io.BytesIO(file_or_bytes)
        if filename and filename.lower().endswith(".csv"):
            df = pd.read_csv(buf)
        else:
            df = pd.read_excel(buf, engine="openpyxl")
    else:
        return pd.DataFrame(), ["Unsupported input type"]

    if df.empty:
        return pd.DataFrame(), ["File is empty or has no data rows"]

    # Normalize columns
    out = _normalize_columns(df)
    if "date" not in out.columns:
        return pd.DataFrame(), ["Required column 'date' not found. Accepted: date, day, Day, Date"]

    # Parse dates
    out["date"] = out["date"].apply(_parse_date)
    invalid_dates = out["date"].isna()
    if invalid_dates.any():
        n = invalid_dates.sum()
        errors.append(f"{n} rows with invalid dates dropped")
    out = out.dropna(subset=["date"])

    # Coerce numeric columns
    for col in ["steps", "calories", "workouts", "weight", "sleep_hours"]:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    # Deduplicate by date (last wins)
    out = out.drop_duplicates(subset=["date"], keep="last").sort_values("date").reset_index(drop=True)

    if out.empty:
        errors.append("No valid rows after parsing")

    return out, errors
