"""End-to-end contract tests for the market salary estimation endpoint.

Authority: ``docs/adr/ADR-014-market-salary-reference-data-and-estimation.md`` §7.
The endpoint has three honest answers and this module pins all of them:

* 200 — an estimate with provenance, built from the sample only in development;
* 409 — a refusal (no family match, too few valid rows, confidence too low);
* 503 — the market-data store itself is unavailable.

A refusal must never contain a figure, and a published figure must never be a
number the engine could not derive from validated rows.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app

ENDPOINT = "/api/v1/simulations/salary-estimation"

VALID_PAYLOAD: dict[str, object] = {
    "job_title": "برنامه‌نویس PHP",
    "experience_years": 5,
    "seniority_level": "mid",
    "employment_type": "full_time",
    "city": "تهران",
    "province": "تهران",
    "work_condition": "on_site",
    "job_description": "توسعه و نگهداری سرویس‌های laravel و php",
    "currency_unit": "toman",
    "skills": [{"name": "php", "level": "advanced"}, {"name": "laravel"}],
}


@pytest.fixture
def sample_client() -> Iterator[TestClient]:
    """An application whose only switch is the explicitly-enabled sample mode."""
    application = create_app(
        Settings(_env_file=None, estimation_allow_sample_data=True)
    )
    with TestClient(application) as client:
        yield client


@pytest.fixture
def bare_client() -> Iterator[TestClient]:
    """An application with no market-data store and no sample data."""
    application = create_app(Settings(_env_file=None, database_url=""))
    with TestClient(application) as client:
        yield client


class TestPublishedEstimate:
    """The 200 response carries every figure with its provenance."""

    def test_returns_the_full_contract(self, sample_client: TestClient) -> None:
        response = sample_client.post(ENDPOINT, json=VALID_PAYLOAD)
        assert response.status_code == 200, response.text
        data = response.json()

        required = {
            "advisory",
            "statutory",
            "advisory_notes",
            "model_version",
            "estimation_version",
            "engine_version",
            "calculation_hash",
            "generated_at",
            "job_title",
            "experience_years",
            "seniority_level",
            "employment_type",
            "work_condition",
            "city",
            "province",
            "primary_estimate_rial",
            "min_salary_rial",
            "median_salary_rial",
            "max_salary_rial",
            "rounding_residual_rial",
            "currency_unit",
            "valid_sample_count",
            "quarantined_sample_count",
            "rejected_sample_count",
            "data_sources",
            "data_collected_at",
            "data_oldest_at",
            "market_rows",
            "distribution",
            "factors_influence",
            "factors_notes",
            "confidence_level",
            "confidence_score",
            "confidence",
            "methodology",
            "match",
            "warnings",
            "legal_minimum_wage_rial",
        }
        assert required <= set(data)
        assert data["advisory"] is True
        assert data["statutory"] is False

    def test_figures_are_ordered_and_toman_exact(self, sample_client: TestClient) -> None:
        data = sample_client.post(ENDPOINT, json=VALID_PAYLOAD).json()
        assert data["min_salary_rial"] <= data["median_salary_rial"] <= data["max_salary_rial"]
        assert data["primary_estimate_rial"] == data["median_salary_rial"]
        for field in ("min_salary_rial", "median_salary_rial", "primary_estimate_rial", "max_salary_rial"):
            assert data[field] % 10 == 0, field
        assert abs(data["rounding_residual_rial"]) <= 15

    def test_provenance_is_populated(self, sample_client: TestClient) -> None:
        data = sample_client.post(ENDPOINT, json=VALID_PAYLOAD).json()
        assert data["valid_sample_count"] > 0
        assert data["data_sources"]
        assert data["data_collected_at"].startswith("20")
        assert data["market_rows"]
        assert len(data["calculation_hash"]) == 32
        assert len(data["distribution"]) >= 1

    def test_sample_data_is_labelled_and_cannot_claim_high_confidence(
        self, sample_client: TestClient
    ) -> None:
        data = sample_client.post(ENDPOINT, json=VALID_PAYLOAD).json()
        assert any("ساختگی" in warning for warning in data["warnings"])
        assert "sample_data_in_use" in data["methodology"]["warning_codes"]
        assert data["confidence_level"] in {"low", "insufficient_data"}
        assert float(data["confidence"]["data_confidence"]) < 1

    def test_methodology_is_reproducible(self, sample_client: TestClient) -> None:
        data = sample_client.post(ENDPOINT, json=VALID_PAYLOAD).json()
        methodology = data["methodology"]
        assert methodology["method"] == "market_cohort_quantiles"
        assert methodology["range_source"] == "p25_p50_p75_of_valid_observations"
        assert methodology["adjustments_applied"] == []
        assert methodology["currency_storage"] == "rial"
        assert "iqr_fence_3x" in methodology["outlier_tests"]


class TestRefusals:
    """A refusal never carries a figure."""

    def test_unknown_title_is_refused(self, sample_client: TestClient) -> None:
        payload = {**VALID_PAYLOAD, "job_title": "مترجم"}
        response = sample_client.post(ENDPOINT, json=payload)
        assert response.status_code == 409
        body = response.json()
        assert body["error"]["code"] == "ESTIMATION_INSUFFICIENT_DATA"
        assert body["error"]["reason"] == "no_job_family_match"
        assert "primary_estimate_rial" not in body

    def test_known_family_without_a_cohort_is_refused(self, sample_client: TestClient) -> None:
        payload = {**VALID_PAYLOAD, "job_title": "راننده", "seniority_level": "senior"}
        response = sample_client.post(ENDPOINT, json=payload)
        assert response.status_code == 409
        assert response.json()["error"]["reason"] == "insufficient_valid_samples"

    def test_no_store_is_an_operational_failure_not_insufficient_data(
        self, bare_client: TestClient
    ) -> None:
        response = bare_client.post(ENDPOINT, json=VALID_PAYLOAD)
        assert response.status_code == 503
        assert response.json()["error"]["code"] == "ESTIMATION_DATASTORE_UNAVAILABLE"

    def test_unmatched_title_is_decided_before_the_store_is_opened(
        self, bare_client: TestClient
    ) -> None:
        payload = {**VALID_PAYLOAD, "job_title": "مترجم"}
        response = bare_client.post(ENDPOINT, json=payload)
        assert response.status_code == 409


class TestRequestContract:
    """The request schema is closed and validated."""

    def test_empty_title_is_rejected(self, sample_client: TestClient) -> None:
        response = sample_client.post(ENDPOINT, json={**VALID_PAYLOAD, "job_title": ""})
        assert response.status_code == 422

    def test_unknown_seniority_is_rejected(self, sample_client: TestClient) -> None:
        response = sample_client.post(
            ENDPOINT, json={**VALID_PAYLOAD, "seniority_level": "principal"}
        )
        assert response.status_code == 422

    def test_unknown_field_is_rejected(self, sample_client: TestClient) -> None:
        response = sample_client.post(
            ENDPOINT, json={**VALID_PAYLOAD, "expected_salary_rial": 1}
        )
        assert response.status_code == 422

    def test_negative_experience_is_rejected(self, sample_client: TestClient) -> None:
        response = sample_client.post(
            ENDPOINT, json={**VALID_PAYLOAD, "experience_years": -1}
        )
        assert response.status_code == 422
