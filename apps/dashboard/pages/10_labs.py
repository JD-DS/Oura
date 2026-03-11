"""Page 10: Lab Results — biomarker trends, reference ranges, out-of-range flags."""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from config import CHART_TEMPLATE, COLOR_WARNING
from components.data import get_lab_results_df
from styles import (
    get_custom_css,
    main_header,
    section_header,
    info_box,
    warning_box,
    success_box,
)

st.markdown(get_custom_css(), unsafe_allow_html=True)

labs_start_default = str(date.today() - timedelta(days=365))
labs_end_default = str(date.today())

start = st.session_state.get("start_date", labs_start_default)
end = st.session_state.get("end_date", labs_end_default)

st.markdown(
    main_header(
        "Lab Results",
        "Track your biomarkers over time with reference ranges and trend analysis"
    ),
    unsafe_allow_html=True
)

try:
    from config import DATA_DIR_ABSOLUTE
    labs = get_lab_results_df(DATA_DIR_ABSOLUTE, start, end)
except Exception as e:
    st.error(str(e))
    st.stop()

if labs.empty:
    st.markdown(
        info_box(
            "No lab results for this date range. Upload blood panel PDFs on the "
            "<strong>Import Data</strong> page (Lab Results tab)."
        ),
        unsafe_allow_html=True
    )
    st.stop()

st.markdown(section_header("Reference Range Status"), unsafe_allow_html=True)

if "reference_low" in labs.columns and "reference_high" in labs.columns:
    def is_out_of_range(row):
        v = row.get("value")
        lo, hi = row.get("reference_low"), row.get("reference_high")
        if pd.isna(v):
            return False
        if lo is not None and v < lo:
            return True
        if hi is not None and v > hi:
            return True
        return False

    labs["out_of_range"] = labs.apply(is_out_of_range, axis=1)
    out_count = labs["out_of_range"].sum()
    
    if out_count > 0:
        st.markdown(
            warning_box(f"⚠️ <strong>{int(out_count)}</strong> result(s) outside reference range"),
            unsafe_allow_html=True
        )
        out_df = labs[labs["out_of_range"]].copy()
        out_df["status"] = out_df.apply(
            lambda r: "🔻 LOW" if r["reference_low"] is not None and r["value"] < r["reference_low"] else "🔺 HIGH",
            axis=1,
        )
        st.dataframe(
            out_df[["panel_date", "test_name", "value", "unit", "reference_low", "reference_high", "status"]],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.markdown(
            success_box("✓ All results within reference range"),
            unsafe_allow_html=True
        )

st.markdown(section_header("Biomarker Trends"), unsafe_allow_html=True)

test_names = sorted(labs["test_name"].unique().tolist())
if not test_names:
    st.stop()

selected_tests = st.multiselect(
    "Select biomarkers to visualize",
    test_names,
    default=test_names[: min(6, len(test_names))],
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
            line=dict(width=2, color="#6C63FF"),
            marker=dict(size=8),
        )
    )

    row0 = subset.iloc[0]
    lo, hi = row0.get("reference_low"), row0.get("reference_high")
    if lo is not None and hi is not None:
        fig.add_hrect(
            y0=lo, y1=hi,
            fillcolor="rgba(102, 187, 106, 0.1)",
            line_width=0,
            annotation_text="Normal range",
            annotation_position="top left",
        )
        fig.add_hline(y=lo, line_dash="dash", line_color=COLOR_WARNING, line_width=1)
        fig.add_hline(y=hi, line_dash="dash", line_color=COLOR_WARNING, line_width=1)

    unit = row0.get("unit", "")
    y_title = f"{test} ({unit})" if unit else test
    fig.update_layout(
        title=dict(
            text=f"{test}",
            font=dict(size=16, color="#E0E0E0"),
        ),
        xaxis_title="Panel date",
        yaxis_title=y_title,
        template=CHART_TEMPLATE,
        hovermode="x unified",
        margin=dict(t=40, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown(section_header("All Lab Results"), unsafe_allow_html=True)

with st.expander("📋 View complete data table"):
    st.dataframe(labs, use_container_width=True, hide_index=True)
