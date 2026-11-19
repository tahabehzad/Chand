# Implementation Roadmap — Salary Estimation Tool

**Document ID:** `DOC-ROADMAP-002`  
**Status:** Draft — pending owner approval  
**Date:** 17 Aban 1405 SH (2026-11-17)  
**Supersedes:** `docs/EXECUTION_PLAN.md` (payroll WBS), `docs/ROADMAP_OPERATIONAL_PAYROLL.md` (payroll roadmap)  
**Related:** `DOC-PRODUCT-SCOPE.md`, `DOC-FUNC-REQ-001`, `DATA_MODEL_SPEC.md`, `ARCHITECTURE.md`

---

## 1. Context

The existing project has 88 WBS tasks across 5 phases for a statutory payroll engine. Those tasks are **not deleted** but are **marked as historical/superseded** for the new product. A new, simplified task list is defined below for the salary estimation tool.

## 2. Implementation Tasks (Ordered)

| # | Task ID | Task Title | Description | Dependencies | Est. Effort |
|:--|:---|:---|:---|:---|:---|
| 1 | T-01 | Owner confirms documentation | Owner reviews and approves this roadmap and all specification docs | — | 1 day |
| 2 | T-02 | Simplify backend | Remove payroll-specific routes/services not needed; keep FastAPI skeleton | T-01 | 3 days |
| 3 | T-03 | Database schema | Create `candidate_estimates`, `market_salary_data`, `users`, `resume_uploads` tables | T-02 | 2 days |
| 4 | T-04 | Seed market data | Seed initial Iranian job market salary data (manual or licensed) | T-03 | 3 days |
| 5 | T-05 | Multi-step resume form | React form: job title, experience, skills, education, city, employment type, seniority | T-02 | 4 days |
| 6 | T-06 | Estimation service | Logic to compute salary range + primary estimate from candidate + market data | T-03, T-04 | 5 days |
| 7 | T-07 | Estimate result page | Display range, primary estimate, influencing factors, confidence, "insufficient data" | T-05, T-06 | 3 days |
| 8 | T-08 | Estimate storage & history | Save estimates, list previous results, view details | T-03, T-06 | 3 days |
| 9 | T-09 | Resume upload (v2) | PDF/text upload and basic info extraction (AI-assisted) | T-05 | 5 days |
| 10 | T-10 | PDF export (v2) | Export estimate result to PDF | T-07 | 3 days |
| 11 | T-11 | Tests | Backend pytest, frontend vitest, lint, typecheck | All above | 4 days |
| 12 | T-12 | Owner demo & approval | End-to-end demo; owner sign-off | All above | 2 days |

**Total estimated effort:** ~39 days (development only; does not include owner review time)

## 3. Phase Summary

| Phase | Scope | Tasks | Gate |
|:---|:---|:---|:---|
| Phase 1 | Foundation | T-01 to T-04 | Backend + DB + seed data ready |
| Phase 2 | Core UI + estimation | T-05 to T-08 | Manager can get and save estimates |
| Phase 3 | Enhancements (v2) | T-09 to T-10 | Resume upload + PDF export |
| Phase 4 | Validation | T-11 to T-12 | Tests pass; owner approves |

## 4. Out of Scope for v1

| Feature | Reason | Post-v1? |
|:---|:---|:---|
| Employee management | Not product scope | No (unless owner requests) |
| Payslip generation | Not product scope | No |
| Tax/insurance calculation | Not product scope | No |
| Multi-tenant RLS | Not needed (single manager) | Maybe |
| MFA / production auth | Not needed in v1 | Maybe |
| Resume PDF upload | Nice-to-have | Yes (T-09) |
| PDF export | Nice-to-have | Yes (T-10) |

## 5. Open Decisions Blocking Implementation

| ID | Decision | Options | Owner |
|:--|:---|:---|:---|
| D-01 | Market data source | Manual seeding vs licensed source vs API | Owner |
| D-02 | Authentication | Password-based vs no auth (trusted manager) | Owner |
| D-03 | Resume parsing AI | Local model vs API vs manual entry only | Owner |
| D-04 | Database | PostgreSQL (simplified) vs SQLite vs other | Owner |
| D-05 | PDF export library | Server-side vs browser print | Owner |

## 6. Validation Plan

- **Backend:** `pytest` on estimation service and repository layer
- **Frontend:** `vitest` on form, result page, history
- **Lint:** `ruff` (backend), logical-utility gate (frontend)
- **Typecheck:** `mypy --strict` (backend), `tsc --noEmit` (frontend)
- **Build:** `uv sync --frozen` (backend), `vite build` (frontend)
- **Manual:** Owner completes end-to-end flow (form → estimate → save → view history)

## 7. Completion Criteria

- All 12 tasks complete
- Owner has signed off on the demo
- All tests pass
- Documentation is consistent with implementation
- No payroll/accounting functionality in the active product path
