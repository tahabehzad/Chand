"""Persisted work-profile API contract.

Authority: ADR-012; WORK_PROFILE_PAYROLL.
Related: P3-T07; existing manager identity and payroll schema.
Scope: nullable profile facts; no automatic merging or experience scoring.
"""

from __future__ import annotations

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.payroll import GrossToNetRequest


class WorkProfileRequest(BaseModel):
    """One explicitly selected employee's work information; null remains unknown."""

    model_config = ConfigDict(extra="forbid", strict=True)
    job_title: str = Field(default="", max_length=120)
    education: str = Field(default="", max_length=40)
    education_subject: str = Field(default="", max_length=120)
    qualifications: str = Field(default="", max_length=4000)
    total_experience_months: int | None = Field(default=None, ge=0, le=1200)
    relevant_experience_months: int | None = Field(default=None, ge=0, le=1200)
    insurance_months: int | None = Field(default=None, ge=0, le=1200)
    employer_tenure_months: int | None = Field(default=None, ge=0, le=1200)
    recognised_seniority_months: int | None = Field(default=None, ge=0, le=1200)
    daily_hours: str | None = Field(default=None, pattern=r"^[0-9]{1,2}(\.[0-9]{1,8})?$")
    schedule_period: Literal["weekly", "monthly"] = "weekly"
    weekly_days: int | None = Field(default=None, ge=1, le=7)
    monthly_paid_days: int | None = Field(default=None, ge=1, le=31)
    workshop_type: Literal["unclassified", "classified"] = "unclassified"
    documented_daily_seniority_rial: int | None = Field(default=None, ge=0, le=10_000_000_000)

    @model_validator(mode="after")
    def validate_dimensions(self) -> Self:
        if (self.total_experience_months is not None and self.relevant_experience_months is not None
                and self.relevant_experience_months > self.total_experience_months):
            raise ValueError("Relevant experience cannot exceed total experience.")
        if self.schedule_period == "weekly" and self.monthly_paid_days is not None:
            raise ValueError("Monthly paid days cannot accompany a weekly schedule.")
        if self.schedule_period == "monthly" and self.weekly_days is not None:
            raise ValueError("Weekly days cannot accompany a monthly schedule.")
        return self


class WorkCalculationRequest(BaseModel):
    """Full-time monthly baseline; the server loads the saved work profile."""

    model_config = ConfigDict(extra="forbid")
    payroll: GrossToNetRequest


class WorkProfileSaveRequest(BaseModel):
    """Optimistic revision prevents silent overwrite by another tab."""

    model_config = ConfigDict(extra="forbid", strict=True)
    profile: WorkProfileRequest
    expected_revision: int = Field(ge=0)
