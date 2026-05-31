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

## Risk Formulas

- **SLE** = Asset Value × Exposure Factor  
- **ALE** = SLE × ARO  
- **R** = (P × V) − M + U  
- **AssessITS** — Rahman et al. (2024). arXiv:2410.01750

## Screenshots

_Add screenshots of Home, Assessment, Results, and Compliance pages here after running the UI._

## License

Academic project — UMT AI Department.
