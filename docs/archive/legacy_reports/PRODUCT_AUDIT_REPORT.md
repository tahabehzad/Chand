# Product Alignment & Technical Audit Report
**Date:** 2026-11-17 | **Project:** Pish Hesabdari | **Scope:** Pre-accounting MVP

---

## Executive Summary

**The product does NOT deliver market-based salary estimation.** It delivers **statutory costing of a manager's salary decision**.

| Question | Answer |
|----------|--------|
| Can a manager get a market-based salary recommendation? | **NO** — no market data exists (DEC-007/008 REJECTED) |
| Does the landing page implement the estimation workflow? | **NO** — dashboard shows demo accounting data |
| Is frontend connected to real backend? | **YES** — all prototype routes hit real API |
| Is statutory payroll engine verified? | **YES** — 1404 baseline, 780 tests PASS |

---

## What Actually Works

| Module | Endpoint | Status |
|--------|----------|--------|
| Manager auth | `POST /api/v1/auth/login` | ✅ Real |
| Employee CRUD | `/api/v1/manager/employees` | ✅ Real |
| Performance observations (4 criteria) | `/api/v1/manager/employees/{id}/observations` | ✅ Real |
| Evidence upload | `/api/v1/manager/employees/{id}/evidence` | ✅ Real |
| Evaluation & scoring (perf-v1) | `POST /api/v1/manager/employees/{id}/evaluations` | ✅ Real |
| Salary recommendation + decisions | `/api/v1/manager/recommendations` | ✅ Real |
| Advisory compensation proposal | `POST /api/v1/valuations/compensation-proposal` | ✅ Real |
| Statutory gross-to-net | `POST /api/v1/simulations/gross-to-net` | ✅ Real |

---

## Critical Gaps vs Requirements

| Requirement | Reality |
|-------------|---------|
| Iranian labor market data | **None** — explicitly out of scope |
| Job title / experience / age / certifications → salary | **Not implemented** — only 4 perf criteria (sales/quality/attendance/responsibility) |
| Manager-supplied band | **Required** — "no band ⇒ refusal, never a generated figure" (ADR-009) |
| Market reasoning in output | **Absent** — only score breakdown & statutory costing |
| Landing page = workflow entry | **No** — `/` shows demo dashboard |

---

## Technical Health

| Check | Result |
|-------|--------|
| Backend tests | 780 PASS, 1 FAIL (outdated table list), 1 SKIP |
| Frontend tests | 124 PASS, 2 FAIL (wrong page context) |
| Ruff lint | 9 errors (scripts only) |
| MyPy strict | PASS (95 files) |
| Build | PASS |
| Engine math | Reproduces Holy Bible Appendix A vectors exactly |

---

## Open Legal Ambiguities (B-series)

| Issue | Status | Blocking |
|-------|--------|----------|
| Night-work supplement duplicate wage | OPEN | Production |
| Leave-buyout daily base (÷30 vs calendar) | OPEN | Production |
| Insurable wage base conflict (B-3) | OPEN | Production |

---

## Minimum Tasks to Ship Intended MVP

1. **Redirect `/` to `/proposal` or `/prototype/people` after login** (0.5d)
2. **Fix integration test table list** (0.25d)
3. **Fix frontend nav tests** (0.25d)
4. **Add job-title/education/age/certification fields to employee** (2d)
5. **Link `/proposal` from authenticated dashboard** (1d)
6. **Resolve B-series with Labour Counsel** (external)
7. **Add explicit UI notice: "Band set by manager; no market data used"** (0.5d)

---

## Verdict

> **NO — a manager cannot receive a credible market-based salary recommendation today.**
>
> The system costs a **manager's decision** under verified 1404 statutory rules. It does not estimate what the market pays. This is by design (ADR-008, ADR-009, DEC-007/008).