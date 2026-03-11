"""Page 3: Readiness & Recovery -- readiness contributors + workout recovery advisor."""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from config import CHART_TEMPLATE, THEME_PRIMARY, default_start_date, default_end_date
from components.data import get_readiness_df, get_workouts_df
from components.charts import trend_line, contributor_bar
from styles import (
    get_custom_css,
    main_header,
    section_header,
    info_box,
)

st.markdown(get_custom_css(), unsafe_allow_html=True)

token = st.session_state.get("access_token", "")
sandbox = st.session_state.get("sandbox_mode", False)
start = st.session_state.get("start_date", str(default_start_date()))
end = st.session_state.get("end_date", str(default_end_date()))

st.markdown(
    main_header(
        "Readiness & Recovery",
        "Understand what affects your daily readiness and optimize recovery"
    ),
    unsafe_allow_html=True
)

rd_df = get_readiness_df(token, start, end, sandbox)

if rd_df.empty:
    st.markdown(
        info_box("No readiness data available for the selected date range."),
        unsafe_allow_html=True
    )
    st.stop()

latest = rd_df.iloc[-1]
readiness_score = latest.get("readiness_score")
hrv_balance = latest.get("hrv_balance")
recovery_index = latest.get("recovery_index")
temp_dev = latest.get("temp_dev")

cols = st.columns(4)
with cols[0]:
    st.metric("Readiness", readiness_score if readiness_score else "—")
with cols[1]:
    st.metric("HRV Balance", hrv_balance if hrv_balance else "—")
with cols[2]:
    st.metric("Recovery Index", recovery_index if recovery_index else "—")
with cols[3]:
    st.metric("Temp Deviation", f"{temp_dev:+.2f}°C" if temp_dev else "—")

st.markdown(section_header("Readiness Score Trend"), unsafe_allow_html=True)
fig = trend_line(rd_df, "day", "readiness_score", "Readiness Score", y_label="Score (0-100)")
st.plotly_chart(fig, use_container_width=True)

st.markdown(section_header("Readiness Contributors Over Time"), unsafe_allow_html=True)
contributor_cols = [
    "hrv_balance", "body_temp", "prev_night", "sleep_balance",
    "recovery_index", "resting_hr", "activity_balance", "sleep_regularity",
]
available_cols = [c for c in contributor_cols if c in rd_df.columns and rd_df[c].notna().any()]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=rd_df["day"], y=rd_df["readiness_score"], name="Readiness Score",
    mode="lines+markers", line=dict(width=3, color=THEME_PRIMARY),
))
for col in available_cols:
    fig.add_trace(go.Scatter(
        x=rd_df["day"], y=rd_df[col],
        name=col.replace("_", " ").title(), mode="lines", opacity=0.5,
    ))
fig.update_layout(
    yaxis_title="Score (0-100)",
    template=CHART_TEMPLATE,
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    hovermode="x unified",
)
st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown(section_header("Weakest Link Analysis"), unsafe_allow_html=True)
    st.caption("Which contributors drag your readiness down most often?")

    if available_cols:
        avg_contribs = rd_df[available_cols].mean().sort_values()
        fig = contributor_bar(
            [c.replace("_", " ").title() for c in avg_contribs.index],
            avg_contribs.values.tolist(),
            "Average Contributor Scores",
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown(section_header("Contributor Heatmap"), unsafe_allow_html=True)
    contrib_data = rd_df.set_index("day")[available_cols].dropna()
    if not contrib_data.empty:
        fig = px.imshow(
            contrib_data.T, aspect="auto",
            labels={"x": "Date", "y": "Contributor", "color": "Score"},
            color_continuous_scale="RdYlGn",
            template=CHART_TEMPLATE,
        )
        fig.update_layout(margin=dict(t=20))
        st.plotly_chart(fig, use_container_width=True)

st.markdown(section_header("Workout Recovery Advisor"), unsafe_allow_html=True)

workouts_df = get_workouts_df(token, start, end, sandbox)

if not workouts_df.empty:
    rd_merge = rd_df[["day", "readiness_score"]].copy()
    rd_merge["day"] = pd.to_datetime(rd_merge["day"])
    rd_merge["next_day_readiness"] = rd_merge["readiness_score"].shift(-1)
    rd_merge["readiness_delta"] = rd_merge["next_day_readiness"] - rd_merge["readiness_score"]

    workouts_df["day"] = pd.to_datetime(workouts_df["day"])
    workout_readiness = workouts_df.merge(rd_merge, on="day", how="left")

    if not workout_readiness.empty:
        st.dataframe(
            workout_readiness[[
                "day", "activity", "intensity", "duration_min",
                "readiness_score", "next_day_readiness", "readiness_delta"
            ]].dropna(subset=["readiness_score"]),
            use_container_width=True,
            hide_index=True,
        )

        from config import COLOR_GOOD, COLOR_BAD
        by_intensity = workout_readiness.groupby("intensity")["readiness_delta"].mean().reset_index()
        if not by_intensity.empty:
            fig = go.Figure(go.Bar(
                x=by_intensity["intensity"],
                y=by_intensity["readiness_delta"],
                marker_color=[COLOR_GOOD if v >= 0 else COLOR_BAD for v in by_intensity["readiness_delta"]],
            ))
            fig.update_layout(
                title="Average Next-Day Readiness Change by Workout Intensity",
                yaxis_title="Readiness Delta",
                template=CHART_TEMPLATE,
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("No overlapping workout and readiness data")
else:
    st.caption("No workout data available")

st.markdown(section_header("Temperature Deviation"), unsafe_allow_html=True)
temp_df = rd_df.dropna(subset=["temp_dev"])
if not temp_df.empty:
    fig = trend_line(temp_df, "day", "temp_dev", "Temperature Deviation", y_label="°C deviation")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.caption("No temperature deviation data available")
