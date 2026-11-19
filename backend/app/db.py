"""Database session layer for the manager workspace.

Authority
---------
``docs/specs/DEPLOYMENT.md`` §5.1 (the database is configured only through
``DATABASE_URL``); ``AGENTS.md`` §2 Security invariants 12-14 (tenant context,
fail-closed).

Related
-------
``app/core/config.py`` (``Settings.database_url``), ``app/core/security/
tenant_context.py`` (the per-transaction binding), ``alembic/versions/0004``.

Scope
-----
One async engine and one session factory.  Nothing else: no model imports
(they belong to ``app.models``), no query helpers and no implicit tenant
behaviour — the tenant binding is applied per request by ``app.api.deps``.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import ConfigurationError, get_settings


def build_engine(database_url: str | None = None) -> AsyncEngine:
    """Return the async engine for the configured or the supplied DSN.

    The explicit DSN argument exists for tests and for the migration harness;
    the application path always reads the fail-closed configuration.
    """
    url = database_url
    if url is None:
        settings = get_settings()
        url = settings.database_url.get_secret_value()
    if not url:
        raise ConfigurationError("DATABASE_URL is not configured; refusing to connect.")
    # The approved dependency set includes asyncpg, not psycopg; a plain
    # ``postgresql://`` DSN is upgraded to the async driver scheme.
    if url.startswith("postgresql://"):
        url = "postgresql+asyncpg://" + url.removeprefix("postgresql://")
    # NullPool: each request opens a fresh connection on its own event loop.
    # A pooled asyncpg connection binds to the loop that created it, which a
    # request worker must never depend on.
    return create_async_engine(url, poolclass=NullPool)


def build_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Return the session factory used by the request dependency."""
    return async_sessionmaker(engine, expire_on_commit=False)


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the process-wide session factory."""
    return build_session_factory(build_engine())


async def session_scope(
    factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    """Yield one session and always close it (commit is the caller's duty)."""
    session = factory()
    try:
        yield session
    finally:
        await session.close()


__all__ = [
    "build_engine",
    "build_session_factory",
    "get_session_factory",
    "session_scope",
]
