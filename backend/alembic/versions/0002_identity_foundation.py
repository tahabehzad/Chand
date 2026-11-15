"""Tenant identity foundation and statutory actor binding (P0-T05).

Authority
---------
``docs/specs/AUTH.md`` (SPEC-AUTH-001) §2 entity model and §3 role set;
ADR-006 (the seven-role set is the accepted DEC-004 choice); ADR-007
(T-2/F-1: the deferred ``users(id)`` actor foreign keys, ``ON DELETE
RESTRICT``, account deactivation instead of deletion, and the replacement of
the temporary P0-T04 write gate); ``docs/PISH_HESABDARI_HOLY_BIBLE.md`` §5.3,
§5.5 and §5.9.

What this migration does
------------------------
1. Creates the seven identity tables with the constraints of SPEC-AUTH-001 §2.
2. Seeds **exactly seven** roles (ADR-006) with deterministic identifiers so
   the seed is idempotent.
3. Validates every existing statutory actor reference and refuses to continue
   when one is orphaned.
4. Installs the deferred ``users(id)`` foreign keys on all seven statutory
   actor columns with ``ON DELETE RESTRICT``.
5. Replaces the temporary P0-T04 write gate with the permanent retention
   guard.

What this migration deliberately does not do
--------------------------------------------
* No permission matrix is seeded.  The role/permission matrix of
  SPEC-AUTH-001 §3 is still ``[PROPOSED]``; only the role set was approved.
  ``permissions`` and ``role_permissions`` exist and stay empty until that
  matrix is approved.
* ``organizations.key_store_id`` carries no foreign key: its target,
  ``tenant_key_stores``, is the P0-T08 deliverable.  P0-T08 adds the key.
* No RLS policy and no tenant context: those are P0-T09.  The identity
  tables are the tenancy model itself, not tenant data tables.
* No legal seed, statutory value, 1405 activation or production evidence.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | None = None
depends_on: str | None = None

#: Deterministic namespace for the seeded role identifiers.  The identifiers
#: are derived from the role key alone, so re-running the seed can never
#: create a second row for the same role.
_ROLE_NAMESPACE: uuid.UUID = uuid.NAMESPACE_OID
_ROLE_NAME_PREFIX: str = "pish-hesabdari:roles:"

#: The seven roles accepted by ADR-006 (SPEC-AUTH-001 §3, P3).
_ROLE_SEED: tuple[tuple[str, str, str], ...] = (
    (
        "OWNER",
        "مالک سازمان",
        "مسئول نهایی سازمان؛ تنها نقشی که می‌تواند نقش‌های سازمانی را تخصیص دهد.",
    ),
    (
        "ADMIN",
        "مدیر سازمان",
        "مدیر عملیاتی سازمان؛ مدیریت اعضا بدون تخصیص نقش.",
    ),
    (
        "HR_MANAGER",
        "مدیر منابع انسانی",
        "مدیر جذب و ارزیابی داوطلبان؛ پرکاربردترین نقش و در معرض ریسک افشا.",
    ),
    (
        "LEGAL_REVIEWER",
        "بازبین حقوقی",
        "بازبین مستندات و اسناد حقوقی؛ تنها نقش کارشناسی که می‌تواند وضعیت تأیید سند را ارتقا دهد.",
    ),
    (
        "ANALYST",
        "تحلیل‌گر",
        "تحلیل‌گر حقوق و دستمزد؛ دسترسی خواندن به داده‌های کارفرما.",
    ),
    (
        "AUDITOR",
        "حسابرس",
        "حسابرس داخلی؛ دسترسی خواندن به گزارش‌ها و رد ممیزی.",
    ),
    (
        "SUPER_ADMIN",
        "مدیر ارشد پلتفرم",
        "مدیریت پلتفرم؛ اعطای آن خارج از سامانه و به‌صورت رویه شکست اضطراری انجام می‌شود.",
    ),
)

#: Statutory actor columns and the foreign key installed on each of them.
#: ADR-007 lists exactly these seven columns.
_STATUTORY_ACTOR_FOREIGN_KEYS: tuple[tuple[str, str, str], ...] = (
    (
        "statutory_rule_set_versions",
        "verified_by",
        "fk_statutory_rule_set_versions_verified_by",
    ),
    (
        "statutory_source_artefacts",
        "archived_by",
        "fk_statutory_source_artefacts_archived_by",
    ),
    (
        "statutory_parameter_signatures",
        "verifier_id",
        "fk_statutory_parameter_signatures_verifier_id",
    ),
    (
        "statutory_rule_changes",
        "requested_by",
        "fk_statutory_rule_changes_requested_by",
    ),
    (
        "statutory_rule_changes",
        "approved_by",
        "fk_statutory_rule_changes_approved_by",
    ),
    (
        "statutory_verification_log",
        "transcriber_id",
        "fk_statutory_verification_log_transcriber_id",
    ),
    (
        "statutory_verification_log",
        "verifier_id",
        "fk_statutory_verification_log_verifier_id",
    ),
)

#: Tables whose evidence may never be destroyed, and the write operations the
#: retention guard refuses on each of them.
#:
#: ``DELETE`` and ``TRUNCATE`` are refused everywhere: retained legal evidence
#: is never destroyed (Holy Bible §5.9 "Retain", ingestion §2.2 item 4).
#: ``UPDATE`` is additionally refused where the specification is unambiguous —
#: a source artefact row is never mutated (ingestion §2.2 item 4) and a
#: verification log entry is a log record (Holy Bible §5.7).  It is *not*
#: refused on ``statutory_rule_set_versions`` (the documented status lifecycle,
#: ingestion §5.3) or on ``statutory_rule_changes`` (``affected_simulation_count``
#: is computed at approval time, ingestion §5.5); those two remain subject to
#: the RLS default-deny until P0-T09 defines the write policies explicitly.
_RETENTION_GUARD_EVENTS: tuple[tuple[str, str], ...] = (
    ("statutory_rule_set_versions", "DELETE OR TRUNCATE"),
    ("statutory_source_artefacts", "UPDATE OR DELETE OR TRUNCATE"),
    ("statutory_rule_changes", "DELETE OR TRUNCATE"),
    ("statutory_verification_log", "UPDATE OR DELETE OR TRUNCATE"),
)

#: ``statutory_parameter_signatures`` keeps its own append-only trigger from
#: P0-T04 (``statutory_parameter_signatures_append_only``), so the retention
#: guard is not installed there: one control per table, no ordering ambiguity.

_RETENTION_GUARD_FUNCTION = """\
CREATE FUNCTION statutory_retention_guard() RETURNS trigger
LANGUAGE plpgsql
SET search_path = pg_catalog
AS $$
DECLARE
    operation text;
BEGIN
    operation := CASE TG_OP
        WHEN 'UPDATE' THEN 'updated'
        WHEN 'DELETE' THEN 'deleted'
        WHEN 'TRUNCATE' THEN 'truncated'
        ELSE lower(TG_OP)
    END;
    RAISE EXCEPTION
        'Statutory evidence in % is retained and must not be % (Holy Bible 5.9; SPEC-STAT-001)',
        TG_TABLE_NAME, operation
        USING ERRCODE = '55000';
    RETURN NULL;
END;
$$;"""

#: The temporary P0-T04 gate.  It exists only while the statutory actor
#: foreign keys are missing; it is recreated by the downgrade so that a
#: rollback returns the schema to the exact P0-T04 state.
_IDENTITY_WRITE_GATE_FUNCTION = """\
CREATE FUNCTION statutory_identity_write_gate() RETURNS trigger
    LANGUAGE plpgsql SET search_path = pg_catalog AS $$ BEGIN
        RAISE EXCEPTION 'Statutory writes require P0-T05 identity FK enforcement'
            USING ERRCODE = '55000';
    END $$"""

#: Tables covered by the temporary write gate.
_GATED_TABLES: tuple[str, ...] = (
    "statutory_rule_set_versions",
    "statutory_source_artefacts",
    "statutory_parameter_signatures",
    "statutory_rule_changes",
    "statutory_verification_log",
)


def _role_identifier(role_key: str) -> uuid.UUID:
    """Return the deterministic identifier of a seeded role."""
    return uuid.uuid5(_ROLE_NAMESPACE, f"{_ROLE_NAME_PREFIX}{role_key}")


def _create_identity_tables() -> None:
    """Create the seven identity tables of SPEC-AUTH-001 §2."""
    op.create_table(
        "organizations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("legal_name_fa", sa.String(length=200), nullable=False),
        sa.Column("national_company_id", sa.String(length=11), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        # The foreign key to tenant_key_stores(id) is P0-T08's deliverable.
        sa.Column("key_store_id", sa.Uuid(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "national_company_id IS NULL OR national_company_id ~ '^[0-9]{11}$'",
            name="ck_organizations_national_company_id",
        ),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        # A login identifier, never a blind index (Holy Bible §5.5).
        sa.Column("email_normalized", sa.String(length=320), nullable=False),
        sa.Column("display_name_fa", sa.String(length=200), nullable=False),
        sa.Column("password_hash", sa.LargeBinary(), nullable=True),
        sa.Column("password_params", postgresql.JSONB(), nullable=True),
        sa.Column("totp_secret_enc", sa.LargeBinary(), nullable=True),
        sa.Column("totp_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "is_platform_admin", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("failed_attempts", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "must_change_password", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email_normalized", name="uq_users_email_normalized"),
    )
    op.create_table(
        "roles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("role_key", sa.String(length=32), nullable=False),
        sa.Column("display_name_fa", sa.String(length=100), nullable=False),
        sa.Column("description_fa", sa.Text(), nullable=True),
        sa.Column("is_system_role", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("role_key", name="uq_roles_role_key"),
    )
    op.create_table(
        "permissions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("permission_key", sa.String(length=120), nullable=False),
        sa.Column("resource", sa.String(length=60), nullable=False),
        sa.Column("action", sa.String(length=40), nullable=False),
        sa.Column("description_fa", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("permission_key", name="uq_permissions_permission_key"),
    )
    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.Uuid(), nullable=False),
        sa.Column("permission_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["role_id"], ["roles.id"], name="fk_role_permissions_role_id", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["permission_id"],
            ["permissions.id"],
            name="fk_role_permissions_permission_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("role_id", "permission_id"),
    )
    op.create_table(
        "organization_memberships",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("role_id", sa.Uuid(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("invited_by", sa.Uuid(), nullable=True),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name="fk_organization_memberships_organization_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_organization_memberships_user_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["role_id"], ["roles.id"], name="fk_organization_memberships_role_id"
        ),
        sa.ForeignKeyConstraint(
            ["invited_by"], ["users.id"], name="fk_organization_memberships_invited_by"
        ),
        sa.UniqueConstraint(
            "organization_id", "user_id", name="uq_organization_memberships_organization_user"
        ),
    )
    op.create_index(
        "ix_organization_memberships_user_id_active",
        "organization_memberships",
        ["user_id"],
        postgresql_where=sa.text("is_active"),
    )
    op.create_table(
        "sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=True),
        sa.Column("token_hash", sa.CHAR(length=64), nullable=False),
        sa.Column("refresh_token_hash", sa.CHAR(length=64), nullable=True),
        sa.Column("ip_address", postgresql.INET(), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("mfa_satisfied", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "issued_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "last_seen_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("absolute_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("idle_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_reason", sa.String(length=120), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_sessions_user_id", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"], ["organizations.id"], name="fk_sessions_organization_id"
        ),
        sa.UniqueConstraint("token_hash", name="uq_sessions_token_hash"),
        sa.UniqueConstraint("refresh_token_hash", name="uq_sessions_refresh_token_hash"),
    )
    op.create_index(
        "ix_sessions_user_id_active",
        "sessions",
        ["user_id"],
        postgresql_where=sa.text("revoked_at IS NULL"),
    )


def _seed_roles() -> None:
    """Seed exactly the seven roles accepted by ADR-006."""
    roles = sa.Table(
        "roles",
        sa.MetaData(),
        sa.Column("id", sa.Uuid()),
        sa.Column("role_key", sa.String(length=32)),
        sa.Column("display_name_fa", sa.String(length=100)),
        sa.Column("description_fa", sa.Text()),
        sa.Column("is_system_role", sa.Boolean()),
    )
    for role_key, display_name_fa, description_fa in _ROLE_SEED:
        op.execute(
            postgresql.insert(roles)
            .values(
                id=_role_identifier(role_key),
                role_key=role_key,
                display_name_fa=display_name_fa,
                description_fa=description_fa,
                is_system_role=True,
            )
            .on_conflict_do_nothing(index_elements=["role_key"])
        )


def _validate_statutory_actor_references() -> None:
    """Refuse to continue when a statutory actor reference has no user.

    The foreign keys installed below would fail for the same reason; this
    explicit check names the cause instead of surfacing a driver error.
    """
    op.execute(
        """DO $$ BEGIN
    IF EXISTS (
        SELECT 1 FROM (
            SELECT verified_by AS actor FROM statutory_rule_set_versions WHERE verified_by IS NOT NULL
            UNION ALL SELECT archived_by FROM statutory_source_artefacts WHERE archived_by IS NOT NULL
            UNION ALL SELECT verifier_id FROM statutory_parameter_signatures WHERE verifier_id IS NOT NULL
            UNION ALL SELECT requested_by FROM statutory_rule_changes WHERE requested_by IS NOT NULL
            UNION ALL SELECT approved_by FROM statutory_rule_changes WHERE approved_by IS NOT NULL
            UNION ALL SELECT transcriber_id FROM statutory_verification_log WHERE transcriber_id IS NOT NULL
            UNION ALL SELECT verifier_id FROM statutory_verification_log WHERE verifier_id IS NOT NULL
        ) actors
        WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id = actors.actor)
    ) THEN
        RAISE EXCEPTION 'Statutory actor references do not exist in users; refusing to install the identity foreign keys';
    END IF;
END $$"""
    )


def _install_statutory_actor_foreign_keys() -> None:
    """Install the deferred ``users(id)`` actor foreign keys (ADR-007)."""
    for table, column, name in _STATUTORY_ACTOR_FOREIGN_KEYS:
        op.create_foreign_key(
            name,
            table,
            "users",
            [column],
            ["id"],
            ondelete="RESTRICT",
        )


def _replace_the_temporary_write_gate() -> None:
    """Replace the P0-T04 write gate with the permanent retention guard.

    The temporary gate refused every write until the actor foreign keys
    existed.  They exist now, so the gate is removed and the destructive
    operations that row-level security cannot police are refused by the
    retention guard instead.
    """
    for table in _GATED_TABLES:
        op.execute(f"DROP TRIGGER IF EXISTS statutory_identity_write_gate ON {table}")
    op.execute("DROP FUNCTION IF EXISTS statutory_identity_write_gate()")
    op.execute(_RETENTION_GUARD_FUNCTION)
    for table, events in _RETENTION_GUARD_EVENTS:
        op.execute(
            f"CREATE TRIGGER statutory_retention_guard BEFORE {events} ON {table} "
            "FOR EACH STATEMENT EXECUTE FUNCTION statutory_retention_guard()"
        )


def _restrict_identity_table_access() -> None:
    """Deny every role but the owner access to the identity tables.

    The statutory reader and reviewer roles stay scoped to statutory
    evidence: they must not be able to resolve the identity behind an actor
    identifier.  A runtime application role is provisioned by P0-T18.
    """
    for table in (
        "organizations",
        "users",
        "roles",
        "permissions",
        "role_permissions",
        "organization_memberships",
        "sessions",
    ):
        op.execute(f"REVOKE ALL ON {table} FROM PUBLIC")


def upgrade() -> None:
    _create_identity_tables()
    _seed_roles()
    _validate_statutory_actor_references()
    _install_statutory_actor_foreign_keys()
    _replace_the_temporary_write_gate()
    _restrict_identity_table_access()


def downgrade() -> None:
    # Restore the exact P0-T04 state: the temporary write gate returns.
    op.execute("DROP FUNCTION IF EXISTS statutory_retention_guard()")
    for table, _events in _RETENTION_GUARD_EVENTS:
        op.execute(f"DROP TRIGGER IF EXISTS statutory_retention_guard ON {table}")
    for table, column, name in _STATUTORY_ACTOR_FOREIGN_KEYS:
        op.execute(f"DROP CONSTRAINT IF EXISTS {name} ON {table}")
    op.execute(_IDENTITY_WRITE_GATE_FUNCTION)
    for table in _GATED_TABLES:
        op.execute(
            f"CREATE TRIGGER statutory_identity_write_gate "
            f"BEFORE INSERT OR UPDATE OR DELETE OR TRUNCATE ON {table} "
            "FOR EACH STATEMENT EXECUTE FUNCTION statutory_identity_write_gate()"
        )
    op.drop_index("ix_sessions_user_id_active", table_name="sessions")
    op.drop_table("sessions")
    op.drop_index(
        "ix_organization_memberships_user_id_active", table_name="organization_memberships"
    )
    op.drop_table("organization_memberships")
    op.drop_table("role_permissions")
    op.drop_table("permissions")
    op.drop_table("roles")
    op.drop_table("users")
    op.drop_table("organizations")
