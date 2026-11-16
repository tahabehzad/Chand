"""The advisory compensation proposal endpoint (ADR-009).

Authority
---------
``docs/adr/ADR-009-compensation-advisory-module.md`` directive 1; the error
and provenance envelope of ``docs/EXECUTION_PLAN.md`` §7.2.

Contract notes
--------------
* One endpoint: ``POST /api/v1/valuations/compensation-proposal``.
* The response is marked ``advisory: true`` / ``statutory: false``: the
  proposal is a decision aid for the manager, never an entitlement and never
  tax advice (DEC-009, DEC-013).
* The clock is read **here**, at the API boundary only; the proposal itself is
  a pure function of the request and the rule-set version (invariant 11).
* Refusals keep the single ``{"error": {"code", "detail"}}`` shape and never
  carry an amount or a personal attribute.
"""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.engines.errors import PayrollEngineError
from app.engines.valuation import EducationLevel
from app.schemas.payroll import ErrorResponse
from app.schemas.valuation import (
    CompensationProposalRequest,
    CompensationProposalResponse,
)
from app.services.valuation_service import ValuationInput, compute_compensation_proposal

router = APIRouter(prefix="/api/v1/valuations", tags=["valuations"])


def _error_response(status_code: int, code: str, detail: str) -> JSONResponse:
    """Build the single categorical error shape."""
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "detail": detail}},
    )


@router.post(
    "/compensation-proposal",
    response_model=CompensationProposalResponse,
    summary="Advisory compensation proposal from a manager-entered profile",
    responses={
        422: {
            "model": ErrorResponse,
            "description": "The request or the proposal was refused.",
        }
    },
)
async def compensation_proposal(
    payload: CompensationProposalRequest,
) -> CompensationProposalResponse | JSONResponse:
    """Score a documented profile and cost the range it implies.

    The manager supplies the money band; the module only positions the profile
    inside it. Both ends and the midpoint are costed by the verified 1404
    statutory engine, so the manager sees the real net and employer cost of
    the decision before making it.
    """
    inputs = ValuationInput(
        total_experience_months=payload.total_experience_months,
        relevant_experience_months=payload.relevant_experience_months,
        skill_level=payload.skill_level,
        education_level=EducationLevel(payload.education_level),
        band_min_gross_rial=payload.band_min_gross_rial,
        band_max_gross_rial=payload.band_max_gross_rial,
        rule_year=payload.rule_year,
        days_in_month=payload.days_in_month,
        tax_posture=payload.tax_posture,
    )
    try:
        result = compute_compensation_proposal(inputs)
    except PayrollEngineError as exc:
        # Every refusal in the taxonomy carries a stable code; the message
        # starts with the same code and never contains an amount.
        return _error_response(422, exc.code, str(exc))
    except ValueError as exc:
        return _error_response(422, "VALUATION_INVALID", str(exc))

    generated_at = datetime.now(UTC).isoformat()
    return CompensationProposalResponse(
        **result.payload,
        calculation_hash=result.calculation_hash,
        generated_at=generated_at,
    )
