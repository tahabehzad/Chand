"""Unit tests for the Dynamic Regulatory Sync Service and versioned persistence.

Authority
---------
ADR-007; ADR-008; ADR-014; ``AGENTS.md`` §2 Invariant 7 (Refuse rather than fabricate);
``financial-data-integrity``; ``iranian-payroll-engineering``.
"""

from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from starlette.testclient import TestClient

from app.engines.rules import (
    StatutoryRuleSet,
    clear_active_rule_set_cache,
    load_rule_set,
    validate_invariants,
)
from app.main import create_app
from app.repositories.statutory_repository import (
    InMemoryStatutoryRepository,
    StatutoryRuleSetRecord,
    get_default_statutory_repository,
    set_default_statutory_repository,
)
from app.services.regulatory.sync_service import (
    OFFICIAL_MONITORED_DOMAINS,
    DiscoveredRegulatoryUpdate,
    RegulatorySyncService,
    clear_regulatory_sync_service,
)

MOCK_GROUNDED_UPDATE_PAYLOAD: dict[str, Any] = {
    "candidates": [
        {
            "content": {
                "parts": [
                    {
                        "text": """```json
{
  "found_update": true,
  "refusal_reason": null,
  "year_shamsi": 1404,
  "daily_minimum_wage_rial": 3800000,
  "monthly_housing_allowance_rial": 10000000,
  "monthly_grocery_allowance_rial": 25000000,
  "monthly_tax_exemption_rial": 260000000,
  "tax_brackets": [
    {"slab": 1, "min_rial": 0, "max_rial": 260000000, "rate": "0.00"},
    {"slab": 2, "min_rial": 260000001, "max_rial": 320000000, "rate": "0.10"},
    {"slab": 3, "min_rial": 320000001, "max_rial": 400000000, "rate": "0.15"},
    {"slab": 4, "min_rial": 400000001, "max_rial": 520000000, "rate": "0.20"},
    {"slab": 5, "min_rial": 520000001, "max_rial": 700000000, "rate": "0.25"},
    {"slab": 6, "min_rial": 700000001, "max_rial": null, "rate": "0.30"}
  ],
  "max_daily_insurable_wage_rial": 26600000,
  "court_precedent_active": true,
  "source_circular_reference": "بخشنامه اصلاحی شماره ۳۴۰ شورای عالی کار منتشره در روزنامه رسمی",
  "effective_date": "1404-06-01",
  "source_urls": [
    "https://rrk.ir/laws/circular-340",
    "https://mcls.gov.ir/circulars/wage-340"
  ]
}
```"""
                    }
                ]
            },
            "groundingMetadata": {
                "groundingChunks": [
                    {"web": {"uri": "https://rrk.ir/laws/circular-340"}},
                    {"web": {"uri": "https://mcls.gov.ir/circulars/wage-340"}},
                ]
            },
        }
    ]
}

MOCK_NO_UPDATE_PAYLOAD: dict[str, Any] = {
    "candidates": [
        {
            "content": {
                "parts": [
                    {
                        "text": """```json
{
  "found_update": false,
  "refusal_reason": "هیچ مصوبه یا اصلاحیه جدیدی در روزنامه رسمی یا تارنمای وزارت کار درج نشده است.",
  "year_shamsi": 1404,
  "daily_minimum_wage_rial": 3463656,
  "monthly_housing_allowance_rial": 9000000,
  "monthly_grocery_allowance_rial": 22000000,
  "monthly_tax_exemption_rial": 240000000,
  "tax_brackets": [],
  "max_daily_insurable_wage_rial": 24245592,
  "court_precedent_active": true,
  "source_circular_reference": "",
  "effective_date": "1404-01-01",
  "source_urls": []
}
```"""
                    }
                ]
            },
            "groundingMetadata": {
                "groundingChunks": [
                    {"web": {"uri": "https://rrk.ir/archive"}},
                ]
            },
        }
    ]
}


@pytest.fixture(autouse=True)
def reset_statutory_state() -> Any:
    """Reset repository and engine caches around each test."""
    clear_active_rule_set_cache()
    clear_regulatory_sync_service()
    repo = InMemoryStatutoryRepository(bootstrap=True)
    set_default_statutory_repository(repo)
    yield
    clear_active_rule_set_cache()
    clear_regulatory_sync_service()


class TestRegulatorySyncParsing:
    """Test parsing of grounded official payloads."""

    def test_parse_gazette_update_payload(self) -> None:
        service = RegulatorySyncService()
        parsed = service.parse_gemini_response(MOCK_GROUNDED_UPDATE_PAYLOAD, fallback_year=1404)

        assert parsed.found_update is True
        assert parsed.refusal_reason is None
        assert parsed.year_shamsi == 1404
        assert parsed.daily_minimum_wage_rial == 3_800_000
        assert parsed.monthly_housing_allowance_rial == 10_000_000
        assert parsed.monthly_grocery_allowance_rial == 25_000_000
        assert parsed.monthly_tax_exemption_rial == 260_000_000
        # Invariant check: 7x daily minimum wage
        assert parsed.max_daily_insurable_wage_rial == 3_800_000 * 7
        assert parsed.court_precedent_active is True
        assert "بخشنامه اصلاحی" in parsed.source_circular_reference
        assert "https://rrk.ir/laws/circular-340" in parsed.source_urls
        assert len(parsed.tax_brackets) == 6

    def test_refuse_when_grounding_finds_no_official_circular(self) -> None:
        service = RegulatorySyncService()
        parsed = service.parse_gemini_response(MOCK_NO_UPDATE_PAYLOAD, fallback_year=1404)

        assert parsed.found_update is False
        assert parsed.refusal_reason is not None
        assert "هیچ مصوبه" in parsed.refusal_reason

    def test_parse_handles_malformed_response_fail_closed(self) -> None:
        service = RegulatorySyncService()
        malformed: dict[str, Any] = {
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": "Not a JSON document and no circular found"}]
                    }
                }
            ]
        }
        parsed = service.parse_gemini_response(malformed, fallback_year=1404)
        assert parsed.found_update is False
        assert "JSON" in (parsed.refusal_reason or "")


class TestVersioningAndPersistence:
    """Test database versioning, immutability, and engine integration."""

    @pytest.mark.asyncio
    async def test_initial_repository_contains_immutable_1404_1(self) -> None:
        repo = get_default_statutory_repository()
        record = await repo.get_active_rule_set_record(1404)
        assert record is not None
        assert record.version_id == "1404.1"
        assert record.is_active is True
        assert record.status == "ACTIVE"
        assert record.parameters_json["daily_minimum_wage_rial"] == 3_463_656

    @pytest.mark.asyncio
    async def test_new_amendment_creates_new_version_and_keeps_old_immutable(self) -> None:
        repo = get_default_statutory_repository()
        service = RegulatorySyncService(repository=repo)

        # Mock gemini call to return the amended payload
        with patch.object(
            service,
            "call_gemini_grounding",
            new_callable=AsyncMock,
            return_value=MOCK_GROUNDED_UPDATE_PAYLOAD,
        ):
            outcome = await service.sync(api_key="AIzaSyTestKeyMock")

        assert outcome.status == "success"
        assert outcome.has_changes is True
        assert outcome.previous_version == "1404.1"
        assert outcome.active_version == "1404.2"

        # Verify old version 1404.1 is still preserved and immutable
        old_version = await repo.get_by_version("1404.1")
        assert old_version is not None
        assert old_version.version_id == "1404.1"
        assert old_version.is_active is False
        assert old_version.status == "RETIRED"
        assert old_version.parameters_json["daily_minimum_wage_rial"] == 3_463_656

        # Verify new active version in repository
        active_rec = await repo.get_active_rule_set_record()
        assert active_rec is not None
        assert active_rec.version_id == "1404.2"
        assert active_rec.is_active is True
        assert active_rec.parameters_json["daily_minimum_wage_rial"] == 3_800_000
        assert active_rec.parameters_json["monthly_tax_exemption_rial"] == 260_000_000

        # Verify engine resolves active version
        rule_set = load_rule_set(1404)
        assert rule_set.statutory_version == "1404.2"
        assert rule_set.daily_minimum_wage_rial == 3_800_000
        assert rule_set.monthly_tax_exemption_rial == 260_000_000

        # Verify all invariants pass on the new version
        inv_results = validate_invariants(rule_set)
        assert all(inv_results.values())

    @pytest.mark.asyncio
    async def test_sync_no_change_does_not_create_version(self) -> None:
        repo = get_default_statutory_repository()
        service = RegulatorySyncService(repository=repo)

        with patch.object(
            service,
            "call_gemini_grounding",
            new_callable=AsyncMock,
            return_value=MOCK_NO_UPDATE_PAYLOAD,
        ):
            outcome = await service.sync(api_key="AIzaSyTestKeyMock")

        assert outcome.status == "no_change"
        assert outcome.has_changes is False
        assert outcome.active_version == "1404.1"

        versions = await repo.list_versions()
        assert len(versions) == 1
        assert versions[0].version_id == "1404.1"

    @pytest.mark.asyncio
    async def test_sync_without_api_key_keeps_existing_active_rule_set(self) -> None:
        repo = get_default_statutory_repository()
        service = RegulatorySyncService(repository=repo)

        outcome = await service.sync(api_key=None)
        assert outcome.status == "no_change"
        assert outcome.active_version == "1404.1"
        assert "معتبر حفظ شد" in outcome.message


class TestRegulatoryApiEndpoints:
    """Test API router endpoints for regulatory status and sync."""

    def test_get_regulatory_status_endpoint(self) -> None:
        app = create_app()
        client = TestClient(app)

        res = client.get("/api/v1/regulatory/status")
        assert res.status_code == 200
        data = res.json()
        assert data["active_version"] == "1404.1"
        assert data["year_shamsi"] == 1404
        assert "sources" in data
        assert len(data["sources"]) == len(OFFICIAL_MONITORED_DOMAINS)
        assert any("rrk.ir" in s for s in data["sources"])
        assert any("divan-edalat.ir" in s for s in data["sources"])

    def test_post_regulatory_sync_endpoint_mocked(self) -> None:
        app = create_app()
        client = TestClient(app)

        with patch(
            "app.services.regulatory.sync_service.RegulatorySyncService.call_gemini_grounding",
            new_callable=AsyncMock,
            return_value=MOCK_GROUNDED_UPDATE_PAYLOAD,
        ):
            res = client.post(
                "/api/v1/regulatory/sync",
                json={"gemini_api_key": "AIzaSyTestValidKey"},
            )
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "success"
            assert data["has_changes"] is True
            assert data["active_version"] == "1404.2"
            assert data["previous_version"] == "1404.1"

        # Check status endpoint now reflects updated active version
        res_after = client.get("/api/v1/regulatory/status")
        assert res_after.status_code == 200
        assert res_after.json()["active_version"] == "1404.2"

        # Check CTC breakdown endpoint now automatically resolves the active 1404.2 version
        ctc_res = client.post(
            "/api/v1/simulations/salary-ctc-breakdown",
            json={"gross_salary_rial": 400_000_000, "year": 1404, "month_days": 30},
        )
        assert ctc_res.status_code == 200
        ctc_data = ctc_res.json()
        assert ctc_data["rule_version"] == "1404.2"
