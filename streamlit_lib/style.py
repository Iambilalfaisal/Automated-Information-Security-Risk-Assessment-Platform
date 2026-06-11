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


_EXTRA_CSS = """
<style>
/* ── Page-transition fade-in for every rerun ── */
[data-testid="stMainBlockContainer"] > div > div {
    animation: fadeInUp 0.38s cubic-bezier(0.23,1,0.32,1) both;
}

/* ── Toast notification ── */
.toast {
    position: fixed;
    bottom: 1.5rem;
    right: 1.5rem;
    z-index: 9999;
    min-width: 260px;
    max-width: 420px;
    background: rgba(15,23,42,0.97);
    backdrop-filter: blur(20px);
    border-radius: 12px;
    padding: 0.9rem 1.25rem;
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.06);
    animation: toastSlide 0.45s cubic-bezier(0.34,1.56,0.64,1) both;
}
@keyframes toastSlide {
    from { opacity:0; transform:translateX(60px) scale(0.95); }
    to   { opacity:1; transform:translateX(0)    scale(1);    }
}
.toast-icon  { font-size:1.2rem; flex-shrink:0; margin-top:0.05rem; }
.toast-title { color:#f1f5f9; font-weight:700; font-size:0.88rem; margin-bottom:0.15rem; }
.toast-body  { color:#64748b; font-size:0.8rem; line-height:1.5; }
.toast-success { border-left:3px solid #22c55e; }
.toast-error   { border-left:3px solid #ef4444; }
.toast-warning { border-left:3px solid #f59e0b; }
.toast-info    { border-left:3px solid #3b82f6; }

/* ── Sidebar status widget ── */
.sb-widget {
    background: rgba(15,23,42,0.7);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 0.85rem 1rem;
    margin: 0.5rem 0;
}
.sb-widget-title {
    color: #334155;
    font-size: 0.6rem;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    font-weight: 700;
    margin-bottom: 0.6rem;
}
.sb-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.28rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.03);
}
.sb-row:last-child { border-bottom: none; }
.sb-row-label { color: #475569; font-size: 0.76rem; }
.sb-row-value { color: #60a5fa; font-size: 0.76rem; font-weight: 700; }
.sb-dot {
    display: inline-block;
    width: 6px; height: 6px;
    border-radius: 50%;
    margin-right: 0.4rem;
    vertical-align: middle;
}

/* ── Animated number counter ── */
@keyframes countUp {
    from { opacity:0; transform:translateY(8px); }
    to   { opacity:1; transform:translateY(0); }
}

/* ── Risk score color pill ── */
.score-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.22rem 0.7rem;
    border-radius: 99px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.03em;
}

/* ── Animated gradient border card ── */
.glow-card {
    position: relative;
    background: rgba(10,18,35,0.8);
    border-radius: 16px;
    padding: 1.5rem;
    animation: fadeInUp 0.5s ease both;
}
.glow-card::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 16px;
    padding: 1px;
    background: linear-gradient(135deg, rgba(59,130,246,0.4), rgba(139,92,246,0.2), rgba(6,182,212,0.3));
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    pointer-events: none;
    animation: gradientFlow 5s ease infinite;
}

/* ── Floating stat orbs ── */
@keyframes statPop {
    0%   { opacity:0; transform:scale(0.5) translateY(20px); }
    70%  { transform:scale(1.05) translateY(-4px); }
    100% { opacity:1; transform:scale(1) translateY(0); }
}

/* ── Section divider with label ── */
.divider-label {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin: 1.5rem 0;
    color: #1e3a5f;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}
.divider-label::before,
.divider-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(59,130,246,0.1));
}
.divider-label::after {
    background: linear-gradient(90deg, rgba(59,130,246,0.1), transparent);
}

/* ── Shimmer skeleton loader ── */
.skeleton {
    background: linear-gradient(90deg, #1e293b 25%, #243044 50%, #1e293b 75%);
    background-size: 200% 100%;
    animation: shimmerLoad 1.5s ease infinite;
    border-radius: 8px;
}
@keyframes shimmerLoad {
    0%   { background-position: 200% center; }
    100% { background-position:-200% center; }
}

/* ── Pulse ring for critical alerts ── */
@keyframes pulseRing {
    0%   { transform:scale(0.8); opacity:0.8; }
    100% { transform:scale(2.0); opacity:0; }
}
.pulse-ring {
    position: relative;
    display: inline-block;
}
.pulse-ring::before {
    content:'';
    position:absolute;
    inset:-4px;
    border-radius:50%;
    background:rgba(239,68,68,0.4);
    animation:pulseRing 1.8s ease-out infinite;
}

/* ── Stagger-in animation for lists ── */
.stagger-item:nth-child(1) { animation-delay:0.04s; }
.stagger-item:nth-child(2) { animation-delay:0.08s; }
.stagger-item:nth-child(3) { animation-delay:0.12s; }
.stagger-item:nth-child(4) { animation-delay:0.16s; }
.stagger-item:nth-child(5) { animation-delay:0.20s; }

/* ── Tabbed section ── */
.stTabs [data-baseweb="tab-panel"] {
    animation: fadeIn 0.3s ease both !important;
}
</style>
"""


def apply_theme() -> None:
    """Inject futuristic dark theme CSS + Google Fonts."""
    st.html(_FONTS + _CSS + _EXTRA_CSS)


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


def sidebar_status(session_id: str, models_module=None) -> None:
    """
    Render an animated status widget in the sidebar showing session context.
    Pass the database models module to fetch live counts.
    """
    from streamlit_lib.paths import ensure_backend_path
    ensure_backend_path()

    if models_module is None:
        try:
            from database import models as _m
            models_module = _m
        except Exception:
            return

    try:
        assets     = models_module.get_assets(session_id)
        assessment = models_module.get_latest_assessment(session_id)
        notifs     = models_module.get_notifications(session_id, unread_only=False)
        cve_count  = sum(1 for n in notifs if "CVE" in (n.get("message") or ""))
        has_assess = bool(assessment and assessment.get("results"))
        total_ale  = 0
        if has_assess:
            total_ale = (assessment["results"].get("summary") or {}).get("total_ale", 0)

        status_dot  = "#22c55e" if has_assess else "#f59e0b"
        status_text = "Active" if has_assess else "Pending"

        with st.sidebar:
            st.markdown(
                f"""
                <div class="sb-widget">
                    <div class="sb-widget-title">Session Status</div>
                    <div class="sb-row">
                        <span class="sb-row-label">
                            <span class="sb-dot" style="background:{status_dot};
                                  box-shadow:0 0 6px {status_dot}88"></span>Assessment
                        </span>
                        <span class="sb-row-value" style="color:{status_dot}">{status_text}</span>
                    </div>
                    <div class="sb-row">
                        <span class="sb-row-label">Assets</span>
                        <span class="sb-row-value">{len(assets)}</span>
                    </div>
                    <div class="sb-row">
                        <span class="sb-row-label">CVE Alerts</span>
                        <span class="sb-row-value" style="color:{'#f87171' if cve_count else '#60a5fa'}">{cve_count}</span>
                    </div>
                    {"" if not has_assess else f'<div class="sb-row"><span class="sb-row-label">Total ALE</span><span class="sb-row-value" style="color:#f87171">${total_ale:,.0f}</span></div>'}
                </div>
                """,
                unsafe_allow_html=True,
            )
    except Exception:
        pass


def toast(title: str, body: str = "", kind: str = "info") -> None:
    """
    Animated toast notification fixed to bottom-right.
    kind: 'success' | 'error' | 'warning' | 'info'
    """
    icons = {"success": "✓", "error": "✕", "warning": "⚠", "info": "ℹ"}
    icon = icons.get(kind, "ℹ")
    body_html = f'<div class="toast-body">{body}</div>' if body else ""
    st.markdown(
        f"""
        <div class="toast toast-{kind}">
            <div class="toast-icon">{icon}</div>
            <div>
                <div class="toast-title">{title}</div>
                {body_html}
            </div>
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
