"""Agent tool definitions and implementations."""

from __future__ import annotations


import pandas as pd

from config import DATA_DIR_ABSOLUTE
from components.data import (
    get_all_daily_data,
    get_sleep_df,
    get_activity_df,
    get_readiness_df,
    get_stress_df,
    get_spo2_df,
    get_imported_activity_df,
)
from components.agent.pubmed import search_pubmed

# OpenAI-style tool definitions for both Anthropic and OpenAI
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "oura_data",
            "description": "Fetch Oura health data for a date range. Returns sleep, activity, readiness, stress, SpO2, HRV. When include_imported is true, also merges user-imported data (steps, calories, workouts from Excel/CSV) for comparison.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                    "data_type": {
                        "type": "string",
                        "enum": ["all", "sleep", "activity", "readiness", "stress", "spo2"],
                        "description": "Type of data to fetch. 'all' merges daily metrics.",
                    },
                    "include_imported": {
                        "type": "boolean",
                        "description": "If true, merge imported steps/calories/workouts for comparison (Oura vs manual tracking). Use when user asks about calories, steps trends, or Oura vs imported data.",
                        "default": True,
                    },
                },
                "required": ["start_date", "end_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "pubmed_search",
            "description": "Search PubMed for biomedical literature on a health topic. Returns article titles, authors, abstracts, PMIDs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query, e.g. 'HRV sleep quality recovery'"},
                    "max_results": {"type": "integer", "description": "Max articles to return", "default": 5},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "statistical_analysis",
            "description": "Run statistical analysis on Oura data: correlation between two metrics, rolling stats, trend.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                    "metric_x": {"type": "string", "description": "First metric (e.g. sleep_score, avg_hrv, steps)"},
                    "metric_y": {"type": "string", "description": "Second metric for correlation"},
                    "analysis": {
                        "type": "string",
                        "enum": ["correlation", "summary", "trend"],
                        "description": "Type of analysis",
                    },
                },
                "required": ["start_date", "end_date", "analysis"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "lab_results",
            "description": "Fetch imported lab results (blood panel biomarkers) for a date range. Returns test_name, value, unit, reference range. Use when user asks about blood work, labs, biomarkers, cholesterol, glucose, vitamin D, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                    "test_name": {"type": "string", "description": "Optional: filter by biomarker (e.g. LDL-C, Glucose, Vitamin D)"},
                },
                "required": ["start_date", "end_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_chart",
            "description": "Generate a chart from Oura data. Creates line, bar, or scatter plots. Use when the user asks to visualize, plot, or graph a metric.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                    "chart_type": {
                        "type": "string",
                        "enum": ["line", "bar", "scatter"],
                        "description": "Type of chart: line for trends over time, bar for daily values, scatter for comparing two metrics",
                    },
                    "metric": {"type": "string", "description": "Primary metric to plot (e.g. sleep_score, avg_hrv, steps, readiness_score)"},
                    "metric_y": {"type": "string", "description": "Second metric for scatter charts (x-axis will use metric, y-axis metric_y)"},
                    "title": {"type": "string", "description": "Chart title"},
                },
                "required": ["start_date", "end_date", "chart_type", "metric"],
            },
        },
    },
]


def execute_tool(
    name: str,
    arguments: dict,
    token: str,
    sandbox: bool,
    charts_out: list | None = None,
) -> str:
    """Execute a tool and return result as string for the LLM."""
    if name == "oura_data":
        return _run_oura_data(arguments, token, sandbox)
    if name == "pubmed_search":
        return _run_pubmed_search(arguments)
    if name == "statistical_analysis":
        return _run_statistical_analysis(arguments, token, sandbox)
    if name == "lab_results":
        return _run_lab_results(arguments)
    if name == "generate_chart":
        return _run_generate_chart(arguments, token, sandbox, charts_out or [])
    return f"Unknown tool: {name}"


def _run_oura_data(args: dict, token: str, sandbox: bool) -> str:
    start = args.get("start_date", "")
    end = args.get("end_date", "")
    data_type = args.get("data_type", "all")
    include_imported = args.get("include_imported", True)
    if not start or not end:
        return "Error: start_date and end_date required."

    try:
        if data_type == "all":
            df = get_all_daily_data(token, start, end, sandbox)
        elif data_type == "sleep":
            df = get_sleep_df(token, start, end, sandbox)
        elif data_type == "activity":
            df = get_activity_df(token, start, end, sandbox)
        elif data_type == "readiness":
            df = get_readiness_df(token, start, end, sandbox)
        elif data_type == "stress":
            df = get_stress_df(token, start, end, sandbox)
        elif data_type == "spo2":
            df = get_spo2_df(token, start, end, sandbox)
        else:
            df = get_all_daily_data(token, start, end, sandbox)

        if df.empty and not include_imported:
            return f"No {data_type} data for {start} to {end}."

        if include_imported:
            imported = get_imported_activity_df(DATA_DIR_ABSOLUTE, start, end)
            if not imported.empty:
                # Rename imported cols to avoid collision with Oura columns
                imp_merge = imported.copy()
                imp_merge = imp_merge.rename(columns={
                    "steps": "steps_imported",
                    "calories": "calories_imported",
                    "workouts": "workouts_imported",
                    "weight": "weight_imported",
                    "sleep_hours": "sleep_hours_imported",
                })
                imp_merge = imp_merge[["day"] + [c for c in imp_merge.columns if c != "day" and c.endswith("_imported")]]
                if not df.empty:
                    df = df.merge(imp_merge, on="day", how="outer").sort_values("day").reset_index(drop=True)
                else:
                    df = imp_merge

        if df.empty:
            return f"No {data_type} data for {start} to {end}."
        summary = df.describe().round(2).to_string()
        head = df.head(14).to_string()
        return f"Data ({len(df)} rows):\n\nSummary:\n{summary}\n\nFirst 14 rows:\n{head}"
    except Exception as e:
        return f"Error fetching Oura data: {e}"


def _run_lab_results(args: dict) -> str:
    start = args.get("start_date", "")
    end = args.get("end_date", "")
    test_name = args.get("test_name", "")
    if not start or not end:
        return "Error: start_date and end_date required."
    try:
        from health_import import query_lab_results

        df = query_lab_results(DATA_DIR_ABSOLUTE, start, end, test_name=test_name or None)
        if df.empty:
            return f"No lab results for {start} to {end}" + (f" (filter: {test_name})" if test_name else ".")
        return df.to_string()
    except Exception as e:
        return f"Error fetching lab results: {e}"


def _run_pubmed_search(args: dict) -> str:
    query = args.get("query", "")
    max_results = int(args.get("max_results", 5))
    if not query:
        return "Error: query required."
    try:
        articles = search_pubmed(query, max_results=max_results)
        if not articles:
            return f"No PubMed results for: {query}"
        lines = []
        for i, a in enumerate(articles, 1):
            authors = ", ".join(a.get("authors", []))[:80]
            lines.append(f"{i}. [{a.get('pmid', '?')}] {a.get('title', '')[:120]}...")
            lines.append(f"   {authors} ({a.get('year', '')})")
            lines.append(f"   {a.get('abstract', '')[:200]}...")
            lines.append("")
        return "\n".join(lines)
    except Exception as e:
        return f"Error searching PubMed: {e}"


def _run_statistical_analysis(args: dict, token: str, sandbox: bool) -> str:
    start = args.get("start_date", "")
    end = args.get("end_date", "")
    analysis = args.get("analysis", "summary")
    metric_x = args.get("metric_x", "")
    metric_y = args.get("metric_y", "")
    if not start or not end:
        return "Error: start_date and end_date required."

    try:
        df = get_all_daily_data(token, start, end, sandbox)
        # Merge imported data when analysing imported metrics or for broader correlation
        imported = get_imported_activity_df(DATA_DIR_ABSOLUTE, start, end)
        if not imported.empty:
            imp_merge = imported.rename(columns={
                "steps": "steps_imported", "calories": "calories_imported",
                "workouts": "workouts_imported", "weight": "weight_imported",
                "sleep_hours": "sleep_hours_imported",
            })
            imp_merge = imp_merge[["day"] + [c for c in imp_merge.columns if c != "day" and c.endswith("_imported")]]
            df = df.merge(imp_merge, on="day", how="outer") if not df.empty else imp_merge
            df = df.sort_values("day").reset_index(drop=True)
        if df.empty:
            return f"No data for {start} to {end}."

        if analysis == "summary":
            numeric = df.select_dtypes(include="number")
            return numeric.describe().round(2).to_string()
        if analysis == "correlation" and metric_x and metric_y:
            if metric_x in df.columns and metric_y in df.columns:
                valid = df[[metric_x, metric_y]].dropna()
                if len(valid) >= 3:
                    r = valid[metric_x].corr(valid[metric_y])
                    return f"Pearson correlation ({metric_x} vs {metric_y}): r = {r:.3f} (n={len(valid)})"
            return f"Metrics {metric_x} or {metric_y} not found. Available: {list(df.columns)[:15]}"
        if analysis == "trend" and metric_x and metric_x in df.columns:
            from scipy import stats
            valid = df[["day", metric_x]].dropna()
            valid["day_ord"] = pd.to_datetime(valid["day"]).astype(int)
            if len(valid) >= 3:
                slope, intercept, r, p, se = stats.linregress(valid["day_ord"], valid[metric_x])
                return f"Trend ({metric_x}): slope={slope:.6e}, R²={r**2:.3f}, p={p:.4f}"
            return "Insufficient data for trend."
        return f"Available metrics: {list(df.columns)}"
    except Exception as e:
        return f"Error in analysis: {e}"


def _run_generate_chart(args: dict, token: str, sandbox: bool, charts_out: list) -> str:
    import plotly.graph_objects as go

    from config import CHART_TEMPLATE
    from components.charts import trend_line

    start = args.get("start_date", "")
    end = args.get("end_date", "")
    chart_type = args.get("chart_type", "line")
    metric = args.get("metric", "")
    metric_y = args.get("metric_y", "")
    title = args.get("title", "")

    if not start or not end or not metric:
        return "Error: start_date, end_date, and metric required."

    try:
        df = get_all_daily_data(token, start, end, sandbox)
        imported = get_imported_activity_df(DATA_DIR_ABSOLUTE, start, end)
        if not imported.empty:
            imp_merge = imported.rename(columns={
                "steps": "steps_imported", "calories": "calories_imported",
                "workouts": "workouts_imported", "weight": "weight_imported",
                "sleep_hours": "sleep_hours_imported",
            })
            imp_merge = imp_merge[["day"] + [c for c in imp_merge.columns if c != "day" and c.endswith("_imported")]]
            df = df.merge(imp_merge, on="day", how="outer") if not df.empty else imp_merge
            df = df.sort_values("day").reset_index(drop=True)
        if df.empty:
            return f"No data for {start} to {end}."

        if "day" not in df.columns:
            return "Data has no date column."
        if metric not in df.columns:
            return f"Metric '{metric}' not found. Available: {list(df.columns)[:20]}"

        if chart_type == "line":
            title = title or f"{metric} over time"
            fig = trend_line(df, "day", metric, title)
        elif chart_type == "bar":
            title = title or f"{metric} by day"
            fig = go.Figure(go.Bar(x=df["day"], y=df[metric], name=metric))
            fig.update_layout(title=title, xaxis_title="Date", yaxis_title=metric, template=CHART_TEMPLATE)
        elif chart_type == "scatter":
            if not metric_y or metric_y not in df.columns:
                return f"For scatter charts, metric_y required. Available: {list(df.columns)[:20]}"
            title = title or f"{metric} vs {metric_y}"
            fig = go.Figure(
                go.Scatter(x=df[metric], y=df[metric_y], mode="markers", name="Data")
            )
            fig.update_layout(title=title, xaxis_title=metric, yaxis_title=metric_y, template=CHART_TEMPLATE)
        else:
            return f"Unknown chart_type: {chart_type}. Use line, bar, or scatter."

        charts_out.append({"fig_json": fig.to_json()})
        return f"Chart generated: {title}"
    except Exception as e:
        return f"Error generating chart: {e}"
