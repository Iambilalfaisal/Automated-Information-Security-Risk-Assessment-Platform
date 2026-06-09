"""
5_History.py — Assessment history with ALE trend and per-assessment detail.
"""

import streamlit as st

from streamlit_lib.paths import ensure_backend_path
from streamlit_lib.session import get_session_id, init_session
from streamlit_lib.style import apply_theme, page_header, risk_table, section_header, stat_card

ensure_backend_path()

from database import models  # noqa: E402
from streamlit_lib.charts import plot_ale_trend  # noqa: E402

st.set_page_config(page_title="History", page_icon="📈", layout="wide")
init_session()
apply_theme()
session_id = get_session_id()

page_header(
    "Assessment History",
    "All assessment runs for this session — ALE trend and per-assessment risk registers.",
)

all_assessments = models.get_all_assessments(session_id)

if not all_assessments:
    st.warning("No assessments found. Run an assessment first to build history.")
    st.page_link("pages/1_Assessment.py", label="Go to Assessment →")
    st.stop()

# ── Summary KPIs ───────────────────────────────────────────────────────────────
latest_summary = all_assessments[0].get("summary", {})
latest_ale     = latest_summary.get("total_ale", 0)

m1, m2, m3 = st.columns(3)
with m1:
    stat_card("Total Runs", str(len(all_assessments)), "assessment history")
with m2:
    stat_card("Latest ALE", f"${latest_ale:,.0f}", "most recent run", accent="#f87171")
with m3:
    if len(all_assessments) > 1:
        prev_ale  = (all_assessments[1].get("summary") or {}).get("total_ale", 0)
        delta     = latest_ale - prev_ale
        direction = "↑" if delta >= 0 else "↓"
        accent    = "#f87171" if delta >= 0 else "#22c55e"
        stat_card(
            "vs Previous Run",
            f"{direction} ${abs(delta):,.0f}",
            "ALE movement",
            accent=accent,
        )
    else:
        stat_card("Assessments", "1", "first run — no trend yet")

st.divider()

# ── ALE trend ─────────────────────────────────────────────────────────────────
plot_ale_trend(all_assessments)

st.divider()

# ── Per-assessment expanders ──────────────────────────────────────────────────
section_header(
    "Assessment Runs",
    "Expand any run to view its full risk register — newest first",
)

total = len(all_assessments)
for i, a in enumerate(all_assessments):
    summary       = a.get("summary") or {}
    org           = summary.get("org_name", "—")
    total_ale     = summary.get("total_ale", 0)
    total_assets  = summary.get("total_assets", 0)
    total_threats = summary.get("total_threats", 0)
    date_str      = (a.get("created_at") or "")[:16]
    run_num       = total - i
    label         = (
        f"Run #{run_num}  —  {date_str}  —  {org}  —  "
        f"ALE: ${total_ale:,.0f}"
    )

    with st.expander(label, expanded=(i == 0)):
        sm1, sm2, sm3 = st.columns(3)
        with sm1:
            stat_card("Total ALE", f"${total_ale:,.0f}", "annual loss expectancy", accent="#f87171")
        with sm2:
            stat_card("Assets", str(total_assets), "in scope")
        with sm3:
            stat_card("Threats", str(total_threats), "mapped")

        register = (a.get("results") or {}).get("risk_register", [])
        if register:
            section_header(f"Risk Register — Top {min(10, len(register))} of {len(register)} Risks")
            risk_table(register[:10])
            if len(register) > 10:
                st.caption(
                    f"Showing 10 of {len(register)} risks. "
                    "Open **Results** for the full sortable register."
                )
        else:
            st.info("No risk register data stored for this run.")

        # AI recommendations summary if present
        llm = (a.get("results") or {}).get("llm_recommendations", {})
        recs = llm.get("recommendations", []) if isinstance(llm, dict) else []
        if recs:
            st.markdown(
                f"""
                <div style="background:#1e293b;border:1px solid #2d3f55;border-left:3px solid #818cf8;
                            border-radius:8px;padding:0.7rem 1rem;margin-top:0.75rem">
                    <span style="color:#a5b4fc;font-size:0.72rem;font-weight:700;
                                 text-transform:uppercase;letter-spacing:0.08em">
                        AI Recommendations ({len(recs)})
                    </span>
                    <div style="color:#94a3b8;font-size:0.83rem;margin-top:0.3rem">
                        {", ".join(r.get("control_id", "") for r in recs[:5])}
                        {"…" if len(recs) > 5 else ""}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
