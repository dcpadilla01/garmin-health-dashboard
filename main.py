"""Garmin Health Dashboard — Streamlit entry point."""

import streamlit as st

st.set_page_config(
    page_title="Garmin Health Dashboard",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
)

from dashboard.theme import inject_global_css
from data.fetch import fetch_all
from data.process import process_all
from dashboard.overview import render_overview
from dashboard.sleep import render_sleep
from dashboard.heart import render_heart
from dashboard.stress import render_stress
from dashboard.activity import render_activity

# Apply dark theme
inject_global_css()

NAV_ITEMS = {
    "Overview":        "📊",
    "Sleep":           "🌙",
    "Heart & HRV":     "❤️",
    "Stress & Energy": "⚡",
    "Activity":        "🏃",
}


@st.cache_data(ttl=3600, show_spinner="Fetching data from Garmin...")
def load_data(days: int) -> dict:
    """Fetch and process all Garmin data (cached for 1 hour)."""
    raw = fetch_all(days=days)
    return process_all(raw)


def main():
    # ── Sidebar ──────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding: 1rem 0 0.5rem 0">
            <p style="font-size:1.5rem; font-weight:700; color:#F1F5F9;
                      margin:0; letter-spacing:-0.02em">Garmin Health</p>
            <p style="font-size:0.8rem; color:#64748B; margin:4px 0 0 0">
                Personal health dashboard</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)
        days = st.slider("Days of history", min_value=7, max_value=90, value=30, step=1)

        if st.button("Refresh Data", use_container_width=True):
            st.cache_data.clear()

        st.markdown("<div style='height: 0.75rem'></div>", unsafe_allow_html=True)

        # Navigation with icons
        page_labels = [f"{icon}  {name}" for name, icon in NAV_ITEMS.items()]
        selected_label = st.radio(
            "Navigate",
            page_labels,
            index=0,
            label_visibility="collapsed",
        )
        # Strip icon to get page name
        page = selected_label.split("  ", 1)[1]

        # Footer
        st.markdown("""
        <div style="position:fixed; bottom:1rem; padding:0 1rem;
                    color:#475569; font-size:0.7rem">
            Timezone: America/Mexico City
        </div>
        """, unsafe_allow_html=True)

    # ── Load Data ────────────────────────────────────────────────
    processed = load_data(days)

    # ── Pages ────────────────────────────────────────────────────
    if page == "Overview":
        render_overview(processed)
    elif page == "Sleep":
        render_sleep(processed)
    elif page == "Heart & HRV":
        render_heart(processed)
    elif page == "Stress & Energy":
        render_stress(processed)
    elif page == "Activity":
        render_activity(processed)


if __name__ == "__main__":
    main()