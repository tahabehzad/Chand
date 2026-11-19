"""Pydantic v2 contracts for market salary estimation (ADR-014).

Authority
---------
``docs/adr/ADR-014-market-salary-reference-data-and-estimation.md`` §7 (published
contract); ``docs/SALARY_ESTIMATION_SPEC.md`` (revisions); ``AGENTS.md`` §2
Financial invariant 9 (every figure carries its provenance).

Contract notes
--------------
* Every monetary field is a JSON **integer in Rial**.  The four published figures
  are whole-Toman multiples of 10 Rial, so the Persian UI can render Toman exactly
  without rounding in the display layer.
* ``confidence_score`` and its components are **strings**: a float would put binary
  rounding on a quality score that the report quotes.
* Unknown request fields are forbidden (``extra="forbid"``); the response is
  likewise closed so an undocumented field cannot leak into a report.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

__all__ = (
    "ConfidenceDetail",
    "DistributionBucket",
    "EstimateRequest",
    "EstimateResponse",
    "MarketDataRow",
    "MethodologySummary",
)

SeniorityValue = Literal["junior", "mid", "senior"]
EmploymentTypeValue = Literal["full_time", "part_time", "contract", "freelance"]
WorkConditionValue = Literal["on_site", "remote", "hybrid"]
ConfidenceValue = Literal["high", "medium", "low", "insufficient_data"]
CurrencyUnitValue = Literal["rial", "toman"]


class SkillView(BaseModel):
    """One skill with its self-declared level."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=100)
    level: Literal["beginner", "intermediate", "advanced"] = "beginner"


class EstimateRequest(BaseModel):
    """One manager-entered candidate profile."""

    model_config = ConfigDict(extra="forbid")

    job_title: str = Field(min_length=1, max_length=200)
    experience_years: int = Field(ge=0, le=60)
    seniority_level: SeniorityValue = "mid"
    employment_type: EmploymentTypeValue = "full_time"
    city: str = Field(min_length=1, max_length=100)
    province: str | None = Field(default=None, max_length=100)
    work_condition: WorkConditionValue = "on_site"
    job_description: str | None = Field(default=None, max_length=4000)
    currency_unit: CurrencyUnitValue = "toman"
    skills: list[SkillView] = Field(default_factory=list)
    education: str | None = Field(default=None, max_length=200)
    certifications: list[str] = Field(default_factory=list, max_length=50)
    previous_jobs: list[dict[str, Any]] = Field(default_factory=list, max_length=30)
    gemini_api_key: str | None = Field(default=None, max_length=200)


class MarketDataRow(BaseModel):
    """One source's contribution to the estimate."""

    model_config = ConfigDict(extra="forbid")

    source: str
    job_title: str
    city: str
    seniority_level: str
    min_salary_rial: int = Field(ge=0)
    median_salary_rial: int = Field(ge=0)
    max_salary_rial: int = Field(ge=0)
    sample_count: int = Field(ge=0)
    collected_at: str
    confidence: str


class DistributionBucket(BaseModel):
    """One bucket of the published salary distribution."""

    model_config = ConfigDict(extra="forbid")

    min_rial: int = Field(ge=0)
    max_rial: int = Field(ge=0)
    count: int = Field(ge=0)


class ConfidenceDetail(BaseModel):
    """Data confidence and prediction confidence are different claims."""

    model_config = ConfigDict(extra="forbid")

    data_confidence: str
    prediction_confidence: str
    method_ceiling: str
    components: dict[str, str]
    weights: dict[str, str]
    notes_fa: list[str]


class MethodologySummary(BaseModel):
    """How the figure was produced, in a form a reviewer can re-derive."""

    model_config = ConfigDict(extra="forbid")

    method: str
    estimation_version: str
    engine_version: str
    cohort_scope: str
    cohort_definition_fa: str
    range_source: str
    percentile_method: str
    outlier_tests: list[str]
    adjustments_applied: list[str]
    data_kind: str
    currency_storage: str
    currency_display: str
    quantisation_rial: int
    warning_codes: list[str]


class EstimateResponse(BaseModel):
    """The complete estimate, with provenance, confidence and refusals."""

    model_config = ConfigDict(extra="forbid")

    advisory: bool = True
    statutory: bool = False
    advisory_notes: list[str]
    data_source_mode: Literal["gemini_live", "database_fallback", "hybrid"] = "database_fallback"

    model_version: str
    estimation_version: str
    engine_version: str
    calculation_hash: str
    generated_at: str

    # Candidate profile echoed back
    job_title: str
    experience_years: int
    seniority_level: SeniorityValue
    employment_type: EmploymentTypeValue
    work_condition: WorkConditionValue
    city: str
    province: str | None

    # Published figures — whole Rial, and whole-Toman multiples of 10 Rial
    primary_estimate_rial: int = Field(ge=0)
    min_salary_rial: int = Field(ge=0)
    median_salary_rial: int = Field(ge=0)
    max_salary_rial: int = Field(ge=0)
    rounding_residual_rial: int
    currency_unit: CurrencyUnitValue

    # Sample provenance
    valid_sample_count: int = Field(ge=0)
    quarantined_sample_count: int = Field(ge=0)
    rejected_sample_count: int = Field(ge=0)
    data_sources: list[str]
    data_collected_at: str | None
    data_oldest_at: str | None
    market_rows: list[MarketDataRow]
    distribution: list[DistributionBucket]

    # Explanation
    factors_influence: list[str]
    factors_notes: list[str]
    confidence_level: ConfidenceValue
    confidence_score: str
    confidence: ConfidenceDetail
    methodology: MethodologySummary
    match: dict[str, Any]
    warnings: list[str]

    # Reference only (ADR-013 D-07)
    legal_minimum_wage_rial: int | None = None
