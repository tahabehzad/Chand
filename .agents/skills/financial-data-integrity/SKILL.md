---
name: financial-data-integrity
description: Enforces exact monetary computation with Decimal, rounding and reconciliation invariants, deterministic reproducibility, immutable statutory rule versioning, hash-chained change auditing, and field-level provenance for every emitted Rial figure.
---

# Financial Data Integrity Skill

## Purpose
Guarantee that every Rial figure Pish Hesabdari emits is exact, reproducible, auditable, and traceable back to the statutory rule that produced it — and that no number can change retroactively after the fact.

## Decimal Discipline
1. **Never use `float` for money.** All monetary arithmetic uses `decimal.Decimal`. Ban `float`, `numpy.float*`, and `math.*` from the calculation modules and enforce it with a lint rule plus a CI grep gate.
2. **One shared context**: `getcontext().prec = 34`, and the only permitted rounding mode for statutory output is `ROUND_HALF_UP`. Python's built-in `round()` uses banker's rounding — it is banned on monetary values.
3. **Integer Rial at the boundaries**: `BIGINT` in the database, integer Rial in JSON payloads. Use `Decimal` only *inside* the computation, then quantize once to `Decimal("1")` Rial at the line-item level.
4. **Round once, at the end.** Do not round an intermediate taxable base and then reuse it downstream. If a legal rule forces a rounded intermediate (e.g. a monthly ceiling expressed in whole Rial), expose it as a named rounding-policy field so it is visible in the audit trail.
5. **Decimal factors, not float literals**: `Decimal(1) / Decimal(12)`, `Decimal("0.07")`. Writing `0.07` reintroduces binary float error at the exact moment precision matters most.
6. Never rely on implicit `float` → `Decimal` coercion; construct `Decimal` from `str` for literals and from `int` for integer Rial.

## Reconciliation Invariants (asserted in every test)
7. **Net identity**: `Gross − sum(deductions) == Net` exactly, in integer Rial.
8. **No hidden rounding residue**: when the sum of individually-rounded line items differs from the rounded total, absorb the difference into an explicit, signed `rounding_residual_rial` line (≤ 1 Rial per line, documented in the response). Never hide it, never let it accumulate silently across line items.
9. **Employer cost identity**: `total_monthly_employer_cost == Gross + employer_SSO + unemployment_fund + sanavat_accrual + eydi_accrual (+ residuals)`.
10. **Inverter round-trip**: Gross-to-Net is the exact inverse of Net-to-Gross to within 1 Rial across a 10,000-case randomized property test (Phase 1 acceptance gate: < 1 Rial deviation).
11. **Split allocation**: when an amount is distributed across N parts, use the **largest remainder method** so the parts sum exactly to the total. Equal division with independent rounding does not.

## Determinism & Reproducibility
12. The calculation engine is a **pure function** of `(inputs, rule_set_version)`. No `datetime.now()`, no `random`, no network calls, no environment reads inside a calculation path.
13. Inject the clock (`now_utc`) and any randomness as explicit parameters.
14. Results must be byte-identical across runs, processes, and machines. Sort any iteration over dicts/sets before it can influence output ordering.
15. Pin the rule set by `rule_set_version_id`, never by "latest" or "current year".

## Rule Versioning & Change Auditing
16. Statutory parameters live in `statutory_rule_set_versions`; the YAML files under `backend/data/seeds/` are bootstrap only. Once a rule set has produced a simulation it is **immutable** — corrections create a NEW version carrying `effective_from` and `supersedes`.
17. Every calculation snapshot persists: `rule_set_version_id`, the input payload (hashed), the output payload, the engine version (git SHA), and the engine code hash.
18. **Change auditing requires a diff report** for every rule-set change: field, old value, new value, legal source citation, effective date, approver, and the list of historical simulations affected. A rule change must never retroactively mutate a stored result.
19. Parameter edits performed through the admin interface are themselves audited events subject to the same hash chain as calculations — an unlogged parameter edit is silent data corruption.

## Provenance & Traceability
20. **Hash chaining** (Module 7): `H_n = SHA256(H_{n-1} ‖ ISO8601_timestamp ‖ tenant_id ‖ canonical_JSON(payload))`. Canonical JSON = sorted keys, no insignificant whitespace, UTF-8, `NaN`/`Infinity` rejected.
21. The audit ledger is append-only: database triggers must reject `UPDATE` and `DELETE` on `audit_logs`.
22. **Field-level provenance**: every returned figure maps to a rule identifier — `provenance[field] = {rule_id, rule_year_shamsi, formula_ref}`. A number with no rule id is an unexplained number.
23. **Audit walk**: a single `simulation_id` + `trace_id` must let an auditor travel from the API response → the rule set version → the code version → the raw inputs → the stored hash, without leaving the system and without querying any external service.
24. **PII discipline in audit payloads**: store encrypted or blinded values only — never a plaintext National ID, mobile number, Sheba, or a real candidate's salary. The ledger is the most-exported artifact in a dispute; it must not become a PII leak.

## Storage & Transport
25. Database types: `BIGINT` for Rial, `NUMERIC(20, 6)` for rates and factors. `FLOAT` / `REAL` / `DOUBLE PRECISION` are forbidden for money, rates, and factors.
26. JSON payloads: monetary fields as JSON integers in Rial (safe — integers within 2^53); rates as **strings** with explicit scale (e.g. `"0.07"`) so a JavaScript client cannot silently coerce them to binary float.
27. Every calculation response carries `rule_version`, `engine_version`, `calculation_hash`, and `generated_at` — without them the value is an assertion, not evidence.

## Verification Harness
28. **Golden vectors**: a versioned, rule-year-keyed corpus of certified tax-accountant-approved input→output pairs. The CI diff must be exactly 0 Rial; a non-zero diff blocks the build.
29. **Property-based tests** (Hypothesis) over the input space, with explicit boundary cases: exactly at the SSO ceiling, exactly on a tax slab edge, net = 0, net below the minimum wage, gross above the ceiling, 30-day vs 31-day months, and Esfand in both 29-day and 30-day variants.
30. **Financial diff gate**: CI fails on any monetary change that is not accompanied by an explicit, reviewed update to the golden vectors and a changelog entry. Silent numeric drift is the failure mode this prevents.
31. **Performance is a correctness constraint**: the fast path stays under 20 ms and the inverter under 5 ms. A regression there is a defect, not an optimization opportunity — the latency budget is part of the API contract.
