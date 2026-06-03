"""
charts.py — Plotly charts for the Streamlit results dashboard.
"""

import math

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


def plot_risk_heatmap(register: list) -> None:
    """
    5×5 Likelihood vs Impact heat map (AssessITS).

    X-axis: Impact bins 1–5 mapped from vulnerability_score (1–5).
    Y-axis: Likelihood bins 1–5 mapped from probability via ceil(p*5), clamped 1–5.
    Cell value: count of risks in that bin; colour intensity scales with count.
    """
    if not register:
        st.info("No risks to display in heat map.")
        return

    # Build 5×5 count matrix and track worst criticality per cell
    CRIT_RANK = {"Low": 0, "Medium": 1, "High": 2, "Critical": 3}
    counts = [[0] * 5 for _ in range(5)]
    worst = [[""] * 5 for _ in range(5)]

    for r in register:
        prob = float(r.get("probability", 0))
        vuln = int(r.get("vulnerability_score", 1))
        crit = r.get("risk_criticality", "Low")

        lbin = min(max(math.ceil(prob * 5), 1), 5) - 1   # row 0-4
        ibin = min(max(vuln, 1), 5) - 1                  # col 0-4

        counts[lbin][ibin] += 1
        if CRIT_RANK.get(crit, 0) >= CRIT_RANK.get(worst[lbin][ibin], 0):
            worst[lbin][ibin] = crit

    axis_labels = ["1 (Low)", "2", "3", "4", "5 (High)"]
    text_matrix = [
        [f"{counts[r][c]}<br>{worst[r][c]}" if counts[r][c] else "" for c in range(5)]
        for r in range(5)
    ]

    fig = go.Figure(
        go.Heatmap(
            z=counts,
            x=axis_labels,
            y=axis_labels,
            text=text_matrix,
            texttemplate="%{text}",
            colorscale=[[0, "#f0fdf4"], [0.33, "#fef08a"], [0.66, "#fed7aa"], [1, "#DC2626"]],
            showscale=True,
            colorbar={"title": "Risk count"},
            hovertemplate="Likelihood: %{y}<br>Impact: %{x}<br>Count: %{z}<extra></extra>",
        )
    )
    fig.update_layout(
        title="Likelihood vs Impact Heat Map (AssessITS)",
        xaxis_title="Impact (Vulnerability Level 1–5)",
        yaxis_title="Likelihood (Probability 0–1 → 1–5)",
        height=380,
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
