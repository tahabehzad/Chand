"""Encrypted profile, document and immutable work-calculation rows.

Authority: ADR-012; WORK_PROFILE_PAYROLL; AGENTS security invariants.
Related: manager.Employee; additive work-profile migration.
Scope: keys and personal plaintext never enter these new tables.
"""

from __future__ import annotations

import datetime
import uuid

from sqlalchemy import (
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    LargeBinary,
    String,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class WorkProfile(Base):
    __tablename__ = "employee_work_profiles"
    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    employee_id: Mapped[uuid.UUID] = mapped_column(Uuid(), nullable=False)
    ciphertext: Mapped[bytes] = mapped_column(LargeBinary(), nullable=False)
    key_id: Mapped[str] = mapped_column(String(40), nullable=False)
    actor_id: Mapped[uuid.UUID] = mapped_column(Uuid(), nullable=False)
    revision: Mapped[int] = mapped_column(Integer(), nullable=False)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    __table_args__ = (Index("uq_work_profile_employee", "tenant_id", "employee_id", unique=True),
        ForeignKeyConstraint(["employee_id", "tenant_id"], ["employees.id", "employees.tenant_id"]))


class WorkDocument(Base):
    __tablename__ = "employee_work_documents"
    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    employee_id: Mapped[uuid.UUID] = mapped_column(Uuid(), nullable=False)
    ciphertext: Mapped[bytes] = mapped_column(LargeBinary(), nullable=False)
    metadata_ciphertext: Mapped[bytes] = mapped_column(LargeBinary(), nullable=False)
    key_id: Mapped[str] = mapped_column(String(40), nullable=False)
    actor_id: Mapped[uuid.UUID] = mapped_column(Uuid(), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    __table_args__ = (Index("ix_work_document_employee", "tenant_id", "employee_id"),
        ForeignKeyConstraint(["employee_id", "tenant_id"], ["employees.id", "employees.tenant_id"]))


class WorkCalculation(Base):
    __tablename__ = "employee_work_calculations"
    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    employee_id: Mapped[uuid.UUID] = mapped_column(Uuid(), nullable=False)
    ciphertext: Mapped[bytes] = mapped_column(LargeBinary(), nullable=False)
    key_id: Mapped[str] = mapped_column(String(40), nullable=False)
    actor_id: Mapped[uuid.UUID] = mapped_column(Uuid(), nullable=False)
    calculation_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    __table_args__ = (Index("ix_work_calculation_employee", "tenant_id", "employee_id"),
        ForeignKeyConstraint(["employee_id", "tenant_id"], ["employees.id", "employees.tenant_id"]))
