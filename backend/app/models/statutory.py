"""Global statutory schema under accepted ADR-007 (P0-T04).

No tenant columns: FORCE RLS and column privileges live in the migration.
User FKs are owned by P0-T05; every write is database-blocked until then.
"""

from __future__ import annotations

import datetime
import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    CHAR,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKeyConstraint,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    false,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models import (
    Base,
    identity as identity_models,  # noqa: F401 -- registers users for the actor keys
)


class StatutoryRuleSetVersion(Base):
    """One revision of one Solar-Hijri statutory rule set (§5.2).

    Identified by ``(rule_year_shamsi, revision)`` — canonical form
    ``YYYY.R``. The verification state is a machine-checkable column, never
    folded into a display string (§5.3, the ``1405.1-VERIFIED`` defect).
    """

    __tablename__ = "statutory_rule_set_versions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    rule_year_shamsi: Mapped[int] = mapped_column(Integer())
    revision: Mapped[int] = mapped_column(Integer())
    effective_from: Mapped[datetime.date] = mapped_column(Date())
    effective_to: Mapped[datetime.date | None] = mapped_column(Date())
    supersedes_id: Mapped[uuid.UUID | None] = mapped_column(Uuid())
    status: Mapped[str] = mapped_column(String(24))
    is_active: Mapped[bool] = mapped_column(Boolean(), server_default=false())
    source_manifest: Mapped[list[dict[str, Any]]] = mapped_column(JSONB())
    parameter_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB())
    verified_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    verified_by: Mapped[uuid.UUID | None] = mapped_column(Uuid())
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "rule_year_shamsi",
            "revision",
            name="uq_statutory_rule_set_versions_year_revision",
        ),
        CheckConstraint(
            "status IN ('DRAFT', 'UNDER_REVIEW', 'VERIFIED', 'ACTIVE', 'RETIRED', 'REJECTED')",
            name="ck_statutory_rule_set_versions_status",
        ),
        ForeignKeyConstraint(
            ["supersedes_id"],
            ["statutory_rule_set_versions.id"],
            name="fk_statutory_rule_set_versions_supersedes_id",
        ),
    )


class StatutorySourceArtefact(Base):
    """One archived statutory source document (§2.2).

    A re-retrieval with a different ``sha256`` creates a new row and a
    change-review task; an existing row is never mutated (§2.2 item 4).
    The referenced S3 object key is WORM-governed under ADR-002.
    """

    __tablename__ = "statutory_source_artefacts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    rule_year_shamsi: Mapped[int] = mapped_column(Integer())
    source_code: Mapped[str] = mapped_column(String(16))
    issuing_authority: Mapped[str] = mapped_column(String(200))
    document_title: Mapped[str] = mapped_column(String(300))
    reference_number: Mapped[str | None] = mapped_column(String(120))
    reference_date_sh: Mapped[str | None] = mapped_column(String(20))
    source_url: Mapped[str] = mapped_column(Text())
    retrieval_level: Mapped[str] = mapped_column(String(2))
    retrieved_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    sha256: Mapped[str] = mapped_column(CHAR(64))
    s3_object_key: Mapped[str] = mapped_column(Text())
    archived_by: Mapped[uuid.UUID] = mapped_column(Uuid())

    __table_args__ = (
        CheckConstraint(
            "retrieval_level IN ('L1', 'L2', 'L3', 'L4')",
            name="ck_statutory_source_artefacts_retrieval_level",
        ),
    )


class StatutoryParameterSignature(Base):
    """One four-eyes signature over one parameter of one revision (§4.2).

    ``signature_sha256`` records
    ``sha256(parameter_canonical_json ‖ verifier_id ‖ timestamp ‖
    artefact_sha256)`` (§4.1 item 5). Rows are append-only; the migration's
    trigger rejects ``UPDATE`` and ``DELETE`` at the database layer.
    """

    __tablename__ = "statutory_parameter_signatures"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    rule_set_version_id: Mapped[uuid.UUID] = mapped_column(Uuid())
    parameter_key: Mapped[str] = mapped_column(String(120))
    parameter_value: Mapped[Decimal] = mapped_column(Numeric(24, 4))
    derivation_note: Mapped[str | None] = mapped_column(Text())
    source_artefact_id: Mapped[uuid.UUID] = mapped_column(Uuid())
    # Allowed roster roles (§4.2/§4.3): TRANSCRIBER, VERIFIER,
    # CERTIFIED_ACCOUNTANT, LABOR_COUNSEL. Unconstrained by design (§2.3).
    verifier_role: Mapped[str] = mapped_column(String(40))
    verifier_id: Mapped[uuid.UUID] = mapped_column(Uuid())
    signature_sha256: Mapped[str] = mapped_column(CHAR(64))
    signed_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint(
            "rule_set_version_id",
            "parameter_key",
            "verifier_role",
            name="uq_statutory_parameter_signatures_version_param_role",
        ),
        ForeignKeyConstraint(
            ["rule_set_version_id"],
            ["statutory_rule_set_versions.id"],
            name="fk_statutory_parameter_signatures_rule_set_version_id",
        ),
        ForeignKeyConstraint(
            ["source_artefact_id"],
            ["statutory_source_artefacts.id"],
            name="fk_statutory_parameter_signatures_source_artefact_id",
        ),
    )


class StatutoryRuleChange(Base):
    """One change-review record for one parameter delta (§5.5).

    Historical simulations are never recomputed; a correction creates a new
    revision with ``supersedes_id`` set and one row here per changed
    parameter.
    """

    __tablename__ = "statutory_rule_changes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    rule_set_version_id: Mapped[uuid.UUID] = mapped_column(Uuid())
    parameter_key: Mapped[str] = mapped_column(String(120))
    old_value: Mapped[Decimal | None] = mapped_column(Numeric(24, 4))
    new_value: Mapped[Decimal | None] = mapped_column(Numeric(24, 4))
    legal_citation: Mapped[str] = mapped_column(Text())
    effective_from: Mapped[datetime.date] = mapped_column(Date())
    change_reason: Mapped[str] = mapped_column(Text())
    requested_by: Mapped[uuid.UUID] = mapped_column(Uuid())
    approved_by: Mapped[uuid.UUID] = mapped_column(Uuid())
    affected_simulation_count: Mapped[int] = mapped_column(Integer(), server_default="0")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["rule_set_version_id"],
            ["statutory_rule_set_versions.id"],
            name="fk_statutory_rule_changes_rule_set_version_id",
        ),
    )


class StatutoryVerificationLog(Base):
    """One transcription/verification log entry (§10).

    P0-T05 will enforce actor foreign keys under ADR-007; writes remain blocked
    until that migration validates the references. ``outcome`` values AGREE / DISAGREE / CANNOT_VERIFY are
    documented but intentionally not constrained (contract §2.3).
    """

    __tablename__ = "statutory_verification_log"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    rule_year_shamsi: Mapped[int] = mapped_column(Integer())
    parameter_key: Mapped[str] = mapped_column(String(120))
    proposed_value: Mapped[Decimal] = mapped_column(Numeric(24, 4))
    proposed_source: Mapped[str] = mapped_column(Text())
    transcription_level: Mapped[str] = mapped_column(String(2))
    transcriber_id: Mapped[uuid.UUID] = mapped_column(Uuid())
    transcribed_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    verifier_id: Mapped[uuid.UUID] = mapped_column(Uuid())
    # Allowed outcomes (§10): AGREE, DISAGREE, CANNOT_VERIFY.
    verifier_role: Mapped[str] = mapped_column(String(40))
    verified_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    outcome: Mapped[str] = mapped_column(String(16))
    discrepancy_note: Mapped[str | None] = mapped_column(Text())
    artefact_sha256: Mapped[str] = mapped_column(CHAR(64))
