# Architecture — Existing and Proposed

- **Document ID:** `DOC-ARCH-001`
- **Status:** Mixed document. §2–§5 describe **what exists and was verified**. §6–§10 describe a **proposed MVP that does not exist yet**. Every proposed element is marked `[PROPOSED]`.
- **Governing decisions:** accepted ADRs in `docs/adr/`; `AGENTS.md §2` invariants. Product-scope proposals: `docs/DECISIONS.md`.

---

## 1. Architectural position today

The repository is a **modular monolith** (ADR-001): one FastAPI process, one React SPA, one PostgreSQL instance, no queue, no worker, no cache. The calculation path is pure and synchronous; the database is used by migrations, verification and tests, **not** by any HTTP request.

That is a strong base for the new product's calculation layer and a weak base for its data layer: there is no person record, no persistence in the request path and no authenticated actor.

## 2. Existing back-end structure (verified)

| Layer | Modules | Responsibility |
| :--- | :--- | :--- |
| HTTP | `app/main.py`, `app/api/v1/payroll.py`, `app/api/v1/valuation.py` | 3 routes, CORS, correlation id, one error envelope |
| Contracts | `app/schemas/payroll.py`, `app/schemas/valuation.py` | Pydantic v2; integer Rial; rates/scores as strings; `extra="forbid"` |
| Composition | `app/services/payroll_service.py`, `app/services/valuation_service.py` | Orchestrate engines, build provenance, hash the payload |
| Domain | `app/engines/*` | Pure Decimal arithmetic; no clock, network or environment |
| Security | `app/core/security/*` | AES-256-GCM transformer, HMAC blind index, tenant context |
| Persistence | `app/models/*`, `alembic/versions/0001…0003` | 5 global statutory tables + 7 identity tables + tenant-context functions |
| Storage | `app/storage/s3_adapter.py` | S3/GOVERNANCE adapter (no live acceptance) |

**Dependency direction (enforced by convention):** `api → schemas → services → engines`; engines import nothing from `api`, `services` or `models`. Any new feature must keep this direction.

## 3. Existing data flow — statutory simulation

```
client JSON (integer Rial)
  → GrossToNetRequest (pydantic, extra=forbid)
  → _to_payroll_input()                    api/v1/payroll.py
  → compute_gross_to_net(PayrollInput)     services/payroll_service.py
       → load_rule_set(1404)               engines/rules.py   (fail-closed)
       → bases → sso → tax(dual posture) → overtime → severance → eydi → ctc
       → termination (scenario)            engines/*.py       (pure Decimal)
       → provenance map + residual + SHA-256 canonical JSON
  → PayrollResponse + generated_at         (clock read only here)
```

## 4. Existing data flow — advisory proposal

```
profile + manager band (no performance data)
  → ValuationInput
  → assess_profile()            engines/valuation.py  (experience 35 / relevant 25 / skill 30 / education 10)
  → propose_gross_range()       band position + ±5 % range
  → compute_gross_to_net() ×3   low / point / high  (statutory costing, advisory only)
  → payload with advisory:true, statutory:false, model_version, engine_version, hash
```

**This is not performance evaluation.** It scores a profile, not contribution, and it uses no observations.

## 5. Existing persistence (verified)

| Migration | Contents | State |
| :--- | :--- | :--- |
| `0001_statutory_baseline.py` | 5 global statutory tables; `ENABLE`+`FORCE ROW LEVEL SECURITY`; reader/reviewer grants; `statutory_identity_write_gate()` trigger | Verified by 42 integration tests |
| `0002_identity_foundation.py` | `organizations`, `users`, `roles`, `permissions`, `role_permissions`, `organization_memberships`, `sessions`; 7-role seed; deferred `users(id)` actor FKs with `ON DELETE RESTRICT`; replaces the temporary write gate | Implemented; WBS still says `NOT_STARTED` |
| `0003_tenant_context.py` | `set_tenant_context(uuid)` (transaction-local GUC), `current_tenant_id()` raising SQLSTATE `55000`, `pish_tenant_rls_violation()` | Verified fail-closed |

**No table holds a person, an observation, an evaluation or a recommendation.** No API request opens a session.

## 6. Proposed MVP architecture `[PROPOSED]`

```
backend/app/prototype/                    [PROPOSED, new package]
  __init__.py        exposes the router + a store factory
  models.py          Person, Observation, ImportBatch, EvaluationRun,
                     CriterionResult, Recommendation, Decision  (dataclasses)
  store.py           InMemoryStore behind a Repository Protocol; reset() for tests
  rules.py           perf-v1: criteria, normalisation, weights, missing-data policy
  scoring.py         deterministic score + per-criterion contributions
  recommendation.py  band placement, suggested gross, delta, statutory costing call
  api.py             APIRouter(prefix="/api/v1/prototype"), environment-gated
```

`app/main.py` registers `prototype.api.router` **only** when `APP_ENV` is local (PB-D11). Existing routers are untouched.

```
frontend/src/routes/prototype/            [PROPOSED]
  dashboard-page.tsx        counts + prototype banner
  people-page.tsx           create/list
  observations-page.tsx     manual entry + review/correct/reject
  recommendation-page.tsx   score breakdown, explanation, approve/edit/reject
frontend/src/api/prototype.ts             [PROPOSED] typed client (no new library)
```

Routes are added **under the existing `AppShell`**, after `/system`, and the contract registry (`src/api/contracts.ts`) gains `delivered` entries with owner `MVP-*` — never `awaiting-backend` fakes.

## 7. Evaluation pipeline `[PROPOSED]`

```
observations (valid, non-rejected, one person, one period)
   → normalise per criterion (bounds published in perf-v1)
   → missing? → apply published policy, record in missing_criteria
   → contribution_i = normalised_i × weight_i          (Decimal, prec 34)
   → score = Σ contributions × 100                     (ROUND_HALF_UP at the boundary)
   → EvaluationRun {rule_set_version, inputs used, contributions, score, hash}
```

Invariants carried over from the statutory engine: no float, no clock, no randomness, no network, one rounding boundary per emitted figure, and an explicit refusal code instead of a default.

## 8. Recommendation pipeline `[PROPOSED]`

```
EvaluationRun + band(min,max) + current gross (optional)
   → position = score_fraction
   → suggested_gross = min + position × width            (reuse band logic from valuation.py)
   → delta = suggested − current
   → statutory costing = compute_gross_to_net(suggested) (advisory only)
   → Recommendation {score, breakdown, observations_used, weights, versions,
                     suggested, delta, net, employer_cost, hash, advisory:true}
   → manager decision {approve|edit|reject, comment, timestamp}
```

An edit stores the original suggestion, the edited amount and the reason; the hash of the original is retained.

## 9. Proposed domain entities `[PROPOSED]`

| Entity | Key fields | Relationship |
| :--- | :--- | :--- |
| `person` | `person_id`, display name, role label, start date, external ref (optional), created_at | 1→N observations, evaluations, recommendations |
| `observation` | `observation_id`, person_id, period, metric_code, raw_value, unit, source, import_batch_id, state(valid/corrected/rejected) | N→1 person |
| `import_batch` | batch_id, source_kind, file name/hash, row counts, errors | 1→N observations |
| `evaluation_rule_set` | version, criteria, weights, normalisation, missing policy | referenced by runs |
| `evaluation_run` | run_id, person_id, period, rule_set_version, score, contributions, inputs_digest, hash, created_at | N→1 person |
| `recommendation` | recommendation_id, run_id, band, suggested, delta, statutory block, hash, state | 1→1 run |
| `decision` | decision_id, recommendation_id, action, edited_amount, comment, decided_at | N→1 recommendation |

**Not present today.** When these become persistent, the first migration that creates a tenant-owned table must add `tenant_id`, its policy and `FORCE ROW LEVEL SECURITY` in the same migration (`AGENTS.md §2.12`), and `pish_tenant_rls_violation()` must stay clean.

## 10. API boundaries

| Boundary | Existing | Proposed |
| :--- | :--- | :--- |
| Public surface | `/health/live`, 2 POST endpoints | + `/api/v1/prototype/*`, environment-gated |
| Auth | none | none in MVP; the gate is *local-only*, not security |
| Validation | pydantic `extra="forbid"` | same |
| Errors | `{"error":{"code","detail"}}` | same, no echoed money |
| Money format | integer Rial; rates/scores strings | same |
| Provenance | rule/engine versions + hash + generated_at | + `rule_set_version` of `perf-v1` |
| Persistence | none in request path | in-memory for MVP; PostgreSQL later |

## 11. Reusable components (do not duplicate)

`app/engines/money.py` (rounding), `app/services/payroll_service.compute_gross_to_net` (costing), `app/engines/valuation.propose_gross_range` (band placement), `app/engines/errors.py` (taxonomy), `app/api/v1/payroll.py` (error/response pattern), `frontend/src/lib/*` (numerals, money), `frontend/src/components/ui/*` (RTL primitives), `frontend/src/api/client.ts` (client, correlation id).

## 12. Architectural risks

| # | Risk | Impact | Mitigation |
| --: | :--- | :--- | :--- |
| AR-1 | **Product-scope conflict**: ADR-008 limits the product to statutory payroll; `DEC-014` marks these modules `OPEN — BLOCKING` | Building the MVP without an ADR erodes the accepted boundary | Prototype labelled, loopback-only, no production claims; PB-D01 raised for owner |
| AR-2 | **Person identity matching** across sources | Silent merging of two people corrupts pay decisions | No auto-merge in MVP; matching is a later, human-confirmed feature (PB-D05) |
| AR-3 | **No persistence** in the MVP | Data lost on restart; no history | Repository protocol now, PostgreSQL behind it later (PB-D06) |
| AR-4 | **No authentication** | Any local process can read/write prototype data | Loopback + environment gate; no LAN/Internet exposure; PB-D09 |
| AR-5 | **Provisional weights** become de-facto policy | Unjustified pay decisions | Versioned rule set, `provisional` flag in payload and UI (PB-D03) |
| AR-6 | **Statutory engine status** (review-ready, 1404-only, no legal sign-off) | A costing is mistaken for lawful payroll | `advisory/statutory` flags, `advisory_notes`, explicit UI copy |
| AR-7 | Re-implementing tax/SSO "just for the MVP" | Two sources of financial truth | Mandatory reuse of `compute_gross_to_net`; a review check on the diff |
| AR-8 | Prototype code becoming production by inertia | Unauthenticated endpoints in a real deployment | Gate defaults to off; `docs/MVP_SCOPE.md §4` exclusions; backlog entry BL-01 |
| AR-9 | Front-end budget (10–20 min per screen) | Demo only reachable via API | Minimal screens; scripted HTTP walkthrough as fallback, stated honestly |
| AR-10 | Two score models coexist (`valuation-v1`, `perf-v1`) | Manager confusion | Different names, versions and purposes; the recommendation states which model produced it |

## 13. What must exist before this architecture can be called production

Authentication and sessions (`P0-T18`) · audit ledger (`P0-T10`) · key management (`P0-T08`) · tenant tables with RLS (`P0-T09`/`P0-T14`) · PostgreSQL persistence for the new entities · backup/PITR (`P0-T16`/`P4-T03`) · CI execution · independent review · legal/accounting sign-off. None exists today.
