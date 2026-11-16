"""Termination and probation liability, including the Article 11 worst case.

Authority
---------
``docs/PISH_HESABDARI_HOLY_BIBLE.md`` §2.3 H/I; Labour Law Arts. 11, 24, 66
and 71; ``FIND-LEG-01`` (probation), ``FIND-LEG-06`` (leave buyout).
Related:
    WBS P1-T12 — termination-liability simulator.

Contract notes
--------------
* **Article 11 (``FIND-LEG-01``, CRITICAL):** if the **employer** terminates
  during the agreed probationary period, the liability is the salary for the
  **entire agreed probation period** — not the days worked.  Only an
  employee-initiated termination is limited to the days worked.  The worst
  case is never truncated.
* **Mutually exclusive scenarios (remediation A-4).**  A termination is
  either a probation termination (employer- or employee-initiated) or an
  ordinary termination.  The engine now requires the scenario and publishes
  exactly one probation line; ``total_liability_rial`` is the sum of the
  published component lines and therefore reconciles by construction.  A
  probation liability is never silently added to an exit settlement.
* The leave buyout caps the *annual* carryover at 9 days per year of
  service (Art. 66) but pays **all accumulated** unused days at exit
  (Art. 71), bounded by ``9 x years``.
* The exit severance is one month of *Mozd-e Saabet* per year of service,
  pro-rated by tenure months.
* **Daily wage (remediation A-3 / B-7).**  The corpus states
  ``EXIT_buyout = min(9 x years, accumulated) x final_daily_wage`` without a
  divisor.  The only daily/monthly convention the verified seed states is
  ``monthly = daily x 30`` (its 29/30/31-day minimum-wage and seniority
  structures, invariants R-01/R-07/R-10).  The engine therefore uses the
  documented 30-day divisor, exposed as
  :data:`STATUTORY_DAILY_WAGE_DIVISOR_DAYS`, instead of an unexplained
  literal.  Whether the welfare allowances belong in the leave-pay base is
  *not* established by the corpus; the engine keeps the *Mozd-e Saabet* base
  that Art. 24/36 Note 3 already define, and the question is recorded as
  ``B-7`` in ``docs/DECISIONS_REGISTER.md`` for a Labour Counsel ruling.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, localcontext
from typing import Literal, cast

from app.engines.errors import PayrollInputError, ProbationBeyondStatutoryMax
from app.engines.money import MONEY_PRECISION, round_half_up

__all__ = (
    "MAX_LEAVE_CARRYOVER_DAYS_PER_YEAR",
    "MAX_PROBATION_MONTHS",
    "STATUTORY_DAILY_WAGE_DIVISOR_DAYS",
    "TerminationResult",
    "TerminationScenario",
    "compute_termination_liability",
)

#: Labour Law Art. 11 caps the probationary period at three months.
MAX_PROBATION_MONTHS: int = 3

#: Art. 66 caps the annual leave carryover at nine days.
MAX_LEAVE_CARRYOVER_DAYS_PER_YEAR: int = 9

#: The documented 30-day monthly/daily convention of the verified seed.
STATUTORY_DAILY_WAGE_DIVISOR_DAYS: int = 30

TerminationScenario = Literal[
    "probation_employer_initiated",
    "probation_employee_initiated",
    "ordinary_termination",
]

_SCENARIOS: frozenset[str] = frozenset(
    {
        "probation_employer_initiated",
        "probation_employee_initiated",
        "ordinary_termination",
    }
)

_THIRTY = Decimal(30)
_TWELVE = Decimal(12)


@dataclass(frozen=True, slots=True)
class TerminationResult:
    """Probation, exit-severance and leave-buyout liability lines.

    Exactly one probation line is *applied*, selected by
    ``termination_scenario``; the other is either absent (``None``) or
    published for reference and excluded from the total.
    """

    termination_scenario: TerminationScenario
    probation_months: int | None
    employer_initiated_probation_liability_rial: int
    employee_initiated_probation_liability_rial: int | None
    applied_probation_liability_rial: int
    probation_base: str
    tenure_months: int
    exit_severance_exact: Decimal
    exit_severance_rial: int
    accumulated_unused_leave_days_input: int
    leave_carryover_cap_days: int
    effective_buyout_days: int
    daily_wage_divisor_days: int
    daily_wage_exact: Decimal
    leave_buyout_rial: int
    total_separation_rial: int
    total_liability_rial: int


def _require_non_negative_int(value: int, field: str) -> int:
    """Return *value* if it is a genuine non-negative ``int``."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise PayrollInputError(
            f"PAYROLL_INPUT_INVALID: {field} must be a non-negative int"
        )
    return value


def _resolve_scenario(
    scenario: str | None,
    probation_months: int | None,
    probation_days_worked: int | None,
) -> TerminationScenario:
    """Return the explicit scenario, or derive the worst-case one.

    With no explicit scenario the historical contract is preserved: a
    probation input *without* days worked is the employer-initiated worst
    case (Art. 11); with days worked it is the employee-initiated case; no
    probation input at all is an ordinary termination.
    """
    if scenario is None:
        if probation_months is None:
            return "ordinary_termination"
        if probation_days_worked is None:
            return "probation_employer_initiated"
        return "probation_employee_initiated"
    if scenario not in _SCENARIOS:
        raise PayrollInputError(
            "PAYROLL_INPUT_INVALID: termination_scenario must be one of "
            + ", ".join(sorted(_SCENARIOS))
        )
    return cast(TerminationScenario, scenario)


def compute_termination_liability(
    mozd_e_saabet_rial: int,
    gross_monthly_rial: int,
    *,
    days_in_month: int,
    probation_months: int | None = None,
    tenure_months: int,
    accumulated_unused_leave_days: int,
    probation_days_worked: int | None = None,
    termination_scenario: str | None = None,
) -> TerminationResult:
    """Compute the termination lines for exactly one termination scenario.

    ``probation_days_worked`` only affects the **employee-initiated**
    liability (days worked); the employer-initiated liability is always the
    full agreed probation period per Art. 11.

    ``total_liability_rial`` is the sum of the applied probation line, the
    exit severance and the leave buyout — the three published components —
    so a reader can always reconcile the total from the response.
    """
    saabet = _require_non_negative_int(mozd_e_saabet_rial, "mozd_e_saabet_rial")
    gross = _require_non_negative_int(gross_monthly_rial, "gross_monthly_rial")
    _require_non_negative_int(days_in_month, "days_in_month")
    _require_non_negative_int(tenure_months, "tenure_months")
    unused = _require_non_negative_int(
        accumulated_unused_leave_days, "accumulated_unused_leave_days"
    )
    if probation_months is not None:
        if isinstance(probation_months, bool) or not isinstance(probation_months, int):
            raise PayrollInputError(
                "PAYROLL_INPUT_INVALID: probation_months must be an int"
            )
        if probation_months < 1:
            raise PayrollInputError(
                "PAYROLL_INPUT_INVALID: probation_months must be at least one month"
            )
        if probation_months > MAX_PROBATION_MONTHS:
            raise ProbationBeyondStatutoryMax(
                "PROBATION_BEYOND_STATUTORY_MAX: probation_months exceeds the "
                "statutory maximum"
            )
    days_worked: int | None = None
    if probation_days_worked is not None:
        days_worked = _require_non_negative_int(
            probation_days_worked, "probation_days_worked"
        )

    scenario = _resolve_scenario(
        termination_scenario, probation_months, probation_days_worked
    )
    if scenario == "ordinary_termination" and probation_months is not None:
        raise PayrollInputError(
            "PAYROLL_INPUT_INVALID: an ordinary termination cannot carry a "
            "probation liability"
        )
    if scenario != "ordinary_termination" and probation_months is None:
        raise PayrollInputError(
            "PAYROLL_INPUT_INVALID: a probation scenario requires probation_months"
        )
    if scenario == "probation_employee_initiated" and days_worked is None:
        raise PayrollInputError(
            "PAYROLL_INPUT_INVALID: an employee-initiated probation termination "
            "requires probation_days_worked"
        )

    employer_liability = 0 if probation_months is None else gross * probation_months
    employee_liability: int | None = None
    if days_worked is not None and probation_months is not None:
        employee_liability = round_half_up(
            Decimal(gross) * Decimal(days_worked) / Decimal(days_in_month),
            field="employee_initiated_probation_liability",
        )

    applied_probation = 0
    if scenario == "probation_employer_initiated":
        applied_probation = employer_liability
    elif scenario == "probation_employee_initiated":
        applied_probation = employee_liability or 0

    with localcontext() as context:
        context.prec = MONEY_PRECISION
        context.rounding = ROUND_HALF_UP
        years = Decimal(tenure_months) / _TWELVE
        exit_severance_exact = Decimal(saabet) * years
        daily_wage = Decimal(saabet) / Decimal(STATUTORY_DAILY_WAGE_DIVISOR_DAYS)
        carryover_cap = Decimal(MAX_LEAVE_CARRYOVER_DAYS_PER_YEAR) * years

    exit_severance_rial = round_half_up(exit_severance_exact, field="exit_severance")
    cap_days = int(carryover_cap.to_integral_value(rounding=ROUND_HALF_UP))
    effective_days = min(unused, cap_days)
    buyout_rial = round_half_up(
        Decimal(effective_days) * daily_wage, field="leave_buyout"
    )
    total_separation = exit_severance_rial + buyout_rial
    total_liability = applied_probation + total_separation
    return TerminationResult(
        termination_scenario=scenario,
        probation_months=probation_months,
        employer_initiated_probation_liability_rial=employer_liability,
        employee_initiated_probation_liability_rial=employee_liability,
        applied_probation_liability_rial=applied_probation,
        probation_base="contractual_gross_monthly_rial",
        tenure_months=tenure_months,
        exit_severance_exact=exit_severance_exact,
        exit_severance_rial=exit_severance_rial,
        accumulated_unused_leave_days_input=unused,
        leave_carryover_cap_days=cap_days,
        effective_buyout_days=effective_days,
        daily_wage_divisor_days=STATUTORY_DAILY_WAGE_DIVISOR_DAYS,
        daily_wage_exact=daily_wage,
        leave_buyout_rial=buyout_rial,
        total_separation_rial=total_separation,
        total_liability_rial=total_liability,
    )
