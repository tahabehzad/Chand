# SALARY_ENGINE_SPECIFICATION.md

Salary Engine Specification — Pish Hesabdari

## 1. Engine Overview

The salary estimation engine is a rule-based, deterministic system that calculates a market-based recommended monthly base salary for a candidate based on Iranian labor market conditions.

**Authority:** ADR-013 Salary Estimation Tool (accepted 2026-11-17)

**Implementation path:** `backend/app/domain/salary_estimation/`

**Calculation model:** Pure function of `(inputs, rule_set_version)`. No clock, randomness, network, or environment reads in the calculation path (except `generated_at` timestamp set at API boundary).

## 2. Money Path Invariants

All monetary calculations follow Holy Bible §13.8 financial invariants:

| Invariant | Implementation |
|-----------|---------------|
| Decimal only, no float literals | `Decimal` throughout; `round_half_up` from `app.engines.money` |
| `getcontext().prec = 34` | Set in `app/engines/money.py` |
| `ROUND_HALF_UP` only | `round_half_up()` used; no Python `round()` |
| Round once at line-item boundary | Single rounding per salary figure |
| `rounding_residual_rial` surfaced | Not applicable (single figure, no line-item splits) |
| No `round()` on money | Enforced by code review |

## 3. Input Schema (EstimationInput)

| Field | Type | Constraints | Validation |
|-------|------|-------------|------------|
| `job_title` | `str` | min 1, max 100 | Non-empty |
| `experience_years` | `int` | ge 0, le 50 | Range check |
| `skills` | `list[str]` | default empty | No validation on content |
| `education` | `str \| None` | max 50, default None | Optional |
| `city` | `str` | min 1, max 50 | Normalized to lowercase |
| `employment_type` | `str` | min 1, max 50 | One of: full_time, part_time, contract, freelance |
| `seniority_level` | `str` | min 1, max 50 | Capitalized (Junior/Mid/Senior) |
| `estimated_at` | `datetime` | default now | Set at API boundary |

## 4. Calculation Algorithm

### Step 1: Market Profile Matching

The matcher (`SalaryMatcher.find_market_profile`) performs deterministic matching:

1. Normalize city to lowercase
2. Normalize job title: lowercase, strip, underscores → spaces
3. Look up normalized job title in `_JOB_TITLE_MAP`
4. Look up city + job key in `EXTENDED_MOCK_MARKET_DATA`
5. Validate seniority level matches profile
6. Validate profile meets minimum data quality (`data_volume >= 10`, `recency_days <= 180`)

**No match → `None` → engine raises `ValueError("insufficient_data: ...")` → HTTP 409 refusal.**

### Step 2: Base Salary Calculation

Base salary = median of available market sources from the matched profile:
- `jobinja_median_rial`
- `jobvision_median_rial`
- `salary_survey_median_rial`

Only sources present in the profile are included. If no values exist → `ValueError`.

### Step 3: Adjustments (Decimal Multipliers)

A fresh `SalaryAdjuster` is created per estimate:

| Factor | Logic | Multiplier |
|--------|-------|------------|
| Experience | <1 yr: 0.8; 1–3: 1.0; 4–7: 1.2; 8–15: 1.5; >15: 2.0 | Decimal |
| Skills premium | 0.1× per relevant skill (React, TypeScript, Node.js, Python, AWS, Docker) | Decimal |
| Education | None: 1.0; Bachelor: 1.1; Master/PhD: 1.2 | Decimal |
| City | Tehran/Isfahan: 1.5; others: 1.0 | Decimal |
| Employment type | contract: 0.9; part_time: 0.8; others: 1.0 | Decimal |

Adjusted salary = `round_half_up(Decimal(base) × total_factor)`

### Step 4: Range Calculation

| Confidence | Variance |
|------------|----------|
| high | ±15% |
| medium | ±25% |
| low | ±40% |

Range = `round_half_up(Decimal(primary) × (1 ± variance))`

### Step 5: Legal Minimum Wage Reference

Loaded from 1404 statutory rule set via `load_rule_set(1404)`:
- `monthly_minimum_wage_30days_rial = 103,909,680`
- Returned as `legal_minimum_wage_rial` in result
- **Reference only — never used as a floor or cap for the estimate**

### Step 6: Result Assembly

`EstimationResult` includes:
- `primary_estimate_rial` — main recommendation
- `min_salary_rial`, `max_salary_rial` — range
- `currency_unit` — always "toman" for display
- `confidence_level` — high/medium/low/insufficient_data
- `data_sources` — only sources actually present in profile
- `factors_influence` — Persian descriptions
- `legal_minimum_wage_rial` — from 1404 rules
- `rule_version` — statutory version from rule set
- `rule_set_status` — DRAFT/UNDER_REVIEW/VERIFIED/ACTIVE from rule set
- `engine_version` — "0.1.0"
- `calculation_hash` — SHA-256 of input + result
- `provenance` — traceability dict

## 5. Output Schema (EstimationResult)

All fields are required unless defaulted. `extra = "forbid"` prevents undeclared fields.

## 6. Refusal Behavior (Insufficient Data)

When market data is insufficient:
1. Matcher returns `None`
2. Estimator raises `ValueError("insufficient_data: ...")`
3. API endpoint catches `ValueError` with `insufficient_data:` prefix
4. Returns HTTP 409 with `{"error": {"code": "ESTIMATION_INSUFFICIENT_DATA", "detail": "..."}}`
5. No numeric estimate, no fabricated data sources

## 7. Provenance

Every result is traceable to:
- Calculation engine version: `0.1.0`
- Rule-set version: from `statutory_rules_1404.yaml`
- Legal data source: `source_circular_reference` from rule set
- Market data sources: only sources actually present in matched profile
- Input snapshot: captured in `provenance.profile_match`
- Calculation timestamp: `generated_at`
- Calculation hash: SHA-256 of `(job_title\|experience_years\|city\|seniority_level\|salary\|confidence)`

## 8. What the Engine Does NOT Do

- ❌ Does not use AI/ML for salary calculation
- ❌ Does not fabricate market data sources
- ❌ Does not return zeros for insufficient data
- ❌ Does not apply legal minimum wage as a floor
- ❌ Does not use float arithmetic for money
- ❌ Does not claim ACTIVE rule-set status when rule set is not verified
