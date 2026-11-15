"""Social Security Organization contributions (employee and employer).

Authority
---------
``docs/PISH_HESABDARI_HOLY_BIBLE.md`` §2.3 A; Social Security Law Arts. 28
and 39; Unemployment Insurance Act; SSO circular S4 item 13;
``REMEDIATED_TECHNICAL_SPECIFICATION_V2.md`` Module 1.
Related:
    WBS P1-T06 — SSO engine.

Contract notes
--------------
* Employee share 7 %, employer share 20 %, unemployment insurance 3 %
  (employer-paid) — all loaded from the rule set, never hard-coded.
* The insurable wage is ``min(earnings, ceiling)`` where the ceiling is
  ``7 x daily minimum wage x days_in_month`` (29/30/31 variants).
* ``ceiling_applied`` is always emitted as an explicit boolean
  (iranian-payroll-engineering rule 4).
* Each emitted line is rounded exactly once, from its exact Decimal value.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, localcontext

from app.engines.money import MONEY_PRECISION, round_half_up
from app.engines.rules import StatutoryRuleSet

__all__ = ("SsoResult", "compute_sso")


@dataclass(frozen=True, slots=True)
class SsoResult:
    """The month's SSO contributions with their exact and rounded values."""

    insurable_wage_rial: int
    ceiling_rial: int
    ceiling_applied: bool
    employee_share_exact: Decimal
    employee_share_rial: int
    employer_share_exact: Decimal
    employer_share_rial: int
    unemployment_share_exact: Decimal
    unemployment_share_rial: int


def compute_sso(
    total_earnings_rial: int,
    rule_set: StatutoryRuleSet,
    days_in_month: int,
) -> SsoResult:
    """Compute employee 7 % and employer 20 % + 3 % on the capped insurable wage.

    The employee share is also returned **unrounded** (``employee_share_exact``)
    because the Article 137 tax deduction is computed on the insurable wage,
    not on a rounded line (iranian-payroll-engineering rule 15).
    """
    if isinstance(total_earnings_rial, bool) or not isinstance(total_earnings_rial, int):
        raise TypeError("total_earnings_rial must be an int number of Rial")
    if total_earnings_rial < 0:
        raise ValueError(
            "PAYROLL_INPUT_INVALID: total_earnings_rial must be a non-negative int"
        )
    ceiling = rule_set.insurable_ceiling_rial(days_in_month)
    insurable = min(total_earnings_rial, ceiling)
    ceiling_applied = total_earnings_rial > ceiling

    with localcontext() as context:
        context.prec = MONEY_PRECISION
        context.rounding = ROUND_HALF_UP
        insurable_decimal = Decimal(insurable)
        employee_exact = insurable_decimal * rule_set.employee_sso_rate
        employer_exact = insurable_decimal * rule_set.employer_sso_rate
        unemployment_exact = insurable_decimal * rule_set.employer_unemployment_rate

    return SsoResult(
        insurable_wage_rial=insurable,
        ceiling_rial=ceiling,
        ceiling_applied=ceiling_applied,
        employee_share_exact=employee_exact,
        employee_share_rial=round_half_up(employee_exact, field="employee_sso_share"),
        employer_share_exact=employer_exact,
        employer_share_rial=round_half_up(employer_exact, field="employer_sso_share"),
        unemployment_share_exact=unemployment_exact,
        unemployment_share_rial=round_half_up(
            unemployment_exact, field="unemployment_share"
        ),
    )
