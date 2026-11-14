# Specification: Deployment, Infrastructure & Operations

- **Document ID:** `SPEC-OPS-001`
- **Status:** Draft — proposed topology and procedures
- **Author:** Documentation Engineering (Infrastructure workstream)
- **Date:** 2026-11-14 (23 Aban 1405 SH)
- **Related:** [`docs/EXECUTION_PLAN.md`](../EXECUTION_PLAN.md) §12, §13 · [`docs/adr/ADR-001-frontend-architecture-react-vite-spa.md`](../adr/ADR-001-frontend-architecture-react-vite-spa.md) · [`docs/adr/ADR-002-object-storage-worm-ceph-s3-governance.md`](../adr/ADR-002-object-storage-worm-ceph-s3-governance.md) · [`docs/adr/ADR-003-sensitive-data-encryption-alee-blind-indexing.md`](../adr/ADR-003-sensitive-data-encryption-alee-blind-indexing.md) · [`docs/adr/ADR-005-async-execution-strategy.md`](../adr/ADR-005-async-execution-strategy.md)

> **Assumption.** The platform runs on a **customer-controlled on-premise host**, which may be air-gapped. **No cloud-managed service may be assumed.** This is ADR-001's stated driver 2 and it drives every choice below.

---

## 1. Topology

### 1.1 Pilot / production topology

```
                       ┌──────────────────────────────┐
   Internet (optional) │  Traefik or Nginx            │
   ───────────────────►│  TLS 1.3 termination        │
                       │  static SPA + /api reverse  │
                       │  rate limiting, security hdr │
                       └───────────────┬──────────────┘
                                       │  http://app:8000
                       ┌───────────────▼──────────────┐
                       │  FastAPI application         │
                       │  (uvicorn, N replicas)       │
                       │  · JWT/session middleware    │
                       │  · ALEE encryption           │
                       │  · statutory engine (sync)   │
                       └──────┬───────────────┬───────┘
                              │               │
              ┌───────────────▼──┐      ┌─────▼──────────────┐
              │ PostgreSQL 16    │      │ Job worker pool   │
              │ · FORCE RLS      │◄─────┤ (separate process)│
              │ · append-only    │      │ OCR / forensics    │
              │   audit ledger   │      └────────────────────┘
              └──────────────────┘
                              │
              ┌───────────────▼──────────────────┐
              │ Ceph Object Gateway (RADOS GW)   │
              │ S3 API, Object Lock GOVERNANCE    │
              │ 3650-day retention                │
              └───────────────────────────────────┘

   Optional (air-gapped sites): HashiCorp Vault
   Alternative (no Vault):        local encrypted master config + Argon2id KEK
```

### 1.2 Mandatory components

| Component | Why mandatory | Alternatives |
| :--- | :--- | :--- |
| PostgreSQL 16 | System of record; RLS; hash-chained ledger; job queue (ADR-005, proposed) | **None** |
| Object storage, S3-compatible | Immutable forensic dossiers (ADR-002) | Ceph RADOS GW (Apache-2.0) or a domestic managed S3 (ArvanCloud, Cloudware, MobinNet) |
| Application runtime | FastAPI | — |
| Reverse proxy | TLS termination, static SPA serving, rate limiting | Traefik 3 or Nginx 1.25 |

**Optional:** HashiCorp Vault (ADR-003 names it). Where it is unavailable — common in air-gapped sites with a small ops team — the fallback is a **local encrypted master configuration file** from which the master KEK is derived via Argon2id. This fallback must be reviewed and accepted by the Security Architect (`SPEC-AUTH-001` §8).

### 1.3 Explicitly excluded

| Excluded | Reason |
| :--- | :--- |
| Redis / Celery as a mandatory broker | ADR-005 (proposed) — rejected on operational-footprint grounds |
| A managed cloud queue, object store or KMS | Air-gapped constraint |
| Kubernetes | Overkill for the target estate; a compose stack is operable by a 2-person team |
| A Node.js runtime in production | ADR-001 |

---

## 2. Local Development Environment (Windows)

### 2.1 Prerequisites

| Tool | Version | Notes |
| :--- | :--- | :--- |
| **Python** | 3.12 (3.13 permitted) | Install via `winget install Python.Python.3.12` or pyenv-win |
| **uv** | latest | Fast, cross-platform dependency + venv manager; the Windows-native choice |
| **Node.js** | 20 LTS | Build-time only — no production runtime (ADR-001) |
| **pnpm** | latest | — |
| **Docker Desktop** | latest | **WSL 2 backend required**; the Linux containers are the production artefacts |
| **Git** | latest | — |
| **psql** | 16 | Optional — `docker compose exec db psql` is sufficient |

### 2.2 Repository layout (target)

```
backend/
  pyproject.toml          # PEP 621; uv-managed
  uv.lock                 # committed
  alembic.ini
  alembic/versions/
  app/
    main.py
    core/       config, security, crypto, db, tenancy, audit
    engines/    statutory, tax, sso, severance, eydi, overtime, ctc, inverter
    models/     SQLAlchemy 2.0 models
    schemas/    Pydantic v2
    services/   domain services
    api/v1/     routers
  tests/
    unit/ integration/ golden/ property/ isolation/ crypto/ api/
    golden/1404/  golden/1405/
  data/seeds/
    statutory_rules_1404.yaml   # verified — do not modify
    statutory_rules_1405.yaml   # placeholder — do not activate
frontend/
  package.json
  pnpm-lock.yaml
  vite.config.ts
  src/
    app/       router, providers
    components/ui/
    features/  simulation/ documents/ auth/ reports/
    lib/       numerals.ts  jalali.ts  currency.ts  api/
    styles/    tokens.css  fonts/
  e2e/         Playwright
infra/
  docker/      Dockerfile.backend  Dockerfile.frontend  Dockerfile.worker
  compose/     compose.dev.yml  compose.staging.yml  compose.prod.yml
  nginx/       nginx.conf  conf.d/app.conf
  postgres/    init/  (extensions, RLS helper functions)
docs/          (this documentation package)
```

> This layout is a **target** described for planning purposes. It is not created by this workstream — no application source code was written.

### 2.3 Backend setup (Windows)

```powershell
# from the repository root
cd backend
uv python install 3.12
uv venv --python 3.12
.\.venv\Scripts\Activate.ps1

uv sync --frozen --all-groups          # install from uv.lock
uv run alembic upgrade head             # apply migrations
uv run pytest -q                       # fast unit suite
uv run uvicorn app.main:app --reload --port 8000
```

### 2.4 Frontend setup (Windows)

```powershell
cd frontend
pnpm install --frozen-lockfile
pnpm dev                               # Vite dev server, proxying /api to :8000
pnpm test                              # Vitest
pnpm exec playwright install chromium
pnpm test:e2e
```

### 2.5 Local dependencies via Docker

```powershell
cd infra/compose
docker compose -f compose.dev.yml up -d db objectstore
```

`compose.dev.yml` provides PostgreSQL 16 with the required extensions and a Ceph RADOS-GW single-container dev instance with Object Lock enabled in `GOVERNANCE` mode.

**Dev-environment deviations from production** (must be explicit, never accidental):

| Dev | Production | Consequence |
| :--- | :--- | :--- |
| Object Lock `GOVERNANCE` with a short retention | `GOVERNANCE`, 3650 days | Dev deletion works; production needs the emergency path |
| Master KEK from a local file | Vault, or the local encrypted file | The local path must still be exercised in dev, or it is untested in production |
| Single app process | N replicas + separate workers | `SET LOCAL` tenant-context behaviour must be tested with connection reuse (§ISO-04) |
| Synthetic fixtures | Scrubbed production-shaped data | RLS must be re-tested with realistic data volumes |

### 2.6 Windows-specific cautions

| Issue | Mitigation |
| :--- | :--- |
| Path separators and UTF-8 filenames | All tooling forced to UTF-8; Persian filenames must be tested |
| `pgcrypto`/`argon2` native wheels | `uv` resolves Windows wheels; if a wheel is missing, the container path is the fallback |
| Long path limits | Enable `LongPathsEnabled` in the registry, or keep the repo path short |
| Antivirus and file locking | Exclude the repo and the Docker data root from real-time scanning (a common source of mysterious test failures) |
| Line endings | `.gitattributes` enforces LF for source and CRLF normalisation only for `.bat`/`.cmd` |
| Celery/Redis on Windows | **Not applicable** — ADR-005 removes the Windows-parity problem |

---

## 3. Container Images

### 3.1 Backend image

| Stage | Contents |
| :--- | :--- |
| Builder | `python:3.12-slim`, `uv`, compile wheels, install into a virtualenv at `/opt/venv` |
| Runtime | `python:3.12-slim`, non-root user, `/opt/venv` on `PATH`, application at `/app`, **no compiler, no package manager, no source** |

Requirements: pinned base image digest, no `latest` tag, `pip check` clean, `pip-audit` clean, no secrets in build args or layers.

### 3.2 Worker image

Same base as the backend, **different entrypoint**. ADR-005 (proposed) requires OCR work in a separate OS process so that CPU-bound inference cannot breach the fast-path latency budget.

### 3.3 Frontend image

`ADR-001` directive 4: multi-stage — Node 20 builder → Nginx 1.25 Alpine runner. The final image contains only the static bundle and the Nginx configuration. Target size ~25 MB.

**Nginx requirements:** `gzip` on; `brotli` on if available; long cache headers for hashed assets (`/assets/*`, 1 year, immutable) and `no-cache` for `index.html`; CSP and `X-Content-Type-Options` headers; the SPA fallback (`try_files $uri /index.html`).

### 3.4 Image policy

| Rule | Enforcement |
| :--- | :--- |
| Pin by digest | CI records the digest; the compose file pins it |
| No `latest` | CI rejects it |
| Scan every image | `trivy`; Critical/High blocks the merge |
| SBOM | CycloneDX per image, archived |
| Rebuild on base-image CVEs | Automated PR that bumps the digest and re-runs the full suite |

---

## 4. Database Provisioning and Migrations

### 4.1 PostgreSQL configuration

| Setting | Value | Reason |
| :--- | :--- | :--- |
| Version | 16 | `REMEDIATED` §3.1 |
| `wal_level` | `replica` | PITR and replicas |
| `max_wal_size` | 4 GB | Bounded recovery time |
| `effective_cache_size` | 50 % of RAM | Planner |
| `shared_buffers` | 25 % of RAM | — |
| `work_mem` | 8 MB | Per-connection limit; the app uses bounded result sets |
| `max_connections` | 200 (tuned per host) | Separate pools for API and worker |
| `statement_timeout` | 30 s | Prevents a runaway analytical query |
| `idle_in_transaction_session_timeout` | 60 s | Prevents a leaked tenant context |
| `log_min_duration_statement` | 500 ms | Slow-query visibility |
| `log_statement` | **NEVER `all`** | `FIND-ARCH-03` — plaintext key exposure via statement logs |
| `ssl` | on, client verification | Connection encryption |
| Extensions | `pgcrypto` (for non-PII hashing only), `pgaudit` | `pgcrypto` **must not** be used for PII encryption (ADR-003) |

### 4.2 Migrations

| Rule | Detail |
| :--- | :--- |
| Tool | **Alembic** (SQLAlchemy 2.0) |
| Mode | Forward-only in production; no automatic downgrade at runtime |
| Review | Every migration is reviewed; a migration that drops or alters a column holding evidence requires a written justification |
| Zero-downtime | Expand → migrate → contract, in three releases, for anything on a hot path |
| Audit ledger | **Never** altered by a migration after activation — `UPDATE`/`DELETE` on `audit_logs` are rejected by triggers, and migrations must not attempt them |
| RLS | Every new tenant table is created with `tenant_id`, its policy, and `FORCE ROW LEVEL SECURITY` **in the same migration** |
| Hash columns | `CHAR(64)` for SHA-256 hex; `BYTEA` for ciphertext. A `CHAR` without an explicit length is **forbidden** by a CI migration lint (this is the `REMEDIATED` §4.1 defect, see `EXECUTION_PLAN.md` §6) |
| Seed data | Reference data (cities, occupation taxonomy) is seeded by migration or a versioned seed command, never hand-edited in the database |
| Verification | Each migration runs against a production-shaped snapshot in CI; the migration job is a release gate (§12 of `TESTING.md`, Stage 12) |

### 4.3 Migration rollback

- DDL is applied in a transaction where PostgreSQL permits it.
- A migration that cannot be reversed must be flagged `downgrade_requires_data_restore` in its docstring, and a data-restore procedure must exist before it ships.
- Rollback rehearsal is a release gate.

---

## 5. Configuration, Environment Variables and Secrets

### 5.1 Environment matrix

| Variable | Local | Staging | Production | Class |
| :--- | :--- | :--- | :--- | :--- |
| `APP_ENV` | `local` | `staging` | `production` | public |
| `APP_DEBUG` | `true` | `false` | `false` | public |
| `DATABASE_URL` | local compose | staging PG | pilot PG | **secret** |
| `DB_SSL_MODE` | `disable` | `require` | `verify-full` | public |
| `S3_ENDPOINT_URL` | local RGW | staging RGW | Ceph / domestic S3 | public |
| `S3_BUCKET` | `pish-dev` | `pish-staging` | `pish-prod` | public |
| `S3_ACCESS_KEY_ID` / `S3_SECRET_ACCESS_KEY` | dev | staging | prod | **secret** |
| `S3_OBJECT_LOCK_MODE` | `GOVERNANCE` | `GOVERNANCE` | `GOVERNANCE` | public (fixed) |
| `S3_RETENTION_DAYS` | 1 | 365 | 3650 | public |
| `VAULT_ADDR` | `http://vault:8200` | — | — | secret |
| `VAULT_TOKEN` / `VAULT_ROLE_ID` | dev | staging | prod | **secret** |
| `BLIND_INDEX_PEPPER` | dev file | secret store | secret store | **secret** |
| `MASTER_KEK` (fallback path) | dev file | secret store | secret store | **secret** |
| `SESSION_COOKIE_SECURE` | `false` | `true` | `true` | public |
| `ALLOWED_ORIGINS` | localhost | staging host | client host | public |
| `LOG_LEVEL` | `DEBUG` | `INFO` | `INFO` | public |
| `OCR_WORKER_CONCURRENCY` | `2` | `2` | per-host | public |
| `JOB_LEASE_SECONDS` | `300` | `300` | `300` | public |

### 5.2 Secret handling

| Rule | Detail |
| --- | --- |
| Storage | A secret store on the host (systemd credentials, Docker secrets, or Vault). **Never** in the repository, the image, or the compose file |
| Injection | Environment or mounted file at runtime. Never baked into a layer |
| Rotation | `BLIND_INDEX_PEPPER` rotation requires a full re-index migration (see `SPEC-AUTH-001` §8.3) — it is not a routine rotation |
| Logging | Secrets are redacted by a `SecretRedactingFilter` installed on every logger; the redaction test (`CR-13`) is blocking |
| `.env` | `.env` files are git-ignored; only `.env.example` (keys, no values) is committed |
| Emergency key | The `s3:BypassGovernanceRetention` capability is **never** present in the runtime environment. It lives in the offline administrative vault (`ADR-002`, `SPEC-AUTH-001` §8.4) |

---

## 6. Reverse Proxy and TLS

| Concern | Configuration |
| :--- | :--- |
| TLS termination | Traefik 3 or Nginx 1.25; **TLS 1.3** preferred, TLS 1.2 permitted for legacy clients |
| Certificate | ACME via a public CA for internet-facing sites; a client-supplied internal CA for intranet/air-gapped sites |
| HSTS | `Strict-Transport-Security: max-age=31536000; includeSubDomains` |
| Redirect | HTTP → HTTPS, 301 |
| Static SPA | Served from the frontend container; `try_files` fallback to `index.html` |
| API proxy | `/api/*` → the app service; `proxy_read_timeout` ≥ 30 s for the synchronous path; **the async path never exceeds the request** |
| Rate limiting | 100 rps per IP on the auth endpoints; 20 rps on login attempts per account; 50 rps general |
| Security headers | `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`, CSP with `font-src 'self'`, `style-src 'self' 'unsafe-inline'` (Tailwind inline styles), `script-src 'self'` |
| Client body size | 50 MB (documents) |
| Compression | gzip + brotli for text and font assets |

---

## 7. Health Checks and Observability

### 7.1 Health endpoints

| Endpoint | Purpose | Checks |
| :--- | :--- | :--- |
| `GET /health/live` | Liveness | Process is running. No dependency checks — a failing dependency must not cause a restart loop |
| `GET /health/ready` | Readiness | PostgreSQL reachable; the active rule set is loadable; the object store is reachable; the worker pool has at least one live worker |
| `GET /health/degraded` | Detailed status | Per-dependency status, queue depth, oldest queued job age, active rule set id and status. **Requires an authenticated privileged role** |
| `GET /metrics` | Prometheus metrics | Scrape endpoint, restricted to the monitoring network |

### 7.2 Logging

| Rule | Detail |
| :--- | --- |
| Format | Structured JSON to stdout; the container runtime collects it |
| Levels | `DEBUG` local, `INFO` production |
| Correlation | Every request carries `X-Request-Id`; every log line, audit event and job record carries it. `correlation_id` is returned to the client |
| Redaction | `SecretRedactingFilter` on every logger; blocklist of key names and value patterns (10-digit codes, mobile numbers, Sheba, bearer tokens) |
| PII | **Never** log a National Code, a mobile number, a Sheba, a candidate name or a salary figure. Log a blind index or a hashed reference instead |
| Retention | Application logs: 30 days locally; 1 year centrally if a central collector exists; 10 years for the **audit ledger** (a different store) |
| Audit separation | The hash-chained `audit_logs` table is **not** the application log. It is evidence and has a different retention and immutability regime |

### 7.3 Metrics

| Metric | Type | Purpose |
| :--- | :--- | :--- |
| `http_requests_total{path,method,status}` | counter | Traffic |
| `http_request_duration_seconds{path}` | histogram | Latency (p50/p95/p99) |
| `simulation_duration_seconds{operation}` | histogram | The < 5 ms inversion budget |
| `simulation_total{operation,rule_year}` | counter | Volume by rule year |
| `job_queue_depth{status}` | gauge | Backlog |
| `job_oldest_queued_age_seconds` | gauge | **Stall detector** — the single most important queue metric |
| `job_failures_total{job_type,error_class}` | counter | Reliability |
| `ocr_pages_processed_total` / `ocr_page_duration_seconds` | counter/histogram | Throughput vs. the `FIND-ARCH-05` budget |
| `audit_chain_verification_failures_total` | counter | **Must always be 0** — a non-zero value is a critical incident |
| `db_pool_checked_out` / `db_pool_size` | gauge | Pool exhaustion |
| `statutory_rule_set_active{rule_year,status}` | gauge | Which rule year is live |

### 7.4 Alerting

| Alert | Condition | Severity | Response |
| :--- | :--- | :--- | :--- |
| Audit chain verification failure | any | **Critical** | Halt the write path; escalate to the Security Architect immediately |
| Plaintext PII detected in logs or the ledger | any | **Critical** | Purge the offending sink; investigate |
| Fast-path p99 > 20 ms | 5 min | High | Check DB pool, recent deploys, rule-set size |
| Inversion p99 > 5 ms | 5 min | High | Same |
| `job_oldest_queued_age_seconds` > 600 | 10 min | High | Worker pool down or a stuck lease — check `P2-T04` reaping |
| Job failure rate > 5 % over 15 min | 15 min | Medium | Inspect `last_error` distribution |
| Dead-letter count > 0 | immediate | Medium | Triage each dead job |
| PostgreSQL disk > 80 % | 10 min | Medium | Prune / extend |
| Backup failure | any | **High** | Restore drill; escalate |
| Certificate expiry < 14 days | daily | Medium | Renew |
| Rule set status changes | any | Info | Confirm the change was authorised (four-eyes) |

---

## 8. Backup and Restore

### 8.1 Backup matrix

| Component | Method | Frequency | Retention | Notes |
| :--- | :--- | :--- | :--: | :--- |
| PostgreSQL | `pg_basebackup` + WAL archiving (PITR) | Continuous WAL; nightly full | 10 years (tax/labour audit) | Encrypted at rest; off-site copy if the site has a second location |
| Object storage | Ceph snapshots + replication | Daily snapshot | 10 years | `GOVERNANCE` mode prevents deletion — this is intentional (ADR-002) |
| Vault | Raft snapshot (if used) | Daily | 30 days + off-site | The KEK loss is unrecoverable for the affected data |
| Configuration | Git + an encrypted config export | On change | Indefinite | — |
| Audit ledger | Covered by the PostgreSQL backup; **additionally** exported to immutable storage on a nightly cadence | Daily | 10 years | The ledger is the evidentiary record; a separate copy is defence in depth |
| Master config (fallback path) | Encrypted file, off-site | On change | Indefinite | Loss is catastrophic — treat as a tier-1 secret |

### 8.2 Restore drill

A restore drill is performed **quarterly** and must:

1. Restore the PostgreSQL backup to an isolated instance.
2. Verify the hash chain end-to-end.
3. Verify that a stored simulation reproduces its recorded output from the restored rule set.
4. Verify that PII decrypts with the restored key material.
5. Measure the **RTO** and compare with the target.

### 8.3 Recovery targets

| Scenario | RTO | RPO |
| :--- | :--- | :--- |
| Application host loss | 2 h | 5 min (WAL) |
| PostgreSQL host loss | 4 h | 5 min (WAL) |
| Object store loss | 8 h | 24 h (snapshot) |
| **Total site loss** | 24 h | 24 h |

> These targets are **proposals** for client acceptance. They must be agreed with each design-partner corporation during pilot onboarding (`P4-T10`).

---

## 9. Operations Runbook

### 9.1 Routine operations

| Frequency | Task |
| :--- | :--- |
| Daily | Verify the backup completed; verify the audit chain; review the dead-letter queue; check the oldest queued job age |
| Weekly | Review error rates and latency percentiles; review failed jobs; verify the rule set status is unchanged |
| Monthly | Apply security patches; review access logs for anomalies; verify the certificate; review privileged-role assignments |
| Quarterly | Restore drill; access review; rotate the platform master KEK (scheduled, planned) |
| Annually | Full penetration test; legal compliance review; rule-set re-verification for the new statutory year |

### 9.2 Incident severity and response

| Severity | Definition | Response | Escalation |
| :--- | :--- | :--: | :-- |
| **SEV-1** | Audit chain broken; plaintext PII exposed; active rule set changed without authorisation; tenant isolation failure | Immediate | CISO + CTO + Legal Counsel, within 1 h |
| **SEV-2** | Platform unavailable; job queue stalled > 30 min; backup failure | 1 h | CTO + DevOps Lead |
| **SEV-3** | Degraded performance; elevated error rate; OCR failure rate > 20 % | 4 h | DevOps Lead |
| **SEV-4** | Cosmetic, documentation, minor UI defect | Next sprint | Team |

### 9.3 SEV-1 runbook — suspected audit-chain or PII incident

1. **Contain** — set the application to read-only mode for writes; do **not** restart or redeploy (a restart destroys volatile evidence).
2. **Preserve** — snapshot the database, the object store and the application logs. Record the chain head `H_n` and the last known-good `H_{n-1}`.
3. **Verify** — run the chain verifier over the preserved snapshot to identify the exact break point.
4. **Assess** — identify the affected rows, the tenant, and the time window.
5. **Notify** — Legal Counsel and the affected organisation's `OWNER` within 4 hours. If personal data is involved, assess the notification obligation under the Iranian Computer Crimes Law and E-Commerce Law Art. 58.
6. **Remediate** — repair only with an append-only correction record; **never** rewrite a historical row. A corrected row is appended with a `supersedes_hash` reference.
7. **Report** — a written incident report with the timeline, the affected scope, the evidence and the corrective actions.

### 9.4 Emergency access runbook

See `SPEC-AUTH-001` §9.2. Summary: two-person authorisation, an offline vault, a legal reference, a ledger entry with `actor_type='EMERGENCY'`, and a post-hoc report.

---

## 10. Data Retention and Lifecycle

| Data | Retention | Basis | Action at expiry |
| :--- | :--- | :--- | :--- |
| Unhired candidate simulation data | **180 days** | `RESEARCH_GAP` §8.5 | Cryptographic erasure: destroy the DEK for that candidate record, rendering the ciphertext unrecoverable; keep the audit ledger row (the count and the hash, not the content) |
| Hired-employee dossiers | **10 years** | Tax and labour audit requirement | Retain; do not purge |
| Audit ledger (`audit_logs`) | **10 years** | Evidentiary requirement | Retain; append-only |
| Forensic document objects | **10 years** (3650-day `GOVERNANCE` retention) | ADR-002 | Retain; deletion only via the emergency path |
| Object-storage access logs | 1 year | — | Delete |
| Application logs | 30 days local / 1 year central | — | Delete |
| Sessions | Absolute + 30 days | — | Delete |
| `statutory_rule_set_versions` | Indefinite | Legal | Retain, never mutate |
| Golden vector corpus | Indefinite, versioned | Legal | Retain; supersede with a new version, never edit in place |

**Cryptographic erasure** is the mechanism for the 180-day purge: destroying the per-candidate key makes the ciphertext mathematically unrecoverable without rewriting history or defeating the WORM store.

---

## 11. Upgrade and Rollback

### 11.1 Release artefact

| Item | Detail |
| :--- | :--- |
| Artefact | Versioned container images pinned by digest + a signed SBOM + a release manifest |
| Versioning | Semantic versioning on the API contract; the `engine_version` and `rule_set_version_id` appear in every response |
| Migration | Applied by an explicit, logged step in the release pipeline — **not** by the app on startup |

### 11.2 Release sequence

```
1. Preflight    — staging smoke test, migration dry-run on a production-shaped snapshot
2. Backup       — verified PostgreSQL backup + object-store snapshot
3. Maintenance  — place the app in read-only mode; drain in-flight jobs
4. Migrate      — apply migrations (expand phase)
5. Deploy       — roll the app containers (rolling, N+1)
6. Verify       — health checks, golden-vector smoke test, audit-chain verification
7. Migrate      — apply contract-phase migrations
8. Resume       — return to read-write; confirm queue drain
9. Observe      — watch the error/latency dashboards for 60 minutes
```

### 11.3 Rollback

| Situation | Action |
| :--- | :--- |
| The app fails to start after deploy | Roll back the image. Migrations are forward-compatible (expand phase) so the previous version still runs |
| A migration breaks the app | Roll back the image; apply the **contract** migration to restore the previous schema |
| A destructive migration has already run | **Database restore** — the previous version's data is recovered from the pre-release backup. This is why the backup is verified *before* the release, not after |
| The rule set was activated in error | Deactivate the rule set (a status change, not a delete), redeploy, and re-run the affected simulations under the corrected rule set. Historical snapshots are never rewritten — they are superseded by a new simulation with a `supersedes_simulation_id` reference |
| A rule set was wrong at activation | Follow the statutory change process in `SPEC-STAT-INGESTION.md` §5.5 — a new revision, never an edit |

**Rollback rehearsal** is a release gate (`TESTING.md` §12, Stage 12).

---

## 12. Air-Gapped Deployment

| Concern | Procedure |
| :--- | :--- |
| Package acquisition | On a connected staging machine, mirror the images (`docker save` → `docker load`), the Python wheels (`uv export` + `pip download`), the npm packages (`pnpm fetch`) and the OCR model weights. Transfer by the client's approved media process |
| Container registry | An on-premise registry (Harbor) or a `docker load` bundle. **No external registry reference in the compose file** |
| OCR models | The PaddleOCR Persian model weights are baked into the worker image. The image is large (~2–4 GB) — it must be mirrored in advance |
| Fonts | Vazirmatn `.woff2` is bundled in the frontend image; the PDF font files are baked into the backend image. **No font CDN** |
| Vault | If Vault is unavailable, the local encrypted master config is used. The KEK-derivation path must be identical in dev and production |
| Telemetry | No outbound telemetry, no crash reporting, no update pings. The application makes **no** outbound network connection in production |
| Certificate | The client supplies an internal CA; the certificate is provisioned by the client's PKI |
| NTP | **Critical** — the lease mechanism in the job queue and the audit chain timestamps depend on accurate time. The client must provide an internal NTP source; clock skew > 60 s between app and worker is an alert |
| Air-gapped CI | The CI runner in an air-gapped site runs from a mirrored image set; dependency mirrors are pre-seeded |

### 12.1 Air-gapped verification checklist (run before pilot sign-off)

| # | Check |
| :-- | :--- |
| 1 | The application container makes no outbound connection (verified by an egress test in a network-isolated namespace) |
| 2 | The frontend serves the Vazirmatn font from its own origin |
| 3 | The PDF renders correctly with the bundled font and no system Persian font installed |
| 4 | The OCR worker loads its model from the local filesystem |
| 5 | The image mirror is complete and the digests match the registry |
| 6 | Time synchronisation is verified across app, worker and database |

---

## 13. Related Tasks

| Task | Phase | Title | Status |
| :--- | :--- | :--- | :--- |
| `P0-T03` | 0 | PostgreSQL 16 provisioning, extensions, hardened configuration | NOT_STARTED |
| `P0-T04` | 0 | Alembic migration baseline and `statutory_rule_set_versions` | NOT_STARTED |
| `P0-T16` | 0 | Backup/restore baseline and retention configuration | NOT_STARTED |
| `P0-T17` | 0 | Deployment skeleton: Dockerfiles, compose, Nginx, environment matrix | NOT_STARTED |
| `P2-T03` | 2 | Ceph/S3 integration (boto3, GOVERNANCE Object Lock) | NOT_STARTED |
| `P4-T01` | 4 | Monitoring, alerting and metrics | NOT_STARTED |
| `P4-T02` | 4 | Operations runbooks and incident response | NOT_STARTED |
| `P4-T03` | 4 | Backup/restore drill and disaster-recovery rehearsal | NOT_STARTED |
| `P4-T04` | 4 | Data retention and cryptographic-erasure purge job | NOT_STARTED |
| `P4-T09` | 4 | Pilot deployment in staging and smoke test | NOT_STARTED |
| `P4-T10` | 4 | Pilot onboarding runbook (3 design partners) | NOT_STARTED |
