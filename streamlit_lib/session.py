"""
session.py — Streamlit session state and database initialisation.
"""

import uuid

import streamlit as st

from streamlit_lib.paths import ensure_backend_path

ensure_backend_path()

from database import models  # noqa: E402


def init_session() -> str:
    """
    Ensure session_id and database are ready.

    Returns:
        Current session_id string.
    """
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "org_name" not in st.session_state:
        st.session_state.org_name = "UMT Organisation"
    models.init_db()
    return st.session_state.session_id


def get_session_id() -> str:
    """Return session id, initialising if needed."""
    return init_session()
