"""P0-T10: append-only, hash-chained audit ledger and the access log models.

Authority
---------
``docs/specs/AUTH.md`` §7.2 (hash chain; separate non-chained access log);
``docs/PISH_HESABDARI_HOLY_BIBLE.md`` §7.2, §2181 and §1652 (``audit_logs``,
10-year retention); AGENTS.md §2 invariants 12 and 14.

Ownership model
---------------
* ``audit_logs`` is the hash-chained evidentiary ledger: every row chains to
  the previous row and is append-only at the database layer.  Tenant-scoped
  via ``tenant_id`` with RLS enabled and forced.
* ``access_log`` is the separate non-chained read-event log (DEC-004b),
  retained and queryable but not hash-chained.  Also tenant-scoped with RLS.

Neither table stores plaintext National IDs, mobile numbers, Sheba numbers or
candidate names (AUTH §7.3): the ``payload`` holds blind indexes and encrypted
values only.
"""

from __future__ import annotations

import datetime
import uuid
from typing import Any

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Index,
    String,
    Uuid,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class AuditLog(Base):
    """One row of the hash-chained, append-only audit ledger."""

    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid(), nullable=False, index=True)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(), nullable=True)
    actor_type: Mapped[str] = mapped_column(String(16), nullable=False)
    event_type: Mapped[str] = mapped_column(String(40), nullable=False)
    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    #: Canonical JSON (sorted keys, UTF-8, no insignificant whitespace).
    #: Blind indexes and encrypted values only -- never plaintext PII.
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB(), nullable=False)
    previous_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    chain_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    sequence_id: Mapped[int] = mapped_column(BigInteger(), nullable=False)

    __table_args__ = (
        CheckConstraint("actor_type IN ('USER','SYSTEM')", name="ck_audit_logs_actor_type"),
        Index("ix_audit_logs_tenant_sequence", "tenant_id", "sequence_id"),
        Index("ix_audit_logs_tenant_time", "tenant_id", "timestamp"),
    )


class AccessLog(Base):
    """One read/event record in the separate non-chained access log."""

    __tablename__ = "access_log"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid(), nullable=False, index=True)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(), nullable=True)
    actor_type: Mapped[str | None] = mapped_column(String(16), nullable=True)
    event_type: Mapped[str] = mapped_column(String(40), nullable=False)
    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "actor_type IS NULL OR actor_type IN ('USER','SYSTEM')",
            name="ck_access_logs_actor_type",
        ),
        Index("ix_access_logs_tenant_time", "tenant_id", "timestamp"),
    )


__all__ = ["AccessLog", "AuditLog"]
