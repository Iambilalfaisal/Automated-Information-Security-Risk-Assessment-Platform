"""
compliance.py — NIST 800-30 compliance checklist API.
"""

from flask import Blueprint, request

from database import models
from routes.reports import NIST_CONTROLS
from utils import api_response, escape_output, get_session_id, rate_limit

compliance_bp = Blueprint("compliance", __name__, url_prefix="/api/compliance")


@compliance_bp.route("", methods=["GET"])
@rate_limit()
def list_compliance():
    """Get full checklist with stored statuses and compliance score."""
    try:
        session_id = get_session_id()
        stored = {c["control_id"]: c for c in models.get_compliance(session_id)}
        items = []
        implemented = 0
        for cid, cname in NIST_CONTROLS:
            row = stored.get(
                cid,
                {
                    "control_id": cid,
                    "control_name": cname,
                    "status": "not_implemented",
                    "notes": "",
                },
            )
            row["control_name"] = cname
            items.append(row)
            st = row.get("status")
            if st == "implemented":
                implemented += 1
            elif st == "partial":
                implemented += 0.5
        score = round((implemented / len(NIST_CONTROLS)) * 100, 1) if NIST_CONTROLS else 0
        gaps = [i for i in items if i.get("status") != "implemented"]
        return api_response(
            True,
            escape_output({"controls": items, "score_percent": score, "gaps": gaps}),
            None,
        )
    except Exception as e:
        return api_response(False, None, str(e), 500)


@compliance_bp.route("", methods=["POST"])
@rate_limit()
def update_compliance():
    """Update a single control status."""
    try:
        session_id = get_session_id()
        body = request.get_json() or {}
        required = ["control_id", "control_name", "status"]
        for field in required:
            if field not in body:
                return api_response(False, None, f"Missing field: {field}", 400)
        if body["status"] not in ("implemented", "partial", "not_implemented"):
            return api_response(False, None, "Invalid status", 400)
        row = models.upsert_compliance(
            session_id,
            body["control_id"],
            body["control_name"],
            body["status"],
            body.get("notes", ""),
        )
        return api_response(True, escape_output(row), None)
    except Exception as e:
        return api_response(False, None, str(e), 500)
