"""
llm_advisor.py — Claude API control recommendations with rule-based fallback.
"""

import json
import os
from pathlib import Path
from typing import Any

import config

_FALLBACK_PATH = Path(__file__).resolve().parent / "fallback_controls.json"


def _load_fallback_by_criticality(criticality: str) -> list[dict[str, Any]]:
    """Load pre-defined controls for a criticality level."""
    with open(_FALLBACK_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get(criticality, data.get("Medium", []))


def get_fallback_recommendations(risk_register: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Rule-based recommendations from fallback_controls.json.

    Args:
        risk_register: Sorted risk register entries.

    Returns:
        Dict with recommendations list and source flag.
    """
    top = risk_register[:5]
    recommendations: list[dict[str, Any]] = []
    seen: set[str] = set()
    for entry in top:
        crit = entry.get("risk_criticality", "Medium")
        for ctrl in _load_fallback_by_criticality(crit):
            cid = ctrl["control_id"]
            if cid not in seen:
                seen.add(cid)
                recommendations.append({**ctrl, "mapped_risk": entry.get("threat_name")})
    return {
        "recommendations": recommendations[:10],
        "source": "fallback",
        "framework": "NIST SP 800-30",
    }


def get_control_recommendations(
    risk_register: list[dict[str, Any]],
    framework: str = "NIST",
) -> dict[str, Any]:
    """
    Recommend NIST SP 800-30 or ISO 27001 controls for top 5 risks.

    Calls Claude API when ANTHROPIC_API_KEY is set; otherwise uses fallback JSON.

    Args:
        risk_register: Sorted risk register from risk_engine.
        framework: "NIST" or "ISO27001".

    Returns:
        Structured dict with recommendations list.
    """
    if not risk_register:
        return {"recommendations": [], "source": "empty", "framework": framework}

    api_key = os.getenv("ANTHROPIC_API_KEY") or config.ANTHROPIC_API_KEY
    if not api_key:
        return get_fallback_recommendations(risk_register)

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        top5 = risk_register[:5]
        context = json.dumps(top5, indent=2)
        system = (
            "You are an information security advisor. Given a risk register, "
            "recommend specific NIST SP 800-30 control IDs for the top risks. "
            "Explain each control in plain English for a non-technical executive. "
            "Output ONLY valid JSON with this schema: "
            '{"recommendations": [{"control_id": "AC-2", "control_name": "...", '
            '"plain_english_explanation": "...", "implementation_priority": 1, '
            '"estimated_cost_range": "$X - $Y", "mapped_risk": "threat name"}]}'
        )
        user_msg = f"Framework: {framework}\nRisk register (top 5):\n{context}"
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            system=system,
            messages=[{"role": "user", "content": user_msg}],
        )
        text = message.content[0].text
        # Strip markdown code fences if present
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        parsed = json.loads(text.strip())
        parsed["source"] = "claude"
        parsed["framework"] = framework
        return parsed
    except Exception:
        return get_fallback_recommendations(risk_register)
