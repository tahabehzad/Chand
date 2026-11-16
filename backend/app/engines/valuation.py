"""Advisory compensation valuation (ADR-009).

Authority
---------
``docs/adr/ADR-009-compensation-advisory-module.md``; ``AGENTS.md`` §2
invariants 1, 2, 4, 5, 6, 9 and 11; ``docs/DECISIONS_REGISTER.md`` DEC-009
(neutral calculator) and DEC-013 (statutory floors stay advisory).

What this module is, and is not
-------------------------------
It answers one question: *given a documented profile, where inside the money
envelope the manager supplied should this person sit?*  It does not price a
role: there is no licensed market data in the repository (DEC-007/DEC-008 are
rejected), so the band is a human judgement and the module only positions a
profile inside it.  No band means no proposal, never an invented figure.

The score is a **published policy heuristic**, not a validated salary science
and not a verdict about a person (invariant 4).  Every response carries the
model version, the weights and each weighted contribution, so a manager can
challenge the number rather than trust it.  The statutory engine remains the
only source of tax, insurance, severance, bonus and employer cost; this module
never re-implements them (ADR-009 directive 5).

Contract notes
--------------
* Pure function of its arguments: no clock, randomness, I/O or environment
  read (invariant 11).  ``generated_at`` is added by the API boundary.
* Total professional experience and relevant occupational experience are
  separate inputs and are never summed, so overlapping periods cannot be
  double counted (invariants 1 and 2).  ``relevant > total`` is refused.
* Scores use ``Decimal``; money leaves this module as whole Rial rounded
  ``ROUND_HALF_UP`` once, at the line boundary (invariants 7 and 8).  No
  float literal appears on this path.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum
from typing import Final

from app.engines.errors import (
    ValuationBandInvalid,
    ValuationBandRequired,
    ValuationExperienceInvalid,
    ValuationProfileInvalid,
)
from app.engines.money import round_half_up

__all__ = (
    "DEFAULT_WEIGHTS",
    "MAX_EXPERIENCE_MONTHS",
    "RANGE_SPREAD_FRACTION",
    "SCORE_SCALE",
    "VALUATION_MODEL_VERSION",
    "BandProposal",
    "EducationLevel",
    "ProfileAssessment",
    "ValuationWeights",
    "assess_profile",
    "propose_gross_range",
)

VALUATION_MODEL_VERSION: Final[str] = "valuation-v1"

#: The widest experience a single career can plausibly carry (60 years).
MAX_EXPERIENCE_MONTHS: Final[int] = 720

#: The score is published on a 0-100 scale.
SCORE_SCALE: Final[Decimal] = Decimal(100)

#: Half-width of the proposed range, as a fraction of the band width.
RANGE_SPREAD_FRACTION: Final[Decimal] = Decimal("0.05")

_TOTAL_EXPERIENCE_FULL_MONTHS: Final[Decimal] = Decimal(120)
_RELEVANT_EXPERIENCE_FULL_MONTHS: Final[Decimal] = Decimal(84)
_ONE: Final[Decimal] = Decimal(1)
_ZERO: Final[Decimal] = Decimal(0)
_MIN_SKILL_LEVEL: Final[int] = 1
_MAX_SKILL_LEVEL: Final[int] = 5


class EducationLevel(StrEnum):
    """The six education bands of the published model."""

    BELOW_DIPLOMA = "below_diploma"
    DIPLOMA = "diploma"
    ASSOCIATE = "associate"
    BACHELOR = "bachelor"
    MASTER = "master"
    DOCTORATE = "doctorate"


_EDUCATION_SCORE: Final[dict[EducationLevel, Decimal]] = {
    EducationLevel.BELOW_DIPLOMA: Decimal(0),
    EducationLevel.DIPLOMA: Decimal("0.25"),
    EducationLevel.ASSOCIATE: Decimal("0.50"),
    EducationLevel.BACHELOR: Decimal("0.70"),
    EducationLevel.MASTER: Decimal("0.90"),
    EducationLevel.DOCTORATE: Decimal(1),
}


@dataclass(frozen=True, slots=True)
class ValuationWeights:
    """The published weights of one model version; they sum to one."""

    total_experience: Decimal = Decimal("0.35")
    relevant_experience: Decimal = Decimal("0.25")
    skill_level: Decimal = Decimal("0.30")
    education: Decimal = Decimal("0.10")

    def __post_init__(self) -> None:
        values = (
            self.total_experience,
            self.relevant_experience,
            self.skill_level,
            self.education,
        )
        if any(not isinstance(value, Decimal) for value in values):
            raise ValuationProfileInvalid(
                "VALUATION_PROFILE_INVALID: model weights must be Decimal"
            )
        if any(value < _ZERO for value in values):
            raise ValuationProfileInvalid(
                "VALUATION_PROFILE_INVALID: model weights must not be negative"
            )
        if sum(values, _ZERO) != _ONE:
            raise ValuationProfileInvalid(
                "VALUATION_PROFILE_INVALID: model weights must sum to exactly one"
            )

    def as_mapping(self) -> dict[str, str]:
        """Return the weights in the response shape (rates are strings)."""
        return {
            "total_experience": str(self.total_experience),
            "relevant_experience": str(self.relevant_experience),
            "skill_level": str(self.skill_level),
            "education": str(self.education),
        }


DEFAULT_WEIGHTS: Final[ValuationWeights] = ValuationWeights()


@dataclass(frozen=True, slots=True)
class ProfileAssessment:
    """The published score, its inputs and each weighted contribution."""

    total_experience_months: int
    relevant_experience_months: int
    skill_level: int
    education_level: EducationLevel
    score_exact: Decimal
    score_100: int
    contributions: dict[str, Decimal]
    weights: ValuationWeights


@dataclass(frozen=True, slots=True)
class BandProposal:
    """Where a score sits inside a manager-supplied monthly gross band."""

    band_min_gross_rial: int
    band_max_gross_rial: int
    band_width_rial: int
    position: Decimal
    proposed_gross_exact_rial: Decimal
    proposed_gross_rial: int
    range_low_rial: int
    range_high_rial: int
    spread_fraction: Decimal
    model_version: str


def _require_months(value: object, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValuationProfileInvalid(f"VALUATION_PROFILE_INVALID: {name} must be an integer")
    if value < 0 or value > MAX_EXPERIENCE_MONTHS:
        raise ValuationProfileInvalid(
            f"VALUATION_PROFILE_INVALID: {name} must be between 0 and {MAX_EXPERIENCE_MONTHS} months"
        )
    return value


def _require_band_amount(value: object, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValuationBandInvalid(f"VALUATION_BAND_INVALID: {name} must be integer Rial")
    if value <= 0:
        raise ValuationBandInvalid(f"VALUATION_BAND_INVALID: {name} must be positive")
    return value


def _capped_ratio(value: int, *, full: Decimal) -> Decimal:
    ratio = Decimal(value) / full
    return _ONE if ratio > _ONE else ratio


def assess_profile(
    *,
    total_experience_months: object,
    relevant_experience_months: object,
    skill_level: object,
    education_level: object,
    weights: ValuationWeights = DEFAULT_WEIGHTS,
) -> ProfileAssessment:
    """Score a documented profile on the published 0-100 scale.

    The four components are normalised independently and then weighted; the
    experience components are capped at ten and seven years respectively, so
    the score saturates rather than rewarding tenure without limit.
    """
    total = _require_months(total_experience_months, name="total_experience_months")
    relevant = _require_months(relevant_experience_months, name="relevant_experience_months")
    if relevant > total:
        raise ValuationExperienceInvalid(
            "VALUATION_EXPERIENCE_INVALID: relevant experience cannot exceed total experience"
        )
    if isinstance(skill_level, bool) or not isinstance(skill_level, int):
        raise ValuationProfileInvalid("VALUATION_PROFILE_INVALID: skill_level must be an integer")
    if skill_level < _MIN_SKILL_LEVEL or skill_level > _MAX_SKILL_LEVEL:
        raise ValuationProfileInvalid(
            f"VALUATION_PROFILE_INVALID: skill_level must be between {_MIN_SKILL_LEVEL} and {_MAX_SKILL_LEVEL}"
        )
    if not isinstance(education_level, EducationLevel):
        raise ValuationProfileInvalid(
            "VALUATION_PROFILE_INVALID: education_level is not a published band"
        )

    components = {
        "total_experience": _capped_ratio(total, full=_TOTAL_EXPERIENCE_FULL_MONTHS),
        "relevant_experience": _capped_ratio(relevant, full=_RELEVANT_EXPERIENCE_FULL_MONTHS),
        "skill_level": Decimal(skill_level) / Decimal(_MAX_SKILL_LEVEL),
        "education": _EDUCATION_SCORE[education_level],
    }
    contributions = {
        "total_experience": weights.total_experience * components["total_experience"],
        "relevant_experience": weights.relevant_experience * components["relevant_experience"],
        "skill_level": weights.skill_level * components["skill_level"],
        "education": weights.education * components["education"],
    }
    score_exact = sum(contributions.values(), _ZERO)
    score_100 = round_half_up(score_exact * SCORE_SCALE, field="valuation_score")

    return ProfileAssessment(
        total_experience_months=total,
        relevant_experience_months=relevant,
        skill_level=skill_level,
        education_level=education_level,
        score_exact=score_exact,
        score_100=score_100,
        contributions=contributions,
        weights=weights,
    )


def propose_gross_range(
    *,
    score_exact: Decimal,
    band_min_gross_rial: object,
    band_max_gross_rial: object,
) -> BandProposal:
    """Place the score inside the manager's band and widen it to a range.

    The band is required.  Without it there is no defensible amount, so the
    refusal is explicit rather than a generated number.
    """
    if band_min_gross_rial is None or band_max_gross_rial is None:
        raise ValuationBandRequired(
            "VALUATION_BAND_REQUIRED: a monthly gross band is required to propose an amount"
        )
    band_min = _require_band_amount(band_min_gross_rial, name="band_min_gross_rial")
    band_max = _require_band_amount(band_max_gross_rial, name="band_max_gross_rial")
    if band_max < band_min:
        raise ValuationBandInvalid(
            "VALUATION_BAND_INVALID: band_max_gross_rial cannot be below band_min_gross_rial"
        )
    if not isinstance(score_exact, Decimal) or score_exact < _ZERO or score_exact > _ONE:
        raise ValuationProfileInvalid(
            "VALUATION_PROFILE_INVALID: the score must be a Decimal between zero and one"
        )

    width = Decimal(band_max - band_min)
    proposed_exact = Decimal(band_min) + (score_exact * width)
    spread = RANGE_SPREAD_FRACTION * width

    low_exact = proposed_exact - spread
    high_exact = proposed_exact + spread
    low = round_half_up(low_exact, field="range_low_rial")
    high = round_half_up(high_exact, field="range_high_rial")
    low = band_min if low < band_min else low
    high = band_max if high > band_max else high
    proposed = round_half_up(proposed_exact, field="proposed_gross_rial")
    low = min(low, proposed)
    high = max(high, proposed)

    return BandProposal(
        band_min_gross_rial=band_min,
        band_max_gross_rial=band_max,
        band_width_rial=band_max - band_min,
        position=score_exact.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP),
        proposed_gross_exact_rial=proposed_exact,
        proposed_gross_rial=proposed,
        range_low_rial=low,
        range_high_rial=high,
        spread_fraction=RANGE_SPREAD_FRACTION,
        model_version=VALUATION_MODEL_VERSION,
    )
