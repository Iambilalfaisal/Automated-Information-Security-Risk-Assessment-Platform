"""
2_Results.py — Animated risk dashboard, compliance, and PDF downloads.
"""

import streamlit as st

from streamlit_lib.paths import ensure_backend_path

ensure_backend_path()

from constants import NIST_CONTROLS  # noqa: E402
from database import models  # noqa: E402
from modules.report_generator import (  # noqa: E402
    generate_cba_pdf,
    generate_compliance_pdf,
    generate_risk_register_pdf,
)
from streamlit_lib.charts import (  # noqa: E402
    plot_ale_by_asset,
    plot_compliance_gauge,
    plot_criticality_pie,
    plot_risk_heatmap,
    plot_top_risks_bar,
)
from streamlit_lib.services import get_compliance_data  # noqa: E402
from streamlit_lib.session import get_session_id, init_session  # noqa: E402
from streamlit_lib.style import (  # noqa: E402
    apply_theme,
    control_cards,
    cve_alerts,
    page_header,
    risk_table,
    section_header,
    stat_card,
)

st.set_page_config(page_title="Results", page_icon="📊", layout="wide")
init_session()
apply_theme()
session_id = get_session_id()

# ── Page header ───────────────────────────────────────────────────────────────
page_header(
    "Results & Reports",
    "Risk dashboard, compliance checklist, and downloadable PDF reports.",
)

# ── Guard: no assessment yet ──────────────────────────────────────────────────
assessment = models.get_latest_assessment(session_id)
if not assessment or not assessment.get("results"):
    st.warning("No assessment found. Go to **Assessment**, load demo data, and run an assessment.")
    st.page_link("pages/1_Assessment.py", label="Go to Assessment →")
    st.stop()

results  = assessment["results"]
register = results.get("risk_register", [])
summary  = results.get("summary", {})
org_name = summary.get("org_name", "Organisation")
llm      = results.get("llm_recommendations", {})

# ── CVE alert cards ───────────────────────────────────────────────────────────
notifications = models.get_notifications(session_id, unread_only=False)
cve_alerts(notifications)

# ── Summary stat cards ────────────────────────────────────────────────────────
highest = summary.get("highest_risk") or {}
m1, m2, m3, m4 = st.columns(4)
with m1:
    stat_card("Total Assets", str(summary.get("total_assets", 0)), "in scope")
with m2:
    stat_card("Total Threats", str(summary.get("total_threats", 0)), "mapped")
with m3:
    stat_card(
        "Total ALE",
        f"${summary.get('total_ale', 0):,.0f}",
        "annual loss expectancy",
        accent="#f87171",
    )
with m4:
    name = highest.get("threat_name", "—")
    display = (name[:17] + "…") if len(name) > 17 else name
    stat_card(
        "Highest Risk",
        display,
        f"Impact: {highest.get('risk_impact_rating', '—')}",
        accent="#fb923c",
    )

st.markdown("<div style='margin-top:0.75rem'></div>", unsafe_allow_html=True)
st.divider()

# ── Charts row 1: donut + bar ─────────────────────────────────────────────────
c1, c2 = st.columns(2)
with c1:
    plot_criticality_pie(register)
with c2:
    plot_top_risks_bar(register)

# ── Charts row 2: heatmap + ALE ───────────────────────────────────────────────
plot_risk_heatmap(register)
plot_ale_by_asset(register)

# ── Risk register ─────────────────────────────────────────────────────────────
section_header("Risk Register", "Full sortable register of all identified risks")

fc1, fc2 = st.columns([3, 1])
with fc1:
    filter_text = st.text_input("Filter by asset or threat name", "", label_visibility="collapsed",
                                placeholder="Filter by asset or threat name…")
with fc2:
    sort_label = st.selectbox(
        "Sort by",
        ["Impact Rating ↓", "ALE ↓", "Risk Score ↓"],
        key="sort_col",
        label_visibility="collapsed",
    )

_SORT_KEY = {
    "Impact Rating ↓": "risk_impact_rating",
    "ALE ↓":           "ale",
    "Risk Score ↓":    "risk_score",
}

filtered = register
if filter_text:
    ft = filter_text.lower()
    filtered = [
        r for r in register
        if ft in (r.get("asset_name") or "").lower()
        or ft in (r.get("threat_name") or "").lower()
    ]

filtered = sorted(filtered, key=lambda r: r.get(_SORT_KEY[sort_label], 0), reverse=True)
risk_table(filtered)

# ── Control recommendations ───────────────────────────────────────────────────
recs = llm.get("recommendations", [])
if recs:
    control_cards(recs, source=llm.get("source", ""), framework=llm.get("framework", ""))

st.divider()

# ── PDF downloads ─────────────────────────────────────────────────────────────
section_header("Download Reports", "PDF exports for risk register, CBA analysis, and compliance")

summary_text = ""
if recs:
    summary_text = "Recommended controls: " + ", ".join(r.get("control_id", "") for r in recs[:5])

d1, d2, d3 = st.columns(3)
with d1:
    pdf_reg = generate_risk_register_pdf(register, org_name, summary_text)
    st.download_button(
        "⬇ Risk Register PDF",
        data=pdf_reg,
        file_name="risk_register.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
with d2:
    pdf_cba = generate_cba_pdf(register, org_name)
    st.download_button(
        "⬇ CBA Report PDF",
        data=pdf_cba,
        file_name="cba_report.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
with d3:
    comp     = get_compliance_data(session_id)
    pdf_comp = generate_compliance_pdf(comp["controls"], org_name, comp["score_percent"])
    st.download_button(
        "⬇ Compliance PDF",
        data=pdf_comp,
        file_name="compliance_report.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

st.divider()

# ── Compliance ────────────────────────────────────────────────────────────────
section_header("NIST SP 800-30 Compliance", "Review and update control implementation status")

comp_data = get_compliance_data(session_id)
score     = comp_data["score_percent"]
gaps      = len(comp_data["gaps"])

g1, g2 = st.columns([1, 2])
with g1:
    plot_compliance_gauge(score)
with g2:
    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    st.progress(score / 100.0, text=f"Compliance score: **{score}%**")
    st.markdown(
        f"""
        <div style="display:flex;gap:1.5rem;margin-top:0.75rem">
            <div style="background:#1e293b;border:1px solid #2d3f55;border-radius:10px;
                        padding:0.8rem 1.2rem;flex:1;text-align:center">
                <div style="color:#475569;font-size:0.68rem;text-transform:uppercase;
                            letter-spacing:0.08em;font-weight:700">Implemented</div>
                <div style="color:#22c55e;font-size:1.6rem;font-weight:700">
                    {len(comp_data["controls"]) - gaps}
                </div>
            </div>
            <div style="background:#1e293b;border:1px solid #2d3f55;border-radius:10px;
                        padding:0.8rem 1.2rem;flex:1;text-align:center">
                <div style="color:#475569;font-size:0.68rem;text-transform:uppercase;
                            letter-spacing:0.08em;font-weight:700">Gaps</div>
                <div style="color:#f87171;font-size:1.6rem;font-weight:700">{gaps}</div>
            </div>
            <div style="background:#1e293b;border:1px solid #2d3f55;border-radius:10px;
                        padding:0.8rem 1.2rem;flex:1;text-align:center">
                <div style="color:#475569;font-size:0.68rem;text-transform:uppercase;
                            letter-spacing:0.08em;font-weight:700">Total Controls</div>
                <div style="color:#60a5fa;font-size:1.6rem;font-weight:700">
                    {len(comp_data["controls"])}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='margin-top:1.25rem'></div>", unsafe_allow_html=True)

STATUS_OPTIONS = ["not_implemented", "partial", "implemented"]
STATUS_COLOR   = {"not_implemented": "#f87171", "partial": "#fbbf24", "implemented": "#22c55e"}

for ctrl in comp_data["controls"]:
    cid     = ctrl["control_id"]
    cname   = ctrl["control_name"]
    current = ctrl.get("status", "not_implemented")
    idx     = STATUS_OPTIONS.index(current) if current in STATUS_OPTIONS else 0
    dot_col = STATUS_COLOR.get(current, "#475569")

    cc1, cc2 = st.columns([4, 1])
    with cc1:
        st.markdown(
            f"""
            <div style="padding:0.5rem 0 0.2rem 0">
                <span style="display:inline-block;width:8px;height:8px;border-radius:50%;
                             background:{dot_col};margin-right:0.5rem;margin-bottom:1px"></span>
                <span style="color:#e2e8f0;font-size:0.88rem;font-weight:600">{cid}</span>
                <span style="color:#64748b;font-size:0.85rem"> — {cname}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with cc2:
        new_status = st.selectbox(
            cid,
            STATUS_OPTIONS,
            index=idx,
            format_func=lambda x: x.replace("_", " ").title(),
            key=f"comp_{cid}",
            label_visibility="collapsed",
        )
    if new_status != current:
        models.upsert_compliance(session_id, cid, cname, new_status, ctrl.get("notes", ""))
        st.rerun()
