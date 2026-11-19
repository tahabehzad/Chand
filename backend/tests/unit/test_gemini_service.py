"""Unit tests for the Gemini Web-Grounded Live Market Salary Service.

Authority: ADR-014 §7; AGENTS.md §2 Financial invariants 7-12.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.domain.salary_estimation.market_data import MarketObservation
from app.domain.salary_estimation.matcher import SalaryMatcher
from app.domain.salary_estimation.salary_estimator import InsufficientMarketDataError
from app.domain.salary_estimation.schemas import EstimationProfile
from app.services.estimation.gemini_service import (
    GEMINI_LIVE_METHOD,
    GeminiLiveSalaryService,
    GeminiUnavailableError,
)

SAMPLE_PROFILE = EstimationProfile(
    job_title="توسعه‌دهنده فرانت‌اند",
    experience_years=3,
    seniority_level="mid",
    employment_type="full_time",
    city="تهران",
    province="تهران",
    work_condition="on_site",
    job_description="توسعه اپلیکیشن‌های فرانت‌اند با React و Next.js",
    skills=("React", "TypeScript", "Next.js"),
    education="کارشناسی کامپیوتر",
)

SAMPLE_GEMINI_SUCCESS_PAYLOAD: dict[str, Any] = {
    "candidates": [
        {
            "content": {
                "parts": [
                    {
                        "text": """```json
{
  "found_data": true,
  "refusal_reason": null,
  "observations": [
    {
      "job_title_reported": "توسعه‌دهنده React",
      "source_name": "Jobinja",
      "source_url": "https://jobinja.ir/jobs/12345",
      "city": "تهران",
      "seniority_level": "mid",
      "amount_rial": 450000000,
      "period": "monthly",
      "license_status": "manual_verified",
      "notes": "آگهی استخدام پاییز ۱۴۰۳"
    },
    {
      "job_title_reported": "برنامه‌نویس فرانت‌اند React",
      "source_name": "Jobvision",
      "source_url": "https://jobvision.ir/jobs/67890",
      "city": "تهران",
      "seniority_level": "mid",
      "amount_rial": 520000000,
      "period": "monthly",
      "license_status": "manual_verified",
      "notes": "آگهی نیازمند ۳ سال سابقه"
    },
    {
      "job_title_reported": "Senior/Mid Frontend Engineer",
      "source_name": "IranTalent",
      "source_url": "https://irantalent.com/jobs/555",
      "city": "تهران",
      "seniority_level": "mid",
      "amount_rial": 400000000,
      "period": "monthly",
      "license_status": "manual_verified",
      "notes": "محدوده حقوق اعلامی کارفرما"
    }
  ],
  "aggregates": [
    {
      "source_name": "گزارش حقوق جاب‌ویژن ۱۴۰۳",
      "job_title_reported": "توسعه‌دهنده React",
      "city": "تهران",
      "seniority_level": "mid",
      "p25_rial": 380000000,
      "median_rial": 480000000,
      "p75_rial": 600000000,
      "sample_size": 180,
      "source_url": "https://jobvision.ir/salary"
    }
  ],
  "factors_influence": [
    "تسلط بر اکوسیستم React و TypeScript",
    "۳ سال سابقه کاری در شرکت‌های فناوری تهران"
  ],
  "factors_notes": [
    "میانگین حقوق فرانت‌اند در تهران در نیمه دوم ۱۴۰۳ بین ۴۰ تا ۵۵ میلیون تومان است"
  ]
}
```"""
                    }
                ]
            },
            "groundingMetadata": {
                "webSearchQueries": ["حقوق برنامه نویس ری اکت تهران جابینجا ۱۴۰۳"],
                "groundingChunks": [
                    {
                        "web": {
                            "uri": "https://jobinja.ir/salaries",
                            "title": "جابینجا - میانگین حقوق توسعه دهندگان",
                        }
                    },
                    {
                        "web": {
                            "uri": "https://jobvision.ir/reports/1403",
                            "title": "گزارش جامع حقوق و دستمزد جاب‌ویژن ۱۴۰۳",
                        }
                    },
                ],
            },
        }
    ]
}


class TestPromptConstruction:
    def test_prompt_contains_iranian_portals_and_invariants(self) -> None:
        service = GeminiLiveSalaryService()
        matcher = SalaryMatcher()
        match = matcher.match(
            job_title=SAMPLE_PROFILE.job_title,
            job_description=SAMPLE_PROFILE.job_description,
            skills=SAMPLE_PROFILE.skills,
            seniority_level=SAMPLE_PROFILE.seniority_level,
        )
        assert match is not None
        prompt = service.build_prompt(SAMPLE_PROFILE, match)

        assert "Jobinja" in prompt or "جابینجا" in prompt
        assert "Jobvision" in prompt or "جاب‌ویژن" in prompt
        assert "IranTalent" in prompt or "ایران‌تلنت" in prompt
        assert "Quera" in prompt or "کوئرا" in prompt
        assert "CRITICAL ANTI-FABRICATION INVARIANT" in prompt
        assert "RIAL" in prompt or "Rial" in prompt
        assert SAMPLE_PROFILE.job_title in prompt
        assert SAMPLE_PROFILE.city in prompt


class TestGeminiApiCall:
    @pytest.mark.asyncio
    async def test_raises_when_api_key_empty(self) -> None:
        service = GeminiLiveSalaryService()
        with pytest.raises(GeminiUnavailableError, match="کلید دسترسی"):
            await service.call_gemini(api_key="", prompt="test")

    @pytest.mark.asyncio
    async def test_handles_http_errors_gracefully(self) -> None:
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 403
        mock_response.text = "Forbidden / Quota"
        mock_client.post.return_value = mock_response

        service = GeminiLiveSalaryService(http_client=mock_client)
        with pytest.raises(GeminiUnavailableError, match="نامعتبر است یا دسترسی مجاز نیست"):
            await service.call_gemini(api_key="bad_key", prompt="test")

    @pytest.mark.asyncio
    async def test_handles_timeout_gracefully(self) -> None:
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post.side_effect = httpx.TimeoutException("Timed out")

        service = GeminiLiveSalaryService(http_client=mock_client)
        with pytest.raises(GeminiUnavailableError, match="مهلت زمان"):
            await service.call_gemini(api_key="key", prompt="test")


class TestResponseParsingAndExtraction:
    def test_parses_valid_payload_with_observations_and_grounding(self) -> None:
        service = GeminiLiveSalaryService()
        as_of = datetime.now(UTC)
        match = SalaryMatcher().match(job_title=SAMPLE_PROFILE.job_title)
        assert match is not None

        (
            observations,
            aggregates,
            factors_influence,
            factors_notes,
            grounding_sources,
        ) = service.parse_gemini_payload(
            SAMPLE_GEMINI_SUCCESS_PAYLOAD,
            SAMPLE_PROFILE,
            match,
            as_of,
        )

        assert len(observations) == 3
        assert len(aggregates) == 1
        assert len(factors_influence) >= 1
        assert len(factors_notes) >= 1
        assert len(grounding_sources) >= 2
        assert any("جابینجا" in s for s in grounding_sources)

        for obs in observations:
            assert isinstance(obs, MarketObservation)
            assert obs.amount_rial >= 400_000_000
            assert obs.period == "monthly"
            assert obs.city == "تهران"

    def test_refuses_when_found_data_is_false(self) -> None:
        payload = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": '{"found_data": false, "refusal_reason": "هیچ آگهی معتبری با حقوق مشخص یافت نشد."}'
                            }
                        ]
                    }
                }
            ]
        }
        service = GeminiLiveSalaryService()
        match = SalaryMatcher().match(job_title=SAMPLE_PROFILE.job_title)
        with pytest.raises(InsufficientMarketDataError) as exc_info:
            service.parse_gemini_payload(payload, SAMPLE_PROFILE, match, datetime.now(UTC))
        assert exc_info.value.reason == "insufficient_live_market_data"


class TestLiveCalculationIntegrity:
    def test_pure_quantiles_and_toman_exactness(self) -> None:
        service = GeminiLiveSalaryService()
        as_of = datetime(2026, 11, 18, 12, 0, 0, tzinfo=UTC)
        match = SalaryMatcher().match(job_title=SAMPLE_PROFILE.job_title)
        assert match is not None

        (
            observations,
            aggregates,
            factors_influence,
            factors_notes,
            grounding_sources,
        ) = service.parse_gemini_payload(
            SAMPLE_GEMINI_SUCCESS_PAYLOAD,
            SAMPLE_PROFILE,
            match,
            as_of,
        )

        outcome = service.calculate_live_outcome(
            profile=SAMPLE_PROFILE,
            match=match,
            observations=observations,
            aggregates=aggregates,
            factors_influence=factors_influence,
            factors_notes=factors_notes,
            grounding_sources=grounding_sources,
            as_of=as_of,
            model="gemini-2.0-flash",
        )

        assert outcome.data_source_mode == "gemini_live"
        assert outcome.methodology["method"] == GEMINI_LIVE_METHOD
        assert outcome.min_salary_rial <= outcome.median_salary_rial <= outcome.max_salary_rial
        assert outcome.primary_estimate_rial == outcome.median_salary_rial

        # Quantisation to whole Toman (multiples of 10 Rial)
        assert outcome.min_salary_rial % 10 == 0
        assert outcome.median_salary_rial % 10 == 0
        assert outcome.max_salary_rial % 10 == 0
        assert outcome.primary_estimate_rial % 10 == 0

        # Provenance and hash
        assert len(outcome.calculation_hash) == 32
        assert len(outcome.data_sources) >= 3
        assert outcome.valid_sample_count == 3
        assert outcome.confidence_level in {"high", "medium", "low"}


class TestGeminiEndpointResponses:
    """Test the salary estimation endpoint with mocked Gemini behaviors."""

    def test_mocked_gemini_live_grounding_response_200(self) -> None:
        """Mocked Gemini live grounding returns 200 with full live estimation outcome."""
        from fastapi.testclient import TestClient

        from app.core.config import Settings
        from app.domain.salary_estimation.schemas import EstimationOutcome
        from app.main import create_app

        app = create_app(Settings(_env_file=None, estimation_allow_sample_data=False))
        client = TestClient(app)

        as_of = datetime(2026, 11, 18, 12, 0, 0, tzinfo=UTC)
        service = GeminiLiveSalaryService()
        match = SalaryMatcher().match(job_title=SAMPLE_PROFILE.job_title)
        assert match is not None

        (
            observations,
            aggregates,
            factors_influence,
            factors_notes,
            grounding_sources,
        ) = service.parse_gemini_payload(
            SAMPLE_GEMINI_SUCCESS_PAYLOAD,
            SAMPLE_PROFILE,
            match,
            as_of,
        )

        fake_outcome = service.calculate_live_outcome(
            profile=SAMPLE_PROFILE,
            match=match,
            observations=observations,
            aggregates=aggregates,
            factors_influence=factors_influence,
            factors_notes=factors_notes,
            grounding_sources=grounding_sources,
            as_of=as_of,
            model="gemini-2.0-flash",
        )

        with patch.object(
            GeminiLiveSalaryService,
            "estimate_market_salary_live",
            new_callable=AsyncMock,
            return_value=fake_outcome,
        ):
            resp = client.post(
                "/api/v1/simulations/salary-estimation",
                json={
                    "job_title": SAMPLE_PROFILE.job_title,
                    "experience_years": SAMPLE_PROFILE.experience_years,
                    "seniority_level": SAMPLE_PROFILE.seniority_level,
                    "employment_type": SAMPLE_PROFILE.employment_type,
                    "city": SAMPLE_PROFILE.city,
                    "skills": [{"name": "React"}],
                    "gemini_api_key": "AIzaSyMockedValidKeyForTesting12345",
                },
            )
            assert resp.status_code == 200, resp.text
            data = resp.json()
            assert data["min_salary_rial"] == fake_outcome.min_salary_rial
            assert data["median_salary_rial"] == fake_outcome.median_salary_rial
            assert data["max_salary_rial"] == fake_outcome.max_salary_rial
            assert data["methodology"]["method"] == GEMINI_LIVE_METHOD
            assert len(data["market_rows"]) == 3

    def test_gemini_timeout_returns_503(self) -> None:
        """When Gemini times out and repository is unavailable, endpoint responds with 503."""
        from fastapi.testclient import TestClient

        from app.core.config import Settings
        from app.main import create_app
        from app.services.estimation.service import DataStoreUnavailableError

        app = create_app(Settings(_env_file=None, estimation_allow_sample_data=False))
        client = TestClient(app)

        with patch.object(
            GeminiLiveSalaryService,
            "estimate_market_salary_live",
            new_callable=AsyncMock,
            side_effect=GeminiUnavailableError("مهلت زمانی ارتباط با جمینای به پایان رسید."),
        ), patch(
            "app.services.estimation.service.build_repository",
            side_effect=DataStoreUnavailableError("DB unavailable"),
        ):
            resp = client.post(
                "/api/v1/simulations/salary-estimation",
                json={
                    "job_title": SAMPLE_PROFILE.job_title,
                    "experience_years": SAMPLE_PROFILE.experience_years,
                    "seniority_level": SAMPLE_PROFILE.seniority_level,
                    "employment_type": SAMPLE_PROFILE.employment_type,
                    "city": SAMPLE_PROFILE.city,
                    "skills": [{"name": "React"}],
                    "gemini_api_key": "AIzaSyMockedValidKeyForTesting12345",
                },
            )
            assert resp.status_code == 503, resp.text
            data = resp.json()
            assert data["error"]["code"] == "ESTIMATION_GEMINI_UNAVAILABLE"
            assert "مهلت زمان" in data["error"]["detail"]

    def test_gemini_refusal_when_insufficient_data_returns_409(self) -> None:
        """When Gemini refuses due to insufficient data and fallback has none, returns 409."""
        from fastapi.testclient import TestClient

        from app.core.config import Settings
        from app.main import create_app
        from app.services.estimation.service import DataStoreUnavailableError

        app = create_app(Settings(_env_file=None, estimation_allow_sample_data=False))
        client = TestClient(app)

        with patch.object(
            GeminiLiveSalaryService,
            "estimate_market_salary_live",
            new_callable=AsyncMock,
            side_effect=InsufficientMarketDataError(
                reason="insufficient_live_market_data",
                detail="هیچ آگهی معتبری با حقوق مشخص برای این شغل یافت نشد.",
                counts={"valid_samples": 0},
            ),
        ), patch(
            "app.services.estimation.service.build_repository",
            side_effect=DataStoreUnavailableError("DB unavailable"),
        ):
            resp = client.post(
                "/api/v1/simulations/salary-estimation",
                json={
                    "job_title": SAMPLE_PROFILE.job_title,
                    "experience_years": SAMPLE_PROFILE.experience_years,
                    "seniority_level": SAMPLE_PROFILE.seniority_level,
                    "employment_type": SAMPLE_PROFILE.employment_type,
                    "city": SAMPLE_PROFILE.city,
                    "skills": [{"name": "React"}],
                    "gemini_api_key": "AIzaSyMockedValidKeyForTesting12345",
                },
            )
            assert resp.status_code == 409, resp.text
            data = resp.json()
            assert data["error"]["code"] == "ESTIMATION_INSUFFICIENT_DATA"
            assert data["error"]["reason"] == "insufficient_live_market_data"

    @pytest.mark.parametrize(
        "job_title,city",
        [
            ("کارشناس بازاریابی دیجیتال", "مشهد"),
            ("طراح گرافیک و رابط کاربری", "اصفهان"),
            ("مهندس عمران و سرپرست کارگاه", "اراک"),
            ("کارشناس حقوقی و قراردادها", "تهران"),
        ],
    )
    def test_arbitrary_non_taxonomy_roles_supported_without_blocker(
        self, job_title: str, city: str
    ) -> None:
        """Non-predefined roles pass straight to Gemini without raising no_job_family_match."""
        from fastapi.testclient import TestClient

        from app.core.config import Settings
        from app.domain.salary_estimation.schemas import EstimationOutcome
        from app.main import create_app

        app = create_app(Settings(_env_file=None, estimation_allow_sample_data=False))
        client = TestClient(app)

        as_of = datetime(2026, 11, 18, 12, 0, 0, tzinfo=UTC)
        mock_outcome = EstimationOutcome(
            primary_estimate_rial=350_000_000,
            min_salary_rial=280_000_000,
            median_salary_rial=350_000_000,
            max_salary_rial=450_000_000,
            rounding_residual_rial=0,
            valid_sample_count=8,
            quarantined_sample_count=0,
            rejected_sample_count=0,
            confidence_level="medium",
            confidence_score=Decimal("0.75"),
            data_confidence=Decimal("0.80"),
            prediction_confidence=Decimal("0.75"),
            confidence_components={"sample_size": "8"},
            confidence_weights={"live": "1.0"},
            factors_influence=("رده شغلی تخصصی",),
            factors_notes=(),
            data_sources=("Jobinja", "Jobvision"),
            data_collected_at=as_of,
            data_oldest_at=as_of,
            market_rows=(),
            distribution=(),
            methodology={
                "method": GEMINI_LIVE_METHOD,
                "cohort_scope": "national",
                "cohort_definition": "میانگین کشوری در سراسر ایران",
            },
            warnings=(),
            match={"family_key": "dynamic_role", "family_title_fa": job_title},
            cohort_scope="national",
            cohort_size=8,
            legal_minimum_wage_rial=71_661_840,
            calculation_hash="hash_dynamic_role_test_12345678",
            generated_at=as_of,
            data_source_mode="gemini_live",
        )

        with patch.object(
            GeminiLiveSalaryService,
            "estimate_market_salary_live",
            new_callable=AsyncMock,
            return_value=mock_outcome,
        ):
            resp = client.post(
                "/api/v1/simulations/salary-estimation",
                json={
                    "job_title": job_title,
                    "experience_years": 3,
                    "seniority_level": "mid",
                    "employment_type": "full_time",
                    "city": city,
                    "gemini_api_key": "AIzaSyMockedValidKeyForTesting12345",
                },
            )
            assert resp.status_code == 200, resp.text
            data = resp.json()
            assert data["primary_estimate_rial"] == 350_000_000
            assert data["job_title"] == job_title
            assert data["match"]["family_key"] == "dynamic_role"
            assert data["methodology"]["cohort_scope"] == "national"

    def test_city_to_national_cascade_sets_national_cohort_scope(self) -> None:
        """When observations are from outside the local city, cohort_scope becomes national."""
        service = GeminiLiveSalaryService()
        as_of = datetime(2026, 11, 18, 12, 0, 0, tzinfo=UTC)
        profile = EstimationProfile(
            job_title="کارشناس بازاریابی دیجیتال",
            experience_years=2,
            seniority_level="junior",
            employment_type="full_time",
            city="یزد",
            province="یزد",
            work_condition="on_site",
            job_description="سئو و ادوردز",
            skills=("SEO", "Google Ads"),
            education="کارشناسی",
        )
        match = SalaryMatcher().match(job_title=profile.job_title)
        if match is None:
            from app.domain.salary_estimation.matcher import JobMatch

            match = JobMatch(
                family_key="dynamic_role",
                family_title_fa=profile.job_title,
                score=Decimal("1.0"),
                reasons=("عنوان پویای بازار کار",),
                components={"title": "1.0"},
            )

        national_payload = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": json.dumps({
                                    "found_data": True,
                                    "cohort_scope": "national",
                                    "observations": [
                                        {
                                            "job_title_reported": "دیجیتال مارکتر",
                                            "source_name": "Jobinja",
                                            "city": "تهران",
                                            "amount_rial": 220_000_000,
                                        },
                                        {
                                            "job_title_reported": "کارشناس بازاریابی دیجیتال",
                                            "source_name": "Jobvision",
                                            "city": "اصفهان",
                                            "amount_rial": 250_000_000,
                                        },
                                    ],
                                    "aggregates": [],
                                    "factors_influence": ["سئو و تبلیغات کلیکی"],
                                    "factors_notes": [],
                                })
                            }
                        ]
                    }
                }
            ]
        }

        (
            observations,
            aggregates,
            factors_influence,
            factors_notes,
            grounding_sources,
        ) = service.parse_gemini_payload(national_payload, profile, match, as_of)

        outcome = service.calculate_live_outcome(
            profile=profile,
            match=match,
            observations=observations,
            aggregates=aggregates,
            factors_influence=factors_influence,
            factors_notes=factors_notes,
            grounding_sources=grounding_sources,
            as_of=as_of,
            model="gemini-2.0-flash",
        )

        assert outcome.cohort_scope == "national"
        assert outcome.methodology["cohort_scope"] == "national"
        assert any("میانگین کشوری" in f for f in outcome.factors_influence)

    def test_min_plausible_salary_threshold_accepts_20m_rial(self) -> None:
        """Monthly salary of 20M Rial (2M Toman) is accepted for entry/intern positions."""
        from app.services.estimation.gemini_service import _parse_observations

        as_of = datetime(2026, 11, 18, 12, 0, 0, tzinfo=UTC)
        profile = EstimationProfile(
            job_title="کارآموز طراحی",
            experience_years=0,
            seniority_level="junior",
            employment_type="part_time",
            city="تهران",
            province="تهران",
            work_condition="remote",
            job_description=None,
            skills=(),
            education=None,
        )

        raw = [
            {"amount_rial": 20_000_000, "source_name": "Divar"},  # Valid (20M Rial)
            {"amount_rial": 25_000_000, "source_name": "Jobinja"},  # Valid (25M Rial)
            {"amount_rial": 1_500_000, "source_name": "Quera"},  # Filtered (< 20M Rial: 1.5M Rial = 150k Toman)
        ]
        parsed = _parse_observations(raw, profile, "dynamic_role", as_of)
        assert len(parsed) == 2
        assert {obs.amount_rial for obs in parsed} == {20_000_000, 25_000_000}

    @pytest.mark.parametrize(
        "custom_title,city,exp,level",
        [
            ("طراح گرافیک", "شیراز", 3, "mid"),
            ("مدیر مارکتینگ", "تهران", 6, "senior"),
            ("کارشناس تولید محتوا", "اصفهان", 2, "junior"),
            ("مهندس عمران", "تبریز", 5, "mid"),
            ("کارشناس فروش تلفنی", "مشهد", 1, "junior"),
        ],
    )
    def test_arbitrary_custom_roles_baseline_fallback_returns_200_realistic_range(
        self, custom_title: str, city: str, exp: int, level: str
    ) -> None:
        """Arbitrary roles without Gemini key or DB seeds return 200 with realistic compensation ranges."""
        from fastapi.testclient import TestClient

        from app.core.config import Settings
        from app.main import create_app

        app = create_app(Settings(_env_file=None, estimation_allow_sample_data=False))
        client = TestClient(app)

        resp = client.post(
            "/api/v1/simulations/salary-estimation",
            json={
                "job_title": custom_title,
                "experience_years": exp,
                "seniority_level": level,
                "employment_type": "full_time",
                "city": city,
            },
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["primary_estimate_rial"] >= 200_000_000  # >= 20M Toman
        assert data["min_salary_rial"] < data["primary_estimate_rial"]
        assert data["max_salary_rial"] > data["primary_estimate_rial"]
        assert data["match"]["family_key"] in ("custom_role", "sales_representative")
        assert data["methodology"]["cohort_scope"] == "national"



