---
title: "Architecture Map — Pish Hesabdari"
document_id: KNOW-ARCH-001
status: Active navigation layer
as_of: 2026-11-16
---

# Architecture Map

> Navigation over the existing architecture sources. The binding architecture is in [ADR-001…004, 006, 007, 008](../../docs/ADR_INDEX.md); ADR-005 remains **PROPOSED** and is not a constraint. This note does not introduce a new architecture.

## System shape

**Modular monolith** for the ADR-008 v1 scope: pure calculation functions, one composition service and one minimal HTTP endpoint, with PostgreSQL/RBAC/storage foundations around them.

```text
Client / tests
    |
    v
FastAPI application (backend/app/main.py)
    |
    +-- API route: POST /api/v1/simulations/gross-to-net
    |       backend/app/api/v1/payroll.py
    |
    +-- Schema validation: backend/app/schemas/payroll.py
    |
    +-- Composition: backend/app/services/payroll_service.py
    |       |
    |       +-- Rule-set loader: app/engines/rules.py
    |       +-- Base decomposition: app/engines/bases.py
    |       +-- SSO: app/engines/sso.py
    |       +-- Tax: app/engines/tax.py
    |       +-- Overtime: app/engines/overtime.py
    |       +-- Severance: app/engines/severance.py
    |       +-- Eydi: app/engines/eydi.py
    |       +-- CTC: app/engines/ctc.py
    |       +-- Termination: app/engines/termination.py
    |       +-- Decimal primitives: app/engines/money.py
    |
    +-- Statutory access / persistence foundation
            backend/app/models/statutory.py
            backend/alembic/versions/0001_statutory_baseline.py
            infra/postgres/statutory_roles.sql
```

**Not decided:** asynchronous execution remains ADR-005 `PROPOSED`; no queue is approved. `P2-T04` remains blocked. Do not describe a background worker as implemented.

## Architectural boundaries

| Boundary | Rule | Source |
| :--- | :--- | :--- |
| Pure calculation | No clock, randomness, network or environment reads in the calculation path | [AGENTS.md §2](../../AGENTS.md) |
| Money | Decimal only; `prec=34`; `ROUND_HALF_UP`; round once at line-item boundary | [AGENTS.md §2](../../AGENTS.md) · [financial-data-integrity skill](../../.agents/skills/financial-data-integrity/SKILL.md) |
| Statutory values | Fail closed; unknown values are never coerced to zero | [AGENTS.md §2](../../AGENTS.md) · [rules.py](../../backend/app/engines/rules.py) |
| Tenant isolation | `tenant_id`, RLS and `FORCE ROW LEVEL SECURITY` in the same migration | [ADR-006](../../docs/adr/ADR-006-phase-0-owner-approved-security-and-schema.md) |
| Statutory evidence | Global tables, restricted reader/reviewer roles, write gate until P0-T05 | [ADR-007](../../docs/adr/ADR-007-statutory-global-access-and-deferred-identity.md) |
| Frontend | React/Vite SPA, RTL, typed API client | [ADR-001](../../docs/adr/ADR-001-frontend-architecture-react-vite-spa.md) · [FRONTEND_PERSIAN](../../docs/specs/FRONTEND_PERSIAN.md) |
| Storage | Ceph / S3-compatible `GOVERNANCE` WORM | [ADR-002](../../docs/adr/ADR-002-object-storage-worm-ceph-s3-governance.md) |
| Encryption | ALEE + HMAC blind indexing; no `pgcrypto` | [ADR-003](../../docs/adr/ADR-003-sensitive-data-encryption-alee-blind-indexing.md) |

## Module map

| Module | Implementation | Specification / decision |
| :--- | :--- | :--- |
| Rule-set loading and fingerprints | [rules.py](../../backend/app/engines/rules.py) | [STATUTORY_INGESTION](../../docs/specs/STATUTORY_INGESTION.md) |
| Base decomposition | [bases.py](../../backend/app/engines/bases.py) | [Holy Bible](../../docs/PISH_HESABDARI_HOLY_BIBLE.md) §2.3 |
| Social Security (SSO) | [sso.py](../../backend/app/engines/sso.py) | ADR-008; B-3 open |
| Progressive income tax | [tax.py](../../backend/app/engines/tax.py) | ADR-008; `conservative_inta` primary |
| Overtime / night shift | [overtime.py](../../backend/app/engines/overtime.py) | ADR-008; B-4 open |
| Sanavat | [severance.py](../../backend/app/engines/severance.py) | ADR-008; B-4 open |
| Eydi | [eydi.py](../../backend/app/engines/eydi.py) | ADR-008; HB-GAP-005; B-5/B-6 open |
| Employer CTC | [ctc.py](../../backend/app/engines/ctc.py) | ADR-008 |
| Article 11 / leave buyout | [termination.py](../../backend/app/engines/termination.py) | ADR-008; B-7/B-8 open |
| Reference-only statutory values | [statutory_reference.py](../../backend/app/engines/statutory_reference.py) | DEC-013 open |
| Composition and provenance | [payroll_service.py](../../backend/app/services/payroll_service.py) | [BOOTSTRAP_CHANGELOG §24](../../docs/BOOTSTRAP_CHANGELOG.md) |
| HTTP contract | [payroll.py](../../backend/app/api/v1/payroll.py) · [schemas/payroll.py](../../backend/app/schemas/payroll.py) | [DEPLOYMENT §7.1](../../docs/specs/DEPLOYMENT.md) |
| Database baseline | [0001_statutory_baseline.py](../../backend/alembic/versions/0001_statutory_baseline.py) | [STATUTORY_DATABASE_CONTRACT](../../docs/specs/STATUTORY_DATABASE_CONTRACT.md) |
| Frontend shell | [frontend/README.md](../../frontend/README.md) · [router.tsx](../../frontend/src/app/router.tsx) | [FRONTEND_PERSIAN](../../docs/specs/FRONTEND_PERSIAN.md) |
| Simulation screen | [simulation-page.tsx](../../frontend/src/routes/simulation-page.tsx) | [PROJECT_STATUS §2](../../docs/PROJECT_STATUS.md) |
| Typed API client | [client.ts](../../frontend/src/api/client.ts) · [contracts.ts](../../frontend/src/api/contracts.ts) | API contract tests |

## Test architecture

| Layer | Location | Current evidence |
| :--- | :--- | :--- |
| Unit | `backend/tests/unit/` | Included in 568 passing tests |
| API / contract | `backend/tests/api/` | Contract suite collects and passes; PostgreSQL-backed cases skip without Docker |
| Property | `backend/tests/property/` | Hypothesis properties P-02…P-08, P-10 |
| Integration | `backend/tests/integration/` | **NOT RUN here** — Docker unavailable |
| Frontend | `frontend/src/**/*.test.ts(x)` | 110 tests recorded |

Source: [TESTING.md](../../docs/specs/TESTING.md) · [BOOTSTRAP_CHANGELOG §24](../../docs/BOOTSTRAP_CHANGELOG.md).

## Deployment and operations

- [DEPLOYMENT.md](../../docs/specs/DEPLOYMENT.md) — topology, containers, migrations, secrets, TLS, observability, backup, rollback.
- [infra/postgres/README.md](../../infra/postgres/README.md) — local PostgreSQL and hardening.
- [ENVIRONMENT_INVENTORY.md](../../docs/ENVIRONMENT_INVENTORY.md) — dated environment evidence; not a current capability guarantee.
- [.github/workflows/ci.yml](../../.github/workflows/ci.yml) — CI definition; **never executed on GitHub** as of the §24 record.

No production deployment, authenticated workflow or phase-gate approval is claimed.
