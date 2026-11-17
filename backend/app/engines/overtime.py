"""Overtime and night-shift premiums on the *Mozd-e Saabet* base.

Authority
---------
``docs/PISH_HESABDARI_HOLY_BIBLE.md`` §2.3 G; Labour Law Arts. 36 Note 3,
51, 58 and 59; ADR-011; ``FIND-LEG-03``.
Related:
    WBS P1-T10 — overtime engine.

Contract notes
--------------
* The premium base is *Mozd-e Saabet* only: the welfare allowances are
  excluded from the hourly rate **and** from the divisor (they are already
  excluded from *Mozd-e Saabet* by :mod:`app.engines.bases`).
* The monthly divisor is ``44 x days_in_month / 6`` paid calendar hours —
  220.00 for a 30-day month, 227.3̅ for 31 days, derived from the rule
  set's weekly hours.  The 176-hour attendance figure is never used.
* The loaded night factor 1.35 includes ordinary wages already in gross;
  only its additional component (factor minus one) is added (ADR-011).
* Each premium line is rounded exactly once.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, localcontext

from app.engines.errors import PayrollInputError
from app.engines.money import MONEY_PRECISION, round_half_up
from app.engines.rules import StatutoryRuleSet

__all__ = ("OvertimeResult", "compute_overtime_premiums")


@dataclass(frozen=True, slots=True)
class OvertimeResult:
    """The month's overtime and night-shift premium lines."""

    divisor: Decimal
    hourly_rate_exact: Decimal
    overtime_pay_exact: Decimal
    overtime_pay_rial: int
    night_pay_exact: Decimal
    night_pay_rial: int
    premium_total_rial: int


def _require_non_negative_int(value: int, field: str) -> int:
    """Return *value* if it is a genuine non-negative ``int``."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise PayrollInputError(
            f"PAYROLL_INPUT_INVALID: {field} must be a non-negative int"
        )
    return value


def compute_overtime_premiums(
    mozd_e_saabet_rial: int,
    overtime_hours: int,
    night_hours: int,
    rule_set: StatutoryRuleSet,
    days_in_month: int,
) -> OvertimeResult:
    """Compute the overtime (x multiplier) and night-shift premium lines.

    Ordinary non-shift night-hour wages are already inside contractual gross.
    Article 58 adds only the supplement; overtime remains a separate 1.40
    payment for additional hours (Article 59).
    """
    saabet = _require_non_negative_int(mozd_e_saabet_rial, "mozd_e_saabet_rial")
    overtime = _require_non_negative_int(overtime_hours, "overtime_hours")
    night = _require_non_negative_int(night_hours, "night_hours")

    divisor = rule_set.overtime_divisor(days_in_month)
    with localcontext() as context:
        context.prec = MONEY_PRECISION
        context.rounding = ROUND_HALF_UP
        hourly = Decimal(saabet) / divisor
        overtime_exact = hourly * overtime * rule_set.overtime_multiplier
        night_supplement = rule_set.night_shift_multiplier - Decimal(1)
        if night_supplement < Decimal(0):
            raise PayrollInputError("PAYROLL_INPUT_INVALID: night total factor is below one")
        night_exact = hourly * night * night_supplement

    overtime_rial = round_half_up(overtime_exact, field="overtime_pay")
    night_rial = round_half_up(night_exact, field="night_pay")
    return OvertimeResult(
        divisor=divisor,
        hourly_rate_exact=hourly,
        overtime_pay_exact=overtime_exact,
        overtime_pay_rial=overtime_rial,
        night_pay_exact=night_exact,
        night_pay_rial=night_rial,
        premium_total_rial=overtime_rial + night_rial,
    )
