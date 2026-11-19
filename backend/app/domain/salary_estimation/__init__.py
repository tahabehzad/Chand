"""Market salary estimation domain (ADR-014).

Authority
---------
``docs/adr/ADR-014-market-salary-reference-data-and-estimation.md`` — data kinds,
validation policy, cohort estimation, confidence model and publication rules;
``docs/SALARY_ESTIMATION_SPEC.md``; ``AGENTS.md`` §2 Financial invariants 7-11.

Related
-------
``app/repositories/market_data.py`` (storage), ``app/services/estimation/`` (I/O),
``app/engines/`` (statutory payroll — a separate product path, untouched).

Scope
-----
Pure, framework-free calculation.  Nothing here reads the clock, the database,
the network or the environment: the caller supplies ``as_of`` and the rows.

Invariants
----------
* Decimal only, ``ROUND_HALF_UP`` only, no float literal touches money.
* A figure is published only from validated market rows, and only above the
  sample floor; otherwise the estimator refuses.
* No invented data: sample rows are labelled synthetic and are rejected unless the
  deployment explicitly enables them.
* City, seniority and employment type select a cohort; they are never multiplied
  on top of a cohort that already encodes them.
"""

from __future__ import annotations

from app.domain.salary_estimation.market_data import (
    APPROVED_LICENSE_STATUSES,
    DataQuality,
    MarketAggregate,
    MarketObservation,
    MarketSource,
    ValidationOutcome,
)
from app.domain.salary_estimation.matcher import JobMatch, SalaryMatcher
from app.domain.salary_estimation.money_validation import (
    EstimationInvariantError,
    validate_estimate_money_path,
)
from app.domain.salary_estimation.salary_estimator import (
    InsufficientMarketDataError,
    estimate_market_salary,
    legal_minimum_wage_reference,
)
from app.domain.salary_estimation.schemas import (
    EstimationOutcome,
    EstimationProfile,
    EstimationThresholds,
    MarketRowSummary,
)
from app.domain.salary_estimation.taxonomy import JOB_FAMILIES, JobFamily, normalize_text
from app.domain.salary_estimation.validation import (
    ValidationPolicy,
    classify_observations,
    reason_text,
)

__all__ = (
    "APPROVED_LICENSE_STATUSES",
    "JOB_FAMILIES",
    "DataQuality",
    "EstimationInvariantError",
    "EstimationOutcome",
    "EstimationProfile",
    "EstimationThresholds",
    "InsufficientMarketDataError",
    "JobFamily",
    "JobMatch",
    "MarketAggregate",
    "MarketObservation",
    "MarketRowSummary",
    "MarketSource",
    "SalaryMatcher",
    "ValidationOutcome",
    "ValidationPolicy",
    "classify_observations",
    "estimate_market_salary",
    "legal_minimum_wage_reference",
    "normalize_text",
    "reason_text",
    "validate_estimate_money_path",
)
