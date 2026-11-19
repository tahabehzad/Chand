# ADR-012: Persisted work profiles, encrypted local documents and proportional payroll

- **Status**: Accepted — owner requested persistence, real uploads and work/seniority effects on 2026-11-17; confirmed full-time 44-hour gross excluding seniority and statutory-only experience effects; delegated the local storage decision to Codex.
- **Date**: 2026-11-17
- **Deciders**: Project Owner
- **Consulted**: Codex implementation and independent engineering review; no external legal certification asserted.

## Context and Problem Statement

The calculator's additional work-profile fields were ephemeral. ADR-010 permitted only evidence metadata; byte storage and work/seniority integration therefore need a narrow prospective amendment. Owner explicitly asks for all three. Production key management, statutory 1405 verification and performance weights remain unresolved.

## Decision Drivers

- Real read-back after refresh; explicit employee association, never automatic matching.
- Application-layer encryption, tenant isolation and immutable calculation history.
- No experience premium or duplicated part-time adjustment.

## Considered Options

1. Keep the local draft and metadata-only evidence.
2. Require production Ceph/Vault before any local upload.
3. Local-development-only encrypted PostgreSQL records with an external local master key.

## Decision Outcome

Chosen option: **3**, using the owner's delegated local implementation choice. This supersedes ADR-010's metadata-only exclusion **for the loopback development prototype only**. Documents, profile text and calculation snapshots are AES-256-GCM encrypted before database writes; the master key is kept under git-ignored `.secrets/`, never in the database or logs. Per-tenant keys are derived with HKDF-SHA256. Production/staging refuse this provider. This does not select a production P0-T08 hierarchy or amend ADR-002's production Ceph/GOVERNANCE target; no rejected technology is introduced.

The owner selects full-time monthly gross including the entered allowances but excluding seniority. Weekly schedule ratio is ordinary weekly hours / 44. Monthly schedule requires **paid calendar-equivalent days including paid rest**, not attendance days; ratio = daily hours × paid days / the baseline's monthly paid-hour divisor. Ratios above one are refused; explicit overtime/night fields remain separate. Monthly attendance days alone are insufficient to infer paid rest and are not silently converted.

Experience effects are statutory only. Recognised seniority must be explicitly supplied, not inferred from professional/insurance history. First eligible unclassified year uses the active rule set's seniority base; earlier accumulated bases or classified-workshop rates require a manager-supplied documented daily amount. No multiplication of this year's increment by total years. Employer tenure feeds the existing ordinary-termination calculation; unrelated experience never raises pay.

### Positive Consequences

- Data and files survive refresh without plaintext personal data in new tables.
- Changes to hours and eligible seniority produce traceable server calculations.

### Negative Consequences / Trade-offs

- Local key backup is essential; loss prevents decryption. No automatic regeneration over an existing key.
- Prototype only, not production authentication, malware certification or a 1405 activation.
- Monthly plans require paid-day knowledge; multi-year/classified seniority requires a documented rate.

## Pros and Cons of Considered Options

| Option | Benefit | Cost |
| :--- | :--- | :--- |
| 1 | No persistence risk | Does not fulfil request |
| 2 | Production target | Services and production choices unavailable |
| 3 | Bounded local delivery | External key custody and explicit prototype restriction |

## Implementation Directives

Follow [WORK_PROFILE_PAYROLL](../specs/WORK_PROFILE_PAYROLL.md). New tenant tables receive FORCE RLS/policy in the same additive migration. No historical row/seed is rewritten. Use existing authentication/tenant context, exact Decimal preparation and the existing payroll engine. Require independent security/financial review and observed persistence, cross-tenant, encrypted-upload round-trip and numerical tests. Apply only the reviewed new migration to local development; do not run unrelated draft migrations or destructive test suites on its data.
