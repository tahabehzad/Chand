# Functional Requirements — Salary Estimation Tool

**Document ID:** `DOC-FUNC-REQ-001`  
**Status:** Draft — pending owner approval  
**Date:** 17 Aban 1405 SH (2026-11-17)  
**Related:** `DOC-PRODUCT-VISION.md`, `DOC-PRODUCT-SCOPE.md`

---

## 1. Functional Requirements

| ID | Requirement | Priority |
|:---|:---|:---|
| FR-01 | The system shall provide access for exactly one manager user type. No other user roles (HR, accountant, employee) shall exist in v1. | Must |
| FR-02 | The manager shall enter candidate information through a multi-step Persian form (not one long page). | Must |
| FR-03 | The form shall collect: job title, years of experience, previous jobs, skills and skill levels, education and field, certifications, city/location, employment type, seniority level (Junior/Mid/Senior). | Must |
| FR-04 | The system shall allow uploading a resume file (PDF or text) and extract relevant information automatically. Priority: nice-to-have for v1, must for v2. | Should |
| FR-05 | The system shall analyze the entered information and produce: (a) a suggested salary range (min–max in Iranian Rial/Toman), (b) a primary recommended estimate, (c) the factors that influenced the estimate, (d) a confidence level or "insufficient data" notice. | Must |
| FR-06 | The system shall compare candidate data against real Iranian job-market data (e.g., Jobinja, JobVision, salary surveys, licensed reports). | Must |
| FR-07 | If market data is insufficient for a role/location, the system shall state that clearly and not provide a fabricated estimate. | Must |
| FR-08 | The system shall display the estimate result on a clean, organized Persian page. | Must |
| FR-09 | The manager shall be able to save an estimate result and view previously saved estimates. | Must |
| FR-10 | The system shall show the legal minimum wage as a separate reference value (not mixed with the market estimate). | Should |
| FR-11 | The system shall support PDF export of the estimate result. Priority: post-v1. | Could |
| FR-12 | The system shall use AI to analyze resumes, identify skills and levels, and compare with market data — combined with calculation logic, not LLM guesswork alone. | Must |
| FR-13 | The system shall not generate fake or unsupported salary statistics. All market figures must be traceable to their sources. | Must |

## 2. User Stories

1. **As a manager**, I want to enter a candidate's information step by step so that I don't feel overwhelmed by a long form.
2. **As a manager**, I want to see a suggested salary range and a primary estimate so that I can make a job offer decision.
3. **As a manager**, I want to know which factors (experience, skills, city, seniority) influenced the estimate so that I can trust the result.
4. **As a manager**, I want to see my previous estimates so that I can compare candidates over time.
5. **As a manager**, I want the system to tell me honestly when there isn't enough market data for a role, so I don't make decisions on fabricated numbers.
6. **As a manager**, I want to upload a resume file (PDF/text) so that I don't have to type all information manually (v2).

## 3. Data Flow (High-Level)

```
Manager input (form or resume file)
    → Resume parser (v2) or direct form capture
    → Candidate profile (job title, experience, skills, education, city, etc.)
    → Market data lookup (job title + city + seniority level)
    → Estimation engine (market data + calculation logic + AI analysis)
    → Output: range, primary estimate, factors, confidence, sources
    → Save to history (optional)
    → Display result page
    → PDF export (v2, optional)
```

## 4. Assumptions (Not Yet Confirmed)

| ID | Assumption | Needs Confirmation |
|:---|:---|:---|
| A-01 | Market salary data will be seeded manually or via licensed source (not scraped from job boards if ToS prohibits) | Owner decision needed |
| A-02 | AI analysis will use a local or API-based LLM with structured output, not unconstrained generation | Owner decision needed |
| A-03 | Estimate history will be stored in PostgreSQL (simplified, no RLS) | Owner decision needed |
| A-04 | PDF export will use a server-side library or browser print | Owner decision needed |
