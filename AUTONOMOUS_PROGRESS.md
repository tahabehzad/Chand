# AUTONOMOUS_PROGRESS — Pish Hesabdari

Persistent engineering log for the autonomous completion mission. If the
session is interrupted, read this file and the git history first.

- **Repository:** `https://github.com/tahabehzad/pish-hesabdari`
- **Working branch:** `autonomous/project-completion`
- **Base commits:** `2fc2b6f` (bootstrap), `eb806e4` (security/database
  baseline), `55eef45` (Decimal money primitives)
- **Authority:** `AGENTS.md`; ADR-008 (product scope: the statutory payroll
  calculation engine on the verified 1404 baseline)

---

## 1. Completed stages

| # | Stage | Commit | Result |
| --: | :--- | :--- | :--- |
| 1 | Repository and uncommitted baseline adopted in three logical commits | `55a9547`, `3ab4c9f`, `abb4ce6` | Backend engine, frontend SPA and the documentation set entered version control; branch pushed to GitHub |
| 2 | Full statutory-engine test suite + the progressive-tax defect fix | `92dc221` | 548 backend tests; a critical tax defect found and corrected |
| 3 | Simulation screen made submittable and truthful | `c42fb9b` | The product's only screen could never be submitted; fixed and covered by 8 new tests |
| 4 | CI workflow for the development repository | (this stage) | `.github/workflows/ci.yml` runs lint, types, tests and the build |

## 2. Bugs discovered and fixed

### 2.1 Critical — the progressive tax ladder was offset by one exemption

- **Where:** `backend/app/engines/tax.py`, `backend/app/engines/eydi.py`,
  `backend/app/engines/rules.py`.
- **Defect:** the engine subtracted the monthly exemption from the taxable
  income and then matched the result against the **absolute** slab edges.
  The seed states the ladder in absolute taxable Rial and its first slab
  *is* the exemption (invariant R-09), so every band sat one whole
  exemption too high and the tax collapsed to zero for any base below the
  first taxable edge.
- **Evidence:** the approved engineering-reference vectors in
  `docs/PISH_HESABDARI_HOLY_BIBLE.md` Appendix A (and ADR-008 directive 4):
  A.4 taxable income 277,920,611.60 → tax **3,792,061**; A.5 taxable income
  377,647,058.87 → tax **17,647,059**. The engine returned **0** for both.
- **Fix:** `StatutoryRuleSet.brackets_above(exemption_rial)` /
  `shift_brackets_by` express the ladder relative to an exemption; the
  reduced base is matched against that ladder. The transformation is exact
  and invertible, and the test suite asserts the equivalence with the
  absolute ladder. The Eydi excess is now taxed across the same shifted
  ladder instead of always at 0 %.
- **Verified:** both reference vectors now reproduce to the Rial; the live
  endpoint returns the corrected figures.

### 2.2 Critical — the simulation screen could never be submitted

- **Where:** `frontend/src/routes/simulation-page.tsx`.
- **Defect:** two independent HTML5 constraint violations blocked the form
  before the request was sent, so the primary button did nothing in any
  browser: the gross field carried `min={1}` with `step={100000}` (the
  seeded 50,000,000 is not `1 + k × 100000`), and the optional liability
  fields were seeded with `0` while the probation field's minimum is one
  month.
- **Fix:** `step="any"` for the Rial fields; an unset optional field is
  empty and is sent as `null`.

### 2.3 High — the client could not read the delivered error envelope

- **Where:** `frontend/src/api/client.ts`, `frontend/src/api/errors.ts`.
- **Defect:** the backend returns `{"error": {"code", "detail"}}`; the
  client only understood a flat `code`, so every refusal was reported as
  the generic `VALIDATION_FAILED` and the categorical code was lost. The
  catalogue still carried the provisional placeholder codes.
- **Fix:** the client reads the nested code and detail; the catalogue
  carries the backend's own codes; the screen shows the Persian explanation
  and the machine code.

### 2.4 High — the loader refused 1405 with the wrong error kind

- **Where:** `backend/app/engines/rules.py`.
- **Defect:** the active-year gate ran before the seed was inspected, so the
  1405 placeholder raised `RuleSetNotActive` and the
  `StatutoryParameterUnavailable` refusal mandated by ADR-008 directive 3
  and by the `P1-T01` acceptance criterion was unreachable.
- **Fix:** the refusal kind now follows the state of the requested year.

### 2.5 Medium — negative monetary input was accepted by three engines

- **Where:** `backend/app/engines/sso.py`, `severance.py`, `eydi.py`,
  `tax.py`.
- **Defect:** a negative base produced a negative statutory figure instead
  of a refusal.
- **Fix:** all four engines now refuse a negative input.

### 2.6 Medium — FastAPI's validation error leaked the rejected input

- **Where:** `backend/app/main.py`.
- **Defect:** the default validation body echoes the rejected value; on this
  endpoint the input is a salary package, so a monetary amount could appear
  inside an error response — the one thing the error contract forbids.
- **Fix:** one handler returns the documented envelope with the field path
  and the failure type only.

### 2.7 Low — engine lint findings and a dead local

- 30 ruff findings in the engine package (ambiguous unicode in docstrings,
  an unused local in the base decomposition, too many positional arguments,
  exception names). All cleared; the exception-name waiver is scoped to the
  catalogue module whose names the specification binds.

## 3. Test results

| Suite | Command | Result |
| :--- | :--- | :--- |
| Backend unit + API | `cd backend && .venv\Scripts\python.exe -m pytest -q` | **548 passed**, 104 skipped (PostgreSQL container unavailable), 16.5 s |
| Backend lint | `.venv\Scripts\python.exe -m ruff check .` | **All checks passed** |
| Backend types | `.venv\Scripts\python.exe -m mypy --strict app tests` | **Success, 62 files** |
| Frontend tests | `cd frontend && node_modules\.bin\vitest.cmd run` | **110 passed** (13 files) |
| Frontend types | `node_modules\.bin\tsc.cmd --noEmit -p tsconfig.app.json` | **PASS** |
| Frontend logical-utility gate | `node scripts\check-logical-utilities.mjs src` | **0 violations** (69 files) |
| Frontend build | `node_modules\.bin\vite.cmd build` | **PASS** |
| Live smoke | `uvicorn app.main:app` + `POST /api/v1/simulations/gross-to-net` | **200** for the 1404 case; **422** with the stable error envelope for 1405, 1403, a negative gross and an unknown field |

## 4. Architectural decisions taken in this mission

| Decision | Rationale |
| :--- | :--- |
| The bracket ladder is shifted by the exemption instead of the base being compared to an absolute ladder | Reproduces both approved reference vectors exactly; the shift is exact and invertible and is asserted by a test |
| The loader's refusal kind depends on the requested year's state | Makes the ADR-008-mandated `StatutoryParameterUnavailable` reachable for 1405 without weakening the refusal |
| One error envelope for every refusal, including request validation | The endpoint's input is a salary package; the envelope must never carry an amount |
| The band rate is carried in the response as a string | The UI must show the applied rate, and a rate may never be a float in JSON |
| The client resolves `globalThis.fetch` per request | A runtime-injected transport must be honoured; it also makes the module-level client testable |
| The screen renders through `formatMoney` / `toPersianDigits` / `formatPercentFromRate` | The project already owns a numeral and money policy; the screen must not re-implement it |
| Hosted CI for the **development** repository only | DEC-F's recorded recommendation (option b); the air-gap constraint applies to the deployed product, and the workflow holds no production credential |
| No net-to-gross inverter | ADR-008 places `P1-T13` out of product scope |

## 5. Remaining tasks

| Item | Status | Note |
| :--- | :--- | :--- |
| `P1-T02` 1405 four-eyes verification | **BLOCKED** | External: primary PDFs and a Certified Tax Accountant. Not producible by an agent |
| `P1-T15` golden vector corpus | **BLOCKED** | External: accountant-signed cases. Not producible by an agent |
| `P1-T03` 1405 activation | Not started | Gated by `P1-T02`; activating 1405 is forbidden while `A1–A8` are unmet |
| `P1-T13` net-to-gross inverter | Out of scope | ADR-008 |
| `P1-T17`, `P1-T18` benchmarking | Out of scope | ADR-008 |
| `P0-T14`, `P0-T15`, `P0-T16` isolation, crypto and backup suites | Partly blocked | The PostgreSQL container image cannot be pulled in this environment, so 104 integration tests self-skip |
| `P0-T18` session and MFA | Not started | Blocked on the unapproved session contract (DEC-010 area) |
| `P0-T19` full 13-stage CI pipeline | Partly done | The lint/type/test/build stages are running; the security, isolation, restore and golden stages are not |
| Independent review of the monetary changes | **Required** | AGENTS.md §6: a security-sensitive or financial change needs review by someone who did not write it. The engine changes in this mission are therefore `READY_FOR_REVIEW`, not `APPROVED` |

## 6. Blocked tasks

- **PostgreSQL integration suites** — the official container image cannot be
  pulled in this environment; the tests skip themselves and report the
  skip rather than passing silently.
- **`gh` CLI authentication** — the stored token is invalid, but the git
  credential helper can push to the remote, so every commit is published
  through git. `gh auth refresh -h github.com` restores the CLI.
- **1405 activation and the certified corpus** — need human legal and
  accounting signatures.

## 7. Known risks

1. **The engine's numbers are engineering-reference, not certified.** They
   reproduce the Holy Bible Appendix A vectors and the ADR-008
   engineering-reference expectations, but no Certified Tax Accountant has
   signed them (`P1-T15` is blocked).
2. **The two Article 137 postures are coupled to the welfare treatment**
   (ADR-008 / DEC-002a): `conservative_inta` taxes the welfare allowances
   and deducts 2/7 of the employee share; `court_precedent` exempts them
   and deducts the whole share. The Appendix A reference vector uses a
   *mixed* combination (welfare taxable with the full deduction), so it
   validates the ladder arithmetic rather than one engine posture.
3. **The Eydi payout tax is modelled with the monthly salary ladder**
   applied to the annual excess above the exemption. The corpus specifies
   "the excess is taxed across the progressive salary brackets" without
   fixing the annualisation; the model is explicit and tested, but it is a
   modelling decision, not a certified one.
4. **No authentication exists.** The endpoint is unauthenticated by design
   (ADR-008's minimal scope); it must not be exposed publicly.
5. **The CI workflow has never run on GitHub** — `gh` cannot be used to
   watch it; the first push of the workflow file triggers it.

## 8. How to run the project

```powershell
# Backend (Python 3.12+)
cd backend
uv sync --frozen --all-groups
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000

# Backend gates
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m mypy --strict app tests
.\.venv\Scripts\python.exe -m pytest -q

# Frontend (Node 20+)
cd frontend
corepack enable
pnpm install --frozen-lockfile
pnpm dev            # http://localhost:5173
pnpm lint && pnpm typecheck && pnpm test && pnpm build
```

The simulation endpoint is `POST /api/v1/simulations/gross-to-net`; the
frontend talks to it through `VITE_API_BASE_URL` (see
`frontend/.env.example`).
