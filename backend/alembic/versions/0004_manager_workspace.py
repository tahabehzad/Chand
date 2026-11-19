"""Manager workspace: tenant tables, RLS and the append-only decision ledger.

Authority
---------
``AGENTS.md`` §2 Security invariant 12 — every tenant table carries
``tenant_id``, an RLS policy and ``FORCE ROW LEVEL SECURITY`` **in the same
migration**; §2 Security invariant 14 — the decision ledger is append-only and
the database rejects ``UPDATE``/``DELETE``; ``docs/adr/ADR-009`` (the advisory
compensation workflow); ``docs/MVP_SCOPE.md`` AC-10.

Related
-------
``alembic/versions/0003_tenant_context.py`` (``current_tenant_id()``, the
fail-closed policy predicate); ``app/models/manager.py`` (the ORM mirror).

What this migration does
------------------------
1. Creates the six manager-workspace tables, each with ``tenant_id``.
2. On every table: enables and **forces** row-level security and attaches one
   policy whose predicate is ``tenant_id = current_tenant_id()`` — an unbound
   session therefore raises SQLSTATE ``55000`` instead of silently seeing
   nothing (fail closed, invariant 10/12).
3. Installs the append-only trigger on ``recommendation_decisions``: an
   ``UPDATE`` or ``DELETE`` is refused by the database.
4. Installs the same refusal on ``employee_observations`` and
   ``salary_recommendations`` **state transitions are updates by design**, so
   those tables stay mutable — only the decision ledger and the evidence
   integrity (content addressed by SHA-256) are immutable.

What this migration deliberately does not do
--------------------------------------------
* No seed data, no employee, no statutory value.
* No new role: the connection role remains the deployment's business
  (P0-T18).  The policies are already correct for a least-privilege role; the
  local development connection runs as the container superuser, which bypasses
  RLS by PostgreSQL design, so the application layer also filters by
  ``tenant_id`` on every query.
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | None = None
depends_on: str | None = None

_METRIC_CODES = ("sales", "quality", "attendance", "responsibility")


def _tenant_policy(table: str) -> str:
    """One per-tenant policy, applied to reads and writes alike."""
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
        "employees",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("role_label", sa.String(length=60), nullable=False),
        sa.Column("start_date", sa.String(length=10), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("start_date ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'", name="ck_employees_start_date_format"),
    )
    op.create_index("ix_employees_tenant_created", "employees", ["tenant_id", "created_at"])

    op.create_table(
        "employee_observations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("employee_id", sa.Uuid(), nullable=False),
        sa.Column("metric_code", sa.String(length=20), nullable=False),
        sa.Column("period", sa.String(length=40), nullable=False),
        sa.Column("raw_value", sa.String(length=24), nullable=False),
        sa.Column("state", sa.String(length=12), nullable=False),
        sa.Column("source", sa.String(length=12), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["employee_id"], ["employees.id"], name="fk_employee_observations_employee_id", ondelete="CASCADE"
        ),
        sa.CheckConstraint(
            "metric_code IN ('sales','quality','attendance','responsibility')",
            name="ck_employee_observations_metric_code",
        ),
        sa.CheckConstraint("state IN ('valid','corrected','rejected')", name="ck_employee_observations_state"),
        sa.CheckConstraint("source IN ('manual','import')", name="ck_employee_observations_source"),
        sa.CheckConstraint("raw_value ~ '^[0-9]{1,18}$'", name="ck_employee_observations_raw_digits"),
    )
    op.create_index(
        "ix_employee_observations_tenant_employee",
        "employee_observations",
        ["tenant_id", "employee_id"],
    )

    op.create_table(
        "employee_evidence",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("employee_id", sa.Uuid(), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=120), nullable=False),
        sa.Column("byte_size", sa.BigInteger(), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("content", sa.LargeBinary(), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["employee_id"], ["employees.id"], name="fk_employee_evidence_employee_id", ondelete="CASCADE"
        ),
    )
    op.create_index(
        "ix_employee_evidence_tenant_employee", "employee_evidence", ["tenant_id", "employee_id"]
    )

    op.create_table(
        "employee_evaluations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("employee_id", sa.Uuid(), nullable=False),
        sa.Column("rule_set_version", sa.String(length=20), nullable=False),
        sa.Column("rule_set_status", sa.String(length=20), nullable=False),
        sa.Column("score_100", sa.Integer(), nullable=False),
        sa.Column("total_bp", sa.Integer(), nullable=False),
        sa.Column("contributions", JSONB(), nullable=False),
        sa.Column("observations_used", JSONB(), nullable=False),
        sa.Column("missing_criteria", JSONB(), nullable=False),
        sa.Column("missing_policy_fa", sa.Text(), nullable=False),
        sa.Column("calculation_hash", sa.String(length=64), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["employee_id"], ["employees.id"], name="fk_employee_evaluations_employee_id", ondelete="CASCADE"
        ),
        sa.CheckConstraint("score_100 >= 0 AND score_100 <= 100", name="ck_employee_evaluations_score_range"),
    )
    op.create_index(
        "ix_employee_evaluations_tenant_employee", "employee_evaluations", ["tenant_id", "employee_id"]
    )

    op.create_table(
        "salary_recommendations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("employee_id", sa.Uuid(), nullable=False),
        sa.Column("evaluation_id", sa.Uuid(), nullable=False),
        sa.Column("period", sa.String(length=40), nullable=False),
        sa.Column("rule_set_version", sa.String(length=20), nullable=False),
        sa.Column("engine_version", sa.String(length=60), nullable=False),
        sa.Column("score_100", sa.Integer(), nullable=False),
        sa.Column("band_min_rial", sa.BigInteger(), nullable=False),
        sa.Column("band_max_rial", sa.BigInteger(), nullable=False),
        sa.Column("band_current_rial", sa.BigInteger(), nullable=True),
        sa.Column("band_position_bp", sa.Integer(), nullable=False),
        sa.Column("suggested_gross_rial", sa.BigInteger(), nullable=False),
        sa.Column("delta_rial", sa.BigInteger(), nullable=True),
        sa.Column("explanation", JSONB(), nullable=False),
        sa.Column("statutory_costing", JSONB(), nullable=False),
        sa.Column("current_costing", JSONB(), nullable=True),
        sa.Column("calculation_hash", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=12), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["employee_id"], ["employees.id"], name="fk_salary_recommendations_employee_id", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["evaluation_id"], ["employee_evaluations.id"], name="fk_salary_recommendations_evaluation_id"
        ),
        sa.CheckConstraint("status IN ('pending','decided')", name="ck_salary_recommendations_status"),
    )
    op.create_index(
        "ix_salary_recommendations_tenant_employee",
        "salary_recommendations",
        ["tenant_id", "employee_id"],
    )
    op.create_index(
        "ix_salary_recommendations_tenant_status", "salary_recommendations", ["tenant_id", "status"]
    )

    op.create_table(
        "recommendation_decisions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("recommendation_id", sa.Uuid(), nullable=False),
        sa.Column("action", sa.String(length=12), nullable=False),
        sa.Column("edited_gross_rial", sa.BigInteger(), nullable=True),
        sa.Column("comment", sa.String(length=500), nullable=False),
        sa.Column("decided_by", sa.Uuid(), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["recommendation_id"],
            ["salary_recommendations.id"],
            name="fk_recommendation_decisions_recommendation_id",
        ),
        sa.CheckConstraint("action IN ('approve','edit','reject')", name="ck_recommendation_decisions_action"),
        sa.UniqueConstraint("recommendation_id", name="uq_recommendation_decisions_one_per_recommendation"),
    )
    op.create_index(
        "ix_recommendation_decisions_tenant_decided",
        "recommendation_decisions",
        ["tenant_id", "decided_at"],
    )

    # --- tenant isolation (invariant 12): enable, force, one policy each ----
    for table in (
        "employees",
        "employee_observations",
        "employee_evidence",
        "employee_evaluations",
        "salary_recommendations",
        "recommendation_decisions",
    ):
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(_tenant_policy(table))

    # --- append-only decision ledger (invariant 14) ------------------------
    op.execute(_append_only_function("recommendation_decisions"))
    op.execute(_append_only_trigger("recommendation_decisions"))


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_recommendation_decisions_append_only ON recommendation_decisions")
    op.execute("DROP FUNCTION IF EXISTS pish_reject_recommendation_decisions_mutation()")
    for table in (
        "recommendation_decisions",
        "salary_recommendations",
        "employee_evaluations",
        "employee_evidence",
        "employee_observations",
        "employees",
    ):
        op.execute(f"DROP POLICY IF EXISTS p_{table}_tenant_isolation ON {table}")
        op.drop_table(table)


__all__ = ["revision", "down_revision", "upgrade", "downgrade", "_METRIC_CODES"]
