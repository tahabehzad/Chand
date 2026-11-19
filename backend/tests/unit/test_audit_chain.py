"""P0-T10 unit tests for the hash-chained audit ledger writer and verifier."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, cast
from uuid import UUID, uuid4

import pytest

from app.services.audit_service import (
    GENESIS_HASH,
    AuditChainError,
    canonical_json,
    chain_hash,
    verify_chain,
)

TENANT: UUID = uuid4()
ACTOR: UUID = uuid4()
OTHER_TENANT: UUID = uuid4()
OTHER_ACTOR: UUID = uuid4()


def _row(
    previous_hash: str,
    *,
    tenant_id: UUID = TENANT,
    actor_id: UUID | None = ACTOR,
    actor_type: str = "USER",
    event_type: str = "SIMULATION_RUN",
    chain_hash_value: str | None = None,
) -> dict[str, Any]:
    timestamp = datetime(1404, 1, 1, tzinfo=UTC)
    payload: dict[str, Any] = {"event_type": event_type, "rule_set_version": "1404.1"}
    return {
        "previous_hash": previous_hash,
        "chain_hash": chain_hash_value
        or chain_hash(previous_hash, timestamp, tenant_id, actor_id, actor_type, payload),
        "timestamp": timestamp,
        "tenant_id": tenant_id,
        "actor_id": actor_id,
        "actor_type": actor_type,
        "payload": payload,
    }


def _chained_row(previous: dict[str, Any]) -> dict[str, Any]:
    return _row(cast(str, previous["chain_hash"]))


def test_canonical_json_is_deterministic_and_sorted() -> None:
    assert canonical_json({"b": 2, "a": 1}) == '{"a":1,"b":2}'
    assert canonical_json({"a": 1, "b": 2}) == '{"a":1,"b":2}'


def test_chain_hash_is_deterministic() -> None:
    timestamp = datetime(1404, 1, 1, tzinfo=UTC)
    payload = {"k": "v"}
    first = chain_hash(GENESIS_HASH, timestamp, TENANT, ACTOR, "USER", payload)
    second = chain_hash(GENESIS_HASH, timestamp, TENANT, ACTOR, "USER", payload)
    assert first == second
    assert len(first) == 64


def test_chain_hash_changes_with_every_input() -> None:
    timestamp = datetime(1404, 1, 1, tzinfo=UTC)
    payload = {"k": "v"}
    base = chain_hash(GENESIS_HASH, timestamp, TENANT, ACTOR, "USER", payload)
    assert base != chain_hash(GENESIS_HASH, timestamp, OTHER_TENANT, ACTOR, "USER", payload)
    assert base != chain_hash(GENESIS_HASH, timestamp, TENANT, OTHER_ACTOR, "USER", payload)
    assert base != chain_hash(GENESIS_HASH, timestamp, TENANT, ACTOR, "SYSTEM", payload)
    assert base != chain_hash(GENESIS_HASH, timestamp, TENANT, None, "SYSTEM", payload)


def test_genesis_anchor_is_fixed() -> None:
    assert len(GENESIS_HASH) == 64
    assert all(c == "0" for c in GENESIS_HASH)


def test_verify_chain_accepts_a_valid_chain() -> None:
    row0 = _row(GENESIS_HASH)
    row1 = _row(row0["chain_hash"])
    row2 = _row(row1["chain_hash"])
    verify_chain([row0, row1, row2])


def test_verify_chain_rejects_broken_previous_hash() -> None:
    row0 = _row(GENESIS_HASH)
    row1 = _row(row0["chain_hash"])
    tampered = dict(row1)
    tampered["previous_hash"] = "f" * 64
    with pytest.raises(AuditChainError) as exc:
        verify_chain([row0, tampered])
    assert "previous_hash" in str(exc.value)


def test_verify_chain_rejects_broken_chain_hash() -> None:
    row0 = _row(GENESIS_HASH)
    row1 = _row(row0["chain_hash"])
    tampered = dict(row1)
    tampered["chain_hash"] = "f" * 64
    with pytest.raises(AuditChainError) as exc:
        verify_chain([row0, tampered])
    assert "chain_hash" in str(exc.value)


def test_verify_chain_rejects_wrong_genesis() -> None:
    row0 = _row("f" * 64)
    with pytest.raises(AuditChainError):
        verify_chain([row0])


def test_verify_chain_accepts_system_actor_with_no_actor_id() -> None:
    timestamp = datetime(1404, 1, 1, tzinfo=UTC)
    payload = {"k": "v"}
    row0 = {
        "previous_hash": GENESIS_HASH,
        "chain_hash": chain_hash(GENESIS_HASH, timestamp, TENANT, None, "SYSTEM", payload),
        "timestamp": timestamp,
        "tenant_id": TENANT,
        "actor_id": None,
        "actor_type": "SYSTEM",
        "payload": payload,
    }
    verify_chain([row0])
