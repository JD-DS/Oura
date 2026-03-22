"""Page 10: Lab Results — biomarker trends, reference ranges, out-of-range flags."""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from config import (
    CHART_BG,
    CHART_GRID_COLOR,
    CHART_PAPER_BG,
    COLOR_WARNING,
    DATA_DIR_ABSOLUTE,
    THEME_PRIMARY,
)
from components.data import get_lab_results_df
from styles import (
    get_custom_css,
    page_header,
    section_header,
    info_card,
    success_card,
    warning_card,
)

st.markdown(get_custom_css(), unsafe_allow_html=True)

labs_start_default = str(date.today() - timedelta(days=365))
labs_end_default = str(date.today())

start = st.session_state.get("start_date", labs_start_default)
end = st.session_state.get("end_date", labs_end_default)

st.markdown(
    page_header("Labs", "Biomarker trends from imported blood panels"),
    unsafe_allow_html=True
)

try:
    labs = get_lab_results_df(DATA_DIR_ABSOLUTE, start, end)
except Exception as e:
    st.error(str(e))
    st.stop()

if labs.empty:
    st.markdown(
        info_card("No lab results for this date range. Upload blood panel PDFs on the Import page."),
        unsafe_allow_html=True
    )
    st.stop()

st.markdown(section_header("Out-of-Range Summary"), unsafe_allow_html=True)

if "reference_low" in labs.columns and "reference_high" in labs.columns:
    def is_out_of_range(row):
        v = row.get("value")
        lo, hi = row.get("reference_low"), row.get("reference_high")
        if pd.isna(v):
            return False
        if pd.notna(lo) and v < lo:
            return True
        if pd.notna(hi) and v > hi:
            return True
        return False

    labs["out_of_range"] = labs.apply(is_out_of_range, axis=1)
    out_count = labs["out_of_range"].sum()
    
    if out_count > 0:
        st.markdown(
            warning_card(f"{int(out_count)} result(s) outside reference range"),
            unsafe_allow_html=True
        )
        out_df = labs[labs["out_of_range"]].copy()
        out_df["status"] = out_df.apply(
            lambda r: "LOW" if pd.notna(r["reference_low"]) and r["value"] < r["reference_low"] else "HIGH",
            axis=1,
        )
        st.dataframe(
            out_df[["panel_date", "test_name", "value", "unit", "reference_low", "reference_high", "status"]],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.markdown(
            success_card("All results within reference range"),
            unsafe_allow_html=True
        )

st.markdown(section_header("Biomarker Trends"), unsafe_allow_html=True)

test_names = sorted(labs["test_name"].unique().tolist())
if not test_names:
    st.stop()

selected_tests = st.multiselect(
    "Select biomarkers",
    test_names,
    default=test_names[:min(6, len(test_names))],
    label_visibility="collapsed",
)

for test in selected_tests:
    subset = labs[labs["test_name"] == test].sort_values("panel_date")
    if subset.empty:
        continue

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=subset["panel_date"],
            y=subset["value"],
            mode="lines+markers",
            name=test,
            line=dict(width=2, color=THEME_PRIMARY),
            marker=dict(size=6),
        )
    )

    row0 = subset.iloc[0]
    lo, hi = row0.get("reference_low"), row0.get("reference_high")
    if pd.notna(lo) and pd.notna(hi):
        fig.add_hrect(
            y0=lo, y1=hi,
            fillcolor="rgba(52, 211, 153, 0.06)",
            line_width=0,
        )
        fig.add_hline(y=lo, line_dash="dash", line_color=COLOR_WARNING, line_width=1)
        fig.add_hline(y=hi, line_dash="dash", line_color=COLOR_WARNING, line_width=1)

    unit = row0.get("unit", "")
    y_title = f"{test} ({unit})" if unit else test
    fig.update_layout(
        title={"text": test, "font": {"family": "Inter, -apple-system, sans-serif", "size": 13, "color": "#d4d4d8"}},
        xaxis_title="Date",
        yaxis_title=y_title,
        paper_bgcolor=CHART_PAPER_BG,
        plot_bgcolor=CHART_BG,
        font={"family": "Inter, -apple-system, sans-serif", "color": "#a1a1aa"},
        xaxis={"gridcolor": CHART_GRID_COLOR},
        yaxis={"gridcolor": CHART_GRID_COLOR},
        hovermode="x unified",
        margin=dict(t=50, b=40, l=50, r=20),
    )
    st.plotly_chart(fig, use_container_width=True)

with st.expander("All lab results"):
    st.dataframe(labs, use_container_width=True, hide_index=True)
