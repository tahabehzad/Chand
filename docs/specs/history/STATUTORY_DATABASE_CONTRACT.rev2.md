# Specification: Statutory Provenance Database Contract (P0-T04)

- **Document ID:** `SPEC-STATDB-001`
- **Status:** **PROPOSED — BLOCKED** (corrective revision of the 2026-11-15 draft; WBS `P0-T04` is `BLOCKED`)
- **Revision:** 2 — corrective, 2026-11-15
- **Author:** MiniMax, under an exclusive **contract-only corrective edit** assigned by the coordinator (see `docs/BOOTSTRAP_CHANGELOG.md` §17.4). The revision-1 draft was written by OpenCode (GLM) as the `P0-T04` packet; its two structural conclusions are **withdrawn, not ratified**.
- **Date:** 2026-11-15
- **Related:** `docs/DECISIONS_REGISTER.md` **DEC-012** (`OPEN — BLOCKING`) · `docs/specs/STATUTORY_INGESTION.md` (`SPEC-STAT-001`, §§2.2, 4.2, 5.2, 5.5, 10) · `docs/specs/AUTH.md` (`SPEC-AUTH-001`, §§1.1, 2, 2.1, 6.1) · `docs/specs/DEPLOYMENT.md` §§4.2, 5.1 · `docs/PISH_HESABDARI_HOLY_BIBLE.md` §§0.3, 5.1, 5.2, 5.3, 5.4, 5.7, 5.8, 5.9, 13.1, 13.8 · `docs/adr/ADR-003` · `docs/adr/ADR-006` · `REMEDIATED_TECHNICAL_SPECIFICATION_V2.md` §4.1 · `docs/EXECUTION_PLAN.md` §14.3 rows `P0-T04`, `P0-T05`, `P0-T09`

> **Blocking notice — read before using this document.**
> Two structural questions (§2.1 tenancy/isolation, §2.2 identity-FK enforcement) are **unresolved decisions reserved to the owner** (DEC-012, `OPEN — BLOCKING`; required approvers: CTO/DBA and Security Architect). This document therefore **proposes**; it approves nothing, ratifies no ADR, selects no schema variant and creates no accepted schema. **No migration implementation may begin** until DEC-012 is `RESOLVED` by a named approver and this contract is re-issued at revision 3 with the ratified choices. Source conflicts in §2.1/§2.2 must be resolved by the owner, not by an implementation default.

---

## 0. What this revision changes, and why

| # | Revision-1 claim | Disposition | Basis |
| :-- | :--- | :--- | :-- |
| 1 | "**Derived conclusion:** the five statutory tables are platform-global — no `tenant_id`, no RLS policy, no `FORCE ROW LEVEL SECURITY`" (§2.2 rev. 1), recorded as "a recorded design decision, testable (AC-06)" | **Withdrawn.** Re-cast as an unratified proposal in §2.1 with alternatives and consequences | A *draft* schema's silence is not a decision. `SPEC-STAT-001` is `Draft — awaiting Legal Counsel and Certified Tax Accountant sign-off`; Holy Bible §5.3 and §5.4 use different table-scope wording; `AGENTS.md` §3 forbids selecting an unresolved schema variant |
| 2 | "**Derived resolution:** FK constraints targeting `users(id)` are deferred" (§2.1 rev. 1), enforced by AC-07 ("no FK to `users`") | **Withdrawn.** Re-cast as an unratified proposal in §2.2; the *absence* of an FK is no longer an acceptance criterion | `DEC-012`; `AGENTS.md` §3; the `ON DELETE` semantics and the owning migration were never decided |
| 3 | "no `pgcrypto` — Holy Bible §13.2 rejected register" (§2.3 rev. 1) | **Attribution corrected** to ADR-003 (deciding authority) + the `security-threat-model` skill (behaviour contract) | §2.3 below; `AGENTS.md` §2 invariant 13 |
| 4 | "DEPLOYMENT.md §12.1" cited for the Alembic configuration | **Citation corrected** to `DEPLOYMENT.md` §4.2 (§12.1 is the air-gapped verification checklist) | §1, §5 |
| 5 | Status "Active"; §7 "Questions recorded … (**none blocks this packet**)" | Corrected to `PROPOSED — BLOCKED`; the two structural questions are `OPEN — BLOCKING` | DEC-012; BOOTSTRAP_CHANGELOG §17.4 |
| 6 | §8 verification matrix "see packet report" | Replaced by the **observed** state: no migration source exists; no packet report was produced | §8 |

Revision 1 remains in the git history; it is not deleted or rewritten (Holy Bible §13.1, "Historical documents are never deleted or overwritten").

---

## 1. Deliverable set — proposed scope and actual state

This contract fixes the *database* slice of `P0-T04` only: a development-only Alembic baseline plus the statutory provenance tables. It does not activate any rule set, seed any statutory value, implement the loader (`P1-T01`), the audit ledger (`P0-T10`), the identity schema (`P0-T05`) or any production migration.

| # | Artefact | Owner file | Source | State (observed 2026-11-15) |
| :-- | :--- | :--- | :-- | :-- |
| D1 | Alembic configuration | `backend/alembic.ini` | WBS `P0-T04` Del; `DEPLOYMENT.md` §4.2 | **Present** — `sqlalchemy.url` empty by design (no DSN/credential in the file) |
| D2 | Alembic environment + one baseline migration | `backend/alembic/**` | WBS `P0-T04` Del ("initial migration") | **NOT DELIVERED** — `backend/alembic/` contains only `script.py.mako`; no `env.py`, no `versions/`, **no migration source exists** |
| D3 | SQLAlchemy models for the statutory tables | `backend/app/models/statutory.py` | WBS `P0-T04`; Holy Bible §5.1 | **Present but unreviewed** — encodes the withdrawn assumptions of §2.1/§2.2 rev. 1 (no `tenant_id`, no RLS, user FKs omitted). **Not an accepted schema**; must be re-derived after ratification |
| D4 | Integration tests incl. the migration lint | `backend/tests/integration/test_statutory_migrations.py` | WBS `P0-T04` AC/V; Holy Bible §5.8 | **NOT DELIVERED** — `backend/tests/integration/` contains only an empty `__init__.py` |
| D5 | This contract | `docs/specs/STATUTORY_DATABASE_CONTRACT.md` | WBS `P0-T04` B column ("detailed provenance/FK/tenancy contract") | **Revised** (this document) — `PROPOSED — BLOCKED` |

Supporting package files exist: `backend/app/models/__init__.py` (not empty — it declares the shared `DeclarativeBase` used by the statutory models) and `backend/tests/integration/__init__.py` (empty, matching `tests/unit` and `tests/api`).

---

## 2. The three structural questions — proposals, not decisions

### 2.1 Tenancy and isolation of the statutory tables — `OPEN — BLOCKING` (DEC-012 part 1)

**Withdrawn claim (revision 1):** "the five statutory tables are platform-global — no `tenant_id`, no RLS policy, no `FORCE ROW LEVEL SECURITY`", asserted as a derived, testable design decision.

**What the sources actually say — exact citations.**

| Source (rank) | Wording | Scope word |
| :--- | :--- | :--- |
| Holy Bible §5.3 row 1 | "Every **tenant table**: `tenant_id UUID NOT NULL REFERENCES organizations(id)`" | *tenant table* |
| Holy Bible §5.3 row 2 | "Every **tenant table**: a policy **and** `ALTER TABLE … FORCE ROW LEVEL SECURITY`, in the same migration" | *tenant table* |
| Holy Bible §5.3 row 3 | "Every FK target: `UNIQUE (tenant_id, id)`" | tenant-scoped FK pattern |
| Holy Bible §5.4 row 1 | "`tenant_id` on **every table** + RLS policy + `FORCE RLS`" — status `ACCEPTED` | *every table* ← **conflict with §5.3** |
| Holy Bible §5.8 (RLS row) | "A new **tenant table** is created with `tenant_id`, its policy and `FORCE RLS` **in the same migration**" | *tenant table* |
| `DEPLOYMENT.md` §4.2 (RLS row) | "Every new **tenant table** is created with `tenant_id`, its policy, and `FORCE ROW LEVEL SECURITY` **in the same migration**" | *tenant table* |
| `SPEC-AUTH-001` §1.1 D4, §6.1 | "Every **tenant table** carries `tenant_id UUID NOT NULL REFERENCES organizations(id)` and `FORCE ROW LEVEL SECURITY`" | *tenant table* |
| `database-engineering` skill §4 | "Every **tenant table** has `tenant_id …`" + "Force security: `ALTER TABLE [table] FORCE ROW LEVEL SECURITY`" | *tenant table* (behaviour contract, Holy Bible §0.3 rank n/a) |
| `security-threat-model` skill §2 | "**Always** enforce `ALTER TABLE … FORCE ROW LEVEL SECURITY` in PostgreSQL" | *unconditional* (behaviour contract, not a product decision) |
| ADR-006 directive 3 | "Preserve RLS/FORCE RLS, application-layer AES-256-GCM, isolated blind-index pepper and append-only evidence invariants" | invariant preservation |
| `REMEDIATED` §4.1 (rank 2) | `STATUTORY_RULE_SET_VERSIONS` is declared **without** `tenant_id FK`, while `CANDIDATES`, `CANDIDATE_CONSENT_RECORDS` and `DOCUMENTS` each declare `uuid tenant_id FK`; the ERD relates `STATUTORY_RULE_SET_VERSIONS` only to `HOKM_SIMULATIONS` (not to `ORGANIZATIONS`) | per-entity |
| Holy Bible §5.2 (ERD) | statutory entities relate to simulations, signatures, changes and artefacts; **no** `ORGANIZATIONS` edge | per-entity |
| Holy Bible §5.9 | `statutory_rule_set_versions` — *Indefinite*, Legal, "Retain, never mutate" (**only** that table is named) | retention class |
| Holy Bible §5.1 | the four tables are "**Missing**" from `REMEDIATED` §4.1, "Added (`P0-T04`)" citing `SPEC-STAT-001` §§2, 4, 5, 10 — **no tenancy attribute is assigned** | silence |
| `SPEC-STAT-001` §§2.2, 4.2, 5.2, 5.5, 10 (rank 4) | no `tenant_id` in any schema block; §10 is headed "**Verification Log Template**" | silence |
| `FIND-ARCH-04` (rank 3) | establishes the *mechanism* (`SET LOCAL app.current_tenant_id`, `FORCE ROW LEVEL SECURITY`, owner/superuser bypass) — says nothing that excludes non-tenant tables | mechanism |

**Why the omission is not a decision.** `SPEC-STAT-001` is `Draft — awaiting Legal Counsel and Certified Tax Accountant sign-off` (its own header) and is a rank-4 document; Holy Bible §0.3 rule 2 forbids narrowing a rank-2 line on the strength of a subordinate document. Holy Bible §5.3/§5.4 do not agree on scope ("every tenant table" vs "every table"), and the cited source for the §5.4 `ACCEPTED` row (ADR-003) concerns encryption and blind indexing only — ADR-003 mentions `tenant_id` solely inside the index it prescribes. `FIND-ARCH-04` does not decide table scope either. ADR-006 preserves RLS/FORCE RLS invariants but decides nothing about the statutory tables. **The scope question is therefore a genuine source conflict and is reserved to the owner.**

**Viable alternatives (none is selected here).**

- **T-1 — Platform-global, no `tenant_id`, RLS explicitly out of scope** (revision 1's proposal). *Consequences:* consistent with `REMEDIATED` §4.1 and Holy Bible §5.2 for `statutory_rule_set_versions`; a single legal baseline serves all tenants without duplication; contradicts the literal "every table" wording of §5.4 and the unconditional `security-threat-model` wording unless an explicit owner statement places platform-global tables outside the tenant-table class; requires the "approved DB access policy for global actor-linked evidence" that DEC-012 part 1 expressly demands — a global table with actor columns and no RLS has no database-enforced read restriction.
- **T-2 — Platform-global *with* RLS enabled, no `tenant_id`** (global tables carry `ENABLE ROW LEVEL SECURITY` + `FORCE ROW LEVEL SECURITY` and a restrictive/platform-scoped policy, e.g. a policy that admits only a platform-authorized context). *Consequences:* satisfies `security-threat-model`'s unconditional FORCE RLS and ADR-006 directive 3 without inventing a tenant column and without duplicating rule sets; requires a platform context value distinct from `app.current_tenant_id` (Holy Bible §5.4 row 2, `SPEC-AUTH-001` §6.1), an extension to the `P0-T09` tenant-context helper, and a named owner for the platform-access policy — new work not currently assigned to any WBS row.
- **T-3 — Tenant-owned**: every statutory table carries `tenant_id UUID NOT NULL REFERENCES organizations(id)`, its policy and `FORCE RLS` in the same migration (Holy Bible §5.8; `DEPLOYMENT.md` §4.2). *Consequences:* the rule set, its signatures and its artefacts are duplicated per tenant, which contradicts the `REMEDIATED` §4.1 / Holy Bible §5.2 relationship in which tenant simulations reference one platform statutory version, and it multiplies the four-eyes evidence (`SPEC-STAT-001` §4.1) across tenants; it also creates an ordering conflict inside `P0-T04` itself — the policy and FK target `organizations(id)`, which is created by `P0-T05`, and `P0-T05` *depends on* `P0-T04` (WBS §14.3) — so the same-migration rule cannot be satisfied before `P0-T05` lands; the retention row in §5.9 (indefinite legal retention) would then apply per tenant copy.

**Required owner ratification:** which of the five tables are global vs tenant-owned; the approved database access policy for global actor-linked evidence; and whether the platform-global class is explicitly excluded from Holy Bible §5.4's "every table" wording.

### 2.2 Enforcement of `users(id)` references despite `P0-T04 → P0-T05` ordering — `OPEN — BLOCKING` (DEC-012 part 2)

**Withdrawn claim (revision 1):** "FK constraints targeting `users(id)` are deferred", with "default `NO ACTION`" and AC-07 asserting "**no FK to `users`**".

**What the sources actually say — exact citations.**

| Column | Declared target | Citation | Form |
| :--- | :--- | :--- | :--- |
| `statutory_source_artefacts.archived_by` | `users(id)` | `SPEC-STAT-001` §2.2 | `UUID NOT NULL -- FK users.id` (comment) |
| `statutory_parameter_signatures.verifier_id` | `users(id)` | `SPEC-STAT-001` §4.2 | `UUID NOT NULL REFERENCES users(id)` |
| `statutory_rule_set_versions.verified_by` | `users(id)` | `SPEC-STAT-001` §5.2 | `UUID REFERENCES users(id)` (nullable) |
| `statutory_rule_changes.requested_by`, `.approved_by` | `users(id)` | `SPEC-STAT-001` §5.5 | `UUID NOT NULL REFERENCES users(id)` |
| `statutory_verification_log.transcriber_id`, `.verifier_id` | **none declared** | `SPEC-STAT-001` §10 ("Template") | `UUID NOT NULL` |

- Ordering: WBS §14.3 row `P0-T05` lists `P0-T04` as its dependency, i.e. `P0-T04` runs first and `users` does not yet exist. PostgreSQL cannot create a foreign key to a non-existent table — `NOT VALID` included — so "create the FK now" is **not available**; this is a technical constraint, not a decision about enforcement.
- `SPEC-AUTH-001` §2: `users` carries **no** `tenant_id`; a user's tenancy is via `organization_memberships`, and `sessions.organization_id` is nullable "for platform-level sessions". `users(id)` is therefore a *platform-level* principal, and the tenant-scoped FK pattern `UNIQUE (tenant_id, id)` (Holy Bible §5.3 row 3; `SPEC-AUTH-001` §6.2) cannot apply to a table that has no `tenant_id` — the two questions in §2.1 and §2.2 interact.
- ADR-006 (DEC-005 accepted) fixes `actor_id → users(id)` for the **audit ledger** only; it does not decide the statutory actor columns. ADR-006 directive 3 requires that accepted invariants be preserved, and does not ratify any statutory-table variant.
- Accepted precedent for an actor column that must outlive the account: the denormalised `actor_display_name` snapshot with `actor_type` (`SPEC-AUTH-001` §2.1; Holy Bible §5.7).

**Viable alternatives (none is selected here).**

- **F-1 — Defer the user FKs to a follow-up migration owned by a named task after `P0-T05`.** *Consequences:* during the interim the actor columns are unconstrained UUIDs — no referential integrity and no orphan detection; the follow-up task, its migration ownership and the `ON DELETE` semantics (`NO ACTION` / `SET NULL` / `RESTRICT` — and `SET NULL` is incompatible with the `NOT NULL` actor columns of §2.2/§4.2/§5.5) must be named by the owner; the interim window must be documented in the legal file.
- **F-2 — Create the identity tables inside `P0-T04`.** *Consequences:* duplicates the `P0-T05` deliverable and contradicts the approved dependency graph; a placeholder `users` risks an unreviewed schema variant diverging from `SPEC-AUTH-001` §2. Revision 1 rejected this; it remains listed because it is the only way to have enforced FKs at `P0-T04` time.
- **F-3 — No FK; retain the actor UUID plus evidence-preserving snapshots** (`actor_display_name`, actor role, and the artefact hash already required by `SPEC-STAT-001` §4.1/§10). *Consequences:* evidence survives account deletion, mirroring the accepted `actor_display_name` pattern; loses referential integrity and orphan detection and therefore requires a periodic orphan-actor audit, which is unassigned; diverges from the literal `REFERENCES users(id)` text of a **draft** specification.
- **F-4 — Mixed enforcement:** enforced FK (after `P0-T05`) for the columns whose source writes an explicit `REFERENCES` clause (§4.2, §5.2, §5.5), and snapshot columns without FK for the comment-style column (§2.2) and the template table (§10). *Consequences:* split semantics across five tables and two evidence models; requires per-column ratification and per-column tests; keeps the §10 template free of a dependency on the identity schema.

**Required owner ratification:** the enforcement model; the owning task and migration for any deferred constraint; the `ON DELETE` semantics; and whether the actor evidence must survive account deletion.

### 2.3 Signature semantics — proposed, and not blocked by DEC-012

`SPEC-STAT-001` §4.1 specifies the semantics; nothing is proposed beyond it:

- A signature is a **recorded SHA-256 digest**: `sha256(parameter_canonical_json ‖ verifier_id ‖ timestamp ‖ artefact_sha256)`, stored as `signature_sha256 CHAR(64)`. It is not a PKI signature and **no keys are stored**.
- Verification state is row arithmetic: a parameter is `VERIFIED` only with ≥2 signatures and ≥1 role `CERTIFIED_ACCOUNTANT`/`LABOR_COUNSEL`. The database stores rows; the state rule belongs to the loader (`P1-T01`).
- Rows are **append-only** (`SPEC-STAT-001` §4.1: "Signature rows are append-only") — the one statutory table for which the source makes append-only explicit, so a `BEFORE UPDATE OR DELETE` trigger that raises is proposed here. (The generic append-only ledger pattern remains `P0-T10`'s contract; `AGENTS.md` §2 invariant 14 governs the ledger.)
- Uniqueness `UNIQUE (rule_set_version_id, parameter_key, verifier_role)` per §4.2.

**Corrected attribution — no `pgcrypto`.** The deciding authority is **ADR-003** (rank 1), which rejected in-database `pgcrypto` because plaintext keys enter the SQL layer, statement logs and replication streams (its Decision Outcome and rejected-technology register entry in Holy Bible §13.2 is a *listing* of that ADR, not the decision); the behaviour contract is the `security-threat-model` skill ("Never use in-database `pgcrypto` for sensitive PII"); `AGENTS.md` §2 invariant 13 states "no `pgcrypto`". Revision 1 attributed this to the Holy Bible §13.2 register alone — corrected.

**Value-list decision rule (proposed):** `CHECK` constraints are implemented **only where the source writes `CHECK` explicitly** (`status`, `retrieval_level`). Allowed values stated only in comments (`verifier_role`, `outcome`, `source_code` families) are documented, not constrained — adding a `CHECK` later is backward-compatible, guessing one now is not (Holy Bible §0.3 rule 2, "no silent narrowing"; `SPEC-STAT-001` §3.5 open items O1–O5).

---

## 3. Table inventory and authority mapping

| Table | Spec authority | In WBS `P0-T04` row? | Proposed inclusion |
| :--- | :--- | :--: | :-- |
| `statutory_rule_set_versions` | `SPEC-STAT-001` §5.2 | Yes (Del) | Yes — the only table with a rank-2 declaration (`REMEDIATED` §4.1) |
| `statutory_source_artefacts` | §2.2 | Yes (Del) | Yes |
| `statutory_parameter_signatures` | §4.2 | Yes (Del) | Yes |
| `statutory_rule_changes` | §5.5 | Yes (Del) | Yes |
| `statutory_verification_log` | §10 | **Omitted from the Del list**, but `EXECUTION_PLAN.md` §4 mapping and Holy Bible §5.1 both assign it to `P0-T04` ("Added (`P0-T04`)", citing §§2, 4, 5, 10) | Yes — see Q-2 (§7) |

The two higher-order mappings agree on the fifth table; the WBS deliverable string is read as an abbreviation, not an exclusion. Inclusion is additive and fully specified in §10; it is flagged for confirmation (Q-2), not silently assumed to be final scope. **Table *set* scope is not itself blocked by DEC-012**, which concerns ownership and identity-FK semantics, not the list of tables.

---

## 4. Measurable acceptance criteria (each maps to a test)

Rows marked **GATED** are not testable until DEC-012 is `RESOLVED`; they must not be implemented, and the *absence* of a column or constraint must not be asserted as an acceptance criterion.

| ID | Criterion | Test | State |
| :-- | :--- | :--- | :-- |
| AC-01 | `upgrade head` succeeds on an isolated test database (`pish_p0t04_migtest_<hex>` on the existing `pish-hesabdari-dev` server); `pish_dev` and all volumes are untouched | roundtrip test | Proposed |
| AC-02 | `downgrade base` after `upgrade head` removes every statutory table, the append-only trigger and its function; the cycle succeeds a second time | roundtrip test | Proposed |
| AC-03 | All five tables exist after `upgrade head` with the column contract of `SPEC-STAT-001` §§2.2, 4.2, 5.2, 5.5, 10 (names, types, nullability, defaults), as ratified | schema + model-consistency tests | Proposed |
| AC-04 | Migration lint passes over the migrated schema and **rejects**: `CHAR`/`VARCHAR` without explicit length; `FLOAT`/`REAL`/`DOUBLE PRECISION`; `TIMESTAMP WITHOUT TIME ZONE` | lint tests (positive + negative probe) | Proposed |
| AC-05 | Hash columns are `CHAR(64)`; parameter values are `NUMERIC(24,4)`; JSON columns are `JSONB`; all timestamps are `TIMESTAMPTZ` | schema tests | Proposed |
| AC-06 | **Withdrawn (revision 1: "No statutory table carries `tenant_id`, `relrowsecurity = false` for all five").** Replaced by GATED-AC-06a/b below — the *absence* of `tenant_id`/RLS is **not** an acceptance criterion | — | **Withdrawn** |
| AC-07 | Declared constraints exist: `UNIQUE (rule_year_shamsi, revision)`; `UNIQUE (rule_set_version_id, parameter_key, verifier_role)`; `CHECK` on `status` and `retrieval_level`; FKs `signatures→versions`, `signatures→artefacts`, `changes→versions`, `versions→versions (supersedes)`. **The revision-1 clause "no FK to `users`" is withdrawn** | constraint tests | Proposed (amended) |
| AC-08 | `status` CHECK rejects an out-of-list value; `retrieval_level` CHECK rejects an out-of-list value | CHECK behaviour tests | Proposed |
| AC-09 | `statutory_parameter_signatures` rejects `UPDATE` and `DELETE` at the database layer and allows `INSERT` | append-only trigger test | Proposed |
| AC-10 | No `pgcrypto` extension is created by the migration; no key material column exists on any statutory table (authority: ADR-003 + `security-threat-model` skill; see §2.3) | extension test | Proposed |
| AC-11 | The migration contains **no seed rows** and touches neither `backend/data/seeds/*` nor any statutory value; test data is synthetic only (year 9999, value 1.0000, status `DRAFT`, `is_active = false`) — nothing is activated | source inspection + test design | Proposed |
| AC-12 | Reflected schema columns match the declarative models in `backend/app/models/statutory.py` exactly (name, type, nullability) | model-consistency test | Proposed |
| AC-13 | No credential, DSN or secret is printed by the tests, `alembic.ini` or `env.py`; `alembic.ini` stores no URL | source inspection | Proposed |
| GATED-AC-06a | **Tenancy model:** each statutory table's ownership class and its `tenant_id`/RLS/`FORCE ROW LEVEL SECURITY` treatment exactly as ratified under DEC-012 part 1 (T-1, T-2 or T-3) | introspection test + isolation test | **GATED — DEC-012** |
| GATED-AC-06b | **Global-access policy:** the ratified database access policy for global actor-linked evidence is implemented and tested (deny by default; platform-authorized context only) where the ratified model requires it | RLS/policy penetration test | **GATED — DEC-012** |
| GATED-AC-07a | **Identity-FK model:** actor columns are enforced exactly as ratified under DEC-012 part 2 (F-1…F-4), including the named owning migration for any deferred constraint and the ratified `ON DELETE` semantics | constraint tests + orphan audit | **GATED — DEC-012** |
| GATED-AC-07b | **Attribution completeness:** every actor column carries the ratified evidence fields (FK, snapshot, or both) so a deleted account cannot render the statutory evidence unintelligible | schema test | **GATED — DEC-012** |

---

## 5. Environment and connection contract

- Runtime: the existing `backend/.venv` interpreter and tools only (`rtk proxy`); no global Python, no dependency change, no `uv` lockfile edit.
- **Isolated runtime:** the P0-T03 hardened `pg_hba.conf` admits TCP **only** to `pish_dev`, so an isolated database on the development server is unreachable by design. The migration suite therefore runs against one **ephemeral, loopback-only PostgreSQL container** started from the official `postgres:16.16-bookworm` image already present locally (no pull, no external network), with trust auth bound to `127.0.0.1` and a generated throwaway database (`pish_p0t04_migtest_<hex>`). It is force-removed at teardown. `pish_dev`, its volume and all existing containers are untouched; the only thing ever dropped is the container the suite itself started.
- **No secret material exists in the harness:** the ephemeral server uses trust auth, so no password is generated, read, stored or printed, and the `DATABASE_URL` built by the suite carries no password. The production secret-reading pattern remains exactly as in `infra/postgres/verify_local.py`, which this packet does not exercise or alter.
- `DATABASE_URL` (the `DEPLOYMENT.md` §5.1 variable, `SecretStr` in `app.core.config`) is the only URL source for `alembic/env.py`; an absent URL fails closed. The URL is never rendered. `alembic.ini` deliberately holds no `sqlalchemy.url`.
- If Docker or the local image is unavailable, tests `pytest.skip` with an explicit `NOT RUN` reason — never a false pass.

---

## 6. Explicit non-goals and boundaries

1. No production migration, deployment or CI migration job (CI itself is unselected — DEC-F open, `P0-T01` incomplete).
2. No seed loading, no rule-set activation, no loader (`P1-T01`), no 1405 transcription anywhere (1405 stays inactive per `SPEC-STAT-001` §7; only 1404 is the verified baseline and it is **not** inserted here).
3. No identity/tenant tables, no audit ledger, no key stores, no storage adapter — other owners.
4. No index beyond constraints named in the specs (GIN on `source_manifest`/`parameter_snapshot` waits for a defined query path — Holy Bible §5.3 "where queried").
5. `pish_dev` runtime state is read through nothing but the isolated test database; the dev database's own schema is never migrated by this packet.
6. **No migration implementation, and no assumption of the §2.1/§2.2 options, until DEC-012 is `RESOLVED` and this contract is re-issued (revision 3).**

---

## 7. Open decisions

| # | Question | Status | Owner / approver | Effect |
| :-- | :--- | :--- | :-- | :-- |
| **DEC-012(1)** | Which statutory/provenance/signature/change tables are global versus tenant-owned; the approved database access policy for global actor-linked evidence; whether platform-global tables are excluded from Holy Bible §5.4's "every table" wording (§2.1, alternatives T-1/T-2/T-3) | **OPEN — BLOCKING** | Project Owner; CTO/DBA + Security Architect | Blocks all migration implementation; blocks GATED-AC-06a/b |
| **DEC-012(2)** | How `users(id)` references are enforced despite `P0-T04` preceding `P0-T05` — enforcement model, owning task/migration, `ON DELETE` semantics, and attribution evidence that survives account deletion (§2.2, alternatives F-1/F-2/F-3/F-4) | **OPEN — BLOCKING** | Project Owner; CTO/DBA + Security Architect | Blocks all migration implementation; blocks GATED-AC-07a/b |
| Q-2 | Confirm `statutory_verification_log` belongs to `P0-T04` (Holy Bible §5.1 + `EXECUTION_PLAN.md` §4) although the WBS deliverable string omits it | OPEN — NON-BLOCKING | Coordinator + Database Eng | §10 schema is complete; inclusion is additive and removable by a trivial downgrade |
| Q-3 | Should `verifier_role` / `outcome` value lists become `CHECK`s once rosters stabilise (§2.3 rule)? | OPEN — NON-BLOCKING | Database Eng + Legal | Current rows unconstrained by design |
| Q-4 | Who owns the follow-up migration, and with which `ON DELETE` semantics, if the ratified model defers identity FKs (F-1)? | OPEN — BLOCKING (subsumed by DEC-012(2)) | Coordinator (after ratification) | Part of DEC-012(2); not tracked separately |

No ADR is approved, superseded or amended by this document. DEC-012 does not reopen ADR-006's four accepted choices.

---

## 8. Verification matrix — observed state (2026-11-15)

| Check | Result |
| :--- | :--- |
| Existence of the baseline migration (`backend/alembic/env.py`, `backend/alembic/versions/`) | **NOT RUN — source does not exist.** `backend/alembic/` holds only `script.py.mako` |
| Existence of the integration migration suite (`backend/tests/integration/test_statutory_migrations.py`) | **NOT RUN — file does not exist**; `backend/tests/integration/` holds only an empty `__init__.py` |
| `backend/alembic.ini` credential/URL hygiene | **PASS (source inspection)** — `sqlalchemy.url` empty, no DSN or secret present |
| `backend/app/models/statutory.py` consistency with the ratified schema | **NOT RUN / NOT APPLICABLE** — the file predates ratification and encodes the withdrawn §2.1/§2.2 assumptions |
| Ruff lint/format on owned files | **NOT RUN** — no code was written or changed in this revision (documentation-only corrective edit) |
| `mypy --strict` on owned files | **NOT RUN** — same reason |
| Integration migration suite on isolated DB | **NOT RUN** — implementation is blocked by DEC-012 |
| CI migration job (Stage 12) | **NOT RUN** — no CI provider selected (DEC-F open) |
| Independent review of the revision-1 contract | **RECORDED** — an independent read-only review of the revision-1 draft was performed and its outcome is recorded by the coordinator in `docs/BOOTSTRAP_CHANGELOG.md` §17.4; this revision is the resulting contract-only corrective edit |

No test was executed against a database in this revision; no result is claimed. The changelog entry required by `AGENTS.md` §3 for this factual correction is recorded by the coordinator in `docs/BOOTSTRAP_CHANGELOG.md` (shared control document; not edited by the contract owner).

---

## 9. Revision history of this contract

| Revision | Date | Status | Change |
| :-- | :-- | :-- | :-- |
| 1 | 2026-11-15 | Superseded (draft) | Initial `P0-T04` design contract. Asserted global/no-RLS ownership and deferred user FKs as derived decisions; mis-attributed the `pgcrypto` rule to the Holy Bible rejected-technology register; cited `DEPLOYMENT.md` §12.1 for the Alembic configuration. |
| 2 | 2026-11-15 | **PROPOSED — BLOCKED** | Corrective revision (this document): withdrawals in §0; §2.1/§2.2 recast as unratified proposals with alternatives, consequences and exact citations; AC-06 and the AC-07 user-FK clause withdrawn and replaced by GATED-AC-06a/b and GATED-AC-07a/b; `pgcrypto` attribution corrected to ADR-003 + `security-threat-model`; `DEPLOYMENT.md` citation corrected to §4.2; §7 and §8 restated against the observed state; DEC-012 cross-referenced. No ADR approved or superseded; no code or shared control document edited. |
| 3 | *pending* | *pending* | To be issued after DEC-012 is `RESOLVED` by a named approver, carrying the ratified choices from §2.1/§2.2 into §4. |

---

*Owner: P0-T04 contract (sole editor: MiniMax, contract-only corrective edit). Coordinator records the register, queue, changelog and task status.*
