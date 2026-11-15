"""Tenant identity schema under SPEC-AUTH-001 §2 and ADR-006/ADR-007 (P0-T05).

The seven-role set is the accepted DEC-004 choice (ADR-006).  The permission
matrix of SPEC-AUTH-001 §3 is still unapproved, so ``permissions`` and
``role_permissions`` exist and stay empty.

Ownership model
---------------
* ``users`` is a **global** principal.  It is not tenant-owned: one human may
  hold memberships in several organisations, and the audit trail must survive
  the end of an engagement (Holy Bible §5.5, §5.7).
* ``organization_memberships`` is the **record-ownership binding**: it is the
  only place where a user is bound to an organisation, and the unique
  ``(organization_id, user_id)`` pair makes the binding one-to-one.
* ``sessions`` may be scoped to an organisation; a platform-level session has
  no organisation and is therefore not a tenant table.
* ``roles``, ``permissions`` and ``role_permissions`` are global catalogues.

None of these tables is a tenant *data* table, so none carries ``tenant_id``
and none receives a row-level security policy in P0-T05: the policies and the
per-transaction tenant context belong to P0-T09.
"""

from __future__ import annotations

import datetime
import uuid
from typing import Any

from sqlalchemy import (
    CHAR,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    false,
    func,
    true,
)
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class Organization(Base):
    """The tenant root and the RLS anchor (Holy Bible §5.5).

    ``key_store_id`` points at ``tenant_key_stores(id)``, the P0-T08
    deliverable.  The column exists here without its foreign key so that the
    identity schema does not depend on a table another task owns; P0-T08 adds
    the key.
    """

    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    legal_name_fa: Mapped[str] = mapped_column(String(200))
    national_company_id: Mapped[str | None] = mapped_column(String(11))
    is_active: Mapped[bool] = mapped_column(Boolean(), server_default=true())
    key_store_id: Mapped[uuid.UUID | None] = mapped_column(Uuid())
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "national_company_id IS NULL OR national_company_id ~ '^[0-9]{11}$'",
            name="ck_organizations_national_company_id",
        ),
    )


class User(Base):
    """The human principal (Holy Bible §5.5).

    ``email_normalized`` is a login identifier stored in clear — it is not a
    blind index and it is never encrypted (Holy Bible §5.5).  ``password_hash``
    holds an Argon2id digest and ``totp_secret_enc`` an AES-256-GCM
    ciphertext; neither plaintext is ever stored, logged or returned.
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    email_normalized: Mapped[str] = mapped_column(String(320), unique=True)
    display_name_fa: Mapped[str] = mapped_column(String(200))
    password_hash: Mapped[bytes | None] = mapped_column(nullable=True)
    password_params: Mapped[dict[str, Any] | None] = mapped_column(JSONB(), nullable=True)
    totp_secret_enc: Mapped[bytes | None] = mapped_column(nullable=True)
    totp_enabled: Mapped[bool] = mapped_column(Boolean(), server_default=false())
    is_platform_admin: Mapped[bool] = mapped_column(Boolean(), server_default=false())
    is_active: Mapped[bool] = mapped_column(Boolean(), server_default=true())
    failed_attempts: Mapped[int] = mapped_column(Integer(), server_default="0")
    locked_until: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_login_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    must_change_password: Mapped[bool] = mapped_column(Boolean(), server_default=false())
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Role(Base):
    """One entry of the seven-role set accepted by ADR-006."""

    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    role_key: Mapped[str] = mapped_column(String(32), unique=True)
    display_name_fa: Mapped[str] = mapped_column(String(100))
    description_fa: Mapped[str | None] = mapped_column(Text(), nullable=True)
    is_system_role: Mapped[bool] = mapped_column(Boolean(), server_default=true())
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Permission(Base):
    """One permission key of the catalogue.

    The catalogue is empty in P0-T05: the role/permission matrix of
    SPEC-AUTH-001 §3 is still ``[PROPOSED]`` and only the role set was
    approved.
    """

    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    permission_key: Mapped[str] = mapped_column(String(120), unique=True)
    resource: Mapped[str] = mapped_column(String(60))
    action: Mapped[str] = mapped_column(String(40))
    description_fa: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class RolePermission(Base):
    """The many-to-many binding between a role and a permission."""

    __tablename__ = "role_permissions"

    role_id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    permission_id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(["role_id"], ["roles.id"], name="fk_role_permissions_role_id", ondelete="CASCADE"),
        ForeignKeyConstraint(
            ["permission_id"],
            ["permissions.id"],
            name="fk_role_permissions_permission_id",
            ondelete="CASCADE",
        ),
    )


class OrganizationMembership(Base):
    """The ownership binding between a user and an organisation.

    The unique ``(organization_id, user_id)`` pair is the record-ownership
    anchor of the platform: a user holds at most one role per organisation,
    and every tenant-scoped record is attributed through this row.
    """

    __tablename__ = "organization_memberships"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    organization_id: Mapped[uuid.UUID] = mapped_column(Uuid())
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid())
    role_id: Mapped[uuid.UUID] = mapped_column(Uuid())
    is_active: Mapped[bool] = mapped_column(Boolean(), server_default=true())
    invited_by: Mapped[uuid.UUID | None] = mapped_column(Uuid(), nullable=True)
    accepted_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name="fk_organization_memberships_organization_id",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_organization_memberships_user_id",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["role_id"], ["roles.id"], name="fk_organization_memberships_role_id"
        ),
        ForeignKeyConstraint(
            ["invited_by"], ["users.id"], name="fk_organization_memberships_invited_by"
        ),
        UniqueConstraint(
            "organization_id", "user_id", name="uq_organization_memberships_organization_user"
        ),
    )


class UserSession(Base):
    """One revocable server-side session (ADR-006, SPEC-AUTH-001 §5).

    Only the SHA-256 digest of the opaque token is stored; the plaintext
    token never reaches the database.  ``organization_id`` is null for a
    platform-level session, so this table is not tenant-owned.
    """

    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid())
    organization_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(), nullable=True)
    token_hash: Mapped[str] = mapped_column(CHAR(64), unique=True)
    refresh_token_hash: Mapped[str | None] = mapped_column(CHAR(64), nullable=True, unique=True)
    ip_address: Mapped[str | None] = mapped_column(INET(), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text(), nullable=True)
    mfa_satisfied: Mapped[bool] = mapped_column(Boolean(), server_default=false())
    issued_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_seen_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    absolute_expires_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    idle_expires_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    revoked_reason: Mapped[str | None] = mapped_column(String(120), nullable=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_sessions_user_id", ondelete="CASCADE"
        ),
        ForeignKeyConstraint(
            ["organization_id"], ["organizations.id"], name="fk_sessions_organization_id"
        ),
    )


__all__ = [
    "Organization",
    "OrganizationMembership",
    "Permission",
    "Role",
    "RolePermission",
    "User",
    "UserSession",
]
