"""API route for Total Cost to Employer (CTC) breakdown.

Authority
---------
``docs/SALARY_ESTIMATION_SPEC.md``; ``docs/PISH_HESABDARI_HOLY_BIBLE.md`` §2.3;
``REMEDIATED_TECHNICAL_SPECIFICATION_V2.md`` Module 6; ``AGENTS.md`` §2.

Contract notes
--------------
* Endpoint: POST ``/api/v1/simulations/salary-ctc-breakdown``
* Reuses existing calculation engines without modifying or reinventing statutory math:
  - SSO: ``app.engines.sso.compute_sso``
  - Income Tax: ``app.engines.tax.compute_tax_for_posture`` (progressive ladder)
  - Severance: ``app.engines.severance.compute_monthly_severance_accrual``
  - Eydi: ``app.engines.eydi.compute_eydi``
  - CTC: ``app.engines.ctc.compute_employer_cost``
* High-precision Decimal arithmetic (prec=34, ROUND_HALF_UP); no binary floats.
* Canonical SHA-256 calculation hash ensuring deterministic auditability.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, localcontext
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.engines import ENGINE_VERSION
from app.engines.ctc import compute_employer_cost
from app.engines.errors import PayrollEngineError
from app.engines.eydi import compute_eydi
from app.engines.money import MONEY_PRECISION
from app.engines.rules import load_rule_set, rule_set_from_record
from app.engines.severance import compute_monthly_severance_accrual
from app.engines.sso import compute_sso
from app.engines.tax import POSTURE_CONSERVATIVE_INTA, compute_tax_for_posture
from app.repositories.statutory_repository import get_default_statutory_repository
from app.schemas.ctc import (
    CtcBreakdownRequest,
    CtcBreakdownResponse,
    CtcDeductions,
    CtcEmployerCosts,
)

__all__ = ("router",)

router = APIRouter(prefix="/api/v1/simulations", tags=["salary-estimation"])


def _error_response(status_code: int, code: str, detail: str) -> JSONResponse:
    """Produce the standard categorical JSON refusal envelope."""
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "detail": detail}},
    )


@router.post(
    "/salary-ctc-breakdown",
    response_model=CtcBreakdownResponse,
    summary="Compute monthly and annual Total Cost to Employer (CTC) and net pay",
    responses={
        422: {
            "model": dict,
            "description": "Validation failure or unverified statutory rule set",
        }
    },
)
async def salary_ctc_breakdown(
    payload: CtcBreakdownRequest,
) -> CtcBreakdownResponse | JSONResponse:
    """Calculate the exact Iranian labor cost breakdown for a given gross salary.

    Itemizes:
    - Employee deductions: SSO (7% capped), progressive income tax (conservative INTA)
    - Take-home net salary
    - Employer overhead: SSO (20% capped), unemployment insurance (3% capped),
      monthly severance accrual (1/12), and monthly bonus accrual (1/12 annual Eydi)
    - Total monthly and annual Cost to Employer (CTC)
    """
    try:
        repo = get_default_statutory_repository()
        record = await repo.get_active_rule_set_record(payload.year)
        if record is not None:
            rule_set = rule_set_from_record(record)
        else:
            rule_set = load_rule_set(payload.year)
    except PayrollEngineError as exc:
        return _error_response(422, exc.code, str(exc))

    with localcontext() as context:
        context.prec = MONEY_PRECISION
        context.rounding = ROUND_HALF_UP

        gross_rial = payload.gross_salary_rial

        # 1. Social Security Organization (SSO) contribution
        sso_result = compute_sso(
            total_earnings_rial=gross_rial,
            rule_set=rule_set,
            days_in_month=payload.month_days,
        )

        # 2. Progressive income tax (conservative INTA reading: 2/7 SSO deduction)
        tax_result = compute_tax_for_posture(
            total_gross_rial=gross_rial,
            employee_sso_exact=sso_result.employee_share_exact,
            welfare_total_rial=0,
            non_welfare_exempt_rial=0,
            posture=POSTURE_CONSERVATIVE_INTA,
            rule_set=rule_set,
        )

        # 3. Monthly severance (Sanavat) accrual
        severance_result = compute_monthly_severance_accrual(mozd_e_saabet_rial=gross_rial)

        # 4. Annual bonus (Eydi) accrual
        eydi_result = compute_eydi(mozd_e_saabet_rial=gross_rial, rule_set=rule_set)

        # 5. Employer total cost synthesis
        employer_result = compute_employer_cost(
            total_gross_rial=gross_rial,
            employer_sso_rial=sso_result.employer_share_rial,
            unemployment_rial=sso_result.unemployment_share_rial,
            severance_accrual_rial=severance_result.monthly_accrual_rial,
            eydi_accrual_rial=eydi_result.monthly_accrual_rial,
        )

    employee_sso = sso_result.employee_share_rial
    income_tax = tax_result.tax_rial
    total_deductions = employee_sso + income_tax
    net_salary = max(0, gross_rial - total_deductions)

    employer_sso = sso_result.employer_share_rial
    unemployment = sso_result.unemployment_share_rial
    severance_monthly = severance_result.monthly_accrual_rial
    eydi_monthly = eydi_result.monthly_accrual_rial
    total_employer_costs = employer_sso + unemployment + severance_monthly + eydi_monthly

    deductions = CtcDeductions(
        employee_sso_rial=employee_sso,
        income_tax_rial=income_tax,
        total_deductions_rial=total_deductions,
    )

    employer_costs = CtcEmployerCosts(
        employer_sso_rial=employer_sso,
        unemployment_rial=unemployment,
        monthly_severance_rial=severance_monthly,
        monthly_eydi_rial=eydi_monthly,
        total_employer_costs_rial=total_employer_costs,
    )

    generated_at = datetime.now(UTC).isoformat()

    # Build canonical payload for deterministic calculation hash (pure function of inputs and results)
    canonical_dict: dict[str, Any] = {
        "annual_cost_to_employer_rial": employer_result.annual_ctc_rial,
        "deductions": {
            "employee_sso_rial": employee_sso,
            "income_tax_rial": income_tax,
            "total_deductions_rial": total_deductions,
        },
        "employer_costs": {
            "employer_sso_rial": employer_sso,
            "monthly_eydi_rial": eydi_monthly,
            "monthly_severance_rial": severance_monthly,
            "total_employer_costs_rial": total_employer_costs,
            "unemployment_rial": unemployment,
        },
        "engine_version": ENGINE_VERSION,
        "gross_salary_rial": gross_rial,
        "net_salary_rial": net_salary,
        "rule_version": rule_set.statutory_version,
        "total_cost_to_employer_rial": employer_result.total_monthly_rial,
    }

    canonical_bytes = json.dumps(
        canonical_dict,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    calculation_hash = hashlib.sha256(canonical_bytes).hexdigest()

    return CtcBreakdownResponse(
        gross_salary_rial=gross_rial,
        net_salary_rial=net_salary,
        deductions=deductions,
        employer_costs=employer_costs,
        total_cost_to_employer_rial=employer_result.total_monthly_rial,
        annual_cost_to_employer_rial=employer_result.annual_ctc_rial,
        rule_version=rule_set.statutory_version,
        engine_version=ENGINE_VERSION,
        calculation_hash=calculation_hash,
        generated_at=generated_at,
    )
