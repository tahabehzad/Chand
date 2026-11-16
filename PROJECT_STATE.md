# PROJECT_STATE — Pish Hesabdari

- **Document ID:** `DOC-STATE-001`
- **Status:** Derived snapshot — no independent facts
- **As at:** 2026-11-16
- **Owners:** delivery `docs/PROJECT_STATUS.md` · tasks `docs/EXECUTION_PLAN.md §14.3` · decisions `docs/DECISIONS_REGISTER.md` + `docs/adr/` · verification `docs/BOOTSTRAP_CHANGELOG.md`

> Snapshot only. Where this file disagrees with an owner, the owner is right and this file is stale. Do not record new facts here.

## Current implementation status

The statutory payroll engine (ADR-008) is implemented on the verified 1404 baseline and served by one minimal endpoint; the Persian RTL simulation screen consumes it. Engine tasks are review-ready but not independently reviewed. No phase gate is passed.

## Completed

- Money primitives (Decimal, `prec = 34`, `ROUND_HALF_UP`, signed rounding residual).
- Fail-closed rule-set loader with published SHA-256 fingerprint (1404 active, 1405 inactive).
- Base decomposition, SSO, progressive tax with both Article 137 postures, overtime/night shift, Sanavat, Eydi, employer CTC, Article 11 termination simulator.
- Gross-to-net service and `POST /api/v1/simulations/gross-to-net` with per-field provenance.
- Isolated AES-256-GCM field encryption and HMAC-SHA256 blind index.
- Statutory baseline migration and identity foundation (isolated verification only).
- Compensation advisory module (ADR-009): manager-entered profile scored on published weights, placed in a manager-supplied band, costed at both bounds by the existing engine. Advisory only — no market data, no persistence.
- Persian RTL frontend shell, the simulation screen and the minimal manager sign-in/proposal screens (presentation-only; no credential is verified).
- CI workflow for backend and frontend gates.

## Incomplete / not implemented

- Real authentication, session management and tenant-security integration; the manager screen is explicitly presentation-only.
- Certified golden corpus and independent (non-author) review of the engine.
- Production migration run and production deployment evidence.
- PostgreSQL integration suites where the container image is unavailable (they self-skip).
- 1405 activation: transcribed, unverified, inactive.

## Known bugs and technical issues

- No open money-path defect recorded at this snapshot; any new failure is a defect, not a quarantine.
- Integration coverage depends on a pullable PostgreSQL image; absence is a coverage gap, not a pass.
- Frontend has no visual, axe or authentication acceptance evidence.

## Pending tasks

Refer to `docs/EXECUTION_PLAN.md §14.3` for the authoritative task list, dependencies and acceptance criteria, and to `docs/DECISIONS_REGISTER.md` for unresolved decisions (ADR-005 remains Proposed).

## Architectural decisions

Accepted: ADR-001…004, ADR-006, ADR-007, ADR-008 and ADR-009. Proposed: ADR-005. ADR-008 supersedes ADR-004's Phase 1 module list; ADR-009 extends ADR-008 with the compensation advisory module. Statutory baseline: 1404 SH verified and active.

## Last verified development checkpoint

- Verification record: `docs/BOOTSTRAP_CHANGELOG.md §28` (minimal manager UI and preview), §27 (ADR-009 module), §24 (independent monetary review remediation) and §23 (engine verification).
- Recorded at that checkpoint: backend suite, ruff, strict mypy, frontend tests, typecheck, logical-utility gate and production build passing; PostgreSQL integration suites self-skipping.
- These are recorded results, not a fresh runtime check. Re-run the narrowest relevant gate for the task at hand.