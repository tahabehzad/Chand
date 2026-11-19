# PRODUCT_SCOPE_AND_REQUIREMENTS.md

Pish Hesabdari — Product Scope and MVP Requirements

## 1. Product Identity

Pish Hesabdari is a tool that helps a company manager determine an appropriate monthly base salary for a new employee based on the employee's information and professional background.

**Core workflow:** Manager enters candidate information → System analyzes employment conditions → Calculates and recommends salary → Manager sees result and calculation details.

**Not:** a general accounting application, complete HR suite, payroll administration platform, or market salary statistics website.

## 2. Primary User

**Company manager / administrator** — single role. No employee accounts, self-service portals, or complex permission systems unless existing verified requirements explicitly demand them.

## 3. Core Input: Candidate Information

The manager enters information about a candidate. All fields are validated at the domain level.

| Field | Required | Purpose / Effect on Result | Validation |
|-------|----------|---------------------------|------------|
| Job title | Yes | Maps to market data profile; different titles yield different estimates | Non-empty string, max 100 chars; must match known market profile (otherwise insufficient_data refusal) |
| Experience years | Yes | Affects experience multiplier (0.8× to 2.0×) | Integer 0–60 |
| Seniority level | Yes | Must match market profile seniority; affects base salary | One of: junior, mid, senior |
| Employment type | Yes | Affects multiplier: full_time=1.0, part_time=0.8, contract=0.9, freelance=1.0 | One of: full_time, part_time, contract, freelance |
| City | Yes | Affects cost-of-living factor: Tehran/Isfahan=1.5, others=1.0; also used for market data lookup | Non-empty string, normalized to lowercase |
| Currency unit | Yes | Display unit: rial or toman | One of: rial, toman |
| Skills | No | Skills premium: 0.1× per relevant skill (React, TypeScript, Node.js, Python, AWS, Docker) | Array of strings from predefined set |
| Education | No | Education bonus: Bachelor=1.1, Master/PhD=1.2 | String, max 50 chars |

**Fields deliberately excluded:** National ID, mobile number, Sheba number, salary history (not needed for base salary recommendation), dependents, marital status (not material to base salary determination).

## 4. Core Output: Three Salary Concepts

### A. Legal Minimum Monthly Base Salary

Loaded from verified 1404 statutory rule set (`backend/data/seeds/statutory_rules_1404.yaml`):
- Value: 103,909,680 Rial per month (30 days)
- Source: Official circular referenced in rule set
- Status: REFERENCE ONLY — displayed as reference, never as a floor or cap for the estimate
- Currency: Rial (internal), convertible to Toman for display

### B. Market-Based Recommended Monthly Base Salary

Calculated from:
- Market data profiles (Jobinja, JobVision, Salary Survey) with median values
- Candidate-specific adjustments (experience, skills, education, city, employment type)
- Range: ±15–40% around primary estimate based on confidence level
- Confidence: high / medium / low / insufficient_data

If insufficient market data exists for the role/city/seniority combination → HTTP 409 refusal with `ESTIMATION_INSUFFICIENT_DATA` error code. No fabricated numbers.

### C. Agreed Monthly Base Salary

Distinct from legal minimum and market recommendation. Manager records the agreed salary separately. Not part of the current MVP calculation path (decision recording deferred to next stage per product scope).

## 5. Result Explanation

Every result includes:
- Calculation engine version (0.1.0)
- Rule-set version (from 1404 statutory rules)
- Calculation hash (SHA-256 of input + result)
- Generated timestamp
- Data sources actually used (not fabricated)
- Confidence level
- Influencing factors (Persian)
- Legal minimum wage reference

## 6. Insufficient Data Behavior

When market data is unavailable for the requested combination:
- HTTP 409 Conflict
- Error code: `ESTIMATION_INSUFFICIENT_DATA`
- No numeric estimate returned
- No fabricated data sources claimed
- Message in Persian explaining the limitation

## 7. MVP Boundaries

### In Scope (MVP)
- Candidate information form (Persian, RTL)
- Backend API contract (POST /api/v1/simulations/salary-estimation)
- Salary calculation engine (Decimal, rule-based)
- Legal minimum wage from 1404 rule set (reference only)
- Market-based recommendation with traceable data
- Insufficient data refusal
- Result display with explanation and provenance

### Out of Scope (Next Stage / Future)
- Agreed salary recording and decision history (P1 next stage)
- Authentication and authorization (D-02 OPEN)
- Employee self-service
- Multi-tenant RLS
- PDF generation
- Background job queue (ADR-005 proposed, not accepted)
- AI-derived resume parsing (optional, not required for MVP)

## 8. Acceptance Criteria

- Manager can start a new salary assessment
- Manager can enter required candidate information with validation
- Frontend and backend use consistent API contract
- Legal salary calculated from versioned 1404 rules
- Market-based recommendation supported by traceable data
- Agreed salary kept distinct (not silently conflated)
- Result displays legal minimum, market recommendation, and explanation
- Insufficient data communicated honestly (409 refusal)
- Assessment result persisted (API response returned)
