"""Unit tests for the P0-T09 tenant-context helpers.

Authority: ``AGENTS.md`` §2 invariant 12 and ``docs/specs/AUTH.md`` §6
(ISO-03, ISO-06, ISO-07).  These tests assert the fail-closed contract; the
server-side functions are exercised against PostgreSQL by the migration
integration suite.
"""

from __future__ import annotations

import uuid
from typing import Any, cast

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.tenant_context import (
    APPLY_TENANT_CONTEXT_SQL,
    TENANT_CONTEXT_SETTING,
    TenantContextError,
    apply_tenant_context,
    peek_tenant_id,
    require_tenant_id,
    tenant_context,
)

TENANT = uuid.UUID("11111111-1111-4111-8111-111111111111")
OTHER_TENANT = uuid.UUID("22222222-2222-4222-8222-222222222222")


class RecordingSession:
    """Minimal stand-in that records the statement and its parameters."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    async def execute(self, statement: Any, parameters: dict[str, Any]) -> None:
        self.calls.append((str(statement), parameters))


def test_unbound_context_refuses_to_continue() -> None:
    assert peek_tenant_id() is None
    with pytest.raises(TenantContextError):
        require_tenant_id()


def test_context_binds_and_restores() -> None:
    with tenant_context(TENANT) as bound:
        assert bound == TENANT
        assert require_tenant_id() == TENANT
    assert peek_tenant_id() is None


def test_string_identifier_is_validated_and_accepted() -> None:
    with tenant_context(str(TENANT)):
        assert require_tenant_id() == TENANT


def test_malformed_identifier_is_refused() -> None:
    for value in ("", "not-a-uuid", "11111111-1111-4111-8111"):
        with pytest.raises(TenantContextError), tenant_context(value):
            pytest.fail("a malformed identifier must not bind a context")


def test_nested_context_restores_the_outer_binding() -> None:
    with tenant_context(TENANT):
        with tenant_context(OTHER_TENANT):
            assert require_tenant_id() == OTHER_TENANT
        assert require_tenant_id() == TENANT
    assert peek_tenant_id() is None


def test_raised_error_does_not_leak_the_context() -> None:
    with pytest.raises(RuntimeError), tenant_context(TENANT):
        raise RuntimeError("failure inside the tenant block")
    assert peek_tenant_id() is None


def test_context_variable_name_matches_the_server_guc() -> None:
    assert TENANT_CONTEXT_SETTING == "app.tenant_id"
    assert "set_tenant_context" in APPLY_TENANT_CONTEXT_SQL


async def test_apply_tenant_context_binds_the_transaction() -> None:
    recorder = RecordingSession()
    bound = await apply_tenant_context(cast(AsyncSession, recorder), TENANT)
    assert bound == TENANT
    assert len(recorder.calls) == 1
    statement, parameters = recorder.calls[0]
    assert statement == APPLY_TENANT_CONTEXT_SQL
    assert parameters == {"tenant_id": str(TENANT)}


async def test_apply_tenant_context_issues_no_statement_for_a_bad_value() -> None:
    recorder = RecordingSession()
    with pytest.raises(TenantContextError):
        await apply_tenant_context(cast(AsyncSession, recorder), "not-a-uuid")
    assert recorder.calls == []
