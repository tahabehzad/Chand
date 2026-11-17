# Project Status — Pish Hesabdari

- **Document ID:** `DOC-STATUS-001`
- **Status:** Active — re-verified at every phase gate
- **As at:** 2026-11-16 — autonomous completion mission: the statutory engine audited, two critical defects corrected, the engine test suite and the CI workflow delivered (§23); the independent monetary review (A-1…A-13) then re-verified and remediated with regression tests and reconciled documentation (§24). Historical records retained.
- **Verification basis:** direct inspection of the workspace and execution of the tooling, not the documentation's own claims
- **Related:** `docs/PISH_HESABDARI_HOLY_BIBLE.md` (authority) · `docs/EXECUTION_PLAN.md` (WBS) · `docs/IMPLEMENTATION_READINESS.md` (readiness) · `docs/ENVIRONMENT_INVENTORY.md` (tools)

> This document reports **what is true**, not what is planned. Where the corpus and the workspace disagree, the disagreement is recorded in §6.

---

## 1. One-line status

**A working statutory payroll calculation engine on the verified 1404 baseline — rule-set loader, base decomposition, SSO, progressive income tax with both Article 137 postures, overtime, Sanavat, Eydi, employer cost and the Article 11 termination simulator — served by one minimal API endpoint and a Persian simulation screen, with FastAPI liveness, isolated field encryption and a tenant-scoped S3 adapter beside it.** Local tests, lint, strict types, build and live requests pass; no real authentication, no integrated tenant-security foundation and no certified golden corpus exist. No phase gate is passed.

## 2. Delivery state

**Current evidence, BOOTSTRAP_CHANGELOG §24:** the independent monetary review's findings A-1…A-13 were re-verified against the tree and remediated. The signed residual was an identity (`total_gross − net` against the same deduction lines), provenance covered seven block keys only, the termination total added mutually exclusive probation lines, and the leave-buyout day value followed the calendar month. Each verified defect now has a regression test. The published contract carries the SHA-256 rule-set fingerprint, per-field provenance, a reference-only statutory block, per-posture exact tax and residual, and a reconciled termination block; the OpenAPI contract suite collects and passes. Engine tasks remain READY_FOR_REVIEW: independent review by a non-author and the PostgreSQL integration run are still outstanding. P1-T04 and P0-T11 passed independent bounded review after immutable-report, safe-error and UTF-8 corrections (§23). Pre-existing frontend code is adopted as bounded IN_PROGRESS work in P3-T01/T02/T04/T05/T06; percentage and unsafe-number defects were reproduced and fixed. Dependencies and phase gates are unchanged. P0-T04 is READY_FOR_REVIEW after owner-approved DEC-012 and isolated migration/security verification (§21). No production or pish_dev migration was run. Earlier dispatch/test counts are historical evidence in §§17–18 and §23.

| Dimension | State | Evidence |
| :--- | :--- | :--- |
| Application source code | FastAPI, isolated AES-256-GCM, bounded official-source collector, Decimal primitives, tenant-scoped S3 adapter, the **complete statutory payroll engine** (rule-set loader, base decomposition, SSO, progressive tax with both Article 137 postures, overtime, Sanavat, Eydi, employer cost, scenario-based termination liability) and the Persian simulation screen | §24 fresh verification; the engine reproduces the Holy Bible Appendix A reference vectors; collector stages remain UNVERIFIED local evidence; no authenticated workflow |
| WBS tasks | **88 total — 1 COMPLETED, 8 IN_PROGRESS, 20 READY_FOR_REVIEW, 55 NOT_STARTED, 4 BLOCKED; 0 APPROVED** | The twelve ADR-008 engine tasks (`P1-T01`, `P1-T05`–`P1-T12`, `P1-T14`, `P1-T16`, `P1-T19`) became review-ready with verified evidence (§23), strengthened by the §24 remediation; independent review is still outstanding, so none is APPROVED; no dependency waived |
| Phase gates passed | **0 of 5** | No gate evidence pack exists |
| Engine code | Decimal conversion, half-up Rial rounding, genuine reconciliation and exact largest-remainder allocation, plus the full statutory engine `0.3.0-payroll-engine`: fail-closed rule-set loader with published SHA-256 fingerprint, base decomposition, SSO, progressive tax with the dual Article 137 posture, overtime, Sanavat, Eydi, employer cost and the Article 11 termination simulator with an explicit scenario model | §24: the residual is `sum(rounded deduction lines) − round(exact total)` rather than a tautology; per-field provenance covers every derived path; the termination probation/separation lines reconcile; the Art. 71 day value uses the statutory 30-day divisor; the Appendix A reference vectors still reproduce to the Rial; the net-to-gross inverter stays out of scope (ADR-008) |
| Migrations | P0-T04 five-table baseline adopted under ADR-007; global FORCE RLS, restricted reader/reviewer, all-write identity gate | Real isolated PostgreSQL upgrade/downgrade/re-upgrade verified historically; 48 integration tests collected (self-skip without Docker; passed when available); users FKs remain P0-T05; CI/production acceptance pending (§21) |
| Tests | **765 backend PASS and 1 skipped** (unit/API/property; the skipped case is the schemathesis contract-valid negative case) **and 123 frontend tests PASS**; strict backend types on 86 files; frontend typecheck/build PASS | Fresh rerun after the X-4 reconciliation (§35): 765 PASS, 1 skipped, 9 warnings, 50.04 s; `ruff check .` and `mypy --strict app tests` (86 files) PASS. CI has never executed on GitHub and the phase gates remain pending |
| PII lookup foundation | `app/core/security/blind_index.py` — HMAC-SHA256 blind index on National ID / mobile / Sheba with the published normalisation rule | §25: 45 unit tests PASS (determinism, tenant/field separation, digit folding, leading zeros, fail-closed pepper); pepper custody (P0-T08) and the database-level CR-05/B-Tree evidence are NOT RUN. READY_FOR_REVIEW |
| Compensation advisory module (ADR-009) | `POST /api/v1/valuations/compensation-proposal` — manager-entered profile scored on the published `valuation-v1` weights, placed inside a manager-supplied gross band, and costed at both bounds by the existing 1404 engine | §27: 65 tests PASS (44 unit, 21 API) including a replay of the point costing through `gross-to-net`; `advisory: true`/`statutory: false` on every response. No market data, no persistence, no authentication. `P5-T01`/`P5-T02` READY_FOR_REVIEW |
| CI/CD | **GitHub Actions for the development repository** — `.github/workflows/ci.yml` runs the backend lint/type/test gates and the frontend lint/type/test/build gates | DEC-F option (b) implemented as recorded; `contents: read` only, no credential, no deployment, no migration; the workflow has not yet run on GitHub (the `gh` token is invalid) |
| Frontend | React/Vite/TypeScript RTL shell, Vazirmatn, number/currency helpers, typed client, disabled presentation-only auth screens and the **gross-to-net simulation screen** | §23: the screen's submission was broken by two HTML5 constraint violations and is now fixed and covered by 8 tests; the gross-to-net endpoint is a delivered backend contract; no visual/axe/auth acceptance |
| Containers | Last recorded PostgreSQL 16.16 + pgAudit runtime passed at `127.0.0.1:55432` | BOOTSTRAP_CHANGELOG §15; container/DB state not re-verified in §19 |
| OpenAPI contract | **Minimal but complete for the ADR-008 scope** — the liveness endpoint and `POST /api/v1/simulations/gross-to-net`. `/health/ready` is deliberately absent. | `docs/specs/DEPLOYMENT.md` §7.1; the endpoint contract is covered by `tests/api/test_payroll_simulation.py` and `tests/api/test_openapi_contract.py`, which now collects and passes (§24); PostgreSQL-backed contract cases skip without Docker |
| Benchmark data | **None.** No licensed corpus, no `salary_observations` rows. | DEC-007 open |

**Local MVP 0.1 supplement (2026-11-15):** the owner explicitly requested a
small accounting-themed UI demo. Dashboard, read-only synthetic transactions,
session-only display settings and navigation are implemented and verified;
102 frontend tests, typecheck, production build and logical-utility gate PASS.
Browser checks at 360 × 800 and 1440 × 1000 verified RTL layout, navigation,
unit changes and no document overflow (table overflow is confined to its region).
See BOOTSTRAP_CHANGELOG §20. This is a bounded local demo, not completion of
P3-T01/T02/T05/T06, a product-scope amendment or a production financial workflow.
The WBS census and outstanding dependencies above are unchanged.

## 3. Version control state

| Item | State |
| :--- | :--- |
| Git repository | **Initialised in session 1** on `main`; the first commit was made in session 2 on `bootstrap/initial-import`, and `main` was then pointed at it. |
| Commits | Local baseline history includes `2fc2b6f`, `eb806e4` and `55eef45`; the autonomous completion mission added `55a9547`, `3ab4c9f`, `abb4ce6`, `92dc221` and `c42fb9b`; the development/publication record is in BOOTSTRAP_CHANGELOG §§19 and 23. |
| Remote | Owner supplied `https://github.com/tahabehzad/pish-hesabdari`; `origin` configured and fetched. Remote initial commit `898388c` is preserved; no force-push authorized. |
| Branch | `autonomous/project-completion` — every commit of the autonomous mission was pushed to that branch; `origin/main` was never touched and no force-push was used (§23). The earlier `codex/foundation-hardening` publication outcome stays in §19. |
| Files git ignores | **`backend/.venv`, the tool caches, `__pycache__`, and `.freebuff/*`** — everything the local toolchain produces |
| Working tree | The statutory engine, the frontend SPA and the documentation set are committed on `autonomous/project-completion` through `f31e01e`, which carries the §24 remediation. The §25 P0-T07 work (blind-index module, its 45 tests, the ruff per-file waiver and the documentation set) is the **uncommitted** set; the `.obsidian/` vault and `Project Knowledge/` remain untracked and uncommitted. The unaccepted migration/model/integration drafts remain committed reviewed drafts outside the accepted scope. |
| Rollback | Revert only the milestone commits after review; preserve uncommitted drafts and both histories. Never reset or remove `.git` as routine rollback. |

## 4. Statutory baseline

| Rule set | Status | Detail |
| :--- | :--- | :--- |
| **1404 SH** (`1404.1`) | **`VERIFIED` / `ACTIVE`** — the only usable baseline | Seed `statutory_rules_1404.yaml`, SHA-256 `CA16C4558D29A81AE3123FBAB63732F130CC4425BF67617932C41B045FABE821`. 8 of 10 `R-` invariants pass exactly; 2 defects recorded (HB-GAP-005, HB-GAP-017). |
| **1405 SH** | **Transcribed, cross-corroborated at L2/L3, NOT four-eyes verified, INACTIVE** | Year-dependent parameters contain 16 null values and an empty bracket list; some constants are populated. `is_verified_and_active: false`. Activation conditions **A1–A8 are not met**. **Must not be activated.** |

## 5. Readiness

**Owner delivery target (2026-11-15):** full existing scope by Wednesday 2026-11-18 (27 Aban), Asia/Tehran; cutoff hour unspecified. Regulatory information collection precedes candidate/salary entry. Execution overlay: EXECUTION_PLAN §14.8. Target is not a commitment, gate waiver or replacement of the approved roadmap. P1-T02 acquisition preparation implemented and independently reviewed; all six official discovery probes failed (403/transport), so no current-year legal parameters were verified/activated (§16).

| Phase | Weeks | Classification | Gate met? | Can work start? |
| :--: | :--: | :--- | :--: | :--- |
| 0 | 1–4 | **READY WITH CONDITIONS** | No | **Yes** — subject to §7 below |
| 1 | 5–8 | **BLOCKED** | No | Engine work only, on 1404 |
| 2 | 9–14 | **BLOCKED** | No | `P2-T01`, `T02`, `T03`, `T07`, `T08` only |
| 3 | 15–18 | **READY WITH CONDITIONS** | No | Yes, from Week 15 |
| 4 | 19–20 | **READY WITH CONDITIONS** | No | No — gated by Phases 0–3 |

**Overall: NOT implementation-ready.** Two of five phases are blocked, and both blocks are external and legal rather than architectural.

## 6. Reconciliation — the Holy Bible versus the actual workspace

The original Holy Bible inventory predates bootstrap. Current factual corrections are reflected in v1.0.1 and the verification record in `docs/BOOTSTRAP_CHANGELOG.md` §10; the original audit remains historical evidence.

| # | Holy Bible says | The workspace actually is | Impact | Action |
| --: | :--- | :--- | :--- | :--: |
| 1 | Original §11.1: no backend source/tests/tooling/Git | FastAPI main/config/logging modules, unit/API tests, tooling, a Git commit and the ADR-008 statutory engine exist | Bootstrap is real; the v1 engine is implemented and tested locally (§24) | Corrected in Holy Bible v1.0.1 and `AGENTS.md`; no task status inferred from documentation |
| 2 | §0.4: *"39 files"* | **40** | None — the 40th is the Holy Bible itself | Already noted in the Holy Bible's Appendix F changelog |

Additional discrepancies: task-count arithmetic; false attribution of a Celery mandate; dangling `P4-T15` dependencies; and the initial misdiagnosis of sandbox-denied Python access. See changelog §10. Current owner approval: ADR-006 is Accepted, resolving DEC-004/004a/004b/005; the register now holds 20 entries — 12 open (8 blocking, 4 non-blocking), 6 resolved by ADR-006/007/008, 2 rejected (DEC-007, DEC-008), plus the B-1…B-11 ambiguity ledger and proposed DEC-013. DEC-014 is partially resolved (Modules A/D by ADR-010; Modules B/C remain OPEN — BLOCKING). ADR-001…004 originals, ADR-005 PROPOSED status and the five-phase/20-week roadmap are preserved. No accountant, labour counsel or licensed/consented datasets are available; external gates stay blocked.

## 7. Phase 0 — what can start, and what cannot

### Can start now (no unresolved decision gates the implementation)

| Task | Title | Owner | Note |
| :--- | :--- | :--- | :--- |
| `P0-T01` | Repository and tooling baseline | Lead Backend Eng | **Verified locally.** `uv sync --frozen --all-groups` ✓, `ruff check .` ✓, `mypy --strict` ✓. The CI workflow now exists (DEC-F option b), but the clause *CI runs both* remains unmet because the workflow has never executed on GitHub. |
| `P0-T02` | FastAPI skeleton and configuration | Lead Backend Eng | **`COMPLETED` in session 2** — see §8. The application boots and `/health/live` answers 200. |
| `P0-T03` | PostgreSQL 16 provisioning and hardening | Codex /root | **READY_FOR_REVIEW**: official image/build, healthy local DB and actual hardening assertions PASS; P0-T01 CI still pending (§15) |
| `P0-T06` | ALEE encryption module | Codex implementation + independent reviewer | **READY_FOR_REVIEW**: isolated primitive tested and reviewed; CI/production key registry and integration evidence still pending |
| `P0-T07` | HMAC-SHA256 blind-index module | Security Eng | No open decision. `P0-T06` is READY_FOR_REVIEW; `P0-T08`'s key-hierarchy/rotation choice is still unresolved. |
| `P0-T11` | Object-storage adapter (S3 / GOVERNANCE) | Backend Eng | No open decision. Requires a local S3-compatible endpoint. |
| `P0-T13` | Reference-data seed | Data Analyst | **Blocked in substance** by DEC-007 (no licensed benchmark source). The *cities and taxonomy* part is unblocked. |
| `P0-T14` | RLS penetration test suite | QA Eng + Security Eng | No open decision. Requires PostgreSQL. |
| `P0-T15` | Encryption and blind-index test suite | QA Eng | Only the harness exists. Crypto acceptance depends on `P0-T06`, `P0-T07`, `P0-T08`; logging/configuration tests do not satisfy those criteria. |
| `P0-T16` | Backup and restore baseline | Database Eng + DevOps Lead | No open decision. Requires PostgreSQL. |
| `P0-T19` | CI pipeline for the Phase 0 gates | DevOps Lead | Workflow committed (DEC-F option b, `contents: read`); it has never run on GitHub, and the real isolation/crypto suites still gate a Phase 0 pass. |

### Remaining sequencing and detailed-contract gates

| Task | Gated by | What may proceed meanwhile |
| :--- | :--- | :--- |
| `P0-T04` | P0-T03/database and detailed statutory-provenance contract | DEC-005/012 are resolved; the five-table baseline is written and verified on an isolated PostgreSQL instance (§21); no production/pish_dev migration and no CI execution |
| `P0-T05` | P0-T04 and complete identity/isolation schema review | DEC-004/005 resolved; all tenant-owned tables still require same-migration FORCE RLS |
| `P0-T08` | Unresolved key-hierarchy/rotation details | Four-choice approval did not select a Vault/local KEK variant; P0-T06 depends only on an explicit registry protocol |
| `P0-T09` | P0-T04/P0-T05 | Approved schema direction does not create or verify policies |
| `P0-T10` | P0-T04/P0-T06; actor model and digest contract | DEC-004b scope resolved; signed-digest cadence/custody/anchor must be specified before implementation |
| `P0-T12` | P0-T04 | DEC-005 resolved; ADR-006 provides formal authority for candidate index correction |
| `P0-T17` | DEC-010 | The image and compose *structure* can be drafted; the production topology and KMS choice wait on DEC-010. |
| `P0-T18` | P0-T05/P0-T06/P0-T08 and detailed session contract | Session/MFA choices accepted; timeouts/remember-me and unapproved recovery/emergency details are not inferred |
| `P0-T20` | Actual RLS/crypto/backup/deployment/auth/CI evidence | Four decision gates cleared; no phase-gate approval or implementation completion follows |

## 8. Work actually performed

### 8.1 Session 1

| # | Change | Class | Verified by |
| --: | :--- | :--- | :--: |
| 1 | `git init -b main` (no add, no commit) | Reversible infrastructure | `git branch --show-current` → `main`; `git rev-list --count HEAD` → no revision (0 commits) |
| 2 | `.gitignore` | New file | `git ls-files --others --exclude-standard` → 46 tracked; `--ignored` → exactly 2 |
| 3 | `.gitattributes` | New file | Content review; `.editorconfig` cross-check |
| 4 | `.editorconfig` | New file | Content review |
| 5 | `README.md` | New file | Content review |
| 6 | `AGENTS.md` | New file | Content review |
| 7 | `backend/pyproject.toml` | New file | `tomllib` parses it |
| 8 | `backend/ruff.toml` | New file | `tomllib` parses it |
| 9 | `backend/mypy.ini` | New file | `configparser` parses it |
| 10 | `backend/.env.example` | New file | Manual review against the `SPEC-OPS-001` §5.1 matrix; **keys only, no values** |
| 11 | `backend/uv.lock` | Generated | `uv lock --check` → "Resolved 166 packages"; **no `.venv` created, nothing installed** |
| 12 | `docs/ENVIRONMENT_INVENTORY.md`, `docs/PROJECT_STATUS.md`, `docs/AGENT_OPERATING_MODEL.md`, `docs/PHASE_0_BOOTSTRAP_PLAN.md`, `docs/DECISION_REQUIRED_FROM_OWNER.md`, `docs/BOOTSTRAP_CHANGELOG.md` | New files | Content review |

### 8.2 Session 2 — the first executable tasks

| # | Change | Class | Verified by |
| --: | :--- | :--- | :--: |
| 13 | `uv sync --frozen --all-groups` (DEC-A) | Dependency install, reversible | `Checked 118 packages`, exit 0 |
| 14 | `backend/ruff.toml` — corrected the `banned-api` schema | Defect fix in a session-1 file | `ruff check .` → `All checks passed!` |
| 15 | `backend/mypy.ini` — corrected the plugin syntax | Defect fix in a session-1 file | `mypy app` → `Success: no issues found` |
| 16 | `backend/app/core/config.py` | New source | 14 unit tests; the production policy and the 1405 guard are asserted |
| 17 | `backend/app/core/logging.py` | New source | 11 unit tests; the CR-13 property is asserted against the real emission path |
| 18 | `backend/app/main.py` | New source | `GET /health/live` → 200 under a live uvicorn |
| 19 | `backend/tests/**` (4 files) | New tests | `pytest -q` → `34 passed` |
| 20 | `LICENSE` | Proprietary licence (DEC-G) | Content review |
| 21 | `backend/pyproject.toml` — the pytest harness | Configuration | `pytest -q` collects and runs |
| 22 | `.gitignore` — npm lockfiles rejected | Configuration | `git ls-files --others --ignored` confirms the ignore |
| 23 | The first commit `2fc2b6f`, on `bootstrap/initial-import`; `main` pointed at it | Version control | `git log --oneline`; the 40-file hash baseline is unchanged |
| 24 | `docs/EXECUTION_PLAN.md` §14.3 — the `P0-T01` and `P0-T02` status columns | Status record | The status matches the evidence in §8.2 |
| 25 | `docs/BOOTSTRAP_CHANGELOG.md` §9 | Audit record | Every command with its actual result |

**Nothing else in the workspace was modified.** The full pre-session SHA-256 baseline of all 40 original files is recorded in `docs/BOOTSTRAP_CHANGELOG.md` §2 and was re-verified at the end of session 2: **40/40 byte-identical.**

## 9. The critical financial and legal protections now in place

| Protection | Where | State |
| :--- | :--- | :--: |
| 1405 cannot be activated | `backend/data/seeds/statutory_rules_1405.yaml` — all values `null`, `is_verified_and_active: false`; loader refuses any year outside `ACTIVE_STATUTORY_YEARS = {1404}` | **Enforced by the seed and the fail-closed loader** (`P1-T01`); a 1405 request raises `StatutoryParameterUnavailable` |
| The 1404 seed is immutable | Hash recorded: `CA16C455…FABE821`; the loader publishes a SHA-256 fingerprint of the canonical parameters | **Recorded; a CI hash pin is still absent.** Invariant `R-10` needs the CI gate, and the workflow has never run on GitHub. → `P0-T19` |
| No defective financial value enters code | The published §5.1 example and the `SPEC-QA-001` §6.2 vector are both defective (100 % effective tax rate; severance on the wrong base) | **Recorded and quarantined**; `P1-T20` is out of ADR-008 scope. The engine reproduces the Holy Bible Appendix A vectors, not the defective example. |
| The flat-10 % Eydi rule in the active 1404 seed | `eydi_tax_excess_rate: 0.10` conflicts with `FIND-LEG-04` | **Known, not consumed.** The Eydi engine applies progressive taxation to the excess and never reads the flat rate (HB-GAP-005, QB-11); the seed stays immutable. |
| No synthetic data presented as acceptance evidence | `DF-01`, the Phase 1 gate and the Phase 2 gate | **Stated in `AGENTS.md` and the Holy Bible.** No CI golden gate exists (`P1-T15` is blocked and out of ADR-008 scope); the §24 results are labelled local tests, not statutory certification. |
| No candidate data leaves the premises | `SPEC-OPS-001` §12 — no outbound connection | Not yet enforceable (no deployment or authenticated workflow). **CONF-03** records that the Gemini OCR fallback in `REMEDIATED` §3.1 contradicts this. |

## 10. What is genuinely ready to build

**The foundation and the ADR-008 v1 engine are now real.** The toolchain is installed and verified (`P0-T01`, one clause short), the FastAPI skeleton boots and answers its liveness probe (`P0-T02`), `P0-T06` is READY_FOR_REVIEW, and the full statutory engine runs on the verified 1404.1 baseline with one minimal endpoint and a passing contract suite (§24).

Under ADR-008, the v1 financial path is **not** gated on 1405 verification or a certified golden corpus; both remain out of product scope (DEC-001/002 stay open only for a future revival). Production and tenant work downstream of `P0-T04`/`P0-T05` still depends on the identity schema, a CI execution and PostgreSQL-backed evidence. No phase gate is passed.

---

*Derived from `docs/EXECUTION_PLAN.md` and `docs/DECISIONS_REGISTER.md`, re-verified against the workspace. Re-verify at every phase gate and after any change to a rank-1…4 document.*


### P0-T04 final verification — 2026-11-15

Owner approved T-2/F-1 explicitly; accepted ADR-007 and contract revision 3 govern this implementation. Local P0-T04 acceptance verified, READY_FOR_REVIEW; no additional completed task or phase. No software version bump: backend/frontend remain 0.1.0. Next work is P0-T05 identity schema and validated statutory actor foreign keys; all statutory writes stay blocked until then. CI provider/migration job remains outstanding. Evidence: BOOTSTRAP_CHANGELOG §21.

**P0-T09 first slice (2026-11-16):** the per-transaction tenant context is real —
`backend/app/core/security/tenant_context.py` plus migration `0003`
(`set_tenant_context`, the fail-closed `current_tenant_id`, and the
`pish_tenant_rls_violation()` catalogue assertion). Verified over a disposable
PostgreSQL 16 round-trip: `732 passed, 1 skipped` backend, `ruff` and
`mypy --strict` (74 files) clean. No RLS policy is attached yet because no
tenant data table exists; the runtime role stays P0-T18 and the penetration
suite P0-T14. `P0-T09` is `IN_PROGRESS`, no phase gate is passed. Evidence:
BOOTSTRAP_CHANGELOG §30.

**P0-T16 slice (2026-11-16):** the backup/restore baseline exists —
`infra/postgres/backup/{backup.sh,restore.sh,schema_fingerprint.sql}` with a
deterministic catalogue digest. Verified on two disposable PostgreSQL 16
containers: a schema-identical restore (fingerprint equality), row and
forced-RLS survival, retention to the newest N sets, and a guard that refuses
to restore onto the source. `735 passed, 1 skipped`, ruff and `mypy --strict`
clean. WAL archiving/PITR and the encrypted off-site copy stay open
(DEC-010, P4-T03). `P0-T16` is `IN_PROGRESS`. Evidence: BOOTSTRAP_CHANGELOG §31.

**Manager workspace prototype — authorized 2026-11-17 (ADR-010):** the Project Owner approved [ADR-010](adr/ADR-010-manager-mvp-product-scope.md) v2 as written, prospectively, effective 2026-11-17 (non-retroactive). The current approved product direction is the manager-only evaluation and compensation-advisory **prototype**: single manager sign-in, tenant-scoped PostgreSQL workspace (same-migration `tenant_id` + RLS policy + `FORCE ROW LEVEL SECURITY`), deterministic `perf-v1` evaluation with provisional labelled weights, advisory recommendations costed through the existing statutory engine, append-only decisions, the manager dashboard, and a four-page RTL manager UI. PB-D01/D02 are confirmed; PB-D06/D09/D11 are superseded; DEC-014 Modules A/D are resolved (Modules B/C stay `OPEN — BLOCKING`). **This is not a production or pilot claim**: the prototype is not production-ready, backend integration is explicitly incomplete (`P0-T10`, `P0-T18`, evidence byte storage, CI, independent review), and deployment stays loopback/dev-only (ADR-010 §3). PB-D03 (real criteria/weights), PB-D04, PB-D05 remain `OPEN`. The §2 summary above describes the pre-ADR-010 delivery state and is refreshed by this note. Evidence: BOOTSTRAP_CHANGELOG §32–§34.
