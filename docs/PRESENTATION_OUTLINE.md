# Viva Presentation Outline (Phase 7)

10-minute presentation + 5-minute Q&A. UI: **Streamlit** (local or Cloud URL).

## Slide 1 — Title
- Project title, team, course, supervisor, date.

## Slide 2 — Problem
- SMEs need accessible quantitative risk tools.

## Slide 3 — Objectives
- Six objectives (formulas, API/DB, reports, CVE/LLM, dashboard, security tests).

## Slide 4 — Architecture
- Streamlit UI → backend modules (risk engine, SQLite, PDF, CVE, LLM).
- Optional Flask API for REST clients.

## Slide 5 — Algorithms
- SLE, ALE, R = P×V−M+U, AssessITS 1–250 band.

## Slide 6 — Live demo
- Streamlit Cloud URL or localhost:8501.
- Load demo → run assessment → results → one PDF.

## Slide 7 — Security
- STRIDE mapping; pytest security suite (SQLi, XSS, load).

## Slide 8 — Results
- Sample chart: top risks from demo inventory.

## Slide 9 — Conclusion
- Deliverables: code, report, security doc, Streamlit deploy.

## Slide 10 — Q&A
- Be ready: AssessITS scaling, SQLite on Cloud, LLM fallback, deployment steps.

## Deploy talking points
1. Push repo to GitHub.
2. share.streamlit.io → New app → `app.py`.
3. Optional `ANTHROPIC_API_KEY` in Secrets.
