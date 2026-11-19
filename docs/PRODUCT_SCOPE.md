# Product Scope — Salary Estimation Tool

**Document ID:** `DOC-PRODUCT-SCOPE-001`  
**Status:** Active — approved by Project Owner  
**Date:** 18 Aban 1405 SH (2026-11-18)  
**Supersedes:** ADR-008 product scope clauses; ADR-010 product direction clauses (partially)

---

## 1. Product Mission

A single manager enters an individual's employment history, resume, skills, education, job title, experience, location, and other relevant professional information. The system analyzes the information and estimates an appropriate monthly salary based on actual Iranian labor market conditions.

The primary objective is to help an employer determine how much salary to offer a potential employee.

## 2. What the Product IS

| Capability | Description |
|:---|:---|
| Resume/career information intake | Multi-step Persian form: job title, experience years, previous jobs, skills and levels, education, certifications, city, employment type, seniority level |
| Resume file upload | PDF or text upload for automatic information extraction (v2 priority) |
| Market-based salary estimation | Comparison of candidate profile against Iranian job-market data |
| Salary range output | Minimum and maximum suggested monthly salary (Rial/Toman) |
| Primary estimate | One recommended salary figure |
| Explanation of estimate | Factors that influenced the estimate (experience, skills, city, etc.) |
| Confidence indicator | Level of confidence and data reliability note |
| Estimate history | Save and view previous estimations |
| Legal minimum wage reference | Displayed as separate reference, not mixed with market estimate |
| PDF export (post-v1) | Export estimate result to PDF |

## 3. What the Product IS NOT (Non-Goals)

| Excluded Capability | Reason |
|:---|:---|
| Accounting application | Not a salary estimation need |
| Payroll management system | No net-pay calculation, no payslip |
| Employee management platform | No employee records, no org management |
| Attendance management | No time tracking |
| Payslip generator | No payslip output |
| Tax or insurance calculator | No SSO, income tax, or deduction computation |
| Statutory payroll engine | 1404/1405 rule sets not used for estimation |
| Multi-tenant security | Single manager only; no tenant_id, no RLS |
| Multi-role authentication | One manager only; no MFA, no sessions |
| Document forensics / OCR | Out of scope for salary estimation |
| Live job-board scraping | Only if Terms of Service permit; otherwise manual/licensed data |

## 4. Primary User

**One manager** — the only user type. Employees are subjects of estimation, not system users.

## 5. Output Specification

Each estimation produces:

| Field | Type | Description |
|:---|:---|:---|
| `primary_estimate_rial` | integer | Recommended monthly salary in Rial |
| `min_salary_rial` | integer | Minimum of suggested range |
| `max_salary_rial` | integer | Maximum of suggested range |
| `currency_unit` | string | `'rial'` or `'toman'` |
| `factors_influence` | list | Factors that influenced the estimate |
| `confidence_level` | string | `'high'`, `'medium'`, `'low'`, or `'insufficient_data'` |
| `data_sources` | list | Market data sources used |
| `estimated_at` | timestamp | When the estimate was generated |
| `legal_minimum_wage_rial` | integer | Legal minimum wage as reference (separate from estimate) |

## 6. Relationship to Existing Code

| Existing Component | Status in New Scope |
|:---|:---|
| Statutory payroll engine (`backend/app/engines/`) | Preserved as technical code; not the product |
| Gross-to-net API endpoint | Preserved as technical code; not the product path |
| Frontend RTL/Persian components | Reusable for estimation UI |
| Money formatting (Decimal, ROUND_HALF_UP) | Reusable wherever money is displayed |
| Testing tooling (vitest, pytest, ruff, mypy) | Reusable |
| ADR-008 invariants (no float literals, per-field provenance) | Preserved as good practice where money is touched |
| ADR-010 guardrails (no production claims, loopback-only) | Preserved as good practice |

## 7. Out-of-Scope but Preserved

The following are **not** part of the salary estimation product but remain in the repository as historical or technical code:

- All statutory payroll engine modules (SSO, tax, severance, Eydi, CTC, termination)
- Statutory rule seeds (`statutory_rules_1404.yaml`, `statutory_rules_1405.yaml`)
- Multi-tenant database migrations (0001–0003)
- Blind indexing and AES-256-GCM security modules
- Compensation advisory module (ADR-009)

None of these are deleted by this scope document. They remain for possible future use but are **not** active product scope.
