---
title: "Risk Register — Pish Hesabdari"
document_id: KNOW-RISK-001
status: Active navigation layer
as_of: 2026-11-16
---

# Risk Register

> **This is a navigation and consolidation layer, not a new risk authority.** Canonical risk IDs and severity come from [Holy Bible Appendix C](../../docs/PISH_HESABDARI_HOLY_BIBLE.md). Readiness risks come from [IMPLEMENTATION_READINESS §8](../../docs/IMPLEMENTATION_READINESS.md); schedule risks from [EXECUTION_PLAN §14.6](../../docs/EXECUTION_PLAN.md). Observed verification gaps are labelled with their actual status, never upgraded by inference.

## Current operational and verification risks

| ID | Risk | Category | Status / evidence | Link |
| :--- | :--- | :--- | :--- | :--- |
| `RISK-OBS-01` | PostgreSQL integration suites were not executed in the latest pass; RLS, migration and database acceptance are unverified here | Verification / database | **NOT RUN** — Docker daemon unavailable; 104 suites self-skip | [BOOTSTRAP_CHANGELOG §24](../../docs/BOOTSTRAP_CHANGELOG.md) · [PROJECT_STATUS §2](../../docs/PROJECT_STATUS.md) |
| `RISK-OBS-02` | CI workflow exists but has never executed on GitHub; merge quality gates are not demonstrated | Delivery / quality | **OPEN** — `gh` token recorded invalid | [PROJECT_STATUS §2](../../docs/PROJECT_STATUS.md) |
| `RISK-OBS-03` | No independent review by a non-author is available; financial/security changes are author-reviewed only | Governance | **OPEN** — all engine tasks remain `READY_FOR_REVIEW`; none `APPROVED` | [AGENTS.md §6](../../AGENTS.md) · [AUTONOMOUS_PROGRESS](../../AUTONOMOUS_PROGRESS.md) |
| `RISK-OBS-04` | No authenticated workflow or integrated tenant-security foundation exists | Security / product | **OPEN** — stated limitation, not a test failure | [PROJECT_STATUS §2](../../docs/PROJECT_STATUS.md) |
| `RISK-OBS-05` | No certified golden corpus; local tests are not statutory certification | Quality / legal | **OPEN / MISSING** — 10,000-case corpus does not exist | [P1-T15](../../docs/EXECUTION_PLAN.md) · [DEC-002](../../docs/DECISIONS_REGISTER.md) |
| `RISK-OBS-06` | 1405 statutory values remain transcribed but unverified and inactive | Legal / regulatory | **UNVERIFIED** — fail-closed loader refuses 1405 | [PROJECT_STATUS §4](../../docs/PROJECT_STATUS.md) · [DEC-001](../../docs/DECISIONS_REGISTER.md) |
| `RISK-OBS-07` | Documentation drift between current status and older snapshots | Documentation | **CONFLICT** — README, handoff and Holy Bible metadata predate §24 | [Decision Status](../Decisions/Decision%20Status.md) |
| `RISK-OBS-08` | ADR-007 is accepted but omitted from ADR_INDEX and DOCUMENTATION_INDEX | Documentation / governance | **CONFLICT / MISSING** — both sources linked, not resolved | [ADR-007](../../docs/adr/ADR-007-statutory-global-access-and-deferred-identity.md) · [ADR_INDEX](../../docs/ADR_INDEX.md) |

## Legal, financial and statutory risks

| ID | Risk | Severity | Mitigation / current posture |
| :--- | :--- | :--: | :--- |
| `HB-RISK-01` | 1405 baseline never verified; platform ships 1404 law in a 1405 year | **CRITICAL** | Interim 1404 position with disclosure; fail-closed loader; year printed on results |
| `HB-RISK-02` | Phase 1 gate cannot be met without a Certified Tax Accountant | **CRITICAL** | External appointment required; no accountant engaged |
| `HB-RISK-04` | Golden corpus substituted with a synthetic one | **HIGH** | Corpus schema must carry `approved_by`; no such corpus exists |
| `HB-RISK-05` | Golden files silently re-baselined to make builds green | **HIGH** | Reviewed change and financial-diff gate required; no CI execution yet |
| `HB-RISK-06` | Defective published example propagates into a golden corpus | **CRITICAL** | Defect recorded; `P1-T20` is out of ADR-008 scope |
| `HB-RISK-07` | Flat-10% Eydi rule causes under-withholding | **CRITICAL** | Engine never consumes the flat rate and applies progressive taxation; seed remains immutable |
| `HB-RISK-08` | SSO insurable base mis-modelled | **HIGH** | B-3 open; requires a written determination |
| `HB-RISK-28` | Advisory boundary misread, creating professional-liability exposure | **HIGH** | DEC-009 open; prominent disclaimer still required |

Full table: [Holy Bible Appendix C](../../docs/PISH_HESABDARI_HOLY_BIBLE.md) (HB-RISK-01…HB-RISK-34).

## Security and tenancy risks

| ID | Risk | Severity | Current mitigation / gap |
| :--- | :--- | :--: | :--- |
| `HB-RISK-09` | Tenant-isolation escape in production | **HIGH** | FORCE RLS design and isolated migration evidence; integration re-run **NOT RUN** |
| `HB-RISK-10` | Host compromise yields ciphertext and DEK | **HIGH** | KEK/DEK design; key registry and production integration not implemented |
| `HB-RISK-20` | Master KEK loss | **HIGH** | Backup/off-site key custody not implemented |
| `HB-RISK-30` | Audit-chain tail truncation | **MEDIUM** | External anchor not specified/implemented |
| `HB-RISK-29` | Lengthless `CHAR` truncates a hash | **HIGH** | Migration lint and `P0-T12` design; full integration not run |

## Schedule and delivery risks

| ID | Risk | Severity | Note |
| :--- | :--- | :--: | :--- |
| `HB-RISK-13` | OCR worker saturates the API | **HIGH if ADR-005 not accepted** | ADR-005 `PROPOSED`; `P2-T04` blocked |
| `HB-RISK-16` | Phase 2 holds 95 engineer-days with 5 blocked tasks | **HIGH** | EXECUTION_PLAN §14.6 R-1; no schedule change approved |
| `HB-RISK-17` | Phase 4 gate cannot be delivered in 2 weeks | **HIGH** | EXECUTION_PLAN §14.6 R-6; vendor engagement required |
| `R-1` | Phase 2 capacity/dependency compression | Recorded, not applied | Requires CTO approval |
| `R-2` | Phase 1 gate depends on an external corpus with no owner | Recorded, not applied | Requires external appointment |

## Top three readiness risks (verbatim source)

1. **Golden vector corpus (`P1-T15`)** — the only evidence of legal correctness; external and not yet engaged.
2. **1405 four-eyes verification (`P1-T02`)** — primary sources unreachable from engineering; legal-team task.
3. **500-slip corpus (`P2-T16`)** — requires employer consent and a redaction pipeline.

Source: [IMPLEMENTATION_READINESS §8](../../docs/IMPLEMENTATION_READINESS.md).

## B-series statutory ambiguities

B-1…B-8 and B-10 remain open and require a human legal/tax ruling; B-9 and B-11 are engineering-resolved. See [Decision Status](../Decisions/Decision%20Status.md) and [DECISIONS_REGISTER](../../docs/DECISIONS_REGISTER.md).

> A risk entry is not a fraud verdict, a legal conclusion or an approval. Do not downgrade a severity or close a risk without evidence from the named owner.
