"""
app.py — Streamlit entry point for the Risk Assessment Platform.

Run locally: streamlit run app.py
Deploy: Streamlit Cloud with main file path app.py
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
    <div style="text-align:center;padding:3.5rem 1rem 2rem 1rem">
        <div style="display:inline-block;padding:0.3rem 1.2rem;
                    background:rgba(59,130,246,0.1);
                    border:1px solid rgba(59,130,246,0.25);
                    border-radius:99px;color:#60a5fa;
                    font-size:0.7rem;font-weight:700;
                    letter-spacing:0.1em;text-transform:uppercase;
                    margin-bottom:1.5rem">
            NIST SP 800-30 &nbsp;·&nbsp; AssessITS &nbsp;·&nbsp; ISO 27001
        </div>
        <h1 style="font-size:2.8rem;font-weight:800;color:#f1f5f9;
                   line-height:1.15;margin:0 0 0.9rem 0">
            Automated InfoSec<br>
            <span style="background:linear-gradient(135deg,#3b82f6,#818cf8);
                         -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                         background-clip:text">
                Risk Assessment Platform
            </span>
        </h1>
        <p style="color:#64748b;font-size:1rem;max-width:600px;
                  margin:0 auto;line-height:1.7">
            Quantitative risk intelligence powered by AI — identify, score, and remediate
            threats across your asset inventory using the AssessITS methodology.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Feature cards ─────────────────────────────────────────────────────────────
_CARD = (
    "background:#1e293b;border:1px solid #2d3f55;border-radius:14px;"
    "padding:1.6rem 1.5rem;margin-bottom:0.5rem"
)
_ICON = "font-size:1.6rem;margin-bottom:0.75rem"
_TITLE = "color:#e2e8f0;font-size:0.95rem;font-weight:700;margin-bottom:0.4rem"
_DESC = "color:#64748b;font-size:0.83rem;line-height:1.6"

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        f"""
        <div style="{_CARD}">
            <div style="{_ICON}">📋</div>
            <div style="{_TITLE}">1 — Assessment</div>
            <div style="{_DESC}">Add assets &amp; threats manually, load the sample dataset,
            or upload your own CSV inventory.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/1_Assessment.py", label="Open Assessment →")

with c2:
    st.markdown(
        f"""
        <div style="{_CARD}">
            <div style="{_ICON}">⚡</div>
            <div style="{_TITLE}">2 — Run Analysis</div>
            <div style="{_DESC}">Compute SLE, ALE, and Risk Impact Rating (1–250 band)
            with live CVE intelligence from NVD.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/1_Assessment.py", label="Run from Assessment →")

with c3:
    st.markdown(
        f"""
        <div style="{_CARD}">
            <div style="{_ICON}">📊</div>
            <div style="{_TITLE}">3 — Results &amp; Reports</div>
            <div style="{_DESC}">Interactive risk dashboard, NIST compliance checklist,
            AI control recommendations, and downloadable PDF reports.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/2_Results.py", label="View Results →")

st.divider()

# ── Quick start banner ────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="background:#1e293b;border:1px solid #2d3f55;
                border-left:3px solid #3b82f6;border-radius:10px;
                padding:1.1rem 1.5rem">
        <div style="color:#60a5fa;font-size:0.68rem;font-weight:700;
                    letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.5rem">
            Quick Start
        </div>
        <div style="color:#94a3b8;font-size:0.9rem;line-height:1.7">
            Open <strong style="color:#e2e8f0">Assessment</strong> &rarr;
            click <strong style="color:#e2e8f0">Load Dataset</strong> &rarr;
            click <strong style="color:#e2e8f0">Run Assessment</strong> &rarr;
            view <strong style="color:#e2e8f0">Results</strong>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
