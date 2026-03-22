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
from styles import (
    get_custom_css,
    sidebar_title,
    sidebar_label,
    mode_indicator,
    theme_toggle_html,
)

DEMO_MODE = os.getenv("DEMO_MODE", "").lower() in ("true", "1", "yes")

st.set_page_config(
    page_title="Oura Health Dashboard",
    page_icon="💍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize theme mode in session state
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "minimal"

theme_mode = st.session_state.get("theme_mode", "minimal")

# Inject custom CSS based on theme mode
st.markdown(get_custom_css(theme_mode), unsafe_allow_html=True)

if DEMO_MODE:
    st.session_state["access_token"] = "__sandbox__"
    st.session_state["sandbox_mode"] = True
else:
    handle_callback()

    if not is_authenticated():
        show_login_page()
        st.stop()

# --- Sidebar controls ---

with st.sidebar:
    # Logo/Title
    st.markdown(sidebar_title(theme_mode), unsafe_allow_html=True)
    
    # Demo mode indicator
    is_sandbox = st.session_state.get("sandbox_mode", False)
    st.markdown(mode_indicator(is_sandbox, theme_mode), unsafe_allow_html=True)
    
    # Theme toggle
    st.markdown(theme_toggle_html(), unsafe_allow_html=True)
    theme_options = {"Minimal": "minimal", "Retro": "retro"}
    selected_theme = st.radio(
        "Theme mode",
        options=list(theme_options.keys()),
        index=0 if theme_mode == "minimal" else 1,
        horizontal=True,
        label_visibility="collapsed",
    )
    if theme_options[selected_theme] != theme_mode:
        st.session_state["theme_mode"] = theme_options[selected_theme]
        st.rerun()
    
    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)
    
    # Date range
    st.markdown(sidebar_label("Date Range"), unsafe_allow_html=True)
    
    today = default_end_date()
    start_default = default_start_date()
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start", value=start_default, max_value=today, label_visibility="collapsed")
    with col2:
        end_date = st.date_input("End", value=today, max_value=today, label_visibility="collapsed")

    if start_date > end_date:
        st.error("Invalid date range")
        st.stop()

    st.session_state["start_date"] = str(start_date)
    st.session_state["end_date"] = str(end_date)

    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

    if not DEMO_MODE and not is_sandbox:
        sandbox_toggle = st.toggle("Demo data", value=False)
        if sandbox_toggle:
            st.session_state["sandbox_mode"] = True
        else:
            st.session_state["sandbox_mode"] = False

    st.markdown("<hr style='margin: 1.25rem 0; border-color: rgba(255, 255, 255, 0.06);'>", unsafe_allow_html=True)
    
    # Export section
    st.markdown(sidebar_label("Export"), unsafe_allow_html=True)
    
    from components.data import get_all_daily_data_with_imported
    token = st.session_state.get("access_token", "")
    sandbox = st.session_state.get("sandbox_mode", False)
    start_str = st.session_state.get("start_date", str(start_default))
    end_str = st.session_state.get("end_date", str(today))
    
    if token:
        export_df = get_all_daily_data_with_imported(token, start_str, end_str, sandbox)
        if not export_df.empty:
            csv_bytes = export_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download CSV",
                data=csv_bytes,
                file_name=f"oura_{start_str}_{end_str}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.caption("No data to export")
    
    st.markdown("<hr style='margin: 1.25rem 0; border-color: rgba(255, 255, 255, 0.06);'>", unsafe_allow_html=True)
    
    if not DEMO_MODE:
        if st.button("Sign out", use_container_width=True):
            logout()
            st.rerun()

# --- Page navigation ---

dashboard_page = st.Page("pages/1_dashboard.py", title="Overview", icon="📊", default=True)
sleep_page = st.Page("pages/2_sleep.py", title="Sleep", icon="🌙")
readiness_page = st.Page("pages/3_readiness.py", title="Readiness", icon="⚡")
activity_page = st.Page("pages/4_activity.py", title="Activity", icon="🏃")
hr_stress_page = st.Page("pages/5_heart_rate_stress.py", title="Heart & Stress", icon="❤️")
correlations_page = st.Page("pages/6_correlations.py", title="Correlations", icon="🔗")
anomalies_page = st.Page("pages/7_anomalies.py", title="Anomalies", icon="🔍")
assistant_page = st.Page("pages/8_assistant.py", title="Assistant", icon="🤖")
import_page = st.Page("pages/9_import.py", title="Import", icon="📥")
labs_page = st.Page("pages/10_labs.py", title="Labs", icon="🧪")

nav = st.navigation([
    dashboard_page,
    sleep_page,
    readiness_page,
    activity_page,
    hr_stress_page,
    correlations_page,
    anomalies_page,
    assistant_page,
    import_page,
    labs_page,
])

nav.run()
