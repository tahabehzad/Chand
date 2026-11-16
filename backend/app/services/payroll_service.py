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
* Both Article 137 postures are always computed side by side;
  ``conservative_inta`` is the primary response posture and its net is the
  headline ``net_rial``.
* Every emitted figure is a whole-Rial ``int`` rounded exactly once; the
  signed ``rounding_residual_rial`` is surfaced per TESTING §4.2(2).
* ``calculation_hash`` is SHA-256 over the canonical JSON of the complete
  result payload (sorted keys, no insignificant whitespace) — reproducible
  byte-for-byte for identical inputs and rule set.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from app.engines.bases import Allowances, decompose_bases
from app.engines.ctc import compute_employer_cost
from app.engines.errors import PayrollInputError
from app.engines.eydi import compute_eydi
from app.engines.money import rounding_residual_rial
from app.engines.overtime import compute_overtime_premiums
from app.engines.rules import load_rule_set
from app.engines.severance import compute_monthly_severance_accrual
from app.engines.sso import compute_sso
from app.engines.tax import (
    POSTURE_CONSERVATIVE_INTA,
    POSTURE_COURT_PRECEDENT,
    PostureTaxResult,
    TaxPosture,
    compute_tax_for_posture,
    validate_posture,
)
from app.engines.termination import compute_termination_liability

__all__ = (
    "ENGINE_VERSION",
    "PayrollInput",
    "PayrollResult",
    "compute_gross_to_net",
)

#: Engine identity carried by every response (financial-data-integrity #27).
ENGINE_VERSION = "0.2.0-payroll-engine"

_VALID_MONTH_LENGTHS = frozenset({29, 30, 31})


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
        "income_tax_rial": result.tax_rial,
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


def compute_gross_to_net(inputs: PayrollInput) -> PayrollResult:
    """Run the full gross-to-net calculation and return the hashed snapshot."""
    _validate_inputs(inputs)
    rule_set = load_rule_set(inputs.rule_year)

    bases = decompose_bases(inputs.gross_monthly_rial, inputs.allowances)
    premiums = compute_overtime_premiums(
        bases.mozd_e_saabet_rial,
        inputs.overtime_hours,
        inputs.night_hours,
        rule_set,
        inputs.days_in_month,
    )
    total_gross = inputs.gross_monthly_rial + premiums.premium_total_rial

    sso = compute_sso(total_gross, rule_set, inputs.days_in_month)
    non_welfare_exempt = 0 if inputs.continuous_attraction_taxable else (
        inputs.allowances.continuous_attraction_rial
    )
    tax_inta = compute_tax_for_posture(
        total_gross,
        sso.employee_share_exact,
        bases.welfare_total_rial,
        non_welfare_exempt,
        posture=POSTURE_CONSERVATIVE_INTA,
        rule_set=rule_set,
    )
    tax_court = compute_tax_for_posture(
        total_gross,
        sso.employee_share_exact,
        bases.welfare_total_rial,
        non_welfare_exempt,
        posture=POSTURE_COURT_PRECEDENT,
        rule_set=rule_set,
    )

    primary_tax = tax_inta if inputs.tax_posture == POSTURE_CONSERVATIVE_INTA else tax_court
    alternate_tax = tax_court if inputs.tax_posture == POSTURE_CONSERVATIVE_INTA else tax_inta
    net_rial = total_gross - sso.employee_share_rial - primary_tax.tax_rial
    alternate_net = (
        total_gross - sso.employee_share_rial - alternate_tax.tax_rial
    )

    severance = compute_monthly_severance_accrual(bases.mozd_e_saabet_rial)
    eydi = compute_eydi(bases.mozd_e_saabet_rial, rule_set)
    employer = compute_employer_cost(
        total_gross_rial=total_gross,
        employer_sso_rial=sso.employer_share_rial,
        unemployment_rial=sso.unemployment_share_rial,
        severance_accrual_rial=severance.monthly_accrual_rial,
        eydi_accrual_rial=eydi.monthly_accrual_rial,
    )

    termination_block: dict[str, Any] | None = None
    if inputs.probation_months is not None:
        termination = compute_termination_liability(
            mozd_e_saabet_rial=bases.mozd_e_saabet_rial,
            gross_monthly_rial=inputs.gross_monthly_rial,
            days_in_month=inputs.days_in_month,
            probation_months=inputs.probation_months,
            tenure_months=inputs.tenure_months or 0,
            accumulated_unused_leave_days=inputs.accumulated_unused_leave_days or 0,
            probation_days_worked=inputs.probation_days_worked,
        )
        termination_block = {
            "probation_months": termination.probation_months,
            "employer_initiated_probation_liability_rial": (
                termination.employer_initiated_probation_liability_rial
            ),
            "employee_initiated_probation_liability_rial": (
                termination.employee_initiated_probation_liability_rial
            ),
            "tenure_months": termination.tenure_months,
            "exit_severance_rial": termination.exit_severance_rial,
            "leave_carryover_cap_days": termination.leave_carryover_cap_days,
            "effective_buyout_days": termination.effective_buyout_days,
            "leave_buyout_rial": termination.leave_buyout_rial,
            "total_separation_rial": termination.total_separation_rial,
        }

    residual = rounding_residual_rial(
        (sso.employee_share_rial, primary_tax.tax_rial),
        total_gross - net_rial,
    )

    payload: dict[str, Any] = {
        "statutory_version": rule_set.statutory_version,
        "rule_set_status": rule_set.rule_set_status,
        "is_verified": rule_set.is_verified,
        "engine_version": ENGINE_VERSION,
        "rule_year_shamsi": rule_set.rule_year_shamsi,
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
            "monthly_accrual_rial": severance.monthly_accrual_rial,
        },
        "eydi": {
            "annual_gross_rial": eydi.annual_gross_rial,
            "at_cap": eydi.at_cap,
            "monthly_accrual_rial": eydi.monthly_accrual_rial,
            "annual_tax_rial": eydi.annual_tax_rial,
            "annual_net_rial": eydi.annual_net_rial,
        },
        "employer_cost": {
            "total_monthly_employer_cost_rial": employer.total_monthly_rial,
            "annual_ctc_12month_rial": employer.annual_ctc_rial,
            "includes_26day_leave_reserve": False,
        },
        "rounding_residual_rial": residual,
        "provenance": {
            "mozd_e_saabet_rial": {
                "rule_id": "LABOUR_LAW_ART_36_NOTE_3_PRECEDENT_3328",
                "rule_year_shamsi": rule_set.rule_year_shamsi,
                "formula_ref": "gross - welfare_allowances (attraction retained)",
            },
            "sso": {
                "rule_id": "SSO_LAW_ART_28_39",
                "rule_year_shamsi": rule_set.rule_year_shamsi,
                "formula_ref": "min(gross, 7 x daily_minimum x days) x rates",
            },
            "income_tax_rial": {
                "rule_id": "DTA_ART_82_92_137",
                "rule_year_shamsi": rule_set.rule_year_shamsi,
                "formula_ref": "progressive slabs on (gross - art137_deduction - exempt)",
            },
            "overtime_pay_rial": {
                "rule_id": "LABOUR_LAW_ART_51_59",
                "rule_year_shamsi": rule_set.rule_year_shamsi,
                "formula_ref": "mozd_e_saabet / (44 x days / 6) x hours x multiplier",
            },
            "severance_sanavat": {
                "rule_id": "LABOUR_LAW_ART_24",
                "rule_year_shamsi": rule_set.rule_year_shamsi,
                "formula_ref": "mozd_e_saabet / 12",
            },
            "eydi": {
                "rule_id": "EYDI_ACT_1370_DTA_ART_91_10",
                "rule_year_shamsi": rule_set.rule_year_shamsi,
                "formula_ref": "min(2 x mozd_e_saabet, max_annual_eydi); progressive excess",
            },
            "employer_cost": {
                "rule_id": "REMEDIATED_MODULE_6",
                "rule_year_shamsi": rule_set.rule_year_shamsi,
                "formula_ref": "gross + employer_sso + unemployment + sanavat + eydi",
            },
        },
    }
    if termination_block is not None:
        payload["termination_liability"] = termination_block

    canonical = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    calculation_hash = hashlib.sha256(canonical).hexdigest()
    return PayrollResult(payload=payload, calculation_hash=calculation_hash)
