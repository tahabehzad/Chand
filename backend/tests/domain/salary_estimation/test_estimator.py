"""Estimator behaviour: real quantiles, cohort selection, refusals, confidence.

Authority: ``docs/adr/ADR-014-market-salary-reference-data-and-estimation.md`` §4,
§6 and §7.  The invariants under test:

* the published range is the market's own p25…p75;
* the median is the arithmetic median (an even sample is not biased upward);
* city and experience never multiply a cohort that already encodes them;
* a figure is published only above the sample floor, and it is a whole-Toman
  multiple so the UI never rounds;
* a missing legal reference never breaks the estimate.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import cast

import pytest

from app.domain.salary_estimation.market_data import MarketAggregate, MarketObservation
from app.domain.salary_estimation.salary_estimator import (
    InsufficientMarketDataError,
    estimate_market_salary,
)
from app.domain.salary_estimation.schemas import (
    EstimationProfile,
    EstimationThresholds,
)

AS_OF = datetime(2026, 10, 1, tzinfo=UTC)
FRESH = datetime(2026, 9, 1, tzinfo=UTC)
MILLION = 1_000_000
FOUR_SAMPLES = EstimationThresholds(min_valid_samples=4)


def observation(
    identifier: str,
    amount_rial: int,
    *,
    family: str = "php_backend",
    city: str = "تهران",
    seniority: str = "mid",
    license_status: str = "manual_verified",
    source: str = "manual-verified-manager",
    collected_at: datetime = FRESH,
    employment_type: str = "full_time",
) -> MarketObservation:
    """Build one valid observation."""
    return MarketObservation(
        id=identifier,
        family_key=family,
        job_title_reported="برنامه‌نویس PHP",
        city=city,
        province=city,
        amount_rial=amount_rial,
        period="monthly",
        currency_unit_reported="rial",
        source_id=source,
        license_status=license_status,
        collected_at=collected_at,
        seniority_level=seniority,
        employment_type=employment_type,
        work_condition="on_site",
    )


def cohort(
    amounts_million: tuple[int, ...],
    *,
    family: str = "php_backend",
    city: str = "تهران",
    seniority: str = "mid",
) -> tuple[MarketObservation, ...]:
    """Build a cohort from whole-million amounts."""
    return tuple(
        observation(
            f"{family}-{city}-{index}",
            value * MILLION,
            family=family,
            city=city,
            seniority=seniority,
        )
        for index, value in enumerate(amounts_million)
    )


def profile(**overrides: object) -> EstimationProfile:
    """Return a mid-level PHP profile in Tehran."""
    base = {
        "job_title": "برنامه‌نویس PHP",
        "experience_years": 5,
        "seniority_level": "mid",
        "employment_type": "full_time",
        "city": "تهران",
        "province": "تهران",
        "job_description": "laravel php mysql",
        "skills": ("php", "laravel"),
    }
    base.update(overrides)
    return EstimationProfile(**base)  # type: ignore[arg-type]


class TestQuantiles:
    """The published figures are the sample's own quantiles."""

    def test_even_sample_median_is_the_mean_of_the_two_central_values(self) -> None:
        observations = cohort((400, 500, 600, 700))
        outcome = estimate_market_salary(
            profile(), observations=observations, as_of=AS_OF, thresholds=FOUR_SAMPLES
        )
        assert outcome.median_salary_rial == 550 * MILLION
        assert outcome.primary_estimate_rial == 550 * MILLION

    def test_range_is_p25_to_p75_not_a_fixed_percentage_band(self) -> None:
        observations = cohort((400, 500, 600, 700))
        outcome = estimate_market_salary(
            profile(), observations=observations, as_of=AS_OF, thresholds=FOUR_SAMPLES
        )
        # Linear interpolation (R-7) on four points: p25 = 475, p75 = 625 million.
        assert outcome.min_salary_rial == 475 * MILLION
        assert outcome.max_salary_rial == 625 * MILLION
        assert outcome.valid_sample_count == 4

    def test_published_figures_are_whole_toman_multiples(self) -> None:
        observations = cohort((401, 503, 607, 709))
        outcome = estimate_market_salary(
            profile(), observations=observations, as_of=AS_OF, thresholds=FOUR_SAMPLES
        )
        for value in (
            outcome.min_salary_rial,
            outcome.median_salary_rial,
            outcome.primary_estimate_rial,
            outcome.max_salary_rial,
        ):
            assert value % 10 == 0, value
        assert abs(outcome.rounding_residual_rial) <= 15

    def test_distribution_is_returned_and_counts_the_valid_sample(self) -> None:
        observations = cohort((400, 500, 600, 700))
        outcome = estimate_market_salary(
            profile(), observations=observations, as_of=AS_OF, thresholds=FOUR_SAMPLES
        )
        assert sum(count for _low, _high, count in outcome.distribution) == 4

    def test_published_figures_are_ordered(self) -> None:
        observations = cohort((400, 500, 600, 700))
        outcome = estimate_market_salary(
            profile(), observations=observations, as_of=AS_OF, thresholds=FOUR_SAMPLES
        )
        assert outcome.min_salary_rial <= outcome.median_salary_rial <= outcome.max_salary_rial


class TestNoDoubleCounting:
    """Cohort selection replaces every fabricated multiplier."""

    def test_no_adjustment_is_applied(self) -> None:
        outcome = estimate_market_salary(
            profile(), observations=cohort((400, 500, 600, 700)), as_of=AS_OF, thresholds=FOUR_SAMPLES
        )
        assert outcome.methodology["adjustments_applied"] == []

    def test_experience_does_not_move_the_figure(self) -> None:
        observations = cohort((400, 500, 600, 700))
        junior_years = estimate_market_salary(
            profile(experience_years=2),
            observations=observations,
            as_of=AS_OF,
            thresholds=FOUR_SAMPLES,
        )
        senior_years = estimate_market_salary(
            profile(experience_years=20),
            observations=observations,
            as_of=AS_OF,
            thresholds=FOUR_SAMPLES,
        )
        assert junior_years.primary_estimate_rial == senior_years.primary_estimate_rial

    def test_city_is_a_cohort_selector_not_a_multiplier(self) -> None:
        observations = (
            *cohort((400, 500, 600, 700), city="تهران"),
            *cohort((200, 250, 300, 350), city="اصفهان"),
        )
        outcome = estimate_market_salary(
            profile(city="اصفهان", province="اصفهان"),
            observations=observations,
            as_of=AS_OF,
            thresholds=FOUR_SAMPLES,
        )
        # 275 million is Isfahan's own median; a Tehran-based multiplier would give
        # a very different figure.
        assert outcome.median_salary_rial == 275 * MILLION
        assert outcome.cohort_scope == "city_seniority_employment"

    def test_seniority_selects_its_own_cohort(self) -> None:
        observations = (
            *cohort((300, 320, 340, 360), seniority="mid"),
            *cohort((600, 620, 640, 660), seniority="senior"),
        )
        outcome = estimate_market_salary(
            profile(seniority_level="senior"),
            observations=observations,
            as_of=AS_OF,
            thresholds=FOUR_SAMPLES,
        )
        assert outcome.valid_sample_count == 4
        assert 600 * MILLION <= outcome.primary_estimate_rial <= 660 * MILLION

    def test_cohort_fallback_is_reported_when_the_narrow_scope_is_thin(self) -> None:
        full_time_rows = cohort((400, 500, 600, 700), seniority="mid")
        one_contract_row = observation(
            "contract-only", 480 * MILLION, seniority="mid", employment_type="contract"
        )
        outcome = estimate_market_salary(
            profile(employment_type="contract"),
            observations=(*full_time_rows, one_contract_row),
            as_of=AS_OF,
            thresholds=FOUR_SAMPLES,
        )
        # Only one contract row exists, so the wider city+seniority cohort is used
        # and the fallback is named in the output.
        assert outcome.cohort_scope == "city_seniority"
        assert outcome.valid_sample_count == 5
        warning_codes = cast(Sequence[str], outcome.methodology["warning_codes"])
        assert "cohort_fallback_city_seniority" in warning_codes


class TestRefusals:
    """No data means no number — never a fabricated one."""

    def test_unknown_title_is_refused(self) -> None:
        with pytest.raises(InsufficientMarketDataError) as error:
            estimate_market_salary(
                profile(job_title="مترجم"), observations=cohort((400,)), as_of=AS_OF
            )
        assert error.value.reason == "no_job_family_match"

    def test_empty_sample_is_refused_with_counts(self) -> None:
        with pytest.raises(InsufficientMarketDataError) as error:
            estimate_market_salary(profile(), observations=(), as_of=AS_OF)
        assert error.value.reason == "insufficient_valid_samples"
        assert error.value.counts["required_samples"] == 5

    def test_sample_floor_is_enforced(self) -> None:
        with pytest.raises(InsufficientMarketDataError) as error:
            estimate_market_salary(profile(), observations=cohort((400, 500)), as_of=AS_OF)
        assert error.value.reason == "insufficient_valid_samples"

    def test_rows_with_unapproved_sources_cannot_produce_a_figure(self) -> None:
        observations = cohort((400, 500, 600, 700, 800))
        tainted = tuple(
            MarketObservation(
                id=row.id,
                family_key=row.family_key,
                job_title_reported=row.job_title_reported,
                city=row.city,
                amount_rial=row.amount_rial,
                period=row.period,
                currency_unit_reported=row.currency_unit_reported,
                source_id=row.source_id,
                license_status="unknown",
                collected_at=row.collected_at,
                seniority_level=row.seniority_level,
                employment_type=row.employment_type,
            )
            for row in observations
        )
        with pytest.raises(InsufficientMarketDataError) as error:
            estimate_market_salary(profile(), observations=tainted, as_of=AS_OF)
        assert error.value.counts["rejected_samples"] == 5

    def test_synthetic_sample_is_refused_by_default(self) -> None:
        observations = tuple(
            MarketObservation(
                id=row.id,
                family_key=row.family_key,
                job_title_reported=row.job_title_reported,
                city=row.city,
                amount_rial=row.amount_rial,
                period=row.period,
                currency_unit_reported=row.currency_unit_reported,
                source_id="sample_dev_v1",
                license_status="synthetic_dev",
                collected_at=row.collected_at,
                seniority_level=row.seniority_level,
                employment_type=row.employment_type,
                is_synthetic=True,
            )
            for row in cohort((400, 500, 600, 700, 800))
        )
        with pytest.raises(InsufficientMarketDataError):
            estimate_market_salary(profile(), observations=observations, as_of=AS_OF)


class TestAggregateFallback:
    """A published aggregate is a different, weaker data kind."""

    def aggregate(self, **overrides: object) -> MarketAggregate:
        base = {
            "id": "report-qa-tehran",
            "family_key": "qa_engineer",
            "city": "تهران",
            "seniority_level": "mid",
            "median_salary_rial": 330 * MILLION,
            "min_salary_rial": 270 * MILLION,
            "max_salary_rial": 410 * MILLION,
            "sample_size": 42,
            "source_id": "licensed-survey-1405",
            "license_status": "published_report",
            "collected_at": FRESH,
        }
        base.update(overrides)
        return MarketAggregate(**base)  # type: ignore[arg-type]

    def test_aggregate_is_used_when_no_raw_sample_exists(self) -> None:
        outcome = estimate_market_salary(
            profile(job_title="مهندس تست"),
            observations=(),
            aggregates=(self.aggregate(),),
            as_of=AS_OF,
        )
        assert outcome.primary_estimate_rial == 330 * MILLION
        assert outcome.min_salary_rial == 270 * MILLION
        assert outcome.methodology["method"] == "published_aggregate"
        assert outcome.confidence_level != "high"

    def test_aggregate_without_a_published_range_is_refused(self) -> None:
        with pytest.raises(InsufficientMarketDataError) as error:
            estimate_market_salary(
                profile(job_title="مهندس تست"),
                observations=(),
                aggregates=(
                    self.aggregate(min_salary_rial=None, max_salary_rial=None),
                ),
                as_of=AS_OF,
            )
        assert error.value.reason == "aggregate_missing_range"


class TestLegalReference:
    """The statutory reference is optional and never an input."""

    def test_missing_legal_reference_does_not_break_the_estimate(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def unavailable(_year: int) -> object:
            raise RuntimeError("rule set unavailable")

        monkeypatch.setattr(
            "app.domain.salary_estimation.salary_estimator.load_rule_set", unavailable
        )
        outcome = estimate_market_salary(
            profile(), observations=cohort((400, 500, 600, 700)), as_of=AS_OF, thresholds=FOUR_SAMPLES
        )
        assert outcome.legal_minimum_wage_rial is None
        warnings_1 = cast(Sequence[str], outcome.methodology["warning_codes"])
        assert "legal_minimum_wage_unavailable" in warnings_1
        assert outcome.primary_estimate_rial > 0

    def test_present_legal_reference_is_labelled_reference_only(self) -> None:
        outcome = estimate_market_salary(
            profile(), observations=cohort((400, 500, 600, 700)), as_of=AS_OF, thresholds=FOUR_SAMPLES
        )
        # The 1404 seed ships in the repository, so the reference is normally
        # available; whether or not it loads, its role is reference-only.
        warnings_2 = cast(Sequence[str], outcome.methodology["warning_codes"])
        assert "legal_reference_only" in warnings_2 or (
            outcome.legal_minimum_wage_rial is None
        )


class TestConfidence:
    """Confidence has components, a ceiling and an honest level."""

    def test_confidence_is_bounded_and_componentised(self) -> None:
        outcome = estimate_market_salary(
            profile(), observations=cohort((400, 500, 600, 700)), as_of=AS_OF, thresholds=FOUR_SAMPLES
        )
        assert 0 <= outcome.prediction_confidence <= 1
        assert 0 <= outcome.data_confidence <= 1
        assert outcome.prediction_confidence <= outcome.data_confidence
        assert "method_ceiling" in outcome.confidence_components

    def test_small_sample_cannot_claim_high_confidence(self) -> None:
        outcome = estimate_market_salary(
            profile(), observations=cohort((400, 500, 600, 700)), as_of=AS_OF, thresholds=FOUR_SAMPLES
        )
        assert outcome.confidence_level in {"low", "medium", "insufficient_data"}
        assert outcome.confidence_level != "high"

    def test_stale_sample_lowers_confidence(self) -> None:
        fresh = cohort((400, 500, 600, 700))
        stale = tuple(
            MarketObservation(
                id=row.id,
                family_key=row.family_key,
                job_title_reported=row.job_title_reported,
                city=row.city,
                amount_rial=row.amount_rial,
                period=row.period,
                currency_unit_reported=row.currency_unit_reported,
                source_id=row.source_id,
                license_status=row.license_status,
                collected_at=datetime(2025, 1, 1, tzinfo=UTC),
                seniority_level=row.seniority_level,
                employment_type=row.employment_type,
            )
            for row in fresh
        )
        fresh_outcome = estimate_market_salary(
            profile(), observations=fresh, as_of=AS_OF, thresholds=FOUR_SAMPLES
        )
        stale_outcome = estimate_market_salary(
            profile(), observations=stale, as_of=AS_OF, thresholds=FOUR_SAMPLES
        )
        assert stale_outcome.prediction_confidence < fresh_outcome.prediction_confidence

    def test_calculation_hash_is_stable_for_the_same_inputs(self) -> None:
        observations = cohort((400, 500, 600, 700))
        first = estimate_market_salary(
            profile(), observations=observations, as_of=AS_OF, thresholds=FOUR_SAMPLES
        )
        second = estimate_market_salary(
            profile(), observations=observations, as_of=AS_OF, thresholds=FOUR_SAMPLES
        )
        assert first.calculation_hash == second.calculation_hash
        assert len(first.calculation_hash) == 32
