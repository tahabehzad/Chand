"""Unit tests for the progressive income tax engine (P1-T05).

Authority:
    ``docs/PISH_HESABDARI_HOLY_BIBLE.md`` §2.3 B/C, §2.5 and Appendix A
    (the independent recalculation of the worked example); Direct Taxation
    Act Arts. 82-92 and 137 with Note 2 of Art. 83; INTA Circular 200/98/44;
    Diwan-e Edalat-e Edari Precedents 1956 and 3328 (``FIND-LEG-02``).
Decision:
    ADR-008 (owner, 2026-11-15) resolves DEC-002a - the welfare allowances
    are taxable under ``conservative_inta`` and exempt under
    ``court_precedent``; both postures are always computed side by side.
Spec:
    ``docs/specs/TESTING.md`` properties P-07 and P-08.
Related:
    WBS P1-T05 - tax engine.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

import pytest

from app.engines.rules import StatutoryRuleSet, load_rule_set
from app.engines.tax import (
    POSTURE_CONSERVATIVE_INTA,
    POSTURE_COURT_PRECEDENT,
    art137_deduction_exact,
    compute_progressive_tax,
    compute_tax_for_posture,
    resolve_welfare_taxable,
    validate_posture,
)

MONTHLY_EXEMPTION_RIAL = 240_000_000


@pytest.fixture(scope="module")
def rule_set() -> StatutoryRuleSet:
    """Return the loaded 1404 rule set."""
    return load_rule_set(1404)


def _ladder_tax(rule_set: StatutoryRuleSet, taxable_exact: Decimal) -> tuple[int, tuple[str, ...]]:
    """Tax *taxable_exact* the way the engine does, in the test itself."""
    base = taxable_exact - Decimal(rule_set.monthly_tax_exemption_rial)
    if base < 0:
        base = Decimal(0)
    exact, labels, _breakdown = compute_progressive_tax(
        base, rule_set.brackets_above(rule_set.monthly_tax_exemption_rial)
    )
    return int(exact.quantize(Decimal("1"), rounding=ROUND_HALF_UP)), labels


# ---------------------------------------------------------------------------
# The approved engineering-reference vectors (Holy Bible Appendix A)
# ---------------------------------------------------------------------------


def test_the_appendix_a4_vector_is_reproduced(rule_set: StatutoryRuleSet) -> None:
    """A.4: taxable income 277,920,611.60 -> tax 3,792,061 (slab 2)."""
    tax_rial, labels = _ladder_tax(rule_set, Decimal("277920611.60"))
    assert tax_rial == 3_792_061
    assert labels == ("Slab 2 (10%)",)


def test_the_appendix_a5_vector_is_reproduced(rule_set: StatutoryRuleSet) -> None:
    """A.5: taxable income 377,647,058.87 -> tax 17,647,059 (slabs 2 and 3)."""
    tax_rial, labels = _ladder_tax(rule_set, Decimal("377647058.87"))
    assert tax_rial == 17_647_059
    assert labels == ("Slab 2 (10%)", "Slab 3 (15%)",)


def test_the_two_reference_vectors_agree_with_the_absolute_ladder(
    rule_set: StatutoryRuleSet,
) -> None:
    """The shifted ladder is equivalent to the absolute ladder on the
    taxable income; the two forms must never diverge."""
    for taxable in ("277920611.60", "377647058.87", "500000000.00", "900000000.00"):
        absolute, _labels, _breakdown = compute_progressive_tax(
            Decimal(taxable), rule_set.tax_brackets
        )
        shifted_rial, _labels2 = _ladder_tax(rule_set, Decimal(taxable))
        base = Decimal(taxable) - Decimal(MONTHLY_EXEMPTION_RIAL)
        if base < 0:
            base = Decimal(0)
        shifted_exact, _l, _b = compute_progressive_tax(
            base, rule_set.brackets_above(MONTHLY_EXEMPTION_RIAL)
        )
        assert shifted_exact == absolute
        assert shifted_rial == int(absolute.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def test_a_taxable_income_below_the_exemption_is_not_taxed(
    rule_set: StatutoryRuleSet,
) -> None:
    tax_rial, labels = _ladder_tax(rule_set, Decimal("100000000"))
    assert tax_rial == 0
    assert labels == ("Slab 1 (0%)",)


# ---------------------------------------------------------------------------
# The slab boundaries are exact to one Rial
# ---------------------------------------------------------------------------


def test_a_base_exactly_on_a_slab_edge_pays_that_band_in_full(
    rule_set: StatutoryRuleSet,
) -> None:
    ladder = rule_set.brackets_above(MONTHLY_EXEMPTION_RIAL)
    # Slab 2 of the shifted ladder covers 1 .. 60,000,000 at 10 %.
    exact, _labels, breakdown = compute_progressive_tax(Decimal(60_000_000), ladder)
    assert exact == Decimal("6000000")
    assert breakdown[0].taxed_amount_rial == 60_000_000
    assert breakdown[0].tax_rial == 6_000_000


def test_each_band_reports_the_rate_that_was_applied(
    rule_set: StatutoryRuleSet,
) -> None:
    """A reviewer must see the rate of every band, not infer it."""
    ladder = rule_set.brackets_above(MONTHLY_EXEMPTION_RIAL)
    _exact, _labels, breakdown = compute_progressive_tax(Decimal(200_000_000), ladder)
    assert [line.slab for line in breakdown] == [2, 3, 4]
    assert [str(line.rate) for line in breakdown] == ["0.10", "0.15", "0.20"]


def test_one_rial_more_spills_into_the_next_band(rule_set: StatutoryRuleSet) -> None:
    ladder = rule_set.brackets_above(MONTHLY_EXEMPTION_RIAL)
    exact, _labels, breakdown = compute_progressive_tax(Decimal(60_000_001), ladder)
    assert len(breakdown) == 2
    assert breakdown[0].tax_rial == 6_000_000
    assert breakdown[1].taxed_amount_rial == 1
    assert int(exact.quantize(Decimal("1"), rounding=ROUND_HALF_UP)) == 6_000_000


def test_a_base_exactly_on_the_last_band_edge_is_not_truncated(
    rule_set: StatutoryRuleSet,
) -> None:
    ladder = rule_set.brackets_above(MONTHLY_EXEMPTION_RIAL)
    exact, _labels, _breakdown = compute_progressive_tax(Decimal(140_000_000), ladder)
    assert int(exact.quantize(Decimal("1"), rounding=ROUND_HALF_UP)) == 6_000_000 + 12_000_000


def test_the_top_band_is_open_ended(rule_set: StatutoryRuleSet) -> None:
    ladder = rule_set.brackets_above(MONTHLY_EXEMPTION_RIAL)
    _exact, _labels, breakdown = compute_progressive_tax(Decimal(1_000_000_000), ladder)
    assert breakdown[-1].slab == 6
    # The band tax is computed on the exact band and rounded once at the
    # line boundary, so it may differ by one Rial from the rate applied to
    # the rounded band amount.
    assert abs(
        breakdown[-1].tax_rial - int(Decimal("0.30") * breakdown[-1].taxed_amount_rial)
    ) <= 1


# ---------------------------------------------------------------------------
# The Article 137 dual posture (DEC-002a, ADR-008)
# ---------------------------------------------------------------------------


def test_the_two_postures_are_named_readings() -> None:
    assert validate_posture(POSTURE_CONSERVATIVE_INTA) == "conservative_inta"
    assert validate_posture(POSTURE_COURT_PRECEDENT) == "court_precedent"
    with pytest.raises(ValueError, match="PAYROLL_INPUT_INVALID"):
        validate_posture("some_other_reading")


def test_the_welfare_treatment_is_bound_to_the_posture() -> None:
    assert resolve_welfare_taxable(POSTURE_CONSERVATIVE_INTA) is True
    assert resolve_welfare_taxable(POSTURE_COURT_PRECEDENT) is False


def test_the_conservative_posture_deducts_two_sevenths_of_the_employee_share() -> None:
    exact = Decimal("23929508.40")
    assert art137_deduction_exact(exact, POSTURE_CONSERVATIVE_INTA) == (
        exact * Decimal(2) / Decimal(7)
    )


def test_the_court_posture_deducts_the_whole_employee_share() -> None:
    exact = Decimal("23929508.40")
    assert art137_deduction_exact(exact, POSTURE_COURT_PRECEDENT) == exact


def test_both_postures_are_always_computed_and_differ(
    rule_set: StatutoryRuleSet,
) -> None:
    gross = 600_000_000
    employee_sso = Decimal("42000000.00")
    welfare = 46_390_968
    attraction = 40_000_000

    inta = compute_tax_for_posture(
        gross,
        employee_sso,
        welfare,
        attraction,
        posture=POSTURE_CONSERVATIVE_INTA,
        rule_set=rule_set,
    )
    court = compute_tax_for_posture(
        gross,
        employee_sso,
        welfare,
        attraction,
        posture=POSTURE_COURT_PRECEDENT,
        rule_set=rule_set,
    )

    assert inta.posture == POSTURE_CONSERVATIVE_INTA
    assert court.posture == POSTURE_COURT_PRECEDENT
    assert inta.welfare_taxable is True
    assert court.welfare_taxable is False
    assert inta.art137_deduction_rial < court.art137_deduction_rial
    assert inta.tax_rial != court.tax_rial


def test_the_conservative_posture_taxes_the_welfare_allowances(
    rule_set: StatutoryRuleSet,
) -> None:
    gross = 600_000_000
    employee_sso = Decimal("42000000.00")
    result = compute_tax_for_posture(
        gross,
        employee_sso,
        46_390_968,
        0,
        posture=POSTURE_CONSERVATIVE_INTA,
        rule_set=rule_set,
    )
    # The welfare total is inside the taxable income under this posture:
    # only the Art. 137 deduction (2/7 of the employee share) is removed.
    assert result.taxable_income_exact == (
        Decimal(gross) - Decimal(2) / Decimal(7) * employee_sso
    )


def test_the_court_posture_exempts_the_welfare_allowances(
    rule_set: StatutoryRuleSet,
) -> None:
    gross = 600_000_000
    employee_sso = Decimal("42000000.00")
    result = compute_tax_for_posture(
        gross,
        employee_sso,
        46_390_968,
        0,
        posture=POSTURE_COURT_PRECEDENT,
        rule_set=rule_set,
    )
    assert result.taxable_income_exact == Decimal(gross) - employee_sso - Decimal(46_390_968)


# ---------------------------------------------------------------------------
# Property P-07 - the taxable base is never negative
# ---------------------------------------------------------------------------


def test_the_taxable_base_is_never_negative(rule_set: StatutoryRuleSet) -> None:
    for gross in (1, 1_000, 1_000_000, 46_390_968, 100_000_000):
        for posture in (POSTURE_CONSERVATIVE_INTA, POSTURE_COURT_PRECEDENT):
            result = compute_tax_for_posture(
                gross,
                Decimal("70000.00"),
                46_390_968,
                0,
                posture=posture,
                rule_set=rule_set,
            )
            assert result.taxable_income_rial >= 0
            assert result.tax_rial >= 0


def test_a_negative_base_is_refused(rule_set: StatutoryRuleSet) -> None:
    with pytest.raises(ValueError, match="TAXABLE_BASE_NEGATIVE"):
        compute_progressive_tax(Decimal(-1), rule_set.tax_brackets)


# ---------------------------------------------------------------------------
# Property P-08 - the applied rate is monotonically non-decreasing
# ---------------------------------------------------------------------------


def test_the_marginal_rate_never_decreases(rule_set: StatutoryRuleSet) -> None:
    ladder = rule_set.brackets_above(MONTHLY_EXEMPTION_RIAL)
    previous_rate = Decimal(0)
    for step in range(0, 900):
        base = Decimal(step * 1_000_000)
        exact, labels, breakdown = compute_progressive_tax(base, ladder)
        assert exact >= 0
        if breakdown:
            rate = Decimal(breakdown[-1].tax_rial) / Decimal(breakdown[-1].taxed_amount_rial)
            assert rate >= previous_rate - Decimal("0.0001")
            previous_rate = rate
        assert labels


def test_the_tax_is_monotonically_non_decreasing_in_the_taxable_base(
    rule_set: StatutoryRuleSet,
) -> None:
    ladder = rule_set.brackets_above(MONTHLY_EXEMPTION_RIAL)
    previous = Decimal(0)
    for step in range(0, 500):
        exact, _labels, _breakdown = compute_progressive_tax(
            Decimal(step * 1_000_000), ladder
        )
        assert exact >= previous
        previous = exact
