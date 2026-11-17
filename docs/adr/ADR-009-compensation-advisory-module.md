# ADR-009: Compensation advisory module — manager-entered profiles, band placement and statutory costing

- **Status**: Accepted
- **Date**: 2026-11-16 (25 Aban 1405 SH)
- **Decider**: Project Owner, by explicit in-session answers (2026-11-16): the product must take information "از جاهای مختلف" about a person and propose a salary based on that person's value ("با توجه به مهارت اون شخص، یعنی سابقه کاری"); the only human user is the manager; the output must be a proposed range **plus** the statutory calculation of that range; the change is to be recorded as an ADR before implementation.
- **Supersedes**: nothing. This ADR **extends** ADR-008; it removes no engine capability and changes no statutory rule, seed, rate or hash. ADR-001…007 remain in force.
- **Partially superseded (2026-11-17)**: the out-of-scope bullets of the Decision Outcome ("Persistence of people, proposals or decisions"; "a UI"; "Multi-tenant identity and authentication") were superseded **for the manager workspace prototype only** by [ADR-010](ADR-010-manager-mvp-product-scope.md), approved by the Project Owner, effective 2026-11-17. The advisory-module design, the `valuation-v1` model, the band requirement and every boundary that binds the implementation are unchanged; employee self-service stays out of scope. This text is retained unchanged.
- **Consulted**: Lead Backend Engineering (corpus synthesis and the existing engine contract)

## Context and Problem Statement

ADR-008 (Accepted) fixed the product boundary at the statutory payroll calculation engine: pure functions plus one minimal endpoint, no employee data, no UI. The owner now needs the step *before* that calculation: given a person's documented skills and experience, **what should this person be paid?** — and then what that decision costs the employer under the verified 1404 rule set.

That is a distinct question from ADR-008's ("what does this package cost?"). Answering it needs a decision, because three of its plausible implementations are excluded by the corpus:

- **Market benchmarking** (what the market pays) is `REJECTED — out of product scope` (DEC-007, DEC-008; ADR-008).
- **Document forensics / OCR ingestion** (extracting the profile from uploaded evidence) is a Phase 2 module, blocked by ADR-005 and the 500-slip corpus.
- **Automated salary decisioning / scoring-as-verdict** contradicts `AGENTS.md` §2 invariant 4 (a computed signal is not a verdict) and invariant 5 (human adjudication remains mandatory).

Two further facts constrain the design: there is **no licensed market data** in the repository, and the engine is **deterministic and pure** (invariant 11). A "value-based salary" is therefore only defensible as a **transparent placement inside a money envelope the manager supplies**, never as a market claim.

## Decision Drivers

1. Owner directive: skill/experience-driven proposal; the manager is the only user.
2. No statutory value may be invented, and no amount may appear that the corpus cannot justify (`AGENTS.md` §2 invariants 4, 6, 9; §11).
3. The existing verified engine must do the money arithmetic — one arithmetic path, one rule set, one set of invariants.
4. Determinism and auditability: the same inputs must produce the same proposal, with the model and weights published.
5. Reversibility: the module must be removable without touching the engine.

## Considered Options

| Option | Description | Outcome |
| :--- | :--- | :--- |
| 1 | Keep ADR-008 as-is; salary setting stays outside the product | Rejected — contradicts the owner's explicit directive |
| 2 | **Add a separate advisory module**: manager-entered profile + manager-supplied band → score-based placement → statutory costing through the existing engine | **Accepted** |
| 3 | Add the module *and* market benchmarking / document ingestion to fill in the band automatically | Rejected — no licensed data, DEC-007/DEC-008 rejected, Phase 2 blocked |
| 4 | Let the engine itself output a salary figure with no band | Rejected — any such figure would be invented, breaching invariants 4/6/9 |

## Decision Outcome

**A second product module, "Compensation Advisory", is added beside the statutory engine.**

- **In scope (v1)**
  - Manual, manager-entered profile per person: total professional experience in months, *relevant occupational* experience in months, skill level 1–5, education level. Total and relevant experience stay **separate** inputs (invariant 1); the model never sums overlapping periods (invariant 2) and refuses `relevant > total`.
  - A manager-supplied **monthly gross band** (minimum and maximum) for the role. The band is the only source of money in the proposal: **no band ⇒ a typed refusal, never a generated figure.**
  - A published, versioned **valuation model** (`valuation-v1`): a weighted sum of normalised attributes producing a score 0–100, with the per-component contributions returned to the caller so the number is reviewable.
  - A **proposed range**: the score's position inside the band, widened by a published fraction of the band width and clamped to the band.
  - **Statutory costing of both ends of the range** through the existing `compute_gross_to_net` path: employee SSO, progressive tax under the primary `conservative_inta` posture, net, severance/Eydi accrual and total monthly employer cost. The statutory figures are the engine's, not the module's.
  - One endpoint: `POST /api/v1/valuations/compensation-proposal`.
- **Explicitly out of scope (unchanged or deferred)**
  - Market/benchmark data of any kind (DEC-007/DEC-008 remain rejected).
  - Document upload, OCR, forensics, and any automatic extraction of the profile (Phase 2; ADR-005 proposed).
  - Persistence of people, proposals or decisions; employee self-service; a UI (the SPA remains a demo, ADR-008 unchanged).
  - Multi-tenant identity and authentication: the module is a **single-operator** surface in v1, exactly like the existing endpoint. `P0-T18` remains the gate for "who may call this"; the endpoint must not be exposed beyond a trusted operator until it lands.
- **Boundaries that bind the implementation**
  - Every response is marked advisory: `advisory: true`, `statutory: false`, `model_version`, and an explicit statement that the proposal is not a legal entitlement, not a market rate and not tax advice (DEC-009 stays a neutral calculator).
  - The statutory floor (1404 minimum wage) is **published as context, never silently applied** — consistent with DEC-013, which remains open.
  - No clock, randomness, network or environment read in the calculation path; `generated_at` is added at the API boundary only.
  - Money stays integer Rial at every boundary; scores and weights use `Decimal` with `ROUND_HALF_UP`; no float literal in `app/engines/**`.

## Pros and Cons of Considered Options

- **Option 1** is the cleanest boundary but ignores the owner's actual product need, and the engine would remain a calculator nobody buys.
- **Option 2** reuses the only verified arithmetic in the repository, adds one pure module and one endpoint, and keeps every invariant intact. Its weakness is honest: the money envelope is a human judgement, so the module ranks and costs, it does not price.
- **Option 3** would look more impressive and would be indefensible: no licensed data, a rejected decision ledger, and a blocked Phase 2.
- **Option 4** is the only option that would produce a number out of nothing.

## Implementation Directives

1. Module: `backend/app/engines/valuation.py` (pure), model version `valuation-v1`; composition only in `backend/app/services/valuation_service.py`; one endpoint in `backend/app/api/v1/valuation.py`, registered in `create_app()`.
2. The model: `experience` (total months ÷ 120, capped at 1) weight 0.35; `relevant` (relevant months ÷ 84, capped at 1) weight 0.25; `skill` (`skill_level ÷ 5`) weight 0.30; `education` (ordinal 0, 0.25, 0.5, 0.7, 0.9, 1.0) weight 0.10. Weights are constants of the model version and are echoed in every response.
3. Range: `position = score`, `proposed = band_min + score × (band_max − band_min)`; the published range is `proposed ± 0.05 × (band_max − band_min)`, clamped to `[band_min, band_max]`; bounds rounded half-up to whole Rial.
4. Refusals are typed and categorical: `VALUATION_BAND_REQUIRED`, `VALUATION_BAND_INVALID`, `VALUATION_EXPERIENCE_INVALID`, `VALUATION_PROFILE_INVALID`. No refusal carries a monetary amount or a personal attribute value.
5. The statutory block is produced by calling the **existing** service; the module never re-implements tax, SSO, severance, Eydi or CTC.
6. Tests: unit tests for every boundary and refusal, and API tests including the OpenAPI contract suite (`tests/api/test_openapi_contract.py` covers every published path).

## Consequences

- **Positive**: the product now answers "what should this person be paid, and what would that cost?" on the same verified arithmetic; the answer is auditable (model version, weights, contributions, both statutory costs) and cannot silently become a statutory claim.
- **Positive**: nothing in the engine changes; the module is removable.
- **Negative**: the module cannot price a role without a manager-supplied band — a deliberate limit, not an omission.
- **Negative**: the model is a **policy heuristic**, not a validated salary science; it must never be described as certified, actuarial or market-calibrated.
- **Open**: authentication/authorisation for the endpoint (`P0-T18`), persistence of proposals (Track D of `docs/ROADMAP_OPERATIONAL_PAYROLL.md`), and any future band automation that would need licensed data.

Verification evidence is recorded in `docs/BOOTSTRAP_CHANGELOG.md` §27; task rows are `P5-T01`/`P5-T02` in `docs/EXECUTION_PLAN.md` §14.3.
