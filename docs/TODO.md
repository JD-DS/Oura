# TODO — Remaining Work

This document tracks what still needs to be built or improved in the Oura Ring API sandbox project.

---

## Phase 3: AI Health Assistant (High Priority)

The main planned feature. Full implementation plan in [03_ai_health_assistant.md](03_ai_health_assistant.md).

### Core Implementation

- [ ] **Agent orchestration layer** — Conversation loop with tool-calling LLM (Claude or GPT-4o)
- [ ] **Oura Data Tool** — Wrapper around `OuraClient` for the agent to fetch and summarize data on demand
- [ ] **PubMed Search Tool** — NCBI E-utilities integration for biomedical literature search
- [ ] **Statistical Analysis Tool** — Correlation, trend, and comparison helpers for the agent
- [ ] **Chart Generation Tool** — Generate inline Plotly charts in chat responses
- [ ] **Streamlit chat UI** — `st.chat_message` interface with conversation memory in session state
- [ ] **LLM provider abstraction** — Support both Anthropic and OpenAI, configurable via `AI_PROVIDER`

### Dependencies

- [ ] Add `anthropic` and `openai` to `requirements.txt` (or optional `ai` extra)
- [ ] Document `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `NCBI_API_KEY`, `NCBI_EMAIL` in `.env.example`

---

## Dashboard Improvements (Medium Priority)

- [ ] **Persistent token storage** — Consider encrypted cookie or secure session storage so users don't have to reconnect every time
- [ ] **Export data** — Allow users to export date-range data as CSV
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

- [x] Core API client with all 16 data types
- [x] OAuth2 auth (CLI and web flows)
- [x] Sandbox mode for development without real data
- [x] 7-page Streamlit dashboard
- [x] Centralized config via `.env` and `config.py`
- [x] Jupyter notebooks for exploration
- [x] 18 tests using sandbox endpoints
- [x] Deployment docs for Streamlit Community Cloud
