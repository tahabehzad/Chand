# ADR-014 — Market salary reference data and the estimation engine

- **Document ID:** `DOC-ADR-014`
- **Status:** **Accepted** — approved by Project Owner (2026-11-18)
- **Date:** 2026-11-18 (28 Aban 1405 SH)
- **Deciders:** Project Owner, CTO, Legal Counsel (for DEC-015)
- **Related:** [`ADR-013`](ADR-013-resume-analysis-salary-estimation-tool.md) (product scope),
  [`ADR-007`](ADR-007-statutory-global-access-and-deferred-identity.md) (global reference tables),
  [`ADR-008`](ADR-008-product-scope-statutory-payroll-engine.md) (statutory engine, preserved),
  [`docs/SALARY_ESTIMATION_SPEC.md`](../SALARY_ESTIMATION_SPEC.md),
  [`docs/LABOR_MARKET_DATA_SPEC.md`](../LABOR_MARKET_DATA_SPEC.md),
  [`docs/DECISIONS_REGISTER.md`](../DECISIONS_REGISTER.md) DEC-015, DEC-016

---

## 1. Context

ADR-013 changed the product from a statutory payroll engine to a salary **estimation**
tool. The code that came with it did not estimate anything:

1. Three fabricated dictionaries (`EXTENDED_MOCK_MARKET_DATA`, `MOCK_MARKET_DATA`,
   `MOCK_MOCK_MARKET_DATA_V2`) plus a fourth copy in the SPA
   (`frontend/src/lib/salary-benchmarks.ts`) were served **as market data** and labelled
   with real brand names (Jobinja/JobVision/IranTalent) that were never contacted.
2. The published figure was built from multipliers — city ×1.20, experience ×1.10,
   seniority, education, skills — applied on top of an already-city-specific baseline,
   so a Tehran senior was raised twice for the same attribute, and none of the
   multipliers had a source.
3. `confidence_score` was computed from the size of the fabricated dictionary, so more
   invented rows produced "higher confidence".
4. Four ORM models (`CandidateEstimate`, `MarketSalaryData`, `ResumeUpload`,
   `EstimationUser`) existed with no table, no migration and no caller; the SPA rounded
   Toman by dividing the Rial figure by 10 in the display layer
   (`Math.round(value / 10)`), i.e. the screen could disagree with the response.

### 1.4 Directive: refuse instead of fabricate

When no verified observation covers a profile, the engine must return
`insufficient_data` together with the reason and the counts it measured. It must **not**
interpolate, must not fall back to a national average it did not measure, and must not
emit a number tagged with a low-but-nonzero confidence. Every published figure is
therefore traceable to a set of rows the engine can name.

## 2. Data foundation

### 2.1 Source register

`market_data_sources` records one row per source: identifier, human name, kind
(`licensed_survey`, `published_report`, `job_board`, `manual`, `synthetic`), licence
status (`licensed`, `published_report`, `manual_verified`, `unknown`), `connected`,
terms URL and notes. A source is marked `connected = true` only after a real ingestion
has stored observations from it; the register is therefore a record of what was
actually collected, not a wish list.

### 2.2 Two data kinds, never mixed

- **Kind A — observation** (`market_salary_observations`): one independent salary with
  title, family, city/province, seniority, experience, employment type, work condition,
  amount, period, currency as reported, source, collection date and validation verdict.
- **Kind B — aggregate** (`market_salary_aggregates`): a published summary. Only the
  statistics the publisher released are stored; a percentile that was not published
  stays `NULL` and is never inferred. IQR/MAD fences are computed on kind A only.

### 2.3 Licence states

`license_status` is stored per source and copied onto every row so a later licence
change cannot retroactively launder earlier rows. Rows whose licence is not one of
`licensed`, `published_report`, `manual_verified` are **rejected** at validation with
`source_not_licensed`, not silently kept.

### 2.4 Admission rule

A row may be stored only with: a source id that exists in the register, a collection
date, a positive integer amount **and** an explicit currency unit and period. The
operator tool `backend/scripts/market_data_ingest.py` refuses a file whose rows lack
any of these, refuses unknown job-family keys, and writes the same validation verdict
the estimator would compute — a row that fails is stored **with** its verdict and
reason so the rejection is auditable.

### 2.5 Sample data

The single sample module (`app/domain/salary_estimation/sample_data.py`) is labelled
`is_synthetic = true`, carries the source `synthetic-dev`, and can be loaded only when
`ESTIMATION_ALLOW_SAMPLE_DATA=true` **and** `APP_ENV=local`. Settings validation refuses
that combination in any other environment, so a production or staging deployment cannot
start with sample data on. The SPA's fabricated table was moved out of the product tree
to `frontend/src/dev/sample-market-benchmarks.ts` and is imported by no route.

## 3. Data model and repository

Three tables in migration `0007_market_salary_reference` (down-revision `0006`):

| Table | Purpose | Personal data |
| :--- | :--- | :--- |
| `market_data_sources` | source register + licence state | none |
| `market_salary_observations` | kind A rows + quality verdict | none |
| `market_salary_aggregates` | kind B published summaries | none |

They are **global reference tables without `tenant_id` or RLS**, following ADR-007's
pattern for reference data: they describe the labour market, not a tenant, and hold no
personal data — so no RLS or encryption requirement is weakened. Estimation **history**
(which profile produced which figure) *is* personal data and was therefore **not**
built; it is blocked on DEC-016 (tenancy), and the engine is pure in the meantime.

Access is confined to `app/repositories/market_data.py`
(`MarketDataRepository` protocol, SQL implementation, in-memory implementation). The
engine receives rows and returns figures; it never imports SQLAlchemy.

## 4. Validation and statistics

### 4.1 Three-tier policy

Every row gets exactly one status with reasons:

- `VALID` — used by the estimator.
- `SUSPICIOUS` — recorded, **excluded** from the published figure, counted in
  `quarantined_sample_count`, and surfaced as a warning.
- `REJECTED` — a definite defect (unit/period/zero-or-negative amount, duplicate of an
  earlier row of the same source, unlicensed source, amount three orders of magnitude
  outside its cohort); excluded and counted in `rejected_sample_count`.

A row is never removed merely for differing from its peers: a difference becomes a
finding with a reason code, and an outlier beyond the fences is `SUSPICIOUS` unless it
also breaks a hard rule.

### 4.2 Cohort-aware fences

Fences are computed **inside the row's own cohort** (job family, city, seniority) with a
fallback ladder, never with one global floor/ceiling:

| Test | Method | Effect |
| :--- | :--- | :--- |
| IQR | p25 − 1.5·IQR … p75 + 1.5·IQR | extreme → `outlier_iqr_extreme` |
| MAD | \\|x − median\\| / (1.4826·MAD) > 3.5 | robust outlier |
| Percentile | p1 … p99 of the cohort | outside the tail |
| Ratio | amount / cohort median | > 10× suspicious, > 1000× rejected |
| Magnitude | absolute plausibility floor/ceiling per period | extra zeros / wrong unit |

A 1,000-Toman monthly salary and a 1,000,000,000-Toman one are both flagged, but by
different tests and with different verdicts — the first as a hard entry error, the
second for review against its own cohort.

### 4.3 Duplicates, staleness, units, periods

Repeats (same source + family + city + seniority + amount + period) are rejected with
the first occurrence kept, so verdicts do not depend on input order. Rows older than
`ESTIMATION_MAX_DATA_AGE_DAYS` are quarantined as stale rather than dropped. Hourly and
daily figures are converted to a monthly equivalent with an explicit, recorded factor
(`PERIOD_FACTORS`) before any comparison; Toman is multiplied by 10 to Rial.

### 4.4 Cohort selection

The estimator publishes the **narrowest cohort that clears the sample floor**:
`city + seniority + employment type` → `city + seniority` → `city` → `province` →
`national` → published aggregate. The scope actually used is published in
`methodology.cohort_scope`, because a national fallback is weaker evidence and must not
look like a city-level answer.

### 4.5 Percentiles, median and quantisation

Median, p25/p75 (and p1/p99 for the fences) use linear interpolation on the sorted
sample (R-7), computed in `Decimal` from integer Rial — no float literal touches a money
path. The published range is the sample's real p25…p75, and `primary_estimate_rial` is
the real median. Each published amount is quantised to a multiple of 10 Rial with the
residual recorded in `rounding_residual_rial` (|residual| ≤ 15 Rial).

### 4.6 Currency convention

Rial is the **only** stored and computed unit (integer, `BigInteger`). A source that
reports Toman is converted at ingest (×10) and the reported unit is preserved in
`currency_unit_reported` for audit. The API returns Rial plus `currency_unit`. The SPA
renders Toman through `lib/money.ts`, which refuses a value that is not divisible by 10
and never rounds — so the display cannot disagree with the response.

## 5. Confidence

Confidence is split into the two questions a reader actually asks:

- `data_confidence` — how good the evidence is: sample size, source licence, freshness,
  cohort narrowness, dispersion.
- `prediction_confidence` — how much the published figure should be trusted for *this*
  profile: match score, cohort scope, dispersion, input completeness.
- `method_ceiling` — the best level the method can claim at all, so a large sample of
  one weak licence can never produce `high`.

`confidence_level` is the worse of the two, and `confidence_score` is a Decimal ratio in
`[0, 1]` with the per-component contributions published in
`confidence.components`/`weights`. `data_volume` no longer exists: volume is one
component of `data_confidence`, not a confidence value by itself.

## 6. API contract

`POST /api/v1/simulations/salary-estimation` returns `SalaryEstimateResponse` with
`primary_estimate_rial`, `min_salary_rial`, `median_salary_rial`, `max_salary_rial`,
`valid_sample_count`, `data_collected_at`, `data_sources`, `confidence_level`,
`confidence_score`, `market_rows`, `methodology`, `warnings` (plus quarantined/rejected
counts, distribution buckets, factors, match explanation and `calculation_hash`).

Refusals use the error envelope and are **not** 200-with-nulls:

| Situation | Status | Code |
| :--- | :--- | :--- |
| no usable cohort / below floor / no match | `409` | `ESTIMATION_INSUFFICIENT_DATA` |
| repository unreachable | `503` | `ESTIMATION_DATASTORE_UNAVAILABLE` |
| invariant broken while assembling the response | `500` | `ESTIMATION_ENGINE_ERROR` |
| request fails schema validation | `422` | `ESTIMATION_INPUT_INVALID` |

## 7. Frontend

`/salary-estimation` (route and navigation entry) replaces `/salaries` and
`/salaries/:job-:city`, which served the fabricated table. The form collects the
profile (title, experience, city, province, seniority, employment type, work condition,
description, education, skills); description and skills drive the **match**, and the
screen states that they do not change the figure. The result screen shows the primary
estimate, p25/median/p75, a distribution bar chart built from the API's own buckets,
valid/quarantined/rejected counts, data date and oldest date, sources, the two
confidence dimensions, factor explanations, the reproducible hash, and a refusal card
for 409/503 that shows no number at all. Every amount goes through `lib/money.ts`;
there is no rounding, division or multiplication of money in the SPA.

## 8. Owner decisions required

| ID | Question | Status | Why it blocks |
| :--- | :--- | :--- | :--- |
| **DEC-015** | Which market-data sources may be collected, under which licence, and who signs off each source before it is marked `connected`? | **OPEN — BLOCKING (data volume only)** | With no licensed source, every production estimate is `insufficient_data`. That is the correct behaviour, but the product cannot answer a real question until a source is approved. DEC-007/DEC-008 (REJECTED, "out of scope") conflict with ADR-013's market-data basis and need the owner to reconcile them explicitly. |
| **DEC-016** | Is estimation **history** tenant-scoped (RLS + `tenant_id`) or a single-tenant audit log, and what is its retention? | **OPEN — BLOCKING (history feature)** | Storing which profile produced which figure is personal data; ADR-007/`AGENTS.md` §2 forbid adding that without owner approval. History is therefore not implemented. |
| **DEC-017** | Does the owner accept the cohort rule (no monetary multiplier for city/experience/seniority/education/skill) as the published methodology? | **OPEN — NON-BLOCKING** | The rule is implemented and documented; approval turns ADR-014 from Proposed to Accepted. |

Nothing in this ADR changes RLS, `tenant_id`, encryption or the statutory engines.

## 9. Consequences

- **Preserved:** statutory payroll engine and its endpoints, the verified 1404 rule set,
  Decimal/ROUND_HALF_UP money rules, all prior migrations, tests and contracts. The
  legal minimum wage is read as an optional *reference* and its absence never fails an
  estimate.
- **Removed:** `mock_data.py`, `adjuster.py` (multipliers), the four dead ORM models, the
  SPA's fabricated table and its `/salaries` routes.
- **Verification:** `pytest` (domain estimation, e2e API, repository, config, migration
  table-set), `ruff check`, `mypy --strict app`, `vitest`, `tsc --noEmit`, `vite build`.
  The DB-dependent manager/work-profile suites cannot run on this host (the migration
  fixture fails identically with and without migration `0007`), so they are reported as
  not run, not as passing.
- **Non-claims:** no real market data has been collected; no accuracy figure is claimed;
  the estimates are advisory and are not a statutory minimum, an offer or a legal
  opinion.
- **Rollback:** drop `0007` (down-revision `0006`), delete the three tables' models, and
  restore the previous endpoint/router; no other table is touched.
