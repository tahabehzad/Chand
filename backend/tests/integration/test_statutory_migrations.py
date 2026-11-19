"""ADR-007 acceptance against a disposable PostgreSQL 16 database.

Reuses a local official image; never pulls, migrates pish_dev or reads secrets.
Only this module's generated container is removed. Role/trigger bypass in the
synthetic-fixture helper is confined to a superuser transaction in that container.
"""

from __future__ import annotations

import asyncio
import os
import secrets
import socket
import subprocess
import time
import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import asyncpg
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.dialects.postgresql.base import PGDialect

from app.core.config import get_settings
from app.core.migration_lint import lint_migration
from app.models import Base, manager, statutory

ROOT = Path(__file__).resolve().parents[2]
TABLES = (
    "statutory_rule_set_versions",
    "statutory_source_artefacts",
    "statutory_parameter_signatures",
    "statutory_rule_changes",
    "statutory_verification_log",
)
#: The manager workspace tables delivered by migration 0004 (all tenant-scoped).
MANAGER_TABLES = (
    "employees",
    "employee_observations",
    "employee_evidence",
    "employee_evaluations",
    "salary_recommendations",
    "recommendation_decisions",
)
IDENTITY_TABLES = (
    "organizations",
    "users",
    "roles",
    "permissions",
    "role_permissions",
    "organization_memberships",
    "sessions",
)
#: The audit ledger tables delivered by migration 0005 (all tenant-scoped,
#: hash-chained / append-only).
AUDIT_TABLES = ("audit_logs", "access_log")
#: Work profile tables delivered by migration 0006 (all tenant-scoped).
WORK_PROFILE_TABLES = ("employee_work_profiles", "employee_work_documents", "employee_work_calculations")
#: Market reference tables delivered by migration 0007 (ADR-014).  Global reference
#: records with no personal data, therefore no tenant_id and no RLS.
ESTIMATION_TABLES = (
    "market_data_sources",
    "market_salary_observations",
    "market_salary_aggregates",
)
ALL_TABLES = TABLES + IDENTITY_TABLES + MANAGER_TABLES + AUDIT_TABLES + WORK_PROFILE_TABLES + ESTIMATION_TABLES
READER = "pish_statutory_reader"
REVIEWER = "pish_statutory_reviewer"
OWNER = "pish_migration_owner"
TENANT = "pish_test_tenant"
ROLES = (READER, REVIEWER, OWNER, TENANT)


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


def query(
    db: dict[str, Any], sql: str, *args: object, role: str | None = None
) -> list[asyncpg.Record]:
    async def run() -> list[asyncpg.Record]:
        conn = await connect(db)
        try:
            if role is not None:
                assert role in ROLES
                await conn.execute(f"SET ROLE {role}")
            if not sql.lstrip().upper().startswith("SELECT") and not args:
                await conn.execute(sql)
                return []
            return list(await conn.fetch(sql, *args))
        finally:
            await conn.close()

    return asyncio.run(run())


@pytest.fixture(scope="module")
def db() -> Iterator[dict[str, Any]]:
    image = "postgres:16.16-bookworm"
    if docker("image", "inspect", image).returncode:
        pytest.skip("NOT RUN: official PostgreSQL image/Docker unavailable; no pull attempted")
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    token = secrets.token_hex(5)
    container = "pish-p0t04-migtest-" + token
    database = {"port": port, "name": "pish_p0t04_migtest_" + token}
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
                query(database, "SELECT 1")
                break
            except (OSError, asyncpg.PostgresError):
                if time.monotonic() > deadline:
                    pytest.fail("Disposable PostgreSQL did not become ready")
                time.sleep(0.3)
        # Role provisioning is deliberately separate from the DB migration.
        query(
            database,
            (ROOT.parent / "infra/postgres/statutory_roles.sql").read_text(encoding="utf-8"),
        )
        query(
            database,
            f"CREATE ROLE {OWNER} NOLOGIN NOSUPERUSER NOBYPASSRLS; "
            f"CREATE ROLE {TENANT} NOLOGIN NOSUPERUSER NOBYPASSRLS; "
            f"GRANT CREATE ON SCHEMA public TO {OWNER}",
        )
        # Adversarial deployment defaults must not widen the column-only reader.
        query(
            database,
            f"ALTER DEFAULT PRIVILEGES FOR ROLE {OWNER} IN SCHEMA public "
            f"GRANT ALL ON TABLES TO {READER}, {REVIEWER}",
        )
        os.environ["DATABASE_URL"] = (
            f"postgresql+asyncpg://postgres@127.0.0.1:{port}/{database['name']}"
        )
        get_settings.cache_clear()
        cfg = Config(str(ROOT / "alembic.ini"))
        cfg.set_main_option("script_location", str(ROOT / "alembic"))
        cfg.attributes["connect_args"] = {"ssl": False, "server_settings": {"role": OWNER}}
        database["config"] = cfg
        command.upgrade(cfg, "head")
        yield database
    finally:
        # Generated name belongs exclusively to this fixture; never remove an existing service.
        removed = docker("rm", "-f", container)
        if previous is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = previous
        get_settings.cache_clear()
        assert removed.returncode == 0, "Disposable test container cleanup failed"


def test_roundtrip(db: dict[str, Any]) -> None:
    def names() -> set[str]:
        return {
            r["tablename"]
            for r in query(db, "SELECT tablename FROM pg_tables WHERE schemaname='public'")
        }

    assert set(TABLES) <= names()
    command.downgrade(db["config"], "base")
    assert not set(TABLES) & names()
    assert query(db, "SELECT version_num FROM alembic_version") == []
    assert query(db, "SELECT to_regclass('statutory_published_rules') AS v")[0]["v"] is None
    assert (
        query(
            db,
            "SELECT proname FROM pg_proc WHERE proname IN "
            "('statutory_identity_write_gate','trg_statutory_parameter_signatures_append_only',"
            "'set_tenant_context','current_tenant_id','pish_tenant_rls_violation')",
        )
        == []
    )
    command.upgrade(db["config"], "head")
    assert set(TABLES) <= names()
    # The manager-workspace migration (0004) and the audit-ledger migration
    # (0005) are both applied; head is the authoritative revision.
    from alembic.script import ScriptDirectory

    head = ScriptDirectory.from_config(db["config"]).get_current_head()
    assert query(db, "SELECT version_num FROM alembic_version")[0]["version_num"] == head
    violation = query(db, "SELECT * FROM pish_tenant_rls_violation()")
    assert violation == [], f"tenant RLS gaps after head ({head}): {violation}"


def test_tenant_context_functions_are_fail_closed(db: dict[str, Any]) -> None:
    """P0-T09: the transaction-local binding and the fail-closed reader."""
    assert query(db, "SELECT * FROM pish_tenant_rls_violation()") == []
    # A bound context round-trips inside its own statement's transaction.
    query(
        db,
        "DO $$ DECLARE bound uuid; BEGIN "
        "PERFORM set_tenant_context('11111111-1111-4111-8111-111111111111'); "
        "bound := current_tenant_id(); "
        "IF bound IS DISTINCT FROM '11111111-1111-4111-8111-111111111111'::uuid THEN "
        "RAISE EXCEPTION 'tenant context did not round-trip'; END IF; END $$",
    )
    # A new statement inherits no binding: the local GUC died with the previous
    # transaction, and the reader refuses instead of returning NULL.
    query(
        db,
        "DO $$ BEGIN "
        "BEGIN PERFORM current_tenant_id(); "
        "RAISE EXCEPTION 'unbound tenant context was readable'; "
        "EXCEPTION WHEN SQLSTATE '55000' THEN NULL; END; END $$",
    )


def test_models_and_storage_match_database(db: dict[str, Any]) -> None:
    assert set(Base.metadata.tables) == set(ALL_TABLES)
    for name in TABLES:
        columns = query(
            db,
            "SELECT column_name, is_nullable, column_default, "
            "format_type(a.atttypid,a.atttypmod) AS sql_type "
            "FROM information_schema.columns c JOIN pg_attribute a "
            "ON a.attrelid=('public.'||c.table_name)::regclass AND a.attname=c.column_name "
            "WHERE c.table_schema='public' AND c.table_name=$1",
            name,
        )
        model = Base.metadata.tables[name]
        assert {r["column_name"] for r in columns} == set(model.columns.keys())
        for row in columns:
            column = model.columns[row["column_name"]]
            # SQLAlchemy leaves this zero-argument third-party constructor untyped.
            declared = column.type.compile(dialect=PGDialect()).lower()  # type: ignore[no-untyped-call]
            normalized = declared.replace("varchar", "character varying").replace(
                "char(", "character("
            )
            assert row["sql_type"].replace(" ", "") == normalized.replace(" ", ""), (
                f"{name}.{column.name}"
            )
            assert (row["is_nullable"] == "YES") == column.nullable
        assert "tenant_id" not in model.columns
    assert (
        query(
            db,
            "SELECT character_maximum_length FROM information_schema.columns "
            "WHERE table_name='statutory_source_artefacts' AND column_name='retrieval_level'",
        )[0][0]
        == 2
    )
    assert (
        query(
            db,
            "SELECT column_default FROM information_schema.columns "
            "WHERE table_name='statutory_rule_set_versions' AND column_name='is_active'",
        )[0][0]
        == "false"
    )
    assert (
        lint_migration(
            (ROOT / "alembic/versions/0001_statutory_baseline.py").read_text(encoding="utf-8")
        )
        == []
    )
    assert query(db, "SELECT extname FROM pg_extension WHERE extname='pgcrypto'") == []


def test_rls_flags_and_owner(db: dict[str, Any]) -> None:
    rows = query(
        db,
        "SELECT c.relname,c.relrowsecurity,c.relforcerowsecurity,r.rolname,r.rolsuper,r.rolbypassrls "
        "FROM pg_class c JOIN pg_roles r ON r.oid=c.relowner "
        "WHERE c.relnamespace='public'::regnamespace AND c.relname=ANY($1)",
        list(TABLES),
    )
    assert len(rows) == 5
    assert all(
        r["relrowsecurity"]
        and r["relforcerowsecurity"]
        and r["rolname"] == OWNER
        and not r["rolsuper"]
        and not r["rolbypassrls"]
        for r in rows
    )


def test_declared_constraints_and_deferred_identity(db: dict[str, Any]) -> None:
    definitions = query(
        db,
        "SELECT t.relname,c.conname,pg_get_constraintdef(c.oid) AS d "
        "FROM pg_constraint c JOIN pg_class t ON t.oid=c.conrelid "
        "WHERE t.relname=ANY($1)",
        list(TABLES),
    )
    names = {r["conname"] for r in definitions}
    assert {
        "uq_statutory_rule_set_versions_year_revision",
        "uq_statutory_parameter_signatures_version_param_role",
        "fk_statutory_parameter_signatures_source_artefact_id",
        "fk_statutory_parameter_signatures_rule_set_version_id",
        "fk_statutory_rule_changes_rule_set_version_id",
        "fk_statutory_rule_set_versions_supersedes_id",
        "ck_statutory_source_artefacts_retrieval_level",
        "ck_statutory_rule_set_versions_status",
    } <= names
    # After migration 0002, the deferred actor FKs are installed on statutory tables.
    actor_fks = {
        "fk_statutory_rule_set_versions_verified_by",
        "fk_statutory_source_artefacts_archived_by",
        "fk_statutory_parameter_signatures_verifier_id",
        "fk_statutory_rule_changes_requested_by",
        "fk_statutory_rule_changes_approved_by",
        "fk_statutory_verification_log_transcriber_id",
        "fk_statutory_verification_log_verifier_id",
    }
    assert actor_fks <= names
    for table in TABLES:
        assert query(db, f"SELECT count(*) FROM {table}")[0][0] == 0


@pytest.mark.parametrize("table", TABLES)
@pytest.mark.parametrize("role", [OWNER, REVIEWER, READER, TENANT])
def test_rls_blocks_insert_for_all_roles(
    db: dict[str, Any], table: str, role: str
) -> None:
    async def run() -> None:
        conn = await connect(db)
        transaction = conn.transaction()
        await transaction.start()
        try:
            # Even with broad grants, RLS policies deny INSERT.
            await conn.execute(f"GRANT ALL ON ALL TABLES IN SCHEMA public TO {role}")
            await conn.execute(f"SET LOCAL ROLE {role}")
            with pytest.raises(asyncpg.InsufficientPrivilegeError, match="row-level security policy"):
                await conn.execute(f"INSERT INTO {table} DEFAULT VALUES")
        finally:
            await transaction.rollback()
            await conn.close()

    asyncio.run(run())


async def seed(conn: asyncpg.Connection) -> tuple[uuid.UUID, uuid.UUID]:
    # Only test postgres may bypass the write gate, inside a rolled-back transaction.
    await conn.execute("SET LOCAL session_replication_role='replica'")
    version_id, artefact_id = uuid.uuid4(), uuid.uuid4()
    for status, active, revision in [
        ("ACTIVE", True, 1),
        ("DRAFT", False, 2),
        ("RETIRED", False, 3),
        ("ACTIVE", False, 4),
    ]:
        await conn.execute(
            "INSERT INTO statutory_rule_set_versions "
            "(id,rule_year_shamsi,revision,effective_from,status,is_active,source_manifest,parameter_snapshot,verified_by) "
            "VALUES ($1,9999,$2,'9999-01-01',$3,$4,'[]','{}',$5)",
            version_id if revision == 1 else uuid.uuid4(),
            revision,
            status,
            active,
            uuid.uuid4(),
        )
    await conn.execute(
        "INSERT INTO statutory_source_artefacts "
        "(id,rule_year_shamsi,source_code,issuing_authority,document_title,source_url,retrieval_level,"
        "retrieved_at,sha256,s3_object_key,archived_by) "
        "VALUES ($1,9999,'S1','Synthetic','Synthetic','https://example.invalid','L1',now(),$2,'test',$3)",
        artefact_id,
        "a" * 64,
        uuid.uuid4(),
    )
    await conn.execute(
        "INSERT INTO statutory_parameter_signatures "
        "(id,rule_set_version_id,parameter_key,parameter_value,source_artefact_id,verifier_role,"
        "verifier_id,signature_sha256,signed_at) VALUES ($1,$2,'synthetic',1,$3,'VERIFIER',$4,$5,now())",
        uuid.uuid4(),
        version_id,
        artefact_id,
        uuid.uuid4(),
        "b" * 64,
    )
    await conn.execute("SET LOCAL session_replication_role='origin'")
    return version_id, artefact_id


def test_reader_projection_reviewer_and_spoofed_context(db: dict[str, Any]) -> None:
    async def run() -> None:
        conn = await connect(db)
        transaction = conn.transaction()
        await transaction.start()
        try:
            await seed(conn)
            for role in [OWNER, TENANT]:
                await conn.execute(f"GRANT SELECT ON ALL TABLES IN SCHEMA public TO {role}")
                await conn.execute(f"SET LOCAL ROLE {role}")
                await conn.execute(
                    "SET LOCAL app.current_tenant_id='00000000-0000-0000-0000-000000000001'; "
                    "SET LOCAL app.platform_authorized='true'"
                )
                for table in TABLES:
                    assert await conn.fetchval(f"SELECT count(*) FROM {table}") == 0
                await conn.execute("RESET ROLE")
            await conn.execute(f"SET LOCAL ROLE {REVIEWER}")
            assert await conn.fetchval("SELECT count(*) FROM statutory_rule_set_versions") == 4
            assert await conn.fetchval("SELECT count(*) FROM statutory_source_artefacts") == 1
            await conn.execute("RESET ROLE")
            await conn.execute(f"SET LOCAL ROLE {READER}")
            rows = await conn.fetch("SELECT * FROM statutory_published_rules")
            assert len(rows) == 1 and rows[0]["status"] == "ACTIVE"
            assert "verified_by" not in rows[0] and "source_manifest" not in rows[0]
            assert await conn.fetchval("SELECT count(id) FROM statutory_rule_set_versions") == 1
        finally:
            await transaction.rollback()
            await conn.close()

    asyncio.run(run())


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT verified_by FROM statutory_rule_set_versions",
        "SELECT source_manifest FROM statutory_rule_set_versions",
        "SELECT * FROM statutory_source_artefacts",
        "SELECT * FROM statutory_parameter_signatures",
        "SELECT * FROM statutory_rule_changes",
        "SELECT * FROM statutory_verification_log",
        "SET ROLE pish_statutory_reviewer",
    ],
)
def test_reader_cannot_read_actor_evidence_or_escalate(db: dict[str, Any], sql: str) -> None:
    # A separate non-superuser connection is essential: SET ROLE from postgres
    # retains the session superuser's ability to select another role.
    async def run() -> None:
        admin = await connect(db)
        try:
            await admin.execute(
                "CREATE ROLE pish_reader_login LOGIN NOSUPERUSER NOBYPASSRLS; "
                "GRANT pish_statutory_reader TO pish_reader_login"
            )
            conn = await asyncpg.connect(
                host="127.0.0.1",
                port=db["port"],
                user="pish_reader_login",
                database=db["name"],
                ssl=False,
            )
            try:
                await conn.execute(f"SET ROLE {READER}")
                with pytest.raises(asyncpg.InsufficientPrivilegeError):
                    await conn.execute(sql)
            finally:
                await conn.close()
        finally:
            await admin.execute("DROP ROLE IF EXISTS pish_reader_login")
            await admin.close()

    asyncio.run(run())


@pytest.mark.parametrize(
    "operation",
    [
        "UPDATE statutory_parameter_signatures SET parameter_value=2",
        "DELETE FROM statutory_parameter_signatures",
        "TRUNCATE statutory_parameter_signatures",
    ],
)
def test_signatures_append_only_independently_of_identity_gate(
    db: dict[str, Any], operation: str
) -> None:
    async def run() -> None:
        conn = await connect(db)
        transaction = conn.transaction()
        await transaction.start()
        try:
            await seed(conn)
            # The append-only trigger (from P0-T04) remains active after 0002.
            # No need to disable the old write gate (it was replaced by retention guard).
            with pytest.raises(asyncpg.RaiseError, match="append-only"):
                await conn.execute(operation)
        finally:
            await transaction.rollback()
            await conn.close()

    asyncio.run(run())


@pytest.mark.parametrize("column,value", [("status", "INVALID"), ("retrieval_level", "L9")])
def test_storage_checks_reject_invalid_values(db: dict[str, Any], column: str, value: str) -> None:
    async def run() -> None:
        conn = await connect(db)
        transaction = conn.transaction()
        await transaction.start()
        try:
            await seed(conn)
            table = (
                "statutory_rule_set_versions"
                if column == "status"
                else "statutory_source_artefacts"
            )
            # Retention guard blocks UPDATE on statutory_source_artefacts; disable it to test check constraint.
            if table == "statutory_source_artefacts":
                await conn.execute(
                    "ALTER TABLE statutory_source_artefacts DISABLE TRIGGER statutory_retention_guard"
                )
            with pytest.raises(asyncpg.CheckViolationError):
                await conn.execute(f"UPDATE {table} SET {column}=$1", value)
        finally:
            await transaction.rollback()
            await conn.close()

    asyncio.run(run())


@pytest.mark.parametrize(
    "unsafe_change",
    [
        "ALTER ROLE pish_statutory_reader LOGIN",
        "ALTER ROLE pish_statutory_reviewer BYPASSRLS",
        "GRANT pish_migration_owner TO pish_statutory_reader",
    ],
)
def test_role_provisioning_rejects_unsafe_existing_roles(
    db: dict[str, Any], unsafe_change: str
) -> None:
    async def run() -> None:
        conn = await connect(db)
        transaction = conn.transaction()
        await transaction.start()
        try:
            await conn.execute(unsafe_change)
            script = (ROOT.parent / "infra/postgres/statutory_roles.sql").read_text(
                encoding="utf-8"
            )
            with pytest.raises(asyncpg.RaiseError, match="unsafe privileges"):
                await conn.execute(script)
        finally:
            await transaction.rollback()
            await conn.close()

    asyncio.run(run())


def test_role_provisioning_is_idempotent(db: dict[str, Any]) -> None:
    query(db, (ROOT.parent / "infra/postgres/statutory_roles.sql").read_text(encoding="utf-8"))
    rows = query(
        db,
        "SELECT rolcanlogin,rolsuper,rolbypassrls,rolcreaterole,rolcreatedb "
        "FROM pg_roles WHERE rolname=ANY($1)",
        [READER, REVIEWER],
    )
    assert len(rows) == 2 and all(not any(row.values()) for row in rows)
