"""Sleep analysis page."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from dashboard.charts import line_chart, COLORS, _apply_layout, _hex_to_rgba
from dashboard.theme import page_header, section_header

PAGE = "Sleep"


def render_sleep(processed: dict):
    """Render the sleep analysis page."""
    page_header("Sleep Analysis", "Sleep stages, scores, and recovery", PAGE)

    sleep_df = processed["sleep_summaries"]
    if sleep_df.empty:
        st.warning("No sleep data available.")
        return

    _render_sleep_stages(sleep_df)
    st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)

    cols = st.columns(2, gap="medium")
    with cols[0]:
        _render_sleep_score_trend(sleep_df)
    with cols[1]:
        _render_body_battery_recharge(sleep_df)

    st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)
    _render_night_detail(processed)


def _render_sleep_stages(sleep_df: pd.DataFrame):
    """Render stacked bar chart of sleep stages per night."""
    section_header("Sleep Stage Breakdown", PAGE)

    plot_df = sleep_df.dropna(subset=["date"]).copy()
    if plot_df.empty:
        st.info("No sleep stage data")
        return

    plot_df["date"] = pd.to_datetime(plot_df["date"])
    plot_df["deep_hrs"] = plot_df["deep_seconds"] / 3600
    plot_df["light_hrs"] = plot_df["light_seconds"] / 3600
    plot_df["rem_hrs"] = plot_df["rem_seconds"] / 3600
    plot_df["awake_hrs"] = plot_df["awake_seconds"] / 3600

    fig = go.Figure()
    stages = [
        ("deep_hrs", "Deep", COLORS["deep"]),
        ("light_hrs", "Light", COLORS["light"]),
        ("rem_hrs", "REM", COLORS["rem"]),
        ("awake_hrs", "Awake", COLORS["awake"]),
    ]
    for col, label, color in stages:
        fig.add_trace(go.Bar(
            x=plot_df["date"], y=plot_df[col],
            name=label,
            marker=dict(color=_hex_to_rgba(color, 0.85), cornerradius=2),
            hovertemplate=f"{label}: %{{y:.1f}}h<extra></extra>",
        ))

    fig.update_layout(barmode="stack")
    _apply_layout(fig, title="", height=350)
    st.plotly_chart(fig, use_container_width=True)


def _render_sleep_score_trend(sleep_df: pd.DataFrame):
    """Render sleep score trend line."""
    section_header("Sleep Score Trend", PAGE)
    plot_df = sleep_df.dropna(subset=["overall_score", "date"]).copy()
    if plot_df.empty:
        st.info("No sleep score data")
        return

    plot_df["date"] = pd.to_datetime(plot_df["date"])
    fig = line_chart(plot_df, "date", "overall_score", "", COLORS["primary"])
    fig.add_hline(y=80, line_dash="dot", line_color=_hex_to_rgba(COLORS["success"], 0.4),
                  annotation_text="Good", annotation_position="right",
                  annotation_font=dict(color="#64748B", size=10))
    fig.add_hline(y=60, line_dash="dot", line_color=_hex_to_rgba(COLORS["warning"], 0.4),
                  annotation_text="Fair", annotation_position="right",
                  annotation_font=dict(color="#64748B", size=10))
    st.plotly_chart(fig, use_container_width=True)


def _render_body_battery_recharge(sleep_df: pd.DataFrame):
    """Render body battery recharge per night."""
    section_header("Body Battery Recharge", PAGE)
    plot_df = sleep_df.dropna(subset=["body_battery_change", "date"]).copy()
    if plot_df.empty:
        st.info("No body battery data")
        return

    plot_df["date"] = pd.to_datetime(plot_df["date"])
    fig = go.Figure()
    colors = [
        _hex_to_rgba(COLORS["success"], 0.8) if v > 0
        else _hex_to_rgba(COLORS["danger"], 0.8)
        for v in plot_df["body_battery_change"]
    ]
    fig.add_trace(go.Bar(
        x=plot_df["date"], y=plot_df["body_battery_change"],
        marker=dict(color=colors, cornerradius=4),
        name="Recharge",
        hovertemplate="+%{y:.0f}<extra></extra>",
    ))
    _apply_layout(fig, title="", height=300)
    st.plotly_chart(fig, use_container_width=True)


def _render_night_detail(processed: dict):
    """Render detailed view for a selected night."""
    section_header("Night Detail", PAGE)

    available_dates = sorted(processed["sleep_details"].keys(), reverse=True)
    if not available_dates:
        st.info("No detailed sleep data available")
        return

    selected = st.selectbox("Select night", available_dates, index=0)
    detail = processed["sleep_details"].get(selected)
    if not detail:
        return

    summary = detail["summary"]

    # Summary metrics as styled cards
    cols = st.columns(4, gap="medium")
    sleep_hrs = (summary.get("sleep_time_seconds", 0) or 0) / 3600
    cols[0].metric("Duration", f"{sleep_hrs:.1f} hrs")
    cols[1].metric("Score", summary.get("overall_score", "—"))
    eff = summary.get("efficiency")
    cols[2].metric("Efficiency", f"{eff * 100:.0f}%" if eff else "—")
    bb = summary.get("body_battery_change")
    cols[3].metric("BB Recharge", f"+{bb}" if bb is not None else "—")

    st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)

    # Sleep time-series in 2-column layout
    hr_df = detail["heart_rate"]
    hrv_df = detail["hrv"]
    bb_df = detail["body_battery"]

    if not hr_df.empty and not hrv_df.empty:
        c1, c2 = st.columns(2, gap="medium")
        with c1:
            fig = line_chart(hr_df, "datetime", "heart_rate",
                             "Heart Rate During Sleep", COLORS["danger"], show_area=True)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig = line_chart(hrv_df, "datetime", "hrv",
                             "HRV During Sleep", COLORS["success"], show_area=True)
            st.plotly_chart(fig, use_container_width=True)
    elif not hr_df.empty:
        fig = line_chart(hr_df, "datetime", "heart_rate",
                         "Heart Rate During Sleep", COLORS["danger"], show_area=True)
        st.plotly_chart(fig, use_container_width=True)

    if not bb_df.empty:
        fig = line_chart(bb_df, "datetime", "body_battery",
                         "Body Battery During Sleep", COLORS["primary"], show_area=True)
        st.plotly_chart(fig, use_container_width=True)