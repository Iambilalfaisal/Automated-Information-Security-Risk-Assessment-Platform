"""
demo.py — Demo data seeding endpoint for live demonstrations.
"""

from flask import Blueprint

import seed_data
from utils import api_response, get_session_id, rate_limit

demo_bp = Blueprint("demo", __name__, url_prefix="/api/demo")


@demo_bp.route("/seed", methods=["POST"])
@rate_limit()
def seed_demo():
    """Load the sample asset inventory and threat profile for the session."""
    try:
        session_id = get_session_id()
        result = seed_data.seed(session_id, reset=True)
        return api_response(True, result, None, 201)
    except Exception as e:
        return api_response(False, None, f"Failed to seed demo data: {e}", 500)
