# Automated Information Security Risk Assessment Platform — Architecture Guide

> **Purpose of this document:** A complete, self-contained reference for any LLM or developer
> who needs to understand this project from scratch — what it does, how it is built, and why
> every technical decision was made.

---

## 1. What This Project Is

A **quantitative information security risk assessment web application** built as a capstone project
for the UMT InfoSec Spring 2026 program.

Users enter their organisation's IT assets and the threats facing each asset. The platform runs a
full risk calculation pipeline based on academic and government standards, fetches live CVE data
from the US government's National Vulnerability Database, asks an AI model for control
recommendations, and produces downloadable PDF reports.

**Problem it solves:** Manual risk assessments are slow, inconsistent, and require specialist
knowledge of NIST and ISO frameworks. This platform automates the entire workflow and makes it
accessible to non-experts.

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    STREAMLIT FRONTEND (Primary)              │
│  app.py  ──  pages/  ──  streamlit_lib/                     │
│  (Landing / Executive Dashboard)                            │
│    1_Assessment.py   – input assets & threats               │
│    2_Results.py      – dashboard, charts, PDF downloads     │
│    3_Threat_Intelligence.py – CVE feed from NVD             │
│    4_Treatment_Plan.py – remediation tracker                │
│    5_History.py      – ALE trend over time                  │
│    6_Methodology.py  – framework docs & formulas            │
└────────────────────────┬────────────────────────────────────┘
                         │ Python function calls (no HTTP in Streamlit mode)
┌────────────────────────▼────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                      │
│  streamlit_lib/services.py  (run_assessment, compliance)    │
│  backend/modules/                                           │
│    risk_engine.py   – NIST + AssessITS formulas             │
│    cve_fetcher.py   – NVD API v2.0 queries                  │
│    llm_advisor.py   – Claude API + rule-based fallback      │
│    report_generator.py – ReportLab PDF creation             │
└────────────────────────┬────────────────────────────────────┘
                         │ parameterised SQL
┌────────────────────────▼────────────────────────────────────┐
│                    DATA LAYER                                │
│  backend/database/models.py  – CRUD operations              │
│  backend/database/schema.sql – 8-table SQLite schema        │
│  backend/database/risk_platform.db – SQLite file on disk    │
└─────────────────────────────────────────────────────────────┘

         ┌──────────────────────────────────────────┐
         │          EXTERNAL SERVICES               │
         │  NIST NVD API v2.0   – CVE lookups       │
         │  Anthropic Claude API – LLM advice       │
         └──────────────────────────────────────────┘

(Optional, standalone REST API — not used by Streamlit)
┌─────────────────────────────────────────────────────────────┐
│                  FLASK REST API (Legacy)                     │
│  backend/app.py  +  backend/routes/                         │
│  Exposes the same business logic over HTTP (port 5000)      │
└─────────────────────────────────────────────────────────────┘
```

**Key architectural decision:** Streamlit calls Python functions directly; Flask is an optional
REST wrapper for the same code. There is no HTTP call between Streamlit and Flask in normal use.

---

## 3. File Tree

```
IS Project/
├── app.py                              ← Streamlit entry point (run: streamlit run app.py)
├── requirements.txt                    ← Top-level Python dependencies
├── .env.example                        ← Template for environment variables
├── .streamlit/config.toml              ← Streamlit server + theme config
│
├── pages/                              ← Streamlit multi-page routing
│   ├── 1_Assessment.py                 ← Asset / threat input forms + demo load
│   ├── 2_Results.py                    ← Charts, risk register table, PDF downloads
│   ├── 3_Threat_Intelligence.py        ← CVE cards from NVD per asset
│   ├── 4_Treatment_Plan.py             ← Risk treatment strategy editor
│   ├── 5_History.py                    ← All past assessment runs + ALE trend
│   └── 6_Methodology.py               ← Framework docs, formulas, references
│
├── streamlit_lib/                      ← Shared Streamlit utilities
│   ├── session.py                      ← st.session_state init + DB bootstrap
│   ├── services.py                     ← run_assessment(), compliance_score()
│   ├── charts.py                       ← Plotly chart factory functions
│   ├── style.py                        ← Dark-theme CSS + UI helper components
│   └── paths.py                        ← Absolute path helpers
│
├── backend/
│   ├── app.py                          ← Flask application factory (optional)
│   ├── config.py                       ← Typed config object from env vars
│   ├── constants.py                    ← NIST control catalogue (20 controls)
│   ├── utils.py                        ← API response envelope + rate-limit decorator
│   ├── dataset_loader.py               ← CSV → DB importer
│   ├── seed_data.py                    ← Hard-coded demo data generator
│   │
│   ├── database/
│   │   ├── models.py                   ← All CRUD functions (parameterised SQL)
│   │   ├── schema.sql                  ← CREATE TABLE statements (8 tables)
│   │   └── risk_platform.db            ← SQLite database file
│   │
│   ├── modules/
│   │   ├── risk_engine.py              ← Core formulas (NIST + AssessITS)
│   │   ├── cve_fetcher.py              ← NVD API client + offline fallback
│   │   ├── llm_advisor.py              ← Claude API client + JSON fallback
│   │   ├── report_generator.py         ← PDF generation (3 report types)
│   │   ├── mock_cves.json              ← Offline CVE data (by software keyword)
│   │   └── fallback_controls.json      ← Pre-mapped NIST controls (by criticality)
│   │
│   ├── routes/                         ← Flask blueprints (optional REST API)
│   │   ├── assets.py   threats.py  assessment.py
│   │   ├── reports.py  compliance.py  demo.py
│   │
│   └── tests/
│       ├── test_risk_engine.py         ← Formula unit tests
│       └── test_security.py            ← XSS / SQLi / rate-limit tests
│
├── data/
│   └── assessits_sample_inventory.csv  ← 20-row synthetic dataset (10 assets × 2 threats)
│
└── docs/                               ← Academic deliverables (Word/PDF, not runtime)
    ├── Technical_Report.docx
    ├── IS_Risk_Assessment_Platform_Presentation.docx
    └── figures/                        ← architecture.png, dataflow.png, etc.
```

---

## 4. Technology Stack

| Layer | Technology | Version | Why |
|---|---|---|---|
| UI framework | Streamlit | 1.28+ | Zero-boilerplate Python web app; trivial cloud deploy |
| Optional REST API | Flask | 3.0+ | If programmatic access needed |
| Database | SQLite 3 | built-in | No infrastructure; sufficient for single-user sessions |
| AI recommendations | Anthropic Claude API | claude-haiku-4-5-20251001 | Fast, cheap, structured JSON output |
| CVE data | NIST NVD API v2.0 | — | Official US government CVE database |
| Charts | Plotly | 5.18+ | Interactive charts in Streamlit |
| PDF generation | ReportLab | 4.0+ | Programmatic PDF without external tools |
| Word documents | python-docx | 1.1+ | Academic report generation |
| Data manipulation | Pandas | 2.0+ | CSV import, tabular operations |
| HTTP client | requests | 2.31+ | NVD API calls |
| Environment config | python-dotenv | 1.0+ | .env file loading |
| Testing | pytest | 8.0+ | Unit + security tests |
| Fonts | Space Grotesk, JetBrains Mono | Google Fonts CDN | Dark-theme brand identity |

---

## 5. Database Schema

Eight SQLite tables. Foreign keys are enabled. WAL mode is on for concurrent reads.

```sql
-- Organisation assets being assessed
assets (
  id INTEGER PRIMARY KEY,
  session_id TEXT NOT NULL,          -- UUID; all data is scoped to this
  name TEXT, asset_type TEXT,
  value_usd REAL,                    -- Monetary value of the asset
  description TEXT, software TEXT,   -- software field drives CVE lookups
  created_at TIMESTAMP
)

-- Threats associated with a specific asset
threats (
  id INTEGER PRIMARY KEY,
  asset_id INTEGER REFERENCES assets(id) ON DELETE CASCADE,
  name TEXT, category TEXT,
  -- NIST SP 800-30 parameters:
  probability REAL,                  -- 0–1; likelihood of threat materialising
  vulnerability_score REAL,          -- 1–5; exploitability score
  mitigation_effectiveness REAL,     -- 0–1; how well current controls reduce risk
  aro REAL,                          -- Annualised Rate of Occurrence
  exposure_factor REAL,              -- 0–1; fraction of asset lost per incident
  uncertainty REAL,                  -- 0–1; confidence modifier
  -- AssessITS parameter:
  threat_level INTEGER,              -- 1–5; qualitative threat severity
  created_at TIMESTAMP
)

-- Saved results of a full assessment run
assessments (
  id INTEGER PRIMARY KEY,
  session_id TEXT NOT NULL,
  results_json TEXT,                 -- Full risk register as JSON string
  llm_recommendations TEXT,          -- Claude output as JSON string
  created_at TIMESTAMP
)

-- NIST SP 800-53 control implementation checklist
compliance_status (
  id INTEGER PRIMARY KEY,
  session_id TEXT, control_id TEXT,  -- UNIQUE(session_id, control_id)
  control_name TEXT,
  status TEXT,                       -- 'implemented' | 'partial' | 'not_implemented'
  notes TEXT
)

-- CVE alerts and system messages
notifications (
  id INTEGER PRIMARY KEY,
  session_id TEXT,
  message TEXT, severity TEXT,       -- 'info' | 'warning' | 'critical'
  read_flag INTEGER DEFAULT 0,
  created_at TIMESTAMP
)

-- Risk treatment decisions per risk item
treatment_plans (
  id INTEGER PRIMARY KEY,
  session_id TEXT, asset_name TEXT, threat_name TEXT,  -- UNIQUE triple
  strategy TEXT,                     -- 'Mitigate' | 'Accept' | 'Transfer' | 'Avoid'
  owner TEXT, due_date TEXT,
  status TEXT,                       -- 'Pending' | 'In Progress' | 'Completed' | 'Accepted'
  notes TEXT,
  created_at TIMESTAMP, updated_at TIMESTAMP
)
```

---

## 6. Core Risk Engine — Formulas Explained

File: [backend/modules/risk_engine.py](backend/modules/risk_engine.py)

This is the mathematical heart of the platform. It implements two frameworks side-by-side.

### 6.1 NIST SP 800-30 (Monetary Risk)

Produces dollar amounts that executives understand.

```
SLE  = Asset Value (USD) × Exposure Factor (0–1)
       "How much money is lost in a single incident?"

ALE  = SLE × ARO
       "How much money is lost per year on average?"

Risk Score = (Probability × Vulnerability) − Mitigation + Uncertainty
             Range: 0.0 to 6.0
             "Composite risk metric accounting for current controls"
```

### 6.2 AssessITS (Impact Scoring — arXiv:2410.01750)

Produces a standardised 1–250 score for cross-organisation benchmarking.

```
Asset Scale     = normalise(value_usd, max=$1M) → 1.0 to 5.0

Threat Value    = Threat Level (1–5) + Vulnerability Score (1–5)
                  Range: 2 to 10

Likelihood      = ARO clamped to 0–5

Risk Impact Rating = Asset Scale × Threat Value × Likelihood
                     Range: 1 to 250

Criticality:
  Rating 1–45   → Low
  Rating 46–99  → Medium
  Rating 100–199→ High
  Rating 200–250→ Critical
```

### 6.3 Cost-Benefit Analysis

```
CBA = ALE_before_control − ALE_after_control − Annual_Control_Cost
      If CBA > 0 → control is cost-effective (recommend it)
      If CBA ≤ 0 → control costs more than the risk it removes
```

### 6.4 Assessment Pipeline

```python
# Pseudocode for what happens when "Run Assessment" is clicked

assets_with_threats = db.get_assets_with_threats(session_id)

risk_register = []
for asset in assets_with_threats:
    for threat in asset.threats:
        validate_inputs(asset, threat)          # raises ValueError on bad data

        sle    = asset.value_usd * threat.exposure_factor
        ale    = sle * threat.aro
        r      = (threat.probability * threat.vulnerability_score)
                 - threat.mitigation_effectiveness + threat.uncertainty

        asset_scale = normalise(asset.value_usd)
        tv          = threat.threat_level + threat.vulnerability_score
        rating      = asset_scale * tv * min(threat.aro, 5)
        criticality = classify(rating)

        ale_after = sle * threat.aro * (1 - threat.mitigation_effectiveness)
        cba       = ale - ale_after - estimated_control_cost

        risk_register.append({all metrics})

risk_register.sort(key=lambda x: x["impact_rating"], reverse=True)

llm_input = risk_register[:5]   # Top 5 risks only (keep prompt small)
recommendations = claude_api(llm_input) or fallback_json(llm_input)

db.save_assessment(session_id, risk_register, recommendations)
```

---

## 7. CVE Fetcher — How CVE Enrichment Works

File: [backend/modules/cve_fetcher.py](backend/modules/cve_fetcher.py)

### 7.1 Live Path (NVD API v2.0)

```
Input:  asset_name, software (e.g. "nginx", "windows", "mysql")
URL:    https://services.nvd.nist.gov/rest/json/cves/2.0
        ?keywordSearch={software}&resultsPerPage=5
Headers: nvdApiKey (optional; rate limit is 5 req/30s without key)

Output per CVE:
  - CVE ID (e.g. "CVE-2024-38063")
  - Description (first sentence)
  - CVSS Score (0.0–10.0)
  - Severity: Critical (9+), High (7–8.9), Medium (4–6.9), Low (<4)
  - Published date
  - NVD URL
```

### 7.2 Offline Fallback

If the NVD API is unreachable, `mock_cves.json` is loaded.
Keyword matching: if "windows" is in the software string → windows CVEs, etc.
Default bucket used if no keyword matches.

### 7.3 Background Thread (Flask mode only)

A daemon thread runs at Flask startup and re-checks CVEs every 24 hours.
New Critical CVEs are written to the `notifications` table.

---

## 8. LLM Advisor — How AI Recommendations Work

File: [backend/modules/llm_advisor.py](backend/modules/llm_advisor.py)

### 8.1 Claude API Path

```
Model: claude-haiku-4-5-20251001  (fast, cheap, sufficient for structured output)
Input: Top 5 risks from the risk register (JSON)

System prompt:
  "You are an information security expert. Given the top risks,
   recommend specific NIST SP 800-53 control IDs.
   Return JSON: {recommendations: [{
     control_id, control_name, plain_english_explanation,
     implementation_priority, estimated_cost_range, mapped_risk
   }]}"

Output parsing:
  - Strip markdown code fences if present (```json ... ```)
  - Parse JSON
  - Tag source = "claude"
```

### 8.2 Rule-Based Fallback

When `ANTHROPIC_API_KEY` is not set (or API call fails):
- Load `fallback_controls.json`
- Find the highest criticality level in the risk register
- Return the pre-mapped controls for that criticality bucket
- Tag source = "fallback"

This means the platform works fully offline for demos.

---

## 9. PDF Reports — What Gets Generated

File: [backend/modules/report_generator.py](backend/modules/report_generator.py)

All three PDFs are generated in-memory (BytesIO) using ReportLab and streamed directly to the
browser as a download. No temporary files are written to disk.

### Report 1: Risk Register PDF
- Executive summary paragraph
- Full risk table: Asset | Threat | SLE | ALE | Risk Score | Criticality | CBA Recommendation
- Criticality pie chart (donut)
- Top 10 risks bar chart
- Bibliography

### Report 2: Cost-Benefit Analysis (CBA) PDF
- Control recommendations from Claude/fallback
- Financial impact per risk
- Controls ranked by CBA value

### Report 3: Compliance PDF
- All 20 NIST SP 800-53 controls with status (Implemented / Partial / Not Implemented)
- Overall compliance score as a percentage
- Gap analysis section

**Colour coding used across all PDFs:**
- Critical → #DC2626 (red)
- High     → #EA580C (orange)
- Medium   → #CA8A04 (amber)
- Low      → #16A34A (green)

---

## 10. Session Model — How Multi-User Isolation Works

There is **no user authentication**. Instead, a random UUID is generated once per browser session
and stored in `st.session_state["session_id"]`. Every database query includes
`WHERE session_id = ?`. Two users with different UUIDs see completely separate data.

This is a design choice appropriate for a demo/capstone tool. For production with real
organisational data, this would need to be replaced with proper auth.

---

## 11. Security Controls

### Input Validation (`backend/utils.py`)
- All string fields: max length enforced, HTML characters escaped
- Numeric fields: range-checked (e.g. probability must be 0–1)
- Validated at the service layer before any DB write

### SQL Injection Prevention (`backend/database/models.py`)
- Every query uses `?` placeholders — no string interpolation
- Example: `cursor.execute("SELECT * FROM assets WHERE session_id = ?", (session_id,))`

### XSS Prevention (`backend/utils.py`)
- `escape_output(value)` recursively HTML-escapes all API response values
- Applied to every Flask route response

### Rate Limiting (`backend/utils.py`)
- `@rate_limit(max_requests=100, window_seconds=60)` decorator on Flask routes
- Per-IP token bucket in memory
- Returns HTTP 429 if exceeded

---

## 12. Streamlit Pages — Detailed UI Flow

### app.py — Landing / Executive Dashboard

**Before first assessment:** Hero text, 3-step quick-start cards, teaser grid of 6 modules.

**After assessment exists:** Four stat cards (Total ALE, Risk Items, Compliance %, CVE Alerts),
criticality pie + top-risks bar chart, recent CVE alert cards.

---

### 1_Assessment.py — Input

1. Enter organisation name
2. Choose: manual entry | Load Demo Data | Upload CSV
3. **Asset form:** Name, Type, Value (USD), Description, Software/OS
4. **Threat form** (per asset):
   - Category (Adversarial / Natural / Structural / Environmental / Accidental / Technical Failure)
   - NIST params: Probability, Vulnerability Score, Mitigation Effectiveness, ARO, Exposure Factor,
     Uncertainty, Threat Level
5. Click "Run Assessment" → triggers the pipeline in Section 6.4 above

---

### 2_Results.py — Dashboard

- Stat cards: Total Assets, Total Threats, Total ALE (USD), Highest Risk Item
- CVE alert banner (top 3 new alerts)
- **Charts (Plotly):**
  - Criticality donut (Critical slice pulled out for emphasis)
  - Top 10 risks bar (Impact Rating, reference line at criticality boundary)
  - Risk heatmap (asset rows × criticality columns)
  - ALE by asset (bar chart, USD)
- **Risk Register table:** sortable + filterable, all metrics shown
- **Control Recommendations:** cards from Claude or fallback (control ID, name, priority,
  cost range, plain-English explanation)
- **Download buttons:** Risk Register PDF, CBA PDF, Compliance PDF

---

### 3_Threat_Intelligence.py — CVE Feed

- Asset selector dropdown (only assets with software defined appear)
- "Fetch CVEs" button → calls NVD API (or offline fallback)
- CVE cards: ID, severity badge, CVSS score, description, published date, NVD link
- Border colour matches severity (red/orange/amber/green)
- Keyword search box → arbitrary NVD query

---

### 4_Treatment_Plan.py — Remediation Tracker

For each risk in the register, an inline-editable row:
- Strategy: Mitigate | Accept | Transfer | Avoid
- Owner (free text)
- Due date
- Status: Pending | In Progress | Completed | Accepted
- Notes (free text)

Changes are auto-saved to the `treatment_plans` table on each edit.
Charts: status donut, strategy breakdown bar.

---

### 5_History.py — Trend Analysis

- Lists every past assessment run (expandable: full risk register for that run)
- ALE trend line chart across all runs
- Delta card: latest ALE vs previous run (+/- %)

---

### 6_Methodology.py — Educational Content

Static documentation page covering:
- Framework alignment (NIST SP 800-30, AssessITS, ISO 27001)
- All formulas with worked examples
- Architecture diagram (ASCII)
- Database schema
- Risk treatment strategies
- Full bibliography

---

## 13. Environment Variables

```ini
# Required for AI recommendations (optional — fallback works without it)
ANTHROPIC_API_KEY=sk-ant-...

# Required for Flask mode (not needed for Streamlit-only use)
FLASK_SECRET_KEY=any-random-string
FLASK_PORT=5000

# Optional — higher NVD rate limit (default 5 req/30s without key)
NVD_API_KEY=nvd-hmac-...

# Database location (default: backend/database/risk_platform.db)
DATABASE_PATH=./backend/database/risk_platform.db

# 'development' enables Flask debug mode
FLASK_ENV=development
```

---

## 14. Running the Project

### Streamlit (primary — this is the main app)

```powershell
cd "c:\Users\PC\Desktop\Uni work\IS Project"
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env          # then add ANTHROPIC_API_KEY
streamlit run app.py
# Opens at http://localhost:8501
```

### Flask REST API (optional)

```powershell
cd backend
python app.py
# Runs at http://localhost:5000
# Health check: GET http://localhost:5000/api/health
```

### Tests

```powershell
cd backend
pytest -v
```

### Streamlit Cloud Deployment

1. Push to GitHub
2. Go to share.streamlit.io → New App → point to `app.py`
3. Add `ANTHROPIC_API_KEY` in the Secrets panel
4. **Note:** SQLite data is reset on every redeploy. Use "Load Demo Data" for live demos.

---

## 15. Flask REST API Reference (Optional Module)

All responses: `{ "success": bool, "data": any, "error": string | null }`

All endpoints require `session_id` as query param or `X-Session-Id` header.

| Method | Path | Description |
|---|---|---|
| GET | /api/health | Health check |
| POST | /api/assets | Create asset |
| GET | /api/assets | List assets |
| GET | /api/assets/\<id\> | Get asset |
| PUT | /api/assets/\<id\> | Update asset |
| DELETE | /api/assets/\<id\> | Delete asset |
| POST | /api/threats | Create threat |
| GET | /api/threats | List threats |
| PUT | /api/threats/\<id\> | Update threat |
| DELETE | /api/threats/\<id\> | Delete threat |
| POST | /api/assessment/run | Run full assessment |
| GET | /api/assessment/results | Get latest results |
| GET | /api/assessment/notifications | Get CVE alerts |
| GET | /api/compliance | Get compliance checklist |
| POST | /api/compliance | Update control status |
| GET | /api/reports/risk-register | Download Risk Register PDF |
| GET | /api/reports/cba | Download CBA PDF |
| GET | /api/reports/compliance | Download Compliance PDF |
| POST | /api/demo/seed | Seed demo data for session |

---

## 16. Sample Dataset (`data/assessits_sample_inventory.csv`)

20 rows representing 10 assets × 2 threats each. Columns:

```
asset_name, asset_type, value_usd, description, software,
threat_name, threat_category,
probability, vulnerability_score, mitigation_effectiveness,
aro, exposure_factor, uncertainty, threat_level
```

Sample assets: Web App Server (nginx), Customer Database (mysql), HR System (sap),
Network Perimeter (fortios), Employee Laptops (windows), Cloud Storage (aws-s3),
VPN Gateway (cisco), Email Server (exchange), Payroll System (linux), Backup System (veritas).

This dataset is used by the "Load Demo Data" button to pre-populate a session for demonstration.

---

## 17. Academic Foundations

| Framework | Reference | What it contributes |
|---|---|---|
| NIST SP 800-30 Rev. 1 (2012) | NIST Guide for Conducting Risk Assessments | SLE, ALE, ARO, Exposure Factor formulas |
| AssessITS (2024) | Rahman et al., arXiv:2410.01750 | Asset Scale, Threat Value, Risk Impact Rating 1–250 |
| NIST SP 800-53 Rev. 4 (2013) | NIST Security and Privacy Controls | 20-control compliance checklist |
| ISO/IEC 27001:2022 | ISMS requirements | Risk treatment strategy (Mitigate/Accept/Transfer/Avoid) |

---

## 18. Known Limitations

1. **SQLite on Streamlit Cloud:** Data is ephemeral — resets on each redeploy.
2. **No authentication:** Session isolation by UUID only; not suitable for sensitive production data.
3. **NVD rate limit:** Without an API key, limited to 5 requests per 30 seconds.
4. **Claude API cost:** claude-haiku is used to keep costs low; more nuanced recommendations
   would require a larger model.
5. **React frontend (`frontend/` folder):** Exists in the repo as a legacy artifact from early
   development; it is NOT used. The Streamlit app is the live product.

---

## 19. Key Design Patterns

- **Fallback everywhere:** Every external service (Claude API, NVD API) has a static JSON fallback
  so the platform works in fully offline/demo mode with no API keys.
- **Session scoping:** Every DB query is `WHERE session_id = ?` — no shared mutable state between
  users.
- **Separation of concerns:** UI pages call `streamlit_lib/services.py`, which calls
  `backend/modules/`, which calls `backend/database/models.py`. No page imports models directly.
- **Stateless REST:** Flask routes read session_id from request headers/params, not server-side
  session storage, making them horizontally scalable.
- **Parameterised SQL only:** Zero raw string interpolation in any query in the codebase.
