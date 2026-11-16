"""The minimal gross-to-net simulation endpoint (ADR-008 v1 scope).

Authority
---------
ADR-008 — the single minimal API surface: one endpoint, no UI, both Article
137 postures in the response, ``conservative_inta`` primary.
The clock is injected **here**, at the API boundary only; the calculation
path never reads it.
Related:
    WBS P1-T19 (Simulation API, minimal v1 scope).

Contract notes
--------------
* Domain failures map to one stable error shape ``{"error": {"code", …}}``
  that never carries a monetary amount, a secret or a raw traceback.
* A request for an unverified rule year (1405) is refused with the
  loader's fail-closed code — no coercion, no fallback.
"""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.engines.bases import Allowances
from app.engines.errors import PayrollEngineError, PayrollInputError
from app.schemas.payroll import (
    AllowancesInput,
    ErrorResponse,
    GrossToNetRequest,
    PayrollResponse,
)
from app.services.payroll_service import PayrollInput, compute_gross_to_net

router = APIRouter(prefix="/api/v1/simulations", tags=["simulations"])


def _error_response(status_code: int, code: str, detail: str) -> JSONResponse:
    """Build the single categorical error shape."""
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "detail": detail}},
    )


def _to_payroll_input(payload: GrossToNetRequest) -> PayrollInput:
    """Map the validated request contract onto the service input."""
    schema_allowances = AllowancesInput() if payload.allowances is None else payload.allowances
    allowances = Allowances(
        housing_rial=schema_allowances.housing,
        grocery_rial=schema_allowances.grocery,
        marriage_rial=schema_allowances.marriage,
        child_rial=schema_allowances.child,
        continuous_attraction_rial=schema_allowances.continuous_attraction,
    )
    return PayrollInput(
        gross_monthly_rial=payload.gross_monthly_rial,
        rule_year=payload.rule_year,
        days_in_month=payload.days_in_month,
        tax_posture=payload.tax_posture,
        allowances=allowances,
        overtime_hours=payload.overtime_hours,
        night_hours=payload.night_hours,
        continuous_attraction_taxable=payload.continuous_attraction_taxable,
        probation_months=payload.probation_months,
        tenure_months=payload.tenure_months,
        accumulated_unused_leave_days=payload.accumulated_unused_leave_days,
        probation_days_worked=payload.probation_days_worked,
        termination_scenario=payload.termination_scenario,
        recognised_service_years=payload.recognised_service_years,
    )


@router.post(
    "/gross-to-net",
    response_model=PayrollResponse,
    summary="Gross-to-net payroll simulation (1404 verified baseline)",
    responses={
        # The endpoint's documented refusal shape. Declaring it here replaces
        # FastAPI's default 422 body, so the OpenAPI contract and the real
        # response agree: a request-validation refusal returns the same
        # `{"error": {"code", "detail"}}` envelope as every domain refusal.
        422: {
            "model": ErrorResponse,
            "description": "The request or the calculation was refused.",
        }
    },
)
async def gross_to_net(payload: GrossToNetRequest) -> PayrollResponse | JSONResponse:
    """Run the statutory gross-to-net calculation for one month.

    Both Article 137 postures are always computed and returned; the primary
    posture's net is the headline ``net_rial``.  The verified 1404 rule set
    is the only loadable baseline.
    """
    inputs = _to_payroll_input(payload)
    try:
        result = compute_gross_to_net(inputs)
    except PayrollInputError as exc:
        return _error_response(
            422, getattr(exc, "code", "PAYROLL_INPUT_INVALID"), str(exc)
        )
    except PayrollEngineError as exc:
        return _error_response(
            422, getattr(exc, "code", "PAYROLL_ENGINE_ERROR"), str(exc)
        )
    except ValueError as exc:
        # Engine input-contract violations carry stable categorical codes
        # and never amounts.
        return _error_response(422, "PAYROLL_INPUT_INVALID", str(exc))
    generated_at = datetime.now(UTC).isoformat()
    return PayrollResponse(
        **result.payload,
        calculation_hash=result.calculation_hash,
        generated_at=generated_at,
    )
