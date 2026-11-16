# Roadmap to an Operationally Usable Payroll Engine

- **Document ID:** `DOC-ROADMAP-001`
- **Status:** Advisory plan derived from the register and the WBS. It creates no task, changes no status and approves no scope.
- **As at:** 2026-11-16 (25 Aban 1405 SH), against HEAD `f31e01e`
- **Authority:** `AGENTS.md` · ADR-008 (product boundary) · `docs/DECISIONS_REGISTER.md` (decision state) · `docs/EXECUTION_PLAN.md` §14.3 (tasks and estimates) · `docs/IMPLEMENTATION_READINESS.md`
- **Related:** `docs/PROJECT_STATUS.md` §2 (delivery state) · `docs/BOOTSTRAP_CHANGELOG.md` §25 (last verification)

> This document answers one question: **what is missing between the delivered
> engine and a payroll engine an Iranian employer could actually run?** It
> separates work that is merely unscheduled from work that is **blocked by a
> legal/tax determination** and work that is **outside the accepted product
> boundary**. It deliberately does not restate the engine's internals.

---

## 1. What "operationally usable" means

The engine is usable when all eight conditions hold. Each is measurable, and
none may be asserted from documentation.

| # | Condition | Current state |
| :--: | :--- | :--- |
| U1 | The **current statutory year (1405)** is verified and `ACTIVE`; the engine refuses nothing a live payroll needs | **Not met** — 1405 is transcribed, unverified, `is_verified_and_active: false`; `ACTIVE_STATUTORY_YEARS = {1404}` |
| U2 | Every monetary rule the product relies on has a **human legal/tax determination**, not an inferred reading | **Not met** — B-1…B-8, B-10 open; DEC-013 open |
| U3 | Calculations are **independently reviewed** by a non-author | **Not met** — 12 engine tasks are `READY_FOR_REVIEW`, 0 `APPROVED` |
| U4 | The **PostgreSQL-backed** suites and the CI pipeline actually run | **Not met** — 105 tests self-skip (no Docker); the workflow has never executed on GitHub |
| U5 | A payroll result can be **stored, retrieved and evidenced** (run, payslip, history, audit trail) | **Not met** — no persistence table, no API write path |
| U6 | Only **authorised users** can compute or read a payroll | **Not met** — the single endpoint is unauthenticated; no session, no RBAC, no tenant context |
| U7 | The engine is **wired into a served application** (readiness probe, deployment, backup) | **Not met** — no `/health/ready`, no deployment skeleton |
| U8 | The **evidence pack** exists: gate review signed with archived results | **Not met** — 0 of 5 phase gates passed |

**Read this as the honest bottom line:** the arithmetic part of the engine is
largely done (U1/U2/U3 aside), and everything that turns arithmetic into an
operational payroll system (U5/U6/U7) is absent.

## 2. Track A — in-domain engineering, no new decision required

These items are authorised by accepted ADRs and the corpus, and no open
register entry gates them. They can start today.

| Order | Item | WBS | Needs | Evidence that closes it |
| :--: | :--- | :-- | :--- | :--- |
| A1 | Reproducible database runtime (Docker + the official PostgreSQL image) | `P0-T03` re-verify | — | The 105 skipped tests execute and pass |
| A2 | CI actually runs (lint, types, tests, migration lint) | `P0-T19` (partial) | A2 needs no provider decision (DEC-F option b recorded) | A green run on GitHub, archived |
| A3 | RLS policies + `set_tenant_context()` for every tenant table | `P0-T09` (4d) | `P0-T04` (done, review-ready) and the identity tables | A tenant without context sees zero rows **and** raises; no table without `FORCE RLS` |
| A4 | Append-only hash-chained audit ledger | `P0-T10` (4d) | DEC-004b is resolved; `P0-T06` primitive exists | Chain verifies end to end; `UPDATE`/`DELETE` rejected by the database |
| A5 | RLS penetration suite (ISO-01…ISO-12) | `P0-T14` (5d) | A1, A3 | 100 % against real PostgreSQL with policies active |
| A6 | Crypto + blind-index acceptance suite (CR-01…CR-13) | `P0-T15` (3d) | A1; `P0-T07` (done) | Every CR check green; zero-plaintext-PII scan finds nothing |
| A7 | `/health/ready` with real dependency checks | `P0-T02` extension | A1, A3 | Probe fails when a dependency is down, passes when all are up |
| A8 | Money-safety AST gate in CI (no float in `app/engines/**`) | `P1-T04`/`P0-T15` clause | A2 | The gate fails when a float literal is introduced |
| A9 | Backup and restore baseline | `P0-T16` (3d) | A1 | A restore reproduces an identical schema on an isolated instance |

> **Added 2026-11-16 (ADR-009).** The compensation advisory module
> (`P5-T01`/`P5-T02`) is now in scope and delivered: a manager-entered profile
> is scored on published weights, placed inside a **manager-supplied** gross
> band, and costed at both bounds by the engine. It changes none of U1–U8: it
> adds no authentication, no persistence and no current-year rule set. Because
> no market data exists, the band remains a human judgement; the module ranks
> and costs, it does not price. See `docs/adr/ADR-009-compensation-advisory-module.md`
> and BOOTSTRAP_CHANGELOG §27.

## 3. Track B — blocked by a legal or tax determination

Every row changes a monetary figure or a legal characterisation. Implementing
any of them from an inference would breach `AGENTS.md` §2 (unknown values stay
unknown) and §11. **No code belongs in this table.**

| B-ID | Question | Blocks | Approver | What changes when resolved |
| :--- | :--- | :--- | :--- | :--- |
| **DEC-001/002 + `P1-T02`** | Is the 1405 rule set correct against the primary circulars (four-eyes)? | **U1 — the whole product**; `P1-T03`, `P1-T22` | Legal Counsel + Certified Tax Accountant (joint) | `P1-T03` activates 1405; the engine becomes usable for the current year |
| **B-2 / `P1-T05`** | Which Article 137 reading has legal effect on a payslip? | Which posture is authoritative | Counsel + Tax Accountant | The primary posture becomes a determined answer, not a default |
| **B-3 / QB-04** | Is the SSO insurable base the total gross or the fixed wage? | Every employer burden; `P1-T06` | SSO + Counsel | Insurable base definition; SSO, CTC and net all shift |
| **B-4** | Do overtime and night premiums enter the Sanavat and Eydi bases? | `P1-T08`, `P1-T09` | Labour Counsel | Accrual bases; annual cost |
| **B-5 / B-6** | Is the Eydi cap applied before or after tax, and how does the annual exemption interact with the salary exemption? | `P1-T09` | Tax Accountant | Eydi accrual and its tax |
| **B-7** | Article 71 leave-buyout: which divisor, and do welfare allowances participate? | `P1-T12` | Labour Counsel | Termination liability |
| **B-8** | Month-length convention for monthly statutory amounts (29/30/31 vs fixed 30) | `P1-T06`, `P1-T12` | Labour Counsel | Monthly minimum/ceiling values |
| **DEC-013 / B-10** | Must the minimum-wage, allowance floors and the seniority increment be applied to net pay, or stay reference-only? | Whether a package may be paid as declared | Project Owner + Counsel/Tax Accountant | Floors become enforced or stay advisory |
| **Unregistered — proposed open item** | **Monthly withholding vs annual cumulative (YTD) tax true-up.** The engine computes a monthly progressive tax on a monthly exemption; real payroll typically withholds cumulatively across the year | Fidelity of every real payslip; `P1-T05` | Certified Tax Accountant | Either a documented "monthly model is sufficient" answer, or a new engine capability. **This must be opened in the register before any implementation** |
| **DEC-011c** | The Article 86 720-day insured-days threshold | Only if insured-history logic is added | Legal Counsel | Eligibility gates |

**Note on the critical path:** the longest and least controllable item is
**DEC-001/002 — 1405 verification**. It is a legal activity, not engineering,
and it gates U1 and the Phase 1 gate. It should be commissioned immediately and
tracked separately from code progress.

## 4. Track C — operational premises (no code, no legal question)

| Item | Why it is a premise, not a feature | Current state |
| :--- | :--- | :--- |
| Docker/PostgreSQL daemon available to the build environment | Every database claim depends on it | Unavailable; 105 tests skip |
| A CI run (provider access) | "CI exists" ≠ "CI passed" | `gh` token invalid; never executed |
| An independent reviewer who did not write the engine | `AGENTS.md` §6 | Not available |
| Certified Tax Accountant, Labour Counsel | Track B | Not engaged |
| Licensed/consented data | Benchmarking only, out of scope | Absent |

## 5. Track D — outside the ADR-008 boundary (needs a written scope decision)

These are required by U5/U6/U8 but **not authorised** by the accepted product
boundary. They must go through a superseding ADR (see DEC-014), not through a
backlog.

| Capability | Why it is not in scope | Entry point |
| :--- | :--- | :--- |
| Employee / organisation master data, payroll runs, payslip records, history | ADR-008 authorises pure functions plus one endpoint; there is no payroll-run schema and no accounting model in the corpus | Owner decision → new ADR → schema + RLS + audit |
| Login, sessions, MFA, RBAC as a running feature | `P0-T18` is gated by `P0-T05`/`P0-T08` and an unwritten session contract (timeouts, remember-me, recovery) | `P0-T18` after `P0-T08` + session contract |
| Net-to-gross inverter | Explicitly excluded by ADR-008 (`P1-T13`) | Future ADR |
| PDF payslip / export, bulk multi-employee runs | Excluded (`P1-T20`–`P1-T22` scope notes) | Future ADR |
| Document forensics, benchmarking | Excluded (Phase 2 modules) | Future ADR |

## 6. Sequenced milestones

Each milestone has an exit criterion that cannot be satisfied by a document.

| Milestone | Content | Exit criterion | Blocked by |
| :--- | :--- | :--- | :--- |
| **M0 — Reproducible green baseline** | A1, A2, A8, `P0-T07` independent review, `P1-T19` contract suite in CI | 0 skipped-for-environment suites; a green CI run archived; `ruff`/`mypy --strict`/pytest recorded with exit codes | None |
| **M1a — Tenant security the API will need** | A3, A4, A5, A6 | No tenant table without `FORCE RLS`; audit chain verifies; ISO and CR suites green on real PostgreSQL | None |
| **M1b — Identity and keys** | `P0-T08` (4d), `P0-T18` (8d) | Both key paths work; AU-01…AU-05, AU-08…AU-10 pass | **DEC-004 key-hierarchy variant not selected; session contract unwritten** |
| **M2 — Current statutory year** | `P1-T02` (6d, external), `P1-T03` (3d) | 1405 `ACTIVE`; 1404 regression still green; the loader loads 1405 | **Externally blocked (legal)** |
| **M3 — Evidence-grade engine** | Independent review of the 12 engine tasks; `P1-T20`; `P1-T22` gate pack | Engine tasks move to `APPROVED`; Phase 1 gate signed or explicitly re-scoped | Independent reviewer; for the original gate also the certified corpus (`P1-T15`, out of scope) |
| **M4 — Operational records** | Employee/payroll-run/payslip persistence, history, audit coverage | A stored run is retrievable, hash-verified and never recomputable-rewritten | **Track D scope decision** |
| **M5 — Serving safely** | Auth in front of the API, tenancy on every request, `P0-T17` deployment skeleton (4d), `P0-T16` backup (3d) | An unauthenticated request is refused; readiness probe reflects dependencies; restore drill passes | `P0-T18`; **DEC-010 topology** |

**Recommended actual sequence:** run **M0 and M1a now** (18 engineer-days of
WBS-estimated work, all unblocked), commission **M2 in parallel from day one**
because it is external and long-lead, and hold **M4/M5** until the owner
records a scope decision. M3 needs a human reviewer and can only follow M0.

## 7. Why this order

1. **No statutory figure changes before the legal answer.** A wrong number
   shipped is worse than a missing feature (invariants 4, 6, 9).
2. **Convert "verified locally" into "verified" first.** Every later claim
   rests on a suite that currently skips 105 tests and a CI that never ran.
3. **Start long-lead external items immediately.** 1405 verification is the
   only item that prevents real use, and it is not engineering.
4. **Security before data.** Storing real employee payroll without
   authentication, tenant context and an audit trail would create the exact
   exposure the invariants forbid.
5. **Outside-boundary work waits for a written decision.** Otherwise the
   boundary erodes one convenient endpoint at a time (DEC-014).

## 8. Effort snapshot (WBS figures only)

| Group | Estimate | Source |
| :--- | :--- | :--- |
| M0 (A2 partial, A8, reviews) | ~4–6 engineer-days | `P0-T19` 4d remainder; `P1-T04`/`P0-T15` clause |
| M1a (A3–A6) | 16 engineer-days | `P0-T09` 4 + `P0-T10` 4 + `P0-T14` 5 + `P0-T15` 3 |
| M1b | 12 engineer-days | `P0-T08` 4 + `P0-T18` 8 |
| M2 | 9 engineer-days + external lead time | `P1-T02` 6 + `P1-T03` 3 |
| M3 | 4 engineer-days + reviewer time | `P1-T20` 2 + `P1-T22` 2 |
| M5 | 7 engineer-days | `P0-T16` 3 + `P0-T17` 4 |
| M4 | **not estimated** | no WBS row exists; requires scoping after the scope decision |

Environment setup (Docker, CI access) is not in any WBS row and is not
estimated; it is a hard premise.

## 9. Explicitly out of this roadmap

Net-to-gross inversion, document forensics and Shahkar, market benchmarking,
the Bühlmann-Kish pipeline, PDF export bridges, and the certified 10,000-case
corpus. All are excluded by ADR-008 and may return only through a superseding
ADR.

## 10. Risks

| Risk | Effect | Mitigation |
| :--- | :--- | :--- |
| 1405 verification stalls (external) | The engine stays legally unusable for current-year payroll, no matter how much code ships | Commission now; track as the critical path; never activate on secondary sources |
| CI keeps never running | Every "verified" claim stays local and unarchived | Treat a green archived run as M0's definition of done |
| Track D work is started "just to demo" | Invariants 4/6/9 breach; boundary erosion | DEC-014 stands; every out-of-scope screen stays labelled synthetic |
| Monthly-tax model turns out insufficient | A late, engine-wide change after persistence exists | Open the decision **before** M4 |
| Inferred legal readings ship as fact | Unlawful payslips | Track B stays a hard gate; `B`-series remains visible in the response |

---

*Derived from `docs/EXECUTION_PLAN.md` §14.3 and `docs/DECISIONS_REGISTER.md`.
Re-derive at every phase gate. Creating this document completes no task and
resolves no decision.*
