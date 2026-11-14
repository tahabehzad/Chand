# Decisions Required from the Project Owner

- **Document ID:** `DOC-DEC-OWNER-001`
- **Status:** Active — the standing owner-decision queue
- **As at:** 2026-11-14 (23 Aban 1405 SH)
- **Related:** `docs/DECISIONS_REGISTER.md` (the engineering register) · `docs/PISH_HESABDARI_HOLY_BIBLE.md` §13.3–§13.5 · `docs/PHASE_0_BOOTSTRAP_PLAN.md`

> **Two queues, not one.** `docs/DECISIONS_REGISTER.md` holds the engineering decisions with technical options and approvers. **This file holds the decisions only the owner can make** — money, legal exposure, external commitments and access to the machine. Items are ordered by what unblocks the most work.

**Nothing here is decided by an agent.** Each entry states the question, the options **as they exist in the source documents**, the consequence, and whether the work is blocked.

> **Session 2 (2026-11-14).** The owner resolved **DEC-A**, **DEC-B** and **DEC-G** in the Phase 0 bootstrap session. The resolutions, their dates and their consequences are recorded in the entries below. **DEC-I (DEC-004 / DEC-004a / DEC-004b / DEC-005) was not answered and was not assumed**: no session strategy, key hierarchy, MFA role set or ERD correction was chosen, and no table was written.

---

## DEC-A — Install the backend dependency set

| Field | Value |
| :--- | :--- |
| **Status** | `RESOLVED` — 2026-11-14 |
| **Question** | May `uv sync` be run to install the resolved dependency set into `backend/.venv`? |
| **Options** | **(a)** Install now — 166 packages, ~1 venv, no system change, fully reversible by deleting `backend/.venv`. **(b)** Defer until the first commit; the developer installs manually. |
| **Consequence of (a)** | `ruff`, `mypy` and `pytest` become runnable immediately, so `P0-T01`'s acceptance criteria can actually be *verified* rather than asserted. `backend/.venv` is git-ignored. Rollback: `Remove-Item -Recurse -Force backend\.venv`. |
| **Consequence of (b)** | `P0-T01` cannot be marked `COMPLETED` — its acceptance criteria are `uv sync --frozen` succeeds, ruff clean, mypy strict clean. The dependency baseline stays unverified. |
| **Recommendation** | **(a).** The install is local, isolated, reversible and unblocks the only verification-capable task available. |
| **Blocked?** | Yes — `P0-T01` completion, and every task that needs `ruff`/`mypy`/`pytest` to prove its work. |

**Resolution (2026-11-14, Project Owner).** Option **(a)** — install. `uv sync --frozen --all-groups` was run and returned `Checked 118 packages`, exit 0. `backend/.venv` exists and is git-ignored; the rollback is `Remove-Item -Recurse -Force backend\.venv`. The acceptance criteria of `P0-T01` are now **verifiable** rather than asserted, and `ruff`, `mypy` and `pytest` are runnable by every engineer and agent.

---

## DEC-B — Make the first Git commit

| Field | Value |
| :--- | :--- |
| **Status** | `RESOLVED` — 2026-11-14 |
| **Question** | May the 46 tracked files be committed on `main` as the initial commit? |
| **Options** | **(a)** Commit on `main` with a conventional message. **(b)** Commit on a `bootstrap/initial-import` branch and merge after review. **(c)** Do not commit yet. |
| **Consequence** | A commit gives a real audit trail, makes `R-10`'s seed hash pin enforceable, and enables **Git worktrees** — the isolation mechanism for parallel agents. It also creates the first shared history. |
| **Risk** | The history becomes part of the record. The 46 files are the full historical corpus; a commit is the honest way to preserve it under version control. |
| **Recommendation** | **(b)** — a reviewable branch, then a merge. |
| **Blocked?** | No for engineering; **yes** for worktree-based parallel agents and for the CI pipeline (`P0-T19`). |

**Resolution (2026-11-14, Project Owner).** Option **(b)** — commit on `bootstrap/initial-import`, then merge into `main`. Both commits exist; the merge was made with `--no-ff` so the branch history is preserved. **Nothing was pushed**: there is still no remote. Worktree-based agent isolation and `P0-T19` are now unblocked.

---

## DEC-C — Provision `pnpm`

| Field | Value |
| :--- | :--- |
| **Status** | `OPEN — NON-BLOCKING` |
| **Question** | May `corepack enable pnpm` be run to provision the spec-mandated frontend package manager? |
| **Options** | **(a)** `corepack enable pnpm` — modifies the global Node installation. **(b)** Use `npm` for local work and provision `pnpm` only inside CI and containers. |
| **Consequence** | `SPEC-OPS-001` §2.4 mandates `pnpm install --frozen-lockfile`. Option (b) risks a `package-lock.json` being created instead of `pnpm-lock.yaml`, which would silently diverge from the spec's lockfile contract. |
| **Recommendation** | **(a)**, with the lockfile type enforced by `.gitignore` (ignore `package-lock.json`). Frontend work is Phase 3, so this is not urgent. |
| **Blocked?** | No — frontend is `P3-T01`. |

---

## DEC-D — Orchestration surface

| Field | Value |
| :--- | :--- |
| **Status** | `OPEN — NON-BLOCKING` |
| **Question** | Is an "Antigravity" agent/team runtime expected to be present, and should one be provisioned? |
| **Options** | **(a)** Proceed with the **verified** surface: opencode's native sub-agent + worktree mechanisms, with Claude Code and Codex held as an unvalidated escalation path. **(b)** Provision a multi-CLI orchestration layer now. |
| **Consequence** | Option (b) adds a second orchestration framework and two more autonomous writers against one working tree, with no proven isolation and no proven Git discipline. The brief explicitly says not to install competing frameworks and not to assume a CLI can be orchestrated because it is installed. |
| **Recommendation** | **(a).** One host, one Git state, one audit trail. `docs/AGENT_OPERATING_MODEL.md` §5 records the preconditions for validating the two external CLIs later. |
| **Blocked?** | No. |

---

## DEC-E — Name the owners and open the three external commissions

| Field | Value |
| :--- | :--- |
| **Status** | `OPEN — BLOCKING` |
| **Question** | Who is the accountable human for each role, and who is appointed to the Certified Tax Accountant, the Iranian Labour Counsel and the Shahkar arrangement? |
| **Options** | **(a)** Name individuals now and issue engagement letters in Week 1. **(b)** Keep role-only ownership and procure later. |
| **Consequence** | Option (b) leaves the three longest-lead external items **unowned**. The Phase 1 gate is defined by the accountant's signed corpus; the Phase 2 gate by a consented 500-slip corpus; the Phase 4 gate by the labour attorney's letter. None can be produced by an agent. The Holy Bible records these as the top three risks. |
| **Recommendation** | **(a).** These are the three highest-leverage actions available in the project and they are all Week 1 items. |
| **Blocked?** | Yes — the Phase 1 and Phase 2 gates, and the operating statutory baseline. |

---

## DEC-F — CI provider and remote

| Field | Value |
| :--- | :--- |
| **Status** | `OPEN — NON-BLOCKING` |
| **Question** | Which CI provider, and is a remote repository configured? |
| **Options** | **(a)** A self-hosted runner in the client's own environment (matches the air-gap constraint, but requires infrastructure the project does not have). **(b)** GitHub Actions or equivalent hosted CI for the development repository only, with production verification performed in the client's environment. **(c)** A local pre-commit + local CI runner for now. |
| **Consequence** | The 13-stage pipeline (`SPEC-QA-001` §15) is specified but unbuildable without a provider. **Option (c) risks a misleading green pipeline**, which the brief forbids. Note that the air-gap requirement is about the *deployed product*, not the *development* pipeline — hosted CI for development does not violate it. |
| **Recommendation** | **(b)** for the development repository, with the air-gapped verification checklist (`SPEC-OPS-001` §12) performed in the client's environment at pilot. |
| **Blocked?** | Yes — `P0-T19`, and therefore the Phase 0 gate's Stage 5. |

---

## DEC-G — Repository licence

| Field | Value |
| :--- | :--- |
| **Status** | `RESOLVED` — 2026-11-14 |
| **Question** | Under which licence is the Pish Hesabdari source released, and to whom? |
| **Options** | **(a)** Proprietary / all rights reserved — consistent with the classification on `REMEDIATED`. **(b)** A permissive licence with a contributor agreement. **(c)** Split: proprietary for the platform, permissive for the skill contracts. |
| **Consequence** | Without a licence, the repository has no default grant: no one may legally copy, modify or redistribute it, and the project's own future contributors have no defined rights. It also interacts with the open-source component licences (Apache-2.0, MIT, BSD-3-Clause) and with the HashiCorp Vault BUSL question (HB-GAP-035). |
| **Recommendation** | **(a)**, with an explicit internal contributor agreement, given that the product embeds Iranian statutory rules and handles identity data. |
| **Blocked?** | No — but it should be settled before the first commit, since the licence file belongs in it. |

**Resolution (2026-11-14, Project Owner).** Option **(a)** — proprietary, all rights reserved. A `LICENSE` file was written and committed with the first commit. The repository therefore has a default grant of *none*, and an internal contributor agreement remains to be drafted by the owner.

---

## DEC-H — Correct the Holy Bible's §11.1 statement about the backend scaffold

| Field | Value |
| :--- | :--- |
| **Status** | `OPEN — TRIVIAL`** |
| **Question** | May the Holy Bible §11.1 be corrected from *"No `backend/app/`, no `backend/tests/`"* to record that the **empty package skeleton exists** (`backend/app/{api,api/v1,core,engines,models,schemas,services}` and `backend/tests/`, created 2026-11-13), containing zero source files? |
| **Consequence** | The current wording says the directories do not exist; they do exist and are empty. The distinction matters: an empty skeleton is consistent with the target layout, but it is **not implementation**, and no task may be marked complete on the strength of it. |
| **Recommendation** | **(a) — correct it.** A factual correction to a rank-4 derived document, with a changelog entry. |
| **Blocked?** | No. |

---

## DEC-I — The four open Phase 0 engineering decisions (summary pointer)

These are **engineering** decisions already tracked in `docs/DECISIONS_REGISTER.md`. They are repeated here because they are the ones that actually sit on the Phase 0 critical path, and because their approvers are named humans.

| ID | Question | Approver | Blocks | Recommendation (from the register) |
| :--- | :--- | :--- | :--- | :--- |
| **DEC-004** | Server-side opaque sessions or stateless JWT? Which identity provider? Which roles? | CISO + CTO | `P0-T05`, `P0-T18`, `P0-T22` | (b) opaque sessions + (c) first-party credentials with an OIDC path later + (b) MFA mandatory for privileged roles |
| **DEC-004a** | Which roles must complete a second factor? | CISO | `P0-T18` | (b) `OWNER`, `ADMIN`, `LEGAL_REVIEWER`, `SUPER_ADMIN` |
| **DEC-004b** | Must every read event be hash-chained, or may reads go to a separate access log? | CISO | `P0-T10` | (b) chain mutations and evidentiary events; a separate, independently tamper-evident access log for reads |
| **DEC-005** | Confirm the ERD corrections: `CHAR(64)` hashes, the blind index on `candidates`, `EMPLOYEES` deferred, `actor_id → users(id)` | CTO + DBA + Security Architect | `P0-T04`, `P0-T05`, `P0-T12`, `P0-T13` | (A) — the full correction |

**Options for each are exactly as recorded in `docs/DECISIONS_REGISTER.md`; they are not restated or invented here.**

---

## DEC-J — The three highest-leverage actions

| # | Action | Why it outranks everything else |
| --: | :--- | :--- |
| 1 | **Appoint the Certified Tax Accountant** | Produces the 10 000-case corpus that *is* the Phase 1 gate. Nothing else can substitute, and it cannot be parallelised away — a 10 000-case corpus is a writing task measured in weeks. |
| 2 | **Appoint the Iranian Labour Counsel and obtain the L1 primary circulars** | Unlocks the 1405 four-eyes verification, closes O1–O10, and is the only route to an activated 1405 baseline. The engineering team cannot reach `mcls.gov.ir`. |
| 3 | **Resolve DEC-004, DEC-004a, DEC-004b and DEC-005** | They sit **on** the Phase 0 critical path. No amount of engineering effort shortens the critical path through them. |

---

## 1. Summary

| ID | Title | Class | Blocks implementation? |
| :--- | :--- | :--: | :--: |
| DEC-A | Install the backend dependency set | **RESOLVED 2026-11-14** (a) | No — `P0-T01` verification now runs |
| DEC-B | Make the first Git commit | **RESOLVED 2026-11-14** (b) | No — worktrees and CI are unblocked |
| DEC-C | Provision `pnpm` | Non-blocking | No (Phase 3) |
| DEC-D | Orchestration surface | Non-blocking | No |
| DEC-E | Name owners; open the three external commissions | **Blocking** | **Yes** — the Phase 1 and Phase 2 gates |
| DEC-F | CI provider and remote | Non-blocking | **Yes** — `P0-T19`, hence the Phase 0 gate |
| DEC-G | Repository licence | **RESOLVED 2026-11-14** (a) | No |
| DEC-H | Correct the Holy Bible §11.1 scaffold statement | Trivial | No |
| DEC-I | The four open Phase 0 engineering decisions | **Blocking** | **Yes** — the Phase 0 critical path |
| DEC-J | The three highest-leverage actions | **Blocking** | **Yes** |

**2 blocking · 2 non-blocking · 3 resolved.** Plus the 17 engineering register entries already tracked in `docs/DECISIONS_REGISTER.md`.

---

*Queue maintained alongside `docs/DECISIONS_REGISTER.md`. When an entry is resolved, record the decision, the date and the approver here and in the register, and update `docs/PROJECT_STATUS.md`.*
