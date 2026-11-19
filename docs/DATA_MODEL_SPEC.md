# Data Model Specification — Salary Estimation Tool

**Document ID:** `DOC-DATA-MODEL-SPEC-001`  
**Status:** Draft — pending owner approval  
**Date:** 17 Aban 1405 SH (2026-11-17)  
**Related:** `DOC-FUNC-REQ-001`, `LABOR_MARKET_DATA_SPEC.md`, `AI_ANALYSIS_SPEC.md`

---

## 1. Database Philosophy

Simplified from the existing project: no `tenant_id`, no RLS, no `FORCE ROW LEVEL SECURITY`, no multi-tenant security foundation. Single manager access only. Standard PostgreSQL access controls apply.

## 2. Tables

### 2.1 `candidate_estimates`

Stores each salary estimation performed by the manager.

| Column | Type | Nullable | Description |
|:---|:---|:---|:---|
| `id` | UUID | NO | Primary key |
| `job_title` | VARCHAR(200) | NO | Candidate's job title |
| `experience_years` | INTEGER | NO | Years of professional experience |
| `seniority_level` | VARCHAR(20) | NO | `junior` \| `mid` \| `senior` |
| `employment_type` | VARCHAR(20) | NO | `full_time` \| `part_time` \| `contract` \| `freelance` |
| `city` | VARCHAR(100) | NO | City of work |
| `skills` | JSONB | NO | List of skills with levels |
| `education` | VARCHAR(200) | YES | Education level and field |
| `certifications` | JSONB | YES | List of certifications |
| `previous_jobs` | JSONB | YES | List of previous employers/roles |
| `min_salary_rial` | INTEGER | NO | Minimum of suggested range |
| `max_salary_rial` | INTEGER | NO | Maximum of suggested range |
| `primary_estimate_rial` | INTEGER | NO | Primary recommended estimate |
| `currency_unit` | VARCHAR(10) | NO | `'rial'` \| `'toman'` |
| `factors_influence` | JSONB | NO | Factors that influenced estimate |
| `confidence_level` | VARCHAR(20) | NO | `high` \| `medium` \| `low` \| `insufficient_data` |
| `data_sources` | JSONB | NO | Market data sources used |
| `legal_minimum_wage_rial` | INTEGER | YES | Legal minimum wage as reference |
| `created_at` | TIMESTAMPTZ | NO | When estimate was created |
| `updated_at` | TIMESTAMPTZ | YES | Last update |

### 2.2 `market_salary_data`

Reference data from Iranian labor market sources.

| Column | Type | Nullable | Description |
|:---|:---|:---|:---|
| `id` | UUID | NO | Primary key |
| `job_title` | VARCHAR(200) | NO | Normalized job title |
| `city` | VARCHAR(100) | NO | City |
| `seniority_level` | VARCHAR(20) | NO | `junior` \| `mid` \| `senior` |
| `employment_type` | VARCHAR(20) | YES | Employment type |
| `min_salary_rial` | INTEGER | NO | Minimum observed |
| `max_salary_rial` | INTEGER | NO | Maximum observed |
| `median_salary_rial` | INTEGER | NO | Median observed |
| `sample_size` | INTEGER | NO | Number of observations |
| `source` | VARCHAR(100) | NO | Data source name |
| `source_url` | TEXT | YES | Source URL |
| `collected_at` | TIMESTAMPTZ | NO | Collection date |
| `confidence` | VARCHAR(20) | NO | `high` \| `medium` \| `low` |
| `is_manual` | BOOLEAN | NO | True if manually entered |
| `is_stale` | BOOLEAN | NO | True if older than 12 months |

### 2.3 `resume_uploads` (v2 — optional)

Stores uploaded resume files (metadata only; file bytes stored separately).

| Column | Type | Nullable | Description |
|:---|:---|:---|:---|
| `id` | UUID | NO | Primary key |
| `estimate_id` | UUID | YES | FK to candidate_estimates |
| `file_name` | VARCHAR(255) | NO | Original file name |
| `file_url` | TEXT | NO | Storage path/URL |
| `file_size_bytes` | INTEGER | NO | File size |
| `mime_type` | VARCHAR(50) | NO | `application/pdf` \| `text/plain` |
| `extracted_skills` | JSONB | YES | AI-extracted skills |
| `extracted_experience_years` | INTEGER | YES | AI-extracted experience |
| `extracted_education` | VARCHAR(200) | YES | AI-extracted education |
| `ai_confidence` | VARCHAR(20) | YES | AI confidence level |
| `requires_manager_review` | BOOLEAN | NO | True if manager review needed |
| `created_at` | TIMESTAMPTZ | NO | Upload time |

### 2.4 `users` (simplified — v1)

Single manager user.

| Column | Type | Nullable | Description |
|:---|:---|:---|:---|
| `id` | UUID | NO | Primary key |
| `email` | VARCHAR(255) | NO | Manager email |
| `password_hash` | VARCHAR(255) | NO | Hashed password |
| `display_name` | VARCHAR(200) | NO | Display name |
| `created_at` | TIMESTAMPTZ | NO | Account creation |
| `is_active` | BOOLEAN | NO | Account active status |

## 3. Relationships

```
candidate_estimates 1:N resume_uploads (via estimate_id)
market_salary_data 1:N (reference; no FK to estimates)
users 1:N candidate_estimates (future; manager who created estimate)
```

## 4. Indexes

| Table | Index | Columns | Purpose |
|:---|:---|:---|:---|
| `candidate_estimates` | `idx_estimates_created_at` | `created_at DESC` | Recent estimates first |
| `candidate_estimates` | `idx_estimates_job_city` | `job_title, city` | Lookup by role+city |
| `market_salary_data` | `idx_market_job_city_level` | `job_title, city, seniority_level` | Fast market lookup |
| `market_salary_data` | `idx_market_collected_at` | `collected_at DESC` | Fresh data first |
| `resume_uploads` | `idx_resumes_estimate_id` | `estimate_id` | Join to estimates |

## 5. Simplifications vs Existing Project

| Existing Feature | New Approach | Reason |
|:---|:---|:---|
| `tenant_id` on all tables | Removed | Single manager only |
| `FORCE ROW LEVEL SECURITY` | Removed | No tenancy |
| AES-256-GCM field encryption | Removed | Resume data not high-sensitivity PII |
| HMAC-SHA256 blind indexing | Removed | No National ID/mobile/Sheba storage |
| Multi-role schema (7 roles) | Removed | Single manager |
| Statutory rule-set tables | Removed | Not used for estimation |

## 6. Assumptions (Unresolved)

| ID | Assumption | Owner Decision Needed |
|:---|:---|:---|
| DM-01 | PostgreSQL as database (simplified, no RLS) | Yes |
| DM-02 | Resume files stored in local filesystem or object storage | Yes |
| DM-03 | Whether to keep existing migration system (Alembic) or simplify | Yes |

---

## 7. Implemented market-salary schema (migration `0007_market_salary_reference`, 2026-11-18)

Three **global reference** tables, following ADR-007's pattern for reference data
(no `tenant_id`, no RLS, no encrypted columns) because they describe the labour
market and hold no personal data:

| Table | Key columns |
|:---|:---|
| `market_data_sources` | `id`, `name`, `kind`, `license_status`, `connected`, `terms_url`, `notes` |
| `market_salary_observations` | `id`, `family_key`, `job_title_reported`, `city`, `province`, `seniority_level`, `experience_years`, `employment_type`, `work_condition`, `amount_rial`, `period`, `currency_unit_reported`, `source_id`, `source_url`, `license_status`, `collected_at`, `is_synthetic`, `data_quality_status`, `quality_reason` |
| `market_salary_aggregates` | `id`, `family_key`, `city`, `province`, `seniority_level`, `employment_type`, `median_salary_rial`, `min_salary_rial`, `max_salary_rial`, `p25_salary_rial`, `p75_salary_rial`, `sample_size`, `period`, `currency_unit_reported`, `source_id`, `collected_at`, `is_synthetic` |

Notes:

- `amount_rial` and every salary column are `BigInteger` Rial; a Toman source is converted
  at ingest and its reported unit kept in `currency_unit_reported`.
- `data_quality_status` / `quality_reason` make the VALID/SUSPICIOUS/REJECTED verdict and
  its reasons auditable per row.
- **Estimation history is deliberately absent.** Storing which profile produced which
  figure is personal data and needs a tenancy decision (DEC-016); no table was created.
- The four dead models of the pre-ADR-014 code (`CandidateEstimate`, `MarketSalaryData`,
  `ResumeUpload`, `EstimationUser`) were removed: they had no migration and no caller.
