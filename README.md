# Pish Hesabdari (پیش‌حسابداری)

Statutory Iranian payroll calculation: SSO insurance, progressive income tax, net pay, overtime/night shift, Sanavat, Eydi, employer cost and the Article 11 termination case, on the verified 1404 SH baseline. The product scope is the calculation engine of [ADR-008](docs/adr/ADR-008-product-scope-statutory-payroll-engine.md); the earlier pre-employment platform scope of ADR-004 is superseded.

## Start here

| Need | Read |
| :--- | :--- |
| Starting an agent task | [AGENTS.md](AGENTS.md), then [Documentation Index §0](docs/DOCUMENTATION_INDEX.md#0-task-focused-reading) |
| Snapshot of the current state | [PROJECT_STATE.md](PROJECT_STATE.md) (derived; owners hold the facts) |
| Current delivery state and blockers | [PROJECT_STATUS §2](docs/PROJECT_STATUS.md#2-delivery-state); exact tasks in EXECUTION_PLAN §14.3 |
| Product knowledge and requirements | Relevant sections of [Holy Bible](docs/PISH_HESABDARI_HOLY_BIBLE.md), then the authoritative source it cites |
| Owner decisions | [DECISIONS_REGISTER](docs/DECISIONS_REGISTER.md) and [DECISION_REQUIRED_FROM_OWNER](docs/DECISION_REQUIRED_FROM_OWNER.md) |
| Environment-dependent work | [ENVIRONMENT_INVENTORY](docs/ENVIRONMENT_INVENTORY.md); recheck only the capability needed |
| Verification evidence | [BOOTSTRAP_CHANGELOG](docs/BOOTSTRAP_CHANGELOG.md) §23 records the fresh statutory-engine verification; §19 the foundation verification; §15 the prior PostgreSQL runtime evidence |

Read sections relevant to the task. The full Holy Bible, complete WBS, execution history and research corpus are not a default startup packet. Required specifications and safety rules still apply.

## Current orientation

**Product scope (ADR-008, accepted 2026-11-15): the statutory payroll calculation engine** — SSO, progressive income tax, net pay, overtime/night shift, Sanavat, Eydi, employer CTC and the Article 11 worst case — delivered as pure functions plus one minimal API endpoint. The prior pre-employment platform scope is superseded; non-engine modules are out of product scope pending a future ADR.

The **statutory payroll engine** is implemented and verified on the 1404 baseline: the fail-closed rule-set loader, the base decomposition, SSO, the progressive income tax with both Article 137 postures, overtime and night shift, Sanavat, Eydi, the employer cost identity and the Article 11 termination simulator, composed by one service and served by one endpoint. The compensation advisory module (ADR-009) extends it with band placement and costing of a proposed range. Exact test counts and the commands that produced them live in [BOOTSTRAP_CHANGELOG](docs/BOOTSTRAP_CHANGELOG.md) §28–§29 and are not duplicated here. No real authentication, no integrated tenant-security foundation and no certified golden corpus are claimed. The PostgreSQL integration tests skip themselves where the container image cannot be pulled.

The verified statutory baseline remains **1404 SH**; 1405 is transcribed, unverified and **inactive**. The five-phase/20-week roadmap table is retained for traceability. Current task counts belong in PROJECT_STATUS and the WBS rather than another duplicate table here.

Accepted ADRs are **001–004, 006, 007, 008 and 009**; ADR-005 remains **Proposed**. ADR-008 supersedes ADR-004's Phase 1 module list and directives 2–3 (product scope refocus on the calculation engine); ADR-009 extends ADR-008 with the compensation advisory module. See [ADR_INDEX](docs/ADR_INDEX.md) for status and [DOCUMENTATION_INDEX](docs/DOCUMENTATION_INDEX.md) for source precedence.

## Repository layout

```text
.agents/skills/      11 shared engineering contracts
backend/
  app/engines/      the statutory payroll engines (loader, bases, SSO, tax, …)
  app/api/v1/       the single gross-to-net simulation endpoint
  app/              FastAPI, security, models, migrations and storage adapter
  tests/            unit, API, property and integration suites
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
PROJECT_STATE.md    derived snapshot of the current state (no independent facts)
```

The frontend has a real health-status client and a working gross-to-net simulation screen; authentication screens are disabled and the business-module screens state their missing dependencies. See [frontend/README.md](frontend/README.md). Historical root Markdown/DOCX research is retained; its supersession map is in DOCUMENTATION_INDEX §§2–4. It is not current implementation guidance.

## Development and verification

Dependency installation was approved and performed earlier; backend/.venv exists. Historical results and current access limitations are distinguished in ENVIRONMENT_INVENTORY. An inaccessible interpreter is not evidence that packages should be reinstalled.

### Run the application

```powershell
# Backend (Python 3.12+)
cd backend
uv sync --frozen --all-groups
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000

# Frontend (Node 20+)
cd frontend
corepack enable
pnpm install --frozen-lockfile
pnpm dev            # http://localhost:5173
```

The simulation endpoint is `POST /api/v1/simulations/gross-to-net`; the liveness
probe is `GET /health/live`. The frontend reads the API origin from
`VITE_API_BASE_URL` (see `frontend/.env.example`).

### Verify

```powershell
# Backend
cd backend
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m mypy --strict app tests
.\.venv\Scripts\python.exe -m pytest -q

# Frontend
cd frontend
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

The same gates run on every push in `.github/workflows/ci.yml` (hosted CI for the
development repository only; it deploys nothing and holds no credential).

The PostgreSQL integration suites need the official container image; where it
cannot be pulled they skip themselves and report the skip rather than passing
silently. DEC-012 blocks running the local Alembic/model drafts against a live
database; their presence is not approval to apply them. For first-time setup use
DEPLOYMENT §2 and the frozen lockfile workflow, subject to current blockers.
Local database setup and its side effects are documented in
[infra/postgres/README.md](infra/postgres/README.md).

## Contributor rules and licence

[AGENTS.md](AGENTS.md) contains the mandatory domain, monetary, security, approval and verification rules. No commit or push is authorized by this README.

[LICENSE](LICENSE) is proprietary, all rights reserved. External redistribution rights are not granted by this repository.
