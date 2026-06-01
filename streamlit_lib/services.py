"""
services.py — Business logic for Streamlit (assessment run, compliance score).
"""

import json

from streamlit_lib.paths import ensure_backend_path

ensure_backend_path()

from constants import NIST_CONTROLS  # noqa: E402
from database import models  # noqa: E402
from modules.llm_advisor import get_control_recommendations  # noqa: E402
from modules.risk_engine import build_risk_register, validate_assessment_inputs  # noqa: E402


def run_assessment(session_id: str, org_name: str) -> dict:
    """
    Run full risk assessment for session.

    Args:
        session_id: User session identifier.
        org_name: Organisation name for reports.

    Returns:
        Results dict with risk_register, summary, llm_recommendations.

    Raises:
        ValueError: If no assets or no threats.
    """
    assets = models.get_assets_with_threats(session_id)
    if not assets:
        raise ValueError("No assets found. Add assets or load demo data first.")
    if not any(a.get("threats") for a in assets):
        raise ValueError("Add at least one threat before running assessment.")

    for asset in assets:
        for threat in asset.get("threats", []):
            validate_assessment_inputs(asset, threat)

    register = build_risk_register(assets)
    llm_result = get_control_recommendations(register)
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
    models.save_assessment(session_id, results, json.dumps(llm_result))
    return results


def get_compliance_data(session_id: str) -> dict:
    """
    Build compliance checklist with score and gaps.

    Returns:
        Dict with controls list, score_percent, gaps.
    """
    stored = {c["control_id"]: c for c in models.get_compliance(session_id)}
    items = []
    implemented = 0.0
    for cid, cname in NIST_CONTROLS:
        row = stored.get(
            cid,
            {"control_id": cid, "control_name": cname, "status": "not_implemented", "notes": ""},
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
    return {"controls": items, "score_percent": score, "gaps": gaps}
