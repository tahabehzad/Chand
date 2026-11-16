"""Statutory floors, allowance minimums and the base-seniority reference.

Authority
---------
``docs/PISH_HESABDARI_HOLY_BIBLE.md`` §1.8 (the statutory floor is in
scope), §2.2 E4 (legally recognised base seniority), §2.3 J (child
allowance = 3 x daily minimum wage) and §2.5 (the minimum-wage hard floor);
``docs/EXECUTION_PLAN.md`` §7.2 rule 5 (the engine reads the rule set and
never hard-codes a statutory value).
Related:
    Remediation A-10 / B-10 — unused statutory parameters, allowance floors
    and the base-seniority increment.

Why a separate module?
----------------------
The gross-to-net path answers "what does this package cost?".  The statutory
floor answers a different question: "is this package allowed, and which
statutory entitlements does it omit?".  Mixing the two would silently change
net pay, which ADR-008 does not authorise.  This module therefore computes
the reference values from the verified seed and publishes them **without**
applying them to the monetary result, so a missing statutory calculation is
visible and testable rather than invisible.

Contract notes
--------------
* Every value is read from the verified 1404 rule set; nothing is hard-coded.
* The block is explicitly reference-only.  ``applied_to_net`` is always
  ``False`` and the reason is published.  The owner decision that would make
  the seniority increment part of the computed wage is ``DEC-013`` (proposed
  in ``docs/DECISIONS_REGISTER.md``).
* Eligibility gates that the corpus does not establish (the Art. 86 720-day
  threshold, DEC-011c) are **not** assumed here: the child floor is per
  eligible child and the caller supplies the declared amount, so no gate is
  invented.
* No float, no clock, no I/O: the module is a pure function of the rule set
  and its arguments.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.engines.errors import PayrollInputError
from app.engines.rules import StatutoryRuleSet

__all__ = (
    "PARAMETER_USAGE",
    "StatutoryReference",
    "build_statutory_reference",
)

#: How every statutory allowance parameter is used by the engine.
#:
#: ``consumed``          the calculation path reads it;
#: ``reference_only``    published as a floor/reference, not applied to net;
#: ``deliberately_unused`` the seed key is a known defect or an attendance
#:                        figure that must never enter a statutory base.
PARAMETER_USAGE: dict[str, str] = {
    "daily_minimum_wage_rial": "consumed",
    "monthly_minimum_wage_30days_rial": "consumed",
    "monthly_minimum_wage_31days_rial": "consumed",
    "monthly_housing_allowance_rial": "reference_only",
    "monthly_grocery_allowance_rial": "reference_only",
    "monthly_marriage_allowance_rial": "reference_only",
    "child_allowance_per_child_rial": "reference_only",
    "daily_seniority_base_rial": "reference_only",
    "monthly_seniority_base_30days_rial": "reference_only",
    "employee_sso_rate": "consumed",
    "employer_sso_rate": "consumed",
    "employer_unemployment_rate": "consumed",
    "max_daily_insurable_wage_rial": "consumed",
    "max_monthly_insurable_wage_30days_rial": "consumed",
    "standard_weekly_hours": "consumed",
    "overtime_monthly_divisor": "consumed",
    "standard_monthly_attendance_hours": "deliberately_unused",
    "overtime_multiplier": "consumed",
    "night_shift_multiplier": "consumed",
    "monthly_tax_exemption_rial": "consumed",
    "annual_tax_exemption_rial": "consumed",
    "tax_brackets": "consumed",
    "eydi_min_days": "consumed",
    "eydi_max_days_min_wage": "consumed",
    "max_annual_eydi_rial": "consumed",
    "eydi_tax_exemption_rial": "consumed",
    "eydi_tax_excess_rate": "deliberately_unused",
    "sanavat_monthly_accrual_rate": "deliberately_unused",
    "non_cash_benefit_annual_tax_exemption_rial": "consumed",
}

#: The reason the reference block is not part of the monetary result.
REFERENCE_ONLY_REASON = (
    "ADR-008 authorises the gross-to-net calculation only; allowance floors "
    "and the base-seniority increment are published for audit and are not "
    "applied to net until DEC-013 is approved"
)


@dataclass(frozen=True, slots=True)
class StatutoryReference:
    """The statutory floor and the omitted entitlements, read from the seed."""

    monthly_minimum_wage_rial: int
    daily_minimum_wage_rial: int
    housing_allowance_floor_rial: int
    grocery_allowance_floor_rial: int
    marriage_allowance_floor_rial: int
    child_allowance_per_child_rial: int
    allowance_floor_excluding_child_rial: int
    declared_child_allowance_rial: int
    declared_child_allowance_below_floor: bool
    total_gross_below_minimum_wage: bool
    daily_seniority_base_rial: int
    monthly_seniority_base_rial: int
    recognised_service_years: int
    monthly_seniority_increment_rial: int
    applied_to_net: bool
    reference_only_reason: str


def _require_non_negative_int(value: int, field: str) -> int:
    """Return *value* if it is a genuine non-negative ``int``."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise PayrollInputError(
            f"PAYROLL_INPUT_INVALID: {field} must be a non-negative int"
        )
    return value


def build_statutory_reference(
    rule_set: StatutoryRuleSet,
    *,
    days_in_month: int,
    total_gross_rial: int,
    declared_child_allowance_rial: int = 0,
    recognised_service_years: int = 0,
) -> StatutoryReference:
    """Build the statutory floor and the omitted-entitlement reference.

    The seniority increment is ``daily base seniority x days in month x
    years of legally recognised service`` (E4).  It is computed only when a
    recognised-service figure is supplied; it is never inferred from total
    experience or current-employer tenure (invariant 1).
    """
    gross = _require_non_negative_int(total_gross_rial, "total_gross_rial")
    child = _require_non_negative_int(
        declared_child_allowance_rial, "declared_child_allowance_rial"
    )
    years = _require_non_negative_int(
        recognised_service_years, "recognised_service_years"
    )
    minimum_monthly = rule_set.monthly_minimum_wage_rial(days_in_month)
    non_child_floor = (
        rule_set.monthly_housing_allowance_rial
        + rule_set.monthly_grocery_allowance_rial
        + rule_set.monthly_marriage_allowance_rial
    )
    per_child = rule_set.child_allowance_per_child_rial
    # A declared child allowance below one statutory child allowance is
    # under-paid; a zero declaration is *not* flagged, because the number of
    # eligible children is an input the corpus does not establish (DEC-011c)
    # and a zero could legitimately mean "no eligible child".
    child_below_floor = 0 < child < per_child
    seniority_increment = (
        rule_set.daily_seniority_base_rial * days_in_month * years
    )
    return StatutoryReference(
        monthly_minimum_wage_rial=minimum_monthly,
        daily_minimum_wage_rial=rule_set.daily_minimum_wage_rial,
        housing_allowance_floor_rial=rule_set.monthly_housing_allowance_rial,
        grocery_allowance_floor_rial=rule_set.monthly_grocery_allowance_rial,
        marriage_allowance_floor_rial=rule_set.monthly_marriage_allowance_rial,
        child_allowance_per_child_rial=per_child,
        allowance_floor_excluding_child_rial=non_child_floor,
        declared_child_allowance_rial=child,
        declared_child_allowance_below_floor=child_below_floor,
        total_gross_below_minimum_wage=gross < minimum_monthly,
        daily_seniority_base_rial=rule_set.daily_seniority_base_rial,
        monthly_seniority_base_rial=rule_set.monthly_seniority_base_30days_rial,
        recognised_service_years=years,
        monthly_seniority_increment_rial=seniority_increment,
        applied_to_net=False,
        reference_only_reason=REFERENCE_ONLY_REASON,
    )
