# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x (Chand)   | :white_check_mark: |
| < 0.2.0 | :x:                |

## Reporting a Vulnerability

We take the security of Chand, our Iranian labor market database, and sensitive candidate personal information seriously.

If you believe you have found a security vulnerability in this project:

1. **Do NOT open a public GitHub issue.**
2. Send an email to the security and engineering contact at `security@pish-hesabdari.local` or through the designated repository maintainer channel.
3. Include:
   - Type of issue (e.g. RLS bypass, PII leakage, injection, cryptographic anomaly)
   - Step-by-step reproduction instructions or proof-of-concept
   - Impact assessment

You should receive an acknowledgment within 48 hours. We will keep you informed of our progress toward resolving the issue.

## Security Architecture & Invariants

Chand operates under strict security and confidentiality constraints:

- **PII Encryption at Rest:** High-sensitivity candidate data (e.g., National ID, Sheba, contact numbers) must be encrypted with AES-256-GCM in the application layer. Cryptographic keys never reside unencrypted in database tables.
- **Blind Indexing:** Exact searching of sensitive identifiers is conducted exclusively through HMAC-SHA256 blind indexing with an isolated pepper.
- **Append-Only Audit Ledger:** Audit trails are cryptographically chained and tamper-evident; `UPDATE` and `DELETE` queries are forbidden on audit log tables.
- **No Sensitive Data in Logs/Traces:** Application loggers and exception handlers explicitly redact real candidate compensation figures, bank account details, and government identifiers.
- **Zero-Fabrication Guarantee:** The estimation engine refuses queries with `insufficient_data` rather than extrapolating unsupported figures, preventing misleading compensation guidance.
