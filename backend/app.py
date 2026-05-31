"""
app.py — Flask application entry point for Risk Assessment Platform.
Registers blueprints, CORS, rate limiting, DB init, and CVE auto-update thread.
"""

import json
import threading
import time
from typing import Set

from flask import Flask
from flask_cors import CORS

import config
from database import models
from modules.cve_fetcher import check_critical_cve_for_software, fetch_cves_for_asset

# In-memory known CVE ids per asset software (for auto-update)
_known_cves: dict[str, Set[str]] = {}
_cve_thread_started = False


def create_app() -> Flask:
    """
    Application factory.

    Returns:
        Configured Flask application.
    """
    app = Flask(__name__)
    app.config["SECRET_KEY"] = config.FLASK_SECRET_KEY

    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        supports_credentials=True,
        allow_headers=["Content-Type", "X-Session-Id"],
        expose_headers=["X-Session-Id"],
    )

    models.init_db()

    from routes.assets import assets_bp
    from routes.threats import threats_bp
    from routes.assessment import assessment_bp
    from routes.reports import reports_bp
    from routes.compliance import compliance_bp

    app.register_blueprint(assets_bp)
    app.register_blueprint(threats_bp)
    app.register_blueprint(assessment_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(compliance_bp)

    @app.route("/api/health", methods=["GET"])
    def health():
        """Health check endpoint."""
        from utils import api_response

        return api_response(True, {"status": "ok", "env": config.FLASK_ENV}, None)

    return app


def _cve_auto_update_loop():
    """
    Background thread: refresh CVE data every 24 hours.
    Flags new Critical CVEs and logs dashboard notifications.
    """
    while True:
        try:
            time.sleep(config.CVE_UPDATE_INTERVAL)
            # Scan all assets (all sessions) — simplified global pass
            with models.get_db() as conn:
                rows = conn.execute(
                    "SELECT id, session_id, name, software FROM assets WHERE software IS NOT NULL AND software != ''"
                ).fetchall()
            for row in rows:
                asset = dict(row)
                software = asset.get("software", "")
                key = f"{asset['id']}:{software}"
                if key not in _known_cves:
                    existing = fetch_cves_for_asset(asset["name"], software)
                    _known_cves[key] = {c["cve_id"] for c in existing}
                known = _known_cves[key]
                new_critical = check_critical_cve_for_software(software, known)
                for cve in new_critical:
                    known.add(cve["cve_id"])
                    msg = (
                        f"New Critical CVE {cve['cve_id']} affects asset "
                        f"'{asset['name']}' ({software})"
                    )
                    models.add_notification(asset.get("session_id"), msg, "critical")
        except Exception:
            pass


def start_cve_background_thread():
    """Start daemon thread for CVE auto-update (once)."""
    global _cve_thread_started
    if _cve_thread_started:
        return
    _cve_thread_started = True
    t = threading.Thread(target=_cve_auto_update_loop, daemon=True)
    t.start()


app = create_app()

if __name__ == "__main__":
    start_cve_background_thread()
    app.run(host="0.0.0.0", port=config.FLASK_PORT, debug=config.FLASK_ENV == "development")
