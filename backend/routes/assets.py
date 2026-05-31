"""
assets.py — Asset CRUD API endpoints and CVE lookup per asset.
"""

from flask import Blueprint, request

from database import models
from modules.cve_fetcher import fetch_cves_for_asset
from utils import (
    api_response,
    escape_output,
    get_session_id,
    rate_limit,
    validate_str_field,
)

assets_bp = Blueprint("assets", __name__, url_prefix="/api/assets")


@assets_bp.route("", methods=["POST"])
@rate_limit()
def create_asset():
    """Add a new asset for the current session."""
    try:
        body = request.get_json() or {}
        session_id = get_session_id()
        required = ["name", "asset_type", "value_usd"]
        for field in required:
            if field not in body:
                return api_response(False, None, f"Missing required field: {field}", 400)
        value_usd = float(body["value_usd"])
        if value_usd < 0:
            return api_response(False, None, "value_usd must be non-negative", 400)
        asset = models.create_asset(
            session_id=session_id,
            name=validate_str_field(body["name"], "name", 150),
            asset_type=validate_str_field(body["asset_type"], "asset_type", 50),
            value_usd=value_usd,
            description=validate_str_field(body.get("description"), "description", 1000, required=False),
            software=validate_str_field(body.get("software"), "software", 255, required=False),
        )
        return api_response(True, escape_output(asset), None, 201)
    except (ValueError, TypeError) as e:
        return api_response(False, None, str(e), 400)
    except Exception as e:
        return api_response(False, None, f"Failed to create asset: {e}", 500)


@assets_bp.route("", methods=["GET"])
@rate_limit()
def list_assets():
    """List all assets for the current session."""
    try:
        session_id = get_session_id()
        assets = models.get_assets(session_id)
        return api_response(True, escape_output(assets), None)
    except Exception as e:
        return api_response(False, None, str(e), 500)


@assets_bp.route("/<int:asset_id>", methods=["GET"])
@rate_limit()
def get_asset(asset_id: int):
    """Get a single asset."""
    try:
        session_id = get_session_id()
        asset = models.get_asset(asset_id, session_id)
        if not asset:
            return api_response(False, None, "Asset not found", 404)
        return api_response(True, escape_output(asset), None)
    except Exception as e:
        return api_response(False, None, str(e), 500)


@assets_bp.route("/<int:asset_id>", methods=["PUT"])
@rate_limit()
def update_asset(asset_id: int):
    """Update an asset."""
    try:
        body = request.get_json() or {}
        session_id = get_session_id()
        asset = models.update_asset(asset_id, session_id, **body)
        if not asset:
            return api_response(False, None, "Asset not found", 404)
        return api_response(True, escape_output(asset), None)
    except Exception as e:
        return api_response(False, None, str(e), 500)


@assets_bp.route("/<int:asset_id>", methods=["DELETE"])
@rate_limit()
def delete_asset(asset_id: int):
    """Delete an asset."""
    try:
        session_id = get_session_id()
        if not models.delete_asset(asset_id, session_id):
            return api_response(False, None, "Asset not found", 404)
        return api_response(True, {"deleted": asset_id}, None)
    except Exception as e:
        return api_response(False, None, str(e), 500)


@assets_bp.route("/<int:asset_id>/cves", methods=["GET"])
@rate_limit()
def get_asset_cves(asset_id: int):
    """Fetch CVEs for asset software/OS."""
    try:
        session_id = get_session_id()
        asset = models.get_asset(asset_id, session_id)
        if not asset:
            return api_response(False, None, "Asset not found", 404)
        software = asset.get("software") or asset.get("name", "")
        cves = fetch_cves_for_asset(asset["name"], software)
        return api_response(True, escape_output(cves), None)
    except Exception as e:
        return api_response(False, None, str(e), 500)