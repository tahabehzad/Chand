"""Manager workspace models: employees, observations, evidence, evaluations,
salary recommendations and decisions.

Authority
---------
``AGENTS.md`` §2 Security invariant 12 (``tenant_id`` + RLS policy +
``FORCE ROW LEVEL SECURITY`` in the same migration — delivered by
``alembic/versions/0004_manager_workspace.py``); ``AGENTS.md`` §2 Financial
invariants (money as exact integer Rial in the API layer, Decimal in engines).

Related
-------
``app/models/identity.py`` (``organizations`` is the tenant anchor),
``app/engines/perf_v1.py`` (the scoring rule set), ``app/engines/errors.py``.

Scope
-----
* Every table below is tenant-scoped data: it carries ``tenant_id`` and is
  protected by the migration's RLS policy backed by ``current_tenant_id()``.
* Money columns are ``BigInteger`` Rial integers — never floats.
* ``recommendation_decisions`` is append-only: the migration installs a
  trigger that rejects ``UPDATE``/``DELETE``.
* No national ID, mobile, Sheba or bank field is accepted in this model set.
"""

from __future__ import annotations

import datetime
import uuid
from typing import Any

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Index,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class Employee(Base):
    """One employee of one tenant, created and owned by the manager."""

    __tablename__ = "employees"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid(), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120))
    role_label: Mapped[str] = mapped_column(String(60))
    start_date: Mapped[str] = mapped_column(String(10))
    created_by: Mapped[uuid.UUID | None] = mapped_column(Uuid(), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("id", "tenant_id", name="uq_employee_tenant_identity"),
        CheckConstraint(
            "start_date ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'", name="ck_employees_start_date_format"
        ),
        Index("ix_employees_tenant_created", "tenant_id", "created_at"),
    )


class EmployeeObservation(Base):
    """One performance observation for one employee in one period."""

    __tablename__ = "employee_observations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid(), nullable=False, index=True)
    employee_id: Mapped[uuid.UUID] = mapped_column(Uuid(), nullable=False)
    #: One of the ``perf-v1`` metric codes: sales / quality / attendance /
    #: responsibility.  Enforced by a CHECK, not by an enum table (MVP).
    metric_code: Mapped[str] = mapped_column(String(20))
    #: Free-form evaluation period label, e.g. ``1404-Q2``.
    period: Mapped[str] = mapped_column(String(40))
    #: Integer digit string in the criterion's own unit.
    raw_value: Mapped[str] = mapped_column(String(24))
    #: valid | corrected | rejected.  Rejected rows are excluded from scoring.
    state: Mapped[str] = mapped_column(String(12))
    #: manual | import.
    source: Mapped[str] = mapped_column(String(12))
    note: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["employee_id"],
            ["employees.id"],
            name="fk_employee_observations_employee_id",
            ondelete="CASCADE",
        ),
        CheckConstraint(
            "metric_code IN ('sales','quality','attendance','responsibility')",
            name="ck_employee_observations_metric_code",
        ),
        CheckConstraint(
            "state IN ('valid','corrected','rejected')",
            name="ck_employee_observations_state",
        ),
        CheckConstraint(
            "source IN ('manual','import')",
            name="ck_employee_observations_source",
        ),
        CheckConstraint("raw_value ~ '^[0-9]{1,18}$'", name="ck_employee_observations_raw_digits"),
        Index("ix_employee_observations_tenant_employee", "tenant_id", "employee_id"),
    )


class EmployeeEvidence(Base):
    """One uploaded supporting document for one employee.

    The MVP stores the file bytes in the row (``content``) with its SHA-256
    digest; object storage (ADR-002) remains the production target.
    """

    __tablename__ = "employee_evidence"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid(), nullable=False, index=True)
    employee_id: Mapped[uuid.UUID] = mapped_column(Uuid(), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(120))
    byte_size: Mapped[int] = mapped_column(BigInteger())
    sha256: Mapped[str] = mapped_column(String(64))
    note: Mapped[str | None] = mapped_column(Text(), nullable=True)
    content: Mapped[bytes] = mapped_column(LargeBinary())
    created_by: Mapped[uuid.UUID | None] = mapped_column(Uuid(), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["employee_id"],
            ["employees.id"],
            name="fk_employee_evidence_employee_id",
            ondelete="CASCADE",
        ),
        Index("ix_employee_evidence_tenant_employee", "tenant_id", "employee_id"),
    )


class EmployeeEvaluation(Base):
    """One persisted evaluation result (rule set ``perf-v1``).

    The full explanation — per-criterion contributions, observations used,
    missing criteria and the published policy — is stored verbatim so a later
    rule set never rewrites a historical evaluation.
    """

    __tablename__ = "employee_evaluations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid(), nullable=False, index=True)
    employee_id: Mapped[uuid.UUID] = mapped_column(Uuid(), nullable=False)
    rule_set_version: Mapped[str] = mapped_column(String(20))
    rule_set_status: Mapped[str] = mapped_column(String(20))
    score_100: Mapped[int] = mapped_column(Integer())
    total_bp: Mapped[int] = mapped_column(Integer())
    contributions: Mapped[list[dict[str, Any]]] = mapped_column(JSONB())
    observations_used: Mapped[list[dict[str, Any]]] = mapped_column(JSONB())
    missing_criteria: Mapped[list[str]] = mapped_column(JSONB())
    missing_policy_fa: Mapped[str] = mapped_column(Text())
    calculation_hash: Mapped[str] = mapped_column(String(64))
    created_by: Mapped[uuid.UUID | None] = mapped_column(Uuid(), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["employee_id"],
            ["employees.id"],
            name="fk_employee_evaluations_employee_id",
            ondelete="CASCADE",
        ),
        CheckConstraint(
            "score_100 >= 0 AND score_100 <= 100", name="ck_employee_evaluations_score_range"
        ),
        Index("ix_employee_evaluations_tenant_employee", "tenant_id", "employee_id"),
    )


class SalaryRecommendation(Base):
    """One explainable salary recommendation with its statutory costing."""

    __tablename__ = "salary_recommendations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid(), nullable=False, index=True)
    employee_id: Mapped[uuid.UUID] = mapped_column(Uuid(), nullable=False)
    evaluation_id: Mapped[uuid.UUID] = mapped_column(Uuid(), nullable=False)
    period: Mapped[str] = mapped_column(String(40))
    rule_set_version: Mapped[str] = mapped_column(String(20))
    engine_version: Mapped[str] = mapped_column(String(60))
    score_100: Mapped[int] = mapped_column(Integer())
    #: Integer Rial.
    band_min_rial: Mapped[int] = mapped_column(BigInteger())
    band_max_rial: Mapped[int] = mapped_column(BigInteger())
    band_current_rial: Mapped[int | None] = mapped_column(BigInteger(), nullable=True)
    band_position_bp: Mapped[int] = mapped_column(Integer())
    suggested_gross_rial: Mapped[int] = mapped_column(BigInteger())
    delta_rial: Mapped[int | None] = mapped_column(BigInteger(), nullable=True)
    #: Explanation payload: reasons, warnings, data-quality limitations.
    explanation: Mapped[dict[str, Any]] = mapped_column(JSONB())
    #: The statutory costing block produced by ``compute_gross_to_net``.
    statutory_costing: Mapped[dict[str, Any]] = mapped_column(JSONB())
    current_costing: Mapped[dict[str, Any] | None] = mapped_column(JSONB(), nullable=True)
    calculation_hash: Mapped[str] = mapped_column(String(64))
    #: pending | decided  (the decision itself lives in the append-only table).
    status: Mapped[str] = mapped_column(String(12))
    created_by: Mapped[uuid.UUID | None] = mapped_column(Uuid(), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["employee_id"],
            ["employees.id"],
            name="fk_salary_recommendations_employee_id",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["evaluation_id"],
            ["employee_evaluations.id"],
            name="fk_salary_recommendations_evaluation_id",
        ),
        CheckConstraint("status IN ('pending','decided')", name="ck_salary_recommendations_status"),
        Index("ix_salary_recommendations_tenant_employee", "tenant_id", "employee_id"),
        Index("ix_salary_recommendations_tenant_status", "tenant_id", "status"),
    )


class RecommendationDecision(Base):
    """One manager decision.  Append-only: never updated or deleted."""

    __tablename__ = "recommendation_decisions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid(), nullable=False, index=True)
    recommendation_id: Mapped[uuid.UUID] = mapped_column(Uuid(), nullable=False)
    #: approve | edit | reject.
    action: Mapped[str] = mapped_column(String(12))
    edited_gross_rial: Mapped[int | None] = mapped_column(BigInteger(), nullable=True)
    comment: Mapped[str] = mapped_column(String(500))
    decided_by: Mapped[uuid.UUID | None] = mapped_column(Uuid(), nullable=True)
    decided_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["recommendation_id"],
            ["salary_recommendations.id"],
            name="fk_recommendation_decisions_recommendation_id",
        ),
        CheckConstraint(
            "action IN ('approve','edit','reject')",
            name="ck_recommendation_decisions_action",
        ),
        #: One final decision per recommendation: the append-only trigger makes
        #: the row immutable, this constraint makes the outcome singular.
        UniqueConstraint(
            "recommendation_id", name="uq_recommendation_decisions_one_per_recommendation"
        ),
        Index("ix_recommendation_decisions_tenant_decided", "tenant_id", "decided_at"),
    )


__all__ = [
    "Employee",
    "EmployeeEvaluation",
    "EmployeeEvidence",
    "EmployeeObservation",
    "RecommendationDecision",
    "SalaryRecommendation",
]
