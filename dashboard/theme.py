"""Global theme and CSS for the Garmin Health Dashboard."""

# ── Page accent colors ──────────────────────────────────────────────
# Each page gets a primary accent for headers, borders, and highlights.

PAGE_ACCENTS = {
    "Overview": "#818CF8",     # Indigo
    "Sleep": "#A78BFA",        # Purple
    "Heart & HRV": "#F87171",  # Red
    "Stress & Energy": "#FBBF24",  # Amber
    "Activity": "#34D399",     # Green
}


def inject_global_css():
    """Inject global CSS to style the Streamlit app with a dark theme."""
    import streamlit as st

    st.markdown("""
    <style>
    /* ── Base dark theme ─────────────────────────────────────── */
    .stApp {
        background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%);
        color: #E2E8F0;
    }

    /* ── Sidebar ─────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F172A 0%, #162032 100%);
        border-right: 1px solid rgba(99, 102, 241, 0.15);
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown label {
        color: #CBD5E1;
    }

    /* ── Headers ─────────────────────────────────────────────── */
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #F1F5F9 !important;
        font-weight: 600 !important;
    }
    h1, .stMarkdown h1 {
        font-size: 1.75rem !important;
        letter-spacing: -0.02em;
    }

    /* ── Radio buttons (navigation) ──────────────────────────── */
    div[data-testid="stRadio"] label {
        color: #94A3B8 !important;
        transition: color 0.2s;
    }
    div[data-testid="stRadio"] label:hover {
        color: #E2E8F0 !important;
    }

    /* ── Metric cards ────────────────────────────────────────── */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1E293B, #293548);
        padding: 1em;
        border-radius: 12px;
        border: 1px solid rgba(148, 163, 184, 0.1);
    }
    div[data-testid="stMetric"] label {
        color: #94A3B8 !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #F1F5F9 !important;
    }

    /* ── Dividers ────────────────────────────────────────────── */
    hr {
        border-color: rgba(148, 163, 184, 0.1) !important;
        margin: 1.5rem 0 !important;
    }

    /* ── Expanders ───────────────────────────────────────────── */
    details[data-testid="stExpander"] {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-radius: 12px;
    }
    details[data-testid="stExpander"] summary span p {
        color: #E2E8F0 !important;
        font-weight: 600 !important;
    }

    /* ── Selectboxes and sliders ──────────────────────────── */
    .stSelectbox label, .stSlider label {
        color: #94A3B8 !important;
    }
    .stSelectbox > div > div {
        background: #1E293B !important;
        border-color: rgba(148, 163, 184, 0.2) !important;
        color: #E2E8F0 !important;
    }

    /* ── Dataframes ──────────────────────────────────────────── */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }

    /* ── Info/warning messages ────────────────────────────────── */
    .stAlert {
        background: rgba(30, 41, 59, 0.6) !important;
        border-radius: 8px;
        color: #CBD5E1 !important;
    }

    /* ── Button styling ──────────────────────────────────────── */
    .stButton > button {
        background: linear-gradient(135deg, #4F46E5, #6366F1) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: opacity 0.2s !important;
    }
    .stButton > button:hover {
        opacity: 0.9 !important;
    }

    /* ── Equal-height columns (for KPI cards) ──────────────── */
    div[data-testid="stHorizontalBlock"] {
        align-items: stretch;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
        display: flex;
        flex-direction: column;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] > div[data-testid="stMarkdownContainer"] {
        flex: 1;
        display: flex;
        flex-direction: column;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] > div[data-testid="stMarkdownContainer"] > div {
        flex: 1;
    }

    /* ── Hide Streamlit chrome ───────────────────────────────── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {
        background: rgba(15, 23, 42, 0.8) !important;
        backdrop-filter: blur(10px);
    }
    </style>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "", page: str = "Overview"):
    """Render a styled page header with accent color."""
    import streamlit as st

    accent = PAGE_ACCENTS.get(page, "#818CF8")
    st.markdown(f"""
    <div style="margin-bottom: 1.5rem">
        <div style="display:inline-block; width:4px; height:28px;
                    background:{accent}; border-radius:2px;
                    vertical-align:middle; margin-right:12px"></div>
        <span style="font-size:1.75rem; font-weight:700; color:#F1F5F9;
                     vertical-align:middle">{title}</span>
        {f'<p style="color:#64748B; font-size:0.9rem; margin:4px 0 0 16px">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


def section_header(title: str, page: str = "Overview"):
    """Render a styled section header."""
    import streamlit as st

    accent = PAGE_ACCENTS.get(page, "#818CF8")
    st.markdown(f"""
    <p style="font-size:1.1rem; font-weight:600; color:#CBD5E1;
              border-left: 3px solid {accent}; padding-left: 10px;
              margin: 1rem 0 0.75rem 0">{title}</p>
    """, unsafe_allow_html=True)


def _md_bold_to_html(text: str) -> str:
    """Convert Markdown **bold** to HTML <strong> tags."""
    import re
    return re.sub(r'\*\*(.+?)\*\*', r'<strong style="color:#F1F5F9">\1</strong>', text)


def insight_card(items: list[str], accent: str = "#818CF8"):
    """Render insights as a styled card."""
    import streamlit as st

    if not items:
        return

    bullets = "".join(
        f'<li style="margin-bottom:0.4em; color:#CBD5E1; line-height:1.5">{_md_bold_to_html(item)}</li>'
        for item in items
    )
    st.markdown(f"""
    <div style="background: rgba(30, 41, 59, 0.5);
                border: 1px solid rgba(148, 163, 184, 0.1);
                border-left: 3px solid {accent};
                border-radius: 0 12px 12px 0;
                padding: 1em 1.2em; margin-bottom: 0.75rem">
        <ul style="list-style: none; padding: 0; margin: 0">
            {bullets}
        </ul>
    </div>
    """, unsafe_allow_html=True)
