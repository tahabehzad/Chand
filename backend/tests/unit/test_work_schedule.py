"""Independent numerical work/seniority vectors for ADR-012.

Authority: WORK_PROFILE_PAYROLL; Labour Law Arts. 39, 51.
Related: P1-T14, unchanged 1404 baseline and proportional Eydi cap.
Scope: pure deterministic calculation; no database or real personnel data.
"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

import pytest

from app.engines.bases import Allowances
from app.engines.errors import PayrollEngineError
from app.engines.eydi import compute_eydi
from app.engines.rules import load_rule_set
from app.engines.work_schedule import WorkSchedule, prepare_work_pay
from app.services.payroll_service import PayrollInput, compute_gross_to_net


def plan(**changes: object) -> WorkSchedule:
    return replace(WorkSchedule("4.4", "weekly", weekly_days=5, recognised_seniority_months=0,
                               employer_tenure_months=12),
                   **changes)  # type: ignore[arg-type]


def test_half_time_and_first_eligible_seniority_have_independent_exact_values() -> None:
    rules = load_rule_set(1404)
    no_service = prepare_work_pay(220_000_000, Allowances(), plan(), rules, 30)
    seniority = prepare_work_pay(220_000_000, Allowances(),
                                plan(recognised_seniority_months=12), rules, 30)
    assert no_service.ratio == "0.5"
    assert no_service.gross_rial == 110_000_000
    assert seniority.seniority_rial == 1_410_000
    assert seniority.gross_rial == 111_410_000
    assert seniority.premium_base_rial == 222_820_000


@pytest.mark.parametrize(("days", "seniority"), [(29, 1_363_000), (30, 1_410_000), (31, 1_457_000)])
def test_seniority_respects_month_length(days: int, seniority: int) -> None:
    result = prepare_work_pay(220_000_000, Allowances(), plan(recognised_seniority_months=12),
                              load_rule_set(1404), days)
    assert result.seniority_rial == seniority


def test_weekly_and_explicit_monthly_paid_day_vectors() -> None:
    rules = load_rule_set(1404)
    weekly = prepare_work_pay(220_000_000, Allowances(), plan(daily_hours="4"), rules, 30)
    monthly = prepare_work_pay(220_000_000, Allowances(), plan(
        daily_hours="4", period="monthly", weekly_days=None, monthly_paid_days=20), rules, 30)
    assert weekly.gross_rial == 100_000_000
    assert monthly.gross_rial == 80_000_000


def test_welfare_scales_once_and_seniority_stays_inside_fixed_wage() -> None:
    result = prepare_work_pay(260_000_000, Allowances(housing_rial=20_000_000,
        grocery_rial=20_000_000), plan(recognised_seniority_months=12), load_rule_set(1404), 30)
    assert result.allowances.housing_rial == 10_000_000
    assert result.allowances.grocery_rial == 10_000_000
    assert result.fixed_wage_rial == 110_000_000
    assert result.gross_rial == 131_410_000
    assert result.rounding_residual_rial == 0


@pytest.mark.parametrize("months", [24, 120])
def test_multiyear_seniority_requires_documented_rate(months: int) -> None:
    with pytest.raises(PayrollEngineError, match="DOCUMENTED_SENIORITY_RATE_REQUIRED"):
        prepare_work_pay(220_000_000, Allowances(), plan(recognised_seniority_months=months,
                         employer_tenure_months=months),
                         load_rule_set(1404), 30)


def test_documented_seniority_is_not_current_increment_times_years() -> None:
    result = prepare_work_pay(220_000_000, Allowances(), plan(
        recognised_seniority_months=120, employer_tenure_months=120,
        documented_daily_seniority_rial=200_000),
        load_rule_set(1404), 30)
    assert result.seniority_rial == 3_000_000
    assert result.seniority_source == "manager_documented_daily_seniority"


@pytest.mark.parametrize("changes", [
    {"recognised_seniority_months": None}, {"recognised_seniority_months": -1},
    {"daily_hours": "NaN"}, {"daily_hours": "0"}, {"daily_hours": "25"},
    {"daily_hours": True}, {"daily_hours": float("4.4")},
    {"daily_hours": "8", "weekly_days": 6}, {"weekly_days": True},
    {"monthly_paid_days": 20}, {"workshop_type": "classified", "recognised_seniority_months": 12},
])
def test_unknown_or_invalid_facts_fail_closed(changes: dict[str, object]) -> None:
    with pytest.raises(PayrollEngineError):
        prepare_work_pay(220_000_000, Allowances(), plan(**changes), load_rule_set(1404), 30)


def test_part_time_premiums_keep_full_time_hourly_rate_and_eydi_cap_scales() -> None:
    prepared = prepare_work_pay(220_000_000, Allowances(), plan(), load_rule_set(1404), 30)
    result = compute_gross_to_net(PayrollInput(
        gross_monthly_rial=prepared.gross_rial, employment_ratio=Decimal(prepared.ratio),
        premium_base_rial=prepared.premium_base_rial, overtime_hours=1, night_hours=1,
    )).payload
    assert result["bases"]["overtime_pay_rial"] == 1_400_000
    assert result["bases"]["night_shift_pay_rial"] == 350_000
    assert result["eydi"]["annual_gross_rial"] == 155_864_520
    assert result["net_rial"] == (
        result["bases"]["total_gross_rial"]
        - result["employee_deductions"]["employee_sso_7pct_rial"]
        - result["employee_deductions"]["income_tax_rial"]
    )


def test_fractional_line_residual_is_signed_and_bounded() -> None:
    result = prepare_work_pay(220_000_001, Allowances(housing_rial=1, grocery_rial=1),
                              plan(), load_rule_set(1404), 30)
    assert result.rounding_residual_rial == 1


@pytest.mark.parametrize("ratio", [Decimal(0), Decimal("NaN"), Decimal("1.1")])
def test_eydi_ratio_cannot_bypass_bounds(ratio: Decimal) -> None:
    with pytest.raises(PayrollEngineError):
        compute_eydi(220_000_000, load_rule_set(1404), employment_ratio=ratio)
