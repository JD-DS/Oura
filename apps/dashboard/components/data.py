"""Cached data-fetching layer for the Streamlit dashboard.

All functions accept an access_token string and date range, returning
DataFrames ready for charting. Cache TTL is configurable via config.py.
"""

from __future__ import annotations

import os
import sys

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

from config import CACHE_TTL_SECONDS, DATA_DIR_ABSOLUTE
from oura_client.auth import OuraAuth
from oura_client.client import OuraClient


def _make_client(token: str, sandbox: bool = False) -> OuraClient:
    auth = OuraAuth(access_token=token)
    return OuraClient(auth=auth, sandbox=sandbox)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner="Fetching sleep data...")
def get_sleep_df(_token: str, start: str, end: str, sandbox: bool = False) -> pd.DataFrame:
    client = _make_client(_token, sandbox)
    records = client.get_sleep(start_date=start, end_date=end)
    if not records:
        return pd.DataFrame()
    rows = []
    for s in records:
        rows.append({
            "day": s.day,
            "total_sleep_h": s.total_sleep_hours,
            "deep_h": s.deep_sleep_hours,
            "light_h": s.light_sleep_hours,
            "rem_h": s.rem_sleep_hours,
            "awake_h": s.awake_hours,
            "efficiency": s.efficiency,
            "avg_hrv": s.average_hrv,
            "avg_hr": s.average_heart_rate,
            "lowest_hr": s.lowest_heart_rate,
            "avg_breath": s.average_breath,
            "latency_min": (s.latency or 0) / 60,
            "restless_periods": s.restless_periods,
            "time_in_bed_h": s.time_in_bed / 3600 if s.time_in_bed else None,
            "type": s.type.value,
            "sleep_phase_5_min": s.sleep_phase_5_min,
            "bedtime_start": s.bedtime_start,
            "bedtime_end": s.bedtime_end,
        })
    return pd.DataFrame(rows).sort_values("day").reset_index(drop=True)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner="Fetching daily scores...")
def get_daily_sleep_df(_token: str, start: str, end: str, sandbox: bool = False) -> pd.DataFrame:
    client = _make_client(_token, sandbox)
    records = client.get_daily_sleep(start_date=start, end_date=end)
    if not records:
        return pd.DataFrame()
    rows = [{"day": r.day, "sleep_score": r.score} for r in records]
    return pd.DataFrame(rows).sort_values("day").reset_index(drop=True)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner="Fetching activity data...")
def get_activity_df(_token: str, start: str, end: str, sandbox: bool = False) -> pd.DataFrame:
    client = _make_client(_token, sandbox)
    records = client.get_daily_activity(start_date=start, end_date=end)
    if not records:
        return pd.DataFrame()
    rows = []
    for a in records:
        rows.append({
            "day": a.day,
            "activity_score": a.score,
            "steps": a.steps,
            "active_cal": a.active_calories,
            "total_cal": a.total_calories,
            "high_activity_min": a.high_activity_minutes,
            "medium_activity_min": a.medium_activity_time / 60,
            "low_activity_min": a.low_activity_time / 60,
            "sedentary_h": a.sedentary_hours,
            "eq_walk_km": a.equivalent_walking_distance / 1000,
            "target_cal": a.target_calories,
            "target_meters": a.target_meters,
        })
    return pd.DataFrame(rows).sort_values("day").reset_index(drop=True)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner="Fetching readiness data...")
def get_readiness_df(_token: str, start: str, end: str, sandbox: bool = False) -> pd.DataFrame:
    client = _make_client(_token, sandbox)
    records = client.get_daily_readiness(start_date=start, end_date=end)
    if not records:
        return pd.DataFrame()
    rows = []
    for r in records:
        rows.append({
            "day": r.day,
            "readiness_score": r.score,
            "temp_dev": r.temperature_deviation,
            "temp_trend_dev": r.temperature_trend_deviation,
            "hrv_balance": r.contributors.hrv_balance,
            "body_temp": r.contributors.body_temperature,
            "prev_night": r.contributors.previous_night,
            "sleep_balance": r.contributors.sleep_balance,
            "recovery_index": r.contributors.recovery_index,
            "resting_hr": r.contributors.resting_heart_rate,
            "activity_balance": r.contributors.activity_balance,
            "prev_day_activity": r.contributors.previous_day_activity,
            "sleep_regularity": r.contributors.sleep_regularity,
        })
    return pd.DataFrame(rows).sort_values("day").reset_index(drop=True)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner="Fetching stress data...")
def get_stress_df(_token: str, start: str, end: str, sandbox: bool = False) -> pd.DataFrame:
    client = _make_client(_token, sandbox)
    records = client.get_daily_stress(start_date=start, end_date=end)
    if not records:
        return pd.DataFrame()
    rows = []
    for s in records:
        rows.append({
            "day": s.day,
            "stress_min": s.stress_high_minutes,
            "recovery_min": s.recovery_high_minutes,
            "stress_summary": s.day_summary.value if s.day_summary else None,
        })
    return pd.DataFrame(rows).sort_values("day").reset_index(drop=True)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner="Fetching resilience data...")
def get_resilience_df(_token: str, start: str, end: str, sandbox: bool = False) -> pd.DataFrame:
    client = _make_client(_token, sandbox)
    records = client.get_daily_resilience(start_date=start, end_date=end)
    if not records:
        return pd.DataFrame()
    rows = []
    for r in records:
        rows.append({
            "day": r.day,
            "resilience_level": r.level.value,
            "sleep_recovery": r.contributors.sleep_recovery,
            "daytime_recovery": r.contributors.daytime_recovery,
            "stress_contrib": r.contributors.stress,
        })
    return pd.DataFrame(rows).sort_values("day").reset_index(drop=True)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner="Fetching SpO2 data...")
def get_spo2_df(_token: str, start: str, end: str, sandbox: bool = False) -> pd.DataFrame:
    client = _make_client(_token, sandbox)
    records = client.get_daily_spo2(start_date=start, end_date=end)
    if not records:
        return pd.DataFrame()
    rows = []
    for r in records:
        avg = r.spo2_percentage.average if r.spo2_percentage else None
        rows.append({"day": r.day, "spo2_avg": avg, "bdi": r.breathing_disturbance_index})
    return pd.DataFrame(rows).sort_values("day").reset_index(drop=True)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner="Fetching heart rate data...")
def get_heart_rate_df(
    _token: str, start_dt: str, end_dt: str, sandbox: bool = False
) -> pd.DataFrame:
    client = _make_client(_token, sandbox)
    records = client.get_heart_rate(start_datetime=start_dt, end_datetime=end_dt)
    if not records:
        return pd.DataFrame()
    rows = [{"timestamp": h.timestamp, "bpm": h.bpm, "source": h.source.value} for h in records]
    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    return df.sort_values("timestamp").reset_index(drop=True)


@st.cache_data(ttl=60, show_spinner=False)  # Short TTL: imports update filesystem
def get_imported_activity_df(data_dir: str, start: str, end: str) -> pd.DataFrame:
    """Fetch imported activity (steps, calories, workouts) from local store."""
    try:
        from health_import import query_activity
        df = query_activity(data_dir, start, end)
        if not df.empty and "date" in df.columns:
            df = df.rename(columns={"date": "day"})
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner="Fetching workout data...")
def get_workouts_df(_token: str, start: str, end: str, sandbox: bool = False) -> pd.DataFrame:
    client = _make_client(_token, sandbox)
    records = client.get_workouts(start_date=start, end_date=end)
    if not records:
        return pd.DataFrame()
    rows = []
    for w in records:
        rows.append({
            "day": w.day,
            "activity": w.activity,
            "calories": w.calories,
            "distance_m": w.distance,
            "intensity": w.intensity.value,
            "duration_min": w.duration_minutes,
            "source": w.source.value,
        })
    return pd.DataFrame(rows).sort_values("day").reset_index(drop=True)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner="Fetching cardiovascular age...")
def get_cardio_age_df(_token: str, start: str, end: str, sandbox: bool = False) -> pd.DataFrame:
    client = _make_client(_token, sandbox)
    records = client.get_daily_cardiovascular_age(start_date=start, end_date=end)
    if not records:
        return pd.DataFrame()
    rows = [{"day": r.day, "vascular_age": r.vascular_age} for r in records]
    return pd.DataFrame(rows).sort_values("day").reset_index(drop=True)


def get_all_daily_data(token: str, start: str, end: str, sandbox: bool = False) -> pd.DataFrame:
    """Fetch all daily data types and merge into one DataFrame keyed by day."""
    sleep_df = get_daily_sleep_df(token, start, end, sandbox)
    activity_df = get_activity_df(token, start, end, sandbox)
    readiness_df = get_readiness_df(token, start, end, sandbox)
    stress_df = get_stress_df(token, start, end, sandbox)
    spo2_df = get_spo2_df(token, start, end, sandbox)
    resilience_df = get_resilience_df(token, start, end, sandbox)

    detail_df = get_sleep_df(token, start, end, sandbox)
    if not detail_df.empty:
        detail_df = detail_df[["day", "avg_hrv", "avg_hr", "lowest_hr"]].drop_duplicates("day")

    merged = sleep_df
    for df in [activity_df, readiness_df, stress_df, spo2_df, resilience_df]:
        if not df.empty and not merged.empty:
            merged = merged.merge(df, on="day", how="outer")
        elif not df.empty:
            merged = df

    if not detail_df.empty and not merged.empty:
        merged = merged.merge(detail_df, on="day", how="left")

    if not merged.empty:
        merged = merged.sort_values("day").reset_index(drop=True)

    return merged


def get_all_daily_data_with_imported(token: str, start: str, end: str, sandbox: bool = False) -> pd.DataFrame:
    """Merge Oura daily data with imported activity (steps, calories, workouts) for Correlations/Anomaly pages."""
    daily = get_all_daily_data(token, start, end, sandbox)
    imported = get_imported_activity_df(DATA_DIR_ABSOLUTE, start, end)
    if not imported.empty:
        imp_merge = imported.rename(columns={
            "steps": "steps_imported",
            "calories": "calories_imported",
            "workouts": "workouts_imported",
            "weight": "weight_imported",
            "sleep_hours": "sleep_hours_imported",
        })
        imp_cols = ["day"] + [c for c in imp_merge.columns if c != "day" and c.endswith("_imported")]
        imp_merge = imp_merge[[c for c in imp_cols if c in imp_merge.columns]]
        if not daily.empty:
            daily = daily.merge(imp_merge, on="day", how="outer").sort_values("day").reset_index(drop=True)
        else:
            daily = imp_merge
    return daily


@st.cache_data(ttl=60, show_spinner=False)
def get_lab_results_df(data_dir: str, start: str, end: str) -> pd.DataFrame:
    """Fetch lab results for a date range."""
    try:
        from health_import import query_lab_results
