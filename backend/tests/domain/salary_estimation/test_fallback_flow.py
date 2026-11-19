"""Domain and service tests for the Gemini-to-PostgreSQL fallback flow.

Authority:
    docs/adr/ADR-014-market-salary-reference-data-and-estimation.md;
    docs/SALARY_ESTIMATION_SPEC.md;
    AGENTS.md §2 Invariant 7 (Refuse instead of fabricate).
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.config import Settings
from app.domain.salary_estimation.market_data import (
    MarketAggregate,
    MarketObservation,
    MarketSource,
)
from app.domain.salary_estimation.salary_estimator import InsufficientMarketDataError
from app.domain.salary_estimation.schemas import EstimationOutcome, EstimationProfile
from app.repositories.market_data import MarketDataRepository
from app.schemas.estimation import EstimateRequest
from app.services.estimation.gemini_service import (
    GEMINI_LIVE_METHOD,
    GeminiLiveSalaryService,
    GeminiUnavailableError,
)
from app.services.estimation.service import (
    compute_estimate,
)


def _sample_request(*, api_key: str | None = "AIzaSyTestKey123") -> EstimateRequest:
    return EstimateRequest(
        job_title="توسعه‌دهنده فرانت‌اند",
        experience_years=3,
        seniority_level="mid",
        employment_type="full_time",
        city="تهران",
        skills=[{"name": "React"}, {"name": "TypeScript"}],
        education="کارشناسی",
        gemini_api_key=api_key,
    )


class MockDbRepository:
    """In-memory repository simulating PostgreSQL reference data."""

    def __init__(self, observations: list[MarketObservation] | None = None) -> None:
        self._observations = (
            observations
            if observations is not None
            else [
                MarketObservation(
                    id="mock_obs_1",
                    family_key="frontend_react",
                    job_title_reported="توسعه‌دهنده React",
                    city="تهران",
                    amount_rial=450_000_000,
                    period="monthly",
                    currency_unit_reported="rial",
                    source_id="mock_db_1",
                    license_status="manual_verified",
                    collected_at=datetime(2026, 11, 1, tzinfo=UTC),
                    seniority_level="mid",
                ),
                MarketObservation(
                    id="mock_obs_2",
                    family_key="frontend_react",
                    job_title_reported="برنامه‌نویس فرانت‌اند React",
                    city="تهران",
                    amount_rial=500_000_000,
                    period="monthly",
                    currency_unit_reported="rial",
                    source_id="mock_db_2",
                    license_status="manual_verified",
                    collected_at=datetime(2026, 11, 2, tzinfo=UTC),
                    seniority_level="mid",
                ),
                MarketObservation(
                    id="mock_obs_3",
                    family_key="frontend_react",
                    job_title_reported="Frontend Developer",
                    city="تهران",
                    amount_rial=520_000_000,
                    period="monthly",
                    currency_unit_reported="rial",
                    source_id="mock_db_3",
                    license_status="manual_verified",
                    collected_at=datetime(2026, 11, 3, tzinfo=UTC),
                    seniority_level="mid",
                ),
            ]
        )

    async def observations_for(self, family_key: str) -> Sequence[MarketObservation]:
        return [obs for obs in self._observations if obs.family_key == family_key]

    async def aggregates_for(self, family_key: str) -> Sequence[MarketAggregate]:
        return []

    async def sources(self) -> Sequence[MarketSource]:
        return []

    async def store_source(self, source: MarketSource) -> None:
        pass

    async def store_observations(self, rows: Sequence[MarketObservation]) -> int:
        return len(rows)

    async def store_aggregates(self, rows: Sequence[MarketAggregate]) -> int:
        return len(rows)

    async def record_quality(self, observation_id: str, status: str, reason: str | None) -> None:
        pass


@pytest.mark.asyncio
class TestFallbackFlow:
    """Verify seamless fallback from Gemini live grounding to reference data."""

    async def test_gemini_unavailable_seamlessly_falls_back_to_db(self) -> None:
        """When Gemini raises GeminiUnavailableError (timeout/network), falls back to DB."""
        request = _sample_request()
        repo = MockDbRepository()
        settings = Settings(
            _env_file=None,
            estimation_min_valid_samples=3,
            estimation_allow_sample_data=False,
        )

        mock_gemini = MagicMock(spec=GeminiLiveSalaryService)
        mock_gemini.estimate_market_salary_live = AsyncMock(
            side_effect=GeminiUnavailableError("مهلت زمانی ارتباط با جمینای به پایان رسید.")
        )

        response = await compute_estimate(
            request,
            repository_factory=lambda: repo,
            settings=settings,
            gemini_service=mock_gemini,
        )

        # Successfully computed from PostgreSQL fallback
        assert response.min_salary_rial > 0
        assert response.median_salary_rial > 0
        assert response.max_salary_rial >= response.median_salary_rial
        assert response.valid_sample_count == 3
        # Warning notifies manager that fallback occurred
        assert any("جمینای با خطا مواجه شد" in w for w in response.warnings)

    async def test_gemini_insufficient_data_seamlessly_falls_back_to_db(self) -> None:
        """When live search finds no live job postings, falls back to DB reference data."""
        request = _sample_request()
        repo = MockDbRepository()
        settings = Settings(
            _env_file=None,
            estimation_min_valid_samples=3,
            estimation_allow_sample_data=False,
        )

        mock_gemini = MagicMock(spec=GeminiLiveSalaryService)
        mock_gemini.estimate_market_salary_live = AsyncMock(
            side_effect=InsufficientMarketDataError(
                reason="insufficient_live_market_data",
                detail="هیچ آگهی معتبری با حقوق مشخص یافت نشد.",
                counts={"valid_samples": 0},
            )
        )

        response = await compute_estimate(
            request,
            repository_factory=lambda: repo,
            settings=settings,
            gemini_service=mock_gemini,
        )

        assert response.min_salary_rial > 0
        assert response.valid_sample_count == 3
        assert any("دادهٔ معتبری در جستجوی زنده وب یافت نشد" in w for w in response.warnings)

    async def test_gemini_success_does_not_invoke_db(self) -> None:
        """When live search succeeds, repository is never queried."""
        request = _sample_request()
        as_of = datetime(2026, 11, 18, 12, 0, 0, tzinfo=UTC)

        from app.domain.salary_estimation.matcher import SalaryMatcher

        svc = GeminiLiveSalaryService()
        match = SalaryMatcher().match(job_title=request.job_title)
        assert match is not None

        obs = [
            MarketObservation(
                id="live_1",
                family_key="frontend_react",
                job_title_reported="توسعه‌دهنده React",
                city="تهران",
                amount_rial=500_000_000,
                period="monthly",
                currency_unit_reported="rial",
                source_id="jobinja",
                license_status="manual_verified",
                collected_at=as_of,
                seniority_level="mid",
            ),
            MarketObservation(
                id="live_2",
                family_key="frontend_react",
                job_title_reported="برنامه‌نویس React",
                city="تهران",
                amount_rial=550_000_000,
                period="monthly",
                currency_unit_reported="rial",
                source_id="jobvision",
                license_status="manual_verified",
                collected_at=as_of,
                seniority_level="mid",
            ),
            MarketObservation(
                id="live_3",
                family_key="frontend_react",
                job_title_reported="React Dev",
                city="تهران",
                amount_rial=600_000_000,
                period="monthly",
                currency_unit_reported="rial",
                source_id="irantalent",
                license_status="manual_verified",
                collected_at=as_of,
                seniority_level="mid",
            ),
        ]

        fake_outcome = svc.calculate_live_outcome(
            profile=EstimationProfile(
                job_title=request.job_title,
                experience_years=request.experience_years,
                seniority_level=request.seniority_level,
                employment_type=request.employment_type,
                city=request.city,
            ),
            match=match,
            observations=obs,
            aggregates=[],
            factors_influence=["تجربه", "مهارت React"],
            factors_notes=[],
            grounding_sources=["https://jobinja.ir/jobs/1"],
            as_of=as_of,
            model="gemini-2.0-flash",
        )

        mock_gemini = MagicMock(spec=GeminiLiveSalaryService)
        mock_gemini.estimate_market_salary_live = AsyncMock(return_value=fake_outcome)

        repo = MagicMock(spec=MarketDataRepository)

        response = await compute_estimate(
            request,
            repository_factory=lambda: repo,
            gemini_service=mock_gemini,
        )

        assert response.methodology.method == GEMINI_LIVE_METHOD
        assert response.primary_estimate_rial == fake_outcome.primary_estimate_rial
        # Repository was never called
        repo.observations_for.assert_not_called()

    async def test_both_gemini_and_db_fail_raises_refusal_not_fabrication(self) -> None:
        """When both Gemini and DB fail, fails closed instead of inventing numbers (ADR-014)."""
        request = _sample_request()
        # Empty DB repository
        repo = MockDbRepository(observations=[])
        settings = Settings(
            _env_file=None,
            estimation_min_valid_samples=3,
            estimation_allow_sample_data=False,
        )

        mock_gemini = MagicMock(spec=GeminiLiveSalaryService)
        mock_gemini.estimate_market_salary_live = AsyncMock(
            side_effect=GeminiUnavailableError("Network timeout")
        )

        with pytest.raises(GeminiUnavailableError):
            await compute_estimate(
                request,
                repository_factory=lambda: repo,
                settings=settings,
                gemini_service=mock_gemini,
            )

    async def test_no_api_key_directly_queries_repository(self) -> None:
        """When no Gemini key is provided, queries DB directly without calling Gemini."""
        request = _sample_request(api_key=None)
        repo = MockDbRepository()
        settings = Settings(
            _env_file=None,
            estimation_min_valid_samples=3,
            estimation_allow_sample_data=False,
        )

        mock_gemini = MagicMock(spec=GeminiLiveSalaryService)

        response = await compute_estimate(
            request,
            repository_factory=lambda: repo,
            settings=settings,
            gemini_service=mock_gemini,
        )

        mock_gemini.estimate_market_salary_live.assert_not_called()
        assert response.valid_sample_count == 3
        assert response.min_salary_rial > 0
