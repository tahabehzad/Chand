---
title: "Module — <module name>"
document_id: MOD-<NNN>
status: DRAFT
as_of: {{date}}
owner: <role>
layer: engine / service / api / persistence / frontend / infrastructure
---

# Module — <module name>

> Documentation of an existing module. It does not grant the module new responsibilities. Binding rules come from the Holy Bible, the accepted ADRs and the module's specification.

## Purpose

<The single responsibility of this module, and what it must not do.>

## Location

| Item | Path |
| :--- | :--- |
| Implementation | <link to the file> |
| Tests | <link to the suite> |
| Specification | <link to the spec section> |
| Governing ADR | <link> |

## Contract

| Direction | Item | Type / rule |
| :--- | :--- | :--- |
| Input | <name> | <type, unit, nullability> |
| Output | <name> | <type, unit, provenance fields> |
| Errors | <exception> | <when it is raised; fail-closed behaviour> |

## Invariants

1. <Invariant copied from AGENTS.md / the ADR, not invented>
2. Decimal only where money is involved; `ROUND_HALF_UP`; no Python `round()`.
3. Unknown statutory values raise, never coerce to zero.

## Dependencies

| Depends on | Why | Direction |
| :--- | :--- | :--- |
| <module> | <...> | inbound / outbound |

**Must not depend on:** <forbidden dependency, e.g. clock, network, environment>

## Verification

| Check | Command / suite | Last observed |
| :--- | :--- | :--- |
| Unit | `<command>` | <PASS / FAIL / NOT RUN, date> |
| Property | `<command>` | <...> |
| Contract | `<command>` | <...> |

## Open questions

- <ambiguity ID (B-x / DEC-x) affecting this module, or "none">

## Links

- <specification>
- <related module note>
