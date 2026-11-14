---
name: database-engineering
description: Engineers PostgreSQL relational schemas, versioned statutory parameter tables, cryptographic audit chaining, blind indexing for encrypted PII, and multi-tenant RLS policies.
---

# Database Engineering & Domain Modeling Skill

## Purpose
Design enterprise-grade relational database schemas, migration strategies, indexing patterns, and audit structures in PostgreSQL 16+.

## Engineering Standards
1. **Immutable Historical Rules**: Never store statutory parameters only in application code or seed files. Model them in a `statutory_rule_set_versions` table:
   - Fields: `id`, `rule_year_shamsi`, `effective_date`, `daily_minimum_wage_rial`, `sso_insurable_ceiling_rial`, `tax_brackets_json`, `is_active`, `created_at`.
   - Every `payroll_run` and `hokm_simulation` must store a foreign key to the exact `statutory_rule_set_version_id` used.
2. **Encrypted PII Storage Pattern**:
   - `national_id_encrypted`: BYTEA (AES-256-GCM ciphertext + IV + Auth Tag)
   - `national_id_bindex`: VARCHAR(64) (HMAC-SHA256 of normalized Code Melli with secret server pepper; indexed with B-Tree)
3. **Cryptographic Audit Log**:
   - Append-only table: `audit_logs`
   - Fields: `id`, `tenant_id`, `actor_id`, `event_type`, `payload_hash`, `prev_hash`, `current_hash`, `created_at`.
   - Enforce database trigger preventing `UPDATE` or `DELETE` on `audit_logs`.
4. **Row-Level Security (RLS)**:
   - Every tenant table has `tenant_id UUID NOT NULL REFERENCES organizations(id)`.
   - Table policy: `CREATE POLICY tenant_isolation_policy ON [table] USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid);`
   - Force security: `ALTER TABLE [table] FORCE ROW LEVEL SECURITY;`
