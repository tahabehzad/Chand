# AUTONOMOUS_PROGRESS — Pish Hesabdari

Persistent progress record for the autonomous completion run (owner directive:
take the project from its current state to full completion, Holy Bible v1.0.7
as the primary context document).

| Field | Value |
| :--- | :--- |
| Started | 2026-11-16 (25 Aban 1405 SH) |
| Authority | `docs/PISH_HESABDARI_HOLY_BIBLE.md` v1.0.7 · `AGENTS.md` §2 invariants · ADR-006/007/008 (Accepted) |
| Product boundary | ADR-008: statutory payroll calculation engine (SSO, progressive income tax, net pay, overtime/night shift, Sanavat, Eydi, employer CTC, Article 11 worst case) + one minimal API endpoint on the verified 1404 SH baseline |
| Active statutory baseline | 1404 SH (`1404.1`, VERIFIED/ACTIVE). 1405 stays transcribed, unverified, inactive — never loadable. |

---

## 1. Verified baseline at the start of this run

Observed directly (not copied from documentation):

| Check | Command | Result |
| :--- | :--- | :--- |
| Backend tests | `backend\.venv\Scripts\python.exe -m pytest -q` | **548 passed, 104 skipped** (skips = PostgreSQL integration suites; Docker daemon not running) |
| Frontend tests | `corepack pnpm test` (frontend/) | **110 passed** (13 files) |
| Frontend build | `corepack pnpm build` | to be re-verified in this run |
| Git | `git log --oneline` | HEAD `c42fb9b fix(frontend): make the simulation screen submittable and truthful` |
| Docker/PostgreSQL | `docker version` | daemon unavailable → integration suites self-skip |

Engine modules present and implemented: `money.py`, `rules.py`, `bases.py`, `sso.py`,
`tax.py`, `overtime.py`, `severance.py`, `eydi.py`, `ctc.py`, `termination.py`;
composition in `services/payroll_service.py`; single endpoint
`POST /api/v1/simulations/gross-to-net`; Persian RTL SPA with a simulation screen.

## 2. Completed in this run

| # | Item | Evidence |
| --: | :--- | :--- |
| 1 | Repository + Holy Bible v1.0.7 inspection; baseline verification above | this file, §1 |
| 2 | Holy Bible refreshed in-repo from v1.0.6 to the owner's v1.0.7 | `docs/PISH_HESABDARI_HOLY_BIBLE.md`, `docs/BOOTSTRAP_CHANGELOG.md` |
| 3 | Independent monetary review of the engine (read-only reviewer, not the author) | `docs/BOOTSTRAP_CHANGELOG.md` §25 |

## 3. Current task

Independent engine review in flight; findings triaged and fixed on receipt.

## 4. Pending

- Golden reference-vector tests from Holy Bible Appendix A (engineering reference only).
- OpenAPI/contract conformance test for the single endpoint.
- End-to-end browser verification of the SPA against the live FastAPI service.
- Status reconciliation: `docs/EXECUTION_PLAN.md` §14.3 (P1 rows), `docs/PROJECT_STATUS.md` §2,
  `docs/BOOTSTRAP_CHANGELOG.md`, `docs/DECISIONS_REGISTER.md`.
- Runbook (`README.md`) and environment documentation.

## 5. Decisions taken in this run

| # | Decision | Rationale |
| --: | :--- | :--- |
| D-1 | The completion target is the **ADR-008 v1 boundary** (calculation engine + one minimal endpoint + the Persian simulation UI), not the superseded pre-employment platform module list | ADR-008 supersedes ADR-004's module list; `AGENTS.md` §1 |
| D-2 | The 1405 rule set stays unloadable; a 1405 request fails closed | ADR-008 directive 3; invariant 10 |
| D-3 | Out-of-scope modules (forensics, benchmarking, inverter, golden corpus, ERP/PDF bridges) are not implemented; their WBS rows are annotated, not deleted | ADR-008 "Out of product scope" |

## 6. Open issues and blockers

| Issue | Impact | Status |
| :--- | :--- | :--- |
| PostgreSQL integration suites (104 tests) cannot run: Docker daemon is not running on this machine | Database/RLS evidence is NOT RUN in this session | Noted; previous session's evidence (BOOTSTRAP_CHANGELOG §15/§21) is the last recorded run |
| Holy Bible Appendix A reference vectors assume a **mixed** Art. 137 posture (full SSO deduction + taxable welfare) that ADR-008's posture binding cannot produce | The vectors are usable only for the ladder arithmetic, not as end-to-end expectations | Recorded in `docs/DECISIONS_REGISTER.md` |
| No Certified Tax Accountant / Labour Counsel / licensed dataset available | No signed statutory verification, no certified golden corpus, no phase gate | External; unchanged |
| DEC-F (CI provider) | Hosted CI for the development repository is configured; the air-gapped deployment pipeline is not built | Partially resolved |

## 7. Exact next action

Triage the independent review findings, fix real defects, and add the
reference-vector and contract tests.
