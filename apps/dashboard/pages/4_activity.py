"""Page 4: Activity trends and goals."""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import (
    CHART_TEMPLATE,
    COLOR_BAD,
    COLOR_GOOD,
    COLOR_INFO,
    COLOR_WARNING,
    THEME_PRIMARY,
    default_end_date,
    default_start_date,
)
from components.data import get_activity_df
from components.charts import trend_line, grouped_bar

token = st.session_state.get("access_token", "")
sandbox = st.session_state.get("sandbox_mode", False)
start = st.session_state.get("start_date", str(default_start_date()))
end = st.session_state.get("end_date", str(default_end_date()))

st.header("Activity")

df = get_activity_df(token, start, end, sandbox)

if df.empty:
    st.info("No activity data available for the selected date range.")
    st.stop()

latest = df.iloc[-1]
cols = st.columns(4)
with cols[0]:
    st.metric("Steps", f"{latest.get('steps', 0):,}")
with cols[1]:
    st.metric("Active Cal", f"{latest.get('active_cal', 0):,}")
with cols[2]:
    st.metric("Activity Score", latest.get("activity_score"))
with cols[3]:
    st.metric("Walk Distance", f"{latest.get('eq_walk_km', 0):.1f} km")

st.subheader("Daily Steps")
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Bar(x=df["day"], y=df["steps"], name="Steps", opacity=0.7, marker_color=THEME_PRIMARY), secondary_y=False)
fig.add_trace(go.Scatter(x=df["day"], y=df["active_cal"], name="Active Cal", mode="lines+markers"), secondary_y=True)
fig.update_layout(title="Daily Steps & Active Calories", template=CHART_TEMPLATE)
fig.update_yaxes(title_text="Steps", secondary_y=False)
fig.update_yaxes(title_text="Active Calories", secondary_y=True)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Calories")
fig = grouped_bar(df, "day", [("active_cal", "Active", COLOR_GOOD), ("total_cal", "Total", COLOR_INFO)], "Active vs Total Calories")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Activity Time Breakdown")
time_cols = ["high_activity_min", "medium_activity_min", "low_activity_min"]
available = [c for c in time_cols if c in df.columns]
if available:
    fig = go.Figure()
    time_colors = {"high_activity_min": COLOR_BAD, "medium_activity_min": COLOR_WARNING, "low_activity_min": COLOR_GOOD}
    for col in available:
        label = col.replace("_activity_min", "").title()
        fig.add_trace(go.Bar(x=df["day"], y=df[col], name=label, marker_color=time_colors.get(col)))
    fig.update_layout(barmode="stack", title="Activity Time Breakdown (min)", yaxis_title="Minutes", template=CHART_TEMPLATE)
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Equivalent Walking Distance")
fig = trend_line(df, "day", "eq_walk_km", "Equivalent Walking Distance", y_label="km")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Sedentary Time")
fig = trend_line(df, "day", "sedentary_h", "Sedentary Time", y_label="Hours")
st.plotly_chart(fig, use_container_width=True)
