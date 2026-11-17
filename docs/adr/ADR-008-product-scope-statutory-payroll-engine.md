# ADR-008: Product Scope Refocus on the Statutory Payroll Calculation Engine

- **Status**: Accepted
- **Partially superseded (2026-11-17, night-work correction)**: [ADR-011](ADR-011-night-work-supplement.md) supersedes only application of the night multiplier: the 1.35 total factor contributes an additional 0.35 above gross, whose ordinary night-hour wages are already included. Historical text below is retained; remaining decisions unchanged.
- **Date**: 2026-11-15 (24 Aban 1405 SH)
- **Decider**: Project Owner, by explicit in-session answers (2026-11-15): "میخوام خیلی مینیمال باشه و ترو تمیز و مرکزیت این پروژه باید همون بخش محاسبه حقوق بر اساس ... باشد" — scope option "کوچک‌سازی رسمی دامنه" selected; interface option "فقط تابع + API" selected; full v1 calculation coverage (SSO + tax + net, overtime/night, sanavat/eydi/CTC, Art. 11) selected; DEC-002a answered "وابسته به قراءة (توصیه)" (welfare allowances taxable under `conservative_inta`, exempt under `court_precedent`); primary response posture answered `conservative_inta`.
- **Consulted**: Lead Backend Engineering (corpus synthesis), independent exploration agents (WBS, skills, governance conventions)
- **Supersedes**: ADR-004 **as to its product-boundary module list and implementation directives 2–3 only**. ADR-004's scope-creep finding (`FIND-PROD-01`/`FIND-PROD-02`), its rationale, and its historical text remain valid and are retained unchanged. ADR-001, ADR-002, ADR-003, ADR-006, ADR-007 and the five-phase/20-week roadmap in REMEDIATED §7 are **not** amended by this ADR.
- **Partially superseded (2026-11-17)**: the product-boundary clauses of this ADR ("pure functions plus one minimal FastAPI endpoint", "no frontend requirement", "no employee data") were superseded **for the manager workspace prototype only** by [ADR-010](ADR-010-manager-mvp-product-scope.md), approved by the Project Owner, effective 2026-11-17. The statutory engine, its invariants, its seeds, its rule sets and its endpoint contract are unchanged by ADR-010. This text is retained unchanged.

## Context and Problem Statement

The owner directed (2026-11-15) that the product be minimal, clean, and centred on the statutory payroll calculation: insurance, progressive income tax, net pay, overtime/night shift, severance (*Sanavat*), annual bonus (*Eydi*), employer Total Cost to Employer, and Article 11 probation worst-case exposure — delivered as pure functions plus one minimal API endpoint, with no UI requirement. Modules outside calculation (document forensics M3, title disambiguation M4, market benchmarking M5, DB snapshot ledger M7) are no longer in the product boundary. This changes the binding module list that ADR-004 §Decision Outcome established for Phase 1, so a superseding ADR is required (Holy Bible §13.1; ADR_INDEX §7).

## Decision Drivers

1. Owner directive: minimal, clean, calculation-centred product.
2. The verified **1404.1** rule set is the only active statutory baseline; 1405 stays inactive (`A1–A8` unmet) — the engine must be usable today without any external gate.
3. Determinism and evidentiary integrity invariants (AGENTS.md §2, financial-data-integrity, iranian-payroll-engineering) are unchanged and bind the engine regardless of scope.
4. Two open accounting decisions that gate the tax engine (DEC-002a; the Art. 137 primary posture) are resolved by this ADR with the owner's explicit answers.

## Considered Options

| Option | Description | Outcome |
| :--- | :--- | :--- |
| 1 | Keep ADR-004's 7-module Phase 1 scope; only reorder execution | Rejected — contradicts the owner's explicit minimal-scope directive |
| 2 | Shrink the product boundary formally to the calculation engine + minimal API; drop/defer the rest | **Accepted** |
| 3 | Shrink scope and also abandon the 20-week roadmap and accepted ADRs 001–003/006/007 | Rejected — no owner authorisation; invariants and roadmap retained |

## Decision Outcome

**The product boundary is the statutory payroll calculation engine**, effective immediately:

- **In scope (v1, owner-selected full coverage)**: *Mozd-e Mabna* / *Mozd-e Saabet* decomposition; employee/employer SSO with insurable ceiling and month-length variants (29/30/31); progressive income tax with the Article 137 dual-posture toggle (both postures always computed side by side; `conservative_inta` is the primary response posture; welfare allowances taxable under `conservative_inta`, exempt under `court_precedent`); overtime and night shift on the *Mozd-e Saabet* base with divisors 220.00/227.33 and multipliers 1.40/1.35; monthly severance accrual `Mozd-e Saabet ÷ 12` (never the seed's `0.0833333333` literal — HB-GAP-017); *Eydi* accrual `min(2 × Mozd-e Saabet, 3 × monthly minimum wage)` with progressive taxation of the exempt-excess (the seed's flat `eydi_tax_excess_rate: 0.10` is never applied — HB-GAP-005, `FIND-LEG-04`); employer monthly cost identity and 12-month CTC without the 26-day leave double count (FIND-MATH-02); Article 11 probation worst-case and Article 66/71 leave buyout. Interface: pure Python functions under `backend/app/engines/` plus a single minimal FastAPI endpoint; no frontend requirement.
- **Out of product scope (deferred, not cancelled)**: document forensics and Shahkar OTP (M3), four-way experience disambiguation (M4), market benchmarking and the Bühlmann-Kish pipeline (M5; DEC-007/DEC-008 are `REJECTED — out of product scope`), the DB snapshot ledger as a product module (M7), the net-to-gross inverter (`P1-T13`), the external 10,000-case golden corpus (`P1-T15`), ERP/PDF export bridges, and M9/M10 packaging. These may return only through a future superseding ADR.
- **Unchanged protections**: the immutable seeds (including their known-defect ledger HB-GAP-005/017), ADR-001…007, the rejected-technology register (ADR_INDEX §5), the statutory verification hierarchy, and every AGENTS.md §2 invariant. The engine reads statutory values from the verified seed via a fail-closed loader — no statutory value is hard-coded.
- **External prototype note**: a Google AI Studio prototype (React/TS + Python sketch) produced outside this repository reproduces the corrected Holy Bible Appendix A vectors (A.4 tax `3,792,061`; A.5 gross `301,075,269` / `449,082,859`; A.7 gross `302,884,615`) and confirms the corrected arithmetic, but it is **not** adopted: its seed files were modified against the pinned hashes, its loaders hard-code values, and its posture defaults contradict the owner decisions recorded here. Only its vector expectations may be reused as engineering-reference test expectations (NOT accountant-certified; `P1-T15` remains blocked).

### Positive Consequences

- The only remaining active product work is the calculation engine on the verified 1404 baseline — no external/legal gate blocks it.
- DEC-002a and the Art. 137 primary posture are resolved, unblocking `P1-T05`/`P1-T09`/`P1-T14` arithmetic decisions.
- The response contract (five provenance fields, dual posture, signed rounding residual) stays identical to the accepted corpus design.

### Negative Consequences / Trade-offs

- Clients needing document forensics, benchmarking, or the inverter wait for a future ADR; the capability gap is explicit rather than silently deferred.
- Some WBS tasks become out-of-scope; their WBS rows are annotated, not deleted (audit trail preserved).

## Pros and Cons of Considered Options

- Option 1 preserves the corpus but defies the owner's directive and keeps blocked external modules in the critical path.
- Option 2 matches the directive, is implementable today on 1404.1, and leaves re-expansion to a future ADR.
- Option 3 was rejected because no owner approval exists to discard accepted ADRs or the roadmap.

## Implementation Directives

1. The engine module layout follows `EXECUTION_PLAN.md` §7.1 under `backend/app/engines/` (rules loader, bases, sso, tax, overtime, severance, eydi, ctc, termination) with composition only in a service layer; the single endpoint is registered in `create_app()`.
2. Every emitted figure carries `rule_version` (`1404.1`), `rule_set_status`, `engine_version`, `calculation_hash`, `generated_at`, and per-field provenance; JSON monetary values are integer Rial and rates are strings.
3. A 1405 request fails closed with `StatutoryParameterUnavailable`; no null is coerced; no silent 1404 fallback.
4. The seed's `eydi_tax_excess_rate: 0.10` and `sanavat_monthly_accrual_rate` keys are never consumed; the corrections (progressive excess; `÷ 12`) are implemented in the engine, and the recorded fix path for the seeds remains the future `1404.2` revision (HB-GAP-005/QB-11).
5. The out-of-scope module list above is recorded in the WBS as annotations on `P1-T13`, `P1-T15`–`P1-T18`, `P1-T20`–`P1-T22`, and the Phase 2/3 module tasks, citing this ADR.
6. Independent review by a non-author is still required before any monetary task is moved beyond `READY_FOR_REVIEW` (AGENTS.md §6).

Verification evidence and accountable owners are recorded in `docs/BOOTSTRAP_CHANGELOG.md` §23.
