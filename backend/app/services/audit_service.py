"""P0-T10: hash-chained audit ledger writer and verifier.

Authority
---------
``docs/specs/AUTH.md`` §7.2 (``H_n = SHA256(H_{n-1} ‖ ISO8601_timestamp ‖
tenant_id ‖ actor_id ‖ actor_type ‖ canonical_JSON(payload))``);
``docs/PISH_HESABDARI_HOLY_BIBLE.md`` §7.2 and §2181; CR-10 / CR-11.

The writer computes chain hashes in the application layer (SHA-256 is never
pushed into the database).  The verifier recomputes the chain from the
genesis hash and confirms every row's ``chain_hash`` and ``previous_hash``.

Canonical JSON: sorted keys, no insignificant whitespace, UTF-8.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

#: Genesis (anchor) hash for the first ledger row.  Fixed and published so the
#: chain is reproducible from an empty ledger.
GENESIS_HASH = "0" * 64

#: Maximum actors per entry is one; ``actor_id`` may be None for SYSTEM events.


def canonical_json(payload: dict[str, Any]) -> str:
    """Return deterministic, sorted-key, compact UTF-8 JSON for hashing."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def chain_hash(  # noqa: PLR0917 — domain hash signature; positional args are the chain inputs
    previous_hash: str,
    timestamp: datetime,
    tenant_id: UUID,
    actor_id: UUID | None,
    actor_type: str,
    payload: dict[str, Any],
) -> str:
    """Compute ``H_n = SHA256(H_{n-1} ‖ ISO8601 ‖ tenant_id ‖ actor_id ‖ actor_type ‖ payload)."""
    hasher = hashlib.sha256()
    hasher.update(previous_hash.encode("utf-8"))
    hasher.update(b"\x00")
    hasher.update(timestamp.astimezone(UTC).isoformat().encode("utf-8"))
    hasher.update(b"\x00")
    hasher.update(str(tenant_id).encode("utf-8"))
    hasher.update(b"\x00")
    hasher.update(str(actor_id).encode("utf-8") if actor_id is not None else b"")
    hasher.update(b"\x00")
    hasher.update(actor_type.encode("utf-8"))
    hasher.update(b"\x00")
    hasher.update(canonical_json(payload).encode("utf-8"))
    return hasher.hexdigest()


class AuditChainError(ValueError):
    """Raised when the hash chain is broken or a ledger row is invalid."""

    code = "AUDIT_CHAIN_BROKEN"

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


def verify_chain(rows: list[dict[str, Any]]) -> None:
    """Verify an ordered list of audit_logs rows forms a valid chain.

    Each row must carry ``previous_hash`` equal to the preceding row's
    ``chain_hash`` (the genesis hash for the first row) and a ``chain_hash``
    that recomputes from the chain formula.  Raises :class:`AuditChainError`
    on the first violation.
    """
    expected = GENESIS_HASH
    for index, row in enumerate(rows):
        previous_hash = row["previous_hash"]
        chain_hash_value = row["chain_hash"]
        if previous_hash != expected:
            raise AuditChainError(
                f"row {index}: previous_hash {previous_hash!r} does not match expected {expected!r}"
            )
        timestamp = row["timestamp"]
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        recomputed = chain_hash(
            previous_hash,
            timestamp,
            row["tenant_id"],
            row.get("actor_id"),
            row["actor_type"],
            row["payload"],
        )
        if recomputed != chain_hash_value:
            raise AuditChainError(
                f"row {index}: chain_hash {chain_hash_value!r} does not match recomputed {recomputed!r}"
            )
        expected = chain_hash_value
