"""Unit tests for the fail-closed statutory rule-set loader (P1-T01).

Authority:
    ``docs/PISH_HESABDARI_HOLY_BIBLE.md`` §10.5 (versioning), §10.6
    (fail-closed loader behaviour) and §5.11 (verified seed inspection);
    ``docs/specs/STATUTORY_INGESTION.md`` §7 (activation criteria A1-A8);
    ``docs/EXECUTION_PLAN.md`` §7.2 rule 6.
Decision:
    ADR-008 directive 3 - a 1405 request fails closed with
    ``StatutoryParameterUnavailable``; no null is coerced and there is no
    silent 1404 fallback.
Related:
    WBS P1-T01 - statutory rule-set loader (versioned, fail-closed).
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from app.engines.errors import RuleSetNotActive, StatutoryParameterUnavailable
from app.engines.rules import (
    ACTIVE_STATUTORY_YEARS,
    StatutoryRuleSet,
    load_rule_set,
    shift_brackets_by,
    validate_invariants,
)

SEEDS_DIR = Path(__file__).resolve().parents[2] / "data" / "seeds"

# The verified 1404 baseline, restated here so a change to the seed is a
# visible test failure rather than a silent re-baselining.
DAILY_MINIMUM_WAGE_RIAL = 3_463_656
MONTHLY_MINIMUM_30D_RIAL = 103_909_680
MONTHLY_MINIMUM_31D_RIAL = 107_373_336
DAILY_INSURABLE_CEILING_RIAL = 24_245_592
MONTHLY_INSURABLE_30D_RIAL = 727_367_760
MONTHLY_TAX_EXEMPTION_RIAL = 240_000_000
ANNUAL_TAX_EXEMPTION_RIAL = 2_880_000_000
MAX_ANNUAL_EYDRI_RIAL = 311_729_040


@pytest.fixture(scope="module")
def rule_set() -> StatutoryRuleSet:
    """Return the loaded 1404 rule set."""
    return load_rule_set(1404)


# ---------------------------------------------------------------------------
# The 1404 baseline loads
# ---------------------------------------------------------------------------


def test_the_verified_1404_rule_set_loads(rule_set: StatutoryRuleSet) -> None:
    assert rule_set.statutory_version == "1404.1"
    assert rule_set.rule_year_shamsi == 1404
    assert rule_set.rule_set_status == "VERIFIED"
    assert rule_set.is_verified is True
    assert rule_set.effective_date == "1404-01-01"
    assert rule_set.source_circular_reference


def test_the_1404_parameters_match_the_verified_seed(
    rule_set: StatutoryRuleSet,
) -> None:
    assert rule_set.daily_minimum_wage_rial == DAILY_MINIMUM_WAGE_RIAL
    assert rule_set.monthly_minimum_wage_30days_rial == MONTHLY_MINIMUM_30D_RIAL
    assert rule_set.monthly_minimum_wage_31days_rial == MONTHLY_MINIMUM_31D_RIAL
    assert rule_set.monthly_minimum_wage_29days_rial == DAILY_MINIMUM_WAGE_RIAL * 29
    assert rule_set.max_daily_insurable_wage_rial == DAILY_INSURABLE_CEILING_RIAL
    assert rule_set.max_monthly_insurable_wage_30days_rial == MONTHLY_INSURABLE_30D_RIAL
    assert rule_set.monthly_tax_exemption_rial == MONTHLY_TAX_EXEMPTION_RIAL
    assert rule_set.annual_tax_exemption_rial == ANNUAL_TAX_EXEMPTION_RIAL
    assert rule_set.max_annual_eydi_rial == MAX_ANNUAL_EYDRI_RIAL


def test_the_sso_rates_are_the_statutory_constants(rule_set: StatutoryRuleSet) -> None:
    assert rule_set.employee_sso_rate == Decimal("0.07")
    assert rule_set.employer_sso_rate == Decimal("0.20")
    assert rule_set.employer_unemployment_rate == Decimal("0.03")


def test_the_ladder_and_the_multipliers_are_loaded(
    rule_set: StatutoryRuleSet,
) -> None:
    assert rule_set.standard_weekly_hours == Decimal("44.00")
    assert rule_set.overtime_multiplier == Decimal("1.40")
    assert rule_set.night_shift_multiplier == Decimal("1.35")
    assert len(rule_set.tax_brackets) == 6
    assert rule_set.tax_brackets[0].rate == Decimal("0.00")
    assert rule_set.tax_brackets[-1].max_rial is None
    assert rule_set.tax_brackets[-1].rate == Decimal("0.30")


# ---------------------------------------------------------------------------
# Fail-closed behaviour
# ---------------------------------------------------------------------------


def test_the_1405_placeholder_is_refused() -> None:
    """The 1405 seed is transcribed and unverified: it must never load."""
    with pytest.raises(StatutoryParameterUnavailable) as caught:
        load_rule_set(1405)
    assert caught.value.code == "STATUTORY_PARAMETER_UNAVAILABLE"
    assert "STATUTORY_SEED_1405_NOT_VERIFIED" in str(caught.value)


def test_a_year_outside_the_verified_baseline_is_refused() -> None:
    for year in (1399, 1400, 1403, 1406, 1405):
        with pytest.raises((RuleSetNotActive, StatutoryParameterUnavailable)):
            load_rule_set(year)


def test_an_unloadable_year_names_no_figure() -> None:
    """A refusal must not leak any statutory value."""
    with pytest.raises(RuleSetNotActive) as caught:
        load_rule_set(1403)
    message = str(caught.value)
    assert "RULE_SET_YEAR_NOT_LOADABLE" in message
    assert not any(character.isdigit() for character in message)


def test_the_active_year_set_is_exactly_1404() -> None:
    assert frozenset({1404}) == ACTIVE_STATUTORY_YEARS


def test_the_1405_seed_file_exists_but_is_inert() -> None:
    """The placeholder is retained for the future 1404.2 / 1405 work."""
    path = SEEDS_DIR / "statutory_rules_1405.yaml"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "is_verified_and_active: false" in text


# ---------------------------------------------------------------------------
# Invariants R-01 ... R-10
# ---------------------------------------------------------------------------


def test_every_offline_invariant_holds(rule_set: StatutoryRuleSet) -> None:
    results = validate_invariants(rule_set)
    assert set(results) == {f"R-{index:02d}" for index in range(1, 11)}
    assert all(results.values()), [name for name, ok in results.items() if not ok]


def test_an_invariant_violation_fails_closed() -> None:
    """A broken rule set must raise, never load with a silent repair."""
    broken = load_rule_set(1404)
    object.__setattr__(broken, "monthly_tax_exemption_rial", 1)
    with pytest.raises(StatutoryParameterUnavailable) as caught:
        validate_invariants(broken)
    assert "STATUTORY_INVARIANT_VIOLATION" in str(caught.value)


# ---------------------------------------------------------------------------
# Month-length variants
# ---------------------------------------------------------------------------


def test_the_monthly_minimum_wage_depends_on_the_month_length(
    rule_set: StatutoryRuleSet,
) -> None:
    assert rule_set.monthly_minimum_wage_rial(29) == DAILY_MINIMUM_WAGE_RIAL * 29
    assert rule_set.monthly_minimum_wage_rial(30) == MONTHLY_MINIMUM_30D_RIAL
    assert rule_set.monthly_minimum_wage_rial(31) == MONTHLY_MINIMUM_31D_RIAL


def test_an_impossible_month_length_is_refused(rule_set: StatutoryRuleSet) -> None:
    with pytest.raises(RuleSetNotActive):
        rule_set.monthly_minimum_wage_rial(28)
    with pytest.raises(RuleSetNotActive):
        rule_set.monthly_minimum_wage_rial(32)


def test_the_insurable_ceiling_is_seven_daily_wages_per_calendar_day(
    rule_set: StatutoryRuleSet,
) -> None:
    for days in (29, 30, 31):
        assert rule_set.insurable_ceiling_rial(days) == (
            DAILY_INSURABLE_CEILING_RIAL * days
        )


def test_the_overtime_divisor_is_the_paid_calendar_hours(
    rule_set: StatutoryRuleSet,
) -> None:
    """44 hours over 6 working days; never the 176-hour attendance figure."""
    assert rule_set.overtime_divisor(30) == Decimal("220.00")
    assert rule_set.overtime_divisor(31) == Decimal("44.00") * 31 / 6
    assert rule_set.overtime_divisor(29) == Decimal("44.00") * 29 / 6
    assert rule_set.overtime_divisor(30) != Decimal("176.00")


# ---------------------------------------------------------------------------
# The known-defect seed keys are never exposed
# ---------------------------------------------------------------------------


def test_the_rejected_seed_literals_are_not_exposed(
    rule_set: StatutoryRuleSet,
) -> None:
    """HB-GAP-005 and HB-GAP-017: the loader must not carry them."""
    field_names = set(StatutoryRuleSet.__dataclass_fields__)
    assert "eydi_tax_excess_rate" not in field_names
    assert "sanavat_monthly_accrual_rate" not in field_names
    assert "standard_monthly_attendance_hours" not in field_names


# ---------------------------------------------------------------------------
# The ladder shift (the exemption-relative view of the tax ladder)
# ---------------------------------------------------------------------------


def test_the_shifted_ladder_moves_every_edge_down_by_the_exemption(
    rule_set: StatutoryRuleSet,
) -> None:
    shifted = rule_set.brackets_above(MONTHLY_TAX_EXEMPTION_RIAL)
    assert len(shifted) == len(rule_set.tax_brackets)
    for original, moved in zip(rule_set.tax_brackets, shifted, strict=True):
        assert moved.slab == original.slab
        assert moved.rate == original.rate
        assert moved.min_rial == original.min_rial - MONTHLY_TAX_EXEMPTION_RIAL
        if original.max_rial is None:
            assert moved.max_rial is None
        else:
            assert moved.max_rial == original.max_rial - MONTHLY_TAX_EXEMPTION_RIAL


def test_the_shifted_ladder_starts_where_the_exemption_ends(
    rule_set: StatutoryRuleSet,
) -> None:
    """The first taxable slab must begin exactly at the exemption edge."""
    shifted = rule_set.brackets_above(MONTHLY_TAX_EXEMPTION_RIAL)
    assert shifted[0].max_rial == 0
    assert shifted[1].min_rial == 1


def test_a_negative_exemption_is_refused(rule_set: StatutoryRuleSet) -> None:
    with pytest.raises(ValueError, match="exemption_rial"):
        rule_set.brackets_above(-1)
    with pytest.raises(ValueError, match="exemption_rial"):
        shift_brackets_by(rule_set.tax_brackets, -1)


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_loading_twice_returns_the_same_snapshot() -> None:
    assert load_rule_set(1404) is load_rule_set(1404)


def test_the_rule_set_is_immutable(rule_set: StatutoryRuleSet) -> None:
    with pytest.raises(Exception):  # noqa: B017 - frozen dataclass
        rule_set.daily_minimum_wage_rial = 1  # type: ignore[misc]
