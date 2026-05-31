"""
cve_fetcher.py — NVD CVE API v2.0 integration with rate limiting and mock fallback.
"""

import json
import time
from pathlib import Path
from typing import Any

import requests

import config

_MOCK_PATH = Path(__file__).resolve().parent / "mock_cves.json"
_nvd_timestamps: list[float] = []


def _severity_from_cvss(score: float) -> str:
    """Map CVSS score to severity label."""
    if score >= 9.0:
        return "Critical"
    if score >= 7.0:
        return "High"
    if score >= 4.0:
        return "Medium"
    return "Low"


def _load_mock_cves(software: str) -> list[dict[str, Any]]:
    """Load mock CVEs keyed by software keyword."""
    with open(_MOCK_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    key = (software or "").lower()
    for keyword in data:
        if keyword != "default" and keyword in key:
            return data[keyword][:5]
    return data.get("default", [])[:5]


def _wait_nvd_rate_limit() -> None:
    """Enforce NVD rate limit: 5 requests per 30 seconds without API key."""
    global _nvd_timestamps
    now = time.time()
    window = config.NVD_RATE_LIMIT_WINDOW
    _nvd_timestamps = [t for t in _nvd_timestamps if now - t < window]
    if len(_nvd_timestamps) >= config.NVD_RATE_LIMIT_REQUESTS:
        sleep_time = window - (now - _nvd_timestamps[0]) + 0.1
        if sleep_time > 0:
            time.sleep(sleep_time)
        _nvd_timestamps = []
    _nvd_timestamps.append(time.time())


def _parse_nvd_response(data: dict) -> list[dict[str, Any]]:
    """Parse NVD API v2.0 JSON into normalised CVE list."""
    results = []
    for item in data.get("vulnerabilities", [])[:5]:
        cve = item.get("cve", {})
        cve_id = cve.get("id", "UNKNOWN")
        descriptions = cve.get("descriptions", [])
        desc = next((d["value"] for d in descriptions if d.get("lang") == "en"), "")
        metrics = cve.get("metrics", {})
        cvss_score = 0.0
        for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
            if key in metrics and metrics[key]:
                cvss_score = float(metrics[key][0]["cvssData"].get("baseScore", 0))
                break
        published = cve.get("published", "")[:10]
        results.append(
            {
                "cve_id": cve_id,
                "description": desc[:500],
                "cvss_score": cvss_score,
                "severity": _severity_from_cvss(cvss_score),
                "published": published,
                "link": f"https://nvd.nist.gov/vuln/detail/{cve_id}",
                "source": "nvd",
            }
        )
    results.sort(key=lambda x: x["cvss_score"], reverse=True)
    return results


def fetch_cves_for_asset(asset_name: str, asset_software: str) -> list[dict[str, Any]]:
    """
    Query NVD API v2.0 for CVEs matching asset software/OS.

    Args:
        asset_name: Asset display name.
        asset_software: Software/OS string for keyword search.

    Returns:
        Top 5 CVEs with id, description, CVSS, date, link, severity.
        Falls back to mock_cves.json on failure or missing network.
    """
    keyword = asset_software or asset_name or "server"
    url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    params: dict[str, Any] = {"keywordSearch": keyword, "resultsPerPage": 5}
    headers: dict[str, str] = {}
    if config.NVD_API_KEY:
        headers["apiKey"] = config.NVD_API_KEY

    try:
        _wait_nvd_rate_limit()
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        if resp.status_code == 200:
            parsed = _parse_nvd_response(resp.json())
            if parsed:
                return parsed
    except Exception:
        pass

    mock = _load_mock_cves(keyword)
    for c in mock:
        c["source"] = "mock"
    return mock


def check_critical_cve_for_software(software: str, known_ids: set[str]) -> list[dict[str, Any]]:
    """
    Fetch CVEs and return new Critical CVEs not in known_ids.

    Used by background CVE auto-update thread.
    """
    cves = fetch_cves_for_asset("", software)
    new_critical = [
        c for c in cves
        if c.get("severity") == "Critical" and c.get("cve_id") not in known_ids
    ]
    return new_critical
