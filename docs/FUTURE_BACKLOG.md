# Future Backlog — Pish-Hesabdari

- **Document ID:** `DOC-BACKLOG-001`
- **Status:** Active backlog for capabilities **not** in the five-hour MVP. Nothing here is committed or scheduled.
- **Priorities:** **B1** = required before any real use · **B2** = required before a pilot · **B3** = valuable after the product is real · **B4** = speculative.
- **Related owners:** historical tasks (`docs/EXECUTION_PLAN.md §14.3`), decisions (`docs/DECISIONS.md` PB-\*, `docs/DECISIONS_REGISTER.md` DEC-\*), architecture risks (`docs/ARCHITECTURE.md §12`).

> Deferred does not mean deleted. Historical implementations, migrations, ADRs and research remain in the repository as evidence.

---

## B1 — Required before any real (non-demo) use

| ID | Capability | Why deferred from the MVP | Prerequisites | Historical owner | Risk |
| :--- | :--- | :--- | :--- | :--- | :--- |
| BL-01 | **Remove or hard-disable the prototype surface** for any non-local environment | The MVP is a demonstration with no authentication | PB-D11 gate proven by AC-11; deployment gate | — | Shipping it would expose unauthenticated data |
| BL-02 | **Authentication, sessions, MFA, RBAC** | Needs DB, hashing, CSRF, rate limiting, tests — weeks, not hours | `P0-T18`; ADR-006 decisions | `P0-T18` (`NOT_STARTED`) | Highest security gap today |
| BL-03 | **PostgreSQL persistence for person/observation/evaluation/recommendation** | Five hours cannot deliver schema + migration + RLS + wiring | PB-D06; tenant-table rule (`AGENTS.md §2.12`) | new; overlaps `P2-T01` (out of product scope) | Data loss / no history |
| BL-04 | **Tenant RLS on data tables + penetration suite** | No tenant table exists yet | BL-03; `P0-T09`; `P0-T14` | `P0-T09` (`IN_PROGRESS`), `P0-T14` | Cross-tenant leak |
| BL-05 | **Hash-chained audit ledger for decisions and evaluations** | No ledger module; needs actor model and canonical JSON | `P0-T10`; actor identity (BL-02) | `P0-T10` | Decisions unprovable, tamperable |
| BL-06 | **Key management (Vault/KEK) and PII custody** | No registry/rotation; prototype stores no PII | `P0-T08`; PB-D04 consent model | `P0-T08` | Cannot legally store real person data |
| BL-07 | **Legal/accounting verification of the statutory engine** | External humans; 1404-only baseline | `P1-T02`, `P1-T15`, `P4-T07`, `P4-T08`; `DEC-001`/`DEC-002` | those tasks (`BLOCKED`/out of scope) | Recommendation may imply unlawful pay |
| BL-08 | **Backup with PITR + rehearsed restore (RTO/RPO)** | Partial logical backup exists | `P0-T16` completion; `P4-T03`; `DEC-010` | `P0-T16` (`IN_PROGRESS`) | Unrecoverable loss |

## B2 — Required before a pilot

| ID | Capability | Why deferred | Prerequisites | Historical owner |
| :--- | :--- | :--- | :--- | :--- |
| BL-09 | **Measurement periods and historical comparison** | MVP is single-period | BL-03; rule-set versioning | new (FR-16) |
| BL-10 | **Import history, duplicate detection, correction audit** | MVP has manual entry (+optional CSV) | BL-03; PB-D05 | new (FR-14) |
| BL-11 | **Evaluation rule-set governance** (who may change weights, four-eyes, effective dates) | Prototype weights are provisional | PB-D03; DEC-001-style gate | new |
| BL-12 | **Automated E2E and accessibility (Playwright + axe)** | Toolchain cost exceeds five hours | MVP routes stable | `P3-T12`, `P3-T13` (out of scope) |
| BL-13 | **CI executed on GitHub and the 13-stage pipeline** | Workflow exists but has never run | DEC-F confirmation; `P0-T19` | `P0-T19` |
| BL-14 | **Deployment topology, containers, health/readiness** | `DEC-010` open; only a Postgres dev compose exists | `DEC-010`; `P0-T17` | `P0-T17` |
| BL-15 | **Load/performance evidence for the recommendation path** | No measurement yet | BL-03 | `P1-T21`/`P4-T05` (out of scope) |
| BL-16 | **External penetration test** | No deployment to test | BL-14; BL-02 | `P4-T06` (dependency defect `P4-T15`) |

## B3 — Valuable after the product is real

| ID | Capability | Notes | Prerequisites |
| :--- | :--- | :--- | :--- |
| BL-17 | **External connectors** (payroll exports, sales/CRM, attendance, project tracking) | Each is an adapter behind one `SourceConnector` port; no engine change | PB-D04; BL-03; consent |
| BL-18 | **Identity matching with human confirmation** | Candidate matches + evidence display; never auto-merge | PB-D05; BL-10 |
| BL-19 | **Multi-criteria evaluation maturity** (normalisation choices, weighting review, sensitivity analysis) | Show how the score moves if a weight changes | PB-D03; BL-11 |
| BL-20 | **Reporting** (per-person, per-period, decision log, compensation drift) | Persian RTL tables; no chart library yet | BL-03; `DEC-006` for chart/PDF choices |
| BL-21 | **PDF recommendation/payslip-style report** | Requires shaping, embedding, reproducibility — `DEC-006` open | `P3-T11` (out of scope) |
| BL-22 | **Jalali picker and period UX** | A port exists (`frontend/src/lib/calendar.ts`); no implementation registered | `DEC-006` (`L-1`) |
| BL-23 | **AI assistance**: extraction from files, summarisation of evidence, anomaly flags | Must be explainable, human-confirmed, no silent money decision | PB-D08; data-governance decision; BL-06 |
| BL-24 | **Compensation survey / benchmark data** | Needs licensed data; `DEC-007` was **rejected out of scope** — requires a new ADR | PB-D04 + legal review |
| BL-25 | **Employee self-service portal** | Deliberately out of MVP (PB-D02) | BL-02; tenancy; consent |

## B4 — Speculative

| ID | Capability | Why speculative |
| :--- | :--- | :--- |
| BL-26 | Multi-tenant SaaS with per-organisation isolation and billing | Requires a tenancy ADR, RLS at scale, enterprise operations |
| BL-27 | Mobile application | Web-first; no validated need |
| BL-28 | Payroll disbursement / bank integration | Regulated; explicitly rejected for the MVP (R-3) |
| BL-29 | Actuarial/statistical valuation (credibility shrinkage, percentile bands) | Original `P1-T17`; needs licensed data and an actuarial owner; out of ADR-008 scope |
| BL-30 | Document forensics / OCR authenticity pipeline | Historical Phase 2; out of product scope; expensive model provisioning |
| BL-31 | Advanced monitoring/observability stack (metrics, alerting, SLOs) | `P4-T01`; only meaningful once deployed |

---

## Cross-reference: historical capabilities that stay deferred

| Historical scope | State | Backlog |
| :--- | :--- | :--- |
| Document forensics (P2-T01…P2-T18) | Out of product scope (ADR-008); T04 blocked by ADR-005 | BL-30 |
| Benchmark data pipeline (P1-T17/T18), DEC-007/008 | Rejected out of scope | BL-24, BL-29 |
| Net-to-gross inverter (P1-T13) | Out of scope | not scheduled |
| Golden corpus (P1-T15) | Blocked external | BL-07 |
| Persian PDF (P3-T11) | Out of scope; `DEC-006` open | BL-21 |
| Audit ledger (P0-T10) | Not started | BL-05 |
| Identity/auth (P0-T05/T18) | Schema drafted; runtime absent | BL-02 |

**Rule:** reviving any of these requires a recorded ADR or decision, not a backlog line alone.
