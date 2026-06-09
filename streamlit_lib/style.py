"""
style.py — Animated professional dark theme + UI component helpers.
"""

import streamlit as st

_CSS = """
<style>
/* ── Keyframe animations ── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(18px); }
    to   { opacity: 1; transform: translateY(0);    }
}
@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-18px); }
    to   { opacity: 1; transform: translateX(0);     }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
@keyframes critPulse {
    0%,100% { box-shadow: 0 0 0 0   rgba(239,68,68,0.35); }
    50%     { box-shadow: 0 0 0 7px rgba(239,68,68,0);    }
}
@keyframes rowSlideIn {
    from { opacity: 0; transform: translateX(-10px); }
    to   { opacity: 1; transform: translateX(0);     }
}

/* ── Stat cards ── */
.scard {
    background: #1e293b;
    border: 1px solid #2d3f55;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    animation: fadeInUp 0.5s ease both;
    transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
    cursor: default;
}
.scard:hover {
    transform: translateY(-5px);
    box-shadow: 0 16px 36px rgba(59,130,246,0.14);
    border-color: #3b82f6;
}
.scard-label {
    color: #475569;
    font-size: 0.67rem;
    text-transform: uppercase;
    letter-spacing: 0.11em;
    font-weight: 700;
    margin-bottom: 0.4rem;
}
.scard-value { font-size: 2rem; font-weight: 700; line-height: 1.15; }
.scard-sub   { color: #475569; font-size: 0.74rem; margin-top: 0.3rem; }

/* ── Section headers ── */
.sec-header {
    border-left: 3px solid #3b82f6;
    padding-left: 0.8rem;
    margin: 1.8rem 0 1rem 0;
    animation: slideInLeft 0.4s ease both;
}
.sec-header h3 {
    color: #e2e8f0;
    margin: 0;
    font-size: 1.05rem;
    font-weight: 700;
    letter-spacing: -0.01em;
}
.sec-header p { color: #475569; font-size: 0.82rem; margin: 0.2rem 0 0 0; }

/* ── Risk register table ── */
.rtable { width: 100%; border-collapse: collapse; font-size: 0.84rem; }
.rtable th {
    padding: 0.65rem 1rem;
    text-align: left;
    color: #475569;
    font-size: 0.67rem;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    font-weight: 700;
    border-bottom: 1px solid #334155;
    white-space: nowrap;
}
.rtable td {
    padding: 0.72rem 1rem;
    border-bottom: 1px solid #1a2535;
}
.rtable tbody tr {
    animation: rowSlideIn 0.35s ease both;
    transition: background 0.12s ease;
}
.rtable tbody tr:hover td { background: #243044 !important; }
.rtable tbody tr:last-child td { border-bottom: none; }

/* ── Criticality badges ── */
.badge {
    display: inline-block;
    padding: 0.18rem 0.65rem;
    border-radius: 99px;
    font-size: 0.69rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    white-space: nowrap;
}
.badge-Critical {
    background: rgba(127,29,29,0.55);
    color: #fca5a5;
    border: 1px solid #991b1b;
    animation: critPulse 2.2s ease infinite;
}
.badge-High   { background: rgba(124,45,18,0.55); color: #fdba74; border: 1px solid #9a3412; }
.badge-Medium { background: rgba(113,63,18,0.55); color: #fde68a; border: 1px solid #854d0e; }
.badge-Low    { background: rgba(20,83,45,0.55);  color: #86efac; border: 1px solid #166534; }

/* ── CVE alert cards ── */
.cve-card {
    background: rgba(245,158,11,0.07);
    border: 1px solid rgba(245,158,11,0.22);
    border-left: 3px solid #f59e0b;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin: 0.35rem 0;
    animation: fadeIn 0.4s ease both;
    font-size: 0.83rem;
    color: #fde68a;
    line-height: 1.5;
}

/* ── Control recommendation cards ── */
.ctrl-card {
    background: #1e293b;
    border: 1px solid #2d3f55;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin: 0.45rem 0;
    animation: fadeInUp 0.4s ease both;
    transition: border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
}
.ctrl-card:hover {
    border-color: #3b82f6;
    transform: translateX(5px);
    box-shadow: 0 4px 20px rgba(59,130,246,0.1);
}
.ctrl-card-id    { color: #60a5fa; font-size: 0.78rem; font-weight: 700; letter-spacing: 0.05em; }
.ctrl-card-name  { color: #e2e8f0; font-size: 0.92rem; font-weight: 600; margin: 0.15rem 0 0.4rem 0; }
.ctrl-card-desc  { color: #64748b; font-size: 0.83rem; line-height: 1.6; }
.ctrl-card-meta  { color: #475569; font-size: 0.75rem; margin-top: 0.5rem; }

/* ── Native metric cards ── */
[data-testid="metric-container"] {
    background: #1e293b;
    border: 1px solid #2d3f55;
    border-radius: 12px;
    padding: 1.2rem 1.5rem !important;
    transition: transform 0.22s ease, box-shadow 0.22s ease;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 28px rgba(59,130,246,0.1);
}
[data-testid="stMetricValue"] > div {
    color: #60a5fa !important;
    font-size: 1.9rem !important;
    font-weight: 700 !important;
}
[data-testid="stMetricLabel"] > div {
    color: #64748b !important;
    font-size: 0.72rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    font-weight: 600 !important;
}

/* ── Buttons ── */
[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #2563eb, #4f46e5) !important;
    border: none !important;
    font-weight: 600 !important;
    transition: filter 0.18s ease, transform 0.15s ease !important;
}
[data-testid="baseButton-primary"]:hover {
    filter: brightness(1.12) !important;
    transform: translateY(-1px) !important;
}
[data-testid="baseButton-secondary"] {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    color: #94a3b8 !important;
    font-weight: 500 !important;
    transition: border-color 0.18s ease, color 0.18s ease !important;
}
[data-testid="baseButton-secondary"]:hover {
    border-color: #3b82f6 !important;
    color: #60a5fa !important;
}

/* ── Progress bar ── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #2563eb, #4f46e5) !important;
    border-radius: 99px !important;
    transition: width 0.8s cubic-bezier(0.25,0.46,0.45,0.94) !important;
}

/* ── Expanders ── */
details {
    border: 1px solid #334155 !important;
    border-radius: 10px !important;
    transition: border-color 0.18s ease !important;
}
details:hover { border-color: #3b82f6 !important; }

/* ── Treatment strategy badges ── */
.sbadge {
    display: inline-block;
    padding: 0.18rem 0.65rem;
    border-radius: 99px;
    font-size: 0.69rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    white-space: nowrap;
}
.sbadge-Mitigate { background: rgba(30,64,175,0.3);  color: #93c5fd; border: 1px solid #1d4ed8; }
.sbadge-Accept   { background: rgba(20,83,45,0.3);   color: #86efac; border: 1px solid #166534; }
.sbadge-Transfer { background: rgba(91,33,182,0.3);  color: #c4b5fd; border: 1px solid #6d28d9; }
.sbadge-Avoid    { background: rgba(127,29,29,0.35); color: #fca5a5; border: 1px solid #991b1b; }

/* ── Treatment status badges ── */
.tbadge {
    display: inline-block;
    padding: 0.18rem 0.65rem;
    border-radius: 99px;
    font-size: 0.69rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    white-space: nowrap;
}
.tbadge-Pending      { background: rgba(51,65,85,0.5);  color: #94a3b8; border: 1px solid #334155; }
.tbadge-In-Progress  { background: rgba(30,64,175,0.3); color: #93c5fd; border: 1px solid #1d4ed8; }
.tbadge-Completed    { background: rgba(20,83,45,0.55); color: #86efac; border: 1px solid #166534; }
.tbadge-Accepted     { background: rgba(91,33,182,0.3); color: #c4b5fd; border: 1px solid #6d28d9; }

/* ── Methodology section cards ── */
.mcard {
    background: #1e293b;
    border: 1px solid #2d3f55;
    border-radius: 12px;
    padding: 1.4rem 1.5rem;
    height: 100%;
    animation: fadeInUp 0.45s ease both;
}
.mcard-icon  { font-size: 1.8rem; margin-bottom: 0.7rem; }
.mcard-title { color: #60a5fa; font-size: 0.78rem; font-weight: 700;
               text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.4rem; }
.mcard-body  { color: #94a3b8; font-size: 0.84rem; line-height: 1.65; }

/* ════════════════════════════════════════════════════════════
   EXTENDED ANIMATIONS & DESIGN SYSTEM
   ════════════════════════════════════════════════════════════ */

@keyframes shimmer {
    0%   { background-position: -200% center; }
    100% { background-position:  200% center; }
}
@keyframes gradientFlow {
    0%   { background-position: 0%   50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0%   50%; }
}
@keyframes floatBob {
    0%, 100% { transform: translateY(0);    }
    50%      { transform: translateY(-6px); }
}
@keyframes scalePop {
    0%   { opacity: 0; transform: scale(0.92); }
    70%  { transform: scale(1.02); }
    100% { opacity: 1; transform: scale(1);    }
}
@keyframes slideInRight {
    from { opacity: 0; transform: translateX(18px); }
    to   { opacity: 1; transform: translateX(0);    }
}
@keyframes borderGlow {
    0%, 100% { box-shadow: 0 0 6px  rgba(59,130,246,0.18); }
    50%      { box-shadow: 0 0 22px rgba(59,130,246,0.48); }
}

/* ── Scrollbar ── */
::-webkit-scrollbar           { width: 5px; height: 5px; }
::-webkit-scrollbar-track     { background: #0a1120; }
::-webkit-scrollbar-thumb     { background: #2d3f55; border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: #3b82f6; }

/* ── App background ── */
[data-testid="stAppViewContainer"] { background: #0a1120 !important; }
.main .block-container { padding-top: 1.8rem !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080e1a 0%, #0f172a 100%) !important;
    border-right: 1px solid #1e293b !important;
}
[data-testid="stSidebarContent"] { background: transparent !important; }
[data-testid="stSidebarNavLink"] {
    border-radius: 8px !important;
    margin: 0.1rem 0.5rem !important;
    padding: 0.5rem 0.85rem !important;
    color: #64748b !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    transition: background 0.18s ease, color 0.18s ease !important;
    border-left: 3px solid transparent !important;
}
[data-testid="stSidebarNavLink"]:hover {
    background: rgba(59,130,246,0.09) !important;
    color: #93c5fd !important;
}
[data-testid="stSidebarNavLink"][aria-current="page"] {
    background: rgba(59,130,246,0.14) !important;
    border-left: 3px solid #3b82f6 !important;
    color: #60a5fa !important;
    font-weight: 600 !important;
}

/* ── Stat card shimmer ── */
.scard { position: relative; overflow: hidden; }
.scard::before {
    content: "";
    position: absolute;
    top: 0; left: -120%; width: 60%; height: 100%;
    background: linear-gradient(105deg, transparent, rgba(255,255,255,0.05), transparent);
    transition: left 0.65s cubic-bezier(0.4,0,0.2,1);
    pointer-events: none;
}
.scard:hover::before { left: 140%; }

/* ── Navigation cards (used on home dashboard) ── */
.nav-card {
    background: #1e293b;
    border: 1px solid #2d3f55;
    border-radius: 14px;
    padding: 1.4rem 1.5rem;
    margin-bottom: 0.4rem;
    position: relative;
    overflow: hidden;
    animation: fadeInUp 0.45s ease both;
    transition: transform 0.22s ease, box-shadow 0.22s ease,
                border-color 0.22s ease, background 0.22s ease;
    cursor: default;
}
.nav-card::before {
    content: "";
    position: absolute;
    top: 0; left: -120%; width: 55%; height: 100%;
    background: linear-gradient(105deg, transparent, rgba(59,130,246,0.06), transparent);
    transition: left 0.6s cubic-bezier(0.4,0,0.2,1);
    pointer-events: none;
}
.nav-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 16px 40px rgba(59,130,246,0.14);
    border-color: #3b82f6;
    background: #1a2942;
}
.nav-card:hover::before { left: 140%; }
.nav-card-icon {
    font-size: 1.55rem; margin-bottom: 0.65rem;
    display: inline-block;
    transition: transform 0.22s ease;
}
.nav-card:hover .nav-card-icon { transform: scale(1.2) rotate(-4deg); }
.nav-card-title { color: #e2e8f0; font-size: 0.9rem; font-weight: 700; margin-bottom: 0.3rem; }
.nav-card-desc  { color: #64748b; font-size: 0.8rem; line-height: 1.55; }

/* ── Hero background (landing page) ── */
.hero-bg {
    background: linear-gradient(-45deg, #0a1120, #1e1b4b, #0f172a, #162032);
    background-size: 400% 400%;
    animation: gradientFlow 10s ease infinite;
    border-radius: 18px;
    padding: 3.5rem 1rem 2.5rem 1rem;
    margin-bottom: 0.5rem;
    position: relative;
    overflow: hidden;
    text-align: center;
}
.hero-bg::before {
    content: "";
    position: absolute;
    width: 320px; height: 320px;
    background: radial-gradient(circle, rgba(59,130,246,0.09) 0%, transparent 70%);
    top: -80px; right: -60px;
    animation: floatBob 6s ease-in-out infinite;
    pointer-events: none;
}
.hero-bg::after {
    content: "";
    position: absolute;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(129,140,248,0.08) 0%, transparent 70%);
    bottom: -40px; left: 8%;
    animation: floatBob 9s ease-in-out infinite reverse;
    pointer-events: none;
}

/* ── Animated gradient text ── */
.grad-text {
    background: linear-gradient(135deg, #3b82f6, #818cf8, #06b6d4, #3b82f6);
    background-size: 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shimmer 4s linear infinite;
}

/* ── Info pill badge ── */
.info-pill {
    display: inline-block;
    background: rgba(59,130,246,0.1);
    border: 1px solid rgba(59,130,246,0.22);
    color: #60a5fa;
    font-size: 0.68rem; font-weight: 700;
    letter-spacing: 0.1em; text-transform: uppercase;
    padding: 0.25rem 0.85rem; border-radius: 99px;
    margin-bottom: 1.2rem;
    animation: fadeIn 0.6s ease both;
}

/* ── Animated HR ── */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg,
        transparent,
        #2d3f55 35%, #334155 50%, #2d3f55 65%,
        transparent) !important;
    margin: 1.5rem 0 !important;
    animation: fadeIn 0.5s ease both !important;
}

/* ── Enhanced primary button ── */
[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #2563eb, #4f46e5) !important;
    border: none !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    transition: filter 0.18s ease, transform 0.15s ease, box-shadow 0.2s ease !important;
}
[data-testid="baseButton-primary"]:hover {
    filter: brightness(1.1) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(59,130,246,0.45) !important;
}
[data-testid="baseButton-primary"]:active {
    transform: translateY(0) scale(0.97) !important;
    box-shadow: none !important;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] > button {
    background: #1e293b !important;
    border: 1px solid #2d3f55 !important;
    color: #94a3b8 !important;
    font-weight: 500 !important;
    transition: border-color 0.18s ease, color 0.18s ease, box-shadow 0.18s ease !important;
}
[data-testid="stDownloadButton"] > button:hover {
    border-color: #3b82f6 !important;
    color: #60a5fa !important;
    box-shadow: 0 4px 16px rgba(59,130,246,0.2) !important;
}

/* ── Form inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {
    background: #1a2535 !important;
    border: 1px solid #2d3f55 !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
    transition: border-color 0.18s ease, box-shadow 0.2s ease !important;
    caret-color: #60a5fa;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stNumberInput > div > div > input:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.18) !important;
    outline: none !important;
}
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: #1a2535 !important;
    border: 1px solid #2d3f55 !important;
    border-radius: 8px !important;
    transition: border-color 0.18s ease !important;
}
.stSelectbox > div > div:focus-within {
    border-color: #3b82f6 !important;
}

/* ── Slider thumb glow ── */
[data-testid="stSlider"] > div > div > div > div {
    background: linear-gradient(90deg, #2563eb, #4f46e5) !important;
}

/* ── Progress bar glow ── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #2563eb, #4f46e5) !important;
    border-radius: 99px !important;
    box-shadow: 0 0 8px rgba(59,130,246,0.35) !important;
    transition: width 0.8s cubic-bezier(0.25,0.46,0.45,0.94) !important;
}

/* ── DataEditor ── */
[data-testid="stDataEditor"] {
    border: 1px solid #2d3f55 !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    animation: fadeInUp 0.45s ease both !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    animation: fadeInUp 0.4s ease both !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    gap: 0.4rem !important;
    border-bottom: 1px solid #1e293b !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px 8px 0 0 !important;
    color: #64748b !important;
    font-weight: 600 !important;
    transition: all 0.18s ease !important;
}
.stTabs [data-baseweb="tab"]:hover  { color: #94a3b8 !important; }
.stTabs [aria-selected="true"] {
    background: rgba(59,130,246,0.1) !important;
    color: #60a5fa !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    background: #3b82f6 !important;
    height: 2px !important;
}

/* ── Caption text ── */
.stCaption,
[data-testid="stCaptionContainer"] > * { color: #475569 !important; font-size: 0.78rem !important; }
</style>
"""


def apply_theme() -> None:
    """Inject animated professional dark theme CSS."""
    st.markdown(_CSS, unsafe_allow_html=True)


def section_header(title: str, subtitle: str = "") -> None:
    """Animated section header with blue left-border accent."""
    sub = f'<p>{subtitle}</p>' if subtitle else ""
    st.markdown(
        f'<div class="sec-header"><h3>{title}</h3>{sub}</div>',
        unsafe_allow_html=True,
    )


def stat_card(label: str, value: str, sub: str = "", accent: str = "#60a5fa") -> None:
    """Animated stat card with hover lift effect."""
    sub_html = f'<div class="scard-sub">{sub}</div>' if sub else ""
    st.markdown(
        f"""
        <div class="scard">
            <div class="scard-label">{label}</div>
            <div class="scard-value" style="color:{accent}">{value}</div>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def risk_table(rows: list[dict]) -> None:
    """
    Animated HTML risk register table.
    Accepts raw register entries from risk_engine.
    """
    if not rows:
        st.info("No rows match the filter.")
        return

    rows_html = ""
    for i, r in enumerate(rows):
        crit = r.get("risk_criticality", "Low")
        delay = f"{min(i * 0.045, 1.0):.2f}s"
        cba = "✓" if r.get("control_recommended") else "—"
        cba_color = "#22c55e" if r.get("control_recommended") else "#334155"
        rows_html += f"""
        <tr style="animation-delay:{delay}">
            <td style="color:#e2e8f0;font-weight:500">{r["asset_name"]}</td>
            <td style="color:#94a3b8">{r["threat_name"]}</td>
            <td style="color:#60a5fa;font-family:monospace">${r["sle"]:,.0f}</td>
            <td style="color:#f87171;font-family:monospace;font-weight:600">${r["ale"]:,.0f}</td>
            <td style="color:#e2e8f0;text-align:center">{r["risk_score"]:.1f}</td>
            <td style="color:#e2e8f0;text-align:center;font-weight:600">{r["risk_impact_rating"]:.0f}</td>
            <td style="text-align:center">
                <span class="badge badge-{crit}">{crit}</span>
            </td>
            <td style="text-align:center;color:{cba_color};font-weight:700">{cba}</td>
        </tr>"""

    st.markdown(
        f"""
        <div style="background:#1e293b;border:1px solid #2d3f55;border-radius:12px;
                    overflow:hidden;overflow-x:auto;margin-top:0.5rem">
            <table class="rtable">
                <thead>
                    <tr style="background:#162032">
                        <th>Asset</th>
                        <th>Threat</th>
                        <th>SLE</th>
                        <th>ALE</th>
                        <th style="text-align:center">Risk Score</th>
                        <th style="text-align:center">Impact</th>
                        <th style="text-align:center">Criticality</th>
                        <th style="text-align:center">CBA</th>
                    </tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


def cve_alerts(notifications: list[dict]) -> None:
    """Animated CVE alert cards."""
    if not notifications:
        return
    cards = "".join(
        f'<div class="cve-card">&#9888; {n["message"]}</div>'
        for n in notifications[:10]
    )
    st.markdown(
        f"""
        <div style="margin:0.5rem 0 1rem 0">
            <div class="sec-header" style="margin-top:0.5rem">
                <h3>CVE Alerts &nbsp;<span style="color:#f59e0b">({len(notifications)})</span></h3>
                <p>Live vulnerability intelligence for your assets</p>
            </div>
            {cards}
        </div>
        """,
        unsafe_allow_html=True,
    )


def control_cards(recs: list[dict], source: str = "", framework: str = "") -> None:
    """Animated control recommendation cards."""
    source_badge = ""
    if source == "claude":
        source_badge = '<span style="background:rgba(99,102,241,0.15);color:#818cf8;border:1px solid rgba(99,102,241,0.3);border-radius:99px;padding:0.15rem 0.6rem;font-size:0.68rem;font-weight:700;margin-left:0.5rem">AI</span>'
    cards = ""
    for i, rec in enumerate(recs):
        delay = f"{i * 0.06:.2f}s"
        pri = rec.get("implementation_priority", "—")
        cost = rec.get("estimated_cost_range", "")
        mapped = rec.get("mapped_risk", "")
        meta_parts = [f"Priority {pri}" if pri else "", cost, f"Risk: {mapped}" if mapped else ""]
        meta = " &nbsp;·&nbsp; ".join(p for p in meta_parts if p)
        cards += f"""
        <div class="ctrl-card" style="animation-delay:{delay}">
            <div class="ctrl-card-id">{rec.get("control_id","")}</div>
            <div class="ctrl-card-name">{rec.get("control_name","")}</div>
            <div class="ctrl-card-desc">{rec.get("plain_english_explanation","")}</div>
            <div class="ctrl-card-meta">{meta}</div>
        </div>"""

    label = "AI-Generated" if source == "claude" else "Rule-Based"
    st.markdown(
        f"""
        <div class="sec-header">
            <h3>Control Recommendations {source_badge}</h3>
            <p>{label} &nbsp;·&nbsp; {framework or "NIST SP 800-30"}</p>
        </div>
        {cards}
        """,
        unsafe_allow_html=True,
    )


def info_banner(text: str) -> None:
    """Styled info banner with blue left border."""
    st.markdown(
        f"""
        <div style="background:#1e293b;border:1px solid #2d3f55;border-left:3px solid #3b82f6;
                    border-radius:10px;padding:1rem 1.25rem;margin:0.75rem 0;
                    animation:fadeIn 0.4s ease both">
            <span style="color:#94a3b8;font-size:0.88rem">{text}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str = "", badge: str = "") -> None:
    """
    Animated page header with shimmer-gradient underline accent.

    Args:
        title:    Main heading text.
        subtitle: Optional muted sub-text below the title.
        badge:    Optional pill badge rendered top-right (e.g. "Assessment Active").
    """
    sub_html   = (
        f'<p style="color:#475569;font-size:0.88rem;margin:0.2rem 0 0 0">{subtitle}</p>'
        if subtitle else ""
    )
    badge_html = (
        f'<div style="background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.25);'
        f'border-radius:99px;color:#60a5fa;font-size:0.68rem;font-weight:700;'
        f'letter-spacing:0.09em;text-transform:uppercase;padding:0.25rem 0.9rem;'
        f'white-space:nowrap;margin-top:0.2rem">{badge}</div>'
        if badge else ""
    )
    st.markdown(
        f"""
        <div style="display:flex;align-items:flex-start;justify-content:space-between;
                    flex-wrap:wrap;gap:0.5rem;margin-bottom:1.2rem;
                    animation:fadeInUp 0.45s ease both">
            <div style="position:relative;padding-bottom:0.65rem">
                <h1 style="font-size:1.9rem;font-weight:800;color:#f1f5f9;
                           margin:0 0 0.15rem 0;line-height:1.2">{title}</h1>
                {sub_html}
                <div style="position:absolute;bottom:0;left:0;width:52px;height:3px;
                            background:linear-gradient(90deg,#3b82f6,#818cf8,#3b82f6);
                            background-size:200%;
                            animation:shimmer 2.5s ease infinite;
                            border-radius:99px"></div>
            </div>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
