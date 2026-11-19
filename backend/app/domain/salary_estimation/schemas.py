"""Domain value objects for market salary estimation.

Authority
---------
``docs/adr/ADR-014-market-salary-reference-data-and-estimation.md`` §4 (cohort
estimation, no multiplicative adjustment, published quantiles) and §6 (confidence
model with its components exposed); ``AGENTS.md`` §2 Financial invariant 11 (the
calculation is a pure function of its inputs — no clock, no environment).

Related
-------
``salary_estimator.py`` (produces :class:`EstimationOutcome`),
``app/schemas/estimation.py`` (the HTTP contract that mirrors it).

Scope
-----
Plain immutable records.  Pydantic is deliberately not used here: the domain is
framework-free, so a contract change cannot alter a calculation silently.
"""

from __future__ import annotations

import datetime
from collections.abc import Mapping
from dataclasses import dataclass, field
from decimal import Decimal

__all__ = (
    "ENGINE_VERSION",
    "ESTIMATION_VERSION",
    "EstimationOutcome",
    "EstimationProfile",
    "EstimationThresholds",
    "MarketRowSummary",
)


#: Version of this estimation engine.  Engine and rule versions travel with every
#: figure (``AGENTS.md`` §2 Financial invariant 9).
ENGINE_VERSION = "0.2.0-estimation"

#: Version of the methodology recorded in ``methodology["method"]``.
ESTIMATION_VERSION = "market-cohort-v2"


@dataclass(frozen=True)
class EstimationProfile:
    """One candidate profile, validated at the HTTP boundary."""

    job_title: str
    experience_years: int
    seniority_level: str
    employment_type: str
    city: str
    skills: tuple[str, ...] = ()
    education: str | None = None
    province: str | None = None
    work_condition: str = "on_site"
    job_description: str | None = None
    certifications: tuple[str, ...] = ()
    currency_unit: str = "toman"
    gemini_api_key: str | None = None


@dataclass(frozen=True)
class EstimationThresholds:
    """Publication thresholds.  Configurable; defaults documented in ADR-014."""

    min_valid_samples: int = 5
    max_data_age_days: int = 730
    allow_synthetic: bool = False
    allow_aggregate_fallback: bool = True
    confidence_publish_floor: Decimal = Decimal("0.20")


@dataclass(frozen=True)
class MarketRowSummary:
    """One source's contribution to the estimate — the ``market_rows`` contract."""

    source: str
    job_title: str
    city: str
    seniority_level: str
    min_salary_rial: int
    median_salary_rial: int
    max_salary_rial: int
    sample_count: int
    collected_at: datetime.datetime
    confidence: str

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-serialisable view."""
        return {
            "source": self.source,
            "job_title": self.job_title,
            "city": self.city,
            "seniority_level": self.seniority_level,
            "min_salary_rial": self.min_salary_rial,
            "median_salary_rial": self.median_salary_rial,
            "max_salary_rial": self.max_salary_rial,
            "sample_count": self.sample_count,
            "collected_at": self.collected_at.isoformat(),
            "confidence": self.confidence,
        }


@dataclass(frozen=True)
class EstimationOutcome:
    """Everything a defensible estimate must publish.

    Every monetary field is a whole Rial integer.  The four published figures are
    quantised to a whole Toman at the emission boundary (so the Persian UI can
    render Toman exactly, per ADR-013's currency convention) and the signed
    rounding outcome is surfaced rather than hidden.
    """

    primary_estimate_rial: int
    min_salary_rial: int
    median_salary_rial: int
    max_salary_rial: int
    rounding_residual_rial: int
    valid_sample_count: int
    quarantined_sample_count: int
    rejected_sample_count: int
    confidence_level: str
    confidence_score: Decimal
    data_confidence: Decimal
    prediction_confidence: Decimal
    confidence_components: Mapping[str, str]
    confidence_weights: Mapping[str, str]
    factors_influence: tuple[str, ...]
    data_sources: tuple[str, ...]
    data_collected_at: datetime.datetime | None
    data_oldest_at: datetime.datetime | None
    market_rows: tuple[MarketRowSummary, ...]
    distribution: tuple[tuple[int, int, int], ...]
    methodology: Mapping[str, object]
    warnings: tuple[str, ...]
    match: Mapping[str, object]
    cohort_scope: str
    cohort_size: int
    legal_minimum_wage_rial: int | None
    calculation_hash: str
    generated_at: datetime.datetime
    engine_version: str = ENGINE_VERSION
    estimation_version: str = ESTIMATION_VERSION
    factors_notes: tuple[str, ...] = field(default_factory=tuple)
    data_source_mode: str = "database_fallback"
