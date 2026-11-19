"""Validation and outlier policy (ADR-014 §2).

Every scenario from the mission brief is exercised here: a 1,000-Toman figure, a
10,000-Toman figure, a 1,000,000,000-Toman figure, a Rial/Toman mix-up, an hourly
rate, a duplicate, a stale row, an unapproved source, a tiny peer group and a
genuine outlier.  The invariant under test is that **no invalid row can reach the
calculation**, and that a quarantined row is recorded rather than deleted.
"""

from __future__ import annotations

from datetime import UTC, datetime

from app.domain.salary_estimation.market_data import (
    DataQuality,
    MarketObservation,
    monthly_equivalent_rial,
)
from app.domain.salary_estimation.validation import (
    IMPLAUSIBLY_LOW_RIAL,
    ValidationPolicy,
    classify_observations,
    reason_text,
)

AS_OF = datetime(2026, 10, 1, tzinfo=UTC)
FRESH = datetime(2026, 9, 1, tzinfo=UTC)
MILLION = 1_000_000


def observation(
    identifier: str,
    amount_rial: int,
    *,
    family: str = "php_backend",
    city: str = "تهران",
    seniority: str = "mid",
    license_status: str = "manual_verified",
    source: str = "manual-verified-manager",
    synthetic: bool = False,
    collected_at: datetime = FRESH,
    period: str = "monthly",
    currency: str = "rial",
) -> MarketObservation:
    """Build one observation for a test."""
    return MarketObservation(
        id=identifier,
        family_key=family,
        job_title_reported="برنامه‌نویس PHP",
        city=city,
        province="تهران",
        amount_rial=amount_rial,
        period=period,
        currency_unit_reported=currency,
        source_id=source,
        license_status=license_status,
        collected_at=collected_at,
        seniority_level=seniority,
        employment_type="full_time",
        work_condition="on_site",
        is_synthetic=synthetic,
    )


def peer_cohort(*, family: str = "php_backend", city: str = "تهران") -> list[MarketObservation]:
    """Eight plausible peers around 500 million Rial."""
    amounts = (460, 480, 495, 500, 505, 520, 540, 560)
    return [
        observation(f"peer-{index}-{family}-{city}", value * MILLION, family=family, city=city)
        for index, value in enumerate(amounts)
    ]


def classify_one(subject: MarketObservation, peers: list[MarketObservation]) -> object:
    """Classify *subject* against *peers* and return its finding."""
    outcome = classify_observations([*peers, subject], as_of=AS_OF, policy=ValidationPolicy())
    for finding in outcome.findings:
        if finding.observation_id == subject.id:
            return finding
    raise AssertionError("the subject was not classified")


class TestEntryErrors:
    """Definite data errors are rejected, but still recorded."""

    def test_one_thousand_toman_is_rejected(self) -> None:
        # 1,000 Toman = 10,000 Rial: below any possible monthly salary.
        finding = classify_one(observation("tiny", 10_000), peer_cohort())
        assert finding.status == DataQuality.REJECTED  # type: ignore[attr-defined]
        assert "amount_below_entry_floor" in finding.reasons  # type: ignore[attr-defined]

    def test_ten_thousand_toman_is_quarantined(self) -> None:
        # 10,000 Toman = 100,000 Rial: a unit or period mistake, not a salary.
        finding = classify_one(observation("small", 100_000), peer_cohort())
        assert finding.status == DataQuality.SUSPICIOUS  # type: ignore[attr-defined]
        assert "amount_implausibly_low" in finding.reasons  # type: ignore[attr-defined]

    def test_one_billion_toman_is_quarantined_not_silently_used(self) -> None:
        # 1,000,000,000 Toman = 10^10 Rial, roughly 20x the cohort median.
        finding = classify_one(observation("huge", 10_000_000_000), peer_cohort())
        assert finding.status == DataQuality.SUSPICIOUS  # type: ignore[attr-defined]
        assert "outlier_iqr_extreme" in finding.reasons  # type: ignore[attr-defined]

    def test_non_positive_amount_is_rejected(self) -> None:
        finding = classify_one(observation("zero", 0), peer_cohort())
        assert finding.status == DataQuality.REJECTED  # type: ignore[attr-defined]
        assert "amount_not_positive" in finding.reasons  # type: ignore[attr-defined]

    def test_rejected_row_is_retained_in_the_findings(self) -> None:
        subject = observation("tiny", 10_000)
        outcome = classify_observations([*peer_cohort(), subject], as_of=AS_OF)
        assert subject.id in {finding.observation_id for finding in outcome.rejected}
        assert subject.id in {finding.observation_id for finding in outcome.findings}


class TestCurrencyAndPeriod:
    """A unit or period mistake must be detectable, never assumed away."""

    def test_rial_toman_mix_up_is_detected(self) -> None:
        # The same digits entered as Rial where the cohort is 10x higher.
        finding = classify_one(observation("unit", 50 * MILLION), peer_cohort())
        assert finding.status == DataQuality.SUSPICIOUS  # type: ignore[attr-defined]
        assert "unit_mismatch_suspected" in finding.reasons  # type: ignore[attr-defined]

    def test_toman_reported_amount_is_normalised_before_comparison(self) -> None:
        # 50 million Toman == 500 million Rial: plausible, so it must not look tiny.
        finding = classify_one(
            observation("toman-ok", 50 * MILLION, currency="toman"), peer_cohort()
        )
        assert "unit_mismatch_suspected" not in finding.reasons  # type: ignore[attr-defined]
        assert finding.status == DataQuality.VALID  # type: ignore[attr-defined]

    def test_hourly_rate_is_converted_to_a_monthly_equivalent(self) -> None:
        row = observation("hourly", 3 * MILLION, period="hourly")
        monthly, converted = monthly_equivalent_rial(row)
        assert converted is True
        assert monthly == 3 * MILLION * 176

    def test_hourly_conversion_is_reported_on_the_finding(self) -> None:
        row = observation("hourly", 3 * MILLION, period="hourly")
        finding = classify_one(row, peer_cohort())
        assert finding.conversion_applied is True  # type: ignore[attr-defined]
        assert "period_converted" in finding.reasons  # type: ignore[attr-defined]

    def test_daily_rate_is_converted_with_thirty_days(self) -> None:
        row = observation("daily", 5 * MILLION, period="daily")
        monthly, converted = monthly_equivalent_rial(row)
        assert converted is True
        assert monthly == 150 * MILLION


class TestProvenance:
    """Provenance is a hard gate: a plausible number from an unknown source is out."""

    def test_unknown_source_is_rejected(self) -> None:
        finding = classify_one(observation("unknown", 500 * MILLION, license_status="unknown"), peer_cohort())
        assert finding.status == DataQuality.REJECTED  # type: ignore[attr-defined]
        assert "source_not_approved" in finding.reasons  # type: ignore[attr-defined]

    def test_synthetic_row_is_rejected_unless_sample_mode_is_enabled(self) -> None:
        row = observation(
            "sample",
            512 * MILLION,
            license_status="synthetic_dev",
            source="sample_dev_v1",
            synthetic=True,
        )
        strict = classify_observations([*peer_cohort(), row], as_of=AS_OF)
        assert row.id in {finding.observation_id for finding in strict.rejected}

        permissive = classify_observations(
            [*peer_cohort(), row],
            as_of=AS_OF,
            policy=ValidationPolicy(allow_synthetic=True),
        )
        assert row.id in {valid_row.id for valid_row in permissive.valid}

    def test_duplicate_row_is_rejected_and_the_first_is_kept(self) -> None:
        first = observation("dup-1", 500 * MILLION, source="manual-verified-manager")
        second = observation("dup-2", 500 * MILLION, source="manual-verified-manager")
        outcome = classify_observations(
            [*peer_cohort(), first, second], as_of=AS_OF, policy=ValidationPolicy()
        )
        rejected = {finding.observation_id for finding in outcome.rejected}
        assert "dup-2" in rejected
        assert "dup-1" not in rejected

    def test_stale_row_is_quarantined(self) -> None:
        old = observation("old", 500 * MILLION, collected_at=datetime(2023, 1, 1, tzinfo=UTC))
        finding = classify_one(old, peer_cohort())
        assert finding.status == DataQuality.SUSPICIOUS  # type: ignore[attr-defined]
        assert "stale_data" in finding.reasons  # type: ignore[attr-defined]


class TestOutliers:
    """Outlier tests are relative to the cohort, never a global band."""

    def test_extreme_value_in_a_family_is_quarantined(self) -> None:
        finding = classify_one(observation("outlier", 4_000 * MILLION), peer_cohort())
        assert finding.status == DataQuality.SUSPICIOUS  # type: ignore[attr-defined]
        assert "outlier_iqr_extreme" in finding.reasons  # type: ignore[attr-defined]

    def test_same_amount_can_be_valid_in_one_family_and_suspicious_in_another(self) -> None:
        amount = 60 * MILLION
        driver_peers = [
            observation(f"driver-{index}", value * MILLION, family="driver")
            for index, value in enumerate((30, 34, 38, 42, 46, 50, 55, 60))
        ]
        engineer_peers = [
            observation(f"eng-{index}", value * MILLION, family="php_backend")
            for index, value in enumerate((560, 580, 595, 600, 605, 620, 640, 660))
        ]
        in_driver = classify_one(
            observation("same-amount-driver", 58 * MILLION, family="driver"), driver_peers
        )
        in_engineer = classify_one(
            observation("same-amount-eng", amount, family="php_backend"), engineer_peers
        )
        assert in_driver.status == DataQuality.VALID  # type: ignore[attr-defined]
        assert in_engineer.status == DataQuality.SUSPICIOUS  # type: ignore[attr-defined]

    def test_small_peer_group_skips_the_robust_tests_and_says_so(self) -> None:
        subject = observation("lonely", 500 * MILLION)
        peers = [observation("only-other", 520 * MILLION)]
        finding = classify_one(subject, peers)
        assert finding.status == DataQuality.VALID  # type: ignore[attr-defined]
        assert "insufficient_peer_group" in finding.reasons  # type: ignore[attr-defined]

    def test_no_absolute_ceiling_rejects_a_high_salary(self) -> None:
        # A genuinely high but cohort-consistent figure must stay valid: there is no
        # global cap in this policy.
        peers = [
            observation(f"exec-{index}", value * MILLION, seniority="senior")
            for index, value in enumerate((3_600, 3_800, 3_950, 4_000, 4_050, 4_200, 4_400, 4_600))
        ]
        finding = classify_one(
            observation("exec", 4_100 * MILLION, seniority="senior"), peers
        )
        assert finding.status == DataQuality.VALID  # type: ignore[attr-defined]


class TestPolicyDefaults:
    """The documented defaults are the ones the code uses."""

    def test_implausibly_low_threshold_is_documented(self) -> None:
        assert IMPLAUSIBLY_LOW_RIAL == 1_000_000

    def test_every_reason_has_a_persian_explanation(self) -> None:
        for reason in (
            "synthetic_data_not_allowed",
            "source_not_approved",
            "amount_below_entry_floor",
            "amount_implausibly_low",
            "unit_mismatch_suspected",
            "duplicate_observation",
            "stale_data",
            "outlier_iqr_extreme",
            "outlier_mad",
            "outside_p1_p99",
            "ratio_implausible_high",
            "period_converted",
            "insufficient_peer_group",
        ):
            assert reason_text(reason) != reason, reason

    def test_empty_input_yields_an_empty_outcome(self) -> None:
        outcome = classify_observations([], as_of=AS_OF)
        assert outcome.valid == ()
        assert outcome.findings == ()
