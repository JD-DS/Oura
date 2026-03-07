# Oura Ring API Development Sandbox

> Implementation plan for the core project scaffolding, API client, and data exploration notebooks.
> **Status: Completed**

## API Capabilities Summary

The Oura API V2 exposes **16 data types** via REST endpoints at `api.ouraring.com/v2/`. Authentication is OAuth2-only (personal tokens deprecated Dec 2025). The API also provides **sandbox endpoints** (`/v2/sandbox/usercollection/...`) that return mock data without requiring real ring data -- useful for development.

Available data: Sleep (detailed stages, HR, HRV, breathing), Daily Sleep/Activity/Readiness/Stress/Resilience/SpO2/Cardiovascular Age scores, Heart Rate (time-series), VO2 Max, Workouts, Sessions, Tags, Sleep Time recommendations, Rest Mode, Ring Configuration, and Webhooks.

OAuth2 scopes: `email`, `personal`, `daily`, `heartrate`, `workout`, `tag`, `session`, `spo2Daily`.

## Tech Stack

- **Python 3.11+** -- best ecosystem for health data analysis
- **httpx** -- async HTTP client for API calls
- **Pydantic** -- data validation and typed models (matches the OpenAPI schema)
- **Jupyter** -- interactive data exploration
- **Plotly** -- interactive charts for health data visualization
- **pandas** -- data manipulation and time-series analysis
- **python-dotenv** -- credential management

## What Was Built

### 1. Project Scaffolding
- Git repo, `pyproject.toml` with all dependencies, `.gitignore`, `.env.example`

### 2. OAuth2 Authentication (`src/oura_client/auth.py`)
- Full OAuth2 authorization code flow with local callback server
- Token exchange and automatic refresh on 401 responses
- Token persistence to `.env` file

### 3. API Client (`src/oura_client/client.py`)
- Typed `OuraClient` class wrapping all 16 data type endpoints
- Automatic pagination via `next_token`
- Built-in rate limit handling (5000 req / 5 min)
- Sandbox mode toggle that routes to `/v2/sandbox/...` endpoints

### 4. Pydantic Models (`src/oura_client/models.py`)
- Type-safe models for all API response types
- Helper properties for duration conversion and sleep phase parsing

### 5. Jupyter Notebooks
- `01_explore_sleep.ipynb` -- Sleep architecture, HRV trends, efficiency
- `02_activity_readiness.ipynb` -- Steps, calories, readiness contributors
- `03_heart_rate_stress.ipynb` -- Intraday HR, stress/recovery balance

### 6. Tests
- 18 tests covering model parsing, client routing, pagination, and auth

## Recommended Application Ideas

### Tier 1 -- Quick Wins (notebooks)
- **Sleep Quality Analyzer** -- Visualize sleep architecture over time, flag poor nights
- **Readiness Forecast** -- Chart readiness contributors, identify limiting factors

### Tier 2 -- Intermediate Apps (Streamlit dashboards)
- **Holistic Health Dashboard** -- All key metrics with trend lines
- **Workout Recovery Advisor** -- Recovery estimates based on readiness/stress
- **Sleep Consistency Tracker** -- Bedtime regularity analysis

### Tier 3 -- Advanced Projects (full applications)
- **Health Anomaly Detector** -- Surface unusual patterns in vitals
- **Correlations Engine** -- Cross-correlate all data types for insights
- **Personal Health API** -- FastAPI backend with webhooks and data storage
