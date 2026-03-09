# TODO — Remaining Work

This document tracks what still needs to be built or improved in the Oura Ring API sandbox project.

---

## Data Privacy & Framework Separation (High Priority)

The repo must function as a **framework** others can fork and configure with their own data. Your personal health data, secrets, and tokens must never be committed. All user-specific data lives outside the public codebase.

### Audit & Hardening

- [x] **Secrets audit** — Confirm no credentials, tokens, or API keys in committed files; all loaded from `.env` or environment
- [x] **Personal data audit** — Verify no real health data (Oura exports, Excel, PDFs, lab results) in repo; `.gitignore` covers all storage paths
- [x] **Pre-commit / CI check** — Add check that `.env`, `tokens.json`, `data/`, `*.db`, `*.sqlite` are never staged (`scripts/check_no_secrets.py`)
- [x] **Document data boundaries** — README section: "Data Boundaries: What Stays Local vs. What's in the Repo"

### Storage & Paths

- [x] **Configurable data directory** — `DATA_DIR` in `.env` (default `data/`); exposed in `config.py` for Phase 4
- [x] **`.gitignore` coverage** — `/data/`, `.env`, `tokens.json`, `*.sqlite`, `*.db` ignored; `docs/data/` for sample files
- [x] **Streamlit Cloud** — Document that secrets go in Cloud UI only; user data not persisted on Cloud (or use external DB with env config)

### Framework vs Personal Instance

- [x] **No hardcoded user identity** — No emails, names, or user IDs in code; all user context from env or runtime
- [x] **Sample data only** — `docs/data/` structure and README added; add example Excel/PDF when Phase 4 import pipeline is built
- [x] **Clone-and-configure workflow** — README: clone → copy `.env.example` → add your credentials → run; your data never touches the repo

---

## Phase 3: AI Health Assistant (High Priority)

The main planned feature. Full implementation plan in [03_ai_health_assistant.md](03_ai_health_assistant.md).

### Core Implementation

- [x] **Agent orchestration layer** — Conversation loop with tool-calling LLM (Claude or GPT-4o)
- [x] **Oura Data Tool** — Wrapper around `OuraClient` for the agent to fetch and summarize data on demand
- [x] **PubMed Search Tool** — NCBI E-utilities integration for biomedical literature search
- [x] **Statistical Analysis Tool** — Correlation, trend, and comparison helpers for the agent
- [x] **Chart Generation Tool** — Generate inline Plotly charts in chat responses
- [x] **Streamlit chat UI** — `st.chat_message` interface with conversation memory in session state
- [x] **LLM provider abstraction** — Support both Anthropic and OpenAI, configurable via `AI_PROVIDER`

### Dependencies

- [x] Add `anthropic` and `openai` to `requirements.txt` (or optional `ai` extra)
- [x] Document `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `NCBI_API_KEY`, `NCBI_EMAIL` in `.env.example`

---

## Phase 4: External Health Data Integration (Medium Priority)

Integrate and persist health data from user-uploaded files (Excel, PDF) alongside Oura data. Reference file formats and sample files in `docs/data/`.

### Excel Data (Calories, Workouts, Steps, etc.)

- [x] **Excel import pipeline** — Parse Excel/CSV files with calories, workouts, steps, and other activity/nutrition metrics (historical data from tracking start through present)
- [x] **Persistent storage** — Save imported data to a local store (SQLite, Parquet, or JSON) keyed by date
- [x] **Incremental updates** — Support appending new rows when updated Excel files are uploaded; avoid duplicates, merge by date; allow adding new data as it comes in
- [x] **Schema definition** — Document expected Excel column names and formats in `docs/data/` for consistent parsing; validate on upload
- [x] **Dashboard integration** — Activity page: merge Excel steps/calories with Oura data; show combined trends, source attribution
- [x] **Correlations & anomalies** — Include Excel metrics in correlation matrix, anomaly detection, and time-lagged analysis
- [x] **AI Assistant integration** — Oura Data Tool extended to query Excel-derived data; agent can compare Oura vs manual tracking, answer queries like "how did my calories trend vs my sleep?"

### Blood Panel PDFs

- [x] **PDF parsing** — Extract lab results from blood panel PDFs (e.g. CBC, metabolic panel, lipids) using pdfplumber
- [x] **Structured extraction** — Map biomarker names and values to a common schema (test name, value, unit, reference range, date)
- [x] **Persistent storage** — Save extracted results; support multiple panels over time (historical + new uploads)
- [x] **Incremental updates** — Add new PDFs as they arrive; associate each panel with a date (from PDF or user input); save old results, append new ones
- [x] **Dashboard integration** — New "Lab Results" page: biomarker trend lines, reference range bands, flag out-of-range values, comparison across draw dates
- [ ] **Correlations** — Correlate biomarkers with Oura metrics (e.g. HRV vs inflammation markers, sleep vs glucose)
- [ ] **Anomaly detection** — Extend anomaly detection to lab trends (e.g. rising LDL, declining vitamin D)
- [x] **AI Assistant integration** — Agent can interpret lab results, explain reference ranges (lab_results tool)
- [ ] **Varied PDF formats** — Different labs use different layouts; configurable extraction rules or manual override for edge cases

### AI-Powered Universal File Wrapper (Future-Proof)

- [ ] **LLM file parser** — Wrapper that accepts any file type (Excel, CSV, PDF, JSON, etc.), uses the AI assistant to automatically identify structure, file type, and schema, and extracts health-relevant data into a normalized format
- [ ] **On-the-fly ingestion** — Users can upload arbitrary health files; no predefined schemas required; AI infers columns, dates, biomarkers, and maps to the unified data model
- [ ] **Fallback to format-specific parsers** — When AI identifies Excel/PDF, optional hand-off to optimized parsers (openpyxl, pdfplumber) for performance; AI used for structure discovery and edge cases

### Cross-Cutting

- [x] **File upload UI** — Streamlit file uploader for Excel and PDF; preview parsed data before saving; store in user data directory (configurable path)
- [ ] **Data deduplication** — When Oura and Excel both have steps/calories, allow user to choose primary source or merge strategy
- [ ] **Unified date-range queries** — Single API/data layer that returns Oura + Excel + blood panel data for a date range
- [ ] **Export** — Allow exporting combined dataset (Oura + Excel + labs) as CSV for backup or external analysis
- [ ] **Privacy** — Ensure user data stays local; document storage location; optional encryption for sensitive health data
- [x] **Dependencies** — Add `openpyxl`, `pdfplumber` to requirements
- [x] **Sample files** — Add example CSV to `docs/data/`; PDF sample when pipeline is built

---

## Dashboard Improvements (Medium Priority)

- [ ] **Persistent token storage** — Consider encrypted cookie or secure session storage so users don't have to reconnect every time
- [x] **Export data** — Allow users to export date-range data as CSV (sidebar download button)
- [ ] **Mobile responsiveness** — Verify and improve layout on smaller screens
- [ ] **Error handling** — More graceful handling of API errors (rate limits, token expiry) with user-friendly messages

---

## Library & Infrastructure (Low Priority)

- [ ] **Webhook support** — Implement webhook registration and handling for real-time data updates (see Oura API docs)
- [ ] **Async client** — Add async variants of API methods for high-throughput use cases
- [ ] **Pre-commit hooks** — Add ruff, pytest to pre-commit for consistent CI
- [ ] **GitHub Actions** — CI workflow for tests and lint on push/PR

---

## Documentation & Polish (Low Priority)

- [ ] **API usage examples** — Add more code snippets to README for each data type
- [ ] **Troubleshooting guide** — Common OAuth errors, redirect URI mismatches, sandbox vs production
- [ ] **Changelog** — Maintain a CHANGELOG.md for releases

---

## Completed

- [x] Anomaly page index fix — `flagged[flagged].index` for correct iteration in "All Detected Anomalies"
- [x] Core API client with all 16 data types
- [x] OAuth2 auth (CLI and web flows)
- [x] Sandbox mode for development without real data
- [x] 7-page Streamlit dashboard
- [x] Centralized config via `.env` and `config.py`
- [x] Jupyter notebooks for exploration
- [x] 18 tests using sandbox endpoints
- [x] Deployment docs for Streamlit Community Cloud
