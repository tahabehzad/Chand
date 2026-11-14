# ADR-005: Asynchronous Execution Strategy for Long-Running Document Processing

- **Status**: **PROPOSED** — not Accepted. Requires approval by CTO + DevOps Lead + Lead Backend Engineer before implementation.
- **Date**: 2026-11-14 (23 Aban 1405 SH)
- **Deciders**: Chief Technology Officer (decision owner), DevOps Lead, Lead Backend Engineer, Security Architect
- **Consulted**: Lead Frontend Engineer, Document Forensics Engineer, Legal Counsel (data residency implications)
- **Supersedes**: nothing. **Related**: `REMEDIATED_TECHNICAL_SPECIFICATION_V2.md` §3.1 and `.agents/skills/software-architecture/SKILL.md` (both specify FastAPI `BackgroundTasks`). Celery/Redis is a historical alternative, not the current specification's mandate.

> **Authority note.** This ADR remains `PROPOSED`; `P2-T04` is blocked until a decision is accepted. The current specification and skill both name `BackgroundTasks`. The real unresolved issue is satisfying durable retry/restart semantics and CPU isolation. Labels such as "Rejected" in the alternative evaluation below are recommendations within this proposal, not accepted project decisions. Correcting the premise does not approve the PostgreSQL queue or amend an accepted ADR.

---

## Context and Problem Statement

Pish Hesabdari has two execution classes with materially different characteristics:

| Class | Examples | Latency budget | Failure cost |
| :--- | :--- | :--- | :--- |
| **Fast path** (synchronous) | Statutory calculation, net-to-gross inversion, CTC projection, benchmark banding | < 20 ms | User retries |
| **Slow path** (asynchronous) | PDF structural forensics, PaddleOCR PP-Structure extraction, ELA image analysis, pyHanko signature verification, cross-document consistency | 1.2 s – 6.0 s per page (`FIND-ARCH-05`) | Work is lost or duplicated |

The slow path is CPU-bound (model inference), can exceed a gateway timeout, and must survive process restart. `REMEDIATED_TECHNICAL_SPECIFICATION_V2.md` §3/§3.1 and `.agents/skills/software-architecture/SKILL.md` specify **FastAPI `BackgroundTasks`**. This proposal evaluates whether a different execution mechanism is needed to meet durability and isolation constraints; it does not resolve that question without acceptance.

**The deployment environment is the dominant constraint.** ADR-001 names Iranian enterprise intranets — including air-gapped and private-cloud installations — as the driving requirement for a static SPA with zero Node.js runtime. A production client may operate a single on-premise host with no managed cloud, and the development team develops on Windows. This is materially different from the implicit assumption of a managed-Kubernetes environment in the original spec.

### Constraints

| # | Constraint | Source |
| :-- | :--- | :--- |
| C1 | Windows is the primary development platform | Environment; `software-architecture` skill |
| C2 | Production targets may be air-gapped Iranian enterprise intranets | ADR-001 decision drivers 2 |
| C3 | No cloud-managed service may be assumed | Task constraint §7 |
| C4 | OCR jobs run 1.2–7.0 s/page and are CPU-bound | `FIND-ARCH-05` |
| C5 | Jobs must be durable across restarts and must not be lost | Reliability requirement |
| C6 | Retry semantics must be explicit and bounded | Reliability requirement |
| C7 | Job state must be observable and auditable | `REMEDIATED` §3 `AsyncRouter`; §7 Module 7 provenance |
| C8 | Added infrastructure components increase on-site operational burden for clients | ADR-001 driver 2 |
| C9 | Hash-chained provenance must record the exact inputs of every computation | `REMEDIATED` Module 7 |

---

## Decision Drivers

1. **Durability under restart** — a document analysis job must not be lost when a worker process is redeployed.
2. **Air-gapped operability** — the stack must install and run with no internet access and no managed service.
3. **Windows development parity** — engineers must be able to run the full stack locally on Windows without a second runtime platform.
4. **Explicit retry and idempotency semantics** — OCR re-runs must not create duplicate forensic artifacts.
5. **Operational footprint** — every additional long-running service is an on-site operational liability for an enterprise client.
6. **Observability** — job state, duration, retry count and failure cause must be queryable and auditable.
7. **Scale headroom** — the design must permit a second and third worker without redesign.
8. **Cost** — Iranian enterprise clients run on modest, often virtualised, hardware.

---

## Considered Options

### Option 1 — Celery + Redis (historical alternative)

Redis as broker/result backend; Celery workers consuming `documents.verify` tasks.

**Pros**
- Mature, widely understood; large body of operational knowledge.
- Built-in retries, routing, chords, rate limits, and result backends.
- Explicit job state transitions; good operational tooling (`flower`, `celery inspect`).
- Natural horizontal scale-out: add workers, done.

**Cons**
- **Redis becomes a fourth stateful service** (PostgreSQL, Ceph/S3, Redis, app) that must be installed, secured, persisted, backed up and monitored on every client site, including air-gapped ones.
- **Redis persistence is not a job-durability guarantee** by default — unless configured with AOF/RDB and a supervisor, a broker loss drops in-flight and queued tasks. AOF + `appendfsync everysec` still permits loss of the last second of writes.
- **Windows support is materially weaker.** Celery on Windows requires the `wint`/`solo` pool, which **does not support prefetch, does not support concurrency > 1, and does not support some scheduling features**. Windows therefore cannot be a faithful development environment for the production topology; parity is lost.
- Celery's task result store duplicates state that PostgreSQL already holds authoritatively.
- Adds an operational failure mode (broker outage) that produces silent job disappearance rather than a loud error.

**Assessment:** production-grade on Linux, but poor fit for C1, C2 and C8.

### Option 2 — FastAPI `BackgroundTasks` (as specified in `.agents/skills/software-architecture`)

In-process async task execution via Starlette's `BackgroundTasks`.

**Pros**
- **Zero additional infrastructure.** No broker, no worker fleet, no extra service to install or monitor.
- Identical behaviour on Windows, Linux and in containers; perfect development/production parity (C1).
- Ideal for the air-gapped case (C2): nothing extra to deploy.
- Trivial operational footprint — the single biggest win against C8.
- Excellent fit for short-ish tasks (< 60 s) that tolerate at-most-once delivery.

**Cons**
- **Tasks are lost on process restart.** `BackgroundTasks` are in-process; a redeploy mid-OCR discards the job.
- **No built-in retry**, no rate limiting, no scheduling.
- **Runs on the event loop's thread pool** — a CPU-bound OCR task blocks or saturates a worker thread and degrades the fast path (violating the < 20 ms budget of `REMEDIATED` §5.1). Offloading to a thread pool does not free the GIL for CPU-bound work.
- **No durable job state**; job status must be reconstructed from the database, which is possible but ad hoc.
- Cannot survive a scale-out across multiple app replicas without sticky routing.

**Assessment:** excellent on C1/C2/C8; fails C5, C6 and the fast-path isolation requirement.

### Option 3 — PostgreSQL-backed job queue (advisory-locked SKIP LOCKED)

A `jobs` table in the existing PostgreSQL instance. Workers claim rows with `SELECT … FOR UPDATE SKIP LOCKED`; state, retry count and payload live in the database. Workers are thin processes launched alongside the app.

**Pros**
- **No new infrastructure.** PostgreSQL is already a required component with an existing backup, HA, and monitoring story (C2, C8).
- **Durability is inherited from PostgreSQL's WAL.** A committed job row survives a full container/host restart; `pg_dump`/base backup already covers it (C5).
- **Retry, backoff, max-attempts, dead-letter and scheduling are plain SQL** — fully explicit and auditable (C6).
- **Windows parity** — the worker is an ordinary Python process using `psycopg`; identical code path on every OS (C1).
- **Job state is queryable in SQL**, which makes the audit trail (`REMEDIATED` Module 7) and the operations runbook straightforward (C7).
- **Idempotency is enforceable** with a unique constraint on an idempotency key, which the document pipeline needs regardless of the queue technology.
- **Scales horizontally** by adding worker processes — same code, same image.
- Only one write path for job state and forensic artifact state, so no cross-store consistency problem.

**Cons**
- Requires a **purpose-built queue discipline**: worker leasing with heartbeat + timeout reaping, `SKIP LOCKED` polling (poll interval must be tuned), and careful transaction boundaries.
- High-contention polling can create load; mitigated by a short poll interval, index design, and `LISTEN/NOTIFY` as an optional wake-up.
- No built-in visual dashboard (must be built; a small read-only ops view is required anyway).
- Worker lease expiry and clock skew need explicit handling.
- Not a general-purpose workflow engine — acceptable, because the platform has exactly one async workload class.

**Assessment:** strongest overall fit; the complexity is real but is *domain* complexity we would otherwise pay in Celery configuration anyway, and it is paid in SQL where it is auditable.

### Option 4 — Hybrid: `BackgroundTasks` for the fast path, PostgreSQL queue for the slow path

**Pros**
- Keeps the fast path free of any queue interaction.
- Durability for the only workload class that needs it.

**Cons**
- Two execution models to reason about and two places for bugs.
- The "hybrid" boundary tends to erode: the next medium-duration job gets pushed onto `BackgroundTasks` by inertia.
- No reduction in complexity relative to Option 3, which already keeps the fast path untouched (the fast path never touches the queue table).

**Assessment:** adds a distinction without adding a capability. Option 3 already isolates the fast path.

### Option 5 — External managed queue / cloud-native broker (SQS, RabbitMQ Cluster, cloud-native job service)

**Excluded before evaluation:** violates C3 (no cloud assumption) and C2 (air-gapped). Recorded for completeness only.

---

## Decision Outcome

**Chosen option: Option 3 — PostgreSQL-backed job queue with `FOR UPDATE SKIP LOCKED` leasing.**

> **Status: PROPOSED.** This outcome is a recommendation. It becomes binding only when the CTO records acceptance in this ADR. Until then the corresponding WBS task `P2-T04` remains `BLOCKED`.

### Rationale

Option 3 satisfies every hard constraint that Options 1 and 2 each fail:

| Constraint | Opt 1 Celery+Redis | Opt 2 BackgroundTasks | **Opt 3 PG queue** |
| :--- | :--- | :--- | :--- |
| C1 Windows parity | ✕ (`solo` pool, no concurrency) | ✓ | ✓ |
| C2 Air-gapped | ✕ (extra service) | ✓ | ✓ |
| C3 No cloud | ✓ | ✓ | ✓ |
| C4 CPU-bound OCR | ✓ | ✕ (blocks fast path) | ✓ |
| C5 Durable across restart | ✕ (broker loss) | ✕ | ✓ (WAL) |
| C6 Explicit retry | ✓ | ✕ | ✓ (SQL) |
| C7 Observable / auditable | ✓ | ✕ | ✓ (SQL) |
| C8 Operational footprint | ✕ | ✓ | ✓ |
| C9 Provenance capture | ✓ | partial | ✓ |

The decision is not "PostgreSQL is better than Redis" in the abstract. It is that **the platform already operates, backs up, secures and monitors PostgreSQL as a mandatory component**, and the marginal cost of a second mandatory stateful service is materially higher in an air-gapped Iranian enterprise deployment than the marginal cost of a disciplined SQL leasing protocol. The added discipline is explicit, reviewable, and testable — which suits a platform whose central claim is auditability.

### Positive Consequences

- One fewer mandatory on-site service for every client; one fewer backup and monitoring surface.
- Job state, forensic artifact state and the audit ledger can be joined in a single query — directly strengthening `REMEDIATED` Module 7.
- Identical code path on Windows, Linux and containers; no dual-environment drift.
- Retry and idempotency semantics become part of the schema and therefore part of the audit trail.

### Negative Consequences / Trade-offs

- We must build and maintain worker leasing, heartbeat and reaping ourselves. This is real work (`P2-T04`, estimated 8 engineer-days) and is a permanent maintenance liability.
- `SKIP LOCKED` polling places a small, constant load on PostgreSQL. Must be tuned and monitored (poll interval, partial indexes on the claimable predicate).
- No off-the-shelf operations dashboard; a minimal read-only ops view is required (`P4-T01`).
- A high-volume burst will contend with the fast path on the same instance. Mitigation: separate the queue connection pool and cap concurrent workers; a dedicated queue instance is the documented scale path.
- Less battle-tested than Celery for exotic routing patterns — which we do not need.

---

## Pros and Cons of Considered Options

| Option | Pros | Cons | Verdict |
| :--- | :--- | :--- | :--- |
| 1. Celery + Redis | Mature; built-in retry/routing/dashboard; strong scale-out | 4th stateful service; broker-loss job loss; weak Windows support; duplicates state | **Rejected** — poor fit for C1/C2/C8 |
| 2. FastAPI `BackgroundTasks` | Zero infra; perfect parity; minimal footprint | Loses jobs on restart; no retry; CPU-bound work degrades the fast path; no durable state | **Rejected** — fails C5/C6 and the < 20 ms fast-path budget |
| **3. PostgreSQL job queue** | Durable via WAL; no new service; full Windows parity; explicit, auditable retry/idempotency; SQL-observable | Must build leasing/heartbeat/reaping; polling load; no built-in dashboard | **Proposed** |
| 4. Hybrid 1+2 | — | Two models, one capability | **Rejected** — no benefit over 3 |
| 5. Managed cloud broker | Managed ops | Violates C2/C3 | **Excluded** |

---

## Implementation Directives

These directives become binding **only on acceptance** of this ADR.

1. **Queue schema.** `jobs` table with: `id UUID PK`, `tenant_id UUID NOT NULL`, `job_type VARCHAR(64) NOT NULL`, `payload JSONB NOT NULL`, `status VARCHAR(16) NOT NULL` (`QUEUED`/`RUNNING`/`SUCCEEDED`/`FAILED`/`DEAD`), `attempts INT NOT NULL DEFAULT 0`, `max_attempts INT NOT NULL`, `available_at TIMESTAMPTZ NOT NULL`, `idempotency_key VARCHAR(200) NOT NULL`, `lease_owner UUID`, `lease_expires_at TIMESTAMPTZ`, `last_error TEXT`, `created_at`, `updated_at`, `completed_at`.
2. **Idempotency.** `UNIQUE (tenant_id, idempotency_key)`. A repeated submission returns the existing job rather than creating a second one. Required for document verification, which must not produce duplicate forensic artefacts.
3. **Claiming.** `SELECT … FROM jobs WHERE status IN ('QUEUED','RUNNING') AND available_at <= now() AND (lease_expires_at IS NULL OR lease_expires_at < now()) ORDER BY available_at FOR UPDATE SKIP LOCKED LIMIT n`, inside a short transaction that sets `status='RUNNING'`, `lease_owner`, `lease_expires_at = now() + lease_seconds`.
4. **Heartbeat.** The worker extends `lease_expires_at` at a fixed interval strictly shorter than the lease duration.
5. **Reaping.** A sweeper transitions `RUNNING` jobs with an expired lease back to `QUEUED` (incrementing `attempts`) up to `max_attempts`, then to `DEAD`. Reaping must be idempotent and safe to run concurrently with workers.
6. **Retry.** Exponential backoff with a configured base and cap; `available_at = now() + backoff(attempts)`. Transient errors (OCR model timeout, S3 throttling) are retryable; deterministic validation failures are not and go straight to `FAILED` with the error surfaced.
7. **Idempotent work.** Every job handler must be idempotent. Document verification writes to a per-`(document_id, analysis_version)` artifact table with a unique constraint so a retry overwrites rather than duplicates.
8. **CPU isolation.** OCR work runs in a **separate OS process** from the ASGI server (a dedicated worker process, not a thread), so that GIL contention cannot breach the fast-path latency budget. The fast path never touches the `jobs` table.
9. **Connection separation.** The worker uses a dedicated connection pool with a small `max_connections`, disjoint from the request path's pool, so polling load cannot starve the API.
10. **Observability.** `jobs` rows carry `attempts`, `last_error`, timing columns and `lease_owner`. A read-only operations view (`P4-T01`) surfaces queue depth, age of oldest `QUEUED` job, failure rate and dead-letter count. Metrics are emitted at job completion.
11. **Audit linkage.** Job creation and completion are written to the hash-chained `AUDIT_LOGS` ledger with the `job_id` and the `rule_set_version_id` where applicable, preserving `REMEDIATED` Module 7 provenance across asynchronous work.
12. **Migration path.** If this ADR is rejected in favour of Option 1 or 2, `P2-T04` is re-planned before `P2-T05` begins. The document pipeline must not be built against an undecided queue abstraction; `P2-T05` consumes a `JobQueue` interface, so the backend is swappable.

---

## Rejected Alternatives — Explicit Record

The following are **rejected** and must not be reintroduced without a new, reviewed ADR:

- **`pgcrypto` in-database encryption** — rejected by ADR-003 (`FIND-ARCH-03`, `FIND-DATA-02`).
- **MinIO with S3 Object Lock `COMPLIANCE` mode** — rejected by ADR-002 (`FIND-ARCH-02`).
- **Bisection-based net-to-gross inversion** — replaced by the O(1) closed-form piecewise inverter (`FIND-MATH-01`).
- **MCDA company-wide salary-review endpoints** — removed from Phase 1 by ADR-004 (`FIND-PROD-01`).
- **Redis as a mandatory on-site broker** — proposed for rejection by this unaccepted ADR; no binding rejection is recorded here.

**2026-11-14 factual correction:** removed the false attribution of a Celery/Redis mandate to `REMEDIATED` and clarified proposal-only authority. No status or implementation decision changed; see `docs/BOOTSTRAP_CHANGELOG.md` §10.
