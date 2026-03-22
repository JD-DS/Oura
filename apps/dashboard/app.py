"""Oura Health Dashboard -- main entry point.

Handles authentication, sidebar controls, and page navigation.
Run with: streamlit run apps/dashboard/app.py
"""

import sys
import os

import streamlit as st
from streamlit.components.v1 import html as _components_html

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
)

def _check_demo_mode() -> bool:
    if os.getenv("DEMO_MODE", "").lower() in ("true", "1", "yes"):
        return True
    try:
        val = st.secrets["DEMO_MODE"]
        if str(val).lower() in ("true", "1", "yes"):
            return True
    except (KeyError, FileNotFoundError, Exception):
        pass
    # Auto-demo when no OAuth credentials are configured
    if not os.getenv("OURA_CLIENT_ID"):
        return True
    return False

DEMO_MODE = _check_demo_mode()

st.set_page_config(
    page_title="Oura Health Dashboard",
    page_icon="💍",
    layout="wide",
    initial_sidebar_state="auto",
)

st.markdown(get_custom_css(), unsafe_allow_html=True)

if DEMO_MODE:
    st.session_state["access_token"] = "__sandbox__"
    st.session_state["sandbox_mode"] = True
else:
    handle_callback()

    if not is_authenticated():
        show_login_page()
        st.stop()

# --- Sidebar ---

with st.sidebar:
    st.markdown(sidebar_title(), unsafe_allow_html=True)

    is_sandbox = st.session_state.get("sandbox_mode", False)
    st.markdown(mode_indicator(is_sandbox), unsafe_allow_html=True)

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

    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

    if not DEMO_MODE and not is_sandbox:
        sandbox_toggle = st.toggle("Demo data", value=False)
        if sandbox_toggle:
            st.session_state["sandbox_mode"] = True
        else:
            st.session_state["sandbox_mode"] = False

    st.markdown("<hr style='margin:1rem 0;border-color:rgba(255,255,255,0.06);'>", unsafe_allow_html=True)

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

    st.markdown("<hr style='margin:1rem 0;border-color:rgba(255,255,255,0.06);'>", unsafe_allow_html=True)

    if not DEMO_MODE:
        if st.button("Sign out", use_container_width=True):
            logout()
            st.rerun()

# --- Sidebar toggle ---

_SIDEBAR_TOGGLE_JS = """
<script>
(function() {
    var doc = window.parent.document;

    var old = doc.getElementById('sidebar-toggle-btn');
    if (old) old.remove();

    var btn = doc.createElement('button');
    btn.id = 'sidebar-toggle-btn';
    btn.title = 'Toggle sidebar';
    btn.setAttribute('aria-label', 'Toggle sidebar');
    btn.innerHTML = '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="3" y1="5" x2="17" y2="5"/><line x1="3" y1="10" x2="17" y2="10"/><line x1="3" y1="15" x2="17" y2="15"/></svg>';

    btn.style.cssText = [
        'position:fixed', 'top:12px', 'left:12px', 'z-index:999999',
        'width:44px', 'height:44px',
        'background:#141419',
        'border:1px solid rgba(255,255,255,0.15)',
        'border-radius:10px', 'cursor:pointer',
        'color:#a1a1aa',
        'display:none', 'align-items:center', 'justify-content:center',
        'transition:all .15s ease', 'padding:0',
        'box-shadow:0 4px 16px rgba(0,0,0,0.6)'
    ].join(';');

    btn.onmouseover = function() {
        btn.style.borderColor = 'rgba(45,212,191,0.4)';
        btn.style.color = '#2dd4bf';
        btn.style.boxShadow = '0 4px 20px rgba(0,0,0,0.7), 0 0 0 1px rgba(45,212,191,0.15)';
    };
    btn.onmouseout = function() {
        btn.style.borderColor = 'rgba(255,255,255,0.15)';
        btn.style.color = '#a1a1aa';
        btn.style.boxShadow = '0 4px 16px rgba(0,0,0,0.6)';
    };

    function getSidebar() {
        return doc.querySelector('[data-testid="stSidebar"]');
    }

    function isExpanded() {
        var sb = getSidebar();
        if (!sb) return false;
        return sb.getAttribute('aria-expanded') !== 'false';
    }

    function updateVisibility() {
        btn.style.display = isExpanded() ? 'none' : 'flex';
    }

    btn.onclick = function() {
        var targets = [
            '[data-testid="stExpandSidebarButton"]',
            '[data-testid="collapsedControl"] button',
            'button[kind="header"]'
        ];
        for (var i = 0; i < targets.length; i++) {
            var el = doc.querySelector(targets[i]);
            if (el) { el.click(); break; }
        }
        setTimeout(updateVisibility, 300);
    };

    doc.body.appendChild(btn);

    // --- Fix broken Material icon text everywhere ---
    var iconMap = {
        'keyboard_double_arrow_left': '\u2039',
        'keyboard_double_arrow_right': '\u203A',
        'keyboard_arrow_right': '\u25B8',
        'keyboard_arrow_down': '\u25BE',
        'keyboard_arrow_left': '\u2039',
        'keyboard_arrow_up': '\u25B4',
        'expand_more': '\u25BE',
        'expand_less': '\u25B4',
        'chevron_right': '\u203A',
        'chevron_left': '\u2039',
        'close': '\u00D7',
        'menu': '\u2630'
    };

    function fixIcons() {
        var walker = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT, null, false);
        var node;
        while (node = walker.nextNode()) {
            var txt = node.textContent.trim();
            if (iconMap[txt]) {
                var el = node.parentElement;
                if (el && el.tagName !== 'SCRIPT' && el.tagName !== 'STYLE') {
                    el.textContent = iconMap[txt];
                    el.style.fontFamily = 'Inter, system-ui, sans-serif';
                    el.style.fontSize = txt.indexOf('double') >= 0 ? '18px' : '14px';
                    el.style.lineHeight = '1';
                }
            }
        }
    }

    // Observe all changes to catch sidebar state and fix icons
    var observer = new MutationObserver(function(mutations) {
        var needIconFix = false;
        for (var i = 0; i < mutations.length; i++) {
            var m = mutations[i];
            if (m.type === 'attributes' && m.attributeName === 'aria-expanded') {
                updateVisibility();
            }
            if (m.type === 'childList' && m.addedNodes.length > 0) {
                updateVisibility();
                needIconFix = true;
            }
        }
        if (needIconFix) fixIcons();
    });
    observer.observe(doc.body, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['aria-expanded']
    });

    // Initial runs with retries for late DOM mount
    updateVisibility();
    fixIcons();
    setTimeout(function() { updateVisibility(); fixIcons(); }, 500);
    setTimeout(function() { updateVisibility(); fixIcons(); }, 1500);
    setTimeout(function() { updateVisibility(); fixIcons(); }, 3000);
    setTimeout(fixIcons, 5000);
})();
</script>
"""
_components_html(_SIDEBAR_TOGGLE_JS, height=0)

# --- Page navigation ---

dashboard_page = st.Page("pages/1_dashboard.py", title="Overview", default=True)
sleep_page = st.Page("pages/2_sleep.py", title="Sleep")
readiness_page = st.Page("pages/3_readiness.py", title="Readiness")
activity_page = st.Page("pages/4_activity.py", title="Activity")
hr_stress_page = st.Page("pages/5_heart_rate_stress.py", title="Heart & Stress")
correlations_page = st.Page("pages/6_correlations.py", title="Correlations")
anomalies_page = st.Page("pages/7_anomalies.py", title="Anomalies")
assistant_page = st.Page("pages/8_assistant.py", title="AI Assistant")
import_page = st.Page("pages/9_import.py", title="Import")
labs_page = st.Page("pages/10_labs.py", title="Labs")

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
