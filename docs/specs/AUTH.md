# Specification: Authentication, Authorization & Tenant Isolation

- **Document ID:** `SPEC-AUTH-001`
- **Status:** Draft — proposed model. Contains a mix of **confirmed** decisions (from accepted ADRs) and **recommendations** requiring approval. Each requirement is labelled **[CONFIRMED]** or **[PROPOSED]**.
- **Author:** Documentation Engineering (Security workstream)
- **Date:** 2026-11-14 (23 Aban 1405 SH)
- **Related:** [`docs/EXECUTION_PLAN.md`](../EXECUTION_PLAN.md) §6, §7, §10 · [`docs/adr/ADR-003-sensitive-data-encryption-alee-blind-indexing.md`](../adr/ADR-003-sensitive-data-encryption-alee-blind-indexing.md) · [`docs/adr/ADR-002-object-storage-worm-ceph-s3-governance.md`](../adr/ADR-002-object-storage-worm-ceph-s3-governance.md) · `REMEDIATED_TECHNICAL_SPECIFICATION_V2.md` §4.1, §4.2

> **Why this document exists.** `REMEDIATED_TECHNICAL_SPECIFICATION_V2.md` §3 mandates a `JWT & Multi-Tenant Middleware` (AuthMW) and §4.1 defines an ERD with **no user, role, permission or membership entity at all**, while `AUDIT_LOGS.actor_id` is left dangling. ADR-002 assumes an "administrative vault" and an "offline administrative vault" key. ADR-003 requires per-tenant Data Encryption Keys. All of that is unimplementable against the current schema. This document closes the gap.

---

## 1. Scope and Authority

**Owner decision update — 2026-11-14:** accepted ADR-006 resolves DEC-004/004a/004b/005. First-party identity with a future OIDC path, opaque revocable sessions, the seven-role set, privileged MFA, separate complete append-only/tamper-evident read evidence, and the candidate/hash/actor schema corrections are now accepted. Older `[PROPOSED]` labels below remain applicable to details outside those exact choices, including session lifetimes/remember-me, emergency access procedure and unresolved key-management variants. P8's original "chain all reads" wording is superseded by ADR-006's split. The original ADR-003 text is retained; ADR-006 formally corrects its index target.

### 1.1 Confirmed decisions inherited from accepted ADRs

| ID | Decision | Source |
| :-- | :--- | :--- |
| D1 | PII is encrypted in the **application layer** with AES-256-GCM; keys never enter the database | ADR-003, `FIND-ARCH-03` |
| D2 | Each tenant has a **distinct Data Encryption Key (DEK)**, wrapped by a master KEK in HashiCorp Vault | ADR-003 |
| D3 | Exact-match PII lookup uses an **HMAC-SHA256 blind index** with an isolated enterprise pepper | ADR-003, `FIND-DATA-02` |
| D4 | Every tenant table carries `tenant_id UUID NOT NULL REFERENCES organizations(id)` and `FORCE ROW LEVEL SECURITY` | `database-engineering` skill, `FIND-ARCH-04` |
| D5 | A **separate cryptographic emergency key** (`s3:BypassGovernanceRetention`) is isolated in an offline administrative vault; standard service accounts are denied it | ADR-002 |
| D6 | Tenant context is injected **per transaction** via `SET LOCAL app.current_tenant_id` | `FIND-ARCH-04` |

### 1.2 Decisions this document proposes (require approval)

| ID | Proposal | Approver | Blocking task |
| :-- | :--- | :--- | :--- |
| P1 | **ACCEPTED — ADR-006:** first-party credentials with Argon2id; future OIDC federation deferred | Project Owner | `P0-T18` |
| P2 | **ACCEPTED — ADR-006:** hashed opaque server sessions with HttpOnly/Secure cookies and CSRF protection; cookie detail must conform to that contract | Project Owner | `P0-T18` |
| P3 | **ACCEPTED — ADR-006:** OWNER, ADMIN, HR_MANAGER, LEGAL_REVIEWER, ANALYST, AUDITOR, SUPER_ADMIN | Project Owner | `P0-T05` |
| P4 | Super-admin is an **out-of-band** role, not assignable in-product | CISO | `P0-T05` |
| P5 | **ACCEPTED — ADR-006:** MFA mandatory for OWNER, ADMIN, LEGAL_REVIEWER, SUPER_ADMIN; hashed recovery codes and two-person administrative recovery | Project Owner | `P0-T18` |
| P6 | Session lifetime: 8 h absolute, 15 min idle, 30-day "remember me" with refresh rotation; every refresh rotates the token | CISO | `P0-T18` |
| P7 | Emergency access requires **two-person authorisation** (dual-key, mirroring the ADR-002 `GOVERNANCE` bypass pattern) | CISO + Legal Counsel | `P0-T18`, `P4-T07` |
| P8 | **ACCEPTED — ADR-006:** chain mutations/calculations/evidentiary events; all reads in separate append-only, independently tamper-evident access log; signed-digest details still require specification | Project Owner | `P0-T10`, `P0-T18` |

> **P2 deserves explicit attention.** `REMEDIATED` §3 names "JWT & Multi-Tenant Middleware". A stateless JWT cannot be revoked before expiry, which is unacceptable for a platform holding encrypted National IDs and salary data accessed by temporary staff and external legal counsel. A server-side opaque session gives immediate revocation, a full access log, and session-level audit attribution. The "JWT" wording in §3 should be read as "bearer-token middleware", not as a mandate for stateless JWTs. **This is a proposed change to an existing specification line and needs CTO sign-off (DEC-004).**

---

## 2. Entity Model

> These entities are **missing** from the `REMEDIATED` §4.1 ERD. Adding them is `P0-T05`.

```
organizations
  id                UUID PK
  legal_name_fa     VARCHAR(200) NOT NULL
  national_company_id VARCHAR(11)            -- 11-digit legal entity ID (modulo-11 validated)
  is_active         BOOLEAN NOT NULL DEFAULT TRUE
  key_store_id      UUID REFERENCES tenant_key_stores(id)
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()

users
  id                UUID PK
  email_normalized  VARCHAR(320) NOT NULL UNIQUE     -- lowercased, trimmed; NOT a blind index
  display_name_fa   VARCHAR(200) NOT NULL
  password_hash     BYTEA                             -- Argon2id (P1)
  password_params   JSONB                             -- {m, t, p, memory_cost, salt_b64}
  totp_secret_enc  BYTEA                             -- AES-256-GCM under the platform KEK
  totp_enabled      BOOLEAN NOT NULL DEFAULT FALSE
  is_platform_admin BOOLEAN NOT NULL DEFAULT FALSE    -- P4: never assignable in-product
  is_active         BOOLEAN NOT NULL DEFAULT TRUE
  failed_attempts   INT NOT NULL DEFAULT 0
  locked_until      TIMESTAMPTZ
  last_login_at     TIMESTAMPTZ
  must_change_password BOOLEAN NOT NULL DEFAULT FALSE
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()

roles
  id                UUID PK
  role_key          VARCHAR(32) NOT NULL UNIQUE    -- OWNER | ADMIN | HR_MANAGER | ...
  display_name_fa   VARCHAR(100) NOT NULL
  description_fa    TEXT
  is_system_role    BOOLEAN NOT NULL DEFAULT TRUE
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()

permissions
  id                UUID PK
  permission_key    VARCHAR(120) NOT NULL UNIQUE  -- e.g. 'simulation:read', 'document:delete'
  resource          VARCHAR(60) NOT NULL
  action            VARCHAR(40) NOT NULL
  description_fa    TEXT
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()

role_permissions
  role_id           UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE
  permission_id     UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE
  PRIMARY KEY (role_id, permission_id)

organization_memberships
  id                UUID PK
  organization_id   UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE
  user_id           UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE
  role_id           UUID NOT NULL REFERENCES roles(id)
  is_active         BOOLEAN NOT NULL DEFAULT TRUE
  invited_by        UUID REFERENCES users(id)
  accepted_at       TIMESTAMPTZ
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
  UNIQUE (organization_id, user_id)
  INDEX  (user_id) WHERE is_active

sessions
  id                UUID PK
  user_id           UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE
  organization_id   UUID REFERENCES organizations(id)   -- NULL for platform-level sessions
  token_hash        CHAR(64) NOT NULL UNIQUE            -- SHA-256 of the opaque token
  refresh_token_hash CHAR(64) UNIQUE
  ip_address        INET
  user_agent        TEXT
  mfa_satisfied     BOOLEAN NOT NULL DEFAULT FALSE
  issued_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
  last_seen_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
  absolute_expires_at TIMESTAMPTZ NOT NULL
  idle_expires_at   TIMESTAMPTZ NOT NULL
  revoked_at        TIMESTAMPTZ
  revoked_reason    VARCHAR(120)
  INDEX (user_id) WHERE revoked_at IS NULL
```

### 2.1 Resolving `AUDIT_LOGS.actor_id`

`REMEDIATED` §4.1 declares `AUDIT_LOGS.actor_id UUID` with no foreign key. Resolution:

- `actor_id` → `users(id)` (the acting human), **nullable** for system-initiated events.
- Add `actor_type VARCHAR(16) NOT NULL DEFAULT 'USER'` with `CHECK (actor_type IN ('USER','SYSTEM','SERVICE','EMERGENCY'))`.
- Add `on_behalf_of_organization_id UUID REFERENCES organizations(id)` so a platform administrator's action is attributable to the tenant it affected.
- Add `actor_display_name VARCHAR(200)` — a **denormalised snapshot** of the actor's name at the time of the event, so the audit trail survives account deletion (required for evidentiary use; the employee/candidate record may be purged under retention policy, but the audit row must remain intelligible).
- The hash-chain payload includes `actor_id`, `actor_type` and `on_behalf_of_organization_id`.

### 2.2 Resolving the `EMPLOYEES` / `CANDIDATES` inconsistency

`ADR-003` directive 3 requires `CREATE UNIQUE INDEX idx_emp_national_id_bindex ON employees (tenant_id, national_id_bindex)`, but the ERD defines `national_id_bindex` on `CANDIDATES`, and `EMPLOYEES` has **no columns at all**.

**Resolution (accepted ADR-006, implementation `P0-T12` pending):** Phase 1 is pre-hire only (ADR-004). The entity that carries a National ID in Phase 1 is the **candidate**. Therefore:

- The blind-index column and index belong to `candidates`.
- `EMPLOYEES` is deferred beyond the current pre-hire scope. ADR-006 formally supersedes ADR-003 directive 3's table target; ADR-003's original text is retained unchanged. No post-hire entity or operational scope is implemented by this correction.

---

## 3. Role and Permission Matrix

**[PROPOSED]** — to be confirmed by the Product Manager and CTO (DEC-004).

| Permission | OWNER | ADMIN | HR_MANAGER | LEGAL_REVIEWER | ANALYST | AUDITOR | SUPER_ADMIN |
| :--- | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| `organization:read` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `organization:manage` | ✓ | ✓ | | | | | ✓ |
| `member:invite` | ✓ | ✓ | | | | | ✓ |
| `member:manage_roles` | ✓ | ✓ | | | | | ✓ |
| `candidate:create` | ✓ | ✓ | ✓ | ✓ | ✓ | | ✓ |
| `candidate:read` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `candidate:delete` | ✓ | ✓ | | ✓ | | | ✓ |
| `document:upload` | ✓ | ✓ | ✓ | ✓ | ✓ | | ✓ |
| `document:read` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `document:delete` | ✓ | ✓ | | ✓ | | | ✓ |
| `document:verify_override` | | | | ✓ | | | ✓ |
| `simulation:read` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `simulation:write` | ✓ | ✓ | ✓ | ✓ | ✓ | | ✓ |
| `simulation:override` | ✓ | | | ✓ | | | ✓ |
| `benchmark:read` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `benchmark:admin` | ✓ | ✓ | | | | | ✓ |
| `statutory_rule:read` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `statutory_rule:propose` | ✓ | ✓ | | | | | ✓ |
| `statutory_rule:activate` | ✓ | | | | | | ✓ |
| `audit_log:read` | ✓ | ✓ | | ✓ | | ✓ | ✓ |
| `audit_log:export` | ✓ | | | ✓ | | | ✓ |
| `key:rotate` | ✓ | | | | | | ✓ |
| `emergency_access:request` | ✓ | | | | | | ✓ |
| `emergency_access:approve` | | | | | | | ✓ (2nd of 2) |

### 3.1 Segregation-of-duties rules (enforced in code, not only in the matrix)

1. `statutory_rule:activate` cannot be held by the same principal as `statutory_rule:propose` for the same rule set within one organisation. *(Four-eyes principle, mirrored from the statutory verification protocol — `SPEC-STAT-001` §4.)*
2. `emergency_access:approve` requires a different principal from `emergency_access:request`, and neither may be a `SUPER_ADMIN` acting alone.
3. `document:verify_override` (which promotes a document's verification status) is restricted to `LEGAL_REVIEWER` and `SUPER_ADMIN` — never to `HR_MANAGER`, who is the most frequent user and therefore the most likely to be compromised.
4. A `SUPER_ADMIN` may not hold an `OWNER` or `ADMIN` role in any organisation. Platform administration and tenant administration are separated.

---

## 4. Authentication Mechanism

### 4.1 Primary: first-party credentials **[PROPOSED — P1]**

| Concern | Control |
| :--- | :--- |
| Password storage | **Argon2id** (RFC 9106), `m=19456` (19 MiB), `t=2`, `p=1`, 16-byte random salt, 32-byte tag. Parameters stored per-user in `password_params` so they can be raised without a schema migration. |
| Password policy | Minimum 12 characters; blocklist of the 50 most common passwords; no composition rules (NIST SP 800-63B guidance); check against a locally bundled breach list — **no external HIBP call**, to satisfy air-gapped operation. |
| Credential stuffing defence | Per-IP and per-account rate limits on the login endpoint; exponential backoff; `failed_attempts` counter with `locked_until` after 10 failures (15 min). |
| Password reset | **Not** by email round-trip. An `OWNER`/`ADMIN` issues a single-use, 30-minute reset token delivered out-of-band. `SUPER_ADMIN` cannot reset another organisation's user. |
| First login | `must_change_password = TRUE`; the user cannot call any business endpoint until the password is changed. |
| MFA **[PROPOSED — P5]** | TOTP (RFC 6238) via a server-side encrypted secret, **mandatory** for `OWNER`, `ADMIN`, `LEGAL_REVIEWER`, `SUPER_ADMIN`. One-time recovery codes, hashed. |

### 4.2 Alternative considered: external IdP (OIDC / Keycloak / LDAP)

**[PROPOSED — deferred]** Enterprise clients may already run Keycloak, AD or an Iranian enterprise identity provider, and requiring re-entry of credentials into our application increases the blast radius of a compromise of *our* system. A future OIDC federation capability is therefore desirable. It is **not** selected for Phase 1 because it adds a mandatory on-site service for clients who do not already run one — the same argument that drives ADR-005's rejection of Redis.

**Mitigation for Phase 1:** the credential store is isolated in its own schema with its own encryption key and its own backup policy, so a later OIDC federation can be added by adding a `users.oidc_subject` column and disabling password login, without migrating any business data.

### 4.3 Shahkar is not authentication **[CONFIRMED — `FIND-ARCH-07`]**

Shahkar validates that a National Code matches a mobile-number subscriber. It is a **candidate identity verification** step, not a workforce authentication mechanism, and it must never be wired into the session lifecycle. `REMEDIATED` §5.2 already models it as an HR-assisted interactive OTP flow; that separation must be preserved in the implementation.

---

## 5. Token and Session Lifecycle **[PROPOSED — P2, P6]**

### 5.1 Token format

Opaque, 256-bit, cryptographically random, URL-safe base64. **No embedded claims** — nothing about the principal, tenant or role is encoded in the token, so it cannot be forged, decoded for reconnaissance, or leaked to a third party without a session lookup.

### 5.2 Lifecycle

```
  POST /auth/login {email, password, totp?}
        │
        ├─ verify Argon2id hash, lockout, rate limit
        ├─ if MFA required and not satisfied → challenge
        ├─ generate session_token (256-bit) and refresh_token (256-bit)
        ├─ store SHA-256(token) and SHA-256(refresh_token) in `sessions`
        ├─ set cookie: pish_session=<token>; HttpOnly; Secure; SameSite=Lax; Path=/
        └─ write AUDIT_LOGS event AUTH_LOGIN (actor_id, org, ip, ua)
```

| Property | Value |
| :--- | :--- |
| Absolute session lifetime | 8 hours |
| Idle timeout | 15 minutes (extended to the absolute cap on each authenticated request) |
| Refresh token lifetime | 30 days, **single use — rotated on every use**; reuse of a consumed refresh token revokes the whole session family |
| Revocation | Immediate — `sessions.revoked_at` is checked on every request; revocation takes effect on the next request, with no token-validity window |
| Cookie | `HttpOnly` (no JS access), `Secure`, `SameSite=Lax`, `Path=/`. `Domain` not set (host-only). |
| CSRF | `SameSite=Lax` **plus** a double-submit CSRF token for all state-changing methods (`POST`/`PUT`/`PATCH`/`DELETE`) |
| Concurrent sessions | Unlimited by default; `OWNER`/`ADMIN` may revoke other sessions for their organisation from the session list. Every session appears in the admin UI with device, IP and last-seen time. |
| Service accounts | Machine-to-machine identities are **not** users. They are separate `service_accounts` rows with scoped permissions and no interactive login. **[PROPOSED]** |

### 5.3 Request pipeline

```
request
  ├─ extract pish_session cookie
  ├─ SELECT ... FROM sessions WHERE token_hash = sha256(token) AND revoked_at IS NULL
  │     ├─ not found → 401
  │     ├─ expired (absolute or idle) → 401, revoke, audit
  │     └─ ok
  ├─ update last_seen_at, refresh idle deadline
  ├─ resolve user, organization_id, active membership, role → effective permission set
  │     └─ no active membership → 403 (not 404; do not leak membership state)
  ├─ SET LOCAL app.current_tenant_id = '<organization_id>'   ← within the request transaction
  ├─ execute handler; RLS applies automatically
  └─ commit / rollback (SET LOCAL is transaction-scoped and auto-clears)
```

**The tenant context is set from the server-resolved membership, never from a client-supplied header.** A `X-Tenant-Id` header, if accepted at all, may only be used as a *cross-check* that fails closed on mismatch.

---

## 6. Tenant Isolation

### 6.1 Database layer **[CONFIRMED — D4, D6]**

- Every tenant table: `tenant_id UUID NOT NULL REFERENCES organizations(id)`.
- `ALTER TABLE <t> FORCE ROW LEVEL SECURITY;` — required because table owners bypass RLS otherwise (`FIND-ARCH-04`).
- Policy pattern:

```sql
CREATE POLICY tenant_isolation_policy ON <table>
  USING      (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid)
  WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid);
```

- The context is set with `SET LOCAL` **inside the request transaction** so it is discarded on commit or rollback — no session-pool leakage.
- If PgBouncer is used, `server_reset_query = DISCARD ALL` is mandatory, and transaction pooling is only safe because `SET LOCAL` is transaction-scoped.

### 6.2 Application layer

- **Fail closed**: a query with no tenant context returns zero rows and raises, never returns all rows.
- Every repository method takes the tenant from the request context, not from a caller-supplied argument. A caller-supplied tenant id is permitted **only** for platform-level (super-admin) operations, which must be individually audited.
- Cross-tenant references (e.g. a candidate belonging to tenant A referenced by a document in tenant B) are impossible by construction: every FK is tenant-scoped with a composite constraint `UNIQUE (tenant_id, id)`.

### 6.3 Storage layer

- Object storage keys are **tenant-prefixed**: `tenants/{tenant_id}/documents/{document_id}/{...}`. An S3 key alone never grants access; the application resolves the tenant from the database first.
- `ADR-002` standard service accounts are denied `s3:BypassGovernanceRetention`. Deletion/expungement requires the separate emergency path (§9).

---

## 7. Audit Actor Resolution and Access Logging

### 7.1 Every access is an audit event

| Event | Actor | Notes |
| :--- | :--- | :--- |
| `AUTH_LOGIN` / `AUTH_LOGOUT` / `AUTH_LOGIN_FAILED` | USER or SYSTEM | includes IP, user agent |
| `AUTH_MFA_CHALLENGE` / `AUTH_MFA_FAILED` | USER | |
| `SESSION_REVOKED` | USER (target) + actor | |
| `MEMBER_INVITED` / `MEMBER_ROLE_CHANGED` / `MEMBER_REMOVED` | USER | |
| `CANDIDATE_CREATED` / `CANDIDATE_VIEWED` / `CANDIDATE_DELETED` | USER | `CANDIDATE_VIEWED` is high volume — retained in a separate non-hashed access log to keep the hash chain tractable |
| `DOCUMENT_UPLOADED` / `DOCUMENT_VERIFIED` / `DOCUMENT_OVERRIDE` / `DOCUMENT_DELETED` | USER or SYSTEM | |
| `SIMULATION_RUN` / `SIMULATION_EXPORTED` | USER | payload hash + `rule_set_version_id` |
| `RULE_SET_PROPOSED` / `RULE_SET_ACTIVATED` | USER | includes the diff |
| `AUDIT_EXPORT` | USER | |
| `EMERGENCY_ACCESS_GRANTED` | SYSTEM + 2 actors | highest severity |

### 7.2 Hash chaining **[CONFIRMED — `REMEDIATED` Module 7]**

```
H_n = SHA256(H_{n-1} ‖ ISO8601_timestamp ‖ tenant_id ‖ actor_id ‖ actor_type ‖ canonical_JSON(payload))
```

- `canonical_JSON` = sorted keys, no insignificant whitespace, UTF-8, `NaN`/`Infinity` rejected.
- The ledger is **append-only**; database triggers reject `UPDATE` and `DELETE`.
- High-frequency access events (reads) are recorded in a **separate** `ACCESS_LOG` table (retained, queryable, not hash-chained). The hash chain covers **mutations and evidentiary events only**. Rationale: chaining every read makes the chain cost proportional to traffic and creates a write-amplification bottleneck on the hot path. The Phase 0 gate ("zero plaintext PII", RLS penetration suite) is unaffected; this split must be confirmed by the Security Architect.

### 7.3 PII in the ledger

The ledger must never contain plaintext National IDs, mobile numbers, Sheba numbers or candidate names. It stores **blind indexes** and **encrypted values** only. See the `financial-data-integrity` skill rule 24.

---

## 8. Key Management and Rotation

### 8.1 Key hierarchy **[CONFIRMED — D1, D2]**

```
Platform Master KEK            (in HashiCorp Vault; or an Argon2id-derived local KEK
                                from an encrypted local master config in air-gapped sites)
   └── Tenant DEK               (one per organization; wraps that tenant's PII)
          ├── ADEK (per-field)  (AES-256-GCM, unique 96-bit IV per encryption)
          └── Blind-index pepper (HMAC key for that tenant's blind indexes)
```

### 8.2 Blind-index pepper

- A **single platform-wide pepper** held in the Vault (or the encrypted local master config), separate from every DEK.
- The pepper must not be derivable from any data stored in the database. If the pepper is lost, **existing blind indexes are permanently unusable** and every candidate must be re-enumerated by decrypting the ciphertext column and re-hashing. This is a deliberate trade-off: a database dump alone does not permit re-identification.
- **Rotation of the pepper requires a full re-index of every tenant** — therefore the pepper is rotated only as part of a planned migration, never on a schedule.

### 8.3 Rotation schedule

| Key | Rotation | Method |
| :--- | :--- | :--- |
| Platform Master KEK | Annually, or on suspected exposure | Vault key rotation; re-wrap tenant DEKs (no data re-encryption required) |
| Tenant DEK | Annually | Generate new DEK; re-encrypt every PII field of that tenant in a single batched transaction with resumable progress |
| Field ciphertext | Never (per-encryption random IV) | — |
| Blind-index pepper | Only on a security incident, with a full re-index migration | — |
| Session tokens | On every use (refresh rotation) | — |

### 8.4 Emergency access key **[CONFIRMED — D5]**

The `s3:BypassGovernanceRetention` capability is held in an **offline administrative vault**, separate from the runtime Vault. Standard application service accounts never possess it. Access requires the two-person procedure in §9.

### 8.5 P0-T06 field-encryption implementation contract

Scope: the accepted ADR-003 primitive only, with key retrieval behind a protocol. This defines the task's measurable interface; it does not settle the conflicting hierarchy/rotation descriptions in §8.1–§8.3 or select a key-management backend.

- Module: `backend/app/core/security/pii_transformer.py`; owner: Codex implementation agent. Independent security review is required before review-ready status.
- `EncryptionContext` is immutable and requires explicit UUID `tenant_id`, UUID `record_id`, nonempty schema `field_name`, and explicit nonempty `key_id`. Names/IDs are metadata, never PII or key material. Field/key names are bounded to 128 characters and contain no control characters. The context has no revealing repr.
- `TenantKeyRegistry.get_key(*, tenant_id, key_id) -> bytes` supplies an unwrapped **32-byte** tenant DEK. The transformer never generates, persists, caches or silently substitutes a DEK; the registry's production authorization/custody/rotation is P0-T08. No production in-memory registry is provided.
- `PiiFieldTransformer.encrypt(value: bytes, *, context) -> bytes` uses AES-256-GCM, fresh CSPRNG 12-byte nonce and full 16-byte authentication tag. Binary layout is exactly `nonce || ciphertext || tag`, retaining ADR-003's BYTEA format. Empty and arbitrary binary values are valid.
- `decrypt(value: bytes, *, context) -> bytes` must authenticate before returning any plaintext. UTF-8 `encrypt_text`/`decrypt_text` helpers preserve Persian/ZWNJ text exactly; monetary values are never implicitly converted or rounded.
- Associated authenticated data is the fixed domain `pish:pii:v1` plus canonical UTF-8 JSON (sorted keys, compact separators) of tenant UUID hex, record UUID hex, schema field and key reference. The same explicit context is required for decryption; tenant/record/field/key substitution fails authentication, even if a defective test registry returns identical key bytes. Callers retain the non-secret key reference with the field's provenance; no key/version auto-detection or old-key fallback occurs.
- Errors use fixed messages without supplied plaintext, ciphertext, key material or registry exception text. Missing/invalid keys fail closed. Malformed, tampered or wrong-context ciphertext raises `PiiDecryptionError`; authentication failure returns no partial result. Chained registry exceptions are suppressed from rendered tracebacks. No logging occurs in the transformer.
- Acceptance: round-trip synthetic empty/binary/Persian field representations; different nonce/output on repeated input; bit-flip/tag/nonce/truncation rejection; wrong tenant/record/field/key rejection; invalid/missing-key rejection; real captured log/error output contains neither synthetic plaintext nor synthetic key material. CR-01…CR-03 apply here; CR-04 blind-index determinism belongs to P0-T07, not this primitive.
- P0-T01's installed-toolchain portion is verified; its CI clause is still incomplete. Local primitive evidence does not complete P0-T01, P0-T08, P0-T15 or the Phase 0 gate. The task remains review-ready pending integration/CI rather than bypassing that dependency.

Library contract checked against the pinned release's [official AESGCM documentation](https://cryptography.io/en/45.0.7/hazmat/primitives/aead/#cryptography.hazmat.primitives.ciphers.aead.AESGCM): never reuse a nonce with a key; the library appends the 16-byte tag and rejects invalid authentication. Random-nonce lifetime/usage limits and key rotation enforcement are integration requirements for P0-T08; local tests do not prove unlimited nonce uniqueness or memory zeroization.

---

### 8.6 P0-T07 blind-index implementation contract

Scope: the ADR-003 blind index and the normalisation rule the corpus leaves open
(Holy Bible §5.6, QB-10, HB-MR-011). This section publishes the rule; it does not
settle pepper custody or rotation, which remain P0-T08.

- Module: `backend/app/core/security/blind_index.py`; owner: Security Eng. The digest is lowercase hex and exactly 64 characters, so it fits ADR-003's `CHAR(64)` column and its unique B-Tree index on `(tenant_id, national_id_bindex)`.
- Interface: `BlindIndexPepperRegistry.get_pepper() -> bytes` supplies the single isolated pepper (at least 32 bytes); `BlindIndexService.index(value, *, tenant_id, field) -> str` returns the digest; `normalise(value, *, field) -> str` publishes the canonical form. No registry, default pepper, cache or database-derived key is provided in this task.
- Supported fields: `national_id`, `mobile`, `sheba`. Names, salaries and free text are **not** blind-indexed: exact-match lookup is a property of these three identifiers only (§7.3).
- **Normalisation rule** (delivered here because HB-MR-011 requires it written down):

| Field | Canonical form | Folding applied before validation |
| :--- | :--- | :--- |
| `national_id` | exactly 10 ASCII digits, leading zeros **kept** | Persian (U+06F0–06F9) and Arabic-Indic (U+0660–0669) digits folded to ASCII; NFKC; LRM/RLM, bidi embedding/isolate controls, BOM, space/NBSP, hyphen/en-dash, dot, underscore and ZWNJ removed |
| `mobile` | `09` + 9 digits | the same folding, plus `+98`/`0098`/`98` international prefixes reduced to the national form |
| `sheba` | `IR` + 24 digits, upper-cased | the same folding; grouping spaces and hyphens removed |

- No padding, truncation or digit-count repair is performed. A value that does not validate is **refused**, never hashed: an index over a malformed identifier would create an undetectable false match.
- Message layout: `b"pish:bindex:v1" + NUL + tenant UUID hex + NUL + field key + NUL + canonical value`, hashed with HMAC-SHA256 under the pepper. Binding the tenant into the message gives the separation §8.1 draws from a per-tenant salt while keeping the single platform pepper of §8.2; a digest is valid for exactly one tenant and one field.
- Failure paths use fixed messages (`Blind-index pepper unavailable.`, `National ID is not ten digits.`, `Mobile number is not a national mobile.`, `Sheba number is not IR plus twenty-four digits.`, `Blind-index value must be text.`). No supplied identifier, key material or registry exception reaches a message, a log line or a traceback; the pepper is read per call and never cached.
- Acceptance (verified): determinism within a tenant and field; different digest across tenants and fields; every documented spelling of one identifier collapses to one digest; leading zeros remain significant; malformed identifiers and unusable peppers fail closed with one registry call; no output on the success path.
- **NOT RUN in this task**: the database-level evidence (the pepper absent from any database object, the unique B-Tree lookup under 1 ms), pepper rotation with full re-index, and independent security review. `P0-T07` is therefore `READY_FOR_REVIEW`, not `APPROVED`, and contributes to P0-T15 rather than completing it. Evidence: `BOOTSTRAP_CHANGELOG.md` §25.

---

## 9. Administrative and Emergency Access

### 9.1 Platform administration **[PROPOSED — P3, P4]**

- `SUPER_ADMIN` is granted **out of band**: a break-glass procedure operated by two named custodians, recorded in a sealed register.
- A super-admin session is bound to a single organisation context for every action; switching tenant requires an explicit, separately audited action.
- Every super-admin action is written to the ledger with `actor_type='SUPER_ADMIN'` and `on_behalf_of_organization_id` set.
- Super-admin cannot read plaintext PII directly. PII is only ever visible through a normal application feature that itself writes an audit event — otherwise the super-admin path becomes a permanent backdoor around the access model.

### 9.2 Emergency access to WORM-retained data **[PROPOSED — P7, D5]**

Trigger: a court order for expungement, or a statutory privacy request (E-Commerce Law Art. 58) that must be reconciled with an immutable retention obligation.

Procedure (two-person):
1. `OWNER` or `SUPER_ADMIN` raises an `EMERGENCY_ACCESS_REQUEST` with a legal reference number.
2. A **second, different** principal (`OWNER` of the same organisation, or `SUPER_ADMIN`) approves.
3. The offline vault is opened by its custodian; the bypass key is applied for the specific object only, with a short validity window.
4. The action is recorded in the ledger with `actor_type='EMERGENCY'`, both approver IDs, the legal reference, the object key and the affected object's `sha256`.
5. A post-hoc report is generated for the legal file.

**Constraint inherited from ADR-002:** `GOVERNANCE` mode was chosen over `COMPLIANCE` mode precisely so that this path exists. If the bypass key is lost, the data cannot be deleted — that is the accepted trade-off.

---

## 10. Session and Access Auditing Requirements

| ID | Requirement | Verification |
| :-- | :--- | :--- |
| AU-01 | An unauthenticated request to any business endpoint returns 401 and reveals no resource existence | Integration test |
| AU-02 | A session token from tenant A cannot read any row of tenant B | RLS penetration test (Phase 0 gate) |
| AU-03 | A revoked session is rejected on the very next request | Integration test |
| AU-04 | Reusing a consumed refresh token revokes the entire session family | Integration test |
| AU-05 | `SET LOCAL` context does not survive the transaction | Multi-tenant test with connection reuse |
| AU-06 | Every mutation appears in the hash chain, and the chain verifies end-to-end | Chain verification test |
| AU-07 | Every read appears in the access log | Integration test |
| AU-08 | A platform super-admin action is attributable to both the actor and the affected tenant | Audit test |
| AU-09 | An emergency-access action requires two distinct principals | Workflow test |
| AU-10 | Passwords, session tokens and TOTP secrets never appear in logs, the ledger or the database in plaintext | Grep-based secret scan in CI |

---

## 11. Open Decisions

| ID | Question | Recommendation | Approver | Status |
| :-- | :--- | :--- | :-- | :--- |
| DEC-004 | Is the session model server-side opaque tokens or stateless JWT? | Opaque server-side sessions (P2) | CTO | OPEN |
| DEC-004a | Which principals require mandatory MFA? | `OWNER`, `ADMIN`, `LEGAL_REVIEWER`, `SUPER_ADMIN` | CISO | OPEN |
| DEC-004b | Is hash-chaining of high-frequency reads required, or is a separate access log acceptable? | Separate access log; chain mutations only | CISO | OPEN |
| DEC-005 | Confirm `EMPLOYEES` removal from the Phase 1 ERD and correction of ADR-003's index directive to `candidates` | Confirm | CTO + DBA | OPEN |

---

## 12. Related Tasks

| Task | Phase | Title | Status |
| :--- | :--- | :--- | :--- |
| `P0-T05` | 0 | Tenant identity schema: organizations, users, roles, permissions, memberships, sessions | NOT_STARTED |
| `P0-T06` | 0 | ALEE encryption module (`PiiFieldTransformer`) | READY_FOR_REVIEW (primitive verified, §8.5; production registry and independent review outstanding) |
| `P0-T07` | 0 | HMAC-SHA256 blind-index module | READY_FOR_REVIEW (module and 45 tests verified, §8.6; pepper custody, DB-level evidence and independent review outstanding) |
| `P0-T08` | 0 | Key management: Vault adapter, local KEK, rotation procedures | NOT_STARTED |
| `P0-T09` | 0 | RLS policies + per-transaction tenant context helper | NOT_STARTED |
| `P0-T10` | 0 | Append-only hash-chained audit ledger | NOT_STARTED |
| `P0-T12` | 0 | ERD defect correction (`CHAR(64)`, `EMPLOYEES`/`CANDIDATES`, `actor_id` FK) | NOT_STARTED |
| `P0-T18` | 0 | Authentication & session implementation | NOT_STARTED |
| `P4-T07` | 4 | Legal review sign-off | NOT_STARTED |
