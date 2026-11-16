-- Empty development cluster only. No application/tenant schema or rules.
REVOKE ALL ON DATABASE pish_dev FROM PUBLIC;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
ALTER DEFAULT PRIVILEGES REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;
CREATE EXTENSION IF NOT EXISTS pgaudit;
ALTER DATABASE pish_dev SET pgaudit.log = 'read,write,ddl,role';
