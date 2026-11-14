# Agent Operating Model — Pish Hesabdari

- **Document ID:** `DOC-AGENT-001`
- **Status:** Active — describes what is genuinely available, and what is planned
- **As at:** 2026-11-14 (23 Aban 1405 SH)
- **Related:** `AGENTS.md` (the rules) · `docs/ENVIRONMENT_INVENTORY.md` (what is installed) · `docs/PISH_HESABDARI_HOLY_BIBLE.md` §13

> **This document does not create agents. It records which agent capabilities are actually present and executable in this environment, and how work is to be delegated, partitioned and reviewed.** No artificial agent framework is proposed or installed.

---

## 1. What actually exists

| Capability | Present? | Evidence | Can it be used for this project now? |
| :--- | :--- | :--- | :--: |
| **Antigravity agent/team runtime** | **No.** No Antigravity CLI, service, API endpoint or configuration is present. | Exhaustive `PATH` probe; no matching binary or config directory | **No.** It cannot be relied on. The closest equivalent is the **Freebuff** tooling (`freebuff` npm shim on `PATH`; `.freebuff/project-id` present in the workspace) plus the three coding CLIs below. |
| **Freebuff project tooling** | Yes | `freebuff` on `PATH`; `.freebuff/project-id` = a UUID; `.freebuff/.gitignore` excludes its own state | Yes — for session/workspace identification only. Its state is excluded from version control. |
| **opencode** | Yes, `v2.2.5` | `opencode --version`; MCP: `browser-control-mcp` (local) | **Yes — this is the current session.** It has native sub-agent spawning, Git worktree creation and MCP. |
| **Claude Code** | Yes, `2.1.300` | `claude --version`; `~/.claude/settings.json` with a `PreToolUse` Bash hook | **Available, not yet validated.** Must be proven to operate on the same working tree without creating competing Git state before it is given any task. |
| **Codex CLI** | Yes, `0.169.0` | `codex --version`; `~/.codex/config.toml`; MCP: `node_repl`, `headroom` | **Available, not yet validated.** Same precondition. |
| **Git worktrees** | Yes, **verified by execution** | `git init` + `git worktree list` in a scratch directory | **Yes** — the isolation mechanism for parallel agents. Requires a first commit to branch from. |
| **Docker** | CLI yes, **daemon down** | `docker info` → npipe connect failure | No, until Docker Desktop is started. |
| **Sub-agent spawning (native)** | Yes | opencode `subagent` tool | **Yes** — the primary delegation mechanism here. |

### Standing on that

The brief's preferred "native Antigravity agent/team functionality" is **not present**. Rather than install a competing framework, this project uses **one** orchestration host (opencode, which is running) with its **native** sub-agent and worktree mechanisms, and keeps the three external CLIs as an *unvalidated* escalation path until they are proven.

**Do not install a second orchestration framework.** One host, one Git state, one audit trail.

---

## 2. The eight logical roles

| # | Role | Responsibility | Accountable for | Available as |
| --: | :--- | :--- | :--- | :--: |
| **A** | **Principal Architect** | Architecture consistency, ADR compliance, dependency decisions, technical boundaries | ADR conformance reviews; the technology inventory; `ADR-005` acceptance recommendation | **Principal orchestrator** (this session). Also the CTO role in the WBS gate reviews. |
| **B** | **Backend Engineer** | Backend design and implementation after the relevant specifications and decisions are approved | `P0-T02`, `P0-T11`; `backend/app/**` | **Sub-agent**, on assignment |
| **C** | **Frontend Engineer** | React + Vite SPA, Persian RTL, accessibility, typed API integration | `P3-T01`…`P3-T14`; `frontend/**` | **Sub-agent**, from Phase 3. Not active in Phase 0. |
| **D** | **Database & Security Engineer** | PostgreSQL, schema integrity, RLS, tenant isolation, encryption, identity architecture | `P0-T03`, `P0-T04`, `P0-T05`, `P0-T06`, `P0-T07`, `P0-T08`, `P0-T09`, `P0-T12` | **Sub-agent**, on assignment. **Gated by DEC-004/DEC-005** for `P0-T04`, `T05`, `T09`, `T12`. |
| **E** | **Domain / Payroll Engineer** | Iranian compensation rules, financial precision, calculation engines, statutory rule-set handling | `P1-T04`…`P1-T09`; `backend/app/engines/**` | **Sub-agent**, from Phase 1. **Gated by DEC-002a and the 1405 verification.** |
| **F** | **QA / Test Engineer** | Test strategy, golden vectors, property-based tests, regression tests, acceptance evidence | `P0-T14`, `P0-T15`, `P1-T16`, `P1-T21`, `P2-T17` | **Sub-agent**, on assignment. The golden corpus itself is an **external** dependency (`P1-T15`). |
| **G** | **DevOps / Infrastructure Engineer** | Repository hygiene, reproducible environments, CI, containers, deployment, monitoring, backup | `P0-T01`, `P0-T16`, `P0-T17`, `P0-T19`, `P4-T01`…`P4-T03` | **Sub-agent**, on assignment. Owner of the repository-hygiene work already performed. |
| **H** | **Independent Reviewer / Red Team** | Challenge assumptions, inspect proposed changes, identify security and correctness defects, reject unsupported claims | Every security-sensitive and financial change | **Sub-agent**, always assigned to a *different* agent than the author. The `doubt-driven-development` skill is the review checklist. |

### Active versus planned

| Status | Roles |
| :--- | :--- |
| **Actively filled now** | A (orchestrator, this session) · G (repository hygiene work performed) · H (review of everything in this session) |
| **Available on assignment** | B, D, F |
| **Planned, not yet startable** | C (Phase 3) · E (Phase 1, and gated on DEC-002a + the 1405 verification) |
| **External, not an agent role** | Certified Tax Accountant, Iranian Labour Counsel, penetration-test vendor, corpus acquisition |

> **Every role in this table is a *logical* role.** The WBS already assigns each task to a role (`EXECUTION_PLAN` §14.3). The table maps those roles onto the actual execution capability. **No role has a named individual** — that is a gap (Holy Bible HB-GAP-041) and an owner action.

---

## 3. Delegation protocol

Every delegation carries a **delegation record**. A task is delegated with:

```
TASK ID            : P0-T0x  (exact WBS ID)
TITLE              : <from EXECUTION_PLAN §14.3>
OWNER              : <one role>            ← exactly one
DOCUMENTS TO READ  : <absolute paths>      ← documents, not summaries
DECISIONS APPLIED  : <which decisions are approved and are therefore binding>
DEPENDENCIES MET   : <which D-column predecessors are complete>
FILE OWNERSHIP     : <exact paths this agent may create or edit>
MUST NOT TOUCH     : <paths and topics outside ownership>
VERIFICATION       : <exact command(s) and the expected evidence>
ASSUMPTIONS        : <any assumption, recorded in the task's Blocking-issues field>
STOP CONDITIONS    : <what forces the agent to stop and report>
```

**Mandatory rules**

1. **One accountable owner.** Shared ownership is no ownership.
2. **Give documents, not summaries.** An agent that has not read `SPEC-AUTH-001` must not write `P0-T05`.
3. **No scope redefinition.** An agent does not resolve an open decision to keep moving.
4. **No file collisions.** Partition by path, or give each agent a Git worktree.
5. **Independent review** for anything touching money, keys, cryptography, RLS or audit.
6. **Auditable trail.** Every delegation, decision and verification lands in `docs/BOOTSTRAP_CHANGELOG.md`.
7. **No fabricated agents.** If the platform cannot run it, it is not in the table.

### File-ownership partition for the next parallel wave

| Agent | May create/edit | Must not touch |
| :--- | :--- | :--- |
| **D — Database & Security** | `backend/app/core/security/**`, `backend/app/core/crypto/**` | `backend/app/engines/**`, `frontend/**` |
| **B — Backend** | `backend/app/main.py`, `backend/app/core/config.py`, `backend/app/core/logging.py`, `backend/app/api/**` | `backend/app/core/security/**`, `backend/app/engines/**` |
| **F — QA** | `backend/tests/**` | everything under `backend/app/**` |
| **G — DevOps** | `infra/**`, `.github/**`, `backend/uv.lock`, `backend/pyproject.toml` | `backend/app/**`, `backend/tests/**` |
| **H — Reviewer** | `docs/BOOTSTRAP_CHANGELOG.md` (review section only) | **all source** — a reviewer that edits the code defeats the review |

---

## 4. Isolation mechanism

| Need | Mechanism | Status |
| :--- | :--- | :--: |
| Two agents editing different files, same tree | Strict path partitioning (§3) | Available now |
| Two agents editing the same file | **Git worktree** per agent | **Verified available**, but requires a first commit (a worktree branches from a commit). Currently blocked on the owner-approved first commit. |
| Long-running analysis that must not touch the tree | Read-only sub-agent | Available now |
| Sandboxed execution | Docker | **Unavailable** — the daemon is down |

**Rule:** until the first commit exists, **only path-partitioned parallel work is permitted**, and no two agents may target the same file. Sequential execution is preferred over a collision.

---

## 5. External CLIs — assessment, not assumption

The brief requires assessing whether `claude` and `codex` can be integrated safely. **They have not been exercised against this repository.** Here is the assessment and the preconditions.

| CLI | Verified present | Preconditions before it may be given any task |
| :--- | :--: | :--- |
| **Claude Code** 2.1.300 | yes | (1) Demonstrate it operates on **this** working tree; (2) demonstrate it does not create a competing `.git` state or its own branch; (3) demonstrate it honours `.gitignore`; (4) confirm the `PreToolUse` hook does not alter command semantics; (5) run it once on a read-only task and diff the tree afterwards. |
| **Codex CLI** 0.169.0 | yes | (1) Same five checks; (2) confirm the `node_repl` and `headroom` MCP servers cannot read outside the workspace; (3) confirm it makes no network calls beyond its own model endpoint; (4) run it once on a read-only task and diff the tree afterwards. |

**Until then: the native opencode sub-agent is the only delegation mechanism in use.** Two CLIs that both write the same tree without proven isolation is worse than one that is proven.

**Mandatory check after every external-CLI run:**
```powershell
git status --short          # must show no unexpected modifications
git diff --stat             # must be empty for a read-only task
```

---

## 6. Escalation matrix

| Situation | Escalate to | Authority |
| :--- | :--- | :--- |
| The specification contradicts an accepted ADR | CTO (Principal Architect) | Raise a contradiction; propose a superseding ADR |
| A decision is needed that no ADR or register entry covers | Product Manager / Owner | Add to `docs/DECISION_REQUIRED_FROM_OWNER.md` |
| A statutory value is unavailable or contradictory | Labour Counsel + Certified Tax Accountant | `SPEC-STAT-001` §3.5 open items; **never estimate** |
| A security defect is suspected | Security Architect | `SPEC-OPS-001` §9.3 SEV-1 runbook |
| A monetary test fails | QA Lead + Domain Engineer | Treat as a defect; never quarantine a money test |
| An agent proposes a product change | Product Manager | Never accept it in-line |

---

## 7. Audit record

Every delegation produces a row in `docs/BOOTSTRAP_CHANGELOG.md`:

| Field | Content |
| :--- | :--- |
| Timestamp | ISO-8601 |
| Task ID | Exact WBS ID |
| Agent | Role letter + tool used |
| Scope | Files touched |
| Decisions applied | Which approved decisions governed the work |
| Verification | Command + result (PASS / FAIL / NOT RUN) |
| Status change | From → To, with evidence |

---

## 8. Known gaps in this model

| # | Gap | Effect | Owner |
| --: | :--- | :--- | :--: |
| 1 | **No Antigravity runtime.** The brief's preferred orchestration surface is absent | Delegation runs on opencode's native sub-agent + worktree mechanisms | Owner (DEC-D) |
| 2 | **No named individuals for any role** | Accountability is to a role, not a person; the three long-lead external commissions have no owner | Owner (DEC-E) |
| 3 | **External CLIs unvalidated** | Not usable as delegation targets yet | Principal Architect |
| 4 | **No first commit** → no worktree branching | Parallel agents must be path-partitioned only | Owner (first commit) |
| 5 | **Docker daemon down** | No isolated execution for agents or for the database | Developer / DevOps Lead |
| 6 | **No review automation** | Independent review is a human/sub-agent act, not a CI gate, until `P0-T19` exists | DevOps Lead |

---

*Related: `AGENTS.md` §6 (agent operating rules) · `docs/ENVIRONMENT_INVENTORY.md` §6 · `docs/PROJECT_STATUS.md` §7.*
