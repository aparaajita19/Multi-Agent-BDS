"""
Chart Builder
─────────────
All Plotly chart definitions in one place.
Returns fig objects ready for st.plotly_chart().
"""

import plotly.express     as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

PLATFORM_COLORS = {
    "Amazon":   "#f0a500",
    "Meesho":   "#d4537e",
    "Flipkart": "#378add",
    "Myntra":   "#639922",
}

_LAYOUT = dict(
    font_family="Arial",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=36, b=28, l=12, r=12),
    height=300,
)


def _color_list(platforms):
    return [PLATFORM_COLORS.get(p, "#888") for p in platforms]


# ── 1. Avg Revenue Bar ────────────────────────────────────────────────────────
def revenue_bar(metrics: dict) -> go.Figure:
    platforms = list(metrics.keys())
    values    = [metrics[p]["avg_revenue"] for p in platforms]
    fig = px.bar(x=platforms, y=values,
                 color=platforms,
                 color_discrete_map=PLATFORM_COLORS,
                 labels={"x": "Platform", "y": "Avg Revenue (₹)", "color": ""},
                 title="Average Revenue per Transaction")
    fig.update_layout(**_LAYOUT, showlegend=False)
    fig.update_traces(marker_line_width=0)
    return fig


# ── 2. Conversion Rate Bar ────────────────────────────────────────────────────
def conversion_bar(metrics: dict) -> go.Figure:
    platforms = list(metrics.keys())
    values    = [metrics[p]["conversion_rate"] for p in platforms]
    fig = px.bar(x=platforms, y=values,
                 color=platforms,
                 color_discrete_map=PLATFORM_COLORS,
                 labels={"x": "Platform", "y": "Conversion Rate (%)", "color": ""},
                 title="Conversion Rate by Platform")
    fig.update_layout(**_LAYOUT, showlegend=False)
    fig.update_traces(marker_line_width=0)
    return fig


# ── 3. Composite Score Radar ─────────────────────────────────────────────────
def radar_chart(metrics: dict, scores: dict) -> go.Figure:
    categories = ["Avg Revenue", "Conversion Rate", "Composite Score"]
    fig = go.Figure()

    rev_max  = max(m["avg_revenue"]    for m in metrics.values()) or 1
    conv_max = max(m["conversion_rate"] for m in metrics.values()) or 1
    sc_max   = max(scores.values()) or 1

    for p, m in metrics.items():
        vals = [
            m["avg_revenue"]    / rev_max  * 100,
            m["conversion_rate"] / conv_max * 100,
            scores.get(p, 0)   / sc_max   * 100,
        ]
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name=p,
            line_color=PLATFORM_COLORS.get(p, "#888"),
            fillcolor=PLATFORM_COLORS.get(p, "#888"),
            opacity=0.3,
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title="Multi-Dimensional Platform Radar",
        showlegend=True,
        height=360,
        margin=dict(t=50, b=20, l=40, r=40),
        paper_bgcolor="rgba(0,0,0,0)",
        font_family="Arial",
    )
    return fig


# ── 4. Revenue Distribution Box ───────────────────────────────────────────────
def revenue_box(df) -> go.Figure:
    fig = px.box(df, x="PLATFORM", y="REVENUE",
                 color="PLATFORM",
                 color_discrete_map=PLATFORM_COLORS,
                 labels={"PLATFORM": "Platform", "REVENUE": "Revenue (₹)"},
                 title="Revenue Distribution by Platform")
    fig.update_layout(**_LAYOUT, showlegend=False)
    return fig


# ── 5. Financial Projection Bar ───────────────────────────────────────────────
def finance_bar(finance: dict) -> go.Figure:
    labels = ["Current Total", "Projected Total"]
    values = [finance["current_total"], finance["projected_total"]]
    colors = ["#adc8f5", "#378add"]

    fig = go.Figure(go.Bar(
        x=labels, y=values,
        marker_color=colors,
        text=[f"₹{v:,.0f}" for v in values],
        textposition="outside",
    ))
    fig.update_layout(
        title="Revenue: Current vs Projected",
        yaxis_title="Revenue (₹)",
        **_LAYOUT,
    )
    return fig


# ── 6. User Distribution Pie ──────────────────────────────────────────────────
def user_pie(metrics: dict) -> go.Figure:
    platforms = list(metrics.keys())
    users     = [metrics[p]["total_users"] for p in platforms]
    fig = go.Figure(go.Pie(
        labels=platforms,
        values=users,
        marker_colors=_color_list(platforms),
        hole=0.4,
    ))
    fig.update_layout(
        title="User Distribution by Platform",
        height=300,
        margin=dict(t=36, b=20, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font_family="Arial",
    )
    return fig
