# ADR-010: Manager-only evaluation and compensation-advisory prototype as the current approved product direction (forward-looking)

- **Status**: **Accepted** — approved by the Project Owner as written (revised draft v2), prospective, **effective 2026-11-17**. Recorded in `docs/BOOTSTRAP_CHANGELOG.md` §34 (approval addendum). The Appendix-A register deltas were applied in one dated pass on 2026-11-17.
- **Effective date**: none yet. **If approved, the decision takes effect prospectively, from the date the owner records acceptance — not from any earlier date.**
- **Non-retroactivity clause**: this ADR does **not** authorize, legitimize or ratify any work performed before its approval date. The existing uncommitted manager slice was built while `DEC-014` stood `OPEN — BLOCKING`; that history is preserved as-is. Approval of this ADR would mean only that the owner, on the approval date, approves this product direction and thereby determines what happens to the existing code (continue it, or rework it) going forward. No claim that the prior implementation "was authorized" is made or implied anywhere in this ADR.
- **Required decider**: Project Owner (scope matters require an ADR per `AGENTS.md` §3 and `docs/DECISIONS.md` change control)
- **Consulted**: Lead Backend Engineering, Database Engineering, Security Architecture (documented review only; no new human sign-off is asserted by this draft)
- **Supersedes / confirms (only upon approval, prospectively)**: see §4 for the exact, classified list. It removes nothing else: ADR-001…007, ADR-009's advisory-module design, all statutory seeds, rates, rule sets and the engine arithmetic are unchanged.

## 0. What approval of this draft would and would not mean

**Approval would mean** that, from the approval date onward:

- the **current approved product direction** is a manager-focused MVP: the manager registers employees, collects performance observations from available sources, runs a deterministic, explainable evaluation, and makes approve/edit/reject decisions on advisory salary recommendations costed by the statutory engine;
- this MVP is a **prototype**, not a production system, and is bounded by §3 below;
- work may continue on it under the guardrails of §5 and the directives of §6.

**Approval would not mean** any of the following, and none may be claimed:

- that the previously built uncommitted slice was ever authorized, or that any earlier decision is retroactively confirmed;
- that the prototype is production-ready, pilot-ready or deployment-ready;
- that backend integration is complete (the open items in §3.2 and §6 remain open);
- that the `perf-v1` weights are approved rules (PB-D03 stays `OPEN`).

## 1. Context and Problem Statement

The owner's product mission: a **manager-only** employee performance evaluation and salary recommendation system. The manager collects employee data from multiple sources, evaluates performance, reviews salary recommendations and makes the final decision. **Employees do not require accounts.** No HR, ERP, attendance or employee self-service module is in scope.

Three accepted instruments currently stand between that mission and any implementation:

1. **ADR-008** (Accepted, 2026-11-15): product boundary = the statutory payroll engine, pure functions plus one minimal endpoint, no employee data, no frontend requirement.
2. **ADR-009** (Accepted, 2026-11-16): adds the compensation-advisory module but explicitly excludes persistence of people/proposals/decisions, any UI beyond the demo, and multi-tenant identity/auth (`P0-T18` gate).
3. **DEC-014** (`OPEN — BLOCKING`): authentication/RBAC, company management, the accounting foundation and a data-backed dashboard may not be implemented before the owner records a superseding ADR.

An uncommitted implementation slice answering the owner's stated direction exists on `autonomous/project-completion` (verification evidence: `BOOTSTRAP_CHANGELOG` §32–§33; `docs/CURRENT_STATE.md` §6). It was built without an authorizing ADR. The problem for the owner is forward-looking only: **whether to adopt the manager-MVP prototype as the current approved product direction from the approval date onward, and what to do with the existing code.**

## 2. Proposed decision outcome (effective only upon approval)

If approved, a **manager workspace prototype** becomes part of the product direction:

- **Identity**: exactly one user type — the manager. An email/password sign-in (Argon2id verification against the existing identity schema), one organisation bound at sign-in, an opaque bearer session token. No employee accounts, no employee portal, no self-service.
- **Workspace data**: tenant-scoped employees, observations (manual entry plus single UTF-8 CSV import), evidence **metadata only** (SHA-256; bytes not stored), evaluations, recommendations and decisions.
- **Evaluation**: a deterministic, versioned rule set `perf-v1` with published weights, normalisation caps and a missing-criteria policy; every score exposes per-criterion contributions. Weights are **illustrative and provisional** (PB-D03 unresolved).
- **Recommendations**: manager-supplied band → score-based placement → statutory costing **through the existing `compute_gross_to_net` path only** (the engine is called, never re-implemented), labelled `advisory: true`, `statutory: false`.
- **Decisions**: every recommendation ends in an explicit manager decision (approve/edit/reject + comment), stored once, append-only at the database level.
- **Persistence**: PostgreSQL tenant tables, each with `tenant_id`, an RLS policy and `FORCE ROW LEVEL SECURITY` in the same migration; an unbound session fails closed.
- **Interface**: a four-page RTL Persian manager UI with a real HTTP data layer and a session guard.

## 3. The prototype boundary — preserved, explicitly

### 3.1 Non-claims that bind all documentation and UI while this remains a prototype

1. **Not production-ready.** No production, pilot, go-live or deployment claim may be made (`DEC-010` stays `OPEN`; `P0-T17` stays `NOT_STARTED`).
2. **Backend integration is not complete.** The prototype's backend slice exists and is verified against a local PostgreSQL instance, but the platform is missing (non-exhaustive): the audit hash chain (`P0-T10`), production-grade authentication (`P0-T18`: HttpOnly cookie session, MFA, CSRF, rate limiting, runtime DB role), evidence byte storage (ADR-002 scope), a CI run on GitHub, and independent non-author review (`AGENTS.md` §6).
3. **Session token lives in `sessionStorage`** — readable by same-origin script; documented compromise, not a control.
4. **Deployment discipline**: loopback/dev hosts only; never exposed on a LAN, tunnel or the internet while in prototype posture.
5. **Data discipline**: synthetic or demo data only; no national ID, mobile, Sheba number or real salary is stored, printed, logged or transmitted.
6. **Labelling**: advisory labelling and the provisional-weights label are unconditional in API and UI; no figure may be described as lawful payroll; no real pay decision may cite `perf-v1`.

### 3.2 Explicitly out of scope (unchanged)

Company/organisation management beyond the one organisation bound at sign-in; the accounting foundation (chart of accounts, journal entries, fiscal periods) — no specification exists; employee self-service; market/benchmark data (DEC-007/008 rejected); OCR/document forensics (ADR-005 still `PROPOSED`); AI scoring (PB-D08 principle stands); automatic person matching/merging (R-1 rejected); automatic payment execution (R-3 rejected).

## 4. Decision-status classification (what each item becomes if approved)

### 4.1 Would become **CONFIRMED** on the approval date (prospectively)

| Item | Confirmed content |
| :--- | :--- |
| Product direction (PB-D01) | Manager-only evaluation and compensation-advisory prototype is the current approved product direction |
| User type (PB-D02) | Exactly one user type (manager); employees are subjects, not users; the 7-role identity schema of migration `0002` stays an unexercised foundation for later phases |

### 4.2 Would become **SUPERSEDED** on the approval date (history preserved, text unchanged)

| Instrument / entry | Superseded clause | Replaced by |
| :--- | :--- | :--- |
| ADR-008 | "pure functions plus one minimal FastAPI endpoint; no frontend requirement; no employee data" | The manager workspace prototype of §2, beside the unchanged statutory engine |
| ADR-009 | out-of-scope bullets: persistence of people/proposals/decisions; a UI; multi-tenant identity/auth | §2's prototype-scoped persistence, UI and single-manager sign-in |
| DEC-014 — Module A (authentication) and Module D (dashboard) | the implementation block | Authorized **in the prototype form of this ADR only** |
| PB-D06 | in-memory store premise | PostgreSQL tenant persistence with same-migration RLS |
| PB-D09 | "ship no login" recommendation | A minimal prototype sign-in exists; `P0-T18` remains the completion gate for production-grade auth |
| PB-D11 | `/api/v1/prototype/*` + `APP_ENV` gate premise | Real prototype API routes (`/api/v1/auth`, `/api/v1/manager`) with mandatory authentication and tenant binding; loopback discipline retained |
| `MVP_SCOPE.md` / `MVP_WBS.md` | "Proposed plan — not started"; in-memory/no-auth premises | Marked superseded planning history; budgets and task plan retained for traceability; no five-hour acceptance criterion is claimed |

### 4.3 Remains **unresolved** regardless of approval — never closed by this ADR

| Item | Status | Why |
| :--- | :--- | :--- |
| PB-D03 — real evaluation criteria and weights | `OPEN` | The 40/30/20/10 split stays illustrative; owner must confirm real criteria before any non-demo use |
| PB-D04 — data sources and integrations | `OPEN` | No connector may be designed yet |
| PB-D05 — person identity matching | `OPEN` | No auto-merge; human confirmation only |
| DEC-014 — Module B (company management) and Module C (accounting foundation) | partially unresolved | Stays blocked for Modules B/C: no specification, no approved schema; a future owner decision must precede any work |
| DEC-001/002, DEC-003, DEC-006, DEC-009…011 series, DEC-013 | unchanged | Untouched by this ADR |
| ADR-005 (async strategy) | `PROPOSED` | `P2-T04` stays blocked |
| Production readiness (DEC-010, P0-T17) | `OPEN` / `NOT_STARTED` | The prototype is not production (§3.1.1) |

## 5. Guardrails binding any continued work under this direction

1. Advisory labelling unconditional; no lawful-payroll claim.
2. `perf-v1` stays provisional and versioned; weight changes mean a new rule-set version; historical decisions are never recomputed.
3. Human decision mandatory per recommendation; append-only decisions.
4. Money and scores: Decimal `prec=34`, `ROUND_HALF_UP`, integer Rial at boundaries; no float literal in `app/engines/**`.
5. Every tenant table adds `tenant_id` + policy + `FORCE ROW LEVEL SECURITY` in the same migration; unbound session fails closed (`55000`).
6. No PII storage or transmission; evidence is metadata + SHA-256 only.
7. No new runtime dependency without a stated, task-specific need (`PB-D13`).
8. The statutory engine is called, never re-implemented (`R-9`); statutory tables stay global and untouched (ADR-007, `R-5`).

## 6. Directives if approved (all open items, none pre-cleared)

1. Reconcile the two `ENGINE_VERSION` constants deliberately and single-source them, with a test asserting the published API version equals the engine's.
2. `P0-T18` remains the completion gate for production-grade authentication; until then §3.1's compromises stand documented.
3. `P0-T10` (hash-chained audit ledger) is the next security task.
4. Independent non-author review of the slice is required before any `READY_FOR_REVIEW → APPROVED` movement.
5. Record the manager slice in `EXECUTION_PLAN §14.3` as a dated addendum block; do not inflate historical task statuses beyond evidence (`P0-T05` advance per X-5 is a separate, evidence-backed edit).
6. Every changelog-worthy action is recorded with its date in `docs/BOOTSTRAP_CHANGELOG.md`; historical decision records are never rewritten.

## 7. Considered options

| Option | Description | Outcome |
| :--- | :--- | :--- |
| 1 | Keep ADR-008/009 as-is; shelve or delete the slice | Rejected as a proposal — contradicts the owner's explicit, repeated direction |
| 2 | **Adopt this ADR: the manager-MVP prototype becomes the current approved product direction, prospectively, under a preserved prototype boundary** | **Proposed** |
| 3 | Authorize the full Batch-01 list (company management + accounting foundation + dashboard) | Rejected as a proposal — Modules B/C have no specification and no owner-approved schema |
| 4 | Continue the in-memory/loopback variant of `MVP_SCOPE` instead | Rejected as a proposal — abandons the verified slice and re-asks for a weaker compromise (no authentication) than the one built |

## 8. Consequences

**Positive if approved**: the product direction matches the owner's stated mission from a recorded approval date; tenant isolation, append-only decisions and provenance carry forward; one arithmetic of record is preserved; the prototype boundary and non-claims are explicit.

**Negative / trade-offs**: two API surfaces exist before the audit chain and production-grade auth; the token lives in `sessionStorage`; evaluation weights are unvalidated policy heuristics; independent review and GitHub CI are outstanding.

**If the owner rejects this ADR (or lets it lapse)**: the product boundary remains ADR-008/009 as accepted; `DEC-014` stays `OPEN — BLOCKING`; the existing slice remains unauthorized, uncommitted work whose disposition (keep, rework, remove) then requires a separate owner decision; nothing is deleted by this ADR either way.

---

## Appendix A — Register deltas to apply **only after explicit owner approval of the revised ADR**

Nothing below is applied now. On the recorded approval date, apply in one pass, each entry dated "per ADR-010 (approved YYYY-MM-DD)", with a same-day `BOOTSTRAP_CHANGELOG` entry; historical texts are retained unchanged everywhere.

1. `docs/DECISIONS_REGISTER.md` — DEC-014: Modules A/D recorded as authorized for the prototype per ADR-010; Modules B/C remain `OPEN — BLOCKING` pending a future owner decision; summary census refreshed; the original DEC-014 evidence text retained.
2. `docs/DECISIONS.md` — PB-D01 → `CONFIRMED (ADR-010, prospective)`; PB-D02 → `CONFIRMED (ADR-010)`; PB-D06, PB-D09, PB-D11 → marked superseded with their original text and dates preserved; PB-D03, PB-D04, PB-D05 explicitly remain `OPEN`.
3. `docs/adr/ADR-008` — header note only: scope clauses superseded for the manager prototype by ADR-010 as of the approval date; text retained unchanged.
4. `docs/adr/ADR-009` — header note only: persistence/UI/auth out-of-scope bullets superseded for the manager prototype; text retained unchanged.
5. `docs/ADR_INDEX.md` — ADR-010 row → `Accepted (effective <date>)` with the supersession list.
6. `docs/MVP_SCOPE.md`, `docs/MVP_WBS.md` — header note: superseded as planning history as of the approval date; premises no longer describe the tree; no completion claim.
7. `docs/PROJECT_STATUS.md` / `EXECUTION_PLAN §14.3` — add the dated manager-prototype addendum block with evidence references; §3.1's non-claims mirrored in both documents.

If the owner requests further changes, this ADR is revised and re-proposed; no register is edited in the meantime.
