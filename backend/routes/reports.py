"""
reports.py — PDF report download endpoints.
"""

import io

from flask import Blueprint, send_file

from constants import NIST_CONTROLS
from database import models
from modules.report_generator import (
    generate_cba_pdf,
    generate_compliance_pdf,
    generate_risk_register_pdf,
)
from utils import api_response, get_session_id, rate_limit

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


def _get_register_and_org(session_id: str):
    assessment = models.get_latest_assessment(session_id)
    if not assessment or not assessment.get("results"):
        return None, None, "No assessment results. Run assessment first."
    results = assessment["results"]
    register = results.get("risk_register", [])
    org = results.get("summary", {}).get("org_name", "Organisation")
    llm = results.get("llm_recommendations", {})
    summary_text = ""
    if llm.get("recommendations"):
        summary_text = "Top recommended controls: " + ", ".join(
            r.get("control_id", "") for r in llm["recommendations"][:5]
        )
    return register, org, summary_text


def _compliance_score(session_id: str) -> tuple[list[dict], float]:
    stored = {c["control_id"]: c for c in models.get_compliance(session_id)}
    items = []
    implemented = 0
    for cid, cname in NIST_CONTROLS:
        row = stored.get(cid, {"control_id": cid, "control_name": cname, "status": "not_implemented", "notes": ""})
        if row.get("control_name") != cname:
            row["control_name"] = cname
        items.append(row)
        if row.get("status") == "implemented":
            implemented += 1
        elif row.get("status") == "partial":
            implemented += 0.5
    score = (implemented / len(NIST_CONTROLS)) * 100 if NIST_CONTROLS else 0
    return items, score


@reports_bp.route("/risk-register", methods=["GET"])
@rate_limit()
def risk_register_pdf():
    """Download Risk Register PDF."""
    try:
        session_id = get_session_id()
        register, org, summary = _get_register_and_org(session_id)
        if register is None:
            return api_response(False, None, summary, 404)
        pdf_bytes = generate_risk_register_pdf(register, org, summary)
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name="risk_register.pdf",
        )
    except Exception as e:
        return api_response(False, None, str(e), 500)


@reports_bp.route("/cba", methods=["GET"])
@rate_limit()
def cba_pdf():
    """Download CBA report PDF."""
    try:
        session_id = get_session_id()
        register, org, err = _get_register_and_org(session_id)
        if register is None:
            return api_response(False, None, err, 404)
        pdf_bytes = generate_cba_pdf(register, org)
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name="cba_report.pdf",
        )
    except Exception as e:
        return api_response(False, None, str(e), 500)


@reports_bp.route("/compliance", methods=["GET"])
@rate_limit()
def compliance_pdf():
    """Download NIST compliance checklist PDF."""
    try:
        session_id = get_session_id()
        items, score = _compliance_score(session_id)
        org = "Organisation"
        assessment = models.get_latest_assessment(session_id)
        if assessment and assessment.get("results"):
            org = assessment["results"].get("summary", {}).get("org_name", org)
        pdf_bytes = generate_compliance_pdf(items, org, score)
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name="compliance_report.pdf",
        )
    except Exception as e:
        return api_response(False, None, str(e), 500)
