"""Page 1: Health Overview Dashboard."""

import streamlit as st

from config import default_start_date, default_end_date
from components.data import get_all_daily_data
from components.charts import sparkline, calendar_heatmap
from styles import get_custom_css, page_header, section_header, empty_state

st.markdown(get_custom_css(), unsafe_allow_html=True)

token = st.session_state.get("access_token", "")
sandbox = st.session_state.get("sandbox_mode", False)
start = st.session_state.get("start_date", str(default_start_date()))
end = st.session_state.get("end_date", str(default_end_date()))

st.markdown(
    page_header("Overview"),
    unsafe_allow_html=True
)

daily = get_all_daily_data(token, start, end, sandbox)

if daily.empty:
    st.markdown(
        empty_state(
            "No data available",
            "Try expanding the date range or enable demo mode in the sidebar.",
            "◇",
        ),
        unsafe_allow_html=True
    )
    st.stop()

st.markdown(section_header("Weekly Trends"), unsafe_allow_html=True)

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

st.markdown(section_header("Readiness Calendar"), unsafe_allow_html=True)

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
