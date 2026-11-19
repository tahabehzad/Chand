"""Development-only sample market data.

Authority
---------
``docs/adr/ADR-014-market-salary-reference-data-and-estimation.md`` §1.4 (sample
data is allowed in development and test **only**, must be unmistakably labelled,
and must never be reachable in production); ``AGENTS.md`` §8 (never present a
sample as evidence).

Related
-------
``market_data.py`` (record shape), ``validation.py`` (a synthetic row is rejected
unless the deployment sets ``allow_synthetic``), ``app/core/config.py``
(``estimation_allow_sample_data``).

Scope
-----
A fixed, deterministic dataset.  Every row carries
``license_status="synthetic_dev"``, ``is_synthetic=True`` and a source id that
cannot be mistaken for a real publication.  **No row is labelled Jobinja,
JobVision, IranTalent or any other real organisation**: inventing a number *and*
attributing it to a named publisher was the defect this replaces.

The numbers are internally plausible for Tehran/Isfahan in 1405 and exist only to
exercise the pipeline (quantiles, validation, chart, refusals).  They are not a
market claim and must not be quoted as one.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from decimal import Decimal

from app.engines.money import round_half_up, to_decimal

from .market_data import MarketAggregate, MarketObservation, MarketSource

__all__ = (
    "SAMPLE_COLLECTED_AT",
    "SAMPLE_SOURCE",
    "sample_aggregates",
    "sample_observations",
    "sample_sources",
)

#: One fixed collection date: a sample whose timestamps move with the clock would
#: change its own staleness verdict between two runs.
SAMPLE_COLLECTED_AT = datetime(2026, 9, 1, tzinfo=UTC)

SAMPLE_SOURCE = MarketSource(
    id="sample_dev_v1",
    name="دادهٔ نمونهٔ توسعه (ساختگی)",
    kind="synthetic",
    license_status="synthetic_dev",
    connected=False,
    notes=(
        "داده ساختگی برای آزمون خط لوله؛ نه داده بازار، نه منبع واقعی. "
        "در تولید با ESTIMATION_ALLOW_SAMPLE_DATA=false رد می‌شود."
    ),
)


def _observations(
    *,
    family_key: str,
    title: str,
    city: str,
    province: str,
    seniority: str,
    base_rial: int,
    offsets_percent: Sequence[int],
    employment_type: str = "full_time",
    work_condition: str = "on_site",
) -> tuple[MarketObservation, ...]:
    """Build a cohort from *base_rial* and integer percent offsets.

    Percentages are applied with Decimal arithmetic; the result is rounded once
    per row (line-item boundary) and never with a float.
    """
    rows: list[MarketObservation] = []
    prefix = f"sample-{family_key}-{city}-{seniority}".replace(" ", "-")
    for index, offset in enumerate(offsets_percent):
        exact = to_decimal(base_rial) * (Decimal(100) + Decimal(offset)) / Decimal(100)
        rows.append(
            MarketObservation(
                id=f"{prefix}-{index + 1:02d}",
                family_key=family_key,
                job_title_reported=title,
                city=city,
                province=province,
                amount_rial=round_half_up(exact),
                period="monthly",
                currency_unit_reported="rial",
                source_id=SAMPLE_SOURCE.id,
                license_status=SAMPLE_SOURCE.license_status,
                collected_at=SAMPLE_COLLECTED_AT,
                seniority_level=seniority,
                experience_years=None,
                employment_type=employment_type,
                work_condition=work_condition,
                is_synthetic=True,
            )
        )
    return tuple(rows)


def sample_observations() -> tuple[MarketObservation, ...]:
    """Return the fixed development dataset (4 families, 6 cohorts)."""
    cohorts: list[tuple[MarketObservation, ...]] = [
        _observations(
            family_key="php_backend",
            title="برنامه‌نویس PHP",
            city="تهران",
            province="تهران",
            seniority="junior",
            base_rial=280_000_000,
            offsets_percent=(-12, -6, -2, 0, 4, 9),
        ),
        _observations(
            family_key="php_backend",
            title="برنامه‌نویس PHP",
            city="تهران",
            province="تهران",
            seniority="mid",
            base_rial=420_000_000,
            offsets_percent=(-14, -8, -3, 0, 2, 6, 11, 18),
        ),
        _observations(
            family_key="php_backend",
            title="توسعه‌دهنده بک‌اند PHP",
            city="تهران",
            province="تهران",
            seniority="senior",
            base_rial=640_000_000,
            offsets_percent=(-16, -9, -4, 0, 3, 8, 14),
        ),
        _observations(
            family_key="frontend_react",
            title="توسعه‌دهنده فرانت‌اند",
            city="تهران",
            province="تهران",
            seniority="mid",
            base_rial=390_000_000,
            offsets_percent=(-10, -5, -1, 0, 5, 12),
        ),
        _observations(
            family_key="frontend_react",
            title="توسعه‌دهنده ارشد فرانت‌اند",
            city="تهران",
            province="تهران",
            seniority="senior",
            base_rial=685_000_000,
            offsets_percent=(-14, -8, -3, 0, 4, 10, 18),
        ),
        _observations(
            family_key="frontend_react",
            title="توسعه‌دهنده فرانت‌اند",
            city="اصفهان",
            province="اصفهان",
            seniority="mid",
            base_rial=310_000_000,
            offsets_percent=(-11, -6, -2, 0, 4),
        ),
        _observations(
            family_key="accountant",
            title="حسابدار",
            city="تهران",
            province="تهران",
            seniority="mid",
            base_rial=250_000_000,
            offsets_percent=(-12, -7, -3, 0, 3, 9),
        ),
    ]
    return tuple(row for cohort in cohorts for row in cohort)


def sample_aggregates() -> tuple[MarketAggregate, ...]:
    """Return one published-style aggregate so the fallback path is exercised.

    It is labelled synthetic exactly like the observations: the *aggregate* data
    kind is a different shape, not a stronger claim.
    """
    return (
        MarketAggregate(
            id="sample-aggregate-qa-tehran-mid",
            family_key="qa_engineer",
            city="تهران",
            province="تهران",
            seniority_level="mid",
            median_salary_rial=330_000_000,
            min_salary_rial=270_000_000,
            max_salary_rial=410_000_000,
            sample_size=42,
            source_id=SAMPLE_SOURCE.id,
            license_status=SAMPLE_SOURCE.license_status,
            collected_at=SAMPLE_COLLECTED_AT,
            is_synthetic=True,
        ),
    )


def sample_sources() -> tuple[MarketSource, ...]:
    """Return the sample source registry (a single, clearly synthetic entry)."""
    return (SAMPLE_SOURCE,)
