# Viva Presentation Outline (Phase 7)

10-minute presentation + 5-minute Q&A. Suggested 10-11 slides, ~1 minute each.

## Slide 1 — Title
- Project title, team members and roll numbers, course code, supervisor, date.
- University logo.

## Slide 2 — Problem and Motivation
- SMEs lack accessible, objective quantitative risk tools.
- Manual NIST/ISO assessments are slow and inconsistent.

## Slide 3 — Objectives
- The six numbered objectives from the report (formulas, secure API, reports, CVE/LLM, dashboard, security testing).

## Slide 4 — Related Work and Gap
- One-line each: NIST SP 800-30, AssessITS, ISO 27005, FAIR, OCTAVE, CVSS, ATT&CK, LLM advisory.
- Gap: no single open tool combining quantitative formulas + CVE + LLM + reporting.

## Slide 5 — System Architecture
- Three-tier diagram (React -> Flask -> SQLite, plus risk engine, CVE, LLM, reports).
- Mention the {success, data, error} API envelope.

## Slide 6 — Core Algorithms
- SLE, ALE, R = P*V - M + U, AssessITS Risk Impact Rating (1-250) and criticality bands.
- Note the corrected scaling so ratings stay in band.

## Slide 7 — Live Demo (link to running app)
- Load demo data, run assessment, show dashboard, heat map, register.
- Show one PDF report.

## Slide 8 — Security Analysis
- STRIDE threat model mapped to controls.
- Test results table: SQLi, XSS, validation, rate limit, LLM fallback, load.

## Slide 9 — Results
- Charts: risk distribution, top risks, ALE by asset.
- Total ALE and highest risk from the demo inventory.

## Slide 10 — Conclusion and Future Work
- Objectives met; lessons learned (TDD caught the scaling bug; graceful fallbacks).
- Future: auth, Monte Carlo, CPE-based CVE matching, containerisation.

## Slide 11 — Q&A
- Be ready to explain: why quantitative vs qualitative, how AssessITS rating is bounded, how injection/XSS are prevented, how the LLM fallback works.

## Demo backup
- If the network is down, the CVE and LLM features fall back to bundled data — the demo still works fully offline.
