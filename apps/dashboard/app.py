"""Oura Health Dashboard -- main entry point.

Handles authentication, sidebar controls, and page navigation.
Run with: streamlit run apps/dashboard/app.py
"""

import sys
import os

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from config import default_start_date, default_end_date
from components.auth_web import (
    handle_callback,
    is_authenticated,
    logout,
    show_login_page,
)

st.set_page_config(
    page_title="Oura Health Dashboard",
    page_icon="💍",
    layout="wide",
    initial_sidebar_state="expanded",
)

handle_callback()

if not is_authenticated():
    show_login_page()
    st.stop()

# --- Sidebar controls (shared across all pages) ---

with st.sidebar:
    st.title("Oura Dashboard")

    is_sandbox = st.session_state.get("sandbox_mode", False)
    if is_sandbox:
        st.info("Sandbox mode -- using demo data")

    st.markdown("### Date Range")
    today = default_end_date()
    start_default = default_start_date()
    start_date = st.date_input("Start", value=start_default, max_value=today)
    end_date = st.date_input("End", value=today, max_value=today)

    if start_date > end_date:
        st.error("Start date must be before end date")
        st.stop()

    st.session_state["start_date"] = str(start_date)
    st.session_state["end_date"] = str(end_date)

    if not is_sandbox:
        st.markdown("---")
        sandbox_toggle = st.toggle("Demo mode (sandbox data)", value=False)
        if sandbox_toggle:
            st.session_state["sandbox_mode"] = True
        else:
            st.session_state["sandbox_mode"] = False

    st.markdown("---")
    if st.button("Logout", use_container_width=True):
        logout()
        st.rerun()

# --- Page navigation ---

dashboard_page = st.Page("pages/1_dashboard.py", title="Dashboard", icon="📊", default=True)
sleep_page = st.Page("pages/2_sleep.py", title="Sleep Analyzer", icon="🌙")
readiness_page = st.Page("pages/3_readiness.py", title="Readiness & Recovery", icon="⚡")
activity_page = st.Page("pages/4_activity.py", title="Activity", icon="🏃")
hr_stress_page = st.Page("pages/5_heart_rate_stress.py", title="Heart Rate & Stress", icon="❤️")
correlations_page = st.Page("pages/6_correlations.py", title="Correlations", icon="🔗")
anomalies_page = st.Page("pages/7_anomalies.py", title="Anomaly Detection", icon="🔍")

nav = st.navigation([
    dashboard_page,
    sleep_page,
    readiness_page,
    activity_page,
    hr_stress_page,
    correlations_page,
    anomalies_page,
])

nav.run()
