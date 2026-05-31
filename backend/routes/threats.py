"""
threats.py — Threat CRUD API endpoints linked to assets.
"""

from flask import Blueprint, request

from database import models
from utils import api_response, escape_output, get_session_id, rate_limit

threats_bp = Blueprint("threats", __name__, url_prefix="/api/threats")


def _threat_belongs_to_session(threat_id: int, session_id: str) -> bool:
    """Verify threat's asset belongs to session."""
    threat = models.get_threat(threat_id)
    if not threat:
        return False
    asset = models.get_asset(threat["asset_id"], session_id)
    return asset is not None


@threats_bp.route("", methods=["POST"])
@rate_limit()
def create_threat():
    """Add a threat to an asset."""
    try:
        body = request.get_json() or {}
        session_id = get_session_id()
        required = [
            "asset_id",
            "name",
            "probability",
            "vulnerability_score",
            "mitigation_effectiveness",
            "aro",
            "exposure_factor",
        ]
        for field in required:
            if field not in body:
                return api_response(False, None, f"Missing required field: {field}", 400)
        asset = models.get_asset(int(body["asset_id"]), session_id)
        if not asset:
            return api_response(False, None, "Asset not found", 404)
        threat = models.create_threat(
            asset_id=int(body["asset_id"]),
            name=str(body["name"]),
            probability=float(body["probability"]),
            vulnerability_score=int(body["vulnerability_score"]),
            mitigation_effectiveness=float(body["mitigation_effectiveness"]),
            aro=float(body["aro"]),
            exposure_factor=float(body["exposure_factor"]),
            category=body.get("category", ""),
            uncertainty=float(body.get("uncertainty", 0.1)),
            threat_level=int(body.get("threat_level", 3)),
        )
        return api_response(True, escape_output(threat), None, 201)
    except (ValueError, TypeError) as e:
        return api_response(False, None, str(e), 400)
    except Exception as e:
        return api_response(False, None, str(e), 500)


@threats_bp.route("", methods=["GET"])
@rate_limit()
def list_threats():
    """List all threats for session."""
    try:
        session_id = get_session_id()
        threats = models.get_threats(session_id=session_id)
        return api_response(True, escape_output(threats), None)
    except Exception as e:
        return api_response(False, None, str(e), 500)


@threats_bp.route("/<int:threat_id>", methods=["PUT"])
@rate_limit()
def update_threat(threat_id: int):
    """Update a threat."""
    try:
        session_id = get_session_id()
        if not _threat_belongs_to_session(threat_id, session_id):
            return api_response(False, None, "Threat not found", 404)
        body = request.get_json() or {}
        threat = models.update_threat(threat_id, **body)
        return api_response(True, escape_output(threat), None)
    except Exception as e:
        return api_response(False, None, str(e), 500)


@threats_bp.route("/<int:threat_id>", methods=["DELETE"])
@rate_limit()
def delete_threat(threat_id: int):
    """Delete a threat."""
    try:
        session_id = get_session_id()
        if not _threat_belongs_to_session(threat_id, session_id):
            return api_response(False, None, "Threat not found", 404)
        models.delete_threat(threat_id)
        return api_response(True, {"deleted": threat_id}, None)
    except Exception as e:
        return api_response(False, None, str(e), 500)
