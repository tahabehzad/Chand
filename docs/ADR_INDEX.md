# Architecture Decision Record Index

- **Document ID:** `DOC-ADRIDX-001`
- **Status:** Active
- **Date:** 2026-11-14 (23 Aban 1405 SH)
- **Related:** [`docs/EXECUTION_PLAN.md`](EXECUTION_PLAN.md) §5 · [`docs/DOCUMENTATION_INDEX.md`](DOCUMENTATION_INDEX.md)

---

## 1. Register

| ADR | Title | Status | Date | Deciders | Affects |
| :--- | :--- | :--- | :--: | :-- | :-- |
| [ADR-001](adr/ADR-001-frontend-architecture-react-vite-spa.md) | Selection of React + Vite SPA over Next.js SSR for the Enterprise Client Application | **Accepted** | 2026-11-13 | Enterprise Architect, Frontend Lead, Security Architect | `P3-T01`, `P3-T14`, deployment topology |
| [ADR-002](adr/ADR-002-object-storage-worm-ceph-s3-governance.md) | Replacement of MinIO with Ceph / S3-compatible storage and adoption of `GOVERNANCE` WORM locking | **Accepted** | 2026-11-13 | Infrastructure Architect, Legal Counsel, Security Lead | `P0-T11`, `P2-T03`, `P4-T04`, emergency access |
| [ADR-003](adr/ADR-003-sensitive-data-encryption-alee-blind-indexing.md) | Adoption of Application-Level Envelope Encryption (ALEE) and blind indexing for candidate PII | **Accepted** | 2026-11-13 | Security Architect, Database Administrator, Lead Backend Engineer | `P0-T06`, `P0-T07`, `P0-T08`, `P0-T12`, `P4-T04` |
| [ADR-004](adr/ADR-004-phase-1-product-boundary-prehire-scope.md) | De-escalation of Phase 1 scope to pure pre-hire simulation and deferral of post-hire HRIS operations | **Accepted** — module list and directives 2–3 superseded by ADR-008 (2026-11-15); original text retained unchanged | 2026-11-13 | Lead Product Manager, CTO, Head of Engineering | `REMEDIATED` §1.2, §2; every phase's scope |
| [ADR-005](adr/ADR-005-async-execution-strategy.md) | Asynchronous execution strategy for long-running document processing | **PROPOSED** | 2026-11-14 | CTO (owner), DevOps Lead, Lead Backend Engineer, Security Architect | `P2-T04` (blocked), `P2-T05`–`P2-T09`, `P4-T01` |
| [ADR-006](adr/ADR-006-phase-0-owner-approved-security-and-schema.md) | Owner-approved identity, privileged MFA, split audit scope and schema corrections | **Accepted** | 2026-11-14 | Project Owner (actual chat approval; no invented human role signatures) | DEC-004/004a/004b/005; supersedes ADR-003 directive 3's table name only |
| [ADR-007](adr/ADR-007-statutory-global-access-and-deferred-identity.md) | Global statutory provenance access and deferred identity references | **Accepted** | 2026-11-15 | Project Owner (explicit approval, T-2/F-1) | Resolves DEC-012; `P0-T04` five-table baseline, roles and write gate; `P0-T05` owns the deferred users FKs |
| [ADR-008](adr/ADR-008-product-scope-statutory-payroll-engine.md) | Product scope refocus on the statutory payroll calculation engine (minimal boundary; DEC-002a and the Art. 137 primary posture resolved) | **Accepted** | 2026-11-15 | Project Owner (explicit in-session answers) | Supersedes ADR-004's Phase 1 module list and implementation directives 2–3 only; resolves DEC-002a; unblocks `P1-T01`–`P1-T12`, `P1-T14` engine path |
| [ADR-009](adr/ADR-009-compensation-advisory-module.md) | Compensation advisory module: manager-entered profiles, band placement and statutory costing of the proposed range | **Accepted** | 2026-11-16 | Project Owner (explicit in-session answers) | Extends ADR-008 (removes nothing); adds `P5-T01`, `P5-T02`; bounds DEC-009 to a neutral calculator posture; keeps DEC-007/DEC-008 rejected |

---

## 2. Status semantics

| Status | Meaning | Binding? |
| :--- | :--- | :--: |
| **Accepted** | Approved by the recorded deciders; implementation must conform | **Yes** |
| **Proposed** | A drafted, fully analysed recommendation awaiting the named approver | **No** |
| **Deprecated** | Superseded by another ADR; retained for history | No |
| **Superseded** | Replaced by a later ADR, which must be named | No |
| **Rejected** | Considered and declined; must not be reintroduced without a new ADR | No |

**Only `Accepted` ADRs are binding.** `ADR-005` is `PROPOSED`; the corresponding task `P2-T04` is `BLOCKED`.

---

## 3. Recorded conflicts between architectural statements

| # | Conflict | Documents | Resolution |
| :--: | :--- | :--- | :--- |
| 1 | **Async durability and isolation.** `REMEDIATED` §3.1 and the architecture skill both specify `BackgroundTasks`; neither mandates Celery/Redis. In-process work does not settle the durable separate-worker requirement. | Current specification versus reliability requirements; alternatives are proposed only. | **ADR-005 remains PROPOSED.** Its factual premise is corrected; `P2-T04` stays `BLOCKED`. No queue has been approved. |
| 2 | **Blind-index table.** ADR-003 directive 3 indexes `employees (tenant_id, national_id_bindex)`. `REMEDIATED` §4.1 defines `national_id_bindex` on `CANDIDATES` and gives `EMPLOYEES` no columns. | ADR-003 (rank 1) vs. the specification (rank 2). | A **correction**, not a conflict of intent: the index belongs on `candidates`, because Phase 1 is pre-hire only (ADR-004). Recorded as **DEC-005**; the ADR text is unchanged pending approval. |
| 3 | **Hash column width.** ADR-003 specifies `CHAR(64)` for the blind index. `REMEDIATED` §4.1 declares `char` without a length, which PostgreSQL treats as `CHAR(1)`. | The specification is defective. | Corrected by migration `P0-T12`; a CI migration lint rejects a lengthless `CHAR`. Recorded in **DEC-005**. |

---

## 4. Decisions that do **not** yet have an ADR

These are gaps. Each is covered by a register entry and, where architectural, should be raised as an ADR.

| Topic | Register | Status |
| :--- | :--: | :--- |
| Authentication/session core, seven roles, privileged MFA, read/mutation audit split | DEC-004/004a/004b | **Resolved — ADR-006 Accepted**; unapproved timing/emergency/key details are not ratified |
| Database schema corrections (§6.2 of the execution plan) | DEC-005 | **Resolved — ADR-006** formally corrects ADR-003 index target; implementation/migrations remain pending |
| Statutory rule-set versioning and the four-eyes activation gate | DEC-001 | Open — procedure documented in `SPEC-STAT-001`; an ADR is recommended |
| Market data ingestion and licensing | DEC-007 | **REJECTED — out of product scope (ADR-008, 2026-11-15)**; DEC-008 likewise out of scope |
| Taxable-base treatment of welfare allowances × Art. 137 posture | DEC-002a | **Resolved — ADR-008 Accepted** (posture-dependent: taxable under `conservative_inta`, exempt under `court_precedent`; both always reported; `conservative_inta` is the primary response posture) |
| Deployment topology | DEC-010 | Open — an ADR is recommended for the air-gapped baseline |
| Persian localisation strategy | DEC-006 | Open — an engineering decision documented in `SPEC-FE-001` |
| Job queue data model and lease protocol | ADR-005 | **Proposed** |

---

## 5. Rejected technologies — the "do not reintroduce" register

A technology on this list may not reappear in any specification or implementation without a **new, reviewed ADR** that supersedes the named decision.

| Technology / approach | Rejected by | Reason |
| :--- | :--- | :--- |
| PostgreSQL `pgcrypto` for PII encryption | ADR-003 (`FIND-ARCH-03`, `FIND-DATA-02`) | Plaintext keys enter the SQL layer, statement logs and replication streams |
| MinIO with S3 Object Lock `COMPLIANCE` mode | ADR-002 (`FIND-ARCH-02`) | AGPLv3 copyleft; `COMPLIANCE` makes judicial expungement impossible |
| The 50-iteration bisection net-to-gross solver | `REMEDIATED` Module 2 (`FIND-MATH-01`) | A piecewise linear function has an O(1) closed form |
| MCDA company-wide salary-review endpoints | ADR-004 (`FIND-PROD-01`) | Scope creep; deferred to a standalone Phase 2 product |
| Operational *Tasviyeh Hesab* execution and Sheba disbursement | ADR-004 (`FIND-PROD-02`) | Out of scope for Phase 1 |
| Next.js SSR | ADR-001 (`FIND-ARCH-01`) | Node.js runtime overhead and attack surface for an authenticated SPA |
| Direct *Sabt-e Ahval* (Civil Registration) API integration | `FIND-ARCH-07` | Legally unavailable to private employers |
| Automated / background Shahkar verification | `FIND-ARCH-07` | The CRA mandate requires interactive SMS OTP consent |
| Live scraping of Jobinja or similar job boards | `1.docx` Defect 5 | Terms-of-service violation; advertised pay ≠ paid salary |
| The 26-day statutory paid-leave reserve inside CTC | `FIND-MATH-02` | Double counting of paid working days already inside 12 months of salary |
| A flat 10 % tax rate on Eydi excess | `FIND-LEG-04` | The excess is taxed across the progressive brackets |
| A 176-hour overtime divisor | `FIND-LEG-03`, `1.docx` Defect 3 | 176 h is for attendance proration; the statutory divisor is 220 / 227.33 h |
| A full 100 % effective tax rate | §3 of the audit report | The defect found in the published §5.1 example |
| Redis as a mandatory on-site broker | **Proposed rejection only** — ADR-005 is not Accepted | Evaluation recorded; not a binding rejection by this index |
| Stateless JWT with no revocation path | **Proposed rejection only** — DEC-004 remains open | Revocation concern remains unresolved; no session implementation authorized |

---

## 6. ADR template

New ADRs follow the MADR 3.0 / Nygard structure already used by ADR-001…ADR-004:

```markdown
# ADR-[NNN]: [Title]

- **Status**: [Proposed | Accepted | Superseded | Deprecated | Rejected]
- **Date**: [YYYY-MM-DD / SH Date]
- **Deciders**: [Roles]
- **Consulted**: [Roles]

## Context and Problem Statement
## Decision Drivers
## Considered Options
## Decision Outcome
### Positive Consequences
### Negative Consequences / Trade-offs
## Pros and Cons of Considered Options
## Implementation Directives
```

**Additional requirements for this project:**

1. An ADR that remains `Proposed` **must not** be cited as a binding constraint by any specification, task acceptance criterion or readiness assessment.
2. Every ADR must state explicitly which rejected technologies it supersedes, using §5 of this index as the canonical list.
3. An ADR affecting `ADR-001`…`ADR-004` must name the ADR it supersedes or amends.

---

## 7. Change control

| Rule | Detail |
| :--- | :--- |
| Status changes | Only the recorded deciders may change a status; the change is appended to the ADR with the date and the reason |
| Amendments | An amendment is a new ADR that supersedes the old one; the old ADR is marked `Superseded` and retained |
| Rejection | A rejected ADR stays in the register with `Rejected` status; its rationale is preserved so the decision is not relitigated without cause |
| Index sync | This index is updated within 1 working day of any ADR change |


## 2026-11-15 — DEC-012 resolution

[ADR-007](adr/ADR-007-statutory-global-access-and-deferred-identity.md) is Accepted by the Project Owner: T-2 global FORCE-RLS statutory records, restricted database roles and F-1 deferred identity FKs with write gate. [Contract revision 3](specs/STATUTORY_DATABASE_CONTRACT.md) governs P0-T04. No existing ADR or roadmap changed.

## 2026-11-15 — ADR-008 Accepted (product scope refocus)

[ADR-008](adr/ADR-008-product-scope-statutory-payroll-engine.md) is Accepted by the Project Owner: the product boundary is the statutory payroll calculation engine (SSO, progressive tax, net, overtime/night, Sanavat, Eydi, CTC, Art. 11) delivered as pure functions plus one minimal API endpoint on the verified 1404.1 baseline. ADR-004's Phase 1 module list and directives 2–3 are superseded (its text is retained unchanged); document forensics, title disambiguation, benchmarking (DEC-007/008 → REJECTED out of scope), the DB snapshot ledger, the net-to-gross inverter (`P1-T13`) and the external golden corpus (`P1-T15`) leave the product boundary pending a future superseding ADR. DEC-002a is resolved (posture-dependent welfare treatment; `conservative_inta` primary). The five-phase/20-week roadmap, ADR-001…007 and the rejected-technology register are unchanged. Evidence: `BOOTSTRAP_CHANGELOG.md` §23.
