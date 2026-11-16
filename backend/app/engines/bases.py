"""Decomposition of gross earnings into the statutory wage bases.

Authority
---------
``docs/PISH_HESABDARI_HOLY_BIBLE.md`` §2.3 D (*Mozd-e Mabna* / *Mozd-e
Saabet* decomposition — the rule most often got wrong) and §2.5;
Labour Law Art. 36 Note 3; Diwan-e Edalat-e Edali En Banc Judgment 3328.
Related:
    WBS P1-T07 — base decomposition.

Contract notes
--------------
* Welfare allowances (حق مسکن، بن خواربار، حق تاهل، حق اولاد) are excluded
  from *Mozd-e Saabet* by Art. 36 Note 3.  The continuous fixed attraction
  allowance (*فوق‌العاده جذب*) **remains inside** *Mozd-e Saabet*
  (``FIND-LEG-05``, Judgment 3328).
* The SSO insurable wage is handled separately in :mod:`app.engines.sso`
  (``min(earnings, ceiling)``); this module owns the *Saabet* split only.
* A gross that does not cover the welfare allowances is an input contract
  violation and fails closed — it is never clamped.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.engines.errors import BaseDecompositionNegative, PayrollInputError

__all__ = ("Allowances", "MozdDecomposition", "decompose_bases")


@dataclass(frozen=True, slots=True)
class Allowances:
    """Monthly fixed allowances, in whole Rial.

    ``child_rial`` is the *total* child allowance actually paid this month
    (already multiplied by the eligible-children count by the caller); the
    Art. 86 eligibility gate is an input-level concern (DEC-011c stays open).
    """

    housing_rial: int = 0
    grocery_rial: int = 0
    marriage_rial: int = 0
    child_rial: int = 0
    continuous_attraction_rial: int = 0

    @property
    def welfare_total_rial(self) -> int:
        """Return the Art. 36 Note 3 welfare total excluded from the base."""
        return (
            self.housing_rial
            + self.grocery_rial
            + self.marriage_rial
            + self.child_rial
        )


@dataclass(frozen=True, slots=True)
class MozdDecomposition:
    """The decomposed bases for one month, in whole Rial."""

    gross_monthly_rial: int
    welfare_total_rial: int
    mozd_e_saabet_rial: int


def _require_non_negative_int(value: int, field: str) -> int:
    """Return *value* if it is a genuine non-negative ``int``."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise PayrollInputError(f"PAYROLL_INPUT_INVALID: {field} must be a non-negative int")
    return value


def decompose_bases(gross_monthly_rial: int, allowances: Allowances) -> MozdDecomposition:
    """Split *gross_monthly_rial* into the welfare total and *Mozd-e Saabet*.

    Formula (Holy Bible §2.3 D)::

        Mozd_e_Saabet = Gross - housing - grocery - marriage - child
                      = Gross - welfare allowances   (attraction RETAINED)

    Raises:
        PayrollInputError: The inputs are not non-negative ints, or the
            gross does not cover the welfare allowances (a negative base is
            never clamped or coerced).
    """
    gross = _require_non_negative_int(gross_monthly_rial, "gross_monthly_rial")
    for value, field in (
        (allowances.housing_rial, "housing_rial"),
        (allowances.grocery_rial, "grocery_rial"),
        (allowances.marriage_rial, "marriage_rial"),
        (allowances.child_rial, "child_rial"),
        (allowances.continuous_attraction_rial, "continuous_attraction_rial"),
    ):
        _require_non_negative_int(value, field)
    welfare_excluded = (
        allowances.housing_rial
        + allowances.grocery_rial
        + allowances.marriage_rial
        + allowances.child_rial
    )
    mozd_e_saabet = gross - welfare_excluded
    if mozd_e_saabet < 0:
        raise BaseDecompositionNegative(
            "BASE_DECOMPOSITION_NEGATIVE: gross does not cover the welfare allowances"
        )
    return MozdDecomposition(
        gross_monthly_rial=gross,
        welfare_total_rial=welfare_excluded,
        mozd_e_saabet_rial=mozd_e_saabet,
    )
