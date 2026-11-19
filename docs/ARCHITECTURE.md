# Architecture — Salary Estimation Tool

**Document ID:** `DOC-ARCH-002`  
**Status:** Draft — pending owner approval  
**Date:** 17 Aban 1405 SH (2026-11-17)  
**Supersedes:** `docs/ARCHITECTURE.md` sections 6–13 (proposed MVP per ADR-010); sections 1–5 preserved as existing technical reference  
**Related:** `DOC-PRODUCT-SCOPE.md`, `DOC-DATA-MODEL-SPEC-001`, `SECURITY_AND_PRIVACY.md`

---

## 1. Architectural Position

The repository is a **modular monolith** (ADR-001): one FastAPI process, one React SPA, one PostgreSQL instance.

For the new product, the existing payroll engine and its infrastructure remain in the repository as technical code but are **not** the active product path. The salary estimation tool uses a simplified stack:

- **Frontend:** React + Vite + TypeScript + Tailwind v4 + RTL Persian + Vazirmatn (existing, preserved)
- **Backend:** FastAPI + Python (existing, simplified)
- **Database:** PostgreSQL (existing, simplified schema — no tenant_id, no RLS)
- **Authentication:** Single manager, email + password (simplified from existing 7-role schema)
- **Queue/Worker:** None (synchronous estimation)
- **Cache:** None
- **External services:** Optional market data APIs or licensed data (no scraping if ToS prohibits)

---

## 2. Backend Structure (Simplified)

| Layer | Modules | Responsibility |
|:---|:---|:---|
| HTTP | `app/main.py`, `app/api/v1/estimation.py` | Routes, CORS, correlation id, error envelope |
| Contracts | `app/schemas/estimation.py` | Pydantic v2; integer Rial; rates/scores as strings |
| Services | `app/services/estimation_service.py` | Orchestrate estimation, build provenance |
| Domain | `app/engines/estimation.py` (new) | Pure calculation logic; Decimal arithmetic |
| Data access | `app/repositories/` | Database queries for estimates and market data |
| Security | `app/core/security/` (simplified) | Password hashing, simple auth |
| Persistence | `app/models/`, `alembic/` | Simplified tables: candidate_estimates, market_salary_data, users |

**Dependency direction:** `api → schemas → services → engines → repositories → models`

---

## 3. Data Flow — Salary Estimation

```
Manager JSON (form data)
    → EstimateRequest (pydantic, extra=forbid)
    → compute_salary_estimate(EstimateRequest)
        → load_market_data(job_title, city, seniority)
        → adjust_for_experience(profile, market_base)
        → adjust_for_skills(profile, market_base)
        → adjust_for_location(profile, market_base)
        → compute_range_and_primary(market_base, adjustments)
        → provenance map + confidence + sources
    → EstimateResponse + generated_at
    → Save to candidate_estimates table
    → Return JSON to frontend
```

---

## 4. Data Flow — Resume Upload (v2)

```
Resume file (PDF/text)
    → ResumeUpload endpoint
    → AI parser extracts skills, experience, education
    → Manager reviews extracted fields (if AI confidence low)
    → Validated profile → EstimateRequest
    → Same estimation flow as above
```

---

## 5. Frontend Structure (Simplified)

| Route | Purpose |
|:---|:---|
| `/` | Landing: "شروع تخمین جدید" |
| `/estimate/new` | Multi-step Persian form |
| `/estimate/result` | Result: range, primary, factors, confidence, sources |
| `/estimate/history` | List of saved estimates |
| `/estimate/history/[id]` | Detail view |
| `/settings` | Display unit (rial/toman), preferences |

Reusable from existing frontend: RTL layout, Vazirmatn, logical CSS, money formatting (Decimal), numeral policy, API client with correlation id.

---

## 6. Reusable Components (Do Not Duplicate)

| Component | Source | Use in New Product |
|:---|:---|:---|
| `frontend/src/lib/money.ts` | Existing | Money formatting (Rial/Toman, Persian digits) |
| `frontend/src/lib/numerals.ts` | Existing | Three-layer numeral policy |
| `frontend/src/components/ui/*` | Existing | RTL UI primitives (button, input, card, badge) |
| `frontend/src/api/client.ts` | Existing | Typed API client, correlation id |
| `frontend/src/lib/cn.ts` | Existing | Class name utility |
| `backend/app/engines/money.py` | Existing | Decimal money primitives |
| `backend/app/engines/errors.py` | Existing | Error taxonomy |
| `backend/app/api/v1/payroll.py` | Existing | Error/response pattern (reference only) |
| `backend/app/engines/valuation.py` | Existing | Band placement logic (reference for range logic) |

---

## 7. Architectural Risks

| # | Risk | Impact | Mitigation |
|:--|:---|:---|:---|
| AR-1 | Market data insufficient for some roles | Estimates refused | `insufficient_data` confidence level; clear UI message |
| AR-2 | AI hallucinates salary figures | Unreliable estimates | AI never computes salary; calculation logic does |
| AR-3 | Existing payroll code confuses developers | Wrong module used | Clear documentation separation; ADR-013 marks payroll as non-product |
| AR-4 | No persistence for estimates | Data lost on restart | `candidate_estimates` table in PostgreSQL |
| AR-5 | Single manager becomes bottleneck | Not scalable for now | Acceptable for v1; multi-user is post-v1 |

---

## 8. What Must Exist Before Production

- Simplified database schema (candidate_estimates, market_salary_data, users)
- Estimation service with market data integration
- Frontend multi-step form and result page
- Tests passing (vitest, pytest, ruff, mypy)
- Owner approval of estimation algorithm and data sources

No RLS, no tenant security, no audit hash chain, no production-grade auth required for v1.
