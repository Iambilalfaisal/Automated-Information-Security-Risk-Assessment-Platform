"""
dataset_loader.py — Load the AssessITS sample inventory CSV into the database.

Default dataset: data/assessits_sample_inventory.csv
Provenance: synthetic SME scenario aligned with AssessITS (arXiv:2410.01750)
and NIST SP 800-30. No real organisation data is included.
"""

import csv
from pathlib import Path
from typing import Any

from database import models

_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_CSV = _ROOT / "data" / "assessits_sample_inventory.csv"

_FLOAT_FIELDS = {"value_usd", "probability", "mitigation_effectiveness", "aro", "exposure_factor", "uncertainty"}
_INT_FIELDS = {"vulnerability_score", "threat_level"}


def _coerce_row(row: dict[str, str]) -> dict[str, Any]:
    """Cast CSV string values to the correct Python types."""
    out: dict[str, Any] = {}
    for k, v in row.items():
        k = k.strip()
        v = v.strip()
        if k in _FLOAT_FIELDS:
            out[k] = float(v)
        elif k in _INT_FIELDS:
            out[k] = int(v)
        else:
            out[k] = v
    return out


def load_dataset(
    session_id: str,
    csv_path: str | None = None,
    reset: bool = True,
) -> dict[str, int]:
    """
    Load assets and threats from a CSV file into the database for a session.

    Args:
        session_id: Session to load data into.
        csv_path: Path to the CSV file. Defaults to data/assessits_sample_inventory.csv.
        reset: If True, clears existing assets for the session before loading.

    Returns:
        Dict with counts of created assets and threats.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
    """
    path = Path(csv_path) if csv_path else _DEFAULT_CSV
    if not path.exists():
        raise FileNotFoundError(f"Dataset CSV not found: {path}")

    models.init_db()

    if reset:
        for asset in models.get_assets(session_id):
            models.delete_asset(asset["id"], session_id)

    # Group rows by asset_name to collect all threats per asset
    assets: dict[str, dict[str, Any]] = {}
    threats_by_asset: dict[str, list[dict[str, Any]]] = {}

    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for raw in reader:
            row = _coerce_row(raw)
            name = row["asset_name"]
            if name not in assets:
                assets[name] = {
                    "asset_name": name,
                    "asset_type": row.get("asset_type", "Software"),
                    "value_usd": row["value_usd"],
                    "description": row.get("description", ""),
                    "software": row.get("software", ""),
                }
                threats_by_asset[name] = []
            threats_by_asset[name].append({
                "name": row["threat_name"],
                "category": row.get("threat_category", "Adversarial"),
                "probability": row["probability"],
                "vulnerability_score": row["vulnerability_score"],
                "mitigation_effectiveness": row["mitigation_effectiveness"],
                "aro": row["aro"],
                "exposure_factor": row["exposure_factor"],
                "uncertainty": row["uncertainty"],
                "threat_level": row["threat_level"],
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
