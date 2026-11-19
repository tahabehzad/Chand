# PROJECT_CURRENT_STATE.md

Verified current state of the Pish Hesabdari repository as of 2026-11-18.

## Repository Root

`C:\project\New project`

## Frontend Structure

| Path | Status | Notes |
|------|--------|-------|
| `frontend/src/components/salary-estimation/SalaryEstimationPage.tsx` | FIXED | Was corrupted with `{v1.0}`, `window.apiClient`, missing `Badge` import. Now compiles. |
| `frontend/src/components/salary-estimation/SalaryEstimationForm.tsx` | FIXED | Used removed `react-hook-form/zod`. Rewritten with native React state, `Input` component with `label` prop, `Badge` with `tone` prop. |
| `frontend/src/components/salary-estimation/SalaryEstimationResults.tsx` | FIXED | Had Korean characters, float-based formatting, incorrect confidence bar. Rewritten with Persian text, `MoneyResult`-safe formatting. |
| `frontend/src/components/salary-discovery/SalaryDiscoveryPage.tsx` | FIXED | Had Cyrillic text, `useEffect`/`Input`/`toPersianDigits` unused imports, `Badge` `variant`→`tone`, `Button variant='outline'`→`'secondary'`, `formatMoney(...).value` union type not handled. Rewritten with native selects. |
| `frontend/src/components/salary-discovery/SalaryResultCard.tsx` | FIXED | Imported `ReactNode` as value, missing `Card` imports. Fixed. |
| `frontend/src/lib/salary-benchmarks.ts` | FIXED | Line 99 had invalid text `man's experience range' to 'maximum'`. Lines 263-265 had `number \| undefined` issues. Fixed with `?? 0`. |
| `frontend/src/api/salary-estimation.ts` | FIXED | `client.request()` returns `ApiResponse<T>`, not `T`. Added `.then(r => r.data)`. Removed unused `apiClient` import. |
| `frontend/src/components/ui/badge.tsx` | UNCHANGED | Uses `tone` prop (neutral\|info\|warning\|danger\|success), NOT `variant`. |
| `frontend/src/components/ui/input.tsx` | UNCHANGED | Uses `label` prop, generates its own `id`. No `id` prop accepted. |
| `frontend/src/components/ui/button.tsx` | UNCHANGED | Uses `variant` (primary\|secondary\|ghost\|danger), `size`. |

**TypeScript (`tsc --noEmit -p tsconfig.app.json`)**: ✅ Passes (0 errors)

**Vitest**: 125 passed, 3 failed — all 3 failures are in `app-shell.test.tsx` due to duplicate "بازار حقوق" nav links (pre-existing, not caused by our changes).

**Vite production build**: ✅ Passes

## Backend Structure

| Path | Status | Notes |
|------|--------|-------|
| `backend/app/domain/salary_estimation/schemas.py` | FIXED | Pydantic v1 `@validator` → v2 `field_validator`. `education` made optional (`str \| None`). City validation removed allowed-values restriction (matcher handles insufficiency). |
| `backend/app/domain/salary_estimation/salary_estimator.py` | FIXED | Float multipliers → `Decimal`. Case-sensitive city → normalized lowercase. Hardcoded legal wage → loaded from 1404 rule set. Zeros-on-insufficient-data → `ValueError` refusal. Hardcoded data sources → actual sources from profile. Fake `rule_set_status="ACTIVE"` → from rule set. |
| `backend/app/domain/salary_estimation/matcher.py` | FIXED | Fuzzy word-overlap matching → deterministic exact match on job_title+seniority+city. Underscores normalized to spaces for job title lookup. |
| `backend/app/domain/salary_estimation/mock_data.py` | UNCHANGED | Dead code, not imported anywhere. |
| `backend/app/domain/salary_estimation/adjust.py` | FIXED | Broken import `backend.app.engines.money` → `app.engines.money`. Dead code, not imported. |
| `backend/app/domain/salary_estimation/__init__.py` | FIXED | `SalaryMatcher` imported from `.matcher` (was incorrectly from `.salary_estimator`). |
| `backend/app/services/estimation/service.py` | FIXED | Removed unused `MarketDataRow` import. Fixed Persian typo "دستمzd" → "دستمزد". `rule_set_status` from domain result. |
| `backend/app/api/v1/estimation/__init__.py` | FIXED | No exception leak (generic `Exception` caught separately). `ValueError` with `insufficient_data:` prefix → HTTP 409. Other errors → 422 with generic message. |
| `backend/app/schemas/estimation.py` | FIXED | `list[dict]` → `list[dict[str, Any]]`. Added `Any` to typing import. `__all__` sorted. |
| `backend/app/engines/money.py` | UNCHANGED | `round_half_up`, `to_decimal` used by estimator. |
| `backend/app/engines/rules.py` | UNCHANGED | `load_rule_set(1404)` returns `StatutoryRuleSet` with `monthly_minimum_wage_30days_rial = 103909680`. |

**Ruff (`ruff check .`)**: 24 errors remaining, all in pre-existing files `create_first_user.py` and `debug_api.py` (hardcoded password, `print` statements, import sorting). Zero errors in estimation modules.

**Mypy (`--strict`)**: ✅ Passes on `app/domain/salary_estimation`, `app/services/estimation`, `app/schemas/estimation.py`, `app/api/v1/estimation`.

**Pytest**: 761 passed, 1 skipped, 0 failed. Integration tests skipped (no PostgreSQL available). E2E salary estimation tests: 7 passed.

## Database

| Item | Status | Notes |
|------|--------|-------|
| `backend/data/seeds/statutory_rules_1404.yaml` | UNCHANGED | Verified source of truth for 1404 minimum wage: `monthly_minimum_wage_30days_rial: 103909680`. |
| Migrations | UNCHANGED | No changes made. Integration tests require PostgreSQL (not available in this environment). |
| `models/estimation.py` | UNCHANGED | DB-04: no migration exists for this model. Not part of current MVP path. |

## Authentication / Security

| Item | Status | Notes |
|------|--------|-------|
| `backend/create_first_user.py` | UNCHANGED | Contains hardcoded bootstrap password `PishHesabdari2026!` (S105). Pre-existing. Not modified per instruction not to run destructive/credential operations without approval. |
| API authentication | NOT IMPLEMENTED | D-02 decision is OPEN — no auth dependency on estimation endpoint. |

## Key Files Modified

**Frontend:**
- `frontend/src/components/salary-estimation/SalaryEstimationPage.tsx`
- `frontend/src/components/salary-estimation/SalaryEstimationForm.tsx`
- `frontend/src/components/salary-estimation/SalaryEstimationResults.tsx`
- `frontend/src/components/salary-discovery/SalaryDiscoveryPage.tsx`
- `frontend/src/components/salary-discovery/SalaryResultCard.tsx`
- `frontend/src/lib/salary-benchmarks.ts`
- `frontend/src/api/salary-estimation.ts`
- `frontend/src/api/contracts.test.ts` (test update for new delivered contract)

**Backend:**
- `backend/app/domain/salary_estimation/schemas.py`
- `backend/app/domain/salary_estimation/salary_estimator.py`
- `backend/app/domain/salary_estimation/matcher.py`
- `backend/app/domain/salary_estimation/adjust.py` (import path only)
- `backend/app/domain/salary_estimation/__init__.py`
- `backend/app/services/estimation/service.py`
- `backend/app/api/v1/estimation/__init__.py`
- `backend/app/schemas/estimation.py`
- `backend/tests/e2e/test_salary_estimation_api.py` (test updates for 409 refusal behavior)
