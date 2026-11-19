# Security and Privacy — Salary Estimation Tool

**Document ID:** `DOC-SECURITY-PRIVACY-001`  
**Status:** Draft — pending owner approval  
**Date:** 17 Aban 1405 SH (2026-11-17)  
**Related:** `DOC-DATA-MODEL-SPEC-001`, `DOC-FUNC-REQ-001`

---

## 1. Security Philosophy

Simplified from the existing project: no `tenant_id`, no RLS, no `FORCE ROW LEVEL SECURITY`, no AES-256-GCM application-layer encryption, no blind indexing. Single manager access only. Standard database access controls and HTTPS suffice for v1.

## 2. Authentication & Authorization

| Requirement | Specification |
|:---|:---|
| User type | Exactly one: manager |
| Authentication | Email + password (hashed with bcrypt/argon2id) |
| MFA | Not required in v1 |
| Sessions | Not required in v1; simple cookie or token |
| Employee accounts | None |
| Role-based access | None (single manager) |
| API authentication | Simple bearer token or session cookie |

## 3. Data Protection

| Data Type | Sensitivity | Protection |
|:---|:---|:---|
| Resume text | Medium | Stored in database; access controlled by manager login |
| Extracted skills/experience | Medium | Stored in database |
| Salary estimates | Medium | Stored in database; manager-only |
| Manager credentials | High | Hashed passwords (argon2id/bcrypt) |
| National ID / mobile / Sheba | Not collected | Not applicable |

## 4. What Is NOT Required (v1)

| Security Feature | Existing Project | New Product | Reason |
|:---|:---|:---|:---|
| `tenant_id` on all tables | Required (ADR-006/007) | Not required | Single manager |
| `FORCE ROW LEVEL SECURITY` | Required | Not required | No tenancy |
| AES-256-GCM encryption | Required (ADR-003) | Not required | Resume data not high-sensitivity PII |
| HMAC-SHA256 blind indexing | Required (ADR-003) | Not required | No National ID/mobile/Sheba |
| Multi-role schema (7 roles) | Required | Not required | Single manager |
| Audit hash chain | Required (P0-T10) | Not required | Simple estimate history |

## 5. Privacy

- No National ID, mobile number, or Sheba number is collected.
- Resume data is stored only with manager consent.
- Estimates are associated with the manager who created them.
- No data is transmitted to external services except optional market data sources.
- No AI training on user data (AI used only for analysis, not model training).

## 6. Assumptions (Unresolved)

| ID | Assumption | Owner Decision Needed |
|:---|:---|:---|
| S-01 | Whether to implement password-based auth or no auth (single trusted manager) | Yes |
| S-02 | Whether to keep AES-256-GCM as optional future security layer | Yes |
| S-03 | Whether resume files need encryption at rest | Yes |
