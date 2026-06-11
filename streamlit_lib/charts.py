"""
charts.py — Animated Plotly charts for the Streamlit results dashboard.
"""

import math

import plotly.graph_objects as go
import streamlit as st

CRIT_COLORS = {
    "Critical": "#ef4444",
    "High":     "#f97316",
    "Medium":   "#eab308",
    "Low":      "#22c55e",
}

_BG    = "#1e293b"
_GRID  = "#243044"
_TEXT  = "#94a3b8"
_TITLE = "#e2e8f0"

_BASE_LAYOUT = dict(
    paper_bgcolor=_BG,
    plot_bgcolor=_BG,
    font=dict(color=_TEXT, family="sans-serif", size=12),
    title_font=dict(color=_TITLE, size=14, family="sans-serif"),
    margin=dict(t=44, b=24, l=12, r=12),
    hoverlabel=dict(bgcolor="#0f172a", bordercolor="#334155", font=dict(color="#e2e8f0")),
)


def _axis(gridcolor=_GRID, zerocolor=_GRID, **kw):
    return dict(gridcolor=gridcolor, zerolinecolor=zerocolor,
                tickcolor=_GRID, linecolor=_GRID, **kw)


def plot_criticality_pie(register: list) -> None:
    """Animated donut chart — critical slice pulled out for emphasis."""
    counts: dict[str, int] = {}
    for r in register:
        c = r.get("risk_criticality", "Low")
        counts[c] = counts.get(c, 0) + 1
    if not counts:
        st.info("No risks to chart.")
        return

    labels = [k for k in ["Critical", "High", "Medium", "Low"] if k in counts]
    values = [counts[k] for k in labels]
    pull   = [0.12 if l == "Critical" else 0.02 for l in labels]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.52,
        pull=pull,
        marker=dict(
            colors=[CRIT_COLORS[l] for l in labels],
            line=dict(color="#0f172a", width=2),
        ),
        textfont=dict(color="#e2e8f0", size=12),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>",
        rotation=90,
    ))

    total = sum(values)
    fig.add_annotation(
        text=f"<b>{total}</b><br><span style='font-size:10px'>risks</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(color="#e2e8f0", size=18),
    )
    fig.update_layout(
        title="Risk Distribution by Criticality",
        legend=dict(font=dict(color=_TEXT), bgcolor="rgba(0,0,0,0)", orientation="h", y=-0.05),
        **_BASE_LAYOUT,
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_top_risks_bar(register: list) -> None:
    """Horizontal bar chart with value labels and mid-scale reference line."""
    top = register[:10]
    if not top:
        return

    labels  = [f"{r['asset_name'][:13]} / {r['threat_name'][:13]}" for r in top]
    ratings = [r["risk_impact_rating"] for r in top]
    colors  = [CRIT_COLORS.get(r["risk_criticality"], _TEXT) for r in top]

    fig = go.Figure(go.Bar(
        y=labels[::-1],
        x=ratings[::-1],
        orientation="h",
        marker=dict(color=colors[::-1], opacity=0.88, line=dict(width=0)),
        text=[f"  {v:.0f}" for v in ratings[::-1]],
        textposition="outside",
        textfont=dict(color=_TEXT, size=11),
        hovertemplate="<b>%{y}</b><br>Impact Rating: %{x:.0f}<extra></extra>",
    ))
    fig.add_vline(
        x=125,
        line_dash="dot", line_color="#334155", line_width=1.5,
        annotation_text="Mid (125)",
        annotation_font_color="#475569",
        annotation_font_size=10,
        annotation_position="top",
    )
    fig.update_layout(
        title="Top Risks by Impact Rating",
        xaxis_title="AssessITS Impact Rating (1–250)",
        xaxis_range=[0, 285],
        height=420,
        **_BASE_LAYOUT,
    )
    fig.update_xaxes(**_axis())
    fig.update_yaxes(**_axis())
    st.plotly_chart(fig, use_container_width=True)


def plot_risk_heatmap(register: list) -> None:
    """
    5×5 Likelihood × Impact heat map (AssessITS methodology).

    X: impact bins 1–5 from vulnerability_score.
    Y: likelihood bins 1–5 from probability via ceil(p×5).
    """
    if not register:
        st.info("No risks to display in heat map.")
        return

    CRIT_RANK = {"Low": 0, "Medium": 1, "High": 2, "Critical": 3}
    counts = [[0] * 5 for _ in range(5)]
    worst  = [[""] * 5 for _ in range(5)]

    for r in register:
        prob  = float(r.get("probability", 0))
        vuln  = int(r.get("vulnerability_score", 1))
        crit  = r.get("risk_criticality", "Low")
        lbin  = min(max(math.ceil(prob * 5), 1), 5) - 1
        ibin  = min(max(vuln, 1), 5) - 1
        counts[lbin][ibin] += 1
        if CRIT_RANK.get(crit, 0) >= CRIT_RANK.get(worst[lbin][ibin], 0):
            worst[lbin][ibin] = crit

    axis_labels = ["1 — Low", "2", "3", "4", "5 — High"]
    text_matrix = [
        [f"<b>{counts[r][c]}</b><br><sub>{worst[r][c]}</sub>"
         if counts[r][c] else "" for c in range(5)]
        for r in range(5)
    ]
    colorscale = [
        [0.00, "#1e293b"],
        [0.01, "#1e3a5f"],
        [0.35, "#92400e"],
        [0.70, "#7c2d12"],
        [1.00, "#7f1d1d"],
    ]

    fig = go.Figure(go.Heatmap(
        z=counts,
        x=axis_labels,
        y=axis_labels,
        text=text_matrix,
        texttemplate="%{text}",
        textfont=dict(color="#e2e8f0", size=11),
        colorscale=colorscale,
        showscale=False,
        hovertemplate="Likelihood: %{y}<br>Impact: %{x}<br>Risk count: %{z}<extra></extra>",
    ))
    fig.update_layout(
        title="Likelihood × Impact Heat Map (AssessITS)",
        xaxis_title="Impact  (Vulnerability Score 1–5)",
        yaxis_title="Likelihood  (Probability → 1–5)",
        height=410,
        **_BASE_LAYOUT,
    )
    fig.update_xaxes(**_axis())
    fig.update_yaxes(**_axis())
    st.plotly_chart(fig, use_container_width=True)


def plot_ale_by_asset(register: list) -> None:
    """Bar chart of ALE per asset, colour-coded low→high."""
    ale_by: dict[str, float] = {}
    for r in register:
        ale_by[r["asset_name"]] = ale_by.get(r["asset_name"], 0) + r["ale"]
    if not ale_by:
        return

    assets = list(ale_by.keys())
    ales   = list(ale_by.values())
    max_v  = max(ales) if ales else 1

    colors = []
    for v in ales:
        ratio = v / max_v
        if ratio > 0.7:
            colors.append("#ef4444")
        elif ratio > 0.35:
            colors.append("#f97316")
        else:
            colors.append("#3b82f6")

    fig = go.Figure(go.Bar(
        x=assets,
        y=ales,
        marker=dict(color=colors, opacity=0.88, line=dict(width=0)),
        text=[f"${v:,.0f}" for v in ales],
        textposition="outside",
        textfont=dict(color=_TEXT, size=10),
        hovertemplate="<b>%{x}</b><br>ALE: $%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        title="Annualised Loss Expectancy by Asset",
        yaxis_title="ALE (USD)",
        xaxis_tickangle=-30,
        **_BASE_LAYOUT,
    )
    fig.update_xaxes(**_axis())
    fig.update_yaxes(**_axis())
    st.plotly_chart(fig, use_container_width=True)


def plot_compliance_gauge(score: float) -> None:
    """Animated gauge chart for overall compliance score."""
    if score < 33:
        color, label = "#ef4444", "Critical Gap"
    elif score < 66:
        color, label = "#f97316", "Partial"
    else:
        color, label = "#22c55e", "Strong"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": f"Compliance — {label}",
               "font": {"color": _TEXT, "size": 13, "family": "sans-serif"}},
        number={"suffix": "%",
                "font": {"color": _TITLE, "size": 44, "family": "sans-serif"}},
        gauge={
            "axis": {
                "range": [0, 100],
                "tickcolor": "#334155",
                "tickfont": {"color": "#475569", "size": 11},
                "nticks": 6,
            },
            "bar": {"color": color, "thickness": 0.65},
            "bgcolor": "#0f172a",
            "borderwidth": 0,
            "steps": [
                {"range": [0,   33],  "color": "#1a0a0a"},
                {"range": [33,  66],  "color": "#1a1000"},
                {"range": [66, 100],  "color": "#0a1a0a"},
            ],
            "threshold": {
                "line": {"color": "#3b82f6", "width": 2},
                "thickness": 0.78,
                "value": score,
            },
        },
    ))
    fig.update_layout(
        height=240,
        paper_bgcolor=_BG,
        plot_bgcolor=_BG,
        font=dict(color=_TEXT, family="sans-serif"),
        margin=dict(t=50, b=10, l=30, r=30),
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_ale_trend(assessments: list) -> None:
    """Line + area chart showing total ALE across assessment history (oldest → newest)."""
    data = []
    for a in reversed(assessments):
        summary  = a.get("summary", {})
        date_str = (a.get("created_at") or "")[:16]
        ale      = summary.get("total_ale", 0)
        if date_str:
            data.append((date_str, ale))

    if len(data) < 2:
        st.info("Run at least 2 assessments to see an ALE trend chart.")
        return

    dates = [d[0] for d in data]
    ales  = [d[1] for d in data]

    fig = go.Figure(go.Scatter(
        x=dates,
        y=ales,
        mode="lines+markers",
        line=dict(color="#3b82f6", width=2.5),
        marker=dict(color="#3b82f6", size=9, line=dict(color="#0f172a", width=2)),
        fill="tozeroy",
        fillcolor="rgba(59,130,246,0.08)",
        hovertemplate="<b>%{x}</b><br>ALE: $%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        title="ALE Trend — Annualised Loss Expectancy Over Time",
        yaxis_title="Total ALE (USD)",
        xaxis_title="Assessment Date",
        height=300,
        **_BASE_LAYOUT,
    )
    fig.update_xaxes(**_axis())
    fig.update_yaxes(**_axis())
    st.plotly_chart(fig, use_container_width=True)


def plot_cve_severity_bar(cves: list) -> None:
    """Horizontal bar chart — CVE severity distribution."""
    counts: dict[str, int] = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for c in cves:
        sev = c.get("severity", "Low")
        if sev in counts:
            counts[sev] += 1

    labels = list(counts.keys())
    values = list(counts.values())
    colors = [CRIT_COLORS.get(lbl, _TEXT) for lbl in labels]
    max_v  = max(values) if any(v > 0 for v in values) else 1

    fig = go.Figure(go.Bar(
        y=labels,
        x=values,
        orientation="h",
        marker=dict(color=colors, opacity=0.88, line=dict(width=0)),
        text=[str(v) if v else "" for v in values],
        textposition="outside",
        textfont=dict(color=_TEXT, size=12),
        hovertemplate="<b>%{y}</b>: %{x} CVE(s)<extra></extra>",
    ))
    fig.update_layout(
        title="CVE Severity Distribution",
        xaxis_title="Count",
        height=220,
        **_BASE_LAYOUT,
    )
    fig.update_xaxes(**_axis(range=[0, max_v * 1.45]))
    fig.update_yaxes(**_axis())
    st.plotly_chart(fig, use_container_width=True)


def plot_treatment_status(plans: list) -> None:
    """Donut chart — treatment plan status breakdown."""
    counts: dict[str, int] = {}
    for p in plans:
        s = p.get("status", "Pending")
        counts[s] = counts.get(s, 0) + 1

    if not counts:
        return

    STATUS_COLORS: dict[str, str] = {
        "Pending":     "#64748b",
        "In Progress": "#3b82f6",
        "Completed":   "#22c55e",
        "Accepted":    "#a78bfa",
    }
    labels = list(counts.keys())
    values = list(counts.values())
    colors = [STATUS_COLORS.get(lbl, _TEXT) for lbl in labels]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.52,
        marker=dict(colors=colors, line=dict(color="#0f172a", width=2)),
        textfont=dict(color="#e2e8f0", size=12),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
        rotation=90,
    ))
    total = sum(values)
    fig.add_annotation(
        text=f"<b>{total}</b><br><span style='font-size:10px'>plans</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(color="#e2e8f0", size=18),
    )
    fig.update_layout(
        title="Treatment Status",
        legend=dict(font=dict(color=_TEXT), bgcolor="rgba(0,0,0,0)", orientation="h", y=-0.05),
        **_BASE_LAYOUT,
    )
    st.plotly_chart(fig, use_container_width=True)
