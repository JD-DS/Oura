"""Reusable Plotly chart builders for the Oura Health Dashboard.

All theme colors, thresholds, and defaults come from config.py.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from config import (
    CHART_TEMPLATE,
    COLOR_BAD,
    COLOR_GOOD,
    COLOR_WARNING,
    ROLLING_WINDOW_DAYS,
    SLEEP_STAGE_COLORS,
    SPARKLINE_HEIGHT,
)


def score_kpi(label: str, value, delta=None, suffix: str = ""):
    """Render a metric card using st.metric."""
    display = f"{value}{suffix}" if value is not None else "N/A"
    st.metric(label=label, value=display, delta=delta)


def sparkline(values: list, height: int | None = None) -> go.Figure:
    h = height or SPARKLINE_HEIGHT
    fig = go.Figure(
        go.Scatter(
            y=values,
            mode="lines",
            line=dict(width=2),
            fill="tozeroy",
            fillcolor="rgba(108,99,255,0.15)",
        )
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=h,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        template=CHART_TEMPLATE,
        showlegend=False,
    )
    return fig


def sleep_architecture_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for stage, color in SLEEP_STAGE_COLORS.items():
        label = stage.replace("_h", "").title()
        fig.add_trace(go.Bar(x=df["day"], y=df[stage], name=label, marker_color=color))
    fig.update_layout(
        barmode="stack",
        title="Sleep Architecture",
        xaxis_title="Date",
        yaxis_title="Hours",
        template=CHART_TEMPLATE,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig


def trend_line(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    rolling_window: int | None = None,
    y_label: str | None = None,
) -> go.Figure:
    window = rolling_window or ROLLING_WINDOW_DAYS
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=df[x], y=df[y], mode="markers+lines", name=y_label or y, opacity=0.6)
    )
    if len(df) >= window:
        rolling = df[y].rolling(window, min_periods=1).mean()
        fig.add_trace(
            go.Scatter(
                x=df[x],
                y=rolling,
                mode="lines",
                name=f"{window}-day avg",
                line=dict(width=3),
            )
        )
    fig.update_layout(
        title=title, xaxis_title="Date", yaxis_title=y_label or y, template=CHART_TEMPLATE
    )
    return fig


def grouped_bar(
    df: pd.DataFrame, x: str, y_cols: list[tuple[str, str, str]], title: str
) -> go.Figure:
    """Grouped bar chart. y_cols is list of (column, name, color)."""
    fig = go.Figure()
    for col, name, color in y_cols:
        fig.add_trace(go.Bar(x=df[x], y=df[col], name=name, marker_color=color))
    fig.update_layout(barmode="group", title=title, template=CHART_TEMPLATE)
    return fig


def scatter_with_trend(
    df: pd.DataFrame, x: str, y: str, title: str, x_label: str = "", y_label: str = ""
) -> go.Figure:
    fig = px.scatter(
        df,
        x=x,
        y=y,
        trendline="ols",
        title=title,
        labels={x: x_label or x, y: y_label or y},
        template=CHART_TEMPLATE,
    )
    return fig


def correlation_matrix(df: pd.DataFrame, columns: list[str] | None = None) -> go.Figure:
    if columns:
        df = df[columns]
    corr = df.select_dtypes(include="number").corr()
    fig = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title="Correlation Matrix",
        template=CHART_TEMPLATE,
        aspect="auto",
    )
    return fig


def calendar_heatmap(df: pd.DataFrame, date_col: str, value_col: str, title: str) -> go.Figure:
    if df.empty:
        return go.Figure()

    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df["weekday"] = df[date_col].dt.dayofweek
    df["week"] = df[date_col].dt.isocalendar().week.astype(int)

    fig = px.scatter(
        df,
        x="week",
        y="weekday",
        color=value_col,
        size=[12] * len(df),
        color_continuous_scale="RdYlGn",
        title=title,
        labels={"weekday": "Day of Week", "week": "Week"},
        template=CHART_TEMPLATE,
    )
    fig.update_yaxes(
        tickvals=list(range(7)),
        ticktext=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        autorange="reversed",
    )
    return fig


def anomaly_timeline(
    df: pd.DataFrame,
    date_col: str,
    metric_col: str,
    window: int = 14,
    threshold: float = 2.0,
    title: str = "",
) -> go.Figure:
    if df.empty or metric_col not in df.columns:
        return go.Figure()

    df = df.copy().dropna(subset=[metric_col])
    rolling_mean = df[metric_col].rolling(window, min_periods=3).mean()
    rolling_std = df[metric_col].rolling(window, min_periods=3).std()
    upper = rolling_mean + threshold * rolling_std
    lower = rolling_mean - threshold * rolling_std
    z_scores = (df[metric_col] - rolling_mean) / rolling_std.replace(0, np.nan)
    anomalies = z_scores.abs() > threshold

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=df[date_col], y=upper, mode="lines", line=dict(width=0), showlegend=False)
    )
    fig.add_trace(
        go.Scatter(
            x=df[date_col],
            y=lower,
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(108,99,255,0.15)",
            name=f"{threshold}\u03c3 band",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df[date_col], y=df[metric_col], mode="lines+markers", name=metric_col, opacity=0.8
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df[date_col],
            y=rolling_mean,
            mode="lines",
            name=f"{window}-day mean",
            line=dict(dash="dash"),
        )
    )
    if anomalies.any():
        anom_df = df[anomalies]
        fig.add_trace(
            go.Scatter(
                x=anom_df[date_col],
                y=anom_df[metric_col],
                mode="markers",
                marker=dict(size=12, color="red", symbol="x"),
                name="Anomaly",
            )
        )
    fig.update_layout(title=title or f"{metric_col} Anomaly Detection", template=CHART_TEMPLATE)
    return fig


def pie_chart(labels: list, values: list, title: str, colors: dict | None = None) -> go.Figure:
    fig = px.pie(
        names=labels,
        values=values,
        title=title,
        color=labels,
        color_discrete_map=colors or {},
        template=CHART_TEMPLATE,
    )
    return fig


def contributor_bar(names: list[str], values: list[float], title: str) -> go.Figure:
    """Horizontal bar chart colored by value thresholds."""
    from config import READINESS_CONTRIBUTOR_LOW, READINESS_CONTRIBUTOR_MED

    colors = [
        COLOR_BAD if v < READINESS_CONTRIBUTOR_LOW
        else COLOR_WARNING if v < READINESS_CONTRIBUTOR_MED
        else COLOR_GOOD
        for v in values
    ]
    fig = go.Figure(go.Bar(x=values, y=names, orientation="h", marker_color=colors))
    fig.update_layout(title=title, xaxis_title="Average Score", template=CHART_TEMPLATE)
    return fig
