"""
config.py — Environment configuration for the Risk Assessment Platform.
Loads variables from .env via python-dotenv and exposes typed settings.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (parent of backend/)
_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_ROOT / ".env")

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = os.getenv(
    "DATABASE_PATH",
    str(BASE_DIR / "database" / "risk_platform.db"),
)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")
NVD_API_KEY = os.getenv("NVD_API_KEY", "")
FLASK_ENV = os.getenv("FLASK_ENV", "development")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))

# Rate limiting
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW_SECONDS = 60

# NVD API rate limit (no key): 5 requests per 30 seconds
NVD_RATE_LIMIT_REQUESTS = 5
NVD_RATE_LIMIT_WINDOW = 30

# CVE auto-update interval (seconds) — 24 hours
CVE_UPDATE_INTERVAL = 86400
