"""Retro-Minimal Dashboard Styles.

Fusion of minimalist typography, data-dense layouts, and 80s synthwave aesthetics.
Supports two theme modes: 'minimal' (subtle) and 'retro' (moderate neon effects).
"""

from __future__ import annotations


def get_custom_css(theme_mode: str = "minimal") -> str:
    """Return custom CSS for the dashboard.
    
    Args:
        theme_mode: Either 'minimal' (default, subtle) or 'retro' (neon effects)
    """
    is_retro = theme_mode == "retro"
    
    glow_intensity = "0.6" if is_retro else "0"
    grid_opacity = "0.04" if is_retro else "0"
    border_glow = "0 0 12px rgba(0, 212, 255, 0.3)" if is_retro else "none"
    text_glow = "0 0 20px rgba(0, 212, 255, 0.5)" if is_retro else "none"
    
    return f"""
<style>
    /* === FONTS === */
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&family=Playfair+Display:wght@500;600&display=swap');
    
    /* === CSS CUSTOM PROPERTIES === */
    :root {{
        /* Background layers */
        --bg-void: #0a0a0f;
        --bg-primary: #0d0d14;
        --bg-surface: #12121a;
        --bg-elevated: #1a1a24;
        --bg-hover: #22222e;
        
        /* Text hierarchy */
        --text-primary: #e8e8e8;
        --text-secondary: #9ca3af;
        --text-muted: #6b7280;
        --text-dim: #4b5563;
        
        /* Neon accent palette */
        --accent-cyan: #00d4ff;
        --accent-magenta: #ff2d95;
        --accent-amber: #ffb800;
        --accent-cyan-dim: rgba(0, 212, 255, 0.15);
        --accent-magenta-dim: rgba(255, 45, 149, 0.15);
        --accent-amber-dim: rgba(255, 184, 0, 0.15);
        
        /* Status colors */
        --status-good: #00d4a0;
        --status-warning: #ffb800;
        --status-danger: #ff4757;
        
        /* Borders and effects */
        --border-subtle: rgba(255, 255, 255, 0.04);
        --border-default: rgba(0, 212, 255, 0.08);
        --border-hover: rgba(0, 212, 255, 0.2);
        --border-active: rgba(0, 212, 255, 0.4);
        
        /* Theme-dependent */
        --glow-intensity: {glow_intensity};
        --grid-opacity: {grid_opacity};
        --border-glow: {border_glow};
        --text-glow: {text_glow};
        
        /* Spacing */
        --radius-sm: 6px;
        --radius-md: 10px;
        --radius-lg: 14px;
        
        /* Typography */
        --font-display: 'Space Grotesk', -apple-system, sans-serif;
        --font-body: 'IBM Plex Sans', -apple-system, sans-serif;
        --font-mono: 'JetBrains Mono', 'SF Mono', monospace;
        --font-serif: 'Playfair Display', Georgia, serif;
    }}
    
    /* === BASE STYLES === */
    .stApp {{
        font-family: var(--font-body);
        background: var(--bg-void);
        color: var(--text-secondary);
    }}
    
    /* Perspective grid background (retro mode) */
    .stApp::before {{
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            linear-gradient(to bottom, transparent 0%, var(--bg-void) 100%),
            repeating-linear-gradient(
                90deg,
                rgba(0, 212, 255, var(--grid-opacity)) 0px,
                transparent 1px,
                transparent 60px
            ),
            repeating-linear-gradient(
                0deg,
                rgba(0, 212, 255, var(--grid-opacity)) 0px,
                transparent 1px,
                transparent 60px
            );
        pointer-events: none;
        z-index: 0;
    }}
    
    /* Hide Streamlit chrome */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header[data-testid="stHeader"] {{background: transparent;}}
    
    /* Main content */
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1280px;
        position: relative;
        z-index: 1;
    }}
    
    /* === TYPOGRAPHY === */
    h1, h2, h3, h4, h5, h6 {{
        font-family: var(--font-display);
        font-weight: 600;
        letter-spacing: -0.02em;
        color: var(--text-primary);
    }}
    
    h1 {{
        font-size: 1.875rem;
        text-shadow: var(--text-glow);
    }}
    
    h2 {{ font-size: 1.5rem; }}
    h3 {{ font-size: 1.125rem; }}
    
    p, span, label, div {{
        font-family: var(--font-body);
    }}
    
    /* Smooth scrolling */
    html {{
        scroll-behavior: smooth;
    }}
    
    /* === SIDEBAR === */
    [data-testid="stSidebar"] {{
        background: var(--bg-primary);
        border-right: 1px solid var(--border-subtle);
    }}
    
    [data-testid="stSidebar"] > div:first-child {{
        padding-top: 1rem;
    }}
    
    /* === METRIC CARDS === */
    [data-testid="stMetric"] {{
        background: var(--bg-surface);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-md);
        padding: 1.25rem;
        transition: all 0.2s ease;
        box-shadow: var(--border-glow);
    }}
    
    [data-testid="stMetric"]:hover {{
        border-color: var(--border-hover);
        transform: translateY(-2px);
        box-shadow: 0 0 20px rgba(0, 212, 255, calc(var(--glow-intensity) * 0.4));
    }}
    
    [data-testid="stMetricLabel"] {{
        font-family: var(--font-body) !important;
        font-size: 0.7rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        color: var(--text-muted) !important;
    }}
    
    [data-testid="stMetricValue"] {{
        font-family: var(--font-mono) !important;
        font-size: 2rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.02em !important;
        text-shadow: var(--text-glow);
    }}
    
    [data-testid="stMetricDelta"] {{
        font-family: var(--font-mono) !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
    }}
    
    /* Positive/negative delta colors */
    [data-testid="stMetricDelta"] svg {{
        display: none;
    }}
    
    /* === BUTTONS === */
    .stButton > button {{
        font-family: var(--font-body);
        background: transparent;
        border: 1px solid var(--border-default);
        border-radius: var(--radius-sm);
        color: var(--text-primary);
        font-weight: 500;
        font-size: 0.875rem;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease;
    }}
    
    .stButton > button:hover {{
        background: var(--bg-elevated);
        border-color: var(--accent-cyan);
        box-shadow: 0 0 15px rgba(0, 212, 255, calc(var(--glow-intensity) * 0.3));
        transform: translateY(-1px);
    }}
    
    .stButton > button:active {{
        transform: translateY(0);
    }}
    
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"] {{
        background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-magenta) 100%);
        border: none;
        color: var(--bg-void);
        font-weight: 600;
    }}
    
    .stButton > button[kind="primary"]:hover {{
        box-shadow: 0 0 25px rgba(0, 212, 255, 0.5), 0 0 25px rgba(255, 45, 149, 0.3);
    }}
    
    /* Download button */
    .stDownloadButton > button {{
        font-family: var(--font-body);
        background: var(--bg-surface);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-sm);
        color: var(--text-primary);
        font-weight: 500;
    }}
    
    .stDownloadButton > button:hover {{
        border-color: var(--accent-cyan);
        box-shadow: var(--border-glow);
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
        border-color: var(--accent-cyan);
        box-shadow: 0 0 10px rgba(0, 212, 255, calc(var(--glow-intensity) * 0.2));
    }}
    
    /* === EXPANDERS === */
    .streamlit-expanderHeader {{
        font-family: var(--font-body);
        background: var(--bg-surface);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-sm);
        font-weight: 500;
        color: var(--text-primary);
    }}
    
    .streamlit-expanderHeader:hover {{
        border-color: var(--border-hover);
    }}
    
    .streamlit-expanderContent {{
        background: var(--bg-surface);
        border: 1px solid var(--border-default);
        border-top: none;
        border-radius: 0 0 var(--radius-sm) var(--radius-sm);
    }}
    
    /* === TABS === */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0;
        background: var(--bg-surface);
        border-radius: var(--radius-sm);
        padding: 4px;
        border: 1px solid var(--border-default);
    }}
    
    .stTabs [data-baseweb="tab"] {{
        font-family: var(--font-body);
        border-radius: var(--radius-sm);
        padding: 0.5rem 1rem;
        font-weight: 500;
        font-size: 0.875rem;
        color: var(--text-muted);
        background: transparent;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: var(--bg-elevated);
        color: var(--accent-cyan);
        box-shadow: var(--border-glow);
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
        border-color: var(--accent-cyan);
        box-shadow: 0 0 15px rgba(0, 212, 255, calc(var(--glow-intensity) * 0.2));
    }}
    
    /* === FILE UPLOADER === */
    [data-testid="stFileUploader"] > div {{
        background: var(--bg-surface);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-md);
    }}
    
    [data-testid="stFileUploader"]:hover > div {{
        border-color: var(--accent-cyan);
    }}
    
    /* === SLIDERS === */
    .stSlider > div > div > div {{
        background: linear-gradient(90deg, var(--accent-cyan), var(--accent-magenta));
    }}
    
    /* === TOGGLE === */
    .stToggle > label > div {{
        background: var(--bg-elevated);
    }}
    
    /* === PROGRESS === */
    .stProgress > div > div {{
        background: linear-gradient(90deg, var(--accent-cyan), var(--accent-magenta));
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
        color: var(--accent-cyan);
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
    
    /* === ANIMATIONS === */
    @keyframes pulse-glow {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.7; }}
    }}
    
    @keyframes scan-line {{
        0% {{ transform: translateY(-100%); }}
        100% {{ transform: translateY(100vh); }}
    }}
    
    /* Reduced motion support */
    @media (prefers-reduced-motion: reduce) {{
        *, *::before, *::after {{
            animation-duration: 0.01ms !important;
            transition-duration: 0.01ms !important;
        }}
    }}
</style>
"""


def page_header(title: str, subtitle: str = "", theme_mode: str = "minimal") -> str:
    """Generate HTML for a page header with retro-minimal styling."""
    is_retro = theme_mode == "retro"
    title_glow = "text-shadow: 0 0 30px rgba(0, 212, 255, 0.5);" if is_retro else ""
    
    subtitle_html = f'<p class="rm-page-subtitle">{subtitle}</p>' if subtitle else ""
    return f"""
    <style>
        .rm-page-header {{
            margin-bottom: 2rem;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid rgba(0, 212, 255, 0.1);
        }}
        .rm-page-title {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 2rem;
            font-weight: 600;
            color: #e8e8e8;
            margin: 0 0 0.5rem 0;
            letter-spacing: -0.02em;
            {title_glow}
        }}
        .rm-page-subtitle {{
            font-family: 'IBM Plex Sans', sans-serif;
            font-size: 0.95rem;
            color: #6b7280;
            margin: 0;
            font-weight: 400;
            letter-spacing: 0.01em;
        }}
    </style>
    <div class="rm-page-header">
        <h1 class="rm-page-title">{title}</h1>
        {subtitle_html}
    </div>
    """


def section_header(title: str, theme_mode: str = "minimal") -> str:
    """Generate HTML for a section header."""
    is_retro = theme_mode == "retro"
    accent_line = "background: linear-gradient(90deg, #00d4ff, transparent);" if is_retro else "background: rgba(255, 255, 255, 0.1);"
    
    return f"""
    <style>
        .rm-section-header {{
            font-family: 'IBM Plex Sans', sans-serif;
            font-size: 0.75rem;
            font-weight: 600;
            color: #9ca3af;
            margin: 2.5rem 0 1rem 0;
            padding-bottom: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            border-bottom: 1px solid rgba(0, 212, 255, 0.1);
            position: relative;
        }}
        .rm-section-header::after {{
            content: '';
            position: absolute;
            bottom: -1px;
            left: 0;
            width: 60px;
            height: 2px;
            {accent_line}
        }}
    </style>
    <h3 class="rm-section-header">{title}</h3>
    """


def metric_card(label: str, value: str, delta: str = "", status: str = "", theme_mode: str = "minimal") -> str:
    """Generate HTML for a metric card with monospace numbers."""
    is_retro = theme_mode == "retro"
    
    status_colors = {
        "good": "#00d4a0",
        "warning": "#ffb800",
        "bad": "#ff4757",
        "": "#e8e8e8"
    }
    value_color = status_colors.get(status, "#e8e8e8")
    
    border_style = "border-color: rgba(0, 212, 255, 0.2); box-shadow: 0 0 15px rgba(0, 212, 255, 0.15);" if is_retro else ""
    value_glow = f"text-shadow: 0 0 20px {value_color};" if is_retro else ""
    
    delta_html = f'<div class="rm-metric-delta">{delta}</div>' if delta else ""
    
    return f"""
    <style>
        .rm-metric-card {{
            background: #12121a;
            border: 1px solid rgba(0, 212, 255, 0.08);
            border-radius: 10px;
            padding: 1.25rem;
            transition: all 0.2s ease;
            {border_style}
        }}
        .rm-metric-card:hover {{
            border-color: rgba(0, 212, 255, 0.25);
            transform: translateY(-2px);
        }}
        .rm-metric-label {{
            font-family: 'IBM Plex Sans', sans-serif;
            font-size: 0.7rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #6b7280;
            margin-bottom: 0.5rem;
        }}
        .rm-metric-value {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 2rem;
            font-weight: 600;
            color: {value_color};
            letter-spacing: -0.02em;
            line-height: 1.1;
            {value_glow}
        }}
        .rm-metric-delta {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            color: #9ca3af;
            margin-top: 0.5rem;
        }}
    </style>
    <div class="rm-metric-card">
        <div class="rm-metric-label">{label}</div>
        <div class="rm-metric-value">{value}</div>
        {delta_html}
    </div>
    """


def info_card(text: str, theme_mode: str = "minimal") -> str:
    """Generate HTML for an info card."""
    is_retro = theme_mode == "retro"
    border_style = "border-color: rgba(0, 212, 255, 0.3);" if is_retro else ""
    
    return f"""
    <style>
        .rm-info-card {{
            background: rgba(0, 212, 255, 0.05);
            border: 1px solid rgba(0, 212, 255, 0.15);
            border-radius: 10px;
            padding: 1rem 1.25rem;
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
            {border_style}
        }}
        .rm-info-icon {{
            color: #00d4ff;
            font-size: 1rem;
            flex-shrink: 0;
        }}
        .rm-info-text {{
            font-family: 'IBM Plex Sans', sans-serif;
            color: #9ca3af;
            font-size: 0.875rem;
            line-height: 1.5;
        }}
    </style>
    <div class="rm-info-card">
        <span class="rm-info-icon">ℹ</span>
        <span class="rm-info-text">{text}</span>
    </div>
    """


def success_card(text: str, theme_mode: str = "minimal") -> str:
    """Generate HTML for a success card."""
    is_retro = theme_mode == "retro"
    glow = "box-shadow: 0 0 15px rgba(0, 212, 160, 0.2);" if is_retro else ""
    
    return f"""
    <style>
        .rm-success-card {{
            background: rgba(0, 212, 160, 0.05);
            border: 1px solid rgba(0, 212, 160, 0.2);
            border-radius: 10px;
            padding: 1rem 1.25rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            {glow}
        }}
        .rm-success-icon {{
            color: #00d4a0;
            font-size: 1rem;
        }}
        .rm-success-text {{
            font-family: 'IBM Plex Sans', sans-serif;
            color: #9ca3af;
            font-size: 0.875rem;
        }}
    </style>
    <div class="rm-success-card">
        <span class="rm-success-icon">✓</span>
        <span class="rm-success-text">{text}</span>
    </div>
    """


def warning_card(text: str, theme_mode: str = "minimal") -> str:
    """Generate HTML for a warning card."""
    is_retro = theme_mode == "retro"
    glow = "box-shadow: 0 0 15px rgba(255, 184, 0, 0.2);" if is_retro else ""
    
    return f"""
    <style>
        .rm-warning-card {{
            background: rgba(255, 184, 0, 0.05);
            border: 1px solid rgba(255, 184, 0, 0.2);
            border-radius: 10px;
            padding: 1rem 1.25rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            {glow}
        }}
        .rm-warning-icon {{
            color: #ffb800;
            font-size: 1rem;
        }}
        .rm-warning-text {{
            font-family: 'IBM Plex Sans', sans-serif;
            color: #9ca3af;
            font-size: 0.875rem;
        }}
    </style>
    <div class="rm-warning-card">
        <span class="rm-warning-icon">⚠</span>
        <span class="rm-warning-text">{text}</span>
    </div>
    """


def empty_state(title: str, description: str, icon: str = "◇", theme_mode: str = "minimal") -> str:
    """Generate HTML for an empty state."""
    is_retro = theme_mode == "retro"
    icon_glow = "text-shadow: 0 0 30px rgba(0, 212, 255, 0.5);" if is_retro else ""
    
    return f"""
    <style>
        .rm-empty-state {{
            text-align: center;
            padding: 4rem 2rem;
            background: #12121a;
            border: 1px solid rgba(0, 212, 255, 0.08);
            border-radius: 14px;
        }}
        .rm-empty-icon {{
            font-size: 3rem;
            margin-bottom: 1.5rem;
            color: #00d4ff;
            opacity: 0.5;
            {icon_glow}
        }}
        .rm-empty-title {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.125rem;
            font-weight: 500;
            color: #e8e8e8;
            margin-bottom: 0.5rem;
        }}
        .rm-empty-description {{
            font-family: 'IBM Plex Sans', sans-serif;
            font-size: 0.875rem;
            color: #6b7280;
            max-width: 320px;
            margin: 0 auto;
            line-height: 1.5;
        }}
    </style>
    <div class="rm-empty-state">
        <div class="rm-empty-icon">{icon}</div>
        <div class="rm-empty-title">{title}</div>
        <div class="rm-empty-description">{description}</div>
    </div>
    """


def neon_badge(text: str, color: str = "cyan", theme_mode: str = "minimal") -> str:
    """Generate HTML for a neon badge/pill."""
    colors = {
        "cyan": ("#00d4ff", "rgba(0, 212, 255, 0.1)", "rgba(0, 212, 255, 0.3)"),
        "magenta": ("#ff2d95", "rgba(255, 45, 149, 0.1)", "rgba(255, 45, 149, 0.3)"),
        "amber": ("#ffb800", "rgba(255, 184, 0, 0.1)", "rgba(255, 184, 0, 0.3)"),
        "green": ("#00d4a0", "rgba(0, 212, 160, 0.1)", "rgba(0, 212, 160, 0.3)"),
    }
    fg, bg, border = colors.get(color, colors["cyan"])
    is_retro = theme_mode == "retro"
    glow = f"box-shadow: 0 0 10px {border};" if is_retro else ""
    
    return f"""
    <span style="
        font-family: 'IBM Plex Sans', sans-serif;
        background: {bg};
        color: {fg};
        border: 1px solid {border};
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
        display: inline-block;
        {glow}
    ">{text}</span>
    """


def theme_toggle_html() -> str:
    """Generate HTML for the theme toggle display."""
    return """
    <style>
        .rm-theme-label {{
            font-family: 'IBM Plex Sans', sans-serif;
            font-size: 0.7rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #6b7280;
            margin-bottom: 0.5rem;
        }}
    </style>
    <p class="rm-theme-label">Theme</p>
    """


def sidebar_title(theme_mode: str = "minimal") -> str:
    """Generate HTML for sidebar title."""
    is_retro = theme_mode == "retro"
    oura_style = "background: linear-gradient(135deg, #00d4ff, #ff2d95); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;" if is_retro else "color: #e8e8e8;"
    
    return f"""
    <div style="margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid rgba(0, 212, 255, 0.1);">
        <span style="
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.25rem;
            font-weight: 600;
            letter-spacing: -0.02em;
            {oura_style}
        ">Oura</span>
        <span style="
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.25rem;
            font-weight: 400;
            color: #4b5563;
            letter-spacing: -0.02em;
        "> Dashboard</span>
    </div>
    """


def sidebar_label(text: str) -> str:
    """Generate HTML for a sidebar section label."""
    return f"""
    <p style="
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 0.7rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #4b5563;
        margin-bottom: 0.5rem;
        margin-top: 0;
    ">{text}</p>
    """


def mode_indicator(is_sandbox: bool, theme_mode: str = "minimal") -> str:
    """Generate HTML for sandbox/demo mode indicator."""
    if not is_sandbox:
        return ""
    
    is_retro = theme_mode == "retro"
    glow = "box-shadow: 0 0 15px rgba(255, 184, 0, 0.2);" if is_retro else ""
    
    return f"""
    <div style="
        background: rgba(255, 184, 0, 0.08);
        border: 1px solid rgba(255, 184, 0, 0.2);
        border-radius: 8px;
        padding: 0.5rem 0.75rem;
        margin-bottom: 1.5rem;
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 0.75rem;
        color: #ffb800;
        {glow}
    ">
        Demo mode
    </div>
    """


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
