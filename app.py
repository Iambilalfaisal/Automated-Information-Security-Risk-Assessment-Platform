"""
app.py — Streamlit entry point for the Risk Assessment Platform.

Run locally: streamlit run app.py
Deploy: Streamlit Cloud with main file path app.py
"""

import streamlit as st

from streamlit_lib.session import init_session

st.set_page_config(
    page_title="InfoSec Risk Platform",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session()

st.title("Automated Information Security Risk Assessment Platform")
st.markdown(
    """
    **UMT InfoSec — Spring 2026**

    Quantitative risk analysis using **NIST SP 800-30** (SLE, ALE) and the **AssessITS**
    methodology (Risk Impact Rating, 1–250 band). Includes CVE intelligence, control
    recommendations, and downloadable PDF reports.
    """
)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### 1. Assessment")
    st.caption("Add assets & threats, or load demo data")
    st.page_link("pages/1_Assessment.py", label="Go to Assessment →", icon="📋")
with col2:
    st.markdown("### 2. Run")
    st.caption("Compute risk register & recommendations")
    st.page_link("pages/1_Assessment.py", label="Run from Assessment", icon="▶️")
with col3:
    st.markdown("### 3. Results")
    st.caption("Dashboard, compliance, PDF exports")
    st.page_link("pages/2_Results.py", label="View Results →", icon="📊")

st.divider()
st.markdown(
    """
    **Quick start:** Open **Assessment** → click **Load Demo Data** → **Run Assessment** → **Results**.

    **Deploy:** Push to GitHub and connect at [share.streamlit.io](https://share.streamlit.io)
    with main file `app.py`.
    """
)
