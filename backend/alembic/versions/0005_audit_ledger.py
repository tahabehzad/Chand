"""P0-T10: append-only, hash-chained audit ledger and the access log.

Authority
---------
``AGENTS.md`` §2 Security invariant 14 (the ledger is append-only; the
database rejects ``UPDATE``/``DELETE``); ``docs/specs/AUTH.md`` §7.2 (the
hash chain and the separate non-chained access log); ``docs/PISH_HESABDARI_HOLY_BIBLE.md``
§7.2 and §2181 (``H_n = SHA256(H_{n-1} ‖ ISO8601_timestamp ‖ tenant_id ‖ actor_id ‖ actor_type ‖ canonical_JSON(payload))``);
CR-10 / CR-11 (chain verifies end-to-end; ``UPDATE``/``DELETE`` rejected); DEC-004b.

What this migration does
------------------------
1. Creates ``audit_logs``: the hash-chained, append-only ledger.  Every row
   carries ``tenant_id``, an ``actor_id``/``actor_type``, an ``event_type``,
   an ISO-8601 timestamp, a canonical-JSON ``payload`` (blind indexes and
   encrypted values only -- never plaintext PII), the previous chain hash and
   the row's own chain hash, plus a monotonic ``sequence_id``.
2. Creates ``access_log``: a separate, non-chained, append-only table for
   high-frequency read events, with the same tenant scoping and append-only
   guard.
3. On every table: enables and **forces** row-level security and attaches one
   policy whose predicate is ``tenant_id = current_tenant_id()`` (fail closed,
   invariant 12).
4. Installs append-only triggers on both tables: ``UPDATE`` and ``DELETE``
   are refused by the database (invariant 14 / CR-11).

What this migration deliberately does not do
-------------------------------------------
* No seed data, no actor, no event.  The application writer service
  (``app.services.audit_service``) computes chain hashes in the application
  layer -- SHA-256 is never pushed into the database (invariant 13: no
  ``pgcrypto``).
* No new role: the connection role remains the deployment's (P0-T18).
* No 1405 activation and no statutory value.
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | None = None
depends_on: str | None = None

_AUDIT_LOG_COLUMNS = [
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column("tenant_id", sa.Uuid(), nullable=False),
    sa.Column("actor_id", sa.Uuid(), nullable=True),
    sa.Column("actor_type", sa.String(length=16), nullable=False),
    sa.Column("event_type", sa.String(length=40), nullable=False),
    sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.Column("payload", JSONB(), nullable=False),
    sa.Column("previous_hash", sa.String(length=64), nullable=False),
    sa.Column("chain_hash", sa.String(length=64), nullable=False),
    sa.Column("sequence_id", sa.BigInteger(), nullable=False),
    sa.CheckConstraint("actor_type IN ('USER','SYSTEM')", name="ck_audit_logs_actor_type"),
]

_ACCESS_LOG_COLUMNS = [
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column("tenant_id", sa.Uuid(), nullable=False),
    sa.Column("actor_id", sa.Uuid(), nullable=True),
    sa.Column("actor_type", sa.String(length=16), nullable=True),
    sa.Column("event_type", sa.String(length=40), nullable=False),
    sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.Column("payload", JSONB(), nullable=False),
    sa.CheckConstraint(
        "actor_type IS NULL OR actor_type IN ('USER','SYSTEM')",
        name="ck_access_logs_actor_type",
    ),
]


def _tenant_policy(table: str) -> str:
    return f"""
CREATE POLICY p_{table}_tenant_isolation ON {table}
    USING (tenant_id = current_tenant_id())
    WITH CHECK (tenant_id = current_tenant_id())
"""


def _append_only_function(table: str) -> str:
    return f"""
CREATE FUNCTION pish_reject_{table}_mutation() RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION '{table} is append-only; UPDATE and DELETE are refused'
        USING ERRCODE = '55006';
END;
$$
"""


def _append_only_trigger(table: str) -> str:
    return f"""
CREATE TRIGGER trg_{table}_append_only
    BEFORE UPDATE OR DELETE ON {table}
    FOR EACH ROW EXECUTE FUNCTION pish_reject_{table}_mutation()
"""


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        *_AUDIT_LOG_COLUMNS,
        sa.PrimaryKeyConstraint("id", name="pk_audit_logs"),
    )
    op.create_index("ix_audit_logs_tenant_sequence", "audit_logs", ["tenant_id", "sequence_id"])
    op.create_index("ix_audit_logs_tenant_time", "audit_logs", ["tenant_id", "timestamp"])

    op.create_table(
        "access_log",
        *_ACCESS_LOG_COLUMNS,
        sa.PrimaryKeyConstraint("id", name="pk_access_log"),
    )
    op.create_index("ix_access_logs_tenant_time", "access_log", ["tenant_id", "timestamp"])

    # --- tenant isolation (invariant 12): enable, force, one policy each ----
    for table in ("audit_logs", "access_log"):
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(_tenant_policy(table))

    # --- append-only guard (invariant 14 / CR-11) --------------------------
    for table in ("audit_logs", "access_log"):
        op.execute(_append_only_function(table))
        op.execute(_append_only_trigger(table))


def downgrade() -> None:
    for table in ("access_log", "audit_logs"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_append_only ON {table}")
        op.execute(f"DROP FUNCTION IF EXISTS pish_reject_{table}_mutation()")
        op.execute(f"DROP POLICY IF EXISTS p_{table}_tenant_isolation ON {table}")
        op.drop_table(table)


__all__ = ["down_revision", "downgrade", "revision", "upgrade"]
