"""Prepare contractual payroll inputs for work schedules and recognised seniority.

Authority: ADR-012; WORK_PROFILE_PAYROLL; Labour Law Arts. 37, 39, 51.
Related: P1-T14; bases/rules/money engines.
Scope: pure Decimal preparation only; no IO, clock, key access or persistence.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation, localcontext

from app.engines.bases import Allowances, decompose_bases
from app.engines.errors import PayrollInputError, StatutoryParameterUnavailable
from app.engines.money import MONEY_PRECISION, round_half_up
from app.engines.rules import StatutoryRuleSet


@dataclass(frozen=True, slots=True)
class WorkSchedule:
    """Ordinary hours and distinct manager-declared statutory service history."""

    daily_hours: str
    period: str
    weekly_days: int | None = None
    monthly_paid_days: int | None = None
    recognised_seniority_months: int | None = None
    employer_tenure_months: int | None = None
    workshop_type: str = "unclassified"
    documented_daily_seniority_rial: int | None = None


@dataclass(frozen=True, slots=True)
class PreparedWorkPay:
    """Rounded component boundaries and exact work preparation provenance."""

    ratio: str
    gross_rial: int
    allowances: Allowances
    fixed_wage_rial: int
    seniority_rial: int
    seniority_daily_rial: int
    seniority_source: str
    rounding_residual_rial: int
    premium_base_rial: int


def _integer(value: int | None, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise PayrollInputError(f"WORK_PROFILE_INVALID: {field}")
    return value


def prepare_work_pay(  # noqa: PLR0912, PLR0915 — explicit fail-closed field checks and line boundaries
    full_time_gross_rial: int,
    allowances: Allowances,
    schedule: WorkSchedule,
    rule_set: StatutoryRuleSet,
    days_in_month: int,
) -> PreparedWorkPay:
    """Scale paid ordinary time and add seniority once before existing payroll."""
    base = decompose_bases(full_time_gross_rial, allowances)
    if base.mozd_e_saabet_rial < rule_set.monthly_minimum_wage_rial(days_in_month):
        raise PayrollInputError("WORK_BASE_BELOW_MINIMUM")
    months = _integer(schedule.recognised_seniority_months, "recognised_seniority_months")
    if schedule.employer_tenure_months is not None:
        _integer(schedule.employer_tenure_months, "employer_tenure_months")
    if schedule.workshop_type not in {"unclassified", "classified"}:
        raise PayrollInputError("WORKSHOP_TYPE_INVALID")
    if schedule.workshop_type == "unclassified" and months >= 12:
        tenure = _integer(schedule.employer_tenure_months, "employer_tenure_months")
        if months > tenure:
            raise PayrollInputError("SENIORITY_EXCEEDS_EMPLOYER_TENURE")
    declared = schedule.documented_daily_seniority_rial
    if declared is not None:
        _integer(declared, "documented_daily_seniority_rial")
    if months < 12:
        if declared not in (None, 0):
            raise PayrollInputError("SENIORITY_NOT_ELIGIBLE")
        seniority_daily, source = 0, "recognised_service_below_12_months"
    elif declared is not None:
        if declared < rule_set.daily_seniority_base_rial:
            raise PayrollInputError("SENIORITY_BELOW_CURRENT_INCREMENT")
        seniority_daily, source = declared, "manager_documented_daily_seniority"
    elif months >= 24 or schedule.workshop_type == "classified":
        raise StatutoryParameterUnavailable("DOCUMENTED_SENIORITY_RATE_REQUIRED")
    else:
        seniority_daily, source = rule_set.daily_seniority_base_rial, "current_first_eligible_year"

    if not isinstance(schedule.daily_hours, str):
        raise PayrollInputError("WORK_DAILY_HOURS_INVALID")
    try:
        hours = Decimal(schedule.daily_hours)
    except (InvalidOperation, ValueError):
        raise PayrollInputError("WORK_DAILY_HOURS_INVALID") from None
    if not hours.is_finite() or hours <= 0 or hours > 24:
        raise PayrollInputError("WORK_DAILY_HOURS_INVALID")

    with localcontext() as context:
        context.prec = MONEY_PRECISION
        context.rounding = ROUND_HALF_UP
        if schedule.period == "weekly":
            days = _integer(schedule.weekly_days, "weekly_days")
            if days < 1 or days > 7 or schedule.monthly_paid_days is not None:
                raise PayrollInputError("WORK_WEEKLY_SCHEDULE_INVALID")
            ratio = hours * days / rule_set.standard_weekly_hours
        elif schedule.period == "monthly":
            days = _integer(schedule.monthly_paid_days, "monthly_paid_days")
            if days < 1 or days > days_in_month or schedule.weekly_days is not None:
                raise PayrollInputError("WORK_MONTHLY_SCHEDULE_INVALID")
            ratio = hours * days / rule_set.overtime_divisor(days_in_month)
        else:
            raise PayrollInputError("WORK_SCHEDULE_PERIOD_INVALID")
        if ratio <= 0 or ratio > 1:
            raise PayrollInputError("WORK_ORDINARY_HOURS_EXCEED_FULL_TIME")
        exact = [
            Decimal(base.mozd_e_saabet_rial) * ratio,
            Decimal(allowances.housing_rial) * ratio,
            Decimal(allowances.grocery_rial) * ratio,
            Decimal(allowances.marriage_rial) * ratio,
            Decimal(allowances.child_rial) * ratio,
            Decimal(seniority_daily) * days_in_month * ratio,
        ]
        lines = [round_half_up(value) for value in exact]
        attraction = round_half_up(Decimal(allowances.continuous_attraction_rial) * ratio)
        residual = sum(lines) - round_half_up(sum(exact, Decimal(0)))
    return PreparedWorkPay(
        ratio=str(ratio),
        gross_rial=sum(lines),
        allowances=Allowances(
            housing_rial=lines[1], grocery_rial=lines[2], marriage_rial=lines[3],
            child_rial=lines[4], continuous_attraction_rial=attraction,
        ),
        fixed_wage_rial=lines[0], seniority_rial=lines[5],
        seniority_daily_rial=seniority_daily, seniority_source=source,
        rounding_residual_rial=residual,
        premium_base_rial=base.mozd_e_saabet_rial + seniority_daily * days_in_month,
    )
