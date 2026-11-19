"""Statutory rule-set repository and persistence layer.

Authority
---------
ADR-007 (global statutory schema); ADR-008 (statutory rule versioning);
``docs/specs/DEPLOYMENT.md`` §5.1; ``financial-data-integrity`` §16;
``AGENTS.md`` §2 Invariants 7-12 (deterministic reproducibility, immutable versions).

Scope
-----
Persists and retrieves versioned statutory rule sets from the PostgreSQL database
table ``statutory_rule_set_versions``, with an in-memory implementation for testing
and decoupled environments. Automatically bootstraps the active 1404 baseline
from ``backend/data/seeds/statutory_rules_1404.yaml`` when empty.
"""

from __future__ import annotations

import datetime
import uuid
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

import yaml
from sqlalchemy import desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.statutory import StatutoryRuleSetVersion

__all__ = (
    "InMemoryStatutoryRepository",
    "SqlStatutoryRepository",
    "StatutoryRepository",
    "StatutoryRuleSetRecord",
    "get_default_statutory_repository",
    "set_default_statutory_repository",
)

_SEEDS_DIR = Path(__file__).resolve().parents[2] / "data" / "seeds"


@dataclass(frozen=True, slots=True)
class StatutoryRuleSetRecord:
    """One immutable stored revision of a statutory rule set."""

    id: uuid.UUID
    version_id: str  # e.g. "1404.1", "1404.2", "1405.1"
    rule_year_shamsi: int
    revision: int
    effective_from: datetime.date
    effective_to: datetime.date | None
    supersedes_id: uuid.UUID | None
    status: str
    is_active: bool
    source_reference: str
    source_urls: tuple[str, ...]
    parameters_json: dict[str, Any]
    created_at: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )


class StatutoryRepository(Protocol):
    """Protocol for statutory rule-set storage and version retrieval."""

    async def get_active_rule_set_record(
        self, year: int | None = None
    ) -> StatutoryRuleSetRecord | None:
        """Return the active rule set for the given year (or latest active)."""
        ...

    async def get_by_version(self, version_id: str) -> StatutoryRuleSetRecord | None:
        """Return a specific immutable version by version_id (e.g. '1404.1')."""
        ...

    async def list_versions(
        self, year: int | None = None
    ) -> Sequence[StatutoryRuleSetRecord]:
        """List all versioned rule sets ordered by year and revision."""
        ...

    async def save_new_version(
        self,
        *,
        version_id: str,
        effective_from: datetime.date,
        source_reference: str,
        source_urls: Sequence[str],
        parameters_json: dict[str, Any],
        is_active: bool = True,
        supersedes_id: uuid.UUID | None = None,
        effective_to: datetime.date | None = None,
        status: str = "ACTIVE",
    ) -> StatutoryRuleSetRecord:
        """Persist a new version, optionally superseding previous revisions."""
        ...


def _parse_version_id(version_id: str) -> tuple[int, int]:
    """Split '1404.1' into (1404, 1)."""
    parts = version_id.strip().split(".")
    if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
        raise ValueError(
            f"Invalid version_id format '{version_id}'. Expected 'YYYY.R' e.g. '1404.1'"
        )
    return int(parts[0]), int(parts[1])


def _load_seed_1404_dict() -> tuple[dict[str, Any], datetime.date, str]:
    """Read the verified 1404 seed file as a baseline dictionary."""
    seed_path = _SEEDS_DIR / "statutory_rules_1404.yaml"
    text = seed_path.read_text(encoding="utf-8")
    loaded = yaml.safe_load(text)
    if not isinstance(loaded, dict):
        raise RuntimeError("Seed statutory_rules_1404.yaml is not a valid YAML dictionary")

    effective_str = str(loaded.get("effective_date", "1404-01-01"))
    # Approximate Shamsi 1404-01-01 to Gregorian 2025-03-21 for standard date storage
    effective_from = datetime.date(2025, 3, 21)
    source_ref = str(
        loaded.get(
            "source_circular_reference",
            "335th High Council of Labor Wage Circular & 1404 Budget Law",
        )
    )

    # Convert numeric types to JSON serializable objects
    parameters_json: dict[str, Any] = {"effective_date": effective_str}
    for k, v in loaded.items():
        if isinstance(v, (int, float, str, bool, list, dict)) or v is None:
            parameters_json[str(k)] = v
        else:
            parameters_json[str(k)] = str(v)

    # Ensure metadata
    parameters_json["rule_year_shamsi"] = 1404
    parameters_json["court_precedent_active"] = True

    return parameters_json, effective_from, source_ref


def bootstrap_baseline_record() -> StatutoryRuleSetRecord:
    """Create the baseline 1404.1 record from verified seed."""
    params, effective_from, source_ref = _load_seed_1404_dict()
    return StatutoryRuleSetRecord(
        id=uuid.UUID("14040000-0000-4000-8000-000000000001"),
        version_id="1404.1",
        rule_year_shamsi=1404,
        revision=1,
        effective_from=effective_from,
        effective_to=None,
        supersedes_id=None,
        status="ACTIVE",
        is_active=True,
        source_reference=source_ref,
        source_urls=(
            "https://rrk.ir",
            "https://mcls.gov.ir",
            "https://intamedia.ir",
        ),
        parameters_json=params,
        created_at=datetime.datetime(2025, 3, 21, 0, 0, 0, tzinfo=datetime.UTC),
    )


class InMemoryStatutoryRepository:
    """In-memory implementation for tests, dev mode, and offline execution."""

    def __init__(self, bootstrap: bool = True) -> None:
        self._records: dict[str, StatutoryRuleSetRecord] = {}
        if bootstrap:
            rec = bootstrap_baseline_record()
            self._records[rec.version_id] = rec

    async def get_active_rule_set_record(
        self, year: int | None = None
    ) -> StatutoryRuleSetRecord | None:
        active = [
            r
            for r in self._records.values()
            if r.is_active and (year is None or r.rule_year_shamsi == year)
        ]
        if not active:
            return None
        # Return highest revision
        return max(active, key=lambda r: (r.rule_year_shamsi, r.revision))

    async def get_by_version(self, version_id: str) -> StatutoryRuleSetRecord | None:
        return self._records.get(version_id)

    async def list_versions(
        self, year: int | None = None
    ) -> Sequence[StatutoryRuleSetRecord]:
        items = [
            r
            for r in self._records.values()
            if year is None or r.rule_year_shamsi == year
        ]
        return sorted(items, key=lambda r: (r.rule_year_shamsi, r.revision))

    async def save_new_version(
        self,
        *,
        version_id: str,
        effective_from: datetime.date,
        source_reference: str,
        source_urls: Sequence[str],
        parameters_json: dict[str, Any],
        is_active: bool = True,
        supersedes_id: uuid.UUID | None = None,
        effective_to: datetime.date | None = None,
        status: str = "ACTIVE",
    ) -> StatutoryRuleSetRecord:
        year, rev = _parse_version_id(version_id)

        # Deactivate previous versions of same year if new one is active
        if is_active:
            for k, r in list(self._records.items()):
                if r.rule_year_shamsi == year and r.is_active:
                    self._records[k] = StatutoryRuleSetRecord(
                        id=r.id,
                        version_id=r.version_id,
                        rule_year_shamsi=r.rule_year_shamsi,
                        revision=r.revision,
                        effective_from=r.effective_from,
                        effective_to=effective_from,
                        supersedes_id=r.supersedes_id,
                        status="RETIRED",
                        is_active=False,
                        source_reference=r.source_reference,
                        source_urls=r.source_urls,
                        parameters_json=r.parameters_json,
                        created_at=r.created_at,
                    )

        new_record = StatutoryRuleSetRecord(
            id=uuid.uuid4(),
            version_id=version_id,
            rule_year_shamsi=year,
            revision=rev,
            effective_from=effective_from,
            effective_to=effective_to,
            supersedes_id=supersedes_id,
            status=status,
            is_active=is_active,
            source_reference=source_reference,
            source_urls=tuple(source_urls),
            parameters_json=dict(parameters_json),
            created_at=datetime.datetime.now(datetime.UTC),
        )
        self._records[version_id] = new_record
        return new_record


def _row_to_record(row: StatutoryRuleSetVersion) -> StatutoryRuleSetRecord:
    """Map SQLAlchemy ORM row to domain record."""
    version_id = f"{row.rule_year_shamsi}.{row.revision}"
    manifest = row.source_manifest if isinstance(row.source_manifest, list) else []
    source_ref = ""
    source_urls: list[str] = []
    if manifest and isinstance(manifest[0], dict):
        source_ref = str(manifest[0].get("source_reference", ""))
        urls = manifest[0].get("source_urls", [])
        if isinstance(urls, list):
            source_urls = [str(u) for u in urls]

    params = row.parameter_snapshot if isinstance(row.parameter_snapshot, dict) else {}

    return StatutoryRuleSetRecord(
        id=row.id,
        version_id=version_id,
        rule_year_shamsi=row.rule_year_shamsi,
        revision=row.revision,
        effective_from=row.effective_from,
        effective_to=row.effective_to,
        supersedes_id=row.supersedes_id,
        status=row.status,
        is_active=row.is_active,
        source_reference=source_ref,
        source_urls=tuple(source_urls),
        parameters_json=params,
        created_at=row.created_at,
    )


class SqlStatutoryRepository:
    """PostgreSQL implementation of StatutoryRepository."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def _ensure_bootstrapped(self, session: AsyncSession) -> None:
        """Seed baseline 1404.1 into empty database table."""
        stmt = select(StatutoryRuleSetVersion).limit(1)
        res = await session.execute(stmt)
        if res.scalar_one_or_none() is None:
            baseline = bootstrap_baseline_record()
            manifest = [
                {
                    "source_reference": baseline.source_reference,
                    "source_urls": list(baseline.source_urls),
                }
            ]
            row = StatutoryRuleSetVersion(
                id=baseline.id,
                rule_year_shamsi=baseline.rule_year_shamsi,
                revision=baseline.revision,
                effective_from=baseline.effective_from,
                effective_to=baseline.effective_to,
                supersedes_id=baseline.supersedes_id,
                status=baseline.status,
                is_active=baseline.is_active,
                source_manifest=manifest,
                parameter_snapshot=baseline.parameters_json,
                verified_at=baseline.created_at,
                verified_by=None,
                created_at=baseline.created_at,
            )
            session.add(row)
            await session.commit()

    async def get_active_rule_set_record(
        self, year: int | None = None
    ) -> StatutoryRuleSetRecord | None:
        async with self._session_factory() as session:
            await self._ensure_bootstrapped(session)
            stmt = select(StatutoryRuleSetVersion).where(
                StatutoryRuleSetVersion.is_active.is_(True)
            )
            if year is not None:
                stmt = stmt.where(StatutoryRuleSetVersion.rule_year_shamsi == year)
            stmt = stmt.order_by(
                desc(StatutoryRuleSetVersion.rule_year_shamsi),
                desc(StatutoryRuleSetVersion.revision),
            )
            res = await session.execute(stmt)
            row = res.scalars().first()
            return _row_to_record(row) if row is not None else None

    async def get_by_version(self, version_id: str) -> StatutoryRuleSetRecord | None:
        year, rev = _parse_version_id(version_id)
        async with self._session_factory() as session:
            await self._ensure_bootstrapped(session)
            stmt = select(StatutoryRuleSetVersion).where(
                StatutoryRuleSetVersion.rule_year_shamsi == year,
                StatutoryRuleSetVersion.revision == rev,
            )
            res = await session.execute(stmt)
            row = res.scalar_one_or_none()
            return _row_to_record(row) if row is not None else None

    async def list_versions(
        self, year: int | None = None
    ) -> Sequence[StatutoryRuleSetRecord]:
        async with self._session_factory() as session:
            await self._ensure_bootstrapped(session)
            stmt = select(StatutoryRuleSetVersion)
            if year is not None:
                stmt = stmt.where(StatutoryRuleSetVersion.rule_year_shamsi == year)
            stmt = stmt.order_by(
                StatutoryRuleSetVersion.rule_year_shamsi,
                StatutoryRuleSetVersion.revision,
            )
            res = await session.execute(stmt)
            return tuple(_row_to_record(row) for row in res.scalars().all())

    async def save_new_version(
        self,
        *,
        version_id: str,
        effective_from: datetime.date,
        source_reference: str,
        source_urls: Sequence[str],
        parameters_json: dict[str, Any],
        is_active: bool = True,
        supersedes_id: uuid.UUID | None = None,
        effective_to: datetime.date | None = None,
        status: str = "ACTIVE",
    ) -> StatutoryRuleSetRecord:
        year, rev = _parse_version_id(version_id)
        new_id = uuid.uuid4()
        now = datetime.datetime.now(datetime.UTC)
        manifest = [
            {
                "source_reference": source_reference,
                "source_urls": list(source_urls),
            }
        ]

        async with self._session_factory() as session:
            if is_active:
                # Deactivate older versions of the same year
                await session.execute(
                    update(StatutoryRuleSetVersion)
                    .where(
                        StatutoryRuleSetVersion.rule_year_shamsi == year,
                        StatutoryRuleSetVersion.is_active.is_(True),
                    )
                    .values(
                        is_active=False,
                        status="RETIRED",
                        effective_to=effective_from,
                    )
                )

            row = StatutoryRuleSetVersion(
                id=new_id,
                rule_year_shamsi=year,
                revision=rev,
                effective_from=effective_from,
                effective_to=effective_to,
                supersedes_id=supersedes_id,
                status=status,
                is_active=is_active,
                source_manifest=manifest,
                parameter_snapshot=parameters_json,
                verified_at=now,
                verified_by=None,
                created_at=now,
            )
            session.add(row)
            await session.commit()
            return _row_to_record(row)


class _RepositoryContainer:
    instance: StatutoryRepository | None = None


def get_default_statutory_repository() -> StatutoryRepository:
    """Return the default repository instance, fallback to in-memory."""
    if _RepositoryContainer.instance is None:
        _RepositoryContainer.instance = InMemoryStatutoryRepository(bootstrap=True)
    return _RepositoryContainer.instance


def set_default_statutory_repository(repo: StatutoryRepository) -> None:
    """Set the default statutory repository."""
    _RepositoryContainer.instance = repo
