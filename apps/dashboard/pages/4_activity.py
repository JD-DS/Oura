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
    DATA_DIR_ABSOLUTE,
    default_end_date,
    default_start_date,
)
from components.data import get_activity_df, get_imported_activity_df
from components.charts import trend_line, grouped_bar
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
        "Activity",
        "Track your daily movement, calories burned, and activity patterns"
    ),
    unsafe_allow_html=True
)

df = get_activity_df(token, start, end, sandbox)
imported = get_imported_activity_df(DATA_DIR_ABSOLUTE, start, end)

if df.empty and imported.empty:
    st.markdown(
        info_box("No activity data available. Connect Oura or import data on the <strong>Import Data</strong> page."),
        unsafe_allow_html=True
    )
    st.stop()

has_oura = not df.empty
has_imported = not imported.empty

latest = df.iloc[-1] if has_oura else {}
latest_imp = imported.iloc[-1] if has_imported else {}

steps_val = latest.get("steps") if has_oura else latest_imp.get("steps")
active_cal = latest.get("active_cal") if has_oura else None
activity_score = latest.get("activity_score") if has_oura else None
walk_km = latest.get("eq_walk_km") if has_oura else None

cols = st.columns(4)
with cols[0]:
    st.metric("Steps", f"{steps_val:,.0f}" if steps_val else "—")
with cols[1]:
    st.metric("Active Calories", f"{active_cal:,.0f}" if active_cal else "—")
with cols[2]:
    st.metric("Activity Score", activity_score if activity_score else "—")
with cols[3]:
    st.metric("Walk Distance", f"{walk_km:.1f} km" if walk_km else "—")

if has_imported:
    cal_imp = latest_imp.get("calories")
    if cal_imp is not None:
        st.caption(f"📥 Imported calories (latest): {cal_imp:,.0f} kcal")

st.markdown(section_header("Daily Steps"), unsafe_allow_html=True)
fig = make_subplots(specs=[[{"secondary_y": True}]])
if has_oura:
    fig.add_trace(
        go.Bar(x=df["day"], y=df["steps"], name="Steps (Oura)", opacity=0.7, marker_color=THEME_PRIMARY),
        secondary_y=False
    )
if has_imported and "steps" in imported.columns:
    fig.add_trace(
        go.Scatter(
            x=imported["day"], y=imported["steps"],
            name="Steps (imported)", mode="lines+markers",
            line=dict(dash="dash", color="#4ECDC4")
        ),
        secondary_y=False
    )
if has_oura:
    fig.add_trace(
        go.Scatter(x=df["day"], y=df["active_cal"], name="Active Cal", mode="lines+markers"),
        secondary_y=True
    )
fig.update_layout(
    title="Daily Steps & Active Calories",
    template=CHART_TEMPLATE,
    hovermode="x unified",
)
fig.update_yaxes(title_text="Steps", secondary_y=False)
fig.update_yaxes(title_text="Active Calories", secondary_y=True)
st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown(section_header("Calories Breakdown"), unsafe_allow_html=True)
    if has_oura:
        fig = grouped_bar(
            df, "day",
            [("active_cal", "Active", COLOR_GOOD), ("total_cal", "Total", COLOR_INFO)],
            "Active vs Total Calories (Oura)"
        )
        st.plotly_chart(fig, use_container_width=True)
    elif has_imported and "calories" in imported.columns:
        fig = go.Figure(go.Bar(
            x=imported["day"], y=imported["calories"],
            name="Calories (imported)", marker_color=COLOR_INFO
        ))
        fig.update_layout(title="Calories (imported)", template=CHART_TEMPLATE)
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown(section_header("Activity Time Breakdown"), unsafe_allow_html=True)
    time_cols = ["high_activity_min", "medium_activity_min", "low_activity_min"]
    available = [c for c in time_cols if c in df.columns] if has_oura else []
    if available:
        fig = go.Figure()
        time_colors = {
            "high_activity_min": COLOR_BAD,
            "medium_activity_min": COLOR_WARNING,
            "low_activity_min": COLOR_GOOD
        }
        for col in available:
            label = col.replace("_activity_min", "").title()
            fig.add_trace(go.Bar(
                x=df["day"], y=df[col],
                name=label, marker_color=time_colors.get(col)
            ))
        fig.update_layout(
            barmode="stack",
            title="Activity Time Breakdown",
            yaxis_title="Minutes",
            template=CHART_TEMPLATE,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("No activity time breakdown available")

if has_imported and "calories" in imported.columns and has_oura:
    st.markdown(section_header("Imported Calories"), unsafe_allow_html=True)
    fig = go.Figure(go.Bar(
        x=imported["day"], y=imported["calories"],
        name="Calories (imported)", marker_color="#4ECDC4"
    ))
    fig.update_layout(title="Calories (imported)", template=CHART_TEMPLATE)
    st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    if has_oura:
        st.markdown(section_header("Equivalent Walking Distance"), unsafe_allow_html=True)
        fig = trend_line(df, "day", "eq_walk_km", "Equivalent Walking Distance", y_label="km")
        st.plotly_chart(fig, use_container_width=True)

with col2:
    if has_oura:
        st.markdown(section_header("Sedentary Time"), unsafe_allow_html=True)
        fig = trend_line(df, "day", "sedentary_h", "Sedentary Time", y_label="Hours")
        st.plotly_chart(fig, use_container_width=True)

if has_imported and "workouts" in imported.columns and imported["workouts"].notna().any():
    st.markdown(section_header("Workout Minutes (imported)"), unsafe_allow_html=True)
    fig = go.Figure(go.Bar(
        x=imported["day"], y=imported["workouts"],
        name="Workouts (imported)", marker_color=COLOR_GOOD
    ))
    fig.update_layout(template=CHART_TEMPLATE)
    st.plotly_chart(fig, use_container_width=True)
