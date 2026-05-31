"""
seed_data.py — Load a realistic sample asset inventory and threat profile.

Used for live demos and to feed real (non-trivial) data into the technical
report generator. Can be run standalone (`python seed_data.py [session_id]`)
or invoked via the /api/demo/seed endpoint.
"""

import sys
from typing import Any

from database import models

DEMO_SESSION_ID = "demo-session"

# Realistic inventory: (name, type, value_usd, description, software)
SAMPLE_ASSETS: list[dict[str, Any]] = [
    {
        "name": "Customer Database Server",
        "asset_type": "Data",
        "value_usd": 850000,
        "description": "Primary MySQL database holding customer PII and payment records.",
        "software": "mysql",
        "threats": [
            {
                "name": "SQL Injection / Data Breach",
                "category": "Adversarial",
                "probability": 0.65,
                "vulnerability_score": 5,
                "mitigation_effectiveness": 0.30,
                "aro": 1.2,
                "exposure_factor": 0.40,
                "uncertainty": 0.15,
                "threat_level": 5,
            },
            {
                "name": "Insider Data Exfiltration",
                "category": "Adversarial",
                "probability": 0.30,
                "vulnerability_score": 4,
                "mitigation_effectiveness": 0.45,
                "aro": 0.5,
                "exposure_factor": 0.35,
                "uncertainty": 0.20,
                "threat_level": 4,
            },
        ],
    },
    {
        "name": "Public Web Server",
        "asset_type": "Software",
        "value_usd": 500000,
        "description": "Customer-facing Apache web application server in the DMZ.",
        "software": "apache",
        "threats": [
            {
                "name": "DDoS Attack",
                "category": "Adversarial",
                "probability": 0.55,
                "vulnerability_score": 3,
                "mitigation_effectiveness": 0.50,
                "aro": 2.0,
                "exposure_factor": 0.20,
                "uncertainty": 0.10,
                "threat_level": 3,
            },
            {
                "name": "Unpatched RCE Vulnerability",
                "category": "Technical Failure",
                "probability": 0.45,
                "vulnerability_score": 5,
                "mitigation_effectiveness": 0.35,
                "aro": 0.8,
                "exposure_factor": 0.50,
                "uncertainty": 0.15,
                "threat_level": 4,
            },
        ],
    },
    {
        "name": "Employee Laptop Fleet",
        "asset_type": "Hardware",
        "value_usd": 220000,
        "description": "150 Windows laptops used by staff, mix of office and remote work.",
        "software": "windows",
        "threats": [
            {
                "name": "Ransomware Infection",
                "category": "Adversarial",
                "probability": 0.50,
                "vulnerability_score": 4,
                "mitigation_effectiveness": 0.40,
                "aro": 1.0,
                "exposure_factor": 0.30,
                "uncertainty": 0.15,
                "threat_level": 5,
            },
            {
                "name": "Phishing / Credential Theft",
                "category": "Adversarial",
                "probability": 0.70,
                "vulnerability_score": 3,
                "mitigation_effectiveness": 0.45,
                "aro": 3.0,
                "exposure_factor": 0.15,
                "uncertainty": 0.10,
                "threat_level": 4,
            },
        ],
    },
    {
        "name": "Core Network Infrastructure",
        "asset_type": "Hardware",
        "value_usd": 400000,
        "description": "Routers, switches, and firewall appliances for the corporate LAN.",
        "software": "fortios",
        "threats": [
            {
                "name": "Firewall Misconfiguration",
                "category": "Structural",
                "probability": 0.35,
                "vulnerability_score": 4,
                "mitigation_effectiveness": 0.55,
                "aro": 0.6,
                "exposure_factor": 0.25,
                "uncertainty": 0.15,
                "threat_level": 3,
            },
        ],
    },
    {
        "name": "Payroll Processing System",
        "asset_type": "Process",
        "value_usd": 300000,
        "description": "Business process and software handling monthly payroll runs.",
        "software": "linux",
        "threats": [
            {
                "name": "Business Email Compromise",
                "category": "Adversarial",
                "probability": 0.40,
                "vulnerability_score": 3,
                "mitigation_effectiveness": 0.40,
                "aro": 0.7,
                "exposure_factor": 0.30,
                "uncertainty": 0.20,
                "threat_level": 4,
            },
        ],
    },
]


def _clear_session(session_id: str) -> None:
    """Remove existing assets (and cascading threats) for a clean reseed."""
    for asset in models.get_assets(session_id):
        models.delete_asset(asset["id"], session_id)


def seed(session_id: str = DEMO_SESSION_ID, reset: bool = True) -> dict[str, int]:
    """
    Populate the database with the sample inventory for a session.

    Args:
        session_id: Session to seed.
        reset: If True, clears existing assets for the session first.

    Returns:
        Dict with counts of created assets and threats.

    Side effects:
        Inserts rows into the assets and threats tables.
    """
    models.init_db()
    if reset:
        _clear_session(session_id)

    asset_count = 0
    threat_count = 0
    for spec in SAMPLE_ASSETS:
        asset = models.create_asset(
            session_id=session_id,
            name=spec["name"],
            asset_type=spec["asset_type"],
            value_usd=spec["value_usd"],
            description=spec["description"],
            software=spec["software"],
        )
        asset_count += 1
        for threat in spec["threats"]:
            models.create_threat(asset_id=asset["id"], **threat)
            threat_count += 1

    return {"assets": asset_count, "threats": threat_count}


if __name__ == "__main__":
    sid = sys.argv[1] if len(sys.argv) > 1 else DEMO_SESSION_ID
    result = seed(sid)
    print(f"Seeded session '{sid}': {result['assets']} assets, {result['threats']} threats")
