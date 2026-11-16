"""Unit evidence for the advisory valuation model (ADR-009).

Every profile here is synthetic.  The suite pins the published model, the
band-required refusal, the range arithmetic and the separation of total from
relevant experience (AGENTS.md invariants 1 and 2).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.engines.errors import (
    ValuationBandInvalid,
    ValuationBandRequired,
    ValuationExperienceInvalid,
    ValuationProfileInvalid,
)
from app.engines.valuation import (
    DEFAULT_WEIGHTS,
    MAX_EXPERIENCE_MONTHS,
    RANGE_SPREAD_FRACTION,
    EducationLevel,
    ValuationWeights,
    assess_profile,
    propose_gross_range,
)

BAND_MIN = 100_000_000
BAND_MAX = 200_000_000
BAND_WIDTH = BAND_MAX - BAND_MIN


def _score(
    *,
    total: int,
    relevant: int,
    skill: int,
    education: EducationLevel,
) -> Decimal:
    return assess_profile(
        total_experience_months=total,
        relevant_experience_months=relevant,
        skill_level=skill,
        education_level=education,
    ).score_exact


def test_the_published_weights_sum_to_one() -> None:
    assert DEFAULT_WEIGHTS.total_experience + DEFAULT_WEIGHTS.relevant_experience == (
        Decimal("0.60")
    )
    assert DEFAULT_WEIGHTS.skill_level + DEFAULT_WEIGHTS.education == Decimal("0.40")


def test_a_saturated_profile_scores_exactly_one_hundred() -> None:
    assessment = assess_profile(
        total_experience_months=120,
        relevant_experience_months=84,
        skill_level=5,
        education_level=EducationLevel.DOCTORATE,
    )
    assert assessment.score_exact == Decimal(1)
    assert assessment.score_100 == 100


def test_an_empty_profile_scores_only_its_skill_component() -> None:
    assessment = assess_profile(
        total_experience_months=0,
        relevant_experience_months=0,
        skill_level=1,
        education_level=EducationLevel.BELOW_DIPLOMA,
    )
    # skill 1/5 = 0.2, weighted 0.30 -> 0.06
    assert assessment.score_exact == Decimal("0.06")
    assert assessment.score_100 == 6


def test_the_worked_profile_matches_its_hand_computation() -> None:
    assessment = assess_profile(
        total_experience_months=60,
        relevant_experience_months=42,
        skill_level=3,
        education_level=EducationLevel.BACHELOR,
    )
    # 0.5*0.35 + 0.5*0.25 + 0.6*0.30 + 0.7*0.10 = 0.55
    assert assessment.score_exact == Decimal("0.55")
    assert assessment.contributions == {
        "total_experience": Decimal("0.175"),
        "relevant_experience": Decimal("0.125"),
        "skill_level": Decimal("0.180"),
        "education": Decimal("0.070"),
    }


def test_experience_saturates_instead_of_rewarding_tenure_without_limit() -> None:
    at_cap = _score(total=120, relevant=84, skill=3, education=EducationLevel.BACHELOR)
    far_beyond = _score(total=540, relevant=84, skill=3, education=EducationLevel.BACHELOR)
    assert at_cap == far_beyond


@pytest.mark.parametrize(
    ("education", "ordered"),
    [
        (EducationLevel.BELOW_DIPLOMA, EducationLevel.DIPLOMA),
        (EducationLevel.DIPLOMA, EducationLevel.ASSOCIATE),
        (EducationLevel.ASSOCIATE, EducationLevel.BACHELOR),
        (EducationLevel.BACHELOR, EducationLevel.MASTER),
        (EducationLevel.MASTER, EducationLevel.DOCTORATE),
    ],
)
def test_education_bands_are_ordered(education: EducationLevel, ordered: EducationLevel) -> None:
    lower = _score(total=12, relevant=12, skill=2, education=education)
    higher = _score(total=12, relevant=12, skill=2, education=ordered)
    assert higher > lower


def test_relevant_experience_is_scored_separately_and_never_exceeds_total() -> None:
    with pytest.raises(ValuationExperienceInvalid) as caught:
        assess_profile(
            total_experience_months=24,
            relevant_experience_months=36,
            skill_level=3,
            education_level=EducationLevel.BACHELOR,
        )
    assert caught.value.code == "VALUATION_EXPERIENCE_INVALID"


def test_more_relevant_experience_scores_higher_at_equal_tenure() -> None:
    narrow = _score(total=120, relevant=12, skill=3, education=EducationLevel.BACHELOR)
    focused = _score(total=120, relevant=84, skill=3, education=EducationLevel.BACHELOR)
    assert focused > narrow


@pytest.mark.parametrize(
    ("total", "relevant"),
    [(-1, 0), (0, -1), (MAX_EXPERIENCE_MONTHS + 1, 0), (0.5, 0), ("12", 0), (True, 0)],
)
def test_invalid_experience_is_refused(total: object, relevant: object) -> None:
    with pytest.raises(ValuationProfileInvalid) as caught:
        assess_profile(
            total_experience_months=total,
            relevant_experience_months=relevant,
            skill_level=3,
            education_level=EducationLevel.BACHELOR,
        )
    assert caught.value.code == "VALUATION_PROFILE_INVALID"


@pytest.mark.parametrize("skill", [0, 6, -1, 2.5, "3", True])
def test_skill_level_outside_the_published_scale_is_refused(skill: object) -> None:
    with pytest.raises(ValuationProfileInvalid):
        assess_profile(
            total_experience_months=12,
            relevant_experience_months=12,
            skill_level=skill,
            education_level=EducationLevel.BACHELOR,
        )


def test_an_unknown_education_band_is_refused() -> None:
    with pytest.raises(ValuationProfileInvalid):
        assess_profile(
            total_experience_months=12,
            relevant_experience_months=12,
            skill_level=3,
            education_level="phd_from_nowhere",
        )


def test_weights_that_do_not_sum_to_one_are_refused() -> None:
    with pytest.raises(ValuationProfileInvalid):
        ValuationWeights(total_experience=Decimal("0.50"))


def test_weights_as_mapping_is_all_strings() -> None:
    mapping = DEFAULT_WEIGHTS.as_mapping()
    assert set(mapping) == {
        "total_experience",
        "relevant_experience",
        "skill_level",
        "education",
    }
    assert all(isinstance(value, str) for value in mapping.values())


# --- band placement --------------------------------------------------------


def test_no_band_is_refused_rather_than_guessed() -> None:
    with pytest.raises(ValuationBandRequired) as caught:
        propose_gross_range(
            score_exact=Decimal("0.5"),
            band_min_gross_rial=None,
            band_max_gross_rial=None,
        )
    assert caught.value.code == "VALUATION_BAND_REQUIRED"


@pytest.mark.parametrize("missing", ["min", "max"])
def test_a_half_supplied_band_is_refused(missing: str) -> None:
    with pytest.raises(ValuationBandRequired):
        propose_gross_range(
            score_exact=Decimal("0.5"),
            band_min_gross_rial=None if missing == "min" else BAND_MIN,
            band_max_gross_rial=None if missing == "max" else BAND_MAX,
        )


@pytest.mark.parametrize(
    ("band_min", "band_max"),
    [(0, BAND_MAX), (-1, BAND_MAX), (BAND_MAX, BAND_MIN), (BAND_MIN, 0), (1.5, BAND_MAX)],
)
def test_an_unusable_band_is_refused(band_min: object, band_max: object) -> None:
    with pytest.raises(ValuationBandInvalid) as caught:
        propose_gross_range(
            score_exact=Decimal("0.5"),
            band_min_gross_rial=band_min,
            band_max_gross_rial=band_max,
        )
    assert caught.value.code == "VALUATION_BAND_INVALID"


def test_the_worked_proposal_matches_its_hand_computation() -> None:
    proposal = propose_gross_range(
        score_exact=Decimal("0.55"),
        band_min_gross_rial=BAND_MIN,
        band_max_gross_rial=BAND_MAX,
    )
    assert proposal.band_width_rial == BAND_WIDTH
    assert proposal.proposed_gross_rial == 155_000_000
    # half-width = 0.05 * 100,000,000 = 5,000,000
    assert proposal.range_low_rial == 150_000_000
    assert proposal.range_high_rial == 160_000_000
    assert proposal.spread_fraction == RANGE_SPREAD_FRACTION
    assert proposal.position == Decimal("0.5500")


def test_the_range_is_clamped_to_the_band() -> None:
    top = propose_gross_range(
        score_exact=Decimal(1), band_min_gross_rial=BAND_MIN, band_max_gross_rial=BAND_MAX
    )
    bottom = propose_gross_range(
        score_exact=Decimal(0), band_min_gross_rial=BAND_MIN, band_max_gross_rial=BAND_MAX
    )
    assert (top.range_low_rial, top.range_high_rial) == (195_000_000, BAND_MAX)
    assert (bottom.range_low_rial, bottom.range_high_rial) == (BAND_MIN, 105_000_000)


def test_a_single_point_band_produces_a_single_point_range() -> None:
    proposal = propose_gross_range(
        score_exact=Decimal("0.42"),
        band_min_gross_rial=50_000_000,
        band_max_gross_rial=50_000_000,
    )
    assert proposal.band_width_rial == 0
    assert proposal.proposed_gross_rial == 50_000_000
    assert (proposal.range_low_rial, proposal.range_high_rial) == (50_000_000, 50_000_000)


def test_a_higher_score_never_proposes_less() -> None:
    proposals = [
        propose_gross_range(
            score_exact=Decimal(step),
            band_min_gross_rial=BAND_MIN,
            band_max_gross_rial=BAND_MAX,
        )
        for step in ("0", "0.25", "0.5", "0.75", "1")
    ]
    points = [proposal.proposed_gross_rial for proposal in proposals]
    assert points == sorted(points)
    assert len(set(points)) == len(points)


@pytest.mark.parametrize("score", [Decimal("-0.01"), Decimal("1.01"), 1, "0.5"])
def test_a_score_outside_the_unit_interval_is_refused(score: object) -> None:
    with pytest.raises(ValuationProfileInvalid):
        propose_gross_range(
            score_exact=score,  # type: ignore[arg-type]
            band_min_gross_rial=BAND_MIN,
            band_max_gross_rial=BAND_MAX,
        )


def test_the_proposal_is_deterministic_and_marked_advisory_model() -> None:
    first = propose_gross_range(
        score_exact=Decimal("0.33"),
        band_min_gross_rial=BAND_MIN,
        band_max_gross_rial=BAND_MAX,
    )
    second = propose_gross_range(
        score_exact=Decimal("0.33"),
        band_min_gross_rial=BAND_MIN,
        band_max_gross_rial=BAND_MAX,
    )
    assert first == second
    assert first.model_version == "valuation-v1"
