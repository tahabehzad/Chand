"""Market reference data models (salary estimation, ADR-014).

Authority
---------
``docs/adr/ADR-014-market-salary-reference-data-and-estimation.md`` §3 (one data
architecture, two data kinds); ``docs/LABOR_MARKET_DATA_SPEC.md`` (source,
licence, collection date and currency unit on every record);
``docs/DATA_MODEL_SPEC.md`` (revisions).

Related
-------
``alembic/versions/0007_market_salary_reference.py`` (the migration that creates
these tables); ``app/repositories/market_data.py`` (the only reader);
``app/domain/salary_estimation/market_data.py`` (the value objects).

Scope
-----
Three **global reference** tables and nothing else:

* ``market_data_sources`` — the registry, with the licence state and whether data
  has actually been received (``connected``).
* ``market_salary_observations`` — data kind A: one independently reported salary.
* ``market_salary_aggregates`` — data kind B: one published summary.

No personal data is stored here, so no ``tenant_id`` and no RLS applies: these are
shared reference records, the same posture ADR-007 gives the statutory catalogue.
Candidate estimates are **not** modelled here: persisting a candidate profile needs
the tenancy decision recorded as DEC-016 (OPEN — BLOCKING), and inventing an
untenanted table for personal data would weaken ``AGENTS.md`` §2 invariant 12
without owner approval.

Superseded draft models
-----------------------
The previous draft of this module declared ``candidate_estimates``,
``market_salary_data``, ``resume_uploads`` and ``estimation_users``.  None was ever
created by a migration, no repository read them and no endpoint wrote them; the
salary-estimation table list in the integration test named them, which made that
test unpassable.  They are replaced by the three tables actually delivered.
"""

from __future__ import annotations

import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base

__all__ = (
    "LICENSE_STATUSES",
    "PAY_PERIODS",
    "QUALITY_STATUSES",
    "MarketDataSource",
    "MarketSalaryAggregate",
    "MarketSalaryObservation",
)

#: Licence states a source may declare.  Only ``licensed``,
#: ``published_report`` and ``manual_verified`` may inform an estimate
#: (``domain/salary_estimation/market_data.py``).
LICENSE_STATUSES = ("licensed", "published_report", "manual_verified", "synthetic_dev", "unknown")
PAY_PERIODS = ("monthly", "hourly", "daily")
QUALITY_STATUSES = ("valid", "suspicious", "rejected")


def _in_list(values: tuple[str, ...]) -> str:
    """Render a SQL ``IN`` list from Python string literals."""
    return ", ".join(f"'{value}'" for value in values)


class MarketDataSource(Base):
    """One market-data source and its licence state."""

    __tablename__ = "market_data_sources"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    license_status: Mapped[str] = mapped_column(String(24), nullable=False)
    connected: Mapped[bool] = mapped_column(Boolean(), nullable=False, server_default="false")
    terms_url: Mapped[str | None] = mapped_column(Text(), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            f"license_status IN ({_in_list(LICENSE_STATUSES)})",
            name="ck_market_data_sources_license_status",
        ),
        CheckConstraint(
            "kind IN ('licensed_survey','published_report','job_board','manual','synthetic')",
            name="ck_market_data_sources_kind",
        ),
    )


class MarketSalaryObservation(Base):
    """Data kind A — one independently reported salary."""

    __tablename__ = "market_salary_observations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    family_key: Mapped[str] = mapped_column(String(64), nullable=False)
    job_title_reported: Mapped[str] = mapped_column(String(200), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    province: Mapped[str | None] = mapped_column(String(100), nullable=True)
    seniority_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    experience_years: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    employment_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    work_condition: Mapped[str | None] = mapped_column(String(20), nullable=True)
    amount_rial: Mapped[int] = mapped_column(BigInteger(), nullable=False)
    period: Mapped[str] = mapped_column(String(10), nullable=False)
    currency_unit_reported: Mapped[str] = mapped_column(String(10), nullable=False)
    source_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("market_data_sources.id"), nullable=False
    )
    source_url: Mapped[str | None] = mapped_column(Text(), nullable=True)
    license_status: Mapped[str] = mapped_column(String(24), nullable=False)
    collected_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    is_synthetic: Mapped[bool] = mapped_column(Boolean(), nullable=False, server_default="false")
    data_quality_status: Mapped[str] = mapped_column(
        String(16), nullable=False, server_default="valid"
    )
    quality_reason: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint("amount_rial > 0", name="ck_market_observations_amount_positive"),
        CheckConstraint(
            f"period IN ({_in_list(PAY_PERIODS)})",
            name="ck_market_observations_period",
        ),
        CheckConstraint(
            "currency_unit_reported IN ('rial','toman')",
            name="ck_market_observations_currency",
        ),
        CheckConstraint(
            f"license_status IN ({_in_list(LICENSE_STATUSES)})",
            name="ck_market_observations_license_status",
        ),
        CheckConstraint(
            f"data_quality_status IN ({_in_list(QUALITY_STATUSES)})",
            name="ck_market_observations_quality",
        ),
        Index(
            "ix_market_observations_cohort",
            "family_key",
            "city",
            "seniority_level",
        ),
        Index("ix_market_observations_collected", "collected_at"),
    )


class MarketSalaryAggregate(Base):
    """Data kind B — one published summary (own range columns, never merged with A)."""

    __tablename__ = "market_salary_aggregates"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    family_key: Mapped[str] = mapped_column(String(64), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    province: Mapped[str | None] = mapped_column(String(100), nullable=True)
    seniority_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    employment_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    published_min_rial: Mapped[int | None] = mapped_column(BigInteger(), nullable=True)
    published_p25_rial: Mapped[int | None] = mapped_column(BigInteger(), nullable=True)
    published_median_rial: Mapped[int] = mapped_column(BigInteger(), nullable=False)
    published_p75_rial: Mapped[int | None] = mapped_column(BigInteger(), nullable=True)
    published_max_rial: Mapped[int | None] = mapped_column(BigInteger(), nullable=True)
    sample_size: Mapped[int] = mapped_column(Integer(), nullable=False)
    period: Mapped[str] = mapped_column(String(10), nullable=False, server_default="monthly")
    currency_unit_reported: Mapped[str] = mapped_column(
        String(10), nullable=False, server_default="rial"
    )
    source_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("market_data_sources.id"), nullable=False
    )
    source_url: Mapped[str | None] = mapped_column(Text(), nullable=True)
    license_status: Mapped[str] = mapped_column(String(24), nullable=False)
    collected_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    is_synthetic: Mapped[bool] = mapped_column(Boolean(), nullable=False, server_default="false")
    data_quality_status: Mapped[str] = mapped_column(
        String(16), nullable=False, server_default="valid"
    )
    quality_reason: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint("sample_size > 0", name="ck_market_aggregates_sample_size"),
        CheckConstraint("published_median_rial > 0", name="ck_market_aggregates_median_positive"),
        CheckConstraint(
            "published_min_rial IS NULL OR published_max_rial IS NULL "
            "OR published_min_rial <= published_max_rial",
            name="ck_market_aggregates_range",
        ),
        CheckConstraint(
            f"period IN ({_in_list(PAY_PERIODS)})",
            name="ck_market_aggregates_period",
        ),
        CheckConstraint(
            "currency_unit_reported IN ('rial','toman')",
            name="ck_market_aggregates_currency",
        ),
        CheckConstraint(
            f"license_status IN ({_in_list(LICENSE_STATUSES)})",
            name="ck_market_aggregates_license_status",
        ),
        CheckConstraint(
            f"data_quality_status IN ({_in_list(QUALITY_STATUSES)})",
            name="ck_market_aggregates_quality",
        ),
        Index("ix_market_aggregates_cohort", "family_key", "city", "seniority_level"),
    )
