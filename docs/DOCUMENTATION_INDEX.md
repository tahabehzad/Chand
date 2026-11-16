# Documentation Index & Change Control

- **Document ID:** `DOC-DOCIDX-001`
- **Status:** Active
- **Date:** 2026-11-14 (23 Aban 1405 SH)
- **Related:** [`docs/EXECUTION_PLAN.md`](EXECUTION_PLAN.md) §1 · [`docs/ADR_INDEX.md`](ADR_INDEX.md)

---

## 0. Task-focused reading

Start with AGENTS.md; use this table to select the relevant source sections. This index routes readers to existing authority; it is not a second specification or a change to the product roadmap.

| Task | Required context |
| :--- | :--- |
| Any first change | Holy Bible §0.3 (authority), §13.1 (change control), §13.8 (agent constraints); relevant §3 requirements |
| Current status / next task | PROJECT_STATUS §2; exact WBS row, dependencies, decisions and AC in EXECUTION_PLAN §14.3; ROADMAP_OPERATIONAL_PAYROLL for what separates the delivered engine from operational use; PROJECT_STATE for one-screen orientation only (derived, non-authoritative) |
| API / configuration | Applicable DEPLOYMENT and AUTH sections; relevant WBS/specification |
| Encryption / database / tenancy | ADR-003 and ADR-006; AUTH security/schema sections; database-engineering and security-threat-model skills |
| Financial / engine work | Relevant Holy Bible §2/§3/§10 and REMEDIATED module; STATUTORY_INGESTION; financial-data-integrity and iranian-payroll-engineering skills; unresolved decisions |
| Persian frontend / PDF | ADR-001; FRONTEND_PERSIAN; persian-rtl-engineering; DEC-006 remains open |
| Document verification | DOCUMENT_FORENSICS; applicable security/privacy requirements; ADR-005 remains proposed |
| Delegation | AGENT_OPERATING_MODEL §3 (ownership/handoff), §4 (isolation) and current environment evidence |
| Verification history | BOOTSTRAP_CHANGELOG §16: latest full suite and regulatory acquisition; §15: PostgreSQL runtime; §13: documentation maintenance |
| Historical evidence | Specific source and section only after the supersession map in §§2–4 |

**Loading discipline:** search headings/IDs first (RTK-prefixed `rg`), then read bounded sections. Load only task-relevant skill bodies and references. Read a required specification in full when its task contract requires it; a handoff summary is not a substitute. Do not routinely dump the full Holy Bible, WBS, changelog, every skill, DOCX corpus or old audit.

Keep the loaded document revision/section in the task handoff; reread when the source changes or the task expands. Check only relevant host capabilities rather than repeating a complete machine inventory. Record verification and status changes as required; avoid duplicate narrative reports when the existing execution record suffices.

**Current versus historical:** PROJECT_STATUS and the WBS own delivery state; DECISIONS_REGISTER and accepted ADRs own decision state; ENVIRONMENT_INVENTORY separates dated observations from current capability checks. Original Holy Bible §0.4 and Appendix E are historical snapshots. Documentation maintenance does not complete a WBS task or revalidate an application test.

---

## 1. The documentation package

### 1.1 Current — binding

| Path | ID | Purpose | Authority rank |
| :--- | :-- | :--- | :--: |
| [`docs/EXECUTION_PLAN.md`](EXECUTION_PLAN.md) | `DOC-EXEC-001` | The master execution plan: scope, specification baseline, WBS, gates | 4 |
| [`docs/DECISIONS_REGISTER.md`](DECISIONS_REGISTER.md) | `REG-DEC-001` | The register of unresolved decisions and blockers | 4 |
| [`docs/IMPLEMENTATION_READINESS.md`](IMPLEMENTATION_READINESS.md) | `DOC-READY-001` | Per-phase readiness classification | 4 |
| [`docs/ADR_INDEX.md`](ADR_INDEX.md) | `DOC-ADRIDX-001` | The ADR register and the rejected-technology list | 4 |
| [`docs/DOCUMENTATION_INDEX.md`](DOCUMENTATION_INDEX.md) | `DOC-DOCIDX-001` | This document: the hierarchy and the supersession map | 4 |
| [`docs/EXECUTION_DOCUMENTATION_AUDIT.md`](EXECUTION_DOCUMENTATION_AUDIT.md) | `DOC-AUDIT-001` | The self-audit of this package | 4 |
| [`docs/ROADMAP_OPERATIONAL_PAYROLL.md`](ROADMAP_OPERATIONAL_PAYROLL.md) | `DOC-ROADMAP-001` | Derived roadmap from the delivered engine to operational use: in-domain, decision-blocked and out-of-scope tracks with milestones | 4 (derived; creates no task or scope authority) |

**Derived snapshot (not an authority):** [`PROJECT_STATE.md`](../PROJECT_STATE.md) (`DOC-STATE-001`) is a short snapshot of the current state for a reader who needs orientation. It holds **no independent facts** and ranks below every row above: delivery state is owned by [`docs/PROJECT_STATUS.md`](PROJECT_STATUS.md), tasks by [`docs/EXECUTION_PLAN.md`](EXECUTION_PLAN.md) §14.3, decisions by [`docs/DECISIONS_REGISTER.md`](DECISIONS_REGISTER.md) and [`docs/adr/`](adr/), verification by [`docs/BOOTSTRAP_CHANGELOG.md`](BOOTSTRAP_CHANGELOG.md). Where the snapshot disagrees with an owner, the owner is correct and the snapshot is stale. Load it instead of the owners only when a one-screen orientation is enough; load the owner for any decision, status change or verification claim.

### 1.2 Subordinate specifications

| Path | ID | Scope |
| :--- | :-- | :--- |
| [`docs/specs/STATUTORY_INGESTION.md`](specs/STATUTORY_INGESTION.md) | `SPEC-STAT-001` | Source identification, acquisition, transcription, four-eyes verification, versioning, change history, activation criteria, 1404 regression |
| [`docs/specs/AUTH.md`](specs/AUTH.md) | `SPEC-AUTH-001` | Users, organizations, membership, roles, permissions, sessions, MFA, tenant isolation, audit attribution, key management, emergency access |
| [`docs/specs/FRONTEND_PERSIAN.md`](specs/FRONTEND_PERSIAN.md) | `SPEC-FE-001` | RTL layout, Vazirmatn, Jalali calendar, numeral and currency policy, text normalisation, PDF shaping and embedding, accessibility, responsive behaviour |
| [`docs/specs/TESTING.md`](specs/TESTING.md) | `SPEC-QA-001` | The 13 test layers, tooling, environments, fixtures, CI stages, blocking rules, coverage, release criteria |
| [`docs/specs/DEPLOYMENT.md`](specs/DEPLOYMENT.md) | `SPEC-OPS-001` | Topology, Windows development, containers, migrations, configuration and secrets, TLS, observability, backup, runbooks, retention, upgrade/rollback, air-gapped deployment |
| [`docs/specs/DOCUMENT_FORENSICS.md`](specs/DOCUMENT_FORENSICS.md) | `SPEC-DOC-001` | Document taxonomy, custody, OCR, tamper detection, signatures, issuer verification, status model, consistency matrix, 4-way disambiguation, `V_score` |

### 1.3 Architecture Decision Records

| Path | Status |
| :--- | :--- |
| [`docs/adr/ADR-001-frontend-architecture-react-vite-spa.md`](adr/ADR-001-frontend-architecture-react-vite-spa.md) | Accepted |
| [`docs/adr/ADR-002-object-storage-worm-ceph-s3-governance.md`](adr/ADR-002-object-storage-worm-ceph-s3-governance.md) | Accepted |
| [`docs/adr/ADR-003-sensitive-data-encryption-alee-blind-indexing.md`](adr/ADR-003-sensitive-data-encryption-alee-blind-indexing.md) | Accepted |
| [`docs/adr/ADR-004-phase-1-product-boundary-prehire-scope.md`](adr/ADR-004-phase-1-product-boundary-prehire-scope.md) | Accepted — module list and directives 2–3 **superseded by ADR-008**; text retained |
| [`docs/adr/ADR-005-async-execution-strategy.md`](adr/ADR-005-async-execution-strategy.md) | **Proposed** |
| [`docs/adr/ADR-006-phase-0-owner-approved-security-and-schema.md`](adr/ADR-006-phase-0-owner-approved-security-and-schema.md) | **Accepted — owner-approved four Phase 0 choices; limited amendment of ADR-003 directive 3** |
| [`docs/adr/ADR-008-product-scope-statutory-payroll-engine.md`](adr/ADR-008-product-scope-statutory-payroll-engine.md) | **Accepted — product scope refocus on the statutory payroll calculation engine; resolves DEC-002a; ADR-004 module list superseded** |

### 1.4 Upstream sources — outside `docs/`, unmodified by this workstream

| Path | Role | Rank |
| :--- | :--- | :--: |
| `REMEDIATED_TECHNICAL_SPECIFICATION_V2.md` | The authoritative product & technical specification | 2 |
| `PHASE_1_RED_TEAM_AUDIT.md` | The findings and correction register | 3 |
| `PHASE_1_FINAL_AUDIT_BRIEF.md` | **Superseded** baseline brief | 6 |
| `RESEARCH_GAP_ANALYSIS_AND_ADVANCED_SPECIFICATION.md` | **Historical** research synthesis | 5 (retained sections only) |
| `گزارش جامع پژوهشی.docx` (PH-RES-1405-01) | Persian baseline research | 5 |
| `Technical Investigation of Related Software Projects.docx` | Technology landscape survey | 5 |
| `1.docx` | Independent audit of the two baseline reports | 5 |
| `backend/data/seeds/statutory_rules_1404.yaml` | **Verified** historical rule set — do not modify | 2 |
| `backend/data/seeds/statutory_rules_1405.yaml` | **Transcribed, unverified candidate** — must remain inactive; unavailable values remain unknown | 2 |
| `.agents/skills/*/SKILL.md` | Agent behaviour contracts — engineering standards, not project documents | n/a |

---

## 2. Supersession map — `RESEARCH_GAP_ANALYSIS_AND_ADVANCED_SPECIFICATION.md`

This document carries a historical banner (lines 2–6) that names only *"Celery/Redis architecture, Next.js, and 1404 SH temporal assumptions"* as superseded. **That under-declares the scope.** The body still prescribes several rejected technologies in the present tense. This section is the **authoritative supersession statement**.

### 2.1 Section-level disposition

| Section | Content | Disposition | Superseded by |
| :--- | :--- | :--- | :--- |
| Header banner | The historical notice | **RETAINED but INCOMPLETE** — must be read with this table | — |
| Deliverable 1 · §1.1 | Mission, boundaries | **RETAINED** | — |
| Deliverable 1 · §1.2 | Audit of the baseline artefacts | **RETAINED** (historical record) | — |
| Deliverable 1 · §1.3 | Three-way research classification | **RETAINED** (methodology) | — |
| Deliverable 1 · §1.4 | Investigation priorities and exclusions | **RETAINED** | — |
| Deliverable 2 · §2.1 | The 12-category document taxonomy | **RETAINED** → `SPEC-DOC-001` §2 | — |
| Deliverable 2 · §2.2.1 | Official verification portals | **RETAINED** → `SPEC-DOC-001` §7.1 | — |
| Deliverable 2 · §2.2.2 | The Shahkar reality check | **RETAINED** → `SPEC-DOC-001` §7.2 | — |
| Deliverable 2 · §2.2.3 | Iranian PKI and pyHanko | **RETAINED** → `SPEC-DOC-001` §6 | — |
| Deliverable 2 · §2.2.4 | PDF structure and metadata forensics | **RETAINED** → `SPEC-DOC-001` §5.1 | — |
| Deliverable 2 · §2.2.5 | ELA and clone detection | **RETAINED** → `SPEC-DOC-001` §5.2 | — |
| Deliverable 2 · §2.2.6 | Persian OCR engine comparison | **RETAINED with a correction** — the latency column is superseded by `FIND-ARCH-05` (3.5–6.0 s CPU / 1.2–1.8 s T4) | `SPEC-DOC-001` §4.2 |
| Deliverable 2 · §2.2.7 | Cross-document consistency matrix | **RETAINED** → `SPEC-DOC-001` §9 | — |
| Deliverable 2 · §2.3 | The verification-status model and weights | **RETAINED** → `SPEC-DOC-001` §8 | — |
| Deliverable 2 · §2.4 | The end-to-end document workflow | **RETAINED** → `SPEC-DOC-001` §13 | — |
| Deliverable 3 · §3.1–§3.3 | 4-way disambiguation, the 3-layer model, `V_score` | **RETAINED** → `SPEC-DOC-001` §10–§11 | — |
| Deliverable 3 · §3.4 | The verified-profile schema | **RETAINED** | — |
| Deliverable 4 · §4.1–§4.5 | Compa-ratio, compression analytics, MCDA, the priority framework | **REJECTED for Phase 1** — post-hire HRIS scope | ADR-004 (`FIND-PROD-01`) |
| Deliverable 5 · §5.1–§5.6 | Lifecycle, CTC, contract structuring, overtime divisors, settlement, dispute resolution | **PARTIALLY RETAINED** — the statutory content is retained and already superseded by `REMEDIATED` Module 1/6; the *operational settlement execution* is rejected | ADR-004 (`FIND-PROD-02`); `REMEDIATED` |
| Deliverable 6 · §6.1 | Library evaluation | **RETAINED**, but the `pgcrypto` row is rejected | ADR-003 |
| Deliverable 6 · §6.2 | Architecture integration (line 1027 `pgcrypto`, line 1028 MinIO) | **REJECTED** | ADR-002, ADR-003 |
| Deliverable 6 · §6.3 | Risk and scalability | **RETAINED** | — |
| Deliverable 7 · §7.1 | The P0–P3 priority matrix | **RETAINED as task granularity only.** The `pgcrypto` prerequisite (line 1094), the `Bisection Net-to-Gross` capability (line 1100), the `Redis, Celery/ARQ` prerequisite (line 1109) and the `MinIO WORM` milestone (line 1155) are rejected | ADR-002, ADR-003, `FIND-MATH-01`, ADR-005 |
| Deliverable 7 · §7.2 | The Month-1 / Month-2 / Quarter-2 schedule | **REJECTED as a schedule** — replaced by the approved 20-week roadmap. Retained only as a source of task granularity | `REMEDIATED` §7, ADR-004 |
| Deliverable 8 · §8.1 | The system architecture blueprint (lines 1209 `pgcrypto`, 1210 MinIO) | **REJECTED in those respects** | ADR-002, ADR-003 |
| Deliverable 8 · §8.2 | The database schema extensions (line 1265 `pgcrypto`, line 1242 MinIO URI) | **PARTIALLY RETAINED** — the table structures are harvested into `SPEC-DOC-001` §3.3; the encryption and storage columns are rejected | ADR-002, ADR-003 |
| Deliverable 8 · §8.3 | The REST API endpoint directory | **PARTIALLY RETAINED** — items 7, 11 (MCDA) are rejected; the rest are superseded by `REMEDIATED` §5 | ADR-004, `REMEDIATED` §5 |
| Deliverable 8 · §8.4 | The regulatory-intelligence framework | **RETAINED with a constraint** — the mandatory human sign-off gate and the absolute prohibition on unsupervised modification are retained and reinforced by `SPEC-STAT-001` | `SPEC-STAT-001` §7 |
| Deliverable 8 · §8.5 | Privacy, legal and data governance (line 1434 `pgcrypto`) | **RETAINED with a correction** — the retention periods and masking rules are retained; the `pgcrypto` sentence is rejected | ADR-003 |

### 2.2 Line-level rejected references in this file

| Line | Content | Rejected by |
| :--: | :--- | :--- |
| 82, 731, 1100, 1193 | The bisection net-to-gross solver | `FIND-MATH-01` → `REMEDIATED` Module 2 |
| 989–990 | MinIO with Object Lock, "PRIMARY SELECTION" | ADR-002 |
| 994, 1027, 1094, 1209, 1265, 1434 | `pgcrypto` for field encryption | ADR-003 |
| 1049, 1155 | MinIO WORM in the architecture and the milestone plan | ADR-002 |
| 1028, 1210, 1242 | The MinIO object store in the blueprint and the schema | ADR-002 |
| 1109 | Redis + Celery/ARQ as the P1 prerequisite | ADR-005 (proposed) |
| §8.3 items 7, 11 | `/compensation/prioritize-reviews`, the compa-ratio and compression endpoints | ADR-004 |

### 2.3 Standing recommendation

A reader who opens this file without reading this table will implement AGPLv3 object storage, in-database key exposure and a 50-iteration solver. **A supersession banner should be added to the file header**, listing the items in §2.2. This workstream could not make that edit: the authorised write scope was `docs/` only. It is raised as a documentation-hygiene action for the project owner.

---

## 3. Supersession map — the DOCX research and audit material

The three `.docx` files are **binary and were not modified**. Their status is therefore declared here.

| File | Status | Retained content | Superseded content |
| :--- | :--- | :--- | :--- |
| `گزارش جامع پژوهشی.docx` (PH-RES-1405-01, 2026-11-13) | **Baseline research — historical** | §2 the six-tier compensation data taxonomy; §5 the Iranian labour-law reference tables and statutory formulae; §8 the preliminary SRS; §9 the relational schema and the deterministic-vs-AI separation; §10 the update-frequency matrix; §11.1 the MoSCoW prioritisation (as task granularity only); §12.1 the data gaps; §12.2 the legal uncertainties; §12.3 the three open Product Owner decisions | §5's 1404 wage tables as the **active** baseline; §11's **7-day** schedule; §9's `pgcrypto` usage; §12.2's `wd/7.33` divisor, which is superseded by the exact `22/3` rational divisor (`1.docx` Defect 3) |
| `Technical Investigation of Related Software Projects.docx` | **Technology survey — historical, incorporated** | Deliverable 1 (the project directory and taxonomy); Deliverable 3 (the comparison matrix); Deliverable 4 (the algorithm and statutory reference); Deliverable 6 (the reusable components); Deliverable 8 (the prioritised technical roadmap) | The "500+ job families" claim, which the independent audit found inconsistent with the 60-occupation MVP (`1.docx`) |
| `1.docx` | **Independent audit — historical, and the correction register** | Defect 1 (the 1404/1405 year mismatch) **as a finding**; Defect 2 (the SSO ceiling in the Art. 137 base); Defect 3 (the 176 vs 220 divisor); Defect 4 (Eydi taxation and the Sanavat base); Defect 5 (the Jobinja ToS violation); the 1405 ingestion procedure; the four-eyes verification requirement | Defect 2's characterisation of the Art. 137 deduction as **a tax cap**, which `FIND-LEG-02` replaced with a two-policy toggle; the inference that 5,541,850 IRR/day was a "digit transposition" (`SPEC-STAT-001` §3.6) |

### 3.1 How the DOCX material is cited

Cite it **by document and section**, always with a marker that it is historical:

> `گزارش جامع پژوهشی.docx` §5 (historical — statutory reference material)

Never cite it as a current specification and never copy a figure from it without re-deriving it against the active rule set.

---

## 4. Rules for using historical documents

| Rule | Detail |
| :--- | :--- |
| 1 | A historical document is **never** a current implementation instruction |
| 2 | A figure from a historical document is re-derived against the active rule set before use |
| 3 | A statutory value from a historical document is **never** transcribed into a rule set without the §4 four-eyes procedure in `SPEC-STAT-001` |
| 4 | A rejected recommendation in a historical document is **never** revived without a new ADR |
| 5 | When a historical document contradicts a current one, the current one wins and the historical one is corrected (or, if it cannot be edited, listed in §2 with its superseding authority) |
| 6 | Historical documents are **never deleted or overwritten**. They are retained for the audit trail |

---

## 5. Change-control policy

### 5.1 Classification

| Class | Definition | Change rule |
| :--- | :--- | :--- |
| **Binding** | An accepted ADR, the authoritative specification | The recorded approver only; a change needs a superseding ADR or an explicitly approved spec amendment |
| **Controlling** | This package (`docs/`) | The named owner; cross-references updated in the same change |
| **Reference** | Historical research, surveys, audits | Never edited; superseded content is declared in §2 and §3 |
| **Immutable artefact** | The statutory seed files | **Never modified.** The 1404 file is hash-pinned in CI; the 1405 file is a controlled placeholder |

### 5.2 Change procedure

1. The author proposes the change with the affected documents identified.
2. The owner reviews, and the approver signs where the change affects a binding document.
3. The change is applied, and every cross-reference is updated in the same commit.
4. `docs/DOCUMENTATION_INDEX.md` and `docs/ADR_INDEX.md` are updated within 1 working day.
5. The change is recorded in the changelog below.

### 5.3 Review cadence

| Cadence | Review |
| :--- | :--- |
| On every phase gate | The package is reviewed against the gate evidence |
| Quarterly | The specification is re-read against the implemented behaviour; drift is logged |
| Annually | The package is re-issued with a new version, alongside the statutory rule-set re-verification |

### 5.4 Changelog

| Version | Date | Change | Author |
| :--: | :--: | :-- | :-- |
| 1.5 | 2026-11-15 | ADR-008 (Accepted, Project Owner): product scope refocused on the statutory payroll calculation engine; ADR-004's module list and directives 2–3 superseded (text retained); DEC-002a resolved, DEC-007/008 rejected out of scope; DEC-K recorded in the owner queue; WBS Phase 1 rows annotated and §14.9 added; AGENTS.md §1 and README orientation aligned. Evidence: BOOTSTRAP_CHANGELOG §23. | Codex implementation owner |
| 1.4 | 2026-11-14 | Owner-authorized documentation maintenance: task-focused reading in §0; current orientation and environment/agent guidance reconciled; historical evidence preserved. No code, roadmap, seed, ADR or WBS-status change. Evidence: BOOTSTRAP_CHANGELOG §13. | Codex documentation owner |
| 1.3 | 2026-11-14 | Add P0-T03 dev contract in DEPLOYMENT §4.1.1 and infra/postgres runbook/verifier; current Docker/image blocker and WBS state recorded. Local checks only, no DB runtime acceptance. Evidence: BOOTSTRAP_CHANGELOG §12. | Codex implementation owner |
| 1.2 | 2026-11-14 | Register accepted ADR-006; AUTH §8.5 defines P0-T06's field-encryption contract; primitive review-ready with 110 passing tests. No prior accepted ADR text rewritten. Evidence: BOOTSTRAP_CHANGELOG §11. | Codex implementation owner |
| 1.1 | 2026-11-14 | Current scaffold/Git/status corrected; false async attribution corrected while ADR-005 remains proposed; owner review package added to existing queue. Exact changes/results in `BOOTSTRAP_CHANGELOG.md` §10. | Codex remediation owner |
| 1.0 | 2026-11-14 | The documentation package established. `RESEARCH_GAP_ANALYSIS_AND_ADVANCED_SPECIFICATION.md` and the three `.docx` files classified with section-level dispositions. ADR-005 drafted as `PROPOSED`. | Documentation Engineering |

---

## 6. Known documentation gaps

These are gaps in the **package**, not in the implementation. Each is a task or a decision.

| # | Gap | Resolution route |
| :--: | :--- | :--- |
| 1 | The supersession banner on `RESEARCH_GAP_ANALYSIS_AND_ADVANCED_SPECIFICATION.md` could not be corrected (write scope was `docs/` only) | Owner action — apply §2.2 to the file header |
| 2 | The three `.docx` files cannot carry a banner | Owner action — declare their status in the README or the package index |
| 3 | `REMEDIATED` §5.1's defective worked example is still published in the source specification | `P1-T20` |
| 4 | `REMEDIATED` §3.1 specifies `BackgroundTasks`; durability and CPU isolation remain undecided | ADR-005 review and decision; no queue implementation before acceptance |
| 5 | `REMEDIATED` §3 still says "JWT" without specifying the revocation model | DEC-004 is resolved by ADR-006; an approved source-specification wording amendment remains separate work |
| 6 | `REMEDIATED` §4.1 still declares `char` without a length and omits the identity entities | `P0-T12` and `P0-T05` (migrations), then a spec amendment |
| 7 | 1405 is transcribed but unverified and inactive; primary evidence and activation conditions remain outstanding | `P1-T02`, `P1-T03`; no activation by this maintenance |
| 8 | Root `README.md` and `AGENTS.md` now exist | Bootstrap; factual status corrected in Holy Bible v1.0.1 |
| 9 | `.gitignore`, `.editorconfig`, `.gitattributes` and proprietary `LICENSE` now exist | Bootstrap; CI remains outstanding in `P0-T01` |


## 2026-11-15 — DEC-012 resolution

[ADR-007](adr/ADR-007-statutory-global-access-and-deferred-identity.md) is Accepted by the Project Owner: T-2 global FORCE-RLS statutory records, restricted database roles and F-1 deferred identity FKs with write gate. [Contract revision 3](specs/STATUTORY_DATABASE_CONTRACT.md) governs P0-T04. No existing ADR or roadmap changed.
