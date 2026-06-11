"""
app.py — Executive dashboard (post-assessment) or landing page (new users).

Run locally:  streamlit run app.py
Deploy:       Streamlit Cloud with main file path app.py
"""

import streamlit as st

from streamlit_lib.paths import ensure_backend_path
from streamlit_lib.session import get_session_id, init_session
from streamlit_lib.style import apply_theme, page_header, section_header, sidebar_status, stat_card

st.set_page_config(
    page_title="InfoSec Risk Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session()
apply_theme()
ensure_backend_path()

from database import models  # noqa: E402
from streamlit_lib.charts import plot_criticality_pie, plot_top_risks_bar  # noqa: E402
from streamlit_lib.services import get_compliance_data  # noqa: E402

session_id = get_session_id()
sidebar_status(session_id)
assessment = models.get_latest_assessment(session_id)

# ── Navigation items (icon, title, description, page path) ──────────────────
_NAV = [
    ("📋", "Assessment",          "Manage assets & threats, run new assessment.",          "pages/1_Assessment.py"),
    ("📊", "Results",             "Risk dashboard, heat map, compliance, PDF exports.",     "pages/2_Results.py"),
    ("🔍", "Threat Intelligence", "Live CVE feed per asset and NVD keyword search.",        "pages/3_Threat_Intelligence.py"),
    ("🛠️", "Treatment Plan",     "Assign strategies, owners and deadlines per risk.",      "pages/4_Treatment_Plan.py"),
    ("📈", "History",             "Assessment history and ALE trend over time.",            "pages/5_History.py"),
    ("📖", "Methodology",         "NIST SP 800-30, AssessITS formulas and references.",     "pages/6_Methodology.py"),
]

_CARD = (
    "background:#1e293b;border:1px solid #2d3f55;border-radius:14px;"
    "padding:1.4rem 1.5rem;margin-bottom:0.4rem"
)
_ICON  = "font-size:1.5rem;margin-bottom:0.6rem"
_TITLE = "color:#e2e8f0;font-size:0.9rem;font-weight:700;margin-bottom:0.3rem"
_DESC  = "color:#64748b;font-size:0.8rem;line-height:1.5"


if assessment and assessment.get("results"):
    # ── Executive Dashboard ────────────────────────────────────────────────────
    results  = assessment["results"]
    register = results.get("risk_register", [])
    summary  = results.get("summary", {})
    org_name = summary.get("org_name", "Organisation")
    created  = (assessment.get("created_at") or "")[:16]

    page_header(
        "Executive Dashboard",
        f"{org_name}  ·  Last assessed: {created}",
        badge="● Assessment Active",
    )

    comp_data     = get_compliance_data(session_id)
    notifications = models.get_notifications(session_id, unread_only=False)
    cve_count     = sum(1 for n in notifications if "CVE" in (n.get("message") or ""))

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        stat_card("Total ALE", f"${summary.get('total_ale', 0):,.0f}", "annual loss expectancy", accent="#f87171")
    with m2:
        stat_card("Risk Items", str(len(register)), "threats in register")
    with m3:
        stat_card("Compliance", f"{comp_data['score_percent']}%", "NIST SP 800-30", accent="#4ade80")
    with m4:
        stat_card("CVE Alerts", str(cve_count), "vulnerability notifications", accent="#fb923c")

    st.markdown("<div style='margin-top:0.5rem'></div>", unsafe_allow_html=True)
    st.divider()

    # Charts
    ch1, ch2 = st.columns(2)
    with ch1:
        plot_criticality_pie(register)
    with ch2:
        plot_top_risks_bar(register)

    # Recent CVE alerts (max 3)
    cve_notifs = [n for n in notifications if "CVE" in (n.get("message") or "")][:3]
    if cve_notifs:
        st.markdown(
            """
            <div class="sec-header" style="margin-top:1rem">
                <h3>Recent CVE Alerts</h3>
                <p>Latest vulnerability notifications — open Threat Intelligence for the full feed</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        for n in cve_notifs:
            st.markdown(f'<div class="cve-card">&#9888; {n["message"]}</div>', unsafe_allow_html=True)
        if cve_count > 3:
            st.page_link("pages/3_Threat_Intelligence.py", label=f"View all {cve_count} alerts →")

    st.divider()

    # Navigation grid
    section_header("Platform Modules", "Navigate to any section of the platform")
    row1 = st.columns(3)
    row2 = st.columns(3)
    for idx, (icon, title, desc, page) in enumerate(_NAV):
        col   = row1[idx] if idx < 3 else row2[idx - 3]
        delay = f"{(idx % 3) * 0.08:.2f}s"
        with col:
            st.markdown(
                f"""
                <div class="nav-card" style="animation-delay:{delay}">
                    <div class="nav-card-icon">{icon}</div>
                    <div class="nav-card-title">{title}</div>
                    <div class="nav-card-desc">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.page_link(page, label="Open →")

else:
    # ── Landing page for new users ─────────────────────────────────────────────
    st.markdown(
        """
        <div class="hero-bg" style="padding:4rem 2rem 3rem">
            <div class="info-pill">
                NIST SP 800-30 &nbsp;·&nbsp; AssessITS &nbsp;·&nbsp; ISO 27001
            </div>
            <h1 style="font-size:3rem;font-weight:800;color:#f1f5f9;
                       line-height:1.12;margin:0 0 1rem 0;letter-spacing:-0.03em">
                Automated InfoSec<br>
                <span class="grad-text">Risk Assessment Platform</span>
            </h1>
            <p style="color:#475569;font-size:1rem;max-width:580px;
                      margin:0 auto 2rem;line-height:1.8">
                Quantitative risk intelligence powered by AI — identify, score, and remediate
                threats across your asset inventory using the AssessITS methodology.
            </p>
            <div style="display:flex;justify-content:center;gap:2.5rem;flex-wrap:wrap;
                        margin-top:1rem">
                <div style="text-align:center">
                    <div style="font-size:1.8rem;font-weight:800;color:#60a5fa;
                                font-family:'Space Grotesk',sans-serif">NIST</div>
                    <div style="color:#334155;font-size:0.72rem;text-transform:uppercase;
                                letter-spacing:0.1em;margin-top:0.2rem">Framework</div>
                </div>
                <div style="text-align:center">
                    <div style="font-size:1.8rem;font-weight:800;color:#a78bfa">1–250</div>
                    <div style="color:#334155;font-size:0.72rem;text-transform:uppercase;
                                letter-spacing:0.1em;margin-top:0.2rem">Risk Rating</div>
                </div>
                <div style="text-align:center">
                    <div style="font-size:1.8rem;font-weight:800;color:#34d399">AI</div>
                    <div style="color:#334155;font-size:0.72rem;text-transform:uppercase;
                                letter-spacing:0.1em;margin-top:0.2rem">Recommendations</div>
                </div>
                <div style="text-align:center">
                    <div style="font-size:1.8rem;font-weight:800;color:#fb923c">CVE</div>
                    <div style="color:#334155;font-size:0.72rem;text-transform:uppercase;
                                letter-spacing:0.1em;margin-top:0.2rem">Intelligence</div>
                </div>
                <div style="text-align:center">
                    <div style="font-size:1.8rem;font-weight:800;color:#f87171">PDF</div>
                    <div style="color:#334155;font-size:0.72rem;text-transform:uppercase;
                                letter-spacing:0.1em;margin-top:0.2rem">Reports</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _QUICKSTART = [
        ("📋", "1 — Assessment",       "Load a sector-specific dataset (healthcare, banking, manufacturing, government…) or add assets manually.",  "pages/1_Assessment.py",  "Open Assessment →"),
        ("⚡", "2 — Run Analysis",      "Compute SLE, ALE, and Risk Impact Rating (1–250 band) with live CVE intelligence and AI controls.",         "pages/1_Assessment.py",  "Run from Assessment →"),
        ("📊", "3 — Results & Reports", "Risk dashboard, scatter map, NIST compliance checklist, AI control recommendations, and PDF reports.",      "pages/2_Results.py",     "View Results →"),
    ]
    qs_cols = st.columns(3)
    for i, (col, (icon, title, desc, page, link_label)) in enumerate(zip(qs_cols, _QUICKSTART)):
        with col:
            st.markdown(
                f"""
                <div class="nav-card" style="animation-delay:{i*0.08:.2f}s">
                    <div class="nav-card-icon">{icon}</div>
                    <div class="nav-card-title">{title}</div>
                    <div class="nav-card-desc">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.page_link(page, label=link_label)

    st.markdown(
        """
        <div style="background:linear-gradient(135deg,rgba(59,130,246,0.07),rgba(139,92,246,0.05));
                    border:1px solid rgba(59,130,246,0.18);border-radius:12px;
                    padding:1.1rem 1.5rem;margin:0.5rem 0 1.5rem;animation:fadeInUp 0.5s ease both">
            <div style="color:#60a5fa;font-size:0.68rem;font-weight:700;
                        letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.5rem">
                Quick Start Guide
            </div>
            <div style="color:#94a3b8;font-size:0.9rem;line-height:1.8">
                1. Open <strong style="color:#e2e8f0">Assessment</strong>
                &nbsp;→&nbsp; 2. Select a <strong style="color:#e2e8f0">Sample Dataset</strong>
                &nbsp;→&nbsp; 3. Click <strong style="color:#e2e8f0">Load Dataset</strong>
                &nbsp;→&nbsp; 4. Click <strong style="color:#e2e8f0">Run Assessment</strong>
                &nbsp;→&nbsp; 5. Explore the <strong style="color:#e2e8f0">Executive Dashboard</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # All 6 platform modules teaser
    section_header("Full Platform", "Six integrated modules — unlocked after first assessment")
    row1 = st.columns(3)
    row2 = st.columns(3)
    for idx, (icon, title, desc, _page) in enumerate(_NAV):
        col   = row1[idx] if idx < 3 else row2[idx - 3]
        delay = f"{(idx % 3) * 0.08:.2f}s"
        with col:
            st.markdown(
                f"""
                <div class="nav-card" style="animation-delay:{delay}">
                    <div class="nav-card-icon">{icon}</div>
                    <div class="nav-card-title">{title}</div>
                    <div class="nav-card-desc">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
