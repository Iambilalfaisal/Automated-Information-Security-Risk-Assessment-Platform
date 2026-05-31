"""
risk_engine.py — NIST SP 800-30 and AssessITS risk calculations.

Formulas cite: Rahman et al. (2024). AssessITS. arXiv:2410.01750
NIST SP 800-30 Rev. 1 for SLE/ALE quantitative risk analysis.
"""

from typing import Any


def calculate_sle(asset_value: float, exposure_factor: float) -> float:
    """
    Single Loss Expectancy: SLE = Asset_Value × Exposure_Factor.

    Args:
        asset_value: Monetary value of the asset (USD).
        exposure_factor: Percentage of asset lost per incident (0.0–1.0).

    Returns:
        SLE in USD.
    """
    if not 0 <= exposure_factor <= 1:
        raise ValueError("exposure_factor must be between 0 and 1")
    if asset_value < 0:
        raise ValueError("asset_value must be non-negative")
    return asset_value * exposure_factor


def calculate_ale(sle: float, aro: float) -> float:
    """
    Annualised Loss Expectancy: ALE = SLE × ARO.

    Args:
        sle: Single Loss Expectancy (USD).
        aro: Annualised Rate of Occurrence (e.g. 1.5 = 1.5 times per year).

    Returns:
        ALE in USD.
    """
    if sle < 0 or aro < 0:
        raise ValueError("sle and aro must be non-negative")
    return sle * aro


def calculate_risk_score(
    probability: float,
    vulnerability: int,
    mitigation: float,
    uncertainty: float = 0.1,
) -> float:
    """
    Composite risk score: R = (P × V) − M + U.

    Args:
        probability: Threat probability P (0–1).
        vulnerability: Vulnerability score V (1–5).
        mitigation: Mitigation effectiveness M (0–1, 1 = fully mitigated).
        uncertainty: Uncertainty factor U (0–1).

    Returns:
        Risk score R.
    """
    if not 0 <= probability <= 1:
        raise ValueError("probability must be between 0 and 1")
    if vulnerability not in range(1, 6):
        raise ValueError("vulnerability must be between 1 and 5")
    if not 0 <= mitigation <= 1:
        raise ValueError("mitigation must be between 0 and 1")
    if not 0 <= uncertainty <= 1:
        raise ValueError("uncertainty must be between 0 and 1")
    return (probability * vulnerability) - mitigation + uncertainty


def calculate_threat_value(threat_level: int, vulnerability_level: int) -> int:
    """
    AssessITS Threat Value = Threat_Level + Vulnerability_Level (both 1–5).

    Rahman et al. (2024). AssessITS. arXiv:2410.01750
    """
    if threat_level not in range(1, 6) or vulnerability_level not in range(1, 6):
        raise ValueError("threat_level and vulnerability_level must be 1–5")
    return threat_level + vulnerability_level


def calculate_risk_impact_rating(
    asset_value: float,
    threat_value: int,
    likelihood: float,
) -> float:
    """
    AssessITS Risk Impact Rating = Asset_Value × Threat_Value × Likelihood.

    Asset value should be normalised 1–5 scale for rating band 1–250.
    Rahman et al. (2024). AssessITS. arXiv:2410.01750
    """
    if asset_value < 1 or asset_value > 5:
        raise ValueError("asset_value scale must be 1–5 for impact rating")
    if not 0 <= likelihood <= 1:
        raise ValueError("likelihood must be between 0 and 1")
    return asset_value * threat_value * likelihood * 50  # scale to 1–250 range


def normalise_asset_value(value_usd: float, max_value: float = 1_000_000) -> float:
    """
    Map USD asset value to 1–5 scale for AssessITS formula.

    Args:
        value_usd: Asset value in dollars.
        max_value: Reference max for normalisation.

    Returns:
        Scale 1.0–5.0.
    """
    if value_usd <= 0:
        return 1.0
    ratio = min(value_usd / max_value, 1.0)
    return 1.0 + ratio * 4.0


def get_criticality(risk_impact_rating: float) -> str:
    """
    AssessITS Risk Criticality Level from impact rating.

    1–45: Low | 46–99: Medium | 100–199: High | 200–250: Critical
    Rahman et al. (2024). AssessITS. arXiv:2410.01750
    """
    rating = max(0, risk_impact_rating)
    if rating <= 45:
        return "Low"
    if rating <= 99:
        return "Medium"
    if rating <= 199:
        return "High"
    return "Critical"


def compute_cba(ale_before: float, ale_after: float, cost_of_control: float) -> float:
    """
    Cost-Benefit Analysis: CBA = ALE_before − ALE_after − Cost_of_Control.

    Control is recommended when CBA > 0.
    """
    return ale_before - ale_after - cost_of_control


def assess_threat_row(asset: dict[str, Any], threat: dict[str, Any]) -> dict[str, Any]:
    """
    Compute all metrics for one asset–threat pair.

    Returns:
        Dict with sle, ale, risk_score, risk_impact_rating, criticality, etc.
    """
    value_usd = float(asset.get("value_usd", 0))
    ef = float(threat.get("exposure_factor", 0.1))
    aro = float(threat.get("aro", 0))
    prob = float(threat.get("probability", 0))
    vuln = int(threat.get("vulnerability_score", 3))
    mit = float(threat.get("mitigation_effectiveness", 0))
    unc = float(threat.get("uncertainty", 0.1))
    threat_level = int(threat.get("threat_level", 3))

    sle = calculate_sle(value_usd, ef)
    ale = calculate_ale(sle, aro)
    risk_score = calculate_risk_score(prob, vuln, mit, unc)

    asset_scale = normalise_asset_value(value_usd)
    tv = calculate_threat_value(threat_level, vuln)
    likelihood = prob
    impact_rating = calculate_risk_impact_rating(asset_scale, tv, likelihood)
    criticality = get_criticality(impact_rating)

    # Default CBA example: 30% ALE reduction, control cost 10% of ALE
    ale_after = ale * 0.7
    control_cost = ale * 0.1
    cba = compute_cba(ale, ale_after, control_cost)
    recommended = cba > 0

    return {
        "asset_id": asset.get("id"),
        "asset_name": asset.get("name"),
        "asset_type": asset.get("asset_type"),
        "asset_value_usd": value_usd,
        "threat_id": threat.get("id"),
        "threat_name": threat.get("name"),
        "threat_category": threat.get("category"),
        "sle": round(sle, 2),
        "ale": round(ale, 2),
        "risk_score": round(risk_score, 4),
        "risk_impact_rating": round(impact_rating, 2),
        "risk_criticality": criticality,
        "threat_value": tv,
        "ale_before": round(ale, 2),
        "ale_after": round(ale_after, 2),
        "control_cost": round(control_cost, 2),
        "cba": round(cba, 2),
        "control_recommended": recommended,
        "probability": prob,
        "vulnerability_score": vuln,
    }


def build_risk_register(assets_with_threats: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Build sorted risk register from assets each with nested threats.

    Args:
        assets_with_threats: List of asset dicts with 'threats' key.

    Returns:
        Risk register entries sorted by risk_impact_rating descending.
    """
    register: list[dict[str, Any]] = []
    for asset in assets_with_threats:
        threats = asset.get("threats") or []
        if not threats:
            continue
        for threat in threats:
            register.append(assess_threat_row(asset, threat))

    register.sort(key=lambda x: x["risk_impact_rating"], reverse=True)
    return register


def validate_assessment_inputs(asset: dict, threat: dict) -> None:
    """Raise ValueError if inputs violate formula constraints."""
    calculate_sle(float(asset["value_usd"]), float(threat["exposure_factor"]))
    calculate_risk_score(
        float(threat["probability"]),
        int(threat["vulnerability_score"]),
        float(threat["mitigation_effectiveness"]),
        float(threat.get("uncertainty", 0.1)),
    )
