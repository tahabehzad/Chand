# IMPLEMENTATION_ROADMAP.md

Implementation Roadmap — Pish Hesabdari

## 1. Completed Work (P0 + P1 Core)

All critical safety and correctness issues and core product functionality have been implemented:

### P0 — Critical Safety and Correctness

| Issue | Fix | Files |
|-------|-----|-------|
| Frontend syntax errors (9 errors in 3 files) | Fixed `{v1.0}`, `window.apiClient`, Cyrillic/Korean text, invalid benchmark text | `SalaryEstimationPage.tsx`, `SalaryDiscoveryPage.tsx`, `salary-benchmarks.ts` |
| Frontend `react-hook-form/zod` dependency removed | Rewritten with native React state | `SalaryEstimationForm.tsx` |
| Frontend/backend contract mismatch | Form maps `string[]` skills to `[{name, level}]` | `SalaryEstimationForm.tsx`, `SalaryEstimationPage.tsx` |
| Domain validators accept invalid values | Pydantic v2 `field_validator` with allowed values | `schemas.py` |
| Fake salary differentiation | Deterministic exact matching on job+seniority+city | `matcher.py` |
| Fabricated data provenance | `data_sources` from actual profile only | `salary_estimator.py` |
| Insufficient data returns zeros | Raises `ValueError` → HTTP 409 refusal | `salary_estimator.py`, `api/v1/estimation/__init__.py` |
| Float arithmetic in money path | `Decimal` multipliers, `round_half_up` | `salary_estimator.py` |
| Hardcoded legal wage | Loaded from 1404 rule set | `salary_estimator.py` |
| Exception leak in API | Separate handling for ValueError vs generic Exception | `api/v1/estimation/__init__.py` |

### P1 — Core Product Functionality

| Feature | Status | Files |
|---------|--------|-------|
| Candidate information form (Persian, RTL) | ✅ Complete | `SalaryEstimationForm.tsx`, `SalaryEstimationPage.tsx` |
| Backend API contract | ✅ Complete | `api/v1/estimation/__init__.py`, `schemas/estimation.py` |
| Salary calculation engine | ✅ Complete | `salary_estimator.py`, `matcher.py` |
| Legal minimum wage reference | ✅ Complete | `salary_estimator.py` (`load_rule_set(1404)`) |
| Market-based recommendation | ✅ Complete | `salary_estimator.py`, `matcher.py` |
| Result explanation and provenance | ✅ Complete | `SalaryEstimationResults.tsx`, `salary_estimator.py` |
| Insufficient data refusal | ✅ Complete | `salary_estimator.py`, `api/v1/estimation/__init__.py` |

## 2. Next Stage (P1 Remaining)

| Task | Description | Priority | Dependency |
|------|-------------|----------|------------|
| Agreed salary input | Manager records agreed base salary, distinct from recommendation | High | None |
| Decision recording (Accept/Modify/Reject) | Append-only decision history | High | Agreed salary input |
| Review/confirmation screen | Between form submission and calculation | Medium | Core form |
| D-02 authentication decision | Product owner decides on auth for estimation endpoint | High | None |
| DEC-01 market data repository | Approve mock seed or require licensed repository | High | None |

## 3. P2 — Reliability

| Task | Description | Priority |
|------|-------------|----------|
| Unit tests for estimator | Test calculation logic, range, refusal | High |
| Frontend component tests | Test SalaryEstimationForm, SalaryEstimationResults | High |
| Integration tests | API contract, DB persistence (requires PostgreSQL) | High |
| Error handling review | Verify all error paths return correct status codes | Medium |

## 4. P3 — Product Quality

| Task | Description | Priority |
|------|-------------|----------|
| Fix duplicate nav links | "بازار حقوق" appears twice in navigation | Medium |
| Accessibility improvements | ARIA labels, keyboard navigation | Medium |
| UI/UX polish | Visual design, responsive layout | Low |
| Documentation | Setup instructions, environment variables | Medium |
| Deployment readiness | Docker, environment config | Low |

## 5. Dependency Order

```
P0 fixes (completed) → P1 core (completed) → Agreed salary input → Decision recording → D-02 auth decision → DEC-01 market data → P2 reliability → P3 quality
```

## 6. Estimated Effort

| Phase | Tasks | Estimated Effort |
|-------|-------|-----------------|
| P0 (completed) | 10 fixes | ~8 hours |
| P1 (completed) | 7 features | ~16 hours |
| P1 remaining | 4 tasks | ~12 hours |
| P2 | 4 tasks | ~16 hours |
| P3 | 5 tasks | ~20 hours |

## 7. Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| No licensed market data | High | High | DEC-01 decision needed; clearly label as seed data |
| No authentication | Medium | Medium | D-02 decision needed; endpoint publicly accessible |
| PostgreSQL not available | Medium | Low | Integration tests skipped; unit tests cover logic |
| Navigation duplication | Low | Low | Fix in P3 |
