-- ADR-007: explicit cluster-role provisioning by a trusted administrator.
-- No logins, secrets or memberships are created. Existing roles are validated.
DO $$
DECLARE role_name text;
BEGIN
    FOREACH role_name IN ARRAY ARRAY['pish_statutory_reader', 'pish_statutory_reviewer'] LOOP
        IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = role_name) THEN
            EXECUTE format('CREATE ROLE %I NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS', role_name);
        END IF;
        IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = role_name AND
            (rolcanlogin OR rolsuper OR rolcreatedb OR rolcreaterole OR rolreplication OR rolbypassrls))
            OR EXISTS (SELECT 1 FROM pg_auth_members m JOIN pg_roles r ON r.oid=m.member
                WHERE r.rolname=role_name)
        THEN RAISE EXCEPTION 'Existing statutory role has unsafe privileges/membership'; END IF;
    END LOOP;
END $$;
