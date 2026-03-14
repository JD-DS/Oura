"""Page 4: Activity trends and goals."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import (
    CHART_BG,
    CHART_GRID_COLOR,
    CHART_PAPER_BG,
    COLOR_BAD,
    COLOR_GOOD,
    COLOR_INFO,
    COLOR_WARNING,
    DATA_DIR_ABSOLUTE,
    THEME_PRIMARY,
    THEME_SECONDARY,
    default_end_date,
    default_start_date,
)
from components.data import get_activity_df, get_imported_activity_df
from components.charts import trend_line, grouped_bar
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
        "Activity",
        "Track your daily movement, calories burned, and activity patterns",
        theme_mode
    ),
    unsafe_allow_html=True
)

df = get_activity_df(token, start, end, sandbox)
imported = get_imported_activity_df(DATA_DIR_ABSOLUTE, start, end)

if df.empty and imported.empty:
    st.markdown(
        info_card("No activity data available. Connect Oura or import data.", theme_mode),
        unsafe_allow_html=True
    )
    st.stop()

has_oura = not df.empty
has_imported = not imported.empty

latest = df.iloc[-1] if has_oura else {}
latest_imp = imported.iloc[-1] if has_imported else {}

cols = st.columns(4)
with cols[0]:
    steps_val = latest.get("steps") if has_oura else latest_imp.get("steps")
    st.metric("Steps", f"{steps_val:,.0f}" if pd.notna(steps_val) else "—")
with cols[1]:
    active_cal = latest.get("active_cal") if has_oura else None
    st.metric("Active Cal", f"{active_cal:,.0f}" if has_oura and pd.notna(active_cal) else "—")
with cols[2]:
    activity_score = latest.get("activity_score") if has_oura else None
    st.metric("Activity Score", activity_score if has_oura and pd.notna(activity_score) else "—")
with cols[3]:
    eq_walk_km = latest.get("eq_walk_km") if has_oura else None
    st.metric("Walk Distance", f"{eq_walk_km:.1f} km" if has_oura and pd.notna(eq_walk_km) else "—")

if has_imported:
    cal_imp = latest_imp.get("calories")
    if pd.notna(cal_imp):
        st.caption(f"Imported calories (latest): {cal_imp:,.0f} kcal")

st.markdown(section_header("Daily Steps", theme_mode), unsafe_allow_html=True)
fig = make_subplots(specs=[[{"secondary_y": True}]])
if has_oura:
    fig.add_trace(go.Bar(x=df["day"], y=df["steps"], name="Steps (Oura)", opacity=0.7, marker_color=THEME_PRIMARY), secondary_y=False)
if has_imported and "steps" in imported.columns:
    fig.add_trace(go.Scatter(x=imported["day"], y=imported["steps"], name="Steps (imported)", mode="lines+markers", line=dict(dash="dash", color=THEME_SECONDARY)), secondary_y=False)
if has_oura:
    fig.add_trace(go.Scatter(x=df["day"], y=df["active_cal"], name="Active Cal", mode="lines+markers", line=dict(color=COLOR_WARNING)), secondary_y=True)
fig.update_layout(
    paper_bgcolor=CHART_PAPER_BG,
    plot_bgcolor=CHART_BG,
    font={"family": "IBM Plex Sans, sans-serif", "color": "#9ca3af"},
    xaxis={"gridcolor": CHART_GRID_COLOR},
    yaxis={"gridcolor": CHART_GRID_COLOR},
    legend=dict(orientation="h", yanchor="bottom", y=1.02, font={"size": 10}),
    margin=dict(t=20, b=40, l=50, r=50),
)
fig.update_yaxes(title_text="Steps", secondary_y=False, gridcolor=CHART_GRID_COLOR)
fig.update_yaxes(title_text="Active Calories", secondary_y=True, gridcolor=CHART_GRID_COLOR)
st.plotly_chart(fig, use_container_width=True)

st.markdown(section_header("Calories", theme_mode), unsafe_allow_html=True)
if has_oura:
    fig = grouped_bar(df, "day", [("active_cal", "Active", COLOR_GOOD), ("total_cal", "Total", COLOR_INFO)], "")
    st.plotly_chart(fig, use_container_width=True)
if has_imported and "calories" in imported.columns:
    fig = go.Figure(go.Bar(x=imported["day"], y=imported["calories"], name="Calories (imported)", marker_color=THEME_SECONDARY))
    fig.update_layout(
        title={"text": "Imported Calories", "font": {"family": "Space Grotesk", "size": 14, "color": "#e8e8e8"}},
        paper_bgcolor=CHART_PAPER_BG,
        plot_bgcolor=CHART_BG,
        font={"family": "IBM Plex Sans, sans-serif", "color": "#9ca3af"},
        xaxis={"gridcolor": CHART_GRID_COLOR},
        yaxis={"gridcolor": CHART_GRID_COLOR},
        margin=dict(t=50, b=40, l=50, r=20),
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown(section_header("Activity Time", theme_mode), unsafe_allow_html=True)
time_cols = ["high_activity_min", "medium_activity_min", "low_activity_min"]
available = [c for c in time_cols if c in df.columns] if has_oura else []
if available:
    fig = go.Figure()
    time_colors = {"high_activity_min": COLOR_BAD, "medium_activity_min": COLOR_WARNING, "low_activity_min": COLOR_GOOD}
    for col in available:
        label = col.replace("_activity_min", "").title()
        fig.add_trace(go.Bar(x=df["day"], y=df[col], name=label, marker_color=time_colors.get(col)))
    fig.update_layout(
        barmode="stack",
        yaxis_title="Minutes",
        paper_bgcolor=CHART_PAPER_BG,
        plot_bgcolor=CHART_BG,
        font={"family": "IBM Plex Sans, sans-serif", "color": "#9ca3af"},
        xaxis={"gridcolor": CHART_GRID_COLOR},
        yaxis={"gridcolor": CHART_GRID_COLOR},
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font={"size": 10}),
        margin=dict(t=20, b=40, l=50, r=20),
    )
    st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)
if has_oura:
    with col1:
        st.markdown(section_header("Walking Distance", theme_mode), unsafe_allow_html=True)
        fig = trend_line(df, "day", "eq_walk_km", "", y_label="km")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(section_header("Sedentary Time", theme_mode), unsafe_allow_html=True)
        fig = trend_line(df, "day", "sedentary_h", "", y_label="Hours")
        st.plotly_chart(fig, use_container_width=True)

if has_imported and "workouts" in imported.columns and imported["workouts"].notna().any():
    st.markdown(section_header("Workout Minutes (Imported)", theme_mode), unsafe_allow_html=True)
    fig = go.Figure(go.Bar(x=imported["day"], y=imported["workouts"], name="Workouts", marker_color=COLOR_GOOD))
    fig.update_layout(
        paper_bgcolor=CHART_PAPER_BG,
        plot_bgcolor=CHART_BG,
        font={"family": "IBM Plex Sans, sans-serif", "color": "#9ca3af"},
        xaxis={"gridcolor": CHART_GRID_COLOR},
        yaxis={"gridcolor": CHART_GRID_COLOR},
        margin=dict(t=20, b=40, l=50, r=20),
    )
    st.plotly_chart(fig, use_container_width=True)
