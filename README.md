# Automated Information Security Risk Assessment Platform

UMT InfoSec Semester Project — Spring 2026

Web-based platform for quantitative risk assessment (NIST SP 800-30 + AssessITS), CVE lookup, LLM control recommendations, and PDF reporting.

## Tech Stack

- **Backend:** Python 3.11+, Flask, SQLite
- **Frontend:** React 18, Vite, Tailwind CSS, Recharts
- **LLM:** Anthropic Claude (optional; rule-based fallback included)
- **CVE:** NVD API v2.0 (mock fallback included)
- **PDF:** ReportLab

## Quick Start

### Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
copy ..\.env.example ..\.env
python app.py
```

API runs at `http://localhost:5000`

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

UI runs at `http://localhost:5173`

### Tests

```powershell
cd backend
.\venv\Scripts\activate
pytest -v
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
risk-assessment-platform/
├── backend/          # Flask API, risk engine, PDF, CVE, LLM
├── frontend/         # React + Tailwind + Recharts
├── SECURITY_TESTING_REPORT.md
└── .env.example
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
