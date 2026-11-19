<!--
Core Obsidian template for a new Architecture Decision Record.
It deliberately mirrors the existing docs/adr/ format (title, bullet metadata,
Context, Drivers, Options, Outcome, Consequences, Pros/Cons, Directives) so a new
ADR is structurally identical to ADR-001…008. There is no YAML frontmatter,
because the existing ADRs do not use any.

Rules: a decision is Proposed until the named approver explicitly accepts it.
Never invent a decider, an approval or a verification result.
-->

# ADR-NNN: <Short decision title>

- **Status**: Proposed
- **Date**: {{date}}
- **Deciders**: <role(s) / named approver>
- **Consulted**: <role(s)>
- **Related**: <DEC-ID, WBS task ID, specification section>

## Context and Problem Statement

<The forces at play, in two to four paragraphs. Cite the authoritative document and section; do not restate the whole specification.>

## Decision Drivers

1. <Driver, ideally traceable to a requirement or an accepted ADR>
2. <Driver>
3. <Driver>

## Considered Options

- **Option 1** — <name>
- **Option 2** — <name>
- **Option 3** — <name>

## Decision Outcome

<One binding sentence naming the chosen option. If nothing is approved, say so explicitly.>

### Positive Consequences

- <...>

### Negative Consequences / Trade-offs

- <...>

## Pros and Cons of Considered Options

### Option 1: <name>

- **Pros:** <...>
- **Cons:** <...>

### Option 2: <name>

- **Pros:** <...>
- **Cons:** <...>

### Option 3: <name>

- **Pros:** <...>
- **Cons:** <...>

## Implementation Directives

1. <What must be implemented, by which WBS ID, and under which invariant>
2. <What stays explicitly open: decisions, phases, external dependencies>
3. <What must not be changed by this ADR>

## Verification and Ownership

- **Accountable owner:** <role>
- **Acceptance evidence:** <WBS acceptance criteria, test suite, changelog section>
- **Status change:** only after observed evidence, recorded in `docs/BOOTSTRAP_CHANGELOG.md`.

<!--
After writing: add the ADR to docs/ADR_INDEX.md and to the supersession map in
docs/DOCUMENTATION_INDEX.md. An Accepted ADR that is missing from both indexes is a
documentation conflict (see Project Knowledge/Decisions/Decision Status.md).
-->
