"""Schemas for Career Document and Evidence Verification (ADR-013 / ADR-014).

Authority
---------
``docs/AI_ANALYSIS_SPEC.md`` §2, §3 (assisted extraction, forensic anomaly is not
a fraud verdict; route it to a human; salary computation uses market data logic);
``AGENTS.md`` §2 Domain invariants 1, 4, 7.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ForensicIndicator(BaseModel):
    """One forensic integrity and authenticity check."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(description="Forensic check title (Persian)")
    status: Literal["pass", "warning", "fail", "info"] = Field(
        description="Check status"
    )
    detail: str = Field(description="Forensic detail and evidence summary (Persian)")


class ExtractedDocumentFacts(BaseModel):
    """Document facts extracted from OCR / vision analysis."""

    model_config = ConfigDict(extra="forbid")

    document_type: str = Field(
        description="Document type key: sso_record, payslip, academic_degree, certificate, contract, general"
    )
    document_type_fa: str = Field(description="Document type label in Persian")
    issuing_organization: str | None = Field(default=None, description="Issuing organization")
    document_number: str | None = Field(default=None, description="Official tracking or document ID")
    issue_date_shamsi: str | None = Field(default=None, description="Shamsi issue date")
    verified_experience_years: int | None = Field(
        default=None, description="Verified experience years from official records"
    )
    verified_last_salary_rial: int | None = Field(
        default=None, description="Verified gross salary from payslip/contract in Rial"
    )
    verified_education_level: str | None = Field(
        default=None, description="Verified academic degree level"
    )
    verified_skills: list[str] = Field(default_factory=list, description="Verified competencies")
    employer_names: list[str] = Field(
        default_factory=list, description="Previous registered employer workshop names"
    )


class SalaryImpact(BaseModel):
    """Document evidence impact on compensation and positioning."""

    model_config = ConfigDict(extra="forbid")

    confidence_boost_percent: int = Field(
        description="Confidence boost percentage e.g. 15%"
    )
    market_quartile_recommendation: Literal["upper_half", "top_quartile", "median", "adjusted"] = Field(
        description="Market quartile recommendation"
    )
    recommended_experience_years: int | None = Field(
        default=None, description="Recommended experience years"
    )
    discrepancy_detected: bool = Field(
        default=False, description="Whether discrepancy with claimed candidate profile was detected"
    )
    discrepancy_message_fa: str | None = Field(
        default=None, description="Discrepancy explanation in Persian for hiring manager"
    )
    explanation_fa: str = Field(
        description="Strategic explanation of document evidence on salary positioning"
    )


class DocumentAnalysisRequest(BaseModel):
    """Payload to submit a career document for forensic authenticity analysis."""

    model_config = ConfigDict(extra="forbid")

    file_base64: str = Field(description="Base64 encoded binary file data")
    file_name: str = Field(description="Uploaded document filename")
    mime_type: str = Field(
        default="image/jpeg", description="MIME type (image/jpeg, image/png, application/pdf)"
    )
    claimed_job_title: str | None = Field(default=None, description="Candidate claimed job title")
    claimed_experience_years: int | None = Field(
        default=None, ge=0, description="Candidate claimed experience in years"
    )
    claimed_education: str | None = Field(default=None, description="Candidate claimed education")
    gemini_api_key: str | None = Field(
        default=None, description="Optional user Gemini API key for multimodal vision"
    )


class DocumentAnalysisResponse(BaseModel):
    """Verified authenticity verdict, extracted facts, and salary impact."""

    model_config = ConfigDict(extra="forbid")

    authenticity_score: float = Field(
        ge=0.0, le=1.0, description="Authenticity confidence score (0.0 to 1.0)"
    )
    authenticity_verdict: Literal["verified", "needs_human_review", "inconclusive", "suspicious"] = Field(
        description="Authenticity verdict status"
    )
    authenticity_verdict_fa: str = Field(description="Authenticity verdict in Persian")
    forensic_indicators: list[ForensicIndicator] = Field(
        description="List of forensic integrity markers"
    )
    extracted_facts: ExtractedDocumentFacts = Field(description="Extracted document facts")
    salary_impact: SalaryImpact = Field(description="Salary impact and quartile recommendations")
    analysis_timestamp: str = Field(description="ISO-8601 analysis timestamp")
