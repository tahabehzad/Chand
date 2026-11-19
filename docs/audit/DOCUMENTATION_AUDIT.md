# Documentation Audit Matrix — Pish Hesabdari

**Document ID:** `DOC-AUDIT-002`  
**Status:** Active  
**Date:** 17 Aban 1405 SH (2026-11-17)  
**Related:** `ADR-013` (product scope change to resume analysis + salary estimation tool)  
**Supersedes/Updates:** `docs/EXECUTION_DOCUMENTATION_AUDIT.md` (`DOC-AUDIT-001`)

---

## 1. Purpose

This document is the authoritative audit matrix of all project documentation after the product redefinition in **ADR-013**. The product is now a **resume analysis and monthly salary estimation tool** for a single manager — not a statutory payroll engine.

This audit:
- Classifies every discovered document against the new product vision.
- Identifies contradictions and obsolescence.
- Records required modifications.
- Preserves historical decisions without rewriting them.

No application code, database schema, migration, or runtime behavior was changed during this audit.

---

## 2. Complete Document Inventory

Total documents discovered: **47 Markdown files** + root README + frontend README.

| # | File Path | ID | Current Purpose | Status | Conflicts With | Required Modification | Dependencies |
|:--|:---|:--|:---|:---|:---|:---|:---|
| 1 | `README.md` | Root | Product entry point; describes salary estimation tool | **VALID** | None | Rewritten for salary estimation tool (ADR-013 & ADR-014) | ADR-013, ADR-014 |
| 2 | `AGENTS.md` | Operating rules | Mandatory rules for contributors; defines salary estimation scope and refusal policy | **VALID** | None | Updated to active salary estimation product scope; financial invariants retained | ADR-013, ADR-014 |
| 3 | `PROJECT_STATE.md` | Derived snapshot | Current state snapshot (aligned with ADR-013 & ADR-014) | **VALID** | None | Updated to 2026-11-18 snapshot with full test and ADR-014 coverage | ADR-013, ADR-014 |
| 4 | `PROJECT_STATUS.md` | Delivery state | Statutory payroll engine status, WBS census, tests | **OUTDATED** | New product scope | Update WBS census to salary estimation tasks; mark payroll tasks as superseded | ADR-013, EXECUTION_PLAN.md |
| 5 | `PROJECT_HANDOFF_SUMMARY.md` | Handoff | Project handoff summary | **UNCERTAIN** | Unknown content vs new scope | Review and classify after read | ADR-013 |
| 6 | `PRODUCT_AUDIT_REPORT.md` | Audit report | Independent audit report | **UNCERTAIN** | May reference payroll scope | Review for contradictions | ADR-013 |
| 7 | `PHASE_1_RED_TEAM_AUDIT.md` | Findings register | Red-team findings and corrections | **OUTDATED** | Payroll-specific findings | Mark as historical; only non-payroll findings remain relevant | ADR-013 |
| 8 | `PHASE_1_FINAL_AUDIT_BRIEF.md` | Audit brief | Superseded baseline brief | **OBSOLETE** | Already marked superseded in DOCUMENTATION_INDEX | Keep as historical; no changes | — |
| 9 | `REMEDIATED_TECHNICAL_SPECIFICATION_V2.md` | Authoritative spec | Product & technical spec for payroll engine | **OUTDATED** | New product scope is salary estimation | Mark as superseded for product scope; keep technical patterns as reference | ADR-013 |
| 10 | `RESEARCH_GAP_ANALYSIS_AND_ADVANCED_SPECIFICATION.md` | Research synthesis | Historical research | **OBSOLETE** | Already classified historical in DOCUMENTATION_INDEX | Keep as historical reference | — |
| 11 | `گزارش جامع پژوهشی.docx` | Persian research | Baseline research | **OBSOLETE** | Historical research | Keep as historical; no changes | — |
| 12 | `Technical Investigation of Related Software Projects.docx` | Tech survey | Technology landscape | **OBSOLETE** | Historical | Keep as historical; no changes | — |
| 13 | `1.docx` | Independent audit | Audit of baseline reports | **OBSOLETE** | Historical | Keep as historical; no changes | — |
| 14 | `docs/ARCHITECTURE.md` | Architecture | Existing + proposed MVP architecture | **NEEDS_UPDATE** | Proposes evaluation/recommendation prototype per ADR-010 | Rewrite for salary estimation architecture; keep reusable components section | ADR-013, ARCHITECTURE.md |
| 15 | `docs/DOCUMENTATION_INDEX.md` | Doc index | Documentation hierarchy and supersession map | **NEEDS_UPDATE** | References payroll specs as binding | Add new salary estimation docs; mark payroll docs as historical/superseded | ADR-013, all new docs |
| 16 | `docs/EXECUTION_PLAN.md` | Master plan | WBS, phases, gates for payroll engine | **OUTDATED** | 88 payroll tasks, 5 phases | Rewrite for salary estimation WBS; mark payroll WBS as historical | ADR-013 |
| 17 | `docs/EXECUTION_DOCUMENTATION_AUDIT.md` | Self-audit | Self-audit of doc package | **SUPERSEDED** | Replaced by this DOC-AUDIT-002 | Mark status as SUPERSEDED; retain historical text | — |
| 18 | `docs/ENVIRONMENT_INVENTORY.md` | Environment | Tooling and capability inventory | **VALID** | None | Minor: note frontend build commands still valid | — |
| 19 | `docs/BOOTSTRAP_CHANGELOG.md` | Changelog | Verification record of all sessions | **VALID** | None | Add entry for this audit and ADR-013 | ADR-013 |
| 20 | `docs/IMPLEMENTATION_READINESS.md` | Readiness | Per-phase readiness classification | **OUTDATED** | Payroll phase readiness | Rewrite for salary estimation readiness | ADR-013 |
| 21 | `docs/DECISIONS_REGISTER.md` | Decision register | Unresolved decisions and blockers | **NEEDS_UPDATE** | Payroll-specific decisions | Add new open decisions for salary estimation; keep payroll decisions as historical | ADR-013 |
| 22 | `docs/DECISION_REQUIRED_FROM_OWNER.md` | Owner decisions | Urgent owner decision needs | **NEEDS_UPDATE** | References payroll activation | Add salary estimation data source decisions | ADR-013 |
| 23 | `docs/DECISIONS.md` | Decisions | Product decisions (PB-Dxx) | **NEEDS_UPDATE** | Payroll advisory decisions | Add salary estimation decisions; mark payroll PB-Dxx as historical | ADR-013 |
| 24 | `docs/CURRENT_STATE.md` | Current state | Current project state | **UNCERTAIN** | Unknown | Review after read | ADR-013 |
| 25 | `docs/specs/STATUTORY_INGESTION.md` | SPEC-STAT-001 | Statutory parameter ingestion | **OUTDATED** | Statutory rule ingestion (1404/1405) | Mark as historical; salary estimation uses market data, not statutory ingestion | ADR-013 |
| 26 | `docs/specs/STATUTORY_DATABASE_CONTRACT.md` | DB contract | Statutory database contract | **OUTDATED** | Statutory DB tables | Mark as historical | ADR-013 |
| 27 | `docs/specs/history/STATUTORY_DATABASE_CONTRACT.rev2.md` | DB contract rev2 | Historical DB contract | **OBSOLETE** | Historical | Keep as historical | — |
| 28 | `docs/specs/FRONTEND_PERSIAN.md` | SPEC-FE-001 | RTL/Persian frontend spec | **VALID** | None | Still applicable to salary estimation UI | — |
| 29 | `docs/specs/TESTING.md` | SPEC-QA-001 | Testing strategy | **NEEDS_UPDATE** | Payroll test layers | Adapt testing strategy to salary estimation | ADR-013 |
| 30 | `docs/specs/DEPLOYMENT.md` | SPEC-OPS-001 | Deployment/ops spec | **NEEDS_UPDATE** | Payroll deployment topology | Simplify for salary estimation (no RLS, no tenant security) | ADR-013 |
| 31 | `docs/specs/AUTH.md` | SPEC-AUTH-001 | Auth/session/tenant spec | **OUTDATED** | Multi-role auth, MFA, RLS | Mark as historical; single manager only needed | ADR-013 |
| 32 | `docs/specs/DOCUMENT_FORENSICS.md` | SPEC-DOC-001 | Document forensics | **OBSOLETE** | Document forensics module (out of scope) | Keep as historical; no changes | — |
| 33 | `docs/specs/DEPLOYMENT.md` | Deployment spec | Deployment | **NEEDS_UPDATE** | See #31 | See #31 | — |
| 34 | `docs/specs/WORK_PROFILE_PAYROLL.md` | Work profile | Work profile + payroll spec | **OUTDATED** | Payroll work profile | Mark as historical | ADR-013 |
| 35 | `docs/ROADMAP_OPERATIONAL_PAYROLL.md` | Roadmap | Operational payroll roadmap | **OUTDATED** | Payroll operational roadmap | Mark as historical | ADR-013 |
| 36 | `docs/MVP_WBS.md` | MVP WBS | MVP work breakdown | **OUTDATED** | MVP payroll WBS | Mark as historical | ADR-013 |
| 37 | `docs/MVP_SCOPE.md` | MVP Scope | MVP scope | **OUTDATED** | MVP payroll scope | Mark as historical | ADR-013 |
| 38 | `docs/FUTURE_BACKLOG.md` | Backlog | Future backlog items | **NEEDS_UPDATE** | Payroll backlog | Add salary estimation backlog items | ADR-013 |
| 39 | `docs/AGENT_OPERATING_MODEL.md` | Agent model | Agent operating rules | **VALID** | None | Still applicable | — |
| 40 | `docs/AGENT_GUIDE.md` | Agent guide | Agent guide | **VALID** | None | Still applicable | — |
| 41 | `docs/ADR_INDEX.md` | ADR index | ADR register | **NEEDS_UPDATE** | ADR-008/010 status | Add ADR-013; update ADR-008/010 rows with partial supersession notes | ADR-013 |
| 42 | `docs/adr/ADR-001…013.md` | ADRs | Architecture decisions | **MIXED** | ADR-008/010 partially superseded | Update headers (done); preserve all historical text | ADR-013 |
| 43 | `infra/postgres/README.md` | Postgres README | PostgreSQL setup | **OUTDATED** | Payroll DB setup | Mark as historical; salary estimation needs simpler DB | ADR-013 |
| 44 | `frontend/README.md` | Frontend README | Frontend foundation docs | **NEEDS_UPDATE** | References payroll WBS tasks | Update to salary estimation frontend tasks | ADR-013 |
| 45 | `AUTONOMOUS_PROGRESS.md` | Progress log | Autonomous progress | **UNCERTAIN** | Unknown | Review after read | ADR-013 |
| 46 | `.kilo/plans/*.md` | Kilo plans | Kilo session plans | **VALID** | None | Add this audit plan | — |
| 47 | `docs/audit/DOCUMENTATION_AUDIT.md` | This file | Documentation audit matrix | **NEW** | — | — | — |

---

## 3. Classification Summary

| Classification | Count | Documents |
|:---|:---|:---|
| **VALID** | 5 | AGENT_OPERATING_MODEL.md, AGENT_GUIDE.md, ENVIRONMENT_INVENTORY.md, BOOTSTRAP_CHANGELOG.md, FRONTEND_PERSIAN.md |
| **NEEDS_UPDATE** | 13 | README.md, AGENTS.md, PROJECT_STATUS.md, PROJECT_STATE.md, ARCHITECTURE.md, DOCUMENTATION_INDEX.md, EXECUTION_PLAN.md, IMPLEMENTATION_READINESS.md, DECISIONS_REGISTER.md, DECISION_REQUIRED_FROM_OWNER.md, DECISIONS.md, TESTING.md, DEPLOYMENT.md, AUTH.md, WORK_PROFILE_PAYROLL.md, FRONTEND_PERSIAN.md(partial), MVP_WBS.md(partial), MVP_SCOPE.md(partial), FUTURE_BACKLOG.md, ADR_INDEX.md, ADR-008/010 headers |
| **OUTDATED** | 12 | PROJECT_STATE.md, PROJECT_HANDOFF_SUMMARY.md, PRODUCT_AUDIT_REPORT.md, PHASE_1_RED_TEAM_AUDIT.md, REMEDIATED_TECHNICAL_SPECIFICATION_V2.md, EXECUTION_PLAN.md (WBS), STATUTORY_INGESTION.md, STATUTORY_DATABASE_CONTRACT.md, AUTH.md, WORK_PROFILE_PAYROLL.md, ROADMAP_OPERATIONAL_PAYROLL.md, MVP_WBS.md, MVP_SCOPE.md, infra/postgres/README.md |
| **OBSOLETE** | 6 | PHASE_1_FINAL_AUDIT_BRIEF.md, RESEARCH_GAP_ANALYSIS_AND_ADVANCED_SPECIFICATION.md, 3 DOCX files, STATUTORY_DATABASE_CONTRACT.rev2.md, DOCUMENT_FORENSICS.md |
| **UNCERTAIN** | 4 | PROJECT_HANDOFF_SUMMARY.md, PRODUCT_AUDIT_REPORT.md, CURRENT_STATE.md, AUTONOMOUS_PROGRESS.md |
| **SUPERSEDED** | 1 | EXECUTION_DOCUMENTATION_AUDIT.md (replaced by this file) |
| **NEW** | 1 | DOCUMENTATION_AUDIT.md (this file) |

---

## 4. Major Contradictions Discovered

| # | Contradiction | Documents Involved | Resolution |
|:--|:---|:---|:---|
| 1 | Product is statutory payroll engine vs product is salary estimation tool | ADR-008, ADR-010, README.md, PROJECT_STATUS.md vs ADR-013 | ADR-013 wins; ADR-008/010 marked partially superseded; README.md to be rewritten |
| 2 | Multi-tenant RLS, tenant_id, FORCE ROW LEVEL SECURITY vs single manager, no tenant isolation | ADR-006, ADR-007, AUTH.md, ARCHITECTURE.md §5 vs ADR-013 §7 | RLS/tenant decisions preserved as technical options but not required for new product; marked optional |
| 3 | AES-256-GCM + blind indexing for PII vs simple manager-only storage | ADR-003, SECURITY sections vs ADR-013 §7 | Encryption preserved as good practice but simplified; no blind index needed for resume data |
| 4 | Statutory rule ingestion (1404/1405) vs market data acquisition | SPEC-STAT-001, ADR-008 vs ADR-013 | Statutory ingestion marked historical; new LABOR_MARKET_DATA_SPEC.md needed |
| 5 | Gross-to-net API endpoint vs salary estimation API | ADR-008, contracts.ts vs ADR-013 | Gross-to-net endpoint preserved as technical code; new estimation endpoints needed |
| 6 | 88 WBS tasks across 5 phases vs simple estimation tool | EXECUTION_PLAN.md, PROJECT_STATUS.md vs ADR-013 | Payroll WBS marked historical; new WBS for estimation tool needed |

---

## 5. Major Product Assumptions Removed

1. **Statutory payroll calculation** (SSO, tax, net pay, overtime, severance, Eydi, CTC, Article 11) — removed as product scope; preserved as technical code.
2. **Multi-tenant architecture** (tenant_id, RLS, FORCE ROW LEVEL SECURITY) — removed as requirement; preserved as optional pattern.
3. **Multi-role authentication** (7 roles, MFA, sessions) — removed; single manager only.
4. **Statutory rule-set activation gate (A1–A8)** — removed; not applicable to market-based estimation.
5. **1404/1405 rule-set loader** — removed as product path; preserved as technical code.
6. **Employee management, payslips, attendance, accounting** — removed entirely.
7. **Document forensics, OCR, Shahkar verification** — removed as product scope.

---

## 6. Required New Documents

Per the mission deliverables, the following documents must be created:

| # | Deliverable | File Path | Status |
|:--|:---|:---|:---|
| 1 | Documentation Audit Matrix | `docs/audit/DOCUMENTATION_AUDIT.md` | **DONE** (this file) |
| 2 | Product Vision | `docs/PRODUCT_VISION.md` | To be created |
| 3 | Product Scope | `docs/PRODUCT_SCOPE.md` | To be created |
| 4 | Functional Requirements | `docs/FUNCTIONAL_REQUIREMENTS.md` | To be created |
| 5 | Non-Functional Requirements | `docs/NON_FUNCTIONAL_REQUIREMENTS.md` | To be created |
| 6 | User Workflows | `docs/USER_WORKFLOWS.md` | To be created |
| 7 | Salary Estimation Spec | `docs/SALARY_ESTIMATION_SPEC.md` | To be created |
| 8 | Labor Market Data Spec | `docs/LABOR_MARKET_DATA_SPEC.md` | To be created |
| 9 | AI Analysis Spec | `docs/AI_ANALYSIS_SPEC.md` | To be created |
| 10 | Data Model Spec | `docs/DATA_MODEL_SPEC.md` | To be created |
| 11 | Security and Privacy | `docs/SECURITY_AND_PRIVACY.md` | To be created |
| 12 | Architecture | `docs/ARCHITECTURE.md` | To be updated (exists) |
| 13 | Implementation Roadmap | `docs/IMPLEMENTATION_ROADMAP.md` | To be created |
| 14 | Open Decisions | `docs/OPEN_DECISIONS.md` | To be created |
| 15 | Updated README | `README.md` | To be updated (exists) |

---

## 7. Documents Preserved as Historical (Not Modified)

These documents retain their historical text and are NOT edited:

- `PHASE_1_FINAL_AUDIT_BRIEF.md`
- `RESEARCH_GAP_ANALYSIS_AND_ADVANCED_SPECIFICATION.md`
- `گزارش جامع پژوهشی.docx`
- `Technical Investigation of Related Software Projects.docx`
- `1.docx`
- `docs/specs/history/STATUTORY_DATABASE_CONTRACT.rev2.md`
- `docs/specs/DOCUMENT_FORENSICS.md`
- All ADR files (`docs/adr/ADR-001…013.md`) — headers updated only; text retained unchanged

---

## 8. Next Steps

1. Owner reviews and approves this audit matrix.
2. Create the 14 new/updated documentation deliverables listed in §6.
3. Update `README.md` to reflect the new product vision.
4. Update `DOCUMENTATION_INDEX.md` to reflect the new documentation structure.
5. Update `ADR_INDEX.md` to include ADR-013 and updated ADR-008/010 rows.
6. Owner reviews final documentation set for consistency.
7. No code changes until documentation is approved.
