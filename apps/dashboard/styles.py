"""Custom CSS styles for the Oura Health Dashboard.

Professional, minimalistic styling with clean typography and generous whitespace.
"""

from __future__ import annotations


def get_custom_css() -> str:
    """Return custom CSS to inject into the dashboard."""
    return """
<style>
    /* Import clean, professional fonts */
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Root variables for consistent theming */
    :root {
        --bg-primary: #0F0F12;
        --bg-secondary: #18181B;
        --bg-card: #1C1C21;
        --bg-elevated: #242429;
        --text-primary: #FAFAFA;
        --text-secondary: #A1A1AA;
        --text-muted: #71717A;
        --accent: #8B5CF6;
        --accent-light: #A78BFA;
        --success: #22C55E;
        --warning: #F59E0B;
        --danger: #EF4444;
        --border: rgba(255, 255, 255, 0.06);
        --border-hover: rgba(255, 255, 255, 0.12);
        --shadow: 0 1px 3px rgba(0, 0, 0, 0.3), 0 1px 2px rgba(0, 0, 0, 0.2);
        --shadow-lg: 0 4px 6px rgba(0, 0, 0, 0.3), 0 2px 4px rgba(0, 0, 0, 0.2);
        --radius: 12px;
        --radius-sm: 8px;
    }
    
    /* Base app styling */
    .stApp {
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        background: var(--bg-primary);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {background: transparent;}
    
    /* Main content area */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'DM Sans', sans-serif;
        font-weight: 600;
        letter-spacing: -0.02em;
        color: var(--text-primary);
    }
    
    p, span, label {
        color: var(--text-secondary);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: var(--bg-secondary);
        border-right: 1px solid var(--border);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
    }
    
    /* Enhanced metric cards */
    [data-testid="stMetric"] {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.25rem 1.5rem;
        transition: all 0.2s ease;
    }
    
    [data-testid="stMetric"]:hover {
        border-color: var(--border-hover);
        background: var(--bg-elevated);
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        color: var(--text-muted) !important;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.02em !important;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.8rem !important;
        font-weight: 500 !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm);
        color: var(--text-primary);
        font-weight: 500;
        padding: 0.5rem 1rem;
        transition: all 0.15s ease;
    }
    
    .stButton > button:hover {
        background: var(--bg-elevated);
        border-color: var(--border-hover);
        transform: translateY(-1px);
    }
    
    .stButton > button[kind="primary"] {
        background: var(--accent);
        border-color: var(--accent);
        color: white;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: var(--accent-light);
        border-color: var(--accent-light);
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm);
        color: var(--text-primary);
        font-weight: 500;
    }
    
    .stDownloadButton > button:hover {
        background: var(--bg-elevated);
        border-color: var(--accent);
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm);
        font-weight: 500;
        color: var(--text-primary);
    }
    
    .streamlit-expanderHeader:hover {
        border-color: var(--border-hover);
    }
    
    .streamlit-expanderContent {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-top: none;
        border-radius: 0 0 var(--radius-sm) var(--radius-sm);
    }
    
    /* Data frames / tables */
    [data-testid="stDataFrame"] {
        border-radius: var(--radius);
        overflow: hidden;
    }
    
    [data-testid="stDataFrame"] > div {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm);
    }
    
    .stSelectbox > div > div:hover {
        border-color: var(--border-hover);
    }
    
    /* Multiselect */
    .stMultiSelect > div > div {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm);
    }
    
    /* Sliders */
    .stSlider > div > div > div {
        background: var(--accent);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: var(--bg-card);
        border-radius: var(--radius-sm);
        padding: 4px;
        border: 1px solid var(--border);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: var(--radius-sm);
        padding: 0.5rem 1rem;
        font-weight: 500;
        color: var(--text-secondary);
        background: transparent;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--bg-elevated);
        color: var(--text-primary);
    }
    
    /* Chat styling */
    .stChatMessage {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1rem;
    }
    
    [data-testid="stChatInput"] > div {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] > div {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
    }
    
    [data-testid="stFileUploader"]:hover > div {
        border-color: var(--accent);
    }
    
    /* Text inputs */
    .stTextInput > div > div {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm);
    }
    
    .stTextInput > div > div:focus-within {
        border-color: var(--accent);
    }
    
    /* Date inputs */
    .stDateInput > div > div {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm);
    }
    
    /* Progress and spinners */
    .stSpinner > div {
        border-color: var(--accent) transparent transparent transparent;
    }
    
    .stProgress > div > div {
        background: var(--accent);
    }
    
    /* Info/Warning/Error/Success boxes */
    .stAlert {
        border-radius: var(--radius-sm);
        border: none;
    }
    
    /* Dividers */
    hr {
        border: none;
        height: 1px;
        background: var(--border);
        margin: 1.5rem 0;
    }
    
    /* Code blocks */
    code {
        font-family: 'JetBrains Mono', monospace;
        background: var(--bg-elevated);
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-size: 0.85em;
    }
    
    /* Captions */
    .stCaption {
        color: var(--text-muted);
        font-size: 0.8rem;
    }
    
    /* Toggle */
    .stToggle > label > div {
        background: var(--bg-elevated);
    }
    
    /* Radio buttons */
    .stRadio > div {
        gap: 0.5rem;
    }
    
    .stRadio > div > label {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm);
        padding: 0.5rem 1rem;
        transition: all 0.15s ease;
    }
    
    .stRadio > div > label:hover {
        border-color: var(--border-hover);
    }
    
    .stRadio > div > label[data-checked="true"] {
        border-color: var(--accent);
        background: rgba(139, 92, 246, 0.1);
    }
    
    /* Plotly chart containers */
    .js-plotly-plot {
        border-radius: var(--radius);
    }
</style>
"""


def page_header(title: str, subtitle: str = "") -> str:
    """Generate HTML for a clean page header."""
    subtitle_html = f'<p class="page-subtitle">{subtitle}</p>' if subtitle else ""
    return f"""
    <style>
        .page-header {{
            margin-bottom: 2rem;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        }}
        .page-title {{
            font-size: 1.75rem;
            font-weight: 600;
            color: #FAFAFA;
            margin: 0 0 0.25rem 0;
            letter-spacing: -0.02em;
        }}
        .page-subtitle {{
            font-size: 0.95rem;
            color: #71717A;
            margin: 0;
            font-weight: 400;
        }}
    </style>
    <div class="page-header">
        <h1 class="page-title">{title}</h1>
        {subtitle_html}
    </div>
    """


def section_header(title: str) -> str:
    """Generate HTML for a clean section header."""
    return f"""
    <style>
        .section-header {{
            font-size: 1rem;
            font-weight: 600;
            color: #FAFAFA;
            margin: 2rem 0 1rem 0;
            padding-bottom: 0.5rem;
            letter-spacing: -0.01em;
        }}
    </style>
    <h3 class="section-header">{title}</h3>
    """


def stat_card(label: str, value: str, delta: str = "", status: str = "") -> str:
    """Generate HTML for a stat card. Status can be 'good', 'warning', 'bad'."""
    status_colors = {
        "good": "#22C55E",
        "warning": "#F59E0B", 
        "bad": "#EF4444",
        "": "#FAFAFA"
    }
    color = status_colors.get(status, "#FAFAFA")
    delta_html = f'<div class="stat-delta">{delta}</div>' if delta else ""
    
    return f"""
    <style>
        .stat-card {{
            background: #1C1C21;
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            text-align: left;
        }}
        .stat-label {{
            font-size: 0.7rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #71717A;
            margin-bottom: 0.5rem;
        }}
        .stat-value {{
            font-size: 1.75rem;
            font-weight: 600;
            color: {color};
            letter-spacing: -0.02em;
            line-height: 1.2;
        }}
        .stat-delta {{
            font-size: 0.8rem;
            color: #A1A1AA;
            margin-top: 0.25rem;
        }}
    </style>
    <div class="stat-card">
        <div class="stat-label">{label}</div>
        <div class="stat-value">{value}</div>
        {delta_html}
    </div>
    """


def info_card(text: str, icon: str = "ℹ️") -> str:
    """Generate HTML for an info card."""
    return f"""
    <style>
        .info-card {{
            background: rgba(139, 92, 246, 0.08);
            border: 1px solid rgba(139, 92, 246, 0.2);
            border-radius: 12px;
            padding: 1rem 1.25rem;
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
        }}
        .info-icon {{
            font-size: 1rem;
            flex-shrink: 0;
        }}
        .info-text {{
            color: #A1A1AA;
            font-size: 0.9rem;
            line-height: 1.5;
        }}
    </style>
    <div class="info-card">
        <span class="info-icon">{icon}</span>
        <span class="info-text">{text}</span>
    </div>
    """


def success_card(text: str) -> str:
    """Generate HTML for a success message."""
    return f"""
    <style>
        .success-card {{
            background: rgba(34, 197, 94, 0.08);
            border: 1px solid rgba(34, 197, 94, 0.2);
            border-radius: 12px;
            padding: 1rem 1.25rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}
        .success-icon {{
            color: #22C55E;
            font-size: 1rem;
        }}
        .success-text {{
            color: #A1A1AA;
            font-size: 0.9rem;
        }}
    </style>
    <div class="success-card">
        <span class="success-icon">✓</span>
        <span class="success-text">{text}</span>
    </div>
    """


def warning_card(text: str) -> str:
    """Generate HTML for a warning message."""
    return f"""
    <style>
        .warning-card {{
            background: rgba(245, 158, 11, 0.08);
            border: 1px solid rgba(245, 158, 11, 0.2);
            border-radius: 12px;
            padding: 1rem 1.25rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}
        .warning-icon {{
            color: #F59E0B;
            font-size: 1rem;
        }}
        .warning-text {{
            color: #A1A1AA;
            font-size: 0.9rem;
        }}
    </style>
    <div class="warning-card">
        <span class="warning-icon">⚠</span>
        <span class="warning-text">{text}</span>
    </div>
    """


def empty_state(title: str, description: str, icon: str = "📊") -> str:
    """Generate HTML for an empty state."""
    return f"""
    <style>
        .empty-state {{
            text-align: center;
            padding: 3rem 2rem;
            background: #1C1C21;
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 12px;
        }}
        .empty-icon {{
            font-size: 2.5rem;
            margin-bottom: 1rem;
            opacity: 0.5;
        }}
        .empty-title {{
            font-size: 1rem;
            font-weight: 500;
            color: #FAFAFA;
            margin-bottom: 0.5rem;
        }}
        .empty-description {{
            font-size: 0.875rem;
            color: #71717A;
            max-width: 300px;
            margin: 0 auto;
        }}
    </style>
    <div class="empty-state">
        <div class="empty-icon">{icon}</div>
        <div class="empty-title">{title}</div>
        <div class="empty-description">{description}</div>
    </div>
    """


def feature_badge(text: str, color: str = "purple") -> str:
    """Generate HTML for a small feature badge."""
    colors = {
        "purple": ("rgba(139, 92, 246, 0.15)", "#A78BFA"),
        "green": ("rgba(34, 197, 94, 0.15)", "#4ADE80"),
        "blue": ("rgba(59, 130, 246, 0.15)", "#60A5FA"),
        "orange": ("rgba(245, 158, 11, 0.15)", "#FBBF24"),
    }
    bg, fg = colors.get(color, colors["purple"])
    return f"""
    <span style="
        background: {bg};
        color: {fg};
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
        display: inline-block;
    ">{text}</span>
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
