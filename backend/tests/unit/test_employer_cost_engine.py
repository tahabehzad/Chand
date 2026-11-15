"""Unit tests for the employer Total Cost to Employer engine (P1-T11).

Authority:
    ``docs/PISH_HESABDARI_HOLY_BIBLE.md`` آ§2.3 H note and آ§1.2 pillar 3;
    ``REMEDIATED_TECHNICAL_SPECIFICATION_V2.md`` Module 6; ``FIND-MATH-02``
    (the 26-day leave reserve is removed from the CTC).
Related:
    WBS P1-T11 - CTC engine.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.engines.ctc import compute_employer_cost


def test_the_employer_cost_identity_holds_exactly() -> None:
    result = compute_employer_cost(
        total_gross_rial=341_850_120,
        employer_sso_rial=68_370_024,
        unemployment_rial=10_255_504,
        severance_accrual_rial=24_621_596,
        eydi_accrual_rial=25_977_420,
    )
    assert result.total_monthly_rial == (
        341_850_120 + 68_370_024 + 10_255_504 + 24_621_596 + 25_977_420
    )


def test_the_appendix_a4_corrected_total_is_reproduced() -> None:
    """A.4: the corrected monthly employer cost is 471,074,664."""
    result = compute_employer_cost(
        total_gross_rial=341_850_120,
        employer_sso_rial=68_370_024,
        unemployment_rial=10_255_504,
        severance_accrual_rial=24_621_596,
        eydi_accrual_rial=25_977_420,
    )
    assert result.total_monthly_rial == 471_074_664


def test_the_annual_ctc_is_twelve_months() -> None:
    result = compute_employer_cost(
        total_gross_rial=100_000_000,
        employer_sso_rial=20_000_000,
        unemployment_rial=3_000_000,
        severance_accrual_rial=8_333_333,
        eydi_accrual_rial=8_333_333,
    )
    assert result.annual_ctc_rial == result.total_monthly_rial * 12


def test_the_employer_burden_is_twenty_three_percent_of_the_gross() -> None:
    gross = 100_000_000
    result = compute_employer_cost(
        total_gross_rial=gross,
        employer_sso_rial=20_000_000,
        unemployment_rial=3_000_000,
        severance_accrual_rial=0,
        eydi_accrual_rial=0,
    )
    assert result.employer_sso_rial + result.unemployment_rial == 23_000_000
    assert result.total_monthly_rial == gross * Decimal("1.23")


def test_no_twenty_six_day_leave_reserve_is_added() -> None:
    """FIND-MATH-02: the 26 statutory leave days are already-paid days."""
    result = compute_employer_cost(
        total_gross_rial=100_000_000,
        employer_sso_rial=20_000_000,
        unemployment_rial=3_000_000,
        severance_accrual_rial=0,
        eydi_accrual_rial=0,
    )
    # A 26-day reserve would add roughly a further month of salary.
    assert result.total_monthly_rial == 123_000_000
    assert result.total_monthly_rial < 100_000_000 * 2


@pytest.mark.parametrize(
    "field",
    [
        "total_gross_rial",
        "employer_sso_rial",
        "unemployment_rial",
        "severance_accrual_rial",
        "eydi_accrual_rial",
    ],
)
def test_a_negative_line_is_refused(field: str) -> None:
    kwargs = {
        "total_gross_rial": 100,
        "employer_sso_rial": 20,
        "unemployment_rial": 3,
        "severance_accrual_rial": 8,
        "eydi_accrual_rial": 8,
    }
    kwargs[field] = -1
    with pytest.raises(ValueError, match="PAYROLL_INPUT_INVALID"):
        compute_employer_cost(**kwargs)


def test_a_boolean_line_is_refused() -> None:
    with pytest.raises(ValueError, match="PAYROLL_INPUT_INVALID"):
        compute_employer_cost(
            total_gross_rial=True,
            employer_sso_rial=0,
            unemployment_rial=0,
            severance_accrual_rial=0,
            eydi_accrual_rial=0,
        )
