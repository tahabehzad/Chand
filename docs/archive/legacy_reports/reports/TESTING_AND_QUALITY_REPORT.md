# TESTING_AND_QUALITY_REPORT.md

Testing and Quality Report — Pish Hesabdari

## 1. Quality Gate Results

| Gate | Command | Result | Details |
|------|---------|--------|---------|
| Frontend TypeScript | `npx tsc --noEmit -p tsconfig.app.json` | ✅ PASS | 0 errors |
| Frontend production build | `npx vite build` | ✅ PASS | Built in 11.30s |
| Frontend tests | `npx vitest run` | ⚠️ PARTIAL | 125 passed, 3 failed (pre-existing nav duplication bugs) |
| Backend ruff | `.\.venv\Scripts\python.exe -m ruff check .` | ⚠️ PARTIAL | 0 errors in estimation modules; 24 pre-existing errors in `create_first_user.py`, `debug_api.py` |
| Backend mypy | `.\.venv\Scripts\python.exe -m mypy --strict app/domain/salary_estimation ...` | ✅ PASS | 0 issues on estimation modules |
| Backend pytest | `.\.venv\Scripts\python.exe -m pytest --ignore=tests/integration --ignore=tests/api/test_manager_workspace.py` | ✅ PASS | 761 passed, 1 skipped |
| Backend e2e salary estimation | `.\.venv\Scripts\python.exe -m pytest tests/e2e/test_salary_estimation_api.py` | ✅ PASS | 7 passed |

## 2. Frontend Test Details

**Passed (125 tests across 14 files):**
- `src/api/client.test.ts` — 12 tests
- `src/prototype/api.test.ts` — 8 tests
- `src/lib/money.test.ts` — 23 tests
- `src/test/logical-utilities-gate.test.ts` — 9 tests
- `src/routes/work-profile-fields.test.tsx` — 3 tests
- `src/routes/simulation-page.test.tsx` — 9 tests
- `src/lib/numerals.test.ts` — 12 tests
- `src/components/icon.test.tsx` — 6 tests
- `src/components/ui/states.test.tsx` — 5 tests
- `src/app/mvp-navigation.test.tsx` — 3 tests
- `src/lib/calendar.test.ts` — 7 tests
- `src/api/provenance.test.ts` — 6 tests
- `src/api/contracts.test.ts` — 6 tests (updated to include `estimations.create`)
- `src/lib/text.test.ts` — 6 tests

**Failed (3 tests, all pre-existing):**
- `src/app/app-shell.test.tsx` — "links every primary screen directly in the main navigation" — duplicate "بازار حقوق" links in navigation
- `src/app/app-shell.test.tsx` — "links every deferred module in the collapsed section" — same duplication
- `src/app/app-shell.test.tsx` — "never links two navigation entries to the same path" — same duplication

These failures are PRE-EXISTING navigation bugs, not caused by our changes. The navigation component renders two links to `/salaries` with the same text.

## 3. Backend Test Details

**Passed (761 tests):**
- All unit tests in `tests/unit/`
- All API tests in `tests/api/` (except `test_manager_workspace.py` which requires PostgreSQL)
- All e2e salary estimation tests: 7/7 passed

**Skipped (1 test):**
- `tests/api/test_openapi_contract.py:85` — schemathesis generated a contract-valid request

**Not run (integration tests):**
- All `tests/integration/*` — require PostgreSQL database (not available in this environment)
- All `tests/api/test_manager_workspace.py` — requires PostgreSQL

## 4. E2E Salary Estimation Test Results

| Test | Result | Notes |
|------|--------|-------|
| test_estimate_salary_valid_request | ✅ PASS | Returns 200 with valid estimate |
| test_estimate_salary_insufficient_data | ✅ PASS | Returns 409 with `ESTIMATION_INSUFFICIENT_DATA` |
| test_estimate_salary_response_fields | ✅ PASS | All required fields present |
| test_money_path_range_consistency | ✅ PASS | min <= primary <= max; skips 409 cities |
| test_estimate_salary_missing_required_field | ✅ PASS | Returns 422 for empty job_title |
| test_estimate_salary_extra_field_rejected | ✅ PASS | Returns 422 for unknown fields |
| test_estimate_salary_invalid_seniority | ✅ PASS | Returns 422 for invalid seniority |

## 5. Money Path Verification

| Property | Verification | Result |
|----------|-------------|--------|
| Decimal only (no float) | Code review of `salary_estimator.py` | ✅ All multipliers are `Decimal` |
| ROUND_HALF_UP only | `round_half_up()` from `app.engines.money` | ✅ Used for all rounding |
| No `round()` on money | Code review | ✅ No Python `round()` calls |
| Round once at boundary | Single `round_half_up` per figure | ✅ |
| Currency unit consistency | Internal Rial, display Toman | ✅ |

## 6. Insufficient Data Verification

| Scenario | Expected | Actual | Result |
|----------|----------|--------|--------|
| Unknown city | 409 `ESTIMATION_INSUFFICIENT_DATA` | 409 | ✅ |
| Unknown job title | 409 `ESTIMATION_INSUFFICIENT_DATA` | 409 | ✅ |
| Mismatched seniority | 409 `ESTIMATION_INSUFFICIENT_DATA` | 409 | ✅ |
| No market data for city+job+seniority | 409 `ESTIMATION_INSUFFICIENT_DATA` | 409 | ✅ |

## 7. Known Test Gaps

| Gap | Reason |
|-----|--------|
| No frontend unit tests for SalaryEstimationForm | Not yet written (P2 task) |
| No frontend unit tests for SalaryEstimationResults | Not yet written (P2 task) |
| No integration tests (PostgreSQL not available) | Environment limitation |
| No end-to-end browser tests | Not yet set up |

## 8. Test Commands and Exit Codes

```
Frontend TypeScript:   npx tsc --noEmit -p tsconfig.app.json     → exit 0
Frontend build:        npx vite build                             → exit 0
Frontend tests:        npx vitest run                             → exit 1 (3 pre-existing failures)
Backend ruff:          ruff check .                               → exit 1 (24 pre-existing errors in unrelated files)
Backend mypy:          mypy --strict app/domain/salary_estimation → exit 0
Backend pytest:        pytest --ignore=tests/integration ...      → exit 0 (761 passed)
Backend e2e:           pytest tests/e2e/test_salary_estimation_api.py → exit 0 (7 passed)
```
