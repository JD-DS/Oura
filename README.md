# Oura Ring API Sandbox

A Python development sandbox for building and testing applications with the [Oura Ring API V2](https://cloud.ouraring.com/v2/docs). Includes a typed API client, data exploration notebooks, a multi-page Streamlit health dashboard, and plans for an AI health assistant with PubMed research integration.

---

## Table of Contents

- [What This Project Does](#what-this-project-does)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Data Boundaries](#data-boundaries-what-stays-local-vs-whats-in-the-repo)
- [How Authentication Works](#how-authentication-works)
- [Running the Project](#running-the-project)
- [Web Dashboard](#web-dashboard)
- [Project Structure](#project-structure)
- [Available Data Types](#available-data-types)
- [Configuration Reference](#configuration-reference)
- [Testing](#testing)
- [Deployment](#deployment)
- [Preparing for GitHub](#preparing-for-github)
- [Documentation](#documentation)
- [What's Next](#whats-next)
- [API Reference](#api-reference)

---

## What This Project Does

1. **API Client** (`src/oura_client/`) — A typed Python client that wraps all 16 Oura API endpoints. Handles OAuth2, pagination, rate limiting, and token refresh. Supports sandbox mode for development without real ring data.

2. **Jupyter Notebooks** (`notebooks/`) — Three notebooks for exploring sleep, activity/readiness, and heart rate/stress data. Use sandbox mode to run without connecting a real ring.

3. **Streamlit Dashboard** (`apps/dashboard/`) — A 7-page web app with OAuth2 login, configurable date ranges, and visualizations for all major Oura metrics. Can run locally or deploy to Streamlit Community Cloud.

4. **Planned: AI Health Assistant** — An agent that analyzes your data, searches PubMed for research, and provides personalized insights. See [docs/03_ai_health_assistant.md](docs/03_ai_health_assistant.md).

---

## Prerequisites

- **Python 3.11+**
- **Oura Ring** with an active subscription
- **OAuth2 application** registered at the [Oura Developer Portal](https://developer.ouraring.com/applications)

---

## Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/oura.git
cd oura

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate

# Install dependencies and the package
pip install -r requirements.txt
pip install -e .
```

For development (tests, linting, pre-commit):

```bash
pip install -e ".[dev]"
pip install pre-commit && pre-commit install
```

Pre-commit blocks `.env`, `tokens.json`, `data/`, and `*.db`/`*.sqlite` from being committed.

Optional: Install pre-commit hooks to block secrets and personal data from being committed:

```bash
pip install pre-commit
pre-commit install
```

---

## Data Boundaries: What Stays Local vs What's in the Repo

This repo is a **framework** you clone and configure. Your personal data and secrets never belong in the repo.

| Stays local (never commit) | In the repo |
|---------------------------|-------------|
| `.env` — OAuth credentials, API keys, tokens | `.env.example` — template with placeholders |
| `tokens.json` — OAuth tokens (if used) | Code, config templates, docs |
| `data/` — Excel imports, blood panel PDFs, workout logs | `docs/data/` — redacted sample files for schema docs |
| `*.sqlite`, `*.db` — local databases | |

**Clone-and-configure workflow:** Clone → copy `.env.example` to `.env` → add your credentials → run. Your data never touches the repo.

---

## Configuration

All secrets and configurable values live in a `.env` file. Copy the example and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your Oura OAuth2 credentials:

```
OURA_CLIENT_ID=your_client_id_here
OURA_CLIENT_SECRET=your_client_secret_here
OURA_REDIRECT_URI=http://localhost:8501/
```

**Important:** The redirect URI must match where your app runs:

- **Local Streamlit:** `http://localhost:8501/` (Streamlit's default port)
- **Streamlit Cloud:** `https://your-app-name.streamlit.app/`
- **CLI auth (OuraAuth):** `http://localhost:8080/callback` — used when running `auth.authorize()` from Python; a local server listens on port 8080

If you use both the CLI and the dashboard, register both redirect URIs in your [Oura OAuth application settings](https://developer.ouraring.com/applications).

---

## Data Boundaries: What Stays Local vs. What's in the Repo

This repo is a **framework** — clone it, add your credentials, and your data never touches the codebase.

| Stays local (never committed) | In the repo |
|--------------------------------|-------------|
| `.env` — OAuth credentials, API keys, tokens | `.env.example` — template with placeholders |
| `tokens.json` — OAuth tokens (CLI auth fallback) | Code, config templates, docs |
| `data/` — Your health data (Excel, PDFs, lab results, workout logs) | `docs/data/` — Redacted sample files for schema docs |
| `*.sqlite`, `*.db` — Local databases | |

**Clone-and-configure workflow:** Clone → copy `.env.example` to `.env` → add your credentials → run. Your personal data stays in `data/` at the project root (or a path you set via `DATA_DIR` in `.env`).

---

## How Authentication Works

### Two Auth Flows

| Context | Flow | Redirect URI |
|---------|------|--------------|
| **CLI / Notebooks** | `OuraAuth().authorize()` starts a local HTTP server on port 8080, opens the browser for Oura consent, captures the callback, exchanges the code for tokens, saves to `.env` | `http://localhost:8080/callback` |
| **Web Dashboard** | User clicks "Connect to Oura" → redirects to Oura → Oura redirects back to the app URL with `?code=...` → Streamlit exchanges the code and stores tokens in session state | Your app URL (e.g. `http://localhost:8501/` or Streamlit Cloud URL) |

### Token Storage

- **CLI/Notebooks:** Tokens are written to `.env` after `auth.authorize()` and persist across sessions.
- **Dashboard:** Tokens live in `st.session_state` and are lost when the browser tab closes. Users must reconnect on each new session.

### Sandbox Mode

When sandbox mode is enabled, the app uses Oura's mock data endpoints (`/v2/sandbox/usercollection/...`). No OAuth or real ring data is required. Use this for demos, development, or exploring the app without an Oura account.

---

## Running the Project

### 1. Fetch Data from the CLI

After running `auth.authorize()` once to get tokens:

```python
from oura_client import OuraClient

client = OuraClient()
sleep = client.get_sleep(start_date="2025-01-01", end_date="2025-01-31")
for s in sleep:
    deep = f"{s.deep_sleep_hours:.1f}h" if s.deep_sleep_hours else "N/A"
    print(f"{s.day}: {deep} deep, HRV avg {s.average_hrv}")
```

### 2. Use Sandbox Mode (No Auth Required)

```python
client = OuraClient(sandbox=True)
sleep = client.get_sleep(start_date="2025-01-01", end_date="2025-01-07")
```

### 3. Run Jupyter Notebooks

```bash
jupyter notebook notebooks/
```

Notebooks use `OuraClient(sandbox=True)` by default so they run without credentials.

### 4. Run the Streamlit Dashboard

```bash
streamlit run apps/dashboard/app.py
```

Opens at `http://localhost:8501`. Use sandbox mode from the sidebar to explore without connecting a real ring.

---

## Web Dashboard

### Pages

| Page | Description |
|------|-------------|
| **Dashboard** | KPI cards (sleep, readiness, activity, stress, SpO2), 7-day sparklines, readiness calendar heatmap |
| **Sleep Analyzer** | Sleep architecture stacked bars, HRV trend, efficiency scatter, phase timeline, poor-night flagging |
| **Readiness & Recovery** | Contributor breakdown, weakest-link analysis, workout recovery advisor |
| **Activity** | Steps, calories, activity time breakdown, sedentary tracking |
| **Heart Rate & Stress** | Intraday HR by source, resting HR trend, stress/recovery bars, resilience timeline |
| **Correlations** | Metric-pair scatter with OLS trendline, correlation matrix, time-lagged analysis |
| **Anomaly Detection** | Rolling z-scores, anomaly flagging, illness early-warning indicators |

### How the Dashboard Works

1. **Entry** — `app.py` checks for an access token. If missing, it looks for an OAuth `code` in the URL (callback). If still missing, it shows a login page.
2. **Sidebar** — Date range picker, sandbox toggle, logout. Dates are stored in `st.session_state` and shared across all pages.
3. **Data** — `components/data.py` wraps `OuraClient` with `@st.cache_data(ttl=300)` so API responses are cached for 5 minutes.
4. **Charts** — `components/charts.py` provides reusable Plotly chart builders (sparklines, stacked bars, heatmaps, etc.).
5. **Config** — `config.py` loads all thresholds, colors, and defaults from `.env`. No magic numbers in page files.

---

## Project Structure

```
oura/
├── src/oura_client/          # Python client library
│   ├── auth.py               # OAuth2 flow (local callback server)
│   ├── client.py             # Typed API client for all 16 endpoints
│   ├── models.py             # Pydantic models for API responses
│   └── sandbox.py            # Sandbox endpoint helpers
├── apps/dashboard/           # Streamlit web dashboard
│   ├── app.py                # Entry point, auth gate, navigation
│   ├── config.py             # Centralized config from .env
│   ├── pages/                # 7 dashboard pages
│   ├── components/           # auth_web, data, charts
│   └── .streamlit/           # Streamlit server config
├── notebooks/                # Jupyter notebooks for exploration
├── tests/                    # 18 tests using sandbox endpoints
├── docs/                     # Implementation plans and TODO
├── openapi/                  # Oura OpenAPI V2 specification
├── .env.example              # Template for secrets and config
├── requirements.txt          # Dependencies for deployment
└── pyproject.toml            # Package metadata and dev deps
```

---

## Available Data Types

| Endpoint | Description | Scope |
|----------|-------------|-------|
| Personal Info | Age, weight, height, biological sex | `personal` |
| Sleep | Detailed sleep periods with stages, HR, HRV, breathing | `daily` |
| Daily Sleep | Daily sleep score with contributors | `daily` |
| Daily Activity | Steps, calories, MET minutes, activity classification | `daily` |
| Daily Readiness | Readiness score with contributors | `daily` |
| Daily Stress | Stress/recovery time, day summary | `daily` |
| Daily Resilience | Resilience level and contributors | `daily` |
| Daily SpO2 | Blood oxygen saturation, breathing disturbance index | `spo2Daily` |
| Daily Cardiovascular Age | Predicted vascular age | `daily` |
| Heart Rate | Time-series BPM with source context | `heartrate` |
| VO2 Max | Estimated VO2 max | `daily` |
| Workouts | Activity type, calories, distance, intensity | `workout` |
| Sessions | Meditation, breathing, nap sessions | `session` |
| Tags / Enhanced Tags | User-entered tags with comments | `tag` |
| Sleep Time | Recommended sleep windows | `daily` |
| Rest Mode Period | Rest mode episodes | `daily` |
| Ring Configuration | Ring hardware, firmware, color, size | `personal` |

---

## Configuration Reference

All configurable values are in `.env`. See `.env.example` for the full list. Key variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OURA_CLIENT_ID` | (required) | OAuth2 client ID |
| `OURA_CLIENT_SECRET` | (required) | OAuth2 client secret |
| `OURA_REDIRECT_URI` | `http://localhost:8501/` | OAuth2 redirect URI |
| `CACHE_TTL_SECONDS` | `300` | Dashboard data cache TTL |
| `DEFAULT_DATE_RANGE_DAYS` | `30` | Default date range for dashboard |
| `SLEEP_EFFICIENCY_FLAG` | `80` | Flag nights below this efficiency |
| `SLEEP_LATENCY_FLAG_MIN` | `30` | Flag nights with latency above this (minutes) |
| `ANOMALY_WINDOW_DAYS` | `14` | Rolling window for anomaly detection |
| `ANOMALY_Z_THRESHOLD` | `2.0` | Z-score threshold for flagging |

---

## Testing

```bash
pytest
```

All 18 tests use the Oura sandbox endpoints, so no credentials or real data are required.

### Pre-commit (optional)

To block secrets and personal data from being committed, and run ruff + tests on each commit:

```bash
pip install pre-commit
pre-commit install
```

Hooks will run automatically on `git commit`. Run manually: `pre-commit run --all-files`

---

## Deployment

### Streamlit Community Cloud

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your GitHub account.
3. Click "New app", select this repo, branch `main`, and file `apps/dashboard/app.py`.
4. Add secrets in the app settings:
   - `OURA_CLIENT_ID`
   - `OURA_CLIENT_SECRET`
   - `OURA_REDIRECT_URI` (your Streamlit Cloud app URL, e.g. `https://oura-dashboard.streamlit.app/`)
5. Register that redirect URI in your [Oura OAuth application](https://developer.ouraring.com/applications).
6. Deploy. Streamlit Cloud auto-deploys on every push to `main`.

**Privacy on Streamlit Cloud:** Store secrets only in the Cloud app's Secrets UI — never in the repo. User OAuth tokens live in session state and are not persisted; users reconnect each session. Uploaded files (Excel, PDF) and imported data are not supported on Cloud unless you add an external database configured via environment variables.

---

## Preparing for GitHub

To initialize this project as a Git repository and push to GitHub:

```bash
git init
git add .
git commit -m "Initial commit: Oura API sandbox with client, dashboard, and docs"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/oura.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username. Ensure `.env` is in `.gitignore` (it is) so credentials are never committed.

---

## Documentation

| Document | Description |
|----------|-------------|
| [docs/01_sandbox_setup.md](docs/01_sandbox_setup.md) | Core client library and project scaffolding |
| [docs/02_streamlit_dashboard.md](docs/02_streamlit_dashboard.md) | Web dashboard architecture and pages |
| [docs/03_ai_health_assistant.md](docs/03_ai_health_assistant.md) | AI chatbot with PubMed integration (planned) |
| [docs/TODO.md](docs/TODO.md) | What still needs to be built |

---

## What's Next

See [docs/TODO.md](docs/TODO.md) for the full list of planned work. The main remaining item is the **AI Health Assistant** (Phase 3).

---

## API Reference

- [Oura API Documentation](https://cloud.ouraring.com/v2/docs)
- [Developer Portal](https://developer.ouraring.com/applications)
- [Authentication Guide](https://cloud.ouraring.com/docs/authentication)
- Rate limit: 5000 requests per 5-minute period
