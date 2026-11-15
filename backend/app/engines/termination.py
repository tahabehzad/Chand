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
* The leave buyout caps the *annual* carryover at 9 days per year of
  service (Art. 66) but pays **all accumulated** unused days at exit
  (Art. 71), bounded by ``9 x years``.
* The exit severance is one month of *Mozd-e Saabet* per year of service,
  pro-rated by tenure months.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, localcontext

from app.engines.money import MONEY_PRECISION, round_half_up

__all__ = (
    "MAX_LEAVE_CARRYOVER_DAYS_PER_YEAR",
    "MAX_PROBATION_MONTHS",
    "TerminationResult",
    "compute_termination_liability",
)

#: Labour Law Art. 11 caps the probationary period at three months.
MAX_PROBATION_MONTHS: int = 3

#: Art. 66 caps the annual leave carryover at nine days.
MAX_LEAVE_CARRYOVER_DAYS_PER_YEAR: int = 9

_THIRTY = Decimal(30)
_TWELVE = Decimal(12)


@dataclass(frozen=True, slots=True)
class TerminationResult:
    """Probation, exit-severance and leave-buyout liability lines."""

    probation_months: int
    employer_initiated_probation_liability_rial: int
    employee_initiated_probation_liability_rial: int | None
    tenure_months: int
    exit_severance_exact: Decimal
    exit_severance_rial: int
    accumulated_unused_leave_days_input: int
    leave_carryover_cap_days: int
    effective_buyout_days: int
    daily_wage_exact: Decimal
    leave_buyout_rial: int
    total_separation_rial: int


def _require_non_negative_int(value: int, field: str) -> int:
    """Return *value* if it is a genuine non-negative ``int``."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"PAYROLL_INPUT_INVALID: {field} must be a non-negative int")
    return value


def compute_termination_liability(
    mozd_e_saabet_rial: int,
    gross_monthly_rial: int,
    *,
    days_in_month: int,
    probation_months: int,
    tenure_months: int,
    accumulated_unused_leave_days: int,
    probation_days_worked: int | None = None,
) -> TerminationResult:
    """Compute the termination and probation liability lines.

    ``probation_days_worked`` only affects the **employee-initiated**
    liability (days worked); the employer-initiated liability is always the
    full agreed probation period per Art. 11.
    """
    saabet = _require_non_negative_int(mozd_e_saabet_rial, "mozd_e_saabet_rial")
    gross = _require_non_negative_int(gross_monthly_rial, "gross_monthly_rial")
    _require_non_negative_int(days_in_month, "days_in_month")
    _require_non_negative_int(tenure_months, "tenure_months")
    unused = _require_non_negative_int(
        accumulated_unused_leave_days, "accumulated_unused_leave_days"
    )
    if isinstance(probation_months, bool) or not isinstance(probation_months, int):
        raise ValueError("PAYROLL_INPUT_INVALID: probation_months must be an int")
    if probation_months < 1:
        raise ValueError(
            "PAYROLL_INPUT_INVALID: probation_months must be at least one month"
        )
    if probation_months > MAX_PROBATION_MONTHS:
        raise ValueError(
            "PROBATION_BEYOND_STATUTORY_MAX: probation_months exceeds the "
            "statutory maximum"
        )
    days_worked: int | None = None
    if probation_days_worked is not None:
        days_worked = _require_non_negative_int(
            probation_days_worked, "probation_days_worked"
        )

    employer_liability = gross * probation_months
    employee_liability: int | None = None
    if days_worked is not None:
        employee_liability = round_half_up(
            Decimal(gross) * Decimal(days_worked) / Decimal(days_in_month),
            field="employee_initiated_probation_liability",
        )

    with localcontext() as context:
        context.prec = MONEY_PRECISION
        context.rounding = ROUND_HALF_UP
        years = Decimal(tenure_months) / _TWELVE
        exit_severance_exact = Decimal(saabet) * years
        daily_wage = Decimal(saabet) / _THIRTY
        carryover_cap = Decimal(MAX_LEAVE_CARRYOVER_DAYS_PER_YEAR) * years

    exit_severance_rial = round_half_up(exit_severance_exact, field="exit_severance")
    cap_days_exact = carryover_cap.to_integral_value(rounding=ROUND_HALF_UP)
    cap_days = int(cap_days_exact)
    effective_days = min(unused, cap_days)
    buyout_rial = round_half_up(
        Decimal(effective_days) * daily_wage, field="leave_buyout"
    )
    total_separation = exit_severance_rial + buyout_rial
    return TerminationResult(
        probation_months=probation_months,
        employer_initiated_probation_liability_rial=employer_liability,
        employee_initiated_probation_liability_rial=employee_liability,
        tenure_months=tenure_months,
        exit_severance_exact=exit_severance_exact,
        exit_severance_rial=exit_severance_rial,
        accumulated_unused_leave_days_input=unused,
        leave_carryover_cap_days=cap_days,
        effective_buyout_days=effective_days,
        daily_wage_exact=daily_wage,
        leave_buyout_rial=buyout_rial,
        total_separation_rial=total_separation,
    )
