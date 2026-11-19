"""End-to-end tests for live-search-first Gemini salary estimation with DB fallback.

Authority: ADR-014; AGENTS.md §2 Financial invariants 7-12.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.core.config import Settings
from app.main import create_app
from app.services.estimation.gemini_service import GeminiUnavailableError

ENDPOINT = "/api/v1/simulations/salary-estimation"

VALID_REQUEST_PAYLOAD: dict[str, Any] = {
    "job_title": "توسعه‌دهنده فرانت‌اند",
    "experience_years": 3,
    "seniority_level": "mid",
    "employment_type": "full_time",
    "city": "تهران",
    "province": "تهران",
    "work_condition": "on_site",
    "job_description": "توسعه فرانت‌اند با React و TypeScript",
    "currency_unit": "toman",
    "skills": [{"name": "React", "level": "intermediate"}],
    "gemini_api_key": "test_gemini_live_key",
}

MOCK_GEMINI_API_RESPONSE: dict[str, Any] = {
    "candidates": [
        {
            "content": {
                "parts": [
                    {
                        "text": """{
  "found_data": true,
  "refusal_reason": null,
  "observations": [
    {
      "job_title_reported": "توسعه‌دهنده React",
      "source_name": "Jobinja",
      "source_url": "https://jobinja.ir/123",
      "city": "تهران",
      "seniority_level": "mid",
      "amount_rial": 480000000,
      "period": "monthly",
      "license_status": "manual_verified"
    },
    {
      "job_title_reported": "برنامه‌نویس فرانت‌اند",
      "source_name": "Jobvision",
      "source_url": "https://jobvision.ir/456",
      "city": "تهران",
      "seniority_level": "mid",
      "amount_rial": 520000000,
      "period": "monthly",
      "license_status": "manual_verified"
    }
  ],
  "aggregates": [],
  "factors_influence": ["تسلط بر React", "شهر تهران"],
  "factors_notes": ["داده‌های زنده زمستان ۱۴۰۳"]
}"""
                    }
                ]
            },
            "groundingMetadata": {
                "groundingChunks": [
                    {
                        "web": {
                            "uri": "https://jobinja.ir/salaries",
                            "title": "جابینجا گزارش حقوق",
                        }
                    }
                ]
            },
        }
    ]
}


@pytest.fixture
def sample_client() -> Iterator[TestClient]:
    """Client with sample repository enabled."""
    application = create_app(Settings(estimation_allow_sample_data=True))
    with TestClient(application) as client:
        yield client


@pytest.fixture
def bare_client() -> Iterator[TestClient]:
    """Client with no database and sample data disabled."""
    application = create_app(Settings(database_url=SecretStr(""), estimation_allow_sample_data=False))
    with TestClient(application) as client:
        yield client


class TestGeminiLiveFirstFlow:
    def test_gemini_live_success_returns_live_mode(self, sample_client: TestClient) -> None:
        with patch(
            "app.services.estimation.gemini_service.GeminiLiveSalaryService.call_gemini",
            new_callable=AsyncMock,
        ) as mock_call:
            mock_call.return_value = MOCK_GEMINI_API_RESPONSE

            response = sample_client.post(ENDPOINT, json=VALID_REQUEST_PAYLOAD)
            assert response.status_code == 200, response.text
            data = response.json()

            assert data["data_source_mode"] == "gemini_live"
            assert data["methodology"]["method"] == "gemini_web_grounded_cohort"
            assert data["primary_estimate_rial"] == 500000000
            assert data["median_salary_rial"] == 500000000
            assert data["min_salary_rial"] == 480000000
            assert data["max_salary_rial"] == 520000000
            assert data["valid_sample_count"] == 2
            assert any("جابینجا" in s for s in data["data_sources"])

    def test_gemini_failure_falls_back_to_database_when_available(
        self, sample_client: TestClient
    ) -> None:
        with patch(
            "app.services.estimation.gemini_service.GeminiLiveSalaryService.call_gemini",
            new_callable=AsyncMock,
        ) as mock_call:
            mock_call.side_effect = GeminiUnavailableError("خطای موقت در ارتباط با جمینای")

            response = sample_client.post(ENDPOINT, json=VALID_REQUEST_PAYLOAD)
            assert response.status_code == 200, response.text
            data = response.json()

            # Successfully fell back to sample DB
            assert data["data_source_mode"] == "database_fallback"
            assert any("سرویس جستجوی زنده جمینای با خطا مواجه شد" in w for w in data["warnings"])

    def test_gemini_failure_returns_503_when_database_unavailable(
        self, bare_client: TestClient
    ) -> None:
        with patch(
            "app.services.estimation.gemini_service.GeminiLiveSalaryService.call_gemini",
            new_callable=AsyncMock,
        ) as mock_call:
            mock_call.side_effect = GeminiUnavailableError("سرویس جمینای در دسترس نیست.")

            response = bare_client.post(ENDPOINT, json=VALID_REQUEST_PAYLOAD)
            assert response.status_code == 503
            body = response.json()
            assert body["error"]["code"] == "ESTIMATION_GEMINI_UNAVAILABLE"
            assert "سرویس جمینای در دسترس نیست" in body["error"]["detail"]

    def test_gemini_insufficient_data_falls_back_to_db(
        self, sample_client: TestClient
    ) -> None:
        empty_gemini_response = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": '{"found_data": false, "refusal_reason": "عدم یافت داده"}'}
                        ]
                    }
                }
            ]
        }
        with patch(
            "app.services.estimation.gemini_service.GeminiLiveSalaryService.call_gemini",
            new_callable=AsyncMock,
        ) as mock_call:
            mock_call.return_value = empty_gemini_response

            response = sample_client.post(ENDPOINT, json=VALID_REQUEST_PAYLOAD)
            assert response.status_code == 200, response.text
            data = response.json()
            assert data["data_source_mode"] == "database_fallback"
            assert any("دادهٔ معتبری در جستجوی زنده وب یافت نشد" in w for w in data["warnings"])

    def test_no_gemini_key_uses_database_directly(self, sample_client: TestClient) -> None:
        payload = dict(VALID_REQUEST_PAYLOAD)
        payload.pop("gemini_api_key")

        response = sample_client.post(ENDPOINT, json=payload)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["data_source_mode"] == "database_fallback"
