# TODO — Future Work

This document tracks remaining improvements and future features. **Phase 3 (AI Assistant) and Phase 4 (External Data) are complete.**

---

## Completed (Phase 3 & 4)

### Phase 3: AI Health Assistant
- [x] Agent orchestration with tool-calling (Claude/GPT-4o)
- [x] Oura Data, PubMed, statistical analysis, chart generation tools
- [x] Streamlit chat UI with conversation memory
- [x] LLM provider abstraction (Anthropic + OpenAI)
- [x] AI Assistant extended to query imported data and lab results

### Phase 4: External Health Data
- [x] Excel/CSV import (steps, calories, workouts)
- [x] Blood panel PDF parsing (pdfplumber)
- [x] SQLite storage (activity + lab_results)
- [x] Import Data page (Excel + PDF tabs)
- [x] Lab Results page (biomarker trends, reference ranges)
- [x] Activity, Correlations, Anomaly: merge imported metrics
- [x] Export CSV (sidebar download)
- [x] Data privacy: check_no_secrets, .gitignore, pre-commit

---

## Future Work

### Phase 4 Extensions (Medium Priority)
- [ ] **Lab–Oura correlations** — Correlate biomarkers with Oura metrics (e.g. HRV vs inflammation, sleep vs glucose)
- [ ] **Lab anomaly detection** — Extend anomaly detection to lab trends (rising LDL, declining vitamin D)
- [ ] **Data deduplication** — When Oura and Excel both have steps/calories, allow user to choose primary source or merge strategy
- [ ] **Varied PDF formats** — Configurable extraction rules or manual override for labs with different layouts
- [ ] **Unified date-range API** — Single data layer returning Oura + Excel + labs for a date range

### AI-Powered Universal File Wrapper (Future-Proof)
- [ ] **LLM file parser** — Accept any file type, use AI to identify structure/schema, extract health data
- [ ] **On-the-fly ingestion** — Upload arbitrary health files; AI infers columns, dates, biomarkers

### Dashboard Improvements (Medium Priority)
- [ ] **Persistent token storage** — Encrypted cookie or session storage so users don't reconnect every time
- [ ] **Mobile responsiveness** — Verify and improve layout on smaller screens
- [ ] **Error handling** — Graceful handling of API errors (rate limits, token expiry)

### Library & Infrastructure (Low Priority)
- [ ] **Webhook support** — Real-time data updates (see Oura API docs)
- [ ] **Async client** — Async variants for high-throughput use cases
- [ ] **GitHub Actions** — CI workflow for tests and lint on push/PR
- [ ] **Privacy enhancements** — Document storage location; optional encryption for sensitive data

### Documentation & Polish (Low Priority)
- [ ] **API usage examples** — More code snippets in README for each data type
- [ ] **Troubleshooting guide** — OAuth errors, redirect URI mismatches, sandbox vs production
- [ ] **Changelog** — CHANGELOG.md for releases

---

## Quick Start When Resuming

1. **Branch:** `feature/phase3-phase4-complete`
2. **Run dashboard:** `streamlit run apps/dashboard/app.py`
3. **AI Assistant:** Set `AI_PROVIDER` and `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` in `.env`
4. **Import data:** Use Import Data page for Excel/CSV and lab PDFs
5. **Pre-commit:** `pip install pre-commit && pre-commit install`
