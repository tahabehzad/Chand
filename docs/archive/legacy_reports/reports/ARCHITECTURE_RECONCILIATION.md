# ARCHITECTURE_RECONCILIATION.md

Architecture Reconciliation — Pish Hesabdari

## 1. Existing Architecture vs. Product Goal

The repository contains multiple architectural layers that were not always aligned with the actual product (salary determination for a new employee).

### Payroll Engine vs. Salary Estimation

Two distinct calculation modules exist:

| Module | Path | Purpose | Status |
|--------|------|---------|--------|
| Payroll engine | `backend/app/engines/` | Gross-to-net payroll, tax, insurance (Article 137) | Verified, used by `/simulation` endpoint |
| Salary estimation | `backend/app/domain/salary_estimation/` | Market-based salary recommendation for new hires | Rewritten for MVP |

The payroll engine is a SEPARATE product feature (gross-to-net simulation) and is NOT used for salary determination. The salary estimation module is the correct engine for the MVP.

### Competing User Models

Multiple user/database models existed:
- `backend/app/models/identity.py` — User, Organization, Role, OrganizationMembership (multi-tenant)
- `backend/app/models/estimation.py` — Estimation records (no migration)

The multi-tenant identity model is appropriate for future multi-tenant deployment but is NOT required for the MVP (single manager user). No changes made to preserve existing work.

## 2. Decision Reconciliation Table

| Decision | Existing Status | Evidence | Conflict | Recommended Resolution | Required Action |
|----------|----------------|----------|----------|----------------------|-----------------|
| D-01: Salary estimation algorithm | Rule-based (not ML) | ADR-013 accepted 2026-11-17 | None | Keep rule-based | No action |
| D-02: Authentication on estimation endpoint | OPEN | DECISIONS_REGISTER.md | Endpoint has no auth dependency | Keep unauthenticated for MVP; D-02 remains open | Product owner decision needed |
| D-06: Market data source | MarketDataRepository (DEC-01 open) | ADR-013 | Mock data used as seed | Keep mock seed data; DEC-01 remains open | Product owner decision needed |
| ADR-013: Salary Estimation Tool | Accepted | docs/ADR_INDEX.md | None | Follow ADR-013 spec | No action |
| AI for salary calculation | Not required | Holy Bible §12 | None | AI not used in calculation path | No action |
| Currency unit | Rial internal, Toman display | skills financial-data-integrity | None | Decimal Rial internally | No action |
| ADR-005 (Background JobQueue) | Proposed, not accepted | docs/DECISIONS_REGISTER.md | None | Do not implement | No action |
| ADR-004 (pre-employment platform) | Superseded | AGENTS.md §1 | Product re-scoped to payroll engine | Ignore ADR-004 module list | No action |

## 3. Contradictions Resolved

### BE-06: Missing education field
- **Claim:** Education field missing from UI/request flow
- **Verification:** Confirmed. Domain schema had `education` as required `str` with `min_length=1`; API made it optional but domain rejected empty string.
- **Resolution:** Made `education` optional (`str \| None`) in domain schema. Frontend collects it but allows empty.

### BE-07: Domain validators don't reject invalid values
- **Claim:** Validators accept invalid seniority, employment_type, city
- **Verification:** Confirmed. `employment_type` accepted any string; `seniority_level` accepted any string; `city` was case-sensitive.
- **Resolution:** Pydantic v2 `field_validator` with explicit allowed values. City normalized to lowercase (no allowed-values restriction — matcher returns None for unknown cities → 409 refusal).

### BE-08: Incorrect salary outputs (fake differentiation)
- **Claim:** Unrelated job titles received different salaries without valid reason
- **Verification:** Confirmed. `_process_job_title` stripped "developer"/"engineer" making all developer titles match the same profile. `_find_fuzzy_match` matched on any word overlap.
- **Resolution:** Deterministic exact matching on normalized job_title + seniority + city. Underscores normalized to spaces. No match → 409 refusal.

### BE-09: Fabricated market-data provenance
- **Claim:** `data_sources: ["Jobinja", "JobVision", "Salary Survey"]` hardcoded regardless of actual data
- **Verification:** Confirmed. All three sources listed even when only one had data.
- **Resolution:** `_data_sources_from_profile()` returns only sources actually present in the matched profile.

### BE-10: Insufficient data returns success with zeros
- **Claim:** Zero-valued salary fields returned as successful result
- **Verification:** Confirmed. `estimate_salary` returned zeros when no match found.
- **Resolution:** Raises `ValueError("insufficient_data: ...")` → HTTP 409 refusal. No numeric estimate returned.

### FE-01: TypeScript syntax errors
- **Claim:** 9 syntax errors in 3 files
- **Verification:** Confirmed. `{v1.0}`, `window.apiClient`, Cyrillic text, Korean text, invalid benchmark text.
- **Resolution:** All syntax errors fixed. `tsc --noEmit` passes.

### FE-02: Frontend/backend contract mismatch
- **Claim:** Form skills type (`string[]`) vs API (`[{name, level}]`)
- **Verification:** Confirmed. Form collected `string[]`, API expected `[{name: string, level?: string}]`.
- **Resolution:** Form maps `string[]` to `[{name, level: 'beginner'}]` at submission boundary.

## 4. Remaining Contradictions (Open Decisions)

| Issue | Description | Impact | Required Decision |
|-------|-------------|--------|-------------------|
| D-02 | Authentication on estimation endpoint | Endpoint is publicly accessible | Product owner: require auth or keep open for MVP |
| DEC-01 | Market data repository vs. mock seed | Mock data used as temporary seed | Product owner: approve seed data or require licensed repository |
| ADR-005 | Background JobQueue | Not accepted; no async processing | Not needed for MVP (synchronous calculation) |
| Navigation duplication | "بازار حقوق" appears twice in nav | Minor UI issue | Fix in next-stage UI work |

## 5. Smallest Reliable Architecture for MVP

```
Manager UI (React, Persian, RTL)
    ↓ HTTP POST
API Endpoint (FastAPI) — /api/v1/simulations/salary-estimation
    ↓
Service Layer (app/services/estimation/service.py)
    ↓
Domain Layer (app/domain/salary_estimation/)
    ├── schemas.py (Pydantic v2 validation)
    ├── matcher.py (deterministic market profile matching)
    └── salary_estimator.py (Decimal calculation, provenance)
    ↓
Rules Engine (app/engines/rules.py) — load_rule_set(1404)
    ↓
Statutory Seed (data/seeds/statutory_rules_1404.yaml)
```

No multi-tenant RLS, no authentication, no background jobs, no AI in the calculation path. All synchronous, deterministic, testable.
