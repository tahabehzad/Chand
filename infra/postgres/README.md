# Local PostgreSQL 16 — P0-T03

Development bootstrap only. DEC-010 production topology, P0-T04 migrations,
P0-T05 identity, P0-T09 isolation and the evidentiary audit ledger are separate.
No candidate data, application tables or statutory seeds are loaded here.

From the repository root (commands respect the project's RTK wrapper):

```powershell
rtk proxy .\backend\.venv\Scripts\python.exe -B infra/postgres/local_material.py
rtk proxy docker compose -f infra/compose/compose.dev.yml config --quiet
rtk proxy docker compose -f infra/compose/compose.dev.yml up -d --build --wait db
rtk proxy .\backend\.venv\Scripts\python.exe -B infra/postgres/verify_local.py
```

Prepare uses the existing Python/cryptography installation. It creates or
validates `.secrets/postgres/`; all private values stay off stdout/argv and
out of the build context. On Windows its ACL allows only the current user
and SYSTEM. Root CA private key is not mounted. Certificates are for local
development: 30-day server/90-day CA. Expired, incomplete or mismatched files
fail closed; there is no silent key/password rotation or overwrite.

The compose project is `pish-hesabdari-dev`; only `127.0.0.1:55432` is
published. TCP requires CA-verified TLS 1.3/SCRAM. Local peer authentication
is reserved for the container's postgres administrator. Applications must
not use that bootstrap identity. The data volume is persistent and is never
deleted by these commands. Do not use `down -v` as a repair step.

The image extends the publisher's `postgres:16.16-bookworm` with the signed
PGDG pgaudit package. A successful build must record its real digest/package
versions before any release pin is claimed. Registry/network failure is not
permission to use an unverified mirror, insecure registry or a different
database. The first failed pull in this environment returned HTTP 403.

Runtime verification checks settings, live TLS, authentication rejections,
extension/privilege policy and synthetic marker confidentiality in actual
server logs. SQL log text/parameter restrictions do not authorize putting
PII/secrets into SQL literals or invalid-value error messages. Parameterize
queries and keep all candidate PII encrypted in the application. pgAudit is
operational metadata, not the append-only hash-chained evidence ledger.

`init.sql` applies only to an **empty** data volume. Existing data is never
reset automatically; initialization failure requires inspection before
retrying. A configuration parse or certificate unit test cannot certify a
database that has not actually booted.

Source contracts: [PostgreSQL 16 TLS](https://www.postgresql.org/docs/16/ssl-tcp.html),
[HBA first-match rules](https://www.postgresql.org/docs/16/auth-pg-hba-conf.html),
[official image setup/secrets](https://github.com/docker-library/docs/blob/master/postgres/README.md),
[pgAudit PostgreSQL-16 branch](https://github.com/pgaudit/pgaudit/blob/REL_16_STABLE/README.md).
Current outcomes and limitations: `docs/BOOTSTRAP_CHANGELOG.md` §15 (official
pull/build and real hardening verifier PASS on 2026-11-15); §12 retains the
historical HTTP 403. The development DB runs at `127.0.0.1:55432`; P0-T01 CI
remains pending. This is not a production or tenant-isolation acceptance.
