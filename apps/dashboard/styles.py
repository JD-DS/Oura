"""Premium Health Analytics Dashboard Styles.

Sophisticated dark palette with teal accent, refined typography,
and polished component styling inspired by Whoop, Apple Health, and Oura.
"""

from __future__ import annotations


def get_custom_css(theme_mode: str = "minimal") -> str:
    """Return custom CSS for the dashboard."""
    is_retro = theme_mode == "retro"

    glow_intensity = "0.4" if is_retro else "0"
    grid_opacity = "0.03" if is_retro else "0"
    border_glow = "0 0 8px rgba(45, 212, 191, 0.15)" if is_retro else "none"
    text_glow = "0 0 12px rgba(45, 212, 191, 0.3)" if is_retro else "none"

    return f"""
<style>
    /* === FONTS === */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* === CSS CUSTOM PROPERTIES === */
    :root {{
        /* Background layers — warm dark */
        --bg-void: #0c0c10;
        --bg-primary: #101014;
        --bg-surface: #16161c;
        --bg-elevated: #1e1e26;
        --bg-hover: #26262f;

        /* Text hierarchy — warm grays */
        --text-primary: #f0f0f2;
        --text-secondary: #a1a1aa;
        --text-muted: #71717a;
        --text-dim: #52525b;

        /* Accent — refined teal */
        --accent: #2dd4bf;
        --accent-soft: rgba(45, 212, 191, 0.12);
        --accent-border: rgba(45, 212, 191, 0.25);
        --accent-hover: rgba(45, 212, 191, 0.18);

        /* Supporting palette */
        --violet: #a78bfa;
        --rose: #fb7185;
        --amber: #fbbf24;
        --sky: #38bdf8;

        /* Status */
        --status-good: #34d399;
        --status-warning: #fbbf24;
        --status-danger: #f87171;

        /* Borders */
        --border-subtle: rgba(255, 255, 255, 0.04);
        --border-default: rgba(255, 255, 255, 0.07);
        --border-hover: rgba(45, 212, 191, 0.2);
        --border-active: rgba(45, 212, 191, 0.35);

        /* Theme-dependent */
        --glow-intensity: {glow_intensity};
        --grid-opacity: {grid_opacity};
        --border-glow: {border_glow};
        --text-glow: {text_glow};

        /* Spacing */
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;

        /* Typography */
        --font-display: 'DM Sans', -apple-system, sans-serif;
        --font-body: 'Inter', -apple-system, sans-serif;
        --font-mono: 'JetBrains Mono', 'SF Mono', monospace;
    }}

    /* === BASE STYLES === */
    .stApp {{
        font-family: var(--font-body);
        background: var(--bg-void);
        color: var(--text-secondary);
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }}

    /* Subtle grid (retro mode only) */
    .stApp::before {{
        content: '';
        position: fixed;
        inset: 0;
        background:
            linear-gradient(to bottom, transparent 0%, var(--bg-void) 100%),
            repeating-linear-gradient(90deg, rgba(45, 212, 191, var(--grid-opacity)) 0px, transparent 1px, transparent 80px),
            repeating-linear-gradient(0deg, rgba(45, 212, 191, var(--grid-opacity)) 0px, transparent 1px, transparent 80px);
        pointer-events: none;
        z-index: 0;
    }}

    /* Hide Streamlit chrome */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header[data-testid="stHeader"] {{background: transparent;}}
    .stDeployButton {{display: none;}}

    /* Main content */
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
        position: relative;
        z-index: 1;
    }}

    /* === TYPOGRAPHY === */
    h1, h2, h3, h4, h5, h6 {{
        font-family: var(--font-display);
        font-weight: 600;
        letter-spacing: -0.025em;
        color: var(--text-primary);
        line-height: 1.2;
    }}

    h1 {{
        font-size: 1.75rem;
        text-shadow: var(--text-glow);
    }}

    h2 {{ font-size: 1.35rem; }}
    h3 {{ font-size: 1.1rem; }}

    p, span, label, div {{
        font-family: var(--font-body);
    }}

    html {{
        scroll-behavior: smooth;
    }}

    /* === SIDEBAR === */
    [data-testid="stSidebar"] {{
        background: var(--bg-primary);
        border-right: 1px solid var(--border-subtle);
    }}

    [data-testid="stSidebar"] > div:first-child {{
        padding-top: 1.25rem;
    }}

    /* === METRIC CARDS === */
    [data-testid="stMetric"] {{
        background: var(--bg-surface);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-md);
        padding: 1rem 1.25rem;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }}

    [data-testid="stMetric"]:hover {{
        border-color: var(--border-hover);
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
    }}

    [data-testid="stMetricLabel"] {{
        font-family: var(--font-body) !important;
        font-size: 0.7rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        color: var(--text-muted) !important;
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: unset !important;
    }}

    [data-testid="stMetricLabel"] > div {{
        overflow: visible !important;
        text-overflow: unset !important;
        white-space: nowrap !important;
    }}

    [data-testid="stMetricLabel"] > div > div {{
        overflow: visible !important;
        text-overflow: unset !important;
    }}

    [data-testid="stMetricValue"] {{
        font-family: var(--font-mono) !important;
        font-size: 1.75rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.02em !important;
        text-shadow: var(--text-glow);
    }}

    [data-testid="stMetricDelta"] {{
        font-family: var(--font-mono) !important;
        font-size: 0.7rem !important;
        font-weight: 500 !important;
    }}

    [data-testid="stMetricDelta"] svg {{
        display: none;
    }}

    /* === BUTTONS === */
    .stButton > button {{
        font-family: var(--font-body);
        background: var(--bg-surface);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-sm);
        color: var(--text-primary);
        font-weight: 500;
        font-size: 0.8rem;
        padding: 0.5rem 1rem;
        transition: all 0.15s ease;
    }}

    .stButton > button:hover {{
        background: var(--bg-elevated);
        border-color: var(--accent-border);
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
    }}

    .stButton > button:active {{
        transform: scale(0.98);
    }}

    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"] {{
        background: var(--accent);
        border: none;
        color: #0c0c10;
        font-weight: 600;
    }}

    .stButton > button[kind="primary"]:hover {{
        box-shadow: 0 4px 20px rgba(45, 212, 191, 0.3);
        filter: brightness(1.1);
    }}

    /* Download button */
    .stDownloadButton > button {{
        font-family: var(--font-body);
        background: var(--bg-surface);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-sm);
        color: var(--text-primary);
        font-weight: 500;
        font-size: 0.8rem;
    }}

    .stDownloadButton > button:hover {{
        border-color: var(--accent-border);
    }}

    /* === INPUTS === */
    .stTextInput > div > div,
    .stSelectbox > div > div,
    .stMultiSelect > div > div,
    .stDateInput > div > div {{
        background: var(--bg-surface);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-sm);
        font-family: var(--font-body);
    }}

    .stTextInput > div > div:focus-within,
    .stSelectbox > div > div:focus-within {{
        border-color: var(--accent);
        box-shadow: 0 0 0 2px var(--accent-soft);
    }}

    /* === EXPANDERS === */
    .streamlit-expanderHeader {{
        font-family: var(--font-body);
        background: var(--bg-surface);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-sm);
        font-weight: 500;
        font-size: 0.85rem;
        color: var(--text-secondary);
    }}

    .streamlit-expanderHeader:hover {{
        border-color: var(--border-hover);
        color: var(--text-primary);
    }}

    .streamlit-expanderContent {{
        background: var(--bg-surface);
        border: 1px solid var(--border-default);
        border-top: none;
        border-radius: 0 0 var(--radius-sm) var(--radius-sm);
    }}

    /* === TABS === */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 2px;
        background: var(--bg-surface);
        border-radius: var(--radius-sm);
        padding: 3px;
        border: 1px solid var(--border-default);
    }}

    .stTabs [data-baseweb="tab"] {{
        font-family: var(--font-body);
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        font-size: 0.8rem;
        color: var(--text-muted);
        background: transparent;
    }}

    .stTabs [aria-selected="true"] {{
        background: var(--bg-elevated);
        color: var(--accent);
    }}

    /* === DATA FRAMES === */
    [data-testid="stDataFrame"] {{
        border-radius: var(--radius-md);
        overflow: hidden;
    }}

    [data-testid="stDataFrame"] > div {{
        background: var(--bg-surface);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-md);
    }}

    /* === CHAT === */
    .stChatMessage {{
        background: var(--bg-surface);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-md);
        padding: 1rem;
    }}

    [data-testid="stChatInput"] > div {{
        background: var(--bg-surface);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-md);
    }}

    [data-testid="stChatInput"] > div:focus-within {{
        border-color: var(--accent);
        box-shadow: 0 0 0 2px var(--accent-soft);
    }}

    /* === FILE UPLOADER === */
    [data-testid="stFileUploader"] > div {{
        background: var(--bg-surface);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-md);
    }}

    [data-testid="stFileUploader"]:hover > div {{
        border-color: var(--accent-border);
    }}

    /* === SLIDERS === */
    .stSlider > div > div > div {{
        background: linear-gradient(90deg, var(--accent), var(--violet));
    }}

    /* === TOGGLE === */
    .stToggle > label > div {{
        background: var(--bg-elevated);
    }}

    /* === PROGRESS === */
    .stProgress > div > div {{
        background: linear-gradient(90deg, var(--accent), var(--sky));
    }}

    /* === ALERTS === */
    .stAlert {{
        border-radius: var(--radius-sm);
        border: 1px solid var(--border-default);
    }}

    /* === CODE === */
    code {{
        font-family: var(--font-mono);
        background: var(--bg-elevated);
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-size: 0.85em;
        color: var(--accent);
    }}

    /* === DIVIDERS === */
    hr {{
        border: none;
        height: 1px;
        background: var(--border-default);
        margin: 1.5rem 0;
    }}

    /* === PLOTLY CHARTS === */
    .js-plotly-plot {{
        border-radius: var(--radius-md);
    }}

    /* === CAPTIONS === */
    .stCaption, [data-testid="stCaption"] {{
        font-family: var(--font-body) !important;
        font-size: 0.75rem !important;
        color: var(--text-muted) !important;
    }}

    /* Reduced motion support */
    @media (prefers-reduced-motion: reduce) {{
        *, *::before, *::after {{
            animation-duration: 0.01ms !important;
            transition-duration: 0.01ms !important;
        }}
    }}

    /* === MOBILE RESPONSIVE === */
    @media (max-width: 768px) {{
        .main .block-container {{
            padding-top: 1rem;
            padding-bottom: 2rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }}

        h1 {{ font-size: 1.3rem; }}
        h2 {{ font-size: 1.1rem; }}
        h3 {{ font-size: 0.95rem; }}

        [data-testid="stMetric"] {{
            padding: 0.75rem;
        }}

        [data-testid="stMetricValue"] {{
            font-size: 1.3rem !important;
        }}

        [data-testid="stMetricLabel"] {{
            font-size: 0.6rem !important;
        }}

        .rm-page-title {{
            font-size: 1.3rem !important;
        }}

        .rm-section-header {{
            font-size: 0.7rem !important;
        }}

        [data-testid="stSidebar"] {{
            min-width: 0 !important;
        }}

        .js-plotly-plot {{
            overflow-x: auto;
        }}
    }}
</style>
"""


def page_header(title: str, subtitle: str = "", theme_mode: str = "minimal") -> str:
    """Generate HTML for a page header."""
    is_retro = theme_mode == "retro"
    title_glow = "text-shadow: 0 0 20px rgba(45, 212, 191, 0.3);" if is_retro else ""
    subtitle_html = f'<p class="rm-page-subtitle">{subtitle}</p>' if subtitle else ""
    return (
        "<style>"
        ".rm-page-header{margin-bottom:2rem;padding-bottom:1.25rem;"
        "border-bottom:1px solid rgba(255,255,255,0.06);}"
        ".rm-page-title{font-family:'DM Sans',sans-serif;font-size:1.6rem;"
        f"font-weight:700;color:#f0f0f2;margin:0 0 .35rem 0;letter-spacing:-.03em;{title_glow}}}"
        ".rm-page-subtitle{font-family:'Inter',sans-serif;font-size:.85rem;"
        "color:#71717a;margin:0;font-weight:400;}"
        "</style>"
        f'<div class="rm-page-header"><h1 class="rm-page-title">{title}</h1>'
        f"{subtitle_html}</div>"
    )


def section_header(title: str, theme_mode: str = "minimal") -> str:
    """Generate HTML for a section header."""
    is_retro = theme_mode == "retro"
    accent = "background:linear-gradient(90deg,#2dd4bf,transparent);" if is_retro else "background:rgba(45,212,191,0.5);"
    return (
        "<style>"
        ".rm-section-header{font-family:'DM Sans',sans-serif;font-size:.8rem;"
        "font-weight:600;color:#a1a1aa;margin:2.5rem 0 1rem 0;padding-bottom:.6rem;"
        "letter-spacing:.02em;border-bottom:1px solid rgba(255,255,255,0.06);"
        "position:relative;}"
        f".rm-section-header::after{{content:'';position:absolute;bottom:-1px;left:0;"
        f"width:40px;height:2px;{accent}border-radius:1px;}}"
        "</style>"
        f'<h3 class="rm-section-header">{title}</h3>'
    )


def metric_card(label: str, value: str, delta: str = "", status: str = "", theme_mode: str = "minimal") -> str:
    """Generate HTML for a metric card with monospace numbers."""
    is_retro = theme_mode == "retro"
    status_colors = {"good": "#34d399", "warning": "#fbbf24", "bad": "#f87171", "": "#f0f0f2"}
    value_color = status_colors.get(status, "#f0f0f2")
    border_style = "border-color:rgba(45,212,191,0.15);" if is_retro else ""
    value_glow = f"text-shadow:0 0 12px {value_color}40;" if is_retro else ""
    delta_html = f'<div style="font-size:.7rem;color:#a1a1aa;margin-top:.25rem;">{delta}</div>' if delta else ""
    outer = f"background:#16161c;border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:1rem 1.25rem;{border_style}"
    label_s = "font-family:'Inter',sans-serif;font-size:.65rem;font-weight:500;text-transform:uppercase;letter-spacing:.08em;color:#71717a;margin-bottom:.4rem;"
    value_s = f"font-family:'JetBrains Mono',monospace;font-size:1.75rem;font-weight:600;color:{value_color};letter-spacing:-.02em;line-height:1.1;{value_glow}"
    return f'<div style="{outer}"><div style="{label_s}">{label}</div><div style="{value_s}">{value}</div>{delta_html}</div>'


def info_card(text: str, theme_mode: str = "minimal") -> str:
    """Generate HTML for an info card."""
    outer = "background:rgba(45,212,191,0.04);border:1px solid rgba(45,212,191,0.12);border-radius:12px;padding:1rem 1.25rem;display:flex;align-items:flex-start;gap:.75rem;"
    text_s = "font-family:'Inter',sans-serif;color:#a1a1aa;font-size:.85rem;line-height:1.5;"
    return f'<div style="{outer}"><span style="color:#2dd4bf;font-size:.9rem;flex-shrink:0;margin-top:1px;">i</span><span style="{text_s}">{text}</span></div>'


def success_card(text: str, theme_mode: str = "minimal") -> str:
    """Generate HTML for a success card."""
    outer = "background:rgba(52,211,153,0.04);border:1px solid rgba(52,211,153,0.15);border-radius:12px;padding:1rem 1.25rem;display:flex;align-items:center;gap:.75rem;"
    text_s = "font-family:'Inter',sans-serif;color:#a1a1aa;font-size:.85rem;"
    return f'<div style="{outer}"><span style="color:#34d399;font-size:.9rem;">&#10003;</span><span style="{text_s}">{text}</span></div>'


def warning_card(text: str, theme_mode: str = "minimal") -> str:
    """Generate HTML for a warning card."""
    outer = "background:rgba(251,191,36,0.04);border:1px solid rgba(251,191,36,0.15);border-radius:12px;padding:1rem 1.25rem;display:flex;align-items:center;gap:.75rem;"
    text_s = "font-family:'Inter',sans-serif;color:#a1a1aa;font-size:.85rem;"
    return f'<div style="{outer}"><span style="color:#fbbf24;font-size:.9rem;">&#9888;</span><span style="{text_s}">{text}</span></div>'


def empty_state(title: str, description: str, icon: str = "&#9671;", theme_mode: str = "minimal") -> str:
    """Generate HTML for an empty state."""
    is_retro = theme_mode == "retro"
    icon_glow = "text-shadow:0 0 20px rgba(45,212,191,0.3);" if is_retro else ""
    outer = "text-align:center;padding:4rem 2rem;background:#16161c;border:1px solid rgba(255,255,255,0.06);border-radius:16px;"
    icon_s = f"font-size:2.5rem;margin-bottom:1.25rem;color:#2dd4bf;opacity:.35;{icon_glow}"
    title_s = "font-family:'DM Sans',sans-serif;font-size:1rem;font-weight:600;color:#f0f0f2;margin-bottom:.4rem;"
    desc_s = "font-family:'Inter',sans-serif;font-size:.85rem;color:#71717a;max-width:320px;margin:0 auto;line-height:1.5;"
    return (
        f'<div style="{outer}">'
        f'<div style="{icon_s}">{icon}</div>'
        f'<div style="{title_s}">{title}</div>'
        f'<div style="{desc_s}">{description}</div>'
        f'</div>'
    )


def neon_badge(text: str, color: str = "cyan", theme_mode: str = "minimal") -> str:
    """Generate HTML for a badge/pill."""
    colors = {
        "cyan": ("#2dd4bf", "rgba(45, 212, 191, 0.08)", "rgba(45, 212, 191, 0.2)"),
        "magenta": ("#fb7185", "rgba(251, 113, 133, 0.08)", "rgba(251, 113, 133, 0.2)"),
        "amber": ("#fbbf24", "rgba(251, 191, 36, 0.08)", "rgba(251, 191, 36, 0.2)"),
        "green": ("#34d399", "rgba(52, 211, 153, 0.08)", "rgba(52, 211, 153, 0.2)"),
    }
    fg, bg, border = colors.get(color, colors["cyan"])
    style = (
        "font-family: 'Inter', sans-serif;"
        f"background: {bg};"
        f"color: {fg};"
        f"border: 1px solid {border};"
        "padding: 0.2rem 0.65rem;"
        "border-radius: 6px;"
        "font-size: 0.7rem;"
        "font-weight: 500;"
        "display: inline-block;"
        "letter-spacing: 0.01em;"
    )
    return f'<span style="{style}">{text}</span>'


def theme_toggle_html() -> str:
    """Generate HTML for the theme toggle display."""
    s = "font-family:'Inter',sans-serif;font-size:.65rem;font-weight:500;text-transform:uppercase;letter-spacing:.08em;color:#52525b;margin-bottom:.5rem;"
    return f'<p style="{s}">Theme</p>'


def sidebar_title(theme_mode: str = "minimal") -> str:
    """Generate HTML for sidebar title."""
    is_retro = theme_mode == "retro"
    accent_style = (
        "background:linear-gradient(135deg,#2dd4bf,#a78bfa);"
        "-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;"
    ) if is_retro else "color:#f0f0f2;"
    outer = "margin-bottom:1.25rem;padding-bottom:.75rem;border-bottom:1px solid rgba(255,255,255,0.06);"
    oura_s = f"font-family:'DM Sans',sans-serif;font-size:1.15rem;font-weight:700;letter-spacing:-.02em;{accent_style}"
    health_s = "font-family:'DM Sans',sans-serif;font-size:1.15rem;font-weight:400;color:#52525b;letter-spacing:-.02em;"
    return f'<div style="{outer}"><span style="{oura_s}">Oura</span><span style="{health_s}"> Health</span></div>'


def sidebar_label(text: str) -> str:
    """Generate HTML for a sidebar section label."""
    s = "font-family:'Inter',sans-serif;font-size:.65rem;font-weight:500;text-transform:uppercase;letter-spacing:.08em;color:#52525b;margin-bottom:.4rem;margin-top:0;"
    return f'<p style="{s}">{text}</p>'


def mode_indicator(is_sandbox: bool, theme_mode: str = "minimal") -> str:
    """Generate HTML for sandbox/demo mode indicator."""
    if not is_sandbox:
        return ""
    s = "background:rgba(251,191,36,0.06);border:1px solid rgba(251,191,36,0.15);border-radius:8px;padding:.4rem .65rem;margin-bottom:1.25rem;font-family:'Inter',sans-serif;font-size:.7rem;font-weight:500;color:#fbbf24;letter-spacing:.02em;"
    return f'<div style="{s}">Demo Mode</div>'


# Backwards compatibility aliases
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
