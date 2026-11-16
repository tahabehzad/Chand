"""Composition of the advisory compensation proposal (ADR-009).

Authority
---------
``docs/adr/ADR-009-compensation-advisory-module.md``, directives 1, 3, 4 and 5.
Related: WBS `P5-T02`; ``AGENTS.md`` §2 invariants 4, 5, 6, 9 and 11.

Design
------
This service is a thin composition, deliberately:

1. the pure valuation model scores the documented profile
   (:func:`app.engines.valuation.assess_profile`);
2. the same model places the score inside the manager's band and publishes a
   range (:func:`app.engines.valuation.propose_gross_range`);
3. **the existing statutory engine** costs the two ends of that range and its
   midpoint (:func:`app.services.payroll_service.compute_gross_to_net`).

Nothing here re-implements tax, insurance, severance, bonus or employer cost,
and nothing here invents a statutory value.  Every response is marked
advisory, carries the model version and the weights, and publishes the exact
request of each statutory call so the figures can be replayed against the
simulation endpoint.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from app.engines.bases import Allowances
from app.engines.rules import StatutoryRuleSet, load_rule_set
from app.engines.tax import POSTURE_CONSERVATIVE_INTA, TaxPosture
from app.engines.valuation import (
    RANGE_SPREAD_FRACTION,
    VALUATION_MODEL_VERSION,
    EducationLevel,
    assess_profile,
    propose_gross_range,
)
from app.services.payroll_service import (
    ENGINE_VERSION,
    PayrollInput,
    compute_gross_to_net,
)

__all__ = ("ValuationInput", "ValuationResult", "compute_compensation_proposal")

#: Published limitations, emitted with every proposal.
_ADVISORY_NOTES: tuple[str, ...] = (
    "This proposal is advisory: the manager decides the salary (AGENTS.md invariant 5).",
    "The band is manager-supplied; no market, benchmark or actuarial data is used (DEC-007/DEC-008 rejected).",
    "The score is a published policy heuristic, not a verdict about the person (AGENTS.md invariant 4).",
    "Statutory figures are the verified 1404 engine's output, not tax advice (DEC-009 neutral calculator).",
    "The statutory minimum wage is published for comparison only and is never applied (DEC-013 open).",
)

#: The allowance set used to cost a proposal: a proposal is a bare gross.
_NO_ALLOWANCES: Allowances = Allowances()


@dataclass(frozen=True, slots=True)
class ValuationInput:
    """One manager-entered profile and the band for its role."""

    total_experience_months: int
    relevant_experience_months: int
    skill_level: int
    education_level: EducationLevel
    band_min_gross_rial: int | None
    band_max_gross_rial: int | None
    rule_year: int = 1404
    days_in_month: int = 30
    tax_posture: TaxPosture = POSTURE_CONSERVATIVE_INTA


@dataclass(frozen=True, slots=True)
class ValuationResult:
    """The hashed proposal snapshot."""

    payload: dict[str, Any]
    calculation_hash: str


def _statutory_cost_of(
    gross_monthly_rial: int,
    inputs: ValuationInput,
    rule_set: StatutoryRuleSet,
) -> dict[str, Any]:
    """Cost one gross amount through the existing statutory engine."""
    payroll = compute_gross_to_net(
        PayrollInput(
            gross_monthly_rial=gross_monthly_rial,
            rule_year=inputs.rule_year,
            days_in_month=inputs.days_in_month,
            tax_posture=inputs.tax_posture,
            allowances=_NO_ALLOWANCES,
        ),
        rule_set=rule_set,
    )
    payload = payroll.payload

    return {
        "request": {
            "gross_monthly_rial": gross_monthly_rial,
            "rule_year": inputs.rule_year,
            "days_in_month": inputs.days_in_month,
            "tax_posture": payload["primary_tax_posture"],
            "allowances_rial": {
                "housing": 0,
                "grocery": 0,
                "marriage": 0,
                "child": 0,
                "continuous_attraction": 0,
            },
        },
        "calculation_hash": payroll.calculation_hash,
        "statutory_version": payload["statutory_version"],
        "rule_set_fingerprint": payload["rule_set_fingerprint"],
        "gross_monthly_rial": payload["bases"]["total_gross_rial"],
        "employee_sso_7pct_rial": payload["employee_deductions"]["employee_sso_7pct_rial"],
        "sso_insurable_ceiling_applied": payload["sso"]["sso_insurable_ceiling_applied"],
        "income_tax_rial": payload["employee_deductions"]["income_tax_rial"],
        "net_rial": payload["net_rial"],
        "monthly_sanavat_accrual_rial": payload["severance_sanavat"]["monthly_accrual_rial"],
        "monthly_eydi_accrual_rial": payload["eydi"]["monthly_accrual_rial"],
        "total_monthly_employer_cost_rial": payload["employer_cost"][
            "total_monthly_employer_cost_rial"
        ],
        "annual_ctc_12month_rial": payload["employer_cost"]["annual_ctc_12month_rial"],
        "rounding_residual_rial": payload["rounding_residual_rial"],
    }


def compute_compensation_proposal(
    inputs: ValuationInput,
    *,
    rule_set: StatutoryRuleSet | None = None,
) -> ValuationResult:
    """Score the profile, place it in the band, and cost the range.

    ``rule_set`` may be injected to pin an exact verified snapshot, exactly as
    the simulation path allows (A-11).  The loader is fail-closed, so a 1405
    request refuses here before any arithmetic.
    """
    active_rule_set = load_rule_set(inputs.rule_year) if rule_set is None else rule_set

    assessment = assess_profile(
        total_experience_months=inputs.total_experience_months,
        relevant_experience_months=inputs.relevant_experience_months,
        skill_level=inputs.skill_level,
        education_level=inputs.education_level,
    )
    proposal = propose_gross_range(
        score_exact=assessment.score_exact,
        band_min_gross_rial=inputs.band_min_gross_rial,
        band_max_gross_rial=inputs.band_max_gross_rial,
    )

    lower = _statutory_cost_of(proposal.range_low_rial, inputs, active_rule_set)
    point = _statutory_cost_of(proposal.proposed_gross_rial, inputs, active_rule_set)
    upper = _statutory_cost_of(proposal.range_high_rial, inputs, active_rule_set)

    minimum_wage_rial = active_rule_set.monthly_minimum_wage_rial(inputs.days_in_month)

    payload: dict[str, Any] = {
        "advisory": True,
        "statutory": False,
        "advisory_notes": list(_ADVISORY_NOTES),
        "model_version": VALUATION_MODEL_VERSION,
        "engine_version": ENGINE_VERSION,
        "proposal_version": f"{VALUATION_MODEL_VERSION}+{ENGINE_VERSION}",
        "rule_year_shamsi": active_rule_set.rule_year_shamsi,
        "rule_set_status": active_rule_set.rule_set_status,
        "statutory_version": active_rule_set.statutory_version,
        "rule_set_fingerprint": active_rule_set.fingerprint(),
        "profile": {
            "total_experience_months": assessment.total_experience_months,
            "relevant_experience_months": assessment.relevant_experience_months,
            "skill_level": assessment.skill_level,
            "education_level": assessment.education_level.value,
            "experience_separation_note": (
                "total and relevant experience are separate inputs; overlapping "
                "periods are never summed (AGENTS.md invariants 1 and 2)"
            ),
        },
        "score": {
            "score_exact": str(assessment.score_exact),
            "score_100": assessment.score_100,
            "weights": assessment.weights.as_mapping(),
            "weighted_contributions": {
                name: str(value) for name, value in assessment.contributions.items()
            },
        },
        "band": {
            "min_gross_rial": proposal.band_min_gross_rial,
            "max_gross_rial": proposal.band_max_gross_rial,
            "width_rial": proposal.band_width_rial,
            "source": "manager_supplied",
            "market_data_used": False,
        },
        "proposed": {
            "position_in_band": str(proposal.position),
            "gross_point_rial": proposal.proposed_gross_rial,
            "range_low_rial": proposal.range_low_rial,
            "range_high_rial": proposal.range_high_rial,
            "spread_fraction": str(RANGE_SPREAD_FRACTION),
            "spread_basis": ("half-width as a fraction of the band width, clamped to the band"),
        },
        "statutory_costing": {
            "lower_bound": lower,
            "point": point,
            "upper_bound": upper,
            "replay_note": (
                "each block's 'request' plus the statutory engine reproduces its "
                "figures through POST /api/v1/simulations/gross-to-net"
            ),
        },
        "statutory_context": {
            "monthly_minimum_wage_rial": minimum_wage_rial,
            "range_low_below_statutory_minimum": (proposal.range_low_rial < minimum_wage_rial),
            "applied_to_net": False,
            "applied_to_net_reason": (
                "DEC-013 remains open: the statutory floor is published for "
                "comparison and is never applied to a proposal"
            ),
        },
    }

    canonical = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return ValuationResult(payload=payload, calculation_hash=hashlib.sha256(canonical).hexdigest())
