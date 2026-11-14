# Environment Inventory — Pish Hesabdari

- **Document ID:** `DOC-ENV-001`
- **Status:** Active — verified by execution, not by assumption
- **Verified on:** 2026-11-14 (23 Aban 1405 SH) by direct execution on the developer workstation — re-verified in session 2 after `uv sync` (DEC-A)
- **Scope:** The machine on which Phase 0 development will occur
- **Related:** `docs/PISH_HESABDARI_HOLY_BIBLE.md` §0.4, §4.12 · `docs/specs/DEPLOYMENT.md` §2

> **Method.** Every row below was produced by *running* the tool and reading its output. A tool that merely appears on `PATH` is marked as such. No credential, token or secret value was read, printed or transmitted during this verification.

---

## 1. Summary

| Class | Count | Items |
| :--- | --: | :--- |
| **Installed and verified working** | 12 | Git, Python 3.12/3.13/3.14, uv, pip, Node, npm, corepack, Docker CLI, Docker Compose, WSL2, VS Code, **the `backend/.venv` toolchain** |
| **Installed but the service is not running** | 2 | Docker Desktop engine (CLI present, daemon down), WSL2 (distro present, backend idle) |
| **Available but not configured** | 3 | `pnpm` (via corepack 0.35.0), Claude Code, Codex |
| **Not installed** | 9 | `psql`/`pg_ctl`/`createdb`, `make`, `jq`, `rg`, `pipx`, `yarn`, `podman`, `gemini`, `aider`/`cursor` |
| **Not present as a CLI** | 1 | Antigravity (see §5 — the Freebuff tooling is the closest equivalent) |

---

## 2. Installed and verified working

| Component | Detected | Version | Path | Role in this project | Issues |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Git** | yes | `2.55.0.windows.5` | `C:\Program Files\Git\cmd\git.exe` | VCS, branch protection, worktrees | Initialised on `main` in session 1; the **first commit** was made in session 2 on `bootstrap/initial-import` and merged into `main`. No remote is configured and **nothing has been pushed**. |
| **uv** | yes | `0.13.8` (3d97a6aad, 2026-11-12, x86_64-pc-windows-msvc) | `C:\Users\Asus\.local\bin\uv.exe` | Dependency management, lockfile, venv | None. Verified: `uv lock` resolved 166 packages; `uv lock --check` passes; **`uv sync --frozen --all-groups` installed 118 packages** into `backend/.venv` (session 2, DEC-A). |
| **Python (managed by uv)** | yes | `CPython 3.12.9` | `C:\Users\Asus\AppData\Roaming\uv\python\cpython-3.12.9-windows-x86_64-none\python.exe` | **The backend runtime.** Matches the `python:3.12-slim` production image in `SPEC-OPS-001` §3.1 | None. |
| **Python (system)** | yes | `3.13.14` (`python`, `python3`) · `3.14.5` (`py`) | `C:\Users\Asus\AppData\Local\Microsoft\WindowsApps\` | Fallback only | The default `python` is **3.13.14**, not 3.12. `requires-python` is pinned to `>=3.12,<3.14`, so the system interpreter must **not** be used directly — always go through `uv`. |
| **Python (system, 32-bit)** | yes | `3.14.5` | `C:\Users\Asus\AppData\Local\Programs\Python\Python314-32\` | — | 32-bit. **Do not use.** |
| **pip** | yes | `26.1.2` | `C:\Users\Asus\AppData\Local\Microsoft\WindowsApps\pip.exe` | Emergency fallback only | Prefer `uv`; `uv sync --frozen` is the only permitted install path. |
| **Node.js** | yes | `v24.20.0` | `C:\Program Files\nodejs\node.exe` | Frontend build toolchain | Node 24 is newer than the Node 20 in ADR-001's Docker directive. The directive governs the **container**, not the developer workstation. |
| **npm** | yes | `11.19.0` | `C:\Program Files\nodejs\npm` | Fallback package manager | The spec mandates `pnpm`. See §3. |
| **corepack** | yes | `0.35.0` | bundled with Node | Can provision `pnpm` | `pnpm` not yet enabled — enabling it modifies the global Node install and needs approval (DEC-C). |
| **Docker CLI** | yes | `29.9.2` (build a82e528) | `C:\Program Files\Docker\Docker\resources\bin\docker.exe` | Local PostgreSQL + object store (WBS P0-T03, P0-T17) | **The daemon is not running** — see §4. |
| **Docker Compose** | yes | `v5.6.1` | bundled with Docker | `infra/compose/compose.dev.yml` orchestration | Requires the daemon. |
| **WSL2** | yes | default version 2; distro `docker-desktop` | `C:\Windows\System32\wsl.exe` | Docker Desktop's Linux backend | The distro is present but idle. |
| **VS Code** | yes | — | `C:\Users\Asus\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd` | Editor | — |

## 2.1 The project virtual environment (session 2)

| Item | Value | Verified by |
| :--- | :--- | :--- |
| Path | `backend/.venv` (git-ignored) | `Test-Path backend\.venv` |
| Interpreter | CPython 3.12.9, uv-managed | `uv run python -c "import sys; print(sys.version)"` |
| Packages installed | **118** | `uv sync --frozen --all-groups` → `Checked 118 packages` |
| Lockfile | `backend/uv.lock`, **166** packages resolved, current | `uv lock --check` → `Resolved 166 packages` |
| `ruff` | 0.17.5 | `uv run ruff check .` → `All checks passed!` |
| `mypy` | 1.20.2, `strict = True` | `uv run mypy app tests` → `Success: no issues found in 11 source files` |
| `pytest` | 8.4.2 | `uv run pytest -q` → `34 passed` |
| `fastapi` / `pydantic` | 0.162.7 / 2.14.3 | `uv run python -c "import fastapi, pydantic"` |
| Native wheels | **Resolved.** `argon2-cffi`, `cryptography` and `asyncpg` all installed on Windows without a compiler | `uv sync` exit 0 |
| Rollback | `Remove-Item -Recurse -Force backend\.venv` | — |

## 3. Available but not configured

| Component | Detected | Version | Available via | Role | Issues |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **pnpm** | no | — | `corepack enable pnpm` (corepack 0.35.0 present) | The **spec-mandated** frontend package manager (`SPEC-OPS-001` §2.4) | Enabling corepack modifies the global Node installation. Requires owner approval (DEC-C). Until then, `npm` is the fallback and the lockfile type must not be committed as `pnpm-lock.yaml`. |
| **Claude Code** | yes | `2.1.300` | `C:\Users\Asus\.local\bin\claude.exe` | External coding agent | Has a `PreToolUse` Bash hook (`rtk hook claude`). **Not yet validated** for safe, non-interactive orchestration of this repository — see §6. |
| **Codex CLI** | yes | `codex-cli 0.169.0` | `C:\Users\Asus\AppData\Local\Programs\OpenAI\Codex\bin\codex.exe` | External coding agent | MCP servers configured: `node_repl`, `headroom`. **Not yet validated** for this repository. |

## 4. Installed but the service is not running

| Component | Detected | State | Evidence | Impact |
| :--- | :--- | :--- | :--- | :--- |
| **Docker Desktop engine** | yes | **DOWN** | `docker info` → `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine`; context `desktop-linux` is selected and shows this error | **No container can be started.** `infra/compose/compose.dev.yml` cannot bring up PostgreSQL 16 or the S3-compatible object store. WBS `P0-T03`, `P0-T16`, `P0-T17` cannot be exercised locally until Docker Desktop is started. |
| **WSL2 backend** | yes | present, idle | `wsl --list --quiet` → `docker-desktop` | Will be used when Docker Desktop starts | Low. |

## 5. Not installed / not present

| Component | State | Consequence | Workaround |
| :--- | :--- | :--- | :--- |
| `psql`, `pg_ctl`, `createdb` | **not installed** | No native PostgreSQL client on the host | Access PostgreSQL **only** through a container (`docker exec`) once the daemon is up. No host-level `psql` in the documented setup path. |
| `make` | not installed | Makefile targets unavailable | Use the explicit `uv`/`npm` commands in `README.md` and `SPEC-OPS-001` §2.3 |
| `jq` | not installed | No shell JSON pretty-printing | Use `python -c` / `node -e` |
| `rg` (ripgrep) | not installed | No fast recursive grep | `Select-String` (PowerShell) / `git grep` after the first commit |
| `pipx` | not installed | No isolated CLI installs | `uv tool install` |
| `yarn` | not installed | — | npm / pnpm |
| `podman` | not installed | No daemonless alternative to Docker | Docker Desktop must be started |
| `gemini`, `aider`, `cursor` | not installed | — | The three CLIs in §3 cover the requirement |
| **Antigravity** | **not present as a CLI** | The brief refers to "Antigravity agent/team functionality" | The closest equivalent in this environment is the **Freebuff** tooling (`freebuff` npm shim on `PATH`; `.freebuff/project-id` present in the workspace) plus the three verified coding CLIs. See `docs/AGENT_OPERATING_MODEL.md` §5. |

## 6. Agent tooling and MCP servers

| Surface | Verified | Configuration observed | Orchestration safety |
| :--- | :--- | :--- | :--- |
| **opencode** | yes, `v2.2.5` | `~/.config/opencode/opencode.jsonc`; one local MCP server: `browser-control-mcp` (`type: local`) | **This session runs here.** Safe: all work is in the shared workspace. |
| **Codex** | yes, `0.169.0` | `~/.codex/config.toml`; MCP servers: `node_repl`, `headroom` | **Not yet exercised.** Before delegating work to it, confirm it operates on the same working tree and does not create a competing Git state. |
| **Claude Code** | yes, `2.1.300` | `~/.claude/settings.json`; `PreToolUse` Bash hook `rtk hook claude` | **Not yet exercised.** The same working-tree check applies. |
| **Git worktrees** | yes | Verified by executing `git init` + `git worktree list` in a scratch directory | **Available and verified.** This is the isolation mechanism for parallel agents once the first commit exists (a worktree needs a commit to branch from). |
| **Session state** | — | `~/.claude/`, `~/.codex/`, `~/.config/opencode/` are **outside** the repository and are excluded by `.gitignore` | No session state enters version control. |

## 7. Resource constraints

| Resource | Value | Note |
| :--- | --- | :--- |
| Free disk on `C:` | **63.8 GB** of 379.5 GB | Adequate. Note the OCR worker image is ~2–4 GB (schedule risk R-4) and must be mirrored in advance for air-gapped sites. |
| Platform | Windows, `win32` | The Linux containers are the production artefacts; the Windows path is a developer convenience (`SPEC-OPS-001` §2.6). |

## 8. Windows-specific hazards to configure before the first test run

From `SPEC-OPS-001` §2.6:

| Hazard | Required action | Owner | Status |
| :--- | :--- | :--- | :--: |
| Long path limits | Enable `LongPathsEnabled` in the registry, or keep the repo path short | DevOps Lead | **Not done** — requires a registry change (admin) |
| Antivirus file locking | Exclude the repo and the Docker data root from real-time scanning | DevOps Lead | **Not done** — requires an AV configuration change |
| UTF-8 filenames | Force UTF-8 in all tooling; Persian filenames must be tested | DevOps Lead | Partially done: `.editorconfig` sets `charset = utf-8`; `.gitattributes` marks all text as UTF-8/LF |
| Line endings | `.gitattributes` enforces LF for source, CRLF only for `.bat`/`.cmd`/`.ps1` | DevOps Lead | **Done** in this session |
| Native wheels (`argon2`, `cryptography`) | `uv` resolves Windows wheels; the container path is the fallback | Lead Backend Eng | **Done** — `uv sync --frozen --all-groups` installed `argon2-cffi`, `cryptography` and `asyncpg` on Windows with no compiler |

---

## 9. Known gaps in this inventory

| # | Gap | Why it is open |
| --: | :--- | :--- |
| 1 | Whether `claude` and `codex` can be driven non-interactively against this repository | Not exercised. Deliberate: the brief forbids assuming a CLI can be orchestrated just because it is installed. The five preconditions in `docs/AGENT_OPERATING_MODEL.md` §5 still stand. |
| 2 | Whether the Docker Desktop engine starts reliably and how long it takes | The daemon is down. Starting it is a GUI action with side effects on the user's machine. |
| 3 | ~~Whether `uv sync` resolves Windows wheels for `argon2-cffi`, `cryptography` and `asyncpg`~~ | **CLOSED in session 2.** All three installed on Windows without a compiler; DEC-A was approved. |
| 4 | Whether a native PostgreSQL 16 is desirable on the host | No `psql` present. The container path is the spec's approach; no host install is proposed. |
| 5 | Antigravity's actual capabilities in this environment | No Antigravity CLI, service or API endpoint is present. Only Freebuff tooling is. Recorded as `UNKNOWN`. |

---

## 10. Re-verification

This inventory is a point-in-time measurement. **Re-run it before any environment-sensitive claim is made**, and after any of these change: a tool upgrade, a Docker Desktop update, a Node/Python change, the addition of an agent CLI, or the enabling of `pnpm`.

---

*Related: `docs/PISH_HESABDARI_HOLY_BIBLE.md` §0.4 (source register), §4.12 (technology inventory).*
