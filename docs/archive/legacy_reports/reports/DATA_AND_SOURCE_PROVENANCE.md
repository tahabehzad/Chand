# DATA_AND_SOURCE_PROVENANCE.md

Data and Source Provenance — Pish Hesabdari

## 1. Legal Data

| Attribute | Value | Source | Verification |
|-----------|-------|--------|--------------|
| Legal year | 1404 SH | `backend/data/seeds/statutory_rules_1404.yaml` | Verified against seed file |
| Monthly minimum wage (30 days) | 103,909,680 Rial | `statutory_rules_1404.yaml` | Verified |
| Currency | Rial | Seed file | Verified |
| Effective component | Monthly base salary (not total compensation) | Seed file | Verified |
| Rule set status | From `rule_set_status` field | Seed file | Verified |
| Source circular | From `source_circular_reference` | Seed file | Verified |
| Calculation method | Pure function, no clock/random/network | Code review | Verified |

**Rule set file:** `backend/data/seeds/statutory_rules_1404.yaml`
**Loader:** `backend/app/engines/rules.py: load_rule_set(1404)`

**Usage in engine:** Legal minimum wage is loaded and returned as `legal_minimum_wage_rial` in the result. It is REFERENCE ONLY — never used as a floor or cap for the market-based estimate.

## 2. Market Data

| Attribute | Value | Status |
|-----------|-------|--------|
| Data sources | Jobinja, JobVision, Salary Survey | Only sources actually present in matched profile are reported |
| Data type | Median salary in Rial per city/job/seniority | Mock seed data |
| Coverage | Tehran (3 profiles), Saveh (2 profiles), Isfahan (1 profile) | Limited — insufficient for production use |
| Data volume | 30–800 samples per profile | Mock values |
| Recency | 30–150 days | Mock values |
| Provenance | `market_data_seed` | Clearly labeled as seed data |

**Market data file:** `backend/app/domain/salary_estimation/salary_estimator.py` (MOCK_MARKET_DATA constant) and `matcher.py` (EXTENDED_MOCK_MARKET_DATA constant)

**Provenance transparency:** The `data_sources` field in `EstimationResult` lists only sources that have non-null values in the matched profile. No sources are fabricated.

**Limitation:** Market data is mock seed data, not from a licensed market data repository. DEC-01 (MarketDataRepository) remains open. Production use requires a licensed data source.

## 3. Provenance Fields in Result

Every `EstimationResult` includes:

```json
{
  "provenance": {
    "profile_match": "city/seniority/job_title",
    "data_source": "market_data_seed",
    "rule_year": "1404",
    "rule_source": "source_circular_reference_from_seed"
  },
  "calculation_hash": "sha256_hex_prefix_16_chars",
  "engine_version": "0.1.0",
  "rule_version": "from_statutory_rules_1404",
  "rule_set_status": "from_rule_set",
  "generated_at": "ISO_8601_timestamp"
}
```

## 4. Data Quality Thresholds

| Threshold | Value | Purpose |
|-----------|-------|---------|
| Minimum data volume | 10 samples | Profile rejected below this |
| Maximum recency | 180 days | Profile rejected if data older |
| Minimum confidence for range | 20 score points | Below → insufficient_data |

## 5. Known Limitations

1. **Mock market data:** Not from a licensed repository. DEC-01 open.
2. **Limited coverage:** Only Tehran, Saveh, Isfahan have profiles. Other cities return 409.
3. **Limited job titles:** Only 5 job titles mapped. Unknown titles return 409.
4. **Rule set status:** Loaded from seed; may be DRAFT/UNDER_REVIEW, not necessarily ACTIVE.

## 6. What Is NOT Claimed

- ❌ No claim that external market APIs were called
- ❌ No claim that rule set is ACTIVE unless the seed says so
- ❌ No claim that data is real-time or from a licensed provider
- ❌ No fabricated salary figures for unknown combinations
