# Project Status — Pish Hesabdari

- **Document ID:** `DOC-STATUS-001`
- **Status:** Active — re-verified at every phase gate
- **As at:** 2026-11-15 — owner-authorized local PostgreSQL recovery/runtime verification; historical session records retained
- **Verification basis:** direct inspection of the workspace and execution of the tooling, not the documentation's own claims
- **Related:** `docs/PISH_HESABDARI_HOLY_BIBLE.md` (authority) · `docs/EXECUTION_PLAN.md` (WBS) · `docs/IMPLEMENTATION_READINESS.md` (readiness) · `docs/ENVIRONMENT_INVENTORY.md` (tools)

> This document reports **what is true**, not what is planned. Where the corpus and the workspace disagree, the disagreement is recorded in §6.

---

## 1. One-line status

**A documented specification with a verified toolchain, FastAPI scaffold and independently reviewed field-encryption primitive.** No financial engine or integrated security/database foundation exists. Owner-approved Phase 0 choices are recorded in ADR-006; implementation readiness still depends on real integration/gate evidence.

## 2. Delivery state

| Dimension | State | Evidence |
| :--- | :--- | :--- |
| Application source code | FastAPI scaffold, isolated AES-256-GCM primitive and bounded official-source acquisition CLI (`app/statutory/collect_sources.py`). No financial engine, database models or product routers | Crypto §11; collector tests/independent review §16. Collector writes UNVERIFIED local staging, not WORM/active laws |
| WBS tasks | **86 total — 1 `COMPLETED` (`P0-T02`), 1 `IN_PROGRESS` (`P0-T01`), 0 `APPROVED`, 2 `READY_FOR_REVIEW` (`P0-T03`, `P0-T06`), 78 `NOT_STARTED`, 4 `BLOCKED`** | P0-T03 local runtime AC verified on 2026-11-15; CI dependency remains; no phase gate passed |
| Phase gates passed | **0 of 5** | No gate evidence pack exists |
| Engine code | **None.** The statutory seeds are *parameter files*, not an engine. | `backend/data/seeds/` |
| Migrations | **None.** No Alembic configuration, no `alembic/versions/`. | Directory listing |
| Tests | Latest full suite: **157 passed**, 2 warnings; strict types on 18 files; lint/format pass (§16) | §15: real PostgreSQL hardening verifier PASS. §16: 40 collector cases; six real sources failed acquisition; RLS/WORM acceptance remains unimplemented |
| CI/CD | **None.** No workflow file, no CI provider configuration. **DEC-F is open.** | Directory listing |
| Frontend | **None.** No `frontend/` directory. | Directory listing |
| Containers | Docker engine **29.9.2**; official PostgreSQL **16.16** + pgAudit development image built; project DB **healthy** at `127.0.0.1:55432` | Official pull/build and runtime verifier PASS, 2026-11-15; BOOTSTRAP_CHANGELOG §15 |
| OpenAPI contract | **Minimal** — the liveness endpoint only. `/health/ready` is deliberately absent. | `docs/specs/DEPLOYMENT.md` §7.1 |
| Benchmark data | **None.** No licensed corpus, no `salary_observations` rows. | DEC-007 open |

## 3. Version control state

| Item | State |
| :--- | :--- |
| Git repository | **Initialised in session 1** on `main`; the first commit was made in session 2 on `bootstrap/initial-import`, and `main` was then pointed at it. |
| Commits | **1** — `2fc2b6f`, the bootstrap commit. `main` and `bootstrap/initial-import` both point at it. |
| Remote | **None configured. Nothing has ever been pushed.** |
| Files git tracks | **72** — the documentation corpus, the seeds, the 11 skill contracts, the control files, the licence and the first application source |
| Files git ignores | **`backend/.venv`, the tool caches, `__pycache__`, and `.freebuff/*`** — everything the local toolchain produces |
| Working tree | Pre-existing documentation edits plus owner-authorized remediation; see `docs/BOOTSTRAP_CHANGELOG.md` §10. No commit or push performed in remediation. |
| Rollback | Review and reverse only the remediation hunks after preserving existing uncommitted edits. There is one commit, so `2fc2b6f^` is not a valid parent revision. Never reset or remove `.git` as a routine rollback. |

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
