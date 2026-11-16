"""Progressive salary income tax with the Article 137 dual-posture toggle.

Authority
---------
``docs/PISH_HESABDARI_HOLY_BIBLE.md`` §2.3 B/C and §2.5; Direct Taxation Act
Arts. 82-92 and 137 with Note 2 of Art. 83; INTA Circular 200/98/44;
Diwan-e Edalat-e Edari Precedents 1956 and 3328; ``FIND-LEG-02``.
Decision:
    ADR-008 (owner, 2026-11-15) resolves DEC-002a — the welfare allowances
    are **taxable under ``conservative_inta``** and **exempt under
    ``court_precedent``**; both postures are always computed side by side and
    ``conservative_inta`` is the primary response posture.
Related:
    WBS P1-T05 — tax engine.

Contract notes
--------------
* The Article 137 deduction is computed on the **insurable** wage (the
  actual employee SSO share, capped), never on raw gross
  (iranian-payroll-engineering rule 15).
* The deduction is never described as a "tax cap"; the two postures are two
  readings of the deduction, both emitted with their labels.
* Tax = progressive slabs applied to ``taxable - monthly exemption``.  The
  seed states the ladder in absolute taxable Rial and its first slab *is* the
  exemption, so the ladder is matched against a base that has already had the
  exemption removed **and** a ladder that has moved down by the same amount
  (:meth:`StatutoryRuleSet.brackets_above`).  Applying the absolute ladder to
  the reduced base would offset every band by one whole exemption and tax the
  excess at the wrong rate.
* Tax is rounded exactly once, from the exact Decimal value.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, localcontext
from typing import Literal

from app.engines.errors import PayrollInputError, TaxableBaseNegative
from app.engines.money import MONEY_PRECISION, round_half_up
from app.engines.rules import StatutoryRuleSet, TaxBracket

__all__ = (
    "POSTURE_CONSERVATIVE_INTA",
    "POSTURE_COURT_PRECEDENT",
    "TaxBracket",
    "TaxPosture",
    "art137_deduction_exact",
    "compute_progressive_tax",
    "compute_tax_for_posture",
    "resolve_welfare_taxable",
)

#: The INTA conservative reading: deduct 2/7 of the employee SSO share
#: (INTA Circular 200/98/44).  The primary response posture per ADR-008.
POSTURE_CONSERVATIVE_INTA: Literal["conservative_inta"] = "conservative_inta"

#: The court reading: deduct the full employee SSO share (Precedents 1956
#: and 3328).
POSTURE_COURT_PRECEDENT: Literal["court_precedent"] = "court_precedent"

TaxPosture = Literal["conservative_inta", "court_precedent"]

_POSTURES: tuple[str, ...] = (POSTURE_CONSERVATIVE_INTA, POSTURE_COURT_PRECEDENT)

_TWO = Decimal(2)
_SEVEN = Decimal(7)


@dataclass(frozen=True, slots=True)
class SlabTaxLine:
    """One taxed slab band, in whole Rial (rounded once from exact values)."""

    slab: int
    rate: Decimal
    taxed_amount_rial: int
    tax_rial: int


@dataclass(frozen=True, slots=True)
class PostureTaxResult:
    """The tax result for one Article 137 posture.

    ``tax_rial`` is the **published** tax total: the sum of the individually
    rounded slab lines, so the published breakdown reconciles with the total
    exactly.  ``tax_exact_rial`` is the exact total rounded once and
    ``rounding_residual_rial`` is their signed difference
    (``sum(lines) - round(exact)``), surfaced per TESTING §4.2(2).
    """

    posture: TaxPosture
    art137_deduction_exact: Decimal
    art137_deduction_rial: int
    welfare_taxable: bool
    taxable_income_exact: Decimal
    taxable_income_rial: int
    taxable_base_clamped: bool
    tax_exact: Decimal
    tax_rial: int
    tax_exact_rial: int
    rounding_residual_rial: int
    slab_labels: tuple[str, ...]
    slab_breakdown: tuple[SlabTaxLine, ...]


def validate_posture(posture: str) -> TaxPosture:
    """Return *posture* if it is one of the two named readings."""
    if posture not in _POSTURES:
        raise PayrollInputError(
            "PAYROLL_INPUT_INVALID: tax_posture must be "
            "'conservative_inta' or 'court_precedent'"
        )
    return cast_tax_posture(posture)


def cast_tax_posture(posture: str) -> TaxPosture:
    """Narrow a validated posture string to the ``TaxPosture`` literal type."""
    return POSTURE_CONSERVATIVE_INTA if posture == POSTURE_CONSERVATIVE_INTA else (
        POSTURE_COURT_PRECEDENT
    )


def resolve_welfare_taxable(posture: TaxPosture) -> bool:
    """Return the DEC-002a binding: welfare taxability per posture.

    ``conservative_inta`` → taxable (the INTA practice);
    ``court_precedent`` → exempt (the Divan rulings).
    """
    return posture == POSTURE_CONSERVATIVE_INTA


def art137_deduction_exact(employee_sso_exact: Decimal, posture: TaxPosture) -> Decimal:
    """Return the exact Article 137 deduction for *posture*.

    ``conservative_inta`` deducts 2/7 of the employee SSO share; the court
    posture deducts the full share.  The input must be the **exact** (not
    rounded) employee share computed on the insurable wage.
    """
    if posture == POSTURE_CONSERVATIVE_INTA:
        return employee_sso_exact * _TWO / _SEVEN
    return employee_sso_exact


def compute_progressive_tax(
    base_after_exemption_exact: Decimal,
    brackets: tuple[TaxBracket, ...],
) -> tuple[Decimal, tuple[str, ...], tuple[SlabTaxLine, ...]]:
    """Return the exact tax on *base_after_exemption_exact* across the slabs.

    The base has already had the exemption removed by the caller, so
    *brackets* must be expressed relative to that same exemption
    (:meth:`StatutoryRuleSet.brackets_above`).  Slab edges are the bracket
    boundaries lowered by one Rial, so a base of exactly ``max_rial`` pays the
    band in full and a base one Rial higher spills into the next slab - the
    boundary is exact to 1 Rial.
    """
    if base_after_exemption_exact < 0:
        raise TaxableBaseNegative(
            "TAXABLE_BASE_NEGATIVE: the post-exemption base is negative"
        )
    with localcontext() as context:
        context.prec = MONEY_PRECISION
        context.rounding = ROUND_HALF_UP
        base = base_after_exemption_exact
        total = Decimal(0)
        labels: list[str] = []
        breakdown: list[SlabTaxLine] = []
        for bracket in brackets:
            if bracket.rate == 0:
                continue
            lower_edge = Decimal(bracket.min_rial - 1)
            if base <= lower_edge:
                continue
            upper_edge = (
                base if bracket.max_rial is None else Decimal(bracket.max_rial)
            )
            band = min(base, upper_edge) - lower_edge
            if band <= 0:
                continue
            band_tax = band * bracket.rate
            total += band_tax
            percent = int(bracket.rate * Decimal(100))
            labels.append(f"Slab {bracket.slab} ({percent}%)")
            breakdown.append(
                SlabTaxLine(
                    slab=bracket.slab,
                    rate=bracket.rate,
                    taxed_amount_rial=round_half_up(band, field="slab_band"),
                    tax_rial=round_half_up(band_tax, field="slab_tax"),
                )
            )
        if not labels:
            labels.append("Slab 1 (0%)")
        return total, tuple(labels), tuple(breakdown)


def compute_tax_for_posture(
    total_gross_rial: int,
    employee_sso_exact: Decimal,
    welfare_total_rial: int,
    non_welfare_exempt_rial: int,
    *,
    posture: TaxPosture,
    rule_set: StatutoryRuleSet,
) -> PostureTaxResult:
    """Compute the full tax result for one posture.

    ``non_welfare_exempt_rial`` carries every non-welfare exempt component
    (currently the continuous attraction allowance when the caller marks it
    exempt); the welfare treatment is bound to the posture by DEC-002a.
    """
    if isinstance(total_gross_rial, bool) or not isinstance(total_gross_rial, int):
        raise PayrollInputError(
            "PAYROLL_INPUT_INVALID: total_gross_rial must be an int number of Rial"
        )
    if total_gross_rial < 0:
        raise PayrollInputError(
            "PAYROLL_INPUT_INVALID: total_gross_rial must be a non-negative int"
        )
    if welfare_total_rial < 0 or non_welfare_exempt_rial < 0:
        raise PayrollInputError(
            "PAYROLL_INPUT_INVALID: the exempt amounts must be non-negative ints"
        )
    deduction_exact = art137_deduction_exact(employee_sso_exact, posture)
    welfare_taxable = resolve_welfare_taxable(posture)
    exempt_total = Decimal(welfare_total_rial if not welfare_taxable else 0) + Decimal(
        non_welfare_exempt_rial
    )
    taxable_exact = Decimal(total_gross_rial) - deduction_exact - exempt_total
    taxable_base_clamped = False
    if taxable_exact < 0:
        # A negative *taxable income* is a legitimate outcome of deductions
        # larger than the gross; it is clamped to zero (no negative tax) and
        # the clamp is published.  A negative *post-exemption base* reaching
        # the ladder is a defect and is refused with TaxableBaseNegative.
        taxable_exact = Decimal(0)
        taxable_base_clamped = True
    base_exact = taxable_exact - Decimal(rule_set.monthly_tax_exemption_rial)
    if base_exact < 0:
        base_exact = Decimal(0)
        taxable_base_clamped = True
    ladder = rule_set.brackets_above(rule_set.monthly_tax_exemption_rial)
    tax_exact, labels, breakdown = compute_progressive_tax(base_exact, ladder)
    # The published total is the sum of the rounded slab lines, so the
    # breakdown reconciles with the total by construction (A-1).  The
    # difference to the exact total is surfaced, signed and bounded.
    tax_rial = sum(line.tax_rial for line in breakdown)
    tax_exact_rial = round_half_up(tax_exact, field="income_tax")
    rounding_residual_rial = tax_rial - tax_exact_rial
    if abs(rounding_residual_rial) > len(breakdown):
        raise TaxableBaseNegative(
            "TAXABLE_BASE_NEGATIVE: the slab reconciliation residual exceeds "
            "one Rial per line"
        )
    return PostureTaxResult(
        posture=posture,
        art137_deduction_exact=deduction_exact,
        art137_deduction_rial=round_half_up(
            deduction_exact, field="art137_deduction"
        ),
        welfare_taxable=welfare_taxable,
        taxable_income_exact=taxable_exact,
        taxable_income_rial=round_half_up(taxable_exact, field="taxable_income"),
        taxable_base_clamped=taxable_base_clamped,
        tax_exact=tax_exact,
        tax_rial=tax_rial,
        tax_exact_rial=tax_exact_rial,
        rounding_residual_rial=rounding_residual_rial,
        slab_labels=labels,
        slab_breakdown=breakdown,
    )
