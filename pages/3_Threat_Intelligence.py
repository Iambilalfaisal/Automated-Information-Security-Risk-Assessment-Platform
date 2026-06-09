"""
3_Threat_Intelligence.py — Live CVE feed per asset and NVD keyword search.
"""

import streamlit as st

from streamlit_lib.paths import ensure_backend_path
from streamlit_lib.session import get_session_id, init_session
from streamlit_lib.style import apply_theme, page_header, section_header, stat_card

ensure_backend_path()

from database import models  # noqa: E402
from modules.cve_fetcher import fetch_cves_for_asset  # noqa: E402
from streamlit_lib.charts import plot_cve_severity_bar  # noqa: E402

st.set_page_config(page_title="Threat Intelligence", page_icon="🔍", layout="wide")
init_session()
apply_theme()
session_id = get_session_id()

page_header(
    "Threat Intelligence",
    "Live CVE data from NIST NVD — monitor vulnerabilities across your asset inventory.",
)

assets         = models.get_assets(session_id)
assets_with_sw = [a for a in assets if a.get("software")]
notifications  = models.get_notifications(session_id, unread_only=False)
cve_notifs     = [n for n in notifications if "CVE" in (n.get("message") or "")]
critical_count = sum(1 for n in cve_notifs if "Critical" in (n.get("message") or ""))

m1, m2, m3, m4 = st.columns(4)
with m1:
    stat_card("Total Assets", str(len(assets)), "in inventory")
with m2:
    stat_card("CVE-Monitored", str(len(assets_with_sw)), "software-defined assets")
with m3:
    stat_card("CVE Alerts", str(len(cve_notifs)), "recorded notifications")
with m4:
    stat_card("Critical CVEs", str(critical_count), "CVSS ≥ 9.0", accent="#ef4444")

st.divider()

# ── Helper: render CVE detail cards ──────────────────────────────────────────
_SEV = {
    "Critical": ("#ef4444", "rgba(127,29,29,0.25)"),
    "High":     ("#f97316", "rgba(124,45,18,0.25)"),
    "Medium":   ("#eab308", "rgba(113,63,18,0.25)"),
    "Low":      ("#22c55e", "rgba(20,83,45,0.25)"),
}


def _cve_cards(cves: list) -> None:
    for cve in cves:
        sev       = cve.get("severity", "Low")
        score     = cve.get("cvss_score", 0)
        link      = cve.get("link", "#")
        raw_desc  = cve.get("description") or ""
        desc      = raw_desc[:220]
        suffix    = "…" if len(raw_desc) > 220 else ""
        published = cve.get("published", "N/A")
        border_col, bg_col = _SEV.get(sev, ("#94a3b8", "rgba(51,65,85,0.2)"))
        st.markdown(
            f"""
            <div style="background:{bg_col};border:1px solid #2d3f55;
                        border-left:3px solid {border_col};border-radius:8px;
                        padding:0.8rem 1rem;margin:0.35rem 0;
                        animation:fadeIn 0.35s ease both">
                <div style="display:flex;justify-content:space-between;
                            align-items:flex-start;flex-wrap:wrap;gap:0.4rem">
                    <div>
                        <span style="color:#60a5fa;font-weight:700;font-family:monospace;
                                     font-size:0.9rem">{cve["cve_id"]}</span>
                        &nbsp;
                        <span style="background:rgba(0,0,0,0.3);color:{border_col};
                                     border:1px solid {border_col};border-radius:99px;
                                     padding:0.1rem 0.5rem;font-size:0.68rem;font-weight:700">
                            {sev} &nbsp;·&nbsp; CVSS {score}
                        </span>
                    </div>
                    <a href="{link}" target="_blank"
                       style="color:#475569;font-size:0.75rem;text-decoration:none;
                              white-space:nowrap">NVD ↗</a>
                </div>
                <div style="color:#94a3b8;font-size:0.83rem;margin-top:0.4rem;line-height:1.55">
                    {desc}{suffix}
                </div>
                <div style="color:#475569;font-size:0.72rem;margin-top:0.3rem">
                    Published: {published}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ── Per-asset CVE feed ─────────────────────────────────────────────────────────
section_header(
    "Asset CVE Intelligence",
    "Select an asset to fetch live vulnerability data from NIST NVD",
)

if not assets_with_sw:
    st.info(
        "No assets with software defined. Go to **Assessment**, add an asset with a "
        "Software / OS field (e.g. 'windows', 'mysql') to enable CVE monitoring."
    )
else:
    asset_labels   = {f"{a['name']}  ·  {a['software']}": a for a in assets_with_sw}
    selected_label = st.selectbox(
        "Select asset",
        list(asset_labels.keys()),
        label_visibility="collapsed",
        key="ti_asset_sel",
    )
    selected_asset = asset_labels[selected_label]

    col_btn, _ = st.columns([1, 5])
    with col_btn:
        fetch_btn = st.button(
            "Fetch CVEs", type="primary", use_container_width=True, key="ti_fetch_btn"
        )

    cache_key = f"cves_asset_{selected_asset['id']}"

    if fetch_btn:
        with st.spinner(f"Querying NVD for \"{selected_asset['software']}\"…"):
            fetched = fetch_cves_for_asset(selected_asset["name"], selected_asset["software"])
        st.session_state[cache_key] = fetched

    if cache_key in st.session_state:
        cves   = st.session_state[cache_key]
        source = cves[0].get("source", "nvd") if cves else "—"
        label  = "Live NVD" if source == "nvd" else "Mock data (NVD unavailable)"
        st.caption(f"Source: **{label}**  ·  {len(cves)} CVE(s) found")

        if cves:
            plot_cve_severity_bar(cves)
            _cve_cards(cves)
        else:
            st.info("No CVEs found for this asset.")

# Show recorded notifications per asset (from previous assessments)
if cve_notifs:
    st.divider()
    section_header(
        f"Recorded CVE Notifications ({len(cve_notifs)})",
        "CVEs captured automatically when assets were added",
    )
    for n in cve_notifs[:20]:
        st.markdown(f'<div class="cve-card">&#9888; {n["message"]}</div>', unsafe_allow_html=True)
    if len(cve_notifs) > 20:
        st.caption(f"Showing 20 of {len(cve_notifs)} notifications.")

st.divider()

# ── CVE Keyword Search ─────────────────────────────────────────────────────────
section_header("CVE Keyword Search", "Search NIST NVD for any software, product, or vulnerability")

sc1, sc2 = st.columns([4, 1])
with sc1:
    search_kw = st.text_input(
        "Keyword",
        placeholder="e.g. apache httpd, windows server, log4j, openssl",
        label_visibility="collapsed",
        key="ti_search_kw",
    )
with sc2:
    search_btn = st.button(
        "Search NVD", type="primary", use_container_width=True, key="ti_search_btn"
    )

if search_btn and search_kw.strip():
    with st.spinner(f"Searching NVD for \"{search_kw.strip()}\"…"):
        results = fetch_cves_for_asset("", search_kw.strip())
    st.session_state["ti_search_results"] = results
    st.session_state["ti_search_term"]    = search_kw.strip()

if "ti_search_results" in st.session_state:
    results = st.session_state["ti_search_results"]
    term    = st.session_state.get("ti_search_term", "")
    source  = results[0].get("source", "nvd") if results else "—"
    st.caption(
        f"**{len(results)} result(s)** for \"{term}\"  ·  "
        f"{'Live NVD' if source == 'nvd' else 'Mock data (NVD unavailable)'}"
    )
    if results:
        plot_cve_severity_bar(results)
        _cve_cards(results)
    else:
        st.info("No CVEs found for that keyword.")
