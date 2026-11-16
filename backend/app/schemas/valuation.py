"""Pydantic v2 contracts for the advisory compensation proposal (ADR-009).

Authority
---------
``docs/adr/ADR-009-compensation-advisory-module.md``;
``docs/EXECUTION_PLAN.md`` §7.2 rule 4 and §7.3; financial-data-integrity
rules 25-27 (integer Rial JSON, rates as strings).

Contract notes
--------------
* Every monetary field is a JSON **integer** in Rial; every score, weight and
  position is a **string** so a JavaScript client cannot turn it into a
  binary float.
* ``advisory`` and ``statutory`` are always emitted: a proposal can never be
  mistaken for a statutory entitlement or for tax advice.
* Unknown request fields are forbidden, so a typo cannot silently change the
  meaning of a proposal.
* The request deliberately leaves numeric validation to the engine, so a bad
  attribute produces the documented categorical refusal
  (``VALUATION_PROFILE_INVALID``) instead of a generic request error.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.schemas.payroll import TaxPostureValue

__all__ = (
    "BandView",
    "CompensationProposalRequest",
    "CompensationProposalResponse",
    "ProfileView",
    "ProposedRangeView",
    "ScoreView",
    "StatutoryContextView",
    "StatutoryCostBlock",
    "StatutoryCostingView",
)

EducationLevelValue = Literal[
    "below_diploma",
    "diploma",
    "associate",
    "bachelor",
    "master",
    "doctorate",
]


class CompensationProposalRequest(BaseModel):
    """One manager-entered profile and the monthly gross band for its role."""

    model_config = ConfigDict(extra="forbid")

    total_experience_months: int
    relevant_experience_months: int
    skill_level: int
    education_level: EducationLevelValue
    #: The band is the only source of money in a proposal.  Omitting it is
    #: refused with ``VALUATION_BAND_REQUIRED`` rather than guessed.
    band_min_gross_rial: int | None = None
    band_max_gross_rial: int | None = None
    rule_year: int = 1404
    days_in_month: Literal[29, 30, 31] = 30
    tax_posture: TaxPostureValue = "conservative_inta"


class ProfileView(BaseModel):
    """The profile as scored, with the separation note."""

    total_experience_months: int
    relevant_experience_months: int
    skill_level: int
    education_level: str
    experience_separation_note: str


class ScoreView(BaseModel):
    """The published score, weights and each weighted contribution."""

    score_exact: str
    score_100: int
    weights: dict[str, str]
    weighted_contributions: dict[str, str]


class BandView(BaseModel):
    """The manager-supplied envelope and where it came from."""

    min_gross_rial: int
    max_gross_rial: int
    width_rial: int
    source: str
    market_data_used: bool


class ProposedRangeView(BaseModel):
    """The point proposal and the published range around it."""

    position_in_band: str
    gross_point_rial: int
    range_low_rial: int
    range_high_rial: int
    spread_fraction: str
    spread_basis: str


class StatutoryCostBlock(BaseModel):
    """One statutory costing produced by the existing engine."""

    request: dict[str, object]
    calculation_hash: str
    statutory_version: str
    rule_set_fingerprint: str
    gross_monthly_rial: int
    employee_sso_7pct_rial: int
    sso_insurable_ceiling_applied: bool
    income_tax_rial: int
    net_rial: int
    monthly_sanavat_accrual_rial: int
    monthly_eydi_accrual_rial: int
    total_monthly_employer_cost_rial: int
    annual_ctc_12month_rial: int
    rounding_residual_rial: int


class StatutoryCostingView(BaseModel):
    """The range costed at its lower bound, its point and its upper bound."""

    lower_bound: StatutoryCostBlock
    point: StatutoryCostBlock
    upper_bound: StatutoryCostBlock
    replay_note: str


class StatutoryContextView(BaseModel):
    """The statutory floor for comparison only, never applied."""

    monthly_minimum_wage_rial: int
    range_low_below_statutory_minimum: bool
    applied_to_net: bool
    applied_to_net_reason: str


class CompensationProposalResponse(BaseModel):
    """The complete, hashed advisory proposal.

    ``generated_at`` is injected by the API layer only; the proposal itself is
    a pure function of the inputs and the rule-set version.
    """

    advisory: bool
    statutory: bool
    advisory_notes: list[str]
    model_version: str
    engine_version: str
    proposal_version: str
    rule_year_shamsi: int
    rule_set_status: str
    statutory_version: str
    rule_set_fingerprint: str
    profile: ProfileView
    score: ScoreView
    band: BandView
    proposed: ProposedRangeView
    statutory_costing: StatutoryCostingView
    statutory_context: StatutoryContextView
    calculation_hash: str
    generated_at: str
