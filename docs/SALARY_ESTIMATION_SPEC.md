# Salary Estimation Specification

**Document ID:** `DOC-SALARY-EST-SPEC-001`  
**Status:** Active — approved by Project Owner (ADR-014)  
**Date:** 18 Aban 1405 SH (2026-11-18)  
**Related:** `DOC-FUNC-REQ-001`, `DOC-NONFUNC-REQ-001`, `LABOR_MARKET_DATA_SPEC.md`, `AI_ANALYSIS_SPEC.md`

---

## 1. Estimation Basis

The primary basis for salary estimation is **actual Iranian labor market data**, not statutory minimum wage tables. Statutory minimum wage is shown only as a separate reference value.

### Factors Considered

| Factor | Source | Weight Concept |
|:---|:---|:---|
| Job title | Market data (Jobinja, JobVision, salary surveys) | Primary driver of salary band |
| Professional experience | Candidate input | Adjusts position within band |
| Skills and expertise | Candidate input + AI extraction | Adjusts premium/discount |
| Seniority level | Candidate input (Junior/Mid/Senior) | Band selection |
| Education | Candidate input | Secondary adjustment |
| Location (city) | Candidate input + market data | Geographic adjustment |
| Employment type | Candidate input | Full-time vs part-time vs contract |
| Market demand | Market data source | Dynamic adjustment |

## 2. Estimation Output

Each estimation produces:

| Field | Type | Example |
|:---|:---|:---|
| `primary_estimate_rial` | integer | 25000000 |
| `min_salary_rial` | integer | 20000000 |
| `max_salary_rial` | integer | 30000000 |
| `currency_unit` | string | `"toman"` or `"rial"` |
| `factors_influence` | list of strings | `["تجربه ۵ سال", "مهارت React", "شهر تهران", "سطح Senior"]` |
| `confidence_level` | string | `"high"` \| `"medium"` \| `"low"` \| `"insufficient_data"` |
| `data_sources` | list of strings | `["Jobinja", "JobVision", "Salary Survey 1405"]` |
| `legal_minimum_wage_rial` | integer | 5541850 (daily) × 30 = 166255500 (monthly, reference only) |
| `estimated_at` | timestamp | ISO-8601 |
| `estimation_version` | string | `"v1.0"` |

## 3. Estimation Methodology (High-Level)

```
Candidate Profile
    → Match against market data (job title + city + seniority)
    → If match found:
        → Base salary = market median for matched profile
        → Adjust for experience years (±X% per year)
        → Adjust for skill levels (premium for in-demand skills)
        → Adjust for education (bonus for relevant degree)
        → Adjust for city (cost-of-living factor)
        → Adjust for employment type (contract vs full-time)
        → Compute range: base × (1 ± variance)
        → Compute confidence based on data volume and recency
    → If no match:
        → Return "insufficient_data" with no numeric estimate
    → Output: range, primary estimate, factors, confidence, sources
```

### Rules

- **No fabricated data:** If market data is insufficient, the system must not invent a number.
- **No statutory enforcement:** Minimum wage is reference only, not a floor for the estimate.
- **Traceability:** Every figure must be traceable to its source data.
- **AI boundary:** AI may extract skills and experience from resumes, but salary computation uses market data + calculation logic, not LLM guesswork alone.

## 4. Confidence Levels

| Level | Meaning |
|:---|:---|
| `high` | Sufficient recent market data for exact role + city + seniority |
| `medium` | Some market data; close role or nearby city |
| `low` | Limited data; broad role category only |
| `insufficient_data` | No usable market data; estimate refused |

## 5. Assumptions (Unresolved)

| ID | Assumption | Owner Decision Needed |
|:---|:---|:---|
| E-01 | Market data will be seeded manually or via licensed source | Yes |
| E-02 | AI model for resume parsing will be local or API-based | Yes |
| E-03 | Estimation algorithm will be rule-based (not pure ML) | Yes |
| E-04 | Data refresh frequency for market salaries | Yes |

---

## 6. Implementation status — ADR-014, 2026-11-18

**The "Weight Concept" column of §1 is superseded.** It described per-factor multipliers,
and the delivered engine applies none: a city/experience/seniority/education/skill
multiplier on top of an already city-specific baseline double-counted the same attribute
and had no source. The published methodology is the cohort rule below.

| Aspect | Delivered behaviour |
|:---|:---|
| Comparison group | Narrowest cohort that clears the sample floor: `city + seniority + employment_type` → `city + seniority` → `city` → `province` → `national` → published aggregate. Reported in `methodology.cohort_scope`. |
| Primary estimate | The cohort's **real median** (R-7 interpolation, `Decimal`). |
| Range | The cohort's real p25…p75. No symmetric ± band, no invented floor. |
| Job matching | Title, description and skills against an internal taxonomy of 10 families, Persian/English aliases; unmatched profiles are **refused** (`no_job_family_match`), ambiguous ones publish their competing candidates and reasons. |
| Education, skills, certifications | Used for matching and explanation only; they change no amount (stated on screen). |
| Sample floor | `ESTIMATION_MIN_VALID_SAMPLES` (default 5) valid rows and confidence ≥ 0.20; below either, the response is `insufficient_data` with counts. |
| Confidence | Split into `data_confidence` and `prediction_confidence` with `method_ceiling`; `confidence_level` is the worse of the two; components and weights are published. |
| Stale / duplicate / unlicensed rows | Quarantined or rejected with a reason code; excluded from the figure and counted in the response. |
| Currency | Stored and computed in Rial only; Toman sources are converted at ingest (×10) with the reported unit preserved; published amounts are exact multiples of 10 Rial with `rounding_residual_rial`. |
| Refusal transport | `409 ESTIMATION_INSUFFICIENT_DATA`, `503 ESTIMATION_DATASTORE_UNAVAILABLE`, `500 ESTIMATION_ENGINE_ERROR`, `422 ESTIMATION_INPUT_INVALID`; never a 200 carrying a made-up number or nulls presented as a figure. |
| Data basis | No real source is connected (DEC-015). Sample data exists only behind `ESTIMATION_ALLOW_SAMPLE_DATA=true` **and** `APP_ENV=local`, labelled `synthetic-dev`. |

Assumptions E-01…E-04 above remain open owner questions; E-03 is partially answered — the
method is rule/statistics-based, not a trained model.
