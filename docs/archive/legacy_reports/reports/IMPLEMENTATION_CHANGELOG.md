# IMPLEMENTATION_CHANGELOG.md

Implementation Changelog — Pish Hesabdari

Every code and documentation change made during this session.

## 2026-11-18 — Frontend Fixes

### SalaryEstimationPage.tsx
- Added missing `Badge` import from `@/components/ui/badge`
- Fixed `{v1.0}` syntax error → `'نسخه v1.0'`
- Replaced `window.apiClient` with imported `apiClient` from `@/api/instance`
- Fixed Persian text: `برآزۀ` → `برآورد`, `برآزه جدید` → `برآورد جدید`
- Removed unused `Card`, `CardContent`, `CardHeader`, `CardTitle` imports
- Fixed `Badge variant='outline'` → `tone='neutral'`
- Fixed `Button variant='outline'` → `variant='secondary'`
- Removed unused `isLoading` state
- Fixed type mismatch: `SalaryEstimationFormData` → `SalaryEstimationRequest` mapping

### SalaryEstimationForm.tsx
- Removed `react-hook-form` and `zod` dependencies (not installed)
- Rewritten with native React `useState` form state
- Fixed `Input` component usage: uses `label` prop (not separate label + `id`)
- Fixed `Badge` component: uses `tone` prop (not `variant`)
- Removed `onClick` from `Badge` (not supported); wrapped badges in `<span>` with `onClick`
- Added `education` field (required text input)
- Fixed Persian text throughout
- Added client-side validation with Persian error messages

### SalaryEstimationResults.tsx
- Removed Korean characters (`و로부터ی羽毛`) → proper Persian text
- Fixed float-based formatting → `Math.round()` for Rial conversion
- Fixed `Badge variant` → `Badge tone`
- Added `insufficient_data` state with danger-colored card
- Added `formatRial()` helper with `fa-IR` locale formatting
- Added calculation hash and timestamp display (collapsible)

### SalaryDiscoveryPage.tsx
- Fixed Cyrillic text at line 351
- Fixed `POPULAR_CITIES` array: `س-THAT` → `ساوه`
- Removed unused imports: `useEffect`, `Input`, `toPersianDigits`
- Removed unused `handleReset` function
- Replaced `Select` component (doesn't exist) with native `<select>`
- Fixed `Badge variant` → `Badge tone`; wrapped in `<span>` with `onClick`
- Fixed `Button variant='outline'` → `variant='secondary'`
- Fixed `formatMoney(...).value` union type handling → `moneyText()` helper
- Fixed `experience.split('-')` undefined handling

### SalaryResultCard.tsx
- Fixed `ReactNode` import: `import type { ReactNode }` (type-only)
- Added missing imports: `Card`, `CardContent`, `CardHeader`, `CardTitle`

### salary-benchmarks.ts
- Fixed line 99: `experienceRange: { min: 1, max: man's experience range' to 'maximum' }` → `{ min: 1, max: 3 }`
- Fixed lines 263-265: `allP25[0]` and `allP25[allP25.length - 1]` → `?? 0`
- Fixed line 263: `medianSalary: median` → `median ?? 0`

### salary-estimation.ts
- Fixed return type: `client.request()` returns `ApiResponse<T>`, added `.then(r => r.data)`
- Removed unused `apiClient` import from `@/api/instance`

### contracts.test.ts
- Updated expected delivered contracts: added `'estimations.create'`

## 2026-11-18 — Backend Fixes

### app/domain/salary_estimation/schemas.py
- Converted Pydantic v1 `@validator` classmethods to v2 `field_validator`
- Made `education` optional (`str \| None`, default None)
- Removed city allowed-values restriction (matcher handles insufficiency)
- Added `dict[str, Any]` type arguments to `to_dict` and `from_dict`

### app/domain/salary_estimation/salary_estimator.py
- Replaced float multipliers with `Decimal`
- Moved inline imports to top-level (`round_half_up`, `load_rule_set`)
- Removed unused `ROUND_HALF_UP` import
- Removed hardcoded legal wage (36,000,000) → loaded from `load_rule_set(1404)`
- Changed insufficient data behavior: returns `None` → raises `ValueError` → HTTP 409
- Changed data sources: only sources actually present in profile
- Changed `rule_set_status`: from rule set (not hardcoded "ACTIVE")
- Changed range calculation: `Decimal` with `ROUND_HALF_UP`
- Fixed `_calculate_employment_type_factor`: `part_time` (underscore) not `part-time`

### app/domain/salary_estimation/matcher.py
- Replaced fuzzy word-overlap matching with deterministic exact match
- Job title normalization: underscores → spaces before map lookup
- Seniority level: exact match against profile
- Data quality validation: `data_volume >= 10`, `recency_days <= 180`
- `calculate_confidence`: composite score from data volume, recency, experience, skills
- Fixed `no-any-return`: wrapped boolean return in `bool()`

### app/domain/salary_estimation/adjust.py
- Fixed broken import: `backend.app.engines.money` → `app.engines.money`

### app/domain/salary_estimation/__init__.py
- Fixed `SalaryMatcher` import: from `.matcher` (not from `.salary_estimator`)

### app/domain/salary_estimation/money_validation.py
- UNCHANGED (already correct)

### app/services/estimation/service.py
- Removed unused `MarketDataRow` import
- Fixed Persian typo: `دستمzd` → `دستمزد`
- `rule_set_status` from domain result (not hardcoded)

### app/api/v1/estimation/__init__.py
- Removed exception leak: generic `Exception` caught separately with generic message
- `ValueError` with `insufficient_data:` prefix → HTTP 409
- Other `ValueError` → HTTP 422
- Generic `Exception` → HTTP 422 with generic Persian message

### app/schemas/estimation.py
- Fixed `list[dict]` → `list[dict[str, Any]]`
- Added `Any` to typing import
- Sorted `__all__`

### tests/e2e/test_salary_estimation_api.py
- Updated `test_estimate_salary_insufficient_data`: expects 409 with error code, not 200 with zeros
- Updated `test_money_path_range_consistency`: skips 409 responses

## 2026-11-18 — Quality Gate Results

| Gate | Result |
|------|--------|
| Frontend TypeScript (`tsc --noEmit`) | ✅ PASS (0 errors) |
| Frontend production build (`vite build`) | ✅ PASS |
| Frontend tests (`vitest run`) | ⚠️ 125 passed, 3 failed (pre-existing nav duplication) |
| Backend ruff (`ruff check .`) | ⚠️ 0 errors in estimation modules; 24 pre-existing in unrelated files |
| Backend mypy (`--strict`) | ✅ PASS (0 issues on estimation modules) |
| Backend pytest | ✅ PASS (761 passed, 1 skipped) |
| Backend e2e salary estimation | ✅ PASS (7 passed) |

## Documentation Created

- `reports/PROJECT_CURRENT_STATE.md`
- `reports/PRODUCT_SCOPE_AND_REQUIREMENTS.md`
- `reports/PRODUCT_WORKFLOW.md`
- `reports/ARCHITECTURE_RECONCILIATION.md`
- `reports/SALARY_ENGINE_SPECIFICATION.md`
- `reports/DATA_AND_SOURCE_PROVENANCE.md`
- `reports/SECURITY_REMEDIATION.md`
- `reports/IMPLEMENTATION_ROADMAP.md`
- `reports/TESTING_AND_QUALITY_REPORT.md`
- `reports/OPEN_PRODUCT_DECISIONS.md`
- `reports/IMPLEMENTATION_CHANGELOG.md` (this file)
- `reports/FINAL_PROJECT_STATUS.md`
