# Pish Hesabdari (پیش‌حسابداری) — Project Summary for Agent Handoff

> **Historical snapshot — do not load for current state.** This file records the phase-1
> agent handoff. Current state is owned by [`PROJECT_STATE.md`](PROJECT_STATE.md) (orientation),
> [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md) (delivery), [`docs/EXECUTION_PLAN.md`](docs/EXECUTION_PLAN.md)
> §14.3 (tasks) and [`docs/BOOTSTRAP_CHANGELOG.md`](docs/BOOTSTRAP_CHANGELOG.md) (verification).
> Retained for traceability only; where it disagrees with an owner, the owner is correct.

## Overview
**Statutory Iranian Payroll Calculation Engine** — Pure functions + minimal FastAPI endpoint on verified 1404 SH baseline.
- **Product scope (ADR-008):** SSO insurance, progressive income tax (Art. 137 dual posture), net pay, overtime/night-shift, Sanavat (severance), Eydi (annual bonus), employer CTC, Article 11 worst-case termination liability.
- **Rule set:** 1404 SH verified/active (`statutory_rules_1404.yaml`, SHA-256 `CA16C455...`). 1405 transcribed but INACTIVE (null params, A1–A8 unmet).
- **Stack:** Python 3.12+ / FastAPI / SQLAlchemy / Alembic / uv / React 19 / TypeScript / Vite / Tailwind / TanStack Query.

---

## Architecture (Modular Monolith)

```
backend/
├── app/
│   ├── engines/           # Pure calculation engines (no I/O, no clock)
│   │   ├── money.py       # Decimal primitives: prec=34, ROUND_HALF_UP, quantize_rial, reconcile_lines
│   │   ├── rules.py       # Fail-closed rule-set loader (only 1404 loads)
│   │   ├── bases.py       # Mozd-e Mabna / Saabet decomposition (Art. 36 Note 3, Precedent 3328)
│   │   ├── sso.py         # SSO: employee 7%, employer 20%, unemployment 3% (capped)
│   │   ├── tax.py         # Progressive tax + Art. 137 dual posture (DEC-002a binding)
│   │   ├── overtime.py    # Overtime 1.40×, night 1.35× on Saabet base
│   │   ├── severance.py   # Sanavat: Saabet ÷ 12 monthly accrual
│   │   ├── eydi.py        # Eydi: min(2×Saabet, 3×min_wage), progressive payout tax
│   │   ├── ctc.py         # Employer CTC identity (exact integer addition)
│   │   ├── termination.py # Art. 11 worst-case + leave buyout + exit severance
│   │   └── errors.py      # Categorical error codes (never amounts/secrets)
│   ├── services/
│   │   └── payroll_service.py  # Composition: compute_gross_to_net (pure, hashed)
│   ├── api/v1/payroll.py       # POST /api/v1/simulations/gross-to-net
│   ├── schemas/payroll.py      # Pydantic v2 contracts (int Rial, string rates)
│   ├── models/statutory.py     # SQLAlchemy statutory tables (RLS, append-only sigs)
│   └── main.py                 # FastAPI app, router registered, /health/live
├── alembic/                    # P0-T04 migration (5 global tables, FORCE RLS)
├── data/seeds/statutory_rules_1404.yaml
└── tests/                      # 548 passing (unit, API and property); 104 PG integration self-skip without the image
```

**Frontend:**
```
frontend/
├── src/
│   ├── app/router.tsx          # React Router v6, lazy routes, Suspense
│   ├── routes/
│   │   ├── simulation-page.tsx # Full gross-to-net UI (delivered endpoint)
│   │   ├── overview-page.tsx   # MVP 0.1 demo dashboard
│   │   └── modules.tsx         # Placeholder pages for pending endpoints
│   ├── api/
│   │   ├── client.ts           # Typed fetch wrapper, correlation-id, error shape
│   │   ├── contracts.ts        # Contract registry (delivered/awaiting-backend)
│   │   ├── payroll-types.ts    # TS types mirroring backend schema
│   │   └── query-client.ts     # TanStack Query config (no 4xx retry)
│   ├── components/ui/          # RTL primitives (Input, Card, Badge, Button, Icon)
│   └── lib/                    # Persian numerals, Vazirmatn, Jalali calendar
```

---

## Financial Integrity Invariants (Non-Negotiable)
1. **Decimal only** in `engines/**` — no float literals; `getcontext().prec=34`, `ROUND_HALF_UP`.
2. **Round once** at line-item boundary; surface signed `rounding_residual_rial` (≤1 Rial/line).
3. **Every emitted figure** carries: `rule_version`, `rule_set_status`, `engine_version`, `calculation_hash`, `generated_at`, per-field provenance.
4. **Unknown statutory values** → `StatutoryParameterUnavailable` (never coerce null→0).
5. **Pure function** of `(inputs, rule_set_version)` — no clock, randomness, network, env reads in calc path.

---

## Current Delivery Status (2026-11-15)

| Dimension | State |
|-----------|-------|
| **Calculation Engines** | **Complete** — all 9 engines implemented, tested, exported, typed |
| **API Endpoint** | **Delivered** — `POST /api/v1/simulations/gross-to-net` (dual Art. 137 posture) |
| **Frontend Simulation Page** | **Complete** — RTL form, Persian numerals, results cards, Art. 11 liability |
| **Database Migration (P0-T04)** | **READY_FOR_REVIEW** — 5 global tables, FORCE RLS, reader/reviewer roles, write gate; 101 PG integration tests pass locally; CI/production pending |
| **Backend Tests** | **548 passing** (342 unit/API, 102 new engine unit/API, 104 property); 104 integration self-skip without the container image |
| **Frontend Tests** | **110 passing** (typecheck, lint, build all pass) |
| **CI/CD** | **None** (DEC-F open) |
| **Auth/Identity (P0-T05)** | **BLOCKED** — depends on P0-T04 FK validation |
| **Official Source Acquisition (P1-T02)** | **BLOCKED** — all 6 probes failed (403/transport) |
| **Phase Gates Passed** | **0 of 5** |

---

## How to Run Locally

```powershell
# Backend
cd backend
.venv\Scripts\python.exe -B -m uvicorn app.main:app --host 127.0.0.1 --port 8000
# → GET /health/live = 200 {"status":"alive"}
# → POST /api/v1/simulations/gross-to-net (see schema below)

# Frontend
cd frontend
pnpm dev -- --host 127.0.0.1 --port 5173
# → http://127.0.0.1:5173/simulation

# Tests
cd backend; .venv\Scripts\python.exe -B -m pytest -q
cd backend; .venv\Scripts\python.exe -B -m mypy --no-incremental app tests
cd frontend; pnpm typecheck && pnpm lint && pnpm test && pnpm build
```

---

## API Contract (Delivered)

**POST `/api/v1/simulations/gross-to-net`**

Request (all monetary fields = integer Rial):
```json
{
  "gross_monthly_rial": 50000000,
  "rule_year": 1404,
  "days_in_month": 30,
  "tax_posture": "conservative_inta",
  "allowances": {
    "housing": 9000000,
    "grocery": 4500000,
    "marriage": 3000000,
    "child": 6000000,
    "continuous_attraction": 0
  },
  "overtime_hours": 0,
  "night_hours": 0,
  "continuous_attraction_taxable": false,
  "probation_months": null,
  "tenure_months": null,
  "accumulated_unused_leave_days": null,
  "probation_days_worked": null
}
```

Response includes:
- `tax_postures`: both `conservative_inta` and `court_precedent` with `art137_deduction_rial`, `welfare_allowances_taxable`, `taxable_income_rial`, `income_tax_rial`, `slab_breakdown`, `net_rial`
- `net_rial` (primary posture), `alternate_posture_net_rial`
- `employee_deductions`, `severance_sanavat`, `eydi`, `employer_cost`
- `termination_liability` (if probation_months provided)
- `rounding_residual_rial`, `calculation_hash`, full `provenance` map

Error shape (never amounts/secrets):
```json
{ "error": { "code": "PAYROLL_INPUT_INVALID|STATUTORY_PARAMETER_UNAVAILABLE|...", "detail": "..." } }
```

---

## Key Decisions (ADRs)

| ADR | Status | Summary |
|-----|--------|---------|
| ADR-001 | Accepted | Modular monolith, sync fast path, async boundary undecided |
| ADR-002 | Accepted | AES-256-GCM field encryption, HMAC-SHA256 blind index, no pgcrypto |
| ADR-006 | Accepted | ADR-005 (BackgroundTasks) superseded; JobQueue interface only |
| ADR-007 | Accepted | P0-T04: 5 global tables, FORCE RLS, restricted reader/reviewer, deferred user FKs |
| ADR-008 | Accepted | Product scope = statutory payroll engine only (supersedes ADR-004 module list) |

---

## Outstanding Blockers (Require Owner Decision)

1. **DEC-F** — CI/CD provider and pipeline config
2. **P0-T05** — Identity schema (User table, validated FKs for statutory write gate)
3. **P1-T02** — Official statutory source access (all probes failed; need legal PDF acquisition path)
4. **1405 Activation** — A1–A8 unmet; requires certified legal sign-off
5. **Benchmark Data (DEC-007)** — No licensed corpus for market bands

---

## Files Added/Modified in This Session

**Backend:**
- `app/engines/__init__.py` — Full exports for all engines
- `app/services/__init__.py` — Export payroll service
- `app/engines/tax.py` — Export `TaxBracket`
- `app/engines/rules.py` — Fix `yaml.ScalarNode` type
- `app/api/v1/payroll.py` — Map schema `AllowancesInput` → engine `Allowances`

**Frontend:**
- `src/routes/simulation-page.tsx` — Complete simulation UI
- `src/api/payroll-types.ts` — TypeScript contracts
- `src/api/contracts.ts` — `grossToNet` marked delivered
- `src/app/router.tsx` — Route to real simulation page
- `src/routes/modules.tsx` — Removed placeholder SimulationPage
- `src/api/contracts.test.ts` — Updated test expectation

---

## Next Steps (If Continuing)

1. **Mock Employee Context Endpoint** — `GET /api/v1/employees/{id}/payroll-context?period=1404-08` to feed simulation page from real data
2. **Employee/Period Selector Page** — Dropdown → redirects to `/simulation` with prefilled context
3. **P0-T04 CI Integration** — GitHub Actions + testcontainers for PG migration tests
4. **P0-T05 Identity Models** — User table, session strategy, key hierarchy
5. **PDF Export** — WeasyPrint/Chromium pipeline for legal payslip (Vazirmatn, Arabic reshaper, bidi)

---

## References
- `docs/PISH_HESABDARI_HOLY_BIBLE.md` — Authority (§0.3, §13.1, §13.8, §2 terminology)
- `docs/EXECUTION_PLAN.md` — WBS (§14.3), API design (§7), financial rules (§7.2)
- `docs/ADR_INDEX.md` — All ADRs
- `docs/BOOTSTRAP_CHANGELOG.md` — Evidence log (§16–§22)
- `docs/PROJECT_STATUS.md` — Current state (§2)
- `docs/specs/STATUTORY_DATABASE_CONTRACT.md` — DB contract rev3