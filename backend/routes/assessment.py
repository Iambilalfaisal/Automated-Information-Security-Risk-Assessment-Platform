"""
assessment.py — Run risk assessment and retrieve results.
"""

import json

from flask import Blueprint, request

from database import models
from modules.llm_advisor import get_control_recommendations
from modules.risk_engine import build_risk_register, validate_assessment_inputs
from utils import api_response, escape_output, get_session_id, rate_limit

assessment_bp = Blueprint("assessment", __name__, url_prefix="/api/assessment")


@assessment_bp.route("/run", methods=["POST"])
@rate_limit()
def run_assessment():
    """Run full risk calculation, store results, return risk register."""
    try:
        session_id = get_session_id()
        body = request.get_json(silent=True) or {}
        org_name = body.get("org_name", "Organisation")
        assets = models.get_assets_with_threats(session_id)
        if not assets:
            return api_response(False, None, "No assets found for assessment", 400)
        has_threat = any(a.get("threats") for a in assets)
        if not has_threat:
            return api_response(False, None, "Add at least one threat before running assessment", 400)

        for asset in assets:
            for threat in asset.get("threats", []):
                validate_assessment_inputs(asset, threat)

        register = build_risk_register(assets)
        llm_result = get_control_recommendations(register)
        llm_json = json.dumps(llm_result)

        total_ale = sum(r["ale"] for r in register)
        highest = register[0] if register else None

        results = {
            "risk_register": register,
            "summary": {
                "total_assets": len(assets),
                "total_threats": sum(len(a.get("threats", [])) for a in assets),
                "total_ale": round(total_ale, 2),
                "highest_risk": highest,
                "org_name": org_name,
            },
            "llm_recommendations": llm_result,
            "session_id": session_id,
        }

        models.save_assessment(session_id, results, llm_json)
        return api_response(True, escape_output(results), None)
    except ValueError as e:
        return api_response(False, None, str(e), 400)
    except Exception as e:
        return api_response(False, None, f"Assessment failed: {e}", 500)


@assessment_bp.route("/results", methods=["GET"])
@rate_limit()
def get_results():
    """Return latest assessment results for session."""
    try:
        session_id = get_session_id()
        assessment = models.get_latest_assessment(session_id)
        if not assessment:
            return api_response(False, None, "No assessment found. Run assessment first.", 404)
        data = assessment.get("results") or {}
        if assessment.get("llm_recommendations_parsed"):
            data["llm_recommendations"] = assessment["llm_recommendations_parsed"]
        return api_response(True, escape_output(data), None)
    except Exception as e:
        return api_response(False, None, str(e), 500)


@assessment_bp.route("/notifications", methods=["GET"])
@rate_limit()
def get_notifications():
    """Dashboard notifications (e.g. new Critical CVEs)."""
    try:
        session_id = get_session_id()
        notes = models.get_notifications(session_id, unread_only=False)
        return api_response(True, escape_output(notes), None)
    except Exception as e:
        return api_response(False, None, str(e), 500)
