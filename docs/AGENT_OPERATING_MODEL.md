# Agent Operating Model — Pish Hesabdari

- **Document ID:** `DOC-AGENT-001`
- **Status:** Active — describes what is genuinely available, and what is planned
- **As at:** 2026-11-14 (23 Aban 1405 SH)
- **Related:** `AGENTS.md` (the rules) · `docs/ENVIRONMENT_INVENTORY.md` (what is installed) · `docs/PISH_HESABDARI_HOLY_BIBLE.md` §13

> **This document does not create agents. It records which agent capabilities are actually present and executable in this environment, and how work is to be delegated, partitioned and reviewed.** No artificial agent framework is proposed or installed.

> **Recorded remediation session (2026-11-14; changelog §10, not this documentation pass):** Codex desktop hosted `/root` (implementation/tests/docs) and `/root/security_review` (independent read-only security review). The reviewer edited no files. Static review passed after fixes; runtime checks were observed by the parent. This historical record does not claim that a reviewer is active now. External accountant/labour counsel/data suppliers remain missing. Current host limits are in §1 below.

---

## 1. Current capabilities and limits

| Capability | Evidence | Allowed conclusion |
| :--- | :--- | :--- |
| Codex desktop | Active documentation-maintenance host; installed package 26.1111.2228.0 | One documentation owner (/root) is active in this pass; no subagent was started |
| Codex CLI | Executable resolves from the desktop package; preceding audit observed 0.169.0 | Presence/version does not prove an unattended cross-tool handoff is safe |
| Antigravity desktop | Process and executable path observed; ~/.gemini/config and ~/.gemini/antigravity exist | Desktop presence VERIFIED; exact version and native orchestration validation UNKNOWN |
| Antigravity CLI | agy, antigravity and gemini not resolved by current command lookup | CLI absence on PATH does not establish absence of the desktop app |
| Git / worktrees | HEAD 2fc2b6f; worktree list returns this repository on main | The “no first commit” blocker is obsolete; no extra worktree was created or tested here |
| Docker / project DB | BOOTSTRAP_CHANGELOG §12 records engine start and official image/build HTTP 403 | Latest recorded DB provisioning is blocked; current runtime NOT RUN here |
| Native delegation | Earlier Codex independent reviews are recorded in §7 and changelog §§10–12 | Historical successful reviews; do not invent current active agents or assume Antigravity interoperability |
| Other hosts | Earlier opencode/Claude/Freebuff observations are in ENVIRONMENT_INVENTORY | Historical evidence only; Freebuff is not an Antigravity substitute proven by this audit |

Use one accountable coordinator per task and one audit trail. Do not install another orchestration framework to bypass a capability gap. Validate each host's native delegation and working-tree behavior before using it; no cross-tool bridge or new framework is introduced by this document.

---

## 2. The eight logical roles

| # | Role | Responsibility | Accountable for | Available as |
| --: | :--- | :--- | :--- | :--: |
| **A** | **Principal Architect** | Architecture consistency, ADR compliance, dependency decisions, technical boundaries | ADR conformance reviews; the technology inventory; `ADR-005` acceptance recommendation | Logical coordinator role; host/owner assigned explicitly per task. No CTO approval authority is implied by an agent role. |
| **B** | **Backend Engineer** | Backend design and implementation after the relevant specifications and decisions are approved | `P0-T02`, `P0-T11`; `backend/app/**` | **Sub-agent**, on assignment |
| **C** | **Frontend Engineer** | React + Vite SPA, Persian RTL, accessibility, typed API integration | `P3-T01`…`P3-T14`; `frontend/**` | **Sub-agent**, from Phase 3. Not active in Phase 0. |
| **D** | **Database & Security Engineer** | PostgreSQL, schema integrity, RLS, tenant isolation, encryption, identity architecture | `P0-T03`, `P0-T04`, `P0-T05`, `P0-T06`, `P0-T07`, `P0-T08`, `P0-T09`, `P0-T12` | **Sub-agent**, on assignment. DEC-004/DEC-005 are resolved by ADR-006; implementation remains subject to WBS predecessors and acceptance evidence. |
| **E** | **Domain / Payroll Engineer** | Iranian compensation rules, financial precision, calculation engines, statutory rule-set handling | `P1-T04`…`P1-T09`; `backend/app/engines/**` | **Sub-agent**, from Phase 1. **Gated by DEC-002a and the 1405 verification.** |
| **F** | **QA / Test Engineer** | Test strategy, golden vectors, property-based tests, regression tests, acceptance evidence | `P0-T14`, `P0-T15`, `P1-T16`, `P1-T21`, `P2-T17` | **Sub-agent**, on assignment. The golden corpus itself is an **external** dependency (`P1-T15`). |
| **G** | **DevOps / Infrastructure Engineer** | Repository hygiene, reproducible environments, CI, containers, deployment, monitoring, backup | `P0-T01`, `P0-T16`, `P0-T17`, `P0-T19`, `P4-T01`…`P4-T03` | **Sub-agent**, on assignment. Owner of the repository-hygiene work already performed. |
| **H** | **Independent Reviewer / Red Team** | Challenge assumptions, inspect proposed changes, identify security and correctness defects, reject unsupported claims | Every security-sensitive and financial change | **Sub-agent**, always assigned to a *different* agent than the author. The `doubt-driven-development` skill is the review checklist. |

### Active versus planned

| Status | Roles |
| :--- | :--- |
| **Active in this documentation pass** | /root: sole documentation owner; no implementation, security review or delegation performed |
| **Assignable logical roles** | A–H only through capabilities actually available in the selected host; not claims of active agents |
| **Phase-gated work** | C (Phase 3) · E (Phase 1, subject to DEC-002a and statutory verification); no gate/status advanced here |
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
| Two agents editing the same file | **Separate Git worktrees** | Bootstrap commit exists; validate isolation before assignment. Creating worktrees was not part of this maintenance |
| Long-running analysis that must not touch the tree | Read-only sub-agent | Use only if available and authorized in the active host; none started here |
| Sandboxed execution | Active host sandbox; Docker when applicable | Recheck needed capability; §12 records image acquisition failure, not a current daemon-down finding |

**Rule:** no two agents may write the same file in the same working tree. Partition paths or use separate worktrees with a designated integration owner. Preserve existing uncommitted work; do not reset, stash, commit or overwrite it as routine setup.

---

## 5. External CLIs — assessment, not assumption

The brief requires assessing whether `claude` and `codex` can be integrated safely. **They have not been exercised against this repository.** Here is the assessment and the preconditions.

| CLI | Verified present | Preconditions before it may be given any task |
| :--- | :--: | :--- |
| **Claude Code** 2.1.300 | yes | (1) Demonstrate it operates on **this** working tree; (2) demonstrate it does not create a competing `.git` state or its own branch; (3) demonstrate it honours `.gitignore`; (4) confirm the `PreToolUse` hook does not alter command semantics; (5) run it once on a read-only task and diff the tree afterwards. |
| **Codex CLI** 0.169.0 | yes | (1) Same five checks; (2) confirm the `node_repl` and `headroom` MCP servers cannot read outside the workspace; (3) confirm it makes no network calls beyond its own model endpoint; (4) run it once on a read-only task and diff the tree afterwards. |

**Current boundary:** historical Codex independent reviews are recorded in §7. Unattended cross-tool orchestration remains unvalidated; no document selects opencode as the permanently exclusive host. Validate the target host and ownership boundary before delegation.

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

**P1-T02 acquisition preparation, 2026-11-15:** `/root` was the sole implementation/test/documentation writer. `/root/collector_security_review` performed independent read-only review of the actual specification, code and tests; no files edited. Final static PASS after link-limit, hard-timeout, response-metadata and partial-write corrections. Parent observed 157 tests, strict types/lint/format PASS and six failed official-source acquisitions. No human legal sign-off, accepted rule or successful source capture is implied. See BOOTSTRAP_CHANGELOG §16. The reviewer is finished, not an ongoing implementation team.

**P0-T03 session:** `/root` owned infrastructure/tests/docs; `/root/security_review` independently reviewed the configuration, TLS/secret preparation and runtime verifier read-only. One P2 audit-probe weakness was fixed and re-reviewed PASS. Real PostgreSQL runtime review remains NOT RUN because image acquisition/build fails; parent observed local checks. See BOOTSTRAP_CHANGELOG §12.

**P0-T06 session:** `/root` was the sole implementation/documentation writer; `/root/security_review` was resumed for independent read-only review of ADR-006, AUTH §8.5, the primitive and tests. Static result PASS; parent ran runtime checks. No human security/legal sign-off or eight-agent team is asserted. Evidence: BOOTSTRAP_CHANGELOG §11.

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
| 1 | **Antigravity version/orchestration unvalidated** | Desktop exists; exact version, loaded project skills and safe native handoff still need evidence | Principal Architect / Owner |
| 2 | **No named individuals for any role** | Accountability is to a role, not a person; the three long-lead external commissions have no owner | Owner (DEC-E) |
| 3 | **External CLIs unvalidated** | Not usable as delegation targets yet | Principal Architect |
| 4 | **Cross-tool worktree integration unvalidated** | Commit exists; demonstrate safe isolation/integration before competing work is assigned | Principal Architect |
| 5 | **Database image acquisition blocked in last runtime evidence** | No project DB acceptance; current runtime must be checked when needed | Developer / DevOps Lead |
| 6 | **No review automation** | Independent review is a human/sub-agent act, not a CI gate, until `P0-T19` exists | DevOps Lead |

---

*Related: `AGENTS.md` §6 (agent operating rules) · `docs/ENVIRONMENT_INVENTORY.md` §6 · `docs/PROJECT_STATUS.md` §7.*
