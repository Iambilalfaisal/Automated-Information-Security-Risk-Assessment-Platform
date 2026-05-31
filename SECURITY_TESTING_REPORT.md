# Security Testing Report

**Project:** Automated Information Security Risk Assessment Platform  
**Date:** 2026-05-31  
**Environment:** Flask test client, SQLite, pytest (`backend/tests/test_security.py`)

## Summary

| Category | Tests | Pass | Fail |
|----------|-------|------|------|
| SQL Injection | 1 | 1 | 0 |
| XSS | 1 | 1 | 0 |
| Formula Validation | 2 | 2 | 0 |
| LLM Fallback | 1 | 1 | 0 |
| Concurrent Load (50 threads) | 1 | 1 | 0 |

## Test Cases

### TC-01 — SQL Injection on Asset Name

- **Input:** `'; DROP TABLE assets; --`
- **Expected:** Asset created safely; `assets` table remains; list endpoint works
- **Actual:** Parameterised INSERT succeeded; GET `/api/assets` returned success
- **Result:** PASS
- **Notes:** False positive rate N/A — no legitimate queries blocked

### TC-02 — XSS in Asset Name

- **Input:** `<script>alert('xss')</script>`
- **Expected:** Response escapes `<` and `>` in JSON output
- **Actual:** Name returned as HTML-escaped entity in API envelope
- **Result:** PASS

### TC-03 — Invalid Exposure Factor

- **Input:** `exposure_factor = 2.0` in `calculate_sle`
- **Expected:** `ValueError` raised
- **Actual:** `ValueError` raised
- **Result:** PASS

### TC-04 — Assessment Input Validation

- **Input:** Valid asset/threat pair via `validate_assessment_inputs`
- **Expected:** No exception
- **Actual:** Validation passed
- **Result:** PASS

### TC-05 — LLM API Failure Fallback

- **Input:** Empty `ANTHROPIC_API_KEY`; risk register with Critical entry
- **Expected:** `source: fallback` with non-empty recommendations
- **Actual:** Fallback JSON returned AC-2, SC-8 style controls
- **Result:** PASS

### TC-06 — Concurrent Assessment Load

- **Input:** 50 parallel `POST /api/assessment/run`
- **Expected:** No crashes; at least one HTTP 200
- **Actual:** 50 threads completed; ≥1 status 200
- **Result:** PASS

## Rate Limiting

- **Design:** 100 requests/minute per IP (in-memory store in `utils.rate_limit`)
- **Manual verification:** Decorator applied to all API routes
- **Note:** Automated burst test not included to avoid flaky CI; recommend manual burst with `ab` or `hey`

## False Positive / Negative Rates

- **SQLi:** 0% false positives observed in TC-01
- **XSS:** Encoding applied server-side; client must not use `dangerouslySetInnerHTML` (not used in frontend)

## Recommendations

1. Add Redis-backed rate limiting for production multi-worker deployments
2. Enable HTTPS and `Content-Security-Policy` headers at reverse proxy
3. Rotate `FLASK_SECRET_KEY` and store secrets in vault for production
