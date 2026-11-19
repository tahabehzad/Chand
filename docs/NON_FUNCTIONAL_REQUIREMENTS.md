# Non-Functional Requirements — Salary Estimation Tool

**Document ID:** `DOC-NONFUNC-REQ-001`  
**Status:** Draft — pending owner approval  
**Date:** 17 Aban 1405 SH (2026-11-17)  
**Related:** `DOC-FUNC-REQ-001`, `DOC-PRODUCT-SCOPE.md`

---

## 1. Non-Functional Requirements

| ID | Requirement | Priority |
|:---|:---|:---|
| NF-01 | The interface shall be Persian (Farsi), simple, and easy to understand. RTL layout at document root. | Must |
| NF-02 | Candidate resume data and personal information shall be stored securely; only the manager shall have access. | Must |
| NF-03 | Estimates shall be stored in a database for later retrieval by the manager. | Must |
| NF-04 | No payroll, tax, insurance, or accounting calculations shall be performed. | Must |
| NF-05 | The system shall not present itself as a legal payroll engine or statutory calculator. | Must |
| NF-06 | Monetary figures shall use Decimal arithmetic with ROUND_HALF_UP; no float literals in calculation paths. | Must |
| NF-07 | Every emitted salary figure shall carry provenance (source, confidence, data freshness). | Must |
| NF-08 | The system shall not generate fabricated salary statistics when data is insufficient. | Must |
| NF-09 | Frontend shall use logical CSS utilities only (no physical RTL overrides), per existing conventions. | Must |
| NF-10 | Fonts: Vazirmatn, self-hosted `.woff2` from app origin, OFL license. | Should |
| NF-11 | Numerals: three-layer policy (display / input / machine); Persian digits in display, ASCII in machine layer. | Must |
| NF-12 | Currency: Rial as canonical unit; Toman display refused when not divisible by 10. Unit label always rendered. | Must |
| NF-13 | Authentication: single manager access; no MFA, no sessions, no employee accounts in v1. | Must |
| NF-14 | Database: simplified schema (no tenant_id, no RLS, no FORCE ROW LEVEL SECURITY) unless owner requires later. | Should |
| NF-15 | Security: standard database access controls; no AES-256-GCM application-layer encryption required for v1 (resume data is not high-sensitivity PII like National ID). | Should |
| NF-16 | AI boundary: AI may analyze resumes and identify skills/experience, but must never invent salary figures or statistics. | Must |
| NF-17 | Testing: vitest (frontend), pytest (backend), ruff, mypy --strict; all tests must pass before release. | Must |
| NF-18 | Build: frontend `vite build` and backend `uv sync --frozen` must succeed. | Must |

## 2. Preserved Technical Conventions (from existing project)

| Convention | Source | Status |
|:---|:---|:---|
| React + Vite + TypeScript + Tailwind v4 | ADR-001, frontend/README.md | Preserved |
| RTL Persian (`dir="rtl"`, `lang="fa"`) | ADR-001, SPEC-FE-001 | Preserved |
| Vazirmatn font | ADR-001, frontend/README.md | Preserved |
| Logical CSS utilities only | SPEC-FE-001 §2.3 | Preserved |
| Decimal money, ROUND_HALF_UP, integer Rial | AGENTS.md §2, SPEC-STAT-001 | Preserved where money is shown |
| Advisory labelling ("not legal payroll advice") | ADR-010 §3.1 | Preserved as good practice |
| No production claims for prototype | ADR-010 §3.1 | Preserved as good practice |
| Loopback/dev-only deployment | ADR-010 §3.1 | Preserved as good practice |

## 3. Quality Attributes

| Attribute | Target |
|:---|:---|
| Time to complete form | < 3 minutes |
| Estimate generation time | < 10 seconds |
| UI language | Persian (Farsi) |
| Currency display | Rial (canonical) + Toman (optional, divisible by 10) |
| Data reliability | Traceable to market data sources; "insufficient data" when unavailable |
