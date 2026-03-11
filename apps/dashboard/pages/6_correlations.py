"""Page 6: Correlations Engine -- cross-metric analysis."""

from datetime import date, timedelta

import streamlit as st
import pandas as pd
import plotly.express as px

from config import (
    CHART_TEMPLATE,
    CORRELATION_MAX_LAG_DAYS,
    CORRELATION_MODERATE,
    CORRELATION_STRONG,
    DATA_DIR_ABSOLUTE,
    default_end_date,
    default_start_date,
)
from components.data import get_all_daily_data_with_imported, get_lab_results_df
from components.charts import scatter_with_trend, correlation_matrix
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
        "Correlations Engine",
        "Discover relationships between your health metrics, imported data, and biomarkers"
    ),
    unsafe_allow_html=True
)

with st.expander("⚙️ Data merge settings"):
    dedup_strategy = st.radio(
        "How to handle overlapping Oura and imported data (steps, calories):",
        options=["both", "oura_primary", "imported_primary", "average"],
        index=0,
        format_func=lambda x: {
            "both": "Keep both sources as separate columns",
            "oura_primary": "Use Oura, fill gaps with imported",
            "imported_primary": "Use imported, fill gaps with Oura",
            "average": "Average overlapping values",
        }[x],
        horizontal=True,
    )

daily = get_all_daily_data_with_imported(token, start, end, sandbox, dedup_strategy=dedup_strategy)

if daily.empty:
    st.markdown(
        info_box("No data available. Try expanding the date range or enabling sandbox mode."),
        unsafe_allow_html=True
    )
    st.stop()

numeric_cols = daily.select_dtypes(include="number").columns.tolist()
numeric_cols = [c for c in numeric_cols if daily[c].notna().sum() >= 3]

if len(numeric_cols) < 2:
    st.warning("Not enough numeric data for correlations.")
    st.stop()

st.markdown(section_header("Metric Pair Analysis"), unsafe_allow_html=True)

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
    
    color = "#66BB6A" if abs(corr_val) > CORRELATION_STRONG else "#FFA726" if abs(corr_val) > CORRELATION_MODERATE else "#9CA3AF"
    st.markdown(f"""
    <div style="
        background: rgba(30, 30, 40, 0.7);
        border-left: 4px solid {color};
        border-radius: 0 8px 8px 0;
        padding: 1rem;
        margin: 0.5rem 0;
    ">
        <strong>Pearson r = {corr_val:.3f}</strong>
        <span style="color: #9CA3AF;"> — {strength} {direction} correlation (n={len(pair_df)})</span>
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("Not enough overlapping data points for these metrics.")

st.markdown(section_header("Correlation Matrix"), unsafe_allow_html=True)
matrix_cols = st.multiselect(
    "Select metrics for correlation matrix",
    numeric_cols,
    default=numeric_cols[:min(8, len(numeric_cols))],
)

if len(matrix_cols) >= 2:
    fig = correlation_matrix(daily, matrix_cols)
    st.plotly_chart(fig, use_container_width=True)

st.markdown(section_header("Time-Lagged Correlations"), unsafe_allow_html=True)
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
        template=CHART_TEMPLATE,
        color="correlation",
        color_continuous_scale="RdBu_r",
        range_color=[-1, 1],
    )
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    st.plotly_chart(fig, use_container_width=True)

    best = lag_df.loc[lag_df["correlation"].abs().idxmax()]
    st.markdown(f"""
    <div style="
        background: rgba(108, 99, 255, 0.1);
        border: 1px solid rgba(108, 99, 255, 0.3);
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
    ">
        <strong>Strongest correlation:</strong> r={best['correlation']:.3f} at lag={int(best['lag'])} days (n={int(best['n'])})
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("Not enough data for time-lagged analysis.")

st.markdown(section_header("Lab Biomarker Correlations"), unsafe_allow_html=True)
st.caption(
    "Correlate blood panel results with Oura metrics. Uses a wider date range (1 year) "
    "and averages Oura metrics around each lab draw date."
)

labs_start = str(date.today() - timedelta(days=365))
labs_end = str(date.today())
labs = get_lab_results_df(DATA_DIR_ABSOLUTE, labs_start, labs_end)

if labs.empty:
    st.markdown(
        info_box("No lab results imported. Upload blood panel PDFs on the <strong>Import Data</strong> page."),
        unsafe_allow_html=True
    )
else:
    test_names = sorted(labs["test_name"].unique().tolist())
    if len(test_names) == 0:
        st.markdown(
            info_box("No biomarkers found in lab results."),
            unsafe_allow_html=True
        )
    else:
        oura_metrics = [c for c in numeric_cols if c not in ("day",)]
        if not oura_metrics:
            st.warning("No Oura metrics available for correlation.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                selected_biomarker = st.selectbox("Biomarker", test_names)
            with col2:
                window_days = st.slider("Oura window (days around draw)", 1, 14, 7, key="lab_window")

            bio_df = labs[labs["test_name"] == selected_biomarker].copy()
            bio_df = bio_df.dropna(subset=["value", "panel_date"])
            bio_df["panel_date"] = pd.to_datetime(bio_df["panel_date"], errors="coerce")
            bio_df = bio_df.dropna(subset=["panel_date"]).sort_values("panel_date")

            if bio_df.empty or len(bio_df) < 2:
                st.markdown(
                    info_box(f"Need at least 2 data points for {selected_biomarker} to compute correlations."),
                    unsafe_allow_html=True
                )
            else:
                daily["day_dt"] = pd.to_datetime(daily["day"], errors="coerce")
                corr_data = []
                for _, row in bio_df.iterrows():
                    draw_date = row["panel_date"]
                    mask = (daily["day_dt"] >= draw_date - pd.Timedelta(days=window_days)) & \
                           (daily["day_dt"] <= draw_date + pd.Timedelta(days=window_days))
                    window_data = daily[mask]
                    if window_data.empty:
                        continue
                    entry = {"panel_date": draw_date, "biomarker_value": row["value"]}
                    for m in oura_metrics:
                        if m in window_data.columns:
                            entry[m] = window_data[m].mean()
                    corr_data.append(entry)

                if len(corr_data) < 2:
                    st.markdown(
                        info_box("Not enough overlapping Oura data around lab draws."),
                        unsafe_allow_html=True
                    )
                else:
                    corr_df = pd.DataFrame(corr_data)
                    avail_metrics = [m for m in oura_metrics if m in corr_df.columns and corr_df[m].notna().sum() >= 2]

                    if not avail_metrics:
                        st.markdown(
                            info_box("No Oura metrics have enough data points around lab draws."),
                            unsafe_allow_html=True
                        )
                    else:
                        correlations = []
                        for m in avail_metrics:
                            valid = corr_df[["biomarker_value", m]].dropna()
                            if len(valid) >= 2:
                                r = valid["biomarker_value"].corr(valid[m])
                                correlations.append({"metric": m, "correlation": r, "n": len(valid)})

                        if correlations:
                            corr_result = pd.DataFrame(correlations).sort_values("correlation", key=abs, ascending=False)
                            st.dataframe(
                                corr_result.style.background_gradient(subset=["correlation"], cmap="RdBu_r", vmin=-1, vmax=1),
                                use_container_width=True,
                                hide_index=True,
                            )

                            top = corr_result.iloc[0]
                            top_metric = top["metric"]
                            if top_metric in corr_df.columns:
                                fig = scatter_with_trend(
                                    corr_df[["biomarker_value", top_metric]].dropna(),
                                    "biomarker_value", top_metric,
                                    f"{selected_biomarker} vs {top_metric}",
                                    x_label=selected_biomarker,
                                    y_label=top_metric.replace("_", " ").title(),
                                )
                                st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.markdown(
                                info_box("Could not compute correlations with available data."),
                                unsafe_allow_html=True
                            )
