"""Unit tests for Career Document Analysis service and endpoint (ADR-013 / ADR-014).

Authority
---------
``docs/AI_ANALYSIS_SPEC.md`` §2, §3; ``AGENTS.md`` §2 Domain invariants 1, 4, 7.
"""

from __future__ import annotations

import base64
import json
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient, Response

from app.core.config import Settings, get_settings
from app.main import create_app
from app.schemas.document_analysis import DocumentAnalysisRequest
from app.services.estimation.document_analyzer import (
    CareerDocumentAnalyzer,
    DocumentAnalysisError,
)

_SAMPLE_PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
)


@pytest.fixture
def dummy_settings() -> Settings:
    return get_settings()


@pytest.mark.asyncio
async def test_sso_preset_verification(dummy_settings: Settings) -> None:
    analyzer = CareerDocumentAnalyzer()
    req = DocumentAnalysisRequest(
        file_base64=_SAMPLE_PNG_BASE64,
        file_name="sso_insurance_record.png",
        mime_type="image/png",
        claimed_job_title="توسعه‌دهنده پایتون",
        claimed_experience_years=4,
        claimed_education="کارشناسی",
    )
    result = await analyzer.analyze(req, settings=dummy_settings)
    assert result.authenticity_score >= 0.90
    assert result.authenticity_verdict == "verified"
    assert "تأمین اجتماعی" in result.extracted_facts.document_type_fa
    assert result.extracted_facts.verified_experience_years == 4
    assert result.salary_impact.confidence_boost_percent >= 15
    assert not result.salary_impact.discrepancy_detected
    assert len(result.forensic_indicators) >= 3


@pytest.mark.asyncio
async def test_sso_preset_discrepancy_detection(dummy_settings: Settings) -> None:
    analyzer = CareerDocumentAnalyzer()
    # Claimed 7 years while SSO only proves 4 years
    req = DocumentAnalysisRequest(
        file_base64=f"data:image/png;base64,{_SAMPLE_PNG_BASE64}",
        file_name="sso_tamin_sabegheh.png",
        mime_type="image/png",
        claimed_job_title="مدیر فنی",
        claimed_experience_years=7,
        claimed_education="کارشناسی ارشد",
    )
    result = await analyzer.analyze(req, settings=dummy_settings)
    assert result.authenticity_verdict == "needs_human_review"
    assert result.salary_impact.discrepancy_detected is True
    assert result.salary_impact.discrepancy_message_fa is not None
    assert "4 سال" in result.salary_impact.discrepancy_message_fa or "۴ سال" in result.salary_impact.discrepancy_message_fa
    assert "7 سال" in result.salary_impact.discrepancy_message_fa or "۷ سال" in result.salary_impact.discrepancy_message_fa


@pytest.mark.asyncio
async def test_payslip_preset_verification(dummy_settings: Settings) -> None:
    analyzer = CareerDocumentAnalyzer()
    req = DocumentAnalysisRequest(
        file_base64=_SAMPLE_PNG_BASE64,
        file_name="payslip_salary_slip.pdf",
        mime_type="application/pdf",
        claimed_job_title="مهندس نرم‌افزار",
        claimed_experience_years=3,
    )
    result = await analyzer.analyze(req, settings=dummy_settings)
    assert result.authenticity_verdict == "verified"
    assert result.extracted_facts.document_type == "payslip"
    assert result.extracted_facts.verified_last_salary_rial == 420000000
    assert result.salary_impact.confidence_boost_percent == 15


@pytest.mark.asyncio
async def test_academic_degree_preset_verification(dummy_settings: Settings) -> None:
    analyzer = CareerDocumentAnalyzer()
    req = DocumentAnalysisRequest(
        file_base64=_SAMPLE_PNG_BASE64,
        file_name="university_degree.jpg",
        mime_type="image/jpeg",
        claimed_job_title="دانشمند داده",
        claimed_education="کارشناسی ارشد کامپیوتر",
    )
    result = await analyzer.analyze(req, settings=dummy_settings)
    assert result.authenticity_verdict == "verified"
    assert result.extracted_facts.document_type == "academic_degree"
    assert result.extracted_facts.verified_education_level is not None
    assert "دانشگاه تهران" in (result.extracted_facts.issuing_organization or "")


@pytest.mark.asyncio
async def test_general_file_fallback(dummy_settings: Settings) -> None:
    analyzer = CareerDocumentAnalyzer()
    req = DocumentAnalysisRequest(
        file_base64=_SAMPLE_PNG_BASE64,
        file_name="my_certificate_scan.png",
        mime_type="image/png",
        claimed_job_title="طراح رابط کاربری",
        claimed_experience_years=3,
    )
    result = await analyzer.analyze(req, settings=dummy_settings)
    assert result.authenticity_score > 0.8
    assert result.extracted_facts.document_type == "general"
    assert result.salary_impact.confidence_boost_percent > 0


@pytest.mark.asyncio
async def test_invalid_base64_raises_error() -> None:
    analyzer = CareerDocumentAnalyzer()
    req = DocumentAnalysisRequest(
        file_base64="invalid_base64_!@#$%",
        file_name="corrupt.png",
        mime_type="image/png",
    )
    with pytest.raises(DocumentAnalysisError, match="Base64"):
        await analyzer.analyze(req)


@pytest.mark.asyncio
async def test_gemini_vision_mock_success(dummy_settings: Settings) -> None:
    mock_payload = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps(
                                {
                                    "authenticity_score": 0.97,
                                    "authenticity_verdict": "verified",
                                    "authenticity_verdict_fa": "تأییدشده و رسمی",
                                    "forensic_indicators": [
                                        {
                                            "name": "مهر و امضای دیجیتال",
                                            "status": "pass",
                                            "detail": "بارکد و مهر دیجیتال سازمانی با موفقیت ردیابی شد.",
                                        }
                                    ],
                                    "extracted_facts": {
                                        "document_type": "sso_record",
                                        "document_type_fa": "سابقه بیمه رسمی",
                                        "issuing_organization": "سازمان تامین اجتماعی",
                                        "document_number": "SSO-9912",
                                        "issue_date_shamsi": "1403/01/10",
                                        "verified_experience_years": 5,
                                        "verified_last_salary_rial": 400000000,
                                        "verified_education_level": None,
                                        "verified_skills": ["Python", "FastAPI"],
                                        "employer_names": ["شرکت الف"],
                                    },
                                    "salary_impact": {
                                        "confidence_boost_percent": 18,
                                        "market_quartile_recommendation": "upper_half",
                                        "recommended_experience_years": 5,
                                        "discrepancy_detected": False,
                                        "discrepancy_message_fa": None,
                                        "explanation_fa": "۵ سال سابقه کار قطعی احراز شد.",
                                    },
                                }
                            )
                        }
                    ]
                }
            }
        ]
    }

    mock_client = AsyncMock(spec=AsyncClient)
    mock_resp = Response(200, json=mock_payload)
    mock_client.post.return_value = mock_resp

    analyzer = CareerDocumentAnalyzer(http_client=mock_client)
    req = DocumentAnalysisRequest(
        file_base64=_SAMPLE_PNG_BASE64,
        file_name="real_scan.png",
        mime_type="image/png",
        gemini_api_key="valid_test_key",
    )
    result = await analyzer.analyze(req, settings=dummy_settings)
    assert result.authenticity_score == 0.97
    assert result.extracted_facts.verified_experience_years == 5
    assert result.salary_impact.confidence_boost_percent == 18


@pytest.mark.asyncio
async def test_document_analysis_endpoint_success() -> None:
    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        payload = {
            "file_base64": _SAMPLE_PNG_BASE64,
            "file_name": "sso_record_test.png",
            "mime_type": "image/png",
            "claimed_job_title": "برنامه‌نویس بک‌اند",
            "claimed_experience_years": 4,
        }
        resp = await client.post("/api/v1/simulations/document-analysis", json=payload)
        assert resp.status_code == 200
        body = resp.json()
        assert "authenticity_score" in body
        assert "authenticity_verdict" in body
        assert "forensic_indicators" in body
        assert "extracted_facts" in body
        assert "salary_impact" in body
        assert body["extracted_facts"]["verified_experience_years"] == 4


@pytest.mark.asyncio
async def test_document_analysis_endpoint_invalid_base64() -> None:
    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        payload = {
            "file_base64": "not_valid_b64!",
            "file_name": "bad.png",
            "mime_type": "image/png",
        }
        resp = await client.post("/api/v1/simulations/document-analysis", json=payload)
        assert resp.status_code == 400
        body = resp.json()
        assert body["error"]["code"] == "DOCUMENT_ANALYSIS_INVALID_PAYLOAD"
