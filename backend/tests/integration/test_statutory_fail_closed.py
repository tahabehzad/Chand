"""ADR-007 fail-closed gate: a missing or unsafe statutory role stops the migration.

ADR-007 requires that "a missing or unsafe role fails closed" and that
"P0-T04 permits no application writes to any of the five tables". The happy
path (roles provisioned, migration succeeds) and the write gate are covered by
``test_statutory_migrations.py``; this module covers the refused path that was
previously only ever exercised by hand.

Each scenario runs in its own generated container, so no test depends on the
order in which they run. The containers are named by this module alone and are
removed in ``finally``. No existing container, volume or database is touched,
``pish_dev`` is never migrated, and no image is pulled.
"""

from __future__ import annotations

import asyncio
import os
import secrets
import socket
import subprocess
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import asyncpg
import pytest
from alembic import command
from alembic.config import Config

from app.core.config import ConfigurationError, get_settings

ROOT = Path(__file__).resolve().parents[2]
TABLES = (
    "statutory_rule_set_versions",
    "statutory_source_artefacts",
    "statutory_parameter_signatures",
    "statutory_rule_changes",
    "statutory_verification_log",
)
OWNER = "pish_migration_owner"
READER = "pish_statutory_reader"
REVIEWER = "pish_statutory_reviewer"


def docker(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", *args], capture_output=True, text=True, timeout=60, check=False
    )


async def connect(db: dict[str, Any]) -> asyncpg.Connection:
    return await asyncpg.connect(
        host="127.0.0.1",
        port=db["port"],
        user="postgres",
        database=db["name"],
        ssl=False,
        timeout=5,
    )


async def execute(db: dict[str, Any], sql: str) -> None:
    conn = await connect(db)
    try:
        await conn.execute(sql)
    finally:
        await conn.close()


async def fetch(db: dict[str, Any], sql: str, *args: object) -> list[asyncpg.Record]:
    conn = await connect(db)
    try:
        return list(await conn.fetch(sql, *args))
    finally:
        await conn.close()


@pytest.fixture(scope="module")
def db() -> Iterator[dict[str, Any]]:
    """A disposable PostgreSQL 16 container with no statutory roles provisioned."""
    image = "postgres:16.16-bookworm"
    if docker("image", "inspect", image).returncode:
        pytest.skip("NOT RUN: official PostgreSQL image/Docker unavailable; no pull attempted")
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    token = secrets.token_hex(5)
    container = "pish-p0t04-failclosed-" + token
    database = {"port": port, "name": "pish_p0t04_failclosed_" + token}
    started = docker(
        "run",
        "-d",
        "--rm",
        "--name",
        container,
        "-p",
        f"127.0.0.1:{port}:5432",
        "-e",
        "POSTGRES_HOST_AUTH_METHOD=trust",
        "-e",
        f"POSTGRES_DB={database['name']}",
        image,
    )
    if started.returncode:
        pytest.fail("Disposable PostgreSQL container could not start")
    previous = os.environ.get("DATABASE_URL")
    try:
        deadline = time.monotonic() + 45
        while True:
            try:
                asyncio.run(fetch(database, "SELECT 1"))
                break
            except (OSError, asyncpg.PostgresError):
                if time.monotonic() > deadline:
                    pytest.fail("Disposable PostgreSQL did not become ready")
                time.sleep(0.3)
        asyncio.run(
            execute(
                database,
                f"CREATE ROLE {OWNER} NOLOGIN NOSUPERUSER NOBYPASSRLS; "
                f"GRANT CREATE ON SCHEMA public TO {OWNER}",
            )
        )
        yield database
    finally:
        removed = docker("rm", "-f", container)
        if previous is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = previous
        get_settings.cache_clear()
        assert removed.returncode == 0, "Disposable test container cleanup failed"


def migration_config(db: dict[str, Any]) -> Config:
    """A migration configuration bound to the disposable database only."""
    os.environ["DATABASE_URL"] = (
        f"postgresql+asyncpg://postgres@127.0.0.1:{db['port']}/{db['name']}"
    )
    get_settings.cache_clear()
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "alembic"))
    cfg.attributes["connect_args"] = {"ssl": False, "server_settings": {"role": OWNER}}
    return cfg


def upgrade(db: dict[str, Any]) -> str:
    """Run the migration; return the sanitized diagnostic, empty when it succeeds."""
    try:
        command.upgrade(migration_config(db), "head")
    except ConfigurationError as exc:
        return str(exc)
    return ""


def table_names(db: dict[str, Any]) -> set[str]:
    rows = asyncio.run(fetch(db, "SELECT tablename FROM pg_tables WHERE schemaname='public'"))
    return {r["tablename"] for r in rows}


def test_missing_roles_fail_closed(db: dict[str, Any]) -> None:
    """No statutory roles: the migration refuses and leaves no schema behind."""
    message = upgrade(db)
    assert message, "the migration must refuse to run without the statutory roles"
    # The refusal is actionable but discloses nothing about the deployment.
    assert "statutory" in message.lower()
    assert db["name"] not in message and str(db["port"]) not in message
    assert not set(TABLES) & table_names(db)
    assert "alembic_version" not in table_names(db)


def test_unsafe_role_fails_closed(db: dict[str, Any]) -> None:
    """A statutory role that may log in is refused exactly like a missing one."""
    asyncio.run(
        execute(
            db,
            f"CREATE ROLE {READER} LOGIN NOSUPERUSER NOBYPASSRLS; "
            f"CREATE ROLE {REVIEWER} NOLOGIN NOSUPERUSER NOBYPASSRLS",
        )
    )
    message = upgrade(db)
    assert message, "the migration must refuse an unsafe statutory role"
    assert "statutory" in message.lower()
    assert db["name"] not in message and str(db["port"]) not in message
    assert not set(TABLES) & table_names(db)


def test_provisioned_roles_allow_the_migration(db: dict[str, Any]) -> None:
    """The same database succeeds once the roles are provisioned safely.

    This proves the two refusals above were the role precondition and not an
    unrelated failure of the migration itself.
    """
    asyncio.run(execute(db, f"ALTER ROLE {READER} NOLOGIN"))
    message = upgrade(db)
    assert message == "", f"the migration must succeed once the roles are safe: {message}"
    names = table_names(db)
    assert set(TABLES) <= names
    rows = asyncio.run(
        fetch(
            db,
            "SELECT relname, relrowsecurity, relforcerowsecurity FROM pg_class "
            "WHERE relname=ANY($1)",
            list(TABLES),
        )
    )
    assert len(rows) == 5
    assert all(r["relrowsecurity"] and r["relforcerowsecurity"] for r in rows)
