"""Page 6: Correlations Engine -- cross-metric analysis."""

from datetime import date, timedelta

import streamlit as st
import pandas as pd
import plotly.express as px

from config import (
    CHART_BG,
    CHART_GRID_COLOR,
    CHART_PAPER_BG,
    CORRELATION_MAX_LAG_DAYS,
    CORRELATION_MODERATE,
    CORRELATION_STRONG,
    DATA_DIR_ABSOLUTE,
    THEME_PRIMARY,
    THEME_SECONDARY,
    default_end_date,
    default_start_date,
)
from components.data import get_all_daily_data_with_imported, get_lab_results_df
from components.charts import scatter_with_trend, correlation_matrix
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
    page_header("Correlations", "Discover relationships between your health metrics", theme_mode),
    unsafe_allow_html=True
)

daily = get_all_daily_data_with_imported(token, start, end, sandbox)

if daily.empty:
    st.markdown(
        info_card("No data available. Try expanding the date range or enabling demo mode.", theme_mode),
        unsafe_allow_html=True
    )
    st.stop()

numeric_cols = daily.select_dtypes(include="number").columns.tolist()
numeric_cols = [c for c in numeric_cols if daily[c].notna().sum() >= 3]

if len(numeric_cols) < 2:
    st.warning("Not enough numeric data for correlations.")
    st.stop()

st.markdown(section_header("Metric Pair Analysis", theme_mode), unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    metric_x = st.selectbox("X-axis metric", numeric_cols, index=0)
with col2:
    default_y = min(1, len(numeric_cols) - 1)
    metric_y = st.selectbox("Y-axis metric", numeric_cols, index=default_y)

pair_df = daily[[metric_x, metric_y]].dropna()

if len(pair_df) >= 3:
    fig = scatter_with_trend(
        pair_df, metric_x, metric_y, "",
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
    
    color = "#34d399" if abs(corr_val) > CORRELATION_STRONG else "#fbbf24" if abs(corr_val) > CORRELATION_MODERATE else "#71717a"
    outer = f"background:#16161c;border-left:3px solid {color};border-radius:0 8px 8px 0;padding:1rem 1.25rem;margin:.5rem 0;font-family:Inter,-apple-system,sans-serif;"
    st.markdown(
        f'<div style="{outer}">'
        f'<span style="font-family:\'JetBrains Mono\',monospace;color:#f0f0f2;font-weight:600;">r = {corr_val:.3f}</span>'
        f'<span style="color:#71717a;"> — {strength} {direction} correlation (n={len(pair_df)})</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
else:
    st.warning("Not enough overlapping data points for these metrics.")

st.markdown(section_header("Correlation Matrix", theme_mode), unsafe_allow_html=True)
matrix_cols = st.multiselect(
    "Select metrics",
    numeric_cols,
    default=numeric_cols[:min(8, len(numeric_cols))],
    label_visibility="collapsed",
)

if len(matrix_cols) >= 2:
    fig = correlation_matrix(daily, matrix_cols)
    st.plotly_chart(fig, use_container_width=True)

st.markdown(section_header("Time-Lagged Correlations", theme_mode), unsafe_allow_html=True)
st.caption("Does metric X today predict metric Y tomorrow?")

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
    colorscale = [[0, THEME_SECONDARY], [0.5, "#16161c"], [1, THEME_PRIMARY]]
    fig = px.bar(
        lag_df, x="lag", y="correlation",
        labels={"lag": "Lag (days)", "correlation": "Pearson r"},
        color="correlation",
        color_continuous_scale=colorscale,
        range_color=[-1, 1],
    )
    fig.add_hline(y=0, line_dash="dash", line_color="#52525b")
    fig.update_layout(
        paper_bgcolor=CHART_PAPER_BG,
        plot_bgcolor=CHART_BG,
        font={"family": "Inter, -apple-system, sans-serif", "color": "#a1a1aa"},
        xaxis={"gridcolor": CHART_GRID_COLOR},
        yaxis={"gridcolor": CHART_GRID_COLOR},
        margin=dict(t=20, b=40, l=50, r=20),
    )
    st.plotly_chart(fig, use_container_width=True)

    best = lag_df.loc[lag_df["correlation"].abs().idxmax()]
    lag_outer = "background:rgba(45,212,191,0.04);border:1px solid rgba(45,212,191,0.15);border-radius:8px;padding:.75rem 1rem;font-family:Inter,-apple-system,sans-serif;"
    st.markdown(
        f'<div style="{lag_outer}">'
        f'<strong style="color:#2dd4bf;">Strongest:</strong>'
        f'<span style="font-family:\'JetBrains Mono\',monospace;color:#f0f0f2;"> r={best["correlation"]:.3f}</span>'
        f'<span style="color:#71717a;"> at lag={int(best["lag"])} days (n={int(best["n"])})</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
else:
    st.warning("Not enough data for time-lagged analysis.")

st.markdown(section_header("Lab Biomarker Correlations", theme_mode), unsafe_allow_html=True)

labs_start = str(date.today() - timedelta(days=365))
labs_end = str(date.today())
labs = get_lab_results_df(DATA_DIR_ABSOLUTE, labs_start, labs_end)

if labs.empty:
    st.markdown(
        info_card("No lab results imported. Upload blood panel PDFs on the Import page.", theme_mode),
        unsafe_allow_html=True
    )
else:
    test_names = sorted(labs["test_name"].unique().tolist())
    if len(test_names) == 0:
        st.markdown(
            info_card("No biomarkers found in lab results.", theme_mode),
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
                window_days = st.slider("Window (days)", 1, 14, 7, key="lab_window")

            bio_df = labs[labs["test_name"] == selected_biomarker].copy()
            bio_df = bio_df.dropna(subset=["value", "panel_date"])
            bio_df["panel_date"] = pd.to_datetime(bio_df["panel_date"], errors="coerce")
            bio_df = bio_df.dropna(subset=["panel_date"]).sort_values("panel_date")

            if bio_df.empty or len(bio_df) < 2:
                st.markdown(
                    info_card(f"Need at least 2 data points for {selected_biomarker}.", theme_mode),
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
                        info_card("Not enough overlapping Oura data around lab draws.", theme_mode),
                        unsafe_allow_html=True
                    )
                else:
                    corr_df = pd.DataFrame(corr_data)
                    avail_metrics = [m for m in oura_metrics if m in corr_df.columns and corr_df[m].notna().sum() >= 2]

                    if not avail_metrics:
                        st.markdown(
                            info_card("No Oura metrics have enough data points.", theme_mode),
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
                            st.dataframe(corr_result, use_container_width=True, hide_index=True)

                            top = corr_result.iloc[0]
                            top_metric = top["metric"]
                            if top_metric in corr_df.columns:
                                fig = scatter_with_trend(
                                    corr_df[["biomarker_value", top_metric]].dropna(),
                                    "biomarker_value", top_metric,
                                    "",
                                    x_label=selected_biomarker,
                                    y_label=top_metric.replace("_", " ").title(),
                                )
                                st.plotly_chart(fig, use_container_width=True)
