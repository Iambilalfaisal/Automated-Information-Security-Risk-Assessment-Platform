"""
2_Results.py — Risk dashboard, compliance checklist, and PDF downloads.
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
    plot_criticality_pie,
    plot_risk_heatmap,
    plot_top_risks_bar,
)
from streamlit_lib.services import get_compliance_data  # noqa: E402
from streamlit_lib.session import get_session_id, init_session  # noqa: E402

st.set_page_config(page_title="Results", layout="wide")
init_session()
session_id = get_session_id()

st.title("Results & Reports")

assessment = models.get_latest_assessment(session_id)
if not assessment or not assessment.get("results"):
    st.warning("No assessment found. Go to **Assessment**, load demo data, and run an assessment.")
    st.page_link("pages/1_Assessment.py", label="Go to Assessment →")
    st.stop()

results = assessment["results"]
register = results.get("risk_register", [])
summary = results.get("summary", {})
org_name = summary.get("org_name", "Organisation")
llm = results.get("llm_recommendations", {})

# --- CVE Alerts banner ---
notifications = models.get_notifications(session_id, unread_only=False)
if notifications:
    with st.expander(f"⚠️ CVE Alerts ({len(notifications)})", expanded=True):
        for n in notifications[:10]:
            sev = n.get("severity", "info")
            if sev == "warning":
                st.warning(n["message"])
            elif sev == "error":
                st.error(n["message"])
            else:
                st.info(n["message"])

# --- Summary metrics ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total assets", summary.get("total_assets", 0))
m2.metric("Total threats", summary.get("total_threats", 0))
m3.metric("Total ALE", f"${summary.get('total_ale', 0):,.0f}")
highest = summary.get("highest_risk") or {}
m4.metric(
    "Highest risk",
    highest.get("threat_name", "—")[:20] if highest else "—",
)

st.divider()

# --- Charts ---
c1, c2 = st.columns(2)
with c1:
    plot_criticality_pie(register)
with c2:
    plot_top_risks_bar(register)

plot_risk_heatmap(register)
plot_ale_by_asset(register)

st.subheader("Risk register")

# Filter + sort controls
fc1, fc2 = st.columns([3, 1])
with fc1:
    filter_text = st.text_input("Filter by asset or threat name", "")
with fc2:
    sort_label = st.selectbox(
        "Sort by",
        ["Impact Rating ↓", "ALE ↓", "Risk Score ↓"],
        key="sort_col",
    )

_SORT_KEY = {
    "Impact Rating ↓": "risk_impact_rating",
    "ALE ↓": "ale",
    "Risk Score ↓": "risk_score",
}

filtered = register
if filter_text:
    ft = filter_text.lower()
    filtered = [
        r
        for r in register
        if ft in (r.get("asset_name") or "").lower()
        or ft in (r.get("threat_name") or "").lower()
    ]

filtered = sorted(filtered, key=lambda r: r.get(_SORT_KEY[sort_label], 0), reverse=True)

if filtered:
    import pandas as pd

    CRIT_BG = {
        "Critical": "#fca5a5",
        "High": "#fed7aa",
        "Medium": "#fef08a",
        "Low": "#bbf7d0",
    }

    def _color_criticality(col):
        return [f"background-color: {CRIT_BG.get(v, '')}" for v in col]

    df = pd.DataFrame(
        [
            {
                "Asset": r["asset_name"],
                "Threat": r["threat_name"],
                "SLE": f"${r['sle']:,.0f}",
                "ALE": f"${r['ale']:,.0f}",
                "R Score": r["risk_score"],
                "Impact": r["risk_impact_rating"],
                "Criticality": r["risk_criticality"],
                "CBA Rec.": "Yes" if r.get("control_recommended") else "No",
            }
            for r in filtered
        ]
    )
    st.dataframe(
        df.style.apply(_color_criticality, subset=["Criticality"]),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No rows match the filter.")

# --- LLM recommendations ---
recs = llm.get("recommendations", [])
if recs:
    st.subheader(f"Control recommendations ({llm.get('source', 'unknown')})")
    for rec in recs:
        with st.expander(f"{rec.get('control_id')} — {rec.get('control_name')}"):
            st.write(rec.get("plain_english_explanation", ""))
            st.caption(
                f"Priority {rec.get('implementation_priority')} · "
                f"{rec.get('estimated_cost_range', '')}"
            )

st.divider()

# --- PDF downloads ---
st.subheader("Download reports")
summary_text = ""
if recs:
    summary_text = "Recommended controls: " + ", ".join(
        r.get("control_id", "") for r in recs[:5]
    )

d1, d2, d3 = st.columns(3)
with d1:
    pdf_reg = generate_risk_register_pdf(register, org_name, summary_text)
    st.download_button(
        "Risk Register PDF",
        data=pdf_reg,
        file_name="risk_register.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
with d2:
    pdf_cba = generate_cba_pdf(register, org_name)
    st.download_button(
        "CBA Report PDF",
        data=pdf_cba,
        file_name="cba_report.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
with d3:
    comp = get_compliance_data(session_id)
    pdf_comp = generate_compliance_pdf(comp["controls"], org_name, comp["score_percent"])
    st.download_button(
        "Compliance PDF",
        data=pdf_comp,
        file_name="compliance_report.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

st.divider()

# --- Compliance checklist ---
st.subheader("NIST SP 800-30 compliance checklist")
comp_data = get_compliance_data(session_id)
st.progress(comp_data["score_percent"] / 100.0, text=f"Compliance: {comp_data['score_percent']}%")
st.caption(f"Gaps: {len(comp_data['gaps'])} control(s) not fully implemented.")

STATUS_OPTIONS = ["not_implemented", "partial", "implemented"]

for ctrl in comp_data["controls"]:
    cid = ctrl["control_id"]
    cname = ctrl["control_name"]
    current = ctrl.get("status", "not_implemented")
    idx = STATUS_OPTIONS.index(current) if current in STATUS_OPTIONS else 0
    new_status = st.selectbox(
        f"{cid} — {cname}",
        STATUS_OPTIONS,
        index=idx,
        format_func=lambda x: x.replace("_", " ").title(),
        key=f"comp_{cid}",
    )
    if new_status != current:
        models.upsert_compliance(session_id, cid, cname, new_status, ctrl.get("notes", ""))
        st.rerun()
