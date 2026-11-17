-- Deterministic schema fingerprint for the P0-T16 restore comparison.
--
-- Authority: docs/specs/DEPLOYMENT.md §5 (backup/restore baseline) and the
-- P0-T16 acceptance criterion "a backup completes and restores to a
-- schema-identical isolated instance".
--
-- The fingerprint covers every catalogue object a logical restore must
-- reproduce: tables, columns and their nullability/types, constraints,
-- indexes, RLS enablement and force flags, policies, non-internal triggers
-- and function bodies. Privileges are compared separately by the caller
-- because they depend on the roles present in each database.
WITH objects AS (
    SELECT 'table' AS kind, c.relname AS name, ''::text AS detail
    FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = 'public' AND c.relkind = 'r'
    UNION ALL
    SELECT 'column', c.relname || '.' || a.attname,
           format_type(a.atttypid, a.atttypmod) || ':' || a.attnotnull::text
    FROM pg_attribute a
    JOIN pg_class c ON c.oid = a.attrelid
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = 'public' AND c.relkind = 'r'
      AND a.attnum > 0 AND NOT a.attisdropped
    UNION ALL
    SELECT 'constraint', conrelid::regclass::text || ':' || conname,
           pg_get_constraintdef(oid, false)
    FROM pg_constraint
    WHERE connamespace = 'public'::regnamespace
    UNION ALL
    SELECT 'index', indexrelid::regclass::text, pg_get_indexdef(indexrelid)
    FROM pg_index i
    JOIN pg_class c ON c.oid = i.indrelid
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = 'public'
    UNION ALL
    SELECT 'policy', polrelid::regclass::text || ':' || polname,
           polcmd::text || '|' || coalesce(pg_get_expr(polqual, polrelid), '')
    FROM pg_policy
    UNION ALL
    SELECT 'trigger', tgrelid::regclass::text || ':' || tgname,
           pg_get_triggerdef(oid, false)
    FROM pg_trigger
    WHERE NOT tgisinternal
    UNION ALL
    SELECT 'function', p.proname, md5(pg_get_functiondef(p.oid))
    FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace
    WHERE n.nspname = 'public'
    UNION ALL
    SELECT 'rls', c.relname,
           c.relrowsecurity::text || '/' || c.relforcerowsecurity::text
    FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = 'public' AND c.relkind = 'r'
)
SELECT md5(string_agg(kind || '|' || name || '|' || detail, E'\n'
                      ORDER BY kind, name, detail)) AS fingerprint,
       count(*) AS object_count
FROM objects;
