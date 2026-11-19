# Pish Hesabdari — Master Execution Plan

- **Document ID:** `DOC-EXEC-001`
- **Version:** 1.0
- **Status:** Active — the central execution reference for Phase 1
- **Date:** 2026-11-14 (23 Aban 1405 SH)
- **Author:** Chief Software Architect (with Technical Program Management and Documentation Engineering)
- **Governing:** `REMEDIATED_TECHNICAL_SPECIFICATION_V2.md` (product & technical specification) + ADR-001…ADR-004 (accepted decisions)
- **Companion documents:** [`docs/DOCUMENTATION_INDEX.md`](DOCUMENTATION_INDEX.md) · [`docs/ADR_INDEX.md`](ADR_INDEX.md) · [`docs/DECISIONS_REGISTER.md`](DECISIONS_REGISTER.md) · [`docs/IMPLEMENTATION_READINESS.md`](IMPLEMENTATION_READINESS.md) · [`docs/EXECUTION_DOCUMENTATION_AUDIT.md`](EXECUTION_DOCUMENTATION_AUDIT.md)

---

## 1. Purpose, Authority and Document Hierarchy

### 1.1 Purpose

This document converts the project's research, specifications, accepted Architecture Decision Records and the external documentation audit into an **implementation-ready execution package**: a scoped product definition, a resolved specification baseline, a task-level work breakdown, a test strategy, an operational design and an explicit register of what remains undecided.

It does not replace the specifications it is derived from; it binds them, sequences them and identifies the gaps between them.

### 1.2 Document authority hierarchy

The following order is **binding**. When two documents conflict, the higher one wins, and the lower one must be corrected.

| Rank | Class | Documents | Binding scope |
| :--: | :--- | :--- | :--- |
| **1** | Accepted ADRs | `docs/adr/ADR-001`, `ADR-002`, `ADR-003`, `ADR-004` | Architectural decisions explicitly decided |
| **2** | Authoritative specification | `REMEDIATED_TECHNICAL_SPECIFICATION_V2.md` | Product scope, functional modules, technology stack, domain model, API contracts, roadmap and gates |
| **3** | Findings register | `PHASE_1_RED_TEAM_AUDIT.md` | Historical findings and their corrections; the disposition of each finding is authoritative |
| **4** | This execution package | `docs/EXECUTION_PLAN.md` + `docs/specs/*` + `docs/DECISIONS_REGISTER.md` | Sequencing, task decomposition, subordinate specifications, decisions register |
| **5** | Research (non-superseded content only) | `RESEARCH_GAP_ANALYSIS_AND_ADVANCED_SPECIFICATION.md`, `گزارش جامع پژوهشی.docx`, `Technical Investigation of Related Software Projects.docx`, `1.docx` | Background, methods, harvested technical content — **never** current implementation instructions |
| **6** | Historical / superseded | `PHASE_1_FINAL_AUDIT_BRIEF.md` | Reference only |

### 1.3 Rules of precedence

1. **No silent revival.** A recommendation rejected by a red-team finding or an ADR may not reappear without a new, reviewed ADR. The rejected set is enumerated in `docs/DOCUMENTATION_INDEX.md` §5.
2. **No silent narrowing.** Where this document proposes a change to a specification line (for example the session model in `REMEDIATED` §3), the proposal is recorded in `docs/DECISIONS_REGISTER.md` and the specification line is **not** altered until the decision lands.
3. **Documentation readiness ≠ implementation completion.** A specification being written does not make a task `COMPLETED`. Task status reflects work actually performed.
4. **Unknown is a first-class value.** An unverified statutory parameter, an inaccessible primary source or an undecided architecture is recorded as such. It is never filled with an estimate.

### 1.4 Change control

| Artefact | Change rule |
| :--- | :--- |
| This document | CTO approval; minor editorial corrections by Documentation Engineering |
| Subordinate specs | The named owner, with a cross-reference update here |
| ADRs | The recorded approver; a change of status is append-only |
| `DECISIONS_REGISTER.md` | Only the named approver may move an entry to `RESOLVED` |
| Task status | The responsible role, on evidence |

### 1.5 A note on file scope

This workstream created and modified files **only under `docs/`**. It did not write application source code, did not create scaffolding, did not install packages, did not modify the statutory seed files, did not execute migrations and did not change project configuration. Where a change outside `docs/` is required, it appears as a WBS task.

---

## 2. Product Scope, Phase Boundaries and Exclusions

### 2.1 Product mission

Pish Hesabdari (پیش‌حسابداری) is an enterprise **pre-employment workforce compensation intelligence and evidentiary verification platform** for the Iranian private and technology sectors. It operates strictly as an **analytical decision-support and pre-hire simulation engine** (*Hokm-e Kargozini* and *Markaz-e Hazineh* simulator) for CEOs, CFOs and HR Directors:

1. Synthesize legally defensible, market-benchmarked offers from verified records rather than self-reported claims.
2. Verify candidate authenticity against official Iranian issuers through multi-layer document forensics and interactive Shahkar identity validation.
3. Compute exact Total Cost to Employer, including direct wages, statutory employer burdens, severance, annual bonus and termination reserves.
4. Guarantee evidentiary immunity before Labor Dispute Settlement Boards (*Heyat-e Tashkhis*, *Heyat-e Hal-e Ekhtelaf*) through Supreme Court Precedent No. 272 and Article 10 clause alignment.

### 2.2 Phase 1 scope — locked by ADR-004

| # | Module | Phase 1 scope |
| :--: | :--- | :--- |
| 1 | Deterministic Iranian Statutory Wage & Tax Engine | 1405 SH active baseline + 1404 historical |
| 2 | Piecewise Analytical Net-to-Gross & Gross-to-Net Inverter | O(1) closed form |
| 3 | Forensic Document Intelligence & Iranian Authenticity Verification | PP-Structure + pyHanko |
| 4 | 4-Way Candidate Experience & Title Disambiguation | — |
| 5 | Pre-Hire Compensation Benchmarking | Bühlmann-Kish credibility model (pre-hire bands only) |
| 6 | Pre-Hire Total Cost to Employer & Termination Liability Simulator | Modelling only |
| 7 | Cryptographic Snapshot Ledger & SHA-256 Provenance Logging | — |

### 2.3 Strict exclusions (Phase 1)

| Excluded | Reason | Reconsider |
| :--- | :--- | :--- |
| Candidate-facing portals, accounts, resumes | No public-facing product surface | Never |
| Biometric attendance / punch clocks | Out of category | Never |
| Monthly payroll disbursement, Shetab batch files | Out of category | Never |
| General ledger accounting, tax filings | Out of category | Never |
| Company-wide annual salary review / MCDA | ADR-004 — deferred to a standalone Phase 2 product | Phase 2 |
| Operational exit settlement execution (*Tasviyeh Hesab*) | ADR-004 — Phase 1 models the liability only | Phase 2 |
| Direct *Sabt-e Ahval* API | Legally unavailable to private employers | Never |
| Live scraping of job boards | ToS violation (`1.docx` Defect 5) | DEC-007 |
| Automatic Shahkar verification | CRA mandate requires interactive OTP (`FIND-ARCH-07`) | Never |

### 2.4 Scope-change control

Any request to add a Phase 1 capability must be tested against §2.3 and against ADR-004. An accepted request requires a new ADR (for architectural items), a `DECISIONS_REGISTER.md` entry (for product-boundary items) and a re-baselined §14.

---

## 3. Regulatory Baseline and 1405 Ingestion Plan

### 3.1 The problem

`REMEDIATED_TECHNICAL_SPECIFICATION_V2.md` declares the **1405 SH** wage circular and Budget Law as the active baseline. The repository's only 1405 artefact, `backend/data/seeds/statutory_rules_1405.yaml`, contains **every parameter as `null`** with `is_verified_and_active: false`. The 1404 seed is populated and verified.

`1.docx` line 470 states the consequence plainly: *"Launching in Aban 1405 with 1404 rates invalidates live hiring recommendations."*

### 3.2 What was established during this workstream

Independent research on 2026-11-14 recovered the 1405 SH parameters with full provenance from the High Council of Labor wage circular (session 1404/12/24), Council of Ministers Resolution No. 9234 (1405/02/15), the SSO insurance-base circular 1405 and the Budget Law 1405.

**The complete transcription, per-parameter provenance, derivation and verification status is in [`docs/specs/STATUTORY_INGESTION.md`](specs/STATUTORY_INGESTION.md) §3.** The headline values:

| Parameter | 1404 (verified) | 1405 (transcribed, **not activated**) | Source |
| :--- | ---: | ---: | :--- |
| Daily minimum wage | 3,463,656 | **5,541,850** | Wage circular بند 1 |
| Monthly minimum wage (30d) | 103,909,680 | **166,255,500** | derived |
| Housing allowance | 9,000,000 | **30,000,000** | Cabinet Resolution 9234 |
| Grocery allowance | 22,000,000 | **22,000,000** (unchanged) | Wage circular بند 3 |
| Marriage allowance | 5,000,000 | **5,000,000** (unchanged) | Wage circular بند 4 |
| Child allowance / child | 10,390,968 | **16,625,550** | Labour Law Art. 86 (3 × daily wage) |
| Daily seniority base | 94,000 | **166,667** | Wage circular بند 2 |
| Monthly SSO ceiling (30d) | 727,367,760 | **1,163,788,500** | SSO circular item 13 (7 × daily) |
| Monthly tax exemption | 240,000,000 | **400,000,000** | Budget Law 1405, Art. 84 ceiling |
| Annual tax exemption | 2,880,000,000 | **4,800,000,000** | Budget Law 1405 |
| Tax slabs | 0/10/15/20/25/30 % @ 240M–666.7M | **0/10/15/20/25/30 % @ 400M–1,400M** | Budget Law 1405 |

### 3.3 What was **not** achieved, and why the baseline stays disabled

| # | Gap | Reason |
| :--: | :--- | :--- |
| 1 | **No L1 primary PDF retrieved** | `mcls.gov.ir` and `intamedia.ir` returned transport errors; `tamin.ir` returned HTTP 403. The values were obtained from L2/L3 legal-database and professional reproductions |
| 2 | Four-eyes verification not performed | Requires a Certified Tax Accountant and a Labor Law Counsel |
| 3 | Open items O1–O5 unresolved | SSO follow-up circular for the housing-allowance increase; the exact tax band edges as printed; the child-allowance legal citation; the budget-law citation string; the SSO circular date |
| 4 | Golden vector corpus does not exist | `P1-T15` |
| 5 | A correction to `1.docx` | `1.docx` inferred that 5,541,850 IRR/day was a "digit transposition" because it compared a **daily** wage against a **monthly** ceiling. Under the correct comparison the figure is a legitimate **+60.0 %** increase. Recorded in `SPEC-STAT-001` §3.6 |

### 3.4 The ingestion procedure

Eight stages, fully specified in [`docs/specs/STATUTORY_INGESTION.md`](specs/STATUTORY_INGESTION.md):

| Stage | Summary | Status |
| :--: | :--- | :--- |
| 1 | Source identification — an authority ladder (L1 primary → L2 legal database → L3 professional → L4 media); only L1/L2 are admissible for activation | Defined |
| 2 | Acquisition & archival — raw artefact to WORM storage with a stored `sha256`; re-retrieval never mutates a prior row | Defined |
| 3 | Parameter transcription — the table in §3.2 above | **Done (transcribed)** |
| 4 | Four-eyes verification — transcriber ≠ verifier; a Certified Tax Accountant or Labor Counsel must sign; signatures are cryptographic and append-only | **Not done** |
| 5 | Effective dating & versioning — `(year, revision)`, `YYYY.R`; status machine `DRAFT → UNDER_REVIEW → VERIFIED → ACTIVE → RETIRED`; a published set is immutable; corrections create a new revision | Defined |
| 6 | Change history & audit trail — a per-parameter diff record with legal citation, effective date, approver and the count of affected historical simulations | Defined |
| 7 | Activation criteria — eight mandatory conditions (A1–A8); the fail-closed loader rule | **Not met** |
| 8 | Regression against 1404 — ten structural invariants (R-01…R-10) plus the golden vectors | Defined |

### 3.5 The interim position

Until DEC-001 is resolved, the engine runs on the **verified 1404** set and every output carries `statutory_version: "1404.1"`, `rule_set_status: "VERIFIED"` and an explicit disclosure of the statutory year on the offer. Running 1404 figures under a 1405 label — which is what the published §5.1 example does — is the precise failure mode this plan exists to prevent.

### 3.6 The `1405.1-VERIFIED` defect

`REMEDIATED` §5.1 publishes `"statutory_version": "1405.1-VERIFIED"` for a calculation performed with 1404 parameters. The string conflates three independent facts — year, revision, verification state — and asserts a verification that did not occur. The corrected design separates them into `statutory_version`, `rule_set_status` and `is_verified`, and the API contract test asserts that the emitted status equals the value read from the database (`SPEC-STAT-001` §5.3, `P1-T19`).

---

## 4. Requirements Traceability

### 4.1 From finding to task

Every red-team finding is dispositioned, and each disposition names the task that delivers it. Findings that were explicitly excised or corrected by the red-team audit are listed for completeness; the actionable ones are traced below.

| Finding | Severity | Disposition | Delivered by |
| :--- | :--- | :--- | :--- |
| `FIND-TIME-01` | Critical | 1405 must be the active baseline; `1404` kept as a historical testbed | `P1-T02`, `P1-T03`, `SPEC-STAT-001` |
| `FIND-LEG-01` | Critical | Employer-initiated probation termination accrues the **full** probation period | `P1-T12` |
| `FIND-ARCH-02` | Critical | MinIO COMPLIANCE → Ceph/S3 GOVERNANCE | ADR-002, `P0-T11`, `P2-T03` |
| `FIND-LEG-02` | High | Art. 137 deduction becomes a configurable dual-policy toggle | `P1-T05`, DEC-002a |
| `FIND-LEG-03` | High | Overtime base excludes housing/grocery/child; 220 and 227.33 divisors | `P1-T10` |
| `FIND-LEG-04` | High | Eydi excess taxed progressively, not at a flat 10 % | `P1-T09` |
| `FIND-LEG-05` | High | *Mozd-e Saabet* includes continuous fixed attraction allowances | `P1-T07`, `P1-T08` |
| `FIND-LEG-06` | Medium | Art. 66 caps annual carryover at 9 days; Art. 71 pays **all** accumulated days at exit | `P1-T12` |
| `FIND-MATH-01` | Medium | Bisection replaced by an O(1) closed-form inverter | `P1-T13` |
| `FIND-MATH-02` | High | The 26-day leave reserve is removed from CTC | `P1-T11` |
| `FIND-MATH-03` | Low | Bühlmann-K credibility `K` clamped to [0.1, 100] | `P1-T17` |
| `FIND-ARCH-01` | High | Next.js → React + Vite SPA | ADR-001, `P3-T01` |
| `FIND-ARCH-03` | High | `pgcrypto` → ALEE + Vault | ADR-003, `P0-T06`, `P0-T08` |
| `FIND-ARCH-04` | High | `FORCE RLS` + per-transaction tenant context | `P0-T09`, `P0-T14` |
| `FIND-ARCH-05` | High | OCR latency budget revised to 3.5–6.0 s CPU / 1.2–1.8 s T4 | `P2-T05`, `SPEC-DOC-001` §4.2 |
| `FIND-ARCH-06` | Medium | pyHanko + local Iranian trust store + offline CRL cache | `P2-T09` |
| `FIND-ARCH-07` | High | Shahkar becomes an HR-assisted interactive OTP flow | `P2-T12` |
| `FIND-DATA-01` | High | `StatutoryRuleSetVersion`, `ForensicAuditArtifact`, `CandidateConsentRecord` entities added | `P0-T04`, `P2-T01`, `P2-T12` |
| `FIND-DATA-02` | High | Blind indexing for encrypted PII | ADR-003, `P0-T07` |
| `FIND-PROD-01` | High | MCDA salary review removed from Phase 1 | ADR-004 |
| `FIND-PROD-02` | Medium | *Tasviyeh Hesab* becomes a termination-liability simulator | ADR-004, `P1-T12` |
| `FIND-PROD-03` | High | Title discrepancy requires a structured commercial justification | `SPEC-DOC-001` §12, `P2-T14` |
| `FIND-INT-02` | Medium | Synchronous fast path separated from asynchronous job endpoints | `REMEDIATED` §5, ADR-005, `P2-T04` |

### 4.2 From module to gate

| Module | Delivered by | Verified by | Gate |
| :--- | :--- | :--- | :--- |
| 1 · Statutory wage & tax engine | `P1-T01`…`P1-T09` | L1 unit + L2 property + L3 golden | Phase 1 |
| 2 · Net-to-gross inverter | `P1-T13`, `P1-T14` | L2 `P-01`, L12 latency | Phase 1 |
| 3 · Document forensics | `P2-T05`…`P2-T11` | L8 accuracy | Phase 2 |
| 4 · 4-way disambiguation | `P2-T14`, `P2-T15` | L1 + L2 | Phase 2 |
| 5 · Pre-hire benchmarking | `P1-T17`, `P1-T18` | L1 statistical | Phase 1 |
| 6 · CTC & termination | `P1-T11`, `P1-T12` | L1 + property | Phase 1 |
| 7 · Provenance ledger | `P0-T10` | L7 `CR-10`, `CR-11` | Phase 0 |
| Frontend (Phase 3) | `P3-T01`…`P3-T14` | L9 + L10 | Phase 3 |

### 4.3 Unmapped requirements

No functional module is unmapped. The **non-functional** requirements that the corpus specifies but that no existing document operationalised — deployment, monitoring, backup, incident response, retention, RBAC, the Persian localisation strategy and the async execution strategy — are mapped in §12, §13, §10 and §8 respectively, each to a subordinate specification and a set of tasks.

---

## 5. Architecture and Technology Decisions

### 5.1 Accepted decisions (binding)

| ADR | Decision | Binding directive |
| :--- | :--- | :--- |
| **ADR-001** | React 18/19 + Vite + TypeScript + Tailwind + Shadcn SPA, not Next.js | Scaffold with `npm create vite`; TanStack Query v5 + Zustand; multi-stage Dockerfile (Node 20 → Nginx 1.25 Alpine) |
| **ADR-002** | Ceph RADOS GW (or a domestic managed S3) with Object Lock **GOVERNANCE**, 3650-day retention | `boto3`; standard accounts denied `s3:BypassGovernanceRetention`; that key isolated in an offline vault |
| **ADR-003** | Application-Level Envelope Encryption (AES-256-GCM) + HMAC-SHA256 blind indexing | `PiiFieldTransformer`; `BYTEA` ciphertext; `CHAR(64)` blind index; unique B-Tree index |
| **ADR-004** | Phase 1 is strictly pre-hire | Remove MCDA endpoints; label `/simulations/pre-hire-ctc` and `/simulations/termination-liability`; freeze the core entities |

### 5.2 Proposed decision (blocking Phase 2)

**ADR-005 — Asynchronous execution strategy** is drafted in `PROPOSED` state: a PostgreSQL-backed job queue with `FOR UPDATE SKIP LOCKED`, a dedicated worker process, explicit retry/backoff and idempotent handlers. Full comparative analysis against Celery+Redis and FastAPI `BackgroundTasks`: [`docs/adr/ADR-005-async-execution-strategy.md`](adr/ADR-005-async-execution-strategy.md).

### 5.3 Technology stack

| Layer | Technology | Status | Source |
| :--- | :--- | :--- | :--- |
| Frontend | React 18/19, Vite, TypeScript, Tailwind, Shadcn/Radix, TanStack Query v5, Zustand | Accepted | ADR-001 |
| Backend | Python 3.12, FastAPI 0.110+, Pydantic v2, SQLAlchemy 2.0, Alembic | Accepted | `REMEDIATED` §3.1 |
| Database | PostgreSQL 16, `FORCE RLS`, JSONB, `pgaudit` | Accepted | `REMEDIATED` §3.1, ADR-003 |
| Object storage | Ceph RADOS GW / domestic S3, `GOVERNANCE` Object Lock | Accepted | ADR-002 |
| KMS | HashiCorp Vault, with a local encrypted-config fallback | Accepted / proposed fallback | ADR-003, `SPEC-AUTH-001` §8.1 |
| Job queue | PostgreSQL-backed | **Proposed** | ADR-005 |
| OCR | PaddleOCR PP-Structure (Persian), self-hosted | Accepted | `REMEDIATED` §3.1 |
| Signature verification | pyHanko 0.25+ | Accepted | `REMEDIATED` §3.1 |
| Statistics | NumPy / SciPy | Accepted | `REMEDIATED` §3.1 |
| Proxy | Traefik 3 or Nginx 1.25, TLS 1.3 | Accepted | `REMEDIATED` §3 |
| Jalali | `persiantools` (+ `jdatetime` cross-check) | Proposed | `SPEC-FE-001` §10, DEC-006 |
| PDF | WeasyPrint preferred; ReportLab + `arabic_reshaper` + `python-bidi` fallback | Proposed | `SPEC-FE-001` §6, DEC-006 |
| Font | Vazirmatn, self-hosted, SIL OFL | Proposed | `SPEC-FE-001` §3.1 |

### 5.4 Explicitly rejected — and not reintroduced

`pgcrypto` for PII encryption · MinIO `COMPLIANCE` mode · the bisection net-to-gross solver · MCDA company-wide salary-review endpoints · direct *Sabt-e Ahval* integration · automated Shahkar verification · live job-board scraping · stateless-JWT-only session management without a revocation path · Redis as a mandatory on-site broker.

The full list with line-level provenance is in [`docs/DOCUMENTATION_INDEX.md`](DOCUMENTATION_INDEX.md) §5.

---

## 6. Domain Model, Database Schema and Migration Strategy

### 6.1 Entity inventory

| Entity | Origin | Phase 1 status |
| :--- | :--- | :--- |
| `ORGANIZATIONS` | `REMEDIATED` §4.1 | Extended (`P0-T05`) |
| `TENANT_KEY_STORES` | `REMEDIATED` §4.1 | Extended (`P0-T08`) |
| `CANDIDATES` | `REMEDIATED` §4.1 | Retained; carries the blind index (`P0-T12`) |
| `HOKM_SIMULATIONS` | `REMEDIATED` §4.1 | Retained |
| `AUDIT_LOGS` | `REMEDIATED` §4.1 | Corrected (`P0-T10`, `P0-T12`) |
| `STATUTORY_RULE_SET_VERSIONS` | `REMEDIATED` §4.1 | Extended (`P0-T04`) |
| `CANDIDATE_CONSENT_RECORDS` | `REMEDIATED` §4.1 | Retained (`P2-T12`) |
| `DOCUMENTS` | `REMEDIATED` §4.1 | Extended (`P2-T01`) |
| `FORENSIC_AUDIT_ARTIFACTS` | `REMEDIATED` §4.1 | Extended (`P2-T01`) |
| `EMPLOYEES` | `REMEDIATED` §4.1 | **Deferred to Phase 2** — DEC-005 |
| `USERS`, `ROLES`, `PERMISSIONS`, `ROLE_PERMISSIONS`, `ORGANIZATION_MEMBERSHIPS`, `SESSIONS` | **Missing** | Added (`P0-T05`) |
| `statutory_source_artefacts`, `statutory_parameter_signatures`, `statutory_rule_changes`, `statutory_verification_log` | **Missing** | Added (`P0-T04`) |
| `documents`, `forensic_audit_artifacts` | Research (§8.2) | Added (`P2-T01`) |
| `jobs` | ADR-005 | Added (`P2-T04`, proposed) |
| `access_log` | **Missing** | Added (`P0-T10`) |

### 6.2 Defects resolved

| # | Defect | Resolution | Task |
| :--: | :--- | :--- | :--: |
| 1 | `AUDIT_LOGS.prev_hash` / `current_hash` / `CANDIDATES.national_id_bindex` declared `char` with no length — PostgreSQL defaults `CHAR` to **1 character**; a SHA-256 hash needs 64 | `CHAR(64)` everywhere; a CI migration lint rejects a lengthless `CHAR`/`VARCHAR` | `P0-T12` |
| 2 | ADR-003's index directive targets `employees`; the ERD defines the blind index on `CANDIDATES` and gives `EMPLOYEES` no columns | The index moves to `candidates`; `EMPLOYEES` is deferred to Phase 2 (ADR-004) | `P0-T12`, DEC-005 |
| 3 | `AUDIT_LOGS.actor_id` has no referential target | `actor_id → users(id)`, plus `actor_type`, `on_behalf_of_organization_id` and a denormalised `actor_display_name` snapshot | `P0-T12`, `P0-T05` |
| 4 | No user/role/permission/membership entity | Six new entities with a segregation-of-duties role matrix | `P0-T05` |
| 5 | No `statutory_rule_set_versions` population procedure | The ingestion procedure in `SPEC-STAT-001` | `P0-T04`, `P1-T03` |

### 6.3 Schema standards

| Rule | Enforcement |
| :--- | :--- |
| Every tenant table: `tenant_id UUID NOT NULL REFERENCES organizations(id)` | Migration lint |
| Every tenant table: a policy + `ALTER TABLE … FORCE ROW LEVEL SECURITY` | Catalogue introspection test (`ISO-06`, `ISO-07`) |
| Every FK target: `UNIQUE (tenant_id, id)` | Migration lint |
| Money: `BIGINT` (Rial). Rates: `NUMERIC(20,6)`. Never `FLOAT`/`REAL`/`DOUBLE PRECISION` | Migration lint |
| Hashes: `CHAR(64)`. Ciphertext: `BYTEA` (nonce ‖ ciphertext ‖ tag) | Migration lint |
| JSON: `JSONB` with a GIN index where queried | Review |
| Timestamps: `TIMESTAMPTZ` everywhere; never a Jalali string in a date column | Migration lint |
| Audit ledger: append-only; triggers reject `UPDATE` and `DELETE` | `CR-11` |

### 6.4 Migration strategy

| Rule | Detail |
| :--- | :--- |
| Tool | Alembic (SQLAlchemy 2.0) |
| Review | Every migration reviewed; a destructive change requires a written justification |
| Zero-downtime | Expand → migrate → contract over three releases for hot-path tables |
| Irreversibility | A migration that cannot be reversed is marked `downgrade_requires_data_restore` and requires a restore procedure before it ships |
| Audit ledger | Never altered by a migration after activation |
| RLS | A new tenant table is created with `tenant_id`, its policy and `FORCE RLS` **in the same migration** |
| Verification | Each migration runs against a production-shaped snapshot in CI; the migration job is a release gate |
| Rollback | Rehearsed before every release (`DEPLOYMENT.md` §11.3) |

---

## 7. Backend Implementation Plan

### 7.1 Module layout

```
backend/app/
  main.py                 app factory, middleware stack, exception handlers
  core/
    config.py             pydantic-settings; the environment matrix
    logging.py            structured JSON logging + SecretRedactingFilter
    db.py                 async engine, session factory, pools (API / worker separate)
    tenancy.py            set_tenant_context(); fail-closed helpers
    security/             PiiFieldTransformer, blind index, key registry, session, rbac
    audit/                canonical JSON, hash chain, writer, verifier
    errors.py             the error catalogue
  engines/
    rules.py              rule set loader (versioned, fail-closed)
    money.py              Decimal primitives, rounding policy, residual handling
    tax.py  sso.py  severance.py  eydi.py  overtime.py  ctc.py  termination.py
    inverter.py           O(1) piecewise net-to-gross
    benchmark.py          Bühlmann-Kish shrinkage, percentile bands
  models/                 SQLAlchemy 2.0 models
  schemas/                Pydantic v2 request/response
  services/               domain services (the only place engines are composed)
  api/v1/                 routers
  workers/                the job worker process (ADR-005, proposed)
```

### 7.2 Rules

1. **Engines are pure.** No database, no network, no clock, no `random`. The clock is injected.
2. **Decimal only.** No `float` literal anywhere under `engines/` — enforced statically.
3. **Round once, at the line-item boundary.** A residual of ≤ 1 Rial per line is surfaced as `rounding_residual_rial`.
4. **Every output carries provenance**: `rule_version`, `rule_set_status`, `engine_version`, `calculation_hash`, `generated_at`, and a `provenance` map from field name → `{rule_id, rule_year, formula_ref}`.
5. **The engine reads the rule set; it never hard-codes a statutory value.**
6. **Fail closed.** An unverified or null rule set raises; it never coerces and never falls back silently.

### 7.3 API surface (Phase 1)

| Method | Path | Class |
| :--- | :--- | :--- |
| POST | `/api/v1/simulations/net-to-gross` | Fast path |
| POST | `/api/v1/simulations/gross-to-net` | Fast path |
| POST | `/api/v1/simulations/pre-hire-ctc` | Fast path |
| POST | `/api/v1/simulations/termination-liability` | Fast path |
| GET | `/api/v1/simulations/{id}` | Fast path |
| POST | `/api/v1/simulations/{id}/pdf` | Fast path → async render |
| POST | `/api/v1/documents/upload` | Async |
| GET | `/api/v1/documents/{id}/status` | Async |
| POST | `/api/v1/documents/{id}/verify` | Async |
| POST | `/api/v1/identity/shahkar/request-otp` | Fast path |
| POST | `/api/v1/identity/shahkar/verify-otp` | Fast path |
| GET | `/api/v1/documents/tasks/{job_id}` | Async |
| POST | `/api/v1/benchmarks/band` | Fast path |
| GET/POST | `/api/v1/statutory/rules`, `/api/v1/statutory/rules/{id}/propose` | Admin |

Full contracts: `REMEDIATED` §5. **The §5.1 worked example is defective and is corrected by `P1-T20`** — see §3.6 and `docs/EXECUTION_DOCUMENTATION_AUDIT.md` §3.

### 7.4 Backend sequencing

`P0-T01`→`P0-T02`→`P0-T06`→`P0-T07`→`P0-T08` → `P1-T04` → `P1-T05`/`P1-T06`/`P1-T07` → `P1-T08`/`P1-T09`/`P1-T10` → `P1-T11`/`P1-T12`/`P1-T13` → `P1-T14` → `P1-T19` → `P1-T21`

---

## 8. Frontend Implementation Plan and Persian Design System

Full specification: [`docs/specs/FRONTEND_PERSIAN.md`](specs/FRONTEND_PERSIAN.md). Summary of the plan:

| Workstream | Tasks | Key content |
| :--- | :--- | :--- |
| Scaffold and design system | `P3-T01`, `P3-T02` | Vite + React + TS + Tailwind + Shadcn; Vazirmatn self-hosted; logical properties only; the three-layer numeral policy; the icon-mirroring registry |
| Calendar and money | `P3-T03`, `P3-T04` | Jalali conversion library; Saturday-first picker; dual Gregorian/Jalali input; rule-year anchoring; Rial/Toman formatting with mandatory unit labels |
| Application | `P3-T05`, `P3-T06`, `P3-T07`, `P3-T08`, `P3-T09`, `P3-T10` | Typed API client; auth screens; the dual-scenario simulation form; the CTC and termination UI; the document forensics UI; benchmark visualisation |
| PDF | `P3-T11` | HTML→PDF; mandatory shaping stage; font embedding; deterministic rendering from the stored snapshot |
| Verification | `P3-T12`, `P3-T13`, `P3-T14` | Component + axe; Playwright with the < 3 s budget; bundle optimisation |

### 8.1 The eight localisation rules that are non-negotiable

1. `dir="rtl" lang="fa"` at the document root — once.
2. CSS logical properties only; a CI lint rejects the physical utilities.
3. Directional icons mirrored with `rtl:-scale-x-100`; assets are never swapped.
4. `<bdi>` isolation for Latin runs; bidi punctuation is never hand-swapped.
5. Numerals: Persian for display, ASCII-normalised on input, **ASCII in the machine layer** — a Persian-digit string is never hashed.
6. Rial is the canonical unit; the unit is always labelled; no decimals.
7. Gregorian UTC internally; Jalali only at the render boundary; the statutory year is anchored to the rule set, never to the clock.
8. PDF shaping (`arabic_reshaper` → `python-bidi`) and font embedding are mandatory and separately tested.

---

## 9. Document Intelligence and Employee Intelligence

Full specification: [`docs/specs/DOCUMENT_FORENSICS.md`](specs/DOCUMENT_FORENSICS.md).

| Area | Tasks | Note |
| :--- | :--- | :--- |
| Custody | `P2-T01`, `P2-T02`, `P2-T03` | Hash before transformation; WORM archival; idempotent duplicates |
| Execution | `P2-T04` | **Blocked on ADR-005** |
| OCR | `P2-T05`, `P2-T06` | PP-Structure, Persian; the 8 Tamin forensic fields; ZWNJ handling; ASCII normalisation |
| Forensics | `P2-T07`, `P2-T08`, `P2-T09` | PDF revision tree, font subsetting, producer metadata; ELA and clone detection; pyHanko with an offline CRL cache |
| Evidence | `P2-T10`, `P2-T11` | The verification-status model with weights; the cross-document consistency matrix |
| Identity | `P2-T12`, `P2-T13` | Interactive Shahkar only; the official issuer orchestrators |
| Intelligence | `P2-T14`, `P2-T15` | The 4-way disambiguation; the Art. 86 720-day gate; the three-layer orthogonal valuation; `V_score` |
| Verification | `P2-T16`, `P2-T17`, `P2-T18` | The 500-slip authentic corpus; the DF-01…DF-13 assertions; the Phase 2 gate |

**The corpus is the long pole.** `P2-T16` requires 500 authentic Social Security slips, consented and redacted. The corpus does not exist, and no synthetic substitute may satisfy the Phase 2 gate — a synthetic corpus does not exercise the failure modes (wrinkles, phone capture, scan artefacts) that the gate exists to measure.

---

## 10. Security, Privacy, Access Control and Data Governance

Full model: [`docs/specs/AUTH.md`](specs/AUTH.md). Operational procedures: [`docs/specs/DEPLOYMENT.md`](specs/DEPLOYMENT.md) §§5, 8–10.

### 10.1 Controls in force

| Control | Source | Task |
| :--- | :--- | :--: |
| AES-256-GCM application-layer encryption; keys never in the database | ADR-003 | `P0-T06` |
| Per-tenant DEK wrapped by a master KEK | ADR-003 | `P0-T08` |
| HMAC-SHA256 blind indexing with an isolated pepper | ADR-003 | `P0-T07` |
| `FORCE RLS` + per-transaction `SET LOCAL` tenant context | ADR-003, `FIND-ARCH-04` | `P0-T09` |
| Append-only, hash-chained audit ledger | `REMEDIATED` Module 7 | `P0-T10` |
| WORM object storage, `GOVERNANCE`, 3650 days, dual-key emergency override | ADR-002 | `P0-T11`, `P2-T03` |
| Interactive-only Shahkar with consent records | `FIND-ARCH-07` | `P2-T12` |
| Statutory rule versioning with four-eyes activation | `SPEC-STAT-001` | `P0-T04`, `P1-T02`, `P1-T03` |
| Retention: 180 days un-hired / 10 years hired / 10 years ledger | `RESEARCH_GAP` §8.5 | `P4-T04` |

### 10.2 Proposed controls awaiting approval

| Proposal | Register | Task |
| :--- | :--- | :--: |
| Server-side opaque sessions with rotation, in place of stateless JWT | DEC-004 | `P0-T18` |
| Mandatory MFA for privileged roles | DEC-004 | `P0-T18` |
| Two-person emergency access | DEC-004 | `P0-T18` |
| Separation of high-frequency access logging from the hash chain | DEC-004b | `P0-T10` |
| Entity corrections (§6.2) | DEC-005 | `P0-T12` |

### 10.3 Legal basis

Iranian Computer Crimes Law (Arts. 1, 16, 17) · E-Commerce Law (Art. 58) · Commercial Code Art. 19 (document evidentiary rules) · Supreme Court Precedent No. 272 · Diwan-e Edalat Precedents 1956 and 3328 · Labour Law Arts. 11, 24, 36 Note 3, 41, 51, 59, 62, 64, 66, 71, 86, 91 · Social Security Law Arts. 28, 39 · Direct Taxes Act Arts. 84, 91, 137 · 1370 Eydi Law.

---

## 11. Testing and Quality Assurance Strategy

Full strategy: [`docs/specs/TESTING.md`](specs/TESTING.md). Summary:

| Layer | Scope | Blocking |
| :--- | :--- | :--: |
| L1 Unit | The money core: tax, SSO, sanavat, Eydi, overtime, CTC, inverter, formatters | Yes |
| L2 Property | 15 Hypothesis invariants | Yes |
| L3 Golden | The certified vector corpus | Yes |
| L4 Integration | API + real PostgreSQL + real S3 | Yes |
| L5 Contract | OpenAPI 3.1 conformance; `rule_set_status` matches the database | Yes |
| L6 Isolation | RLS penetration (the Phase 0 gate) | Yes |
| L7 Cryptography | ALEE, blind index, rotation, chain integrity | Yes |
| L8 Documents | OCR accuracy, forensics detectors (the Phase 2 gate) | Yes / accuracy |
| L9 Frontend | Vitest + Testing Library + axe | Yes |
| L10 E2E | Playwright (the Phase 3 gate) | Yes |
| L11 Security | SAST, dependency audit, secret scan, container scan | Yes |
| L12 Performance | The latency budgets | At release |
| L13 Regression | Cross-year differential | Yes |

### 11.1 The invariants that make a result trustworthy

1. `Gross − Σ(deductions) == Net` exactly, in integer Rial.
2. `Σ(line items) − total == rounding_residual_rial`, with `|residual| ≤ 1` per line, signed and surfaced.
3. The employer-cost identity holds exactly.
4. `net_to_gross(gross_to_net(G)) == G` within 1 Rial.
5. Every emitted figure is an integer; no `float` ever reaches the boundary.
6. `rule_set_status` in the response equals the value read from the database.

Invariant (2) is what would have caught the defective §5.1 example, whose severance accrual used the wrong base and whose total silently absorbed the difference.

### 11.2 The corpus gap

The golden vector corpus **does not exist**. `P1-T15` is the longest-lead external item in the project, because the Phase 1 gate is defined in terms of it. It must start in **Week 1**, not Week 5.

---

## 12. Deployment, Infrastructure and CI/CD

Full specification: [`docs/specs/DEPLOYMENT.md`](specs/DEPLOYMENT.md).

### 12.1 Topology

```
Traefik/Nginx (TLS 1.3, static SPA, rate limiting)
        │
FastAPI (uvicorn, N replicas) ── PostgreSQL 16 (FORCE RLS, hash-chained ledger, job queue)
        │                                          │
        └──────────── worker pool ──────────────►  └── Ceph/S3 (GOVERNANCE, 3650 days)
```

Four mandatory components: PostgreSQL, object storage, the application runtime, the reverse proxy. **No cloud-managed service is assumed.** No Redis, no Kubernetes, no Node.js runtime.

### 12.2 Environment matrix

Three environments — local (Windows + containers), staging (production-shaped) and pilot. The matrix in `DEPLOYMENT.md` §5.1 lists every variable with its value per environment and its secret classification. Secrets are never in the repository, an image layer or a compose file.

### 12.3 Windows development

`uv` + Python 3.12, `pnpm` + Node 20, Docker Desktop on WSL 2. The Linux containers are the production artefacts; the Windows path is a developer convenience. Windows-specific hazards (path lengths, antivirus file locking, UTF-8 filenames, line endings) are enumerated in `DEPLOYMENT.md` §2.6.

### 12.4 CI stages

Thirteen stages (`TESTING.md` §15). Stages 0–8 gate every pull request; 9–10 run nightly and must be green for 7 consecutive nights before a release; 11–12 gate the release. A migration dry-run and a rollback rehearsal are release gates.

### 12.5 Air-gapped deployment

The full mirroring, verification and no-outbound-connection checklist is `DEPLOYMENT.md` §12. Air-gapped operation is an explicit pilot acceptance item, not an aspiration.

---

## 13. Monitoring, Operations and Maintenance

Full procedures: [`docs/specs/DEPLOYMENT.md`](specs/DEPLOYMENT.md) §§7–10.

### 13.1 Observability

Three health endpoints (liveness, readiness, authenticated detail), a Prometheus metrics surface, structured JSON logging with mandatory redaction, and a correlation ID on every request, log line, audit event and job record.

**The metric that matters most is `job_oldest_queued_age_seconds`** — it is the stall detector, and it does not exist without a job queue (hence ADR-005).

### 13.2 Alerting

Eleven alert rules with severity and response (`DEPLOYMENT.md` §7.4). Two are Critical: **audit-chain verification failure** and **plaintext PII detected in logs or the ledger**. A non-zero `audit_chain_verification_failures_total` is a SEV-1 incident.

### 13.3 Operations

| Cadence | Activity |
| :--- | :--- |
| Daily | Backup verified; chain verified; dead-letter queue reviewed; oldest queued job age |
| Weekly | Error and latency review; failed-job review; rule-set status confirmed unchanged |
| Monthly | Security patches; access-log anomaly review; certificate check; privileged-role review |
| Quarterly | Restore drill; access review; planned master-KEK rotation |
| Annually | Penetration test; legal compliance review; rule-set re-verification for the new year |

### 13.4 Incident response

Four severity levels with response and escalation targets, plus a dedicated SEV-1 runbook for a suspected audit-chain or PII incident — **contain without redeploying, preserve, verify, assess, notify, remediate by append-only correction, report**.

### 13.5 Retention and lifecycle

180 days for un-hired candidate simulation data (via **cryptographic erasure** — destroying the per-candidate DEK, so the ciphertext is unrecoverable without rewriting history or defeating WORM) · 10 years for hired dossiers, the ledger and forensic objects · rule sets and golden corpora retained indefinitely, superseded rather than edited.

---

## 14. Milestones, Work Breakdown Structure and Release Gates

### 14.1 The approved roadmap — preserved unchanged

| Phase | Weeks | Theme | Acceptance gate (verbatim) |
| :-- | :--: | :--- | :--- |
| **Phase 0** | 1–4 | Security and Relational Foundation | 100% automated test pass on multi-tenant RLS penetration suite; zero plaintext PII in database |
| **Phase 1** | 5–8 | Deterministic Engine and Inverters | 10,000-case automated test suite matching certified tax accountant test vectors with < 1 Rial deviation |
| **Phase 2** | 9–14 | Document Forensics and Identity | Successful parsing of 500 authentic Social Security slips with > 95% field extraction accuracy |
| **Phase 3** | 15–18 | Pre-Hire Simulation and React SPA | Full end-to-end simulation completed in < 3 seconds via browser UI |
| **Phase 4** | 19–20 | Pilot Hardening and Compliance Sign-Off | External security penetration testing (OWASP Top 10 + multi-tenant isolation); external legal review sign-off by Iranian labor attorneys |

**No phase was re-scoped, re-sequenced or re-timed by this plan.** The historical 7-day and 30-day schedules were rejected. Where a phase is at risk, it is recorded in §14.6 as a proposed change requiring approval — not applied silently.

### 14.2 Task status vocabulary

`NOT_STARTED` · `IN_PROGRESS` · `BLOCKED` · `READY_FOR_REVIEW` · `APPROVED` · `COMPLETED`

**Task statuses reflect actual implementation evidence.** Application source code exists for the ADR-008 statutory payroll engine, the ADR-009 valuation service, and the ADR-010 manager workspace prototype; 29 tasks have implementation evidence and 7,400+ test lines exist. Writing a specification does not advance a task, but neither does a specification negate implemented work.

### 14.3 Work breakdown structure

Column legend — **T** title · **R** responsible role · **D** dependencies · **E** estimated effort (engineer-days) · **Del** deliverable · **AC** acceptance criteria · **V** verification method · **B** blocking issues · **S** status.

---

#### Phase 0 — Security and Relational Foundation (Weeks 1–4)

| ID | T | R | D | E | Del | AC | V | B | S |
| :-- | :-- | :-- | :-- | :-: | :-- | :-- | :-- | :-- | :-: |
| P0-T01 | Repository and tooling baseline | Lead Backend Eng | — | 2d | `pyproject.toml`, `uv.lock`, ruff/mypy config, `.gitattributes`, `.env.example` | `uv sync --frozen` succeeds; ruff and `mypy --strict` clean; CI runs both | CI self-test on the bootstrap commit | DEC-005 (lint rule - resolved by SPEC-QA-001 3.1: the AST gate is authoritative, owned by P1-T04/P0-T15); DEC-F (CI provider) | IN_PROGRESS |
| P0-T02 | FastAPI skeleton and configuration | Lead Backend Eng | P0-T01 | 2d | `app/main.py`, `core/config.py`, `core/logging.py` | App boots; `/health/live` returns 200; no secret in any log line | Unit test + log inspection | — | COMPLETED |
| P0-T03 | PostgreSQL 16 provisioning and hardening | Codex /root (sole accountable implementation owner) | P0-T01 | 3d | Init SQL, PostgreSQL config/HBA, dev Compose, private material prep, runtime assertion script | `log_statement ≠ 'all'`; TLS on; `pgaudit` present; extension policy documented | Official pull/build, healthy local server and real TLS/SCRAM/settings/pgAudit/privacy verifier PASS; previous independent static review retained | Image blocker cleared; local AC verified. P0-T01 CI clause remains; see BOOTSTRAP_CHANGELOG §15. No phase gate passed | READY_FOR_REVIEW |
| P0-T04 | Alembic baseline and the statutory rule-set tables | Codex /root (sole implementation owner) | P0-T01, P0-T03 | 3d | Adopted Alembic baseline, five typed statutory tables, global FORCE-RLS policies, restricted reader projection, identity write gate and storage lint | Isolated upgrade/downgrade/re-upgrade and non-superuser access/write-gate assertions PASS | 48 integration tests (self-skip without Docker; 48 pass when available) plus unit/API regression; independent read-only security review PASS; BOOTSTRAP_CHANGELOG §21 | DEC-012 resolved by owner T-2/F-1 (ADR-007); CI migration job/P0-T01 CI still pending; P0-T05 owns validated users FKs with ON DELETE RESTRICT before gate removal | READY_FOR_REVIEW |
| P0-T05 | Tenant identity schema | Database Eng + Security Eng | P0-T04 | 4d | `organizations`, `users`, `roles`, `permissions`, `role_permissions`, `organization_memberships`, `sessions` + role seed | All entities present with the specified constraints; exactly 7 roles seeded; `UNIQUE (tenant_id, id)` on every tenant table | Catalogue introspection test; validate statutory actor FKs before removing identity write gate | ADR-006/ADR-007 resolved choices; P0-T05 owns users FKs with ON DELETE RESTRICT and account deactivation | READY_FOR_REVIEW |
| P0-T06 | ALEE encryption module | Codex /root (sole accountable implementation owner) | P0-T01 | 4d | `PiiFieldTransformer`, AES-256-GCM, 96-bit random IV, key registry interface | Round-trip on every field type; identical plaintext → different ciphertext; tampering raises; no key in a log | CR-01…CR-03 + logging; independent static review PASS; CR-04 blind index remains P0-T07 | Local primitive verified; P0-T01 CI clause and production registry/integration evidence remain; see AUTH §8.5 and BOOTSTRAP_CHANGELOG §11 | READY_FOR_REVIEW |
| P0-T07 | HMAC-SHA256 blind-index module | Security Eng | P0-T06, P0-T08 | 2d | Blind-index service, isolated pepper, per-tenant salt, normalisation | Deterministic within a tenant; differs across tenants; the pepper is absent from the DB; B-Tree lookup < 1 ms | CR-04…CR-07: determinism, tenant/field separation, spelling folding, leading zeros, fixed error messages and fail-closed pepper PASS (45 tests); DB-level CR-05 and the < 1 ms B-Tree are NOT RUN (no Docker) | P0-T08 remains NOT_STARTED and owns pepper custody/rotation, so no Vault or local-KEK path exists; the normalisation rule is published in AUTH §8.6; BOOTSTRAP_CHANGELOG §25 | READY_FOR_REVIEW |
| P0-T08 | Key management: Vault adapter and local KEK | Security Eng + DevOps Lead | P0-T01 | 4d | Vault client, local encrypted master config, Argon2id KEK derivation, DEK wrap/unwrap, rotation | Both paths work; the local path is exercised in dev; DEK rotation re-encrypts a tenant losslessly | CR-08, CR-09 | DEC-004 | NOT_STARTED |
| P0-T09 | RLS policies and the tenant-context helper | Database Eng + Security Eng | P0-T04, P0-T05 | 4d | Policies on every tenant table, `FORCE RLS`, `set_tenant_context()`, fail-closed helpers | No tenant table without a policy and `FORCE RLS`; no context → zero rows **and** an exception | ISO-03, ISO-06, ISO-07 | DEC-005 resolved by ADR-006. Revision `0003` installs `set_tenant_context()` (transaction-local `app.tenant_id`) and `current_tenant_id()` (raises `55000` when unbound) plus `pish_tenant_rls_violation()`, the catalogue assertion behind the AC; verified over a real PostgreSQL 16 upgrade→base→head round-trip (42 integration tests PASS). No tenant data table exists yet, so no policy is attached; P0-T14 owns the penetration suite and P0-T18 the runtime role. BOOTSTRAP_CHANGELOG §30 | IN_PROGRESS |
| P0-T10 | Append-only hash-chained audit ledger | Backend Eng + Database Eng | P0-T04, P0-T06 | 4d | `audit_logs`, `access_log`, canonical JSON, chain writer and verifier, rejecting triggers | The chain verifies end-to-end; `UPDATE`/`DELETE` are rejected; every mutation is chainable | CR-10, CR-11 | DEC-004b | NOT_STARTED |
| P0-T11 | Object-storage adapter (S3 / GOVERNANCE) | Codex /root (adoption and hardening owner) | P0-T01 | 3d | `boto3` client, bucket + Object Lock config, tenant-prefixed keys | Upload under `GOVERNANCE` succeeds; the standard credential cannot delete; `s3:BypassGovernanceRetention` is absent from the runtime credential | Local unit suite and independent review PASS; live RGW integration NOT RUN | P0-T01 CI incomplete; no local RGW/credential-policy acceptance. Adapter source adopted and malformed-key error fixed; BOOTSTRAP_CHANGELOG §19 | READY_FOR_REVIEW |
| P0-T12 | ERD defect correction | Database Eng | P0-T04 | 1d | A migration fixing the hash column lengths, the `candidates`/`employees` naming and the `actor_id` FK | Every hash column is `CHAR(64)`; the blind index is on `candidates`; `actor_id → users(id)` | Introspection test + the DEC-005 approval record | DEC-005 | NOT_STARTED |
| P0-T13 | Reference-data seed | Data Analyst | P0-T04 | 4d | Iranian cities, the 60-occupation MVP taxonomy, versioned seed commands | Seeds are idempotent and versioned; no seed mutates an existing row in place | Seed idempotency test | DEC-007 | NOT_STARTED |
| P0-T14 | RLS penetration test suite | QA Eng + Security Eng | P0-T05, P0-T09 | 5d | ISO-01…ISO-12, tenant-escape and privilege-escalation suites | 100 % of the suite passes against real PostgreSQL with policies active | CI stage 5 | — | NOT_STARTED |
| P0-T15 | Encryption and blind-index test suite | QA Eng | P0-T06, P0-T07, P0-T08 | 3d | CR-01…CR-13 plus the zero-plaintext-PII scan | All pass; the PII scan finds nothing | CI stage 5 | — | NOT_STARTED |
| P0-T16 | Backup and restore baseline | Database Eng + DevOps Lead | P0-T03, P0-T04 | 3d | `pg_basebackup` + WAL archiving, retention config, a restore script | A backup completes and restores to a schema-identical isolated instance | Restore dry run | — | IN_PROGRESS |
| P0-T17 | Deployment skeleton | DevOps Lead | P0-T02, P0-T03, P0-T11 | 4d | Backend/worker/frontend Dockerfiles, compose dev+prod, `nginx.conf`, environment matrix | The stack comes up on a clean host; the SPA is served; `/health/ready` answers | Boot smoke test in CI | DEC-010 | NOT_STARTED |
| P0-T18 | Authentication and session implementation | Backend Eng + Security Eng | P0-T05, P0-T06, P0-T08 | 8d | Login/logout/session endpoints, Argon2id, TOTP, rate limiting, CSRF, RBAC middleware | AU-01…AU-05, AU-08…AU-10 pass | Integration suite | DEC-004 | NOT_STARTED |
| P0-T19 | CI pipeline for the Phase 0 gates | DevOps Lead | P0-T01, P0-T03, P0-T14, P0-T15 | 4d | CI stages 0–8, a containerised test DB, the migration lint, secret scanning | A push runs stages 0–5; the RLS and crypto suites gate the merge | CI self-test | — | NOT_STARTED |
| P0-T20 | **Phase 0 gate review** | CTO + QA Lead + Security Architect | P0-T14, P0-T15, P0-T16, P0-T17, P0-T18, P0-T19 | 2d | Gate evidence pack, sign-off record | Both Phase 0 criteria demonstrably met with archived evidence | Gate review + evidence archive | DEC-004, DEC-005 | NOT_STARTED |

---

#### Phase 1 — Deterministic Engine and Inverters (Weeks 5–8)

| ID | T | R | D | E | Del | AC | V | B | S |
| :-- | :-- | :-- | :-- | :-: | :-- | :-- | :-- | :-- | :-: |
| P1-T01 | Statutory rule-set loader (versioned, fail-closed) | Backend Eng | P0-T04 | 4d | `rules.py` loader, month-length variants, invariants R-01…R-10 | Loading the 1405 placeholder raises `StatutoryParameterUnavailable`; 1404 loads; every invariant holds | Unit + integration tests — 1404 loads; 1405 refuses with `StatutoryParameterUnavailable`; invariants R-01…R-10 hold, with R-01 now compared against the seed's independent 30-day ceiling; R-11's overtime divisor loads; the canonical-parameter SHA-256 fingerprint is published; a cached-rule-set mutation regression test passes (BOOTSTRAP_CHANGELOG §23, §24)| DEC-001 does not gate the 1404-only v1 path (ADR-008); 1405 activation remains gated | READY_FOR_REVIEW |
| P1-T02 | **1405 four-eyes verification against the primary PDFs** | Payroll Eng + Certified Tax Accountant + Legal Counsel | — (external, long lead) | 6d | Signed parameter verification log; archived artefacts; Codex /root implemented bounded acquisition preparation only | Every 1405 parameter carries ≥ 2 signatures, one by a Certified Tax Accountant or Labor Counsel, bound to an artefact `sha256` | Verification-log review; acquisition slice tested/reviewed, BOOTSTRAP_CHANGELOG §16 | **BLOCKED** — six official discovery probes failed (403/transport); WORM/DB integration, human signatures and O1–O5 remain. Collector does not prove latest-law coverage | **BLOCKED** |
| P1-T03 | 1405 activation and 1404 regression | Backend Eng + Database Eng | P1-T01, P1-T02 | 3d | A new `statutory_rule_set_versions` row with status `ACTIVE`; the 1404 differential report | 1405 is `ACTIVE` and `VERIFIED`; every changed line in the 1404 differential is attributable to a named parameter delta | Regression suite L13 | DEC-001 | NOT_STARTED |
| P1-T04 | Decimal money primitives and the rounding policy | Codex /root (adoption and hardening owner) | P0-T01 | 3d | `money.py`, `prec=34`, `ROUND_HALF_UP`, residual reconciliation, largest-remainder allocation | No `float` literal under `engines/`; the residual is ≤ 1 Rial per line and is surfaced | Existing AST gate, regression/property tests and independent review PASS; §24 replaces the former tautological residual with `sum(rounded deduction lines) − round(exact total)` and covers it with a non-tautology regression test | P0-T01 CI incomplete; no complete engine/golden-corpus acceptance. BOOTSTRAP_CHANGELOG §19 | READY_FOR_REVIEW |
| P1-T05 | Tax engine | Backend Eng | P1-T01, P1-T04 | 5d | Progressive slabs, exemption, the Art. 137 dual policy, the welfare-treatment toggle | Every slab boundary exact to 1 Rial; both postures and both welfare treatments produce the expected base; P-07 and P-08 hold | Unit + property tests — Slab boundaries exact to 1 Rial; the Appendix A vectors (3,792,061 / 17,647,059) reproduce; both postures and both welfare treatments verified (§23); §24 makes the published tax total equal the sum of its rounded slab lines and publishes the exact total plus signed residual per posture| DEC-002a RESOLVED — ADR-008 (posture-dependent; `conservative_inta` primary) | READY_FOR_REVIEW |
| P1-T06 | SSO engine | Backend Eng | P1-T01, P1-T04 | 3d | Rates, the ceiling per month length, capped and uncapped paths | The ceiling applies exactly at the boundary; 29/30/31-day variants correct; P-04 holds | Unit + property tests — The ceiling applies exactly at the boundary; the 29/30/31 variants verified; P-04 holds (§23)| — | READY_FOR_REVIEW |
| P1-T07 | *Mozd-e Saabet* / *Mozd-e Mabna* decomposition | Backend Eng + Payroll Eng | P1-T01 | 3d | The base definitions: welfare excluded, continuous attraction included | `Mozd-e Saabet = gross − housing − grocery − marriage − child`; the continuous attraction is retained | Unit tests — Welfare excluded, continuous attraction retained; the Appendix A base reproduces (§23)| — | READY_FOR_REVIEW |
| P1-T08 | Sanavat engine | Backend Eng | P1-T04, P1-T07 | 2d | The 1/12 monthly accrual on *Mozd-e Saabet* | Accrual = `Mozd-e Saabet / 12` ± 1 Rial; P-05 holds | Unit + property tests — Accrual = Mozd-e Saabet ÷ 12 ± 1 Rial; P-05 holds (§23)| — | READY_FOR_REVIEW |
| P1-T09 | Eydi engine | Backend Eng | P1-T05, P1-T07 | 3d | The 60-day floor, the 90-day-of-min-wage cap, progressive taxation of the excess | Below floor / at floor / between floor and cap / at cap / above cap all correct; P-06 holds | Unit + property tests — Floor, cap and progressive excess verified; the flat seed rate is never consumed; P-06 holds (§23); §24 renames the at-cap test to its actual meaning, covers the true-above-cap case and uses Decimal half-up division for the monthly accrual| DEC-002a RESOLVED — ADR-008; the seed's flat `eydi_tax_excess_rate` is never consumed (HB-GAP-005) | READY_FOR_REVIEW |
| P1-T10 | Overtime engine | Backend Eng | P1-T07 | 3d | The 220 / 227.33 divisors, welfare excluded from numerator **and** divisor, 1.40 / 1.35 multipliers | Both divisors correct; welfare excluded from both bases; no 176-hour divisor anywhere in the engine | Unit tests — The 220 / 227.33 / 212.67 divisors verified; the welfare is excluded from both bases; no 176-hour divisor (§23)| — | READY_FOR_REVIEW |
| P1-T11 | CTC engine | Backend Eng | P1-T06, P1-T08, P1-T09 | 4d | Annual and monthly CTC; no 26-day leave double count; carryover capped at 9 days | No 26-day reserve appears; the carryover is ≤ 9 days; the employer-cost identity holds exactly | Unit + property tests — The employer-cost identity holds exactly; no 26-day reserve; the Appendix A corrected total reproduces (§23)| — | READY_FOR_REVIEW |
| P1-T12 | Termination-liability simulator | Backend Eng | P1-T08, P1-T11 | 4d | Art. 11 full-probation liability on employer termination; the Art. 66/71 leave buyout | Employer termination on day 15 of a 90-day probation yields the full 3 months; the exit buyout uses total accumulated days ≤ 9 × years | Unit tests + Gherkin — Employer termination on day 15 of a 90-day probation yields the full 3 months; the buyout uses the total accumulated days ≤ 9 × years (§23); §24 adds the explicit scenario model (exactly one probation line + separation = total) and the statutory 30-day leave-buyout divisor| — | READY_FOR_REVIEW |
| P1-T13 | Net-to-Gross closed-form inverter | Backend Eng | P1-T05, P1-T06 | 5d | The O(1) piecewise solver with region detection and boundary verification; a Newton-Raphson fallback | The solved gross reproduces the target net within 1 Rial in every region; the boundary check is enforced; p99 < 5 ms | Property tests + performance suite | **Out of product scope — ADR-008 (owner, 2026-11-15)**; deferred pending a superseding ADR | NOT_STARTED |
| P1-T14 | Gross-to-Net forward calculator | Backend Eng | P1-T05, P1-T06 | 2d | The forward calculation on the same tax model | Forward and inverse agree within 1 Rial (P-01) | Property tests — The forward calculation, the net identity, the dual posture and the calculation hash are covered by unit and property tests (§23); §24 reconciles the published tax total to its slab lines and publishes the exact total/residual per posture| — | READY_FOR_REVIEW |
| P1-T15 | **Golden vector corpus** | Certified Tax Accountant + Payroll Eng | — (external, long lead) | 10d | ≥ 10,000 signed cases for the active rule year | The CI golden gate reports 0 Rial deviation against a corpus signed by a Certified Tax Accountant | CI stage 3 | **BLOCKED** — no accountant engaged; the corpus does not exist; **out of product scope — ADR-008** | **BLOCKED** |
| P1-T16 | Property-based test suite | QA Eng | P1-T04, P1-T05, P1-T13 | 4d | Hypothesis strategies; P-01…P-15 | Every property passes over the full example budget in the nightly run | CI stages 2 and 9 — The engine properties P-02…P-08 and P-10 pass over 200 examples each; the inverter-dependent P-01 follows P1-T13, out of scope (§23); §24 moves P-05 to Decimal half-up arithmetic| Engine properties remain in scope; inverter-dependent properties (P-01) follow `P1-T13` out of scope (ADR-008) | READY_FOR_REVIEW |
| P1-T17 | Bühlmann-Kish shrinkage and percentile bands | Actuarial Analyst + Backend Eng | P1-T01 | 4d | Credibility `Z`, clamped `K`, the P10–P90 bands | `K` is clamped to [0.1, 100]; the band widens as the sample shrinks; unverified claims never inflate P50 | Unit + statistical tests | **Out of product scope — ADR-008**; DEC-007 REJECTED out of scope | NOT_STARTED |
| P1-T18 | Benchmark data pipeline | Data Analyst + Backend Eng | P0-T13, P1-T17 | 5d | The curated offline seed loader; the IQR/MAD outlier filter; Rial/Toman normalisation; the statutory-floor filter | Only licensed offline sources load; the legal floor is enforced; outliers are rejected by the documented rule | Unit + dataset-validation test | **Out of product scope — ADR-008**; DEC-007 REJECTED out of scope | NOT_STARTED |
| P1-T19 | Simulation API | Backend Eng | P1-T11, P1-T12, P1-T13, P1-T14, P1-T18 | 5d | `/simulations/net-to-gross`, `gross-to-net`, `pre-hire-ctc`, `termination-liability`; the dual-scenario response; the provenance map | Every response carries `rule_version`, `rule_set_status`, `engine_version`, `calculation_hash`, `generated_at`; the contract suite passes | Schemathesis + contract suite — The endpoint returns the five provenance fields, both postures, per-field provenance, the rule-set fingerprint and a reconciled signed residual (`sum(rounded deduction lines) − round(exact total)`, not the former total − net identity); every refusal uses one typed envelope; the contract suite now collects and passes, with PostgreSQL-backed cases skipping without Docker; a live request and a live 1405 refusal were observed (§23, §24)| ADR-008 v1 scope: a single minimal endpoint on 1404.1 only (CTC and termination inside the response); DEC-001 does not gate the 1404-only path | READY_FOR_REVIEW |
| P1-T20 | **Correct the §5.1 worked example and the API documentation** | Documentation Eng + Payroll Eng | P1-T02, P1-T19 | 2d | A recomputed example with every intermediate value; the defect analysis; the amended spec section | The published example reproduces from the engine within 0 Rial; the defect analysis is recorded; no response is labelled with a verification state the loader did not read | Golden case + documentation review | **Out of product scope — ADR-008**; DEC-001/DEC-002 remain open for any future revival | NOT_STARTED |
| P1-T21 | Performance benchmark suite | QA Eng | P1-T13, P1-T19 | 2d | k6/Locust scripts; the latency budgets | Inversion p99 < 5 ms; fast-path p99 < 20 ms | CI stage 11 | **Out of product scope — ADR-008** (depends on the deferred inverter) | NOT_STARTED |
| P1-T22 | **Phase 1 gate review** | CTO + QA Lead + Certified Tax Accountant | P1-T03, P1-T15, P1-T20, P1-T21 | 2d | Gate evidence pack; sign-off | The 10,000-case suite matches the certified vectors with < 1 Rial deviation; the active rule set is `VERIFIED` and `ACTIVE` | Gate review + evidence archive | **Out of product scope — ADR-008**; depends on blocked/deferred external items | NOT_STARTED |

---

#### Phase 5 — Compensation advisory module (ADR-009, owner 2026-11-16)

> **Scope note (ADR-009):** this phase is **added beside** the ADR-008 engine; it removes no engine capability and changes no statutory rule, seed or hash. The manager supplies the monthly gross band; the module scores a documented profile, places it in that band and costs the range through the existing engine. It is advisory (`statutory: false`), never a market claim and never tax advice. Estimated effort: 4d total for both rows.

| ID | T | R | D | E | Del | AC | V | B | S |
| :-- | :-- | :-- | :-- | :-: | :-- | :-- | :-- | :-- | :-: |
| P5-T01 | Advisory valuation model (`valuation-v1`) | Backend Eng | P1-T04, P1-T07 | 2d | `app/engines/valuation.py`: weighted score, published weights, band placement, published range, typed refusals | Score deterministic and bounded 0–100; no band ⇒ `VALUATION_BAND_REQUIRED`; `relevant > total` refused; range clamped to the band; no float literal | 44 unit tests (`tests/unit/test_valuation_engine.py`) PASS; AST money gate | No market data exists (DEC-007/DEC-008 rejected), so the band is manager-supplied only | READY_FOR_REVIEW |
| P5-T02 | Compensation proposal endpoint and composition | Backend Eng | P5-T01, P1-T19 | 2d | `POST /api/v1/valuations/compensation-proposal`; `services/valuation_service.py`; response contract with advisory flags, weights, and three statutory costings | Every emitted figure carries the provenance envelope; the point costing is byte-identical to the simulation endpoint's; refusals keep the single error shape; 1405 fails closed | 21 API tests (`tests/api/test_valuation_api.py`) including a replay against `gross-to-net`; `ruff` and `mypy --strict` PASS; BOOTSTRAP_CHANGELOG §27 | Authentication (`P0-T18`) still absent: the endpoint is a trusted-operator surface only. Persistence of proposals is out of scope | READY_FOR_REVIEW |

---

#### Phase 2 — Document Forensics and Identity (Weeks 9–14)

> **Scope note (ADR-008, owner 2026-11-15):** the document-forensics module (M3) is **out of product scope**; the rows below are retained unchanged for the audit trail. Any revival requires a superseding ADR.

| ID | T | R | D | E | Del | AC | V | B | S |
| :-- | :-- | :-- | :-- | :-: | :-- | :-- | :-- | :-- | :-: |
| P2-T01 | Document taxonomy and storage model | Database Eng | P0-T04 | 3d | `documents`, `forensic_audit_artifacts` with their unique constraints | `UNIQUE (tenant_id, file_sha256)` and `UNIQUE (document_id, analysis_version)` exist | Introspection test | — | NOT_STARTED |
| P2-T02 | Upload endpoint, MIME magic validation, SHA-256 | Backend Eng | P0-T11, P2-T01 | 4d | `POST /api/v1/documents/upload`; magic-byte sniffing; the size limit; hashing before transformation | A renamed executable is rejected; the hash is of the bytes as received; a duplicate returns the existing document | Integration suite | — | NOT_STARTED |
| P2-T03 | Ceph/S3 `GOVERNANCE` integration | Backend Eng | P0-T11, P2-T02 | 3d | WORM archival under tenant-prefixed keys; version IDs; the retention configuration | Objects lock in `GOVERNANCE` for 3650 days; the standard credential cannot delete | Integration test against the local RGW | — | NOT_STARTED |
| P2-T04 | **Async execution strategy and the job pipeline** | Backend Eng + DevOps Lead | ADR-005 approval | 8d | The `JobQueue` interface, the `jobs` table, `SKIP LOCKED` claiming, the heartbeat, the reaper, the retry/backoff policy, the worker process, idempotent handlers | A job survives a worker restart; an expired lease is reaped; a retry never duplicates an artifact; the fast path never touches the `jobs` table | Integration + chaos test | **BLOCKED** — ADR-005 is `PROPOSED`, not `Accepted` | **BLOCKED** |
| P2-T05 | PaddleOCR PP-Structure Persian pipeline | Document Forensics Eng | P2-T04 | 8d | Model provisioning (weights in the image), layout and table extraction, ZWNJ-aware normalisation, confidence scoring | The worker loads its model from the local filesystem; no outbound connection is made | Container test + air-gapped check | DEC-003 | NOT_STARTED |
| P2-T06 | Per-category field extraction and validation | Document Forensics Eng | P2-T05 | 6d | Extractors for the 12 categories; the 8 Tamin forensic fields; modulo-11 validation; ASCII numeral normalisation | An invalid National Code is rejected before storage; digits are ASCII in the machine layer | Unit + corpus test | — | NOT_STARTED |
| P2-T07 | PDF structural forensics | Document Forensics Eng | P2-T01 | 4d | The `pikepdf` revision-tree walk, font-subset consistency, producer metadata, timestamp checks | A known-tampered PDF raises the expected flags; a clean PDF raises none | Forensics unit tests | — | NOT_STARTED |
| P2-T08 | ELA and copy-move image forensics | Document Forensics Eng | P2-T01 | 4d | The ELA difference map; ORB/SIFT clone detection; score normalisation | ELA on a pasted region scores higher than on an untouched region | Forensics unit tests | — | NOT_STARTED |
| P2-T09 | pyHanko signature verification and the Iranian trust store | Document Forensics Eng + Security Eng | P2-T01 | 6d | The local Root CA trust store, byte-range integrity, the offline CRL cache (24 h), `REVOCATION_UNKNOWN` semantics | A valid Iranian CA signature verifies; a modified byte range fails; an unavailable revocation check reports `UNKNOWN`, never valid | Unit + trust-store test | — | NOT_STARTED |
| P2-T10 | Verification-status model and weighting | Backend Eng | P2-T06, P2-T08, P2-T09 | 3d | The status enum, the weights, the append-only transition log | A transition is actor-attributed and never overwritten | Integration test | — | NOT_STARTED |
| P2-T11 | Cross-document consistency engine | Backend Eng | P2-T06, P2-T10 | 5d | The 8 consistency rules; two-workshop overlap detection; under-reporting detection | Each rule fires on a crafted fixture pair and stays silent on a clean pair | Integration tests | — | NOT_STARTED |
| P2-T12 | Shahkar interactive OTP flow and consent records | Backend Eng + Security Eng | P0-T18, P2-T02 | 5d | `request-otp`, `verify-otp` with a 120 s window, `CANDIDATE_CONSENT_RECORDS` | Verification without a consent record is impossible; **no automated verification code path exists** | Integration test + code-path audit | — | NOT_STARTED |
| P2-T13 | Official issuer verification orchestrators | Backend Eng | P2-T06, P2-T11 | 5d | Tamin, MSRT/Sajjad, TVTO, Sana and `rrk` integrators; the candidate-initiated token flow | Each integrator sits behind an interface with a recorded manual fallback | Integration tests with fixtures | DEC-011a | NOT_STARTED |
| P2-T14 | 4-way experience disambiguation engine | Actuarial Analyst + Backend Eng | P1-T01, P2-T06, P2-T11 | 5d | `E_total`, `E_sso`, `S_current`, `S_legal`; the Art. 86 720-day gate | The child allowance is refused when `E_sso < 720`; the four dimensions never cross-contaminate | Unit + property tests | — | NOT_STARTED |
| P2-T15 | Evidence credibility score (`V_score`) | Actuarial Analyst + Backend Eng | P2-T10, P2-T14 | 4d | The `V_score` computation, band widening, zero optimistic imputation | A missing document lowers `V_score` and widens the band; P50 never rises from unverified data | Unit + statistical tests | — | NOT_STARTED |
| P2-T16 | **OCR accuracy harness and the 500-document corpus** | Document Forensics Eng + QA Lead | — (external, long lead) | 10d | A consented, redacted corpus of 500 authentic Tamin slips; a per-field metric harness | The corpus is assembled, consented and redacted; the harness reports per-field and aggregate accuracy on it | Evaluation report | **BLOCKED** — the corpus does not exist; employer consent and a redaction pipeline are required | **BLOCKED** |
| P2-T17 | Document forensics test suite | QA Eng | P2-T05…P2-T16 | 5d | The DF-01…DF-13 assertions | All blocking assertions pass; DF-01 reports > 95 % on the authentic corpus | CI stage 10 | DEC-011 | NOT_STARTED |
| P2-T18 | **Phase 2 gate review** | CTO + QA Lead + Product Manager | P2-T16, P2-T17 | 2d | Gate evidence pack; sign-off | 500 authentic slips parse with > 95 % field extraction accuracy, with the corpus and the measured metrics archived | Gate review + evidence archive | DEC-011, DEC-011b | NOT_STARTED |

---

#### Phase 3 — Pre-Hire Simulation and React SPA (Weeks 15–18)

> **Scope note (ADR-008, owner 2026-11-15):** the simulation/benchmark/frontend-product module set (M5 UI, benchmark band visualisation, PDF/ERP bridges) is **out of product scope**; the existing partial frontend remains adopted bounded work (`IN_PROGRESS` rows below), and the rows are retained unchanged for the audit trail. Any revival requires a superseding ADR.

| ID | T | R | D | E | Del | AC | V | B | S |
| :-- | :-- | :-- | :-- | :-: | :-- | :-- | :-- | :-- | :-: |
| P3-T01 | Frontend scaffold | Codex /root (baseline adoption owner) | P1-T19 | 3d | Vite + React 19 + TS + Tailwind + Shadcn; TanStack Query; Zustand; the RTL root; the routing; the physical-utility lint gate | `pnpm build` succeeds; the lint gate rejects a physical direction utility | Local build/tests/logical-utility gate PASS (§19) | Bounded pre-existing scaffold adopted; P1-T19 and CI missing; no phase sequencing waived | IN_PROGRESS |
| P3-T02 | Persian design system | Codex /root (baseline adoption owner) | P3-T01 | 5d | Vazirmatn self-hosted; the logical-property token set; the numeral helpers; the currency formatter; the icon-mirroring registry | FE-01, FE-02, FE-06 pass; the font is served from the app origin | Existing components/helpers verified locally (§19); visual/axe NOT RUN | P3-T01 incomplete; DEC-006 remains open; bounded scaffold only | IN_PROGRESS |
| P3-T03 | Jalali calendar integration | Lead Frontend Eng | P3-T01 | 4d | `persiantools` integration; the Saturday-first picker; the dual Gregorian/Jalali input; the timezone policy; the rule-year anchoring | FE-04 and FE-05 pass; the picker handles Esfand 29/30 correctly | Component tests | DEC-006 | NOT_STARTED |
| P3-T04 | Currency and money formatting layer | Codex /root (implementation/adoption owner) | P3-T02 | 2d | The Rial/Toman formatter with mandatory unit labels; percentage formatting; rate-as-string handling | FE-06 passes; no fractional Rial is displayed | Rate-shift and unsafe-number defects reproduced, repaired and independently reviewed; formatter tests PASS (§19) | P3-T02 incomplete; real simulation/API integration absent | IN_PROGRESS |
| P3-T05 | API client and error handling | Codex /root (baseline adoption owner) | P0-T18, P3-T01 | 3d | The typed client; the query hooks; the error-catalogue mapping; correlation-id propagation; the `rule_set_status` warning surface | A non-`VERIFIED` rule set surfaces the warning; a 401 redirects to sign-in | Existing client tests PASS; live health/CORS/correlation smoke PASS (§19) | P0-T18/P3-T01 incomplete; provisional errors; only health contract delivered | IN_PROGRESS |
| P3-T06 | Route map, authentication screens, app shell | Codex /root (baseline adoption owner) | P3-T05 | 4d | Login; the MFA challenge; session expiry; navigation; the RTL shell; the responsive breakpoints | The sign-in flow works at 360 px; the session-expiry path is exercised | Existing shell/component tests PASS (§19); real sign-in/E2E NOT RUN | P3-T05 incomplete; presentation-only auth screens; no session implementation or timeout choice | IN_PROGRESS |
| P3-T07 | Net-to-gross simulation form | Lead Frontend Eng | P3-T04, P3-T05, P3-T06 | 5d | The dual-mode Simple/Advanced form; the dual-scenario result panel; the provenance display; the warning banner | Both scenarios are displayed with their posture labels; the displayed net equals the API response exactly | E2E test | — | NOT_STARTED |
| P3-T08 | CTC and termination simulator UI | Lead Frontend Eng | P3-T07 | 4d | The cost breakdown; the leave carryover; the Art. 11 probation visualisation | Every figure matches the API response; the Art. 11 case is demonstrated | E2E test | — | NOT_STARTED |
| P3-T09 | Document upload and forensics status UI | Lead Frontend Eng | P2-T12, P3-T05 | 4d | Upload; job-status polling; the verification status; the anomaly flags; the human-review queue | A document reaches a terminal status in the UI; flags are displayed as flags, not verdicts | E2E test | — | NOT_STARTED |
| P3-T10 | Benchmark band visualisation | Lead Frontend Eng + Actuarial Analyst | P3-T02, P1-T18 | 4d | The P10–P90 band chart with Persian axis labels; the compa-ratio and range-penetration display | The chart renders Persian axis labels; a library that cannot is rejected | Component test + visual review | DEC-006 | NOT_STARTED |
| P3-T11 | Persian PDF report generation | Backend Eng + Documentation Eng | P3-T02, P3-T03, P1-T19 | 6d | The HTML→PDF pipeline; the shaping stage; the font embedding; the page furniture; deterministic rendering from the snapshot | The PDF's figures equal the API response exactly; the text renders connected and correctly ordered; the output is reproducible from the snapshot | PDF snapshot test + visual diff | DEC-006 | NOT_STARTED |
| P3-T12 | Frontend component tests and the accessibility audit | QA Eng | P3-T02…P3-T11 | 5d | Vitest + Testing Library + jest-axe; FE-09…FE-14 | axe is clean on every route; all RTL and numeral assertions pass | CI stage 6 | — | NOT_STARTED |
| P3-T13 | End-to-end test suite | QA Eng | P2-T18, P3-T07, P3-T08, P3-T09, P3-T11 | 5d | The Playwright journeys; the < 3 s budget assertion; tenant isolation through the UI | A full simulation completes in < 3 s in the browser; every journey is repeatable | CI stage 7 | — | NOT_STARTED |
| P3-T14 | Performance and bundle optimisation | Lead Frontend Eng | P3-T13 | 3d | Route-level code splitting; font subsetting; the image budgets | The initial bundle meets the agreed budget; LCP does not regress | Bundle analysis + Lighthouse | — | NOT_STARTED |
| P3-T15 | **Phase 3 gate review** | CTO + QA Lead + Product Manager | P3-T12, P3-T13, P3-T14 | 2d | Gate evidence pack; sign-off | A full end-to-end simulation completes in < 3 s via the browser UI, with the evidence archived | Gate review + evidence archive | — | NOT_STARTED |

---

#### Phase 4 — Pilot Hardening and Compliance Sign-Off (Weeks 19–20)

| ID | T | R | D | E | Del | AC | V | B | S |
| :-- | :-- | :-- | :-- | :-: | :-- | :-- | :-- | :-- | :-: |
| P4-T01 | Monitoring, alerting and metrics | DevOps Lead | P0-T17, P1-T19, P2-T04 | 5d | The health endpoints; the redacting JSON logging; the Prometheus metrics; the alert rules; the read-only ops view | Every alert in `DEPLOYMENT.md` §7.4 has a rule and a documented response; the audit-chain alert is Critical | Synthetic-trigger alert test | DEC-003 | NOT_STARTED |
| P4-T02 | Operations runbooks and incident response | DevOps Lead + Security Architect | P4-T01 | 4d | The routine operations; the SEV-1…4 procedures; the SEV-1 audit-chain runbook; the emergency-access runbook | The SEV-1 runbook is reviewed by the CISO and rehearsed once | Tabletop exercise | — | NOT_STARTED |
| P4-T03 | Backup/restore drill and DR rehearsal | Database Eng + DevOps Lead | P0-T16 | 3d | A full restore drill with chain verification and RTO/RPO measurement | A restore succeeds; the chain verifies; a stored simulation reproduces; RTO/RPO are measured and published | Drill report | — | NOT_STARTED |
| P4-T04 | Data retention and the cryptographic-erasure purge job | Backend Eng + Database Eng | P0-T06, P2-T01 | 4d | The 180-day purge; DEK destruction; the 10-year retentions; the purge audit record | An expired candidate record is unrecoverable after the purge; the audit row survives with the count and the hash | Integration test + purge rehearsal | — | NOT_STARTED |
| P4-T05 | Performance and load test at pilot scale | QA Eng | P4-T01 | 3d | The load profiles at 50 rps sustained; the OCR throughput; a soak test | All budgets hold; no memory leak over a 2-hour soak | Load report | — | NOT_STARTED |
| P4-T06 | External penetration test | Security Eng (external vendor) | P4-T15 | 5d | OWASP Top 10 and multi-tenant isolation testing | No unresolved Critical or High finding | External report | — | NOT_STARTED |
| P4-T07 | Legal review sign-off | Legal Counsel (external) | P1-T20, P4-T15 | 4d | Iranian labour-attorney review of the engine, the worked example and the UI copy; the sign-off letter | A written sign-off is on file covering the statutory engine, the tax postures and the leave rules | Signed letter | DEC-001, DEC-009 | NOT_STARTED |
| P4-T08 | Tax accountant review of the golden vectors | Certified Tax Accountant | P1-T22, P4-T15 | 2d | Final review and acceptance of the vector corpus | Written acceptance of the corpus is on file | Signed record | DEC-002 | NOT_STARTED |
| P4-T09 | Pilot deployment in staging and smoke test | DevOps Lead | P3-T15, P4-T01, P4-T03, P4-T04 | 3d | A production-shaped staging deployment; the migration dry-run; the smoke test | The stack deploys from the release artefacts; the rollback rehearsal succeeds | Deployment record | DEC-010 | NOT_STARTED |
| P4-T10 | Pilot onboarding runbook | DevOps Lead + Product Manager | P4-T09 | 3d | The air-gapped mirroring checklist; the 3 design-partner onboarding plan; the RTO/RPO agreement template | The checklist is executed end-to-end with one design partner | Onboarding rehearsal | DEC-010 | NOT_STARTED |
| P4-T11 | **Go / No-Go review** | CTO + Product Manager + Legal Counsel + Security Architect + QA Lead | P4-T05, P4-T06, P4-T07, P4-T08, P4-T09, P4-T10 | 2d | The release decision record | Every release criterion in `TESTING.md` §18 is satisfied with archived evidence | Decision record | DEC-001…DEC-011 | NOT_STARTED |

---

### 14.4 Task census

**Dependency-integrity finding (2026-11-14, OPEN):** `P4-T06`, `P4-T07` and `P4-T08` depend on `P4-T15`, which does not exist in this 86-task WBS (Phase 4 ends at `P4-T11`). CTO + Product Manager must confirm the intended predecessor(s). No automatic substitution or roadmap/task-count change has been made. These three tasks must not start against an invented dependency. See `docs/DECISION_REQUIRED_FROM_OWNER.md` and changelog §10.

| Phase | Tasks | Effort (engineer-days) |
| :-- | --: | --: |
| Phase 0 | 20 | 69 |
| Phase 1 | 22 | 80 |
| Phase 2 | 18 | 95 |
| Phase 3 | 15 | 55 |
| Phase 4 | 11 | 34 |
| **Total** | **86** | **333** |

Effort excludes the external lead time (the tax accountant, the labour attorney, the penetration-test vendor, the corpus acquisition) and the calendar durations of the gates.

### 14.5 Critical path and parallelism

**Critical path** (the longest dependency chain to the Go/No-Go decision):

```
P0-T01 → P0-T04 → P0-T05 → P0-T06 → P0-T08 → P0-T07
  → P0-T09 → P0-T14 → P0-T18 → P0-T20
  → P1-T01 → P1-T04 → P1-T05 → P1-T13 → P1-T19
  → P1-T21 → P1-T22
  → P3-T01 → P3-T07 → P3-T13 → P3-T15
  → P4-T11
```

**Three independent long-lead chains** converge on the Phase 1 gate and must start in **Week 1**, not Week 5:

| Chain | Lead time | Why it is on the critical path |
| :--- | :--: | :--- |
| `P1-T02` · 1405 four-eyes verification | External: primary PDFs + a Certified Tax Accountant + a Legal Counsel | No statutory engine work can be certified without it |
| `P1-T15` · Golden vector corpus | External: a Certified Tax Accountant must author and sign 10,000 cases | The Phase 1 gate is defined in terms of it |
| `P2-T16` · The 500-slip authentic corpus | External: employer consent + a redaction pipeline | The Phase 2 gate is defined in terms of it |

**Parallelisable at t=0** (no unmet dependency):

| Task | Note |
| :-- | :-- |
| `P0-T01` | The only task with no predecessor. Everything else chains from it |
| `P1-T02` | External engagement; start immediately even though completion is blocked |
| `P1-T15` | External engagement; start immediately |
| `P2-T16` | External engagement; start immediately |

**Parallelisable within Phase 0** once `P0-T04` lands: `P0-T06`‖`P0-T08`‖`P0-T11`‖`P0-T13`‖`P0-T16`‖`P0-T17`; then `P0-T09`‖`P0-T10`‖`P0-T14`‖`P0-T15`‖`P0-T19`.

**Phase 2 parallelism**: `P2-T05`…`P2-T09` all depend on `P2-T04` and are mutually independent — they can be developed in parallel by separate engineers once the job interface is fixed.

**Phase 3 parallelism**: `P3-T02`‖`P3-T03`‖`P3-T05`; then `P3-T04`‖`P3-T06`; then `P3-T07`…`P3-T10` in parallel.

### 14.6 Schedule risk — recorded, not applied

The following are **observations for approval**, not changes. The 20-week roadmap stands as approved.

| # | Observation | Impact if unaddressed | Proposed response (requires approval) |
| :--: | :--- | :--- | :--- |
| R-1 | Phase 2 contains 95 engineer-days of work in a 6-week window with 5 tasks depending on `P2-T04`, which is itself blocked on a decision | Phase 2 compresses to ~3 engineers × 6 weeks × 5 d = 90 days against 95 days of effort, before the external corpus lead time | Approve ADR-005 in Week 1; add one engineer to Phase 2; start `P2-T16` in Week 1 |
| R-2 | The Phase 1 gate depends on an external artifact (10,000 signed vectors) with no current owner | The 20-week roadmap slips by an unbounded amount | Appoint the Certified Tax Accountant **now**; Phase 1 cannot be planned as committed until they accept |
| R-3 | Phase 0's 69 engineer-days against a 4-week window for a team of three = 60 days | Phase 0 is ~15 % over capacity | Accept a small Phase 0 overrun into Phase 1's start, or add one engineer in Weeks 1–4. Both are schedule changes requiring CTO approval |
| R-4 | `P2-T05` bakes a ~2–4 GB OCR model into the worker image; the air-gapped mirroring must complete before the pilot | A late discovery blocks the pilot | Perform the mirroring exercise as part of `P2-T05`, not at `P4-T09` |
| R-5 | The 1405 rule set may not be verifiable within the project window | Phase 1 ships on 1404 | Accepted interim position (DEC-001 Option C) with disclosure. This is a legal decision, not a schedule one |
| R-6 | The Phase 4 gate is an external penetration test plus an Iranian labour-attorney legal review — neither is deliverable inside a 2-week window that begins only after Phases 0–3 are complete | The Phase 4 gate cannot be met, and the pilot slips without an agreed buffer | Either extend Phase 4 to 4 weeks (a schedule change requiring CTO approval), or start the vendor engagements in Week 16 so the fieldwork runs in parallel with Phase 3 completion. **Both are schedule changes requiring approval** |

**No schedule change has been applied.** Each row requires CTO approval and, where it affects a gate, a documented approved change to `REMEDIATED` §7.

### 14.7 Release gates

Phase gates are in §14.1. **Release** criteria — the conditions under which a release candidate may be approved — are `docs/specs/TESTING.md` §18 and are not restated here.

### 14.8 Owner-requested full-scope compression target — 2026-11-15

Owner instruction: preserve the entire product scope, target Wednesday **2026-11-18 (27 Aban 1405), Asia/Tehran**; exact cutoff hour unspecified. Prioritize automatic collection of regulatory information before manual candidate/salary entry. This is an execution target over the existing 86 WBS tasks, not a rewrite of REMEDIATED §7, a passed gate or a commitment that external sign-offs will arrive. The approved five-phase/20-week baseline remains preserved for traceability. Accountable coordinator: Codex `/root`; no additional implementation team is claimed. Scope and acceptance criteria are unchanged.

| Date | Priority / existing WBS coverage | Measurable exit target and dependencies |
| :--- | :--- | :--- |
| Sun Nov 15 | Regulatory collection first: evidence-acquisition slice of P1-T02; provenance contract P0-T04. Open external work immediately: P1-T02/P1-T15, DEC-007/011 corpora, P4-T06/07/08 review | Tested official-source collector, source reachability report, acquisition/provenance boundaries. External engagement requires named humans/providers; no contact sent by the agent without authorization |
| Mon Nov 16 | Remaining P0-T01…T20 foundation: migrations, identity/RLS, key management/blind indexing, ledger, WORM, auth, restore, CI; P1-T01…T04 rule pipeline | Real DB migration/isolation/crypto/restore checks; controlled rule staging and blocked-activation checks. CI/provider, key/session/digest details and WORM endpoint must be resolved; P0 gate stays unpassed until evidence exists |
| Tue Nov 17 | Remaining P1-T05…T22 financial/statistical APIs; P2-T01…T18 document/experience pipeline; P3-T01…T15 Persian UI and outputs | Verified arithmetic/property/golden/contract checks; authentic document acceptance; complete UI paths. Depends on legal interpretation, independent signatures, licensed/consented data, async/PDF choices and preceding implementations |
| Wed Nov 18 | Remaining P4-T01…T11 deployment/observability/retention/reviews and all unresolved P0–P3 criteria; integration/release gate | Full required suites, genuine external legal/tax/security sign-offs, corpus acceptance and release evidence; report each unmet item as NOT RUN/FAIL/BLOCKED. Public deployment is not authorized by this target |

Every existing task remains in §14.3; none is dropped, replaced by a scaffold or counted complete from a plan. These dates are aggressive targets, not demonstrated capacity: 85 tasks lack COMPLETED status, external certified vectors/authentic corpora/reviewers are absent, and sequencing constrains concurrent work. Full-scope completion by Wednesday cannot currently be certified or promised. Escalate unmet dependencies immediately and report actual progress rather than relaxing legal/security gates.

Acquisition → staged candidate extraction → source-linked review/diff → independent approval → versioned activation → deterministic calculation is the intended information flow (M9). Collection can be automated; an unknown/unverified current rule must not yield an authoritative wage. Legal minima and market compensation remain separate; a legal crawler does not supply a licensed salary benchmark corpus.

### 14.9 Approved product-scope change — ADR-008 (2026-11-15)

**Owner decision (2026-11-15):** the product boundary is formally shrunk to the **statutory payroll calculation engine** — *Mozd-e Mabna/Saabet* decomposition, SSO (7 %/20 %/3 % with the insurable ceiling and 29/30/31-day variants), progressive income tax with the Article 137 dual-posture toggle (`conservative_inta` primary; welfare allowances taxable under `conservative_inta`, exempt under `court_precedent` — DEC-002a resolved), overtime/night shift on *Mozd-e Saabet* (220.00/227.33 divisors, 1.40/1.35 multipliers), severance `Mozd-e Saabet ÷ 12`, Eydi with the progressive excess tax (HB-GAP-005 never consumed), employer CTC without the 26-day double count, and the Article 11 worst case — delivered as pure functions under `backend/app/engines/` plus one minimal API endpoint, with no UI requirement.

Out of product scope (rows annotated in §14.3, not deleted): `P1-T13`, `P1-T15`, `P1-T17`, `P1-T18`, `P1-T20`, `P1-T21`, `P1-T22`, the Phase 2 forensics module, and the Phase 3 simulation/benchmark/PDF product set. DEC-007/DEC-008 are `REJECTED — out of product scope`. This is the first approved §14.6-class change: unlike the observations above, it **is** approved (ADR-008, Project Owner). The five-phase/20-week roadmap table in §14.1 is retained unchanged for traceability; §14.8's full-scope compression target is superseded by this scope decision for everything outside the engine boundary. Evidence: `BOOTSTRAP_CHANGELOG.md` §23.

### 14.10 Approved product-scope change — ADR-010 (2026-11-17)

**Owner decision (2026-11-17):** [ADR-010](adr/ADR-010-manager-mvp-product-scope.md) v2 is **Accepted** as written, prospectively, effective 2026-11-17 (non-retroactive). The current approved product direction is the **manager-only evaluation and compensation-advisory prototype**: single manager sign-in (Argon2id, opaque session token; `P0-T18` remains the completion gate), tenant-scoped PostgreSQL workspace (six tables, `tenant_id` + RLS policy + `FORCE ROW LEVEL SECURITY` in the same migration; append-only decision ledger at the DB level), deterministic `perf-v1` evaluation with **provisional, labelled** weights (PB-D03 stays `OPEN`), advisory recommendations costed through the existing statutory engine only, explicit approve/edit/reject decisions, the manager dashboard (DEC-014 Module D), manual entry plus single UTF-8 CSV import, and a four-page RTL Persian manager UI.

**Boundary of this authorization (ADR-010 §3 binds every task under it):** the prototype is **not production-ready**; backend integration is explicitly incomplete (`P0-T10` audit hash chain, `P0-T18` production-grade authentication, evidence byte storage, CI execution on GitHub, independent non-author review); deployment stays loopback/dev-only; synthetic data only; no production/pilot claim may be made in any document or UI.

**Out of scope (unchanged, `DEC-014` Modules B–C remain `OPEN — BLOCKING`):** company/organisation management beyond the one organisation bound at sign-in, the accounting foundation (chart of accounts, journal entries, fiscal periods), employee self-service, market data, OCR/forensics, AI scoring, production deployment (`DEC-010`).

**WBS mapping:** the manager prototype maps to no existing §14.3 task ID; it is recorded here as a dated addendum. Existing task statuses, dependencies and acceptance criteria in §14.3 are unchanged by this section. Every changelog-worthy action under this direction is dated in `docs/BOOTSTRAP_CHANGELOG.md` §34.

---

*End of `docs/EXECUTION_PLAN.md`. Task status, decisions and readiness are maintained in `docs/DECISIONS_REGISTER.md` and `docs/IMPLEMENTATION_READINESS.md`.*
