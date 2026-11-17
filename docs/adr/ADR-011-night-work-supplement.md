# ADR-011: Apply only the Article 58 night-work supplement above contractual gross

- **Status**: Accepted — Project Owner explicitly instructed this correction on 2026-11-17.
- **Date**: 2026-11-17
- **Deciders**: Project Owner
- **Consulted**: Codex implementation; independent engineering review recorded in BOOTSTRAP_CHANGELOG. No external counsel sign-off asserted.

## Context and Problem Statement

ADR-008's overtime/night-work clause specifies a 1.35 night multiplier. The immutable 1404 seed also stores 1.35. The engine adds the resulting amount to contractual gross even though ordinary night-hour wages are already in gross. Article 58 of the Labour Law provides a 35% supplement for non-shift night work, so adding 135% duplicates ordinary wages. Primary text: [Labour Law, Article 58, page 10 of the reproduced instrument](https://shenasname.ir/wp-content/uploads/2025/02/قانون-کار-با-اصلاحات-بعدی.pdf).

Owner authorization: «اختلاف ضریب شب‌کاری رو هم طبق قانون درست کن و تست بگیر که محاسبه‌اش صحیح باشه». This narrowly supersedes ADR-008's night-work multiplier application, effective prospectively. Its remaining decisions and all other ADRs remain binding. No rejected technology is revived.

## Decision Drivers

- Avoid double-counting wages already in monthly gross.
- Preserve the immutable 1404 seed and historical results.
- Keep Decimal precision, line-boundary half-up rounding and field provenance.

## Considered Options

1. Retain the 1.35 amount as an additional payment.
2. Edit the immutable seed to 0.35.
3. Interpret the loaded 1.35 as total compensation and derive the additional factor by subtracting one ordinary-wage component.

## Decision Outcome

Chosen option: **3**, because it applies the 35% supplement without modifying historical statutory data. `night_pay_exact = hourly_wage × night_hours × (night_shift_multiplier − 1)`. Ordinary wages for these hours must already be in gross. This applies only to non-shift night hours; it does not implement rotating-shift premiums, overtime eligibility or attendance calculation.

### Positive Consequences

- Correct additional night-work payment; existing overtime factor 1.40 unchanged.
- Original seed bytes/fingerprint retained; new engine version and calculation hash identify corrected computations.

### Negative Consequences / Trade-offs

- Nonzero-night-hour results differ from the previous engine. Historical stored results must never be recalculated or overwritten.
- The historical seed field retains its total-factor name and value; its application must be documented and tested.

## Pros and Cons of Considered Options

| Option | Benefit | Defect / cost |
| :--- | :--- | :--- |
| 1 | No code change | Duplicates ordinary wages |
| 2 | Simple factor | Violates immutable seed contract |
| 3 | Correct supplement, preserves history | Requires explicit interpretation and version bump |

## Implementation Directives

1. Derive the supplement from the loaded Decimal multiplier; fail closed if it is below one. No float, seed change, new rule-year activation or historical rewrite.
2. Publish `LABOUR_LAW_ART_58` and the supplement formula in provenance; bump engine to `0.3.1-payroll-engine`.
3. Verify zero hours, fixed independent numerical vectors, 29/30/31 days, half-up boundaries, unchanged overtime and service-level gross/net/employer-cost reconciliation. Independently review the change.
