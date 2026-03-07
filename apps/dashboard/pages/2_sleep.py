"""Page 2: Sleep Quality Analyzer."""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from config import (
    CHART_TEMPLATE,
    SLEEP_EFFICIENCY_FLAG,
    SLEEP_EFFICIENCY_GOOD,
    SLEEP_LATENCY_FLAG_MIN,
    SLEEP_STAGE_COLORS,
    default_end_date,
    default_start_date,
)
from components.data import get_sleep_df
from components.charts import sleep_architecture_chart, trend_line

token = st.session_state.get("access_token", "")
sandbox = st.session_state.get("sandbox_mode", False)
start = st.session_state.get("start_date", str(default_start_date()))
end = st.session_state.get("end_date", str(default_end_date()))

st.header("Sleep Analyzer")

df = get_sleep_df(token, start, end, sandbox)

if df.empty:
    st.info("No sleep data available for the selected date range.")
    st.stop()

st.subheader("Sleep Architecture")
fig = sleep_architecture_chart(df)
st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("HRV During Sleep")
    hrv_df = df.dropna(subset=["avg_hrv"])
    if not hrv_df.empty:
        fig = trend_line(hrv_df, "day", "avg_hrv", "Average HRV During Sleep", y_label="HRV (ms)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("No HRV data")

with col2:
    st.subheader("Sleep Efficiency")
    eff_df = df.dropna(subset=["efficiency"])
    if not eff_df.empty:
        fig = px.scatter(
            eff_df, x="day", y="efficiency", size="total_sleep_h", color="latency_min",
            title="Efficiency (bubble=total sleep, color=latency)",
            labels={"efficiency": "Efficiency %", "latency_min": "Latency (min)"},
            template=CHART_TEMPLATE,
        )
        fig.add_hline(y=SLEEP_EFFICIENCY_GOOD, line_dash="dot", annotation_text="Good", line_color="green")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("No efficiency data")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Heart Rate During Sleep")
    hr_df = df.dropna(subset=["avg_hr"])
    if not hr_df.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hr_df["day"], y=hr_df["avg_hr"], name="Avg HR", mode="lines+markers"))
        fig.add_trace(go.Scatter(x=hr_df["day"], y=hr_df["lowest_hr"], name="Lowest HR", mode="lines+markers"))
        fig.update_layout(title="HR During Sleep", yaxis_title="BPM", template=CHART_TEMPLATE)
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Breathing Rate")
    br_df = df.dropna(subset=["avg_breath"])
    if not br_df.empty:
        fig = trend_line(br_df, "day", "avg_breath", "Average Breathing Rate", y_label="breaths/sec")
        st.plotly_chart(fig, use_container_width=True)

st.subheader("Sleep Phase Timeline")
nights = df[df["sleep_phase_5_min"].notna()]
if not nights.empty:
    selected_day = st.selectbox("Select night", nights["day"].tolist(), index=len(nights) - 1)
    row = nights[nights["day"] == selected_day].iloc[0]
    phases = [int(c) for c in row["sleep_phase_5_min"]]
    phase_labels = {1: "Deep", 2: "Light", 3: "REM", 4: "Awake"}
    phase_colors_map = {1: SLEEP_STAGE_COLORS["deep_h"], 2: SLEEP_STAGE_COLORS["light_h"], 3: SLEEP_STAGE_COLORS["rem_h"], 4: SLEEP_STAGE_COLORS["awake_h"]}

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=list(range(len(phases))), y=[1] * len(phases),
        marker_color=[phase_colors_map.get(p, "#888") for p in phases],
        hovertext=[phase_labels.get(p, "?") for p in phases],
    ))
    fig.update_layout(
        title=f"Sleep Phases -- {selected_day} (5-min intervals from bedtime)",
        xaxis_title="Time (5-min intervals)", yaxis=dict(visible=False),
        template=CHART_TEMPLATE, height=150, showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.caption("No phase data available")

st.subheader("Flagged Nights")
eff_thresh = st.slider("Efficiency threshold", 50, 100, SLEEP_EFFICIENCY_FLAG)
lat_thresh = st.slider("Latency threshold (min)", 5, 120, SLEEP_LATENCY_FLAG_MIN)

flagged = df[
    (df["efficiency"].notna() & (df["efficiency"] < eff_thresh))
    | (df["latency_min"] > lat_thresh)
]

if not flagged.empty:
    st.warning(f"{len(flagged)} night(s) flagged")
    st.dataframe(
        flagged[["day", "efficiency", "latency_min", "total_sleep_h", "avg_hrv"]],
        use_container_width=True, hide_index=True,
    )
else:
    st.success("No nights below threshold")
