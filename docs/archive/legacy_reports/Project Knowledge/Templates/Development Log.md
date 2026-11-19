---
title: "Development Log — <YYYY-MM-DD> — <short title>"
document_id: DEVLOG-<NNN>
status: RECORDED
as_of: {{date}}
task: <WBS ID>
owner: <role>
---

# Development Log — {{date}} — <short title>

> Chronological evidence, not an acceptance record. Status changes belong in `docs/PROJECT_STATUS.md` and `docs/BOOTSTRAP_CHANGELOG.md`. Never write a PASS you did not observe.

## Scope

- **WBS task:** <ID and exact row title>
- **Objective:** <one sentence>
- **Files owned:** <explicit list; no other file was edited>
- **Out of scope:** <what was deliberately not touched>

## Changes

| File | Change | Reason |
| :--- | :--- | :--- |
| <path> | <added / modified / removed> | <...> |

## Verification performed

| Command | Working directory | Result | Observed output |
| :--- | :--- | :--: | :--- |
| `<exact command>` | `<path>` | PASS / FAIL / NOT RUN | <counts or error summary> |

**Not run and why:** <e.g. Docker unavailable; PostgreSQL integration suites skipped>

## Decisions touched

- <DEC / ADR IDs read, and whether any status changed. Normally: none.>

## Git state

- Branch: <branch>
- HEAD before: <sha>
- Staged / committed / pushed: **No** (unless explicitly instructed)

## Follow-ups

- [ ] <next action, with owner>
- [ ] <blocker, with the decision or external party that unblocks it>

## Links

- <task specification>
- <changelog entry>
