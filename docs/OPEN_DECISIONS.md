# Open Decisions — Salary Estimation Tool

**Document ID:** `DOC-OPEN-DECISIONS-001`  
**Status:** Active  
**Date:** 17 Aban 1405 SH (2026-11-17)  
**Related:** `IMPLEMENTATION_ROADMAP.md`, `DOC-FUNC-REQ-001`, `DATA_MODEL_SPEC.md`, `SECURITY_AND_PRIVACY.md`

---

## 1. Purpose

Records decisions that require owner approval before implementation can proceed. Each decision is listed with options, impact, and the responsible owner.

---

## 2. Decisions Requiring Owner Approval

| ID | Decision | Options | Impact | Owner | Status |
|:--|:---|:---|:---|:---|:---|
| D-01 | Market data source | (a) Manual seeding only<br>(b) Licensed salary survey data<br>(c) Job board scraping (if ToS permits) | Determines data quality, legal risk, and implementation effort | Project Owner | **OPEN — NON-BLOCKING** (Manual & licensed ingestion tool delivered in `market_data_ingest.py`) |
| D-02 | Authentication | (a) Email + password (hashed)<br>(b) No auth (single trusted manager, local only) | Determines security complexity and deployment constraints | Project Owner | **OPEN — NON-BLOCKING** (Single-manager session active) |
| D-03 | Resume parsing AI | (a) Local LLM (e.g., Ollama)<br>(b) API-based LLM<br>(c) Manual entry only (defer AI to v2) | Determines infrastructure, cost, and privacy boundary | Project Owner | **OPEN — NON-BLOCKING** |
| D-04 | Database | PostgreSQL (simplified, existing migration 0007) | Determines deployment and operational complexity | Project Owner | **RESOLVED** (PostgreSQL 16 with migration 0007 confirmed) |
| D-05 | PDF export | (a) Server-side library (e.g., ReportLab)<br>(b) Browser print/CSS<br>(c) Defer to v2 | Determines v1 feature completeness | Project Owner | **RESOLVED** (Browser print for v1 per ADR-013 D-05) |
| D-06 | Estimation algorithm | Hybrid (Cohort P25…P75 + real median + zero fabrication) | Determines accuracy, explainability, and maintenance | Project Owner | **RESOLVED** (ADR-014 Accepted) |
| D-07 | Legal minimum wage display | Show as separate reference value only | Determines regulatory framing of estimates | Project Owner | **RESOLVED** (ADR-013 D-07 & ADR-014 §7) |

---

## 3. Decisions Already Made (Recorded for Reference)

| ID | Decision | Made By | Date | Source |
|:--|:---|:---|:---|:---|
| D-M-01 | Product is salary estimation tool, not payroll engine | Project Owner | 2026-11-17 | ADR-013 |
| D-M-02 | Single manager user type | Project Owner | 2026-11-17 | ADR-013, USER_WORKFLOWS.md |
| D-M-03 | No accounting, payroll, or employee management | Project Owner | 2026-11-17 | ADR-013, PRODUCT_SCOPE.md |
| D-M-04 | Market data basis (not statutory minimum wage) | Project Owner | 2026-11-17 | ADR-013, SALARY_ESTIMATION_SPEC.md |
| D-M-05 | Output: range + primary estimate + factors + confidence | Project Owner | 2026-11-17 | ADR-013, FUNCTIONAL_REQUIREMENTS.md |
| D-M-06 | AI for resume analysis only, not salary invention | Project Owner | 2026-11-17 | ADR-013, AI_ANALYSIS_SPEC.md |
| D-M-07 | Preserve useful technical conventions (Decimal, RTL, Vazirmatn, testing) | Project Owner | 2026-11-17 | ADR-013, ARCHITECTURE.md |

---

## 4. Decisions Explicitly Deferred (Not in v1)

| ID | Decision | Reason for Deferral | Revisit Trigger |
|:--|:---|:---|:---|
| D-D-01 | Multi-tenant RLS and tenant_id | Single manager only in v1 | If multi-user needed |
| D-M-02 | AES-256-GCM field encryption | Not needed for resume data | If high-sensitivity PII collected |
| D-D-03 | MFA and session management | Not needed in v1 | If production-grade auth required |
| D-D-04 | Audit hash chain | Not needed for estimate history | If compliance requires |
| D-D-05 | Document forensics / OCR | Out of scope | If resume verification needed |

---

## 5. How to Resolve

Owner should review each **OPEN — BLOCKING** decision (D-01, D-02, D-06) before implementation begins. **OPEN — NON-BLOCKING** decisions can be resolved during implementation but should be recorded.

When a decision is made, update this document:
- Change status from `OPEN` to `RESOLVED`
- Record the chosen option
- Record the date and owner
- Add a reference to the implementing ADR or task

---

## 6. Open decisions raised by ADR-014 (2026-11-18)

| ID | Decision | Status | Blocks |
|:--|:---|:---|:---|
| D-07 (DEC-015) | Licensed market-data sources, their licence state and sign-off; reconciles DEC-007/DEC-008 | OPEN — NON-BLOCKING (Ingestion tooling ready) | Any real estimate |
| D-08 (DEC-016) | Estimation-history tenancy (single-manager audit log vs multi-tenant) and retention | OPEN — NON-BLOCKING | Saved history list endpoint |
| D-09 (DEC-017) | Approval of the cohort methodology as published | **RESOLVED** (ADR-014 Accepted by Project Owner 2026-11-18) | None |

The engine already behaves as if all three were answered conservatively: no invented
source, no personal-data table, and no monetary multiplier that lacks a source.
