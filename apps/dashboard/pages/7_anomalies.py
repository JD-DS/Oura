"""Page 7: Health Anomaly Detection -- rolling z-scores and early warning."""

from datetime import date, timedelta

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from config import (
    ANOMALY_WINDOW_DAYS,
    ANOMALY_Z_THRESHOLD,
    CHART_BG,
    CHART_GRID_COLOR,
    CHART_PAPER_BG,
    COLOR_WARNING,
    DATA_DIR_ABSOLUTE,
    THEME_PRIMARY,
    default_end_date,
    default_start_date,
)
from components.data import (
    get_all_daily_data_with_imported,
    get_lab_results_df,
    get_readiness_df,
    get_sleep_df,
)
from components.charts import anomaly_timeline
from styles import (
    get_custom_css,
    page_header,
    section_header,
    info_card,
    success_card,
    warning_card,
)

st.markdown(get_custom_css(), unsafe_allow_html=True)

token = st.session_state.get("access_token", "")
sandbox = st.session_state.get("sandbox_mode", False)
start = st.session_state.get("start_date", str(default_start_date()))
end = st.session_state.get("end_date", str(default_end_date()))

st.markdown(
    page_header("Anomalies", "Detect unusual patterns in your health metrics"),
    unsafe_allow_html=True
)

daily = get_all_daily_data_with_imported(token, start, end, sandbox)
sleep_df = get_sleep_df(token, start, end, sandbox)
readiness_df = get_readiness_df(token, start, end, sandbox)

if daily.empty:
    st.markdown(
        info_card("No data available. Try expanding the date range or enabling demo mode."),
        unsafe_allow_html=True
    )
    st.stop()

st.markdown(section_header("Detection Settings"), unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    window = st.slider("Rolling window (days)", 7, 30, ANOMALY_WINDOW_DAYS)
with col2:
    threshold = st.slider("Z-score threshold (σ)", 1.0, 3.0, ANOMALY_Z_THRESHOLD, 0.5)

st.markdown(section_header("Vital Signs"), unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    if "temp_dev" in readiness_df.columns and readiness_df["temp_dev"].notna().any():
        st.caption("Temperature Deviation")
        fig = anomaly_timeline(readiness_df, "day", "temp_dev", window, threshold, "")
        fig.update_layout(height=280, margin=dict(t=10, b=30, l=50, r=20))
        st.plotly_chart(fig, use_container_width=True)

    if not sleep_df.empty and "lowest_hr" in sleep_df.columns and sleep_df["lowest_hr"].notna().any():
        st.caption("Resting Heart Rate")
        fig = anomaly_timeline(sleep_df, "day", "lowest_hr", window, threshold, "")
        fig.update_layout(height=280, margin=dict(t=10, b=30, l=50, r=20))
        st.plotly_chart(fig, use_container_width=True)

with col2:
    if not sleep_df.empty and "avg_hrv" in sleep_df.columns and sleep_df["avg_hrv"].notna().any():
        st.caption("Heart Rate Variability")
        fig = anomaly_timeline(sleep_df, "day", "avg_hrv", window, threshold, "")
        fig.update_layout(height=280, margin=dict(t=10, b=30, l=50, r=20))
        st.plotly_chart(fig, use_container_width=True)

    if "spo2_avg" in daily.columns and daily["spo2_avg"].notna().any():
        st.caption("Blood Oxygen (SpO2)")
        fig = anomaly_timeline(daily, "day", "spo2_avg", window, threshold, "")
        fig.update_layout(height=280, margin=dict(t=10, b=30, l=50, r=20))
        st.plotly_chart(fig, use_container_width=True)

if "steps_imported" in daily.columns and daily["steps_imported"].notna().any():
    st.markdown(section_header("Steps (Imported)"), unsafe_allow_html=True)
    fig = anomaly_timeline(daily, "day", "steps_imported", window, threshold, "")
    st.plotly_chart(fig, use_container_width=True)

if "calories_imported" in daily.columns and daily["calories_imported"].notna().any():
    st.markdown(section_header("Calories (Imported)"), unsafe_allow_html=True)
    fig = anomaly_timeline(daily, "day", "calories_imported", window, threshold, "")
    st.plotly_chart(fig, use_container_width=True)

st.markdown(section_header("Illness Early Warning"), unsafe_allow_html=True)
st.caption("Flags days where temperature rises AND HRV declines — a pattern often associated with illness onset.")

if (
    not readiness_df.empty
    and not sleep_df.empty
    and "temp_dev" in readiness_df.columns
    and "avg_hrv" in sleep_df.columns
):
    temp_series = readiness_df.set_index("day")["temp_dev"]
    hrv_series = sleep_df.drop_duplicates("day").set_index("day")["avg_hrv"]
    combined = pd.DataFrame({"temp_dev": temp_series, "avg_hrv": hrv_series}).dropna()

    if len(combined) >= window:
        temp_roll = combined["temp_dev"].rolling(window, min_periods=3)
        hrv_roll = combined["avg_hrv"].rolling(window, min_periods=3)
        temp_z = (combined["temp_dev"] - temp_roll.mean()) / temp_roll.std().replace(0, np.nan)
        hrv_z = (combined["avg_hrv"] - hrv_roll.mean()) / hrv_roll.std().replace(0, np.nan)
        warnings = (temp_z > threshold) & (hrv_z < -threshold)
        warning_days = combined.index[warnings]

        if len(warning_days) > 0:
            st.markdown(
                warning_card(f"Potential illness signals on {len(warning_days)} day(s)"),
                unsafe_allow_html=True
            )
            for d in warning_days:
                st.markdown(f"- **{d}**: temp z={temp_z.loc[d]:.1f}σ, HRV z={hrv_z.loc[d]:.1f}σ")
        else:
            st.markdown(
                success_card("No illness warning signals detected"),
                unsafe_allow_html=True
            )
    else:
        st.caption(f"Need at least {window} days of data for illness detection.")
else:
    st.caption("Temperature and HRV data needed for illness detection.")

st.markdown(section_header("All Detected Anomalies"), unsafe_allow_html=True)

anomaly_metrics = []
imported_cols = [c for c in ["steps_imported", "calories_imported", "workouts_imported"] if c in daily.columns]
all_metrics = ["temp_dev", "avg_hrv", "lowest_hr", "spo2_avg"] + imported_cols
for col in all_metrics:
    source_df = readiness_df if col in readiness_df.columns else (
        sleep_df if not sleep_df.empty and col in sleep_df.columns else daily
    )
    if col not in source_df.columns or not source_df[col].notna().any():
        continue
    series = source_df[col].dropna()
    if len(series) < window:
        continue
    roll_mean = series.rolling(window, min_periods=3).mean()
    roll_std = series.rolling(window, min_periods=3).std()
    z = ((series - roll_mean) / roll_std.replace(0, np.nan)).abs()
    flagged = z > threshold
    if flagged.any():
        for idx in flagged[flagged].index:
            anomaly_metrics.append({
                "day": source_df.loc[idx, "day"],
                "metric": col.replace("_", " ").title(),
                "value": source_df.loc[idx, col],
                "z_score": z.loc[idx],
            })

if anomaly_metrics:
    anom_table = pd.DataFrame(anomaly_metrics).sort_values("day")
    st.dataframe(anom_table, use_container_width=True, hide_index=True)
else:
    st.markdown(
        success_card("No anomalies detected with the current settings"),
        unsafe_allow_html=True
    )

st.markdown(section_header("Lab Biomarker Trends"), unsafe_allow_html=True)

labs_start = str(date.today() - timedelta(days=730))
labs_end = str(date.today())
labs = get_lab_results_df(DATA_DIR_ABSOLUTE, labs_start, labs_end)

if labs.empty:
    st.markdown(
        info_card("No lab results imported. Upload blood panel PDFs on the Import page."),
        unsafe_allow_html=True
    )
else:
    test_names = sorted(labs["test_name"].unique().tolist())
    if not test_names:
        st.markdown(
            info_card("No biomarkers found."),
            unsafe_allow_html=True
        )
    else:
        selected_labs = st.multiselect(
            "Select biomarkers",
            test_names,
            default=test_names[:min(6, len(test_names))],
            key="anomaly_labs",
            label_visibility="collapsed",
        )

        lab_anomalies = []

        for test in selected_labs:
            subset = labs[labs["test_name"] == test].copy()
            subset = subset.dropna(subset=["value", "panel_date"])
            subset["panel_date"] = pd.to_datetime(subset["panel_date"], errors="coerce")
            subset = subset.dropna(subset=["panel_date"]).sort_values("panel_date")

            if len(subset) < 2:
                continue

            values = subset["value"].values
            dates = subset["panel_date"].values

            mean_val = np.mean(values[:-1]) if len(values) > 1 else values[0]
            std_val = np.std(values[:-1]) if len(values) > 1 else 0
            latest_val = values[-1]
            latest_date = dates[-1]

            z_score = (latest_val - mean_val) / std_val if std_val > 0 else 0

            ref_low = subset.iloc[0].get("reference_low")
            ref_high = subset.iloc[0].get("reference_high")

            status = "normal"
            if ref_low is not None and latest_val < ref_low:
                status = "LOW"
            elif ref_high is not None and latest_val > ref_high:
                status = "HIGH"
            elif abs(z_score) > threshold:
                status = "unusual"

            if len(values) >= 3:
                x = np.arange(len(values))
                slope, _ = np.polyfit(x, values, 1)
                pct_change = (slope * len(values)) / mean_val * 100 if mean_val != 0 else 0
            else:
                slope = 0
                pct_change = 0

            trend_direction = "stable"
            if pct_change > 10:
                trend_direction = "rising"
            elif pct_change < -10:
                trend_direction = "declining"

            if status != "normal" or trend_direction != "stable":
                lab_anomalies.append({
                    "biomarker": test,
                    "latest_value": latest_val,
                    "date": pd.Timestamp(latest_date).strftime("%Y-%m-%d"),
                    "z_score": round(z_score, 2),
                    "status": status,
                    "trend": trend_direction,
                    "change_pct": round(pct_change, 1),
                })

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=subset["panel_date"],
                y=subset["value"],
                mode="lines+markers",
                name=test,
                line=dict(width=2, color=THEME_PRIMARY),
                marker=dict(size=6),
            ))

            if ref_low is not None and ref_high is not None:
                fig.add_hrect(
                    y0=ref_low, y1=ref_high,
                    fillcolor="rgba(52, 211, 153, 0.06)",
                    line_width=0
                )
                fig.add_hline(y=ref_low, line_dash="dash", line_color=COLOR_WARNING, line_width=1)
                fig.add_hline(y=ref_high, line_dash="dash", line_color=COLOR_WARNING, line_width=1)

            if mean_val and std_val:
                fig.add_hline(
                    y=mean_val, line_dash="dot", line_color="#52525b",
                    annotation_text="baseline", annotation_position="right"
                )

            unit = subset.iloc[0].get("unit", "")
            y_title = f"{test} ({unit})" if unit else test
            trend_label = f" ({trend_direction})" if trend_direction != "stable" else ""
            fig.update_layout(
                title={"text": f"{test}{trend_label}", "font": {"family": "Inter, -apple-system, sans-serif", "size": 13, "color": "#d4d4d8"}},
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

        if lab_anomalies:
            st.markdown(
                warning_card(f"{len(lab_anomalies)} biomarker(s) flagged"),
                unsafe_allow_html=True
            )
            anom_df = pd.DataFrame(lab_anomalies)
            st.dataframe(anom_df, use_container_width=True, hide_index=True)
        elif selected_labs:
            st.markdown(
                success_card("All selected biomarkers within normal range"),
                unsafe_allow_html=True
            )
