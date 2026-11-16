"""Alembic environment for the Pish Hesabdari backend.

Authority
---------
``docs/specs/DEPLOYMENT.md`` §4.2 (migration tool rules);
``docs/specs/STATUTORY_DATABASE_CONTRACT.md`` §5 (environment contract);
``docs/PISH_HESABDARI_HOLY_BIBLE.md`` §5.8 (migration strategy).

Security rules (contract AC-13)
-------------------------------
- The database URL comes only from the approved ``DATABASE_URL`` variable,
  read through ``app.core.config`` (fail-closed when absent). It is never
  logged, printed, embedded in a message or written into ``alembic.ini``.
- SSL/other driver parameters may be supplied programmatically through
  ``config.attributes["connect_args"]``. The integration harness passes
  ``ssl=False`` only for its disposable loopback test server; production
  connections keep TLS enforcement at the server (P0-T03 ``pg_hba.conf``).
- ``sqlalchemy.engine`` logging stays at WARNING: a URL with credentials is
  rendered only at INFO/DEBUG.

Driver note: the approved dependency set includes ``asyncpg`` and not
``psycopg``, so migrations run on SQLAlchemy's async engine.
"""

from __future__ import annotations

import asyncio
import sys
from typing import Any

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.config import ConfigurationError, get_settings
from app.models import Base, statutory  # noqa: F401 -- register autogenerate metadata

config = context.config

# Autogenerate support: the statutory models are the current metadata; later
# schema tasks register their models on the same Base.
target_metadata = Base.metadata

#: Scheme prefix required for the async driver.
_ASYNC_PREFIX = "postgresql+asyncpg://"

#: Fixed, self-authored markers for the migration's own fail-closed guards.
#: Only these literal strings may ever be reflected back to an operator; every
#: other driver message stays hidden, so no DSN, parameter or credential can
#: reach a log, a ticket or a terminal.
_ROLE_PRECONDITION_MARKERS = (
    "Provision safe statutory NOLOGIN roles before migration",
    "Statutory roles must not inherit other roles",
)


def _sanitized_migration_failure(exc: Exception) -> str:
    """Return a diagnostic for a failed migration that renders nothing unsafe.

    The migration owner is a trusted deployment principal, and a missing or
    unsafe statutory role is an operator-actionable precondition failure. The
    two markers below are literal strings owned by this repository, so echoing
    them discloses nothing about the deployment. Any other driver error keeps
    the generic message.
    """
    text = str(exc)
    if any(marker in text for marker in _ROLE_PRECONDITION_MARKERS):
        return (
            "Migration refused: the safe statutory database roles are not provisioned "
            "as required (infra/postgres/statutory_roles.sql). No schema was changed."
        )
    return "Migration failed; inspect sanitized deployment checks."


def _database_url() -> str:
    """Return the configured async database URL, never rendering it."""
    url = get_settings().database_url.get_secret_value()
    if not url:
        raise ConfigurationError(
            "DATABASE_URL is empty: Alembic refuses to run without an explicit "
            "database URL (fail-closed; docs/specs/STATUTORY_DATABASE_CONTRACT.md §5)."
        )
    if url.startswith("postgresql://"):
        url = _ASYNC_PREFIX + url.removeprefix("postgresql://")
    if not url.startswith(_ASYNC_PREFIX):
        raise ConfigurationError(
            "DATABASE_URL must use the postgresql+asyncpg:// driver scheme "
            "(psycopg is not an approved dependency)."
        )
    return url


def _connectable() -> Any:
    connect_args: dict[str, Any] = dict(config.attributes.get("connect_args", {}))
    return async_engine_from_config(
        {"sqlalchemy.url": _database_url()},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=connect_args,
        hide_parameters=True,
    )


def run_migrations_offline() -> None:
    """Emit SQL to the script output without a database connection."""
    context.configure(
        url=_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live connection (async engine)."""

    def do_migrations(connection: Connection) -> None:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()

    async def run() -> None:
        connectable = None
        try:
            connectable = _connectable()
            async with connectable.connect() as connection:
                await connection.run_sync(do_migrations)
        except Exception as exc:
            # Driver errors may contain DSNs/parameters. Do not render them.
            import traceback
            print(f"ACTUAL ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
            traceback.print_exception(type(exc), exc, exc.__traceback__)
            raise ConfigurationError(_sanitized_migration_failure(exc)) from None
        finally:
            if connectable is not None:
                await connectable.dispose()

    asyncio.run(run())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
