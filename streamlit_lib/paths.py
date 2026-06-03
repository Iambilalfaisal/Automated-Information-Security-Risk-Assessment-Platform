"""
paths.py — Add backend/ to sys.path so Streamlit can import existing modules.
"""

import os
import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parent.parent / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

# Bridge Streamlit Cloud secrets → os.environ before any backend import reads config.
try:
    import streamlit as st  # noqa: PLC0415

    for _k in ("ANTHROPIC_API_KEY", "NVD_API_KEY"):
        if not os.environ.get(_k):
            _v = st.secrets.get(_k, "")
            if _v:
                os.environ[_k] = str(_v)
except Exception:
    pass


def ensure_backend_path() -> None:
    """Call once at app startup before any backend imports."""
    if str(_BACKEND) not in sys.path:
        sys.path.insert(0, str(_BACKEND))
