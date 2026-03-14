"""Page 2: Sleep Analysis."""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from config import (
    CHART_BG,
    CHART_PAPER_BG,
    CHART_GRID_COLOR,
    SLEEP_EFFICIENCY_FLAG,
    SLEEP_EFFICIENCY_GOOD,
    SLEEP_LATENCY_FLAG_MIN,
    SLEEP_STAGE_COLORS,
    THEME_PRIMARY,
    THEME_SECONDARY,
    COLOR_GOOD,
    default_end_date,
    default_start_date,
)
from components.data import get_sleep_df
from components.charts import sleep_architecture_chart, trend_line
from styles import (
    get_custom_css,
    page_header,
    section_header,
    empty_state,
    warning_card,
    success_card,
)

theme_mode = st.session_state.get("theme_mode", "minimal")
st.markdown(get_custom_css(theme_mode), unsafe_allow_html=True)

token = st.session_state.get("access_token", "")
sandbox = st.session_state.get("sandbox_mode", False)
start = st.session_state.get("start_date", str(default_start_date()))
end = st.session_state.get("end_date", str(default_end_date()))

st.markdown(
    page_header("Sleep", "Analyze your sleep patterns and quality", theme_mode),
    unsafe_allow_html=True
)

df = get_sleep_df(token, start, end, sandbox)

if df.empty:
    st.markdown(
        empty_state("No sleep data", "Try expanding the date range.", "◇", theme_mode),
        unsafe_allow_html=True
    )
    st.stop()

st.markdown(section_header("Sleep Architecture", theme_mode), unsafe_allow_html=True)
fig = sleep_architecture_chart(df)
st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown(section_header("HRV During Sleep", theme_mode), unsafe_allow_html=True)
    hrv_df = df.dropna(subset=["avg_hrv"])
    if not hrv_df.empty:
        fig = trend_line(hrv_df, "day", "avg_hrv", "", y_label="HRV (ms)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("No HRV data")

with col2:
    st.markdown(section_header("Sleep Efficiency", theme_mode), unsafe_allow_html=True)
    eff_df = df.dropna(subset=["efficiency"])
    if not eff_df.empty:
        fig = px.scatter(
            eff_df, x="day", y="efficiency", size="total_sleep_h", color="latency_min",
            labels={"efficiency": "Efficiency %", "latency_min": "Latency (min)"},
            color_continuous_scale=[[0, THEME_PRIMARY], [1, THEME_SECONDARY]],
        )
        fig.add_hline(y=SLEEP_EFFICIENCY_GOOD, line_dash="dot", line_color=COLOR_GOOD)
        fig.update_layout(
            paper_bgcolor=CHART_PAPER_BG,
            plot_bgcolor=CHART_BG,
            font={"family": "IBM Plex Sans, sans-serif", "color": "#9ca3af"},
            margin=dict(t=20, b=40, l=50, r=20),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("No efficiency data")

col1, col2 = st.columns(2)
with col1:
    st.markdown(section_header("Heart Rate", theme_mode), unsafe_allow_html=True)
    hr_df = df.dropna(subset=["avg_hr"])
    if not hr_df.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hr_df["day"], y=hr_df["avg_hr"],
            name="Average", mode="lines+markers",
            line=dict(color=THEME_PRIMARY, width=1.5),
            marker=dict(size=4),
        ))
        fig.add_trace(go.Scatter(
            x=hr_df["day"], y=hr_df["lowest_hr"],
            name="Lowest", mode="lines+markers",
            line=dict(color=COLOR_GOOD, width=1.5),
            marker=dict(size=4),
        ))
        fig.update_layout(
            yaxis_title="BPM",
            paper_bgcolor=CHART_PAPER_BG,
            plot_bgcolor=CHART_BG,
            font={"family": "IBM Plex Sans, sans-serif", "color": "#9ca3af"},
            xaxis={"gridcolor": CHART_GRID_COLOR},
            yaxis={"gridcolor": CHART_GRID_COLOR},
            hovermode="x unified",
            margin=dict(t=20, b=40, l=50, r=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, font={"size": 11}),
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown(section_header("Breathing Rate", theme_mode), unsafe_allow_html=True)
    br_df = df.dropna(subset=["avg_breath"])
    if not br_df.empty:
        fig = trend_line(br_df, "day", "avg_breath", "", y_label="breaths/min")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("No breathing data")

st.markdown(section_header("Sleep Phases", theme_mode), unsafe_allow_html=True)
nights = df[df["sleep_phase_5_min"].notna()]
if not nights.empty:
    selected_day = st.selectbox(
        "Night",
        nights["day"].tolist(),
        index=len(nights) - 1,
        label_visibility="collapsed"
    )
    row = nights[nights["day"] == selected_day].iloc[0]
    phases = [int(c) for c in row["sleep_phase_5_min"]]
    phase_labels = {1: "Deep", 2: "Light", 3: "REM", 4: "Awake"}
    phase_colors_map = {
        1: SLEEP_STAGE_COLORS["deep_h"],
        2: SLEEP_STAGE_COLORS["light_h"],
        3: SLEEP_STAGE_COLORS["rem_h"],
        4: SLEEP_STAGE_COLORS["awake_h"]
    }

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=list(range(len(phases))), y=[1] * len(phases),
        marker_color=[phase_colors_map.get(p, "#888") for p in phases],
        hovertext=[phase_labels.get(p, "?") for p in phases],
    ))
    fig.update_layout(
        title={"text": str(selected_day), "font": {"family": "Space Grotesk", "size": 14, "color": "#e8e8e8"}},
        xaxis_title="5-min intervals",
        yaxis=dict(visible=False),
        paper_bgcolor=CHART_PAPER_BG,
        plot_bgcolor=CHART_BG,
        font={"family": "IBM Plex Sans, sans-serif", "color": "#9ca3af"},
        height=120,
        showlegend=False,
        margin=dict(t=35, b=30, l=20, r=20),
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.caption("No phase data")

st.markdown(section_header("Flagged Nights", theme_mode), unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.caption("Efficiency below")
    eff_thresh = st.slider("eff", 50, 100, SLEEP_EFFICIENCY_FLAG, label_visibility="collapsed")
with col2:
    st.caption("Latency above (min)")
    lat_thresh = st.slider("lat", 5, 120, SLEEP_LATENCY_FLAG_MIN, label_visibility="collapsed")

flagged = df[
    (df["efficiency"].notna() & (df["efficiency"] < eff_thresh))
    | (df["latency_min"] > lat_thresh)
]

if not flagged.empty:
    st.markdown(
        warning_card(f"{len(flagged)} night(s) below thresholds", theme_mode),
        unsafe_allow_html=True
    )
    st.dataframe(
        flagged[["day", "efficiency", "latency_min", "total_sleep_h", "avg_hrv"]],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.markdown(
        success_card("All nights above thresholds", theme_mode),
        unsafe_allow_html=True
    )
