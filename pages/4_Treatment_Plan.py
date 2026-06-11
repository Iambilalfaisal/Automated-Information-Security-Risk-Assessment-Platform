"""
4_Treatment_Plan.py — Risk treatment strategy and remediation tracker.

For each risk in the register the user can assign:
  Strategy  : Mitigate / Accept / Transfer / Avoid
  Owner     : free-text responsible party
  Due Date  : free-text target date
  Status    : Pending / In Progress / Completed / Accepted
  Notes     : free-text notes
"""

import pandas as pd
import streamlit as st

from streamlit_lib.paths import ensure_backend_path
from streamlit_lib.session import get_session_id, init_session
from streamlit_lib.style import apply_theme, page_header, section_header, sidebar_status, stat_card

ensure_backend_path()

from database import models  # noqa: E402
from streamlit_lib.charts import plot_treatment_status, plot_strategy_breakdown  # noqa: E402

st.set_page_config(page_title="Treatment Plan", page_icon="🛠️", layout="wide")
init_session()
apply_theme()
session_id = get_session_id()
sidebar_status(session_id)

page_header(
    "Treatment Plan",
    "Assign risk treatment strategies, owners and deadlines for each identified risk.",
)

# ── Guard ──────────────────────────────────────────────────────────────────────
assessment = models.get_latest_assessment(session_id)
if not assessment or not assessment.get("results"):
    st.warning("No assessment found. Run an assessment first.")
    st.page_link("pages/1_Assessment.py", label="Go to Assessment →")
    st.stop()

register       = assessment["results"].get("risk_register", [])
existing_plans = {
    f"{p['asset_name']}|{p['threat_name']}": p
    for p in models.get_treatment_plans(session_id)
}

# ── Summary KPIs ───────────────────────────────────────────────────────────────
plans_list = list(existing_plans.values())
completed  = sum(1 for p in plans_list if p.get("status") == "Completed")
in_prog    = sum(1 for p in plans_list if p.get("status") == "In Progress")
mitigate   = sum(1 for p in plans_list if p.get("strategy") == "Mitigate")

m1, m2, m3, m4 = st.columns(4)
with m1:
    stat_card("Total Risks", str(len(register)), "in register")
with m2:
    stat_card("Completed", str(completed), "fully remediated", accent="#22c55e")
with m3:
    stat_card("In Progress", str(in_prog), "being addressed", accent="#3b82f6")
with m4:
    stat_card("Mitigate Strategy", str(mitigate), "control-based treatment", accent="#a78bfa")

# Status donut + strategy breakdown (only if plans exist)
if plans_list:
    st.markdown("<div style='margin-top:0.5rem'></div>", unsafe_allow_html=True)
    dc1, dc2 = st.columns(2)
    with dc1:
        plot_treatment_status(plans_list)
    with dc2:
        plot_strategy_breakdown(plans_list)

st.divider()

# ── Inline editor ──────────────────────────────────────────────────────────────
section_header(
    "Risk Treatment Editor",
    "Edit strategies inline — use the Strategy and Status dropdowns, then click Save",
)
st.caption(
    "Disabled columns (Asset, Threat, Criticality, ALE) are read-only. "
    "Owner, Due Date and Notes are free-text. Click **Save Treatment Plan** to persist."
)

# Build DataFrame merging register with saved plans
rows = []
for r in register:
    key  = f"{r['asset_name']}|{r['threat_name']}"
    plan = existing_plans.get(key, {})
    rows.append({
        "Asset":       r["asset_name"],
        "Threat":      r["threat_name"],
        "Criticality": r.get("risk_criticality", "Low"),
        "ALE ($)":     round(float(r.get("ale", 0)), 2),
        "Strategy":    plan.get("strategy", "Mitigate"),
        "Owner":       plan.get("owner", ""),
        "Due Date":    plan.get("due_date", ""),
        "Status":      plan.get("status", "Pending"),
        "Notes":       plan.get("notes", ""),
    })

df = pd.DataFrame(rows) if rows else pd.DataFrame(
    columns=["Asset", "Threat", "Criticality", "ALE ($)",
             "Strategy", "Owner", "Due Date", "Status", "Notes"]
)

edited_df = st.data_editor(
    df,
    column_config={
        "Asset":       st.column_config.TextColumn("Asset",       disabled=True),
        "Threat":      st.column_config.TextColumn("Threat",      disabled=True),
        "Criticality": st.column_config.TextColumn("Criticality", disabled=True),
        "ALE ($)":     st.column_config.NumberColumn("ALE ($)",   format="$%.2f", disabled=True),
        "Strategy":    st.column_config.SelectboxColumn(
            "Strategy",
            options=["Mitigate", "Accept", "Transfer", "Avoid"],
            required=True,
        ),
        "Status":      st.column_config.SelectboxColumn(
            "Status",
            options=["Pending", "In Progress", "Completed", "Accepted"],
            required=True,
        ),
        "Owner":    st.column_config.TextColumn("Owner",    max_chars=120),
        "Due Date": st.column_config.TextColumn("Due Date", max_chars=30,
                                                help="e.g. 2025-12-31 or Q4 2025"),
        "Notes":    st.column_config.TextColumn("Notes",    max_chars=500),
    },
    hide_index=True,
    use_container_width=True,
    num_rows="fixed",
    key="treatment_editor",
)

# Action buttons
bc1, bc2, bc3 = st.columns([1, 1, 3])
with bc1:
    save_btn = st.button("Save Treatment Plan", type="primary", use_container_width=True)
with bc2:
    csv_data = edited_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇ Export CSV",
        data=csv_data,
        file_name="treatment_plan.csv",
        mime="text/csv",
        use_container_width=True,
    )

if save_btn:
    saved = 0
    for _, row in edited_df.iterrows():
        models.upsert_treatment_plan(
            session_id=session_id,
            asset_name=str(row["Asset"]),
            threat_name=str(row["Threat"]),
            strategy=str(row["Strategy"]),
            owner=str(row.get("Owner") or ""),
            due_date=str(row.get("Due Date") or ""),
            status=str(row["Status"]),
            notes=str(row.get("Notes") or ""),
        )
        saved += 1
    st.success(f"Saved {saved} treatment plan entries.")
    st.rerun()

st.divider()
_tc1, _tc2 = st.columns(2)
with _tc1:
    st.page_link("pages/2_Results.py", label="📊 Back to Results →")
with _tc2:
    st.page_link("pages/5_History.py", label="📈 View History →")
