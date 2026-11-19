# Pish Hesabdari (پیش‌حسابداری)

Smart salary estimation platform for the Iranian labor market. A single manager enters a candidate's resume and career information, and the system estimates an appropriate monthly salary based on actual Iranian labor market conditions. The product scope is defined in [ADR-013](docs/adr/ADR-013-resume-analysis-salary-estimation-tool.md); the earlier statutory payroll engine scope (ADR-008) is partially superseded for product direction.

## Start here

| Need | Read |
| :--- | :--- |
| Product vision and scope | [PRODUCT_VISION.md](docs/PRODUCT_VISION.md), [PRODUCT_SCOPE.md](docs/PRODUCT_SCOPE.md) |
| Functional requirements | [FUNCTIONAL_REQUIREMENTS.md](docs/FUNCTIONAL_REQUIREMENTS.md) |
| Non-functional requirements | [NON_FUNCTIONAL_REQUIREMENTS.md](docs/NON_FUNCTIONAL_REQUIREMENTS.md) |
| User workflows | [USER_WORKFLOWS.md](docs/USER_WORKFLOWS.md) |
| Salary estimation spec | [SALARY_ESTIMATION_SPEC.md](docs/SALARY_ESTIMATION_SPEC.md) |
| Labor market data spec | [LABOR_MARKET_DATA_SPEC.md](docs/LABOR_MARKET_DATA_SPEC.md) |
| AI analysis spec | [AI_ANALYSIS_SPEC.md](docs/AI_ANALYSIS_SPEC.md) |
| Data model spec | [DATA_MODEL_SPEC.md](docs/DATA_MODEL_SPEC.md) |
| Security and privacy | [SECURITY_AND_PRIVACY.md](docs/SECURITY_AND_PRIVACY.md) |
| Architecture | [ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| Implementation roadmap | [IMPLEMENTATION_ROADMAP.md](docs/IMPLEMENTATION_ROADMAP.md) |
| Open decisions | [OPEN_DECISIONS.md](docs/OPEN_DECISIONS.md) |
| Documentation audit | [docs/audit/DOCUMENTATION_AUDIT.md](docs/audit/DOCUMENTATION_AUDIT.md) |
| Owner decisions | [DECISIONS_REGISTER.md](docs/DECISIONS_REGISTER.md) and [OPEN_DECISIONS.md](docs/OPEN_DECISIONS.md) |
| Architecture decisions | [ADR_INDEX.md](docs/ADR_INDEX.md) and [docs/adr/](docs/adr/) |

Read sections relevant to the task. The full documentation history is retained; ADRs are preserved with their historical text unchanged.

## Current orientation

**Product scope (ADR-013, accepted 2026-11-17): a resume analysis and monthly salary estimation tool** — one manager enters a candidate's career information (job title, experience, skills, education, city, employment type, seniority level), and the system returns a suggested salary range with a primary estimate, influencing factors, and confidence level. The prior statutory payroll calculation engine scope (ADR-008) is partially superseded for product direction; its technical code and invariants (Decimal money, ROUND_HALF_UP, fail-closed loader, no float literals) are preserved where applicable.

The statutory payroll engine (SSO, progressive income tax, net pay, overtime/night shift, Sanavat, Eydi, employer CTC, Article 11) remains implemented on the verified 1404 baseline but is **not** the active product. The verified statutory baseline remains **1404 SH**; 1405 is transcribed, unverified and **inactive**.

Accepted ADRs are **001–004, 006, 007, 008, 009, 010, 011, 012, 013, and 014**; ADR-005 remains **Proposed**. ADR-013 and ADR-014 define the active salary estimation product; earlier payroll-era boundary clauses are superseded while technical invariants (Decimal money, ROUND_HALF_UP, fail-closed loader, no float literals) are preserved. See [ADR_INDEX](docs/ADR_INDEX.md) for status and [DOCUMENTATION_INDEX](docs/DOCUMENTATION_INDEX.md) for source precedence.

## Key Features & Architecture

### 1. Single-Page Live Salary Dashboard
The primary user interface (`/`) is an interactive Persian RTL dashboard tailored for hiring managers:
* **Candidate Career Profiling:** Collects job title, experience years, seniority level, employment type, city/province, work condition, education, and skills.
* **Salary Range Gauge (P25…P75):** Visualizes lower quartile, median, and upper quartile benchmarked against the statutory minimum wage reference.
* **Market Sample Distribution:** Histogram of actual market observations and empirical density.
* **Strategic Negotiation Sheet:** Provides market percentile positioning (<P25, P25-P50, P50-P75, >P75), tactical talking points for Iranian labor negotiations, and true employer cost multiplier.
* **Audit & Provenance Envelope:** Emits transparent calculation hash, data recency, confidence scores, and rule versions.

### 2. Gemini BYOK (Bring Your Own Key) & Live Grounding
* **Client-Side Secret Storage:** The Gemini API key is stored exclusively in the browser's `localStorage` and sent per-request. It is **never** logged, never written to backend databases, and never leaked in exception traces.
* **Live Web Grounding:** Performs real-time search across Iranian job portals (Jobinja, Jobvision, IranTalent, Quera) for current job compensation.
* **Anti-Fabrication Guardrail (ADR-014):** AI is restricted to structured web extraction. If no valid market data covers the cohort, the system refuses with `409 ESTIMATION_INSUFFICIENT_DATA`; it **never** invents numbers.
* **Seamless Database Fallback:** If Gemini is unreachable or disabled, queries PostgreSQL benchmark reference tables with zero disruption.

### 3. Total Cost to Employer (CTC) & Net Pay Breakdown
Reuses the verified Iranian statutory calculation engine (1404 SH baseline) to compute:
* **Employee Net Pay:** Deducts capped employee Social Security (7%) and progressive income tax (Article 137 conservative posture).
* **Employer Overhead:** Computes employer Social Security (20%), unemployment insurance (3%), monthly severance accrual (1/12), and monthly annual bonus accrual (1/12 capped Eydi).
* **Full Reconciliation:** Net salary + deductions = gross; gross + employer overhead = CTC. All calculations use `Decimal` with `prec = 34` and `ROUND_HALF_UP` (no float literals).

## Repository layout

```text
.agents/skills/      11 shared engineering contracts
backend/
  app/domain/       active domain engines (salary_estimation core)
  app/engines/      preserved engines (statutory payroll)
  app/api/v1/       API endpoints (estimation active; gross-to-net preserved)
  app/              FastAPI, security, models, migrations and repositories
  tests/            unit, API, property, e2e and integration suites
  data/seeds/       immutable 1404 baseline; inactive 1405 candidate
  pyproject.toml    dependencies/tooling; uv.lock pins exact versions
docs/
  adr/              architecture decisions (ADR-001…014)
  specs/            subsystem specifications
  audit/            documentation audit matrix
  archive/          archived legacy audit reports and historical plans
  PROJECT_VISION.md, PRODUCT_SCOPE.md, FUNCTIONAL_REQUIREMENTS.md,
  NON_FUNCTIONAL_REQUIREMENTS.md, USER_WORKFLOWS.md,
  SALARY_ESTIMATION_SPEC.md, LABOR_MARKET_DATA_SPEC.md,
  AI_ANALYSIS_SPEC.md, DATA_MODEL_SPEC.md, SECURITY_AND_PRIVACY.md,
  ARCHITECTURE.md, IMPLEMENTATION_ROADMAP.md, OPEN_DECISIONS.md
frontend/           React/Vite/TypeScript Persian RTL SPA
PROJECT_STATE.md    derived snapshot of the current state (no independent facts)
```

The frontend has a Persian RTL shell with Vazirmatn font, number/currency helpers, and a typed API client. The active screen is the Salary Estimation Screen (`/`), with the legacy gross-to-net simulation preserved at `/simulation`. See [frontend/README.md](frontend/README.md).

## Development and verification

Dependency installation was approved and performed earlier; backend/.venv exists.

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

### Verify

```powershell
# Backend (Python 3.12+)
cd backend
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m mypy --strict app tests
.\.venv\Scripts\python.exe -m pytest tests/ -v --tb=short

# Frontend (Node 20+)
cd frontend
npx pnpm tsc --noEmit -p tsconfig.app.json
npx pnpm vitest run
npx pnpm vite build
```

The same gates run on every push in `.github/workflows/ci.yml` (hosted CI for the development repository only; it deploys nothing and holds no credential).

## Contributor rules and licence

[AGENTS.md](AGENTS.md) contains the mandatory domain, monetary, security, approval and verification rules. No commit or push is authorized by this README.

[LICENSE](LICENSE) is proprietary, all rights reserved. External redistribution rights are not granted by this repository.
