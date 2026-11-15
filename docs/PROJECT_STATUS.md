# Project Status — Pish Hesabdari

- **Document ID:** `DOC-STATUS-001`
- **Status:** Active — re-verified at every phase gate
- **As at:** 2026-11-15 — owner-authorized development, independent review and fresh local verification (§19); historical records retained
- **Verification basis:** direct inspection of the workspace and execution of the tooling, not the documentation's own claims
- **Related:** `docs/PISH_HESABDARI_HOLY_BIBLE.md` (authority) · `docs/EXECUTION_PLAN.md` (WBS) · `docs/IMPLEMENTATION_READINESS.md` (readiness) · `docs/ENVIRONMENT_INVENTORY.md` (tools)

> This document reports **what is true**, not what is planned. Where the corpus and the workspace disagree, the disagreement is recorded in §6.

---

## 1. One-line status

**An executable foundation with FastAPI liveness, reviewed Decimal primitives, isolated field encryption, a reviewed tenant-scoped S3 adapter and a partial Persian React interface.** No complete statutory engine, real authentication or integrated tenant-security/database foundation exists. Local tests/builds pass; no phase gate is passed.

## 2. Delivery state

**Current evidence, BOOTSTRAP_CHANGELOG §19:** P1-T04 and P0-T11 passed independent bounded code review after immutable-report, safe-error and UTF-8 corrections; both remain READY_FOR_REVIEW because CI/live acceptance is incomplete. Pre-existing frontend code is adopted as bounded IN_PROGRESS work in P3-T01/T02/T04/T05/T06; percentage and unsafe-number defects were reproduced and fixed. Dependencies and phase gates are unchanged. P0-T04 is now READY_FOR_REVIEW after owner-approved DEC-012 and isolated migration/security verification (§21). No production or pish_dev migration was run. Earlier dispatch/test counts are historical evidence in §§17–18.

| Dimension | State | Evidence |
| :--- | :--- | :--- |
| Application source code | FastAPI, isolated AES-256-GCM, bounded official-source collector, Decimal primitives, tenant-scoped S3 adapter and partial React interface | §19 fresh verification; collector stages UNVERIFIED local evidence; no complete financial engine or authenticated workflow |
| WBS tasks | **86 total — 1 COMPLETED, 6 IN_PROGRESS, 5 READY_FOR_REVIEW, 70 NOT_STARTED, 4 BLOCKED; 0 APPROVED** | Existing partial frontend work reconciled; P0-T11 becomes review-ready locally; no dependency waived |
| Phase gates passed | **0 of 5** | No gate evidence pack exists |
| Engine code | Decimal conversion, half-up Rial rounding, signed reconciliation and exact largest-remainder allocation | Reviewed bounded primitives only; tax/SSO/CTC/inverters/loader absent |
| Migrations | P0-T04 five-table baseline adopted under ADR-007; global FORCE RLS, restricted reader/reviewer, all-write identity gate | Real isolated PostgreSQL upgrade/downgrade/re-upgrade and 101 integration tests PASS; users FKs remain P0-T05; CI/production acceptance pending (§21) |
| Tests | **443 backend (342 unit/API + 101 real PostgreSQL integration) and 102 frontend tests PASS**; strict backend types on 30 files; frontend typecheck/build PASS | Final backend rerun: 443 PASS, 2 third-party deprecation warnings, 16.99s; local HTTP startup PASS; independent security review PASS (§21). CI/phase gates remain pending |
| CI/CD | **None.** No workflow file, no CI provider configuration. **DEC-F is open.** | Directory listing |
| Frontend | React/Vite/TypeScript RTL shell, Vazirmatn, number/currency helpers, typed client and disabled presentation-only auth screens | Local build/component tests PASS (§19); only health is a delivered backend contract; no visual/axe/auth acceptance |
| Containers | Last recorded PostgreSQL 16.16 + pgAudit runtime passed at `127.0.0.1:55432` | BOOTSTRAP_CHANGELOG §15; container/DB state not re-verified in §19 |
| OpenAPI contract | **Minimal** — the liveness endpoint only. `/health/ready` is deliberately absent. | `docs/specs/DEPLOYMENT.md` §7.1 |
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
| Commits | Local baseline history includes `2fc2b6f`, `eb806e4` and `55eef45`; development/publication record is in BOOTSTRAP_CHANGELOG §19. |
| Remote | Owner supplied `https://github.com/tahabehzad/pish-hesabdari`; `origin` configured and fetched. Remote initial commit `898388c` is preserved; no force-push authorized. |
| Branch | `codex/foundation-hardening`; publication outcome recorded in §19. |
| Files git ignores | **`backend/.venv`, the tool caches, `__pycache__`, and `.freebuff/*`** — everything the local toolchain produces |
| Working tree | Owner-authorized development and adoption of reviewed existing code. Unaccepted migration/model/integration/contract drafts remain outside this milestone. |
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
| --: | :--- | :--- | :--- | :--: | :--- |
| 1 | Original §11.1: no backend source/tests/tooling/Git | FastAPI main/config/logging modules, unit/API tests, tooling and a Git commit exist | Bootstrap is real; domain implementation remains absent | Corrected in Holy Bible v1.0.1 and `AGENTS.md`; no task status inferred from documentation |
| 2 | §0.4: *"39 files"* | **40** | None — the 40th is the Holy Bible itself | Already noted in the Holy Bible's Appendix F changelog |

Additional discrepancies: task-count arithmetic; false attribution of a Celery mandate; dangling `P4-T15` dependencies; and the initial misdiagnosis of sandbox-denied Python access. See changelog §10. Current owner approval: ADR-006 is Accepted, resolving DEC-004/004a/004b/005; the 17-entry engineering register has 4 resolved and 13 open entries. ADR-001…004 originals, ADR-005 PROPOSED status and the five-phase/20-week roadmap are preserved. No accountant, labour counsel or licensed/consented datasets are available; external gates stay blocked.

## 7. Phase 0 — what can start, and what cannot

### Can start now (no unresolved decision gates the implementation)

| Task | Title | Owner | Note |
| :--- | :--- | :--- | :--- |
| `P0-T01` | Repository and tooling baseline | Lead Backend Eng | **Verified in session 2.** `uv sync --frozen --all-groups` ✓, `ruff check .` ✓, `mypy --strict` ✓. The one unmet clause is *CI runs both*, which needs DEC-F. |
| `P0-T02` | FastAPI skeleton and configuration | Lead Backend Eng | **`COMPLETED` in session 2** — see §8. The application boots and `/health/live` answers 200. |
| `P0-T03` | PostgreSQL 16 provisioning and hardening | Codex /root | **READY_FOR_REVIEW**: official image/build, healthy local DB and actual hardening assertions PASS; P0-T01 CI still pending (§15) |
| `P0-T06` | ALEE encryption module | Codex implementation + independent reviewer | **READY_FOR_REVIEW**: isolated primitive tested and reviewed; CI/production key registry and integration evidence still pending |
| `P0-T07` | HMAC-SHA256 blind-index module | Security Eng | No open decision. Depends on `P0-T06`, `P0-T08`. Both are startable. |
| `P0-T11` | Object-storage adapter (S3 / GOVERNANCE) | Backend Eng | No open decision. Requires a local S3-compatible endpoint. |
| `P0-T13` | Reference-data seed | Data Analyst | **Blocked in substance** by DEC-007 (no licensed benchmark source). The *cities and taxonomy* part is unblocked. |
| `P0-T14` | RLS penetration test suite | QA Eng + Security Eng | No open decision. Requires PostgreSQL. |
| `P0-T15` | Encryption and blind-index test suite | QA Eng | Only the harness exists. Crypto acceptance depends on `P0-T06`, `P0-T07`, `P0-T08`; logging/configuration tests do not satisfy those criteria. |
| `P0-T16` | Backup and restore baseline | Database Eng + DevOps Lead | No open decision. Requires PostgreSQL. |
| `P0-T19` | CI pipeline for the Phase 0 gates | DevOps Lead | Bootstrap commit exists. **Requires DEC-F and the real isolation/crypto suites.** |

### Remaining sequencing and detailed-contract gates

| Task | Gated by | What may proceed meanwhile |
| :--- | :--- | :--- |
| `P0-T04` | P0-T03/database and detailed statutory-provenance contract | DEC-005 is resolved; no migration has been written or verified yet |
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
| 1405 cannot be activated | `backend/data/seeds/statutory_rules_1405.yaml` — all values `null`, `is_verified_and_active: false` | **Enforced by the seed itself.** The engine's fail-closed loader is `P1-T01` — not yet written. |
| The 1404 seed is immutable | Hash recorded: `CA16C455…FABE821` | **Recorded, but not yet enforced.** Invariant `R-10` requires a CI hash pin; there is no CI. → `P0-T19` |
| No defective financial value enters code | The published §5.1 example and the `SPEC-QA-001` §6.2 vector are both defective (100 % effective tax rate; severance on the wrong base) | **Recorded and quarantined.** No engine code exists, so nothing defective has been implemented. `P1-T20` must publish the corrected example. |
| The flat-10 % Eydi rule in the active 1404 seed | `eydi_tax_excess_rate: 0.10` conflicts with `FIND-LEG-04` | **Known, not yet corrected.** The file is immutable, so the correction is a new `1404.2` revision (HB-GAP-005, QB-11). |
| No synthetic data presented as acceptance evidence | `DF-01`, the Phase 1 gate and the Phase 2 gate | **Stated in `AGENTS.md` and the Holy Bible.** Enforced by the CI golden gate once `P1-T15` exists. |
| No candidate data leaves the premises | `SPEC-OPS-001` §12 — no outbound connection | Not yet enforceable (no runtime). **CONF-03** records that the Gemini OCR fallback in `REMEDIATED` §3.1 contradicts this. |

## 10. What is genuinely ready to build

**The foundation is now real.** The toolchain is installed and verified (`P0-T01`, one clause short), the FastAPI skeleton boots and answers its liveness probe (`P0-T02`), and the security primitives (`P0-T06`, `P0-T07`) remain startable — none of which touches an unresolved decision or a statutory value.

Everything downstream of `P0-T04`/`P0-T05` is gated on DEC-004 and DEC-005, and everything financial is additionally gated on the 1405 verification and the certified golden corpus.

---

*Derived from `docs/EXECUTION_PLAN.md` and `docs/DECISIONS_REGISTER.md`, re-verified against the workspace. Re-verify at every phase gate and after any change to a rank-1…4 document.*


### P0-T04 final verification — 2026-11-15

Owner approved T-2/F-1 explicitly; accepted ADR-007 and contract revision 3 govern this implementation. Local P0-T04 acceptance verified, READY_FOR_REVIEW; no additional completed task or phase. No software version bump: backend/frontend remain 0.1.0. Next work is P0-T05 identity schema and validated statutory actor foreign keys; all statutory writes stay blocked until then. CI provider/migration job remains outstanding. Evidence: BOOTSTRAP_CHANGELOG §21.
