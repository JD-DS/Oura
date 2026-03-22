"""Page 5: Heart Rate & Stress analysis."""

import streamlit as st
import pandas as pd
import plotly.express as px

from config import (
    CHART_BG,
    CHART_COLOR_SEQUENCE,
    CHART_GRID_COLOR,
    CHART_PAPER_BG,
    COLOR_BAD,
    COLOR_GOOD,
    STRESS_COLORS,
    default_end_date,
    default_start_date,
)
from components.data import get_heart_rate_df, get_stress_df, get_resilience_df, get_sleep_df
from components.charts import grouped_bar, trend_line, pie_chart
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
        "Heart & Stress",
        "Monitor your cardiovascular health, stress levels, and recovery patterns",
        theme_mode
    ),
    unsafe_allow_html=True
)

sleep_df = get_sleep_df(token, start, end, sandbox)
stress_df = get_stress_df(token, start, end, sandbox)
res_df = get_resilience_df(token, start, end, sandbox)

latest_sleep = sleep_df.iloc[-1] if not sleep_df.empty else {}
latest_stress = stress_df.iloc[-1] if not stress_df.empty else {}
latest_res = res_df.iloc[-1] if not res_df.empty else {}

lowest_hr = latest_sleep.get("lowest_hr")
avg_hr = latest_sleep.get("avg_hr")
stress_summary = latest_stress.get("stress_summary", "N/A")
resilience = latest_res.get("resilience_level", "N/A")

cols = st.columns(4)
with cols[0]:
    st.metric("Lowest HR", f"{lowest_hr:.0f} bpm" if pd.notna(lowest_hr) else "—")
with cols[1]:
    st.metric("Avg Sleep HR", f"{avg_hr:.0f} bpm" if pd.notna(avg_hr) else "—")
with cols[2]:
    st.metric("Today's Stress", stress_summary if pd.notna(stress_summary) else "—")
with cols[3]:
    st.metric("Resilience", resilience.title() if pd.notna(resilience) else "—")

st.markdown(section_header("Heart Rate Time Series", theme_mode), unsafe_allow_html=True)
st.caption("Select a narrower date range for detailed HR data")

hr_start = f"{start}T00:00:00"
hr_end = f"{end}T23:59:59"

hr_df = get_heart_rate_df(token, hr_start, hr_end, sandbox)

if not hr_df.empty:
    fig = px.scatter(
        hr_df, x="timestamp", y="bpm", color="source",
        labels={"bpm": "BPM", "timestamp": "Time"},
        opacity=0.7,
        color_discrete_sequence=CHART_COLOR_SEQUENCE,
    )
    fig.update_traces(marker=dict(size=3))
    fig.update_layout(
        paper_bgcolor=CHART_PAPER_BG,
        plot_bgcolor=CHART_BG,
        font={"family": "Inter, -apple-system, sans-serif", "color": "#a1a1aa"},
        xaxis={"gridcolor": CHART_GRID_COLOR},
        yaxis={"gridcolor": CHART_GRID_COLOR},
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font={"size": 10}),
        margin=dict(t=20, b=40, l=50, r=20),
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(section_header("HR by Source", theme_mode), unsafe_allow_html=True)
        fig = px.box(
            hr_df, x="source", y="bpm", color="source",
            color_discrete_sequence=CHART_COLOR_SEQUENCE,
        )
        fig.update_layout(
            paper_bgcolor=CHART_PAPER_BG,
            plot_bgcolor=CHART_BG,
            font={"family": "Inter, -apple-system, sans-serif", "color": "#a1a1aa"},
            xaxis={"gridcolor": CHART_GRID_COLOR},
            yaxis={"gridcolor": CHART_GRID_COLOR},
            showlegend=False,
            margin=dict(t=20, b=40, l=50, r=20),
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown(section_header("Resting HR Trend", theme_mode), unsafe_allow_html=True)
        if not sleep_df.empty:
            rhr_df = sleep_df.dropna(subset=["lowest_hr"])
            if not rhr_df.empty:
                fig = trend_line(rhr_df, "day", "lowest_hr", "", y_label="BPM")
                st.plotly_chart(fig, use_container_width=True)
else:
    st.markdown(
        info_card("No heart rate data available for the selected date range.", theme_mode),
        unsafe_allow_html=True
    )

st.markdown(section_header("Daily Stress & Recovery", theme_mode), unsafe_allow_html=True)

if not stress_df.empty:
    has_data = stress_df[["stress_min", "recovery_min"]].notna().any().any()
    if has_data:
        fig = grouped_bar(
            stress_df, "day",
            [("stress_min", "High Stress (min)", COLOR_BAD), ("recovery_min", "High Recovery (min)", COLOR_GOOD)],
            "",
        )
        st.plotly_chart(fig, use_container_width=True)

    summary_counts = stress_df["stress_summary"].dropna().value_counts()
    if not summary_counts.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(section_header("Stress Distribution", theme_mode), unsafe_allow_html=True)
            fig = pie_chart(
                summary_counts.index.tolist(), summary_counts.values.tolist(),
                "", colors=STRESS_COLORS,
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown(section_header("Summary Stats", theme_mode), unsafe_allow_html=True)
            stats_df = stress_df.groupby("stress_summary")[["stress_min", "recovery_min"]].mean().round(1)
            st.dataframe(stats_df, use_container_width=True)
else:
    st.markdown(
        info_card("No stress data available for the selected date range.", theme_mode),
        unsafe_allow_html=True
    )

st.markdown(section_header("Resilience Timeline", theme_mode), unsafe_allow_html=True)

if not res_df.empty:
    level_order = ["limited", "adequate", "solid", "strong", "exceptional"]
    res_df["level_num"] = res_df["resilience_level"].map({v: i for i, v in enumerate(level_order)})

    fig = px.scatter(
        res_df, x="day", y="level_num", color="resilience_level",
        labels={"level_num": "Level", "day": "Date"},
        category_orders={"resilience_level": level_order},
        color_discrete_sequence=CHART_COLOR_SEQUENCE,
    )
    fig.update_yaxes(tickvals=list(range(5)), ticktext=[level.title() for level in level_order])
    fig.update_traces(marker=dict(size=10))
    fig.update_layout(
        paper_bgcolor=CHART_PAPER_BG,
        plot_bgcolor=CHART_BG,
        font={"family": "Inter, -apple-system, sans-serif", "color": "#a1a1aa"},
        xaxis={"gridcolor": CHART_GRID_COLOR},
        yaxis={"gridcolor": CHART_GRID_COLOR},
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font={"size": 10}),
        margin=dict(t=20, b=40, l=50, r=20),
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        fig = trend_line(res_df, "day", "sleep_recovery", "", y_label="Score")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = trend_line(res_df, "day", "daytime_recovery", "", y_label="Score")
        st.plotly_chart(fig, use_container_width=True)
    with col3:
        fig = trend_line(res_df, "day", "stress_contrib", "", y_label="Score")
        st.plotly_chart(fig, use_container_width=True)
else:
    st.markdown(
        info_card("No resilience data available for the selected date range.", theme_mode),
        unsafe_allow_html=True
    )
