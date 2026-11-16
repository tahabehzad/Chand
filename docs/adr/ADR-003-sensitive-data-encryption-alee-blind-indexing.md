# ADR-003: Adoption of Application-Level Envelope Encryption (ALEE) and Blind Indexing for Candidate PII

- **Status**: Accepted
- **Date**: 2026-11-13 (22 Aban 1405 SH)
- **Deciders**: Security Architect, Database Administrator, Lead Backend Engineer
- **Consulted**: Legal Counsel (Iranian Computer Crimes Law Specialist)

## Context and Problem Statement
Pish Hesabdari processes sensitive personally identifiable information (PII), including National IDs (*Code Melli*), Shenasnameh serials, bank Sheba account numbers, and historical salary records. 

The original brief proposed using PostgreSQL's in-database `pgcrypto` extension. The Red-Team Audit (`FIND-ARCH-03` and `FIND-DATA-02`) demonstrated that:
1. `pgcrypto` requires passing plaintext encryption keys in SQL queries, exposing them in PostgreSQL query logs (`log_statement = 'all'`), performance views (`pg_stat_statements`), and replication streams.
2. Encrypting fields with randomized initialization vectors (AES-GCM) renders database equality lookups (`WHERE national_id = :val`) impossible without decrypting every row in the table via an unscalable $O(N)$ full table scan.

## Decision Drivers
1. **Zero Plaintext Key Exposure**: Encryption keys must never enter the database engine or appear in SQL statements.
2. **High-Performance Searchability**: System must detect duplicate candidate profiles and perform identity lookups in $O(1)$ B-Tree index time.
3. **Statutory Compliance**: Strict adherence to Iranian Computer Crimes Law (Articles 1, 16, 17) and E-Commerce Law (Article 58) regarding protection of confidential data.

## Considered Options
1. **Option 1**: PostgreSQL `pgcrypto` in-database encryption (Original proposal)
2. **Option 2**: Database Transparent Data Encryption (TDE) only
3. **Option 3**: Application-Level Envelope Encryption (ALEE) with HashiCorp Vault and HMAC-SHA256 Blind Indexing

## Decision Outcome
Chosen option: **Option 3: Application-Level Envelope Encryption (ALEE) with Blind Indexing**.

### Positive Consequences
- **Cryptographic Separation**: PostgreSQL stores only encrypted ciphertexts and blind hashes; a compromised database or rogue DBA cannot decrypt PII without the external KMS.
- **Fast Equality Search via Blind Indexing**: Exact lookups on National ID (*Code Melli*) and Sheba use a deterministic HMAC-SHA256 hash salted with an isolated secret enterprise pepper (`national_id_bindex`). Lookups execute in $< 1$ms via standard PostgreSQL B-Tree indexes.
- **Tenant Key Isolation**: Each enterprise tenant possesses a distinct Data Encryption Key (DEK) wrapped by a master Key Encryption Key (KEK) in HashiCorp Vault.

### Negative Consequences / Trade-offs
- Range queries and substring searches (`LIKE '%123%'`) cannot be performed on encrypted fields (acceptable, as National IDs and Shebas require exact matching).
- Requires operational maintenance of a HashiCorp Vault instance (or KMS sidecar).

## Implementation Directives
1. Application Layer: Implement `PiiFieldTransformer` in Python using `cryptography.hazmat.primitives.ciphers.aead.AESGCM`.
2. Storage Format in PostgreSQL:
   - `national_id_ciphertext`: `BYTEA` (Nonce + Ciphertext + Tag)
   - `national_id_bindex`: `CHAR(64)` (Hex-encoded HMAC-SHA256(Code Melli, PEPPER))
3. Database Index: `CREATE UNIQUE INDEX idx_emp_national_id_bindex ON employees (tenant_id, national_id_bindex);`
