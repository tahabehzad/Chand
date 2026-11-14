# Bootstrap Changelog — Pish Hesabdari

- **Document ID:** `DOC-BOOTLOG-001`
- **Status:** Active — the append-only record of every change made during engineering bootstrap
- **Session 1:** 2026-11-14 (23 Aban 1405 SH) — Engineering Readiness & Phase 0 Bootstrap
- **Related:** `docs/PROJECT_STATUS.md` · `docs/AGENT_OPERATING_MODEL.md` · `docs/ENVIRONMENT_INVENTORY.md`

> **Rule.** Every modification made in this repository is recorded here with the exact command run and its actual result. A change without a verification result is not a change — it is an intention. Results are separated into **PASS**, **FAIL** and **NOT RUN**.

---

## 1. Session 1 summary

| Class | Count |
| :--- | --: |
| Files created | 16 |
| Files modified | 0 in the corpus; **1** — `docs/EXECUTION_PLAN.md`, the `P0-T01`/`P0-T02` status columns only |
| Files deleted | 0 |
| Infrastructure actions | 1 (`git init`) |
| Commits made | **0** |
| Remotes configured | **0** |
| Dependencies installed | **0** |
| Packages installed globally | **0** |
| Source documents modified | **0** |

---

## 2. Pre-session integrity baseline

SHA-256 (first 16 hex characters) of **all 40 files** present before this session. Any later change to these is detectable.

| Hash (16) | Bytes | Path |
| :--- | --: | :--- |
| `8551624BAD06356D` | 1 525 | `.agents/skills/actuarial-risk-modeling/SKILL.md` |
| `D2D42377234465CC` | 1 723 | `.agents/skills/adr-authoring/SKILL.md` |
| `EEF4B6325CC357B0` | 1 760 | `.agents/skills/database-engineering/SKILL.md` |
| `B330B27A6331225F` | 1 520 | `.agents/skills/doubt-driven-development/SKILL.md` |
| `1A5BB1AEE037501B` | 6 839 | `.agents/skills/financial-data-integrity/SKILL.md` |
| `A43C8F76BF6B68C3` | 7 976 | `.agents/skills/iranian-payroll-engineering/SKILL.md` |
| `1DDF0161BF0355BD` | 7 267 | `.agents/skills/persian-rtl-engineering/SKILL.md` |
| `8ECC4521FB2C82E4` | 1 650 | `.agents/skills/product-discovery/SKILL.md` |
| `7303DFC9953DBFF8` | 1 970 | `.agents/skills/security-threat-model/SKILL.md` |
| `E39FAAD6A8FAC176` | 1 547 | `.agents/skills/software-architecture/SKILL.md` |
| `82DB08D18069F6BC` | 1 536 | `.agents/skills/spec-driven-development/SKILL.md` |
| `A3D153F67099DD5A` | 114 | `.freebuff/.gitignore` |
| `1DE92128CBCAA95D` | 37 | `.freebuff/project-id` |
| `110B010C237E3C9E` | 64 784 | `1.docx` |
| `CA16C4558D29A81A` | 3 166 | `backend/data/seeds/statutory_rules_1404.yaml` |
| `1F357DEE4DCB48A3` | 2 835 | `backend/data/seeds/statutory_rules_1405.yaml` |
| `19BB7E213CDB8A67` | 3 992 | `docs/adr/ADR-001-frontend-architecture-react-vite-spa.md` |
| `DC8124FC2BD7F741` | 3 583 | `docs/adr/ADR-002-object-storage-worm-ceph-s3-governance.md` |
| `3BF4EF167FE659ED` | 3 424 | `docs/adr/ADR-003-sensitive-data-encryption-alee-blind-indexing.md` |
| `59C757B0FDF8F6F3` | 3 819 | `docs/adr/ADR-004-phase-1-product-boundary-prehire-scope.md` |
| `EE4E658A35EB2915` | 17 894 | `docs/adr/ADR-005-async-execution-strategy.md` |
| `5A4BA85DA3A8C4AB` | 8 498 | `docs/ADR_INDEX.md` |
| `3410A72F9B1D6899` | 39 325 | `docs/DECISIONS_REGISTER.md` |
| `6DA56718E0AE1114` | 16 608 | `docs/DOCUMENTATION_INDEX.md` |
| `6AA1A119F4AB3A7A` | 25 838 | `docs/EXECUTION_DOCUMENTATION_AUDIT.md` |
| `90FA8E5702C1895F` | 73 022 | `docs/EXECUTION_PLAN.md` |
| `9E866F7DB5DD69F5` | 17 831 | `docs/IMPLEMENTATION_READINESS.md` |
| `AECE27677E9412E4` | 357 002 | `docs/PISH_HESABDARI_HOLY_BIBLE.md` |
| `DF67B35D7C10E455` | 27 651 | `docs/specs/AUTH.md` |
| `152259B9818ABC10` | 31 089 | `docs/specs/DEPLOYMENT.md` |
| `423A32643741666F` | 31 747 | `docs/specs/DOCUMENT_FORENSICS.md` |
| `7C91BE40D8D7A21D` | 25 400 | `docs/specs/FRONTEND_PERSIAN.md` |
| `542C9E58A5752CFF` | 25 591 | `docs/specs/STATUTORY_INGESTION.md` |
| `6B24DA5A9DB22856` | 30 627 | `docs/specs/TESTING.md` |
| `6170F1326A00D949` | 37 582 | `PHASE_1_FINAL_AUDIT_BRIEF.md` |
| `635F7869AE275C12` | 48 622 | `PHASE_1_RED_TEAM_AUDIT.md` |
| `23036D673F3446B8` | 31 625 | `REMEDIATED_TECHNICAL_SPECIFICATION_V2.md` |
| `CD0E60BFFAD608FC` | 129 854 | `RESEARCH_GAP_ANALYSIS_AND_ADVANCED_SPECIFICATION.md` |
| `9FBFB865F4605547` | 72 755 | `Technical Investigation of Related Software Projects.docx` |
| `75FE86DBCC5D9F16` | 102 616 | `گزارش جامع پژوهشی.docx` |

> **The 1404 seed hash `CA16C4558D29A81AE3123FBAB63732F130CC4425BF67617932C41B045FABE821` (full) is recorded here for the first time.** Invariant `R-10` requires it to be pinned in CI; there is no CI yet, so the pin is currently recorded here only. → `P0-T19`.

---

## 3. Change record

### 3.1 Infrastructure

| # | Action | Command | Result | Class | Rollback |
| --: | :--- | :--- | :--- | :--: | :--- |
| C-01 | Initialise the Git repository on `main` | `git init -b main` | **PASS** — `Initialized empty Git repository in C:/project/New project/.git/`; `git branch --show-current` → `main` | Reversible | `Remove-Item -Recurse -Force .git` |
| C-02 | Confirm **no** commit was created | `git rev-list --count HEAD` | **PASS** — no `HEAD` revision; 0 commits | n/a | n/a |
| C-03 | Confirm **no** remote is configured | `git remote -v` | **PASS** — empty | n/a | n/a |
| C-04 | Configure `core.quotepath=false` so Persian filenames are readable in Git output | `git config core.quotepath false` | **PASS** | Local repo config | `git config --unset core.quotepath` |
| C-05 | Set `core.autocrlf=false` — line endings are governed by `.gitattributes`, not by the platform | `git config core.autocrlf false` | **PASS** | Local repo config | `git config --unset core.autocrlf` |

### 3.2 Files created — repository hygiene

| # | Path | Purpose | Verification | Result |
| --: | :--- | :--- | :--- | :--: |
| C-06 | `.gitignore` | Exclude secrets, local databases, venvs, build outputs, uploads, session state; **explicitly keep** the seeds, `docs/` and `uv.lock` | `git ls-files --others --exclude-standard` → 46 tracked; `git ls-files --others --ignored --exclude-standard` → exactly 2 (`.freebuff/project-id`, `.freebuff/.gitignore`) | **PASS** |
| C-07 | `.gitattributes` | LF for source, CRLF for `.bat`/`.cmd`/`.ps1`; text/binary classification (`.docx`, fonts, models as binary) | Content review against `SPEC-OPS-001` §2.6 | **PASS** |
| C-08 | `.editorconfig` | UTF-8, LF, final newline, per-language indent | Content review | **PASS** |

> **Note on the `check-ignore` false positive.** `git check-ignore -v` exits 0 and prints the matching pattern even when that pattern is a **negation** (`!`). It was therefore *not* a valid test of whether a path is ignored. The authoritative test used everywhere in this changelog is `git ls-files --others --exclude-standard` versus `--ignored --exclude-standard`.

### 3.3 Files created — backend tooling (`WBS P0-T01`, partial)

| # | Path | Purpose | Verification | Result |
| --: | :--- | :--- | :--- | :--: |
| C-09 | `backend/pyproject.toml` | PEP 621 project, `requires-python = ">=3.12,<3.14"`, runtime dependencies limited to the approved technology inventory, `dev` dependency group for the QA toolchain, `documents`/`pdf` optional groups for later phases | `python -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))"` | **PASS** |
| C-10 | `backend/ruff.toml` | Lint + format configuration; the money rule is deliberately left to the AST gate in `TESTING.md` §3.1 | `tomllib` parse | **PASS** |
| C-11 | `backend/mypy.ini` | `strict = True`; `disallow_any_explicit` in `app.engines.*` | `configparser` parse; 9 sections read | **PASS** |
| C-12 | `backend/.env.example` | **Keys only, no values.** Every name and class taken from the `SPEC-OPS-001` §5.1 matrix; secret-class variables left empty | Manual diff against the matrix; `git ls-files` confirms it is tracked while `backend/.env` is ignored | **PASS** |
| C-13 | `backend/uv.lock` | The committed, exact dependency pin | `uv lock` → `Resolved 166 packages in 10.01s`; `uv lock --check` → `Resolved 166 packages in 1ms` (lock is current) | **PASS** |

**Resolved versions (from `uv.lock`):** fastapi 0.162.7 · pydantic 2.14.3 · sqlalchemy 2.1.8 · alembic 1.20.1 · asyncpg 0.32.0 · boto3 1.44.3 · cryptography 45.0.7 · argon2-cffi 25.1.0 · numpy 2.5.4 · scipy 1.18.1 · persiantools 6.2.0 · jdatetime 5.3.0 · uvicorn 0.54.0 · pyyaml 6.0.3 · pytest 8.4.2 · hypothesis 6.170.15 · schemathesis 3.39.16 · ruff 0.17.5 · mypy 1.20.2. All satisfy the minimums in `REMEDIATED` §3.1.

### 3.4 Files created — control documents

| # | Path | Purpose | Verification |
| --: | :--- | :--- | :--: |
| C-14 | `README.md` | Project entry point; points at the Holy Bible rather than restating it | Content review |
| C-15 | `AGENTS.md` | Global agent operating rules; the non-negotiable invariants; the change-control table; the escalation path | Content review |
| C-16 | `docs/ENVIRONMENT_INVENTORY.md` | The verified environment inventory, with a clear separation between installed-and-working, available-but-unconfigured, not-installed and unknown | Every row produced by executing the tool |
| C-17 | `docs/PROJECT_STATUS.md` | The verified current state, the Phase 0 startable/gated split, and the reconciliation against the Holy Bible | Content review |
| C-18 | `docs/AGENT_OPERATING_MODEL.md` | The eight logical roles, the delegation protocol, the file-ownership partition, the isolation mechanism, and the honest statement that no Antigravity runtime is present | Content review |
| C-19 | `docs/PHASE_0_BOOTSTRAP_PLAN.md` | The Phase 0 sequence, the local service architecture, the CI design, the financial/legal protection workstream, the defect-to-test mapping | Content review |
| C-20 | `docs/DECISION_REQUIRED_FROM_OWNER.md` | The owner-decision queue, with the consequences of each option | Content review |
| C-21 | `docs/BOOTSTRAP_CHANGELOG.md` | This file | — |

### 3.5 Files created — empty-directory preservation

| # | Path | Purpose | Verification |
| --: | :--- | :--- | :--: |
| C-22 | `.gitkeep` × 9 in `backend/app/`, `backend/app/api/`, `backend/app/api/v1/`, `backend/app/core/`, `backend/app/engines/`, `backend/app/models/`, `backend/app/schemas/`, `backend/app/services/`, `backend/tests/` | Preserve the pre-existing empty package skeleton across the first commit — Git does not track empty directories | `git ls-files --others --exclude-standard` lists them |

---

## 4. Verification results — the full log

### 4.1 PASS

| # | Command | Result |
| --: | :--- | :--- |
| V-01 | `git init -b main` | Repository initialised on `main` |
| V-02 | `git branch --show-current` | `main` |
| V-03 | `git rev-list --count HEAD` | No revision — 0 commits |
| V-04 | `git ls-files --others --exclude-standard` | 46 files would be tracked **at the moment of `git init`**; **63** in the final state (after the 16 control files and 9 `.gitkeep` files were added) |
| V-05 | `git ls-files --others --ignored --exclude-standard` | Exactly 2 files ignored (`.freebuff/project-id`, `.freebuff/.gitignore`) — unchanged in the final state |
| V-06 | `git check-ignore` on 6 candidate paths | The `backend/.env`, `backend/.venv/pyvenv.cfg`, `node_modules/x`, `__pycache__/x.pyc`, `secret.pem` and `frontend/dist/index.html` probes are all ignored |
| V-07 | `python -c "import tomllib; …"` on `pyproject.toml` and `ruff.toml` | Both parse |
| V-08 | `python -c "import configparser; …"` on `mypy.ini` | Parses; 9 sections |
| V-09 | `uv lock` | `Resolved 166 packages in 10.01s`; `backend/uv.lock` written (488 658 bytes) |
| V-10 | `uv lock --check` | `Resolved 166 packages in 1ms` — the lockfile is current |
| V-11 | `Test-Path backend/.venv` after `uv lock` | **False** — no virtual environment was created; nothing was installed |
| V-12 | `uv python find 3.12` | `…\uv\python\cpython-3.12.9-windows-x86_64-none\python.exe` — the spec's runtime is present |
| V-13 | `git worktree list` in a scratch repository | The worktree mechanism is available |
| V-14 | ADR status extraction over `docs/adr/*.md` | ADR-001…004 = `Accepted`; ADR-005 = `**PROPOSED**` |
| V-15 | Phase 0 WBS extraction from `docs/EXECUTION_PLAN.md` | 20 tasks, all `NOT_STARTED`, with the expected roles, effort and blockers |
| V-16 | Exhaustive recursive file and directory listing | 40 files, 29 directories, 0 source files, 0 secret-like files |
| V-17 | `Get-FileHash` over all 40 pre-existing files | The baseline in §2 |

### 4.2 FAIL / NOT AVAILABLE — recorded, not worked around

| # | Check | Result | Consequence |
| --: | :--- | :--- | :--- |
| N-01 | `docker info` | **FAIL** — `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine` | The Docker daemon is down. No container can start. `P0-T03`, `P0-T11`, `P0-T16`, `P0-T17` cannot be exercised locally. |
| N-02 | `wsl --status` | **PASS** — default version 2, distro `docker-desktop` | The backend is present but idle. |
| N-03 | `psql --version` | **NOT INSTALLED** | PostgreSQL is reachable only through a container. No host client. |
| N-04 | `pnpm --version` | **NOT INSTALLED** (corepack 0.35.0 is present) | The spec-mandated frontend package manager needs `corepack enable pnpm` → DEC-C. |
| N-05 | `make`, `jq`, `rg`, `pipx`, `yarn`, `podman`, `gemini`, `aider`, `cursor` | **NOT INSTALLED** | No impact; each has a documented workaround. |
| N-06 | `claude --version` / `codex --version` | **PASS** (2.1.300 / 0.169.0) but **NOT EXERCISED** against this repository | Not usable as delegation targets until the five preconditions in `docs/AGENT_OPERATING_MODEL.md` §5 are met. |
| N-07 | Antigravity CLI / service / API endpoint | **NOT PRESENT** | The brief's preferred orchestration surface is absent. The Freebuff tooling is the closest equivalent. → DEC-D |
| N-08 | `uv sync` (install ~166 packages, create `backend/.venv`) | **NOT RUN** — requires owner approval | `P0-T01` cannot be marked `COMPLETED`; its acceptance criteria are unverified. → DEC-A |
| N-09 | `git add` / `git commit` / `git push` | **NOT RUN** — explicitly out of scope | The working tree is untracked; the audit trail for this session is this file. → DEC-B |
| N-10 | `corepack enable pnpm` | **NOT RUN** — modifies the global Node install | Frontend setup is Phase 3. → DEC-C |
| N-11 | `ruff check`, `mypy`, `pytest` | **NOT RUN** — the tools are not installed in this environment | No static-analysis or test result is claimed anywhere in this session. |
| N-12 | `docker compose up` (PostgreSQL 16 + object store) | **NOT RUN** — the daemon is down | No database or object-store verification was possible. |
| N-13 | Migration execution (`alembic upgrade head`) | **NOT RUN** — no migration exists | Deliberate: production migrations encoding unresolved schema decisions are not permitted. |
| N-14 | Any statutory-engine or calculation code | **NOT WRITTEN** — deliberately | The active 1404 seed carries a known Eydi defect (HB-GAP-005) and the published worked example is defective. Writing engine code before those are resolved would embed a defect. |

---

## 5. Final verification sweep (end of session)

| # | Check | Result |
| --: | :--- | :--- |
| F-01 | Re-hash all 40 pre-existing files against the §2 baseline | **PASS** — 40/40 byte-identical. (One path in the first sweep reported "MISSING" purely because the Persian filename could not be encoded in the PowerShell literal; a direct hash confirmed `75FE86DBCC5D9F16`, unchanged.) |
| F-02 | All 16 control files present and non-empty | **PASS** — 16/16 present |
| F-03 | 9 `.gitkeep` files present in the empty skeleton | **PASS** — 9/9 |
| F-04 | Git: branch, commits, remotes, staged files | **PASS** — `main`; 0 commits; no remote; 0 staged |
| F-05 | Git: files that would be tracked / ignored | **PASS** — 63 tracked; exactly 2 ignored |
| F-06 | Secret audit of every created file | **PASS** — 36 keyword occurrences, **all variable names or prose**; **0 secret variables carry a value** (`DATABASE_URL`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`, `VAULT_TOKEN`, `VAULT_ROLE_ID`, `BLIND_INDEX_PEPPER`, `MASTER_KEK` are all empty) |
| F-07 | `backend/.env.example` parsed against the `SPEC-OPS-001` §5.1 matrix | **PASS** — every name present; secret-class variables empty |
| F-08 | TOML / INI parse | **PASS** — `pyproject.toml`, `ruff.toml`, `mypy.ini` (9 sections) |
| F-09 | `uv lock --check` | **PASS** — `Resolved 166 packages in 1ms`; the lockfile is current |
| F-10 | No `.venv` created | **PASS** — nothing was installed |
| F-11 | **1404 seed unchanged** | **PASS** — SHA-256 `CA16C4558D29A81AE3123FBAB63732F130CC4425BF67617932C41B045FABE821`, identical to the baseline |
| F-12 | **1405 seed remains inert** | **PASS** — `is_verified_and_active: false`, **16 null-valued parameters**, no flat-10 % Eydi rule |
| F-13 | Prohibited-state audit | **PASS** — no commit, no remote, no `.venv`, no migration, no `frontend/`, no `infra/`, no `.github/` |
| F-14 | Accepted ADRs unmodified | **PASS** — ADR-001…004 hashes identical to the baseline; ADR-005 still `PROPOSED` |

---

## 6. Explicitly NOT done, and why

| Action | Why not |
| :--- | :--- |
| Modify `docs/adr/ADR-001`…`ADR-004` | Accepted ADRs are immutable without a superseding ADR. |
| Modify `backend/data/seeds/statutory_rules_1404.yaml` | An immutable legal artefact, hash-pinned by `R-10`. |
| Modify `backend/data/seeds/statutory_rules_1405.yaml` | It must stay inert until A1–A8 are met. |
| Activate the 1405 rule set | Four-eyes verification has not happened. |
| Approve ADR-005 | Only the owner may. It remains `PROPOSED`. |
| Write production migrations | They would encode unresolved schema decisions (DEC-005). |
| Write calculation-engine code | The active seed carries a known Eydi defect; the published example is defective. |
| Create a production schema for identity | DEC-004 is open. |
| Commit or push | Explicitly out of scope; owner approval required (DEC-B). |
| Install packages or modify the global Node/Python | Not required for this session's deliverables (DEC-A, DEC-C). |
| Delete or rewrite any historical document | Prohibited. The full 40-file corpus is preserved byte-identical. |
| Change the five-phase, 20-week roadmap | Prohibited. |

---

## 7. Rollback instructions

| To undo | Run |
| :--- | :--- |
| The whole session's infrastructure | `Remove-Item -Recurse -Force .git` — restores the pre-session state exactly; no tracked file is affected |
| The generated lockfile | `Remove-Item backend\uv.lock` |
| All 16 created files | Delete them individually; they are listed in §3.2–§3.5 and are all new paths with no pre-existing content |
| The local Git config | `git config --unset core.quotepath` · `git config --unset core.autocrlf` |

**No rollback step requires restoring an original file** — every pre-existing file is byte-identical to its §2 baseline.

---

## 8. Next session

1. Read `docs/DECISION_REQUIRED_FROM_OWNER.md` and obtain DEC-A, DEC-B and DEC-I.
2. `uv sync --frozen --all-groups` → verify `ruff check .`, `mypy app` and `pytest -q`.
3. Execute `P0-T02` (FastAPI skeleton) — the first task with no decision dependency.
4. Start Docker Desktop and execute `P0-T03` (PostgreSQL 16 provisioning).
5. Commission the Certified Tax Accountant and the Labour Counsel (**DEC-E**) — the two longest-lead items in the project.

---

## 9. Session 2 — the first executable Phase 0 tasks

- **Session 2:** 2026-11-14 (23 Aban 1405 SH) — `P0-T01` (partial) and `P0-T02`
- **Scope decided by the owner:** `P0-T01` close + `P0-T02` FastAPI skeleton. The crypto wave (`P0-T06`/`T08`/`T07`/`T15`) was **not** started.
- **Related:** `docs/PROJECT_STATUS.md` · `docs/DECISION_REQUIRED_FROM_OWNER.md` · `docs/PHASE_0_BOOTSTRAP_PLAN.md`

### 9.1 Owner decisions obtained before any action

| Decision | Answer | Effect |
| :--- | :--- | :--- |
| **DEC-A** | Install the resolved dependency set — **yes** | `uv sync --frozen --all-groups` run; `backend/.venv` created (118 packages) |
| **DEC-B** | Make the first commit — **yes**, on `bootstrap/initial-import`, then merge | The audit trail now exists; worktrees and CI are unblocked |
| **DEC-G** | Repository licence — **proprietary, all rights reserved** | `LICENSE` written and committed |
| Scope | `P0-T01` + `P0-T02` only | The crypto wave stays unstarted |

**DEC-I (DEC-004 / DEC-004a / DEC-004b / DEC-005) was not answered and was not assumed.** No table, key hierarchy, session strategy or ERD was chosen.

### 9.2 Infrastructure and dependency actions

| # | Action | Command | Result | Class |
| --: | :--- | :--- | :--- | :--- |
| C-23 | Install the pinned dependency set | `uv sync --frozen --all-groups` | **PASS** — `Checked 118 packages in 8ms`, exit 0; `backend/.venv` created | Reversible (`Remove-Item -Recurse -Force backend\.venv`) |
| C-24 | Confirm the runtime interpreter | `uv run python -c "import sys; print(sys.version)"` | **PASS** — CPython **3.12.9**, the `python:3.12-slim` production baseline | n/a |
| C-25 | Confirm the resolved framework versions | `uv run python -c "import fastapi, pydantic, pydantic_settings"` | **PASS** — fastapi 0.162.7, pydantic 2.14.3 | n/a |
| C-26 | Create the reviewable branch | `git switch -c bootstrap/initial-import` | **PASS** | Reversible |
| C-27 | Stage the corpus | `git add -A` | **PASS** — 72 files staged, 0 secrets | Reversible (`git reset`) |
| C-28 | Commit the corpus | `git commit` | **PASS** — see §9.7 | **Permanent** — first shared history |
| C-29 | Create `main` from the reviewed branch | `git branch main bootstrap/initial-import` → `git switch main` | **PASS** — both refs now point at `2fc2b6f`. **A `--no-ff` merge was not possible:** `main` had never existed as a ref (the repository was initialised with `-b main` but the first commit landed on the new branch), so there was no second parent to merge. `main` therefore points at the reviewed commit directly, and the branch is kept for review | Reversible (`git branch -D bootstrap/initial-import`) |

### 9.3 Defects found and fixed in this session

Three of these were latent defects in the **session-1** configuration files. They were invisible to `tomllib`/`configparser`, which validate syntax, not the schema of the tool that consumes the file. **A configuration file is not verified until the tool that reads it has read it.**

| # | Defect | Detection | Fix |
| --: | :--- | :--- | :--- |
| D-01 | `backend/ruff.toml` — `banned-api = ["round"]` is **invalid** for ruff 0.17.5, which requires a map. `ruff check .` aborted with `invalid type: sequence, expected a map` and exit 2 | `uv run ruff check .` | Rewritten as `[lint.flake8-tidy-imports.banned-api]` with a `msg`. The comment was also corrected: TID251 flags *imports* of a banned API, not calls to `round()` — the AST gate remains the authoritative money-safety ban |
| D-02 | `backend/mypy.ini` — `plugins = ["pydantic.mypy"]` uses TOML list syntax in an INI file; mypy aborted with `No module named '["pydantic'` and exit 2 | `uv run mypy app` | Changed to the INI form `plugins = pydantic.mypy` |
| D-03 | A **bearer token passed as a format argument leaked into the log**. The filter redacted `record.msg` and `record.args` separately, so `"Bearer %s"` and the token were never seen together | `pytest` — `test_no_secret_reaches_a_log_line` failed | The filter now redacts an argument **wholesale** when the format string names a credential (`bearer`, `authorization`, `token`, `password`, `secret`, `credential`, …). A JWT is also matched by shape, so it is removed even without a keyword |
| D-04 | The **correlation id was logged as `-`** — the contextvar was reset before the request line was written | `pytest` — `test_the_request_id_is_echoed_and_carried_into_the_log` failed | The request line is now emitted **inside** the `try`, before the `finally` that resets the binding |
| D-05 | The filter **reshaped `record.args`**, which broke uvicorn's own access-log formatter (`TypeError: cannot unpack non-iterable NoneType object`) — a log record is shared with every handler in the chain, and each formatter has its own contract for `args` | **Live server**, not the test client — `uvicorn app.main:app` produced `--- Logging error ---` on every request | The filter now preserves the **shape** of `args` exactly (tuple length, mapping keys). The uvicorn loggers also had their default plain-text handlers removed, so there is now one JSON stream and no duplicate copy that bypasses redaction |
| D-06 | `backend/app/.gitkeep`, `backend/app/core/.gitkeep`, `backend/tests/.gitkeep` were redundant once the packages had content | Directory review | Deleted. Six `.gitkeep` files remain, in the directories that are still empty |
| D-07 | **A process defect, not a product defect.** The documentation was edited with Python's text mode, which translates newlines on *both* read and write: a CRLF file was read as LF and written back as CRLF. Six files were silently converted — including `docs/EXECUTION_PLAN.md`, one of the 40 pre-existing corpus files | The end-of-session hash sweep: **39/40 identical, 1 changed** — the one change being the WBS status rows I had deliberately edited | All six files restored to LF. The change was verified by reverting only the two intended WBS rows and re-hashing: the result is the baseline `90FA8E5702C1895F`, **exactly**. `git diff` shows no content change, because `.gitattributes` normalises to LF on add — the committed blobs were always correct; only the working tree had drifted. **Lesson: on Windows, never edit a file through a text-mode round-trip. Read and write bytes.** |

### 9.4 Files created — `P0-T02`

| # | Path | Purpose |
| --: | :--- | :--- |
| C-30 | `backend/app/__init__.py`, `backend/app/core/__init__.py` | Package markers, each naming its authority |
| C-31 | `backend/app/core/config.py` | `Settings` — one field per §5.1 matrix variable; secret-class variables are `SecretStr`; `ConfigurationError` for every fail-closed breach |
| C-32 | `backend/app/core/logging.py` | `SecretRedactingFilter`, `JsonFormatter`, `ApplicationHandler`, `configure_logging`, the correlation-id contextvar |
| C-33 | `backend/app/main.py` | `create_app()`, the `X-Request-Id` middleware, `GET /health/live` |
| C-34 | `backend/tests/__init__.py`, `backend/tests/unit/__init__.py`, `backend/tests/api/__init__.py` | Test package markers |
| C-35 | `backend/tests/unit/test_config.py` | 14 tests — the matrix, the secret/public split, the production policy, the 1405 guard, the object-lock guard |
| C-36 | `backend/tests/unit/test_logging.py` | 11 tests — the redaction rules and the CR-13 property |
| C-37 | `backend/tests/api/test_health.py` | 6 tests — the liveness probe, the correlation id, the startup log, the `APP_DEBUG` behaviour |
| C-38 | `LICENSE` | Proprietary — all rights reserved (DEC-G) |
| C-39 | `backend/pyproject.toml` §`[tool.pytest.ini_options]` | The pytest harness: `testpaths`, `pythonpath`, strict markers, `asyncio_mode = "auto"` |
| C-40 | `.gitignore` | `package-lock.json` and `npm-shrinkwrap.json` rejected — the spec mandates `pnpm-lock.yaml` (`SPEC-OPS-001` §2.4) |

### 9.5 Verification results

#### PASS

| # | Command | Result |
| --: | :--- | :--- |
| V-18 | `uv sync --frozen --all-groups` | `Checked 118 packages in 8ms`; exit 0 |
| V-19 | `uv run ruff check .` | `All checks passed!`; exit 0 |
| V-20 | `uv run ruff format --check .` | `11 files already formatted`; exit 0 |
| V-21 | `uv run mypy app` | `Success: no issues found in 5 source files`; exit 0 |
| V-22 | `uv run mypy app tests` | `Success: no issues found in 11 source files`; exit 0 |
| V-23 | `uv run pytest -q` | `34 passed`; exit 0 |
| V-24 | `uv run uvicorn app.main:app --host 127.0.0.1 --port 8124` + `GET /health/live` | **PASS** — `STATUS=200`, `BODY={"status":"alive"}`, `Content-Type: application/json`, `X-Request-Id` echoed |
| V-25 | The live server's log stream | **PASS** — one JSON object per line, **0** `--- Logging error ---`, the correlation id carried into every application line |
| V-26 | `uv lock --check` | `Resolved 166 packages` — the lockfile is still current after the `pyproject.toml` change |
| V-27 | Re-hash of all 40 pre-existing files against the §2 baseline | **PASS** — 39/40 byte-identical. The 40th, `docs/EXECUTION_PLAN.md`, differs **only** in the two WBS status rows: reverting those two rows and re-hashing returns the baseline `90FA8E5702C1895F` exactly (see D-07) |
| V-31 | Line-ending audit of every file touched in session 2 | **PASS** — all LF, matching `.gitattributes` (`* text=auto eol=lf`) and `.editorconfig`. `git diff` reports no content change for the six restored files |
| V-32 | Secret scan over the 72 staged blobs | **PASS** — 30 matches, **all** false positives: type declarations, empty `SecretStr("")` defaults, specification pseudo-code, and synthetic fixtures explicitly named `FAKE_*`. **No live secret, National Code, mobile number, Sheba number or salary is committed** |
| V-28 | 1404 seed SHA-256 | **PASS** — `CA16C4558D29A81AE3123FBAB63732F130CC4425BF67617932C41B045FABE821`, identical to the pin |
| V-29 | 1405 seed | **PASS** — `is_verified_and_active: false`, 16 null-valued parameters, inert |
| V-30 | `git ls-files --others --exclude-standard` | 72 files to track; `backend/.venv`, `__pycache__`, the tool caches and `.freebuff/*` all ignored |

#### FAIL — found, diagnosed, fixed, re-verified

| # | Command | Failure | Outcome |
| --: | :--- | :--- | :--- |
| F-01 | `uv run ruff check .` (first run) | exit 2 — invalid `ruff.toml` schema | **Fixed (D-01)**, now exit 0 |
| F-02 | `uv run mypy app` (first run) | exit 2 — invalid plugin syntax | **Fixed (D-02)**, now exit 0 |
| F-03 | `uv run pytest -q` (first run) | 3 failed — a bearer token leaked, the correlation id was `-`, and a test asserted an undetectable guarantee | **Fixed (D-03, D-04) and the test corrected**; now 34 passed |
| F-04 | The live server (first run) | `--- Logging error ---` on every request — `record.args` was reshaped | **Fixed (D-05)**; now 0 logging errors |

#### NOT RUN — deliberately

| # | Action | Why not |
| --: | :--- | :--- |
| N-15 | `git push` | No remote is configured, and the owner has not created one. **Never pushed.** |
| N-16 | `docker compose up` | The Docker daemon is still down. `P0-T03`, `P0-T11`, `P0-T16`, `P0-T17` remain unexercised |
| N-17 | `alembic upgrade head` | No migration exists; writing one would encode unresolved schema decisions (DEC-005) |
| N-18 | Any statutory-engine or calculation code | The active 1404 seed carries the Eydi defect (HB-GAP-005) and the published worked example is defective |
| N-19 | `corepack enable pnpm` | DEC-C is still open. The lockfile protection was added to `.gitignore`; the package manager was **not** provisioned |
| N-20 | CI configuration | DEC-F (provider and remote) is still open. **This is the one unmet clause of `P0-T01`.** |
| N-21 | `git worktree add` | The mechanism is now unblocked by the first commit, but no worktree was created — no parallel agent was assigned a task in this session |

### 9.6 What the redaction filter can and cannot do

The honest boundary, recorded so that no one over-claims CR-13:

| Case | Result |
| :--- | :--- |
| A secret named by a **key** (`extra={"database_url": …}`) | **Removed** |
| A **URL credential** (`scheme://user:password@host`) | **Removed**; the user and host remain readable |
| A **bearer token** introduced by the format string | **Removed** — the argument is replaced wholesale |
| A **JWT** anywhere in the line | **Removed** by shape |
| A **National Code**, **mobile number** or **Sheba** | **Removed** |
| A traceback containing any of the above | **Removed** |
| An unlabelled random string (`"the value is hunter2"`) | **Not removable.** No pattern matches it. The protection is that a secret is never interpolated into a message in the first place |

### 9.7 The commit

Recorded after the fact; the hashes are those produced by the commands in §9.2.

| Item | Value |
| :--- | :--- |
| Commit | `2fc2b6f998861c6af04f0f3668d925bf139350ba` — "chore: bootstrap the Pish Hesabdari repository (P0-T01 partial, P0-T02 complete)" |
| Files committed | **72** — the full corpus, the licence and the first application source |
| Branches | `bootstrap/initial-import` and `main` both point at `2fc2b6f`. `main` did not previously exist as a ref, so there was no merge commit to make — see C-29 |
| Remote | **none** — nothing was pushed |
| Rollback | `git reset --hard 2fc2b6f^` restores the pre-commit tree; `git branch -D bootstrap/initial-import` removes the review branch; `git reflog` lists every ref movement |

### 9.8 Explicitly NOT done, and why

| Action | Why not |
| :--- | :--- |
| Modify `docs/adr/ADR-001`…`ADR-004` | Accepted ADRs are immutable without a superseding ADR |
| Modify `backend/data/seeds/statutory_rules_1404.yaml` | An immutable legal artefact, hash-pinned by `R-10` |
| Modify `backend/data/seeds/statutory_rules_1405.yaml` | It must stay inert until A1–A8 are met |
| Activate the 1405 rule set | Four-eyes verification has not happened |
| Choose between opaque sessions and JWT (DEC-004) | Not answered. The schema was not written |
| Write the identity tables (DEC-005) | Not answered. No table was written |
| Write `GET /health/ready` | It must report on PostgreSQL, the rule set, the object store and the worker pool. **None of them exists.** A readiness probe that cannot fail is worse than none |
| Approve ADR-005 | Only the owner may; it remains `PROPOSED` |
| Start the crypto wave (`P0-T06`/`T07`/`T08`/`T15`) | Outside the scope the owner set for this session |
| Correct the Holy Bible §11.1 (DEC-H) | The owner did not answer DEC-H in this session. The statement remains as written |
| Push to a remote | No remote exists, and the owner did not authorise one |

---

*Append-only. Every subsequent session adds a new section; existing entries are never rewritten.*

---

## 10. Owner-authorized remediation and decision preparation — 2026-11-14

### 10.1 Authorization, ownership and limits

The owner explicitly approved environment investigation, dependency reinstall only if needed, logging/retention fixes, tests and documentation correction. They requested concrete technical proposals for later approval and confirmed no Certified Tax Accountant, Iranian Labour Counsel or licensed/consented datasets are available. External commissions/data stay `MISSING / BLOCKING`. No financial/legal value was inferred from their absence.

Accountable implementation owner: Codex `/root`, WBS `P0-T02` remediation and `P0-T01` environment verification. File ownership: `backend/app/core/{config,logging}.py`, related unit tests, a factual comment in `backend/pyproject.toml`, `AGENTS.md` and the derived control documents listed below. Existing six dirty documentation files were preserved; no reset/checkout was used. Acceptance: actual captured emission must redact nested sensitive fields, rendered sensitive assignments, error/stack text and Persian/Arabic identifier digits; production must reject any retention other than 3650 days; the original missing-secret gate must remain independently exercised. Approved authority: ADR-002 plus DEPLOYMENT §§5/7.2 and TESTING CR-13.

No dependencies were installed, no lockfile/seed/accepted ADR was changed, no migration or domain engine was written, no service was started, and no commit/push was performed. No WBS task or open architecture decision was marked complete/resolved by this remediation. DEC-H alone is resolved by the owner's authorization to make factual documentation corrections.

### 10.2 Corrected environment diagnosis

The previous audit reported that Python was absent because `backend/.venv/Scripts/python.exe` returned `No Python at ...` in the sandbox. A direct probe of its configured base interpreter returned `Access is denied`; the same baseline test command with the required filesystem access then returned **34 passed**. The previous missing-interpreter diagnosis is withdrawn. No environment repair/reinstall was necessary. This also corrects TA-03: the blocker was restricted access, not a demonstrated damaged environment.

### 10.3 Changes and verification scope

| Files | Change | Evidence / disposition |
| :--- | :--- | :--- |
| `backend/app/core/config.py`; `backend/tests/unit/test_config.py` | Positive retention everywhere; exactly 3650 days in production; all eight missing-secret cases tested with otherwise valid TLS/retention | `IMPLEMENTED` and verified by suite below. Actual bucket locking remains `NOT RUN` |
| `backend/app/core/logging.py`; `backend/tests/unit/test_logging.py` | Recursive copies of mappings/lists/tuples; cycle/depth limits; unknown objects masked without repr; credential/PII templates and sensitive assignments conservatively masked; cached exception/stack text scrubbed; Persian/Arabic digits matched without rewriting unrelated text | `IMPLEMENTED`; actual logger/filter/formatter/stdout regressions pass. Caller-owned containers preserved; standard uvicorn positional argument shape retained |
| `backend/pyproject.toml` | Correct stale dependency-approval comment only | Dependency specifications and `uv.lock` unchanged |
| `AGENTS.md`; `docs/PISH_HESABDARI_HOLY_BIBLE.md`; `docs/{PROJECT_STATUS,IMPLEMENTATION_READINESS,ENVIRONMENT_INVENTORY,PHASE_0_BOOTSTRAP_PLAN}.md` | Correct obsolete no-code/no-Git claims and WBS counts; withdraw Python diagnosis; distinguish historical evidence from current state | 86 tasks: 1 `COMPLETED`, 1 `IN_PROGRESS`, 80 `NOT_STARTED`, 4 `BLOCKED`; no status changed |
| `docs/{DECISIONS_REGISTER,ADR_INDEX,DOCUMENTATION_INDEX,EXECUTION_DOCUMENTATION_AUDIT}.md`; proposed `docs/adr/ADR-005-async-execution-strategy.md` | Correct false Celery mandate; current spec/skill both name `BackgroundTasks`; real durability/isolation issue remains undecided. Clarify that a proposed rejection is not accepted | ADR-005 still `PROPOSED`; DEC-003 open. ADR-001…004 untouched |
| `docs/DECISIONS_REGISTER.md`; `docs/DECISION_REQUIRED_FROM_OWNER.md` | Correct dangling gate IDs `P0-T22` → `P0-T20`, `P2-T22` → `P2-T18`, as already documented by HB-GAP-048 | Factual reference correction; no new gate/task |
| `docs/EXECUTION_PLAN.md` | Record three unresolved dependencies on nonexistent `P4-T15` in §14.4 | `OPEN`; CTO/Product Manager must confirm intended predecessors. No inferred replacement, task-count or roadmap change |
| `docs/DECISION_REQUIRED_FROM_OWNER.md` | Four concrete owner-review proposals, reasons/trade-offs, formal change-control caveat for ADR-003; no people/data available; owner-queue counts corrected | DEC-004/004a/004b/005 all remain `OPEN`; no identity/schema implementation |
| `docs/AGENT_OPERATING_MODEL.md` | Record genuinely used Codex parent and read-only independent reviewer; distinguish earlier opencode inventory | No parallel file writers or new framework |

The original 16 findings in Holy Bible Appendix E.1 remain historical evidence. Current disposition: #1/#8/#9 numerical examples not independently recalculated in this session; #2 false attribution corrected but async decision open; #3–#7 seed defects/key drift unchanged and blocked from silent fixes; #10 authentication/activation approvals open; #11 Vault distribution/legal review pending; #12 cloud/air-gap conflict open; #13 contract-clause specification gap open; #14 partially obsolete because LICENSE/tooling/Git now exist, while business/CI/domain API gaps remain; #15 benchmark parameters open; #16 gate-ID references corrected, with the separate `P4-T15` defect newly recorded. This is not a legal verification or certification of any numerical example.

### 10.4 Independent security review

`/root/security_review` was actually spawned using the platform collaboration tool, as required by `AGENTS.md` §6. Scope was read-only: review current config/logging and regression tests against the source documents, not a summary. The reviewer read AGENTS, Holy Bible authority/security/governance sections, ADR-002/003, DEPLOYMENT §§5/7.2/9.3 and TESTING §9.

The reviewer found quoted-key exception/text bypasses, PII-labelled formatting gaps, nested sensitive-container text and Persian/Arabic digit gaps. The parent fixed them and added captured-emission regressions; the reviewer re-read the changes and returned **PASS — no remaining blocking finding in the modified paths**. They edited no files. **Reviewer runtime verification: NOT RUN.** Parent-run commands/results are below. The seven other logical engineering roles were not instantiated; no human legal/accounting specialist was substituted with an agent.

### 10.5 Commands and actual results

All Python checks ran from `backend/` using the existing venv and the required elevated filesystem access. Ruff/Git checks ran from the repository root. No install/upgrade command ran.

| Result | Exact command | Observed output |
| :--- | :--- | :--- |
| PASS — original baseline | `rtk proxy .\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider` | `34 passed, 2 warnings` |
| FAIL — before fixes, deliberately reproduced | `rtk proxy .\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider --tb=no tests/unit/test_config.py tests/unit/test_logging.py` | `15 failed, 30 passed, 1 warning`; both reported defects reproduced |
| PASS — final suite | `rtk proxy .\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider --tb=short` | `67 passed, 2 warnings in 1.20s`; exit 0 |
| PASS — lint | `rtk proxy .\backend\.venv\Scripts\ruff.exe check --no-cache backend` | `All checks passed!`; exit 0 |
| PASS — format | `rtk proxy .\backend\.venv\Scripts\ruff.exe format --check --no-cache backend` | `11 files already formatted`; exit 0 |
| PASS — strict types | `rtk proxy .\.venv\Scripts\python.exe -B -m mypy --no-incremental --cache-dir=.mypy_cache/codex-remediation app tests` | `Success: no issues found in 11 source files`; exit 0 |
| PASS — whitespace | `rtk git diff --check` | Empty output; exit 0 |
| PASS — protected artefacts | `rtk proxy git diff --exit-code HEAD -- docs/adr/ADR-001-frontend-architecture-react-vite-spa.md docs/adr/ADR-002-object-storage-worm-ceph-s3-governance.md docs/adr/ADR-003-sensitive-data-encryption-alee-blind-indexing.md docs/adr/ADR-004-phase-1-product-boundary-prehire-scope.md backend/data/seeds/statutory_rules_1404.yaml backend/data/seeds/statutory_rules_1405.yaml REMEDIATED_TECHNICAL_SPECIFICATION_V2.md backend/uv.lock` | Empty diff; exit 0 |

Intermediate failures are retained here: Ruff initially rejected one function's return count, two redundant comprehensions and formatting; corrected without disabling rules. Mypy with `--cache-dir=NUL` returned an internal error; using the project-local ignored cache then exposed test `**dict` typing and digit-map variance errors, which were corrected. Final formatting changed whitespace only after the passing test/type runs. The two remaining warnings come from Starlette's deprecated anyio alias and Schemathesis's deprecated jsonschema reference exception; no dependency upgrade was attempted.

The following inline PowerShell checks were also executed via `rtk proxy powershell -NoProfile -Command` (read-only; exact script body):

```powershell
$ErrorActionPreference='Stop'
$rows=@(Get-Content -Encoding UTF8 docs/EXECUTION_PLAN.md | Where-Object { $_ -match '^\| P[0-4]-T\d+ \|' })
"WBS_TOTAL="+$rows.Count
$rows | ForEach-Object { (($_ -split '\|')[-2]).Trim('*',' ') } | Group-Object | ForEach-Object { $_.Name+'='+$_.Count }
$protected=@('docs/adr/ADR-001-frontend-architecture-react-vite-spa.md','docs/adr/ADR-002-object-storage-worm-ceph-s3-governance.md','docs/adr/ADR-003-sensitive-data-encryption-alee-blind-indexing.md','docs/adr/ADR-004-phase-1-product-boundary-prehire-scope.md','backend/data/seeds/statutory_rules_1404.yaml','backend/data/seeds/statutory_rules_1405.yaml','REMEDIATED_TECHNICAL_SPECIFICATION_V2.md','backend/uv.lock')
& rtk proxy git diff --exit-code HEAD -- @protected
"PROTECTED_DIFF_EXIT="+$LASTEXITCODE
if($LASTEXITCODE -ne 0){throw 'Protected artefact changed'}
"LOCAL_LINKS:"
$md=@(Get-ChildItem -File -Filter *.md)+@(Get-ChildItem docs -Recurse -File -Filter *.md)
$total=0;$broken=0
foreach($file in $md){
 foreach($m in [regex]::Matches([IO.File]::ReadAllText($file.FullName),'\[[^\]]*\]\(([^)]+)\)')){
  $target=$m.Groups[1].Value.Trim('<','>')
  if($target -match '^(https?://|#|mailto:)'){continue}
  $target=($target -split '#')[0]
  if(-not $target){continue}
  $total++
  if($target -match '^file:'){$resolved=([Uri]$target).LocalPath}else{$resolved=Join-Path $file.DirectoryName ([Uri]::UnescapeDataString($target))}
  if(-not(Test-Path -LiteralPath $resolved)){$broken++;$file.Name+' -> '+$target}
 }
}
"LINKS_CHECKED=$total BROKEN=$broken"
```

Observed: `WBS_TOTAL=86`, `IN_PROGRESS=1`, `COMPLETED=1`, `NOT_STARTED=80`, `BLOCKED=4`, `PROTECTED_DIFF_EXIT=0`, `LINKS_CHECKED=83 BROKEN=0`. This checks file targets, not heading anchors or the portability of historical `file:` links. Three dangling `P4-T15` dependency mentions remain explicitly unresolved; they are not Markdown file links.

### 10.6 NOT RUN, residual boundaries and safe continuation

- `NOT RUN`: PostgreSQL/RLS, encryption/key-rotation, real WORM bucket tests, financial golden corpus, OCR corpus, deployment or production access. No readiness or financial correctness claim follows from the 67 bootstrap tests.
- `NOT RUN`: installation/reinstallation, `uv sync`, dependency upgrades, migration/seed edits, Git commit/push. Existing protected artefacts match HEAD.
- Unlabelled arbitrary sensitive strings cannot be discovered by pattern matching. Application callers must not log candidate payloads, names, salaries or secret values. Known sensitive assignments/templates are conservatively masked in full, so some diagnostic detail is intentionally lost. Unknown objects are masked rather than rendered.
- DEC-004/004a/004b/005 proposals await owner review and recorded approvers; ADR-005 remains `PROPOSED`. No production table, auth strategy or queue was selected. `P0-T01` still needs CI.
- The original first commit has no parent; historical rollback text using `2fc2b6f^` is not executable guidance. To undo remediation, preserve all uncommitted work and reverse only reviewed remediation hunks; never use a blanket reset/delete of Git history.

This section appends current corrections without rewriting the earlier session evidence.

---

## 11. Four owner decisions accepted; P0-T06 implementation — 2026-11-14

### 11.1 Authorization and formal decision record

The owner was asked whether all four previously prepared proposals (session/identity, privileged MFA, audit scope and schema corrections) were approved so dependent work could start. They answered **yes**. Accepted ADR-006 records that exact authorization and its boundaries. DEC-004/004a/004b/005 are now `RESOLVED`: four resolved, thirteen open register entries. ADR-005 stays `PROPOSED`; CI/provider, deployment, key-management variants, digest details, unapproved session timing, statutory activation and external data/legal dependencies are not silently approved.

ADR-006 supersedes only ADR-003 directive 3's index table target (`employees` → `candidates`) and overrides the specification's JWT label for the selected session mechanism. It does not edit the original accepted ADR files or source specification. Actual approver: **Project Owner in chat**. No named human CISO/CTO/DBA/legal sign-off is fabricated. This is not a legal certification, production authorization, commit or push approval.

### 11.2 Task, specification, ownership and dependency treatment

- Exact WBS: **P0-T06**, ALEE encryption module. Sole accountable implementation owner: Codex `/root`.
- Before coding, the accepted ADR-003 requirements, AUTH key sections, TESTING CR-01…03/13 and security skill were read; the specific verifiable contract was added to existing AUTH §8.5. The pinned library's [official AESGCM documentation](https://cryptography.io/en/45.0.7/hazmat/primitives/aead/#cryptography.hazmat.primitives.ciphers.aead.AESGCM) was checked. No new package or alternative crypto algorithm was introduced.
- Dependency P0-T01: installed toolchain is verified, but the **CI clause remains unmet**. This bounded partial dependency is explicit. Local primitive work does not complete P0-T01 or bypass its gate; P0-T06 is **READY_FOR_REVIEW**, not COMPLETED. Production registry, key custody/authorization/rotation and integration are separate P0-T08/P0-T15 evidence.
- File ownership: `backend/app/core/security/{__init__,pii_transformer}.py`, `backend/tests/unit/test_pii_transformer.py`; source contract `docs/specs/AUTH.md` §8.5; accepted `docs/adr/ADR-006-phase-0-owner-approved-security-and-schema.md`; associated status/register/index updates. There were no competing file writers.
- Actual WBS state change: P0-T06 `NOT_STARTED` → implementation/test/review work in this session → `READY_FOR_REVIEW`. No task was marked COMPLETED. Current census: 86 total = 1 COMPLETED, 1 IN_PROGRESS, 1 READY_FOR_REVIEW, 79 NOT_STARTED, 4 BLOCKED.

### 11.3 Implementation and measurable evidence

`PiiFieldTransformer` retrieves an explicit tenant/version **32-byte** key via a protocol and uses AES-256-GCM with a new CSPRNG 12-byte nonce and the full 16-byte tag. Stored bytes retain `nonce || ciphertext || tag`. Domain-separated canonical AAD binds tenant UUID, record UUID, schema field and explicit key reference. Text helpers preserve exact UTF-8, including Persian/ZWNJ; no monetary coercion, statutory value or normalization is introduced.

Keys are not generated/persisted/cached by this primitive, and no active/old-key fallback exists. Registry failures, authentication failures and nonce-source failures use fixed errors, suppressing sensitive underlying exception chains in rendered tracebacks. The transformer emits no logs. No production in-memory key registry is supplied; test stubs use explicitly synthetic material.

The **43 new regression cases** cover empty/binary/Persian round-trips; nonce/output variation; nonce/ciphertext/tag mutation; truncation; wrong tenant/record/field/key context **even with identical key bytes**; AES-128/192/wrong-size key rejection on encrypt/decrypt; missing-key failure/log/traceback confidentiality; no fallback; immutable non-revealing context; invalid metadata; non-UTF-8 decode failure; an independently spelled AAD interoperability check; successful sensitive-field calls emitting no output; and random-source failure without exception-data disclosure.

### 11.4 Independent review

The existing `/root/security_review` agent was resumed for an actual independent, read-only review required by AGENTS §6. It read ADR-006, AUTH §8.5, original ADR-003, TESTING CR-01…03/13 and the security skill, then inspected the primitive and tests. Final result: **PASS — no blocking findings**. The reviewer edited no files; no additional framework/worktree was installed. Parent ran/observed all runtime checks. Reviewer runtime verification: **NOT RUN**.

Review explicitly retained the boundaries: random-nonce lifetime/usage limits and production key custody, authorization and rotation are P0-T08 integration requirements. Local tests do not prove unlimited nonce uniqueness, memory zeroization, real database isolation, legal correctness or a passed phase gate.

### 11.5 Exact commands and observed results

Python checks ran from `backend/` through the existing interpreter with the required filesystem access. Ruff/Git checks ran from root. No install/lock update ran.

| Result | Command | Actual result |
| :--- | :--- | :--- |
| PASS — initial implementation suite | `rtk proxy .\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider --tb=short` | `104 passed, 2 warnings`; before six additional coverage cases |
| FAIL then fixed — first lint | `rtk proxy .\backend\.venv\Scripts\ruff.exe check --no-cache backend` | Four issues: error class lacked Error suffix and three regex assertion patterns were not raw/escaped. Renamed to PiiKeyUnavailableError and corrected patterns; no rule disabled |
| PASS — final full suite | `rtk proxy .\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider --tb=short` | `110 passed, 2 warnings in 1.44s`; exit 0 |
| PASS — final lint | `rtk proxy .\backend\.venv\Scripts\ruff.exe check --no-cache backend` | `All checks passed!`; exit 0 |
| PASS — final format | `rtk proxy .\backend\.venv\Scripts\ruff.exe format --check --no-cache backend` | `14 files already formatted`; exit 0 |
| PASS — strict types | `rtk proxy .\.venv\Scripts\python.exe -B -m mypy --no-incremental --cache-dir=.mypy_cache/codex-remediation app tests` | `Success: no issues found in 14 source files`; exit 0 |

The two third-party deprecation warnings are unchanged from §10. All previous 67 tests remain included; new crypto tests are synthetic technical evidence, not certified accountant/golden or authentic-document acceptance evidence.

### 11.6 Documentation and remaining work

Updated the four decision entries and owner queue, ADR/documentation indexes, AUTH accepted-choice notice/rows, Holy Bible v1.0.2, WBS/status/readiness, environment/bootstrap notes and agent operating record. Historical session evidence is retained. Original accepted ADR-001…004, both statutory seeds, authoritative specification/roadmap and uv.lock remain protected. No financial code, migration, production access, deployment, commit or push was performed.

Remaining: CI/provider, PostgreSQL infrastructure and real isolation evidence; production key registry/key-hierarchy contract and nonce lifecycle controls; blind indexing; full audit digest/signing contract; detailed auth/session contract; approved topology; unresolved P4-T15 predecessors; external accountant/counsel and licensed/consented corpora. The four decisions remove their decision gates, not these implementation/evidence dependencies.

### 11.7 Final integrity checks

- `rtk git diff --check` → PASS, empty output, exit 0.
- The exact protected-file command recorded in §10.5 (`rtk proxy git diff --exit-code HEAD --` followed by ADR-001…004, both seeds, authoritative specification and uv.lock paths) was re-executed → PASS, empty diff, exit 0. New ADR-006 supplies the formal amendment; no old accepted ADR text changed.
- Re-executed the §10.5 read-only inline census/link script (without the redundant protected-file block) and added the following exact decision census:

```powershell
$states=@(Get-Content -Encoding UTF8 docs/DECISIONS_REGISTER.md | Where-Object {$_ -match '^\| \*\*Status\*\*'})
"DECISION_ENTRIES="+$states.Count
"RESOLVED="+@($states | Where-Object {$_ -match 'RESOLVED'}).Count
```

Observed: `WBS_TOTAL=86`, `IN_PROGRESS=1`, `COMPLETED=1`, `NOT_STARTED=79`, `READY_FOR_REVIEW=1`, `BLOCKED=4`, `DECISION_ENTRIES=17`, `RESOLVED=4`, `LINKS_CHECKED=86 BROKEN=0`. Local file targets only, not heading-anchor validation.

- `rtk git status --short` → original uncommitted remediation retained; three new untracked paths: `backend/app/core/security/`, `backend/tests/unit/test_pii_transformer.py`, `docs/adr/ADR-006-phase-0-owner-approved-security-and-schema.md`. No staging/commit/push command ran. These are reviewable working-tree changes.

---

## 12. P0-T03 local PostgreSQL scaffold; registry blocker — 2026-11-14

### 12.1 Authorization, specification and actual state

The owner asked to continue work. The next concrete task selected was **P0-T03, PostgreSQL 16 provisioning/hardening**, not an unapproved production deployment. The exact WBS acceptance criteria, DEPLOYMENT §§2.5/4.1, database-engineering and security-threat-model skills were read; the measurable development-only contract was written in existing DEPLOYMENT §4.1.1 before implementing its files. P0-T01's installed tools work, but its CI clause is still incomplete.

Sole accountable writer: Codex `/root`. An actual independent read-only review was delegated to `/root/security_review`; no concurrent file writers or new framework/worktree. No topology under DEC-010, key hierarchy, async queue, schema migration or statutory value was selected.

Docker Desktop was initially stopped. `docker desktop start --timeout 45` succeeded; the engine now responds as **29.9.2**. The canonical `postgres:16.16-bookworm` pull and actual Compose build both failed with **HTTP 403** from image distribution; manifest inspection also hit a remote connection reset. No cached PostgreSQL image or project database container is available. This is an external acquisition/runtime blocker, not an automatic approval rejection and not a PostgreSQL test failure.

P0-T03 is **BLOCKED**, not COMPLETED/READY. Actual WBS census: 86 total, 1 COMPLETED, 1 IN_PROGRESS, 1 READY_FOR_REVIEW, 78 NOT_STARTED, 5 BLOCKED. No phase gate passed. PostgreSQL settings/SQL/pgAudit/runtime isolation are **NOT RUN** despite a complete local scaffold and passing certificate/config tests.

### 12.2 Files and implemented controls

| Files | Purpose / evidence boundary |
| :--- | :--- |
| `infra/compose/compose.dev.yml` | Development-only db service, localhost 55432, project volume, readonly root/config, private secret-file references, tmpfs server-key copy, bounded memory/log rotation; Compose parses successfully |
| `infra/postgres/{Dockerfile,.dockerignore}` | Official PostgreSQL 16.16 Debian base + signed PGDG pgaudit package; allowlisted context excludes all runtime secrets. Actual digest/package versions unverified because build could not acquire base image |
| `infra/postgres/{entrypoint.sh,postgresql.conf,pg_hba.conf,init.sql}` | 0600 postgres-owned server-key copy; TLS1.3/SCRAM; first-match plaintext rejection; restricted Unix peer admin; WAL/memory/timeouts; metadata-only pgAudit, no bound parameter logging; PUBLIC privilege revocation. CREATE EXTENSION precedes database-level pgAudit class enablement. Syntax/static evidence only; no server boot |
| `infra/postgres/local_material.py` | Exclusive non-overwriting dev password/CA/server certificate creation, validate-on-repeat, reject partial/expired/mismatched material. Windows DACL permits only current owner and SYSTEM; CA private key never mounted. Real local material prepared in ignored `.secrets/postgres/`, values never printed |
| `infra/postgres/{verify-hardening.sql,verify_local.py}` | Real-server assertions for version, live TLS, normalized settings, extensions, SCRAM, PUBLIC privilege policy, expected connection rejections and current-run audit/privacy probes. Raw errors/logs/passwords suppressed. Verifier attempt correctly exited 1 with no database; no positive SQL result claimed |
| `backend/tests/unit/test_postgres_material.py` | Seven tests: create/repeat/no-output; strict CA/hostname TLS1.3 memory handshake and wrong hostname rejection; partial material; expiry; mismatched key; actual private ACL inspection; audit probe rejects old/missing/leaking evidence |
| `infra/postgres/ruff.toml`; `backend/mypy.ini` | Inherit existing project lint rules; narrow asyncpg import exception because the pinned wheel has no stubs/py.typed. Project code remains strict; driver runtime API still requires real-server testing |
| `infra/postgres/README.md`; status/readiness/Bible/index/agent docs | Reproducible commands and limitations, no automatic volume deletion/secret rotation; current blocker/counts/evidence synchronized |

No password/DSN was added to Compose environment values, image layers, shell argv or Git. `.secrets/` is already ignored. Files are owner/SYSTEM-only on this host, independently checked by tests. Unit tests use temporary material and never render private contents on assertion failure. Existing data volumes were not deleted/reset and no application login role/table or candidate data was created.

### 12.3 Independent security review

The reviewer read the source contract, security/database skills and relevant accepted decisions, then reviewed infrastructure, material generation, verifier and tests without editing. It found a P2 false-positive risk: any historical AUDIT line could satisfy the initial probe. Fixed by collecting logs since this run's start and requiring CREATE TABLE/INSERT/SELECT metadata for a unique, non-secret generated probe relation. The private payload marker/password must still be absent; raw logs stay in memory.

A regression test rejects historical relation names, incomplete command evidence and private-marker/password leakage. The reviewer re-read the fix and returned **PASS — no remaining blocking static finding**. SQL identifiers in the probe come only from a fixed prefix plus CSPRNG hexadecimal output; values remain bound. The two local S608 suppressions document this static false positive, not a global SQL-injection rule waiver.

Reviewer runtime: **NOT RUN**. Parent observed only the local checks below. HBA, installed extension/settings, actual PostgreSQL TLS/authentication and log behavior must still be validated after image acquisition/build succeeds. pgAudit is operational logging, not the immutable evidentiary ledger or ADR-006's signed read digest.

### 12.4 Commands and actual outcomes

Root-relative commands unless noted. Docker/Python commands used the required access to host Docker/interpreter; this did not bypass network restrictions. No live secret values were output.

| State | Exact command | Observed result |
| :--- | :--- | :--- |
| FAIL — initial service probe | `rtk proxy docker info --format '{{.ServerVersion}}'` | Desktop Linux-engine pipe absent |
| PASS | `rtk proxy docker desktop start --timeout 45` | `Starting Docker Desktop`; exit 0 |
| PASS | `rtk proxy docker info --format '{{.ServerVersion}}'` | `29.9.2`; exit 0 |
| FAIL — acquisition | `rtk proxy docker pull postgres:16.16-bookworm` | HTTP 403 from publisher distribution; signed URL intentionally not copied into documentation |
| FAIL — registry metadata | `rtk proxy docker buildx imagetools inspect docker.io/library/postgres:16.16-bookworm` | Remote connection forcibly closed; no digest verified |
| PASS — inventory | `rtk proxy docker image ls --filter reference=*postgres* --format '{{.Repository}}:{{.Tag}}'` | Empty; no cached PostgreSQL image |
| PASS — config only | `rtk proxy docker compose -f infra/compose/compose.dev.yml config --quiet` | Empty output; exit 0; no secret values printed |
| PASS — material prep | `rtk proxy .\backend\.venv\Scripts\python.exe -B infra/postgres/local_material.py` | `PASS: private local PostgreSQL material ready; values suppressed.`; exit 0 |
| FAIL — actual build | `rtk proxy docker compose --progress plain -f infra/compose/compose.dev.yml build db` | Base image metadata/download HTTP 403; exit 1; see captured-output wrapper below |
| FAIL — correct refusal, not a successful SQL test | `rtk proxy .\backend\.venv\Scripts\python.exe -B infra/postgres/verify_local.py` | `FAIL: PostgreSQL runtime verification did not pass; raw details suppressed.`; exit 1. No server/SQL assertions completed |
| PASS — no created DB container | `rtk proxy docker compose -f infra/compose/compose.dev.yml ps -a --format json` | Empty output; exit 0 |
| PASS — private material excluded | `rtk proxy git ls-files --others --exclude-standard -- .secrets` | Empty output; no private file is eligible as untracked content |
| PASS — final full suite, from backend/ | `rtk proxy .\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider --tb=short` | `117 passed, 2 warnings in 7.86s`; exit 0 |
| PASS — strict types, from backend/ | `rtk proxy .\.venv\Scripts\python.exe -B -m mypy --no-incremental --cache-dir=.mypy_cache/codex-remediation app tests ../infra/postgres/local_material.py ../infra/postgres/verify_local.py` | `Success: no issues found in 17 source files`; exit 0 |
| PASS — lint | `rtk proxy .\backend\.venv\Scripts\ruff.exe check --no-cache backend infra/postgres` | `All checks passed!`; exit 0 |
| PASS — format | `rtk proxy .\backend\.venv\Scripts\ruff.exe format --check --no-cache backend infra/postgres` | `18 files already formatted`; exit 0 |
| PASS — shell syntax only | `rtk proxy "C:\Program Files\Git\bin\bash.exe" -n infra/postgres/entrypoint.sh` | Empty output; exit 0; no Linux bootstrap execution implied |

Actual build command was executed within `rtk proxy powershell -NoProfile -Command` using this captured-output wrapper so public signed download URLs did not reach the transcript:

```powershell
$buildOutput = & rtk proxy docker compose --progress plain -f infra/compose/compose.dev.yml build db 2>&1
$buildExit = $LASTEXITCODE
$buildOutput | ForEach-Object { $_.ToString() -replace 'https://[^\s"]+\?[^\s"]+', '[signed-download-URL-suppressed]' } | Select-Object -Last 14
"BUILD_EXIT=$buildExit"
exit $buildExit
```

Observed `BUILD_EXIT=1`, source image metadata/download HTTP 403. No unverified mirror, daemon registry reconfiguration, insecure registry, disabled TLS, remote production system or different database was used. Docker is left running; there is no project database container. CI/deployment choices remain open.

Intermediate checker failures were corrected: unused import and initial out-of-scope lint-config selection; async subprocess call moved to `asyncio.to_thread`; explicit `check=False` in the ACL test; pinned asyncpg lacks typing metadata so only that import is excepted. No project strictness or security control was globally weakened. The 2 third-party deprecation warnings from earlier sessions remain.

### 12.5 Remaining gate and safe continuation

P0-T03 cannot be marked complete until the official base image and signed pgaudit package build successfully, the resulting digest/version are recorded, and the real TLS/SCRAM/settings/audit/privacy verifier passes. No migration or schema task depending on the database is claimed as implemented. Existing statutory seeds, accepted ADRs, source specification/roadmap and dependency lock remain unchanged. No host package install, financial code, commit, push or production deployment occurred.

Official contracts consulted: [PostgreSQL TLS](https://www.postgresql.org/docs/16/ssl-tcp.html), [HBA first-match behavior](https://www.postgresql.org/docs/16/auth-pg-hba-conf.html), [official PostgreSQL image tags/secrets/init lifecycle](https://github.com/docker-library/docs/blob/master/postgres/README.md), [pgAudit PostgreSQL-16 branch](https://github.com/pgaudit/pgaudit/blob/REL_16_STABLE/README.md). These document supported behavior, not execution evidence for this blocked server.

### 12.6 Final integrity results

`rtk git diff --check` → PASS, empty output, exit 0. Re-executed the exact eight-path protected-file command in §10.5 (`rtk proxy git diff --exit-code HEAD -- ...`) → PASS, empty diff, exit 0. Both seeds, ADR-001…004, authoritative specification/roadmap and uv.lock are unchanged.

The §10.5 read-only WBS/link script was re-executed without its redundant protected-file block; Markdown enumeration now includes the infra runbook using this exact line:

```powershell
$md=@(Get-ChildItem -File -Filter *.md)+@(Get-ChildItem docs -Recurse -File -Filter *.md)+@(Get-ChildItem infra -Recurse -File -Filter *.md)
```

Observed: WBS_TOTAL=86, IN_PROGRESS=1, COMPLETED=1, BLOCKED=5, NOT_STARTED=78, READY_FOR_REVIEW=1; LINKS_CHECKED=86 BROKEN=0. File targets only, not heading-anchor validation.

`rtk git status --short` lists the existing uncommitted remediation plus the new infra directory, certificate test and backend/mypy.ini update; no `.secrets` file appears. No staging, commit, push, volume deletion or registry reconfiguration occurred.

## 13. Documentation freshness and selective loading — 2026-11-14

### 13.1 Authorization, owner and acceptance

The owner explicitly requested Phase 1 of the AI-environment audit: correct stale/conflicting documentation and reduce unnecessary context loading, **without code or product-roadmap changes**. This is documentation maintenance, not a new product WBS item; no WBS ID, completion, decision approval or phase-gate advancement is fabricated. Sole accountable owner/writer: Codex /root. No subagent was started.

Acceptance: current startup guidance agrees with existing implementation/accepted decisions; dated evidence is distinguished from new observations; all 15 root invariants and required financial/security review remain; task-focused reading replaces default full-document loading; local links resolve; every file outside the seven-document scope remains byte-identical to this session's baseline.

### 13.2 Scope and factual corrections

Only AGENTS.md, README.md, DOCUMENTATION_INDEX.md, ENVIRONMENT_INVENTORY.md, AGENT_OPERATING_MODEL.md, PISH_HESABDARI_HOLY_BIBLE.md and this changelog are in scope. Existing uncommitted code/documentation work is preserved.

- AGENTS keeps its original section numbering and 15 invariants, approval/stop rules and mandatory independent review. Duplicate orientation/detail is replaced with references; no safety exemption is introduced.
- README now acknowledges existing FastAPI/tests/encryption/infra, prior dependency installation and proprietary LICENSE. Delivery counts route to PROJECT_STATUS/WBS instead of another stale table.
- DOCUMENTATION_INDEX §0 routes tasks to required source sections and skills. Required specifications still must be read; summaries do not replace them. No context folder, tool configuration, skill installation or discovery migration is introduced.
- Holy Bible v1.0.4 reflects accepted ADR-006 and the four already-resolved decisions, labels initial inventory/census as historical, corrects live Git/licence/1405 instructions and replaces the full-document startup instruction. Historical research and original audit evidence remain intact.
- Agent/environment documents distinguish observed Antigravity desktop/configuration presence from unverified CLI orchestration; remove the absent-first-commit blocker and unsupported Freebuff equivalence. Codex is the maintenance host; recorded earlier reviews are not presented as active agents.
- Runtime evidence remains §12 (117 tests passed in that recorded run; database image/build HTTP 403). Application tests, database state and Antigravity version/discovery were NOT RUN here. The previous restricted Python-launch failure is not a missing-interpreter diagnosis.

Current read-only observations: Codex package 26.1111.2228.0; codex/rtk/rg command paths resolved; Antigravity process/path and ~/.gemini/config + ~/.gemini/antigravity present; agy/antigravity/gemini commands not resolved on this session's PATH; HEAD 2fc2b6f; one existing worktree on main. No process was started/stopped and no config/secret values were printed.

### 13.3 Measured context changes

| Entry document | Before bytes | After bytes | Before characters | After characters |
| :--- | ---: | ---: | ---: | ---: |
| AGENTS.md | 12,384 | 8,000 | 12,198 | 7,923 |
| README.md | 6,965 | 4,699 | 6,725 | 4,674 |

AGENTS bytes decreased 35.4%; README bytes decreased 32.5%. These are file-size/character measurements, not measured model tokens, billed savings or an overall corpus reduction. Required sections of the Holy Bible and primary specifications still load when relevant; the 361,880-byte pre-change master document is no longer requested in full by default.

### 13.4 Verification commands and results

Read-only verification bodies are recorded exactly below; no test/helper file was added. The SHA-256 inventory was captured before edits and compared in orchestration memory with the same command after edits. Exclusions are Git internals, secrets, dependencies and generated caches; no secret directory was read.

**Scope inventory command:**

```powershell
rtk proxy powershell -NoProfile -Command '$ErrorActionPreference="Stop"; $skip=@(".git",".venv","__pycache__",".pytest_cache",".ruff_cache",".mypy_cache","node_modules",".secrets"); $todo=[Collections.Generic.Stack[string]]::new(); $todo.Push((Get-Location).Path); $files=@{}; $sha=[Security.Cryptography.SHA256]::Create(); while($todo.Count){$p=$todo.Pop(); Get-ChildItem -LiteralPath $p -Force | ForEach-Object {if($_.PSIsContainer){if($_.Name -notin $skip){$todo.Push($_.FullName)}} else {$rel=$_.FullName.Substring((Get-Location).Path.Length+1); $hash=[BitConverter]::ToString($sha.ComputeHash([IO.File]::ReadAllBytes($_.FullName))).Replace("-",""); $files[$rel]=@{sha256=$hash; bytes=$_.Length}}}}; $files | ConvertTo-Json -Compress -Depth 4'
```

Observed baseline: 93 files. Before this log update: 93 files, 6 changed (the documentation paths above excluding this log), 87 byte-identical, 0 added/deleted and 0 non-Markdown changes. Final scope check follows in §13.5.

The first inventory attempt used Get-FileHash and FAILED because that cmdlet was unavailable in this shell; it was replaced by the .NET SHA256 implementation above. No file write was part of either probe.

**Local file-link check:**

```powershell
rtk proxy powershell -NoProfile -Command '$ErrorActionPreference="Stop"; $paths=@("AGENTS.md","README.md","docs/DOCUMENTATION_INDEX.md","docs/AGENT_OPERATING_MODEL.md","docs/ENVIRONMENT_INVENTORY.md","docs/PISH_HESABDARI_HOLY_BIBLE.md"); $broken=@(); $checked=0; foreach($p in $paths){$full=Join-Path (Get-Location) $p; $s=[IO.File]::ReadAllText($full); foreach($m in [regex]::Matches($s,"\]\(([^)]+)\)")){$target=$m.Groups[1].Value; if($target -match "^(https?://|mailto:|#)"){continue}; $target=($target -split "#",2)[0]; if($target -match "[<>*`]"){continue}; $checked++; $resolved=Join-Path ([IO.Path]::GetDirectoryName($full)) $target; if(!(Test-Path -LiteralPath $resolved)){$broken+="$p -> $target"}}}; "LOCAL_LINKS_CHECKED=$checked BROKEN=$($broken.Count)"; $broken; if($broken.Count){exit 1}'
```

Observed: LOCAL_LINKS_CHECKED=34 BROKEN=0, exit 0. This covers local Markdown file targets in the six edited guidance documents, not all historical links, external URLs or every heading anchor.

**Invariant/routing check:**

```powershell
rtk proxy powershell -NoProfile -Command '$ErrorActionPreference="Stop"; $s=[IO.File]::ReadAllText((Join-Path (Get-Location) "AGENTS.md")); $n=[regex]::Matches($s,"(?m)^(\d+)\. ") | ForEach-Object {$_.Groups[1].Value}; if(($n -join ",") -ne ((1..15) -join ",")){throw "Invariant numbering differs"}; foreach($t in @("ROUND_HALF_UP","StatutoryParameterUnavailable","rounding_residual_rial","FORCE ROW LEVEL SECURITY","AES-256-GCM","HMAC-SHA256","independent review","five phases / 20 weeks")){if(!$s.Contains($t)){throw "Missing guard"}}; $i=[IO.File]::ReadAllText((Join-Path (Get-Location) "docs/DOCUMENTATION_INDEX.md")); if(!$i.Contains("## 0. Task-focused reading")){throw "Missing routing section"}; $b=[IO.File]::ReadAllText((Join-Path (Get-Location) "docs/PISH_HESABDARI_HOLY_BIBLE.md")); if($b.Contains("**Load this document first**")){throw "Stale full-document loading rule"}; "INVARIANTS=15 REQUIRED_GUARDS=PASS ROUTING=PASS"'
```

**Protected-file check against HEAD:**

```powershell
rtk proxy git --no-optional-locks diff --exit-code HEAD -- docs/adr/ADR-001-frontend-architecture-react-vite-spa.md docs/adr/ADR-002-object-storage-worm-ceph-s3-governance.md docs/adr/ADR-003-sensitive-data-encryption-alee-blind-indexing.md docs/adr/ADR-004-phase-1-product-boundary-prehire-scope.md backend/data/seeds/statutory_rules_1404.yaml backend/data/seeds/statutory_rules_1405.yaml REMEDIATED_TECHNICAL_SPECIFICATION_V2.md backend/uv.lock
```

Observed: empty diff, exit 0. Both seeds, ADR-001…004, the authoritative specification/roadmap and lockfile are unchanged. Other code, configs, skills, ADRs (including pre-existing untracked ADR-006), historical research and WBS are compared with the session baseline rather than assuming a clean HEAD.

**Whitespace check:** `rtk proxy git diff --check` → exit 0, no whitespace errors; Git emitted a pre-existing changelog CRLF-to-LF advisory before this log edit.

NOT RUN: application/unit/security/financial tests, Docker/database verification, package installation, live Antigravity discovery and symlink experiments. Documentation verification does not rerun or certify §12's application results.

### 13.5 Final verification

PASS — re-executed the scope inventory: FILES_BEFORE=93 FILES_AFTER=93 CHANGED=7 UNCHANGED=86 ADDED=0 DELETED=0 UNEXPECTED=0. Changed paths are exactly the seven Markdown documents in §13.2. All other inventoried files, including application/tests, infrastructure, configs, skills, WBS, seeds, ADRs and historical research, match the pre-edit SHA-256 baseline. Git internals/secrets/dependencies/caches were excluded, not modified by this work.

PASS — invariant/routing command: INVARIANTS=15 REQUIRED_GUARDS=PASS ROUTING=PASS, exit 0. The textual check supplements direct review of the original/new rules; it is not a financial or security implementation test.

PASS — local-link command: LOCAL_LINKS_CHECKED=34 BROKEN=0, exit 0. The two new README heading targets were also checked with this exact command:

```powershell
rtk proxy powershell -NoProfile -Command '$ErrorActionPreference="Stop"; foreach($p in @(@("docs/DOCUMENTATION_INDEX.md","## 0. Task-focused reading"),@("docs/BOOTSTRAP_CHANGELOG.md","## 12. P0-T03 local PostgreSQL scaffold; registry blocker — 2026-11-14"))){$s=[IO.File]::ReadAllText((Join-Path (Get-Location) $p[0])); if(!$s.Contains($p[1])){throw "Missing linked heading"}}; "NEW_LINKED_HEADINGS=2 PASS"'
```

Observed NEW_LINKED_HEADINGS=2 PASS, exit 0. This confirms the target headings, not a general Markdown-renderer anchor conformance test.

PASS — protected-file command in §13.4 returned an empty diff, exit 0. Final whitespace command `rtk proxy git --no-optional-locks diff --check -- AGENTS.md README.md docs/DOCUMENTATION_INDEX.md docs/AGENT_OPERATING_MODEL.md docs/ENVIRONMENT_INVENTORY.md docs/PISH_HESABDARI_HOLY_BIBLE.md docs/BOOTSTRAP_CHANGELOG.md` returned exit 0, no whitespace errors (Git's changelog CRLF-to-LF advisory remains informational).

NOT RUN — application/runtime tests and live Antigravity discovery. No commit, push, dependency/configuration change, code edit, roadmap change or WBS status advancement occurred. This completes only the owner's documentation-maintenance scope; unresolved legal, architecture and runtime gates remain unresolved.

## 14. Codex token-saver skill installation — 2026-11-15

Owner: Codex (single accountable executor; no delegation). Scope: owner's explicit local tooling request, outside the product WBS; no product task status advanced. Only this verification record changes in the project. Existing uncommitted work is preserved.

Installed only `token-saver-codex` v0.1.0 from `otnc/agent-skills`, pinned to commit `bcd5cf823813756b2b92de1614584210e025d978`, at `C:\Users\Asus\.codex\skills\token-saver-codex`. Read the repository README, source repository installation/usage instructions, complete skill contract, audit implementation, configuration levers and optional always-on snippet before installation. No packages, other skills, plugins or MCP servers were installed. No Antigravity files/configurations were written. No application, architecture, statutory, reasoning, security or testing settings changed. Existing targeted documentation rules make an additional always-on snippet unnecessary.

Verification observed by the owner:

- PASS — `rtk proxy 'C:\Users\Asus\AppData\Roaming\uv\python\cpython-3.12.9-windows-x86_64-none\python.exe' 'C:\Users\Asus\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py' --repo otnc/agent-skills --ref bcd5cf823813756b2b92de1614584210e025d978 --path skills/token-saver-codex --dest 'C:\Users\Asus\.codex\skills' --method download` — exit 0; installed the single requested directory without overwriting an existing destination.
- PASS — `rtk proxy node 'C:\Users\Asus\.codex\skills\token-saver-codex\scripts\audit.mjs' --agent codex --home 'C:\Users\Asus'` — exit 0; zero warnings, four optional notes (verbosity, tool-output cap, existing MCP servers, skill metadata). No suggested configuration changes applied.
- PASS — `codex --version`: `0.169.0-alpha.11.1`; Node.js `v24.20.0` meets the audit's Node.js 18+ requirement.
- PASS — actual Codex `app-server --stdio` protocol check under the Asus account: `initialize`, `initialized`, then `skills/list` with `{"cwds":["C:\\project\\New project"],"forceReload":true}`. Result: exact installed SKILL.md path, `scope: user`, `enabled: true`, no loading errors. The initial sandbox-account check did not see the user's skill and was superseded by this real-account check.
- PASS — read-only Node validation compared every installed file's Git blob SHA-1 with the pinned GitHub tree: all six matched. SKILL.md frontmatter, name/description, version/agent metadata, compatibility declaration and linked reference/assets files validated; Codex successfully parsed the skill.
- PASS — before this record, project Git diff hash and porcelain status matched the pre-install baseline. No application tests were needed for a user skill installation.
- FAIL (resolved) — sandbox network access and Python launcher/venv execution were unavailable; the bundled installer succeeded with the existing user Python under authorized escalation. An overbroad optional Antigravity inventory encountered a locked runtime file; no write occurred, and no comprehensive Antigravity integrity comparison is claimed.

Use `$token-saver-codex` explicitly on the next turn. Discovery is verified; no restart was required for the fresh app-server check. Skill suggestions about lower reasoning, cheaper models or fewer checks do not override the owner's quality requirements. Pricing, context estimates and configuration advice are dated heuristics, not measured token savings or automatically applied settings. NOT RUN: application/runtime suites, Antigravity activation and billed-token benchmarks.

## 15. P0-T03 official image recovery and runtime verification — 2026-11-15

### 15.1 Scope, ownership and result

Owner-authorized scope: investigate the official image download, run the local development database and execute its real hardening verifier. Sole accountable owner: Codex `/root`. Ownership: existing delivery/evidence records and the infra runbook; no infrastructure source/configuration change, migrations, production deployment, statutory logic or key-management choices. Existing unrelated working-tree changes are preserved. Acceptance: official image acquisition and recorded digest/package versions; healthy localhost-only database; actual TLS/SCRAM/settings/pgAudit/privacy assertions.

The previous HTTP 403 did not recur: official pull/build and actual hardening verifier **PASS**. Historical root cause is not proven; no registry/proxy/TLS settings were changed. No mirror was used. P0-T03 moves BLOCKED → READY_FOR_REVIEW: local acceptance criteria are verified, while P0-T01's CI dependency remains incomplete. Census: 86 = 1 COMPLETED + 1 IN_PROGRESS + 2 READY_FOR_REVIEW + 78 NOT_STARTED + 4 BLOCKED. No phase gate passed.

Previous independent security review in §12 remains applicable because no infrastructure source/configuration changed. No new delegation or independent runtime review was performed. Parent directly ran and observed the real-server verifier. Probe data is synthetic and temporary; no candidate data, tenant table or statutory seed was loaded. Existing unrelated containers remained healthy; no container/volume was deleted. Local DB is left running with persistent project volume `pish-hesabdari-dev_db-data`.

### 15.2 Exact commands and observed outcomes

Root-relative commands; Docker and the existing Python used authorized host access. Captured pull/build output used the §12.4 wrapper with signed-URL suppression (pull substituted for build on acquisition).

| State | Command | Observed result |
| :--- | :--- | :--- |
| FAIL — sandbox access | `rtk proxy docker info --format '{{.ServerVersion}}'` | Permission denied to Docker config/pipe; no credential values read or printed |
| PASS — host access | `rtk proxy docker info --format '{{.ServerVersion}}'` | `29.9.2`, exit 0 |
| PASS | `rtk proxy docker pull postgres:16.16-bookworm` | Download complete, exit 0; official digest below |
| PASS | `rtk proxy docker image inspect postgres:16.16-bookworm --format '{{json .RepoDigests}}'` | `postgres@sha256:a49f7438ba03589f9b1ca062f2da82e899b48ea1dc50d2449fa09a70be83ebca` |
| PASS | `rtk proxy .\backend\.venv\Scripts\python.exe -B infra/postgres/local_material.py` | Existing private material validated; values suppressed; exit 0 |
| PASS | `rtk proxy docker compose -f infra/compose/compose.dev.yml config --quiet` | Exit 0 |
| PASS | `rtk proxy docker compose --progress plain -f infra/compose/compose.dev.yml build db` | `BUILD_EXIT=0`; signed package installed using existing Dockerfile |
| PASS | `rtk proxy docker compose -f infra/compose/compose.dev.yml up -d --no-build --wait db` | Project network/volume/container created; Healthy; exit 0 |
| PASS | `rtk proxy .\backend\.venv\Scripts\python.exe -B infra/postgres/verify_local.py` | `PASS: PostgreSQL 16 TLS/SCRAM/settings/audit/privacy assertions.`, exit 0 |
| PASS | `rtk proxy docker compose -f infra/compose/compose.dev.yml exec -T db dpkg-query -W postgresql-16 postgresql-16-pgaudit` | PostgreSQL `16.16-1.pgdg12+1`; pgAudit `16.1-2.pgdg12+2` |
| PASS | `rtk proxy docker image inspect pish-hesabdari-postgres:16.16-dev --format '{{.Id}}'` | `sha256:7da30fc28265498616ea96101ad86a12d7ad64b1634c207a652385a282c66e70` |
| PASS | `rtk proxy docker compose -f infra/compose/compose.dev.yml ps --format json` | `pish-hesabdari-dev-db-1`: running, healthy, only `127.0.0.1:55432->5432/tcp` |

An initial PowerShell wrapper quoting attempt failed before Docker ran; corrected by using a single-quoted script. No image configuration fix was necessary. Official tag/source consulted: [publisher PostgreSQL image documentation](https://github.com/docker-library/docs/blob/master/postgres/README.md). Digest is observed evidence, not a newly introduced Dockerfile release pin.

NOT RUN: full application suite/type/lint rerun (no application/infra source changed), CI, migrations, tenant RLS, backup/restore, WORM and production gates. Last full suite remains 117 passed in §12. Remaining work: CI selection/integration and P0-T04 schema/provenance contract. No commit/push or public deployment performed.

### 15.3 Documentation and integrity verification

Updated PROJECT_STATUS, EXECUTION_PLAN, IMPLEMENTATION_READINESS, DECISIONS_REGISTER's operational note, ENVIRONMENT_INVENTORY, DOCUMENTATION_INDEX, Holy Bible v1.0.5 and the infra runbook to reference actual §15 evidence. AGENTS.md changed only its latest-evidence pointer (DB §15, full suite §12). No decision was resolved by this operational recovery.

- PASS — `rtk proxy git diff --check`: exit 0; only an informational CRLF-to-LF advisory for this changelog.
- PASS — `rtk proxy git diff --exit-code HEAD -- backend/data/seeds/statutory_rules_1404.yaml backend/data/seeds/statutory_rules_1405.yaml docs/adr/ADR-001-frontend-architecture-react-vite-spa.md docs/adr/ADR-002-object-storage-worm-ceph-s3-governance.md docs/adr/ADR-003-sensitive-data-encryption-alee-blind-indexing.md docs/adr/ADR-004-phase-1-product-boundary-prehire-scope.md REMEDIATED_TECHNICAL_SPECIFICATION_V2.md backend/uv.lock`: empty diff, exit 0.
- PASS — read-only Node `-e` checker: parsed 86 WBS rows, normalized Markdown bold status markers, obtained 1 IN_PROGRESS / 1 COMPLETED / 2 READY_FOR_REVIEW / 78 NOT_STARTED / 4 BLOCKED; verified all seven current-evidence files exist and contain §15, changelog §14 precedes §15, and version 1.0.5's record is inside Appendix F. Initial checker failed because four BLOCKED cells include Markdown `**`; normalization corrected the checker, no WBS values were changed to satisfy it.

## 16. Full-scope Wednesday target; regulatory acquisition first — 2026-11-15

Owner requested full scope within less than one week, prioritized automatic information collection, then clarified Wednesday this week: 2026-11-18, Asia/Tehran; cutoff hour not supplied. Execution overlay is EXECUTION_PLAN §14.8; original roadmap is preserved and no gate is waived. Sole accountable implementation writer: Codex `/root`. Initial implementation ownership: `backend/app/statutory/`, related unit tests and existing spec/status/evidence records. Exact WBS slice: P1-T02 public-source evidence acquisition, which has no predecessor; its human verification/certified sign-off block remains. P0-T04/P0-T11 integration is explicitly deferred to its own contracts, not claimed complete. No seed, statutory value, financial logic, new auth schema or queue choice is authorized by this slice.

Read before implementation: Holy Bible §§0.3/13.1/13.8 and M9; SPEC-STAT-001 (full; previously truncated bounded sections re-read); WBS P1-T01/02/03/15; relevant DEC-001/002/002a; spec-driven-development, software-architecture, database-engineering and security-threat-model contracts. Skill proposals for BackgroundTasks/cloud OCR remain superseded/unapproved. Measurable collector contract is SPEC-STAT-001 §2.1. Current network probes via web tool did not retrieve official ministry/tax/gazette/SSO pages; this is not proof of absence of a document. No numerical legal conclusion was adopted from search results.

### 16.1 Implemented slice and actual independent review

New `backend/app/statutory/{__init__,collect_sources}.py` and `backend/tests/unit/test_statutory_collection.py`: six explicit public discovery targets; HTTPS allowlist and public-address DNS validation; pinned-IP connection with original hostname certificate verification; no redirects/proxies/cookies; 8-MiB response cap and 30-second killable-child bound covering DNS/TLS/headers/body; bounded PDF-link discovery with optional one-level download; exclusive local staging manifests with hashes of completed bytes. All evidence remains UNVERIFIED/LOCAL_STAGING/DISCOVERY_ONLY and `activation_eligible=false`. This CLI is manually invoked, not a scheduler, extraction engine, WORM archive, DB provenance service or activated legal rule set. Partial storage writes stay quarantined `.part`, never accepted as a complete body/hash.

Actual delegation: `/root/collector_security_review`, independent reviewer role H; read-only, no file ownership/writes. Delegation and final static result recorded by coordinator at `2026-11-15T00:57:43+03:30` (clock observed `2026-11-14 21:27:43 UTC`). Reviewer read the actual required contracts/specification and source/tests. Findings fixed: duplicate href attributes bypassing link cap; lack of hard total network deadline; lost HTTP metadata on policy/transport failures; premature hash/body reference on failed write. Regression cases were added, final source re-read and **PASS — no blocking static finding remains**. Reviewer runtime NOT RUN (restricted Python access); parent directly observed all checks below. No agent substitutes for human statutory signatories.

### 16.2 Exact commands and results

Backend-relative Python commands below used the existing environment with authorized host execution; no dependency installation or lockfile change. Ruff commands are root-relative.

| State | Command | Observed result |
| :--- | :--- | :--- |
| PASS — final suite | `rtk proxy .\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider --tb=short` | **157 passed, 2 warnings in 8.52s**, exit 0. Includes 40 collection cases and all prior 117; two third-party deprecations retained |
| PASS — final strict types | `rtk proxy .\.venv\Scripts\python.exe -B -m mypy --no-incremental --cache-dir=.mypy_cache/codex-remediation app tests` | No issues in **18 source files**, exit 0 |
| PASS — final lint | `rtk proxy .\backend\.venv\Scripts\ruff.exe check --no-cache backend infra/postgres` | All checks passed, exit 0 |
| PASS — final format | `rtk proxy .\backend\.venv\Scripts\ruff.exe format --check --no-cache backend infra/postgres` | **21 files already formatted**, exit 0 |
| FAIL — real acquisition | `rtk proxy .\.venv\Scripts\python.exe -B -m app.statutory.collect_sources --source sso-wage-discovery --source labor --source tax --source gazette --source cabinet --source sso` | Exit 1; labor/tax/gazette TRANSPORT_FAILED; SSO root/news and Cabinet HTTP403; **0 accepted bodies**, no legal PDF captured |
| FAIL — final-code real acquisition | `rtk proxy .\.venv\Scripts\python.exe -B -m app.statutory.collect_sources --source sso` | Exit 1; HTTP403, sanitized manifest; no statutory value emitted |
| PASS — whitespace | `rtk proxy git diff --check` | Exit 0; only informational changelog line-ending advisory |
| PASS — protected files | Exact eight-path `rtk proxy git diff --exit-code HEAD -- ...` command recorded in §15.3, re-executed unchanged | Empty diff, exit 0 |
| PASS — no staged evidence/secrets eligible for Git | `rtk proxy git ls-files --others --exclude-standard -- .freebuff/statutory-acquisition .secrets` | Empty output, exit 0 |

Read-only Node `-e` checker also PASS: WBS still 86 with unchanged census (1 completed/1 in progress/2 ready/78 not started/4 blocked); Holy Bible v1.0.6 record correctly in Appendix F; current-evidence references point to §16. No task marked complete from collection preparation. Intermediate lint/type failures were fixed (exception naming, narrow subprocess/CLI print annotations, explicit TLS-context type, test imports and header-validation factoring); no global strictness weakening. Targeted collector suite first passed 36 cases before four additional regression cases; final full suite above supersedes intermediate runs.

### 16.3 Delivery and remaining blockers

Full existing scope is retained. EXECUTION_PLAN §14.8 maps all five WBS phases to the owner-requested Wednesday target with explicit dependencies/capacity limits. DECISION_REQUIRED_FROM_OWNER records urgent existing external/decision needs, not newly resolved choices. Updated current-status/evidence pointers in PROJECT_STATUS, DOCUMENTATION_INDEX, ENVIRONMENT_INVENTORY, AGENT_OPERATING_MODEL, Holy Bible and AGENTS.md; the latter only changes its latest-evidence pointer. P1-T02 remains BLOCKED on current official-source access, WORM/DB provenance integration, independent human signatures and open legal items. No seed, 1405 activation, financial engine, authentication/schema variant, async strategy or production topology was chosen. No CI/backup/RLS/legal/golden-corpus gate was passed. No contacts sent, purchase, commit, push or deployment occurred.

Safe next implementation priority: P0-T04 provenance/migration contract and source archive interface P0-T11, alongside a legitimate route to official artefacts; then staged extraction/diffs, independent verification, fail-closed rule loading and deterministic calculations. No CAPTCHA/TLS/registry bypass or unofficial mirror is authorized. A manually supplied official artefact would still require archival/provenance/signatures before activation.

## 17. Owner-authorized external-tool build — 2026-11-15

Owner authorized starting the full approved scope with OpenCode, AlphaCode and Kilo using free models; Codex coordinates only. Final interactive debugging waits for the owner; component verification and independent financial/security review remain required. No unresolved decision, legal sign-off, statutory activation, production deployment or commit is authorized by this instruction.

Preflight: OpenCode/deepseek-v4.1-flash-free read AGENTS.md and DOCUMENTATION_INDEX §0 and inspected branch/ignore rules read-only. Parent observed unchanged Git status/diff-stat afterwards (PASS). Branch main; .secrets ignored. Its claim that .freebuff contents are unignored is NOT accepted from checking the directory itself; historical ignore rule covers contents. Never read secrets/credential files or transmit candidate data. Full implementation ownership is assigned per bounded work packet; tools must report actual evidence, not claim completion from scaffolds. No additional in-process Codex subagents are started.

Initial packets: OpenCode owns P1-T04 money primitives and corresponding new money tests only (P0-T01 CI incompleteness recorded; bounded local implementation only); AlphaCode owns P1-T02 collection improvements and its existing collector test file only, with P1-T02 still BLOCKED on humans/official access/WORM; Kilo owns read-only independent review of these packets plus P0-T04 contract/dependency assessment. Shared control docs and final integration/status changes remain solely with Codex. Tools must read the actual WBS/specifications/skills and preserve existing dirty files. No overlapping writers are authorized.

### 17.1 Owner-authorized Git/GitHub publication preparation

Owner explicitly requested Git/GitHub connection and ongoing commits. Existing repository is main with no remote. `rtk proxy gh auth status` FAIL: stored GitHub credential invalid; no credential printed. User indicated the desired account is already signed in in their browser; no assumption that an email equals a GitHub username. Official `gh auth login --hostname github.com --git-protocol https --web --clipboard` is running with output captured (device code suppressed), awaiting user authorization. Proposed remote is a PRIVATE `pish-hesabdari` repository after authenticated account identification. No public publication or credential extraction authorized.

Parent baseline verification before commit: `rtk proxy .\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider --tb=short` (backend cwd) PASS: 157 passed, 2 third-party warnings, 9.70s. `rtk proxy git diff --cached --check` PASS. `rtk proxy git grep --cached -l -E 'BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_|AKIA[0-9A-Z]{16}' -- .` returned no matching filenames (a narrow signature check, not a comprehensive secret audit). Explicitly staged existing project source/docs/infra; .secrets, .freebuff, environment credentials, virtualenv and agent caches excluded. No newly generated money files staged in this baseline commit. This preserves pre-existing owner work as explicitly requested.

AlphaCode completed its collector packet with NO CODE CHANGES; parent does not accept its broad PASS claims from the wrong global Python environment. Parent-observed baseline suite above is authoritative; P1-T02 remains BLOCKED. Kilo read-only review and OpenCode money implementation are still running. Their claims are not acceptance until independently observed/reviewed.
