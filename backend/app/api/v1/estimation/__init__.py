"""Salary estimation API endpoint (ADR-014 contract).

Authority
---------
``docs/adr/ADR-014-market-salary-reference-data-and-estimation.md`` §7 (published
contract and refusal shapes); ``docs/adr/ADR-013`` (advisory, never statutory).

Contract notes
--------------
* One POST endpoint: ``/api/v1/simulations/salary-estimation``.
* 200 — an estimate with full provenance (samples, sources, dates, confidence).
* 409 — a refusal: no job-family match, insufficient valid samples, or confidence
  below the publication floor.  **No figure is returned in a refusal.**
* 503 — the market-data store could not be read.  An unreachable database is an
  operational failure, never evidence that the market lacks data.
* 500 — an engine invariant failed; the estimate is withheld.
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.core.config import Settings, get_settings
from app.domain.salary_estimation.money_validation import EstimationInvariantError
from app.domain.salary_estimation.salary_estimator import InsufficientMarketDataError
from app.schemas.estimation import EstimateRequest, EstimateResponse
from app.services.estimation.service import (
    DataStoreUnavailableError,
    GeminiUnavailableError,
    build_repository,
    compute_estimate,
)

router = APIRouter(prefix="/api/v1/simulations", tags=["salary-estimation"])


def _error_response(
    status_code: int,
    code: str,
    detail: str,
    *,
    reason: str | None = None,
    counts: dict[str, int | None] | None = None,
) -> JSONResponse:
    """Build the one error shape used by this endpoint."""
    body: dict[str, object] = {"code": code, "detail": detail}
    if reason is not None:
        body["reason"] = reason
    if counts:
        body["counts"] = counts
    return JSONResponse(status_code=status_code, content={"error": body})


@router.post(
    "/salary-estimation",
    response_model=EstimateResponse,
    summary="Market salary estimation for the Iranian labour market (advisory)",
    responses={
        409: {"model": dict, "description": "Refusal — insufficient or unmatched data"},
        503: {"model": dict, "description": "Market-data store unavailable"},
    },
)
async def salary_estimation(
    payload: EstimateRequest, request: Request
) -> EstimateResponse | JSONResponse:
    """Estimate a monthly market salary for one candidate profile.

    The calculation is rule-based and cohort-based, not a model guess: the answer is
    the market's own p25/median/p75 over the validated sample, and every figure is
    traceable to its rows, sources and collection date.

    The legal minimum wage is a separate reference value, never a floor.
    """
    settings: Settings = getattr(request.app.state, "settings", None) or get_settings()
    try:
        return await compute_estimate(
            payload,
            repository_factory=lambda: build_repository(settings),
            settings=settings,
        )
    except InsufficientMarketDataError as exc:
        return _error_response(
            409,
            "ESTIMATION_INSUFFICIENT_DATA",
            exc.detail,
            reason=exc.reason,
            counts=exc.counts,
        )
    except GeminiUnavailableError as exc:
        return _error_response(503, "ESTIMATION_GEMINI_UNAVAILABLE", str(exc))
    except DataStoreUnavailableError as exc:
        return _error_response(503, "ESTIMATION_DATASTORE_UNAVAILABLE", str(exc))
    except EstimationInvariantError:
        return _error_response(
            500,
            "ESTIMATION_ENGINE_ERROR",
            "خطای داخلی در محاسبهٔ برآورد؛ عددی منتشر نشد.",
        )
    except ValueError as exc:
        return _error_response(422, "ESTIMATION_INPUT_INVALID", str(exc))


__all__ = ("router",)
