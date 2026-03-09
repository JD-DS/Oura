"""Page 10: Lab Results — biomarker trends, reference ranges, out-of-range flags."""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from config import CHART_TEMPLATE, COLOR_WARNING
from components.data import get_lab_results_df

st.set_page_config(page_title="Lab Results", page_icon="🧪", layout="wide")

# Labs use longer default range since draws are infrequent
labs_start_default = str(date.today() - timedelta(days=365))
labs_end_default = str(date.today())

start = st.session_state.get("start_date", labs_start_default)
end = st.session_state.get("end_date", labs_end_default)

st.header("Lab Results")
st.caption(
    "Biomarker trends from imported blood panel PDFs. Upload PDFs on the Import Data page."
)

try:
    from config import DATA_DIR_ABSOLUTE

    labs = get_lab_results_df(DATA_DIR_ABSOLUTE, start, end)
except Exception as e:
    st.error(str(e))
    st.stop()

if labs.empty:
    st.info(
        "No lab results for this date range. Upload blood panel PDFs on the "
        "**Import Data** page (Lab Results tab)."
    )
    st.stop()

# Out-of-range summary
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
        st.warning(f"**{int(out_count)}** result(s) outside reference range")
        out_df = labs[labs["out_of_range"]].copy()
        out_df["status"] = out_df.apply(
            lambda r: "LOW" if r["reference_low"] is not None and r["value"] < r["reference_low"] else "HIGH",
            axis=1,
        )
        st.dataframe(
            out_df[["panel_date", "test_name", "value", "unit", "reference_low", "reference_high", "status"]],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.success("All results within reference range")

# Biomarker trend charts
test_names = sorted(labs["test_name"].unique().tolist())
if not test_names:
    st.stop()

selected_tests = st.multiselect(
    "Select biomarkers to plot",
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
            line=dict(width=2),
        )
    )

    # Reference range bands if available
    row0 = subset.iloc[0]
    lo, hi = row0.get("reference_low"), row0.get("reference_high")
    if lo is not None and hi is not None:
        fig.add_hrect(y0=lo, y1=hi, fillcolor="rgba(102, 187, 106, 0.15)", line_width=0)
        fig.add_hline(y=lo, line_dash="dash", line_color=COLOR_WARNING)
        fig.add_hline(y=hi, line_dash="dash", line_color=COLOR_WARNING)

    unit = row0.get("unit", "")
    y_title = f"{test} ({unit})" if unit else test
    fig.update_layout(
        title=f"{test} over time",
        xaxis_title="Panel date",
        yaxis_title=y_title,
        template=CHART_TEMPLATE,
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

st.subheader("All lab results")
st.dataframe(labs, use_container_width=True, hide_index=True)
