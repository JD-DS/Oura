"""Page 6: Correlations Engine -- cross-metric analysis."""

import streamlit as st
import pandas as pd
import plotly.express as px

from config import (
    CHART_TEMPLATE,
    CORRELATION_MAX_LAG_DAYS,
    CORRELATION_MODERATE,
    CORRELATION_STRONG,
    default_end_date,
    default_start_date,
)
from components.data import get_all_daily_data_with_imported
from components.charts import scatter_with_trend, correlation_matrix

token = st.session_state.get("access_token", "")
sandbox = st.session_state.get("sandbox_mode", False)
start = st.session_state.get("start_date", str(default_start_date()))
end = st.session_state.get("end_date", str(default_end_date()))

st.header("Correlations Engine")
st.caption("Includes Oura metrics and imported data (steps, calories, workouts) when available.")

daily = get_all_daily_data_with_imported(token, start, end, sandbox)

if daily.empty:
    st.info("No data available. Try expanding the date range or enabling sandbox mode.")
    st.stop()

numeric_cols = daily.select_dtypes(include="number").columns.tolist()
numeric_cols = [c for c in numeric_cols if daily[c].notna().sum() >= 3]

if len(numeric_cols) < 2:
    st.warning("Not enough numeric data for correlations.")
    st.stop()

st.subheader("Metric Pair Analysis")

col1, col2 = st.columns(2)
with col1:
    metric_x = st.selectbox("X-axis metric", numeric_cols, index=0)
with col2:
    default_y = min(1, len(numeric_cols) - 1)
    metric_y = st.selectbox("Y-axis metric", numeric_cols, index=default_y)

pair_df = daily[[metric_x, metric_y]].dropna()

if len(pair_df) >= 3:
    fig = scatter_with_trend(
        pair_df, metric_x, metric_y, f"{metric_x} vs {metric_y}",
        x_label=metric_x.replace("_", " ").title(),
        y_label=metric_y.replace("_", " ").title(),
    )
    st.plotly_chart(fig, use_container_width=True)

    corr_val = pair_df[metric_x].corr(pair_df[metric_y])
    strength = (
        "strong" if abs(corr_val) > CORRELATION_STRONG
        else "moderate" if abs(corr_val) > CORRELATION_MODERATE
        else "weak"
    )
    direction = "positive" if corr_val > 0 else "negative"
    st.markdown(f"**Pearson r = {corr_val:.3f}** ({strength} {direction} correlation, n={len(pair_df)})")
else:
    st.warning("Not enough overlapping data points for these metrics.")

st.subheader("Correlation Matrix")
matrix_cols = st.multiselect(
    "Select metrics for correlation matrix", numeric_cols,
    default=numeric_cols[:min(8, len(numeric_cols))],
)

if len(matrix_cols) >= 2:
    fig = correlation_matrix(daily, matrix_cols)
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Time-Lagged Correlations")
st.caption("Does metric X today predict metric Y tomorrow (or vice versa)?")

col1, col2, col3 = st.columns(3)
with col1:
    lag_x = st.selectbox("Lead metric", numeric_cols, index=0, key="lag_x")
with col2:
    lag_y = st.selectbox("Lagged metric", numeric_cols, index=min(1, len(numeric_cols) - 1), key="lag_y")
with col3:
    max_lag = st.slider("Max lag (days)", 1, 7, CORRELATION_MAX_LAG_DAYS)

lag_results = []
for lag in range(-max_lag, max_lag + 1):
    shifted = daily[lag_y].shift(-lag)
    valid = pd.DataFrame({"x": daily[lag_x], "y": shifted}).dropna()
    if len(valid) >= 5:
        r = valid["x"].corr(valid["y"])
        lag_results.append({"lag": lag, "correlation": r, "n": len(valid)})

if lag_results:
    lag_df = pd.DataFrame(lag_results)
    fig = px.bar(
        lag_df, x="lag", y="correlation",
        title=f"Cross-correlation: {lag_x} leading {lag_y}",
        labels={"lag": f"Lag (days, positive = {lag_x} leads)", "correlation": "Pearson r"},
        template=CHART_TEMPLATE, color="correlation", color_continuous_scale="RdBu_r", range_color=[-1, 1],
    )
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    st.plotly_chart(fig, use_container_width=True)

    best = lag_df.loc[lag_df["correlation"].abs().idxmax()]
    st.markdown(f"**Strongest correlation:** r={best['correlation']:.3f} at lag={int(best['lag'])} days (n={int(best['n'])})")
else:
    st.warning("Not enough data for time-lagged analysis.")
