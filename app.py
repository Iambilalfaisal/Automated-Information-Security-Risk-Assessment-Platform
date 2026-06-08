"""
app.py — Streamlit entry point for the Risk Assessment Platform.
Run locally:  streamlit run app.py
Deploy:       Streamlit Cloud — main file: app.py
"""

import streamlit as st

from streamlit_lib.session import init_session
from streamlit_lib.style import apply_theme

st.set_page_config(
    page_title="InfoSec Risk Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session()
apply_theme()

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Hero-specific styles */
    .hero-wrap {
        position: relative;
        text-align: center;
        padding: 4.5rem 1rem 3.5rem;
        overflow: hidden;
        border-radius: 20px;
        border: 1px solid rgba(59,130,246,0.08);
        background: rgba(6,13,26,0.5);
        backdrop-filter: blur(20px);
        margin-bottom: 2.5rem;
    }
    .orb {
        position: absolute;
        border-radius: 50%;
        filter: blur(72px);
        pointer-events: none;
    }
    .orb-1 {
        width: 480px; height: 480px;
        background: radial-gradient(circle, rgba(59,130,246,0.14), transparent 65%);
        top: -160px; left: -120px;
        animation: orbFloat 11s ease-in-out infinite;
    }
    .orb-2 {
        width: 380px; height: 380px;
        background: radial-gradient(circle, rgba(139,92,246,0.12), transparent 65%);
        top: -80px; right: -80px;
        animation: orbFloat 13s ease-in-out -4.5s infinite;
    }
    .orb-3 {
        width: 280px; height: 280px;
        background: radial-gradient(circle, rgba(6,182,212,0.09), transparent 65%);
        bottom: -60px; left: 50%;
        transform: translateX(-50%);
        animation: orbFloat 9s ease-in-out -7s infinite;
    }
    .hero-inner { position: relative; z-index: 1; }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.38rem 1.2rem;
        background: rgba(59,130,246,0.07);
        border: 1px solid rgba(59,130,246,0.18);
        border-radius: 99px;
        margin-bottom: 1.6rem;
        animation: fadeInDown 0.6s cubic-bezier(0.23,1,0.32,1) both,
                   badgePulse 3.5s ease 0.8s infinite;
    }
    .badge-live-dot {
        width: 7px; height: 7px;
        border-radius: 50%;
        background: #3b82f6;
        box-shadow: 0 0 10px rgba(59,130,246,0.9), 0 0 20px rgba(59,130,246,0.4);
        animation: dotBlink 1.8s ease infinite;
        flex-shrink: 0;
    }
    .badge-text {
        color: #60a5fa;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
    }

    .hero-title {
        font-size: 3.4rem;
        font-weight: 800;
        color: #f8fafc;
        line-height: 1.08;
        letter-spacing: -0.035em;
        margin: 0 0 0.9rem;
        animation: fadeInUp 0.7s cubic-bezier(0.23,1,0.32,1) 0.1s both;
    }
    .hero-gradient {
        background: linear-gradient(135deg, #3b82f6, #818cf8, #06b6d4, #3b82f6);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradientShift 4.5s ease infinite;
    }
    .hero-sub {
        color: #475569;
        font-size: 1rem;
        max-width: 540px;
        margin: 0 auto 1rem;
        line-height: 1.8;
        animation: fadeInUp 0.7s cubic-bezier(0.23,1,0.32,1) 0.2s both;
    }

    /* Feature cards */
    .fcard {
        background: rgba(6,13,26,0.65);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 18px;
        padding: 1.8rem 1.6rem;
        height: 100%;
        transition: transform 0.3s cubic-bezier(0.34,1.56,0.64,1),
                    box-shadow 0.3s ease, border-color 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .fcard::before {
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 50%; height: 1px;
        background: linear-gradient(90deg, transparent, rgba(59,130,246,0.5), transparent);
        animation: shimmerSweep 4s ease infinite;
    }
    .fcard:hover {
        transform: translateY(-10px);
        box-shadow: 0 30px 60px rgba(0,0,0,0.6), 0 0 0 1px rgba(59,130,246,0.25),
                    0 0 60px rgba(59,130,246,0.06);
        border-color: rgba(59,130,246,0.25);
    }
    .fcard-icon {
        width: 52px; height: 52px;
        border-radius: 14px;
        background: linear-gradient(135deg, rgba(59,130,246,0.15), rgba(139,92,246,0.15));
        border: 1px solid rgba(59,130,246,0.22);
        display: flex; align-items: center; justify-content: center;
        font-size: 1.45rem;
        margin-bottom: 1.1rem;
        box-shadow: 0 4px 16px rgba(59,130,246,0.12);
    }
    .fcard-step {
        color: #1e3a5f;
        font-size: 0.62rem;
        font-weight: 700;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        margin-bottom: 0.3rem;
    }
    .fcard-title {
        color: #e2e8f0;
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        letter-spacing: -0.01em;
    }
    .fcard-desc {
        color: #334155;
        font-size: 0.83rem;
        line-height: 1.65;
    }

    /* Quick-start banner */
    .qs-banner {
        background: rgba(6,13,26,0.7);
        border: 1px solid rgba(59,130,246,0.12);
        border-radius: 14px;
        padding: 1.2rem 1.6rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        backdrop-filter: blur(16px);
        animation: fadeIn 0.6s ease 0.5s both;
    }
    .qs-icon {
        font-size: 1.3rem;
        flex-shrink: 0;
        filter: drop-shadow(0 0 8px rgba(59,130,246,0.5));
    }
    .qs-step {
        color: #3b82f6;
        font-weight: 700;
        font-size: 0.88rem;
    }
    .qs-arrow {
        color: #1e3a5f;
        margin: 0 0.1rem;
    }
    </style>

    <div class="hero-wrap">
        <div class="orb orb-1"></div>
        <div class="orb orb-2"></div>
        <div class="orb orb-3"></div>
        <div class="hero-inner">
            <div class="hero-badge">
                <div class="badge-live-dot"></div>
                <span class="badge-text">NIST SP 800-30 &nbsp;·&nbsp; AssessITS &nbsp;·&nbsp; ISO 27001</span>
            </div>
            <div class="hero-title">
                Automated InfoSec<br>
                <span class="hero-gradient">Risk Assessment Platform</span>
            </div>
            <p class="hero-sub">
                Quantitative risk intelligence powered by AI — identify, score, and remediate
                threats across your asset inventory using the AssessITS methodology.
            </p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Feature cards ─────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3, gap="medium")

with c1:
    st.markdown(
        """
        <div class="fcard" style="animation:fadeInUp 0.6s cubic-bezier(0.23,1,0.32,1) 0.1s both">
            <div class="fcard-icon">📋</div>
            <div class="fcard-step">Step 01</div>
            <div class="fcard-title">Assessment</div>
            <div class="fcard-desc">Add assets &amp; threats manually, load the sample CSV dataset,
            or upload your own inventory file.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/1_Assessment.py", label="Open Assessment →")

with c2:
    st.markdown(
        """
        <div class="fcard" style="animation:fadeInUp 0.6s cubic-bezier(0.23,1,0.32,1) 0.2s both">
            <div class="fcard-icon">⚡</div>
            <div class="fcard-step">Step 02</div>
            <div class="fcard-title">Run Analysis</div>
            <div class="fcard-desc">Compute SLE, ALE, and Risk Impact Rating (1–250 band)
            with live CVE intelligence fetched from NVD.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/1_Assessment.py", label="Run from Assessment →")

with c3:
    st.markdown(
        """
        <div class="fcard" style="animation:fadeInUp 0.6s cubic-bezier(0.23,1,0.32,1) 0.3s both">
            <div class="fcard-icon">📊</div>
            <div class="fcard-step">Step 03</div>
            <div class="fcard-title">Results &amp; Reports</div>
            <div class="fcard-desc">Interactive risk dashboard, heat map, NIST compliance,
            AI control recommendations, and downloadable PDF reports.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/2_Results.py", label="View Results →")

st.divider()

# ── Quick-start banner ────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="qs-banner">
        <span class="qs-icon">🛡️</span>
        <div>
            <div style="color:#334155;font-size:0.65rem;text-transform:uppercase;
                        letter-spacing:0.14em;font-weight:700;margin-bottom:0.3rem">Quick Start</div>
            <div style="font-size:0.88rem">
                <span class="qs-step">Assessment</span>
                <span class="qs-arrow"> → </span>
                <span class="qs-step">Load Dataset</span>
                <span class="qs-arrow"> → </span>
                <span class="qs-step">Run Assessment</span>
                <span class="qs-arrow"> → </span>
                <span class="qs-step">Results</span>
                <span style="color:#1e3a5f;font-size:0.82rem;margin-left:0.5rem">
                    · Full demo in under 60 seconds</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Methodology strip ─────────────────────────────────────────────────────────
st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

col_a, col_b, col_c, col_d = st.columns(4)
_PILL = (
    "background:rgba(6,13,26,0.7);border:1px solid rgba(255,255,255,0.05);"
    "border-radius:10px;padding:0.9rem 1rem;text-align:center;"
    "backdrop-filter:blur(12px);animation:scaleIn 0.5s ease both"
)
_PILL_V  = "color:#e2e8f0;font-size:1.1rem;font-weight:700;letter-spacing:-0.01em"
_PILL_L  = "color:#1e3a5f;font-size:0.62rem;text-transform:uppercase;letter-spacing:0.12em;font-weight:700;margin-top:0.2rem"

with col_a:
    st.markdown(f'<div style="{_PILL};animation-delay:0.1s"><div style="{_PILL_V}">SLE / ALE</div>'
                f'<div style="{_PILL_L}">Quantitative Risk</div></div>', unsafe_allow_html=True)
with col_b:
    st.markdown(f'<div style="{_PILL};animation-delay:0.2s"><div style="{_PILL_V}">1–250</div>'
                f'<div style="{_PILL_L}">AssessITS Band</div></div>', unsafe_allow_html=True)
with col_c:
    st.markdown(f'<div style="{_PILL};animation-delay:0.3s"><div style="{_PILL_V}">NIST SP 800-30</div>'
                f'<div style="{_PILL_L}">Framework</div></div>', unsafe_allow_html=True)
with col_d:
    st.markdown(f'<div style="{_PILL};animation-delay:0.4s"><div style="{_PILL_V}">ISO 27001</div>'
                f'<div style="{_PILL_L}">Compliance</div></div>', unsafe_allow_html=True)
