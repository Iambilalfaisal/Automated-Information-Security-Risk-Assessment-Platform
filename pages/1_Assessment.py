"""
1_Assessment.py — Asset inventory, threats, demo seed, and run assessment.
"""

import streamlit as st

from streamlit_lib.paths import ensure_backend_path
from streamlit_lib.style import apply_theme, page_header, section_header

ensure_backend_path()

import dataset_loader  # noqa: E402
import seed_data  # noqa: E402
from database import models  # noqa: E402
from modules.cve_fetcher import fetch_cves_for_asset  # noqa: E402
from streamlit_lib.services import run_assessment  # noqa: E402
from streamlit_lib.session import get_session_id, init_session  # noqa: E402

st.set_page_config(page_title="Assessment", page_icon="📋", layout="wide")
init_session()
apply_theme()
session_id = get_session_id()

page_header(
    "Risk Assessment",
    "Add assets & threats, load sample data, then run the quantitative analysis.",
)

# Organisation, demo, dataset, and run
col_a, col_b, col_c, col_d = st.columns([2, 1, 1, 1])
with col_a:
    st.session_state.org_name = st.text_input(
        "Organisation name",
        value=st.session_state.get("org_name", "UMT Organisation"),
    )
with col_b:
    if st.button("Load Demo Data", type="secondary", use_container_width=True):
        result = seed_data.seed(session_id, reset=True)
        st.success(f"Loaded {result['assets']} assets and {result['threats']} threats.")
        st.rerun()
with col_c:
    if st.button("Load Dataset", type="secondary", use_container_width=True):
        try:
            result = dataset_loader.load_dataset(session_id, reset=True)
            st.success(
                f"Loaded {result['assets']} assets and {result['threats']} threats from CSV dataset."
            )
            st.rerun()
        except FileNotFoundError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Dataset load failed: {e}")
with col_d:
    if st.button("Run Assessment", type="primary", use_container_width=True):
        try:
            run_assessment(session_id, st.session_state.org_name)
            st.success("Assessment complete! Open **Results** in the sidebar.")
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Assessment failed: {e}")

# Optional CSV upload
with st.expander("Upload custom CSV dataset"):
    st.caption(
        "CSV must have columns: asset_name, asset_type, value_usd, description, software, "
        "threat_name, threat_category, probability, vulnerability_score, "
        "mitigation_effectiveness, aro, exposure_factor, uncertainty, threat_level"
    )
    uploaded = st.file_uploader("Choose CSV file", type=["csv"], key="csv_upload")
    if uploaded is not None:
        import tempfile, os  # noqa: E401

        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            tmp.write(uploaded.read())
            tmp_path = tmp.name
        try:
            result = dataset_loader.load_dataset(session_id, csv_path=tmp_path, reset=True)
            st.success(f"Loaded {result['assets']} assets and {result['threats']} threats.")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to load CSV: {e}")
        finally:
            os.unlink(tmp_path)

st.divider()

# --- Add asset ---
section_header("Add Asset", "Define an asset in your organisation's inventory")
ASSET_TYPES = ["Hardware", "Software", "Data", "People", "Process"]

with st.form("add_asset", clear_on_submit=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        a_name = st.text_input("Asset name *", max_chars=150)
        a_type = st.selectbox("Type *", ASSET_TYPES)
    with c2:
        a_value = st.number_input("Value (USD) *", min_value=0.0, step=1000.0, value=100000.0)
        a_software = st.text_input("Software / OS (for CVE lookup)", max_chars=255, placeholder="e.g. windows, mysql")
    with c3:
        a_desc = st.text_area("Description", max_chars=1000, height=68)
    submitted_asset = st.form_submit_button("Add asset")

if submitted_asset:
    if not a_name.strip():
        st.error("Asset name is required.")
    else:
        try:
            asset = models.create_asset(
                session_id=session_id,
                name=a_name.strip(),
                asset_type=a_type,
                value_usd=float(a_value),
                description=a_desc or "",
                software=a_software or "",
            )
            st.success(f"Added asset: {asset['name']}")
            if a_software:
                cves = fetch_cves_for_asset(asset["name"], a_software)
                if cves:
                    st.markdown("**CVEs for this asset:**")
                    for c in cves:
                        sev = c.get("severity", "Unknown")
                        st.markdown(
                            f"- **{c['cve_id']}** ({sev}, CVSS {c.get('cvss_score', 'N/A')}) — "
                            f"{c.get('description', '')[:120]}…"
                        )
                        models.add_notification(
                            session_id,
                            f"CVE {c['cve_id']} ({sev}, CVSS {c.get('cvss_score', 'N/A')}) "
                            f"on {asset['name']}: {c.get('description', '')[:80]}",
                            severity="warning",
                        )
        except Exception as e:
            st.error(str(e))

# --- Add threat ---
assets = models.get_assets(session_id)
section_header("Add Threat", "Map a threat to an asset using NIST SP 800-30 parameters")
if not assets:
    st.info("Add at least one asset before defining threats.")
else:
    CATEGORIES = [
        "Adversarial",
        "Natural",
        "Structural",
        "Environmental",
        "Accidental",
        "Technical Failure",
    ]
    asset_options = {f"{a['name']} (id {a['id']})": a["id"] for a in assets}

    with st.form("add_threat", clear_on_submit=True):
        t1, t2 = st.columns(2)
        with t1:
            asset_label = st.selectbox("Asset *", list(asset_options.keys()))
            t_name = st.text_input("Threat name *", max_chars=150)
            t_cat = st.selectbox("NIST category", CATEGORIES)
        with t2:
            t_prob = st.slider("Probability (P)", 0.0, 1.0, 0.5, 0.05)
            t_vuln = st.slider("Vulnerability (V)", 1, 5, 3)
            t_mit = st.slider("Mitigation (M)", 0.0, 1.0, 0.3, 0.05)
        t3, t4 = st.columns(2)
        with t3:
            t_aro = st.slider("ARO (incidents/year)", 0.0, 5.0, 1.0, 0.1)
            t_ef = st.slider("Exposure factor (%)", 0, 100, 30) / 100.0
        with t4:
            t_unc = st.slider("Uncertainty (U)", 0.0, 1.0, 0.1, 0.05)
            t_level = st.slider("Threat level", 1, 5, 3)
        submitted_threat = st.form_submit_button("Add threat")

    if submitted_threat:
        if not t_name.strip():
            st.error("Threat name is required.")
        else:
            try:
                models.create_threat(
                    asset_id=asset_options[asset_label],
                    name=t_name.strip(),
                    probability=t_prob,
                    vulnerability_score=t_vuln,
                    mitigation_effectiveness=t_mit,
                    aro=t_aro,
                    exposure_factor=t_ef,
                    category=t_cat,
                    uncertainty=t_unc,
                    threat_level=t_level,
                )
                st.success(f"Added threat: {t_name}")
                st.rerun()
            except Exception as e:
                st.error(str(e))

st.divider()

# --- Lists ---
col_assets, col_threats = st.columns(2)
with col_assets:
    section_header(f"Assets ({len(assets)})")
    if assets:
        for a in assets:
            ac1, ac2 = st.columns([4, 1])
            with ac1:
                st.markdown(
                    f"**{a['name']}** — {a['asset_type']} · "
                    f"${float(a['value_usd']):,.0f}"
                )
                if a.get("software"):
                    st.caption(f"Software: {a['software']}")
            with ac2:
                if st.button("Delete", key=f"del_a_{a['id']}"):
                    models.delete_asset(a["id"], session_id)
                    st.rerun()
    else:
        st.caption("No assets yet.")

with col_threats:
    threats = models.get_threats(session_id=session_id)
    section_header(f"Threats ({len(threats)})")
    if threats:
        for t in threats:
            tc1, tc2 = st.columns([4, 1])
            with tc1:
                st.markdown(
                    f"**{t['name']}** (asset {t['asset_id']}) · P={t['probability']} · "
                    f"V={t['vulnerability_score']} · EF={t['exposure_factor']*100:.0f}%"
                )
            with tc2:
                if st.button("Delete", key=f"del_t_{t['id']}"):
                    models.delete_threat(t["id"])
                    st.rerun()
    else:
        st.caption("No threats yet.")
