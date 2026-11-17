"""Per-transaction tenant context for row-level security (P0-T09).

Authority
---------
``AGENTS.md`` §2 Security invariant 12 (every tenant table carries
``tenant_id``, an RLS policy and ``FORCE ROW LEVEL SECURITY`` in the same
migration); ``docs/specs/AUTH.md`` §6 multi-tenant isolation; Holy Bible §5.5
and §5.9.  ADR-007 keeps the statutory tables global, so no tenant policy is
defined there.

Related
-------
``app/models/identity.py`` (the ``organizations`` anchor),
``alembic/versions/0003_tenant_context.py`` (the ``set_tenant_context`` and
``current_tenant_id`` server functions this module drives).

Scope
-----
Two fail-closed surfaces, deliberately separate:

* :func:`tenant_context` — the in-process context variable.  The application
  layer reads the tenant from it and never from a request field, so a missing
  context raises instead of silently defaulting.
* :func:`apply_tenant_context` — the database binding.  It calls the
  transaction-local ``set_tenant_context()`` function, so the context dies
  with the transaction and cannot leak into a pooled connection.

Nothing here chooses a tenant, authenticates a principal or reads
configuration.  Those belong to the authentication work (P0-T18); this module
only guarantees that *no tenant is assumed*.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

#: The server-side custom GUC that carries the tenant identifier.  It matches
#: the value read by ``current_tenant_id()`` in migration ``0003``.
TENANT_CONTEXT_SETTING = "app.tenant_id"

#: The statement that binds the context for the current transaction only.
#: ``set_tenant_context`` uses ``is_local = true``, so a rollback or a commit
#: ends the binding and a pooled connection is never left scoped to a tenant.
APPLY_TENANT_CONTEXT_SQL = "SELECT set_tenant_context(:tenant_id)"

_current_tenant: ContextVar[uuid.UUID | None] = ContextVar(
    "pish_current_tenant", default=None
)


class TenantContextError(RuntimeError):
    """Raised when a tenant-scoped operation has no usable tenant context.

    The message is fixed and carries no identifier: a tenant identifier is
    never written to a log, an error payload or a traceback.
    """


def _coerce_tenant_id(tenant_id: uuid.UUID | str) -> uuid.UUID:
    """Return ``tenant_id`` as a UUID, refusing anything else.

    A string is accepted only because identifiers arrive as text at the
    process boundary (a header, a CLI argument, a test literal).  A malformed
    value is a programming or boundary error, never a reason to continue
    unbound.
    """
    if isinstance(tenant_id, uuid.UUID):
        return tenant_id
    try:
        return uuid.UUID(str(tenant_id))
    except (AttributeError, TypeError, ValueError):
        raise TenantContextError(
            "Tenant context requires an organisation identifier."
        ) from None


def require_tenant_id() -> uuid.UUID:
    """Return the current tenant identifier or refuse to continue.

    Raises:
        TenantContextError: when no tenant context is bound.  This is the
            application-layer mirror of the server's ``current_tenant_id()``
            refusal: an unbound read is a defect, not an empty result.
    """
    tenant_id = _current_tenant.get()
    if tenant_id is None:
        raise TenantContextError(
            "Tenant context is not set; refusing to read tenant data."
        )
    return tenant_id


def peek_tenant_id() -> uuid.UUID | None:
    """Return the current tenant identifier, or ``None`` when unbound.

    Only for diagnostics and for tests that assert the absence of a context.
    Tenant-scoped work uses :func:`require_tenant_id`.
    """
    return _current_tenant.get()


@contextmanager
def tenant_context(tenant_id: uuid.UUID | str) -> Iterator[uuid.UUID]:
    """Bind ``tenant_id`` for the duration of the block, then restore.

    The previous binding is restored even when the block raises, so a nested
    or failed operation cannot widen the scope of the caller.

    Raises:
        TenantContextError: when ``tenant_id`` is not a UUID.
    """
    resolved = _coerce_tenant_id(tenant_id)
    token = _current_tenant.set(resolved)
    try:
        yield resolved
    finally:
        _current_tenant.reset(token)


async def apply_tenant_context(
    session: AsyncSession, tenant_id: uuid.UUID | str
) -> uuid.UUID:
    """Bind ``tenant_id`` on the database transaction and in process.

    The server function is transaction-local, so the binding ends with the
    transaction on both commit and rollback.  The returned identifier is the
    validated value that was bound.

    Raises:
        TenantContextError: when ``tenant_id`` is not a UUID.  No statement is
            issued in that case.
    """
    resolved = _coerce_tenant_id(tenant_id)
    await session.execute(
        sa.text(APPLY_TENANT_CONTEXT_SQL), {"tenant_id": str(resolved)}
    )
    return resolved


__all__ = [
    "APPLY_TENANT_CONTEXT_SQL",
    "TENANT_CONTEXT_SETTING",
    "TenantContextError",
    "apply_tenant_context",
    "peek_tenant_id",
    "require_tenant_id",
    "tenant_context",
]
