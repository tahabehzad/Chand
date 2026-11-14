---
name: iranian-payroll-engineering
description: Implements exact Iranian payroll, SSO insurance, progressive income tax, overtime, severance (Sanavat), annual bonus (Eydi), and Total Cost to Employer calculations on correct statutory bases, with verified rounding and legal citations.
---

# Iranian Payroll Engineering Skill

## Purpose
Implement the deterministic statutory wage engine (Module 1), the closed-form Net-to-Gross inverter (Module 2), and the CTC / termination simulator (Module 6) of `REMEDIATED_TECHNICAL_SPECIFICATION_V2.md` so that every emitted Rial figure is defensible before a Labor Dispute Settlement Board (*Heyat-e Tashkhis* / *Heyat-e Hal-e Ekhtelaf*).

## Core Vocabulary — Never Confuse These Bases
| Concept | Persian | Legal definition | Correctly used as base for |
| :--- | :--- | :--- | :--- |
| *Mozd-e Mabna* | مزد مبنا | Wage subject to SSO insurance | SSO 7% / 20% / 3% contributions |
| *Mozd-e Saabet* | مزد ثابت | Base wage + continuous fixed attraction allowances (Precedent 3328) | Overtime, Sanavat, Eydi |
| *Hoghoogh* | حقوق | Total contractual entitlement | CTC |
| *Fogholadeh Jazb* | فوق‌العاده جذب | Fixed, continuous attraction allowance | MUST be **inside** *Mozd-e Saabet* (`FIND-LEG-05`) |
| *Hagh-e Maskan / Bon-e Kharobar / Hagh-e Olad* | حق مسکن / بن خواربار / حق اولاد | Welfare allowances | MUST be **excluded** from the overtime base (Art. 36 Note 3, `FIND-LEG-03`) |

**Inclusion test for *Mozd-e Saabet***: an allowance qualifies only if it is (a) fixed — identical every month, (b) continuous — paid unconditionally, and (c) not a welfare allowance under Art. 36 Note 3. Variable bonus, commission, overtime pay, and benefits are always outside. Getting this wrong silently changes overtime, severance, and Eydi simultaneously.

## Statutory Engine Rules (Module 1)
1. **Source of truth**: never hard-code a rate in Python. Load parameters from `statutory_rule_set_versions` (database) or `backend/data/seeds/statutory_rules_*.yaml` (bootstrap only). Every calculation snapshot persists `rule_set_version_id`.
2. **Fail closed on unverified rules**: `backend/data/seeds/statutory_rules_1405.yaml` currently ships `is_verified_and_active: false` with `null` parameters. The engine MUST raise `StatutoryParameterUnavailable` rather than coerce `null` to `0`. Serving 1404 figures under a 1405 label manufactures illegal contracts (`FIND-TIME-01`).
3. **SSO rates**: employee 7%, employer 20%, unemployment insurance fund 3% (employer-paid). Employer burden totals 23%. These are statutory constants, not tunable parameters — never expose them in the admin UI.
4. **Insurable ceiling**: `C = 7 × daily_minimum_wage` per day; monthly ceiling `= C × days_in_month` (30 or 31). Contributions are computed on `min(gross, C)`. Always emit `sso_insurable_ceiling_applied` as an explicit boolean.
5. **Progressive salary tax**: slabs 0 / 10 / 15 / 20 / 25 / 30% applied to the taxable base after the monthly exemption and statutory deductions. Taxable base = gross − employee SSO − other deductible allowances − exemption.
6. **Article 137 deduction policy toggle** (`FIND-LEG-02`): implement and always report **both** named policies side-by-side:
   - `conservative_inta` — deduct only the medical share of the employee 7% SSO (2/7 of it).
   - `court_precedent` — deduct the full employee 7% SSO (Precedents 1956 & 3328).
   Never silently default to one in a single-value field, and never describe this deduction as a "tax cap".
7. **Overtime** (Art. 59, Art. 36 Note 3): base is *Mozd-e Saabet* only. Monthly divisors `220.00` (30-day month, `44 × 30 / 6`) and `227.33` (31-day month, `44 × 31 / 6`). Multiplier 1.40; night shift 1.35. Welfare allowances are excluded from the divisor base *and* from the numerator base.
8. **Sanavat** (Art. 24): 1 month of *Mozd-e Saabet* per year of service = `1/12` monthly accrual. The base MUST include continuous fixed attraction allowances (`FIND-LEG-05`). Round each monthly accrual to whole Rial.
9. **Eydi** (1370 Law): minimum 60 days of *Mozd-e Saabet*; maximum 90 days of minimum wage (= 3 × monthly minimum wage). Tax exemption = `1/12` of the annual Article 84 exemption; the excess is taxed **across the progressive salary brackets**. A flat 10% is a legal fallacy (`FIND-LEG-04`).
10. **Art. 91 non-cash benefits**: exemption = `2/12` of the annual exemption.

## Net-to-Gross Closed-Form Inverter (Module 2)
Replace the 50-step bisection loop (`FIND-MATH-01`) with an O(1) piecewise solve. The net function is:
```
Net(G) = G − sso_emp(G) − tax(G)
sso_emp(G) = s · min(G, C)                      # s = 0.07, capped at C
tax(G)     = r_k · (taxable base) + T_k          # T_k = accumulated tax of all lower slabs
```
Two regions must be solved separately, because SSO stops being proportional above the ceiling:

- **Region A (G ≤ C)** — SSO proportional:
  `G = (Net + T_k − E·r_k) / ((1 − s)(1 − r_k))`
- **Region B (G > C)** — SSO capped at `s·C`:
  `G = (Net + T_k − E·r_k + s·C·(1 − r_k)) / (1 − r_k)`

**Mandatory algorithm**: for each candidate slab `k`, solve for `G`, then **verify** `G` actually lies in that slab's interval and in the assumed region. If the check fails, advance to the adjacent slab and re-solve. Never return a candidate that has not passed the boundary check — a piecewise solver that skips verification produces off-by-a-slab salaries that still "look plausible".

**Fallback**: only when allowance rules introduce genuine non-linearity, use Newton-Raphson on the piecewise function, and cap it at 3 iterations with a bisection backstop. Assert convergence to within 1 Rial.

## CTC, Termination & Leave (Module 6)
11. **Annual CTC** (`FIND-MATH-02`):
    `CTC_annual = 12 × Gross + 12 × SSO_employer(23%) + Sanavat_annual + Eydi_annual + LeaveCarryoverLiability + RecruitmentFriction`
12. **No double-counted leave**: the 26 days of statutory annual leave are already-paid working days inside the 12 months of salary. Never accrue an additional 26-day cash reserve. Accrue only for expected unexercised carryover:
    `LeaveCarryoverLiability = min(9, ExpectedUnusedDays) × DailyWage × P_non_utilization`
13. **Exit leave buyout** (`FIND-LEG-06`): Art. 66 caps *annual carryover* at 9 days, but Art. 71 requires paying **all accumulated** unused leave from every year upon exit:
    `LeaveBuyout = TotalAccumulatedUnusedDays × FinalDailyWage` where `TotalAccumulatedUnusedDays ≤ 9 × TenureYears`. The 9-day cap applies per year, not in total.
14. **Art. 11 probation liability** (`FIND-LEG-01`): if the **employer** terminates during probation, liability = full salary for the **entire agreed probation period** (up to 3 months), NOT the days worked. Termination by the employee remains days-worked. Never truncate this.
15. **Deduction base**: the Art. 137 SSO deduction is computed on the *insurable* wage, not the raw gross.

## Domain Glossary for API & UI
`Mazd-e Mabna` / `Mozd-e Saabet` / `Hoghoogh` / `Sanavat` / `Eydi` / `Hagh-e Maskan` / `Bon-e Kharobar` / `Hagh-e Olad` / `Payeh Sanavat` / `Fogholadeh Jazb` / `Sabegheh Tamin` / `Hokm-e Kargozini`. Never use English loanwords ("severance pay", "bonus") in user-facing Persian strings — use the statutory Persian term so the output is intelligible to a *Heyat-e Tashkhis* reviewer.

## Non-Negotiable Invariants
16. A calculation result is only valid alongside its `rule_set_version_id`; a result without it is not evidence.
17. Every statutory output is an integer number of Rial. See `financial-data-integrity` for the rounding discipline that guarantees this.
18. Gross-to-Net must be the exact inverse of Net-to-Gross to within 1 Rial across a 10,000-case property test (Phase 1 acceptance gate).
19. Any change to a statutory formula, base definition, or rate requires a new ADR plus a migration note for stored snapshots — it is never a hotfix.
