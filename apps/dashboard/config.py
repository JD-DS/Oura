"""Centralized configuration for the Oura Health Dashboard.

All configurable values are loaded from environment variables (via .env)
with sensible defaults. No hardcoded magic numbers in page files.
"""

from __future__ import annotations

import os
from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv

_env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(_env_path)


def _env(key: str, default: str = "") -> str:
    return os.getenv(key, default)


def _env_int(key: str, default: int) -> int:
    return int(os.getenv(key, str(default)))


def _env_float(key: str, default: float) -> float:
    return float(os.getenv(key, str(default)))


def _env_bool(key: str, default: bool) -> bool:
    return os.getenv(key, str(default)).lower() in ("true", "1", "yes")


# --- Oura OAuth2 ---

OURA_CLIENT_ID = _env("OURA_CLIENT_ID")
OURA_CLIENT_SECRET = _env("OURA_CLIENT_SECRET")
OURA_REDIRECT_URI = _env("OURA_REDIRECT_URI", "http://localhost:8501/")
OURA_AUTHORIZE_URL = _env("OURA_AUTHORIZE_URL", "https://cloud.ouraring.com/oauth/authorize")
OURA_TOKEN_URL = _env("OURA_TOKEN_URL", "https://api.ouraring.com/oauth/token")
OURA_API_BASE_URL = _env("OURA_API_BASE_URL", "https://api.ouraring.com")

# --- API Client ---

API_TIMEOUT = _env_float("API_TIMEOUT", 30.0)
API_MAX_RETRIES = _env_int("API_MAX_RETRIES", 3)
API_RETRY_AFTER_DEFAULT = _env_int("API_RETRY_AFTER_DEFAULT", 60)

# --- Data Caching ---

CACHE_TTL_SECONDS = _env_int("CACHE_TTL_SECONDS", 300)

# --- Dashboard Defaults ---

DEFAULT_DATE_RANGE_DAYS = _env_int("DEFAULT_DATE_RANGE_DAYS", 30)

# --- Chart Theme ---

CHART_TEMPLATE = _env("CHART_TEMPLATE", "plotly_dark")

THEME_PRIMARY = _env("THEME_PRIMARY", "#6C63FF")

SLEEP_STAGE_COLORS = {
    "deep_h": _env("COLOR_DEEP_SLEEP", "#1a237e"),
    "light_h": _env("COLOR_LIGHT_SLEEP", "#42a5f5"),
    "rem_h": _env("COLOR_REM_SLEEP", "#ab47bc"),
    "awake_h": _env("COLOR_AWAKE", "#ef5350"),
}

COLOR_GOOD = _env("COLOR_GOOD", "#66bb6a")
COLOR_WARNING = _env("COLOR_WARNING", "#ffa726")
COLOR_BAD = _env("COLOR_BAD", "#ef5350")
COLOR_INFO = _env("COLOR_INFO", "#42a5f5")

STRESS_COLORS = {
    "restored": COLOR_GOOD,
    "normal": COLOR_INFO,
    "stressful": COLOR_BAD,
}

# --- Sleep Analyzer Thresholds ---

SLEEP_EFFICIENCY_GOOD = _env_int("SLEEP_EFFICIENCY_GOOD", 85)
SLEEP_EFFICIENCY_FLAG = _env_int("SLEEP_EFFICIENCY_FLAG", 80)
SLEEP_LATENCY_FLAG_MIN = _env_int("SLEEP_LATENCY_FLAG_MIN", 30)

# --- Readiness Thresholds ---

READINESS_CONTRIBUTOR_LOW = _env_int("READINESS_CONTRIBUTOR_LOW", 70)
READINESS_CONTRIBUTOR_MED = _env_int("READINESS_CONTRIBUTOR_MED", 85)

# --- Correlation Thresholds ---

CORRELATION_STRONG = _env_float("CORRELATION_STRONG", 0.7)
CORRELATION_MODERATE = _env_float("CORRELATION_MODERATE", 0.4)
CORRELATION_MAX_LAG_DAYS = _env_int("CORRELATION_MAX_LAG_DAYS", 3)

# --- Anomaly Detection ---

ANOMALY_WINDOW_DAYS = _env_int("ANOMALY_WINDOW_DAYS", 14)
ANOMALY_Z_THRESHOLD = _env_float("ANOMALY_Z_THRESHOLD", 2.0)

# --- Sparkline ---

SPARKLINE_HEIGHT = _env_int("SPARKLINE_HEIGHT", 60)

# --- Rolling Average ---

ROLLING_WINDOW_DAYS = _env_int("ROLLING_WINDOW_DAYS", 7)

# --- AI Assistant (Phase 3) ---

AI_PROVIDER = _env("AI_PROVIDER", "anthropic")
ANTHROPIC_API_KEY = _env("ANTHROPIC_API_KEY")
OPENAI_API_KEY = _env("OPENAI_API_KEY")
NCBI_API_KEY = _env("NCBI_API_KEY")
NCBI_EMAIL = _env("NCBI_EMAIL")
NCBI_TOOL_NAME = _env("NCBI_TOOL_NAME", "oura-health-assistant")


def default_start_date() -> date:
    return date.today() - timedelta(days=DEFAULT_DATE_RANGE_DAYS)


def default_end_date() -> date:
    return date.today()
