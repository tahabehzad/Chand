# PROJECT_STATE — Chand (چند؟)

- **Document ID:** `DOC-STATE-002`
- **Status:** Derived snapshot — no independent facts
- **As at:** 2026-11-19 (28 Aban 1405 SH)
- **Owners:** scope `docs/PRODUCT_SCOPE.md` · vision `docs/PRODUCT_VISION.md` · delivery `docs/PROJECT_STATUS.md` · decisions `docs/DECISIONS_REGISTER.md` + `docs/ADR_INDEX.md` · verification `docs/BOOTSTRAP_CHANGELOG.md`

> Snapshot only. Where this file disagrees with an owner document above, the owner is right and this file is stale. Do not record new facts here.

---

## 1. Current Product and Implementation Status

The active product is the **Resume Analysis and Monthly Salary Estimation Tool** (ADR-013 accepted 2026-11-17; ADR-014 accepted 2026-11-18). It serves a single hiring manager entering candidate profile details (or uploading a resume) to estimate a market-based monthly salary range (P25…P75) and primary median estimate grounded in verified Iranian labor market data.

The prior statutory payroll calculation engine (ADR-008) remains implemented in code on the 1404 SH baseline as preserved technical foundation, but is superseded as the active product direction.

---

## 2. Completed

### Market Salary Estimation Engine (ADR-013 & ADR-014)
- **Mathematical & Statistical Core:** Pure estimation function in `backend/app/domain/salary_estimation/` computing real median, P25, P75, IQR, and MAD outlier filtering with `numpy`, `scipy`, and `decimal.Decimal` (`prec = 34`).
- **Validation & Refusal Policy:** The engine strictly enforces "Refuse instead of Fabricate" — returns `insufficient_data` when verified market observations do not meet minimum sample thresholds; zero hallucinated figures.
- **Gemini Live BYOK Web Grounding:** Client-side stored Gemini API key (`localStorage` only, never logged or persisted in backend databases) enabling live market search against Iranian portals (Jobinja, Jobvision, IranTalent, Quera).
- **Seamless Database Fallback:** Automatic failover to PostgreSQL reference tables when Gemini is unavailable, offline, or returns insufficient live data.
- **Total Cost to Employer (CTC) & Net Pay Breakdown:** Itemized calculation of employee net salary (gross minus capped 7% SSO and Article 137 income tax) and employer overhead (20% SSO, 3% unemployment, 1/12 monthly severance, and 1/12 annual Eydi) under verified 1404 statutory rules with canonical calculation hash.
- **Database Schema:** Migration `0007_market_salary_reference.py` providing global reference tables: `market_data_sources`, `market_salary_observations` (Kind A), and `market_salary_aggregates` (Kind B).
- **APIs:** `POST /api/v1/simulations/salary-estimation` and `POST /api/v1/simulations/salary-ctc-breakdown` with Pydantic v2 validation (`model_config = ConfigDict(extra="forbid")`), correlation IDs, and comprehensive error taxonomy.
- **Frontend Dashboard:** Persian RTL `SalaryEstimationPage` at `/` with Vazirmatn variable typography, candidate profiling form, interactive `SalaryRangeGauge` (P25, P50, P75), `DistributionHistogram`, `NegotiationSheet` with tactical talking points and true employer cost multiplier, `CtcBreakdown`, `GeminiSettings`, and PDF report export.
- **Testing:** 872 backend tests PASS (unit, domain, API, and property tests) with 74 skipped (live PostgreSQL/Docker container tests gracefully skipping when local daemon is absent).

### Preserved Statutory Foundation (Historical ADR-008)
- Exact Decimal money primitives (`ROUND_HALF_UP`, signed residual).
- Fail-closed rule-set loader (1404 verified baseline).
- Base decomposition, SSO, progressive income tax, overtime/night shift, Sanavat, Eydi, employer CTC, and Article 11 termination simulator.

### Frontend Foundation
- React 19 + TypeScript 5.7 + Vite 6 + Tailwind CSS v4.
- Persian RTL logical CSS properties (`ms-`, `me-`, `ps-`, `pe-`).
- Accessibility: `prefers-reduced-motion: reduce` disables all animations; accessible Persian labels and ARIA attributes across all inputs.
- 170 Vitest tests passing across 23 test files; clean production build.

---

## 3. Product Deliverables Status

1. **Root Route (`/`):** Defaulted to `SalaryEstimationPage` as primary application view.
2. **BYOK Gemini Integration:** Fully tested with mocked live responses, 503 timeout handling, and 409 refusal translation.
3. **CTC Calculation:** Fully integrated and tested with exact integer Rial statutory math.
4. **Negotiation Cheat Sheet & PDF Export:** Completed with market percentile statement badges and Iranian labor market talking points.
5. **Quality Gate:** Zero-tolerance Ruff, Mypy strict, and TypeScript compiler checks fully passing.

---

## 4. Architectural Decisions

- **Accepted:** ADR-001…004, ADR-006, ADR-007, ADR-008, ADR-009, ADR-010, ADR-011, ADR-012, ADR-013, and ADR-014.
- **Proposed:** ADR-005 (Async execution strategy; remains proposed as estimation is currently synchronous).
- **Superseded:** Product-boundary clauses of ADR-004, ADR-008, and ADR-010 are superseded by ADR-013 and ADR-014.

---

## 5. Verification Checkpoint

- Backend: 872 tests PASS (74 skipped, 0 failed, 0 errors in 27.79s); `ruff check .` PASS (0 errors); `mypy --strict app tests` PASS (0 issues in 131 files).
- Frontend: 170 Vitest tests PASS across 23 test files; `tsc --noEmit -p tsconfig.app.json` PASS (0 errors); `vite build` PASS (clean build in 3.03s).
