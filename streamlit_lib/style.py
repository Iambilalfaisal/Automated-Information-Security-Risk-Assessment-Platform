"""
style.py — Futuristic animated dark theme + UI component library.
"""

import re

import streamlit as st

# ── Fonts ──────────────────────────────────────────────────────────────────────
_FONTS = (
    "<link rel='preconnect' href='https://fonts.googleapis.com'>"
    "<link rel='preconnect' href='https://fonts.gstatic.com' crossorigin>"
    "<link href='https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700"
    "&family=JetBrains+Mono:wght@400;600&display=swap' rel='stylesheet'>"
)

# ── Master CSS ─────────────────────────────────────────────────────────────────
_CSS = """
<style>
/* ── Global font ── */
html, body, [class*="css"], .stMarkdown, button, input, select, textarea {
    font-family: 'Space Grotesk', -apple-system, sans-serif !important;
}
code, pre, .mono { font-family: 'JetBrains Mono', monospace !important; }

/* ── Custom scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #1e3a5f; border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: #3b82f6; }

/* ── App background — animated grid ── */
[data-testid="stAppViewContainer"] {
    background-color: #060d1a !important;
    background-image:
        radial-gradient(ellipse at 15% 25%, rgba(59,130,246,0.08) 0%, transparent 55%),
        radial-gradient(ellipse at 85% 75%, rgba(139,92,246,0.06) 0%, transparent 55%),
        radial-gradient(ellipse at 50% 50%, rgba(6,182,212,0.03) 0%, transparent 65%),
        linear-gradient(rgba(59,130,246,0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(59,130,246,0.02) 1px, transparent 1px) !important;
    background-size: 100% 100%, 100% 100%, 100% 100%, 60px 60px, 60px 60px !important;
    animation: gridDrift 30s linear infinite !important;
}
@keyframes gridDrift {
    0%   { background-position: 0% 0%, 100% 100%, 50% 50%, 0px 0px, 0px 0px; }
    100% { background-position: 0% 0%, 100% 100%, 50% 50%, 60px 60px, 60px 60px; }
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(6,13,26,0.97) !important;
    border-right: 1px solid rgba(59,130,246,0.1) !important;
    backdrop-filter: blur(20px);
}
[data-testid="stSidebarNav"] a {
    color: #475569 !important;
    border-radius: 8px;
    transition: all 0.2s ease;
    font-weight: 500;
}
[data-testid="stSidebarNav"] a:hover,
[data-testid="stSidebarNav"] a[aria-selected="true"] {
    background: rgba(59,130,246,0.1) !important;
    color: #60a5fa !important;
}

/* ── Top header ── */
[data-testid="stHeader"] {
    background: rgba(6,13,26,0.85) !important;
    border-bottom: 1px solid rgba(59,130,246,0.07) !important;
    backdrop-filter: blur(20px);
}

/* ── Keyframes ── */
@keyframes fadeInUp {
    from { opacity:0; transform:translateY(22px);  }
    to   { opacity:1; transform:translateY(0);     }
}
@keyframes fadeInDown {
    from { opacity:0; transform:translateY(-18px); }
    to   { opacity:1; transform:translateY(0);     }
}
@keyframes slideInLeft {
    from { opacity:0; transform:translateX(-22px); }
    to   { opacity:1; transform:translateX(0);     }
}
@keyframes fadeIn { from { opacity:0; } to { opacity:1; } }
@keyframes scaleIn {
    from { opacity:0; transform:scale(0.9);  }
    to   { opacity:1; transform:scale(1);    }
}
@keyframes gradientShift {
    0%   { background-position:0% 50%;   }
    50%  { background-position:100% 50%; }
    100% { background-position:0% 50%;   }
}
@keyframes shimmerSweep {
    0%   { left:-100%; }
    100% { left:250%;  }
}
@keyframes orbFloat {
    0%,100% { transform:translateY(0) scale(1);     }
    50%     { transform:translateY(-18px) scale(1.04); }
}
@keyframes badgePulse {
    0%,100% { box-shadow:0 0 0 0   rgba(59,130,246,0.4); }
    50%     { box-shadow:0 0 0 10px rgba(59,130,246,0);  }
}
@keyframes critPulse {
    0%,100% { box-shadow:0 0 0 0  rgba(239,68,68,0.45); }
    50%     { box-shadow:0 0 0 8px rgba(239,68,68,0);   }
}
@keyframes rowSlide {
    from { opacity:0; transform:translateX(-14px); }
    to   { opacity:1; transform:translateX(0);     }
}
@keyframes barGrow {
    0%   { background-position:200% 50%; }
    100% { background-position:0%   50%; }
}
@keyframes dotBlink {
    0%,100% { opacity:1; }
    50%     { opacity:0.3; }
}

/* ── Stat cards ── */
.scard {
    background: rgba(10,18,35,0.75);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 16px;
    padding: 1.35rem 1.5rem;
    position: relative;
    overflow: hidden;
    animation: scaleIn 0.5s cubic-bezier(0.34,1.56,0.64,1) both;
    transition: transform 0.3s cubic-bezier(0.34,1.56,0.64,1),
                box-shadow 0.3s ease, border-color 0.3s ease;
    cursor: default;
}
.scard::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 55%; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(59,130,246,0.7), transparent);
    animation: shimmerSweep 3.5s ease infinite;
}
.scard::after {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse at top left, rgba(59,130,246,0.05) 0%, transparent 55%);
    pointer-events: none;
}
.scard:hover {
    transform: translateY(-8px) scale(1.015);
    box-shadow: 0 28px 56px rgba(0,0,0,0.55),
                0 0 0 1px rgba(59,130,246,0.3),
                0 0 50px rgba(59,130,246,0.07);
    border-color: rgba(59,130,246,0.28);
}
.scard-label {
    color: #334155;
    font-size: 0.63rem;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    font-weight: 700;
    margin-bottom: 0.5rem;
}
.scard-value {
    font-size: 2.15rem;
    font-weight: 700;
    line-height: 1.1;
    letter-spacing: -0.025em;
}
.scard-sub { color: #1e3a5f; font-size: 0.72rem; margin-top: 0.35rem; font-weight: 500; }

/* ── Section headers ── */
.sec-hdr {
    display: flex;
    align-items: flex-start;
    gap: 0.7rem;
    margin: 2rem 0 1rem 0;
    animation: slideInLeft 0.45s cubic-bezier(0.23,1,0.32,1) both;
}
.sec-hdr-accent {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 3px;
    padding-top: 2px;
    flex-shrink: 0;
}
.sec-hdr-bar {
    width: 3px; height: 18px;
    border-radius: 99px;
    background: linear-gradient(180deg, #3b82f6, #8b5cf6);
}
.sec-hdr-dot {
    width: 5px; height: 5px;
    border-radius: 50%;
    background: #3b82f6;
    box-shadow: 0 0 8px rgba(59,130,246,0.7);
    animation: dotBlink 2s ease infinite;
}
.sec-hdr-text h3 {
    color: #f1f5f9;
    margin: 0;
    font-size: 1.05rem;
    font-weight: 700;
    letter-spacing: -0.015em;
}
.sec-hdr-text p {
    color: #334155;
    font-size: 0.79rem;
    margin: 0.15rem 0 0;
    font-weight: 400;
}

/* ── Risk register table ── */
.rtable { width:100%; border-collapse:collapse; font-size:0.83rem; }
.rtable thead tr {
    background: linear-gradient(90deg, rgba(6,13,26,0.95), rgba(15,23,42,0.7));
    border-bottom: 1px solid rgba(59,130,246,0.18);
}
.rtable th {
    padding: 0.72rem 1rem;
    text-align: left;
    color: #3b82f6;
    font-size: 0.63rem;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    font-weight: 700;
    white-space: nowrap;
}
.rtable td {
    padding: 0.75rem 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.025);
    transition: background 0.12s ease;
}
.rtable tbody tr { animation: rowSlide 0.35s cubic-bezier(0.23,1,0.32,1) both; }
.rtable tbody tr:hover td { background: rgba(59,130,246,0.05) !important; }
.rtable tbody tr:last-child td { border-bottom: none; }

/* ── Criticality badges ── */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 0.28rem;
    padding: 0.19rem 0.62rem;
    border-radius: 99px;
    font-size: 0.67rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    white-space: nowrap;
}
.badge::before { content:''; width:5px; height:5px; border-radius:50%; flex-shrink:0; }
.badge-Critical {
    background: rgba(127,29,29,0.35);
    color: #fca5a5;
    border: 1px solid rgba(239,68,68,0.35);
    box-shadow: 0 0 14px rgba(239,68,68,0.12), inset 0 1px 0 rgba(255,255,255,0.03);
    animation: critPulse 2.5s ease infinite;
}
.badge-Critical::before { background:#ef4444; box-shadow:0 0 6px rgba(239,68,68,0.8); }
.badge-High {
    background: rgba(124,45,18,0.35);
    color: #fdba74;
    border: 1px solid rgba(249,115,22,0.32);
    box-shadow: 0 0 10px rgba(249,115,22,0.08);
}
.badge-High::before { background:#f97316; }
.badge-Medium {
    background: rgba(113,63,18,0.35);
    color: #fde68a;
    border: 1px solid rgba(234,179,8,0.28);
}
.badge-Medium::before { background:#eab308; }
.badge-Low {
    background: rgba(20,83,45,0.35);
    color: #86efac;
    border: 1px solid rgba(34,197,94,0.28);
}
.badge-Low::before { background:#22c55e; }

/* ── CVE alert cards ── */
.cve-card {
    background: rgba(245,158,11,0.05);
    border: 1px solid rgba(245,158,11,0.18);
    border-left: 2px solid #f59e0b;
    border-radius: 10px;
    padding: 0.8rem 1rem;
    margin: 0.32rem 0;
    animation: fadeIn 0.4s ease both;
    font-size: 0.81rem;
    color: #fde68a;
    line-height: 1.58;
    backdrop-filter: blur(8px);
    transition: border-color 0.2s ease;
}
.cve-card:hover { border-color: rgba(245,158,11,0.4); }

/* ── Control recommendation cards ── */
.ctrl-card {
    background: rgba(6,13,26,0.65);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.04);
    border-radius: 13px;
    padding: 1.1rem 1.3rem;
    margin: 0.45rem 0;
    animation: fadeInUp 0.4s cubic-bezier(0.23,1,0.32,1) both;
    position: relative;
    overflow: hidden;
    transition: border-color 0.25s ease, transform 0.25s cubic-bezier(0.23,1,0.32,1),
                box-shadow 0.25s ease;
}
.ctrl-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0;
    width: 2px; height: 100%;
    background: linear-gradient(180deg, #3b82f6, #8b5cf6);
    opacity: 0;
    transition: opacity 0.25s ease;
}
.ctrl-card:hover {
    border-color: rgba(59,130,246,0.2);
    transform: translateX(7px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.35), -4px 0 24px rgba(59,130,246,0.07);
}
.ctrl-card:hover::before { opacity: 1; }
.ctrl-card-id   { color: #3b82f6; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; }
.ctrl-card-name { color: #e2e8f0; font-size: 0.9rem; font-weight: 600; margin: 0.15rem 0 0.4rem; }
.ctrl-card-desc { color: #475569; font-size: 0.81rem; line-height: 1.68; }
.ctrl-card-meta { color: #1e3a5f; font-size: 0.72rem; margin-top: 0.55rem; display:flex; gap:0.9rem; flex-wrap:wrap; }

/* ── Asset / Threat list items ── */
.list-item {
    background: rgba(10,18,35,0.6);
    border: 1px solid rgba(255,255,255,0.04);
    border-radius: 10px;
    padding: 0.75rem 1rem;
    margin: 0.3rem 0;
    animation: fadeInUp 0.35s cubic-bezier(0.23,1,0.32,1) both;
    transition: border-color 0.2s ease, background 0.2s ease;
}
.list-item:hover { border-color: rgba(59,130,246,0.2); background: rgba(15,23,42,0.7); }
.list-item-name  { color: #e2e8f0; font-weight: 600; font-size: 0.88rem; }
.list-item-meta  { color: #334155; font-size: 0.76rem; margin-top: 0.15rem; }
.list-item-tag   { display:inline-block; padding:0.1rem 0.5rem; border-radius:99px;
                   background:rgba(59,130,246,0.1); border:1px solid rgba(59,130,246,0.2);
                   color:#60a5fa; font-size:0.65rem; font-weight:700; letter-spacing:0.05em; }

/* ── Native Streamlit metric ── */
[data-testid="metric-container"] {
    background: rgba(10,18,35,0.75);
    backdrop-filter: blur(24px);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 16px;
    padding: 1.2rem 1.5rem !important;
    transition: transform 0.3s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.3s ease;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-5px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.4), 0 0 0 1px rgba(59,130,246,0.2);
}
[data-testid="stMetricValue"] > div {
    color: #60a5fa !important;
    font-size: 1.9rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.025em !important;
}
[data-testid="stMetricLabel"] > div {
    color: #334155 !important;
    font-size: 0.62rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.15em !important;
    font-weight: 700 !important;
}

/* ── Buttons ── */
[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #1d4ed8, #4338ca) !important;
    border: none !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    box-shadow: 0 4px 18px rgba(59,130,246,0.28) !important;
    transition: filter 0.2s ease, transform 0.2s cubic-bezier(0.34,1.56,0.64,1),
                box-shadow 0.2s ease !important;
}
[data-testid="baseButton-primary"]:hover {
    filter: brightness(1.15) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 30px rgba(59,130,246,0.38) !important;
}
[data-testid="baseButton-secondary"] {
    background: rgba(6,13,26,0.85) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    color: #475569 !important;
    font-weight: 500 !important;
    transition: border-color 0.2s ease, color 0.2s ease, transform 0.2s ease !important;
    backdrop-filter: blur(8px);
}
[data-testid="baseButton-secondary"]:hover {
    border-color: rgba(59,130,246,0.35) !important;
    color: #60a5fa !important;
    transform: translateY(-1px) !important;
}

/* ── Download buttons ── */
[data-testid="stDownloadButton"] button {
    background: rgba(6,13,26,0.85) !important;
    border: 1px solid rgba(59,130,246,0.22) !important;
    color: #60a5fa !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
    transition: all 0.22s ease !important;
    backdrop-filter: blur(8px);
}
[data-testid="stDownloadButton"] button:hover {
    background: rgba(59,130,246,0.09) !important;
    border-color: rgba(59,130,246,0.45) !important;
    box-shadow: 0 6px 20px rgba(59,130,246,0.18) !important;
    transform: translateY(-2px) !important;
}

/* ── Progress bar ── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #1d4ed8, #7c3aed, #0891b2, #1d4ed8) !important;
    background-size: 300% 100% !important;
    animation: gradientShift 3s ease infinite !important;
    border-radius: 99px !important;
}

/* ── Expanders ── */
details {
    background: rgba(6,13,26,0.6) !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(12px);
    transition: border-color 0.22s ease !important;
}
details:hover { border-color: rgba(59,130,246,0.22) !important; }
details summary { font-weight: 600 !important; color: #cbd5e1 !important; }

/* ── Divider ── */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(59,130,246,0.12),
                rgba(139,92,246,0.09), transparent) !important;
    margin: 1.5rem 0 !important;
}

/* ── Inputs ── */
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
    background: rgba(6,13,26,0.85) !important;
    border-color: rgba(255,255,255,0.07) !important;
    color: #e2e8f0 !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    border-radius: 8px !important;
}
[data-baseweb="input"] input:focus,
[data-baseweb="textarea"] textarea:focus {
    border-color: rgba(59,130,246,0.45) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.1) !important;
}

/* ── Select boxes ── */
[data-baseweb="select"] > div {
    background: rgba(6,13,26,0.85) !important;
    border-color: rgba(255,255,255,0.07) !important;
    border-radius: 8px !important;
}

/* ── Info/warning/error boxes ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    backdrop-filter: blur(8px);
}

/* ── Form submit button ── */
[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(135deg, #1e3a8a, #3730a3) !important;
    border: none !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 15px rgba(59,130,246,0.2) !important;
    transition: filter 0.2s ease, transform 0.2s ease !important;
}
[data-testid="stFormSubmitButton"] button:hover {
    filter: brightness(1.12) !important;
    transform: translateY(-1px) !important;
}

/* ── Sliders ── */
[data-testid="stSlider"] [data-testid="stThumbValue"] {
    background: #3b82f6 !important;
    color: #fff !important;
}
[data-testid="stSlider"] div[role="slider"] {
    background: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.2) !important;
}
</style>
"""


def apply_theme() -> None:
    """Inject futuristic dark theme CSS + Google Fonts."""
    st.markdown(_FONTS + _CSS, unsafe_allow_html=True)


# ── Component helpers ──────────────────────────────────────────────────────────

def section_header(title: str, subtitle: str = "") -> None:
    """Animated section header — gradient bar + pulsing dot."""
    sub = f'<p>{subtitle}</p>' if subtitle else ""
    st.markdown(
        f"""
        <div class="sec-hdr">
            <div class="sec-hdr-accent">
                <div class="sec-hdr-bar"></div>
                <div class="sec-hdr-dot"></div>
            </div>
            <div class="sec-hdr-text"><h3>{title}</h3>{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def stat_card(label: str, value: str, sub: str = "", accent: str = "#60a5fa") -> None:
    """
    Animated stat card with JS counter for numeric values.
    Shimmer sweep plays on loop; card lifts on hover.
    """
    uid = abs(hash(label + value)) % 99999
    sub_html = f'<div class="scard-sub">{sub}</div>' if sub else ""

    # Try to extract a numeric value for the counter animation
    stripped = re.sub(r"[^\d.]", "", value)
    try:
        num = float(stripped) if stripped else None
    except ValueError:
        num = None

    if num is not None and num >= 1:
        prefix = re.match(r"^([^\d]*)", value).group(1)
        suffix_m = re.search(r"(\D+)$", value)
        suffix = suffix_m.group(1) if suffix_m and not suffix_m.group(1).startswith(",") else ""

        counter_js = f"""
        <script>
        (function(){{
            var el=document.getElementById('sv{uid}');
            if(!el)return;
            var t={num},d=1100,s0=performance.now();
            function u(n){{
                var p=Math.min((n-s0)/d,1),e=1-Math.pow(1-p,3),v=Math.round(e*t);
                el.textContent='{prefix}'+v.toLocaleString()+'{suffix}';
                if(p<1)requestAnimationFrame(u);
            }}
            requestAnimationFrame(u);
        }})();
        </script>"""
        value_html = (
            f'<div class="scard-value" id="sv{uid}" style="color:{accent}">0</div>'
            + counter_js
        )
    else:
        value_html = f'<div class="scard-value" style="color:{accent}">{value}</div>'

    st.markdown(
        f'<div class="scard"><div class="scard-label">{label}</div>{value_html}{sub_html}</div>',
        unsafe_allow_html=True,
    )


def risk_table(rows: list[dict]) -> None:
    """Animated HTML risk register — staggered row slide-in, glow badges."""
    if not rows:
        st.info("No rows match the filter.")
        return

    body = ""
    for i, r in enumerate(rows):
        crit  = r.get("risk_criticality", "Low")
        delay = f"{min(i * 0.04, 0.9):.2f}s"
        cba_icon  = "✓" if r.get("control_recommended") else "—"
        cba_color = "#22c55e" if r.get("control_recommended") else "#1e3a5f"
        body += f"""
        <tr style="animation-delay:{delay}">
            <td style="color:#e2e8f0;font-weight:600">{r["asset_name"]}</td>
            <td style="color:#64748b">{r["threat_name"]}</td>
            <td style="color:#60a5fa;font-family:'JetBrains Mono',monospace">${r["sle"]:,.0f}</td>
            <td style="color:#f87171;font-family:'JetBrains Mono',monospace;font-weight:700">${r["ale"]:,.0f}</td>
            <td style="color:#cbd5e1;text-align:center">{r["risk_score"]:.1f}</td>
            <td style="color:#e2e8f0;text-align:center;font-weight:700">{r["risk_impact_rating"]:.0f}</td>
            <td style="text-align:center"><span class="badge badge-{crit}">{crit}</span></td>
            <td style="text-align:center;color:{cba_color};font-weight:700;font-size:1rem">{cba_icon}</td>
        </tr>"""

    st.markdown(
        f"""
        <div style="background:rgba(6,13,26,0.7);border:1px solid rgba(59,130,246,0.12);
                    border-radius:16px;overflow:hidden;overflow-x:auto;
                    backdrop-filter:blur(16px);margin-top:0.5rem">
            <table class="rtable">
                <thead>
                    <tr>
                        <th>Asset</th><th>Threat</th><th>SLE</th><th>ALE</th>
                        <th style="text-align:center">Score</th>
                        <th style="text-align:center">Impact</th>
                        <th style="text-align:center">Criticality</th>
                        <th style="text-align:center">CBA</th>
                    </tr>
                </thead>
                <tbody>{body}</tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


def cve_alerts(notifications: list[dict]) -> None:
    """Animated amber CVE alert cards."""
    if not notifications:
        return
    cards = "".join(
        f'<div class="cve-card" style="animation-delay:{i*0.05:.2f}s">'
        f'<span style="color:#f59e0b;font-weight:700;margin-right:0.4rem">&#9888;</span>'
        f'{n["message"]}</div>'
        for i, n in enumerate(notifications[:10])
    )
    st.markdown(
        f"""
        <div class="sec-hdr" style="margin-top:0.75rem">
            <div class="sec-hdr-accent">
                <div class="sec-hdr-bar" style="background:linear-gradient(180deg,#f59e0b,#ef4444)"></div>
                <div class="sec-hdr-dot" style="background:#f59e0b;box-shadow:0 0 8px rgba(245,158,11,0.7)"></div>
            </div>
            <div class="sec-hdr-text">
                <h3>CVE Alerts &nbsp;<span style="color:#f59e0b">({len(notifications)})</span></h3>
                <p>Live vulnerability intelligence for your assets</p>
            </div>
        </div>
        {cards}
        """,
        unsafe_allow_html=True,
    )


def control_cards(recs: list[dict], source: str = "", framework: str = "") -> None:
    """Animated glassmorphism control recommendation cards."""
    ai_badge = ""
    if source == "claude":
        ai_badge = (
            '<span style="background:rgba(139,92,246,0.15);color:#a78bfa;'
            'border:1px solid rgba(139,92,246,0.3);border-radius:99px;'
            'padding:0.14rem 0.6rem;font-size:0.65rem;font-weight:700;margin-left:0.5rem">'
            "AI ✦</span>"
        )
    cards = ""
    for i, rec in enumerate(recs):
        delay = f"{i * 0.06:.2f}"
        pri   = rec.get("implementation_priority", "")
        cost  = rec.get("estimated_cost_range", "")
        risk  = rec.get("mapped_risk", "")
        meta  = " &nbsp;·&nbsp; ".join(
            x for x in [
                f"Priority {pri}" if pri else "",
                cost,
                f"Risk: {risk}" if risk else "",
            ] if x
        )
        cards += f"""
        <div class="ctrl-card" style="animation-delay:{delay}s">
            <div class="ctrl-card-id">{rec.get("control_id","")}</div>
            <div class="ctrl-card-name">{rec.get("control_name","")}</div>
            <div class="ctrl-card-desc">{rec.get("plain_english_explanation","")}</div>
            <div class="ctrl-card-meta">{meta}</div>
        </div>"""

    label = "AI-Generated" if source == "claude" else "Rule-Based"
    st.markdown(
        f"""
        <div class="sec-hdr">
            <div class="sec-hdr-accent">
                <div class="sec-hdr-bar" style="background:linear-gradient(180deg,#8b5cf6,#06b6d4)"></div>
                <div class="sec-hdr-dot" style="background:#8b5cf6;box-shadow:0 0 8px rgba(139,92,246,0.7)"></div>
            </div>
            <div class="sec-hdr-text">
                <h3>Control Recommendations {ai_badge}</h3>
                <p>{label} &nbsp;·&nbsp; {framework or "NIST SP 800-30"}</p>
            </div>
        </div>
        {cards}
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str = "") -> None:
    """Futuristic animated page header with gradient underline."""
    sub = (
        f'<p style="color:#334155;font-size:0.86rem;margin:0.3rem 0 0;font-weight:400">'
        f'{subtitle}</p>'
    ) if subtitle else ""
    st.markdown(
        f"""
        <div style="animation:fadeInDown 0.5s cubic-bezier(0.23,1,0.32,1) both;margin-bottom:0.5rem">
            <h1 style="font-size:1.85rem;font-weight:800;color:#f8fafc;margin:0;
                       letter-spacing:-0.025em;line-height:1.2">{title}</h1>
            {sub}
            <div style="height:2px;width:60px;margin-top:0.6rem;border-radius:99px;
                        background:linear-gradient(90deg,#3b82f6,#8b5cf6);
                        box-shadow:0 0 12px rgba(59,130,246,0.5)"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def info_banner(text: str) -> None:
    """Styled info banner with animated blue border."""
    st.markdown(
        f"""
        <div style="background:rgba(6,13,26,0.7);border:1px solid rgba(59,130,246,0.15);
                    border-left:2px solid #3b82f6;border-radius:12px;
                    padding:1rem 1.25rem;margin:0.75rem 0;
                    animation:fadeIn 0.4s ease both;backdrop-filter:blur(12px)">
            <span style="color:#64748b;font-size:0.87rem">{text}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
