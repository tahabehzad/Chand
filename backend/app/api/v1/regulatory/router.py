"""Regulatory sync API endpoints.

Authority
---------
ADR-007; ADR-008; ADR-014; ``financial-data-integrity``;
``AGENTS.md`` §2 Domain & Financial invariants.

Endpoints
---------
* GET ``/api/v1/regulatory/status``: Returns active statutory version and monitored sources.
* POST ``/api/v1/regulatory/sync``: Triggers sync with Iranian official sources and persists new version if changes exist.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header
from fastapi.responses import JSONResponse

from app.schemas.regulatory import (
    RegulatoryStatusResponse,
    RegulatorySyncRequest,
    RegulatorySyncResponse,
)
from app.services.regulatory.sync_service import (
    RegulatorySyncService,
    get_regulatory_sync_service,
)

__all__ = ("router",)

router = APIRouter(prefix="/api/v1/regulatory", tags=["regulatory"])

SyncServiceDep = Annotated[RegulatorySyncService, Depends(get_regulatory_sync_service)]
GeminiHeaderDep = Annotated[str | None, Header(alias="X-Gemini-API-Key")]


@router.get(
    "/status",
    response_model=RegulatoryStatusResponse,
    summary="Get active statutory version and monitored official sources status",
)
async def get_regulatory_status(
    sync_service: SyncServiceDep,
) -> RegulatoryStatusResponse:
    """Return the active statutory rule-set version and governmental sources status."""
    status_data = await sync_service.get_status()
    return RegulatoryStatusResponse(
        active_version=str(status_data["active_version"]),
        year_shamsi=int(status_data["year_shamsi"]),
        effective_date=str(status_data["effective_date"]),
        last_synced_at=str(status_data["last_synced_at"]),
        sources=list(status_data["sources"]),
        source_urls=list(status_data["source_urls"]),
    )


@router.post(
    "/sync",
    response_model=RegulatorySyncResponse,
    summary="Trigger regulatory synchronization against verified official sources",
)
async def sync_regulatory_rules(
    sync_service: SyncServiceDep,
    request: RegulatorySyncRequest | None = None,
    x_gemini_api_key: GeminiHeaderDep = None,
) -> RegulatorySyncResponse | JSONResponse:
    """Synchronize statutory payroll rules from verified Iranian portals."""
    api_key: str | None = None
    force = False
    if request is not None:
        api_key = request.gemini_api_key
        force = request.force
    if not api_key and x_gemini_api_key:
        api_key = x_gemini_api_key

    outcome = await sync_service.sync(api_key=api_key, force=force)

    return RegulatorySyncResponse(
        status=outcome.status,
        previous_version=outcome.previous_version,
        active_version=outcome.active_version,
        year_shamsi=outcome.year_shamsi,
        has_changes=outcome.has_changes,
        message=outcome.message,
        last_synced_at=outcome.last_synced_at,
        source_urls=outcome.source_urls,
    )
