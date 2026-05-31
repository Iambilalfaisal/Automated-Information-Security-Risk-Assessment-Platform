"""
test_risk_engine.py — Unit tests for NIST SP 800-30 and AssessITS risk formulas.
"""

import pytest

from modules.risk_engine import (
    build_risk_register,
    calculate_ale,
    calculate_risk_impact_rating,
    calculate_risk_score,
    calculate_sle,
    calculate_threat_value,
    compute_cba,
    get_criticality,
    normalise_asset_value,
)


class TestNISTSLEALE:
    """NIST SP 800-30 worked example: AV=$1M, EF=30%, ARO=1.5."""

    def test_sle_worked_example(self):
        sle = calculate_sle(1_000_000, 0.30)
        assert sle == 300_000

    def test_ale_worked_example(self):
        sle = calculate_sle(1_000_000, 0.30)
        ale = calculate_ale(sle, 1.5)
        assert ale == 450_000

    def test_sle_invalid_ef(self):
        with pytest.raises(ValueError):
            calculate_sle(1000, 1.5)


class TestCompositeRisk:
    def test_r_formula(self):
        # R = (P * V) - M + U = (0.5 * 4) - 0.2 + 0.1 = 1.9
        r = calculate_risk_score(0.5, 4, 0.2, 0.1)
        assert abs(r - 1.9) < 0.001

    def test_invalid_probability(self):
        with pytest.raises(ValueError):
            calculate_risk_score(1.5, 3, 0.5)


class TestAssessITS:
    def test_threat_value(self):
        assert calculate_threat_value(3, 4) == 7

    def test_criticality_bands(self):
        assert get_criticality(30) == "Low"
        assert get_criticality(50) == "Medium"
        assert get_criticality(150) == "High"
        assert get_criticality(220) == "Critical"

    def test_normalise_asset_value(self):
        assert normalise_asset_value(0) == 1.0
        assert normalise_asset_value(1_000_000) == 5.0


class TestCBA:
    def test_cba_positive_recommended(self):
        cba = compute_cba(450_000, 200_000, 50_000)
        assert cba == 200_000
        assert cba > 0

    def test_cba_negative_not_recommended(self):
        cba = compute_cba(100_000, 95_000, 10_000)
        assert cba < 0


class TestRiskRegister:
    def test_build_register_sorted(self):
        assets = [
            {
                "id": 1,
                "name": "Web Server",
                "asset_type": "Software",
                "value_usd": 500_000,
                "threats": [
                    {
                        "id": 1,
                        "name": "Data Breach",
                        "probability": 0.6,
                        "vulnerability_score": 4,
                        "mitigation_effectiveness": 0.3,
                        "aro": 1.0,
                        "exposure_factor": 0.25,
                        "uncertainty": 0.1,
                        "threat_level": 4,
                        "category": "Adversarial",
                    }
                ],
            }
        ]
        reg = build_risk_register(assets)
        assert len(reg) == 1
        assert "sle" in reg[0]
        assert "ale" in reg[0]
        assert reg[0]["risk_criticality"] in ("Low", "Medium", "High", "Critical")
