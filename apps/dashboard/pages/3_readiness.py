"""Page 3: Readiness & Recovery -- readiness contributors + workout recovery advisor."""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from config import (
    CHART_BG,
    CHART_GRID_COLOR,
    CHART_PAPER_BG,
    COLOR_BAD,
    COLOR_GOOD,
    THEME_PRIMARY,
    default_end_date,
    default_start_date,
)
from components.data import get_readiness_df, get_workouts_df
from components.charts import trend_line, contributor_bar
from styles import (
    get_custom_css,
    page_header,
    section_header,
    info_card,
)

theme_mode = st.session_state.get("theme_mode", "minimal")
st.markdown(get_custom_css(theme_mode), unsafe_allow_html=True)

token = st.session_state.get("access_token", "")
sandbox = st.session_state.get("sandbox_mode", False)
start = st.session_state.get("start_date", str(default_start_date()))
end = st.session_state.get("end_date", str(default_end_date()))

st.markdown(
    page_header(
        "Readiness",
        "Understand what affects your daily readiness and optimize recovery",
        theme_mode
    ),
    unsafe_allow_html=True
)

rd_df = get_readiness_df(token, start, end, sandbox)

if rd_df.empty:
    st.markdown(
        info_card("No readiness data available for the selected date range.", theme_mode),
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
    st.metric("Readiness", readiness_score if pd.notna(readiness_score) else "—")
with cols[1]:
    st.metric("HRV Balance", hrv_balance if pd.notna(hrv_balance) else "—")
with cols[2]:
    st.metric("Recovery Index", recovery_index if pd.notna(recovery_index) else "—")
with cols[3]:
    st.metric("Temp Deviation", f"{temp_dev:+.2f}°C" if pd.notna(temp_dev) else "—")

st.markdown(section_header("Readiness Score Trend", theme_mode), unsafe_allow_html=True)
fig = trend_line(rd_df, "day", "readiness_score", "", y_label="Score (0-100)")
st.plotly_chart(fig, use_container_width=True)

st.markdown(section_header("Contributors Over Time", theme_mode), unsafe_allow_html=True)
contributor_cols = [
    "hrv_balance", "body_temp", "prev_night", "sleep_balance",
    "recovery_index", "resting_hr", "activity_balance", "sleep_regularity",
]
available_cols = [c for c in contributor_cols if c in rd_df.columns and rd_df[c].notna().any()]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=rd_df["day"], y=rd_df["readiness_score"], name="Readiness",
    mode="lines+markers", line=dict(width=2, color=THEME_PRIMARY),
    marker=dict(size=4),
))
for i, col in enumerate(available_cols):
    fig.add_trace(go.Scatter(
        x=rd_df["day"], y=rd_df[col],
        name=col.replace("_", " ").title(), mode="lines", opacity=0.5,
    ))
fig.update_layout(
    yaxis_title="Score (0-100)",
    paper_bgcolor=CHART_PAPER_BG,
    plot_bgcolor=CHART_BG,
    font={"family": "IBM Plex Sans, sans-serif", "color": "#9ca3af"},
    xaxis={"gridcolor": CHART_GRID_COLOR},
    yaxis={"gridcolor": CHART_GRID_COLOR},
    legend=dict(orientation="h", yanchor="bottom", y=1.02, font={"size": 10}),
    hovermode="x unified",
    margin=dict(t=20, b=40, l=50, r=20),
)
st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown(section_header("Weakest Contributors", theme_mode), unsafe_allow_html=True)

    if available_cols:
        avg_contribs = rd_df[available_cols].mean().sort_values()
        fig = contributor_bar(
            [c.replace("_", " ").title() for c in avg_contribs.index],
            avg_contribs.values.tolist(),
            "",
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown(section_header("Contributor Heatmap", theme_mode), unsafe_allow_html=True)
    contrib_data = rd_df.set_index("day")[available_cols].dropna()
    if not contrib_data.empty:
        colorscale = [[0, COLOR_BAD], [0.5, "#ffb800"], [1, COLOR_GOOD]]
        fig = px.imshow(
            contrib_data.T, aspect="auto",
            labels={"x": "Date", "y": "Contributor", "color": "Score"},
            color_continuous_scale=colorscale,
        )
        fig.update_layout(
            paper_bgcolor=CHART_PAPER_BG,
            plot_bgcolor=CHART_BG,
            font={"family": "IBM Plex Sans, sans-serif", "color": "#9ca3af"},
            margin=dict(t=20, b=40, l=100, r=20),
        )
        st.plotly_chart(fig, use_container_width=True)

st.markdown(section_header("Workout Recovery", theme_mode), unsafe_allow_html=True)

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

        by_intensity = workout_readiness.groupby("intensity")["readiness_delta"].mean().reset_index()
        if not by_intensity.empty:
            fig = go.Figure(go.Bar(
                x=by_intensity["intensity"],
                y=by_intensity["readiness_delta"],
                marker_color=[COLOR_GOOD if v >= 0 else COLOR_BAD for v in by_intensity["readiness_delta"]],
            ))
            fig.update_layout(
                title={"text": "Next-Day Readiness by Workout Intensity", "font": {"family": "Space Grotesk", "size": 14, "color": "#e8e8e8"}},
                yaxis_title="Readiness Delta",
                paper_bgcolor=CHART_PAPER_BG,
                plot_bgcolor=CHART_BG,
                font={"family": "IBM Plex Sans, sans-serif", "color": "#9ca3af"},
                xaxis={"gridcolor": CHART_GRID_COLOR},
                yaxis={"gridcolor": CHART_GRID_COLOR},
                margin=dict(t=50, b=40, l=50, r=20),
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("No overlapping workout and readiness data")
else:
    st.caption("No workout data available")

st.markdown(section_header("Temperature Deviation", theme_mode), unsafe_allow_html=True)
temp_df = rd_df.dropna(subset=["temp_dev"])
if not temp_df.empty:
    fig = trend_line(temp_df, "day", "temp_dev", "", y_label="°C deviation")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.caption("No temperature deviation data available")
