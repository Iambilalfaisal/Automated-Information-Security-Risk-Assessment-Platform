"""
charts.py — Plotly charts for the Streamlit results dashboard.
"""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

CRIT_COLORS = {
    "Critical": "#DC2626",
    "High": "#EA580C",
    "Medium": "#CA8A04",
    "Low": "#16A34A",
}


def plot_criticality_pie(register: list) -> None:
    """Pie chart of risk count by criticality."""
    counts: dict[str, int] = {}
    for r in register:
        c = r.get("risk_criticality", "Low")
        counts[c] = counts.get(c, 0) + 1
    if not counts:
        st.info("No risks to chart.")
        return
    labels = [k for k in ["Critical", "High", "Medium", "Low"] if k in counts]
    fig = px.pie(
        names=labels,
        values=[counts[k] for k in labels],
        title="Risk Distribution by Criticality",
        color=labels,
        color_discrete_map=CRIT_COLORS,
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_top_risks_bar(register: list) -> None:
    """Horizontal bar chart of top risks by impact rating."""
    top = register[:10]
    if not top:
        return
    labels = [f"{r['asset_name'][:15]} / {r['threat_name'][:15]}" for r in top]
    fig = go.Figure(
        go.Bar(
            y=labels[::-1],
            x=[r["risk_impact_rating"] for r in top][::-1],
            orientation="h",
            marker_color=[CRIT_COLORS.get(r["risk_criticality"], "#94a3b8") for r in top][::-1],
        )
    )
    fig.update_layout(
        title="Top Risks by Impact Rating",
        xaxis_title="AssessITS Impact Rating (1-250)",
        xaxis_range=[0, 250],
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_ale_by_asset(register: list) -> None:
    """Bar chart of total ALE per asset."""
    ale_by: dict[str, float] = {}
    for r in register:
        ale_by[r["asset_name"]] = ale_by.get(r["asset_name"], 0) + r["ale"]
    if not ale_by:
        return
    fig = px.bar(
        x=list(ale_by.keys()),
        y=list(ale_by.values()),
        labels={"x": "Asset", "y": "ALE (USD)"},
        title="Total Annualised Loss Expectancy by Asset",
    )
    fig.update_layout(xaxis_tickangle=-25)
    st.plotly_chart(fig, use_container_width=True)
