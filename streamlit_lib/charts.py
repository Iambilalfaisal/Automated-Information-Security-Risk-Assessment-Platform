"""
charts.py — Animated Plotly charts for the Streamlit results dashboard.
"""

import math

import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

CRIT_COLORS = {
    "Critical": "#ef4444",
    "High":     "#f97316",
    "Medium":   "#eab308",
    "Low":      "#22c55e",
}

_BG    = "#111827"
_BG2   = "#1e293b"
_GRID  = "#1e2d3d"
_TEXT  = "#64748b"
_TITLE = "#e2e8f0"
_SUB   = "#475569"

_BASE_LAYOUT = dict(
    paper_bgcolor=_BG,
    plot_bgcolor=_BG,
    font=dict(color=_TEXT, family="'Space Grotesk', sans-serif", size=12),
    title_font=dict(color=_TITLE, size=14, family="'Space Grotesk', sans-serif"),
    margin=dict(t=52, b=28, l=16, r=16),
    hoverlabel=dict(
        bgcolor="#0f172a",
        bordercolor="#334155",
        font=dict(color="#e2e8f0", size=12, family="'Space Grotesk', sans-serif"),
    ),
    transition=dict(duration=500, easing="cubic-in-out"),
)

_CONFIG = dict(
    displayModeBar=True,
    displaylogo=False,
    modeBarButtonsToRemove=["select2d", "lasso2d", "autoScale2d"],
    toImageButtonOptions=dict(format="png", filename="risk_chart"),
)


def _axis(gridcolor=_GRID, zerocolor=_GRID, **kw):
    return dict(
        gridcolor=gridcolor,
        zerolinecolor=zerocolor,
        tickcolor=_GRID,
        linecolor=_GRID,
        tickfont=dict(color=_SUB, size=11),
        **kw,
    )


def _title_html(main: str, sub: str = "") -> str:
    sub_part = f'<span style="font-size:11px;color:{_SUB}"> — {sub}</span>' if sub else ""
    return f"<b>{main}</b>{sub_part}"


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
    pull   = [0.12 if lbl == "Critical" else 0.03 for lbl in labels]

    hover_texts = [
        f"<b>{lbl}</b><br>Count: {cnt}<br>Share: {cnt/sum(values)*100:.1f}%"
        for lbl, cnt in zip(labels, values)
    ]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        pull=pull,
        customdata=hover_texts,
        hovertemplate="%{customdata}<extra></extra>",
        marker=dict(
            colors=[CRIT_COLORS[lbl] for lbl in labels],
            line=dict(color="#0a1120", width=3),
        ),
        textinfo="percent",
        textfont=dict(color="#e2e8f0", size=12, family="'Space Grotesk', sans-serif"),
        insidetextorientation="radial",
        rotation=90,
    ))

    total = sum(values)
    critical_n = counts.get("Critical", 0)
    fig.add_annotation(
        text=f"<b style='font-size:22px'>{total}</b><br><span style='font-size:11px;color:{_SUB}'>risks</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(color="#e2e8f0", size=18),
    )
    fig.update_layout(
        title=dict(text=_title_html("Risk Distribution", f"{critical_n} Critical"), x=0.02),
        legend=dict(
            font=dict(color=_TEXT, size=12),
            bgcolor="rgba(0,0,0,0)",
            orientation="h",
            y=-0.06,
            xanchor="center",
            x=0.5,
        ),
        height=360,
        **_BASE_LAYOUT,
    )
    st.plotly_chart(fig, use_container_width=True, config=_CONFIG)


def plot_top_risks_bar(register: list) -> None:
    """Horizontal bar chart with value labels and mid-scale reference line."""
    top = sorted(register, key=lambda r: r.get("risk_impact_rating", 0), reverse=True)[:10]
    if not top:
        return

    labels  = [f"{r['asset_name'][:15]} / {r['threat_name'][:15]}" for r in top]
    ratings = [r["risk_impact_rating"] for r in top]
    colors  = [CRIT_COLORS.get(r["risk_criticality"], _TEXT) for r in top]
    ale_vals = [r.get("ale", 0) for r in top]

    fig = go.Figure(go.Bar(
        y=labels[::-1],
        x=ratings[::-1],
        orientation="h",
        marker=dict(
            color=colors[::-1],
            opacity=0.90,
            line=dict(width=0),
        ),
        customdata=[[ale_vals[::-1][i], top[::-1][i].get("risk_criticality", ""), top[::-1][i].get("asset_name", "")] for i in range(len(top))],
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Impact Rating: <b>%{x:.0f}</b>/250<br>"
            "ALE: $%{customdata[0]:,.0f}<br>"
            "Criticality: %{customdata[1]}"
            "<extra></extra>"
        ),
        text=[f" {v:.0f}" for v in ratings[::-1]],
        textposition="outside",
        textfont=dict(color=_TEXT, size=11),
    ))

    fig.add_vline(
        x=125,
        line_dash="dot",
        line_color="#334155",
        line_width=1.5,
        annotation_text="Mid-scale (125)",
        annotation_font_color="#475569",
        annotation_font_size=10,
        annotation_position="top right",
    )
    fig.update_layout(
        title=dict(text=_title_html("Top 10 Risks", "by AssessITS Impact Rating"), x=0.02),
        xaxis_title="Impact Rating (1–250)",
        xaxis_range=[0, 295],
        height=440,
        **_BASE_LAYOUT,
    )
    fig.update_xaxes(**_axis())
    fig.update_yaxes(**_axis(showgrid=False))
    st.plotly_chart(fig, use_container_width=True, config=_CONFIG)


def plot_risk_heatmap(register: list) -> None:
    """
    5×5 Likelihood × Impact heat map (AssessITS methodology).
    X: impact bins 1–5. Y: likelihood bins 1–5.
    """
    if not register:
        st.info("No risks to display in heat map.")
        return

    CRIT_RANK = {"Low": 0, "Medium": 1, "High": 2, "Critical": 3}
    counts = [[0] * 5 for _ in range(5)]
    worst  = [[""] * 5 for _ in range(5)]
    assets_in_cell = [[[] for _ in range(5)] for _ in range(5)]

    for r in register:
        prob = float(r.get("probability", 0))
        vuln = int(r.get("vulnerability_score", 1))
        crit = r.get("risk_criticality", "Low")
        lbin = min(max(math.ceil(prob * 5), 1), 5) - 1
        ibin = min(max(vuln, 1), 5) - 1
        counts[lbin][ibin] += 1
        assets_in_cell[lbin][ibin].append(r.get("asset_name", "?")[:12])
        if CRIT_RANK.get(crit, 0) >= CRIT_RANK.get(worst[lbin][ibin], 0):
            worst[lbin][ibin] = crit

    axis_labels = ["1 — Minimal", "2 — Low", "3 — Medium", "4 — High", "5 — Critical"]
    text_matrix = [
        [
            (f"<b>{counts[row][col]}</b><br><sub style='font-size:9px'>{worst[row][col]}</sub>"
             if counts[row][col] else "")
            for col in range(5)
        ]
        for row in range(5)
    ]

    hover_matrix = [
        [
            (f"Likelihood: {axis_labels[row]}<br>Impact: {axis_labels[col]}<br>"
             f"Risks: {counts[row][col]}<br>Worst: {worst[row][col]}<br>"
             f"Assets: {', '.join(set(assets_in_cell[row][col][:3]))}")
            for col in range(5)
        ]
        for row in range(5)
    ]

    colorscale = [
        [0.00, "#0d1f35"],
        [0.01, "#1e3a5f"],
        [0.25, "#7c2d12"],
        [0.60, "#991b1b"],
        [1.00, "#7f1d1d"],
    ]

    fig = go.Figure(go.Heatmap(
        z=counts,
        x=axis_labels,
        y=axis_labels,
        text=text_matrix,
        customdata=hover_matrix,
        texttemplate="%{text}",
        textfont=dict(color="#e2e8f0", size=12),
        colorscale=colorscale,
        showscale=True,
        colorbar=dict(
            thickness=12,
            len=0.85,
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            tickfont=dict(color=_SUB, size=10),
            title=dict(text="Count", font=dict(color=_SUB, size=10), side="right"),
        ),
        hovertemplate="%{customdata}<extra></extra>",
        xgap=3,
        ygap=3,
    ))
    fig.update_layout(
        title=dict(text=_title_html("Likelihood × Impact Heat Map", "AssessITS 5×5 matrix"), x=0.02),
        xaxis_title="Impact (Vulnerability Score)",
        yaxis_title="Likelihood (Probability)",
        height=430,
        **_BASE_LAYOUT,
    )
    fig.update_xaxes(**_axis(showgrid=False))
    fig.update_yaxes(**_axis(showgrid=False))
    st.plotly_chart(fig, use_container_width=True, config=_CONFIG)


def plot_ale_by_asset(register: list) -> None:
    """Bar chart of ALE per asset, colour-coded low→high with gradient effect."""
    ale_by: dict[str, float] = {}
    threat_counts: dict[str, int] = {}
    for r in register:
        name = r["asset_name"]
        ale_by[name] = ale_by.get(name, 0) + r["ale"]
        threat_counts[name] = threat_counts.get(name, 0) + 1
    if not ale_by:
        return

    sorted_items = sorted(ale_by.items(), key=lambda x: x[1], reverse=True)
    assets = [x[0] for x in sorted_items]
    ales   = [x[1] for x in sorted_items]
    max_v  = max(ales) if ales else 1

    colors = []
    for v in ales:
        ratio = v / max_v
        if ratio > 0.65:
            colors.append("#ef4444")
        elif ratio > 0.35:
            colors.append("#f97316")
        elif ratio > 0.15:
            colors.append("#eab308")
        else:
            colors.append("#3b82f6")

    fig = go.Figure(go.Bar(
        x=assets,
        y=ales,
        marker=dict(
            color=colors,
            opacity=0.88,
            line=dict(width=0),
        ),
        customdata=[[threat_counts.get(a, 0)] for a in assets],
        text=[f"${v:,.0f}" for v in ales],
        textposition="outside",
        textfont=dict(color=_TEXT, size=10),
        hovertemplate=(
            "<b>%{x}</b><br>"
            "ALE: <b>$%{y:,.0f}</b><br>"
            "Threats: %{customdata[0]}"
            "<extra></extra>"
        ),
    ))
    fig.update_layout(
        title=dict(text=_title_html("Annualised Loss Expectancy", "per asset"), x=0.02),
        yaxis_title="ALE (USD)",
        xaxis_tickangle=-28,
        height=380,
        **_BASE_LAYOUT,
    )
    fig.update_xaxes(**_axis(showgrid=False))
    fig.update_yaxes(**_axis())
    st.plotly_chart(fig, use_container_width=True, config=_CONFIG)


def plot_risk_scatter(register: list) -> None:
    """
    Bubble scatter: Probability (X) × Vulnerability Score (Y), bubble size = ALE.
    Color-coded by criticality. Click bubbles to see asset details.
    """
    if not register:
        return

    fig = go.Figure()

    for crit in ["Critical", "High", "Medium", "Low"]:
        subset = [r for r in register if r.get("risk_criticality") == crit]
        if not subset:
            continue
        ales = [r.get("ale", 1) for r in subset]
        max_ale = max(ales) if ales else 1
        sizes = [max(10, min(60, (a / max_ale) * 55 + 10)) for a in ales]

        fig.add_trace(go.Scatter(
            x=[r.get("probability", 0) for r in subset],
            y=[r.get("vulnerability_score", 1) for r in subset],
            mode="markers",
            name=crit,
            marker=dict(
                color=CRIT_COLORS[crit],
                size=sizes,
                opacity=0.75,
                line=dict(color="#0a1120", width=1.5),
                sizemode="diameter",
            ),
            customdata=[
                [r["asset_name"], r["threat_name"], r.get("ale", 0), r.get("risk_impact_rating", 0)]
                for r in subset
            ],
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Threat: %{customdata[1]}<br>"
                "Probability: %{x:.2f}<br>"
                "Vulnerability: %{y}/5<br>"
                "ALE: $%{customdata[2]:,.0f}<br>"
                "Impact Rating: %{customdata[3]:.0f}"
                "<extra></extra>"
            ),
        ))

    fig.update_layout(
        title=dict(text=_title_html("Risk Scatter", "Probability × Vulnerability — bubble size = ALE"), x=0.02),
        xaxis_title="Probability (0–1)",
        yaxis_title="Vulnerability Score (1–5)",
        xaxis_range=[-0.05, 1.1],
        yaxis_range=[0.5, 5.5],
        legend=dict(
            font=dict(color=_TEXT, size=12),
            bgcolor="rgba(0,0,0,0)",
            orientation="h",
            y=1.08,
            xanchor="right",
            x=1,
        ),
        height=420,
        **_BASE_LAYOUT,
    )
    fig.update_xaxes(**_axis())
    fig.update_yaxes(**_axis(), tickvals=[1, 2, 3, 4, 5])

    # Add risk zone background annotations
    fig.add_hrect(y0=3.5, y1=5.5, fillcolor="rgba(239,68,68,0.04)", layer="below", line_width=0)
    fig.add_hrect(y0=0.5, y1=3.5, fillcolor="rgba(59,130,246,0.03)", layer="below", line_width=0)

    st.plotly_chart(fig, use_container_width=True, config=_CONFIG)


def plot_compliance_gauge(score: float) -> None:
    """Animated gauge chart for overall compliance score."""
    if score < 33:
        color, label = "#ef4444", "Critical Gap"
    elif score < 66:
        color, label = "#f97316", "Partial"
    else:
        color, label = "#22c55e", "Strong"

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        title={
            "text": f"Compliance — <b style='color:{color}'>{label}</b>",
            "font": {"color": _TEXT, "size": 13, "family": "'Space Grotesk', sans-serif"},
        },
        number={
            "suffix": "%",
            "font": {"color": _TITLE, "size": 40, "family": "'Space Grotesk', sans-serif"},
        },
        delta={
            "reference": 66,
            "valueformat": ".0f",
            "suffix": "% vs target",
            "font": {"size": 11},
        },
        gauge={
            "axis": {
                "range": [0, 100],
                "tickcolor": "#334155",
                "tickfont": {"color": "#475569", "size": 10},
                "nticks": 6,
            },
            "bar": {"color": color, "thickness": 0.68},
            "bgcolor": "#0a1120",
            "borderwidth": 0,
            "steps": [
                {"range": [0,   33], "color": "rgba(239,68,68,0.08)"},
                {"range": [33,  66], "color": "rgba(249,115,22,0.05)"},
                {"range": [66, 100], "color": "rgba(34,197,94,0.06)"},
            ],
            "threshold": {
                "line": {"color": "#3b82f6", "width": 2},
                "thickness": 0.82,
                "value": score,
            },
        },
    ))
    fig.update_layout(
        height=265,
        paper_bgcolor=_BG,
        plot_bgcolor=_BG,
        font=dict(color=_TEXT, family="'Space Grotesk', sans-serif"),
        margin=dict(t=55, b=15, l=35, r=35),
        transition=dict(duration=600, easing="cubic-in-out"),
    )
    st.plotly_chart(fig, use_container_width=True, config=_CONFIG)


def plot_ale_trend(assessments: list) -> None:
    """Line + area chart showing total ALE across assessment history (oldest → newest)."""
    data = []
    for a in reversed(assessments):
        summary  = a.get("summary", {})
        date_str = (a.get("created_at") or "")[:16]
        ale      = summary.get("total_ale", 0)
        assets_n = summary.get("total_assets", 0)
        threats_n = summary.get("total_threats", 0)
        if date_str:
            data.append((date_str, ale, assets_n, threats_n))

    if len(data) < 2:
        st.info("Run at least 2 assessments to see an ALE trend chart.")
        return

    dates    = [d[0] for d in data]
    ales     = [d[1] for d in data]
    assets_n = [d[2] for d in data]
    threats_n = [d[3] for d in data]

    first_ale = ales[0] if ales[0] else 1
    pct_change = [(v - first_ale) / first_ale * 100 for v in ales]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dates,
        y=ales,
        mode="lines+markers",
        name="Total ALE",
        line=dict(color="#3b82f6", width=2.5, shape="spline"),
        marker=dict(
            color="#3b82f6",
            size=9,
            line=dict(color="#0a1120", width=2),
            symbol="circle",
        ),
        fill="tozeroy",
        fillcolor="rgba(59,130,246,0.07)",
        customdata=[[assets_n[i], threats_n[i], pct_change[i]] for i in range(len(dates))],
        hovertemplate=(
            "<b>%{x}</b><br>"
            "ALE: <b>$%{y:,.0f}</b><br>"
            "Assets: %{customdata[0]}<br>"
            "Threats: %{customdata[1]}<br>"
            "Change from first: %{customdata[2]:+.1f}%"
            "<extra></extra>"
        ),
    ))

    fig.update_layout(
        title=dict(text=_title_html("ALE Trend", "annualised loss expectancy over time"), x=0.02),
        yaxis_title="Total ALE (USD)",
        xaxis_title="Assessment Date",
        height=320,
        showlegend=False,
        **_BASE_LAYOUT,
    )
    fig.update_xaxes(**_axis())
    fig.update_yaxes(**_axis())
    st.plotly_chart(fig, use_container_width=True, config=_CONFIG)


def plot_cve_severity_bar(cves: list) -> None:
    """Horizontal bar chart — CVE severity distribution with counts."""
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
        marker=dict(
            color=colors,
            opacity=0.88,
            line=dict(width=0),
        ),
        text=[str(v) if v else "0" for v in values],
        textposition="outside",
        textfont=dict(color=_TEXT, size=12),
        hovertemplate="<b>%{y}</b>: <b>%{x}</b> CVE(s)<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text=_title_html("CVE Severity", f"{sum(values)} total findings"), x=0.02),
        xaxis_title="Count",
        height=230,
        **_BASE_LAYOUT,
    )
    fig.update_xaxes(**_axis(range=[0, max_v * 1.5]))
    fig.update_yaxes(**_axis(showgrid=False))
    st.plotly_chart(fig, use_container_width=True, config=_CONFIG)


def plot_treatment_status(plans: list) -> None:
    """Donut chart — treatment plan status breakdown."""
    counts: dict[str, int] = {}
    for p in plans:
        s = p.get("status", "Pending")
        counts[s] = counts.get(s, 0) + 1

    if not counts:
        return

    STATUS_COLORS: dict[str, str] = {
        "Pending":     "#475569",
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
        hole=0.55,
        marker=dict(colors=colors, line=dict(color="#0a1120", width=3)),
        textinfo="percent",
        textfont=dict(color="#e2e8f0", size=12),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
        rotation=90,
    ))
    total = sum(values)
    completed_n = counts.get("Completed", 0)
    fig.add_annotation(
        text=f"<b>{total}</b><br><span style='font-size:10px;color:{_SUB}'>plans</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(color="#e2e8f0", size=18),
    )
    fig.update_layout(
        title=dict(text=_title_html("Treatment Status", f"{completed_n} completed"), x=0.02),
        legend=dict(
            font=dict(color=_TEXT, size=12),
            bgcolor="rgba(0,0,0,0)",
            orientation="h",
            y=-0.06,
            xanchor="center",
            x=0.5,
        ),
        height=340,
        **_BASE_LAYOUT,
    )
    st.plotly_chart(fig, use_container_width=True, config=_CONFIG)


def plot_strategy_breakdown(plans: list) -> None:
    """Horizontal bar chart — risk treatment strategy counts."""
    counts: dict[str, int] = {}
    for p in plans:
        s = p.get("strategy", "Mitigate")
        counts[s] = counts.get(s, 0) + 1
    if not counts:
        return

    STRAT_COLORS = {
        "Mitigate": "#3b82f6",
        "Accept":   "#22c55e",
        "Transfer": "#a78bfa",
        "Avoid":    "#ef4444",
    }
    labels = list(counts.keys())
    values = list(counts.values())
    colors = [STRAT_COLORS.get(lbl, _TEXT) for lbl in labels]

    fig = go.Figure(go.Bar(
        y=labels,
        x=values,
        orientation="h",
        marker=dict(color=colors, opacity=0.88, line=dict(width=0)),
        text=[str(v) for v in values],
        textposition="outside",
        textfont=dict(color=_TEXT, size=12),
        hovertemplate="<b>%{y}</b>: %{x} risk(s)<extra></extra>",
    ))
    max_v = max(values) if values else 1
    fig.update_layout(
        title=dict(text=_title_html("Strategy Breakdown", "ISO 27001 treatment options"), x=0.02),
        xaxis_title="Count",
        height=230,
        **_BASE_LAYOUT,
    )
    fig.update_xaxes(**_axis(range=[0, max_v * 1.45]))
    fig.update_yaxes(**_axis(showgrid=False))
    st.plotly_chart(fig, use_container_width=True, config=_CONFIG)
