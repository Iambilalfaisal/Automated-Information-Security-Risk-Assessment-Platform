"""
dataset_loader.py — Load CSV datasets into the database.

Supports two schemas:
  1. Standard (14-column): asset_name, asset_type, value_usd, description, software,
     threat_name, threat_category, probability, vulnerability_score,
     mitigation_effectiveness, aro, exposure_factor, uncertainty, threat_level
  2. Demo/IS-Risk (20-column): Asset_Name, Asset_Type, Threat_Description,
     Threat_Category, Likelihood (1-5), Impact (1-5), Risk_Score, Residual_Risk, etc.

Column headers are normalised to lowercase before schema detection.
"""

import csv
from pathlib import Path
from typing import Any

from database import models

_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_CSV = _ROOT / "data" / "assessits_sample_inventory.csv"

_FLOAT_FIELDS = {"value_usd", "probability", "mitigation_effectiveness", "aro", "exposure_factor", "uncertainty"}
_INT_FIELDS = {"vulnerability_score", "threat_level"}

# Mapping from demo CSV Asset_Type values to internal asset types
_ASSET_TYPE_MAP = {
    "data": "Data",
    "infrastructure": "Hardware",
    "application": "Software",
    "network": "Hardware",
    "endpoint": "Hardware",
    "identity": "People",
    "cloud": "Software",
    "physical": "Hardware",
    "process": "Process",
    "people": "People",
    "hardware": "Hardware",
    "software": "Software",
}

# Mapping from demo CSV Threat_Category to NIST categories
_THREAT_CAT_MAP = {
    "unauthorized access": "Adversarial",
    "phishing attack": "Adversarial",
    "sql injection": "Adversarial",
    "ransomware": "Adversarial",
    "brute force attack": "Adversarial",
    "intellectual property theft": "Adversarial",
    "misconfiguration": "Accidental",
    "malware infection": "Adversarial",
    "data exposure": "Accidental",
    "unauthorized physical access": "Adversarial",
    "privilege escalation": "Adversarial",
    "data leakage": "Accidental",
    "supply chain attack": "Adversarial",
    "log tampering": "Adversarial",
    "dns spoofing / cache poisoning": "Adversarial",
    "natural": "Natural",
    "structural": "Structural",
    "environmental": "Environmental",
    "accidental": "Accidental",
    "technical failure": "Technical Failure",
}

_RESIDUAL_RISK_MITIGATION = {
    "low": 0.6,
    "medium": 0.3,
    "high": 0.1,
}


def _normalise_headers(row: dict) -> dict:
    """Lowercase and strip all keys."""
    return {k.strip().lower(): v for k, v in row.items()}


def _is_demo_schema(headers: set) -> bool:
    """Return True if the CSV uses the IS-Risk demo schema (20-column format)."""
    demo_indicators = {"threat_description", "likelihood (1-5)", "impact (1-5)", "risk_score"}
    return bool(demo_indicators & headers)


def _coerce_standard(row: dict) -> dict:
    """Cast standard-schema CSV values to correct Python types."""
    out: dict[str, Any] = {}
    for k, v in row.items():
        k = k.strip().lower()
        v = str(v).strip()
        if k in _FLOAT_FIELDS:
            out[k] = float(v)
        elif k in _INT_FIELDS:
            out[k] = int(v)
        else:
            out[k] = v
    return out


def _map_demo_row(row: dict) -> tuple[dict, dict]:
    """
    Convert a demo-schema row into (asset_spec, threat_spec) dicts
    matching the internal schema.
    """
    # Asset fields
    asset_type_raw = row.get("asset_type", "hardware").strip().lower()
    asset_type = _ASSET_TYPE_MAP.get(asset_type_raw, "Hardware")

    # Derive asset value from Risk_Score (range 1–25 in CSV → $50K–$1.25M)
    try:
        risk_score = float(row.get("risk_score", "10"))
    except ValueError:
        risk_score = 10.0
    value_usd = round(risk_score * 50000, 2)

    description = row.get("vulnerability", "") or row.get("owner", "")
    software = ""  # no direct equivalent in demo CSV

    asset_spec = {
        "asset_name": row.get("asset_name", "").strip(),
        "asset_type": asset_type,
        "value_usd": value_usd,
        "description": description[:1000],
        "software": software,
    }

    # Threat fields
    threat_cat_raw = row.get("threat_category", "").strip().lower()
    threat_category = _THREAT_CAT_MAP.get(threat_cat_raw, "Adversarial")

    try:
        likelihood = float(row.get("likelihood (1-5)", "3"))
    except ValueError:
        likelihood = 3.0
    likelihood = max(1.0, min(5.0, likelihood))

    try:
        impact = float(row.get("impact (1-5)", "3"))
    except ValueError:
        impact = 3.0
    impact = max(1.0, min(5.0, impact))

    residual_raw = row.get("residual_risk", "medium").strip().lower()
    mitigation = _RESIDUAL_RISK_MITIGATION.get(residual_raw, 0.3)

    probability = round(likelihood / 5.0, 2)         # 0.0–1.0
    vulnerability_score = int(round(impact))          # 1–5
    exposure_factor = round(impact / 5.0, 2)          # 0.0–1.0
    aro = likelihood                                   # approximate ARO from likelihood
    threat_level = int(round(impact))                 # 1–5

    threat_desc = row.get("threat_description", "").strip()
    threat_name = (threat_desc[:147] + "...") if len(threat_desc) > 150 else threat_desc

    threat_spec = {
        "name": threat_name or f"{threat_cat_raw.title()} Threat",
        "category": threat_category,
        "probability": probability,
        "vulnerability_score": vulnerability_score,
        "mitigation_effectiveness": mitigation,
        "aro": aro,
        "exposure_factor": exposure_factor,
        "uncertainty": 0.1,
        "threat_level": threat_level,
    }

    return asset_spec, threat_spec


def load_dataset(
    session_id: str,
    csv_path: str | None = None,
    reset: bool = True,
) -> dict[str, int]:
    """
    Load assets and threats from a CSV file into the database for a session.

    Accepts both the standard 14-column schema and the IS-Risk demo 20-column schema.

    Args:
        session_id: Session to load data into.
        csv_path: Path to the CSV file. Defaults to data/assessits_sample_inventory.csv.
        reset: If True, clears existing assets for the session before loading.

    Returns:
        Dict with counts of created assets and threats.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        KeyError: If required columns are missing from the CSV.
    """
    path = Path(csv_path) if csv_path else _DEFAULT_CSV
    if not path.exists():
        raise FileNotFoundError(f"Dataset CSV not found: {path}")

    models.init_db()

    if reset:
        for asset in models.get_assets(session_id):
            models.delete_asset(asset["id"], session_id)

    assets: dict[str, dict[str, Any]] = {}
    threats_by_asset: dict[str, list[dict[str, Any]]] = {}
    schema_detected = None

    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        headers = {h.strip().lower() for h in (reader.fieldnames or [])}
        schema_detected = "demo" if _is_demo_schema(headers) else "standard"

        for raw in reader:
            row = _normalise_headers(raw)

            if schema_detected == "demo":
                asset_spec, threat_spec = _map_demo_row(row)
                name = asset_spec["asset_name"]
                if not name:
                    continue
                if name not in assets:
                    assets[name] = asset_spec
                    threats_by_asset[name] = []
                threats_by_asset[name].append(threat_spec)
            else:
                # Standard schema — coerce types
                coerced = _coerce_standard(row)
                name = coerced.get("asset_name", "")
                if not name:
                    continue
                if name not in assets:
                    assets[name] = {
                        "asset_name": name,
                        "asset_type": coerced.get("asset_type", "Software"),
                        "value_usd": coerced.get("value_usd", 100000.0),
                        "description": coerced.get("description", ""),
                        "software": coerced.get("software", ""),
                    }
                    threats_by_asset[name] = []
                threats_by_asset[name].append({
                    "name": coerced["threat_name"],
                    "category": coerced.get("threat_category", "Adversarial"),
                    "probability": coerced["probability"],
                    "vulnerability_score": coerced["vulnerability_score"],
                    "mitigation_effectiveness": coerced["mitigation_effectiveness"],
                    "aro": coerced["aro"],
                    "exposure_factor": coerced["exposure_factor"],
                    "uncertainty": coerced["uncertainty"],
                    "threat_level": coerced["threat_level"],
                })

    asset_count = 0
    threat_count = 0
    for name, spec in assets.items():
        asset = models.create_asset(
            session_id=session_id,
            name=spec["asset_name"],
            asset_type=spec["asset_type"],
            value_usd=spec["value_usd"],
            description=spec["description"],
            software=spec["software"],
        )
        asset_count += 1
        for threat in threats_by_asset[name]:
            models.create_threat(asset_id=asset["id"], **threat)
            threat_count += 1

    return {"assets": asset_count, "threats": threat_count}
