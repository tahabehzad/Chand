"""Tenant context functions and the tenant-RLS invariant gate (P0-T09).

Authority
---------
``AGENTS.md`` §2 Security invariant 12; ``docs/specs/AUTH.md`` §6 multi-tenant
isolation (ISO-03, ISO-06, ISO-07); Holy Bible §5.5 and §5.9; ADR-007 (the
statutory tables are global and keep their own platform policies).

What this migration does
------------------------
1. Creates ``set_tenant_context(uuid)``: a transaction-local binding of the
   ``app.tenant_id`` GUC.  ``is_local = true`` means the binding ends at
   commit or rollback, so nothing can leak through a pooled connection.
2. Creates ``current_tenant_id()``: the fail-closed reader.  An unbound
   session raises SQLSTATE ``55000`` instead of returning ``NULL``, so a
   tenant policy that calls it can never degrade into "no rows" silence.
3. Installs ``pish_tenant_rls_violation()``, the catalogue assertion that a
   table carrying ``tenant_id`` also has row-level security enabled, forced
   and at least one policy.  It is invoked by the migration lint test and by
   the deployment check; it changes no schema.

What this migration deliberately does not do
--------------------------------------------
* No tenant table is created and no policy is attached: the platform has no
  tenant-owned data table yet.  The identity tables of ``0002`` are the
  tenancy model itself, and the statutory tables are global under ADR-007.
  Each future tenant table adds its ``tenant_id``, policy and
  ``FORCE ROW LEVEL SECURITY`` in its own migration (invariant 12).
* No role is provisioned.  The functions are ``SECURITY INVOKER`` and touch
  only the session GUC, so they cross no privilege boundary; the runtime
  application role remains P0-T18's deliverable.
* No data, no statutory value and no 1405 activation.
"""

from __future__ import annotations

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | None = None
depends_on: str | None = None

_SET_TENANT_CONTEXT = """
CREATE FUNCTION set_tenant_context(p_tenant_id uuid) RETURNS void
LANGUAGE plpgsql
SET search_path = pg_catalog
AS $$
BEGIN
    IF p_tenant_id IS NULL THEN
        RAISE EXCEPTION 'Tenant context requires an organisation identifier'
            USING ERRCODE = '22004';
    END IF;
    PERFORM set_config('app.tenant_id', p_tenant_id::text, true);
END;
$$
"""

_CURRENT_TENANT_ID = """
CREATE FUNCTION current_tenant_id() RETURNS uuid
LANGUAGE plpgsql
STABLE
SET search_path = pg_catalog
AS $$
DECLARE
    bound_value text;
BEGIN
    bound_value := current_setting('app.tenant_id', true);
    IF bound_value IS NULL OR bound_value = '' THEN
        RAISE EXCEPTION
            'Tenant context is not set; refusing to read tenant data'
            USING ERRCODE = '55000';
    END IF;
    RETURN bound_value::uuid;
END;
$$
"""

#: Catalogue assertion: every table with a ``tenant_id`` column must have RLS
#: enabled, forced, and at least one policy.  Returns the offending tables
#: instead of raising so that a verification query can report all of them at
#: once; ``tests/integration`` asserts that the result is empty.
_TENANT_RLS_VIOLATION = """
CREATE FUNCTION pish_tenant_rls_violation() RETURNS TABLE (table_name text)
LANGUAGE sql
STABLE
SET search_path = pg_catalog
AS $$
    SELECT c.relname::text
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    JOIN pg_attribute a ON a.attrelid = c.oid
    WHERE c.relkind = 'r'
      AND n.nspname = 'public'
      AND a.attname = 'tenant_id'
      AND a.attnum > 0
      AND NOT a.attisdropped
      AND (
          NOT c.relrowsecurity
          OR NOT c.relforcerowsecurity
          OR NOT EXISTS (SELECT 1 FROM pg_policy p WHERE p.polrelid = c.oid)
      )
    ORDER BY c.relname
$$
"""

_FUNCTIONS = ("set_tenant_context(uuid)", "current_tenant_id()")


def upgrade() -> None:
    op.execute(_SET_TENANT_CONTEXT)
    op.execute(_CURRENT_TENANT_ID)
    op.execute(_TENANT_RLS_VIOLATION)
    # The helpers carry no privilege: they read and write only the session
    # GUC, and any role may set a custom GUC.  Executing them is therefore
    # granted to PUBLIC explicitly, matching that absence of a boundary.
    for signature in _FUNCTIONS:
        op.execute(f"GRANT EXECUTE ON FUNCTION {signature} TO PUBLIC")


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS pish_tenant_rls_violation()")
    for signature in _FUNCTIONS:
        op.execute(f"DROP FUNCTION IF EXISTS {signature}")
