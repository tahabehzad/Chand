"""Market-data value objects shared by the estimator, the validator and the
repository layer.

Authority
---------
``docs/adr/ADR-014-market-salary-reference-data-and-estimation.md`` §2 (two data
kinds that must never be confused: individual observations and published
aggregates); ``docs/LABOR_MARKET_DATA_SPEC.md`` (source attribution, licence
status, collection date, currency unit per record).

Related
-------
``app/repositories/market_data.py`` builds these from PostgreSQL;
``validation.py`` classifies observations; ``salary_estimator.py`` publishes the
quantiles.

Scope
-----
Immutable records plus the query value object.  No SQL, no I/O, no clock reads.
Every amount is a whole Rial integer; the *period* and the *reported currency*
travel with the record so a normalisation can never be silently assumed.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from app.engines.money import to_decimal

__all__ = (
    "APPROVED_LICENSE_STATUSES",
    "DataQuality",
    "MarketAggregate",
    "MarketObservation",
    "MarketSource",
    "ObservationFinding",
    "PeerCohort",
    "ValidationOutcome",
    "monthly_equivalent_rial",
)

#: Licence states that may contribute to a published estimate.  ``synthetic_dev``
#: and ``unknown`` are deliberately absent: a sample row or an unattributed row
#: is never market evidence.
APPROVED_LICENSE_STATUSES: frozenset[str] = frozenset(
    {"licensed", "published_report", "manual_verified"}
)

#: A development-only row.  It may be served only when the application is
#: explicitly configured to allow sample data (``ESTIMATION_ALLOW_SAMPLE_DATA``),
#: which the production configuration refuses to start with.
SYNTHETIC_LICENSE_STATUS = "synthetic_dev"

#: Documented conversion assumptions.  They are NOT statutory divisors and are
#: never used for payroll: they exist only to turn a reported hourly or daily
#: market rate into a monthly comparison figure.  Every converted row carries a
#: warning so the assumption is visible in the output.
HOURS_PER_MONTH = Decimal("176")
DAYS_PER_MONTH = Decimal("30")


class DataQuality:
    """The three validation outcomes (``docs/adr/ADR-014`` §2.3)."""

    VALID = "valid"
    SUSPICIOUS = "suspicious"
    REJECTED = "rejected"

    ALL = (VALID, SUSPICIOUS, REJECTED)


@dataclass(frozen=True)
class MarketObservation:
    """One independently reported salary.  Data kind **A**."""

    id: str
    family_key: str
    job_title_reported: str
    city: str
    amount_rial: int
    period: str  # monthly | hourly | daily
    currency_unit_reported: str  # rial | toman
    source_id: str
    license_status: str
    collected_at: datetime
    province: str | None = None
    seniority_level: str | None = None
    experience_years: int | None = None
    employment_type: str | None = None
    work_condition: str | None = None
    source_url: str | None = None
    is_synthetic: bool = False
    data_quality_status: str = DataQuality.VALID
    quality_reason: str | None = None

    @property
    def is_approved_source(self) -> bool:
        """Whether the licence state permits this row to inform an estimate."""
        return self.license_status in APPROVED_LICENSE_STATUSES


@dataclass(frozen=True)
class MarketAggregate:
    """One published summary.  Data kind **B** — never mixed with observations.

    Only statistics the publisher actually released are stored.  A percentile
    the report did not publish stays ``None``; it is never inferred.
    """

    id: str
    family_key: str
    city: str
    median_salary_rial: int
    source_id: str
    license_status: str
    collected_at: datetime
    sample_size: int
    province: str | None = None
    seniority_level: str | None = None
    employment_type: str | None = None
    min_salary_rial: int | None = None
    max_salary_rial: int | None = None
    p25_salary_rial: int | None = None
    p75_salary_rial: int | None = None
    period: str = "monthly"
    currency_unit_reported: str = "rial"
    source_url: str | None = None
    is_synthetic: bool = False

    @property
    def is_approved_source(self) -> bool:
        """Whether the licence state permits this aggregate to inform an estimate."""
        return self.license_status in APPROVED_LICENSE_STATUSES


@dataclass(frozen=True)
class MarketSource:
    """One registered source and its licence state.

    ``connected`` records whether data has actually been received from the
    source.  A source with ``connected=False`` must never appear in an
    estimate's ``data_sources``.
    """

    id: str
    name: str
    kind: str
    license_status: str
    connected: bool = False
    terms_url: str | None = None
    notes: str | None = None


@dataclass(frozen=True)
class PeerCohort:
    """The comparison group used for robust outlier tests."""

    scope: str
    values_rial: tuple[Decimal, ...] = ()

    @property
    def size(self) -> int:
        """Number of peer values in the cohort."""
        return len(self.values_rial)


@dataclass(frozen=True)
class ObservationFinding:
    """The classification of one observation, with every reason recorded."""

    observation_id: str
    status: str
    reasons: tuple[str, ...]
    monthly_rial: int
    peer_scope: str
    conversion_applied: bool = False


@dataclass(frozen=True)
class ValidationOutcome:
    """The classified sample.  Quarantined rows are retained, never deleted."""

    valid: tuple[MarketObservation, ...] = ()
    suspicious: tuple[ObservationFinding, ...] = ()
    rejected: tuple[ObservationFinding, ...] = ()
    findings: tuple[ObservationFinding, ...] = ()
    monthly_by_id: dict[str, int] = field(default_factory=dict)

    @property
    def valid_values(self) -> tuple[Decimal, ...]:
        """The monthly Rial values that may inform the estimate."""
        return tuple(to_decimal(self.monthly_by_id[row.id]) for row in self.valid)

    @property
    def quarantine_reasons(self) -> dict[str, int]:
        """Count of rows per reason, for the output warnings."""
        counts: dict[str, int] = {}
        for finding in (*self.suspicious, *self.rejected):
            for reason in finding.reasons:
                counts[reason] = counts.get(reason, 0) + 1
        return counts


def monthly_equivalent_rial(observation: MarketObservation) -> tuple[Decimal, bool]:
    """Return ``(monthly_rial, converted)`` for one observation.

    The reported currency is applied first (Toman x 10), then the period.  Both
    steps are exact decimal arithmetic; the caller rounds once when it publishes
    a figure.
    """
    amount = to_decimal(observation.amount_rial)
    if observation.currency_unit_reported == "toman":
        amount = amount * 10
    if observation.period == "hourly":
        return amount * HOURS_PER_MONTH, True
    if observation.period == "daily":
        return amount * DAYS_PER_MONTH, True
    return amount, False


@dataclass(frozen=True)
class MarketQuery:
    """The cohort requested by an estimation."""

    family_key: str
    city: str
    province: str | None = None
    seniority_level: str | None = None
    employment_type: str | None = None

    def as_dict(self) -> dict[str, str | None]:
        """Return a JSON-serialisable description of the query."""
        return {
            "family_key": self.family_key,
            "city": self.city,
            "province": self.province,
            "seniority_level": self.seniority_level,
            "employment_type": self.employment_type,
        }


def distinct_sources(rows: Sequence[MarketObservation]) -> tuple[str, ...]:
    """Return the source ids of *rows*, in first-seen order."""
    seen: dict[str, None] = {}
    for row in rows:
        seen.setdefault(row.source_id, None)
    return tuple(seen)
