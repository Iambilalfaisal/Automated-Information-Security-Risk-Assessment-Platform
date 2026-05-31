"""
security_tests.py — Security and load tests for the Risk Assessment Platform.
"""

import json
import threading

import pytest

from app import create_app
from database import models
from modules.llm_advisor import get_control_recommendations
from modules.risk_engine import calculate_sle, validate_assessment_inputs


@pytest.fixture
def client():
    """Flask test client with fresh DB."""
    app = create_app()
    app.config["TESTING"] = True
    models.init_db()
    return app.test_client()


@pytest.fixture
def session_header():
    return {"X-Session-Id": "security-test-session", "Content-Type": "application/json"}


class TestSQLInjection:
    def test_sql_injection_asset_name(self, client, session_header):
        payload = {
            "name": "'; DROP TABLE assets; --",
            "asset_type": "Software",
            "value_usd": 1000,
            "description": "test",
            "software": "linux",
        }
        r = client.post("/api/assets", data=json.dumps(payload), headers=session_header)
        assert r.status_code in (200, 201)
        data = r.get_json()
        assert data["success"] is True
        # Table still exists
        r2 = client.get("/api/assets", headers=session_header)
        assert r2.get_json()["success"] is True


class TestXSS:
    def test_xss_escaped_in_response(self, client, session_header):
        payload = {
            "name": "<script>alert('xss')</script>",
            "asset_type": "Data",
            "value_usd": 500,
        }
        r = client.post("/api/assets", data=json.dumps(payload), headers=session_header)
        data = r.get_json()
        assert data["success"]
        name = data["data"]["name"]
        assert "<script>" not in name or "&lt;script&gt;" in name


class TestFormulaValidation:
    def test_invalid_exposure_factor(self):
        with pytest.raises(ValueError):
            calculate_sle(1000, 2.0)

    def test_validate_assessment_inputs(self):
        asset = {"value_usd": 1000}
        threat = {
            "exposure_factor": 0.5,
            "probability": 0.5,
            "vulnerability_score": 3,
            "mitigation_effectiveness": 0.2,
            "uncertainty": 0.1,
        }
        validate_assessment_inputs(asset, threat)


class TestLLMFallback:
    def test_fallback_without_api_key(self, monkeypatch):
        import config

        monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "")
        register = [
            {
                "risk_criticality": "Critical",
                "threat_name": "Ransomware",
            }
        ]
        result = get_control_recommendations(register)
        assert result["source"] == "fallback"
        assert len(result["recommendations"]) > 0


class TestLoadConcurrent:
    def test_concurrent_assessment_requests(self, client, session_header, monkeypatch):
        """50 concurrent assessment run attempts."""
        monkeypatch.setattr("config.RATE_LIMIT_REQUESTS", 10000)
        from utils import _rate_limit_store

        _rate_limit_store.clear()
        # Setup asset + threat once
        client.post(
            "/api/assets",
            data=json.dumps(
                {
                    "name": "Load Test Asset",
                    "asset_type": "Hardware",
                    "value_usd": 10000,
                    "software": "windows",
                }
            ),
            headers=session_header,
        )
        assets = client.get("/api/assets", headers=session_header).get_json()["data"]
        aid = assets[0]["id"]
        client.post(
            "/api/threats",
            data=json.dumps(
                {
                    "asset_id": aid,
                    "name": "Malware",
                    "probability": 0.3,
                    "vulnerability_score": 3,
                    "mitigation_effectiveness": 0.2,
                    "aro": 0.5,
                    "exposure_factor": 0.2,
                }
            ),
            headers=session_header,
        )

        results = []
        errors = []

        def run():
            try:
                app = create_app()
                app.config["TESTING"] = True
                with app.test_client() as tc:
                    r = tc.post(
                        "/api/assessment/run",
                        data=json.dumps({}),
                        headers=session_header,
                    )
                    results.append(r.status_code)
            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=run) for _ in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(errors) == 0
        assert len(results) == 50
        assert any(s == 200 for s in results)
