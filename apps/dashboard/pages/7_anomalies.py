"""Page 7: Health Anomaly Detection -- rolling z-scores and early warning."""

import streamlit as st
import pandas as pd
import numpy as np

from config import ANOMALY_WINDOW_DAYS, ANOMALY_Z_THRESHOLD, default_start_date, default_end_date
from components.data import get_all_daily_data, get_sleep_df, get_readiness_df
from components.charts import anomaly_timeline

token = st.session_state.get("access_token", "")
sandbox = st.session_state.get("sandbox_mode", False)
start = st.session_state.get("start_date", str(default_start_date()))
end = st.session_state.get("end_date", str(default_end_date()))

st.header("Anomaly Detection")
st.caption(
    "Detect unusual patterns in your health metrics using rolling z-scores. "
    "Anomalies may indicate illness onset, overtraining, or environmental changes."
)

daily = get_all_daily_data(token, start, end, sandbox)
sleep_df = get_sleep_df(token, start, end, sandbox)
readiness_df = get_readiness_df(token, start, end, sandbox)

if daily.empty:
    st.info("No data available. Try expanding the date range or enabling sandbox mode.")
    st.stop()

col1, col2 = st.columns(2)
with col1:
    window = st.slider("Rolling window (days)", 7, 30, ANOMALY_WINDOW_DAYS)
with col2:
    threshold = st.slider("Z-score threshold (\u03c3)", 1.0, 3.0, ANOMALY_Z_THRESHOLD, 0.5)

if "temp_dev" in readiness_df.columns and readiness_df["temp_dev"].notna().any():
    st.subheader("Temperature Deviation")
    fig = anomaly_timeline(readiness_df, "day", "temp_dev", window, threshold, "Temperature Deviation Anomalies")
    st.plotly_chart(fig, use_container_width=True)

if not sleep_df.empty and "avg_hrv" in sleep_df.columns and sleep_df["avg_hrv"].notna().any():
    st.subheader("Heart Rate Variability (HRV)")
    fig = anomaly_timeline(sleep_df, "day", "avg_hrv", window, threshold, "HRV Anomalies")
    st.plotly_chart(fig, use_container_width=True)

if not sleep_df.empty and "lowest_hr" in sleep_df.columns and sleep_df["lowest_hr"].notna().any():
    st.subheader("Resting Heart Rate (Lowest During Sleep)")
    fig = anomaly_timeline(sleep_df, "day", "lowest_hr", window, threshold, "Resting HR Anomalies")
    st.plotly_chart(fig, use_container_width=True)

if "spo2_avg" in daily.columns and daily["spo2_avg"].notna().any():
    st.subheader("Blood Oxygen (SpO2)")
    fig = anomaly_timeline(daily, "day", "spo2_avg", window, threshold, "SpO2 Anomalies")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Illness Early Warning")
st.caption(
    "Flags days where temperature is rising AND HRV is declining simultaneously -- "
    "a pattern often associated with illness onset."
)

if (
    not readiness_df.empty
    and not sleep_df.empty
    and "temp_dev" in readiness_df.columns
    and "avg_hrv" in sleep_df.columns
):
    temp_series = readiness_df.set_index("day")["temp_dev"]
    hrv_series = sleep_df.drop_duplicates("day").set_index("day")["avg_hrv"]
    combined = pd.DataFrame({"temp_dev": temp_series, "avg_hrv": hrv_series}).dropna()

    if len(combined) >= window:
        temp_roll = combined["temp_dev"].rolling(window, min_periods=3)
        hrv_roll = combined["avg_hrv"].rolling(window, min_periods=3)
        temp_z = (combined["temp_dev"] - temp_roll.mean()) / temp_roll.std().replace(0, np.nan)
        hrv_z = (combined["avg_hrv"] - hrv_roll.mean()) / hrv_roll.std().replace(0, np.nan)
        warnings = (temp_z > threshold) & (hrv_z < -threshold)
        warning_days = combined.index[warnings]

        if len(warning_days) > 0:
            st.error(f"Potential illness signals detected on {len(warning_days)} day(s):")
            for d in warning_days:
                st.write(f"  - **{d}**: temp z={temp_z.loc[d]:.1f}\u03c3, HRV z={hrv_z.loc[d]:.1f}\u03c3")
        else:
            st.success("No illness warning signals detected in this period.")
    else:
        st.caption(f"Need at least {window} days of data for illness detection.")
else:
    st.caption("Temperature and HRV data needed for illness detection.")

st.subheader("All Detected Anomalies")

anomaly_metrics = []
for col in ["temp_dev", "avg_hrv", "lowest_hr", "spo2_avg"]:
    source_df = readiness_df if col in readiness_df.columns else (
        sleep_df if not sleep_df.empty and col in sleep_df.columns else daily
    )
    if col not in source_df.columns or not source_df[col].notna().any():
        continue
    series = source_df[col].dropna()
    if len(series) < window:
        continue
    roll_mean = series.rolling(window, min_periods=3).mean()
    roll_std = series.rolling(window, min_periods=3).std()
    z = ((series - roll_mean) / roll_std.replace(0, np.nan)).abs()
    flagged = z > threshold
    if flagged.any():
        for idx in source_df.index[flagged]:
            anomaly_metrics.append({
                "day": source_df.loc[idx, "day"],
                "metric": col.replace("_", " ").title(),
                "value": source_df.loc[idx, col],
                "z_score": z.loc[idx],
            })

if anomaly_metrics:
    anom_table = pd.DataFrame(anomaly_metrics).sort_values("day")
    st.dataframe(anom_table, use_container_width=True, hide_index=True)
else:
    st.success("No anomalies detected with the current settings.")
