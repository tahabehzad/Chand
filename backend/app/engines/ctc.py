"""Employer Total Cost to Employer (monthly and 12-month annual).

Authority
---------
``docs/PISH_HESABDARI_HOLY_BIBLE.md`` §2.3 H note and §1.2 pillar 3;
``REMEDIATED_TECHNICAL_SPECIFICATION_V2.md`` Module 6; ``FIND-MATH-02``.
Related:
    WBS P1-T11 — CTC engine.

Contract notes
--------------
* The employer-cost identity is exact and integer::

      total_monthly_employer_cost_rial =
          total gross
          + employer SSO (20 %, capped)
          + unemployment insurance (3 %, capped)
          + monthly severance accrual
          + monthly bonus accrual

* The 26 statutory paid-leave days are **never** accrued as an extra cash
  reserve — they are already-paid working days inside the 12 months of
  salary (``FIND-MATH-02``).  A carryover liability is a termination-side
  input (:mod:`app.engines.termination`), never a standing accrual.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.engines.errors import PayrollInputError

__all__ = ("EmployerCostResult", "compute_employer_cost")


@dataclass(frozen=True, slots=True)
class EmployerCostResult:
    """The employer's monthly and annual cost, exact by integer identity."""

    total_gross_rial: int
    employer_sso_rial: int
    unemployment_rial: int
    severance_accrual_rial: int
    eydi_accrual_rial: int
    total_monthly_rial: int
    annual_ctc_rial: int


def compute_employer_cost(
    total_gross_rial: int,
    employer_sso_rial: int,
    unemployment_rial: int,
    severance_accrual_rial: int,
    eydi_accrual_rial: int,
) -> EmployerCostResult:
    """Assemble the employer-cost identity from already-rounded line items.

    Every input must be a whole-Rial ``int`` line item that was rounded once
    upstream; the identity is then exact by integer addition, and the
    surfaced residual is structurally zero.
    """
    fields = (
        ("total_gross_rial", total_gross_rial),
        ("employer_sso_rial", employer_sso_rial),
        ("unemployment_rial", unemployment_rial),
        ("severance_accrual_rial", severance_accrual_rial),
        ("eydi_accrual_rial", eydi_accrual_rial),
    )
    for name, value in fields:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise PayrollInputError(
                f"PAYROLL_INPUT_INVALID: {name} must be a non-negative int"
            )
    monthly = total_gross_rial + employer_sso_rial + unemployment_rial + (
        severance_accrual_rial + eydi_accrual_rial
    )
    return EmployerCostResult(
        total_gross_rial=total_gross_rial,
        employer_sso_rial=employer_sso_rial,
        unemployment_rial=unemployment_rial,
        severance_accrual_rial=severance_accrual_rial,
        eydi_accrual_rial=eydi_accrual_rial,
        total_monthly_rial=monthly,
        annual_ctc_rial=monthly * 12,
    )
