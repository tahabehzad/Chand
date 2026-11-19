---
title: "Risk Report — <RISK-ID> — <short title>"
document_id: RISKREP-<NNN>
status: OPEN
as_of: {{date}}
severity: CRITICAL / HIGH / MEDIUM / LOW
owner: <accountable role>
---

# Risk Report — <RISK-ID> — <short title>

> A risk report is not a fraud verdict, a legal conclusion or an approval. Severity may only be lowered by the named owner, with evidence. Canonical risk IDs live in the Holy Bible Appendix C and the readiness/schedule registers; do not invent a competing ID.

## Identification

| Field | Value |
| :--- | :--- |
| **Risk ID** | <RISK-ID> |
| **Category** | Legal / financial / security / architecture / schedule / operational / documentation |
| **Likelihood** | <Low / Medium / High> |
| **Impact** | <Low / Medium / High / Critical> |
| **Severity** | <computed from the source register, not guessed> |
| **Canonical source** | <link to the row in its original register> |
| **Related decision** | <DEC / ADR ID, or "none"> |

## Description

<What can happen, to which component or obligation, and how it becomes visible.>

## Evidence

| Evidence | Status | Location |
| :--- | :--- | :--- |
| <test, migration, contract, external letter> | VERIFIED / UNVERIFIED / MISSING / NOT RUN | <link> |

## Mitigation

| # | Control | Owner | Status |
| :--: | :--- | :--- | :--- |
| 1 | <preventive or detective control> | <role> | <proposed / implemented / verified> |

## Residual exposure

<What remains after the controls above. If the answer is "unknown", say unknown.>

## Escalation

- **Trigger:** <condition that turns this into an incident or a blocking issue>
- **Route:** <DECISIONS_REGISTER / DECISION_REQUIRED_FROM_OWNER / incident procedure>
- **Do not:** weaken an invariant, delete evidence, or mark a failing money-path test as quarantined.

## Links

- <canonical register>
- <related ADR or decision>
