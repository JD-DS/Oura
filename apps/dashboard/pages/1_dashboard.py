"""Page 1: Health Overview Dashboard."""

import streamlit as st

from config import default_start_date, default_end_date
from components.data import get_all_daily_data
from components.charts import sparkline, calendar_heatmap
from styles import get_custom_css, page_header, section_header, empty_state

# Get theme mode from session state
theme_mode = st.session_state.get("theme_mode", "minimal")
st.markdown(get_custom_css(theme_mode), unsafe_allow_html=True)

token = st.session_state.get("access_token", "")
sandbox = st.session_state.get("sandbox_mode", False)
start = st.session_state.get("start_date", str(default_start_date()))
end = st.session_state.get("end_date", str(default_end_date()))

st.markdown(
    page_header("Overview", "Your health at a glance", theme_mode),
    unsafe_allow_html=True
)

daily = get_all_daily_data(token, start, end, sandbox)

if daily.empty:
    st.markdown(
        empty_state(
            "No data available",
            "Try expanding the date range or enable demo mode in the sidebar.",
            "◇",
            theme_mode
        ),
        unsafe_allow_html=True
    )
    st.stop()

latest = daily.iloc[-1] if not daily.empty else {}

# Key metrics row
cols = st.columns(5)

stress_val = latest.get("stress_summary", "—")
if isinstance(stress_val, str) and len(stress_val) > 8:
    stress_val = stress_val[:8].rstrip()

metrics = [
    ("Sleep", latest.get("sleep_score"), ""),
    ("Ready", latest.get("readiness_score"), ""),
    ("Activity", latest.get("activity_score"), ""),
    ("Stress", stress_val, ""),
    ("SpO2", f"{latest.get('spo2_avg', 0):.0f}%" if latest.get("spo2_avg") else "—", ""),
]

for i, (label, value, suffix) in enumerate(metrics):
    with cols[i]:
        display_value = value if value is not None else "—"
        st.metric(label, display_value)

st.markdown(section_header("Weekly Trends", theme_mode), unsafe_allow_html=True)

recent = daily.tail(7)
spark_cols = st.columns(5)
trend_metrics = [
    ("sleep_score", "Sleep"),
    ("readiness_score", "Readiness"),
    ("activity_score", "Activity"),
    ("steps", "Steps"),
    ("avg_hrv", "HRV"),
]

for i, (col_name, label) in enumerate(trend_metrics):
    with spark_cols[i]:
        st.caption(label)
        vals = recent[col_name].dropna().tolist() if col_name in recent.columns else []
        if vals:
            st.plotly_chart(
                sparkline(vals),
                use_container_width=True,
                config={"displayModeBar": False}
            )
        else:
            st.caption("—")

st.markdown(section_header("Readiness Calendar", theme_mode), unsafe_allow_html=True)

if "readiness_score" in daily.columns:
    fig = calendar_heatmap(
        daily.dropna(subset=["readiness_score"]),
        "day",
        "readiness_score",
        ""
    )
    st.plotly_chart(fig, use_container_width=True)

with st.expander("Raw data"):
    display_cols = [
        c for c in [
            "day", "sleep_score", "readiness_score", "activity_score",
            "steps", "avg_hrv", "stress_summary", "spo2_avg"
        ]
        if c in daily.columns
    ]
    st.dataframe(daily[display_cols], use_container_width=True, hide_index=True)
