"""Shared chart helpers using Plotly."""

import plotly.graph_objects as go
import pandas as pd

# ── Color palette ───────────────────────────────────────────────────

COLORS = {
    "primary": "#818CF8",
    "secondary": "#EC4899",
    "success": "#34D399",
    "warning": "#FBBF24",
    "danger": "#F87171",
    "info": "#60A5FA",
    "deep": "#818CF8",
    "light": "#A5B4FC",
    "rem": "#C084FC",
    "awake": "#FBBF24",
    "muted": "#64748B",
}

# ── Chart layout defaults ───────────────────────────────────────────

LAYOUT_DEFAULTS = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=48, r=16, t=48, b=48),
    font=dict(family="Inter, system-ui, sans-serif", size=12, color="#94A3B8"),
    title_font=dict(size=14, color="#CBD5E1"),
    hovermode="x unified",
    hoverlabel=dict(
        bgcolor="#1E293B",
        bordercolor="rgba(148, 163, 184, 0.2)",
        font=dict(color="#E2E8F0", size=12),
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        borderwidth=0,
        font=dict(color="#94A3B8", size=11),
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
    ),
    xaxis=dict(
        gridcolor="rgba(148, 163, 184, 0.06)",
        zerolinecolor="rgba(148, 163, 184, 0.1)",
        tickfont=dict(color="#64748B"),
    ),
    yaxis=dict(
        gridcolor="rgba(148, 163, 184, 0.06)",
        zerolinecolor="rgba(148, 163, 184, 0.1)",
        tickfont=dict(color="#64748B"),
    ),
)


def _apply_layout(fig: go.Figure, **kwargs) -> go.Figure:
    """Apply default layout settings to a figure."""
    layout = {**LAYOUT_DEFAULTS, **kwargs}
    fig.update_layout(**layout)
    return fig


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    """Convert hex color to rgba string."""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    return f"rgba({r},{g},{b},{alpha})"


# ── Line chart ──────────────────────────────────────────────────────

def line_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str = "",
    color: str = COLORS["primary"],
    show_area: bool = False,
    height: int = 300,
) -> go.Figure:
    """Create a line chart with optional gradient fill."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x], y=df[y],
        mode="lines",
        line=dict(color=color, width=2.5, shape="spline", smoothing=0.8),
        fill="tozeroy" if show_area else None,
        fillcolor=_hex_to_rgba(color, 0.08) if show_area else None,
        name=y.replace("_", " ").title(),
        hovertemplate="%{y:.1f}<extra></extra>",
    ))
    return _apply_layout(fig, title=title, height=height)


# ── Multi-line chart ────────────────────────────────────────────────

def multi_line_chart(
    df: pd.DataFrame,
    x: str,
    y_columns: list[str],
    title: str = "",
    colors: list[str] | None = None,
    height: int = 300,
) -> go.Figure:
    """Create a multi-line chart."""
    fig = go.Figure()
    color_list = colors or list(COLORS.values())
    for i, col in enumerate(y_columns):
        c = color_list[i % len(color_list)]
        fig.add_trace(go.Scatter(
            x=df[x], y=df[col],
            mode="lines",
            line=dict(color=c, width=2.5, shape="spline", smoothing=0.8),
            name=col.replace("_", " ").title(),
        ))
    return _apply_layout(fig, title=title, height=height)


# ── Bar chart ───────────────────────────────────────────────────────

def bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str = "",
    color: str = COLORS["primary"],
    height: int = 300,
) -> go.Figure:
    """Create a bar chart with rounded appearance."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df[x], y=df[y],
        marker=dict(
            color=_hex_to_rgba(color, 0.8),
            line=dict(color=color, width=0),
            cornerradius=4,
        ),
        name=y.replace("_", " ").title(),
        hovertemplate="%{y:.1f}<extra></extra>",
    ))
    return _apply_layout(fig, title=title, height=height)


# ── Stacked bar chart ──────────────────────────────────────────────

def stacked_bar_chart(
    df: pd.DataFrame,
    x: str,
    y_columns: list[str],
    title: str = "",
    colors: list[str] | None = None,
    height: int = 300,
) -> go.Figure:
    """Create a stacked bar chart."""
    fig = go.Figure()
    color_list = colors or list(COLORS.values())
    for i, col in enumerate(y_columns):
        c = color_list[i % len(color_list)]
        fig.add_trace(go.Bar(
            x=df[x], y=df[col],
            marker=dict(color=_hex_to_rgba(c, 0.85), cornerradius=2),
            name=col.replace("_", " ").title(),
            hovertemplate="%{y:.1f}h<extra></extra>",
        ))
    fig.update_layout(barmode="stack")
    return _apply_layout(fig, title=title, height=height)


# ── KPI card ────────────────────────────────────────────────────────

def kpi_card_html(
    label: str,
    value: str,
    delta: str = "",
    delta_good: bool = True,
    accent: str = "#818CF8",
) -> str:
    """Generate HTML for a KPI card with accent glow."""
    delta_color = "#34D399" if delta_good else "#F87171"
    delta_html = (
        f'<p style="color:{delta_color};font-size:0.8em;margin:4px 0 0 0;'
        f'font-weight:500">{delta}</p>'
        if delta else ""
    )
    return f"""
    <div style="background: linear-gradient(135deg, #1E293B 0%, #293548 100%);
                padding: 1.25em 1em;
                border-radius: 14px;
                text-align: center;
                border: 1px solid rgba(148, 163, 184, 0.08);
                box-shadow: 0 0 20px {_hex_to_rgba(accent, 0.06)};
                position: relative;
                overflow: hidden">
        <div style="position:absolute; top:0; left:0; right:0; height:3px;
                    background: linear-gradient(90deg, transparent, {accent}, transparent)"></div>
        <p style="color:#64748B; font-size:0.75em; margin:0 0 0.4em 0;
                  text-transform:uppercase; letter-spacing:0.1em;
                  font-weight:600">{label}</p>
        <p style="color:#F1F5F9; font-size:1.9em; font-weight:700;
                  margin:0; letter-spacing:-0.02em;
                  line-height:1.1">{value}</p>
        {delta_html}
    </div>
    """


# ── HRV band chart ─────────────────────────────────────────────────

def hrv_band_chart(
    hrv_df: pd.DataFrame,
    baseline_low: float | None = None,
    balanced_low: float | None = None,
    balanced_upper: float | None = None,
    height: int = 300,
) -> go.Figure:
    """Create HRV chart with baseline bands."""
    fig = go.Figure()

    if "date" in hrv_df.columns and "last_night_avg" in hrv_df.columns:
        x_col, y_col = "date", "last_night_avg"
    elif "datetime" in hrv_df.columns and "hrv" in hrv_df.columns:
        x_col, y_col = "datetime", "hrv"
    else:
        return _apply_layout(fig, title="HRV", height=height)

    # Baseline bands
    if balanced_low is not None and balanced_upper is not None:
        fig.add_hrect(
            y0=balanced_low, y1=balanced_upper,
            fillcolor="rgba(52, 211, 153, 0.08)",
            line_width=0,
            annotation_text="Balanced",
            annotation_position="top left",
            annotation_font=dict(color="#64748B", size=10),
        )
    if baseline_low is not None and balanced_low is not None:
        fig.add_hrect(
            y0=baseline_low, y1=balanced_low,
            fillcolor="rgba(251, 191, 36, 0.06)",
            line_width=0,
            annotation_text="Low",
            annotation_position="top left",
            annotation_font=dict(color="#64748B", size=10),
        )

    fig.add_trace(go.Scatter(
        x=hrv_df[x_col], y=hrv_df[y_col],
        mode="lines+markers",
        line=dict(color=COLORS["success"], width=2.5, shape="spline", smoothing=0.8),
        marker=dict(size=6, color=COLORS["success"], line=dict(width=1, color="#1E293B")),
        name="HRV",
        hovertemplate="%{y:.0f} ms<extra></extra>",
    ))

    return _apply_layout(fig, title="HRV Nightly Average", height=height)