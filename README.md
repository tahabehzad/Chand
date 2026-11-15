# Pish Hesabdari (پیش‌حسابداری)

Pre-employment compensation intelligence and evidentiary verification for Iran. The product supports verified-record hiring offers, statutory simulation, employer-cost modeling and document verification within the boundary of [ADR-004](docs/adr/ADR-004-phase-1-product-boundary-prehire-scope.md).

## Start here

| Need | Read |
| :--- | :--- |
| Starting an agent task | [AGENTS.md](AGENTS.md), then [Documentation Index §0](docs/DOCUMENTATION_INDEX.md#0-task-focused-reading) |
| Current delivery state and blockers | [PROJECT_STATUS §2](docs/PROJECT_STATUS.md#2-delivery-state); exact tasks in EXECUTION_PLAN §14.3 |
| Product knowledge and requirements | Relevant sections of [Holy Bible](docs/PISH_HESABDARI_HOLY_BIBLE.md), then the authoritative source it cites |
| Owner decisions | [DECISIONS_REGISTER](docs/DECISIONS_REGISTER.md) and [DECISION_REQUIRED_FROM_OWNER](docs/DECISION_REQUIRED_FROM_OWNER.md) |
| Environment-dependent work | [ENVIRONMENT_INVENTORY](docs/ENVIRONMENT_INVENTORY.md); recheck only the capability needed |
| Verification evidence | [BOOTSTRAP_CHANGELOG](docs/BOOTSTRAP_CHANGELOG.md) §19 records fresh foundation verification; §15 records prior PostgreSQL runtime evidence |

Read sections relevant to the task. The full Holy Bible, complete WBS, execution history and research corpus are not a default startup packet. Required specifications and safety rules still apply.

## Current orientation

**Product scope (ADR-008, accepted 2026-11-15): the statutory payroll calculation engine** — SSO, progressive income tax, net pay, overtime/night shift, Sanavat, Eydi, employer CTC and the Article 11 worst case — delivered as pure functions plus one minimal API endpoint. The prior pre-employment platform scope is superseded; non-engine modules are out of product scope pending a future ADR.

FastAPI liveness, isolated field encryption, reviewed Decimal money primitives, a tenant-scoped S3 adapter and a partial Persian React interface exist. Fresh verification: 329 backend unit/API tests and 99 frontend tests pass; frontend build, strict backend types and scoped lint/security checks pass. No complete statutory engine, real authentication or integrated tenant-security/database foundation is claimed. PostgreSQL runtime passed in changelog §15; its current state was not rechecked in §19.

The verified statutory baseline remains **1404 SH**; 1405 is transcribed, unverified and **inactive**. The five-phase/20-week roadmap table is retained for traceability. Current task counts belong in PROJECT_STATUS and the WBS rather than another duplicate table here.

Accepted ADRs are **001–004, 006, 007 and 008**; ADR-005 remains **Proposed**. ADR-008 supersedes ADR-004's Phase 1 module list and directives 2–3 (product scope refocus on the calculation engine). See [ADR_INDEX](docs/ADR_INDEX.md) for status and [DOCUMENTATION_INDEX](docs/DOCUMENTATION_INDEX.md) for source precedence.

## Repository layout

```text
.agents/skills/      11 shared engineering contracts
backend/
  app/              FastAPI, security, money primitives and storage adapter
  tests/            unit/API tests; unaccepted migration tests kept separate
  data/seeds/       immutable 1404 baseline; inactive 1405 candidate
  pyproject.toml    dependencies/tooling; uv.lock pins exact versions
docs/
  adr/              decisions
  specs/            subsystem requirements
  PROJECT_STATUS.md current delivery summary
  EXECUTION_PLAN.md WBS, dependencies and acceptance criteria
infra/
  compose/          development Compose configuration
  postgres/         local PostgreSQL scaffold, runbook and verifiers
frontend/           partial React/Vite Persian RTL interface and typed API client
```

The frontend has a real health-status client; authentication screens are disabled and business-module screens state their missing dependencies. See [frontend/README.md](frontend/README.md). Historical root Markdown/DOCX research is retained; its supersession map is in DOCUMENTATION_INDEX §§2–4. It is not current implementation guidance.

## Development and verification

Dependency installation was approved and performed earlier; backend/.venv exists. Historical results and current access limitations are distinguished in ENVIRONMENT_INVENTORY. An inaccessible interpreter is not evidence that packages should be reinstalled.

For an existing usable environment, from the repository root:

```powershell
rtk proxy .\backend\.venv\Scripts\python.exe -B -m ruff check backend/app backend/tests/unit backend/tests/api
rtk proxy .\backend\.venv\Scripts\python.exe -B -m mypy --config-file backend/mypy.ini backend/app backend/tests/unit backend/tests/api
rtk proxy .\backend\.venv\Scripts\python.exe -B -m pytest -q backend/tests/unit backend/tests/api
```

The scope above deliberately excludes unaccepted migration tests. DEC-012 blocks running the local Alembic/model drafts; their presence is not approval to apply them. For first-time setup use DEPLOYMENT §2 and the frozen lockfile workflow, subject to current blockers. Local database setup and its side effects are documented in [infra/postgres/README.md](infra/postgres/README.md).

## Contributor rules and licence

[AGENTS.md](AGENTS.md) contains the mandatory domain, monetary, security, approval and verification rules. No commit or push is authorized by this README.

[LICENSE](LICENSE) is proprietary, all rights reserved. External redistribution rights are not granted by this repository.
