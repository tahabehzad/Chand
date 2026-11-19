"""Money-path post-conditions for a published estimate.

Authority: ``AGENTS.md`` §2 Financial invariants 7-8; ADR-013's currency convention
as reconciled in ``docs/adr/ADR-014`` §4.6.

The previous version of this module claimed to validate range consistency but only
summed the values, so ``min > max`` passed.  These tests pin the check that the
name always promised.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from app.domain.salary_estimation.money_validation import validate_estimate_money_path


class TestOrderingAndCurrency:
    """Ordering, sign and exact Toman divisibility."""

    def test_a_correct_estimate_passes(self) -> None:
        report = validate_estimate_money_path(
            min_salary_rial=475_000_000,
            median_salary_rial=550_000_000,
            primary_estimate_rial=550_000_000,
            max_salary_rial=625_000_000,
        )
        assert report.passed
        assert report.ordering_ok
        assert report.toman_exact

    def test_inverted_range_fails(self) -> None:
        report = validate_estimate_money_path(
            min_salary_rial=625_000_000,
            median_salary_rial=550_000_000,
            primary_estimate_rial=550_000_000,
            max_salary_rial=475_000_000,
        )
        assert not report.passed
        assert not report.ordering_ok

    def test_a_figure_that_is_not_a_whole_toman_fails(self) -> None:
        report = validate_estimate_money_path(
            min_salary_rial=475_000_003,
            median_salary_rial=550_000_000,
            primary_estimate_rial=550_000_000,
            max_salary_rial=625_000_000,
        )
        assert not report.passed
        assert not report.toman_exact

    def test_primary_must_equal_the_market_median(self) -> None:
        report = validate_estimate_money_path(
            min_salary_rial=475_000_000,
            median_salary_rial=550_000_000,
            primary_estimate_rial=560_000_000,
            max_salary_rial=625_000_000,
        )
        assert not report.passed
        assert any("median" in issue for issue in report.issues)

    def test_negative_amount_fails(self) -> None:
        report = validate_estimate_money_path(
            min_salary_rial=-10,
            median_salary_rial=550_000_000,
            primary_estimate_rial=550_000_000,
            max_salary_rial=625_000_000,
        )
        assert not report.passed


class TestReportShape:
    """The report is immutable and self-describing."""

    def test_report_is_frozen(self) -> None:
        report = validate_estimate_money_path(10, 10, 10, 10)
        with pytest.raises(FrozenInstanceError):
            report.issues = ()  # type: ignore[misc]

    def test_issues_are_empty_on_success(self) -> None:
        assert validate_estimate_money_path(10, 10, 10, 10).issues == ()
