"""
paths.py — Add backend/ to sys.path so Streamlit can import existing modules.
"""

import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parent.parent / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))


def ensure_backend_path() -> None:
    """Call once at app startup before any backend imports."""
    if str(_BACKEND) not in sys.path:
        sys.path.insert(0, str(_BACKEND))
