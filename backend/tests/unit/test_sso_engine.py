"""Unit tests for the Social Security Organization engine (P1-T06).

Authority:
    ``docs/PISH_HESABDARI_HOLY_BIBLE.md`` آ§2.3 A; Social Security Law
    Arts. 28 and 39; Unemployment Insurance Act; SSO circular S4 item 13.
Spec:
    ``docs/specs/TESTING.md`` property P-04.
Related:
    WBS P1-T06 - SSO engine.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.engines.errors import RuleSetNotActive
from app.engines.rules import StatutoryRuleSet, load_rule_set
from app.engines.sso import compute_sso

DAILY_INSURABLE_CEILING_RIAL = 24_245_592
CEILING_29D = DAILY_INSURABLE_CEILING_RIAL * 29
CEILING_30D = DAILY_INSURABLE_CEILING_RIAL * 30
CEILING_31D = DAILY_INSURABLE_CEILING_RIAL * 31


@pytest.fixture(scope="module")
def rule_set() -> StatutoryRuleSet:
    """Return the loaded 1404 rule set."""
    return load_rule_set(1404)


def test_the_three_rates_are_applied_to_the_insurable_wage(
    rule_set: StatutoryRuleSet,
) -> None:
    """Appendix A steps 3 and 7: the reference package's exact lines."""
    result = compute_sso(341_850_120, rule_set, 30)
    assert result.employee_share_rial == 23_929_508
    assert result.employer_share_rial == 68_370_024
    assert result.unemployment_share_rial == 10_255_504


def test_the_employee_share_is_also_returned_unrounded(
    rule_set: StatutoryRuleSet,
) -> None:
    """The Art. 137 deduction is computed on the insurable wage, not on a
    rounded line (iranian-payroll-engineering rule 15)."""
    result = compute_sso(341_850_120, rule_set, 30)
    assert result.employee_share_exact == Decimal("23929508.40")
    assert result.employee_share_rial == 23_929_508


def test_the_ceiling_is_not_applied_below_it(rule_set: StatutoryRuleSet) -> None:
    result = compute_sso(341_850_120, rule_set, 30)
    assert result.ceiling_rial == CEILING_30D
    assert result.insurable_wage_rial == 341_850_120
    assert result.ceiling_applied is False


def test_the_ceiling_applies_exactly_at_the_boundary(
    rule_set: StatutoryRuleSet,
) -> None:
    """At the ceiling the wage is fully insurable and the flag stays false."""
    result = compute_sso(CEILING_30D, rule_set, 30)
    assert result.insurable_wage_rial == CEILING_30D
    assert result.ceiling_applied is False
    assert result.employee_share_rial == 50_915_743


def test_the_ceiling_applies_one_rial_above_the_boundary(
    rule_set: StatutoryRuleSet,
) -> None:
    result = compute_sso(CEILING_30D + 1, rule_set, 30)
    assert result.insurable_wage_rial == CEILING_30D
    assert result.ceiling_applied is True


def test_a_gross_far_above_the_ceiling_is_capped(rule_set: StatutoryRuleSet) -> None:
    result = compute_sso(5_000_000_000, rule_set, 30)
    assert result.insurable_wage_rial == CEILING_30D
    assert result.ceiling_applied is True
    assert result.employee_share_rial == 50_915_743
    assert result.employer_share_rial == 145_473_552
    assert result.unemployment_share_rial == 21_821_033


@pytest.mark.parametrize(
    ("days", "expected"),
    [(29, CEILING_29D), (30, CEILING_30D), (31, CEILING_31D)],
)
def test_the_ceiling_follows_the_month_length(
    rule_set: StatutoryRuleSet, days: int, expected: int
) -> None:
    result = compute_sso(expected, rule_set, days)
    assert result.ceiling_rial == expected
    assert result.insurable_wage_rial == expected


def test_the_ceiling_is_seven_daily_minimum_wages_per_day(
    rule_set: StatutoryRuleSet,
) -> None:
    for days in (29, 30, 31):
        result = compute_sso(1, rule_set, days)
        assert result.ceiling_rial == rule_set.daily_minimum_wage_rial * 7 * days


def test_the_employer_and_employee_shares_sum_to_27_percent(
    rule_set: StatutoryRuleSet,
) -> None:
    """Property P-04, for a gross below and above the ceiling."""
    for gross in (1, 50_000_000, CEILING_30D, CEILING_30D + 1, 5_000_000_000):
        result = compute_sso(gross, rule_set, 30)
        expected = Decimal("0.27") * Decimal(result.insurable_wage_rial)
        actual = Decimal(result.employee_share_rial) + Decimal(result.employer_share_rial)
        assert abs(actual - expected) <= 1


def test_the_unemployment_insurance_is_employer_paid_only(
    rule_set: StatutoryRuleSet,
) -> None:
    result = compute_sso(100_000_000, rule_set, 30)
    assert result.unemployment_share_rial == 3_000_000
    assert result.employee_share_rial == 7_000_000


def test_a_non_integer_earnings_value_is_refused(rule_set: StatutoryRuleSet) -> None:
    with pytest.raises(TypeError):
        compute_sso(1.5, rule_set, 30)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        compute_sso(True, rule_set, 30)


def test_an_impossible_month_length_is_refused(rule_set: StatutoryRuleSet) -> None:
    with pytest.raises(RuleSetNotActive):
        compute_sso(1_000_000, rule_set, 28)
