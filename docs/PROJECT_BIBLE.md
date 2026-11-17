# Project Bible — Pish-Hesabdari (پیش‌حسابداری)

- **Document ID:** `DOC-BIBLE-001`
- **Status:** Active reference — created 2026-11-16 on explicit owner instruction. The product direction described in §3–§5 is **owner-stated but not yet an accepted ADR** (see `docs/DECISIONS.md` PB-D01).
- **Authority order:** `AGENTS.md` → accepted ADRs (`docs/adr/`) → `docs/DECISIONS_REGISTER.md` → `docs/EXECUTION_PLAN.md §14.3` (task status) → `docs/PROJECT_STATUS.md` (delivery) → this Bible → `docs/CURRENT_STATE.md`.
  Where this Bible and an accepted ADR disagree, **the ADR wins** and the disagreement is listed in `docs/DECISIONS.md`.
- **Does not replace:** statutory status owners, the 88-task WBS, the ADR register, or `docs/BOOTSTRAP_CHANGELOG.md`.
- **Language:** Persian for user-facing prose, English for code/identifiers/paths (`AGENTS.md §0`).

---

## 1. Project identity

| Field | Value |
| :--- | :--- |
| Name | Pish-Hesabdari — پیش‌حسابداری |
| Repository | `C:\project\New project` (branch `autonomous/project-completion`) |
| Current product (accepted) | Statutory Iranian payroll calculation engine on the verified 1404 SH baseline (ADR-008) |
| Emerging product (owner-stated, provisional) | Management system for evaluating people and producing explainable compensation recommendations |
| Initial user | Manager / organisation owner only (PB-D02) |
| Stack as built | Python 3.12 / FastAPI / SQLAlchemy / Alembic / PostgreSQL 16 · React 19 / TypeScript / Vite / Tailwind v4 / TanStack Query / Zustand |
| Statutory baseline | **1404 SH** verified and active; **1405 transcribed, unverified, fail-closed** |

## 2. Executive summary

The repository today is a **working, tested statutory payroll engine** with a thin API and a Persian RTL React front-end. It is not a management system: there is no person record, no persistence in the request path, no authentication, no evaluation of performance, and no stored recommendation.

The owner has stated a broader direction: collect information about people from several sources, evaluate contribution, and produce a **justified, explainable compensation recommendation** for a manager. That direction is **not yet authorised by a superseding ADR**; the accepted boundary (ADR-008) is the payroll engine only, and `DEC-014` holds exactly these modules `OPEN — BLOCKING`.

Therefore this Bible separates three things deliberately:

1. **What exists** — evidence in `docs/CURRENT_STATE.md`.
2. **Where the product is going** — §3–§5, provisional until PB-D01 is decided.
3. **What five hours can demonstrate** — `docs/MVP_SCOPE.md` and `docs/MVP_WBS.md`, a labelled prototype.

## 3. Product vision

> Turn scattered operational information about people into structured, explainable, actionable compensation insight, so a manager can decide with evidence instead of impression.

The system should let one manager register people, gather their work and performance data from several sources, review and correct it, score contribution on published criteria, and receive a compensation recommendation that shows **exactly which data, weights and rules produced it**.

It is **not** a traditional accounting dashboard, and it is **not** only a statutory payroll calculator. The payroll engine is a reusable technical asset for costing a decision; it does not define the product.

## 4. Problem being solved

| Problem | Consequence today | Desired outcome |
| :--- | :--- | :--- |
| Compensation decisions rest on memory and opinion | Unexplainable pay gaps, retention loss, disputes | A published, reproducible basis for each recommendation |
| Performance evidence is scattered across files and systems | Manager re-collects it every cycle, inconsistently | One normalised, source-attributed record per person |
| Payroll tools answer "what must I pay legally", not "what should I pay this person" | Statutory compliance and management judgement are conflated | Two clearly separated layers: advisory recommendation vs statutory costing |
| Existing tools are black boxes | Manager cannot defend or correct a number | Per-criterion breakdown, data-source trace, rule version |

## 5. Target users and use cases

**Primary (and only MVP) user:** Manager / organisation owner (PB-D02). Employees are **subjects**, never application users. No employee portal in the MVP.

| ID | Use case | MVP? |
| :--- | :--- | :--: |
| UC-01 | Register and maintain people | Yes |
| UC-02 | Enter performance data manually | Yes |
| UC-03 | Import performance data from a file | Optional (CSV) |
| UC-04 | Review, correct and reject collected data | Yes |
| UC-05 | Score a person on published criteria | Yes |
| UC-06 | Generate a compensation recommendation with explanation | Yes |
| UC-07 | Approve / edit / reject a recommendation and record the decision | Yes |
| UC-08 | See a management summary of people and decisions | Yes (basic) |
| UC-09 | Import from external systems (integrations) | Later |
| UC-10 | Compare recommendation history across periods | Later |
| UC-11 | Employee self-service | Later (deferred) |

## 6. Product principles

1. **Explainability over sophistication.** Every score and recommendation must be reconstructable from published inputs, weights and rule version. No black box.
2. **Recommendation, not execution.** The manager decides; the system never transfers money (PB-D07).
3. **Advisory and statutory are different layers.** A recommendation is not legally compliant payroll and must never be labelled as such.
4. **Fail closed on missing data.** Unknown values stay unknown; never coerce to zero (`AGENTS.md §2.10`).
5. **Source attribution everywhere.** Each observation keeps its origin, import batch and timestamp.
6. **Deterministic before intelligent.** A rule engine first; AI only as assistance, never silently deciding money.
7. **No identity guessing.** Similar names are not the same person (§11).
8. **Reuse, don't rebuild.** The statutory engine already answers "what does this gross cost" — call it.
9. **Prototype honesty.** A demonstration is labelled a demonstration in the UI and the docs.

## 7. Functional requirements

Marked `MVP` where `docs/MVP_SCOPE.md` includes it. IDs are stable for future work.

| ID | Requirement | MVP |
| :--- | :--- | :--: |
| FR-01 | Create, read and list people with a display name, role label and start date | Yes |
| FR-02 | Reject a person record with malformed or missing required fields, with a typed error | Yes |
| FR-03 | Attach performance observations to exactly one person, with metric, period, value and source | Yes |
| FR-04 | Import observations from CSV with per-row validation and an import batch record | Optional |
| FR-05 | Show validation state per observation and allow correction or rejection | Yes |
| FR-06 | Define evaluation criteria and weights as a versioned rule set | Yes |
| FR-07 | Compute a deterministic 0–100 score with per-criterion contributions | Yes |
| FR-08 | Handle missing criteria by an explicit, published policy (never silent zero-fill) | Yes |
| FR-09 | Generate a compensation recommendation: score, position in a manager-supplied band, suggested gross, delta to current pay | Yes |
| FR-10 | Cost the suggested gross through the statutory engine (net, employer cost) and label it advisory | Yes |
| FR-11 | Display the full explanation: observations used, weights, contributions, rule version, engine version | Yes |
| FR-12 | Record manager decision (approve / edit / reject) with comment and timestamp | Yes |
| FR-13 | Show a management dashboard: people, pending recommendations, recent decisions | Yes (basic) |
| FR-14 | Detect duplicate observations and duplicate person candidates without auto-merging | Later |
| FR-15 | Persist everything across restarts in PostgreSQL with tenant isolation | Later |
| FR-16 | Manage several evaluation periods and compare history | Later |
| FR-17 | Connectors for external data sources | Later |
| FR-18 | Role-based access and authenticated sessions | Later (blocks any shared deployment) |

## 8. Non-functional requirements

| ID | Requirement | Status |
| :--- | :--- | :--- |
| NFR-01 | Money is integer Rial in JSON; computation in `Decimal` (`prec=34`, `ROUND_HALF_UP`); no float in money paths | Enforced in existing engines; must extend to new modules |
| NFR-02 | Every emitted figure carries `rule_version`/`model_version`, `engine_version`, `calculation_hash`, `generated_at` | Existing endpoints do; new recommendation must |
| NFR-03 | Deterministic: same inputs + same rule version ⇒ same score and hash | Required for MVP |
| NFR-04 | Persian RTL UI, logical CSS properties, Persian numerals only in display layer | Existing front-end convention |
| NFR-05 | No secret, national ID, mobile or Sheba in logs, errors or fixtures | `AGENTS.md §2.15` |
| NFR-06 | Response time for one recommendation < 300 ms locally (no network calls in the path) | Target, unmeasured |
| NFR-07 | Append-only audit trail for decisions | Not implemented (`P0-T10`) |
| NFR-08 | Multi-tenant isolation with RLS and `FORCE ROW LEVEL SECURITY` per tenant table | Not implemented for data tables |
| NFR-09 | Backup with PITR and rehearsed restore | Partial (`P0-T16`) |

## 9. Data source strategy

Intake is **mixed**, and no external system is selected (PB-D04). The architecture must accept a new source without touching the scoring engine.

| Channel | MVP | Design consequence |
| :--- | :--: | :--- |
| Manual form | Yes | Validated DTO → observation record |
| CSV file | Optional | Parser produces the **same** observation DTO; per-row errors reported |
| XLSX | No | Needs a new dependency; deferred |
| External API / connector | Later | Adapter implements a `SourceConnector` port; no engine change |
| OCR / documents | Later (historical P2 scope, out of product scope) | Deferred; do not revive without a new ADR |

Every ingestion must be able to: validate, normalise (units, dates, numerals), detect duplicates, attribute source, record an import batch, report errors, allow correction, and trace an evaluation back to the original input (FR-14, `docs/ARCHITECTURE.md §7`).

## 10. Person identity and data model concepts

- A **person** is a subject of evaluation, identified by an internal `person_id`. It is not a user account and has no login.
- Identity attributes: display name, role label, start date, optional employee reference from an external system. **No national ID or bank data in the MVP prototype** (PB-D06/R4).
- **Matching is a first-class risk.** Two records with similar names are **not** assumed to be the same person. The MVP must not auto-merge. Future matching requires an evidence-based rule with human confirmation (PB-D05).
- Proposed entities (not yet implemented — `docs/ARCHITECTURE.md §9`): `person`, `performance_observation`, `import_batch`, `evaluation_rule_set`, `evaluation_run`, `evaluation_criterion_result`, `compensation_recommendation`, `recommendation_decision`.
- Statutory tables (`statutory_*`) stay **global** and separate (ADR-007); performance data must never be written into them.

## 11. Evaluation engine concepts

**Existing:** `app/engines/valuation.py` (`valuation-v1`) scores **experience (35 %), relevant experience (25 %), skill level (30 %), education (10 %)** and places the score in a manager-supplied band. This is a **profile heuristic, not performance evaluation**.

**Required for the product (provisional model, PB-D03):**

| Criterion (illustrative only) | Illustrative weight | Real metric | Source |
| :--- | --: | :--- | :--- |
| Sales / measurable output | 40 % | UNKNOWN | UNKNOWN |
| Work quality | 30 % | UNKNOWN | UNKNOWN |
| Attendance and discipline | 20 % | UNKNOWN | UNKNOWN |
| Responsibility and reliability | 10 % | UNKNOWN | UNKNOWN |

> **These weights and criteria are examples from the owner brief. They are NOT approved business rules** (PB-D03). No code may treat them as statutory or final.

Engine requirements: configurable criteria and weights; versioned rule sets; explicit missing-data policy; per-criterion normalisation; deterministic Decimal arithmetic; published contributions; historical runs retained; refusal codes instead of silent defaults.

**AI boundary:** may later assist extraction, summarisation and anomaly detection. It must never silently produce a financial decision (PB-D08).

## 12. Compensation recommendation workflow

```
observations (person, period, source)
        ↓ normalise + validate
evaluation run (rule set version vN)
        ↓ score 0–100 + per-criterion contributions
band position (manager-supplied min/max gross)      ← current compensation (optional)
        ↓ suggested gross + delta
statutory costing of suggested gross (existing engine: net, employer cost)
        ↓
recommendation (advisory: true, statutory: false, hashes, explanation)
        ↓
manager: approve / edit / reject  →  decision record (comment, timestamp)
```

A recommendation must contain: person, period, score, breakdown, current pay (if known), suggested pay, difference, explanation, data sources, model and rule versions, decision and comments (FR-09…FR-12).

No automatic bank transfer. No claim of legal compliance. An edited amount must preserve the original suggestion and the edit reason.

## 13. Existing technical architecture (verified)

```
backend/app/
  main.py                 FastAPI app, CORS, correlation id, /health/live
  api/v1/payroll.py       POST /api/v1/simulations/gross-to-net
  api/v1/valuation.py     POST /api/v1/valuations/compensation-proposal
  services/               payroll_service.py (composition + hash), valuation_service.py
  engines/                money, rules, bases, sso, tax, overtime, severance, eydi,
                          ctc, termination, valuation, statutory_reference, errors
  schemas/                Pydantic v2 contracts (integer Rial, rates as strings)
  models/                 statutory.py (5 global tables), identity.py (7 tables)
  core/                   config.py, logging.py, security/{pii_transformer,blind_index,tenant_context}
  storage/                s3_adapter.py (GOVERNANCE adapter)
alembic/versions/         0001 statutory baseline · 0002 identity · 0003 tenant context
frontend/src/             app/ (shell, router) · routes/ · api/ (typed client, contracts)
                          components/ui/ · lib/ (numerals, money, calendar port)
infra/                    postgres/ (hardened 16.16 image, roles, verify) · compose/compose.dev.yml
```

Verified facts: exactly **three** HTTP routes exist; **no API route uses a database session**; there is **no authentication dependency anywhere**; `ENGINE_VERSION = "0.3.0-payroll-engine"` (`app/engines/__init__.py:80`, reconciled per ADR-010 directive 1).

## 14. Reusable modules (map before building)

| Need | Reuse | Do not rebuild |
| :--- | :--- | :--- |
| Money arithmetic, rounding, residual | `app/engines/money.py` | Decimal helpers |
| Costing a gross (net, SSO, tax, employer cost) | `app/services/payroll_service.py` → `compute_gross_to_net` | tax/SSO formulas |
| Band placement logic | `app/engines/valuation.py` (`propose_gross_range`) | new interpolation |
| Score + weights + contributions shape | `valuation.py` (`assess_profile`, `ValuationWeights`) | new score envelope |
| Error envelope and refusal codes | `app/engines/errors.py`, API pattern in `api/v1/payroll.py` | new error shape |
| Provenance/hash | `payroll_service._provenance`, SHA-256 canonical JSON | new hashing scheme |
| Persian numerals / money display | `frontend/src/lib/*` | new formatters |
| RTL primitives, states, shell | `frontend/src/components/ui/*`, `app/app-shell.tsx` | new design system |
| Contract registry honesty | `frontend/src/api/contracts.ts` | fake endpoints |

## 15. Known limitations

- No person, observation, evaluation or recommendation entity; no persistence; no database in the request path.
- No performance evaluation: `valuation-v1` is experience/skill/education only.
- No authentication, session, RBAC, rate limiting; both POST endpoints are open.
- No hash-chained audit ledger; no key management; no tenant RLS on data tables.
- No E2E suite, no visual/axe verification, no load test.
- No independent review sign-off on any engine task (`0 APPROVED`), no legal/accounting sign-off.
- 1405 inactive; statutory outputs are 1404-baseline only and must not be called legally final.
- `tsc -b` fails (vite/vitest typing); documented gate `pnpm typecheck` passes. `pnpm` is not on `PATH` on this host.

## 16. Security considerations

| Control | State |
| :--- | :--- |
| Encryption of PII fields (AES-256-GCM) | Module exists and is tested; no production key registry |
| Blind index (HMAC-SHA256) | Module exists; DB-level lookup and pepper custody absent |
| Tenant isolation | Helpers and assertion function exist; **no tenant data table yet** |
| Audit ledger | Absent |
| Authentication | Absent (login screen is presentation-only) |
| Secrets handling | Keys only in `.env.example`; `.secrets/` untracked; never read or print |
| Prototype endpoint exposure | Must be loopback-only and environment-gated (PB-D11) |

Any new MVP endpoint inherits the gap list above: a prototype that stores person data must not be exposed beyond the local machine.

## 17. Legal and accounting boundaries

1. The payroll engine is **not legally approved**. 1404 is the only active baseline; 1405 is fail-closed.
2. Management recommendations are **not** statutory payroll. They must be labelled `advisory`/`statutory: false`.
3. Do not merge performance logic with statutory rules. The statutory engine may only **cost** a proposed gross.
4. Legal/accounting verification (independent review, `P1-T15`, `P4-T07`, `P4-T08`) is required before any real payroll use.
5. Open legal questions remain (`DEC-001`, `DEC-002`, `DEC-013`, B-1…B-8, B-10). Unknown stays unknown.
6. MVP data is synthetic/labelled. Real person data requires the security work in §16.

## 18. Five-hour MVP target

A single-manager, local, end-to-end demonstration: register a person → enter or import performance observations → review and correct them → score with a published rule set → generate an explained recommendation → approve/edit/reject → see it on a dashboard.

- It is a **prototype**: in-memory store, no authentication, loopback only, synthetic data, explicit banner.
- It reuses the statutory engine for costing and the existing UI primitives.
- Full scope, exclusions, acceptance criteria and compromises: `docs/MVP_SCOPE.md`
- Task plan totalling exactly five hours: `docs/MVP_WBS.md`

**The five hours do not complete any historical WBS task and pass no phase gate.**

## 19. Long-term roadmap

| Horizon | Theme | Prerequisites |
| :--- | :--- | :--- |
| H1 (this session) | Labelled prototype of the evaluation→recommendation loop | PB-D01 recorded; PB-D06 persistence choice |
| H2 | Authenticated single-tenant product on PostgreSQL with audit ledger | `P0-T18`, `P0-T10`, `P0-T08`, person schema with RLS |
| H3 | Ingestion adapters, duplicate/identity matching, import history | PB-D04, PB-D05, connector ports |
| H4 | Multi-period evaluation, history, reporting, PDF | `P3-T11`, `DEC-006` |
| H5 | Multi-tenant enterprise, RBAC, employee portal, mobile | ADR for tenancy + auth; penetration test |
| H6 | AI assistance (extraction, anomaly support), never autonomous decisions | Data governance, evaluation of false positives |

Deferred capability register: `docs/FUTURE_BACKLOG.md`.

## 20. Glossary

| Term | Meaning |
| :--- | :--- |
| مزد مبنا / Mozd-e Mabna | Statutory base wage — never merged with other wage terms |
| مزد ثابت / Mozd-e Saabet | Fixed wage used for overtime, severance, Eydi bases |
| سنوات / Sanavat | Severance accrual (1/12 of Saabet per month) |
| عیدی / Eydi | Annual bonus with statutory floor/cap |
| CTC | Total cost to employer (monthly and annual) |
| Art. 137 posture | Two published readings of tax exemption; `conservative_inta` is primary |
| Rule set | Versioned statutory parameter set (1404 active) |
| Model version | Scoring model identifier (`valuation-v1` today) |
| Recommendation | Advisory compensation proposal; never an entitlement |
| Observation | One sourced performance datum about one person in one period |
| Prototype | Labelled, local MVP in `docs/MVP_SCOPE.md`; not production |

## 21. Open questions and unresolved decisions

Product-scope and product-design decisions are tracked with stable IDs in `docs/DECISIONS.md` (PB-D01…PB-D12). Statutory/legal decisions remain in `docs/DECISIONS_REGISTER.md` (DEC-001…DEC-014). The most consequential open items:

| Question | Owner | Where |
| :--- | :--- | :--- |
| Is the management-evaluation product formally in scope (superseding ADR-008)? | Project Owner | PB-D01 / DEC-014 |
| Which real criteria and weights? | Project Owner | PB-D03 |
| Which data sources, in what order? | Project Owner | PB-D04 |
| Identity-matching policy | Project Owner + Security | PB-D05 |
| Persistence for MVP and after | Architect + Owner | PB-D06 |
| Authentication before any shared use | Owner + Security | PB-D09 / `P0-T18` |
| Relationship between recommendation and statutory payroll | Owner + Labour Counsel | PB-D07 |

## 22. Document map

| Need | Read |
| :--- | :--- |
| What exists, with evidence | `docs/CURRENT_STATE.md` |
| Five-hour scope and acceptance | `docs/MVP_SCOPE.md` |
| Five-hour task plan (300 min) | `docs/MVP_WBS.md` |
| Current vs proposed architecture | `docs/ARCHITECTURE.md` |
| Decisions: confirmed, provisional, open, rejected | `docs/DECISIONS.md` |
| Deferred capabilities | `docs/FUTURE_BACKLOG.md` |
| How agents must work | `docs/AGENT_GUIDE.md` |
| Statutory status owners | `docs/PROJECT_STATUS.md`, `docs/EXECUTION_PLAN.md §14.3` |
| Operating rules (binding) | `AGENTS.md` |
