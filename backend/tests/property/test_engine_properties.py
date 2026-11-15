"""Property-based tests for the statutory payroll engine (P1-T16).

Authority:
    ``docs/specs/TESTING.md`` §4 (the property layer) and the property
    table P-02, P-03, P-04, P-05, P-06, P-07, P-08 and P-10.
Scope:
    ADR-008 keeps the engine properties in scope.  P-01 (the inverter
    round-trip) follows ``P1-T13``, which is out of product scope.
Related:
    WBS P1-T16 - property-based test suite.
"""

from __future__ import annotations

from decimal import Decimal

from hypothesis import HealthCheck, given, settings, strategies as st

from app.engines.bases import Allowances, decompose_bases
from app.engines.eydi import compute_eydi
from app.engines.overtime import compute_overtime_premiums
from app.engines.rules import load_rule_set
from app.engines.severance import compute_monthly_severance_accrual
from app.engines.sso import compute_sso
from app.engines.tax import (
    POSTURE_CONSERVATIVE_INTA,
    POSTURE_COURT_PRECEDENT,
    compute_tax_for_posture,
)
from app.services.payroll_service import PayrollInput, compute_gross_to_net

RULE_SET = load_rule_set(1404)

SETTINGS = settings(
    max_examples=200,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)

#: A plausible gross band for a single month, in whole Rial.
GROSSES = st.integers(min_value=1, max_value=5_000_000_000)
#: The three statutory month lengths.
MONTH_LENGTHS = st.sampled_from([29, 30, 31])
#: The five monthly allowances, each non-negative and plausible.
ALLOWANCES = st.builds(
    Allowances,
    housing_rial=st.integers(min_value=0, max_value=20_000_000),
    grocery_rial=st.integers(min_value=0, max_value=30_000_000),
    marriage_rial=st.integers(min_value=0, max_value=10_000_000),
    child_rial=st.integers(min_value=0, max_value=40_000_000),
    continuous_attraction_rial=st.integers(min_value=0, max_value=60_000_000),
)


def _welfare_total(allowances: Allowances) -> int:
    """Return the Art. 36 Note 3 welfare total of *allowances*."""
    return (
        allowances.housing_rial
        + allowances.grocery_rial
        + allowances.marriage_rial
        + allowances.child_rial
    )


@SETTINGS
@given(gross=GROSSES, days=MONTH_LENGTHS)
def test_p04_the_employer_and_employee_shares_sum_to_27_percent(
    gross: int, days: int
) -> None:
    result = compute_sso(gross, RULE_SET, days)
    expected = Decimal("0.27") * Decimal(result.insurable_wage_rial)
    actual = Decimal(result.employee_share_rial) + Decimal(result.employer_share_rial)
    assert abs(actual - expected) <= 1


@SETTINGS
@given(gross=GROSSES, days=MONTH_LENGTHS)
def test_p04_the_insurable_wage_never_exceeds_the_ceiling(gross: int, days: int) -> None:
    result = compute_sso(gross, RULE_SET, days)
    assert result.insurable_wage_rial <= result.ceiling_rial
    assert result.insurable_wage_rial <= gross
    assert result.ceiling_applied == (gross > result.ceiling_rial)


@SETTINGS
@given(gross=GROSSES, allowances=ALLOWANCES, days=MONTH_LENGTHS)
def test_p05_the_sanavat_accrual_is_one_twelfth_of_the_base(
    gross: int, allowances: Allowances, days: int
) -> None:
    welfare = (
        allowances.housing_rial
        + allowances.grocery_rial
        + allowances.marriage_rial
        + allowances.child_rial
    )
    if gross < welfare:
        return
    saabet = gross - welfare
    result = compute_monthly_severance_accrual(saabet)
    assert abs(result.monthly_accrual_rial - saabet / 12) <= 1


@SETTINGS
@given(gross=GROSSES, allowances=ALLOWANCES)
def test_p06_the_eydi_is_the_smaller_of_twice_the_base_and_the_cap(
    gross: int, allowances: Allowances
) -> None:
    welfare = (
        allowances.housing_rial
        + allowances.grocery_rial
        + allowances.marriage_rial
        + allowances.child_rial
    )
    if gross < welfare:
        return
    saabet = gross - welfare
    result = compute_eydi(saabet, RULE_SET)
    assert result.annual_gross_rial == min(
        2 * saabet, 3 * RULE_SET.monthly_minimum_wage_30days_rial
    )
    assert result.at_cap == (2 * saabet > RULE_SET.max_annual_eydi_rial)


@SETTINGS
@given(gross=GROSSES, allowances=ALLOWANCES, days=MONTH_LENGTHS)
def test_p07_the_taxable_base_is_never_negative(
    gross: int, allowances: Allowances, days: int
) -> None:
    sso = compute_sso(gross, RULE_SET, days)
    for posture in (POSTURE_CONSERVATIVE_INTA, POSTURE_COURT_PRECEDENT):
        result = compute_tax_for_posture(
            gross,
            sso.employee_share_exact,
            allowances.welfare_total_rial,
            0,
            posture=posture,
            rule_set=RULE_SET,
        )
        assert result.taxable_income_rial >= 0
        assert result.tax_rial >= 0
        assert result.art137_deduction_rial >= 0


@SETTINGS
@given(gross=GROSSES, allowances=ALLOWANCES, days=MONTH_LENGTHS)
def test_p03_the_net_identity_holds_for_every_posture(
    gross: int, allowances: Allowances, days: int
) -> None:
    if gross < _welfare_total(allowances):
        return
    calculation = compute_gross_to_net(
        PayrollInput(
            gross_monthly_rial=gross,
            rule_year=1404,
            days_in_month=days,
            allowances=allowances,
        )
    )
    payload = calculation.payload
    total_gross = payload["bases"]["total_gross_rial"]
    employee_sso = payload["sso"]["employee_share_7pct_rial"]
    for posture in (POSTURE_CONSERVATIVE_INTA, POSTURE_COURT_PRECEDENT):
        tax = payload["tax_postures"][posture]["income_tax_rial"]
        assert total_gross - employee_sso - tax == payload["tax_postures"][posture]["net_rial"]
    assert total_gross - employee_sso - payload["employee_deductions"]["income_tax_rial"] == (
        payload["net_rial"]
    )


@SETTINGS
@given(gross=GROSSES, allowances=ALLOWANCES, days=MONTH_LENGTHS)
def test_the_employer_cost_identity_holds_for_every_input(
    gross: int, allowances: Allowances, days: int
) -> None:
    if gross < _welfare_total(allowances):
        return
    calculation = compute_gross_to_net(
        PayrollInput(
            gross_monthly_rial=gross,
            rule_year=1404,
            days_in_month=days,
            allowances=allowances,
        )
    )
    payload = calculation.payload
    assert payload["employer_cost"]["total_monthly_employer_cost_rial"] == (
        payload["bases"]["total_gross_rial"]
        + payload["sso"]["employer_share_20pct_rial"]
        + payload["sso"]["unemployment_fund_3pct_rial"]
        + payload["severance_sanavat"]["monthly_accrual_rial"]
        + payload["eydi"]["monthly_accrual_rial"]
    )


@SETTINGS
@given(gross=GROSSES, allowances=ALLOWANCES)
def test_p10_the_allowance_order_does_not_change_the_result(
    gross: int, allowances: Allowances
) -> None:
    if gross < _welfare_total(allowances):
        return
    reordered = Allowances(
        housing_rial=allowances.housing_rial,
        grocery_rial=allowances.grocery_rial,
        marriage_rial=allowances.marriage_rial,
        child_rial=allowances.child_rial,
        continuous_attraction_rial=allowances.continuous_attraction_rial,
    )
    first = compute_gross_to_net(PayrollInput(gross_monthly_rial=gross, allowances=allowances))
    second = compute_gross_to_net(PayrollInput(gross_monthly_rial=gross, allowances=reordered))
    assert first.calculation_hash == second.calculation_hash


@SETTINGS
@given(
    low=st.integers(min_value=1, max_value=2_000_000_000),
    high=st.integers(min_value=1, max_value=2_000_000_000),
)
def test_p02_the_net_is_monotonically_non_decreasing_in_the_gross(
    low: int, high: int
) -> None:
    first_gross = min(low, high)
    second_gross = max(low, high)
    first = compute_gross_to_net(PayrollInput(gross_monthly_rial=first_gross)).payload["net_rial"]
    second = compute_gross_to_net(PayrollInput(gross_monthly_rial=second_gross)).payload["net_rial"]
    assert second >= first


@SETTINGS
@given(gross=GROSSES, hours=st.integers(min_value=0, max_value=200))
def test_the_overtime_premium_is_never_negative(gross: int, hours: int) -> None:
    result = compute_overtime_premiums(gross, hours, hours, RULE_SET, 30)
    assert result.overtime_pay_rial >= 0
    assert result.night_pay_rial >= 0
    assert result.premium_total_rial == (
        result.overtime_pay_rial + result.night_pay_rial
    )


@SETTINGS
@given(gross=GROSSES, allowances=ALLOWANCES)
def test_the_decomposition_never_produces_a_negative_base(
    gross: int, allowances: Allowances
) -> None:
    welfare = (
        allowances.housing_rial
        + allowances.grocery_rial
        + allowances.marriage_rial
        + allowances.child_rial
    )
    if gross < welfare:
        return
    result = decompose_bases(gross, allowances)
    assert result.mozd_e_saabet_rial >= 0
    assert result.welfare_total_rial >= 0
    assert result.gross_monthly_rial - result.welfare_total_rial == (
        result.mozd_e_saabet_rial
    )
