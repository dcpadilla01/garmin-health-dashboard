"""Stress & energy page."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from dashboard.charts import line_chart, COLORS, _apply_layout, _hex_to_rgba
from dashboard.theme import page_header, section_header

PAGE = "Stress & Energy"


def render_stress(processed: dict):
    """Render the stress & energy page."""
    page_header("Stress & Energy", "Daily stress patterns and body battery", PAGE)

    cols = st.columns(2, gap="medium")
    with cols[0]:
        _render_stress_by_hour(processed)
    with cols[1]:
        _render_daily_stress_trend(processed)

    st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)
    _render_body_battery_day(processed)


def _render_stress_by_hour(processed: dict):
    """Render average stress by hour of day."""
    section_header("Average Stress by Hour", PAGE)
    stress_df = processed["stress"]
    if stress_df.empty:
        st.info("No stress data")
        return

    hourly = stress_df.copy()
    hourly["hour"] = hourly["datetime"].dt.hour
    hourly_avg = hourly.groupby("hour")["stress"].mean().reset_index()

    fig = go.Figure()
    colors = [
        _hex_to_rgba(COLORS["success"], 0.8) if s < 30 else
        _hex_to_rgba(COLORS["warning"], 0.8) if s < 50 else
        _hex_to_rgba(COLORS["danger"], 0.8)
        for s in hourly_avg["stress"]
    ]
    fig.add_trace(go.Bar(
        x=hourly_avg["hour"], y=hourly_avg["stress"],
        marker=dict(color=colors, cornerradius=4),
        hovertemplate="Hour %{x}:00<br>Avg stress: %{y:.0f}<extra></extra>",
    ))
    _apply_layout(fig, title="", height=300,
                  xaxis_title="Hour of Day", yaxis_title="Avg Stress")
    fig.update_xaxes(dtick=2)
    st.plotly_chart(fig, use_container_width=True)


def _render_daily_stress_trend(processed: dict):
    """Render daily average stress trend."""
    section_header("Daily Stress Trend", PAGE)
    stress_df = processed["stress"]
    if stress_df.empty:
        st.info("No stress data")
        return

    daily = stress_df.copy()
    daily["date"] = daily["datetime"].dt.date
    daily_avg = daily.groupby("date")["stress"].mean().reset_index()
    daily_avg["date"] = pd.to_datetime(daily_avg["date"])

    fig = line_chart(daily_avg, "date", "stress", "", COLORS["warning"], show_area=True)
    fig.add_hline(y=25, line_dash="dot", line_color=_hex_to_rgba(COLORS["success"], 0.3),
                  annotation_text="Low", annotation_position="right",
                  annotation_font=dict(color="#64748B", size=10))
    fig.add_hline(y=50, line_dash="dot", line_color=_hex_to_rgba(COLORS["warning"], 0.3),
                  annotation_text="Medium", annotation_position="right",
                  annotation_font=dict(color="#64748B", size=10))
    fig.add_hline(y=75, line_dash="dot", line_color=_hex_to_rgba(COLORS["danger"], 0.3),
                  annotation_text="High", annotation_position="right",
                  annotation_font=dict(color="#64748B", size=10))
    st.plotly_chart(fig, use_container_width=True)


def _render_body_battery_day(processed: dict):
    """Render body battery curve for a selected day."""
    section_header("Body Battery — Daily Curve", PAGE)
    bb_df = processed["body_battery"]
    if bb_df.empty:
        st.info("No body battery data")
        return

    bb_df = bb_df.copy()
    bb_df["date_str"] = bb_df["datetime"].dt.strftime("%Y-%m-%d")
    available_dates = sorted(bb_df["date_str"].unique(), reverse=True)

    selected = st.selectbox("Select day", available_dates, index=0, key="bb_day_select")
    day_bb = bb_df[bb_df["date_str"] == selected]

    fig = go.Figure()

    # Energy zone bands
    zones = [
        (0, 25, "rgba(248, 113, 113, 0.04)", "Low"),
        (25, 50, "rgba(251, 191, 36, 0.04)", "Moderate"),
        (50, 75, "rgba(96, 165, 250, 0.04)", "Good"),
        (75, 100, "rgba(52, 211, 153, 0.04)", "High"),
    ]
    for y0, y1, fill, label in zones:
        fig.add_hrect(
            y0=y0, y1=y1, fillcolor=fill, line_width=0,
            annotation_text=label, annotation_position="top left",
            annotation_font=dict(color="#475569", size=9),
        )

    fig.add_trace(go.Scatter(
        x=day_bb["datetime"], y=day_bb["body_battery"],
        mode="lines",
        fill="tozeroy",
        line=dict(color=COLORS["primary"], width=2.5, shape="spline", smoothing=0.8),
        fillcolor=_hex_to_rgba(COLORS["primary"], 0.1),
        hovertemplate="Battery: %{y:.0f}<extra></extra>",
    ))

    _apply_layout(fig, title="", height=350, yaxis_range=[0, 100])
    st.plotly_chart(fig, use_container_width=True)