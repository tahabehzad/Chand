# AUTONOMOUS_PROGRESS — Pish Hesabdari

Persistent progress record for the autonomous completion run (owner directive:
take the project from its current state to full completion, Holy Bible v1.0.7
as the primary context document).

| Field | Value |
| :--- | :--- |
| Updated | 2026-11-16 (25 Aban 1405 SH) |
| Branch | `autonomous/project-completion` (HEAD `f31e01e`; no commit or push was made by any pass recorded here — the §24 set was committed later under an explicit owner instruction, the Batch-01 set below is uncommitted) |
| Authority | `docs/PISH_HESABDARI_HOLY_BIBLE.md` v1.0.7 · `AGENTS.md` §2 · ADR-006/007/008 (Accepted) |
| Product boundary | ADR-008 v1: statutory payroll engine (SSO, progressive tax, net, overtime/night, Sanavat, Eydi, CTC, Art. 11) + one minimal endpoint on the verified 1404 baseline |
| Active statutory baseline | 1404 SH (`1404.1`, VERIFIED/ACTIVE). 1405 stays transcribed, unverified, inactive. |

---

## 1. Verified baseline at the start of the remediation pass

| Check | Command | Result |
| :--- | :--- | :--- |
| Backend tests | `backend\.venv\Scripts\python.exe -m pytest -q` | **FAIL at collection** — `tests/api/test_openapi_contract.py` rejected FastAPI's OpenAPI 3.1.0 document (`schemathesis` 3.39.16) |
| Ruff | `python -m ruff check .` | not run before the fixes (collection stopped the suite) |
| Docker/PostgreSQL | `docker version` | daemon unavailable → 104 integration tests self-skip |

## 2. Findings verified against the current code

Every finding was re-verified before editing; documentation claims were not
treated as proof.

| ID | Verified defect | Remediation |
| :--- | :--- | :--- |
| A-1 | The signed residual compared `total_gross - net` with the same deduction lines (an identity that can never fail); the published tax total did not equal the sum of its rounded slab lines | Residual is now `sum(rounded deduction lines) - round(exact deduction total)`; the published tax total is the sum of rounded slab lines and the exact total plus the signed residual are published per posture |
| A-2 | Provenance covered only seven block keys, so most emitted figures had no traceable rule | Per-field provenance keyed by JSON path (bases, SSO, both postures, every slab line, severance, Eydi, employer cost, termination, reference block); block keys retained for compatibility |
| A-3 | Termination added the employer-initiated probation line, the employee-initiated line and the separation lines into one total | Explicit `TerminationScenario`; one probation line applies; `applied_probation_liability_rial` + `total_separation_rial` reconcile to `total_liability_rial` |
| A-4 | The leave-buyout daily wage was `Mozd-e Saabet / days_in_month`, so a 31-day month changed the Art. 71 value | `STATUTORY_DAILY_WAGE_DIVISOR_DAYS = 30`; divisor published in the block |
| A-5 | `test_the_exact_decimal_base_is_used_for_the_article_137_deduction` compared the line with `(rounded + 1) × 2/7` under ±1 Rial, so either base passed | Fixture chosen so rounding the SSO share first changes the deduction by 1 Rial; the test asserts the exact value and the discriminating fixture |
| A-6 | Float division (`/ 12`) and Python `round()` in the Eydi and property tests | Decimal division + `ROUND_HALF_UP`; no float/`round()` remains on the money path in tests |
| A-7 | Invariant R-01 compared a property with the expression that defined it | The seed's independent 30-day ceiling is loaded; R-01 compares derived vs seed and a regression test breaks the seed value |
| A-8 | `test_the_cap_flag_is_true_at_the_cap` asserted `False` | Renamed to `test_the_cap_flag_is_false_exactly_at_the_cap`; a true-above-cap test was added (behaviour unchanged: `at_cap` means the cap truncated the accrual) |
| A-9 | `TaxableBaseNegative` existed but the engine raised bare `ValueError`, and the API collapsed it to `PAYROLL_INPUT_INVALID`; other engines still raised bare `TypeError`/`ValueError` | One taxonomy under `PayrollEngineError` (a `ValueError`, preserving the historical catch), stable `code` read structurally by the API; all engines converted |
| A-10 | Statutory allowance floors, child-allowance floor and the seniority base were loaded but never surfaced | `statutory_reference` block + `statutory_parameter_usage`; `applied_to_net=false`; proposed `DEC-013` |
| A-11 | The calculation could not be re-verified against the exact parameter snapshot | Optional injected `StatutoryRuleSet`, SHA-256 `rule_set_fingerprint()` published with every result, injected set must match the request year |
| A-12 | §23's evidence claims were broader than the code (residual, provenance, contract suite) | Corrected in BOOTSTRAP_CHANGELOG §24 (historical §23 left intact) |
| A-13 | Test-integrity defects: the loader test mutated the lru-cached 1404 rule set via `object.__setattr__`; the contract test could not collect at all | Isolated `dataclasses.replace` copy + assertion the cache is untouched; contract test fixed (`force_schema_version="30"`, path-regex filter, contract-valid negative cases skipped) |

## 3. Completed in this pass

1. Unified error catalogue (`app/engines/errors.py`); every engine refusal carries a stable code.
2. Rule-set loader: independent R-01 seed ceiling, R-11 overtime divisor, `canonical_parameters()`/`fingerprint()`, status-source field.
3. Tax engine: slab-total reconciliation, exact total and residual per posture, typed refusal; no bare `ValueError`/`TypeError` left in `app/engines/`.
4. Eydi: floor from `eydi_min_days`, tax reconciliation, typed refusal.
5. Termination engine: scenario model, reconciled total, 30-day divisor, probation base.
6. Statutory reference block (A-10) and parameter-usage audit.
7. Service: engine version `0.3.0-payroll-engine`, genuine residual, per-field provenance, fingerprint, rule-set injection, reference and conflict exposure.
8. Request/response schemas and endpoint mapping updated (`termination_scenario`, `recognised_service_years`, all published blocks).
9. Regression tests added for A-1…A-11; terminated the cached-mutation defect; contract test repaired.
10. `ruff`, `mypy --strict`, full backend suite PASS (results in §5).
11. Documentation: this file, BOOTSTRAP_CHANGELOG §24 (including §24.6), DECISIONS_REGISTER DEC-013 + B-series ledger with corrected 19-entry arithmetic, PROJECT_STATUS/EXECUTION_PLAN evidence, IMPLEMENTATION_READINESS census and the owner-queue register summary.

## 4. Open issues (not defects in this pass)

| Issue | Impact | Status |
| :--- | :--- | :--- |
| PostgreSQL integration suites (104 tests + contract skips) | Database/RLS evidence is NOT RUN in this session | Docker daemon unavailable; last recorded runtime evidence remains BOOTSTRAP_CHANGELOG §15/§21 |
| B-series statutory ambiguities (mixed Appendix A posture, SSO base, overtime in Sanavat/Eydi, Eydi cap/tax, Art. 71 welfare participation, unused floors) | Legal/tax meaning, not arithmetic correctness | Documented in `docs/DECISIONS_REGISTER.md`; owner/Counsel/Tax Accountant required; no value invented |
| DEC-013 (apply allowance floors / seniority to net) | Product/legal scope | Proposed; implementation keeps them reference-only |
| Independent review by a non-author | AGENTS.md §6 | Not available in this environment; engine tasks stay READY_FOR_REVIEW, never APPROVED |
| 1405 activation | External four-eyes verification | Unchanged; 1405 remains unloadable |

## 5. Verification (observed, this pass)

| Command | Result |
| :--- | :--- |
| `backend\.venv\Scripts\python.exe -m pytest -q` | **PASS** — 568 passed, 105 skipped, 9 warnings, 18.69 s |
| `python -m ruff check .` | **PASS** — `All checks passed!` |
| `python -m mypy --strict app tests` | **PASS** — `Success: no issues found in 64 source files` |
| Integration suites (PostgreSQL) | **NOT RUN** — Docker daemon unavailable; the suites self-skip |
| Frontend | not changed in this pass; last recorded evidence remains BOOTSTRAP_CHANGELOG §23 |
| Final re-run after the documentation reconciliation | **PASS** — 568 passed, 105 skipped, 9 third-party warnings; `ruff` and `mypy --strict` unchanged (64 files). `PROJECT_STATUS.md` §2/§3/§7/§9/§10 and `EXECUTION_PLAN.md` §14.3 now cite §24 and the corrected counts |

## 6. Exact next action

Owner review of DEC-013 and the B-series legal questions; then independent
review (AGENTS.md §6) before any engine task moves from `READY_FOR_REVIEW` to
`APPROVED`. PostgreSQL integration re-run is required when a Docker daemon is
available. No commit or push was made by this pass.

---

# Batch 01 — audit and the scope conflict (2026-11-16)

## 7. Audit of the four requested modules

Every row was checked against the tree, not against the documentation.

| Module | Requested | What actually exists | Verdict |
| :--- | :--- | :--- | :--- |
| **A — Authentication / authorization** | login, logout, hashing, RBAC, protected routes, sessions | `app/models/identity.py` (7 tables) + `alembic/versions/0002_identity_foundation.py`; `PiiFieldTransformer` (AES-256-GCM); **no** auth router, no Argon2id path, no session/token endpoint, no RBAC middleware; the frontend auth screens are disabled presentation only | Schema only. Gated by DEC-014, `P0-T08`, `P0-T18` |
| **B — Company / organization** | profile, settings, units, user↔company, isolation | `organizations` + `organization_memberships` tables and their constraints; no API, no service, no tenant-context helper (`P0-T09`), no RLS policy on any tenant table | Schema only |
| **C — Accounting foundation** | chart of accounts, periods, entries, lines, debit=credit, draft/posted, audit | **Nothing.** No model, no migration, no specification, no ADR. The only "transactions" are `frontend/src/data/demo-accounting.ts` fixtures rendered by a read-only demo table | Not authorised by any ADR; no specification to build against |
| **D — Dashboard / navigation** | cards from real API data, role-aware nav, states | React shell, RTL layout, navigation, unit toggle and dashboard cards exist (BOOTSTRAP CHANGELOG §20); **every figure is a synthetic fixture**; the only real endpoint is `POST /api/v1/simulations/gross-to-net`; `/health/ready` is deliberately absent | Demo only; "real API data" for financial cards has no source |

Cross-cutting facts established by the audit: `P0-T07` (blind index) was absent
from the tree although `AGENTS.md` §2 invariant 13 requires it; Docker is not
running, so all 105 PostgreSQL-dependent tests self-skip; the CI workflow has
never executed on GitHub.

## 8. The blocking conflict — DEC-014

Modules A–D are the **superseded** ADR-004 platform scope (plus an accounting
module no ADR authorises). ADR-008 (Accepted) fixes the boundary as the payroll
engine with no frontend requirement. Implementing A–D would therefore need a
superseding ADR and would encode decisions still open in the register
(`P0-T08` key hierarchy, `P0-T18` session contract, `P0-T09` RLS ordering).

Per `AGENTS.md` §11 the affected work was stopped, not improvised, and the
conflict is recorded as **DEC-014** (`OPEN — BLOCKING`) in
`docs/DECISIONS_REGISTER.md`. No authentication, company, accounting or
dashboard code was written.

## 9. Delivered instead — P0-T07

Chosen because it is (a) required by a non-negotiable invariant, (b) missing
from the tree, (c) a prerequisite for any future identity work — so it is not
wasted whichever way DEC-014 is decided — and (d) explicitly assigned its
normalisation rule by the corpus (Holy Bible §5.6, QB-10, HB-MR-011), so no
legal or product value had to be invented.

| Task | Module | Previous | Current | Files | Tests | Remaining |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `P0-T07` | A (foundation) | NOT_STARTED | READY_FOR_REVIEW | `backend/app/core/security/blind_index.py`, `backend/tests/unit/test_blind_index.py`, `backend/ruff.toml` | 45 new tests; all PASS | Pepper custody/rotation (`P0-T08`); database-level CR-05 and < 1 ms B-tree (no Docker); independent security review |

Implementation: injected pepper registry (≥ 32 bytes, read per call, no cache,
no default, no database derivation); `BlindIndexService.index(value, *,
tenant_id, field)` returning 64 lowercase hex characters; tenant and field bound
into the message (`pish:bindex:v1` NUL tenant NUL field NUL canonical); the
normalisation rule for National ID, mobile and Sheba published in AUTH §8.6;
fixed failure messages that never carry the identifier, the key or a registry
exception.

Decisions taken (all internal, none statutory): bind the tenant in the message
rather than deriving a per-tenant key, which satisfies both §8.1 (per-tenant
separation) and §8.2 (single platform pepper) without choosing a custody
backend; refuse rather than repair a malformed identifier.

## 10. Batch-01 verification (observed)

| Command | Result |
| :--- | :--- |
| `pytest tests/unit/test_blind_index.py -q` | PASS — 45 passed |
| `pytest -q` | PASS — 613 passed, 105 skipped, 32.37 s |
| `ruff check .` | PASS — `All checks passed!` |
| `mypy --strict app tests` | PASS — 66 source files |
| PostgreSQL integration suites | NOT RUN — Docker daemon unavailable |
| Frontend tests / build | NOT RUN — no frontend change |
| Independent security review | NOT RUN — no second reviewer available |

## 11. Batch-01 open items

| Item | Status |
| :--- | :--- |
| DEC-014 — product scope for Modules A–D | OPEN — BLOCKING; owner decision required |
| Module A authentication, Module B company API, Module C accounting, Module D real dashboard | NOT_STARTED — blocked by DEC-014 (and, for A/B, by `P0-T08`/`P0-T09`/`P0-T18`) |
| `P0-T07` pepper custody and rotation | Blocked by `P0-T08` (DEC-004 key hierarchy) |
| Database-level CR-05 / RLS / B-tree evidence | NOT RUN — needs PostgreSQL |
| Commit / push | None. The Batch-01 set is uncommitted |

No commit or push was made in this batch.

---

# Batch 02 — compensation advisory module (ADR-009, 2026-11-16)

## 12. Owner decision and scope

The owner asked for an engine that proposes a salary from a person's skills and
experience, with the manager as the only user, emitting a range plus its
statutory cost. Four questions were asked and answered: manual manager input;
skill/experience basis; range plus statutory costing; **ADR first, then
implement**.

`docs/adr/ADR-009-compensation-advisory-module.md` (Accepted) extends ADR-008
and removes nothing. Market benchmarking stays rejected (DEC-007/DEC-008),
document ingestion stays out, and a proposal without a band was refused as an
option because the number would be invented. DEC-014 is untouched and open.

## 13. Delivered

| Task | Module | Status | Files | Tests |
| :--- | :--- | :--- | :--- | :--- |
| `P5-T01` | Advisory valuation model `valuation-v1` | READY_FOR_REVIEW | `backend/app/engines/valuation.py`, `backend/app/engines/errors.py` | 44 unit tests |
| `P5-T02` | Proposal endpoint and composition | READY_FOR_REVIEW | `backend/app/services/valuation_service.py`, `backend/app/schemas/valuation.py`, `backend/app/api/v1/valuation.py`, `backend/app/main.py` | 21 API tests |

Behaviour: score = 0.35·(%of 120 months total) + 0.25·(%of 84 months relevant)
+ 0.30·(skill/5) + 0.10·(education band). The band is manager-supplied;
`proposed = band_min + score × width`, range `± 5 %` of the width clamped to
the band. Both ends and the midpoint are costed by the **existing** engine; the
point costing replays byte-identically through `gross-to-net` (asserted).

Refusals: `VALUATION_BAND_REQUIRED`, `VALUATION_BAND_INVALID`,
`VALUATION_EXPERIENCE_INVALID`, `VALUATION_PROFILE_INVALID`; 1405 still fails
closed with `STATUTORY_PARAMETER_UNAVAILABLE`.

## 14. Verification (observed)

| Command | Result |
| :--- | :--- |
| `pytest tests/unit/test_valuation_engine.py tests/api/test_valuation_api.py -q` | PASS — 65 passed |
| `pytest -q` | PASS — 678 passed, 105 skipped, 34.07 s |
| `ruff check .` | PASS |
| `ruff format` (new/changed files only) | PASS — 4 reformatted |
| `mypy --strict app tests` | PASS — 72 files |
| PostgreSQL integration suites | NOT RUN — no Docker |
| Frontend tests / build | NOT RUN — no frontend change |
| Independent review | NOT RUN — no non-author reviewer available |

## 15. Open after Batch 02

| Item | Status |
| :--- | :--- |
| Authentication in front of the new endpoint (`P0-T18`) | OPEN — the endpoint is a trusted-operator surface only |
| Persistence of proposals and decisions | Out of scope; Track D of the roadmap |
| Band automation from market data | Impossible: DEC-007/DEC-008 rejected, no licensed data |
| Independent review of `P5-T01`/`P5-T02` | Outstanding; both stay READY_FOR_REVIEW |
| DEC-009 (advisory boundary) | Still OPEN — NON-BLOCKING; ADR-009 records the bounded reading actually implemented |

No commit or push was made.
