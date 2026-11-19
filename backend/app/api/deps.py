"""Request-scoped dependencies: the database session and the manager context.

Authority
---------
``AGENTS.md`` §2 Security invariants 12-15 (tenant isolation fails closed,
actions are traceable); ``docs/specs/AUTH.md`` §6 (ISO-06: the tenant is never
chosen by the client).

Related
-------
``app/db.py`` (engine and session factory), ``app/services/identity_service.py``
(session issue), ``app/core/security/tenant_context.py`` (the binding).

Scope
-----
* ``get_db`` yields one session per request and closes it.
* ``require_manager`` resolves the ``Authorization: Bearer <token>`` header to
  a live, unexpired, unrevoked session; binds the *server-side* organisation
  of that session (never a client field) as the tenant context; and exposes
  the bound identity to the handler.  Every refusal is a structured 401 with
  one stable code and no identifier.
* The tenant binding is transaction-local: handlers must rebind after an
  explicit commit (``renew_tenant``) before any further tenant query.
"""

from __future__ import annotations

import datetime
import hashlib
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.security.tenant_context import (
    TenantContextError,
    apply_tenant_context,
    peek_tenant_id,
    tenant_context,
)
from app.db import get_session_factory
from app.models.identity import User, UserSession

#: The overridable process session factory, held in a one-element list so the
#: test harness can swap it without a module-level ``global`` statement.
_STATE: list[async_sessionmaker[AsyncSession]] = []


def get_session_factory_dep() -> async_sessionmaker[AsyncSession]:
    """Return the active session factory (overridable by the test harness)."""
    if not _STATE:
        _STATE.append(get_session_factory())
    return _STATE[0]


def set_session_factory(
    factory: async_sessionmaker[AsyncSession] | None,
) -> None:
    """Override the process session factory (tests and the migration harness)."""
    _STATE.clear()
    if factory is not None:
        _STATE.append(factory)


async def get_db() -> AsyncIterator[AsyncSession]:
    """One async session per request."""
    session = get_session_factory_dep()()
    try:
        yield session
    finally:
        await session.close()


DbSession = Annotated[AsyncSession, Depends(get_db)]


@dataclass(frozen=True, slots=True)
class ManagerContext:
    """The authenticated manager and the tenant bound to the request."""

    user_id: UUID
    session_id: UUID
    tenant_id: UUID
    display_name: str
    email: str


class NotAuthenticatedError(Exception):
    """A stable 401 condition; the API renders it without any identifier."""

    code = "AUTH_SESSION_INVALID"


def _bearer_token(request: Request) -> str:
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        raise NotAuthenticatedError()
    token = header[len("Bearer ") :].strip()
    if not token:
        raise NotAuthenticatedError()
    return token


async def require_manager(request: Request, db: DbSession) -> AsyncIterator[ManagerContext]:
    """Resolve the bearer session and bind its organisation as the tenant.

    The organisation comes from the stored session row, never from a request
    field, so a client cannot choose a tenant (ISO-06).  The process-level
    context variable is bound for exactly the request scope and reset on
    exit, so a pooled worker task can never inherit a stale tenant.
    """
    token = _bearer_token(request)
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    user_session = (
        await db.execute(select(UserSession).where(UserSession.token_hash == digest))
    ).scalar_one_or_none()

    now = datetime.datetime.now(datetime.UTC)
    if (
        user_session is None
        or user_session.revoked_at is not None
        or user_session.absolute_expires_at <= now
        or user_session.idle_expires_at <= now
        or user_session.organization_id is None
    ):
        raise NotAuthenticatedError()

    user = (
        await db.execute(select(User).where(User.id == user_session.user_id))
    ).scalar_one_or_none()
    if user is None or not user.is_active:
        raise NotAuthenticatedError()

    # Touch the session's idle window before any tenant query is issued.
    user_session.last_seen_at = now
    await db.flush()

    # The binding is transaction-local; it must be renewed after any commit.
    tenant_id = user_session.organization_id
    await apply_tenant_context(db, tenant_id)
    binding = tenant_context(tenant_id)
    binding.__enter__()
    try:
        yield ManagerContext(
            user_id=user.id,
            session_id=user_session.id,
            tenant_id=tenant_id,
            display_name=user.display_name_fa,
            email=user.email_normalized,
        )
    finally:
        binding.__exit__(None, None, None)


async def renew_tenant(db: AsyncSession, context: ManagerContext) -> None:
    """Rebind the tenant after an explicit commit cleared the transaction.

    The process-level variable is already bound by the dependency; only the
    transaction-local database binding needs renewal.
    """
    if peek_tenant_id() != context.tenant_id:
        raise TenantContextError("Tenant context is not set; refusing to read tenant data.")
    await apply_tenant_context(db, context.tenant_id)


ManagerRequired = Annotated[ManagerContext, Depends(require_manager)]


__all__ = [
    "DbSession",
    "ManagerContext",
    "ManagerRequired",
    "NotAuthenticatedError",
    "get_db",
    "renew_tenant",
    "require_manager",
    "set_session_factory",
]
