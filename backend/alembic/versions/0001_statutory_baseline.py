"""Global FORCE-RLS statutory baseline, owner-approved ADR-007 / P0-T04.

Requires separately provisioned NOLOGIN roles. No role membership, legal seed
or production evidence is created. P0-T05 owns user FKs and removal of the
temporary write gate. This unapplied draft is adopted with its original ID.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None

_STATUSES = "'DRAFT', 'UNDER_REVIEW', 'VERIFIED', 'ACTIVE', 'RETIRED', 'REJECTED'"
_RETRIEVAL_LEVELS = "'L1', 'L2', 'L3', 'L4'"

_APPEND_ONLY_FUNCTION = """\
CREATE FUNCTION trg_statutory_parameter_signatures_append_only()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = pg_catalog
AS $$
BEGIN
    RAISE EXCEPTION
        'statutory_parameter_signatures rows are append-only (SPEC-STAT-001 4.1)';
    RETURN NULL;
END;
$$;"""

_APPEND_ONLY_TRIGGER = """\
CREATE TRIGGER statutory_parameter_signatures_append_only
BEFORE UPDATE OR DELETE OR TRUNCATE ON statutory_parameter_signatures
FOR EACH STATEMENT EXECUTE FUNCTION trg_statutory_parameter_signatures_append_only();"""


TABLES = (
    "statutory_rule_set_versions",
    "statutory_source_artefacts",
    "statutory_parameter_signatures",
    "statutory_rule_changes",
    "statutory_verification_log",
)
SAFE_COLUMNS = (
    "id, rule_year_shamsi, revision, effective_from, effective_to, supersedes_id, "
    "status, is_active, parameter_snapshot, created_at"
)


def upgrade() -> None:
    # Roles are cluster-scoped; provisioning is an explicit administrator step.
    op.execute("""DO $$ BEGIN
        IF (SELECT count(*) FROM pg_roles WHERE rolname IN
            ('pish_statutory_reader', 'pish_statutory_reviewer')
            AND NOT rolcanlogin AND NOT rolsuper AND NOT rolbypassrls
            AND NOT rolcreaterole AND NOT rolcreatedb AND NOT rolreplication) <> 2
        THEN RAISE EXCEPTION 'Provision safe statutory NOLOGIN roles before migration';
        END IF;
        IF EXISTS (SELECT 1 FROM pg_auth_members m JOIN pg_roles r ON r.oid=m.member
            WHERE r.rolname IN ('pish_statutory_reader','pish_statutory_reviewer'))
        THEN RAISE EXCEPTION 'Statutory roles must not inherit other roles'; END IF;
    END $$""")
    op.create_table(
        "statutory_rule_set_versions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("rule_year_shamsi", sa.Integer(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("supersedes_id", sa.Uuid(), nullable=True),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("source_manifest", postgresql.JSONB(), nullable=False),
        sa.Column("parameter_snapshot", postgresql.JSONB(), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verified_by", sa.Uuid(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            f"status IN ({_STATUSES})",
            name="ck_statutory_rule_set_versions_status",
        ),
        sa.ForeignKeyConstraint(
            ["supersedes_id"],
            ["statutory_rule_set_versions.id"],
            name="fk_statutory_rule_set_versions_supersedes_id",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "rule_year_shamsi",
            "revision",
            name="uq_statutory_rule_set_versions_year_revision",
        ),
    )
    op.create_table(
        "statutory_source_artefacts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("rule_year_shamsi", sa.Integer(), nullable=False),
        sa.Column("source_code", sa.String(length=16), nullable=False),
        sa.Column("issuing_authority", sa.String(length=200), nullable=False),
        sa.Column("document_title", sa.String(length=300), nullable=False),
        sa.Column("reference_number", sa.String(length=120), nullable=True),
        sa.Column("reference_date_sh", sa.String(length=20), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("retrieval_level", sa.String(length=2), nullable=False),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sha256", sa.CHAR(length=64), nullable=False),
        sa.Column("s3_object_key", sa.Text(), nullable=False),
        sa.Column("archived_by", sa.Uuid(), nullable=False),
        sa.CheckConstraint(
            f"retrieval_level IN ({_RETRIEVAL_LEVELS})",
            name="ck_statutory_source_artefacts_retrieval_level",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "statutory_parameter_signatures",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("rule_set_version_id", sa.Uuid(), nullable=False),
        sa.Column("parameter_key", sa.String(length=120), nullable=False),
        sa.Column("parameter_value", sa.Numeric(24, 4), nullable=False),
        sa.Column("derivation_note", sa.Text(), nullable=True),
        sa.Column("source_artefact_id", sa.Uuid(), nullable=False),
        # Roster roles per SPEC-STAT-001 §4.2/§4.3: TRANSCRIBER, VERIFIER,
        # CERTIFIED_ACCOUNTANT, LABOR_COUNSEL. Unconstrained by design
        # (contract §2.3 value-list rule).
        sa.Column("verifier_role", sa.String(length=40), nullable=False),
        sa.Column("verifier_id", sa.Uuid(), nullable=False),
        sa.Column("signature_sha256", sa.CHAR(length=64), nullable=False),
        sa.Column("signed_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["rule_set_version_id"],
            ["statutory_rule_set_versions.id"],
            name="fk_statutory_parameter_signatures_rule_set_version_id",
        ),
        sa.ForeignKeyConstraint(
            ["source_artefact_id"],
            ["statutory_source_artefacts.id"],
            name="fk_statutory_parameter_signatures_source_artefact_id",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "rule_set_version_id",
            "parameter_key",
            "verifier_role",
            name="uq_statutory_parameter_signatures_version_param_role",
        ),
    )
    op.create_table(
        "statutory_rule_changes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("rule_set_version_id", sa.Uuid(), nullable=False),
        sa.Column("parameter_key", sa.String(length=120), nullable=False),
        sa.Column("old_value", sa.Numeric(24, 4), nullable=True),
        sa.Column("new_value", sa.Numeric(24, 4), nullable=True),
        sa.Column("legal_citation", sa.Text(), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("change_reason", sa.Text(), nullable=False),
        sa.Column("requested_by", sa.Uuid(), nullable=False),
        sa.Column("approved_by", sa.Uuid(), nullable=False),
        sa.Column(
            "affected_simulation_count", sa.Integer(), nullable=False, server_default=sa.text("0")
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["rule_set_version_id"],
            ["statutory_rule_set_versions.id"],
            name="fk_statutory_rule_changes_rule_set_version_id",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "statutory_verification_log",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("rule_year_shamsi", sa.Integer(), nullable=False),
        sa.Column("parameter_key", sa.String(length=120), nullable=False),
        sa.Column("proposed_value", sa.Numeric(24, 4), nullable=False),
        sa.Column("proposed_source", sa.Text(), nullable=False),
        sa.Column("transcription_level", sa.String(length=2), nullable=False),
        sa.Column("transcriber_id", sa.Uuid(), nullable=False),
        sa.Column("transcribed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("verifier_id", sa.Uuid(), nullable=False),
        # Outcomes per SPEC-STAT-001 §10: AGREE, DISAGREE, CANNOT_VERIFY.
        sa.Column("verifier_role", sa.String(length=40), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("outcome", sa.String(length=16), nullable=False),
        sa.Column("discrepancy_note", sa.Text(), nullable=True),
        sa.Column("artefact_sha256", sa.CHAR(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute(_APPEND_ONLY_FUNCTION)
    op.execute(_APPEND_ONLY_TRIGGER)
    op.execute("""CREATE FUNCTION statutory_identity_write_gate() RETURNS trigger
        LANGUAGE plpgsql SET search_path = pg_catalog AS $$ BEGIN
        RAISE EXCEPTION 'Statutory writes require P0-T05 identity FK enforcement'
            USING ERRCODE = '55000';
        END $$""")
    for table in TABLES:
        # Identifiers below are fixed migration constants, never request input.
        op.execute(
            f"REVOKE ALL ON {table} FROM PUBLIC, pish_statutory_reader, pish_statutory_reviewer"
        )
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY statutory_platform_review ON {table} FOR SELECT "
            "TO pish_statutory_reviewer "
            "USING (current_user = 'pish_statutory_reviewer')"
        )
        op.execute(f"GRANT SELECT ON {table} TO pish_statutory_reviewer")
        op.execute(
            f"CREATE TRIGGER statutory_identity_write_gate "
            f"BEFORE INSERT OR UPDATE OR DELETE OR TRUNCATE ON {table} "
            "FOR EACH STATEMENT EXECUTE FUNCTION statutory_identity_write_gate()"
        )
    op.execute(
        "CREATE POLICY statutory_active_reader ON statutory_rule_set_versions "
        "FOR SELECT TO pish_statutory_reader USING "
        "(current_user = 'pish_statutory_reader' AND status = 'ACTIVE' AND is_active)"
    )
    op.execute(
        f"GRANT SELECT ({SAFE_COLUMNS}) ON statutory_rule_set_versions TO pish_statutory_reader"
    )
    op.execute(
        f"CREATE VIEW statutory_published_rules WITH "
        "(security_invoker=true, security_barrier=true) AS SELECT "
        f"{SAFE_COLUMNS} FROM statutory_rule_set_versions "
        "WHERE status = 'ACTIVE' AND is_active"
    )
    op.execute(
        "REVOKE ALL ON statutory_published_rules FROM PUBLIC, pish_statutory_reader, pish_statutory_reviewer"
    )
    op.execute("GRANT SELECT ON statutory_published_rules TO pish_statutory_reader")


def downgrade() -> None:
    op.execute("DROP VIEW statutory_published_rules")
    for table in TABLES:
        op.execute(f"DROP TRIGGER statutory_identity_write_gate ON {table}")
    op.execute("DROP FUNCTION statutory_identity_write_gate()")
    op.execute(
        "DROP TRIGGER IF EXISTS statutory_parameter_signatures_append_only "
        "ON statutory_parameter_signatures"
    )
    op.execute("DROP FUNCTION IF EXISTS trg_statutory_parameter_signatures_append_only()")
    op.drop_table("statutory_verification_log")
    op.drop_table("statutory_rule_changes")
    op.drop_table("statutory_parameter_signatures")
    op.drop_table("statutory_source_artefacts")
    op.drop_table("statutory_rule_set_versions")
