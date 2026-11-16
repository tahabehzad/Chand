# Statutory provenance database contract — P0-T04

- **Document ID:** SPEC-STATDB-001
- **Revision:** 3, 2026-11-15
- **Status:** Accepted owner choices; implementation/verification tracked separately
- **Owner:** Codex /root
- **Authority:** [ADR-007](../adr/ADR-007-statutory-global-access-and-deferred-identity.md),
  [ingestion spec](STATUTORY_INGESTION.md) §§2.2, 4.2, 5.2, 5.5, 10;
  [AUTH](AUTH.md) §2; [WBS](../EXECUTION_PLAN.md) §14.3.
- **History:** [Revision 2](history/STATUTORY_DATABASE_CONTRACT.rev2.md), retained verbatim.

## Ratified boundaries

DEC-012 is resolved by the owner's explicit T-2/F-1 approval in chat. All five
tables are global with ENABLE/FORCE RLS in their creation migration. Default
access is denied. pish_statutory_reader receives only SELECT on the explicitly
safe rule columns and a security-invoker, security-barrier projection filtered
to status ACTIVE AND is_active. It cannot read verified_by or source_manifest.
pish_statutory_reviewer can SELECT all statutory evidence, never write it.
Policies compare current_user to these isolated database roles; custom GUCs
cannot grant access. No role membership is provisioned by the migration.

Provision NOLOGIN/non-superuser/non-BYPASSRLS roles using
infra/postgres/statutory_roles.sql, under a trusted administrator. Applying that
script to existing roles validates privileges and never silently downgrades or
reconfigures an existing role. The baseline checks the same requirements.

P0-T05 owns the follow-up identity migration: archived_by, verifier_id,
verified_by, requested_by, approved_by, transcriber_id and verification-log
verifier_id receive users(id) FKs with ON DELETE RESTRICT. Accounts referenced
by legal evidence are deactivated rather than deleted. Until all FKs are
installed and validated, a statement-level database trigger rejects INSERT,
UPDATE, DELETE and TRUNCATE on every statutory table, even for a table owner.
Only the trusted migration owner can replace that gate in the follow-up.
No fake users, FK stubs, production evidence, seed loading or activation.

## Table and column contract

Reuse the five tables/columns in ingestion §§2.2, 4.2, 5.2, 5.5, 10.
Hashes CHAR(64), values NUMERIC(24,4), JSONB snapshots, timezone-aware timestamps,
explicit string lengths. Correct retrieval_level/transcription_level to
VARCHAR(2): the draft's CHAR(1) cannot store its own L1…L4 labels.
Keep declared uniqueness/self/source/version FKs and status/level CHECKs.
Signatures reject UPDATE, DELETE and TRUNCATE independently of the temporary
write gate. No pgcrypto or key storage. Existing statutory seed files are immutable.

## Acceptance criteria

1. Explicit Alembic upgrade head, downgrade base, re-upgrade succeeds on an
   empty isolated database; all five tables, policies, view and functions are
   created/removed transactionally. No startup migration.
2. Database catalogue matches typed models, nullability, defaults, unique/FK
   constraints, CHAR(64), NUMERIC(24,4), JSONB and TIMESTAMPTZ. Source levels L1…L4 fit.
3. No statutory table has tenant_id; all have ENABLE/FORCE RLS. A non-superuser
   owner and ordinary tenant with broad SELECT still see zero rows. Spoofed
   app settings do not open access. Reader sees only active safe parameters;
   reviewer sees evidence. Reader cannot inspect actor columns or source manifests.
4. Every role, including reviewer and table owner, is denied INSERT/UPDATE/
   DELETE/TRUNCATE until P0-T05. Signatures remain append-only independently.
5. Schema/source lint rejects lengthless strings, floating point and naive
   timestamps. No credentials/DSN in diagnostics, config, SQL output or tests.
6. Tests use only synthetic fixtures in an explicitly generated throwaway
   container. They never migrate pish_dev or touch existing containers/volumes.
7. Unit/API regression, strict types, lint, frontend typecheck/build/startup
   pass. CI/provider remains DEC-F; no phase or certified financial claim.

## Test environment

Reuse the locally available official postgres:16.16-bookworm image, no pull.
Loopback-only disposable test server; no secrets or real candidate data.
Create cluster roles only there, before the migration. Missing Docker/image
is NOT RUN, never successful database acceptance. Restore DATABASE_URL after
tests. Downgrade applies only to the harness-owned empty/synthetic database;
production destructive rollback requires the normal explicit release procedure.
