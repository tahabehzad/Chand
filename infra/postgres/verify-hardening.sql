-- Read-only assertions, run by verify_local.py through CA-verified TLS.
DO $$
BEGIN
    IF current_setting('server_version_num')::int NOT BETWEEN 160000 AND 169999 THEN
        RAISE EXCEPTION 'FAIL: PostgreSQL major version';
    END IF;
    IF current_setting('ssl') <> 'on'
       OR current_setting('ssl_min_protocol_version') <> 'TLSv1.3'
       OR NOT EXISTS (SELECT FROM pg_stat_ssl WHERE pid=pg_backend_pid() AND ssl AND version='TLSv1.3') THEN
        RAISE EXCEPTION 'FAIL: TLS policy/session';
    END IF;
    IF current_setting('log_statement') <> 'none'
       OR current_setting('log_parameter_max_length') <> '0'
       OR current_setting('log_parameter_max_length_on_error') <> '0'
       OR current_setting('log_min_error_statement') <> 'panic'
       OR current_setting('pgaudit.log_statement') <> 'off'
       OR current_setting('pgaudit.log_parameter') <> 'off'
       OR current_setting('pgaudit.log_client') <> 'off' THEN
        RAISE EXCEPTION 'FAIL: private logging policy';
    END IF;
    IF NOT ('pgaudit' = ANY(string_to_array(current_setting('shared_preload_libraries'), ',')))
       OR NOT EXISTS (SELECT FROM pg_extension WHERE extname='pgaudit')
       OR NOT (ARRAY['read','write','ddl','role'] <@ string_to_array(lower(replace(current_setting('pgaudit.log'), ' ', '')), ','))
       OR EXISTS (SELECT FROM pg_extension WHERE extname NOT IN ('plpgsql','pgaudit')) THEN
        RAISE EXCEPTION 'FAIL: extension policy';
    END IF;
    IF current_setting('password_encryption') <> 'scram-sha-256'
       OR NOT EXISTS (SELECT FROM pg_authid WHERE rolname=current_user AND rolpassword LIKE 'SCRAM-SHA-256$%') THEN
        RAISE EXCEPTION 'FAIL: bootstrap SCRAM policy';
    END IF;
    -- pg_settings.setting is normalized to each parameter's documented
    -- base unit; avoid depending on SHOW's human-readable 60s/1min spelling.
    IF current_setting('wal_level') <> 'replica' OR EXISTS (
        SELECT FROM (VALUES
            ('block_size','8192'),
            ('max_wal_size','4096'),
            ('shared_buffers','32768'),
            ('effective_cache_size','65536'),
            ('work_mem','8192'),
            ('max_connections','200'),
            ('statement_timeout','30000'),
            ('idle_in_transaction_session_timeout','60000'),
            ('log_min_duration_statement','500')
        ) required(name,value)
        LEFT JOIN pg_settings actual USING (name)
        WHERE actual.setting IS DISTINCT FROM required.value
    ) THEN
        RAISE EXCEPTION 'FAIL: WAL/timeout policy';
    END IF;
    IF EXISTS (SELECT FROM pg_hba_file_rules WHERE error IS NOT NULL) THEN
        RAISE EXCEPTION 'FAIL: invalid HBA rule';
    END IF;
    IF EXISTS (
        SELECT FROM pg_namespace n,
          LATERAL aclexplode(COALESCE(n.nspacl, acldefault('n', n.nspowner))) a
        WHERE n.nspname='public' AND a.grantee=0 AND a.privilege_type='CREATE'
    ) OR EXISTS (
        SELECT FROM pg_database d,
          LATERAL aclexplode(COALESCE(d.datacl, acldefault('d', d.datdba))) a
        WHERE d.datname=current_database() AND a.grantee=0
    ) THEN
        RAISE EXCEPTION 'FAIL: PUBLIC privilege policy';
    END IF;
END $$;
