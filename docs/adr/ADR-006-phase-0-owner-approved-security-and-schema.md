# ADR-006: Owner-approved Phase 0 identity, audit scope and schema corrections

- **Status**: Accepted
- **Date**: 2026-11-14
- **Deciders**: Project Owner, by explicit confirmation of the four proposals in the project chat
- **Consulted**: Technical recommendations in DEC-004, DEC-004a, DEC-004b and DEC-005; no named human CISO, CTO, DBA or legal signatory is asserted
- **Supersedes**: ADR-003 implementation directive 3 **only as to the indexed table name** (`employees` → `candidates`). All other ADR-003 decisions remain binding; its original text is retained unchanged.

## Context and Problem Statement

The owner reviewed the concrete four-item package in `docs/DECISION_REQUIRED_FROM_OWNER.md`, was asked to approve all four before dependent work started, and answered yes. The owner has final strategic and architectural authority under the project handoff. This record preserves that approval without pretending that engineering role titles are named human signatures. Implementation, independent review and phase-gate evidence are separate from decision acceptance.

The authoritative specification names JWT middleware but does not define a revocable session model. ADR-003 names an employee index while ADR-004 scopes the product to candidates before hiring. The audit ledger has an unresolved actor target and high-volume read scope. These contradictions must be reconciled before dependent migrations are written.

## Decision Drivers

- Immediate revocation of access to sensitive data.
- Mandatory second factor for privileged operations.
- Complete read-access evidence without coupling every read to the mutation chain.
- Traceable human actors and full-length cryptographic hashes.
- Preserve the accepted pre-hire boundary and historical decisions.

## Considered Options

1. DEC-004 session options (a) stateless JWT, (b) opaque server sessions, (c) hybrid; identity-provider options (a) first-party, (b) external IdP, (c) first-party now with future federation.
2. DEC-004a options (a) optional MFA, (b) privileged-role MFA, (c) universal MFA.
3. DEC-004b options (a) chain all events, (b) separate complete read log, (c) sampled reads.
4. DEC-005 options A (candidate/schema correction), B (employee placeholder), C (separate audit actor entity).

## Decision Outcome

The owner accepted the following four proposals:

| Register | Accepted choice | Exact boundary |
| :--- | :--- | :--- |
| DEC-004 | Session (b), identity provider (c), MFA (b) | First-party Argon2id credentials; random revocable server-side opaque sessions, hashed at rest, in HttpOnly/Secure cookies with CSRF protection; future OIDC integration remains deferred. Retain the existing proposed seven-role set for the identity schema. This overrides the JWT label in `REMEDIATED` §3 for the session mechanism only. |
| DEC-004a | (b) | MFA required for OWNER, ADMIN, LEGAL_REVIEWER and SUPER_ADMIN; hashed recovery codes and two-person administrative recovery. Other roles are not made mandatory-MFA by this approval. |
| DEC-004b | (b) | Hash-chain mutations, calculations and evidentiary events. Record all reads in a separate append-only access log with independent tamper evidence via signed digests; no read sampling. Digest cadence, signing-key custody and anchor storage must be specified before that path is implemented. |
| DEC-005 | A | Hashes CHAR(64); blind index and unique `(tenant_id, national_id_bindex)` index on `candidates`; operational employees deferred beyond the current pre-hire scope; human audit `actor_id` references `users(id)`. Null/system actor details still require the explicit implementation contract. |

### Positive Consequences

- The four engineering decision gates are resolved by actual owner authorization.
- The session and candidate-index contradictions have a rank-1 reconciliation without rewriting ADR-001…004 or the source specification.
- Security foundations can proceed within their documented dependencies.

### Negative Consequences / Trade-offs

- Sessions add a database lookup and operational responsibility for credential recovery.
- Separate read evidence requires a defined signing/anchoring design before use; an ordinary editable access log does not satisfy this decision.
- Acceptance is not implementation, legal certification, or independent security review.

## Pros and Cons of Considered Options

The comparisons in DEC-004/004a/004b/005 and the owner review package remain the rationale. Opaque sessions prioritize revocation over stateless validation. Privileged MFA limits the initial enrolment burden. Complete separate read evidence avoids sampling while limiting mutation-chain contention. The candidate correction avoids adding post-hire operations.

## Implementation Directives

1. Mark only DEC-004, DEC-004a, DEC-004b and DEC-005 resolved; retain their recommendations and record the actual approver as Project Owner. Do not invent CISO/CTO/DBA sign-offs.
2. Reconcile `AUTH.md` labels only for the accepted choices. Session timeout/remember-me parameters, emergency WORM access procedure, key hierarchy/rotation conflicts, digest implementation and other unapproved details are not silently ratified.
3. Preserve RLS/FORCE RLS, application-layer AES-256-GCM, isolated blind-index pepper and append-only evidence invariants.
4. P0-T06 may implement the existing accepted field-encryption primitive behind a key-registry protocol. It must not select or implement Vault/local KEK/pepper hierarchy as a side effect.
5. CI provider (DEC-F), deployment (DEC-010), asynchronous execution (ADR-005/DEC-003), statutory activation and legal/data dependencies remain open. No commit, push or deployment is authorized by this ADR.
6. The five-phase/20-week roadmap and immutable statutory seeds are unchanged. Task status changes require observed implementation evidence.

Verification and accountable owners are recorded in `docs/BOOTSTRAP_CHANGELOG.md` §11.
