"""Overview page components."""

import streamlit as st
import pandas as pd

from dashboard.charts import kpi_card_html, line_chart, COLORS
from dashboard.theme import page_header, section_header, insight_card, PAGE_ACCENTS
from analysis.health import generate_all_insights


def render_overview(processed: dict):
    """Render the overview page."""
    page_header("Health Overview", "Your key metrics at a glance", "Overview")

    _render_kpis(processed)
    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)
    _render_sparklines(processed)
    st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)
    _render_insights(processed)


def _render_kpis(processed: dict):
    """Render KPI cards row."""
    cols = st.columns(5, gap="medium")

    # RHR
    rhr_df = processed["rhr"]
    if not rhr_df.empty:
        current_rhr = rhr_df.iloc[-1]["rhr"]
        delta = ""
        delta_good = True
        if len(rhr_df) >= 7:
            week_ago = rhr_df.iloc[-7]["rhr"]
            diff = current_rhr - week_ago
            delta = f"{diff:+.0f} vs 7d ago"
            delta_good = diff <= 0
        cols[0].markdown(
            kpi_card_html("Resting HR", f"{current_rhr:.0f}", delta, delta_good, "#F87171"),
            unsafe_allow_html=True,
        )
    else:
        cols[0].markdown(kpi_card_html("Resting HR", "—", accent="#F87171"), unsafe_allow_html=True)

    # HRV Status
    hrv_df = processed["hrv_summaries"]
    if not hrv_df.empty:
        latest_hrv = hrv_df.iloc[-1]
        status = latest_hrv.get("status", "—")
        avg = latest_hrv.get("weekly_avg", "")
        cols[1].markdown(
            kpi_card_html("HRV Status", status, f"Weekly avg: {avg}" if avg else "", accent="#34D399"),
            unsafe_allow_html=True,
        )
    else:
        cols[1].markdown(kpi_card_html("HRV Status", "—", accent="#34D399"), unsafe_allow_html=True)

    # Sleep Score
    sleep_df = processed["sleep_summaries"]
    if not sleep_df.empty:
        latest_sleep = sleep_df.iloc[-1]
        score = latest_sleep.get("overall_score", "—")
        qualifier = latest_sleep.get("overall_qualifier", "")
        cols[2].markdown(
            kpi_card_html("Sleep Score", str(score), qualifier, accent="#A78BFA"),
            unsafe_allow_html=True,
        )
    else:
        cols[2].markdown(kpi_card_html("Sleep Score", "—", accent="#A78BFA"), unsafe_allow_html=True)

    # Body Battery
    bb_df = processed["body_battery"]
    if not bb_df.empty:
        latest_bb = bb_df.iloc[-1]["body_battery"]
        cols[3].markdown(
            kpi_card_html("Body Battery", str(int(latest_bb)), accent="#FBBF24"),
            unsafe_allow_html=True,
        )
    else:
        cols[3].markdown(kpi_card_html("Body Battery", "—", accent="#FBBF24"), unsafe_allow_html=True)

    # Today's Steps
    steps_df = processed["daily_steps"]
    if not steps_df.empty:
        latest = steps_df.iloc[-1]
        total = latest.get("total_steps", 0)
        goal = latest.get("step_goal", 0)
        pct = (total / goal * 100) if goal > 0 else 0
        cols[4].markdown(
            kpi_card_html("Steps", f"{total:,}", f"{pct:.0f}% of goal",
                          delta_good=pct >= 80, accent="#60A5FA"),
            unsafe_allow_html=True,
        )
    else:
        cols[4].markdown(kpi_card_html("Steps", "—", accent="#60A5FA"), unsafe_allow_html=True)


def _render_sparklines(processed: dict):
    """Render 30-day sparkline trends."""
    section_header("30-Day Trends", "Overview")
    cols = st.columns(3, gap="medium")

    # RHR trend
    rhr_df = processed["rhr"]
    if not rhr_df.empty:
        fig = line_chart(rhr_df, "date", "rhr", "Resting Heart Rate", COLORS["danger"], show_area=True)
        cols[0].plotly_chart(fig, use_container_width=True)
    else:
        cols[0].info("No RHR data")

    # HRV weekly avg trend
    hrv_df = processed["hrv_summaries"]
    if not hrv_df.empty and "weekly_avg" in hrv_df.columns:
        hrv_plot = hrv_df.dropna(subset=["weekly_avg", "date"]).copy()
        if not hrv_plot.empty:
            hrv_plot["date"] = pd.to_datetime(hrv_plot["date"])
            fig = line_chart(hrv_plot, "date", "weekly_avg", "HRV Weekly Average",
                             COLORS["success"], show_area=True)
            cols[1].plotly_chart(fig, use_container_width=True)
        else:
            cols[1].info("No HRV data")
    else:
        cols[1].info("No HRV data")

    # Sleep score trend
    sleep_df = processed["sleep_summaries"]
    if not sleep_df.empty and "overall_score" in sleep_df.columns:
        sleep_plot = sleep_df.dropna(subset=["overall_score", "date"]).copy()
        if not sleep_plot.empty:
            sleep_plot["date"] = pd.to_datetime(sleep_plot["date"])
            fig = line_chart(sleep_plot, "date", "overall_score", "Sleep Score",
                             COLORS["primary"], show_area=True)
            cols[2].plotly_chart(fig, use_container_width=True)
        else:
            cols[2].info("No sleep data")
    else:
        cols[2].info("No sleep data")


def _render_insights(processed: dict):
    """Render health insights as styled cards."""
    section_header("Health Insights", "Overview")
    insights = generate_all_insights(processed)

    # Map categories to accent colors
    category_accents = {
        "Sleep": PAGE_ACCENTS["Sleep"],
        "Cardiovascular": PAGE_ACCENTS["Heart & HRV"],
        "Stress & Energy": PAGE_ACCENTS["Stress & Energy"],
        "Activity": PAGE_ACCENTS["Activity"],
        "SpO2": "#60A5FA",
    }

    # Render in 2 columns for better layout
    active = [(cat, items) for cat, items in insights.items() if items]
    if not active:
        st.info("Not enough data to generate insights yet.")
        return

    cols = st.columns(2, gap="medium")
    for i, (category, items) in enumerate(active):
        with cols[i % 2]:
            accent = category_accents.get(category, "#818CF8")
            st.markdown(f"""
            <p style="font-size:0.85rem; font-weight:600; color:{accent};
                      text-transform:uppercase; letter-spacing:0.05em;
                      margin:0.75rem 0 0.25rem 0">{category}</p>
            """, unsafe_allow_html=True)
            insight_card(items, accent)