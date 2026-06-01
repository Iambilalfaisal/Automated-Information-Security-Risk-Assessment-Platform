# 10-Minute Video Demo Script

Project: Automated Information Security Risk Assessment Platform  
UI: **Streamlit** (`streamlit run app.py`)

## Setup (before recording)

```powershell
cd "c:\Users\PC\Desktop\Uni work\IS Project"
.\venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Open **http://localhost:8501** (or your Streamlit Cloud public URL).

## Timeline

### 0:00 - 0:45 Introduction
- Problem: organisations need objective quantitative risk assessment.
- Solution: NIST SP 800-30 + AssessITS, CVE intelligence, LLM control advice, PDF reports.
- Stack: Streamlit UI + Python backend (SQLite).

### 0:45 - 2:30 Assessment page
- Sidebar → **Assessment**.
- Click **Load Demo Data** (5 assets, 8 threats).
- Optionally add one asset manually and show CVE list after submit.
- Show threat sliders (P, V, M, ARO, exposure %).
- Set organisation name.
- Click **Run Assessment**.

### 2:30 - 5:00 Results page
- Sidebar → **Results**.
- Walk through metrics: assets, threats, total ALE, highest risk.
- Show pie chart (criticality), bar chart (top risks), ALE by asset.
- Scroll the risk register table; use filter box.
- Expand control recommendations (note fallback vs Claude if applicable).

### 5:00 - 6:00 Compliance & PDFs
- Download **Risk Register**, **CBA**, and **Compliance** PDFs.
- Open Risk Register PDF briefly (colour-coded table).
- Toggle a few NIST compliance controls; show % updating.

### 6:00 - 7:30 Security & code
- Terminal: `cd backend; pytest -v` (19 tests).
- Mention `SECURITY_TESTING_REPORT.md`.
- Optional: show GitHub commit history.

### 7:30 - 8:30 Report & deploy
- Show `docs/Technical_Report.docx` (IEEE format).
- If deployed: show Streamlit Cloud URL for public access.

### 8:30 - 10:00 Wrap-up
- Objectives met; future work (auth, persistent DB on cloud).

## Streamlit Cloud tip
Record using your deployed app URL so viewers see a live public demo without local setup.
