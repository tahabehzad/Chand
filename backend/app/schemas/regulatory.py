"""Schemas for dynamic regulatory sync API contracts."""

from __future__ import annotations

from pydantic import BaseModel, Field

__all__ = (
    "RegulatoryStatusResponse",
    "RegulatorySyncRequest",
    "RegulatorySyncResponse",
)


class RegulatoryStatusResponse(BaseModel):
    """Current statutory active rule version and monitoring status."""

    active_version: str = Field(
        ...,
        description="Active statutory rule-set version identifier (e.g. '1404.1')",
        examples=["1404.1"],
    )
    year_shamsi: int = Field(
        ...,
        description="Active statutory Solar-Hijri year",
        examples=[1404],
    )
    effective_date: str = Field(
        ...,
        description="Statutory effective date string",
        examples=["1404-01-01"],
    )
    last_synced_at: str = Field(
        ...,
        description="ISO 8601 timestamp of the most recent synchronization check",
    )
    sources: list[str] = Field(
        ...,
        description="Official governmental sources monitored for statutory updates",
    )
    source_urls: list[str] = Field(
        ...,
        description="Verified URLs of official portals",
    )


class RegulatorySyncRequest(BaseModel):
    """Optional parameters for triggering a regulatory synchronization."""

    gemini_api_key: str | None = Field(
        default=None,
        max_length=200,
        description="Optional Gemini API key with Google Search Grounding access",
    )
    force: bool = Field(
        default=False,
        description="Force creating a new version even when parameters match active ones",
    )


class RegulatorySyncResponse(BaseModel):
    """Result payload of a regulatory synchronization run."""

    status: str = Field(
        ...,
        description="Execution status ('success', 'no_change', 'refused', 'unavailable')",
    )
    previous_version: str = Field(..., description="Active version prior to sync")
    active_version: str = Field(..., description="Active version following sync")
    year_shamsi: int = Field(..., description="Active statutory year")
    has_changes: bool = Field(
        ...,
        description="Whether official circular changes were detected and versioned",
    )
    message: str = Field(..., description="Human-readable status summary in Persian")
    last_synced_at: str = Field(..., description="ISO 8601 timestamp of execution")
    source_urls: list[str] = Field(
        default_factory=list,
        description="Verified official URLs cited during grounding",
    )
