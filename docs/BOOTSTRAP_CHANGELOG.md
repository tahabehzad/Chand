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

Owner subsequently deferred GitHub; the pending gh authorization process was cancelled (exit 1), no remote or push created. Local baseline commit is `eb806e4`. OpenCode money packet and Kilo independent review continue. AlphaCode was assigned P0-T11 adapter preparation with exclusive ownership `backend/app/storage/**` and `backend/tests/unit/test_object_storage.py`; it must read ADR-002/specification before writing, use the existing environment, report absent endpoint integration as NOT RUN and leave completion unclaimed. No shared files or decisions are delegated. Parent has not yet accepted final money/storage results.

### 17.2 Parent-observed packet results and next dispatch

OpenCode P1-T04 run exited 0 with three new owned files: engines/money.py, engines/__init__.py and tests/unit/test_money.py. Parent directly ran backend-relative `rtk proxy .\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider --tb=short`: PASS, **245 passed, 2 warnings, 8.58s**; and `rtk proxy .\.venv\Scripts\python.exe -B -m mypy --no-incremental app/engines tests/unit/test_money.py`: PASS, 3 source files. The 88 new cases cover money primitives, not a complete payroll engine or certified golden corpus. Tool also reported lint/format/Bandit PASS; those claims were not independently re-executed in this check. P1-T04 NOT_STARTED → READY_FOR_REVIEW, not complete: P0-T01 CI and final independent Kilo disposition remain; public `rounding_residual_rial` mapping/sign must be verified before an API contract consumes the primitive's `residual_rial`/`closing_adjustment_rial` fields.

Kilo read-only review process remains running, no final disposition accepted. AlphaCode P0-T11 process remains running; no storage source file existed at inspection. No completion or fresh package assignment is falsely claimed for these busy tools.

OpenCode was dispatched next on free `opencode/glm-5.3-flash-free` to P0-T04. Exclusive allowed files: backend/alembic.ini, backend/alembic/**, backend/app/models/statutory.py, backend/tests/integration/test_statutory_migrations.py and new docs/specs/STATUTORY_DATABASE_CONTRACT.md. Must derive and write exact contract before code from actual required specifications/ADRs; user-FK ordering, statutory tenancy and signature semantics must not be guessed. If unresolved, report precise questions in owned spec, stop only affected migration. Existing pish_dev/volumes must not be dropped; runtime checks require an isolated test DB. P0-T04 status is IN_PROGRESS only for contract assessment, no implemented migration or accepted schema is claimed. No file ownership overlaps storage/money or shared control docs. Full task census now 1 COMPLETED, 2 IN_PROGRESS (including P0-T04 assessment), 3 READY_FOR_REVIEW, 76 NOT_STARTED, 4 BLOCKED = 86.

### 17.3 Continued dispatch after completed external processes

Owner requested continuing bounded packages. AlphaCode storage process exited 0 without implementation, incorrectly treating absent new owned paths as a blocker. Coordinator explicitly corrected that it may CREATE backend/app/storage/** and test_object_storage.py and restarted the same P0-T11 packet with bounded exploration. This is a retry, not a completed package or real product blocker. Kilo's prior process exited 0 without a final usable review disposition; checks visible in its output do not establish independent approval. A new narrowly scoped read-only review was dispatched using free kilo/cohere/north-mini-code:free, focusing on money precision/ambient-context behavior and exact findings. OpenCode database contract assessment continues in its already exclusive paths. No source edited by Codex; no completion gate advanced.

### 17.4 Tool failure recovery and database decision escalation

AlphaCode's corrected storage run still produced empty files/malformed write calls; interrupted before accepting any artifact. Free alternate poolside/laguna-s-2.1:free returned HTTP404; AlphaCode's OpenCode provider lacks configured authentication (no credentials inspected/changed). Transferred SAME exclusive P0-T11 paths to verified free OpenCode/deepseek-v4.1-flash-free. Empty files are failed output, not implementation. No simultaneous storage writers remain. Kilo/north-mini-code review repeatedly used incompatible shell/global Python and wrote scratch scripts outside the requested read-only scope; interrupted, no review accepted. Retried read-only review using free Kilo Auto with exact paths and bounded calls. These are observed reliability failures, not claims of quota exhaustion.

OpenCode/GLM created only docs/specs/STATUTORY_DATABASE_CONTRACT.md, asserting that global/no-RLS scope and deferred user FKs were derived decisions. Coordinator paused the writer BEFORE any migration code. Actual independent read-only review by OpenCode/MiniMax returned migration MUST NOT PROCEED: draft-schema omissions do not authorize no-RLS; deferred user attribution constraints require explicit decision/ownership, and the no-pgcrypto citation was wrong. Raise DEC-012 OPEN — BLOCKING; never silently choose a security/schema variant. Contract-only corrective edit assigned exclusively to MiniMax; no approved ADR changes. Parent has not verified any migration, and no migration exists. P0-T04 becomes BLOCKED; P0-T11 becomes IN_PROGRESS (fallback implementation). Updated census: 1 COMPLETED, 2 IN_PROGRESS, 3 READY_FOR_REVIEW, 75 NOT_STARTED, 5 BLOCKED = 86. Original full scope and gates remain unchanged.

### 17.5 Owner-requested coordinator pause and unaccepted late artifacts

Owner explicitly requested handing work to external tools and pausing Codex promptly. Active bounded jobs at handoff: free OpenCode/DeepSeek implements P0-T11 storage; free OpenCode/MiniMax corrects the proposed database contract only; another free MiniMax job was dispatched to reproduce/repair P1-T04 ambient Decimal context behavior in money.py/test_money.py only. No overlapping writers. AlphaCode routes failed or produced empty files; Kilo money review finished with a claimed FAIL, but its 1.5→2 example alone does not demonstrate a defect. Repair agent must reproduce a genuine identical-input precision counterexample before changing code; review claim is not accepted blindly. Parent verification of new output is NOT RUN while paused.

Correction to §17.4 timing claim: subsequent filesystem inspection found unaccepted backend/alembic.ini, alembic/env.py, script.py.mako, versions/0001_statutory_baseline.py and app/models/statutory.py from the stopped assessment process. Their write timing relative to the interrupted launcher is not established; the earlier claim of no migration files must not be relied on. These artifacts are NOT APPROVED/VERIFIED, must not be run or counted as completed under DEC-012, and are preserved for later review rather than silently deleted. A targeted process inventory found no matching active P0-T04 writer. Schema decision block remains. No deployment/seed activation is authorized.

No promise of automatic cross-tool supervision after the coordinator pauses: each launched process has only its assigned packet and must report completion/blockers; additional reassignment and parent-observed verification wait for the owner's next continuation. No project-wide completion or final debugging is claimed.

## 18. Owner-requested progress inspection — 2026-11-15

Scope: inspect actual worker output and verify current artifacts; no implementation/fixes or new dispatch. Previous exec process IDs are no longer available, so exit reports cannot be recovered from those handles. A targeted process inventory found no matching active assigned worker. Current files, not assumed process success, establish the findings below.

- Money primitive repair exists: quantization now uses an internal precision-34/HALF_UP context and ambient-context regression cases were added. Complete payroll/tax/SSO engines and current-law activation are still absent.
- S3 adapter and its unit tests now contain real implementations (s3_adapter.py 19,662 bytes; test_object_storage.py 17,914 bytes). This is source/local-unit evidence, not a live retention/credential-policy acceptance.
- Frontend exists with React/Vite/TypeScript, RTL shell, Vazirmatn, number/currency helpers, typed client boundary and presentation-only auth screens. README explicitly labels missing APIs and provisional contracts; actual authentication, simulations, Jalali conversion and PDF pipeline are not delivered. Synthetic development preview is labelled. Its chunk is emitted in the production build; no visual/production-access review was performed here.
- Database contract revision 2 is PROPOSED/BLOCKED; old unaccepted migration/model/integration-test artifacts remain present. Contract §8 statements that migration/test source is absent are stale compared with this filesystem inspection. No migration or database integration test was run; DEC-012 remains unresolved. No scope/status or legal decision was silently advanced.

Parent-observed commands (backend/ cwd):

| Result | Exact command | Observed evidence |
| :--- | :--- | :--- |
| PASS | `rtk proxy .\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider --tb=short tests/unit tests/api` | **317 passed**, 2 third-party warnings, 12.10s; deliberately excludes unaccepted migration integration tests |
| PASS | `rtk proxy .\.venv\Scripts\ruff.exe check --no-cache app tests/unit tests/api` | All checks passed |
| PASS | `rtk proxy .\.venv\Scripts\python.exe -B -m mypy --no-incremental app tests/unit tests/api` | No issues in **25 source files** |

Parent-observed commands (frontend/ cwd), reusing installed dependencies without install/global changes:

| Result | Exact command | Observed evidence |
| :--- | :--- | :--- |
| PASS | `rtk proxy npm run typecheck` | TypeScript exits 0 |
| PASS | `rtk proxy npm run lint` | Logical-utility gate: 58 files, zero violations; not a full ESLint/accessibility claim |
| PASS | `rtk proxy npm test -- --reporter=dot` | **90 tests**, 11 files, passed; React act warning in drawer test |
| PASS | `rtk proxy npm run build` | Vite 6.4.6 production build succeeded, 135 modules; 4.43s |

No new package was installed, no source fixed, no worker relaunched, no migration executed and no commit/push performed in this inspection. Pending edits and newly generated backend/frontend files remain uncommitted after `55eef45`; no complete-product or phase-gate claim follows from passing isolated suites.

## 19. Reviewed foundation milestone — 2026-11-15

### 19.1 Authorization, ownership and implementation plan

The owner supplied a development mission explicitly authorizing implementation,
local execution, verification, meaningful commits and verified GitHub pushes.
The owner then supplied `https://github.com/tahabehzad/pish-hesabdari` and
confirmed it is public. This supersedes the earlier coordinator-only/pause and
GitHub-deferral instructions for this bounded work. It does not approve an open
schema, legal, authentication-detail, CI-provider or production decision.

Scope/plan: audit actual implementation against accepted decisions; adopt and
repair the existing P1-T04 money and P0-T11 storage packets; independently review;
verify unit/API/build/live behavior; reconcile factual status; publish reviewed
source on a separate development branch while preserving both Git histories.
P3-T01/T02/T04/T05/T06 contain pre-existing partial interface work, not newly
completed Phase 3 tasks. The formatter defects discovered during review were
fixed under P3-T04 before adoption. No predecessor or phase gate is waived.

Sole accountable implementation/integration owner: Codex `/root`. Owned files:
`backend/app/engines/money.py`, `backend/tests/unit/test_money.py`,
`backend/app/storage/**`, `backend/tests/unit/test_object_storage.py`; adopted
`frontend/**` source/config/lockfile with bounded formatter/copy fixes; root
README and existing status/execution/changelog documents. All pre-existing
unaccepted Alembic/model/integration/contract drafts are preserved outside the
milestone and were not executed. No financial rate, statutory seed or accepted
ADR was changed. P0-T01's installed tooling is usable; its CI clause remains
incomplete. P0-T11 still needs actual RGW and credential-policy acceptance.

Actual delegation (both agents read required source documents, never wrote):

| Task/role | Agent | Actual scope and evidence |
| :--- | :--- | :--- |
| Independent financial/security review | `/root/independent_review` | Read money/storage source, tests, governing specs/skills/ADR-002; reproduced mutable report/allocation and invalid-Unicode-key defects; identified money amounts in exception text. Independently observed 160 baseline and 170 corrected scoped tests PASS. Final bounded review PASS; no live RGW or phase acceptance. |
| Architecture/roadmap and independent frontend review | `/root/roadmap_audit` | Read the entire Holy Bible in bounded chunks, accepted ADRs and required execution sources; inspected all frontend runtime source/config. Confirmed dependency blocks; found wrong percentage shifting and unsafe-number acceptance. Independently ran corrected formatter suite: 23 PASS. Final baseline review PASS; no visual/axe/production acceptance. |

No external OpenCode/AlphaCode/Kilo writer was launched. No planned role is
represented as an active worker. Parent directly observed all checks below;
reviewer claims do not substitute for parent verification.

### 19.2 Real changes and observed verification

- Money: preserved the pre-existing ambient-context repair after review; copied
  validated report/allocation input into immutable tuples; exposed canonical
  `rounding_residual_rial = sum(rounded lines) - rounded total`, retaining
  `residual_rial` compatibility. `closing_adjustment_rial` remains the opposite
  signed posting under its own name. Removed financial amounts from mismatch
  errors. Added regressions and two Hypothesis properties (200 examples each,
  no persistent example database) for exact signed allocation/reconciliation.
  Existing AST float/round/purity checks already existed and were verified,
  rather than duplicated or falsely claimed as newly implemented.
- Storage: adopted the existing tenant-prefixed GOVERNANCE adapter after review;
  invalid UTF-8 surrogate keys now produce sanitised `InvalidStorageKeyError`
  before client calls. No bucket/IAM provisioner, destructive API or live WORM
  acceptance is implied.
- Frontend: adopted the pre-existing partial Persian RTL shell/client and
  disabled auth screens. Fixed rate-to-percent decimal shifting (`1.5` now
  displays `۱۵۰٫۰٪`, `0.7` displays `۷۰٫۰٪`); rejected unsafe JavaScript number
  amounts while preserving exact strings/bigints. Corrected the prior test
  expecting the wrong percentage. Removed misleading session-expiry and base-URL
  claims. No login, session expiry enforcement or business API was invented.

Commands below ran in `backend/` unless marked `frontend/`. All fixtures were
synthetic. No installation, real candidate data, migration or production access.

| Result | Exact command/check | Observed evidence |
| :--- | :--- | :--- |
| PASS | `rtk proxy .\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider --tb=short tests/unit tests/api` (baseline) | 317 passed, 2 third-party warnings, 7.93s |
| PASS | `rtk proxy .\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider --tb=short tests/unit/test_money.py tests/unit/test_object_storage.py` | 170 passed, 1 third-party warning, 0.50s; before two additional property tests |
| PASS | `rtk proxy .\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider --tb=short tests/unit tests/api` (final) | **329 passed**, 2 third-party warnings, 8.42s; includes existing AST gate and both new property tests |
| PASS | `rtk proxy .\.venv\Scripts\python.exe -B -m mypy --no-incremental app tests/unit tests/api` | No issues in 25 source files |
| PASS | `rtk proxy .\.venv\Scripts\ruff.exe check --no-cache app tests/unit tests/api` | All checks passed after the import-order correction |
| PASS | `rtk proxy .\.venv\Scripts\ruff.exe format --check app/engines app/storage tests/unit/test_money.py tests/unit/test_object_storage.py` | 6 files already formatted after formatting correction |
| PASS | `rtk proxy .\.venv\Scripts\python.exe -B -m bandit -q -r app/engines app/storage` | Exit 0, no findings |
| FAIL → PASS | Same scoped `ruff format --check` command above; then `rtk proxy .\.venv\Scripts\ruff.exe format app/engines/money.py tests/unit/test_money.py` | Initial 1 unformatted file; repaired and final check PASS |
| FAIL → PASS | Same full `ruff check` command above | Initial unsorted Hypothesis import; combined imports and final check PASS |
| FAIL → PASS | `rtk proxy npm test -- src/lib/money.test.ts --reporter=dot` (`frontend/`) | Before fix: 6 failures/23 tests reproduced percentage/unsafe-number defects; after fix: 23 PASS. No monetary failure quarantined |
| PASS | `rtk proxy npm test -- --reporter=dot` (`frontend/`, final) | **99 tests**, 11 files passed, 8.93s; existing React act warning in drawer test |
| PASS | `rtk proxy npm run build` (`frontend/`, final) | TypeScript and Vite 6.4.6 production build succeed, 135 modules, 4.73s |
| PASS | `rtk proxy npm run lint` (`frontend/`) | Logical-utility gate: 58 files, 0 violations; not a full ESLint/accessibility claim |
| PASS | Live backend HTTP smoke below | Actual 200/alive, correlation echo and allowed-origin CORS verified |
| PASS | Live frontend HTTP smoke below | Actual 200 and document `lang=fa`/`dir=rtl`; not a visual browser check |
| NOT RUN | Alembic upgrade/downgrade and migration integration tests | DEC-012 unresolved; drafts remain unaccepted |
| NOT RUN | Actual RGW upload/delete-denial/bypass-permission checks, RLS, auth/session, certified golden corpus, visual/axe/E2E and production/phase gates | Required dependencies/environments/approvals not delivered; mocks and a build do not replace them |

Exact local backend launch (`backend/`):

```powershell
rtk proxy .\.venv\Scripts\python.exe -B -c "import uvicorn; from app.main import create_app; from app.core.config import Settings; uvicorn.run(create_app(Settings(_env_file=None, allowed_origins='http://127.0.0.1:5273')), host='127.0.0.1', port=58000)"
```

Exact backend smoke (`backend/`):

```powershell
rtk proxy .\.venv\Scripts\python.exe -B -c "import httpx; r=httpx.get('http://127.0.0.1:58000/health/live', headers={'Origin':'http://127.0.0.1:5273','X-Request-Id':'synthetic-smoke-001'}); assert r.status_code == 200; assert r.json() == {'status':'alive'}; assert r.headers['X-Request-Id'] == 'synthetic-smoke-001'; assert r.headers['access-control-allow-origin'] == 'http://127.0.0.1:5273'; print('PASS live HTTP liveness, correlation and CORS')"
```

Exact frontend launch (`frontend/`, installed dependencies reused):

```powershell
rtk proxy ..\backend\.venv\Scripts\python.exe -B -c "import os, subprocess; process_env = os.environ.copy(); process_env['VITE_API_BASE_URL'] = 'http://127.0.0.1:58000'; subprocess.run(['node', 'node_modules/vite/bin/vite.js', '--host', '127.0.0.1', '--port', '5273', '--strictPort'], env=process_env, check=True)"
```

Exact frontend smoke (`backend/`):

```powershell
rtk proxy .\.venv\Scripts\python.exe -B -c "import httpx; r=httpx.get('http://127.0.0.1:5273/'); assert r.status_code==200; assert 'dir='+chr(34)+'rtl'+chr(34) in r.text; assert 'lang='+chr(34)+'fa'+chr(34) in r.text; print('PASS local frontend HTTP and Persian RTL root')"
```

The first frontend-smoke attempt failed in shell quoting before any HTTP
request; the exact corrected command above passed. Both services bind loopback
only. Startup/request logs were observed; no application error in these smokes.
An orphan production chunk still contains labelled synthetic preview fixtures;
the production route is unregistered, but absence of the chunk is not claimed.

Status changes: P0-T11 IN_PROGRESS → READY_FOR_REVIEW for local code review only;
P1-T04 remains READY_FOR_REVIEW; P3-T01/T02/T04/T05/T06 NOT_STARTED → IN_PROGRESS
to reflect existing partial code and the formatter repairs. Census: 1 COMPLETED,
6 IN_PROGRESS, 4 READY_FOR_REVIEW, 70 NOT_STARTED, 5 BLOCKED = 86. No new task or
phase is COMPLETED. Assumptions/blockers remain in the respective WBS rows and
must be rechecked at the phase gate.

### 19.3 Git/GitHub record

`origin` was added from the owner's exact repository URL and fetched. Remote
`main` initially contains only README commit `898388c`; local history ends at
`55eef45` before this milestone. Work uses `codex/foundation-hardening`.
`rtk proxy gh auth status` and the subsequent `gh api` permission probe FAIL
because gh's stored credential is invalid (401); no credential was printed.
Git's separate credential path works: `rtk proxy git -c credential.interactive=false -c core.askPass= push --dry-run origin HEAD:refs/heads/codex/foundation-hardening`
PASS. No login/credential extraction or account switch was needed.

Documentation checks PASS: `rtk git diff --check` found no whitespace defects;
parent's Python local-link check found no missing file targets in README,
frontend README, PROJECT_STATUS, EXECUTION_PLAN and this changelog. WBS row
enumeration independently produced 86 tasks and the exact §19.2 status counts.
The pre-existing DEC-012 register entry/census is adopted with its unresolved
status; its stale operational sentence was corrected. No decision resolved.

Publication finalization is pending in this entry until commit, history
integration, actual push and remote-ref verification are observed. No force-push,
main rewrite, repository creation or CI-provider choice is authorized/implied.

## 20. Owner-requested MVP 0.1 local frontend demo — 2026-11-15

Owner: Codex /root, sole implementer; no delegation. Status: COMPLETED for the
bounded local demo only. Related existing WBS: P3-T01/P3-T02/P3-T06; P3-T04
formatting and P3-T05 client reused without financial/client implementation changes.
Read Holy Bible §§0.3, 3.2 M8, 4.2–4.3, 13.1, 13.8; ADR-001; SPEC-FE-001;
DOCUMENTATION_INDEX §0; current WBS rows/dependencies and PROJECT_STATUS §2.
Ownership: frontend demo files, shell/router/navigation/icons/styles and bounded
status/README/changelog/owner-request record updates. Backend, seeds, ADRs,
existing staged changes and migration drafts preserved; no commit/push/deployment.

Acceptance: Persian RTL/light/Vazirmatn dashboard, three summary cards,
six-month income/expense chart with exact-value accessible table, recent synthetic
transactions, basic session-only unit settings, working desktop/mobile navigation.
Data is separately labelled synthetic UI fixtures, never a production API fallback.
Previous overview/health client retained at /system; previous module routes retained.
No new dependencies, backend architecture, calculations or auth implementation.

Blocking issues/assumptions: no blocker to this local synthetic UI demo. Existing
P1-T19/P0-T18 dependencies and DEC-006 remain unresolved as recorded; no WBS task
or phase gate advanced. Demo amounts are precomputed fixtures, not emitted statutory
figures, rule activation or candidate data. Settings reset on full reload. Chart
bar geometry is predefined presentation data; exact amounts are in its disclosure.

Verification observed by /root (frontend working directory unless stated):
- FAIL: rtk proxy pnpm run typecheck: host wrapper attempted dependency reinstall
  and refused non-interactive modules replacement; no dependency/config change made.
- PASS: rtk proxy pnpm --config.manage-package-manager-versions=false --config.verify-deps-before-run=false run typecheck.
- PASS: rtk proxy node node_modules/typescript/bin/tsc --noEmit -p tsconfig.app.json.
- Initial FAIL: rtk proxy node node_modules/vitest/vitest.mjs run: 2 new assertions
  matched both summary and chart detail amounts. Scoped assertions to summary region.
- PASS: rtk proxy node node_modules/vitest/vitest.mjs run: 102 tests across 12 files;
  all prior tests retained. Existing shell tests now expand preserved navigation.
- PASS: rtk proxy node node_modules/vite/bin/vite.js build: 142 modules; local
  Vazirmatn woff2 assets emitted; route chunks built successfully.
- PASS: rtk proxy node scripts/check-logical-utilities.mjs src: 66 files, 0 violations.
- PASS: rtk git diff --check (workspace root).
- PASS: local Vite server via rtk proxy node node_modules/vite/bin/vite.js --host
  127.0.0.1; browser loaded dashboard at http://127.0.0.1:5273/.
- PASS: browser desktop settings → Toman → dashboard and mobile menu → transactions;
  drawer closes on navigation. RTL/lang/font observed in rendered document.
- PASS: browser viewport 360 × 800: document content/viewport both 360 px; table
  608 px confined to 326 px scroll region. At 1440 × 1000: content/viewport both
  1425 px (scrollbar excluded); summary renders three 363 px columns.
- NOT RUN: backend tests/migrations (backend untouched), production deployment,
  axe audit, real financial API/auth flows. No such acceptance claimed.

Desktop screenshot saved outside repository in the session visualization directory
as pish-mvp-desktop.jpg. Temporary viewport override reset after browser checks.

Final verification: PASS rtk proxy pnpm --config.manage-package-manager-versions=false --config.verify-deps-before-run=false run build (typecheck + Vite).
PASS rtk proxy node node_modules/vitest/vitest.mjs run after adding cleanup before
store reset: 102/102 tests; the prior React act warning no longer appears.
PASS: Python local Markdown-link check for the four modified documentation files;
final git diff --check. Git index preserved: no staging, commit or push performed.
The owned local preview server was stopped after QA (Ctrl+C); restart instructions
are in frontend/README.md. No application server was left running by this task.


## 21. Owner-approved P0-T04 baseline and final verification — 2026-11-15

Owner explicitly approved “T-2 و F-1 با همون شرایطی که گفتی”. Codex /root
implemented the existing P0-T04 milestone, retaining backend/frontend 0.1.0 and
the approved roadmap. No new product scope or statutory interpretation.
ADR-007/contract revision 3 record the exact approval. Previous contract rev2
is retained verbatim in docs/specs/history; pre-edit draft code copies are in
the active chat's work/p0t04-before. Existing staged/unstaged work was preserved.

Implementation: adopted the unapplied 0001 migration and typed models; corrected
L1…L4 storage to VARCHAR(2); installed ENABLE/FORCE RLS on all five global tables,
column-limited ACTIVE-only security-invoker/security-barrier reader view,
separate evidence-reviewer SELECT and database-wide statutory write gate until
P0-T05 validates users FKs (ON DELETE RESTRICT). Append-only signatures separately
reject UPDATE/DELETE/TRUNCATE. Role provisioning is explicit, NOLOGIN and no
membership grant; validates existing unsafe roles. Migration AST storage lint
rejects lengthless strings, floating point and naive timestamps. Connection
diagnostics are sanitized and metadata is registered for autogeneration.

Required independent security review was delegated to
`/root/statutory_security_review`, read-only/no file ownership, under AGENTS §6
and AGENT_OPERATING_MODEL §3. Reviewer read the actual ADR/contract/AUTH/ingestion
sources and owned code. Found a default-ACL leak: owner deployment defaults
could grant reader full-table SELECT, including actor/source columns. Fixed by
clearing role table/view grants before exact grants; integration fixture now
deliberately sets broad deployment defaults. Reviewer re-read the fix and
reported PASS with no further actionable findings. Parent observed runtime
verification independently. No named human security/legal approval is asserted.

Exact backend checks (backend/):

| Result | Command | Observed evidence |
| :--- | :--- | :--- |
| PASS | `rtk proxy .venv\Scripts\python.exe -B -m pytest tests/unit tests/api tests/integration -q --tb=short -p no:cacheprovider` | Final resumed run: **443 passed**, 2 existing third-party deprecation warnings, 16.99s; 342 unit/API + 101 actual PostgreSQL integration; no skips |
| PASS | `rtk proxy .venv\Scripts\python.exe -B -m mypy --no-incremental app tests/unit tests/api tests/integration alembic/env.py` | No issues in **30 source files** |
| PASS | `rtk proxy .venv\Scripts\ruff.exe check --no-cache app tests/unit tests/api tests/integration alembic/env.py` | All checks passed |
| PASS | `rtk proxy .venv\Scripts\ruff.exe format --check app/core/migration_lint.py app/models/statutory.py alembic tests/integration/test_statutory_migrations.py tests/unit/test_migration_lint.py` | 5 files already formatted |

Frontend checks performed in this same implementation stage; frontend code was
not modified by P0-T04 and did not change before the resumed final verification:

| Result | Command (frontend/) | Observed evidence |
| :--- | :--- | :--- |
| PASS | `rtk proxy node node_modules/vitest/vitest.mjs run` | **102 passed**, 12 files |
| PASS | `rtk proxy node node_modules/typescript/bin/tsc --noEmit -p tsconfig.app.json` | Exit 0 |
| PASS | `rtk proxy node node_modules/vite/bin/vite.js build` | Vite 6.4.6, 142 modules, production build succeeds |

FAIL → fixed during development: asyncpg multi-command helper used a prepared
fetch; switched provisioning statements to execute. TRUNCATE test originally
stopped at FK protection; used CASCADE with deliberately broad fixture grants
to exercise the write gate. mypy found SQLAlchemy's untyped dialect constructor;
used one documented third-party-only no-untyped-call exemption in test code.
Unused test noqa removed. All final checks above passed; no failure quarantined.

Startup: parent ran chat work/p0t04_smoke.py through the existing backend Python.
Actual backend /health/live and built frontend returned HTTP 200; Persian
lang/RTL root verified. Both loopback-only child processes were stopped in
finally. Integration tests created and removed only their generated
pish-p0t04-migtest-* containers using locally cached official PostgreSQL 16.16;
pish_dev and other services/volumes were untouched. No test container remains.

Git: no stage, commit, push or history rewrite. Seed diff empty; 1404 hash still
CA16C4558D29A81AE3123FBAB63732F130CC4425BF67617932C41B045FABE821.
Final whitespace/link checks recorded below after documentation updates.

Status: **P0-T04 READY_FOR_REVIEW**, not COMPLETED: local acceptance and independent
static review passed; P0-T01 CI clause/real CI migration job remain unmet.
Current census: 1 COMPLETED, 6 IN_PROGRESS, 5 READY_FOR_REVIEW, 70 NOT_STARTED,
4 BLOCKED = 86; no phase gate passed. P0-T05 owns the real identity schema and
validated statutory actor FKs; all five statutory write paths remain closed.
NOT RUN: production/pish_dev migration, identity/auth integration, certified
financial corpus, real RGW, release gate or production deployment. No 1405
activation, seed change, legal sign-off or production-readiness claim.

Final record: PASS rtk git diff --check; seed diffs empty (staged/unstaged); local Markdown-link check on ADR-007/contract/indexes; independently enumerated WBS census matches 86 tasks and the status counts above. No application code changed after the successful final suite.

## 22. P0-T04 database/security re-verification and fail-closed hardening — 2026-11-15

Database and Security Infrastructure Engineer (continuation task). Scope: verify the
already-implemented ADR-007 baseline against the owner decision, close the remaining
fail-closed test gap and fix the defects found. No product scope, statutory value,
frontend, dashboard, authentication or ADR content was changed; ADR-001…007 and the
approved decisions were read and left untouched.

Read for this pass: Holy Bible §0.3/§5.1–§5.11/§13.8, AGENTS.md, ADR-001…007,
STATUTORY_DATABASE_CONTRACT revision 3, STATUTORY_INGESTION §§2.2/4.2/5.2/5.5/10,
DECISIONS_REGISTER DEC-012, DECISION_REQUIRED_FROM_OWNER (DEC-012 resolved
2026-11-15), EXECUTION_PLAN §14.3. The owner decision is confirmed as T-2 + F-1 per
ADR-007: five global tables with ENABLE/FORCE RLS, restricted reader/reviewer
database roles, deferred users FKs owned by P0-T05, every statutory write path closed
until then.

### Defects found and fixed

| # | Defect | Fix |
| :-- | :--- | :--- |
| D-1 | `trg_statutory_parameter_signatures_append_only()` had no pinned `search_path`, unlike its sibling `statutory_identity_write_gate()`. Asymmetric hardening on a trigger that runs before every statutory write. | The migration now declares the append-only function with `SET search_path = pg_catalog`. Behaviour is unchanged (the body references no object); the downgrade still drops it. |
| D-2 | Every migration failure collapsed into one generic message, so the fail-closed refusal for missing/unsafe statutory roles was undiagnosable for an operator. | `alembic/env.py` maps only two repository-owned literal markers to a sanitized, actionable message. Every other driver error keeps the generic message, so no DSN, parameter or credential can still reach a log. |
| D-3 | ADR-007 requires "a missing or unsafe role fails closed", but no test covered the refused path — it had only ever been exercised by hand. | New `backend/tests/integration/test_statutory_fail_closed.py`: missing roles refuse and leave no schema; an unsafe (LOGIN) role refuses identically; the same database then succeeds once the roles are safe, proving the refusals were the role precondition. Each scenario owns its own generated container. |

Defect deliberately **not** changed: `infra/postgres/statutory_roles.sql` creates
NOINHERIT roles but does not reject a pre-existing role carrying INHERIT. That is not
a gap: the migration precondition already refuses any role membership, and a role
with no memberships behaves identically with or without INHERIT. Changing it would
alter an approved provisioning script without an owner decision.

### Independent adversarial verification (outside the repository test suite)

Re-probed the baseline with an independent harness against its own disposable
containers. Confirmed: the migration refuses without the statutory roles and rolls
back completely (no table, no `alembic_version`); the reader role holds no
table-level privilege on any of the five tables and only the ten published columns
of `statutory_rule_set_versions` plus the view; `verified_by`, `source_manifest`,
`verified_at` and `to_jsonb(row)` are all refused for the reader; the reviewer reads
all statutory evidence and is refused every write; the table owner sees zero rows
(FORCE RLS) and is refused by the write gate with `Statutory writes require P0-T05
identity FK enforcement`. Adversarial `ALTER DEFAULT PRIVILEGES ... GRANT ALL ON
TABLES` for the migration owner is neutralised by the migration's explicit REVOKE,
which is what keeps the reader column-limited.

### Observed results

| Result | Command (backend/) | Observed evidence |
| :--- | :--- | :--- |
| PASS | `.venv\Scripts\python.exe -B -m pytest tests/unit tests/api tests/integration -q --tb=short -p no:cacheprovider` | **446 passed**, 2 existing third-party deprecation warnings, 19.30s; no skips, no failures, no quarantined test |
| PASS | `.venv\Scripts\python.exe -m mypy --no-incremental app tests/unit tests/api tests/integration alembic/env.py` | Success: no issues found in **31 source files** |
| PASS | `.venv\Scripts\ruff.exe check --no-cache app tests/unit tests/api tests/integration alembic/env.py` | All checks passed |
| PASS | `.venv\Scripts\ruff.exe format --check --no-cache app/core/migration_lint.py app/models/statutory.py alembic/env.py alembic/versions tests/integration tests/unit/test_migration_lint.py` | 8 files already formatted (two files reformatted during this pass) |
| PASS | `git diff --check` | No whitespace defects introduced |

Test census: 342 unit/API (unchanged by this pass) + 101 statutory migration
integration + 3 new fail-closed integration = 446.

Containers: only this module's generated `pish-p0t04-failclosed-*` containers were
created and each was removed in `finally`; `docker ps -a` shows no P0-T04 test
container remains. `pish_dev`, the pre-existing `pish-hesabdari-dev-db-1` container
and all other volumes were untouched; the locally cached official
`postgres:16.16-bookworm` image was reused and nothing was pulled.

Git: no stage, commit, push or history rewrite. This pass changed only
`backend/alembic/env.py`, `backend/alembic/versions/0001_statutory_baseline.py` and
the new `backend/tests/integration/test_statutory_fail_closed.py`, all inside the
already-untracked P0-T04 paths, plus this entry. Pre-existing staged and unstaged
work was preserved; no unrelated change was committed or reverted.

Status: unchanged — **P0-T04 READY_FOR_REVIEW**, not COMPLETED. P0-T01 CI clause and
the real CI migration job remain unmet; P0-T05 still owns the identity schema and the
validated statutory actor FKs. NOT RUN: production/pish_dev migration,
identity/authentication integration, certified financial corpus, release gate and
production deployment. No 1405 activation, seed change, legal sign-off or
production-readiness claim is made.

---

## 23. Autonomous statutory-engine completion, audit and verification — 2026-11-16

Lead Backend Engineer (autonomous mission). Scope: adopt the uncommitted ADR-008
engine into version control, audit the whole statutory calculation path against the
verified 1404 baseline, correct the defects found, and build the missing test
coverage. No statutory value, seed, ADR-001…007, product scope or legal conclusion
was changed; the 1405 placeholder stays inactive and the certified corpus stays
blocked.

Read for this pass: AGENTS.md; Holy Bible §0.3/§2.3/§2.5/§10.5/§10.6/§13.1/§13.8
and **Appendix A** (the independent recalculation); ADR-006, ADR-007, ADR-008;
EXECUTION_PLAN §7.1/§7.2/§14.3; SPEC-QA-001 §4 (the property table) and §5;
TESTING §3.1 (the money-safety AST gate); the `financial-data-integrity` and
`iranian-payroll-engineering` behaviour contracts; the seeds (read only).

### Version control

| Item | Value |
| :--- | :--- |
| Remote | `https://github.com/tahabehzad/pish-hesabdari` (pre-existing; verified, not recreated) |
| Branch | `autonomous/project-completion` (created for this mission) |
| Push | Every commit was pushed to that branch; **no force-push**, `origin/main` untouched |
| Commits | `55a9547` engine, `3ab4c9f` frontend, `abb4ce6` documentation, `92dc221` the tax fix and the engine test suite, `c42fb9b` the screen fix and its tests, plus this documentation commit |
| `gh` CLI | **NOT RUN** — the stored token is invalid (`gh auth status` → "The token in keyring is invalid"). Git pushes succeed through the credential helper, so the branch is published. `gh auth refresh -h github.com` restores the CLI |
| Secrets | None committed: `.secrets/` and `.env` remain ignored; only `.env.example` is tracked |

### Defects found and fixed

| # | Severity | Defect | Fix | Evidence |
| :-- | :--- | :--- | :--- | :--- |
| E-1 | **Critical** | The progressive tax ladder was offset by one whole exemption: the engine subtracted the monthly exemption from the taxable income and then matched the result against the **absolute** slab edges, although the seed states the ladder in absolute taxable Rial and its first slab *is* the exemption (invariant R-09). Every band therefore sat too high and the tax collapsed to 0 for any base below the first taxable edge. | `StatutoryRuleSet.brackets_above(exemption_rial)` / `shift_brackets_by` express the ladder relative to an exemption; the reduced base is matched against that ladder. The transformation is exact and invertible, and a test asserts the equivalence with the absolute ladder. The Eydi excess is taxed across the same shifted ladder. | Holy Bible Appendix A: A.4 taxable income 277,920,611.60 → tax **3,792,061** (slab 2); A.5 taxable income 377,647,058.87 → tax **17,647,059** (slabs 2 and 3). The engine returned **0** for both before the fix and now reproduces both to the Rial. ADR-008 directive 4 lists the same two figures as the reusable engineering-reference expectations |
| E-2 | **Critical** | The simulation screen — the product's only screen — could never be submitted. Two independent HTML5 constraint violations blocked the form before any request was sent: the gross field carried `min={1}` with `step={100000}` (the seeded 50,000,000 is not `1 + k × 100000`), and the optional liability fields were seeded with `0` while the probation field's minimum is one month. | `step="any"` for the Rial fields; an unset optional field is empty and is sent as `null`; a cleared field returns to `null`. | `frontend/src/routes/simulation-page.test.tsx` — the request is now observed; before the fix the fetch mock was never called |
| E-3 | High | The API client could not read the delivered error envelope `{"error": {"code", "detail"}}`, so every refusal was reported as the generic `VALIDATION_FAILED` and the categorical code was lost. The error catalogue still carried the provisional placeholder codes. | The client reads the nested code and the detail line; the catalogue carries the backend's own codes (`RULE_SET_NOT_ACTIVE`, `PAYROLL_REQUEST_INVALID`, `PAYROLL_INPUT_INVALID`); the screen shows the Persian explanation together with the machine code. | The refusal test asserts `STATUTORY_PARAMETER_UNAVAILABLE` reaches the screen |
| E-4 | High | The loader's active-year gate ran before the seed was inspected, so the 1405 placeholder raised `RuleSetNotActive` and the `StatutoryParameterUnavailable` refusal mandated by ADR-008 directive 3 and by the `P1-T01` acceptance criterion was unreachable. | The refusal kind now follows the state of the requested year: no seed → `RuleSetNotActive`; a seed that exists but is unverified → `StatutoryParameterUnavailable`; a verified seed outside the baseline → `StatutoryParameterUnavailable`. | `tests/unit/test_statutory_rule_loader.py`; live `POST` with `rule_year=1405` → 422 `STATUTORY_PARAMETER_UNAVAILABLE` |
| E-5 | Medium | A negative monetary input was accepted by the SSO, severance, Eydi and tax engines, so a negative statutory figure could be produced. | All four engines refuse a negative input with `PAYROLL_INPUT_INVALID`. | Engine unit tests |
| E-6 | Medium | FastAPI's default validation body echoes the rejected input; on this endpoint the input is a salary package, so a monetary amount could appear inside an error response — the one thing the error contract forbids. | One exception handler returns the documented envelope with the field path and the failure type only. | Live `POST` with a negative gross → 422 `{"error": {"code": "PAYROLL_REQUEST_INVALID", "detail": "body.gross_monthly_rial: greater_than"}}` — no value echoed |
| E-7 | Low | 30 ruff findings in the engine package: ambiguous unicode in docstrings, a dead local in the base decomposition, too many positional arguments, and exception names that the specification binds. | All cleared. The step-mismatch between the two postures was fixed by making the affected arguments keyword-only. `N818` is waived **only** for the error-catalogue module, whose names the specification and ADR-008 directive 3 bind. | `ruff check .` → `All checks passed!` |
| E-8 | Low | The screen re-implemented money and numeral formatting with a local `Intl.NumberFormat` helper, bypassing the project's own `formatMoney` / `toPersianDigits` / `formatPercentFromRate` policy, and rendered the tax bands as mixed Latin/Persian text without the rate. | The screen renders through the project helpers; the band rate is carried in the response as a **string** (`rate`) and the band is rendered as a Persian label with the applied rate. | The logical-utility gate and the typecheck pass; the screen test asserts `پله ۲` |

### Test coverage added

| Layer | File | Content |
| :--- | :--- | :--- |
| L1 unit | `tests/unit/test_statutory_rule_loader.py` | the 1404 baseline, the 1405 refusal, the refusal kinds, invariants R-01…R-10, the month-length variants, the ladder shift, the never-exposed seed literals |
| L1 unit | `tests/unit/test_base_decomposition.py` | the welfare exclusion, the retained attraction, the fail-closed negative base |
| L1 unit | `tests/unit/test_sso_engine.py` | the three rates, the ceiling at and above the boundary, the 29/30/31 variants, property P-04 |
| L1 unit | `tests/unit/test_tax_engine.py` | the two Appendix A reference vectors, the slab boundaries to one Rial, the two postures, properties P-07 and P-08 |
| L1 unit | `tests/unit/test_overtime_engine.py` | the 220 / 227.33 / 212.67 divisors, the multipliers, the excluded welfare |
| L1 unit | `tests/unit/test_severance_engine.py` | the 1/12 accrual, the single rounding, the never-used seed literal, property P-05 |
| L1 unit | `tests/unit/test_eydi_engine.py` | the floor and the cap, the progressive excess, property P-06 |
| L1 unit | `tests/unit/test_employer_cost_engine.py` | the employer-cost identity, the Appendix A corrected total, the absent 26-day reserve |
| L1 unit | `tests/unit/test_termination_engine.py` | the Art. 11 full-probation liability, the days-worked employee liability, the Art. 66/71 leave buyout |
| L1 unit | `tests/unit/test_payroll_service.py` | the five provenance fields, the net and employer-cost identities, the dual posture, the calculation hash, property P-02 and P-10 |
| L2 property | `tests/property/test_engine_properties.py` | properties P-02, P-03, P-04, P-05, P-06, P-07, P-08 and P-10 over 200 examples each |
| L5 contract | `tests/api/test_payroll_simulation.py` | the response envelope, the fail-closed refusals, the error shape, the absence of a float in the response |
| L5 contract | `frontend/src/routes/simulation-page.test.tsx` | the request, the envelope, both postures, the band breakdown, the termination block, the refusal path, the absence of a fractional amount |

### Observed results

| Command | Result |
| :--- | :--- |
| `cd backend && .venv\Scripts\python.exe -m pytest -q` | **PASS** — 548 passed, 104 skipped, 2 third-party deprecation warnings, 16.5 s |
| `cd backend && .venv\Scripts\python.exe -m ruff check .` | **PASS** — `All checks passed!` |
| `cd backend && .venv\Scripts\python.exe -m mypy --strict app tests` | **PASS** — `Success: no issues found in 62 source files` |
| `cd frontend && node_modules\.bin\vitest.cmd run` | **PASS** — 110 passed, 13 files |
| `cd frontend && node_modules\.bin\tsc.cmd --noEmit -p tsconfig.app.json` | **PASS** — exit 0 |
| `cd frontend && node scripts\check-logical-utilities.mjs src` | **PASS** — 69 files, 0 violations |
| `cd frontend && node_modules\.bin\vite.cmd build` | **PASS** — production bundle built |
| `uvicorn app.main:app` + `GET /health/live` | **PASS** — 200 `{"status":"alive"}` |
| Live `POST /api/v1/simulations/gross-to-net` (1404 reference package) | **PASS** — 200; welfare 46,390,968; *Mozd-e Saabet* 295,459,152; employee SSO 23,929,508; conservative tax 5,501,312; Sanavat 24,621,596; Eydi 25,977,420; employer cost 471,074,664 — each equal to the independently derived Appendix A value |
| Live `POST` with `rule_year=1405` | **PASS** — 422 `STATUTORY_PARAMETER_UNAVAILABLE`, no fallback to 1404 |
| Live `POST` with `rule_year=1403` | **PASS** — 422 `RULE_SET_NOT_ACTIVE` |
| Live `POST` with a negative gross | **PASS** — 422 `PAYROLL_REQUEST_INVALID`, no amount echoed |
| Live `POST` with an unknown field | **PASS** — 422 `PAYROLL_REQUEST_INVALID` (`extra_forbidden`) |
| The 104 PostgreSQL integration tests | **NOT RUN** — the official container image cannot be pulled in this environment; the suites skip themselves and report the skip rather than passing silently |
| `gh run list` | **NOT RUN** — the `gh` token is invalid; the workflow has never executed on GitHub |
| Independent review of the monetary changes | **NOT RUN** — AGENTS.md §6 requires review by someone who did not write the change. Every monetary task in this session therefore stops at `READY_FOR_REVIEW` |

### CI

`.github/workflows/ci.yml` runs the backend lint, type and test gates and the
frontend lint, type, test and build gates on push and pull request, with
`contents: read` only. It holds no credential, deploys nothing, migrates nothing
and activates no rule set. It implements DEC-F option (b) — hosted CI for the
**development** repository — which is the option the decision page records as
recommended; the owner confirmation is still open, and the air-gapped verification
checklist (`SPEC-OPS-001` §12) remains the client's responsibility at pilot.

### Task status after this pass

`P1-T01`, `P1-T05`, `P1-T06`, `P1-T07`, `P1-T08`, `P1-T09`, `P1-T10`, `P1-T11`,
`P1-T12`, `P1-T14`, `P1-T16` (engine properties) and `P1-T19` move from
`NOT_STARTED` to `READY_FOR_REVIEW`: the implementation and the acceptance
evidence exist and are verified locally, but AGENTS.md §6 requires independent
review before any of them can be marked `APPROVED`. `P1-T02` and `P1-T15` remain
`BLOCKED` on external signatures; `P1-T03` stays gated on `P1-T02`.

No 1405 activation, seed change, legal sign-off, certified corpus, release gate
or production-readiness claim is made.

---

## 24. Statutory-engine remediation pass (review findings A-1…A-13) — 2026-11-16

Lead Backend Engineer (autonomous remediation). Scope: re-verify every finding
of the independent monetary review against the current tree, fix only the
verified defects, add a regression test for each, and correct the evidence
record. No seed, ADR-001…008, product boundary or legal conclusion was changed;
1405 stays unloadable and the certified corpus stays blocked. No commit or push
was made in this pass.

Read for this pass: `AGENTS.md`; Holy Bible §2.3/§2.5/Appendix A, §13.1 and
§13.8; ADR-008; EXECUTION_PLAN §7.1–7.3/§14.3; TESTING §4.2/§4.3; the seeds
(read only); every engine, service, schema and API module; the test tree.

### 24.1 Defects fixed

| ID | Verified defect | Correction | Regression evidence |
| :-- | :--- | :--- | :--- |
| A-1 | The signed residual compared `total_gross - net` with the same lines (always an identity), and the published tax total did not equal the sum of its slab lines | Residual = `sum(rounded deduction lines) - round(exact total)`; published tax = sum of rounded slab lines; exact total and signed residual published per posture | `test_the_tax_breakdown_sums_to_the_published_total`, `test_the_employee_deduction_residual_is_not_a_tautology`, API `test_the_response_tax_lines_reconcile` |
| A-2 | Provenance covered seven block keys only | Field-level provenance keyed by JSON path for every derived monetary line (including both postures and every slab), block keys retained | `test_the_provenance_covers_every_field_level_path` |
| A-3 | The termination total summed mutually exclusive probation lines with the separation lines | `TerminationScenario` (`probation_employer_initiated`, `probation_employee_initiated`, `ordinary_termination`); one applied line + separation = `total_liability_rial` | Termination scenario tests; API scenario tests |
| A-4 | Leave buyout divided by the calendar month length | `STATUTORY_DAILY_WAGE_DIVISOR_DAYS = 30`, published as `daily_wage_divisor_days` | `test_the_leave_buyout_uses_the_statutory_thirty_day_divisor` |
| A-5 | The Art. 137 “exact base” test could pass on either base (±1 tolerance against rounded+1) | A deliberately discriminating fixture (rounding the SSO share changes the deduction by 1 Rial) asserts the exact value | `test_the_article_137_deduction_uses_the_exact_sso_share` |
| A-6 | Float `/ 12` and Python `round()` in Eydi/property tests | Decimal division and `ROUND_HALF_UP` | `test_the_monthly_accrual_is_the_annual_over_twelve`, P-05 property |
| A-7 | R-01 compared a property with its defining expression | The seed's independent 30-day ceiling is loaded and compared; the invariant can now fail | `test_the_insurable_ceiling_invariant_is_independent` |
| A-8 | A test named “true at the cap” asserted `False` | Renamed to the actual meaning; true-above-cap case added; behaviour unchanged (the flag means the cap truncated the accrual) | Eydi cap tests |
| A-9 | `TaxableBaseNegative` was unreachable; engines raised bare `ValueError`/`TypeError`; the API collapsed the code | One taxonomy under `PayrollEngineError` (subclasses `ValueError` for historical compatibility) with a stable `code`; the API reads `code` | Tax/engine/API refusal tests |
| A-10 | Loaded allowance floors, child floor and seniority base were never surfaced | `statutory_reference` + `statutory_parameter_usage`, `applied_to_net=false`, link to proposed DEC-013 | `test_the_statutory_reference_is_published_but_not_applied`, `test_the_rule_set_usage_is_published` |
| A-11 | A stored result could not be re-verified against the exact parameter values | Optional injected rule set, `rule_set_fingerprint()` (SHA-256 of canonical parameters) published; injection must match the request year | `test_the_rule_set_fingerprint_is_published`, `test_an_injected_rule_set_is_used_and_must_match_the_year` |
| A-12 | §23's evidence claims were broader than the implementation (residual, provenance, contract suite) | This section corrects the record; §23 is preserved as history | This table |
| A-13 | The loader test mutated the lru-cached 1404 rule set; the contract test could not collect | `dataclasses.replace` copy plus a cache-intact assertion; contract test uses `force_schema_version="30"`, a path regex and skips contract-valid negative cases | `test_an_invariant_violation_fails_closed`; `tests/api/test_openapi_contract.py` |

### 24.2 Published contract changes

The response now carries `rule_set_status_source`, `rule_set_fingerprint`,
`insurable_base`, `statutory_reference`, `statutory_parameter_usage`,
`rounding_residual_scope`, per-posture exact tax/residual/clamp fields, a typed
`severance_sanavat`/`eydi`/`employer_cost` block, and the reconciled
termination block. The request accepts optional `termination_scenario` and
`recognised_service_years`. `ENGINE_VERSION` is `0.3.0-payroll-engine`.
Refusal codes are now specific (`BASE_DECOMPOSITION_NEGATIVE`,
`PAYROLL_MONTH_LENGTH_INVALID`, `PROBATION_BEYOND_STATUTORY_MAX`,
`TAXABLE_BASE_NEGATIVE`, …); the historical `ValueError` catch still works.

### 24.3 Exact commands and observed results (PASS / FAIL / NOT RUN)

| Command | Result |
| :--- | :--- |
| `cd backend; .\.venv\Scripts\python.exe -m pytest -q` (baseline, before fixes) | **FAIL** — collection error in `tests/api/test_openapi_contract.py` (schemathesis rejects OpenAPI 3.1.0) |
| `cd backend; .\.venv\Scripts\python.exe -m pytest -q` (after fixes) | **PASS** — 568 passed, 105 skipped, 9 warnings, 18.69 s |
| `cd backend; .\.venv\Scripts\python.exe -m ruff check .` | **PASS** — `All checks passed!` |
| `cd backend; .\.venv\Scripts\python.exe -m mypy --strict app tests` | **PASS** — `Success: no issues found in 64 source files` |
| PostgreSQL integration suites | **NOT RUN** — Docker daemon unavailable; 104 suites self-skip with an explicit NOT RUN reason |
| `cd backend; .\.venv\Scripts\python.exe -m pytest -q` (final re-run after the documentation reconciliation) | **PASS** — 568 passed, 105 skipped, 9 third-party warnings |
| Markdown table and local-link check on the changed documents | **PASS** — pipe counts consistent; no missing relative link. Pre-existing malformed tables in `ENVIRONMENT_INVENTORY.md` and the Holy Bible were left untouched |
| Frontend test/typecheck/build | **NOT RUN in this pass** — no frontend file changed; last evidence remains §23 |
| Independent review by a non-author | **NOT RUN** — unavailable; AGENTS.md §6 keeps every engine task at READY_FOR_REVIEW |

### 24.4 Corrections to §23

1. §23 reports “548 passed, 104 skipped”; the suite is now 568/105 because 20
   regression/contract tests were added and the contract test now collects.
2. §23's statement that “every figure carries provenance” was true only for
   seven block keys; §24.1 A-2 records the actual coverage and the fix.
3. §23's `rounding_residual_rial` claim (“signed residual surfaced”) did not
   state that the old value was an identity; A-1 records the correction.
4. §23's “Schemathesis + contract suite” evidence referred to a test file that
   did not collect and was untracked; A-13 records the repair.
5. No legal, seed or scope statement in §23 is changed.

### 24.5 Task status after this pass

No task moves to `COMPLETED` or `APPROVED`. `P1-T01`, `P1-T05`–`P1-T12`,
`P1-T14`, `P1-T16` and `P1-T19` remain `READY_FOR_REVIEW` with stronger
evidence; independent review and the PostgreSQL integration run are still
required. `P1-T02`/`P1-T15` remain `BLOCKED`; `P1-T03` remains gated.

### 24.6 Documentation reconciliation (2026-11-16)

The delivery documents were re-read against the tree after the code fixes. The
following factual corrections were made; no code, seed, ADR or legal statement
changed in this documentation pass.

| Document | Correction |
| :--- | :--- |
| `docs/PROJECT_STATUS.md` | §2 now cites §24, reports **568 passed / 105 skipped**, 64 strict-typed files and the new contract/fingerprint/provenance evidence; the engine is no longer described as absent. §3 records the uncommitted remediation set; §6 arithmetic reconciled to 19 register entries; §7 records the written/verified migration and the never-executed CI; §9 replaces the pre-engine statements with the enforced loader, the non-consumed flat Eydi rate and the local (not certified) evidence posture; §10 states the ADR-008 v1 boundary correctly |
| `docs/EXECUTION_PLAN.md` §14.3 | `P1-T01` (R-01 independence, R-11 divisor, fingerprint, cache-mutation test), `P1-T04` (tautological residual replaced), `P1-T05` (slab-total reconciliation), `P1-T09` (cap-test meaning, Decimal accrual), `P1-T12` (scenario model + 30-day divisor), `P1-T14`, `P1-T16` (Decimal P-05) and `P1-T19` (collecting contract suite, per-field provenance, reconciled residual) cite §24; no status or dependency changed |
| `docs/DECISIONS_REGISTER.md` | Summary arithmetic corrected: the 19 listed rows are **11 open (7 blocking, 4 non-blocking), 6 resolved and 2 rejected**, not “12 open / 5 resolved”. DEC-013 and the B-1…B-11 ledger are unchanged in substance |
| `docs/DECISION_REQUIRED_FROM_OWNER.md` | The register summary now says 19 entries / 11 open / 6 resolved / 2 rejected and surfaces proposed DEC-013 as a non-blocking owner question; v1 keeps the floors and seniority base reference-only |
| `docs/IMPLEMENTATION_READINESS.md` | Census refreshed to **1 COMPLETED / 6 IN_PROGRESS / 17 READY_FOR_REVIEW / 58 NOT_STARTED / 4 BLOCKED / 0 APPROVED**, the “financial engines do not exist” statement removed, and a malformed 5-column table header corrected to 4; the verdict remains **NOT implementation-ready** because 11 decisions, external acquisitions and a phase-gate evidence pack are still absent |

Checks: the final `pytest -q` re-run passed (568/105), `ruff check .` and
`mypy --strict app tests` (64 files) remained green, and a pipe-count/local-link
check on the changed documents found no new defect. The uncommitted state is
unchanged: no commit or push was made.

## 25. P0-T07 blind index, and the Batch-01 scope conflict — 2026-11-16

**Directive.** An autonomous "Batch 01" instruction asked for four application
modules: authentication/authorization, company management, the accounting
foundation (chart of accounts, periods, journal entries) and a data-backed
dashboard.

**Finding — the request contradicts an accepted decision.** `AGENTS.md` §1 and
ADR-008 (Accepted) fix the product boundary as the statutory payroll engine
plus one minimal endpoint, with *no frontend requirement*; ADR-004's module
list is superseded. Modules A–D are that superseded platform scope plus an
accounting module no ADR has ever authorised, and their implementation would
also encode decisions the register still holds open (`P0-T08` key hierarchy,
`P0-T18` session contract, `P0-T09` RLS/context ordering). Per `AGENTS.md` §11
the affected work was stopped and the conflict was raised as **DEC-014**
(`OPEN — BLOCKING`), rather than silently choosing an implementation. No
authentication, company, accounting or dashboard code was written in this
pass.

**Work delivered instead — the in-scope, unblocked foundation gap.** `P0-T07`
(the HMAC-SHA256 blind index required by `AGENTS.md` §2 invariant 13) did not
exist in the tree. It is a prerequisite for any identity work and carries no
open decision: the corpus explicitly assigns the normalisation rule to this
task (Holy Bible §5.6, QB-10, HB-MR-011).

| Artifact | Change |
| :--- | :--- |
| `backend/app/core/security/blind_index.py` | New. `BlindIndexPepperRegistry` (injected pepper, ≥ 32 bytes, no cache, no default, no database derivation), `BlindIndexService.index(value, *, tenant_id, field)` returning lowercase hex of 64 characters, `normalise(value, *, field)` publishing the canonical form, and the `national_id`/`mobile`/`sheba` rule. Message = `pish:bindex:v1` NUL tenant hex NUL field NUL canonical value, HMAC-SHA256. Fixed failure messages; no logging or I/O. |
| `backend/tests/unit/test_blind_index.py` | New. 45 tests: determinism; every documented spelling of one identifier collapsing to one digest (Persian, Arabic-Indic, fullwidth, ZWNJ, separators, bidi controls, `+98`/`0098` mobile forms, Sheba grouping/case); leading zeros significant; tenant and field separation (with an independently spelled message in the test); malformed identifier refused with no value in the message or traceback; unusable/missing pepper fails closed with exactly one registry call; no output on the success path. |
| `backend/ruff.toml` | `RUF001` added to the tests-only per-file ignores, because the fixtures are deliberately confusable numeral forms; the reason is recorded in the file. No product code exemption was added. |
| `docs/specs/AUTH.md` | New §8.6 publishing the P0-T07 contract and the normalisation rule (HB-MR-011), including the §8.1-per-tenant-salt / §8.2-single-pepper reconciliation and the NOT-RUN list; §12 rows for P0-T06/P0-T07 corrected to their real status. |
| `docs/EXECUTION_PLAN.md` §14.3 | `P0-T07` evidence column, blocking issues and status (`READY_FOR_REVIEW`). |
| `docs/PROJECT_STATUS.md` | Tests row (613/105, 66 strict files), a new PII-lookup row, and the working-tree row corrected to commit `f31e01e`. |
| `docs/DECISIONS_REGISTER.md` | New **DEC-014** and the census corrected to 20 entries (12 open, 8 blocking). |

**Verification (observed in this pass).**

| Command | Result |
| :--- | :--- |
| `./.venv/Scripts/python.exe -m pytest tests/unit/test_blind_index.py -q` | **PASS** — 45 passed |
| `./.venv/Scripts/python.exe -m pytest -q` | **PASS** — 613 passed, 105 skipped, 9 third-party warnings, 32.37 s |
| `./.venv/Scripts/python.exe -m ruff check .` | **PASS** — `All checks passed!` |
| `./.venv/Scripts/python.exe -m ruff format --check` (new files) | **PASS** — no reformat needed after `ruff format` |
| `./.venv/Scripts/python.exe -m mypy --strict app tests` | **PASS** — `Success: no issues found in 66 source files` |
| PostgreSQL integration suites (104 tests + contract skips) | **NOT RUN** — Docker daemon unavailable; the suites self-skip. CR-05 database evidence and the < 1 ms B-tree are therefore unverified |
| Frontend suite / build | **NOT RUN** — no frontend file changed in this pass |
| Independent security review of the new module | **NOT RUN** — no second reviewer is available in this environment |

**Status.** `P0-T07` is `READY_FOR_REVIEW`: implementation and local tests are
verified; pepper custody/rotation (`P0-T08`), the database-level CR-05 evidence,
the B-tree timing and independent review remain outstanding, so the task is not
`APPROVED` and does not complete `P0-T15` or the Phase 0 gate. No commit or push
was made; the working tree carries this pass, and `.obsidian/` plus
`Project Knowledge/` remain untracked.

## 26. Operational roadmap (advisory) — 2026-11-16

**Directive.** Write a prioritised roadmap that separates in-domain work from
work blocked by a legal/tax determination.

**Artifact.** `docs/ROADMAP_OPERATIONAL_PAYROLL.md` (`DOC-ROADMAP-001`), listed
in `docs/DOCUMENTATION_INDEX.md` §0 and §1.1.

**Content.** Eight measurable conditions for operational usability (U1–U8,
each marked met/not met against the tree); four tracks — A: in-domain and
unblocked (`P0-T09`, `P0-T10`, `P0-T14`, `P0-T15`, `P0-T16`, `P0-T19`, plus the
readiness probe and the money AST gate); B: blocked by a determination
(DEC-001/002 with `P1-T02`/`P1-T03`, B-2…B-8, DEC-013, DEC-011c, and the
**unregistered monthly-vs-annual-cumulative tax question**, which must be added
to the register before any implementation); C: operational premises (Docker,
CI execution, independent reviewer, external advisors); D: outside ADR-008
(persistence of employees/runs/payslips, login as a feature, inverter, export).
Six milestones with non-documentary exit criteria, a sequencing rationale, a
WBS-only effort snapshot and a risk table.

**Boundary respected.** The roadmap creates no task, resolves no decision,
changes no status and authorises no scope. Track D is routed to DEC-014 and a
superseding ADR, not to a backlog. The proposed monthly-vs-annual tax item is
recorded as **not yet a register entry** rather than being invented as DEC-015.

**Verification.** Documentation-only: every command, count and status cited was
read from the tree or from §24/§25 evidence; no application test, migration or
build was executed for this document, so no test result is claimed. No commit
or push was made.

## 27. ADR-009 compensation advisory module — 2026-11-16

**Directive.** The owner asked for an engine that takes a person's information
and, from that person's skills and experience, proposes a salary; the only user
is the manager; the output must be a proposed range plus its statutory cost;
the change is to be recorded as an ADR first.

**Scope decision.** ADR-009 (Accepted, Project Owner) **extends** ADR-008 and
removes nothing: the engine, the seed, the statutory figures and every
invariant are untouched. Market benchmarking (DEC-007/DEC-008) stays rejected,
document ingestion stays out, and pricing-without-a-band was refused as an
option because any such number would be invented. DEC-014 (authentication,
company, accounting, dashboard) is unaffected and remains open.

| Artifact | Change |
| :--- | :--- |
| `docs/adr/ADR-009-compensation-advisory-module.md` | New. Boundary, the four considered options, the published model, the band rule, directives and consequences. |
| `backend/app/engines/valuation.py` | New. `valuation-v1`: weighted score over total experience (÷120 months), relevant experience (÷84), skill level (÷5) and education (six bands); band placement and the `± 5 %` published range clamped to the band; typed refusals. Pure, Decimal, no float literal, no clock. |
| `backend/app/engines/errors.py` | `ValuationError` and four subclasses with stable codes, inside the existing taxonomy. |
| `backend/app/services/valuation_service.py` | Composition only: score → band → **existing** `compute_gross_to_net` at the lower bound, point and upper bound; advisory envelope; statutory floor published, never applied. |
| `backend/app/schemas/valuation.py` | Request/response contracts: integer Rial, rates and scores as strings, `advisory`/`statutory` flags, `extra="forbid"`. |
| `backend/app/api/v1/valuation.py`, `backend/app/main.py` | `POST /api/v1/valuations/compensation-proposal` registered; clock read at the boundary only; single error shape. |
| `backend/tests/unit/test_valuation_engine.py`, `backend/tests/api/test_valuation_api.py` | New suites. |
| `docs/ADR_INDEX.md` | ADR-009 row added; the missing **ADR-007** row was restored (it existed as a file but was absent from the register table). |
| `docs/EXECUTION_PLAN.md` §14.3 | New "Phase 5 — Compensation advisory module" with `P5-T01`/`P5-T02` (`READY_FOR_REVIEW`). |
| `docs/DECISIONS_REGISTER.md` | DEC-009 updated with ADR-009's bounded reading (stays open); DEC-014 updated to record that ADR-009 does not resolve it. |
| `docs/PROJECT_STATUS.md`, `docs/ROADMAP_OPERATIONAL_PAYROLL.md` | Delivery row and test counts; the roadmap notes the module does not change U1–U8. |

**Verification (observed in this pass).**

| Command | Result |
| :--- | :--- |
| `pytest tests/unit/test_valuation_engine.py tests/api/test_valuation_api.py -q` | **PASS** — 65 passed |
| `pytest -q` | **PASS** — 678 passed, 105 skipped, 9 third-party warnings, 34.07 s |
| `ruff check .` | **PASS** — `All checks passed!` |
| `ruff format` on the new/changed files | **PASS** — 4 reformatted, 3 unchanged (the wider repository is not format-clean and was deliberately not reformatted) |
| `mypy --strict app tests` | **PASS** — `Success: no issues found in 72 source files` |
| Cross-endpoint replay | **PASS** — the proposal's point costing reproduces `net_rial`, `income_tax_rial`, employer cost **and** `calculation_hash` through `POST /api/v1/simulations/gross-to-net` |
| PostgreSQL integration suites | **NOT RUN** — Docker daemon unavailable |
| Frontend suite / build | **NOT RUN** — no frontend file changed; the module has no UI |
| Independent review, authentication, persistence | **NOT RUN / absent** — `P5-T01`/`P5-T02` stay `READY_FOR_REVIEW`; the endpoint is a trusted-operator surface until `P0-T18` lands |

**Limits stated in the response itself.** Every proposal carries
`advisory: true`, `statutory: false`, the model version, the weights and each
weighted contribution; the statutory floor is published with
`range_low_below_statutory_minimum` and never applied (DEC-013); no market,
benchmark or actuarial data is used. The score is a policy heuristic, not a
verdict about a person.

**Version control.** No commit and no push. The working tree now carries the
§25 and §27 sets plus this change.

## 28. Minimal manager UI for the proposal engine — 2026-11-16

**Directive.** Make the project previewable with a clean, fast frontend: a sign-in
screen and a salary screen, minimal scope, finished quickly.

| Artifact | Change |
| :--- | :--- |
| `frontend/src/routes/manager-login-page.tsx` | New. Persian RTL manager gate. **Presentation-only**: it stores a session-scoped name and states on the card that no credential is verified, because no identity endpoint exists (`P0-T18`). Mounted at `/login`, replacing the previously disabled sign-in screen. |
| `frontend/src/routes/proposal-page.tsx` | New. One form (total/relevant experience, skill level, education, monthly band in Toman) → `POST /api/v1/valuations/compensation-proposal` → score, proposed range and a three-column table of gross, employee SSO, tax, net and employer cost. Every figure comes from the response; nothing is computed in the browser. |
| `frontend/src/api/errors.ts` | The five valuation codes added to `ErrorCode` and the Persian catalogue, so a refusal keeps its meaning on screen instead of collapsing to `UNKNOWN`. |
| `frontend/src/app/router.tsx` | `/login` now renders the manager gate; `/proposal` added as a top-level route. |

**Verification (observed).** `tsc --noEmit` PASS; `vitest run` **115 passed / 13 files**;
logical-utility lint **0 violations**; dev server on `127.0.0.1:5274` with
`VITE_API_BASE_URL=http://127.0.0.1:8001` served the preview, the login navigated to the
proposal screen, the submit issued `POST … → 200`, the table rendered five rows and the
browser console was clean. A stale Vite child process was terminated with `taskkill` after
its port was confirmed free; no other process was touched. The pre-existing listener on
port 8000 was left alone, so the API for this preview runs on 8001 with an explicit
`ALLOWED_ORIGINS` for 5274.

**Scope statement.** The screens are a local preview of the advisory module. They are not
`P3-T01…P3-T06` completion, not a security control, and not a deployment. No commit or push.

## 29. Context and token optimization pass — 2026-11-16

**Directive.** Optimize the project structure and development workflow to minimize AI
token and context consumption while preserving project integrity, security and existing
functionality. Documentation, ignore rules and regenerable caches only: no application
code, migration, seed, database record or business rule was touched.

### Documentation set (minimal)

| Artifact | Change |
| :--- | :--- |
| `AGENTS.md` | New §0 (language), §12 (language and communication), §13 (context and token discipline, 11 rules), §14 (documentation set and single-owner rule), §15 (coding conventions), §16 (git safety); ADR-009 added to the accepted set in §1. Existing §§1–11 unchanged. |
| `PROJECT_STATE.md` | New derived snapshot `DOC-STATE-001`. Holds no independent facts; names `PROJECT_STATUS`, `EXECUTION_PLAN §14.3`, `DECISIONS_REGISTER`/`adr/` and `BOOTSTRAP_CHANGELOG` as owners. |
| `README.md` | Scope paragraph corrected from the superseded ADR-004 boundary to ADR-008; `PROJECT_STATE.md` added to the reading table and the repository layout; ADR-009 added to the accepted set. Test counts left to `BOOTSTRAP_CHANGELOG` instead of being duplicated here. |
| `docs/DOCUMENTATION_INDEX.md` | §0 routing row and §1.1 note for `PROJECT_STATE.md`, explicitly ranked below every authority and marked non-authoritative. |
| `PROJECT_HANDOFF_SUMMARY.md` | Marked as a historical snapshot superseded by `PROJECT_STATE.md`/`PROJECT_STATUS.md`; retained for traceability, not to be loaded for current state. |

### Repository hygiene

| Action | Detail |
| :--- | :--- |
| `.gitignore` | Added `.obsidian/` and `Project Knowledge/` (local editor/vault artifacts and a parallel non-authoritative knowledge layer). No tracked file became ignored. |
| Cache removal | Removed root `.mypy_cache/` (66,197 KB), `backend/.mypy_cache/` (97,309 KB), `backend/.ruff_cache/`, `backend/.pytest_cache/`, `infra/postgres/.ruff_cache/` and 19 `__pycache__/` directories outside `.venv`/`node_modules`. All are regenerable and were git-ignored. |
| Preserved | `.venv/`, `node_modules/`, `.hypothesis/`, `frontend/dist/`, `.freebuff/` statutory acquisition evidence, `.secrets/`, and every uncommitted source change. |
| Local tool | Installed `ripgrep` 15.2.0 (winget, `BurntSushi.ripgrep.MSVC`) so the `rg` commands in `AGENTS.md` §13 and `DOCUMENTATION_INDEX` §0 resolve on this machine. No paid service, no project dependency. |

### Verification (observed)

| Result | Command / check | Evidence |
| :--- | :--- | :--- |
| PASS | relative-link resolution in `AGENTS.md`, `README.md`, `PROJECT_STATE.md`, `docs/DOCUMENTATION_INDEX.md` | every `](path)` target exists on disk; no dead link introduced |
| PASS | `git check-ignore -v .obsidian/app.json "Project Knowledge/Project Home.md"` | matched `.gitignore:55` and `.gitignore:56` |
| PASS | `git status --porcelain -uall` census | untracked entries dropped 32 → 13; modified 15 → 16 (`.gitignore`); no source file lost |
| PASS | `rg --version`; `rg -l StatutoryParameterUnavailable backend/app backend/tests` | ripgrep 15.2.0; 5 files found, gitignore-respecting |
| PASS | factual cross-check of snapshot claims against owners | ADR-009 Accepted, 0 of 5 phase gates, engine review-ready — all match `PROJECT_STATUS` §2 and `ADR_INDEX` |
| NOT RUN | backend pytest / ruff / mypy, frontend vitest / tsc / build | documentation-and-ignore-only pass; no application code, dependency or schema changed. Not a fresh runtime check and does not revalidate §28. |

### Scope statement

No commit, no push, no amend, no reset. No deletion of a tracked file: the handoff summary
was annotated rather than removed because removal would rewrite history and it is still a
record of the phase-1 handoff. No change to application behaviour, business logic, database
structure, financial calculation or architecture. This entry does not complete any WBS task
and does not pass a phase gate.
