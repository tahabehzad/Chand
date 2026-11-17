"""Encrypted work profiles, local documents and immutable calculation history.

Authority: ADR-012; WORK_PROFILE_PAYROLL; AGENTS §2 tenant/crypto invariants.
Related: P3-T07 integration; P2-T02 local upload slice.
Scope: additive schema only; no legacy row/seed rewrite or production migration.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | None = None
depends_on: str | None = None

TABLES = ("employee_work_profiles", "employee_work_documents", "employee_work_calculations")


def upgrade() -> None:
    op.create_unique_constraint("uq_employee_tenant_identity", "employees", ["id", "tenant_id"])
    for table in TABLES:
        extra: list[sa.Column[object]] = []
        if table == "employee_work_profiles":
            extra.append(sa.Column("revision", sa.Integer(), nullable=False))
            extra.append(sa.Column("updated_at", sa.DateTime(timezone=True),
                                   server_default=sa.func.now(), nullable=False))
        else:
            extra.append(sa.Column("created_at", sa.DateTime(timezone=True),
                                   server_default=sa.func.now(), nullable=False))
        if table == "employee_work_documents":
            extra.append(sa.Column("metadata_ciphertext", sa.LargeBinary(), nullable=False))
        if table == "employee_work_calculations":
            extra.append(sa.Column("calculation_hash", sa.String(64), nullable=False))
        op.create_table(
            table,
            sa.Column("id", sa.Uuid(), primary_key=True),
            sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("organizations.id"), nullable=False),
            sa.Column("employee_id", sa.Uuid(), nullable=False),
            sa.Column("ciphertext", sa.LargeBinary(), nullable=False),
            sa.Column("key_id", sa.String(40), nullable=False),
            sa.Column("actor_id", sa.Uuid(), nullable=False),
            *extra,
            sa.ForeignKeyConstraint(["employee_id", "tenant_id"], ["employees.id", "employees.tenant_id"]),
        )
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY p_{table}_tenant ON {table} "
            "USING (tenant_id = current_tenant_id()) "
            "WITH CHECK (tenant_id = current_tenant_id())"
        )
    op.create_index("uq_work_profile_employee", TABLES[0], ["tenant_id", "employee_id"], unique=True)
    op.create_index("ix_work_document_employee", TABLES[1], ["tenant_id", "employee_id"])
    op.create_index("ix_work_calculation_employee", TABLES[2], ["tenant_id", "employee_id"])
    op.execute("""
        CREATE FUNCTION pish_reject_work_snapshot_mutation() RETURNS trigger
        LANGUAGE plpgsql AS $$ BEGIN
            RAISE EXCEPTION 'Work calculation snapshots are append-only' USING ERRCODE='55006';
        END; $$
    """)
    op.execute("""
        CREATE TRIGGER trg_work_snapshot_immutable
        BEFORE UPDATE OR DELETE ON employee_work_calculations
        FOR EACH ROW EXECUTE FUNCTION pish_reject_work_snapshot_mutation()
    """)


def downgrade() -> None:
    for table in reversed(TABLES):
        op.drop_table(table)
    op.execute("DROP FUNCTION pish_reject_work_snapshot_mutation()")
    op.drop_constraint("uq_employee_tenant_identity", "employees", type_="unique")
