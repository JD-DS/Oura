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
    CHART_BG,
    CHART_COLOR_SEQUENCE,
    CHART_GRID_COLOR,
    CHART_PAPER_BG,
    CHART_TEMPLATE,
    COLOR_BAD,
    COLOR_GOOD,
    COLOR_WARNING,
    ROLLING_WINDOW_DAYS,
    SLEEP_STAGE_COLORS,
    SPARKLINE_HEIGHT,
    THEME_PRIMARY,
    THEME_SECONDARY,
)


def _get_chart_layout() -> dict:
    """Return common layout settings for charts."""
    return {
        "template": CHART_TEMPLATE,
        "paper_bgcolor": CHART_PAPER_BG,
        "plot_bgcolor": CHART_BG,
        "font": {"family": "Inter, -apple-system, sans-serif", "color": "#a1a1aa", "size": 11},
        "title": {
            "font": {"family": "Inter, -apple-system, sans-serif", "size": 13, "color": "#d4d4d8", "weight": 600},
            "x": 0,
            "xanchor": "left",
            "pad": {"l": 4},
        },
        "xaxis": {
            "gridcolor": CHART_GRID_COLOR,
            "linecolor": "rgba(255, 255, 255, 0.03)",
            "tickfont": {"size": 10, "color": "#71717a"},
            "title_font": {"size": 10, "color": "#71717a"},
            "zeroline": False,
        },
        "yaxis": {
            "gridcolor": CHART_GRID_COLOR,
            "linecolor": "rgba(255, 255, 255, 0.03)",
            "tickfont": {"size": 10, "color": "#71717a"},
            "title_font": {"size": 10, "color": "#71717a"},
            "zeroline": False,
        },
        "legend": {
            "font": {"size": 10, "color": "#a1a1aa"},
            "bgcolor": "rgba(0,0,0,0)",
        },
        "hoverlabel": {
            "bgcolor": "#18181d",
            "bordercolor": "rgba(255, 255, 255, 0.08)",
            "font": {"family": "Inter, sans-serif", "color": "#fafafa", "size": 11},
        },
        "margin": {"t": 40, "b": 32, "l": 44, "r": 12},
        "hovermode": "x unified",
    }


def score_kpi(label: str, value, delta=None, suffix: str = ""):
    """Render a metric card using st.metric."""
    display = f"{value}{suffix}" if value is not None else "—"
    st.metric(label=label, value=display, delta=delta)


def sparkline(values: list, height: int | None = None) -> go.Figure:
    """Minimal sparkline chart."""
    h = height or SPARKLINE_HEIGHT
    fig = go.Figure(
        go.Scatter(
            y=values,
            mode="lines",
            line=dict(width=1.5, color=THEME_PRIMARY, shape="spline"),
            fill="tozeroy",
            fillcolor="rgba(45, 212, 191, 0.05)",
        )
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=h,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )
    return fig


def sleep_architecture_chart(df: pd.DataFrame) -> go.Figure:
    """Stacked bar chart for sleep stages."""
    fig = go.Figure()
    for stage, color in SLEEP_STAGE_COLORS.items():
        label = stage.replace("_h", "").title()
        fig.add_trace(go.Bar(x=df["day"], y=df[stage], name=label, marker_color=color))
    
    layout = _get_chart_layout()
    layout.update({
        "barmode": "stack",
        "title": {"text": "Sleep Architecture"},
        "xaxis_title": "Date",
        "yaxis_title": "Hours",
        "legend": {"orientation": "h", "yanchor": "bottom", "y": 1.02, "font": {"size": 11}},
    })
    fig.update_layout(**layout)
    return fig


def trend_line(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    rolling_window: int | None = None,
    y_label: str | None = None,
) -> go.Figure:
    """Line chart with rolling average overlay."""
    window = rolling_window or ROLLING_WINDOW_DAYS
    fig = go.Figure()
    
    # Data points
    fig.add_trace(
        go.Scatter(
            x=df[x],
            y=df[y],
            mode="markers+lines",
            name=y_label or y,
            line=dict(color=THEME_PRIMARY, width=1),
            marker=dict(size=5, color=THEME_PRIMARY),
            opacity=0.7,
        )
    )
    
    # Rolling average
    if len(df) >= window:
        rolling = df[y].rolling(window, min_periods=1).mean()
        fig.add_trace(
            go.Scatter(
                x=df[x],
                y=rolling,
                mode="lines",
                name=f"{window}-day avg",
                line=dict(width=2, color=THEME_SECONDARY),
            )
        )
    
    layout = _get_chart_layout()
    layout.update({
        "title": {"text": title},
        "xaxis_title": "Date",
        "yaxis_title": y_label or y,
    })
    fig.update_layout(**layout)
    return fig


def grouped_bar(
    df: pd.DataFrame, x: str, y_cols: list[tuple[str, str, str]], title: str
) -> go.Figure:
    """Grouped bar chart. y_cols is list of (column, name, color)."""
    fig = go.Figure()
    for col, name, color in y_cols:
        fig.add_trace(go.Bar(x=df[x], y=df[col], name=name, marker_color=color))
    
    layout = _get_chart_layout()
    layout.update({
        "barmode": "group",
        "title": {"text": title},
    })
    fig.update_layout(**layout)
    return fig


def scatter_with_trend(
    df: pd.DataFrame, x: str, y: str, title: str, x_label: str = "", y_label: str = ""
) -> go.Figure:
    """Scatter plot with OLS trendline."""
    fig = px.scatter(
        df,
        x=x,
        y=y,
        trendline="ols",
        title=title,
        labels={x: x_label or x, y: y_label or y},
        color_discrete_sequence=[THEME_PRIMARY],
    )
    
    # Style the trendline
    if len(fig.data) > 1:
        fig.data[1].line.color = THEME_SECONDARY
    
    layout = _get_chart_layout()
    layout.update({"title": {"text": title}})
    fig.update_layout(**layout)
    return fig


def correlation_matrix(df: pd.DataFrame, columns: list[str] | None = None) -> go.Figure:
    """Heatmap for correlation matrix."""
    if columns:
        df = df[columns]
    corr = df.select_dtypes(include="number").corr()
    
    colorscale = [
        [0.0, "#f87171"],    # Negative: rose
        [0.5, "#09090b"],
        [1.0, "#2dd4bf"],    # Positive: teal
    ]
    
    fig = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale=colorscale,
        zmin=-1,
        zmax=1,
        aspect="auto",
    )
    
    layout = _get_chart_layout()
    layout.update({
        "title": {"text": "Correlation Matrix"},
    })
    fig.update_layout(**layout)
    return fig


def calendar_heatmap(df: pd.DataFrame, date_col: str, value_col: str, title: str) -> go.Figure:
    """Calendar-style heatmap."""
    if df.empty:
        return go.Figure()

    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df["weekday"] = df[date_col].dt.dayofweek
    df["week"] = df[date_col].dt.isocalendar().week.astype(int)

    colorscale = [
        [0.0, "#f87171"],
        [0.5, "#fbbf24"],
        [1.0, "#34d399"],
    ]

    fig = px.scatter(
        df,
        x="week",
        y="weekday",
        color=value_col,
        size=[12] * len(df),
        color_continuous_scale=colorscale,
        labels={"weekday": "Day of Week", "week": "Week"},
    )
    fig.update_yaxes(
        tickvals=list(range(7)),
        ticktext=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        autorange="reversed",
    )
    
    layout = _get_chart_layout()
    layout.update({"title": {"text": title}})
    fig.update_layout(**layout)
    return fig


def anomaly_timeline(
    df: pd.DataFrame,
    date_col: str,
    metric_col: str,
    window: int = 14,
    threshold: float = 2.0,
    title: str = "",
) -> go.Figure:
    """Timeline with anomaly detection bands."""
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
    
    # Confidence band
    fig.add_trace(
        go.Scatter(
            x=df[date_col], y=upper, mode="lines", line=dict(width=0), showlegend=False
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df[date_col],
            y=lower,
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(45, 212, 191, 0.06)",
            name=f"{threshold}σ band",
        )
    )
    
    # Data line
    fig.add_trace(
        go.Scatter(
            x=df[date_col],
            y=df[metric_col],
            mode="lines+markers",
            name=metric_col,
            line=dict(color=THEME_PRIMARY, width=1.5),
            marker=dict(size=4, color=THEME_PRIMARY),
            opacity=0.9,
        )
    )
    
    # Rolling mean
    fig.add_trace(
        go.Scatter(
            x=df[date_col],
            y=rolling_mean,
            mode="lines",
            name=f"{window}-day mean",
            line=dict(dash="dash", color="#6b7280", width=1),
        )
    )
    
    # Anomaly markers
    if anomalies.any():
        anom_df = df[anomalies]
        fig.add_trace(
            go.Scatter(
                x=anom_df[date_col],
                y=anom_df[metric_col],
                mode="markers",
                marker=dict(size=10, color=COLOR_BAD, symbol="x"),
                name="Anomaly",
            )
        )
    
    layout = _get_chart_layout()
    layout.update({"title": {"text": title or f"{metric_col} Anomaly Detection"}})
    fig.update_layout(**layout)
    return fig


def pie_chart(labels: list, values: list, title: str, colors: dict | None = None) -> go.Figure:
    """Pie chart with retro colors."""
    color_map = colors or {label: CHART_COLOR_SEQUENCE[i % len(CHART_COLOR_SEQUENCE)] for i, label in enumerate(labels)}
    
    fig = px.pie(
        names=labels,
        values=values,
        color=labels,
        color_discrete_map=color_map,
    )
    
    layout = _get_chart_layout()
    layout.update({"title": {"text": title}})
    fig.update_layout(**layout)
    fig.update_traces(
        textfont={"family": "Inter, sans-serif", "size": 11},
        marker={"line": {"color": CHART_BG, "width": 2}},
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
    
    layout = _get_chart_layout()
    layout.update({
        "title": {"text": title},
        "xaxis_title": "Average Score",
    })
    fig.update_layout(**layout)
    return fig
