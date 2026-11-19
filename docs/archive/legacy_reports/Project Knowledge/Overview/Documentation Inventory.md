---
title: "Documentation Inventory — Pish Hesabdari"
document_id: KNOW-INV-001
status: Active navigation layer
as_of: 2026-11-16
---

# Documentation Inventory

> Audit of the existing project documentation. **No file was moved, renamed, copied or rewritten.** All links point to the original location.

## Summary

| Group | Count | Notes |
| :--- | :--: | :--- |
| Root Markdown documents | 8 | governance, handoff, audits, historical research |
| `docs/` Markdown documents | 29 | includes 8 ADRs, 8 specifications, indexes and evidence |
| Agent skill contracts | 11 | `.agents/skills/*/SKILL.md` |
| Module READMEs | 2 | `frontend/README.md`, `infra/postgres/README.md` |
| **Project Markdown total** | **50** | excludes `.kilo/` and `.zcode/` local agent plans, caches, `node_modules`, `.venv` and this Obsidian layer |

**Authoritative version of the Holy Bible:** `DOC-HOLY-001`, **version 1.0.7**, compiled 2026-11-15. The version is read from the document header; its implementation-state metadata is a dated snapshot and is **not** the current delivery status.

**Current delivery status authority:** [PROJECT_STATUS.md](../../docs/PROJECT_STATUS.md) (§2, evidence §24) plus the WBS in [EXECUTION_PLAN.md](../../docs/EXECUTION_PLAN.md) §14.3.

## Root documents

| File | Role | Status / note |
| :--- | :--- | :--- |
| [AGENTS.md](../../AGENTS.md) | Operating contract, invariants, change control | Active |
| [README.md](../../README.md) | Repository overview and run commands | Active, but its test counts predate §24 — use PROJECT_STATUS |
| [AUTONOMOUS_PROGRESS.md](../../AUTONOMOUS_PROGRESS.md) | Remediation tracker | Active local record |
| [PROJECT_HANDOFF_SUMMARY.md](../../PROJECT_HANDOFF_SUMMARY.md) | Agent handoff summary | **Historical snapshot**; counts superseded |
| [REMEDIATED_TECHNICAL_SPECIFICATION_V2.md](../../REMEDIATED_TECHNICAL_SPECIFICATION_V2.md) | Product/technical specification | Rank 2 authority |
| [PHASE_1_RED_TEAM_AUDIT.md](../../PHASE_1_RED_TEAM_AUDIT.md) | Findings and corrections register | Rank 3 evidence |
| [PHASE_1_FINAL_AUDIT_BRIEF.md](../../PHASE_1_FINAL_AUDIT_BRIEF.md) | Baseline brief | **Superseded**; historical |
| [RESEARCH_GAP_ANALYSIS_AND_ADVANCED_SPECIFICATION.md](../../RESEARCH_GAP_ANALYSIS_AND_ADVANCED_SPECIFICATION.md) | Research synthesis | **Historical**; supersession map in DOCUMENTATION_INDEX |

## `docs/` — governance, status and planning

| File | Role |
| :--- | :--- |
| [PISH_HESABDARI_HOLY_BIBLE.md](../../docs/PISH_HESABDARI_HOLY_BIBLE.md) | Primary project knowledge base; v1.0.7 |
| [DOCUMENTATION_INDEX.md](../../docs/DOCUMENTATION_INDEX.md) | Task-focused reading and supersession map |
| [ADR_INDEX.md](../../docs/ADR_INDEX.md) | ADR register and rejected technologies |
| [PROJECT_STATUS.md](../../docs/PROJECT_STATUS.md) | **Current delivery state and verified evidence** |
| [EXECUTION_PLAN.md](../../docs/EXECUTION_PLAN.md) | Master plan, WBS, dependencies, gates |
| [DECISIONS_REGISTER.md](../../docs/DECISIONS_REGISTER.md) | 19 DEC entries + B-series ambiguity ledger |
| [DECISION_REQUIRED_FROM_OWNER.md](../../docs/DECISION_REQUIRED_FROM_OWNER.md) | Owner-facing decision queue |
| [IMPLEMENTATION_READINESS.md](../../docs/IMPLEMENTATION_READINESS.md) | Per-phase readiness assessment |
| [BOOTSTRAP_CHANGELOG.md](../../docs/BOOTSTRAP_CHANGELOG.md) | Chronological execution evidence; §24 is the latest |
| [AGENT_OPERATING_MODEL.md](../../docs/AGENT_OPERATING_MODEL.md) | Roles, delegation, isolation and verification |
| [ENVIRONMENT_INVENTORY.md](../../docs/ENVIRONMENT_INVENTORY.md) | Dated tool/environment observations |
| [PHASE_0_BOOTSTRAP_PLAN.md](../../docs/PHASE_0_BOOTSTRAP_PLAN.md) | Phase 0 bootstrap plan |
| [EXECUTION_DOCUMENTATION_AUDIT.md](../../docs/EXECUTION_DOCUMENTATION_AUDIT.md) | Documentation-package self-audit |

## `docs/adr/` — Architecture Decision Records

| ADR | Status |
| :--- | :--- |
| [ADR-001 — React + Vite SPA](../../docs/adr/ADR-001-frontend-architecture-react-vite-spa.md) | Accepted |
| [ADR-002 — Ceph / S3 WORM storage](../../docs/adr/ADR-002-object-storage-worm-ceph-s3-governance.md) | Accepted |
| [ADR-003 — ALEE encryption and blind indexing](../../docs/adr/ADR-003-sensitive-data-encryption-alee-blind-indexing.md) | Accepted |
| [ADR-004 — Phase 1 product boundary](../../docs/adr/ADR-004-phase-1-product-boundary-prehire-scope.md) | Accepted; module list/directives 2–3 superseded by ADR-008 |
| [ADR-005 — Async execution](../../docs/adr/ADR-005-async-execution-strategy.md) | **PROPOSED** — not binding |
| [ADR-006 — Phase 0 security and schema](../../docs/adr/ADR-006-phase-0-owner-approved-security-and-schema.md) | Accepted |
| [ADR-007 — Global statutory access](../../docs/adr/ADR-007-statutory-global-access-and-deferred-identity.md) | Accepted; **missing from ADR_INDEX and DOCUMENTATION_INDEX** |
| [ADR-008 — Product scope refocus](../../docs/adr/ADR-008-product-scope-statutory-payroll-engine.md) | Accepted |

**Conflict:** the two indexes above do not list ADR-007. The ADR file and [DECISIONS_REGISTER](../../docs/DECISIONS_REGISTER.md) both record `Accepted`. This inventory does not resolve the conflict; the original documents are unchanged.

## `docs/specs/` — subsystem specifications

| File | Scope |
| :--- | :--- |
| [AUTH.md](../../docs/specs/AUTH.md) | Identity, roles, sessions, MFA, tenant isolation, audit, keys |
| [DEPLOYMENT.md](../../docs/specs/DEPLOYMENT.md) | Topology, configuration, TLS, observability, backup, rollback, §7.1 API |
| [DOCUMENT_FORENSICS.md](../../docs/specs/DOCUMENT_FORENSICS.md) | Document forensics — out of ADR-008 v1 scope |
| [FRONTEND_PERSIAN.md](../../docs/specs/FRONTEND_PERSIAN.md) | RTL, typography, Jalali calendar, Persian PDF |
| [STATUTORY_DATABASE_CONTRACT.md](../../docs/specs/STATUTORY_DATABASE_CONTRACT.md) | Five statutory tables, RLS and access contract |
| [STATUTORY_INGESTION.md](../../docs/specs/STATUTORY_INGESTION.md) | Acquisition, transcription, verification, activation |
| [TESTING.md](../../docs/specs/TESTING.md) | Test layers, fixtures, CI stages, release criteria |
| [history/STATUTORY_DATABASE_CONTRACT.rev2.md](../../docs/specs/history/STATUTORY_DATABASE_CONTRACT.rev2.md) | Retained historical revision |

## Agent skill contracts

| Skill | File |
| :--- | :--- |
| Actuarial risk modeling | [SKILL.md](../../.agents/skills/actuarial-risk-modeling/SKILL.md) |
| ADR authoring | [SKILL.md](../../.agents/skills/adr-authoring/SKILL.md) |
| Database engineering | [SKILL.md](../../.agents/skills/database-engineering/SKILL.md) |
| Doubt-driven development | [SKILL.md](../../.agents/skills/doubt-driven-development/SKILL.md) |
| Financial data integrity | [SKILL.md](../../.agents/skills/financial-data-integrity/SKILL.md) |
| Iranian payroll engineering | [SKILL.md](../../.agents/skills/iranian-payroll-engineering/SKILL.md) |
| Persian RTL engineering | [SKILL.md](../../.agents/skills/persian-rtl-engineering/SKILL.md) |
| Product discovery | [SKILL.md](../../.agents/skills/product-discovery/SKILL.md) |
| Security threat model | [SKILL.md](../../.agents/skills/security-threat-model/SKILL.md) |
| Software architecture | [SKILL.md](../../.agents/skills/software-architecture/SKILL.md) |
| Spec-driven development | [SKILL.md](../../.agents/skills/spec-driven-development/SKILL.md) |

## Module READMEs

- [frontend/README.md](../../frontend/README.md) — frontend development and test commands.
- [infra/postgres/README.md](../../infra/postgres/README.md) — local PostgreSQL setup and hardening.

## Not included as authorities

- `.kilo/plans/`, `.zcode/plans/` — local agent planning state, not project documentation.
- `.freebuff/`, `.secrets/`, caches, `node_modules/`, `.venv/` — local state; never publish or sync.
- `Project Knowledge/` — this navigation layer, ranked below implementation documentation.
