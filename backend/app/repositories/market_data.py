"""Market reference data repository.

Authority
---------
``docs/adr/ADR-014-market-salary-reference-data-and-estimation.md`` §8;
``docs/specs/DEPLOYMENT.md`` §5.1 (the database is reached only through
``DATABASE_URL``); ``AGENTS.md`` §2 Security invariant 10 (fail closed — no
fallback data).

Related
-------
``app/models/estimation.py`` (tables), ``app/domain/salary_estimation/market_data.py``
(value objects), ``app/db.py`` (session factory).

Scope
-----
Two implementations of one protocol: PostgreSQL for the application, and an
in-memory store used by tests and by the explicitly-enabled development sample
mode.  **No repository invents data**: an empty table yields an empty sequence,
and the estimator then refuses.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.salary_estimation import sample_data
from app.domain.salary_estimation.market_data import (
    MarketAggregate,
    MarketObservation,
    MarketSource,
)
from app.models.estimation import (
    MarketDataSource,
    MarketSalaryAggregate,
    MarketSalaryObservation,
)

__all__ = (
    "InMemoryMarketDataRepository",
    "MarketDataRepository",
    "SqlMarketDataRepository",
    "repository_for_sample_mode",
)


class MarketDataRepository(Protocol):
    """What the estimation service needs from storage."""

    async def observations_for(self, family_key: str) -> Sequence[MarketObservation]:
        """Return every observation of *family_key* (classified later)."""
        ...

    async def aggregates_for(self, family_key: str) -> Sequence[MarketAggregate]:
        """Return every published aggregate of *family_key*."""
        ...

    async def sources(self) -> Sequence[MarketSource]:
        """Return the registered sources with their licence state."""
        ...

    async def store_source(self, source: MarketSource) -> None:
        """Register or update one source."""
        ...

    async def store_observations(self, rows: Sequence[MarketObservation]) -> int:
        """Insert observations; return the number written."""
        ...

    async def store_aggregates(self, rows: Sequence[MarketAggregate]) -> int:
        """Insert aggregates; return the number written."""
        ...

    async def record_quality(self, observation_id: str, status: str, reason: str | None) -> None:
        """Persist a verdict so a quarantined row stays traceable."""
        ...


def _observation_from_row(row: MarketSalaryObservation) -> MarketObservation:
    """Map an ORM row to the domain value object."""
    return MarketObservation(
        id=row.id,
        family_key=row.family_key,
        job_title_reported=row.job_title_reported,
        city=row.city,
        province=row.province,
        seniority_level=row.seniority_level,
        experience_years=row.experience_years,
        employment_type=row.employment_type,
        work_condition=row.work_condition,
        amount_rial=row.amount_rial,
        period=row.period,
        currency_unit_reported=row.currency_unit_reported,
        source_id=row.source_id,
        source_url=row.source_url,
        license_status=row.license_status,
        collected_at=row.collected_at,
        is_synthetic=row.is_synthetic,
        data_quality_status=row.data_quality_status,
        quality_reason=row.quality_reason,
    )


def _aggregate_from_row(row: MarketSalaryAggregate) -> MarketAggregate:
    """Map an ORM row to the domain value object."""
    return MarketAggregate(
        id=row.id,
        family_key=row.family_key,
        city=row.city,
        province=row.province,
        seniority_level=row.seniority_level,
        employment_type=row.employment_type,
        median_salary_rial=row.published_median_rial,
        min_salary_rial=row.published_min_rial,
        max_salary_rial=row.published_max_rial,
        p25_salary_rial=row.published_p25_rial,
        p75_salary_rial=row.published_p75_rial,
        sample_size=row.sample_size,
        period=row.period,
        currency_unit_reported=row.currency_unit_reported,
        source_id=row.source_id,
        source_url=row.source_url,
        license_status=row.license_status,
        collected_at=row.collected_at,
        is_synthetic=row.is_synthetic,
    )


def _observation_to_row(observation: MarketObservation) -> MarketSalaryObservation:
    """Map a domain value object to an ORM row."""
    return MarketSalaryObservation(
        id=observation.id,
        family_key=observation.family_key,
        job_title_reported=observation.job_title_reported,
        city=observation.city,
        province=observation.province,
        seniority_level=observation.seniority_level,
        experience_years=observation.experience_years,
        employment_type=observation.employment_type,
        work_condition=observation.work_condition,
        amount_rial=observation.amount_rial,
        period=observation.period,
        currency_unit_reported=observation.currency_unit_reported,
        source_id=observation.source_id,
        source_url=observation.source_url,
        license_status=observation.license_status,
        collected_at=observation.collected_at,
        is_synthetic=observation.is_synthetic,
        data_quality_status=observation.data_quality_status,
        quality_reason=observation.quality_reason,
    )


def _aggregate_to_row(aggregate: MarketAggregate) -> MarketSalaryAggregate:
    """Map a domain value object to an ORM row."""
    return MarketSalaryAggregate(
        id=aggregate.id,
        family_key=aggregate.family_key,
        city=aggregate.city,
        province=aggregate.province,
        seniority_level=aggregate.seniority_level,
        employment_type=aggregate.employment_type,
        published_min_rial=aggregate.min_salary_rial,
        published_p25_rial=aggregate.p25_salary_rial,
        published_median_rial=aggregate.median_salary_rial,
        published_p75_rial=aggregate.p75_salary_rial,
        published_max_rial=aggregate.max_salary_rial,
        sample_size=aggregate.sample_size,
        period=aggregate.period,
        currency_unit_reported=aggregate.currency_unit_reported,
        source_id=aggregate.source_id,
        source_url=aggregate.source_url,
        license_status=aggregate.license_status,
        collected_at=aggregate.collected_at,
        is_synthetic=aggregate.is_synthetic,
    )


class SqlMarketDataRepository:
    """PostgreSQL implementation of :class:`MarketDataRepository`."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def observations_for(self, family_key: str) -> Sequence[MarketObservation]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(MarketSalaryObservation)
                .where(MarketSalaryObservation.family_key == family_key)
                .order_by(
                    MarketSalaryObservation.collected_at,
                    MarketSalaryObservation.id,
                )
            )
            return tuple(_observation_from_row(row) for row in result.scalars())

    async def aggregates_for(self, family_key: str) -> Sequence[MarketAggregate]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(MarketSalaryAggregate).where(
                    MarketSalaryAggregate.family_key == family_key
                )
            )
            return tuple(_aggregate_from_row(row) for row in result.scalars())

    async def sources(self) -> Sequence[MarketSource]:
        async with self._session_factory() as session:
            result = await session.execute(select(MarketDataSource))
            return tuple(
                MarketSource(
                    id=row.id,
                    name=row.name,
                    kind=row.kind,
                    license_status=row.license_status,
                    connected=row.connected,
                    terms_url=row.terms_url,
                    notes=row.notes,
                )
                for row in result.scalars()
            )

    async def store_source(self, source: MarketSource) -> None:
        async with self._session_factory() as session:
            existing = await session.get(MarketDataSource, source.id)
            if existing is None:
                session.add(
                    MarketDataSource(
                        id=source.id,
                        name=source.name,
                        kind=source.kind,
                        license_status=source.license_status,
                        connected=source.connected,
                        terms_url=source.terms_url,
                        notes=source.notes,
                    )
                )
            else:
                existing.name = source.name
                existing.kind = source.kind
                existing.license_status = source.license_status
                existing.connected = source.connected
                existing.terms_url = source.terms_url
                existing.notes = source.notes
            await session.commit()

    async def store_observations(self, rows: Sequence[MarketObservation]) -> int:
        async with self._session_factory() as session:
            for row in rows:
                session.add(_observation_to_row(row))
            await session.commit()
            return len(rows)

    async def store_aggregates(self, rows: Sequence[MarketAggregate]) -> int:
        async with self._session_factory() as session:
            for row in rows:
                session.add(_aggregate_to_row(row))
            await session.commit()
            return len(rows)

    async def record_quality(self, observation_id: str, status: str, reason: str | None) -> None:
        async with self._session_factory() as session:
            row = await session.get(MarketSalaryObservation, observation_id)
            if row is None:
                return
            row.data_quality_status = status
            row.quality_reason = reason
            await session.commit()


class InMemoryMarketDataRepository:
    """Test / development implementation.

    The sample mode is selected by ``ESTIMATION_ALLOW_SAMPLE_DATA``, which the
    production configuration refuses to enable.
    """

    def __init__(
        self,
        observations: Sequence[MarketObservation] = (),
        aggregates: Sequence[MarketAggregate] = (),
        sources: Sequence[MarketSource] = (),
    ) -> None:
        self._observations: dict[str, MarketObservation] = {row.id: row for row in observations}
        self._aggregates: dict[str, MarketAggregate] = {row.id: row for row in aggregates}
        self._sources: dict[str, MarketSource] = {row.id: row for row in sources}

    async def observations_for(self, family_key: str) -> Sequence[MarketObservation]:
        return tuple(row for row in self._observations.values() if row.family_key == family_key)

    async def aggregates_for(self, family_key: str) -> Sequence[MarketAggregate]:
        return tuple(row for row in self._aggregates.values() if row.family_key == family_key)

    async def sources(self) -> Sequence[MarketSource]:
        return tuple(self._sources.values())

    async def store_source(self, source: MarketSource) -> None:
        self._sources[source.id] = source

    async def store_observations(self, rows: Sequence[MarketObservation]) -> int:
        for row in rows:
            self._observations[row.id] = row
        return len(rows)

    async def store_aggregates(self, rows: Sequence[MarketAggregate]) -> int:
        for row in rows:
            self._aggregates[row.id] = row
        return len(rows)

    async def record_quality(self, observation_id: str, status: str, reason: str | None) -> None:
        row = self._observations.get(observation_id)
        if row is None:
            return
        self._observations[observation_id] = replace(
            row,
            data_quality_status=status,
            quality_reason=reason,
        )


def repository_for_sample_mode() -> InMemoryMarketDataRepository:
    """Return the explicitly-labelled development repository."""
    return InMemoryMarketDataRepository(
        observations=sample_data.sample_observations(),
        aggregates=sample_data.sample_aggregates(),
        sources=sample_data.sample_sources(),
    )
