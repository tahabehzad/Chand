"""Unit tests for the payroll composition service (P1-T14).

Authority:
    ``docs/EXECUTION_PLAN.md`` آ§7.1 (engines are composed only in a service
    layer) and آ§7.2 (calculation integrity rules, including rule 4's five
    provenance fields); ADR-008 (single minimal calculation path, dual
    posture, ``conservative_inta`` primary).
Spec:
    ``docs/specs/TESTING.md`` properties P-02, P-03, P-10 and the
    financial-data-integrity net-identity and employer-cost identities.
Related:
    WBS P1-T14 - Gross-to-Net forward calculator.
"""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal

import pytest

from app.engines.bases import Allowances
from app.engines.errors import PayrollInputError, RuleSetNotActive, StatutoryParameterUnavailable
from app.engines.rules import load_rule_set
from app.engines.tax import POSTURE_CONSERVATIVE_INTA, POSTURE_COURT_PRECEDENT
from app.services.payroll_service import (
    ENGINE_VERSION,
    PayrollInput,
    PayrollResult,
    compute_gross_to_net,
)

ALLOWANCES = Allowances(
    housing_rial=9_000_000,
    grocery_rial=22_000_000,
    marriage_rial=5_000_000,
    child_rial=10_390_968,
    continuous_attraction_rial=40_000_000,
)


def _inputs(**overrides: object) -> PayrollInput:
    """Return a standard monthly input for the 1404 baseline."""
    defaults: dict[str, object] = {
        "gross_monthly_rial": 341_850_120,
        "rule_year": 1404,
        "days_in_month": 30,
        "tax_posture": POSTURE_CONSERVATIVE_INTA,
        "allowances": ALLOWANCES,
        "overtime_hours": 0,
        "night_hours": 0,
        "continuous_attraction_taxable": False,
    }
    defaults.update(overrides)
    return PayrollInput(**defaults)  # type: ignore[arg-type]


@pytest.fixture(scope="module")
def result() -> PayrollResult:
    """Return one standard calculation."""
    return compute_gross_to_net(_inputs())


# ---------------------------------------------------------------------------
# The five provenance fields (EXECUTION_PLAN آ§7.2 rule 4)
# ---------------------------------------------------------------------------


def test_the_response_carries_the_five_provenance_fields(
    result: PayrollResult,
) -> None:
    payload = result.payload
    assert payload["statutory_version"] == "1404.1"
    assert payload["rule_set_status"] == "VERIFIED"
    assert payload["is_verified"] is True
    assert payload["engine_version"] == ENGINE_VERSION
    assert result.calculation_hash
    assert len(result.calculation_hash) == 64


def test_the_calculation_hash_is_a_sha256_over_the_canonical_payload(
    result: PayrollResult,
) -> None:
    canonical = json.dumps(
        result.payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    assert hashlib.sha256(canonical).hexdigest() == result.calculation_hash


def test_every_emitted_figure_carries_a_rule_id(result: PayrollResult) -> None:
    provenance = result.payload["provenance"]
    assert isinstance(provenance, dict)
    assert provenance
    for figure, entry in provenance.items():
        assert figure, "a provenance entry must name its figure"
        assert entry["rule_id"]
        assert entry["rule_year_shamsi"] == 1404
        assert entry["formula_ref"]


def test_the_provenance_covers_the_statutory_lines(result: PayrollResult) -> None:
    provenance = result.payload["provenance"]
    for figure in (
        "mozd_e_saabet_rial",
        "sso",
        "income_tax_rial",
        "overtime_pay_rial",
        "severance_sanavat",
        "eydi",
        "employer_cost",
    ):
        assert figure in provenance


# ---------------------------------------------------------------------------
# Property P-03 - the net identity
# ---------------------------------------------------------------------------


def test_the_net_identity_holds_exactly(result: PayrollResult) -> None:
    payload = result.payload
    total_gross = payload["bases"]["total_gross_rial"]
    employee_sso = payload["sso"]["employee_share_7pct_rial"]
    tax = payload["employee_deductions"]["income_tax_rial"]
    assert total_gross - employee_sso - tax == payload["net_rial"]


def test_the_employer_cost_identity_holds_exactly(result: PayrollResult) -> None:
    payload = result.payload
    employer = payload["employer_cost"]
    assert employer["total_monthly_employer_cost_rial"] == (
        payload["bases"]["total_gross_rial"]
        + payload["sso"]["employer_share_20pct_rial"]
        + payload["sso"]["unemployment_fund_3pct_rial"]
        + payload["severance_sanavat"]["monthly_accrual_rial"]
        + payload["eydi"]["monthly_accrual_rial"]
    )


def test_the_rounding_residual_never_exceeds_one_rial(result: PayrollResult) -> None:
    assert abs(result.payload["rounding_residual_rial"]) <= 1


def test_no_emitted_monetary_value_is_a_float(result: PayrollResult) -> None:
    """Monetary values are JSON integers in Rial (financial-data-integrity 26)."""
    for key in ("net_rial", "rounding_residual_rial", "alternate_posture_net_rial"):
        assert isinstance(result.payload[key], int)
    assert isinstance(result.payload["sso"], dict)
    for key, value in result.payload["sso"].items():
        assert isinstance(value, (int, bool)), key


# ---------------------------------------------------------------------------
# The dual posture (ADR-008)
# ---------------------------------------------------------------------------


def test_both_postures_are_always_computed(result: PayrollResult) -> None:
    postures = result.payload["tax_postures"]
    assert set(postures) == {POSTURE_CONSERVATIVE_INTA, POSTURE_COURT_PRECEDENT}


def test_the_conservative_posture_is_primary_by_default(result: PayrollResult) -> None:
    assert result.payload["primary_tax_posture"] == POSTURE_CONSERVATIVE_INTA
    conservative = result.payload["tax_postures"][POSTURE_CONSERVATIVE_INTA]
    assert conservative["net_rial"] == result.payload["net_rial"]


def test_the_alternate_posture_net_is_the_other_posture() -> None:
    calculation = compute_gross_to_net(_inputs())
    postures = calculation.payload["tax_postures"]
    assert (
        calculation.payload["alternate_posture_net_rial"]
        == postures[POSTURE_COURT_PRECEDENT]["net_rial"]
    )


def test_selecting_the_court_posture_swaps_the_headline_net() -> None:
    calculation = compute_gross_to_net(_inputs(tax_posture=POSTURE_COURT_PRECEDENT))
    postures = calculation.payload["tax_postures"]
    assert calculation.payload["primary_tax_posture"] == POSTURE_COURT_PRECEDENT
    assert calculation.payload["net_rial"] == postures[POSTURE_COURT_PRECEDENT]["net_rial"]
    assert (
        calculation.payload["alternate_posture_net_rial"]
        == postures[POSTURE_CONSERVATIVE_INTA]["net_rial"]
    )


def test_the_two_postures_really_differ() -> None:
    calculation = compute_gross_to_net(_inputs())
    postures = calculation.payload["tax_postures"]
    assert (
        postures[POSTURE_CONSERVATIVE_INTA]["income_tax_rial"]
        != postures[POSTURE_COURT_PRECEDENT]["income_tax_rial"]
    )


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_the_same_inputs_produce_the_same_hash() -> None:
    first = compute_gross_to_net(_inputs())
    second = compute_gross_to_net(_inputs())
    assert first.calculation_hash == second.calculation_hash
    assert first.payload == second.payload


def test_a_different_gross_produces_a_different_hash() -> None:
    first = compute_gross_to_net(_inputs())
    second = compute_gross_to_net(_inputs(gross_monthly_rial=341_850_121))
    assert first.calculation_hash != second.calculation_hash


def test_the_calculation_reads_no_clock_or_environment() -> None:
    """The service is a pure function of (inputs, rule_set_version)."""
    payload = compute_gross_to_net(_inputs()).payload
    assert "generated_at" not in payload
    assert "timestamp" not in payload


# ---------------------------------------------------------------------------
# Property P-10 - allowance order independence
# ---------------------------------------------------------------------------


def test_the_allowance_order_does_not_change_the_result() -> None:
    first = compute_gross_to_net(_inputs(allowances=ALLOWANCES))
    reordered = Allowances(
        child_rial=ALLOWANCES.child_rial,
        continuous_attraction_rial=ALLOWANCES.continuous_attraction_rial,
        marriage_rial=ALLOWANCES.marriage_rial,
        grocery_rial=ALLOWANCES.grocery_rial,
        housing_rial=ALLOWANCES.housing_rial,
    )
    second = compute_gross_to_net(_inputs(allowances=reordered))
    assert first.calculation_hash == second.calculation_hash


# ---------------------------------------------------------------------------
# Property P-02 - the net is monotonically non-decreasing in the gross
# ---------------------------------------------------------------------------


def test_the_net_is_monotonically_non_decreasing_in_the_gross() -> None:
    previous = -1
    for gross in range(50_000_000, 50_000_000 + 5_000_000, 250_000):
        net = compute_gross_to_net(_inputs(gross_monthly_rial=gross)).payload["net_rial"]
        assert net >= previous
        previous = net


# ---------------------------------------------------------------------------
# The bases and the premiums
# ---------------------------------------------------------------------------


def test_the_saabet_and_the_welfare_total_are_reported(result: PayrollResult) -> None:
    bases = result.payload["bases"]
    assert bases["welfare_total_rial"] == 46_390_968
    assert bases["mozd_e_saabet_rial"] == 295_459_152
    assert bases["total_gross_rial"] == 341_850_120


def test_the_overtime_premium_is_added_to_the_total_gross() -> None:
    calculation = compute_gross_to_net(_inputs(overtime_hours=10, night_hours=5))
    bases = calculation.payload["bases"]
    assert bases["total_gross_rial"] == (
        341_850_120 + bases["overtime_pay_rial"] + bases["night_shift_pay_rial"]
    )
    assert bases["overtime_divisor"] == "220.00"


def test_the_overtime_divisor_follows_the_month_length() -> None:
    calculation = compute_gross_to_net(_inputs(days_in_month=31))
    divisor = Decimal(calculation.payload["bases"]["overtime_divisor"])
    assert abs(divisor - Decimal("44.00") * 31 / 6) < Decimal("1e-20")
    assert divisor != Decimal("176.00")


def test_the_sso_ceiling_flag_is_reported(result: PayrollResult) -> None:
    assert result.payload["sso"]["sso_insurable_ceiling_applied"] is False
    assert result.payload["sso"]["insurable_ceiling_rial"] == 727_367_760


def test_the_ceiling_flag_becomes_true_above_the_ceiling() -> None:
    calculation = compute_gross_to_net(_inputs(gross_monthly_rial=900_000_000))
    assert calculation.payload["sso"]["sso_insurable_ceiling_applied"] is True
    assert calculation.payload["sso"]["insurable_wage_rial"] == 727_367_760


def test_the_employer_cost_has_no_leave_reserve(result: PayrollResult) -> None:
    assert result.payload["employer_cost"]["includes_26day_leave_reserve"] is False


# ---------------------------------------------------------------------------
# The termination block
# ---------------------------------------------------------------------------


def test_the_termination_block_is_absent_without_probation() -> None:
    assert "termination_liability" not in compute_gross_to_net(_inputs()).payload


def test_the_termination_block_is_present_with_probation() -> None:
    calculation = compute_gross_to_net(
        _inputs(probation_months=3, tenure_months=24, accumulated_unused_leave_days=12)
    )
    block = calculation.payload["termination_liability"]
    assert block is not None
    assert block["employer_initiated_probation_liability_rial"] == 1_025_550_360
    assert block["exit_severance_rial"] == 590_918_304
    assert block["leave_carryover_cap_days"] == 18
    assert block["effective_buyout_days"] == 12
    assert block["total_separation_rial"] == (
        block["exit_severance_rial"] + block["leave_buyout_rial"]
    )


# ---------------------------------------------------------------------------
# Input validation (nothing is coerced)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "overrides",
    [
        {"gross_monthly_rial": -1},
        {"gross_monthly_rial": 1.5},
        {"days_in_month": 28},
        {"overtime_hours": -1},
        {"night_hours": -1},
        {"tax_posture": "some_other_reading"},
        {"tenure_months": -1},
        {"probation_months": 4},
    ],
)
def test_an_invalid_input_is_refused(overrides: dict[str, object]) -> None:
    with pytest.raises((PayrollInputError, ValueError)):
        compute_gross_to_net(_inputs(**overrides))


def test_an_unverified_rule_year_is_refused() -> None:
    with pytest.raises(StatutoryParameterUnavailable):
        compute_gross_to_net(_inputs(rule_year=1405))


def test_a_year_without_a_rule_set_is_refused() -> None:
    with pytest.raises(RuleSetNotActive):
        compute_gross_to_net(_inputs(rule_year=1403))


def test_the_rule_set_used_is_the_verified_one() -> None:
    rule_set = load_rule_set(1404)
    calculation = compute_gross_to_net(_inputs())
    assert calculation.payload["statutory_version"] == rule_set.statutory_version
    assert calculation.payload["rule_year_shamsi"] == rule_set.rule_year_shamsi


def test_the_exact_decimal_base_is_used_for_the_article_137_deduction() -> None:
    """The deduction is computed on the exact, unrounded employee share."""
    calculation = compute_gross_to_net(_inputs())
    sso = calculation.payload["sso"]
    conservative = calculation.payload["tax_postures"][POSTURE_CONSERVATIVE_INTA]
    expected = Decimal(sso["employee_share_7pct_rial"] + 1) * Decimal(2) / Decimal(7)
    assert abs(Decimal(conservative["art137_deduction_rial"]) - expected) <= 1
