"""Annual bonus (*Eydi*) accrual and its progressive payout taxation.

Authority
---------
``docs/PISH_HESABDARI_HOLY_BIBLE.md`` §2.3 F; the 1370 Eydi Payment Act;
Direct Taxation Act Art. 91(10); ``FIND-LEG-04`` (the excess is taxed
**progressively** — a flat 10 % is a legal fallacy).
Decisions:
    ADR-008 — the accrual follows the corpus property P-06,
    ``min(2 x Mozd-e Saabet, 3 x monthly minimum wage)``; the seed's
    ``eydi_tax_excess_rate: 0.10`` is never consumed (HB-GAP-005).
Related:
    WBS P1-T09 — Eydi engine.

Contract notes
--------------
* The floor (60 x daily wage) and the cap (90 x daily minimum wage) collapse
  into ``min(2 x Mozd-e Saabet, max_annual_eydi_rial)`` for a 30-day month;
  ``max_annual_eydi_rial`` is the seed's verified cap (3 x monthly minimum).
* The payout tax applies the **annual** exemption recorded in the seed
  (1/12 of the annual Art. 84 exemption) and taxes the excess across the
  progressive slabs - reusing the slab machinery from :mod:`app.engines.tax`.
  The ladder is shifted by the same exemption, so the excess is taxed as
  income immediately above the exemption edge; the seed's flat
  ``eydi_tax_excess_rate`` is never consumed (HB-GAP-005).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, localcontext

from app.engines.money import MONEY_PRECISION, round_half_up
from app.engines.rules import StatutoryRuleSet, shift_brackets_by
from app.engines.tax import TaxBracket, compute_progressive_tax

__all__ = ("EydiResult", "compute_eydi")

_TWO = Decimal(2)
_TWELVE = Decimal(12)


@dataclass(frozen=True, slots=True)
class EydiResult:
    """The annual *Eydi* and its monthly accrual with payout taxation."""

    annual_gross_exact: Decimal
    annual_gross_rial: int
    at_cap: bool
    monthly_accrual_rial: int
    annual_tax_rial: int
    annual_net_rial: int


def compute_eydi(
    mozd_e_saabet_rial: int,
    rule_set: StatutoryRuleSet,
    brackets: tuple[TaxBracket, ...] | None = None,
) -> EydiResult:
    """Compute the annual *Eydi*, the monthly accrual and the payout tax.

    ``brackets`` defaults to the rule set's own salary slabs; the excess
    over the annual exemption is taxed across those same progressive bands.
    """
    if isinstance(mozd_e_saabet_rial, bool) or not isinstance(mozd_e_saabet_rial, int):
        raise TypeError("mozd_e_saabet_rial must be an int number of Rial")
    if mozd_e_saabet_rial < 0:
        raise ValueError(
            "PAYROLL_INPUT_INVALID: mozd_e_saabet_rial must be a non-negative int"
        )
    active_brackets = rule_set.tax_brackets if brackets is None else brackets

    with localcontext() as context:
        context.prec = MONEY_PRECISION
        context.rounding = ROUND_HALF_UP
        saabet = Decimal(mozd_e_saabet_rial)
        floor_bound = saabet * _TWO
        cap = Decimal(rule_set.max_annual_eydi_rial)
        annual_exact = min(floor_bound, cap)
        monthly_exact = annual_exact / _TWELVE

    annual_rial = round_half_up(annual_exact, field="eydi_annual")
    at_cap = floor_bound > cap
    monthly_rial = round_half_up(monthly_exact, field="eydi_monthly_accrual")

    exempt = Decimal(rule_set.eydi_tax_exemption_rial)
    excess = annual_exact - exempt
    if excess < 0:
        excess = Decimal(0)
    ladder = shift_brackets_by(active_brackets, rule_set.eydi_tax_exemption_rial)
    tax_exact, _labels, _breakdown = compute_progressive_tax(excess, ladder)
    tax_rial = round_half_up(tax_exact, field="eydi_tax")
    return EydiResult(
        annual_gross_exact=annual_exact,
        annual_gross_rial=annual_rial,
        at_cap=at_cap,
        monthly_accrual_rial=monthly_rial,
        annual_tax_rial=tax_rial,
        annual_net_rial=annual_rial - tax_rial,
    )
