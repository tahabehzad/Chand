"""Unit tests for the overtime and night-shift premium engine (P1-T10).

Authority:
    ``docs/PISH_HESABDARI_HOLY_BIBLE.md`` §2.3 G; Labour Law Arts. 36
    Note 3, 51 and 59; ``FIND-LEG-03``.
Related:
    WBS P1-T10 - overtime engine.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

import pytest

from app.engines.errors import MonthLengthInvalid
from app.engines.overtime import compute_overtime_premiums
from app.engines.rules import StatutoryRuleSet, load_rule_set

APPENDIX_A_SAABET = 295_459_152


@pytest.fixture(scope="module")
def rule_set() -> StatutoryRuleSet:
    """Return the loaded 1404 rule set."""
    return load_rule_set(1404)


def _rial(value: Decimal) -> int:
    """Round a Decimal to whole Rial, half up."""
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def test_the_thirty_day_divisor_is_220_paid_calendar_hours(
    rule_set: StatutoryRuleSet,
) -> None:
    """44 hours over 6 working days; the 176-hour figure is never used."""
    result = compute_overtime_premiums(APPENDIX_A_SAABET, 0, 0, rule_set, 30)
    assert result.divisor == Decimal("220.00")
    assert result.divisor != Decimal("176.00")


def test_the_thirty_one_day_divisor_is_44_times_31_over_6(
    rule_set: StatutoryRuleSet,
) -> None:
    result = compute_overtime_premiums(APPENDIX_A_SAABET, 0, 0, rule_set, 31)
    assert result.divisor == Decimal("44.00") * 31 / 6


def test_the_twenty_nine_day_divisor_is_44_times_29_over_6(
    rule_set: StatutoryRuleSet,
) -> None:
    result = compute_overtime_premiums(APPENDIX_A_SAABET, 0, 0, rule_set, 29)
    assert result.divisor == Decimal("44.00") * 29 / 6


def test_the_overtime_premium_uses_the_saabet_base_and_the_multiplier(
    rule_set: StatutoryRuleSet,
) -> None:
    hourly = Decimal(APPENDIX_A_SAABET) / Decimal("220.00")
    expected = _rial(hourly * 10 * rule_set.overtime_multiplier)
    result = compute_overtime_premiums(APPENDIX_A_SAABET, 10, 0, rule_set, 30)
    assert result.hourly_rate_exact == hourly
    assert result.overtime_pay_rial == expected
    assert result.overtime_pay_rial == 18_801_946


def test_the_night_shift_premium_uses_its_own_multiplier(
    rule_set: StatutoryRuleSet,
) -> None:
    hourly = Decimal(APPENDIX_A_SAABET) / Decimal("220.00")
    expected = _rial(hourly * 5 * rule_set.night_shift_multiplier)
    result = compute_overtime_premiums(APPENDIX_A_SAABET, 0, 5, rule_set, 30)
    assert result.night_pay_rial == expected
    assert result.night_pay_rial == 9_065_224


def test_the_premium_total_is_the_sum_of_the_two_lines(
    rule_set: StatutoryRuleSet,
) -> None:
    result = compute_overtime_premiums(APPENDIX_A_SAABET, 12, 8, rule_set, 30)
    assert result.premium_total_rial == (
        result.overtime_pay_rial + result.night_pay_rial
    )


def test_no_hours_means_no_premium(rule_set: StatutoryRuleSet) -> None:
    result = compute_overtime_premiums(APPENDIX_A_SAABET, 0, 0, rule_set, 30)
    assert result.overtime_pay_rial == 0
    assert result.night_pay_rial == 0
    assert result.premium_total_rial == 0


def test_the_welfare_allowances_are_excluded_from_the_base(
    rule_set: StatutoryRuleSet,
) -> None:
    """The premium base is Mozd-e Saabet, never the gross (FIND-LEG-03)."""
    with_welfare = compute_overtime_premiums(100_000_000, 10, 0, rule_set, 30)
    without_welfare = compute_overtime_premiums(130_000_000, 10, 0, rule_set, 30)
    # 130,000,000 - 100,000,000 is exactly the 30,000,000 of welfare that the
    # decomposition removed, so the two hourly rates differ.
    assert with_welfare.hourly_rate_exact < without_welfare.hourly_rate_exact


def test_a_longer_month_raises_the_hourly_rate_never_lowers_it(
    rule_set: StatutoryRuleSet,
) -> None:
    thirty = compute_overtime_premiums(APPENDIX_A_SAABET, 10, 0, rule_set, 30)
    thirty_one = compute_overtime_premiums(APPENDIX_A_SAABET, 10, 0, rule_set, 31)
    assert thirty_one.hourly_rate_exact < thirty.hourly_rate_exact


@pytest.mark.parametrize(
    ("overtime_hours", "night_hours"),
    [(-1, 0), (0, -1), (True, 0), (0, 1.5), (-5, -5)],
)
def test_an_invalid_hour_count_is_refused(
    rule_set: StatutoryRuleSet, overtime_hours: int, night_hours: int
) -> None:
    with pytest.raises(ValueError, match="PAYROLL_INPUT_INVALID"):
        compute_overtime_premiums(
            APPENDIX_A_SAABET, overtime_hours, night_hours, rule_set, 30
        )


def test_an_invalid_base_is_refused(rule_set: StatutoryRuleSet) -> None:
    with pytest.raises(ValueError, match="PAYROLL_INPUT_INVALID"):
        compute_overtime_premiums(-1, 0, 0, rule_set, 30)


def test_an_impossible_month_length_is_refused(rule_set: StatutoryRuleSet) -> None:
    with pytest.raises(MonthLengthInvalid):
        compute_overtime_premiums(APPENDIX_A_SAABET, 0, 0, rule_set, 28)
