"""Market-data repository behaviour (in-memory implementation).

Authority: ``docs/adr/ADR-014-market-salary-reference-data-and-estimation.md`` §8.
The repository is the only place that knows about storage; these tests pin that it
never invents a row, that it filters by family, and that a quarantine verdict is
persisted for traceability.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.domain.salary_estimation.market_data import (
    DataQuality,
    MarketAggregate,
    MarketObservation,
    MarketSource,
)
from app.repositories.market_data import (
    InMemoryMarketDataRepository,
    repository_for_sample_mode,
)

COLLECTED = datetime(2026, 9, 1, tzinfo=UTC)


def observation(identifier: str, *, family: str = "php_backend") -> MarketObservation:
    """Build one observation."""
    return MarketObservation(
        id=identifier,
        family_key=family,
        job_title_reported="برنامه‌نویس PHP",
        city="تهران",
        amount_rial=500_000_000,
        period="monthly",
        currency_unit_reported="rial",
        source_id="manual-verified-manager",
        license_status="manual_verified",
        collected_at=COLLECTED,
        seniority_level="mid",
    )


@pytest.mark.asyncio
async def test_observations_are_filtered_by_family() -> None:
    repository = InMemoryMarketDataRepository(
        observations=(observation("a"), observation("b", family="accountant"))
    )
    rows = await repository.observations_for("php_backend")
    assert [row.id for row in rows] == ["a"]


@pytest.mark.asyncio
async def test_an_empty_store_returns_nothing() -> None:
    repository = InMemoryMarketDataRepository()
    assert await repository.observations_for("php_backend") == ()
    assert await repository.aggregates_for("php_backend") == ()
    assert await repository.sources() == ()


@pytest.mark.asyncio
async def test_quarantine_verdict_is_persisted() -> None:
    repository = InMemoryMarketDataRepository(observations=(observation("a"),))
    await repository.record_quality("a", DataQuality.SUSPICIOUS, "stale_data")
    rows = await repository.observations_for("php_backend")
    assert rows[0].data_quality_status == DataQuality.SUSPICIOUS
    assert rows[0].quality_reason == "stale_data"


@pytest.mark.asyncio
async def test_store_and_source_round_trip() -> None:
    repository = InMemoryMarketDataRepository()
    await repository.store_source(
        MarketSource(
            id="manual-verified-manager",
            name="ورود دستی تأییدشده مدیر",
            kind="manual",
            license_status="manual_verified",
            connected=True,
        )
    )
    written = await repository.store_observations((observation("a"),))
    assert written == 1
    assert len(await repository.sources()) == 1

    aggregate = MarketAggregate(
        id="agg-1",
        family_key="qa_engineer",
        city="تهران",
        median_salary_rial=330_000_000,
        sample_size=42,
        source_id="manual-verified-manager",
        license_status="manual_verified",
        collected_at=COLLECTED,
    )
    assert await repository.store_aggregates((aggregate,)) == 1
    assert len(await repository.aggregates_for("qa_engineer")) == 1


@pytest.mark.asyncio
async def test_sample_mode_is_explicitly_synthetic() -> None:
    repository = repository_for_sample_mode()
    rows = await repository.observations_for("php_backend")
    assert rows, "the sample dataset must exist for local development"
    assert all(row.is_synthetic for row in rows)
    assert all(row.license_status == "synthetic_dev" for row in rows)
    sources = await repository.sources()
    assert all(source.license_status == "synthetic_dev" for source in sources)
    # No row may name a real publication.
    forbidden = {"jobinja", "jobvision", "irantalent", "iransalary", "quera"}
    for row in rows:
        assert row.source_id.lower() not in forbidden
        assert not any(name in row.source_id.lower() for name in forbidden)


@pytest.mark.asyncio
async def test_quality_is_recorded_even_for_an_unknown_id() -> None:
    repository = InMemoryMarketDataRepository()
    await repository.record_quality("missing", DataQuality.REJECTED, "reason")
    assert await repository.observations_for("php_backend") == ()
