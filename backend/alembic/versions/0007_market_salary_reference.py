"""Market salary reference tables — observations, aggregates and the source registry.

Authority
---------
``docs/adr/ADR-014-market-salary-reference-data-and-estimation.md`` §3 (one data
architecture, two data kinds) and §8 (repository and persistence scope);
``AGENTS.md`` §2 Financial invariant 7 (money is an integer Rial, never a float).

Related
---------
``app/models/estimation.py`` (the ORM mirror), ``app/repositories/market_data.py``
(the only reader/writer), migration ``0006`` (work profiles).

What this migration does
------------------------
1. Creates ``market_data_sources`` — the source registry, including
   ``connected``: a source that never delivered data cannot be claimed.
2. Creates ``market_salary_observations`` (data kind A) with the reported
   currency, the pay period, the licence state, the collection date and the
   validation verdict.
3. Creates ``market_salary_aggregates`` (data kind B) with only the statistics a
   publisher actually released; ever percentile the report omitted stays NULL.
4. Adds the cohort and collection-date indexes the estimator's queries use.

What this migration deliberately does not do
--------------------------------------------
* **No tenant_id and no RLS**: these are global reference records with no personal
  data (see the model docstring).  No candidate profile is persisted here, because
  that needs the tenancy decision recorded as DEC-016.
* No seed data of any kind.  A real observation can only arrive through
  ``backend/scripts/market_data_ingest.py`` with a licence state and a source id.
* No role or grant change.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | None = None
depends_on: str | None = None

_LICENSE = "'licensed', 'published_report', 'manual_verified', 'synthetic_dev', 'unknown'"
_PERIOD = "'monthly', 'hourly', 'daily'"
_QUALITY = "'valid', 'suspicious', 'rejected'"


def upgrade() -> None:
    op.create_table(
        "market_data_sources",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("license_status", sa.String(length=24), nullable=False),
        sa.Column("connected", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("terms_url", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            f"license_status IN ({_LICENSE})", name="ck_market_data_sources_license_status"
        ),
        sa.CheckConstraint(
            "kind IN ('licensed_survey','published_report','job_board','manual','synthetic')",
            name="ck_market_data_sources_kind",
        ),
    )

    op.create_table(
        "market_salary_observations",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("family_key", sa.String(length=64), nullable=False),
        sa.Column("job_title_reported", sa.String(length=200), nullable=False),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("province", sa.String(length=100), nullable=True),
        sa.Column("seniority_level", sa.String(length=20), nullable=True),
        sa.Column("experience_years", sa.Integer(), nullable=True),
        sa.Column("employment_type", sa.String(length=20), nullable=True),
        sa.Column("work_condition", sa.String(length=20), nullable=True),
        sa.Column("amount_rial", sa.BigInteger(), nullable=False),
        sa.Column("period", sa.String(length=10), nullable=False),
        sa.Column("currency_unit_reported", sa.String(length=10), nullable=False),
        sa.Column("source_id", sa.String(length=64), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("license_status", sa.String(length=24), nullable=False),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_synthetic", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "data_quality_status", sa.String(length=16), nullable=False, server_default="valid"
        ),
        sa.Column("quality_reason", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["source_id"], ["market_data_sources.id"], name="fk_market_observations_source_id"
        ),
        sa.CheckConstraint("amount_rial > 0", name="ck_market_observations_amount_positive"),
        sa.CheckConstraint(f"period IN ({_PERIOD})", name="ck_market_observations_period"),
        sa.CheckConstraint(
            "currency_unit_reported IN ('rial','toman')", name="ck_market_observations_currency"
        ),
        sa.CheckConstraint(
            f"license_status IN ({_LICENSE})", name="ck_market_observations_license_status"
        ),
        sa.CheckConstraint(
            f"data_quality_status IN ({_QUALITY})", name="ck_market_observations_quality"
        ),
    )
    op.create_index(
        "ix_market_observations_cohort",
        "market_salary_observations",
        ["family_key", "city", "seniority_level"],
    )
    op.create_index(
        "ix_market_observations_collected", "market_salary_observations", ["collected_at"]
    )

    op.create_table(
        "market_salary_aggregates",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("family_key", sa.String(length=64), nullable=False),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("province", sa.String(length=100), nullable=True),
        sa.Column("seniority_level", sa.String(length=20), nullable=True),
        sa.Column("employment_type", sa.String(length=20), nullable=True),
        sa.Column("published_min_rial", sa.BigInteger(), nullable=True),
        sa.Column("published_p25_rial", sa.BigInteger(), nullable=True),
        sa.Column("published_median_rial", sa.BigInteger(), nullable=False),
        sa.Column("published_p75_rial", sa.BigInteger(), nullable=True),
        sa.Column("published_max_rial", sa.BigInteger(), nullable=True),
        sa.Column("sample_size", sa.Integer(), nullable=False),
        sa.Column("period", sa.String(length=10), nullable=False, server_default="monthly"),
        sa.Column(
            "currency_unit_reported", sa.String(length=10), nullable=False, server_default="rial"
        ),
        sa.Column("source_id", sa.String(length=64), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("license_status", sa.String(length=24), nullable=False),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_synthetic", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "data_quality_status", sa.String(length=16), nullable=False, server_default="valid"
        ),
        sa.Column("quality_reason", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["source_id"], ["market_data_sources.id"], name="fk_market_aggregates_source_id"
        ),
        sa.CheckConstraint("sample_size > 0", name="ck_market_aggregates_sample_size"),
        sa.CheckConstraint("published_median_rial > 0", name="ck_market_aggregates_median_positive"),
        sa.CheckConstraint(
            "published_min_rial IS NULL OR published_max_rial IS NULL "
            "OR published_min_rial <= published_max_rial",
            name="ck_market_aggregates_range",
        ),
        sa.CheckConstraint(f"period IN ({_PERIOD})", name="ck_market_aggregates_period"),
        sa.CheckConstraint(
            "currency_unit_reported IN ('rial','toman')", name="ck_market_aggregates_currency"
        ),
        sa.CheckConstraint(
            f"license_status IN ({_LICENSE})", name="ck_market_aggregates_license_status"
        ),
        sa.CheckConstraint(
            f"data_quality_status IN ({_QUALITY})", name="ck_market_aggregates_quality"
        ),
    )
    op.create_index(
        "ix_market_aggregates_cohort",
        "market_salary_aggregates",
        ["family_key", "city", "seniority_level"],
    )


def downgrade() -> None:
    op.drop_index("ix_market_aggregates_cohort", table_name="market_salary_aggregates")
    op.drop_table("market_salary_aggregates")
    op.drop_index("ix_market_observations_collected", table_name="market_salary_observations")
    op.drop_index("ix_market_observations_cohort", table_name="market_salary_observations")
    op.drop_table("market_salary_observations")
    op.drop_table("market_data_sources")
