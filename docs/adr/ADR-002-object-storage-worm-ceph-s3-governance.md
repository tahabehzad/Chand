# ADR-002: Replacement of MinIO with Ceph / S3-Compatible Storage and Adoption of GOVERNANCE WORM Locking

- **Status**: Accepted
- **Date**: 2026-11-13 (22 Aban 1405 SH)
- **Deciders**: Infrastructure Architect, Legal Counsel, Security Lead
- **Consulted**: Compliance Officer, Lead Backend Engineer

## Context and Problem Statement
Under Article 19 of the Iranian Commercial Code and forensic document evidentiary rules, candidate verification dossiers, historical salary snapshots, and inquiry slips must be stored immutably. 

The original brief specified **MinIO with S3 Object Lock in COMPLIANCE mode**. The Red-Team Audit (`FIND-ARCH-02`) revealed two fatal defects:
1. MinIO transitioned to the **GNU AGPLv3 copyleft license** in 2021, creating viral open-source licensing risks for commercial SaaS deployments, while commercial MinIO licenses cannot be legally procured in Iran due to US OFAC sanctions.
2. `COMPLIANCE` mode completely bars object deletion by ANY identity, including root. If an operator mistakenly uploads corrupt files, or if an individual exercises their statutory privacy rights (E-Commerce Law Art. 58) or a court orders document expungement, data cannot be removed without physically destroying the storage cluster.

## Decision Drivers
1. **Licensing Safety**: The storage engine must be under a permissive open-source license (Apache 2.0 or MIT) to prevent viral SaaS copyleft contamination.
2. **Domestic Cloud Feasibility**: Must be natively compatible with leading Iranian S3 cloud storage providers (e.g., ArvanCloud, Cloudware, MobinNet) and self-hosted on-premise clusters.
3. **Legal vs. Operational Balance**: Must guarantee tamper-evident immutability while preserving an authorized emergency override for judicial expungement.

## Considered Options
1. **Option 1**: MinIO S3 Object Lock in COMPLIANCE Mode (Original proposal)
2. **Option 2**: Ceph Object Gateway (RADOS GW) or S3-Compatible Provider with GOVERNANCE Mode WORM
3. **Option 3**: Local Filesystem with Linux Append-Only (`chattr +a`) Attributes

## Decision Outcome
Chosen option: **Option 2: Ceph Object Gateway (or Managed S3 Provider) with Object Lock in GOVERNANCE Mode**.

### Positive Consequences
- **Zero Licensing Risk**: Ceph is licensed under **Apache 2.0 / LGPL 2.1**, completely eliminating AGPLv3 legal liabilities.
- **Tamper-Evident Immutability**: In `GOVERNANCE` mode, objects cannot be overwritten, modified, or deleted by standard API credentials throughout their retention window.
- **Judicial & Compliance Safety**: Authorized compliance officers possessing a separate cryptographic emergency key (`s3:BypassGovernanceRetention`) can purge or expunge records when legally mandated by court order.
- **Provider Portability**: Standard AWS S3 Signature Version 4 API supported natively across on-premise Ceph clusters and domestic Iranian cloud object stores.

### Negative Consequences / Trade-offs
- Ceph cluster setup on-premise requires specialized storage engineering expertise (mitigated by using domestic managed S3 during initial rollout).

## Implementation Directives
1. Storage Client: Use `boto3` or `aioboto3` with standard S3 API.
2. Default Bucket Configuration: Enable Object Lock on bucket creation:
   `ObjectLockConfiguration: {'ObjectLockEnabled': 'Enabled', 'Rule': {'DefaultRetention': {'Mode': 'GOVERNANCE', 'Days': 3650}}}`.
3. Access Control: Standard application service accounts are denied `s3:BypassGovernanceRetention`. This permission is isolated to an offline administrative vault.
