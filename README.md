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
| Verification evidence | [BOOTSTRAP_CHANGELOG §12](docs/BOOTSTRAP_CHANGELOG.md#12-p0-t03-local-postgresql-scaffold-registry-blocker--2026-11-14); §13 records documentation maintenance |

Read sections relevant to the task. The full Holy Bible, complete WBS, execution history and research corpus are not a default startup packet. Required specifications and safety rules still apply.

## Current orientation

FastAPI scaffolding, tests, an isolated field-encryption primitive and a local PostgreSQL scaffold exist. No completed financial engine or integrated tenant-security/database foundation is claimed. The last recorded PostgreSQL attempt was blocked by official image/build HTTP 403; see the evidence above rather than assuming a live service.

The verified statutory baseline remains **1404 SH**; 1405 is transcribed, unverified and **inactive**. The approved roadmap remains **five phases / 20 weeks**. Current task counts belong in PROJECT_STATUS and the WBS rather than another duplicate table here.

Accepted ADRs are **001–004 and 006**; ADR-005 remains **Proposed**. ADR-006 amends only ADR-003's indexed table target and records the owner's four Phase 0 decisions. See [ADR_INDEX](docs/ADR_INDEX.md) for status and [DOCUMENTATION_INDEX](docs/DOCUMENTATION_INDEX.md) for source precedence.

## Repository layout

```text
.agents/skills/      11 shared engineering contracts
backend/
  app/              FastAPI, configuration/logging and isolated security code
  tests/            scaffold, security and local-material tests
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
```

Frontend scaffolding is not present. Historical root Markdown/DOCX research is retained; its supersession map is in DOCUMENTATION_INDEX §§2–4. It is not current implementation guidance.

## Development and verification

Dependency installation was approved and performed earlier; backend/.venv exists. Historical results and current access limitations are distinguished in ENVIRONMENT_INVENTORY. An inaccessible interpreter is not evidence that packages should be reinstalled.

For an existing usable environment, from the repository root:

```powershell
rtk proxy .\backend\.venv\Scripts\python.exe -B -m ruff check backend/app backend/tests
rtk proxy .\backend\.venv\Scripts\python.exe -B -m ruff format --check backend/app backend/tests
rtk proxy .\backend\.venv\Scripts\python.exe -B -m mypy --config-file backend/mypy.ini backend/app backend/tests
rtk proxy .\backend\.venv\Scripts\python.exe -B -m pytest -q backend/tests
```

These are application verification commands, not checks run by the documentation-maintenance session. For first-time setup use DEPLOYMENT §2 and the frozen lockfile workflow; do not reinstall or start services merely to inspect documentation. Local database setup and its side effects are documented in [infra/postgres/README.md](infra/postgres/README.md).

## Contributor rules and licence

[AGENTS.md](AGENTS.md) contains the mandatory domain, monetary, security, approval and verification rules. No commit or push is authorized by this README.

[LICENSE](LICENSE) is proprietary, all rights reserved. External redistribution rights are not granted by this repository.
