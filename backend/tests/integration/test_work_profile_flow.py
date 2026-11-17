"""Isolated PostgreSQL acceptance for ADR-012; never truncate pish_dev tables.

Authority: WORK_PROFILE_PAYROLL acceptance; tenant/encryption invariants.
Related: migration 0006, real FastAPI routes and service.
Scope: generated disposable schema/NOLOGIN role, synthetic records and test keys.
"""

from __future__ import annotations

import asyncio
import hashlib
import importlib.util
import uuid
from collections.abc import AsyncIterator, Iterator
from pathlib import Path
from typing import Any

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.api.deps import DbSession, ManagerContext, NotAuthenticatedError, get_db, require_manager
from app.core.config import get_settings
from app.core.security import local_workspace
from app.core.security.tenant_context import apply_tenant_context
from app.main import create_app

TENANT_A, TENANT_B, EMPLOYEE_A, EMPLOYEE_B, ACTOR = [uuid.uuid4() for _ in range(5)]
PROFILE = {"job_title": "Demo analyst", "daily_hours": "4.4", "weekly_days": 5,
           "recognised_seniority_months": 12, "employer_tenure_months": 12}
PAYROLL = {"gross_monthly_rial": 220_000_000}
PDF = b"%PDF-1.4\nsynthetic document\n%%EOF"


@pytest.fixture(scope="module")
def isolated(tmp_path_factory: pytest.TempPathFactory) -> Iterator[dict[str, Any]]:
    suffix = uuid.uuid4().hex
    schema, role = "wp_test_" + suffix, "wp_reader_" + suffix
    dsn = get_settings().database_url.get_secret_value().replace("postgresql://", "postgresql+asyncpg://", 1)
    if not dsn:
        pytest.fail("Explicit local PostgreSQL configuration is required.")
    engine = create_async_engine(dsn, poolclass=NullPool, hide_parameters=True,
        connect_args={"server_settings": {"search_path": schema + ",public"}})
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async def setup() -> None:
        async with engine.begin() as connection:
            await connection.execute(text(f'CREATE SCHEMA "{schema}"'))
            await connection.execute(text("CREATE TABLE organizations (id uuid PRIMARY KEY)"))
            await connection.execute(text("""CREATE TABLE employees (
                id uuid PRIMARY KEY, tenant_id uuid NOT NULL, name varchar(120) NOT NULL,
                role_label varchar(60) NOT NULL, start_date varchar(10) NOT NULL,
                created_by uuid, created_at timestamptz DEFAULT now(), updated_at timestamptz DEFAULT now())"""))
            path = Path("alembic/versions/0006_work_profiles.py")
            spec = importlib.util.spec_from_file_location("workspace_test_migration", path)
            assert spec and spec.loader
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            def apply(sync_connection: Any) -> None:
                with Operations.context(MigrationContext.configure(sync_connection)):
                    module.upgrade()
            await connection.run_sync(apply)
            for tenant, employee in ((TENANT_A, EMPLOYEE_A), (TENANT_B, EMPLOYEE_B)):
                await connection.execute(text("INSERT INTO organizations(id) VALUES (:id)"), {"id": tenant})
                await connection.execute(text("INSERT INTO employees(id,tenant_id,name,role_label,start_date) VALUES (:id,:tenant,'Demo','Analyst','2025-01-01')"), {"id": employee, "tenant": tenant})
            await connection.execute(text(f'CREATE ROLE "{role}" NOLOGIN NOSUPERUSER NOBYPASSRLS'))
            await connection.execute(text(f'GRANT USAGE ON SCHEMA "{schema}" TO "{role}"'))
            await connection.execute(text(f'GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA "{schema}" TO "{role}"'))
    asyncio.run(setup())
    key = tmp_path_factory.mktemp("workspace-key") / "master.key"
    key.write_bytes(b"synthetic-workspace-test-key-32!!!"[:32])
    key.with_suffix(".ready").write_text(hashlib.sha256(key.read_bytes()).hexdigest(), encoding="ascii")
    original_key = local_workspace.KEY_PATH
    local_workspace.KEY_PATH = key
    app = create_app(get_settings())

    async def database() -> AsyncIterator[AsyncSession]:
        async with factory() as session:
            yield session

    async def manager(request: Request, db: DbSession) -> AsyncIterator[ManagerContext]:
        token = request.headers.get("Authorization")
        if token not in {"Bearer test-a", "Bearer test-b"}:
            raise NotAuthenticatedError()
        tenant = TENANT_A if token == "Bearer test-a" else TENANT_B
        await apply_tenant_context(db, tenant)
        yield ManagerContext(ACTOR, uuid.uuid4(), tenant, "Demo", "test@example.invalid")

    app.dependency_overrides[get_db] = database
    app.dependency_overrides[require_manager] = manager
    with TestClient(app) as client:
        yield {"client": client, "factory": factory, "schema": schema, "role": role}
    local_workspace.KEY_PATH = original_key

    async def cleanup() -> None:
        async with engine.begin() as connection:
            await connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
            await connection.execute(text(f'DROP ROLE "{role}"'))
        await engine.dispose()
    asyncio.run(cleanup())


def url(employee: uuid.UUID = EMPLOYEE_A, path: str = "work-profile") -> str:
    return f"/api/v1/manager/employees/{employee}/{path}"


def headers(tenant: str = "a") -> dict[str, str]:
    return {"Authorization": "Bearer test-" + tenant}


def test_profile_real_persistence_revision_conflict_and_encrypted_text(isolated: dict[str, Any]) -> None:
    client = isolated["client"]
    assert client.get(url(), headers=headers()).json() is None
    response = client.put(url(), headers=headers(), json={"profile": PROFILE, "expected_revision": 0})
    assert response.status_code == 200
    assert response.json()["revision"] == 1
    assert client.get(url(), headers=headers()).json()["profile"]["job_title"] == "Demo analyst"
    assert client.put(url(), headers=headers(), json={"profile": PROFILE, "expected_revision": 0}).status_code == 409
    async def inspect() -> None:
        async with isolated["factory"]() as session:
            row = (await session.execute(text("SELECT ciphertext, actor_id FROM employee_work_profiles"))).one()
            assert b"Demo analyst" not in row[0]
            assert row[1] == ACTOR
    asyncio.run(inspect())


def test_document_upload_download_magic_encryption_and_tenant_boundaries(isolated: dict[str, Any]) -> None:
    client = isolated["client"]
    path = url(path="work-documents")
    response = client.post(path, headers=headers(), files={"file": ("demo.pdf", PDF, "application/pdf")})
    assert response.status_code == 201
    document = response.json()
    assert document["sha256"] == hashlib.sha256(PDF).hexdigest()
    assert client.get(path, headers=headers()).json()[0]["id"] == document["id"]
    download = path + "/" + document["id"] + "/content"
    result = client.get(download, headers=headers())
    assert result.content == PDF
    assert result.headers["cache-control"] == "no-store"
    assert result.headers["x-content-type-options"] == "nosniff"
    assert client.get(download, headers=headers("b")).status_code == 404
    assert client.get(download).status_code == 401
    assert client.post(path, headers=headers(), files={"file": ("bad.pdf", b"malicious", "application/pdf")}).status_code == 422
    assert client.post(path, headers=headers(), files={"file": ("bad.pdf", b"x" * 5_100_000, "application/pdf")}).status_code == 413
    async def inspect() -> None:
        async with isolated["factory"]() as session:
            row = (await session.execute(text("SELECT ciphertext,metadata_ciphertext FROM employee_work_documents"))).one()
            assert PDF not in row[0] and b"demo.pdf" not in row[1]
    asyncio.run(inspect())


def test_calculation_uses_saved_hours_seniority_and_restores_immutable_result(isolated: dict[str, Any]) -> None:
    client = isolated["client"]
    response = client.post(url(path="work-profile/calculate"), headers=headers(), json={"payroll": PAYROLL})
    assert response.status_code == 200
    result = response.json()
    assert result["work_context"]["gross_rial"] == 111_410_000
    assert result["work_context"]["seniority_rial"] == 1_410_000
    assert result["work_context"]["provenance"]["gross_rial"]["rule_version"] == "1404.1"
    assert len(result["payroll"]["calculation_hash"]) == 64
    assert result["payroll"]["termination_liability"]["exit_severance_rial"] == 111_410_000
    restored = client.get(url(path="work-profile/calculations/latest"), headers=headers())
    assert restored.json() == result
    assert client.get(url(), headers=headers("b")).status_code == 404
    assert client.put(url(), headers=headers("b"), json={"profile": PROFILE, "expected_revision": 1}).status_code == 404
    async def inspect() -> None:
        from sqlalchemy.exc import DBAPIError
        async with isolated["factory"]() as session:
            with pytest.raises(DBAPIError):
                await session.execute(text("UPDATE employee_work_calculations SET calculation_hash='tampered'"))
            await session.rollback()
    asyncio.run(inspect())


def test_rls_is_forced_and_restricted_role_cannot_see_another_tenant(isolated: dict[str, Any]) -> None:
    async def inspect() -> None:
        async with isolated["factory"]() as session:
            flags = (await session.execute(text("SELECT relrowsecurity,relforcerowsecurity FROM pg_class JOIN pg_namespace n ON n.oid=relnamespace WHERE n.nspname=:schema AND relname IN ('employee_work_profiles','employee_work_documents','employee_work_calculations')"), {"schema": isolated["schema"]})).all()
            assert len(flags) == 3 and all(row[0] and row[1] for row in flags)
            role = isolated["role"]
            await session.execute(text(f'SET LOCAL ROLE "{role}"'))
            await apply_tenant_context(session, TENANT_B)
            assert (await session.execute(text("SELECT count(*) FROM employee_work_profiles"))).scalar() == 0
            await apply_tenant_context(session, TENANT_A)
            assert (await session.execute(text("SELECT count(*) FROM employee_work_profiles"))).scalar() == 1
    asyncio.run(inspect())


def test_unknown_key_reference_refuses_plaintext_fallback(isolated: dict[str, Any]) -> None:
    async def change(key: str) -> None:
        async with isolated["factory"]() as session:
            await session.execute(text("UPDATE employee_work_profiles SET key_id=:key"), {"key": key})
            await session.commit()
    asyncio.run(change("unrecognised-key"))
    assert isolated["client"].get(url(), headers=headers()).status_code == 503
    asyncio.run(change(local_workspace.KEY_ID))
