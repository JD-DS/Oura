"""Oura Health Dashboard — design system."""

from __future__ import annotations


def get_custom_css() -> str:
    """Return the dashboard CSS."""
    return """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ================================================================
       AGGRESSIVE OVERRIDES — these must beat Streamlit's defaults
       ================================================================ */

    /* --- Accent bar at top of page --- */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #2dd4bf 0%, #06b6d4 40%, #a78bfa 100%);
        z-index: 9999;
    }

    /* --- Base app --- */
    .stApp, .stApp > div {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: #09090b !important;
        color: #a1a1aa;
        -webkit-font-smoothing: antialiased;
    }

    /* --- NUKE all Streamlit chrome --- */
    #MainMenu, footer, .stDeployButton,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    button[title="View app in Streamlit Community Cloud"],
    .viewerBadge_container__r5tak,
    .styles_viewerBadge__CvC9N,
    [data-testid="manage-app-button"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
        overflow: hidden !important;
    }
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 0 !important;
        min-height: 0 !important;
        padding: 0 !important;
    }

    /* --- Main content area --- */
    .main .block-container {
        padding: 2.5rem 2.5rem 3rem !important;
        max-width: 1200px;
    }

    /* --- Typography — force Inter everywhere --- */
    h1, h2, h3, h4, h5, h6,
    p, span, label, div, a, li, td, th, input, textarea, select, button {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    h1, h2, h3, h4, h5, h6 {
        font-weight: 600 !important;
        color: #f4f4f5 !important;
        letter-spacing: -0.03em !important;
    }
    h1 { font-size: 1.6rem !important; }
    h2 { font-size: 1.2rem !important; }
    h3 { font-size: 0.95rem !important; }

    /* ================================================================
       SIDEBAR — completely restyled
       ================================================================ */
    [data-testid="stSidebar"] {
        background: #0c0c0f !important;
        border-right: 1px solid rgba(255,255,255,0.06) !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem !important;
    }

    /* Nav items — clean, no emojis (removed via app.py), pill-style active */
    [data-testid="stSidebarNav"] ul {
        padding: 0 0.5rem !important;
    }
    [data-testid="stSidebarNav"] li {
        margin-bottom: 1px !important;
    }
    [data-testid="stSidebarNav"] li a {
        font-size: 0.82rem !important;
        font-weight: 400 !important;
        color: #71717a !important;
        padding: 0.45rem 0.85rem !important;
        border-radius: 8px !important;
        transition: all 0.15s ease !important;
        text-decoration: none !important;
        display: block !important;
        border-left: 2px solid transparent !important;
    }
    [data-testid="stSidebarNav"] li a:hover {
        color: #d4d4d8 !important;
        background: rgba(255,255,255,0.03) !important;
    }
    [data-testid="stSidebarNav"] li a[aria-current="page"] {
        color: #f4f4f5 !important;
        font-weight: 500 !important;
        background: rgba(45, 212, 191, 0.06) !important;
        border-left-color: #2dd4bf !important;
    }

    /* Hide the sidebar collapse arrow styling */
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] {
        opacity: 0.3;
        transition: opacity 0.2s;
    }
    [data-testid="stSidebar"]:hover [data-testid="stSidebarCollapseButton"] {
        opacity: 0.7;
    }

    /* ================================================================
       METRIC CARDS — bolder, with gradient accent
       ================================================================ */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #141419 0%, #111115 100%) !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 12px !important;
        padding: 1rem 1.15rem !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.4), 0 0 1px rgba(255,255,255,0.05) inset !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.5), 0 0 1px rgba(255,255,255,0.08) inset !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.6rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        color: #52525b !important;
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: unset !important;
    }
    [data-testid="stMetricLabel"] > div,
    [data-testid="stMetricLabel"] > div > div {
        overflow: visible !important;
        text-overflow: unset !important;
        white-space: nowrap !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', 'SF Mono', monospace !important;
        font-size: 1.75rem !important;
        font-weight: 500 !important;
        color: #f4f4f5 !important;
        letter-spacing: -0.03em !important;
    }
    [data-testid="stMetricDelta"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.65rem !important;
    }
    [data-testid="stMetricDelta"] svg { display: none; }

    /* ================================================================
       BUTTONS
       ================================================================ */
    .stButton > button {
        background: #141419 !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 8px !important;
        color: #d4d4d8 !important;
        font-weight: 500 !important;
        font-size: 0.8rem !important;
        padding: 0.45rem 1rem !important;
        transition: all 0.12s ease !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3) !important;
    }
    .stButton > button:hover {
        background: #1c1c23 !important;
        border-color: rgba(255,255,255,0.12) !important;
        box-shadow: 0 3px 10px rgba(0,0,0,0.4) !important;
    }
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #2dd4bf 0%, #14b8a6 100%) !important;
        border: none !important;
        color: #09090b !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 12px rgba(45, 212, 191, 0.25) !important;
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 4px 20px rgba(45, 212, 191, 0.35) !important;
        filter: brightness(1.05);
    }
    .stDownloadButton > button {
        background: #141419 !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 8px !important;
        color: #d4d4d8 !important;
        font-weight: 500 !important;
        font-size: 0.8rem !important;
    }

    /* ================================================================
       INPUTS
       ================================================================ */
    .stTextInput > div > div,
    .stSelectbox > div > div,
    .stMultiSelect > div > div,
    .stDateInput > div > div {
        background: #141419 !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 8px !important;
    }
    .stTextInput > div > div:focus-within,
    .stSelectbox > div > div:focus-within {
        border-color: #2dd4bf !important;
        box-shadow: 0 0 0 2px rgba(45, 212, 191, 0.12) !important;
    }

    /* ================================================================
       EXPANDERS
       ================================================================ */
    .streamlit-expanderHeader,
    [data-testid="stExpander"] summary {
        background: #141419 !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 0.82rem !important;
        color: #a1a1aa !important;
    }
    .streamlit-expanderContent,
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        background: #111115 !important;
        border: 1px solid rgba(255,255,255,0.04) !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
    }

    /* ================================================================
       TABS — underline style
       ================================================================ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0 !important;
        background: transparent !important;
        border-bottom: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 0 !important;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 0.6rem 1.1rem !important;
        font-weight: 500 !important;
        font-size: 0.8rem !important;
        color: #52525b !important;
        background: transparent !important;
        border-radius: 0 !important;
        border-bottom: 2px solid transparent !important;
        margin-bottom: -1px !important;
    }
    .stTabs [aria-selected="true"] {
        color: #f4f4f5 !important;
        border-bottom-color: #2dd4bf !important;
    }

    /* ================================================================
       DATA FRAMES
       ================================================================ */
    [data-testid="stDataFrame"] {
        border-radius: 10px !important;
        overflow: hidden !important;
    }
    [data-testid="stDataFrame"] > div {
        background: #111115 !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-radius: 10px !important;
    }

    /* ================================================================
       CHAT
       ================================================================ */
    .stChatMessage {
        background: #111115 !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }
    [data-testid="stChatInput"] > div {
        background: #141419 !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 12px !important;
    }
    [data-testid="stChatInput"] > div:focus-within {
        border-color: #2dd4bf !important;
        box-shadow: 0 0 0 2px rgba(45, 212, 191, 0.12) !important;
    }

    /* ================================================================
       FILE UPLOADER
       ================================================================ */
    [data-testid="stFileUploader"] > div {
        background: #111115 !important;
        border: 1px dashed rgba(255,255,255,0.08) !important;
        border-radius: 12px !important;
    }
    [data-testid="stFileUploader"]:hover > div {
        border-color: rgba(45, 212, 191, 0.2) !important;
        background: rgba(45, 212, 191, 0.02) !important;
    }

    /* ================================================================
       SLIDERS, TOGGLES, PROGRESS
       ================================================================ */
    .stSlider [data-baseweb="slider"] [role="slider"] {
        background: #2dd4bf !important;
    }
    .stSlider > div > div > div {
        background: #2dd4bf !important;
    }
    .stToggle > label > div {
        background: #25252e !important;
    }
    .stProgress > div > div {
        background: linear-gradient(90deg, #2dd4bf, #06b6d4) !important;
    }

    /* ================================================================
       ALERTS
       ================================================================ */
    .stAlert {
        border-radius: 10px !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
    }

    /* ================================================================
       CODE
       ================================================================ */
    code {
        font-family: 'JetBrains Mono', monospace !important;
        background: #1c1c23 !important;
        padding: 0.15rem 0.35rem !important;
        border-radius: 4px !important;
        font-size: 0.82em !important;
        color: #2dd4bf !important;
    }

    /* ================================================================
       PLOTLY CHARTS — seamless, modebar hidden until hover
       ================================================================ */
    .js-plotly-plot {
        border-radius: 10px !important;
    }
    .js-plotly-plot .modebar {
        opacity: 0 !important;
        transition: opacity 0.2s ease !important;
    }
    .js-plotly-plot:hover .modebar {
        opacity: 0.5 !important;
    }

    /* ================================================================
       SMALL ELEMENTS
       ================================================================ */
    hr {
        border: none !important;
        height: 1px !important;
        background: rgba(255,255,255,0.05) !important;
        margin: 1.25rem 0 !important;
    }
    .stCaption, [data-testid="stCaption"] {
        font-size: 0.7rem !important;
        color: #52525b !important;
    }
    [data-testid="column"] {
        padding: 0 0.4rem !important;
    }

    /* ================================================================
       RESPONSIVE
       ================================================================ */
    @media (prefers-reduced-motion: reduce) {
        * { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
    }
    @media (max-width: 768px) {
        .main .block-container { padding: 1.5rem 1rem 2rem !important; }
        h1 { font-size: 1.25rem !important; }
        [data-testid="stMetric"] { padding: 0.65rem !important; }
        [data-testid="stMetricValue"] { font-size: 1.2rem !important; }
        [data-testid="stSidebar"] { min-width: 0 !important; }
        .js-plotly-plot { overflow-x: auto; }
    }
</style>
"""


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------

def page_header(title: str, subtitle: str = "") -> str:
    sub = (
        f'<p style="color:#52525b;font-size:.82rem;margin:0;font-weight:400;">{subtitle}</p>'
        if subtitle else ""
    )
    return (
        f'<div style="margin-bottom:2rem;padding-bottom:1rem;'
        f'border-bottom:1px solid rgba(255,255,255,0.06);">'
        f'<h1 style="font-size:1.6rem;font-weight:700;color:#f4f4f5;margin:0 0 .3rem 0;'
        f'letter-spacing:-.03em;line-height:1.2;">{title}</h1>'
        f'{sub}</div>'
    )


def section_header(title: str) -> str:
    return (
        f'<div style="display:flex;align-items:center;gap:.5rem;margin:2rem 0 .75rem 0;'
        f'padding-bottom:.5rem;border-bottom:1px solid rgba(255,255,255,0.05);">'
        f'<div style="width:3px;height:14px;border-radius:2px;'
        f'background:linear-gradient(180deg,#2dd4bf,#06b6d4);flex-shrink:0;"></div>'
        f'<span style="font-size:.7rem;font-weight:600;color:#71717a;'
        f'letter-spacing:.08em;text-transform:uppercase;">{title}</span></div>'
    )


def metric_card(label: str, value: str, delta: str = "", status: str = "") -> str:
    colors = {"good": "#34d399", "warning": "#fbbf24", "bad": "#f87171", "": "#f4f4f5"}
    vc = colors.get(status, "#f4f4f5")
    d = f'<div style="font-size:.65rem;color:#52525b;margin-top:.2rem;">{delta}</div>' if delta else ""
    return (
        f'<div style="background:linear-gradient(135deg,#141419,#111115);'
        f'border:1px solid rgba(255,255,255,0.06);border-radius:12px;padding:1rem 1.1rem;'
        f'box-shadow:0 2px 8px rgba(0,0,0,0.4);">'
        f'<div style="font-size:.58rem;font-weight:600;text-transform:uppercase;'
        f'letter-spacing:.1em;color:#52525b;margin-bottom:.4rem;">{label}</div>'
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:1.75rem;font-weight:500;'
        f'color:{vc};letter-spacing:-.03em;line-height:1.1;">{value}</div>'
        f'{d}</div>'
    )


def info_card(text: str) -> str:
    return (
        f'<div style="background:rgba(45,212,191,0.03);border-left:3px solid #2dd4bf;'
        f'border-radius:0 10px 10px 0;padding:.75rem 1rem;display:flex;align-items:center;gap:.6rem;">'
        f'<span style="color:#a1a1aa;font-size:.82rem;line-height:1.5;">{text}</span></div>'
    )


def success_card(text: str) -> str:
    return (
        f'<div style="background:rgba(52,211,153,0.03);border-left:3px solid #34d399;'
        f'border-radius:0 10px 10px 0;padding:.75rem 1rem;display:flex;align-items:center;gap:.6rem;">'
        f'<span style="color:#a1a1aa;font-size:.82rem;">{text}</span></div>'
    )


def warning_card(text: str) -> str:
    return (
        f'<div style="background:rgba(251,191,36,0.03);border-left:3px solid #fbbf24;'
        f'border-radius:0 10px 10px 0;padding:.75rem 1rem;display:flex;align-items:center;gap:.6rem;">'
        f'<span style="color:#a1a1aa;font-size:.82rem;">{text}</span></div>'
    )


def empty_state(title: str, description: str, icon: str = "&#9671;") -> str:
    return (
        f'<div style="text-align:center;padding:3.5rem 2rem;'
        f'background:linear-gradient(135deg,#111115,#0e0e12);'
        f'border:1px solid rgba(255,255,255,0.04);border-radius:16px;'
        f'box-shadow:0 4px 16px rgba(0,0,0,0.3);">'
        f'<div style="font-size:1.5rem;margin-bottom:.75rem;color:#3f3f46;opacity:.6;">{icon}</div>'
        f'<div style="font-size:.95rem;font-weight:600;color:#f4f4f5;margin-bottom:.3rem;">{title}</div>'
        f'<div style="font-size:.8rem;color:#52525b;max-width:300px;margin:0 auto;line-height:1.5;">{description}</div>'
        f'</div>'
    )


def neon_badge(text: str, color: str = "cyan") -> str:
    palette = {
        "cyan": ("#2dd4bf", "rgba(45,212,191,0.06)", "rgba(45,212,191,0.15)"),
        "magenta": ("#fb7185", "rgba(251,113,133,0.06)", "rgba(251,113,133,0.15)"),
        "amber": ("#fbbf24", "rgba(251,191,36,0.06)", "rgba(251,191,36,0.15)"),
        "green": ("#34d399", "rgba(52,211,153,0.06)", "rgba(52,211,153,0.15)"),
    }
    fg, bg, bd = palette.get(color, palette["cyan"])
    return (
        f'<span style="background:{bg};color:{fg};border:1px solid {bd};'
        f'padding:.2rem .6rem;border-radius:5px;font-size:.65rem;font-weight:500;'
        f'display:inline-block;letter-spacing:.02em;">{text}</span>'
    )


def sidebar_title() -> str:
    return (
        '<div style="margin:0 .85rem .85rem;padding-bottom:.6rem;'
        'border-bottom:1px solid rgba(255,255,255,0.06);">'
        '<span style="font-size:1.05rem;font-weight:700;color:#f4f4f5;letter-spacing:-.02em;">Oura</span>'
        '<span style="font-size:1.05rem;font-weight:300;color:#3f3f46;letter-spacing:-.02em;"> Health</span>'
        '</div>'
    )


def sidebar_label(text: str) -> str:
    return (
        f'<p style="font-size:.6rem;font-weight:600;text-transform:uppercase;'
        f'letter-spacing:.1em;color:#3f3f46;margin:0 0 .25rem 0;">{text}</p>'
    )


def mode_indicator(is_sandbox: bool) -> str:
    if not is_sandbox:
        return ""
    return (
        '<div style="background:rgba(45,212,191,0.04);border:1px solid rgba(45,212,191,0.1);'
        'border-radius:6px;padding:.25rem .6rem;margin-bottom:.75rem;'
        'font-size:.62rem;font-weight:500;color:#2dd4bf;letter-spacing:.02em;">'
        'Sandbox Mode</div>'
    )


# Backwards compatibility
def main_header(title: str, subtitle: str = "") -> str:
    return page_header(title, subtitle)

def info_box(text: str) -> str:
    return info_card(text)

def success_box(text: str) -> str:
    return success_card(text)

def warning_box(text: str) -> str:
    return warning_card(text)

def feature_badge(text: str, color: str = "cyan") -> str:
    return neon_badge(text, color)

def stat_card(label: str, value: str, delta: str = "", status: str = "") -> str:
    return metric_card(label, value, delta, status)

def theme_toggle_html() -> str:
    return ""
