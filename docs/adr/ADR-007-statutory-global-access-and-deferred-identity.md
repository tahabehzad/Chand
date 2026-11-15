# ADR-007: Global statutory access and deferred identity references

- **Status:** Accepted
- **Date:** 2026-11-15
- **Decider:** Project Owner, explicit chat approval: “تأیید است، T-2 و F-1 با همون شرایطی که گفتی.”
- **Resolves:** DEC-012; clarifies statutory table scope only. ADR-001…006 remain unchanged.

## Decision

All five statutory provenance tables are platform-global, without tenant_id,
with ENABLE and FORCE ROW LEVEL SECURITY (T-2). Tenant data remains isolated
under its own mandatory tenant policies. Global does not mean public evidence.

The database reader role may read only ACTIVE/is_active rule parameters via a
column-limited projection; no actor identities or source manifests. A separate
platform review role may read provenance. Neither role is granted to PUBLIC;
neither may create roles, bypass RLS, or inherit the migration owner. SQL roles,
not caller-controlled tenant IDs or custom settings, authorize platform access.

Actor UUID columns keep their specified nullability. Their users(id) foreign
keys are deferred to the identity migration owned by P0-T05 (F-1), for every
statutory actor column including archival and verification-log actors. Use
ON DELETE RESTRICT; deactivate referenced accounts instead of deleting them.
P0-T05 must validate existing references and install every FK before removing
the database write gate. P0-T04 permits no application writes to any of the five
tables, including drafts: real evidence cannot enter the unenforced interval.
There is no runtime setting or application escape hatch for this gate.

## Implementation and acceptance

Provision two NOLOGIN database roles separately using infra/postgres/statutory_roles.sql.
Migrations do not create cluster roles or grant role membership. A missing or
unsafe role fails closed. P0-T04 owns their table privileges and policies;
P0-T09 owns subsequent connection integration; no identity/session is invented.
The migration owner is a trusted deployment principal, never an API identity.

The ingestion draft's CHAR(1) cannot store L1…L4. Use VARCHAR(2) for both source
level fields, retaining the documented values; this is a storage correction,
not a statutory interpretation. No legal seed or statutory value is changed.

Accept only after real isolated PostgreSQL upgrade/downgrade/re-upgrade, schema
checks, non-superuser role and owner RLS tests, restricted projection tests,
write-gate/append-only checks, lint and strict typing. Independent review and
CI/Phase-0 sign-off remain separate from this owner decision.
