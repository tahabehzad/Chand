"""Severance (*Sanavat*) accrual on the *Mozd-e Saabet* base.

Authority
---------
``docs/PISH_HESABDARI_HOLY_BIBLE.md`` §2.3 E; Labour Law Art. 24;
``FIND-LEG-05`` (base includes the continuous attraction allowance,
Diwan Precedent 3328).
Related:
    WBS P1-T08 — Sanavat engine.

Contract notes
--------------
* The monthly accrual is computed as the exact division
  ``Mozd-e Saabet ÷ 12`` and rounded once.  The seed's
  ``sanavat_monthly_accrual_rate: 0.0833333333`` literal is **never**
  consumed (HB-GAP-017) — the loader does not even expose it.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, localcontext

from app.engines.money import MONEY_PRECISION, round_half_up

__all__ = ("SeveranceAccrual", "compute_monthly_severance_accrual")

_TWELVE = Decimal(12)


@dataclass(frozen=True, slots=True)
class SeveranceAccrual:
    """One month's severance accrual, exact and rounded."""

    monthly_accrual_exact: Decimal
    monthly_accrual_rial: int


def compute_monthly_severance_accrual(mozd_e_saabet_rial: int) -> SeveranceAccrual:
    """Return ``Mozd-e Saabet ÷ 12`` rounded once to whole Rial."""
    if isinstance(mozd_e_saabet_rial, bool) or not isinstance(mozd_e_saabet_rial, int):
        raise TypeError("mozd_e_saabet_rial must be an int number of Rial")
    with localcontext() as context:
        context.prec = MONEY_PRECISION
        context.rounding = ROUND_HALF_UP
        exact = Decimal(mozd_e_saabet_rial) / _TWELVE
    return SeveranceAccrual(
        monthly_accrual_exact=exact,
        monthly_accrual_rial=round_half_up(exact, field="sanavat_accrual"),
    )
