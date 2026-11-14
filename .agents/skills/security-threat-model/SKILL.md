---
name: security-threat-model
description: Performs STRIDE threat modeling, analyzes multi-tenant isolation, secures cryptographic key management (ALEE/Vault), prevents RLS leakage, and enforces Iranian cyber law compliance.
---

# Security & Threat Modeling Skill

## Purpose
Identify security vulnerabilities, threat vectors, privilege escalation paths, and compliance risks across Iranian enterprise SaaS environments.

## Threat Analysis Framework
1. **STRIDE Analysis**:
   - *Spoofing*: Candidate forgery, manipulated PDF signatures, spoofed tenant headers.
   - *Tampering*: Alteration of historical calculation snapshots, parameter tampering.
   - *Repudiation*: Employer denying settlement calculation without cryptographic audit logs.
   - *Information Disclosure*: Leaking candidate National IDs, Sheba numbers, or salary history across tenants.
   - *Denial of Service*: Malformed PDFs or zip bombs overwhelming the OCR worker pool.
   - *Elevation of Privilege*: Standard HR user accessing cross-departmental executive salaries.
2. **Multi-Tenant Isolation Mandate**:
   - Always enforce `ALTER TABLE ... FORCE ROW LEVEL SECURITY` in PostgreSQL.
   - For local single-user/enterprise deployment without external connection poolers (PgBouncer), enforce scoped session context setting (`SET LOCAL app.current_tenant_id`) within each transaction boundary.
3. **Application-Level Envelope Encryption (ALEE)**:
   - Never use in-database `pgcrypto` for sensitive PII.
   - Encrypt National IDs and Sheba numbers in Python with AES-256-GCM using tenant-specific Data Encryption Keys (DEKs) wrapped by a secure local master key (Argon2id-derived from local encrypted master config).
   - Implement Blind Indexing (HMAC-SHA256 with pepper) for exact-match database queries.
4. **Legal Compliance**:
   - Enforce Iranian Computer Crimes Law (Articles 1, 16, 17) and E-Commerce Law (Article 58) regarding unauthorized data dissemination.
