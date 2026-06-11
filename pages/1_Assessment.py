"""
1_Assessment.py — Asset inventory, threats, demo seed, and run assessment.
"""

import streamlit as st
from pathlib import Path

from streamlit_lib.paths import ensure_backend_path
from streamlit_lib.style import apply_theme, page_header, section_header, sidebar_status

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
sidebar_status(session_id)

page_header(
    "Risk Assessment",
    "Add assets & threats, load sample data, then run the quantitative analysis.",
)

# ── Post-run success banner ────────────────────────────────────────────────────
if st.session_state.get("_assessment_just_run"):
    st.session_state._assessment_just_run = False
    st.markdown(
        """
        <div style="background:linear-gradient(135deg,rgba(34,197,94,0.12),rgba(59,130,246,0.08));
                    border:1px solid rgba(34,197,94,0.35);border-radius:14px;
                    padding:1.2rem 1.5rem;margin-bottom:1rem;animation:fadeInUp 0.5s ease both;
                    display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem">
            <div>
                <div style="color:#4ade80;font-weight:700;font-size:1rem;margin-bottom:0.2rem">
                    ✓ Assessment Complete
                </div>
                <div style="color:#64748b;font-size:0.85rem">
                    Risk register generated — view your full dashboard and reports.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.page_link("pages/2_Results.py", label="📊 View Results & Reports →")
    with col_r2:
        st.page_link("pages/4_Treatment_Plan.py", label="🛠️ Set Treatment Plans →")

# ── Sample datasets picker ─────────────────────────────────────────────────────
_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_SAMPLE_DATASETS = {
    "Default — General IT Organisation":       _DATA_DIR / "assessits_sample_inventory.csv",
    "Healthcare Hospital":                      _DATA_DIR / "healthcare_hospital.csv",
    "Banking & FinTech":                        _DATA_DIR / "banking_fintech.csv",
    "Manufacturing & IoT / SCADA":              _DATA_DIR / "manufacturing_iot.csv",
    "E-Commerce & Retail":                      _DATA_DIR / "ecommerce_retail.csv",
    "Government Agency":                        _DATA_DIR / "government_agency.csv",
}
_available = {k: v for k, v in _SAMPLE_DATASETS.items() if v.exists()}

# Organisation, demo, dataset, and run
col_a, col_b, col_c, col_d = st.columns([2, 1, 1, 1])
with col_a:
    st.session_state.org_name = st.text_input(
        "Organisation name",
        value=st.session_state.get("org_name", "UMT Organisation"),
    )
with col_b:
    if st.button("Load Demo Data", type="secondary", use_container_width=True):
        with st.spinner("Loading demo data…"):
            result = seed_data.seed(session_id, reset=True)
        st.success(f"Loaded {result['assets']} assets and {result['threats']} threats.")
        st.rerun()
with col_c:
    if st.button("Load Dataset", type="secondary", use_container_width=True):
        selected_ds = st.session_state.get("_selected_dataset", list(_available.keys())[0])
        csv_path = _available.get(selected_ds)
        try:
            with st.spinner(f"Loading {selected_ds}…"):
                result = dataset_loader.load_dataset(session_id, csv_path=str(csv_path), reset=True)
            st.success(
                f"Loaded {result['assets']} assets and {result['threats']} threats from **{selected_ds}**."
            )
            st.rerun()
        except FileNotFoundError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Dataset load failed: {e}")
with col_d:
    if st.button("Run Assessment", type="primary", use_container_width=True):
        try:
            with st.spinner("Running quantitative risk analysis…"):
                run_assessment(session_id, st.session_state.org_name)
            st.session_state._assessment_just_run = True
            st.rerun()
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Assessment failed: {e}")

# ── Sample dataset selector ────────────────────────────────────────────────────
if _available:
    with st.expander("Choose a sample dataset", expanded=False):
        st.markdown(
            '<p style="color:#64748b;font-size:0.83rem;margin-bottom:0.6rem">'
            'Select a sector-specific dataset then click <strong style="color:#e2e8f0">Load Dataset</strong>.'
            '</p>',
            unsafe_allow_html=True,
        )
        st.session_state._selected_dataset = st.selectbox(
            "Sample dataset",
            list(_available.keys()),
            label_visibility="collapsed",
        )
        _chosen_path = _available[st.session_state._selected_dataset]
        _icons = {"Healthcare": "🏥", "Banking": "🏦", "Manufacturing": "🏭",
                  "E-Commerce": "🛒", "Government": "🏛️", "Default": "🏢"}
        _icon = next((v for k, v in _icons.items() if k in st.session_state._selected_dataset), "📁")
        st.markdown(
            f'<div style="background:rgba(59,130,246,0.06);border:1px solid rgba(59,130,246,0.15);'
            f'border-radius:8px;padding:0.65rem 1rem;margin-top:0.4rem;font-size:0.82rem;color:#94a3b8">'
            f'{_icon} &nbsp; <strong style="color:#e2e8f0">{st.session_state._selected_dataset}</strong>'
            f' &nbsp;·&nbsp; {_chosen_path.name}</div>',
            unsafe_allow_html=True,
        )

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
    section_header(f"Assets ({len(assets)})", "Your organisation's inventory")
    if assets:
        for a in assets:
            ac1, ac2 = st.columns([5, 1])
            with ac1:
                sw_tag = (
                    f'<span class="list-item-tag">{a["software"]}</span>'
                    if a.get("software") else ""
                )
                st.markdown(
                    f"""
                    <div class="list-item" style="animation-delay:{assets.index(a)*0.04:.2f}s">
                        <div class="list-item-name">{a['name']}</div>
                        <div class="list-item-meta">
                            {a['asset_type']} &nbsp;·&nbsp;
                            <span style="color:#60a5fa;font-weight:600">${float(a['value_usd']):,.0f}</span>
                            &nbsp; {sw_tag}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with ac2:
                st.markdown("<div style='margin-top:0.55rem'></div>", unsafe_allow_html=True)
                if st.button("✕", key=f"del_a_{a['id']}", help="Delete asset"):
                    models.delete_asset(a["id"], session_id)
                    st.rerun()
    else:
        st.markdown(
            '<div class="list-item" style="color:#1e3a5f;font-size:0.83rem">No assets yet.</div>',
            unsafe_allow_html=True,
        )

with col_threats:
    threats = models.get_threats(session_id=session_id)
    section_header(f"Threats ({len(threats)})", "Mapped to assets")
    if threats:
        for t in threats:
            tc1, tc2 = st.columns([5, 1])
            with tc1:
                st.markdown(
                    f"""
                    <div class="list-item" style="animation-delay:{threats.index(t)*0.04:.2f}s">
                        <div class="list-item-name">{t['name']}</div>
                        <div class="list-item-meta">
                            Asset {t['asset_id']} &nbsp;·&nbsp;
                            P=<span style="color:#fde68a">{t['probability']}</span> &nbsp;·&nbsp;
                            V=<span style="color:#fdba74">{t['vulnerability_score']}</span> &nbsp;·&nbsp;
                            EF=<span style="color:#f87171">{t['exposure_factor']*100:.0f}%</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with tc2:
                st.markdown("<div style='margin-top:0.55rem'></div>", unsafe_allow_html=True)
                if st.button("✕", key=f"del_t_{t['id']}", help="Delete threat"):
                    models.delete_threat(t["id"])
                    st.rerun()
    else:
        st.markdown(
            '<div class="list-item" style="color:#1e3a5f;font-size:0.83rem">No threats yet.</div>',
            unsafe_allow_html=True,
        )
