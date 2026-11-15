"""Unit tests for the termination and probation liability engine (P1-T12).

Authority:
    ``docs/PISH_HESABDARI_HOLY_BIBLE.md`` §2.3 H/I; Labour Law Arts. 11,
    24, 66 and 71; ``FIND-LEG-01`` (probation) and ``FIND-LEG-06`` (leave
    buyout).
Related:
    WBS P1-T12 - termination-liability simulator.
"""

from __future__ import annotations

import pytest

from app.engines.termination import (
    MAX_LEAVE_CARRYOVER_DAYS_PER_YEAR,
    MAX_PROBATION_MONTHS,
    compute_termination_liability,
)

GROSS = 100_000_000
SAABET = 100_000_000


def test_the_employer_initiated_probation_liability_is_the_whole_period() -> None:
    """FIND-LEG-01: Art. 11 is never truncated by the days worked."""
    result = compute_termination_liability(
        SAABET,
        GROSS,
        days_in_month=30,
        probation_months=3,
        tenure_months=0,
        accumulated_unused_leave_days=0,
        probation_days_worked=15,
    )
    assert result.probation_months == 3
    assert result.employer_initiated_probation_liability_rial == 300_000_000


def test_the_employer_liability_does_not_depend_on_the_days_worked() -> None:
    early = compute_termination_liability(
        SAABET,
        GROSS,
        days_in_month=30,
        probation_months=3,
        tenure_months=0,
        accumulated_unused_leave_days=0,
        probation_days_worked=1,
    )
    late = compute_termination_liability(
        SAABET,
        GROSS,
        days_in_month=30,
        probation_months=3,
        tenure_months=0,
        accumulated_unused_leave_days=0,
        probation_days_worked=90,
    )
    assert (
        early.employer_initiated_probation_liability_rial
        == late.employer_initiated_probation_liability_rial
        == 300_000_000
    )


def test_the_employee_initiated_liability_is_the_days_worked() -> None:
    result = compute_termination_liability(
        SAABET,
        GROSS,
        days_in_month=30,
        probation_months=3,
        tenure_months=0,
        accumulated_unused_leave_days=0,
        probation_days_worked=15,
    )
    assert result.employee_initiated_probation_liability_rial == 50_000_000


def test_the_employee_liability_is_absent_without_days_worked() -> None:
    result = compute_termination_liability(
        SAABET,
        GROSS,
        days_in_month=30,
        probation_months=2,
        tenure_months=0,
        accumulated_unused_leave_days=0,
    )
    assert result.employee_initiated_probation_liability_rial is None


def test_the_probation_period_cannot_exceed_the_statutory_maximum() -> None:
    with pytest.raises(ValueError, match="PROBATION_BEYOND_STATUTORY_MAX"):
        compute_termination_liability(
            SAABET,
            GROSS,
            days_in_month=30,
            probation_months=MAX_PROBATION_MONTHS + 1,
            tenure_months=0,
            accumulated_unused_leave_days=0,
        )


def test_a_zero_probation_period_is_refused() -> None:
    with pytest.raises(ValueError, match="PAYROLL_INPUT_INVALID"):
        compute_termination_liability(
            SAABET,
            GROSS,
            days_in_month=30,
            probation_months=0,
            tenure_months=0,
            accumulated_unused_leave_days=0,
        )


def test_the_exit_severance_is_one_month_per_year_of_service() -> None:
    result = compute_termination_liability(
        SAABET,
        GROSS,
        days_in_month=30,
        probation_months=1,
        tenure_months=24,
        accumulated_unused_leave_days=0,
    )
    assert result.exit_severance_rial == 200_000_000


def test_the_exit_severance_is_pro_rated_by_tenure_months() -> None:
    result = compute_termination_liability(
        SAABET,
        GROSS,
        days_in_month=30,
        probation_months=1,
        tenure_months=18,
        accumulated_unused_leave_days=0,
    )
    assert result.exit_severance_rial == 150_000_000


def test_the_leave_carryover_is_capped_at_nine_days_per_year() -> None:
    """FIND-LEG-06: Art. 66 caps the carryover at nine days per year."""
    result = compute_termination_liability(
        SAABET,
        GROSS,
        days_in_month=30,
        probation_months=1,
        tenure_months=24,
        accumulated_unused_leave_days=40,
    )
    assert result.leave_carryover_cap_days == (
        MAX_LEAVE_CARRYOVER_DAYS_PER_YEAR * 2
    )
    assert result.effective_buyout_days == 18
    assert result.accumulated_unused_leave_days_input == 40


def test_the_leave_buyout_pays_every_day_up_to_the_cap() -> None:
    """Art. 71: all accumulated unused days are paid at exit."""
    result = compute_termination_liability(
        SAABET,
        GROSS,
        days_in_month=30,
        probation_months=1,
        tenure_months=24,
        accumulated_unused_leave_days=12,
    )
    assert result.effective_buyout_days == 12
    assert result.leave_buyout_rial == 40_000_000  # 12 x (100,000,000 / 30)


def test_the_total_separation_is_the_severance_plus_the_buyout() -> None:
    result = compute_termination_liability(
        SAABET,
        GROSS,
        days_in_month=30,
        probation_months=1,
        tenure_months=24,
        accumulated_unused_leave_days=12,
    )
    assert result.total_separation_rial == (
        result.exit_severance_rial + result.leave_buyout_rial
    )


def test_a_zero_tenure_yields_no_exit_severance() -> None:
    result = compute_termination_liability(
        SAABET,
        GROSS,
        days_in_month=30,
        probation_months=1,
        tenure_months=0,
        accumulated_unused_leave_days=0,
    )
    assert result.exit_severance_rial == 0
    assert result.leave_carryover_cap_days == 0
    assert result.total_separation_rial == 0


@pytest.mark.parametrize(
    "field",
    [
        "days_in_month",
        "tenure_months",
        "accumulated_unused_leave_days",
        "probation_days_worked",
    ],
)
def test_a_negative_input_is_refused(field: str) -> None:
    kwargs = {
        "days_in_month": 30,
        "probation_months": 1,
        "tenure_months": 0,
        "accumulated_unused_leave_days": 0,
        "probation_days_worked": None,
    }
    kwargs[field] = -1
    with pytest.raises(ValueError, match="PAYROLL_INPUT_INVALID"):
        compute_termination_liability(SAABET, GROSS, **kwargs)  # type: ignore[arg-type]
