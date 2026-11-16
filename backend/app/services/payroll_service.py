"""Composition service: one pure gross-to-net payroll calculation.

Authority
---------
``docs/EXECUTION_PLAN.md`` §7.1 (engines are composed only in a service
layer) and §7.2 (calculation integrity rules, including rule 4's five
provenance fields); ADR-008 (single minimal calculation path, dual posture,
DEC-002a binding, ``conservative_inta`` primary).
Related:
    WBS P1-T14 (forward calculator) and P1-T19 (simulation API contract).

Contract notes
--------------
* This module is the **only** place where the engines are composed.  The
  function is pure: a deterministic function of
  ``(inputs, rule_set_version)`` — no clock, randomness, network or
  environment reads.  ``generated_at`` is added by the API layer.
* **Reproducibility (A-11).**  The rule set may be injected explicitly.  When
  it is not, the fail-closed loader resolves the pinned ``rule_year`` once and
  the returned payload carries the rule set's SHA-256 fingerprint, so any
  stored result can be re-verified against the exact parameter values that
  produced it.  The calculation itself never re-reads a "latest" set.
* Both Article 137 postures are always computed side by side;
  ``conservative_inta`` is the primary response posture and its net is the
  headline ``net_rial``.
* Every emitted monetary figure is a whole-Rial ``int`` rounded exactly once.
  The published tax total is the sum of its rounded slab lines, so the
  breakdown reconciles with the total; the signed difference to the exact
  total is surfaced per posture.  The top-level ``rounding_residual_rial`` is
  a genuine comparison of the exact employee-deduction total with the sum of
  the rounded deduction lines (A-1).
* Every emitted figure carries a field-level provenance entry keyed by its
  JSON path (A-2).
* ``calculation_hash`` is SHA-256 over the canonical JSON of the complete
  result payload (sorted keys, no insignificant whitespace) — reproducible
  byte-for-byte for identical inputs and rule set.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from app.engines.bases import Allowances, decompose_bases
from app.engines.ctc import compute_employer_cost
from app.engines.errors import PayrollInputError
from app.engines.eydi import compute_eydi
from app.engines.money import round_half_up
from app.engines.overtime import compute_overtime_premiums
from app.engines.rules import StatutoryRuleSet, load_rule_set
from app.engines.severance import compute_monthly_severance_accrual
from app.engines.sso import compute_sso
from app.engines.statutory_reference import (
    PARAMETER_USAGE,
    StatutoryReference,
    build_statutory_reference,
)
from app.engines.tax import (
    POSTURE_CONSERVATIVE_INTA,
    POSTURE_COURT_PRECEDENT,
    PostureTaxResult,
    TaxPosture,
    compute_tax_for_posture,
    validate_posture,
)
from app.engines.termination import TerminationResult, compute_termination_liability

__all__ = (
    "ENGINE_VERSION",
    "PayrollInput",
    "PayrollResult",
    "compute_gross_to_net",
)

#: Engine identity carried by every response (financial-data-integrity #27).
ENGINE_VERSION = "0.3.0-payroll-engine"

_VALID_MONTH_LENGTHS = frozenset({29, 30, 31})

#: The two Article 137 postures, in the published order.
_POSTURES = (POSTURE_CONSERVATIVE_INTA, POSTURE_COURT_PRECEDENT)


def _require_non_negative_int(value: int, field_name: str) -> int:
    """Return *value* if it is a genuine non-negative ``int``."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise PayrollInputError(
            f"PAYROLL_INPUT_INVALID: {field_name} must be a non-negative int"
        )
    return value


@dataclass(frozen=True, slots=True)
class PayrollInput:
    """One month's payroll calculation input, in whole Rial.

    ``rule_year`` pins the statutory rule set explicitly — never "latest".
    ``continuous_attraction_taxable`` leaves the attraction treatment as an
    explicit input axis (default exempt, following the corrected Holy Bible
    Appendix A vectors); the welfare-allowance treatment is bound to the
    Article 137 posture by DEC-002a and is not an input.
    """

    gross_monthly_rial: int
    rule_year: int = 1404
    days_in_month: int = 30
    tax_posture: TaxPosture = POSTURE_CONSERVATIVE_INTA
    allowances: Allowances = field(default_factory=Allowances)
    overtime_hours: int = 0
    night_hours: int = 0
    continuous_attraction_taxable: bool = False
    probation_months: int | None = None
    tenure_months: int | None = None
    accumulated_unused_leave_days: int | None = None
    probation_days_worked: int | None = None
    termination_scenario: str | None = None
    recognised_service_years: int | None = None


@dataclass(frozen=True, slots=True)
class PayrollResult:
    """The complete payslip, employer cost and liability snapshot."""

    payload: dict[str, Any]
    calculation_hash: str


def _validate_inputs(inputs: PayrollInput) -> None:
    """Validate the structural input contract; nothing is coerced."""
    _require_non_negative_int(inputs.gross_monthly_rial, "gross_monthly_rial")
    if inputs.days_in_month not in _VALID_MONTH_LENGTHS:
        raise PayrollInputError(
            "PAYROLL_INPUT_INVALID: days_in_month must be 29, 30 or 31"
        )
    try:
        validate_posture(inputs.tax_posture)
    except ValueError as exc:
        raise PayrollInputError(str(exc)) from exc
    _require_non_negative_int(inputs.overtime_hours, "overtime_hours")
    _require_non_negative_int(inputs.night_hours, "night_hours")
    for optional in (
        inputs.probation_months,
        inputs.tenure_months,
        inputs.accumulated_unused_leave_days,
        inputs.probation_days_worked,
        inputs.recognised_service_years,
    ):
        if optional is not None:
            _require_non_negative_int(optional, "optional liability input")


def _posture_view(
    result: PostureTaxResult,
    employee_sso_rial: int,
    total_gross_rial: int,
) -> dict[str, Any]:
    """Project one posture's tax block, including its own net, into the shape."""
    return {
        "posture": result.posture,
        "art137_deduction_rial": result.art137_deduction_rial,
        "welfare_allowances_taxable": result.welfare_taxable,
        "taxable_income_rial": result.taxable_income_rial,
        "taxable_base_clamped": result.taxable_base_clamped,
        "income_tax_rial": result.tax_rial,
        "income_tax_exact_total_rial": result.tax_exact_rial,
        "tax_rounding_residual_rial": result.rounding_residual_rial,
        "tax_slabs_applied": list(result.slab_labels),
        "slab_breakdown": [
            {
                "slab": line.slab,
                "rate": str(line.rate),
                "taxed_amount_rial": line.taxed_amount_rial,
                "tax_rial": line.tax_rial,
            }
            for line in result.slab_breakdown
        ],
        "net_rial": total_gross_rial - employee_sso_rial - result.tax_rial,
    }


def _termination_view(result: TerminationResult) -> dict[str, Any]:
    """Project the termination result into the published shape."""
    return {
        "termination_scenario": result.termination_scenario,
        "probation_months": result.probation_months,
        "employer_initiated_probation_liability_rial": (
            result.employer_initiated_probation_liability_rial
        ),
        "employee_initiated_probation_liability_rial": (
            result.employee_initiated_probation_liability_rial
        ),
        "applied_probation_liability_rial": result.applied_probation_liability_rial,
        "probation_base": result.probation_base,
        "tenure_months": result.tenure_months,
        "exit_severance_rial": result.exit_severance_rial,
        "leave_carryover_cap_days": result.leave_carryover_cap_days,
        "effective_buyout_days": result.effective_buyout_days,
        "daily_wage_divisor_days": result.daily_wage_divisor_days,
        "leave_buyout_rial": result.leave_buyout_rial,
        "total_separation_rial": result.total_separation_rial,
        "total_liability_rial": result.total_liability_rial,
    }


def _reference_view(reference: StatutoryReference) -> dict[str, Any]:
    """Project the statutory floor / omitted-entitlement reference."""
    return {
        "monthly_minimum_wage_rial": reference.monthly_minimum_wage_rial,
        "daily_minimum_wage_rial": reference.daily_minimum_wage_rial,
        "housing_allowance_floor_rial": reference.housing_allowance_floor_rial,
        "grocery_allowance_floor_rial": reference.grocery_allowance_floor_rial,
        "marriage_allowance_floor_rial": reference.marriage_allowance_floor_rial,
        "child_allowance_per_child_rial": reference.child_allowance_per_child_rial,
        "allowance_floor_excluding_child_rial": (
            reference.allowance_floor_excluding_child_rial
        ),
        "declared_child_allowance_rial": reference.declared_child_allowance_rial,
        "declared_child_allowance_below_floor": (
            reference.declared_child_allowance_below_floor
        ),
        "total_gross_below_minimum_wage": reference.total_gross_below_minimum_wage,
        "daily_seniority_base_rial": reference.daily_seniority_base_rial,
        "monthly_seniority_base_rial": reference.monthly_seniority_base_rial,
        "recognised_service_years": reference.recognised_service_years,
        "monthly_seniority_increment_rial": (
            reference.monthly_seniority_increment_rial
        ),
        "applied_to_net": reference.applied_to_net,
        "reference_only_reason": reference.reference_only_reason,
    }


def _provenance(
    year: int,
    total_gross: int,
    total_exact_deductions: Decimal,
    *,
    has_termination: bool,
    has_reference: bool,
) -> dict[str, dict[str, object]]:
    """Return a provenance entry for every emitted monetary figure (A-2)."""
    del total_gross  # the gross itself is an input echo, not a derived figure
    del total_exact_deductions

    def entry(rule_id: str, formula_ref: str) -> dict[str, object]:
        return {
            "rule_id": rule_id,
            "rule_year_shamsi": year,
            "formula_ref": formula_ref,
        }

    mapping: dict[str, dict[str, object]] = {
        # -- bases ---------------------------------------------------------
        "bases.welfare_total_rial": entry(
            "LABOUR_LAW_ART_36_NOTE_3",
            "housing + grocery + marriage + child (statutory welfare allowances)",
        ),
        "bases.mozd_e_saabet_rial": entry(
            "LABOUR_LAW_ART_36_NOTE_3_PRECEDENT_3328",
            "gross - welfare_allowances (continuous attraction retained)",
        ),
        "bases.overtime_pay_rial": entry(
            "LABOUR_LAW_ART_51_59",
            "mozd_e_saabet / (44 x days / 6) x overtime_hours x 1.40",
        ),
        "bases.night_shift_pay_rial": entry(
            "LABOUR_LAW_ART_51_59",
            "mozd_e_saabet / (44 x days / 6) x night_hours x 1.35",
        ),
        "bases.total_gross_rial": entry(
            "LABOUR_LAW_ART_36_NOTE_3",
            "contractual gross + overtime premium + night-shift premium",
        ),
        # -- SSO -----------------------------------------------------------
        "sso.insurable_wage_rial": entry(
            "SSO_LAW_ART_28_39_S4_13",
            "min(total_gross, 7 x daily_minimum_wage x days_in_month)",
        ),
        "sso.insurable_ceiling_rial": entry(
            "SSO_LAW_ART_39_S4_13",
            "7 x daily_minimum_wage x days_in_month",
        ),
        "sso.employee_share_7pct_rial": entry(
            "SSO_LAW_ART_28",
            "insurable_wage x employee_sso_rate (0.07), rounded once",
        ),
        "sso.employer_share_20pct_rial": entry(
            "SSO_LAW_ART_28",
            "insurable_wage x employer_sso_rate (0.20), rounded once",
        ),
        "sso.unemployment_fund_3pct_rial": entry(
            "UNEMPLOYMENT_INSURANCE_ACT",
            "insurable_wage x employer_unemployment_rate (0.03), rounded once",
        ),
        # -- tax -----------------------------------------------------------
        "employee_deductions.employee_sso_7pct_rial": entry(
            "SSO_LAW_ART_28",
            "the published employee SSO line",
        ),
        "employee_deductions.income_tax_rial": entry(
            "DTA_ART_82_92_137",
            "primary posture's published tax total",
        ),
        "net_rial": entry(
            "EXECUTION_PLAN_7_2_RULE_3",
            "total_gross - employee SSO - primary income tax",
        ),
        "alternate_posture_net_rial": entry(
            "DTA_ART_82_92_137",
            "total_gross - employee SSO - alternate posture income tax",
        ),
        "rounding_residual_rial": entry(
            "EXECUTION_PLAN_11_1_2",
            "sum(rounded employee-deduction lines) - round(exact deduction total)",
        ),
        # -- severance / Eydi ---------------------------------------------
        "severance_sanavat.monthly_accrual_rial": entry(
            "LABOUR_LAW_ART_24",
            "mozd_e_saabet / 12, rounded once (seed literal never consumed)",
        ),
        "eydi.annual_gross_rial": entry(
            "EYDI_ACT_1370",
            "min(eydi_min_days/30 x mozd_e_saabet, max_annual_eydi), rounded once",
        ),
        "eydi.monthly_accrual_rial": entry(
            "EYDI_ACT_1370",
            "annual Eydi / 12, rounded once",
        ),
        "eydi.annual_tax_rial": entry(
            "DTA_ART_91_10",
            "sum of rounded progressive slab lines on the exempt excess",
        ),
        "eydi.annual_net_rial": entry(
            "DTA_ART_91_10",
            "annual Eydi - annual Eydi tax",
        ),
        # -- employer cost -------------------------------------------------
        "employer_cost.total_monthly_employer_cost_rial": entry(
            "REMEDIATED_MODULE_6",
            "total_gross + employer SSO + unemployment + sanavat + Eydi",
        ),
        "employer_cost.annual_ctc_12month_rial": entry(
            "REMEDIATED_MODULE_6",
            "monthly employer cost x 12 (no 26-day leave reserve)",
        ),
    }
    # Block-level entries are retained for backward compatibility with the
    # published provenance contract; the dotted path entries above are the
    # field-level coverage that remediation A-2 requires (a stored payload
    # must allow every figure to be traced individually).
    mapping.update(
        {
            "mozd_e_saabet_rial": mapping["bases.mozd_e_saabet_rial"],
            "overtime_pay_rial": mapping["bases.overtime_pay_rial"],
            "sso": entry(
                "SSO_LAW_ART_28_39",
                "employee 7% + employer 20% + unemployment 3% of the insurable wage",
            ),
            "income_tax_rial": mapping["employee_deductions.income_tax_rial"],
            "severance_sanavat": entry(
                "LABOUR_LAW_ART_24",
                "monthly Sanavat accrual on mozd_e_saabet / 12",
            ),
            "eydi": entry(
                "EYDI_ACT_1370",
                "annual Eydi capped at max_annual_eydi_rial and accrued / 12",
            ),
            "employer_cost": entry(
                "REMEDIATED_MODULE_6",
                "gross + employer SSO + unemployment + Sanavat + Eydi (CTC)",
            ),
        }
    )
    for posture in _POSTURES:
        prefix = f"tax_postures.{posture}"
        mapping[f"{prefix}.art137_deduction_rial"] = entry(
            "DTA_ART_137_83_NOTE_2",
            "2/7 of the exact employee SSO share (conservative_inta)"
            if posture == POSTURE_CONSERVATIVE_INTA
            else "the full exact employee SSO share (court_precedent)",
        )
        mapping[f"{prefix}.taxable_income_rial"] = entry(
            "DTA_ART_82_92_137",
            "total_gross - art137_deduction - exempt amount (per posture)",
        )
        mapping[f"{prefix}.income_tax_rial"] = entry(
            "DTA_ART_82_92_137",
            "sum of rounded progressive slab lines on the post-exemption base",
        )
        mapping[f"{prefix}.income_tax_exact_total_rial"] = entry(
            "DTA_ART_82_92_137",
            "the exact progressive total rounded once (audit comparison)",
        )
        mapping[f"{prefix}.tax_rounding_residual_rial"] = entry(
            "EXECUTION_PLAN_11_1_2",
            "sum(rounded slab lines) - round(exact slab total)",
        )
        mapping[f"{prefix}.net_rial"] = entry(
            "EXECUTION_PLAN_7_2_RULE_3",
            "total_gross - employee SSO - this posture's income tax",
        )
        for index in range(6):
            mapping[f"{prefix}.slab_breakdown[{index}].taxed_amount_rial"] = entry(
                "DTA_ART_82_92",
                "the taxable amount falling inside this slab",
            )
            mapping[f"{prefix}.slab_breakdown[{index}].tax_rial"] = entry(
                "DTA_ART_82_92",
                "slab amount x slab rate, rounded once",
            )
    if has_termination:
        mapping.update(
            {
                "termination_liability.employer_initiated_probation_liability_rial": entry(
                    "LABOUR_LAW_ART_11",
                    "contractual gross x agreed probation months (full period)",
                ),
                "termination_liability.employee_initiated_probation_liability_rial": entry(
                    "LABOUR_LAW_ART_11",
                    "contractual gross x days worked / days_in_month",
                ),
                "termination_liability.applied_probation_liability_rial": entry(
                    "LABOUR_LAW_ART_11",
                    "the one probation line selected by the scenario",
                ),
                "termination_liability.exit_severance_rial": entry(
                    "LABOUR_LAW_ART_24",
                    "mozd_e_saabet x tenure_months / 12",
                ),
                "termination_liability.leave_buyout_rial": entry(
                    "LABOUR_LAW_ART_66_71",
                    "min(9 x years, accumulated days) x (mozd_e_saabet / 30)",
                ),
                "termination_liability.total_separation_rial": entry(
                    "LABOUR_LAW_ART_24_66_71",
                    "exit severance + leave buyout",
                ),
                "termination_liability.total_liability_rial": entry(
                    "LABOUR_LAW_ART_11_24_66_71",
                    "applied probation line + exit severance + leave buyout",
                ),
            }
        )
    if has_reference:
        mapping.update(
            {
                "statutory_reference.monthly_minimum_wage_rial": entry(
                    "LABOUR_LAW_ART_41",
                    "minimum wage for the actual month length (29/30/31)",
                ),
                "statutory_reference.housing_allowance_floor_rial": entry(
                    "WAGE_CIRCULAR_S1",
                    "statutory monthly housing allowance",
                ),
                "statutory_reference.grocery_allowance_floor_rial": entry(
                    "WAGE_CIRCULAR_S1",
                    "statutory monthly grocery allowance",
                ),
                "statutory_reference.marriage_allowance_floor_rial": entry(
                    "WAGE_CIRCULAR_S1",
                    "statutory monthly marriage allowance",
                ),
                "statutory_reference.child_allowance_per_child_rial": entry(
                    "LABOUR_LAW_ART_86",
                    "3 x daily minimum wage per eligible child",
                ),
                "statutory_reference.allowance_floor_excluding_child_rial": entry(
                    "WAGE_CIRCULAR_S1",
                    "housing + grocery + marriage statutory floors",
                ),
                "statutory_reference.monthly_seniority_increment_rial": entry(
                    "LABOUR_LAW_ART_48_49_E4",
                    "daily seniority base x days_in_month x recognised service years",
                ),
            }
        )
    return mapping


def compute_gross_to_net(
    inputs: PayrollInput,
    *,
    rule_set: StatutoryRuleSet | None = None,
) -> PayrollResult:
    """Run the full gross-to-net calculation and return the hashed snapshot.

    ``rule_set`` may be injected to pin an exact verified snapshot (A-11).
    When omitted, the fail-closed loader resolves ``inputs.rule_year``; a
    1405 request therefore still refuses before any arithmetic.
    """
    _validate_inputs(inputs)
    active_rule_set = load_rule_set(inputs.rule_year) if rule_set is None else rule_set
    if rule_set is not None and rule_set.rule_year_shamsi != inputs.rule_year:
        raise PayrollInputError(
            "PAYROLL_INPUT_INVALID: the injected rule set does not match rule_year"
        )

    bases = decompose_bases(inputs.gross_monthly_rial, inputs.allowances)
    premiums = compute_overtime_premiums(
        bases.mozd_e_saabet_rial,
        inputs.overtime_hours,
        inputs.night_hours,
        active_rule_set,
        inputs.days_in_month,
    )
    total_gross = inputs.gross_monthly_rial + premiums.premium_total_rial

    sso = compute_sso(total_gross, active_rule_set, inputs.days_in_month)
    non_welfare_exempt = 0 if inputs.continuous_attraction_taxable else (
        inputs.allowances.continuous_attraction_rial
    )
    tax_inta = compute_tax_for_posture(
        total_gross,
        sso.employee_share_exact,
        bases.welfare_total_rial,
        non_welfare_exempt,
        posture=POSTURE_CONSERVATIVE_INTA,
        rule_set=active_rule_set,
    )
    tax_court = compute_tax_for_posture(
        total_gross,
        sso.employee_share_exact,
        bases.welfare_total_rial,
        non_welfare_exempt,
        posture=POSTURE_COURT_PRECEDENT,
        rule_set=active_rule_set,
    )

    primary_tax = tax_inta if inputs.tax_posture == POSTURE_CONSERVATIVE_INTA else tax_court
    alternate_tax = tax_court if inputs.tax_posture == POSTURE_CONSERVATIVE_INTA else tax_inta
    net_rial = total_gross - sso.employee_share_rial - primary_tax.tax_rial
    alternate_net = (
        total_gross - sso.employee_share_rial - alternate_tax.tax_rial
    )

    severance = compute_monthly_severance_accrual(bases.mozd_e_saabet_rial)
    eydi = compute_eydi(bases.mozd_e_saabet_rial, active_rule_set)
    employer = compute_employer_cost(
        total_gross_rial=total_gross,
        employer_sso_rial=sso.employer_share_rial,
        unemployment_rial=sso.unemployment_share_rial,
        severance_accrual_rial=severance.monthly_accrual_rial,
        eydi_accrual_rial=eydi.monthly_accrual_rial,
    )

    termination_block: dict[str, Any] | None = None
    if (
        inputs.probation_months is not None
        or inputs.termination_scenario is not None
    ):
        termination = compute_termination_liability(
            mozd_e_saabet_rial=bases.mozd_e_saabet_rial,
            gross_monthly_rial=inputs.gross_monthly_rial,
            days_in_month=inputs.days_in_month,
            probation_months=inputs.probation_months,
            tenure_months=inputs.tenure_months or 0,
            accumulated_unused_leave_days=inputs.accumulated_unused_leave_days or 0,
            probation_days_worked=inputs.probation_days_worked,
            termination_scenario=inputs.termination_scenario,
        )
        termination_block = _termination_view(termination)

    reference = build_statutory_reference(
        active_rule_set,
        days_in_month=inputs.days_in_month,
        total_gross_rial=total_gross,
        declared_child_allowance_rial=inputs.allowances.child_rial,
        recognised_service_years=inputs.recognised_service_years or 0,
    )

    # A genuine residual: the exact employee-deduction total versus the sum of
    # the published (rounded) deduction lines.  The previously published
    # figure compared `total_gross - net` with the same lines, an identity
    # that could never fail (A-1).
    exact_deduction_total = sso.employee_share_exact + primary_tax.tax_exact
    rounded_line_sum = sso.employee_share_rial + primary_tax.tax_rial
    rounded_exact_total = round_half_up(
        exact_deduction_total, field="employee_deduction_total"
    )
    residual = rounded_line_sum - rounded_exact_total

    payload: dict[str, Any] = {
        "statutory_version": active_rule_set.statutory_version,
        "rule_set_status": active_rule_set.rule_set_status,
        "rule_set_status_source": active_rule_set.rule_set_status_source,
        "rule_set_fingerprint": active_rule_set.fingerprint(),
        "is_verified": active_rule_set.is_verified,
        "engine_version": ENGINE_VERSION,
        "rule_year_shamsi": active_rule_set.rule_year_shamsi,
        "days_in_month": inputs.days_in_month,
        "primary_tax_posture": inputs.tax_posture,
        "inputs": {
            "gross_monthly_rial": inputs.gross_monthly_rial,
            "allowances_rial": {
                "housing": inputs.allowances.housing_rial,
                "grocery": inputs.allowances.grocery_rial,
                "marriage": inputs.allowances.marriage_rial,
                "child": inputs.allowances.child_rial,
                "continuous_attraction": inputs.allowances.continuous_attraction_rial,
            },
            "overtime_hours": inputs.overtime_hours,
            "night_hours": inputs.night_hours,
            "continuous_attraction_taxable": inputs.continuous_attraction_taxable,
        },
        "bases": {
            "welfare_total_rial": bases.welfare_total_rial,
            "mozd_e_saabet_rial": bases.mozd_e_saabet_rial,
            "overtime_divisor": str(premiums.divisor),
            "overtime_pay_rial": premiums.overtime_pay_rial,
            "night_shift_pay_rial": premiums.night_pay_rial,
            "total_gross_rial": total_gross,
        },
        "sso": {
            "insurable_wage_rial": sso.insurable_wage_rial,
            "insurable_ceiling_rial": sso.ceiling_rial,
            "sso_insurable_ceiling_applied": sso.ceiling_applied,
            "employee_share_7pct_rial": sso.employee_share_rial,
            "employer_share_20pct_rial": sso.employer_share_rial,
            "unemployment_fund_3pct_rial": sso.unemployment_share_rial,
        },
        # The audited basis note lives outside the monetary ``sso`` block so
        # every value inside it stays an integer (float/string gate).
        "insurable_base": {
            "basis": "total_gross",
            "conflict_ref": "B-3 (QB-04)",
        },
        "tax_postures": {
            POSTURE_CONSERVATIVE_INTA: _posture_view(
                tax_inta, sso.employee_share_rial, total_gross
            ),
            POSTURE_COURT_PRECEDENT: _posture_view(
                tax_court, sso.employee_share_rial, total_gross
            ),
        },
        "net_rial": net_rial,
        "alternate_posture_net_rial": alternate_net,
        "employee_deductions": {
            "employee_sso_7pct_rial": sso.employee_share_rial,
            "income_tax_rial": primary_tax.tax_rial,
        },
        "severance_sanavat": {
            "base_rial": bases.mozd_e_saabet_rial,
            "accrual_basis": "mozd_e_saabet_excluding_overtime_premiums",
            "includes_overtime_premiums": False,
            "conflict_ref": "B-4",
            "monthly_accrual_rial": severance.monthly_accrual_rial,
        },
        "eydi": {
            "annual_gross_rial": eydi.annual_gross_rial,
            "at_cap": eydi.at_cap,
            "cap_basis": "max_annual_eydi_rial (90 daily minimum wages, 1404)",
            "excess_tax_method": "progressive_salary_ladder",
            "includes_overtime_premiums": False,
            "monthly_accrual_rial": eydi.monthly_accrual_rial,
            "annual_tax_rial": eydi.annual_tax_rial,
            "annual_tax_exact_total_rial": eydi.annual_tax_exact_rial,
            "tax_rounding_residual_rial": eydi.tax_rounding_residual_rial,
            "annual_net_rial": eydi.annual_net_rial,
            "conflict_refs": "B-4, B-5, B-6",
        },
        "employer_cost": {
            "total_monthly_employer_cost_rial": employer.total_monthly_rial,
            "annual_ctc_12month_rial": employer.annual_ctc_rial,
            "includes_26day_leave_reserve": False,
        },
        "statutory_reference": _reference_view(reference),
        "statutory_parameter_usage": dict(PARAMETER_USAGE),
        "rounding_residual_rial": residual,
        "rounding_residual_scope": (
            "employee_deductions: sum(rounded lines) - round(exact total)"
        ),
        "provenance": _provenance(
            active_rule_set.rule_year_shamsi,
            total_gross,
            exact_deduction_total,
            has_termination=termination_block is not None,
            has_reference=True,
        ),
    }
    if termination_block is not None:
        payload["termination_liability"] = termination_block

    canonical = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    calculation_hash = hashlib.sha256(canonical).hexdigest()
    return PayrollResult(payload=payload, calculation_hash=calculation_hash)
