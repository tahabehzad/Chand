# Labor Market Data Specification

**Document ID:** `DOC-LABOR-MARKET-SPEC-001`  
**Status:** Draft — pending owner approval  
**Date:** 17 Aban 1405 SH (2026-11-17)  
**Related:** `SALARY_ESTIMATION_SPEC.md`, `DOC-FUNC-REQ-001`

---

## 1. Purpose

Define how Iranian labor market salary data is acquired, stored, verified, and used for salary estimation. The product must not present unsupported or fabricated market salaries as verified facts.

## 2. Data Sources (Priority Order)

| Priority | Source | Type | Reliability | Notes |
|:---|:---|:---|:---|:---|
| 1 | Licensed salary surveys (Iranian HR/consulting firms) | Licensed | High | Preferred if available |
| 2 | Job board job postings (Jobinja, JobVision, etc.) | Public job ads | Medium | Only if Terms of Service permit |
| 3 | Published salary reports (annual compensation reports) | Public reports | Medium | Year-specific |
| 4 | Manual curation by manager | Manager input | Low | Last resort; marked as manual |

## 3. Data Model (Market Salary)

| Field | Type | Description |
|:---|:---|:---|
| `id` | UUID | Primary key |
| `job_title` | string | Normalized job title (e.g., "برنامه‌نویس نرم‌افزار") |
| `city` | string | City (e.g., "تهران") |
| `seniority_level` | string | `junior` \| `mid` \| `senior` |
| `employment_type` | string | `full_time` \| `part_time` \| `contract` \| `freelance` |
| `min_salary_rial` | integer | Minimum observed salary |
| `max_salary_rial` | integer | Maximum observed salary |
| `median_salary_rial` | integer | Median observed salary |
| `sample_size` | integer | Number of observations |
| `source` | string | Data source name |
| `source_url` | string | URL of source (if applicable) |
| `collected_at` | timestamp | When data was collected |
| `confidence` | string | `high` \| `medium` \| `low` |
| `is_manual` | boolean | True if manually entered |

## 4. Acquisition Rules

| Rule | Description |
|:---|:---|
| R-01 | No scraping of job boards that prohibit it in Terms of Service (DEC-007/008 rejection stands) |
| R-02 | All market data must carry a source attribution |
| R-03 | Data older than 12 months is marked as stale |
| R-04 | Manual entries must be marked `is_manual = true` |
| R-05 | When insufficient data exists for a role/city/seniority combination, the system returns `insufficient_data` |

## 5. Data Freshness

- Market data should be refreshed at least annually.
- Stale data (>12 months) carries lower confidence.
- The system displays `collected_at` or "آخرین به‌روزرسانی" on the result page.

## 6. Assumptions (Unresolved)

| ID | Assumption | Owner Decision Needed |
|:---|:---|:---|
| M-01 | Initial market data will be seeded manually or via licensed source | Yes |
| M-02 | Whether to attempt job board scraping (subject to ToS review) | Yes |
| M-03 | Data refresh schedule and automation | Yes |

---

## 7. Implementation status — ADR-014, 2026-11-18

| Requirement | Where it is enforced |
|:---|:---|
| Every record has a source, collection date, period and currency unit | `market_data_sources` / `market_salary_observations`; `scripts/market_data_ingest.py` refuses a CSV row without them |
| Licence state is stored, not assumed | `license_status` on the source **and** copied onto each row; rows with `unknown` are rejected as `source_not_licensed` |
| Observations (kind A) and aggregates (kind B) are never mixed | separate tables and separate domain dataclasses; IQR/MAD run on kind A only, and an unpublished percentile stays `NULL` |
| Manual owner-verified data is allowed next to licensed data | `manual_verified` is an accepted licence state and is reported as such in `data_sources` |
| Stale data never silently counts | quarantined as `stale_source` beyond `ESTIMATION_MAX_DATA_AGE_DAYS`, counted in `quarantined_sample_count` |
| No source is claimed without a real ingestion | a source is `connected = true` only after `store_observations` stored rows from it; `--census` prints the actual holdings per family |
| Sample data cannot reach production | `is_synthetic` rows are rejected unless `ESTIMATION_ALLOW_SAMPLE_DATA=true` **and** `APP_ENV=local`; settings validation refuses the combination in every other environment |

**Currently connected sources: none.** No licensed report, job board or manual dataset has
been ingested — DEC-015 is open. The `--census` command reports zero observations, and
every production estimate therefore refuses with `insufficient_data`. This is the state of
the system, not a placeholder figure.
