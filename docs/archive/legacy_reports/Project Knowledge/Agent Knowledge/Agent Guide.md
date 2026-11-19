---
title: "Agent Guide — Working with the Obsidian Vault"
document_id: KNOW-AGENT-001
status: Active navigation layer
as_of: 2026-11-16
---

# Agent Guide

> This note explains how coding agents (OpenCode, Claude Code and compatible tools) should use the Obsidian layer. It does **not** replace [AGENTS.md](../../AGENTS.md) or [docs/AGENT_OPERATING_MODEL.md](../../docs/AGENT_OPERATING_MODEL.md). If this note conflicts with either, the project documents win.

## Authority hierarchy

1. **Holy Bible and approved specifications** — [PISH_HESABDARI_HOLY_BIBLE.md](../../docs/PISH_HESABDARI_HOLY_BIBLE.md), [REMEDIATED_TECHNICAL_SPECIFICATION_V2.md](../../REMEDIATED_TECHNICAL_SPECIFICATION_V2.md)
2. **Accepted ADRs** — [ADR_INDEX](../../docs/ADR_INDEX.md) and the ADR files; only `Accepted` is binding
3. **Approved execution plans** — [EXECUTION_PLAN.md](../../docs/EXECUTION_PLAN.md)
4. **Implementation documentation** — specs, project status, changelog
5. **Development notes and agent reports** — handoff summaries, this vault navigation layer

**Obsidian is not an alternative source of truth.** Do not quote a dashboard summary where the source document is available. A status in this vault is only a pointer.

## Recommended reading order

| Task | Read first |
| :--- | :--- |
| Any change | [AGENTS.md](../../AGENTS.md) §1–§3, then [DOCUMENTATION_INDEX §0](../../docs/DOCUMENTATION_INDEX.md) |
| Current status | [PROJECT_STATUS §2](../../docs/PROJECT_STATUS.md), then [EXECUTION_PLAN §14.3](../../docs/EXECUTION_PLAN.md) |
| Decision-sensitive work | [DECISIONS_REGISTER](../../docs/DECISIONS_REGISTER.md), the relevant ADR, [Decision Status](../Decisions/Decision%20Status.md) |
| Monetary/engine change | `financial-data-integrity` and `iranian-payroll-engineering` skills; [Architecture Map](../Architecture/Architecture%20Map.md) |
| Database/security | [ADR-003](../../docs/adr/ADR-003-sensitive-data-encryption-alee-blind-indexing.md), [ADR-006](../../docs/adr/ADR-006-phase-0-owner-approved-security-and-schema.md), [ADR-007](../../docs/adr/ADR-007-statutory-global-access-and-deferred-identity.md), [STATUTORY_DATABASE_CONTRACT](../../docs/specs/STATUTORY_DATABASE_CONTRACT.md) |
| Persian UI/PDF | [FRONTEND_PERSIAN](../../docs/specs/FRONTEND_PERSIAN.md), [ADR-001](../../docs/adr/ADR-001-frontend-architecture-react-vite-spa.md) |
| Tests/CI | [TESTING](../../docs/specs/TESTING.md), [BOOTSTRAP_CHANGELOG §24](../../docs/BOOTSTRAP_CHANGELOG.md) |
| Delegation | [AGENT_OPERATING_MODEL](../../docs/AGENT_OPERATING_MODEL.md) |

## Reading discipline

- Search headings and IDs first; load only task-relevant sections.
- Read a required specification in full when the task contract says so; a summary is not a substitute.
- Re-read a source when it changes or the task expands.
- Do not bulk-load the Holy Bible, WBS, changelog, all skills or the research corpus by default.
- Record the document revision/section in the handoff.

## Status vocabulary

Use the project's existing labels exactly:

| Label | Meaning |
| :--- | :--- |
| `VERIFIED` / `ACTIVE` | checked against evidence and usable |
| `ACCEPTED` | approved decision; binding |
| `PROPOSED` | drafted, not binding |
| `UNVERIFIED` | not checked; do not treat as valid |
| `CONFLICT` | sources disagree; both linked, unresolved |
| `MISSING` | required artifact/evidence does not exist |

Task statuses: `NOT_STARTED`, `IN_PROGRESS`, `BLOCKED`, `READY_FOR_REVIEW`, `APPROVED`, `COMPLETED`. Never mark a task `COMPLETED` from documentation alone. Never change a status to bypass a blocker.

## Obsidian usage

- Keep Markdown portable. Ordinary relative Markdown links are used; no Obsidian-only syntax is required to read this vault.
- Properties (YAML frontmatter) are metadata only; they do not override source documents.
- Use **Backlinks**, **Graph View**, **Local Graph**, **Search**, **Outline**, **Properties**, **Templates** and **Canvas** from core Obsidian.
- No community plugin is installed. Do not add one without explicit owner approval and a documented need.
- No cloud sync is enabled. Do not upload project documents to external services.
- Templates live in `Project Knowledge/Templates/` — start from [ADR Template](../Templates/ADR%20Template.md) or [Module Documentation](../Templates/Module%20Documentation.md). They must not replace the project's ADR format.

## Safety rules

- **Never** put secrets, API keys, `.env` contents, private configuration, National IDs, mobile numbers, Sheba numbers or real candidate salaries into a note, canvas, template or property.
- Do not open or copy `.secrets/`, `.freebuff/`, `.kilo/`, `.zcode/` or local agent state into shared knowledge.
- Do not modify `backend/`, `frontend/`, migrations, seeds, Git configuration or authoritative documents as part of knowledge management.
- Do not stage, commit, push, reset or delete files without explicit instruction.
- A financial or security-sensitive change requires independent review by someone who did not write it.

## Adding a knowledge note

1. Check whether an authoritative document already covers the topic; link it instead of duplicating it.
2. If a new note is genuinely needed, place it in the matching folder:
   - `Overview/` — inventories and orientation
   - `Architecture/` — navigation over architecture
   - `Decisions/` — indexes of decisions, never new decisions
   - `Development Log/` — chronology and links to evidence
   - `Risks/` — consolidation over the canonical risk register
   - `Agent Knowledge/` — working conventions for agents
3. Add frontmatter with `title`, `document_id`, `status`, `as_of`.
4. Use relative links; verify each target exists.
5. Mark derived statements as derived, and cite the source section.
6. If sources conflict, record **both** links and keep `CONFLICT`; do not guess.

## Handoff checklist

- [ ] Task ID and exact WBS row identified
- [ ] Required documents read (not summaries)
- [ ] Decisions checked; no open decision silently resolved
- [ ] File ownership and isolation agreed
- [ ] Exact verification command and observed PASS/FAIL/NOT RUN recorded
- [ ] No secret or personal data in notes, logs or commits
- [ ] Source statuses preserved; conflicts linked
