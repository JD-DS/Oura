"""Page 5: Heart Rate & Stress analysis."""

import streamlit as st
import plotly.express as px

from config import CHART_TEMPLATE, STRESS_COLORS, default_start_date, default_end_date
from components.data import get_heart_rate_df, get_stress_df, get_resilience_df, get_sleep_df
from components.charts import grouped_bar, trend_line, pie_chart, COLOR_BAD, COLOR_GOOD

token = st.session_state.get("access_token", "")
sandbox = st.session_state.get("sandbox_mode", False)
start = st.session_state.get("start_date", str(default_start_date()))
end = st.session_state.get("end_date", str(default_end_date()))

st.header("Heart Rate & Stress")

st.subheader("Heart Rate Time Series")
st.caption("Select a narrower date range for detailed HR data (large ranges may be slow)")

hr_start = f"{start}T00:00:00"
hr_end = f"{end}T23:59:59"

hr_df = get_heart_rate_df(token, hr_start, hr_end, sandbox)

if not hr_df.empty:
    fig = px.scatter(
        hr_df, x="timestamp", y="bpm", color="source",
        title="Heart Rate by Source",
        labels={"bpm": "BPM", "timestamp": "Time"},
        template=CHART_TEMPLATE, opacity=0.7,
    )
    fig.update_traces(marker=dict(size=4))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("HR Distribution by Source")
    fig = px.box(hr_df, x="source", y="bpm", color="source", title="BPM by Source", template=CHART_TEMPLATE)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No heart rate data available.")

st.subheader("Resting Heart Rate Trend")
sleep_df = get_sleep_df(token, start, end, sandbox)
if not sleep_df.empty:
    rhr_df = sleep_df.dropna(subset=["lowest_hr"])
    if not rhr_df.empty:
        fig = trend_line(rhr_df, "day", "lowest_hr", "Lowest HR During Sleep", y_label="BPM")
        st.plotly_chart(fig, use_container_width=True)

st.subheader("Daily Stress & Recovery")
stress_df = get_stress_df(token, start, end, sandbox)

if not stress_df.empty:
    has_data = stress_df[["stress_min", "recovery_min"]].notna().any().any()
    if has_data:
        fig = grouped_bar(
            stress_df, "day",
            [("stress_min", "High Stress (min)", COLOR_BAD), ("recovery_min", "High Recovery (min)", COLOR_GOOD)],
            "Stress vs Recovery Time",
        )
        st.plotly_chart(fig, use_container_width=True)

    summary_counts = stress_df["stress_summary"].dropna().value_counts()
    if not summary_counts.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Day Summary Distribution")
            fig = pie_chart(
                summary_counts.index.tolist(), summary_counts.values.tolist(),
                "Stress Day Summaries", colors=STRESS_COLORS,
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Stress Summary Stats")
            st.dataframe(
                stress_df.groupby("stress_summary")[["stress_min", "recovery_min"]].mean().round(1),
                use_container_width=True,
            )
else:
    st.info("No stress data available.")

st.subheader("Resilience Level Timeline")
res_df = get_resilience_df(token, start, end, sandbox)

if not res_df.empty:
    level_order = ["limited", "adequate", "solid", "strong", "exceptional"]
    res_df["level_num"] = res_df["resilience_level"].map({v: i for i, v in enumerate(level_order)})

    fig = px.scatter(
        res_df, x="day", y="level_num", color="resilience_level",
        title="Resilience Level Over Time",
        labels={"level_num": "Level", "day": "Date"},
        template=CHART_TEMPLATE, category_orders={"resilience_level": level_order},
    )
    fig.update_yaxes(tickvals=list(range(5)), ticktext=level_order)
    fig.update_traces(marker=dict(size=10))
    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        fig = trend_line(res_df, "day", "sleep_recovery", "Sleep Recovery", y_label="Score")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = trend_line(res_df, "day", "daytime_recovery", "Daytime Recovery", y_label="Score")
        st.plotly_chart(fig, use_container_width=True)
    with col3:
        fig = trend_line(res_df, "day", "stress_contrib", "Stress Contributor", y_label="Score")
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No resilience data available.")
