"""Page 1: Holistic Health Dashboard -- overview of all key metrics."""

import streamlit as st

from config import default_start_date, default_end_date
from components.data import get_all_daily_data
from components.charts import score_kpi, sparkline, calendar_heatmap

token = st.session_state.get("access_token", "")
sandbox = st.session_state.get("sandbox_mode", False)
start = st.session_state.get("start_date", str(default_start_date()))
end = st.session_state.get("end_date", str(default_end_date()))

st.header("Health Dashboard")

daily = get_all_daily_data(token, start, end, sandbox)

if daily.empty:
    st.info("No data available for the selected date range. Try expanding the range or enabling sandbox mode.")
    st.stop()

latest = daily.iloc[-1] if not daily.empty else {}

cols = st.columns(5)
with cols[0]:
    score_kpi("Sleep Score", latest.get("sleep_score"))
with cols[1]:
    score_kpi("Readiness", latest.get("readiness_score"))
with cols[2]:
    score_kpi("Activity", latest.get("activity_score"))
with cols[3]:
    summary = latest.get("stress_summary", "N/A")
    score_kpi("Stress", summary if summary else "N/A")
with cols[4]:
    spo2 = latest.get("spo2_avg")
    score_kpi("SpO2", f"{spo2:.0f}" if spo2 else None, suffix="%")

st.markdown("### 7-Day Trends")

recent = daily.tail(7)
spark_cols = st.columns(5)
metrics = [
    ("sleep_score", "Sleep"),
    ("readiness_score", "Readiness"),
    ("activity_score", "Activity"),
    ("steps", "Steps"),
    ("avg_hrv", "HRV"),
]

for i, (col_name, label) in enumerate(metrics):
    with spark_cols[i]:
        st.caption(label)
        vals = recent[col_name].dropna().tolist() if col_name in recent.columns else []
        if vals:
            st.plotly_chart(sparkline(vals), use_container_width=True, config={"displayModeBar": False})
        else:
            st.caption("No data")

st.markdown("### Readiness Calendar")
if "readiness_score" in daily.columns:
    fig = calendar_heatmap(daily.dropna(subset=["readiness_score"]), "day", "readiness_score", "Readiness Score by Day")
    st.plotly_chart(fig, use_container_width=True)

with st.expander("Raw Daily Data"):
    display_cols = [c for c in ["day", "sleep_score", "readiness_score", "activity_score", "steps", "avg_hrv", "stress_summary", "spo2_avg"] if c in daily.columns]
    st.dataframe(daily[display_cols], use_container_width=True, hide_index=True)
