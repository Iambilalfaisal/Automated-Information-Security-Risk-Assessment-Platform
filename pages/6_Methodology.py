"""
6_Methodology.py — Academic methodology page: frameworks, formulas, architecture, references.
"""

import streamlit as st

from streamlit_lib.session import get_session_id, init_session
from streamlit_lib.style import apply_theme, page_header, section_header, sidebar_status

st.set_page_config(page_title="Methodology", page_icon="📖", layout="wide")
init_session()
apply_theme()
sidebar_status(get_session_id())

page_header(
    "Methodology & Framework",
    "Theoretical foundation, quantitative formulas, system design and academic references.",
)

# ── 1. Platform Overview ───────────────────────────────────────────────────────
section_header("1. Platform Overview")

st.markdown(
    """
    <div style="background:#1e293b;border:1px solid #2d3f55;border-radius:12px;
                padding:1.4rem 1.6rem;margin-bottom:1rem">
        <p style="color:#94a3b8;font-size:0.9rem;line-height:1.8;margin:0">
            The <strong style="color:#e2e8f0">Automated Information Security Risk Assessment Platform</strong>
            is a capstone project implementing a quantitative IS risk assessment pipeline aligned with
            three complementary international standards:
            <strong style="color:#60a5fa">NIST SP 800-30 Rev. 1</strong>,
            the <strong style="color:#60a5fa">AssessITS</strong> methodology
            (Rahman et al., 2024), and
            <strong style="color:#60a5fa">ISO/IEC 27001:2022</strong>.
        </p>
        <p style="color:#94a3b8;font-size:0.9rem;line-height:1.8;margin:0.8rem 0 0 0">
            The platform accepts an organisation's asset inventory and threat catalogue,
            computes monetary risk metrics (SLE, ALE) and the AssessITS Risk Impact Rating,
            enriches findings with live CVE data from the NVD, generates AI-assisted NIST control
            recommendations via Claude, and produces downloadable PDF risk reports.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── 2. Framework Alignment ─────────────────────────────────────────────────────
section_header("2. Risk Framework Alignment")

c1, c2, c3 = st.columns(3)
_MC = "background:#1e293b;border:1px solid #2d3f55;border-radius:12px;padding:1.4rem 1.5rem"
_MT = "color:#60a5fa;font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.5rem"
_MB = "color:#94a3b8;font-size:0.84rem;line-height:1.7"

with c1:
    st.markdown(
        f"""
        <div style="{_MC}">
            <div style="font-size:1.8rem;margin-bottom:0.6rem">🏛️</div>
            <div style="{_MT}">NIST SP 800-30 Rev. 1</div>
            <div style="{_MB}">
                Provides the overarching risk management process: threat identification,
                vulnerability assessment, likelihood and impact analysis, and risk determination.
                Controls from the NIST SP 800-53 catalogue are used for compliance tracking
                (RA-1 through CP-2).
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        f"""
        <div style="{_MC}">
            <div style="font-size:1.8rem;margin-bottom:0.6rem">📐</div>
            <div style="{_MT}">AssessITS (Rahman et al., 2024)</div>
            <div style="{_MB}">
                Defines the quantitative scoring model. Assets are scored 1–5, threats
                are classified by level and vulnerability, producing a
                <strong style="color:#e2e8f0">Risk Impact Rating (1–250)</strong> that maps
                directly to Low / Medium / High / Critical criticality bands.
                Source: arXiv:2410.01750.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        f"""
        <div style="{_MC}">
            <div style="font-size:1.8rem;margin-bottom:0.6rem">📋</div>
            <div style="{_MT}">ISO/IEC 27001:2022</div>
            <div style="{_MB}">
                Provides the information security management system (ISMS) context.
                Risk treatment options — Mitigate, Accept, Transfer, Avoid — align with
                ISO 27001 Clause 6.1.3, and the compliance checklist tracks ISMS control
                implementation status.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── 3. Quantitative Formulas ───────────────────────────────────────────────────
section_header("3. Quantitative Risk Formulas")

st.markdown(
    "<p style='color:#475569;font-size:0.88rem;margin-bottom:0.75rem'>"
    "All formulas are implemented verbatim in "
    "<code style='color:#60a5fa;background:#0f172a;padding:0.1rem 0.3rem;"
    "border-radius:4px'>backend/modules/risk_engine.py</code>.</p>",
    unsafe_allow_html=True,
)

# SLE
st.markdown(
    "<div class='sec-header' style='margin-top:1.2rem'><h3>Single Loss Expectancy (SLE)</h3>"
    "<p>NIST SP 800-30 — monetary loss per incident</p></div>",
    unsafe_allow_html=True,
)
st.latex(r"SLE = \text{Asset Value}_{USD} \times \text{Exposure Factor}")
st.markdown(
    "<p style='color:#64748b;font-size:0.83rem;margin-top:0.3rem'>"
    "Exposure Factor ∈ [0, 1] — fraction of asset value lost in a single incident.</p>",
    unsafe_allow_html=True,
)

# ALE
st.markdown(
    "<div class='sec-header'><h3>Annualised Loss Expectancy (ALE)</h3>"
    "<p>NIST SP 800-30 — expected annual monetary loss</p></div>",
    unsafe_allow_html=True,
)
st.latex(r"ALE = SLE \times ARO")
st.markdown(
    "<p style='color:#64748b;font-size:0.83rem;margin-top:0.3rem'>"
    "ARO = Annualised Rate of Occurrence (e.g. 0.5 = once every 2 years).</p>",
    unsafe_allow_html=True,
)

# Risk Score
st.markdown(
    "<div class='sec-header'><h3>Composite Risk Score</h3>"
    "<p>AssessITS — dimensionless risk indicator</p></div>",
    unsafe_allow_html=True,
)
st.latex(r"R = (P \times V) - M + U")
st.markdown(
    "<p style='color:#64748b;font-size:0.83rem;margin-top:0.3rem'>"
    "P = Threat probability [0,1] &nbsp;·&nbsp; "
    "V = Vulnerability score [1,5] &nbsp;·&nbsp; "
    "M = Mitigation effectiveness [0,1] &nbsp;·&nbsp; "
    "U = Uncertainty [0,1].</p>",
    unsafe_allow_html=True,
)

# Threat Value
st.markdown(
    "<div class='sec-header'><h3>Threat Value</h3>"
    "<p>AssessITS — combined threat and vulnerability score</p></div>",
    unsafe_allow_html=True,
)
st.latex(r"TV = \text{Threat Level} + \text{Vulnerability Level}, \quad TV \in [2,\,10]")

# Asset Value Scale
st.markdown(
    "<div class='sec-header'><h3>Asset Value Normalisation</h3>"
    "<p>Maps USD monetary value to the AssessITS 1–5 scale</p></div>",
    unsafe_allow_html=True,
)
st.latex(
    r"A_s = 1.0 + \frac{\min(\text{Value}_{USD},\; 10^6)}{10^6} \times 4.0, "
    r"\quad A_s \in [1,\,5]"
)

# Risk Impact Rating
st.markdown(
    "<div class='sec-header'><h3>Risk Impact Rating (RIR)</h3>"
    "<p>AssessITS — primary risk score on the 1–250 band</p></div>",
    unsafe_allow_html=True,
)
st.latex(r"\text{RIR} = A_s \times TV \times L_s")
st.markdown(
    "<p style='color:#64748b;font-size:0.83rem;margin-top:0.3rem'>"
    "L_s = P × 5 (maps probability to the 0–5 likelihood scale) &nbsp;·&nbsp; "
    "RIR ∈ [1, 250].</p>",
    unsafe_allow_html=True,
)

# CBA
st.markdown(
    "<div class='sec-header'><h3>Cost-Benefit Analysis (CBA)</h3>"
    "<p>Determines whether a control is economically justified</p></div>",
    unsafe_allow_html=True,
)
st.latex(r"CBA = ALE_{before} - ALE_{after} - C_{control}")
st.markdown(
    "<p style='color:#64748b;font-size:0.83rem;margin-top:0.3rem'>"
    "A control is recommended when CBA &gt; 0. "
    "The platform uses ALE_after = 0.7 × ALE_before and C_control = 0.1 × ALE_before as defaults.</p>",
    unsafe_allow_html=True,
)

# ── 4. Criticality Bands ───────────────────────────────────────────────────────
section_header("4. Risk Criticality Bands")

st.markdown(
    """
    <p style="color:#94a3b8;font-size:0.88rem;margin-bottom:0.75rem">
    Criticality is derived from the Risk Impact Rating using the AssessITS scale
    (Rahman et al., 2024, Table 3):
    </p>
    """,
    unsafe_allow_html=True,
)

bands = [
    ("1 – 45",   "Low",      "#22c55e", "rgba(20,83,45,0.3)"),
    ("46 – 99",  "Medium",   "#eab308", "rgba(113,63,18,0.3)"),
    ("100 – 199","High",     "#f97316", "rgba(124,45,18,0.3)"),
    ("200 – 250","Critical", "#ef4444", "rgba(127,29,29,0.35)"),
]
bc1, bc2, bc3, bc4 = st.columns(4)
for col, (rng, label, color, bg) in zip([bc1, bc2, bc3, bc4], bands):
    with col:
        st.markdown(
            f"""
            <div style="background:{bg};border:1px solid {color};border-radius:10px;
                        padding:1rem 1.2rem;text-align:center">
                <div style="color:{color};font-size:1.5rem;font-weight:800">{label}</div>
                <div style="color:#94a3b8;font-size:0.8rem;margin-top:0.25rem">RIR {rng}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ── 5. System Architecture ─────────────────────────────────────────────────────
section_header("5. System Architecture")

st.markdown(
    """
    <div style="background:#1e293b;border:1px solid #2d3f55;border-radius:12px;
                padding:1.4rem 1.6rem">
        <div style="color:#94a3b8;font-size:0.88rem;line-height:1.85">
            <strong style="color:#e2e8f0">Frontend:</strong>
            Streamlit multi-page application (app.py + pages/) with Plotly charts
            and a custom animated dark-theme CSS layer.
            <br><br>
            <strong style="color:#e2e8f0">Backend:</strong>
            Pure Python modules under backend/ — risk_engine.py (formulas),
            cve_fetcher.py (NVD API v2.0), llm_advisor.py (Claude API), and
            report_generator.py (ReportLab PDF).
            <br><br>
            <strong style="color:#e2e8f0">Data Layer:</strong>
            SQLite via a parameterised DAL (database/models.py). Tables: assets, threats,
            assessments (JSON blob), compliance_status, notifications, treatment_plans.
            <br><br>
            <strong style="color:#e2e8f0">External APIs:</strong>
            NIST NVD CVE API v2.0 (vulnerability enrichment) and Anthropic Claude API
            (AI control recommendations). Both degrade gracefully to mock/rule-based
            fallbacks when unavailable.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

# Data flow diagram
st.markdown(
    """
    <div style="background:#0f172a;border:1px solid #1e293b;border-radius:10px;
                padding:1.2rem 1.5rem;font-family:monospace;font-size:0.82rem;
                color:#64748b;line-height:2">
        <span style="color:#60a5fa">User Input</span>
        (assets + threats + CSV)
        <br>
        &nbsp;&nbsp;&nbsp;&nbsp;&darr;
        <br>
        <span style="color:#60a5fa">Risk Engine</span>
        &nbsp;→ SLE / ALE / Risk Score / Risk Impact Rating / CBA
        <br>
        &nbsp;&nbsp;&nbsp;&nbsp;&darr; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&darr;
        <br>
        <span style="color:#60a5fa">NVD CVE API</span>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        <span style="color:#a78bfa">Claude API</span>
        (control recommendations)
        <br>
        &nbsp;&nbsp;&nbsp;&nbsp;&darr; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&darr;
        <br>
        <span style="color:#60a5fa">SQLite</span>
        (persist results, notifications, compliance, treatment plans)
        <br>
        &nbsp;&nbsp;&nbsp;&nbsp;&darr;
        <br>
        <span style="color:#60a5fa">Dashboard / Reports</span>
        &nbsp;→ PDF (ReportLab) + Plotly charts + Streamlit UI
    </div>
    """,
    unsafe_allow_html=True,
)

# ── 6. Threat Categories ───────────────────────────────────────────────────────
section_header("6. NIST SP 800-30 Threat Categories")

categories = [
    ("Adversarial",      "Deliberate attacks by individuals, groups, or nation-states with intent to exploit."),
    ("Natural",          "Acts of nature — floods, earthquakes, fires — that damage infrastructure."),
    ("Structural",       "Failures of equipment, software, or environmental controls within the facility."),
    ("Environmental",    "External environmental hazards such as power outages or HVAC failures."),
    ("Accidental",       "Unintentional errors by authorised users — misconfigurations, data entry mistakes."),
    ("Technical Failure","Hardware or software malfunctions not caused by external parties."),
]
tc1, tc2 = st.columns(2)
for i, (cat, desc) in enumerate(categories):
    col = tc1 if i % 2 == 0 else tc2
    with col:
        st.markdown(
            f"""
            <div style="background:#1e293b;border:1px solid #2d3f55;border-radius:8px;
                        padding:0.75rem 1rem;margin:0.3rem 0">
                <span style="color:#60a5fa;font-weight:700;font-size:0.83rem">{cat}</span>
                <div style="color:#64748b;font-size:0.81rem;margin-top:0.2rem;line-height:1.55">
                    {desc}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ── 7. References ──────────────────────────────────────────────────────────────
section_header("7. References")

refs = [
    (
        "Rahman, M. A. et al. (2024)",
        "AssessITS: Integrating IT and Operational Technology for Comprehensive Cybersecurity "
        "Risk Assessment. arXiv:2410.01750",
        "https://arxiv.org/abs/2410.01750",
    ),
    (
        "NIST (2012)",
        "Guide for Conducting Risk Assessments. NIST Special Publication 800-30 Revision 1. "
        "National Institute of Standards and Technology, Gaithersburg, MD.",
        "https://csrc.nist.gov/publications/detail/sp/800-30/rev-1/final",
    ),
    (
        "ISO/IEC (2022)",
        "Information security, cybersecurity and privacy protection — Information security "
        "management systems — Requirements. ISO/IEC 27001:2022.",
        "https://www.iso.org/standard/82875.html",
    ),
    (
        "NIST NVD (2024)",
        "National Vulnerability Database — CVE API v2.0. National Institute of Standards "
        "and Technology.",
        "https://nvd.nist.gov/developers/vulnerabilities",
    ),
    (
        "Anthropic (2024)",
        "Claude API — Large Language Model for security control recommendations. "
        "Model: claude-haiku-4-5.",
        "https://docs.anthropic.com",
    ),
]

for author, text, url in refs:
    st.markdown(
        f"""
        <div style="background:#1e293b;border:1px solid #2d3f55;border-radius:8px;
                    padding:0.7rem 1rem;margin:0.35rem 0;display:flex;gap:1rem;align-items:flex-start">
            <div style="color:#60a5fa;font-size:0.78rem;font-weight:700;
                        white-space:nowrap;min-width:160px;margin-top:0.1rem">
                {author}
            </div>
            <div>
                <div style="color:#94a3b8;font-size:0.83rem;line-height:1.55">{text}</div>
                <a href="{url}" target="_blank"
                   style="color:#475569;font-size:0.73rem;text-decoration:none">{url}</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
