# Agent Guide — Pish-Hesabdari

- **Document ID:** `DOC-AGENT-001`
- **Status:** Active operating guide for AI agents and new contributors. `AGENTS.md` remains **binding**; this guide explains how to apply it to the current repository.
- **Audience:** an agent starting a task with no prior context.

---

## 1. Read order

Read only what the task needs (`AGENTS.md §13`), but read it in this order:

| # | Read | Why |
| --: | :--- | :--- |
| 1 | `AGENTS.md` | Binding invariants: money, security, statuses, escalation |
| 2 | `docs/PROJECT_BIBLE.md` §1–§7 and §14–§17 | Product identity, principles, reuse map, legal boundaries |
| 3 | `docs/CURRENT_STATE.md` §1 (verification record) and the rows for your capability | What is actually verified, with evidence |
| 4 | `docs/MVP_SCOPE.md` + `docs/MVP_WBS.md` — **only if the task is the five-hour MVP** | Scope, acceptance criteria, budget |
| 5 | `docs/ARCHITECTURE.md` §2–§5 (existing) and §6–§9 (proposed) | Boundaries; never confuse the two halves |
| 6 | `docs/DECISIONS.md` | PB-\* status before you implement a product behaviour |
| 7 | `docs/DECISIONS_REGISTER.md` (the entry your task names) + the relevant ADR | Statutory/legal constraints |
| 8 | `docs/EXECUTION_PLAN.md §14.3` row for the historical task | Dependencies, acceptance criteria, current status |
| 9 | `docs/specs/TESTING.md` §3–§4, §16 | Tooling and what counts as a failure |
| 10 | `docs/DOCUMENTATION_INDEX.md §0` | Which document owns which fact |

Do **not** load the whole Holy Bible, the research corpus, the WBS or the changelog by default.

## 2. Hard rules (restated because they are violated most often)

1. **No product behaviour without a decision.** SCORE, weights, approval flow, persistence or authentication must trace to a `CONFIRMED` PB-D entry or an accepted ADR. If it is `OPEN`, stop and record the question.
2. **Money:** integer Rial in JSON; `Decimal` only; `prec = 34`; `ROUND_HALF_UP`; no float literal, no `round()` on money, no `float()` conversion (`AGENTS.md §2.7`). Scores and rates are published as **strings**.
3. **Never weaken a money or security assertion** to make a test pass. A failing money-path test is a defect.
4. **No secrets, no real PII.** Never read or print `.env`, `.secrets/`, tokens, keys. Fixtures are synthetic. Never log national IDs, mobiles, Sheba or real salaries.
5. **Do not modify** ADR-001…004, `backend/data/seeds/statutory_rules_1404.yaml`, the roadmap in REMEDIATED §7, or accepted decisions. A change needs a superseding ADR.
6. **Do not commit, push, reset or clean** without explicit instruction. Preserve uncommitted work (there is some — see `docs/CURRENT_STATE.md §3`).
7. **No new dependency** without a stated, task-specific need (PB-D13).
8. **Do not fake a security control.** No "presentation-only" login presented as authentication; no client-side route guard implying a session that does not exist.
9. **One owner per file.** Never let two agents edit the same file; partition or use worktrees (`AGENTS.md §6`).
10. **A prototype is labelled.** Anything built under the five-hour scope says so in the UI and in its response payload.

## 3. Commands (verified on this host)

Run from the repository root. Bash syntax (Git Bash on Windows).

### Backend

```bash
cd backend
.venv/Scripts/python.exe -m pytest -q                      # 735 passed, 1 skipped (this host, 2026-11-16)
.venv/Scripts/python.exe -m pytest tests/unit/test_x.py -q # narrow first
.venv/Scripts/python.exe -m ruff check .
.venv/Scripts/python.exe -m mypy --strict app tests
```

- `pytest` collects `tests/` (unit, api, property, integration). Integration tests start **disposable PostgreSQL 16 containers**; they need Docker (available here, 29.9.2) and take ~20 s.
- Sequential runs on Windows: avoid running the same DB-backed test in two shells at once.

### Frontend

`pnpm` is **not on `PATH`** on this host (although `package.json` declares `pnpm@9.15.9`). Use the binaries directly; do not install anything globally:

```bash
cd frontend
./node_modules/.bin/vitest run          # 115 passed
./node_modules/.bin/tsc -p tsconfig.app.json --noEmit
node scripts/check-logical-utilities.mjs src
./node_modules/.bin/vite build
```

If `pnpm` is available elsewhere, the documented scripts are `pnpm typecheck|test|lint|build`.

### Run locally (when a task actually needs a live server)

```bash
cd backend && .venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
cd frontend && ./node_modules/.bin/vite --host 127.0.0.1 --port 5273
```

Bind to `127.0.0.1` only. The prototype has no authentication.

## 4. Known tooling traps

| Trap | Fact | What to do |
| :--- | :--- | :--- |
| `tsc -b` fails | `vite.config.ts` uses `vite`'s `defineConfig` with a `test` key and `tsconfig.node.json` lacks vitest types → TS2769 | Use the documented `tsc -p tsconfig.app.json` gate; do not "fix" the config as a side effect of an unrelated task |
| `pnpm` missing | Not installed on this host | `node_modules/.bin/*` or `npx --yes pnpm@9 …` |
| Docs disagree with code | 11 recorded conflicts in `docs/CURRENT_STATE.md §4` | Trust the tree; cite the conflict; never edit a status to match a document |
| Engine version | Code says `0.2.0-payroll-engine`; `PROJECT_STATUS §2` says `0.3.0` | Read `app/engines/__init__.py`; do not bump silently |
| Test counts in docs | Stale (678/105, 86 tasks, 110 tests) | Use `docs/CURRENT_STATE.md §1` |
| Orphan dev chunk | `dist/` can contain `dev-preview` fixture code | Do not treat the built bundle as proof a route is unreachable |
| Persian digits | Display only; machine layer is ASCII | Never put Persian numerals in JSON, ids or tests |

## 5. Architecture boundaries

```
api/  →  schemas/  →  services/  →  engines/
                                    ↑ pure: no clock, no network, no env, no ORM
```

- `engines/**` must stay pure and Decimal-only. `generated_at` is injected at the API boundary.
- No API route currently opens a database session. If a task needs persistence, it needs a **new** design decision, a migration with `tenant_id` + policy + `FORCE ROW LEVEL SECURITY`, and a recorded decision — not an ad-hoc `Session`.
- New prototype code belongs in `backend/app/prototype/` and `frontend/src/routes/prototype/`, registered only under the local-environment gate.
- Frontend: no financial calculation in the browser; displayed values must equal the API response byte-for-byte. Use the logical-utility gate (no `ml-4`, no `left-0`); use the existing `components/ui` primitives; no new UI or state library.

## 6. Avoid duplicate implementations

Before writing code, check the reuse map (`docs/PROJECT_BIBLE.md §14`):

| If you need… | Call this, do not rewrite it |
| :--- | :--- |
| Rounding / Rial quantisation | `app/engines/money.py` |
| Net, SSO, tax, employer cost of a gross | `app/services/payroll_service.compute_gross_to_net` |
| Band position from a score | `app/engines/valuation.propose_gross_range` |
| Error codes and envelope | `app/engines/errors.py`, pattern in `app/api/v1/payroll.py` |
| Canonical JSON + SHA-256 provenance | `payroll_service` / `valuation_service` pattern |
| Persian numerals, money formatting | `frontend/src/lib/*` |
| RTL primitives, loading/empty/error states | `frontend/src/components/ui/*` |
| Contract availability honesty | `frontend/src/api/contracts.ts` |

A second implementation of tax, insurance or money is a defect even if it passes tests.

## 7. How to record work

| What happened | Where it goes |
| :--- | :--- |
| A command was run and observed | Append to `docs/CURRENT_STATE.md §1` (prototype/product work) or `docs/BOOTSTRAP_CHANGELOG.md` (statutory/security work, with the existing entry style) — never overwrite history |
| A new product/architecture question | Add `PB-Dxx` to `docs/DECISIONS.md` with status and consequences |
| A statutory/legal question | `docs/DECISIONS_REGISTER.md` (DEC-xxx), not `DECISIONS.md` |
| A product-scope change | Proposal in `docs/DECISION_REQUIRED_FROM_OWNER.md` **plus** a superseding ADR; never edit ADR-008 in place |
| A historical task status change | `docs/EXECUTION_PLAN.md §14.3` **with** evidence and a recorded explanation; never to bypass a blocker |
| A new user-facing capability | `docs/PROJECT_BIBLE.md` FR row + `docs/ARCHITECTURE.md` if the boundary changes |

Do not create a new Markdown document for a fact that already has an owner (`AGENTS.md §14`).

## 8. Reporting incomplete work

Every final report must separate:

- **Observed** — command, exit status, exact counts (e.g. "`pytest -q`: 735 passed, 1 skipped, exit 0").
- **Not run** — and why (no Docker, no server, no credential).
- **Written but unobserved** — code exists, no execution evidence.
- **Blocked** — the decision or external artefact needed.

Forbidden: "all tests pass" without a run; "authentication is implemented" when a page is presentation-only; "production ready"; silently skipping a failing money test; reporting a plan as a result.

## 9. Five-hour session discipline

When the task is the MVP:

1. Work `docs/MVP_WBS.md` in order; keep the 300-minute budget in view.
2. Optional work (`MVP-07` CSV) is cut before any essential task.
3. Re-run only the checks your change affects (`AGENTS.md §13.5`), then the full gates once at the end.
4. If time runs out mid-phase, stop and report: last completed task, first incomplete task, observed failures. Do not widen scope to "finish" the demo.
5. Record the outcome in `docs/CURRENT_STATE.md` before ending the session.

## 10. Escalation triggers

Stop and escalate when:

- a task requires a behaviour whose PB-D status is `OPEN`;
- a statutory value is missing (never estimate);
- a money-path test fails (defect, not quarantine);
- a security control would be implied but not implemented;
- a change would touch an accepted ADR, the 1404 seed or the roadmap;
- two documents contradict each other on a fact you must rely on (log it in `docs/CURRENT_STATE.md §4`, then proceed on the code evidence and say so).
