"""Heart rate & HRV page."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from dashboard.charts import line_chart, hrv_band_chart, COLORS, _apply_layout, _hex_to_rgba
from dashboard.theme import page_header, section_header

PAGE = "Heart & HRV"


def render_heart(processed: dict):
    """Render the heart rate & HRV page."""
    page_header("Heart Rate & HRV", "Cardiovascular trends and recovery", PAGE)

    cols = st.columns(2, gap="medium")
    with cols[0]:
        _render_rhr_trend(processed)
    with cols[1]:
        _render_hrv_trend(processed)

    st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)
    _render_hr_distribution(processed)
    st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)
    _render_intraday_hr(processed)


def _render_rhr_trend(processed: dict):
    """Render 30-day RHR trend."""
    section_header("Resting Heart Rate", PAGE)
    rhr_df = processed["rhr"]
    if rhr_df.empty:
        st.info("No RHR data")
        return

    fig = line_chart(rhr_df, "date", "rhr", "", COLORS["danger"], show_area=True)
    if len(rhr_df) >= 7:
        rhr_ma = rhr_df.copy()
        rhr_ma["rhr_7d"] = rhr_ma["rhr"].rolling(7).mean()
        fig.add_trace(go.Scatter(
            x=rhr_ma["date"], y=rhr_ma["rhr_7d"],
            mode="lines",
            line=dict(color=COLORS["warning"], width=2, dash="dot"),
            name="7-day avg",
            hovertemplate="%{y:.1f} bpm<extra></extra>",
        ))
    st.plotly_chart(fig, use_container_width=True)


def _render_hrv_trend(processed: dict):
    """Render HRV nightly average with baseline bands."""
    section_header("HRV Nightly Average", PAGE)
    hrv_df = processed["hrv_summaries"]
    if hrv_df.empty:
        st.info("No HRV data")
        return

    latest = hrv_df.iloc[-1]
    fig = hrv_band_chart(
        hrv_df,
        baseline_low=latest.get("low_upper"),
        balanced_low=latest.get("balanced_low"),
        balanced_upper=latest.get("balanced_upper"),
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_hr_distribution(processed: dict):
    """Render heart rate distribution histogram."""
    section_header("Heart Rate Distribution", PAGE)
    hr_df = processed["heart_rate"]
    if hr_df.empty:
        st.info("No heart rate data")
        return

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=hr_df["heart_rate"],
        nbinsx=50,
        marker=dict(
            color=_hex_to_rgba(COLORS["danger"], 0.6),
            line=dict(color=COLORS["danger"], width=0.5),
        ),
    ))
    _apply_layout(fig, title="", height=280,
                  xaxis_title="Heart Rate (bpm)", yaxis_title="Count",
                  bargap=0.05)
    st.plotly_chart(fig, use_container_width=True)


def _render_intraday_hr(processed: dict):
    """Render intraday heart rate for a selected day."""
    section_header("Intraday Heart Rate", PAGE)
    hr_df = processed["heart_rate"]
    if hr_df.empty:
        st.info("No heart rate data")
        return

    hr_df = hr_df.copy()
    hr_df["date_str"] = hr_df["datetime"].dt.strftime("%Y-%m-%d")
    available_dates = sorted(hr_df["date_str"].unique(), reverse=True)

    selected = st.selectbox("Select day", available_dates, index=0, key="hr_day_select")
    day_hr = hr_df[hr_df["date_str"] == selected]

    fig = line_chart(day_hr, "datetime", "heart_rate", "", COLORS["danger"], show_area=True)
    st.plotly_chart(fig, use_container_width=True)