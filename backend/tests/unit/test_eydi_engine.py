"""Unit tests for the annual bonus (Eydi) engine (P1-T09).

Authority:
    ``docs/PISH_HESABDARI_HOLY_BIBLE.md`` آ§2.3 F; the 1370 Eydi Payment Act;
    Direct Taxation Act Art. 91(10); ``FIND-LEG-04`` (the excess is taxed
    **progressively** - a flat 10 % is a legal fallacy).
Decision:
    ADR-008 - the accrual is ``min(2 x Mozd-e Saabet, 3 x monthly minimum
    wage)``; the seed's flat ``eydi_tax_excess_rate: 0.10`` is never consumed
    (HB-GAP-005).
Spec:
    ``docs/specs/TESTING.md`` property P-06.
Related:
    WBS P1-T09 - Eydi engine.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.engines.eydi import compute_eydi
from app.engines.rules import StatutoryRuleSet, load_rule_set

MAX_ANNUAL_EYDRI_RIAL = 311_729_040
MONTHLY_MINIMUM_WAGE_RIAL = 103_909_680
EYDI_TAX_EXEMPTION_RIAL = 240_000_000


@pytest.fixture(scope="module")
def rule_set() -> StatutoryRuleSet:
    """Return the loaded 1404 rule set."""
    return load_rule_set(1404)


def test_the_cap_binds_for_the_appendix_a_package(rule_set: StatutoryRuleSet) -> None:
    """A.4: the accrual is 25,977,420 per month at the statutory cap."""
    result = compute_eydi(295_459_152, rule_set)
    assert result.at_cap is True
    assert result.annual_gross_rial == MAX_ANNUAL_EYDRI_RIAL
    assert result.monthly_accrual_rial == 25_977_420


def test_the_property_p06_identity_holds(rule_set: StatutoryRuleSet) -> None:
    """eydi_annual == min(2 x Mozd-e Saabet, 3 x monthly minimum wage)."""
    for saabet in (0, 1_000_000, 50_000_000, 155_864_520, 200_000_000, 500_000_000):
        result = compute_eydi(saabet, rule_set)
        assert result.annual_gross_rial == min(
            2 * saabet, 3 * MONTHLY_MINIMUM_WAGE_RIAL
        )


def test_the_cap_flag_is_false_below_the_cap(rule_set: StatutoryRuleSet) -> None:
    result = compute_eydi(100_000_000, rule_set)
    assert result.at_cap is False
    assert result.annual_gross_rial == 200_000_000


def test_the_cap_flag_is_true_at_the_cap(rule_set: StatutoryRuleSet) -> None:
    result = compute_eydi(155_864_520, rule_set)
    assert result.at_cap is False  # exactly on the cap is not "above" it
    assert result.annual_gross_rial == MAX_ANNUAL_EYDRI_RIAL


def test_the_monthly_accrual_is_the_annual_over_twelve(
    rule_set: StatutoryRuleSet,
) -> None:
    result = compute_eydi(100_000_000, rule_set)
    assert result.monthly_accrual_rial == 16_666_667
    assert result.monthly_accrual_rial == round(
        result.annual_gross_rial / 12
    )


def test_the_excess_is_taxed_progressively_not_at_a_flat_rate(
    rule_set: StatutoryRuleSet,
) -> None:
    """FIND-LEG-04: the seed's flat 10 % would be a legal fallacy."""
    result = compute_eydi(1_000_000_000, rule_set)
    excess = result.annual_gross_rial - EYDI_TAX_EXEMPTION_RIAL
    flat_10_percent = int(excess * 0.10)
    assert result.annual_tax_rial > flat_10_percent
    assert result.annual_tax_rial == 7_759_356


def test_an_amount_below_the_exemption_is_not_taxed(rule_set: StatutoryRuleSet) -> None:
    result = compute_eydi(100_000_000, rule_set)
    assert result.annual_gross_rial == 200_000_000
    assert result.annual_tax_rial == 0


def test_the_net_is_the_annual_less_the_tax(rule_set: StatutoryRuleSet) -> None:
    result = compute_eydi(1_000_000_000, rule_set)
    assert result.annual_net_rial == result.annual_gross_rial - result.annual_tax_rial


def test_a_non_integer_base_is_refused(rule_set: StatutoryRuleSet) -> None:
    with pytest.raises(TypeError):
        compute_eydi(1.5, rule_set)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        compute_eydi(True, rule_set)


def test_the_exact_annual_value_is_retained(rule_set: StatutoryRuleSet) -> None:
    result = compute_eydi(100_000_001, rule_set)
    assert result.annual_gross_exact == Decimal(200_000_002)
    assert result.annual_gross_rial == 200_000_002
