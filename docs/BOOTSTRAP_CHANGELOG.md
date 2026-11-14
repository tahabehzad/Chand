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
| Files modified | 0 |
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
| C-29 | Merge into `main` | `git merge --no-ff bootstrap/initial-import` | **PASS** — merge commit, history preserved | Reversible (`git reset --hard <sha>`) |

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
| V-27 | Re-hash of all 40 pre-existing files against the §2 baseline | **PASS** — 40/40 byte-identical, 0 changed, 0 missing |
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
| Branch | `bootstrap/initial-import` |
| Files committed | 72 |
| Merge | `--no-ff` into `main` |
| Remote | **none** — nothing was pushed |
| Rollback | `git reset --hard <the pre-merge sha>` restores the tree; `git reflog` lists both commits |

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
