"""Activity & fitness page."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from dashboard.charts import line_chart, COLORS, _apply_layout, _hex_to_rgba
from dashboard.theme import page_header, section_header

PAGE = "Activity"


def render_activity(processed: dict):
    """Render the activity & fitness page."""
    page_header("Activity & Fitness", "Workouts, steps, and training metrics", PAGE)

    _render_activity_log(processed)
    st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)

    cols = st.columns(2, gap="medium")
    with cols[0]:
        _render_steps_trend(processed)
    with cols[1]:
        _render_vo2max_trend(processed)

    st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)
    _render_hr_zones(processed)


def _render_activity_log(processed: dict):
    """Render activity log table."""
    section_header("Activity Log", PAGE)
    activities_df = processed["activities"]
    if activities_df.empty:
        st.info("No activities recorded")
        return

    display_cols = ["date", "name", "type", "duration_min", "distance_km",
                    "avg_hr", "max_hr", "calories", "aerobic_te", "anaerobic_te"]
    display = activities_df[display_cols].copy()
    display["date"] = display["date"].dt.strftime("%Y-%m-%d %H:%M")
    display.columns = ["Date", "Name", "Type", "Duration (min)", "Distance (km)",
                       "Avg HR", "Max HR", "Calories", "Aerobic TE", "Anaerobic TE"]

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Aerobic TE": st.column_config.NumberColumn(format="%.1f"),
            "Anaerobic TE": st.column_config.NumberColumn(format="%.1f"),
            "Distance (km)": st.column_config.NumberColumn(format="%.2f"),
        },
    )


def _render_steps_trend(processed: dict):
    """Render daily steps vs goals."""
    section_header("Daily Steps vs Goal", PAGE)
    steps_df = processed["daily_steps"]
    if steps_df.empty:
        st.info("No step data")
        return

    fig = go.Figure()
    # Color bars: green if goal met, muted otherwise
    if "step_goal" in steps_df.columns:
        bar_colors = [
            _hex_to_rgba(COLORS["success"], 0.75) if s >= g
            else _hex_to_rgba(COLORS["primary"], 0.5)
            for s, g in zip(steps_df["total_steps"], steps_df["step_goal"])
        ]
    else:
        bar_colors = _hex_to_rgba(COLORS["primary"], 0.5)

    fig.add_trace(go.Bar(
        x=steps_df["date"], y=steps_df["total_steps"],
        marker=dict(color=bar_colors, cornerradius=4),
        name="Steps",
        hovertemplate="%{y:,.0f} steps<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=steps_df["date"], y=steps_df["step_goal"],
        mode="lines",
        line=dict(color=COLORS["warning"], width=2, dash="dot"),
        name="Goal",
        hovertemplate="Goal: %{y:,.0f}<extra></extra>",
    ))
    _apply_layout(fig, title="", height=300)
    st.plotly_chart(fig, use_container_width=True)


def _render_vo2max_trend(processed: dict):
    """Render VO2 max trend from activities."""
    section_header("VO2 Max Trend", PAGE)
    activities_df = processed["activities"]
    if activities_df.empty:
        st.info("No activity data")
        return

    vo2_data = activities_df.dropna(subset=["vo2max"]).sort_values("date")
    if vo2_data.empty:
        st.info("No VO2 max readings")
        return

    fig = line_chart(vo2_data, "date", "vo2max", "", COLORS["success"], show_area=True)
    st.plotly_chart(fig, use_container_width=True)


def _render_hr_zones(processed: dict):
    """Render HR zone time distribution for activities."""
    section_header("HR Zone Distribution", PAGE)
    activities_df = processed["activities"]
    if activities_df.empty:
        st.info("No activity data")
        return

    zone_cols = ["hr_zone_1", "hr_zone_2", "hr_zone_3", "hr_zone_4", "hr_zone_5"]
    has_zones = activities_df.dropna(subset=zone_cols, how="all")
    if has_zones.empty:
        st.info("No HR zone data")
        return

    options = has_zones.apply(
        lambda r: f"{r['date'].strftime('%Y-%m-%d')} — {r['name']} ({r['type']})", axis=1
    ).tolist()
    selected_idx = st.selectbox("Select activity", range(len(options)),
                                format_func=lambda i: options[i], key="hr_zone_select")
    activity = has_zones.iloc[selected_idx]

    zone_values = [activity.get(z, 0) or 0 for z in zone_cols]
    zone_labels = ["Zone 1<br><span style='font-size:0.8em;color:#64748B'>Easy</span>",
                   "Zone 2<br><span style='font-size:0.8em;color:#64748B'>Fat Burn</span>",
                   "Zone 3<br><span style='font-size:0.8em;color:#64748B'>Cardio</span>",
                   "Zone 4<br><span style='font-size:0.8em;color:#64748B'>Hard</span>",
                   "Zone 5<br><span style='font-size:0.8em;color:#64748B'>Peak</span>"]
    zone_colors = ["#60A5FA", "#34D399", "#FBBF24", "#FB923C", "#F87171"]

    zone_minutes = [v / 60 for v in zone_values]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=zone_labels, y=zone_minutes,
        marker=dict(
            color=[_hex_to_rgba(c, 0.8) for c in zone_colors],
            cornerradius=6,
        ),
        hovertemplate="%{y:.1f} min<extra></extra>",
    ))
    _apply_layout(fig, title="", height=300, yaxis_title="Minutes")
    st.plotly_chart(fig, use_container_width=True)