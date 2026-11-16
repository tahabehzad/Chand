---
name: adr-authoring
description: Authors, formats, and maintains Architecture Decision Records (ADRs) following standard MADR/Nygard formats, capturing context, alternatives, trade-offs, and consequences.
---

# Architecture Decision Record (ADR) Authoring Skill

## Purpose
Standardize the documentation of significant architectural and technical decisions, recording the context, evaluated alternatives, selection rationale, and downstream consequences.

## ADR Template Format (MADR 3.0 / Nygard)
Every ADR document must follow this exact structure:
```markdown
# ADR-[NUMBER]: [Short Title of Architectural Decision]

- **Status**: [Proposed | Accepted | Superseded | Deprecated]
- **Date**: [YYYY-MM-DD / SH Date]
- **Deciders**: [List of roles / stakeholders]
- **Consulted**: [Subject matter experts consulted]

## Context and Problem Statement
[Describe the architectural dilemma, technical constraints, security concerns, or business drivers.]

## Decision Drivers
- [Key driver 1, e.g., Licensing compliance, intranet deployment feasibility]
- [Key driver 2, e.g., PII confidentiality, latency budget]

## Considered Options
1. **Option 1**: [Description]
2. **Option 2**: [Description]
3. **Option 3**: [Description]

## Decision Outcome
Chosen option: **[Option Name]**, because [justification linking to decision drivers].

### Positive Consequences
- [Benefit 1]
- [Benefit 2]

### Negative Consequences / Trade-offs
- [Trade-off 1]
- [Mitigation strategy]

## Pros and Cons of Considered Options
[Detailed comparison matrix]

## Implementation Directives
[Specific technical rules, library choices, or code patterns required to realize the decision.]
```
