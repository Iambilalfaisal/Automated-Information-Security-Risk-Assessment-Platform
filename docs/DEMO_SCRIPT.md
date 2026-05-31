# 10-Minute Video Demo Script

Project: Automated Information Security Risk Assessment Platform
Use this as the storyboard for the recorded demo (Phase 5 deliverable).

## Setup (before recording)
- Terminal 1: `cd backend; .\venv\Scripts\activate; python app.py`
- Terminal 2: `cd frontend; npm run dev`
- Open the browser at the Vite URL (default `http://localhost:5173`).
- Have the generated `docs/Technical_Report.docx` ready to show briefly.

## Timeline

### 0:00 - 0:45 Introduction
- State the problem: organisations need objective, quantitative risk assessment.
- One sentence on the approach: NIST SP 800-30 + AssessITS, automated, with CVE and LLM advisory.
- Mention the tech stack (Flask + SQLite backend, React + Tailwind + Recharts frontend).

### 0:45 - 2:00 Home and Asset Entry
- Show the Home page and click Start Assessment.
- On the Assessment page, click "Load Demo Data" to populate five realistic assets and eight threats.
- Briefly add one asset manually (e.g. "Backup Server", Software, $120,000, software "linux") to show the multi-step form and the CVEs returned for that asset with severity colour coding.

### 2:00 - 3:30 Threats and Formulas
- Add a threat to the new asset using the sliders (Probability, Vulnerability, Mitigation, ARO, Exposure Factor).
- Explain on screen the four formulas: SLE, ALE, R = P*V - M + U, and the AssessITS Risk Impact Rating (1-250 band).

### 3:30 - 5:30 Run Assessment and Dashboard
- Click "Run Assessment".
- Go to Results. Walk through:
  - Summary cards (total assets, threats, highest risk, total ALE).
  - Bar chart of Risk Impact Rating by asset.
  - Likelihood-vs-impact heat map.
  - Sortable/filterable risk register table with criticality colour coding.
  - Control recommendations (note the source label: claude or fallback).

### 5:30 - 6:30 Compliance Checklist
- Scroll to the NIST 800-30 compliance checklist.
- Toggle a few controls between Implemented / Partial / Not Implemented.
- Show the compliance percentage and gap count updating live.

### 6:30 - 7:30 PDF Reports
- Click each of the three download buttons: Risk Register PDF, CBA PDF, Compliance PDF.
- Open the Risk Register PDF and show the colour-coded table, charts, and references footer.

### 7:30 - 8:30 Security Testing
- Switch to a terminal and run `cd backend; .\venv\Scripts\pytest -v`.
- Point out the SQL injection, XSS, rate-limit, validation, LLM-fallback, and 50-thread load tests passing.
- Reference `SECURITY_TESTING_REPORT.md`.

### 8:30 - 9:30 Technical Report and Code Quality
- Briefly open `docs/Technical_Report.docx` to show the IEEE-format report with figures generated from real data.
- Show the GitHub commit history demonstrating incremental progress.

### 9:30 - 10:00 Wrap-up
- Recap objectives met.
- Mention future work (multi-user auth, Monte Carlo loss, CPE-based CVE matching).

## Tips
- Record at 1080p, narrate clearly, keep the cursor movements deliberate.
- If CVE/LLM are offline, mention that the platform falls back to bundled data by design.
