# Automated Information Security Risk Assessment Platform

UMT InfoSec Semester Project — Spring 2026

Web-based platform for quantitative risk assessment (NIST SP 800-30 + AssessITS), CVE lookup, LLM control recommendations, and PDF reporting.

## Tech Stack

- **UI (primary):** Streamlit — single app, easy deploy on [Streamlit Cloud](https://share.streamlit.io)
- **Backend:** Python 3.11+, SQLite, risk engine, ReportLab PDFs
- **API (optional):** Flask REST for programmatic access
- **LLM:** Anthropic Claude (optional; rule-based fallback included)
- **CVE:** NVD API v2.0 (mock fallback included)

## Quick Start (Streamlit — recommended)

One terminal, no Node.js required:

```powershell
cd "c:\Users\PC\Desktop\Uni work\IS Project"
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

Open **http://localhost:8501** → **Assessment** → **Load Demo Data** → **Run Assessment** → **Results**.

### Deploy on Streamlit Cloud

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. **Main file path:** `app.py`
4. **Python:** 3.11 or 3.12
5. Optional **Secrets** (TOML): `ANTHROPIC_API_KEY = "your-key"` for live Claude recommendations.

**Note:** SQLite data on Streamlit Cloud is ephemeral (resets on redeploy). Use **Load Demo Data** for each demo session.

### Tests

```powershell
cd backend
..\venv\Scripts\activate
pytest -v
```

## Legacy: Flask API + React frontend

The original React UI remains in [frontend/](frontend/) for reference. To run it you need **two** terminals (Flask on port 5000 + Vite on 5173). Prefer Streamlit for demos and deployment.

```powershell
# Terminal 1 — API
cd backend
.\venv\Scripts\activate
python app.py

# Terminal 2 — React
cd frontend
npm install
npm run dev
```

## API Documentation

All endpoints return `{ "success": bool, "data": any, "error": string | null }`.

Pass session via header `X-Session-Id` or query `session_id`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/assets` | Create asset |
| GET | `/api/assets` | List assets |
| PUT | `/api/assets/<id>` | Update asset |
| DELETE | `/api/assets/<id>` | Delete asset |
| GET | `/api/assets/<id>/cves` | CVEs for asset software |
| POST | `/api/threats` | Create threat |
| GET | `/api/threats` | List threats |
| PUT | `/api/threats/<id>` | Update threat |
| DELETE | `/api/threats/<id>` | Delete threat |
| POST | `/api/assessment/run` | Run assessment |
| GET | `/api/assessment/results` | Latest results |
| GET | `/api/assessment/notifications` | CVE alerts |
| GET | `/api/compliance` | Compliance checklist |
| POST | `/api/compliance` | Update control status |
| GET | `/api/reports/risk-register` | Risk Register PDF |
| GET | `/api/reports/cba` | CBA PDF |
| GET | `/api/reports/compliance` | Compliance PDF |
| GET | `/api/health` | Health check |

## Dataset

`data/assessits_sample_inventory.csv` — 20-row synthetic SME scenario (10 assets, 20 threats)
aligned with AssessITS (arXiv:2410.01750) and NIST SP 800-30. Provenance: hand-crafted by
the project team to represent a realistic small enterprise; values calibrated against published
NIST worked examples and AssessITS 1–5 scales. No real organisation data is included.

Load it with the **Load Dataset** button on the Assessment page, or upload your own CSV
(same column schema). Optional CSV upload is available via the expander on the Assessment page.

## Demo Data

Load a realistic sample inventory (5 assets, 8 threats) in one click via the
**Load Demo Data** button on the Assessment page, or from the CLI:

```powershell
cd backend
.\venv\Scripts\python seed_data.py demo-session
```

## Deliverables

| Deliverable | Location |
|-------------|----------|
| Technical Report (IEEE format, .docx) | [docs/Technical_Report.docx](docs/Technical_Report.docx) |
| Report generator (regenerates the .docx) | [docs/generate_report.py](docs/generate_report.py) |
| Report figures | [docs/figures/](docs/figures/) |
| Security Testing Report | [SECURITY_TESTING_REPORT.md](SECURITY_TESTING_REPORT.md) |
| Video Demo Script | [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) |
| Viva Presentation Outline | [docs/PRESENTATION_OUTLINE.md](docs/PRESENTATION_OUTLINE.md) |

Regenerate the technical report (re-seeds demo data, rebuilds figures, writes the .docx):

```powershell
cd backend
.\venv\Scripts\activate
cd ..\docs
python generate_report.py
```

Open `docs/Technical_Report.docx` in Microsoft Word and choose **Update Field**
(Ctrl+A then F9) to populate the Table of Contents and page numbers.

## Risk Formulas

- **SLE** = Asset Value × Exposure Factor  
- **ALE** = SLE × ARO  
- **R** = (P × V) − M + U  
- **AssessITS** — Rahman et al. (2024). arXiv:2410.01750

## Project Structure

```
├── app.py              # Streamlit entry (primary UI)
├── pages/              # Assessment & Results
├── streamlit_lib/      # Session, charts, services
├── backend/            # Risk engine, DB, PDF, CVE, LLM, optional Flask API
├── frontend/           # Legacy React UI
├── docs/               # Technical report & figures
└── requirements.txt    # Root deps for Streamlit Cloud
```

## Screenshots

| Page | Description |
|------|-------------|
| Home | Overview and start assessment CTA |
| Assessment | Asset form, threat matrix, run assessment |
| Results | Dashboard, compliance, PDF downloads |

_Add screenshots after running the UI locally._

## Git Commits

This project uses feature-based commits per implementation task (15+ commits for instructor review).

## License

Academic project — UMT AI Department.
