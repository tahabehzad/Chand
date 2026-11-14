# Phase 0 Bootstrap Plan — Pish Hesabdari

- **Document ID:** `DOC-P0BOOT-001`
- **Status:** Active — the Phase 0 preparation and task sequence
- **As at:** 2026-11-14 (23 Aban 1405 SH)
- **Roadmap authority:** `REMEDIATED_TECHNICAL_SPECIFICATION_V2.md` §7 — **five phases / 20 weeks, unchanged**
- **Related:** `docs/EXECUTION_PLAN.md` §14 · `docs/PROJECT_STATUS.md` · `docs/DECISION_REQUIRED_FROM_OWNER.md`

> **This plan does not rewrite the roadmap.** It sequences the *existing* Phase 0 tasks, separates the unblocked from the decision-gated, and states the verification evidence each one must produce.

---

## 1. Phase 0 definition of done

**Weeks 1–4.** Acceptance gate, verbatim from `REMEDIATED` §7:

> *100 % automated test pass on the multi-tenant RLS penetration suite; zero plaintext PII in the database.*

The gate has two conditions and neither may be waived. **The gate cannot be signed until DEC-004 and DEC-005 are resolved**, because `P0-T18` (8 days) and `P0-T12` implement them.

---

## 2. The 20 tasks, with their real blockers

The **B** column is taken from `docs/EXECUTION_PLAN.md` §14.3 — the blocking issue each task carries.

| ID | Title | Owner | Deps | E | Blocked by | Startable? |
| :--- | :--- | :--- | :--- | :-: | :--- | :--: |
| `P0-T01` | Repository and tooling baseline | Lead Backend Eng | — | 2d | DEC-005 (lint rule) | **YES** — partially done |
| `P0-T02` | FastAPI skeleton and configuration | Lead Backend Eng | `P0-T01` | 2d | — | **YES** |
| `P0-T03` | PostgreSQL 16 provisioning and hardening | Database Eng | `P0-T01` | 2d→3d | — (needs the Docker daemon) | **YES**, after Docker starts |
| `P0-T04` | Alembic baseline and the statutory rule-set tables | Database Eng | `P0-T01`, `P0-T03` | 3d | DEC-005 | **PARTIAL** |
| `P0-T05` | Tenant identity schema | Database Eng + Security Eng | `P0-T04` | 4d | DEC-004 | **NO** |
| `P0-T06` | ALEE encryption module | Security Eng | `P0-T01` | 4d | — | **YES** |
| `P0-T07` | HMAC-SHA256 blind-index module | Security Eng | `P0-T06`, `P0-T08` | 2d | — | **YES** |
| `P0-T08` | Key management: Vault adapter and local KEK | Security Eng + DevOps Lead | `P0-T01` | 4d | DEC-004 | **PARTIAL** |
| `P0-T09` | RLS policies and the tenant-context helper | Database Eng + Security Eng | `P0-T04`, `P0-T05` | 4d | DEC-005 | **PARTIAL** |
| `P0-T10` | Append-only hash-chained audit ledger | Backend Eng + Database Eng | `P0-T04`, `P0-T06` | 4d | DEC-004b | **PARTIAL** |
| `P0-T11` | Object-storage adapter (S3 / GOVERNANCE) | Backend Eng | `P0-T01` | 3d | — (needs an S3 endpoint) | **YES**, after Docker starts |
| `P0-T12` | ERD defect correction | Database Eng | `P0-T04` | 1d | DEC-005 | **NO** — this *is* DEC-005 |
| `P0-T13` | Reference-data seed | Data Analyst | `P0-T04` | 4d | DEC-007 | **PARTIAL** |
| `P0-T14` | RLS penetration test suite | QA Eng + Security Eng | `P0-T05`, `P0-T09` | 5d | — | **NO** (depends on `T05`, `T09`) |
| `P0-T15` | Encryption and blind-index test suite | QA Eng | `P0-T06`, `P0-T07`, `P0-T08` | 3d | — | **YES** |
| `P0-T16` | Backup and restore baseline | Database Eng + DevOps Lead | `P0-T03`, `P0-T04` | 3d | — | **PARTIAL** (needs `T04`) |
| `P0-T17` | Deployment skeleton | DevOps Lead | `P0-T02`, `P0-T03`, `P0-T11` | 4d | DEC-010 | **PARTIAL** |
| `P0-T18` | Authentication and session implementation | Backend Eng + Security Eng | `P0-T05`, `P0-T06`, `P0-T08` | 8d | DEC-004 | **NO** |
| `P0-T19` | CI pipeline for the Phase 0 gates | DevOps Lead | `P0-T01`, `P0-T03`, `P0-T14`, `P0-T15` | 4d | — | **PARTIAL** (needs `T14`) |
| `P0-T20` | **Phase 0 gate review** | CTO + QA Lead + Security Architect | `T14`, `T15`, `T16`, `T17`, `T18`, `T19` | 2d | DEC-004, DEC-005 | **NO** |

**Critical path:** `P0-T01 → P0-T04 → P0-T05 → P0-T06 → P0-T08 → P0-T07 → P0-T09 → P0-T14 → P0-T18 → P0-T20`.

**The binding observation:** the critical path runs **through** DEC-004 and DEC-005. Nothing the engineering team does can shorten it. **Decisions are the critical path.**

---

## 3. Execution sequence

### Wave 0 — complete (session 1)

| Item | Status | Evidence |
| :--- | :--- | :--: |
| Repository initialised on `main` | ✅ | `git branch --show-current` → `main` |
| `.gitignore`, `.gitattributes`, `.editorconfig` | ✅ | `git ls-files --others --exclude-standard` → 46 tracked / 2 ignored |
| `backend/pyproject.toml`, `ruff.toml`, `mypy.ini` | ✅ | `tomllib` / `configparser` parse cleanly |
| `backend/uv.lock` | ✅ | `uv lock --check` → "Resolved 166 packages" |
| `backend/.env.example` | ✅ | Keys only; checked against the `SPEC-OPS-001` §5.1 matrix |
| Control documents | ✅ | `README.md`, `AGENTS.md`, `docs/{ENVIRONMENT_INVENTORY,PROJECT_STATUS,AGENT_OPERATING_MODEL,PHASE_0_BOOTSTRAP_PLAN,DECISION_REQUIRED_FROM_OWNER,BOOTSTRAP_CHANGELOG}.md` |

### Wave 1 — no decision required

> **Session 2 (2026-11-14):** items **1** and **2** are done — `P0-T01` is `IN_PROGRESS` (its CI clause awaits DEC-F) and `P0-T02` is `COMPLETED`. Items **3–6** are unstarted and are now unblocked by a verified toolchain.

| Order | Task | What it produces | Verification |
| :--: | :--- | :--- | :--- |
| 1 | **`P0-T01` (finish)** | `uv.lock` committed; the lint-rule set; `.env.example`; the CI skeleton | `uv sync --frozen` ✓ · `ruff check .` ✓ · `mypy app` ✓ · *the CI job runs both* — **NOT DONE, DEC-F** → `IN_PROGRESS` |
| 2 | **`P0-T02`** | `app/main.py`, `core/config.py`, `core/logging.py`; `/health/live` | App boots ✓ · `/health/live` returns 200 ✓ · **no secret in any log line** ✓ · `ruff` + `mypy` clean ✓ → **`COMPLETED`** |
| 3 | **`P0-T06`** | `core/security/pii_transformer.py` — AES-256-GCM, 96-bit random IV | CR-01…CR-04: ciphertext ≠ plaintext; identical plaintext → different ciphertext; tampering raises; no key in a log |
| 4 | **`P0-T08` (partial)** | The Vault adapter **interface** and the local Argon2id KEK path | CR-08, CR-09; the **local** path must be exercised in dev, or it is untested in production |
| 5 | **`P0-T07`** | The blind-index service, the isolated pepper, the per-tenant salt, the normalisation rule | CR-04…CR-07: deterministic within a tenant; differs across tenants; the pepper is absent from the DB; B-Tree lookup < 1 ms |
| 6 | **`P0-T15`** | The crypto test suite | CR-01…CR-13 pass; the zero-plaintext-PII scan finds nothing |
| 7 | **`P0-T03`** *(after Docker starts)* | The PostgreSQL 16 init SQL, `postgres.conf`, the compose service | `log_statement ≠ 'all'`; TLS on; `pgaudit` present; the extension policy documented |

> **Prerequisite for waves 1 and 3–6 — RESOLVED in session 2.** `uv sync --frozen --all-groups` was approved (DEC-A) and ran: **118 packages installed** into `backend/.venv`, exit 0. `ruff`, `mypy` and `pytest` are now runnable, so waves 1 and 3–6 can be executed and *proved*.

### Wave 2 — requires DEC-005 and/or DEC-004

| Task | Unblocked by | Blocked by | What must not be written yet |
| :--- | :--- | :--- | :--- |
| `P0-T04` | DEC-005 Option A | — | The **identity** and **statutory-provenance** tables until DEC-005 is ratified |
| `P0-T08` (finish) | DEC-004 | — | The chosen key hierarchy and the Vault-as-primary path |
| `P0-T09` | DEC-005 | — | The catalogue of protected tables, until `P0-T04`/`P0-T05` exist |
| `P0-T10` | DEC-004b | DEC-004 | The ledger table's actor FK, until `P0-T05` exists |
| `P0-T05` | DEC-004 | — | **Everything** — this task *is* DEC-004 + DEC-005 |
| `P0-T12` | DEC-005 | — | **Everything** |
| `P0-T18` | DEC-004, DEC-004a | — | **Everything** — it must not choose between opaque sessions and JWT, or set the MFA role set |
| `P0-T13` (partial) | DEC-007 for the benchmark half | — | The benchmark half; the **cities and occupation taxonomy** are unblocked |
| `P0-T14` | — | `P0-T05`, `P0-T09` | The isolation suite's target tables |
| `P0-T16` | DEC-010 for the topology | `P0-T04` | The production topology; the backup mechanics are unblocked |
| `P0-T17` | DEC-010 | — | The production topology and the KMS choice |
| `P0-T19` | — | `P0-T14` | The stages that depend on the isolation suite |
| `P0-T20` | DEC-004, DEC-005 | all above | — |

### Wave 3 — Phase 0 gate

`P0-T20` is executed **only** when: the RLS suite passes 100 %, the plaintext-PII scan is clean, DEC-004 and DEC-005 are `RESOLVED`, and every preceding task is genuinely `COMPLETED`.

---

## 4. Local service architecture

Per `SPEC-OPS-001` §1 and §2.5. **Nothing here is implemented yet** — `infra/` does not exist.

| Service | Image | Purpose | ADR / spec | State |
| :--- | :--- | :--- | :--- | :--: |
| **Database** | PostgreSQL 16 | System of record; RLS; hash-chained ledger | `REMEDIATED` §3.1 | **Not created.** Needs the Docker daemon. |
| **Object store** | Ceph RADOS GW single-container dev instance with Object Lock `GOVERNANCE` | WORM forensic dossiers | **ADR-002** | **Not created.** Needs the Docker daemon. MinIO is **not** an option. |
| **Key management** | HashiCorp Vault **or** the local encrypted master config + Argon2id KEK | The master KEK | **ADR-003**; `SPEC-OPS-001` §8 | **DEC-010** governs the choice. The **local** path must be exercised in dev or it is untested in production. |
| **Application** | `python:3.12-slim` + `uv`, non-root, no compiler, no package manager, no source in the runtime layer | API runtime | `SPEC-OPS-001` §3.1 | **Not created** (`P0-T17`). |
| **Worker** | Same base, different entrypoint | OCR / forensics in a separate OS process | **ADR-005 (PROPOSED)** | **Must not be implemented against a specific queue.** Build behind a `JobQueue` interface only. |
| **Reverse proxy** | Traefik 3 or Nginx 1.25 | TLS 1.3, static SPA, rate limiting, security headers | `SPEC-OPS-001` §6 | **Not created.** |
| **Observability** | Prometheus metrics + JSON logs + three health endpoints | — | `SPEC-OPS-001` §7 | **Not created.** |
| **Backup** | `pg_basebackup` + WAL archiving; Ceph snapshots; Vault Raft snapshot | 10-year retention | `SPEC-OPS-001` §8 | **Not created.** |

> **Excluded and not to be revived:** Redis/Celery as a mandatory broker (ADR-005 rejects it), a managed cloud service of any kind, Kubernetes, a Node.js runtime in production (ADR-001), MinIO (`COMPLIANCE` mode) (ADR-002), `pgcrypto` (ADR-003).

**Dev-vs-production deviations must be explicit, never accidental** (`SPEC-OPS-001` §2.5): a short `GOVERNANCE` retention in dev, the local KEK in dev, a single app process in dev, and synthetic fixtures in dev.

---

## 5. CI design (to be implemented in `P0-T19`)

Thirteen stages, from `SPEC-QA-001` §15. The design is fixed; the implementation is not started.

| Stage | Trigger | Content | Blocking |
| --: | :--- | :--- | :--: |
| 0 | push | format, lint, type check, **secret scan** | yes |
| 1 | push | unit tests (L1) + coverage | yes |
| 2 | push | property-based (L2), reduced example count | yes |
| 3 | push | golden vectors (L3) + regression (L13) | yes |
| 4 | PR | integration + contract (L4, L5) | yes |
| 5 | PR | isolation + cryptography (L6, L7) — **the Phase 0 gate** | yes |
| 6 | PR | frontend unit + accessibility (L9) | yes |
| 7 | PR | E2E (L10) | yes |
| 8 | PR | security scans (L11) | yes |
| 9 | nightly | full property-based run | gates the release after 7 green nights |
| 10 | nightly | document pipeline suite (L8) | as above |
| 11 | pre-release | performance/load (L12) + full L2 + full L8 | release |
| 12 | release | penetration re-test + migration dry-run + rollback rehearsal | release |

**CI must never be created in a form that skips a required check.** A green pipeline that does not run the RLS suite is worse than no pipeline, because it manufactures confidence. The Stage 5 content is the Phase 0 gate; until `P0-T14` exists, Stage 5 has nothing real to run and must be marked **NOT RUN**, not **PASS**.

**CI provider is undecided** — GitHub Actions is implied by the corpus but no provider is configured and the repository has no remote. See DEC-F.

---

## 6. Financial and legal protection workstream

This workstream runs **in parallel** with engineering and is **not** on the engineering critical path. It is the reason the project will be able to ship at all.

| # | Work item | Owner | Evidence required | Gate | State |
| --: | :--- | :--- | :--- | :--: | :--: |
| 1 | **1405 four-eyes verification** (`P1-T02`) | Labour Counsel + Certified Tax Accountant | ≥ 2 signatures per parameter, ≥ 1 by a Certified Tax Accountant or Labour Counsel, bound to an artefact `sha256` | A1, A4, A7 | **NOT STARTED** — the blocking external commission |
| 2 | **Primary-source acquisition** | Labour Counsel | The L1 PDFs archived to WORM with a stored `sha256` | A2, A3 | **NOT STARTED** — `mcls.gov.ir` / `intamedia.ir` unreachable, `tamin.ir` HTTP 403 |
| 3 | **Open items O1–O10** | Labour Counsel + Tax Accountant | Each closed with a citation | A4 | O1…O5 open; O6…O10 raised by this plan |
| 4 | **1405 activation + 1404 regression** (`P1-T03`) | Backend Eng + Database Eng | A new `ACTIVE` rule set; a differential report attributing every changed line to a named parameter delta | A5, A8 | **NOT STARTED** |
| 5 | **Certified golden vector corpus** (`P1-T15`) | Certified Tax Accountant | ≥ 10 000 signed cases covering every slab, exemption and ceiling boundary | A6 | **NOT STARTED** — the longest-lead external item |
| 6 | **Corrected worked example** (`P1-T20`) | Documentation Eng + Payroll Eng | The published example reproduces from the engine within 0 Rial; the defect analysis published | DEC-002 | **NOT STARTED** — see §7 |
| 7 | **1404 Eydi defect correction** | Payroll Eng + DBA | A `1404.2` revision with progressive Eydi taxation; `1404.1` retired for new work | HB-GAP-005 | **NOT STARTED** — the seed is immutable, so a revision is the only route |
| 8 | **Canonical parameter schema** | Backend Eng + DBA | One schema both seeds map onto; a loader that maps both shapes | HB-GAP-013 | **NOT STARTED** |
| 9 | **SSO insurable-base determination** | Certified Tax Accountant | A written determination; a rule-set parameter | HB-GAP-006, QB-04 | **NOT STARTED** |

### 6.1 The statutory rule set must fail closed — acceptance criteria

The loader (`P1-T01`) must satisfy all of these, and they are **testable**:

```
1. Loading a rule set whose status is not ACTIVE raises StatutoryParameterUnavailable.
2. A null parameter raises; it is never coerced to 0.
3. A rule set for the requested year that does not exist raises — it never falls back to 1404.
4. A 1404 computation is labelled 1404.1 and never 1405.x.
5. Every response carries rule_version, rule_set_status, is_verified as SEPARATE fields.
6. The loader is the ONLY source of statutory values; no rate is hard-coded in Python.
```

### 6.2 Defect-to-test mapping

Every known financial defect maps to a test that must exist before the defect can be called closed.

| Defect | Where | Required test | Task |
| :--- | :--- | :--- | :--- |
| Income tax applied at 100 % of the post-exemption base | `REMEDIATED` §5.1; `SPEC-QA-001` §6.2 | A golden case whose taxable base sits **inside** a progressive slab, asserting the slab rate | `P1-T15`, `P1-T20` |
| Severance computed on total gross instead of *Mozd-e Saabet* | `REMEDIATED` §5.1 | A case with welfare allowances present, asserting `sanavat_accrual == Mozd_e_Saabet / 12` | `P1-T15`, `P1-T20` |
| The illustrative case exercises no tax slab | `REMEDIATED` §5.1 | A published example whose taxable income engages ≥ 2 slabs | `P1-T20` |
| Flat-10 % Eydi in the active 1404 seed | `statutory_rules_1404.yaml` | A case where the Eydi excess is taxed progressively, at the marginal bracket | `P1-T09`, `P1-T15` |
| `R-08` fails against the pinned seed (`0.0833333333 ≠ 1/12`) | `statutory_rules_1404.yaml` | The accrual computed as `Mozd_e_Saabet / 12`, never by multiplying a rounded rate | `P1-T08` |
| The 1404 seed has no `article_137_deduction_policy` key | `statutory_rules_1404.yaml` | The posture read from the rule set, never from a hard-coded default | `P1-T05` |
| Seed key-name drift between 1404 and 1405 | both seeds | A loader test over **both** rule years; `R-01`…`R-10` hold for each | `P1-T01` |
| The 1404 seed hash is not pinned | `R-10` | A CI job that fails when the seed's `sha256` changes | `P0-T19` |
| The SSO insurable base is modelled on total gross | `1.docx` §3 vs the corpus | A case with a child allowance, asserting the determined base | `P1-T06` — **gated on a Tax Accountant determination** |

**Do not copy any defective value into a test.** A golden vector that encodes the defect becomes a permanent regression lock on the defect.

---

## 7. The corrected worked example (Appendix A of the Holy Bible)

The published `REMEDIATED` §5.1 example is **defective** and must be replaced by `P1-T20`. The corrected figures were derived independently and are recorded in `docs/PISH_HESABDARI_HOLY_BIBLE.md` Appendix A. They are **proposals**, not certified vectors.

**Corrections required:**

| Field | Published | Corrected | Note |
| :--- | ---: | ---: | :--- |
| `statutory_version` | `1405.1-VERIFIED` | `1404.1` + separate `rule_set_status` / `is_verified` | The published label was false |
| `income_tax_rial` | 37,920,612 | **3,792,061** | The published figure was a 100 % effective rate |
| `tax_slab_applied` | "Slab 2 (10%) & Slab 3 (15%)" | **"Slab 2 (10%)"** | The base never reached slab 3 |
| `monthly_sanavat_accrual_rial` | 28,487,510 | **24,621,596** | Wrong base: total gross instead of *Mozd-e Saabet* |
| `total_monthly_employer_cost_rial` | 474,940,578 | **471,074,664** | The severance error propagated |

**Also required:** the `SPEC-QA-001` §6.2 reference vector must be replaced — it repeats the identical 100 %-tax defect.

**And:** the published example is a *degenerate* case (net 280,000,000 lands exactly on the 1404 exemption boundary, so the tax is zero and no slab is exercised). A non-degenerate replacement is published in the Holy Bible Appendix A.5 (net 400,000,000 → gross 449,082,859, engaging slabs 2 and 3).

---

## 8. External dependencies register

| # | Dependency | Gates | Owner | State |
| --: | :--- | :--- | :--- | :--: |
| 1 | **Certified Tax Accountant** | The Phase 1 gate entirely | Owner to appoint | **Unengaged.** The longest-lead item. |
| 2 | **Iranian Labour Counsel** | The 1405 verification; the Phase 4 legal sign-off | Owner to appoint | **Unengaged.** |
| 3 | **500 authentic Social Security slips** | The Phase 2 gate entirely | Document Forensics Eng + employer consents | **Does not exist.** No synthetic substitute is admissible. |
| 4 | **Licensed benchmark data** | Module 5 | Legal + Product (DEC-007) | **None acquired.** |
| 5 | **Iranian Root CA trust store** | `P2-T09` | Document Forensics Eng | **Not obtained.** |
| 6 | **Shahkar commercial arrangement** | `P2-T13`, `P2-T18` | Legal + Procurement (DEC-011a) | **No arrangement.** |
| 7 | **External penetration test** | The Phase 4 gate | Vendor (not engaged) | **Not booked.** |
| 8 | **L1 primary legal sources** | 1405 activation | Labour Counsel | **Unreachable from the engineering environment.** |
| 9 | **Design-partner pilot corporations** | The Phase 4 gate | Product Manager | **None engaged.** |

**Synthetic test fixtures may be used only when explicitly labelled as synthetic and never represented as acceptance evidence.**

---

## 9. Definition of done for Phase 0

```
□ Every Phase 0 task is genuinely COMPLETED with its acceptance criteria verified by command
□ The RLS penetration suite passes 100 % against real PostgreSQL 16 with policies active
□ The zero-plaintext-PII scan finds nothing in the database or the ledger
□ The audit chain verifies end-to-end; UPDATE and DELETE are rejected by the database
□ DEK rotation re-encrypts a tenant's PII and leaves every blind index unchanged
□ The 1404 seed's SHA-256 is pinned in CI and the pin is green
□ The loader fails closed for 1405 and for any non-ACTIVE rule set
□ Every committed figure is traceable to a rule id, a rule year and a formula reference
□ DEC-004, DEC-004a, DEC-004b and DEC-005 are RESOLVED with a named approver
□ The gate evidence pack is archived
```

---

*Sequenced from `docs/EXECUTION_PLAN.md` §14. The five-phase, 20-week roadmap is unchanged. Schedule risks R-1…R-6 remain recorded as proposals requiring CTO approval and are not applied here.*
