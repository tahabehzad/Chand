"""Unit tests for the ``perf-v1`` scoring engine (MVP-10, AC-05…AC-08).

Authority
---------
``docs/MVP_SCOPE.md`` §5; ``AGENTS.md`` §2 Financial invariants (Decimal only,
deterministic, no clock).  These tests pin the semantics that the historical
frontend prototype established, so a backend/prototype divergence is a defect.
"""

from __future__ import annotations

import pytest

from app.engines.errors import CodedDomainError
from app.engines.perf_v1 import (
    CRITERIA,
    METRIC_CODES,
    RULE_SET_STATUS,
    RULE_SET_VERSION,
    WEIGHTS_SUM_BP,
    ScoreInput,
    criterion_by_code,
    normalise_to_bp,
    score_observations,
    validate_observation_value,
)


def _obs(code: str, raw: str, suffix: str = "1") -> ScoreInput:
    return ScoreInput(code=code, raw=raw, observation_id=f"obs-{code}-{suffix}", period="1404-Q2")


def test_rule_set_version_is_published_and_provisional() -> None:
    """AC-05: the version string is emitted and the status is never approved."""
    assert RULE_SET_VERSION == "perf-v1"
    assert RULE_SET_STATUS == "PROVISIONAL_DRAFT"


def test_weights_sum_to_exactly_one() -> None:
    """AC-05: weights sum to exactly 10 000 basis points (Decimal(1))."""
    assert sum(criterion.weight_bp for criterion in CRITERIA) == WEIGHTS_SUM_BP
    assert all(criterion.weight_bp > 0 for criterion in CRITERIA)
    assert {c.code for c in CRITERIA} == set(METRIC_CODES)


def test_normalisation_bounds() -> None:
    """The inclusive bounds clamp at both ends."""
    sales = criterion_by_code("sales")
    assert sales is not None
    assert normalise_to_bp(sales, "0") == 0
    assert normalise_to_bp(sales, "1000000000") == 10_000
    assert normalise_to_bp(sales, "500000000") == 5_000
    resp = criterion_by_code("responsibility")
    assert resp is not None
    assert normalise_to_bp(resp, "1") == 0
    assert normalise_to_bp(resp, "5") == 10_000
    assert normalise_to_bp(resp, "3") == 5_000
    assert normalise_to_bp(resp, "0") == 0  # clamped, never negative


def test_contributions_sum_to_total_and_score_is_deterministic() -> None:
    """AC-06/AC-07: contributions sum to the score and reruns are identical."""
    inputs = [
        _obs("sales", "800000000"),
        _obs("quality", "82"),
        _obs("attendance", "29"),
        _obs("responsibility", "4"),
    ]
    first = score_observations(inputs)
    second = score_observations(inputs)

    assert first.score_100 == second.score_100
    assert first.total_bp == second.total_bp
    assert first.calculation_hash == second.calculation_hash

    contribution_total = sum(c.contribution_bp for c in first.contributions)
    assert contribution_total == first.total_bp
    # 0.8*4000 + 0.82*3000 + (29/30)*2000 + 0.75*1000 = 3200+2460+1933+750
    assert first.total_bp == 3200 + 2460 + 1933 + 750
    assert first.score_100 == 83


def test_missing_criteria_score_zero_and_are_named() -> None:
    """AC-08: an absent criterion is reported, never silently imputed."""
    result = score_observations([_obs("quality", "65"), _obs("attendance", "27")])
    assert set(result.missing_criteria) == {"sales", "responsibility"}
    missing_rows = [c for c in result.contributions if c.missing]
    assert {c.code for c in missing_rows} == {"sales", "responsibility"}
    assert all(c.contribution_bp == 0 for c in missing_rows)
    assert result.missing_policy_fa.startswith("معیار ثبت‌نشده")


def test_rejected_observations_never_reach_the_scorer_via_caller_contract() -> None:
    """The engine only sees what the service passes; the service filter is AC-04."""
    # The engine itself is total over duplicates (documented behaviour).
    first = score_observations([_obs("quality", "65", "a"), _obs("quality", "90", "b")])
    assert first.total_bp == 2_700  # the later entry wins
    assert len(first.observations_used) == 1
    assert first.observations_used[0]["id"] == "obs-quality-b"


def test_full_score_is_100() -> None:
    inputs = [
        _obs("sales", "1000000000"),
        _obs("quality", "100"),
        _obs("attendance", "30"),
        _obs("responsibility", "5"),
    ]
    result = score_observations(inputs)
    assert result.score_100 == 100
    assert result.total_bp == 10_000


def test_observation_value_validation() -> None:
    assert validate_observation_value("sales", "0") == "0"
    with pytest.raises(CodedDomainError) as metric_error:
        validate_observation_value("unknown", "5")
    assert metric_error.value.code == "OBSERVATION_METRIC_INVALID"
    with pytest.raises(CodedDomainError) as value_error:
        validate_observation_value("sales", "-5")
    assert value_error.value.code == "OBSERVATION_VALUE_INVALID"
    with pytest.raises(CodedDomainError) as bound_error:
        validate_observation_value("attendance", "31")
    assert bound_error.value.code == "OBSERVATION_VALUE_INVALID"
