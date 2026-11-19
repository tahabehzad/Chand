---
title: "Decision Status — Pish Hesabdari"
document_id: KNOW-DEC-001
status: Active navigation layer
as_of: 2026-11-16
---

# Decision Status

> **Status labels are copied from the source.** This note does not resolve, approve or reopen any decision. Authority: [DECISIONS_REGISTER.md](../../docs/DECISIONS_REGISTER.md), [ADR_INDEX.md](../../docs/ADR_INDEX.md) and the individual ADR files. Where sources disagree, both are linked and the conflict remains open.

## Accepted ADRs (binding)

| ADR | Title | Status | Date |
| :--- | :--- | :--- | :--: |
| [ADR-001](../../docs/adr/ADR-001-frontend-architecture-react-vite-spa.md) | React + Vite SPA | **Accepted** | 2026-11-13 |
| [ADR-002](../../docs/adr/ADR-002-object-storage-worm-ceph-s3-governance.md) | Ceph / S3-compatible storage and `GOVERNANCE` WORM locking | **Accepted** | 2026-11-13 |
| [ADR-003](../../docs/adr/ADR-003-sensitive-data-encryption-alee-blind-indexing.md) | ALEE encryption and blind indexing | **Accepted** | 2026-11-13 |
| [ADR-004](../../docs/adr/ADR-004-phase-1-product-boundary-prehire-scope.md) | Phase 1 pre-hire boundary | **Accepted** — module list/directives 2–3 superseded by ADR-008; original text retained | 2026-11-13 |
| [ADR-006](../../docs/adr/ADR-006-phase-0-owner-approved-security-and-schema.md) | Owner-approved Phase 0 security and schema choices | **Accepted** | 2026-11-14 |
| [ADR-007](../../docs/adr/ADR-007-statutory-global-access-and-deferred-identity.md) | Global statutory access and deferred identity references | **Accepted** | 2026-11-15 |
| [ADR-008](../../docs/adr/ADR-008-product-scope-statutory-payroll-engine.md) | Product scope refocus on the statutory payroll engine | **Accepted** | 2026-11-15 |

## Proposed ADR (not binding)

| ADR | Title | Status | Consequence |
| :--- | :--- | :--- | :--- |
| [ADR-005](../../docs/adr/ADR-005-async-execution-strategy.md) | Asynchronous execution strategy | **PROPOSED** | Must not be cited as a binding constraint; `P2-T04` remains blocked; no queue is approved. |

## DEC register

**Summary from the source:** 19 entries — **11 open (7 blocking, 4 non-blocking)**, **6 resolved**, **2 rejected**. Source: [DECISIONS_REGISTER](../../docs/DECISIONS_REGISTER.md).

### Open — blocking

| ID | Question | Phase |
| :--- | :--- | :--: |
| `DEC-001` | 1405 statutory baseline verification | Phase 1 |
| `DEC-002` | Corrected worked example and golden corpus | Phase 1 |
| `DEC-003` | Asynchronous execution strategy | Phase 2 |
| `DEC-010` | Deployment topology | Phase 4 |
| `DEC-011` | Document-intelligence acceptance criteria | Phase 2 |
| `DEC-011a` | Shahkar access route | Phase 2 |
| `DEC-011c` | Article 86 720-day insured-days threshold | Phase 2 |

### Open — non-blocking

| ID | Question | Phase |
| :--- | :--- | :--: |
| `DEC-006` | Persian RTL / Jalali / PDF choices | Phase 3 |
| `DEC-009` | Tax-optimization advisory boundary | Phase 3 |
| `DEC-011b` | Human adjudication of flagged documents | Phase 2 |
| `DEC-013` | Apply statutory allowance floors and seniority base to net | v1 reference-only |

### Resolved

| ID | Resolution | Authority |
| :--- | :--- | :--- |
| `DEC-002a` | Taxable-base definition | ADR-008 |
| `DEC-004` | Authentication and authorization model | ADR-006 |
| `DEC-004a` | MFA mandatory role set | ADR-006 |
| `DEC-004b` | Hash-chain scope for access events | ADR-006 |
| `DEC-005` | Database schema corrections | ADR-006 |
| `DEC-012` | Statutory provenance ownership and user-FK ordering | ADR-007 |

### Rejected — out of product scope

| ID | Decision | Authority |
| :--- | :--- | :--- |
| `DEC-007` | Market-data ingestion and licensing | ADR-008 |
| `DEC-008` | Data-flywheel policy | ADR-008 |

**Do not reintroduce a rejected technology or decision without a new, reviewed ADR that supersedes the named decision.** See [ADR_INDEX §5 rejected technologies](../../docs/ADR_INDEX.md).

## B-series ambiguity ledger

These are statutory/product ambiguities raised by the engine review, separate from the DEC numbering. They do **not** authorise inventing a statutory value.

| ID | Ambiguity | Status |
| :--- | :--- | :--- |
| B-1 | Appendix A mixes a full Article 137 deduction with taxable welfare allowances | `OPEN` — Tax Accountant; DEC-002 |
| B-2 | Which Article 137 reading has legal effect | `OPEN` — Counsel; ADR-008 scope decision |
| B-3 | SSO insurable base: total gross vs fixed wage | `OPEN` — SSO/Counsel |
| B-4 | Overtime/night premiums in Sanavat and Eydi bases | `OPEN` — Labour Counsel |
| B-5 | Eydi cap basis and pre/post-tax application | `OPEN` — Tax Accountant |
| B-6 | Eydi exemption interaction with salary exemption | `OPEN` — Tax Accountant |
| B-7 | Article 71 leave-buyout divisor and welfare participation | `OPEN` — Labour Counsel |
| B-8 | Month-length convention for monthly statutory amounts | `OPEN` — Labour Counsel |
| B-9 | Seed status flag vs loader year gate | `RESOLVED — engineering` (fail-closed behaviour verified) |
| B-10 | Loaded but unused statutory parameters | `OPEN` — Project Owner; DEC-013 |
| B-11 | Refusal taxonomy | `RESOLVED — engineering` (A-9/A-13) |

Source: [DECISIONS_REGISTER B-series ledger](../../docs/DECISIONS_REGISTER.md).

## Conflicts and gaps

> [!warning] باز — حل‌نشده
> **1. ADR-007 missing from both indexes.**
> The ADR file and DECISIONS_REGISTER record `Accepted`, but [ADR_INDEX](../../docs/ADR_INDEX.md) and [DOCUMENTATION_INDEX](../../docs/DOCUMENTATION_INDEX.md) do not list ADR-007. Status: **CONFLICT / MISSING**. No index was edited during this Obsidian integration.
>
> **2. Stale implementation snapshots.**
> [README](../../README.md), [PROJECT_HANDOFF_SUMMARY](../../PROJECT_HANDOFF_SUMMARY.md) and the Holy Bible metadata record older test counts and an older WBS census. [PROJECT_STATUS](../../docs/PROJECT_STATUS.md) §2 (2026-11-16, §24) is the current delivery authority. Status: **CONFLICT / stale snapshot**; historical documents were not rewritten.
>
> **3. ADR_INDEX §4 wording on migrations.**
> The ADR index still says DEC-005 implementation/migrations remain pending, while the isolated P0-T04 migration exists and is `READY_FOR_REVIEW` ([PROJECT_STATUS §2](../../docs/PROJECT_STATUS.md)). Treat the index statement as historical wording, not current status. Status: **CONFLICT / stale wording**.

## Reading rule

1. Accepted ADRs are binding; Proposed ADRs are not.
2. A decision register entry is authoritative for its own status.
3. An open decision must not be resolved by an implementation note, a dashboard or an agent.
4. A legal ambiguity is escalated to the named human approver; it is never closed by guessing.
