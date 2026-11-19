"""Document and Career Evidence Analysis Endpoint (ADR-013 / ADR-014).

Authority
---------
``docs/AI_ANALYSIS_SPEC.md`` §2, §3; ``AGENTS.md`` §2 Domain invariants 1, 4, 7.

Contract
--------
* POST ``/api/v1/simulations/document-analysis``
* 200 — verified authenticity, forensic indicators, extracted facts, and salary impact.
* 400 — malformed payload or base64 structure.
* 500 — internal processing error.
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.core.config import Settings, get_settings
from app.schemas.document_analysis import (
    DocumentAnalysisRequest,
    DocumentAnalysisResponse,
)
from app.services.estimation.document_analyzer import (
    CareerDocumentAnalyzer,
    DocumentAnalysisError,
)

router = APIRouter(prefix="/api/v1/simulations", tags=["document-analysis"])


def _error_response(
    status_code: int,
    code: str,
    detail: str,
) -> JSONResponse:
    """Standard error shape."""
    return JSONResponse(status_code=status_code, content={"error": {"code": code, "detail": detail}})


@router.post(
    "/document-analysis",
    response_model=DocumentAnalysisResponse,
    summary="Career document forensic verification and salary impact analysis",
    responses={
        400: {"model": dict, "description": "Invalid base64 payload or file error"},
        500: {"model": dict, "description": "Processing error"},
    },
)
async def analyze_career_document(
    payload: DocumentAnalysisRequest,
    request: Request,
) -> DocumentAnalysisResponse | JSONResponse:
    """Analyze career documents (SSO record, payslip, degree) for authenticity and salary impact.

    Uses multimodal Gemini Vision when an API key is available, or deterministic
    forensic verification for standard presets and offline evaluation.
    """
    settings: Settings = getattr(request.app.state, "settings", None) or get_settings()
    analyzer = CareerDocumentAnalyzer()
    try:
        return await analyzer.analyze(payload, settings=settings)
    except DocumentAnalysisError as exc:
        return _error_response(400, "DOCUMENT_ANALYSIS_INVALID_PAYLOAD", str(exc))
    except Exception as exc:
        return _error_response(
            500,
            "DOCUMENT_ANALYSIS_FAILED",
            f"خطای غیرمنتظره در تحلیل سند: {exc}",
        )
