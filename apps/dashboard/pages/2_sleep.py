"""Page 2: Sleep Analysis."""

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
from styles import (
    get_custom_css,
    page_header,
    section_header,
    empty_state,
    warning_card,
    success_card,
)

st.markdown(get_custom_css(), unsafe_allow_html=True)

token = st.session_state.get("access_token", "")
sandbox = st.session_state.get("sandbox_mode", False)
start = st.session_state.get("start_date", str(default_start_date()))
end = st.session_state.get("end_date", str(default_end_date()))

st.markdown(
    page_header("Sleep", "Analyze your sleep patterns and quality"),
    unsafe_allow_html=True
)

df = get_sleep_df(token, start, end, sandbox)

if df.empty:
    st.markdown(
        empty_state("No sleep data", "Try expanding the date range."),
        unsafe_allow_html=True
    )
    st.stop()

st.markdown(section_header("Sleep architecture"), unsafe_allow_html=True)
fig = sleep_architecture_chart(df)
st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown(section_header("HRV during sleep"), unsafe_allow_html=True)
    hrv_df = df.dropna(subset=["avg_hrv"])
    if not hrv_df.empty:
        fig = trend_line(hrv_df, "day", "avg_hrv", "", y_label="HRV (ms)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("No HRV data")

with col2:
    st.markdown(section_header("Sleep efficiency"), unsafe_allow_html=True)
    eff_df = df.dropna(subset=["efficiency"])
    if not eff_df.empty:
        fig = px.scatter(
            eff_df, x="day", y="efficiency", size="total_sleep_h", color="latency_min",
            labels={"efficiency": "Efficiency %", "latency_min": "Latency (min)"},
            template=CHART_TEMPLATE,
        )
        fig.add_hline(y=SLEEP_EFFICIENCY_GOOD, line_dash="dot", line_color="#22C55E")
        fig.update_layout(title="", margin=dict(t=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("No efficiency data")

col1, col2 = st.columns(2)
with col1:
    st.markdown(section_header("Heart rate"), unsafe_allow_html=True)
    hr_df = df.dropna(subset=["avg_hr"])
    if not hr_df.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hr_df["day"], y=hr_df["avg_hr"],
            name="Average", mode="lines+markers",
            line=dict(color="#8B5CF6")
        ))
        fig.add_trace(go.Scatter(
            x=hr_df["day"], y=hr_df["lowest_hr"],
            name="Lowest", mode="lines+markers",
            line=dict(color="#22C55E")
        ))
        fig.update_layout(
            title="", yaxis_title="BPM", template=CHART_TEMPLATE,
            hovermode="x unified", margin=dict(t=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown(section_header("Breathing rate"), unsafe_allow_html=True)
    br_df = df.dropna(subset=["avg_breath"])
    if not br_df.empty:
        fig = trend_line(br_df, "day", "avg_breath", "", y_label="breaths/min")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("No breathing data")

st.markdown(section_header("Sleep phases"), unsafe_allow_html=True)
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
        title=f"{selected_day}",
        xaxis_title="5-min intervals",
        yaxis=dict(visible=False),
        template=CHART_TEMPLATE,
        height=120,
        showlegend=False,
        margin=dict(t=30, b=30),
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.caption("No phase data")

st.markdown(section_header("Flagged nights"), unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    eff_thresh = st.slider("Efficiency below", 50, 100, SLEEP_EFFICIENCY_FLAG, label_visibility="collapsed")
with col2:
    lat_thresh = st.slider("Latency above (min)", 5, 120, SLEEP_LATENCY_FLAG_MIN, label_visibility="collapsed")

flagged = df[
    (df["efficiency"].notna() & (df["efficiency"] < eff_thresh))
    | (df["latency_min"] > lat_thresh)
]

if not flagged.empty:
    st.markdown(
        warning_card(f"{len(flagged)} night(s) below thresholds"),
        unsafe_allow_html=True
    )
    st.dataframe(
        flagged[["day", "efficiency", "latency_min", "total_sleep_h", "avg_hrv"]],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.markdown(
        success_card("All nights above thresholds"),
        unsafe_allow_html=True
    )
