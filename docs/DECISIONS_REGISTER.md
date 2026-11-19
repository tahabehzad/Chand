# Project Decisions & Blockers Register

- **Document ID:** `REG-DEC-001`
- **Status:** Living register. Every entry is **open** unless an explicit approval is recorded.
- **Owner:** Chief Software Architect (register), with the approver named per entry
- **Date:** 2026-11-14 (23 Aban 1405 SH)
- **Related:** [`docs/EXECUTION_PLAN.md`](EXECUTION_PLAN.md) §14 · [`docs/IMPLEMENTATION_READINESS.md`](IMPLEMENTATION_READINESS.md) · [`docs/specs/STATUTORY_INGESTION.md`](specs/STATUTORY_INGESTION.md)

> **Standing rule.** A recommendation in this register is **not** a decision. No task blocked by an open entry may be marked `APPROVED` or `COMPLETED`, and no recommendation may be implemented unilaterally on the grounds that it is "obvious". Where a task must proceed before the decision lands, the assumption must be recorded in the task's *Blocking issues* field and reviewed at the phase gate.

**Status vocabulary:** `OPEN` · `OPEN — BLOCKING` · `OPEN — NON-BLOCKING` · `RESOLVED` · `REJECTED`

---

## DEC-001 — 1405 SH Statutory Baseline Verification

| Field | Value |
| :--- | :--- |
| **Status** | `OPEN — BLOCKING` |
| **Question** | When may the 1405 SH rule set be activated as the active statutory baseline, and what is the interim position while it is pending? |
| **Responsible role** | Labor Law Counsel + Certified Tax Accountant (verification); Payroll Engineer (transcription) |
| **Required approver** | Chief Technology Officer **and** Legal Counsel (joint) |
| **Blocking tasks** | `P1-T02`, `P1-T03`, `P1-T15`, `P1-T19`, `P1-T20`, `P1-T22` |

**Current evidence**

- `backend/data/seeds/statutory_rules_1405.yaml` ships **all values `null`** with `is_verified_and_active: false`.
- `REMEDIATED_TECHNICAL_SPECIFICATION_V2.md` declares the **active** baseline as 1405 SH, and its §5.1 example is labelled `1405.1-VERIFIED` while in fact using **1404** parameters.
- Independent research during this workstream (2026-11-14) established the 1405 values from the High Council of Labor wage circular (session 1404/12/24), Council of Ministers Resolution No. 9234 (1405/02/15), the SSO insurance-base circular 1405, and the Budget Law 1405. Full transcription and provenance: `docs/specs/STATUTORY_INGESTION.md` §3.
- **No L1 primary PDF was retrievable** — `mcls.gov.ir` and `intamedia.ir` returned transport errors, `tamin.ir` returned HTTP 403.
- `1.docx` line 470: *"Launching in Aban 1405 with 1404 rates invalidates live hiring recommendations."*

**Available options**

| Option | Description |
| :--- | :--- |
| **A** | Activate the transcribed 1405 values immediately, on secondary-source evidence |
| **B** | Obtain the primary PDFs, complete four-eyes verification, activate 1405 |
| **C** | Run on the verified **1404** set in the interim, label every output `1404.1`, and disclose the statutory year on every offer |
| **D** | Ship with no statutory engine at all |

**Recommendation: B, with C as the interim state.**

Rationale: Option A is not defensible — no primary source has been sighted, and the open items O1–O5 in `SPEC-STAT-001` §3.5 (the SSO follow-up circular for the housing-allowance increase, the exact tax band edges, the child-allowance legal citation, the budget-law citation string, and the SSO circular date) remain unresolved. Option C is legally conservative and transparent: it does not mislabel a 1404 computation as 1405, which is precisely the failure mode that produces unlawful contracts.

**Risks**

| Risk | Likelihood | Mitigation |
| :--- | :--- | :--- |
| Activation on unverified values produces unlawful contracts and SSO exposure | Medium | Four-eyes gate; fail-closed loader; the activation gate in `SPEC-STAT-001` §7 |
| Primary sources remain unreachable from the engineering environment | High | Verification performed by the Legal Counsel, who has access to the official channels; the engineering team transcribes from the archived artefact |
| Interim 1404 operation is later misrepresented as 1405 | Medium | `rule_set_status` and `statutory_version` are separate machine-checked fields (`SPEC-STAT-001` §5.3); contract test asserts they match the database |
| The housing-allowance increase triggers an SSO follow-up circular that changes the insurance base (O1) | Medium | Resolve O1 before activation; re-verify the `mozd_e_mabna` treatment |

---

## DEC-002 — Corrected Worked API Example and Golden Vector Corpus

| Field | Value |
| :--- | :--- |
| **Status** | `OPEN — BLOCKING` |
| **Question** | What is the authoritative §5.1 worked example, and who certifies the golden vector corpus? |
| **Responsible role** | Payroll Engineer (recompute); Certified Tax Accountant (certify) |
| **Required approver** | CTO + Certified Tax Accountant |
| **Blocking tasks** | `P1-T15`, `P1-T20`, `P1-T22` |

**Current evidence**

An independent recomputation during this workstream (`docs/specs/STATUTORY_INGESTION.md` and §3 of this package) reproduced every line of the published §5.1 example and found **two defects**:

1. **Income tax.** The published `income_tax_rial` of 37,920,612 is arithmetically identical to the *entire* post-exemption taxable base (277,920,611.60 − 240,000,000). The progressive slab-2 rate of 10 % yields **3,792,061**. The published figure therefore behaves as a 100 % rate. The accompanying label `"Slab 2 (10%) & Slab 3 (15%)"` is also wrong — a base of 277,920,612 never reaches slab 3.
2. **Severance accrual.** The published `monthly_sanavat_accrual_rial` of 28,487,510 is `gross ÷ 12`. The statutory base is *Mozd-e Saabet* = gross − welfare allowances = 295,459,152, giving **24,621,596** — an overstatement of **3,865,914 Rial per month / 46,390,968 Rial per year** in employer cost.

Consequence: the published gross of 341,850,120 produces a net of 280,000,000 only through the defective tax figure. Under **every** candidate reading of the tax model, the net from that gross is 306.7 M – 314.8 M. The example is internally consistent only with itself.

**Available options**

| Option | Description |
| :--- | :--- |
| **A** | Leave the published example unchanged and let the implementation reveal the discrepancy |
| **B** | Replace §5.1 with a recomputed, fully-intermediate example and publish the defect analysis |
| **C** | Remove the worked example entirely |

**Recommendation: B.**

Option A would propagate a 100 % effective tax rate into the golden corpus. Option C loses the only concrete contract example the API has. The corrected example must show **every intermediate value** and must state its tax-model assumptions explicitly, because the taxable-base definition (which allowances are exempt under each posture) is itself an unresolved sub-question (DEC-002a).

**Risks**

| Risk | Mitigation |
| :--- | :--- |
| The certified corpus is never obtained, so the Phase 1 gate can never pass | `P1-T15` is the longest-lead external item; it must start in **Week 1**, not Week 5 |
| A synthetic corpus is substituted for the certified one | The corpus schema records `approved_by`; a corpus without a certified approver is rejected by the CI gate |
| Golden files are silently re-baselined to make the build green | A golden-file change requires a reviewed PR stating why the engine's behaviour changed; the financial-diff gate blocks otherwise |

---

## DEC-002a — Taxable-Base Definition (Which Allowances Are Exempt)

> **Resolution — 2026-11-15, Project Owner (ADR-008):** Option **B** — posture-dependent. Welfare allowances (housing, grocery, marriage, child) are **taxable under `conservative_inta`** and **exempt under `court_precedent`**. Both postures are always computed and reported side by side, and the **primary response posture is `conservative_inta`**. This resolves the arithmetic axis for `P1-T05`/`P1-T09`/`P1-T14` within the ADR-008 minimal scope; the original analysis below is retained as history.

| Field | Value |
| :--- | :--- |
| **Status** | `RESOLVED` — owner approval 2026-11-15, ADR-008 (Option B; primary posture `conservative_inta`) |
| **Question** | Under each tax posture, are the welfare allowances (housing, grocery, marriage, child) taxable, exempt, or posture-dependent? |
| **Responsible role** | Certified Tax Accountant |
| **Required approver** | Legal Counsel + Certified Tax Accountant |
| **Blocking tasks** | `P1-T05`, `P1-T13`, `P1-T20` (within ADR-008 scope: `P1-T05`, `P1-T09`, `P1-T14`; `P1-T13`/`P1-T20` are out of product scope) |

**Current evidence**

- `FIND-LEG-02` establishes that the Article 137 deduction of the employee SSO contribution is the axis of dispute (conservative INTA: 2/7; court precedent: full 7 %), confirmed by an INTA circular reference found during this workstream ("کسر دو هفتم حق بیمه‌ی سهم کارگر از مبنای مالیات").
- The welfare-allowance question is **separate** and is described in the historical Persian research as a live divergence between the INTA practice (treats مسکن، بن و تاهل as taxable, sometimes at a flat 10 %) and the *Divan-e Edalat* rulings (exempt). `REMEDIATED` Module 1 does **not** specify it.
- Consequently, the corrected gross for a given net depends on this answer: for net = 280,000,000 under 1405 the gross is 301,075,269 under all four combinations — but the **taxable base** and therefore the *reported* taxable income differ, and at higher nets the four readings diverge materially.

**Available options**

| Option | Description |
| :--- | :--- |
| **A** | Welfare allowances always taxable; only the Art. 137 SSO deduction varies |
| **B** | Welfare allowances exempt under the court-precedent posture, taxable under conservative INTA |
| **C** | Expose welfare-allowance treatment as a third independent toggle |

**Recommendation: B, with C as a possible Phase 2 refinement.**

B reflects the actual structure of the dispute and lets the platform present the genuinely dual-scenario view the product promises. The tax posture toggle then has two independent axes — the Art. 137 deduction and welfare-allowance treatment — which must be surfaced together in the API response so the user sees which combination produced which number.

**Risks:** a wrong default changes every tax figure. Mitigation: the engine must emit both scenarios by default (`REMEDIATED` Module 2 "Dual-Scenario Reporting") and the posture must be recorded in the simulation snapshot.

---

## DEC-003 — Asynchronous Execution Strategy

| Field | Value |
| :--- | :--- |
| **Status** | `OPEN — BLOCKING` |
| **Question** | Celery + Redis, FastAPI `BackgroundTasks`, or a PostgreSQL-backed job queue? |
| **Responsible role** | CTO (decision owner); DevOps Lead and Lead Backend Engineer (consulted) |
| **Required approver** | CTO |
| **Blocking tasks** | `P2-T04`, `P2-T05`, `P2-T06`, `P2-T07`, `P2-T08`, `P2-T09` |

**Current evidence**

- `REMEDIATED` §3.1 and `.agents/skills/software-architecture/SKILL.md` both specify FastAPI `BackgroundTasks`. The specification mentions Celery/Redis while explaining the complexity it avoids, not as a mandate. The unresolved issue is durability/retry and CPU isolation versus in-process execution. **No alternative is accepted by ADR-005; `P2-T04` remains blocked.**
- Comparative analysis: `docs/adr/ADR-005-async-execution-strategy.md`.

**Available options**

| Option | Summary |
| :--- | :--- |
| **A** | Celery + Redis (historical alternative, not mandated by current `REMEDIATED` §3.1) |
| **B** | FastAPI `BackgroundTasks` (as in the skill corpus) |
| **C** | PostgreSQL-backed queue with `FOR UPDATE SKIP LOCKED` |
| **D** | Hybrid A + B |

**Recommendation: C — PostgreSQL-backed job queue.**

It is the only option that satisfies all nine constraints simultaneously: Windows parity, air-gapped operability, no new mandatory on-site service, durability across restart (via the PostgreSQL WAL), explicit and auditable retry semantics, CPU isolation from the fast path, and SQL-observable job state that joins directly with the hash-chained audit ledger. A and B each fail three or more constraints. D adds a distinction without adding a capability.

**ADR-005 is drafted in `PROPOSED` state and awaits CTO approval.** `P2-T04` remains `BLOCKED` until then.

**Risks**

| Risk | Mitigation |
| :--- | :--- |
| Building the lease/heartbeat/reaper protocol is under-estimated | 8 engineer-days budgeted in `P2-T04`; the `JobQueue` interface keeps the pipeline swappable if a later ADR reverses the decision |
| `SKIP LOCKED` polling load degrades the fast path | A dedicated connection pool with a small `max_connections`, disjoint from the request pool; polling interval tuned and monitored |
| Two engineers build the pipeline against different assumptions | The `JobQueue` interface is defined and the worker consumes only that interface (`P2-T04` precedes `P2-T05`) |

---

## DEC-004 — Authentication and Authorization Model

**Resolution — 2026-11-14, Project Owner:** approved session (b), identity provider (c), MFA (b) and the existing seven-role set. Accepted ADR-006 is the rank-1 record; no named CISO/CTO signature is claimed. Session timing/remember-me and key-management details outside that exact approval remain subject to their contracts.

| Field | Value |
| :--- | :--- |
| **Status** | `RESOLVED` — owner approval, ADR-006 |
| **Question** | Server-side opaque sessions or stateless JWTs? Which principals require MFA? Which roles exist? |
| **Responsible role** | Security Architect |
| **Required approver** | CISO + CTO |
| **Blocking tasks** | `P0-T05`, `P0-T18`, `P0-T20` |

**Current evidence**

- `REMEDIATED` §3 mandates a `JWT & Multi-Tenant Middleware`; §4.1 defines **no** user, role, permission or membership entity, leaving `AUDIT_LOGS.actor_id` dangling.
- ADR-003 requires per-tenant DEKs and a blind-index pepper; ADR-002 assumes an offline administrative vault.
- `REMEDIATED` §3 mentions "HTTP-only Secure SameSite cookies" only in ADR-001's trade-off note.
- Proposed model: `docs/specs/AUTH.md`.

**Available options**

| Axis | Options |
| :--- | :--- |
| Session | (a) Stateless JWT · (b) Server-side opaque sessions with rotation · (c) Hybrid (short-lived access + revocable server-side session) |
| Identity provider | (a) First-party credentials (Argon2id) · (b) External OIDC/Keycloak/LDAP · (c) First-party now, OIDC federation later |
| MFA | (a) Optional · (b) Mandatory for privileged roles |

**Recommendation: (b) + (c) + (b).**

Server-side opaque sessions, because a stateless JWT cannot be revoked before expiry — unacceptable for encrypted National IDs and salary data accessed by temporary staff and external counsel. First-party credentials now with a designed path to OIDC later, because a mandatory Keycloak instance is the same on-site burden that makes Redis the wrong choice. MFA mandatory for `OWNER`, `ADMIN`, `LEGAL_REVIEWER` and `SUPER_ADMIN`.

**Risks**

| Risk | Mitigation |
| :--- | :--- |
| "JWT" in §3 is read as a hard mandate on stateless tokens | The wording is clarified in `SPEC-AUTH-001` §1.2; the spec text should be amended to "bearer-token middleware" when DEC-004 is decided |
| Credential storage expands the attack surface | Isolated schema, its own encryption key, its own backup policy; OIDC-federable without business-data migration |
| The session table becomes a hot row | Partitioned index on `(user_id) WHERE revoked_at IS NULL`; a short idle timeout keeps the live set small |

---

## DEC-004a — MFA Mandatory Role Set

**Resolution — 2026-11-14, Project Owner:** option (b), mandatory MFA for OWNER/ADMIN/LEGAL_REVIEWER/SUPER_ADMIN, hashed recovery codes and two-person administrative recovery. Recorded in accepted ADR-006; no named human CISO sign-off is asserted.

| Field | Value |
| :--- | :--- |
| **Status** | `RESOLVED` — owner approval, ADR-006 |
| **Question** | Which roles must complete a second factor before an interactive session is issued? |
| **Responsible role** | Security Architect |
| **Required approver** | CISO |
| **Blocking tasks** | `P0-T18` |

**Current evidence.** `REMEDIATED` §7 and §3 mandate a multi-tenant middleware but specify no authentication mechanism at all; no MFA requirement exists anywhere in the corpus. The privileged roles in the proposed matrix are `OWNER`, `ADMIN`, `LEGAL_REVIEWER` and `SUPER_ADMIN`; `LEGAL_REVIEWER` in particular can promote a document's verification status and read the audit chain.

**Available options:** (a) MFA optional for all · (b) mandatory for `OWNER`, `ADMIN`, `LEGAL_REVIEWER`, `SUPER_ADMIN` · (c) mandatory for every role.

**Recommendation: (b).**

Option (c) adds friction to the high-volume `HR_MANAGER` and `ANALYST` paths for a modest marginal gain, since those roles already cannot reach the highest-impact operations. Option (b) concentrates the second factor exactly where a compromise is most damaging.

**Risks:** MFA enrolment can be used to lock an organisation out of its own account → recovery codes, hashed, plus a two-person admin reset path. TOTP secrets must be encrypted under the platform KEK and must never be exported in plaintext (CR-13).

---

## DEC-004b — Hash-Chain Scope for High-Frequency Access Events

**Resolution — 2026-11-14, Project Owner:** option (b), chain mutations/calculations/evidentiary events; all reads in a separate append-only, independently tamper-evident access log. Signed-digest cadence/custody/anchor must be specified before implementation. ADR-006 records acceptance; it does not claim that the access-log controls exist.

| Field | Value |
| :--- | :--- |
| **Status** | `RESOLVED` — owner approval, ADR-006 |
| **Question** | Must every read event be written into the hash-chained ledger, or may high-frequency access events go to a separate, non-chained access log? |
| **Responsible role** | Security Architect + Database Engineer |
| **Required approver** | CISO |
| **Blocking tasks** | `P0-T10` |

**Current evidence.** `REMEDIATED` Module 7 specifies hash chaining for "every calculation snapshot and parameter override". It is silent on read events. `AUDIT_LOGS` as drawn in §4.1 carries a `payload_snapshot` and a `bigint sequence_id`, implying high-volume use. `SPEC-AUTH-001` §7.2 proposes a split: the hash chain covers mutations and evidentiary events; a separate `ACCESS_LOG` covers reads.

**Available options:** (a) chain every event, including reads · (b) chain mutations and evidentiary events only; a separate access log for reads · (c) chain reads at a sampled rate.

**Recommendation: (b).**

Chaining every read makes the write cost proportional to traffic and creates a write-amplification bottleneck on the hot path, which conflicts with the < 20 ms fast-path budget. Option (c) weakens the audit trail in a way that is hard to defend in a dispute. Option (b) preserves the evidentiary guarantee that matters — the chain proves the integrity of every *record of change* — while reads remain individually queryable and retained.

**Risks:** an adversary could delete read events from the access log without breaking the chain → the access log needs its own tamper-evidence (a periodic signed digest over a window of rows) and the same append-only triggers.

---

## DEC-005 — Database Schema Corrections

**Resolution — 2026-11-14, Project Owner:** option A. Accepted ADR-006 formally supersedes ADR-003 directive 3's table target only, retaining the original ADR text. CHAR(64), candidate blind index, deferred employees and `actor_id → users` are approved. No migration or named human DBA/security signature is implied.

| Field | Value |
| :--- | :--- |
| **Status** | `RESOLVED` — owner approval, ADR-006 |
| **Question** | Confirm the ERD corrections: `CHAR` lengths, `EMPLOYEES` vs `CANDIDATES`, `AUDIT_LOGS.actor_id` foreign key |
| **Responsible role** | Database Engineer |
| **Required approver** | CTO + Database Administrator + Security Architect |
| **Blocking tasks** | `P0-T04`, `P0-T05`, `P0-T12`, `P0-T13` |

**Current evidence**

Three concrete defects in `REMEDIATED` §4.1:

1. **`char` without a length.** `AUDIT_LOGS.prev_hash`, `AUDIT_LOGS.current_hash` and `CANDIDATES.national_id_bindex` are declared `char`. PostgreSQL `CHAR` without a length **defaults to `CHAR(1)`** — a SHA-256 hash needs 64 hex characters. ADR-003 correctly specifies `CHAR(64)` for the blind index, contradicting the ERD.
2. **`EMPLOYEES` vs `CANDIDATES`.** ADR-003 directive 3 requires an index on `employees (tenant_id, national_id_bindex)`, but the ERD defines the blind index on `CANDIDATES` and gives `EMPLOYEES` no columns. Phase 1 is pre-hire only (ADR-004), so `CANDIDATES` is the entity that carries a National ID.
3. **`actor_id` has no referential target**, and there is no entity from which a human actor could be resolved — which makes the hash chain's `actor_id` unresolvable and the forensic trail unattributable.

**Available options**

| Option | Description |
| :--- | :--- |
| **A** | Correct the ERD: `CHAR(64)` hashes, `CANDIDATES` carries the blind index, `EMPLOYEES` deferred to Phase 2, `actor_id → users(id)` |
| **B** | Keep `EMPLOYEES` in Phase 1 as a post-hire placeholder |
| **C** | Add a separate `audit_actors` table |

**Recommendation: A.**

Option B adds an entity with no data and no use in Phase 1, and forces a premature decision about the post-hire data model. Option C duplicates `users` for no benefit.

**Risks**

| Risk | Mitigation |
| :--- | :--- |
| A `CHAR` without a length reaches production | A CI migration lint rejects `CHAR`/`VARCHAR` without an explicit length |
| Correcting ADR-003's index directive is treated as amending an accepted ADR | The correction preserves ADR-003's *intent* (blind-index `CANDIDATES` under a per-tenant B-Tree) and is recorded explicitly in `SPEC-AUTH-001` §2.2 and in this register — it is not silently applied |

---

## DEC-006 — Persian RTL / Jalali / PDF Implementation Choices

| Field | Value |
| :--- | :--- |
| **Status** | `OPEN — NON-BLOCKING` (decidable on engineering judgement; CTO confirms) |
| **Question** | Which Jalali library, which PDF pipeline, and which font subsetting strategy? |
| **Responsible role** | Lead Frontend Engineer |
| **Required approver** | CTO |
| **Blocking tasks** | `P3-T02`, `P3-T03`, `P3-T04`, `P3-T11` |

**Current evidence**

`ADR-001` directive 2 specifies "RTL support for Persian typography (Vazirmatn)" in one line. There is no localisation strategy, no Jalali policy, no numeral policy, and no PDF text-shaping requirement anywhere in the corpus. Full specification proposed: `docs/specs/FRONTEND_PERSIAN.md`.

**Available options**

| Axis | Options |
| :--- | :--- |
| Jalali library | `persiantools` · `jdatetime` · the jalaali algorithm vendored |
| PDF pipeline | WeasyPrint · headless Chromium · ReportLab + `arabic_reshaper` + `python-bidi` |
| Font | Full Vazirmatn · subset with a ZWNJ-aware test · subset + separate PDF font files |

**Recommendation:** `persiantools` (with `jdatetime` as a cross-check in tests) · **WeasyPrint preferred, headless Chromium as the alternative, ReportLab only as a fallback** · subset with a **ZWNJ-regression test** that renders a ZWNJ corpus and compares glyph counts.

The PDF choice is the one that carries real risk: omitting the shaping stage produces disconnected and/or reversed Persian text that no Latin-reading reviewer would notice. Shaping must be a separately tested stage.

**Risks**

| Risk | Mitigation |
| :--- | :--- |
| A font subset drops ZWNJ-contextual forms | Subset regression test with a ZWNJ corpus |
| A charting library renders its own Latin axis labels | Evaluate during `P3-T10` before adoption |
| WeasyPrint is unavailable on a Windows developer machine | The containerised pipeline is the canonical path; Windows developers use the container |

---

## DEC-007 — Market Data Ingestion and Licensing

> **Resolution — 2026-11-15, Project Owner (ADR-008):** **REJECTED — out of product scope.** The market-benchmarking module (M5, `P1-T17`, `P1-T18`) is outside the ADR-008 minimal product boundary; no ingestion or licensing path is approved or implemented. Any revival requires a new superseding ADR. The original analysis below is retained as history.

| Field | Value |
| :--- | :--- |
| **Status** | `REJECTED` — out of product scope, ADR-008 (2026-11-15) |
| **Question** | How is salary-benchmark reference data obtained and licensed? |
| **Responsible role** | Product Manager + Data Analyst |
| **Required approver** | Legal Counsel + Product Manager |
| **Blocking tasks** | `P1-T17`, `P1-T18`, `P2-T16` |

**Current evidence**

- `1.docx` Defect 5 records that one baseline report recommended live scraping of Jobinja via `sepehr071/jobinja-mcp` and `Hexanol777/Jobinja-Crawler`, while the companion report documented the **ToS prohibition** — an explicit contradiction, and a legal risk.
- `RESEARCH_GAP` §8.4 proposes a monitoring pipeline over `rrk.ir`, `mcls.gov.ir`, `intamedia.ir`, `tamin.ir`, `divan-edalat.ir` and commercial salary reports, with a **mandatory human sign-off gate** and an absolute prohibition on unsupervised rule modification.
- The Persian research §12.3 records the open Product Owner decision on market-data ingestion.

**Available options**

| Option | Description |
| :--- | :--- |
| **A** | Live scraping of public job boards |
| **B** | A curated, offline, manually-maintained seed dataset from licensed survey reports (JobVision, IranTalent, IranSalary, Quera) |
| **C** | A B2B give-to-get network: employers contribute anonymised compensation data |
| **D** | A negotiated official feed from job boards |
| **E** | An internal analyst team ingesting periodic published survey reports |

**Recommendation: B for Phase 1, with C evaluated for Phase 2, and E as the fallback.**

Option A is excluded on ToS grounds and on data quality: 70–80 % of specialist ads are "negotiable", so advertised pay is a budget floor, not paid salary (the Persian research's six-tier data taxonomy). Option C is attractive but conflicts with the privacy posture and is itself the subject of DEC-008.

**Risks**

| Risk | Mitigation |
| :--- | :--- |
| Legal exposure from ToS violation | Legal sign-off before any ingestion; the raw-scraping path is not implemented without it |
| Advertised pay treated as paid salary | The six-tier compensation taxonomy is enforced in the data model; each source carries a `bias_class` and a weight |
| Sparse coverage outside major cities | The Bayesian shrinkage toward provincial benchmarks and the legal floor, with an honestly low confidence score — never an imputation of a missing value |

---

## DEC-008 — Data-Flywheel Policy

> **Resolution — 2026-11-15, Project Owner (ADR-008):** **REJECTED — out of product scope.** The data flywheel depends on the benchmarking module that ADR-008 removed from the product boundary; no pooling of employer-contributed data is authorised. Any revival requires a new superseding ADR. The original analysis below is retained as history.

| Field | Value |
| :--- | :--- |
| **Status** | `REJECTED` — out of product scope, ADR-008 (2026-11-15) |
| **Question** | May employer-contributed candidate salary expectations and budgets be pooled into the benchmark corpus after hiring and full anonymisation? |
| **Responsible role** | Product Manager |
| **Required approver** | Legal Counsel + Product Manager |
| **Blocking tasks** | `P1-T17`, `P1-T18` |

**Current evidence.** Recorded verbatim in the Persian research §12.3 as an open Product Owner decision: *"every time an employer records a candidate's expected salary and their budget, first-hand data on current market expectations and employer budgets is created, and it must be specified whether the system may enter these figures into the `salary_observations` repository with a high credibility weight after final hiring confirmation and complete anonymisation."*

**Available options:** (a) never pool employer-contributed data · (b) pool after hiring confirmation and anonymisation, with a high credibility weight · (c) pool with employer opt-in and a published policy.

**Recommendation: (c).**

The contribution must be **opt-in per organisation**, the policy must be published in the UI at the point of contribution, and the consent must be a first-class record — not an implied consent buried in a terms-of-service link.

**Risks:** a flywheel that turns an employer-facing tool into a data-extraction vector would be a serious trust and legal failure. Mitigation: explicit opt-in, published policy, a `salary_observations` provenance field on every row, and the ability to exclude an organisation's data retroactively.

---

## DEC-009 — Tax-Optimization Advisory Boundary

| Field | Value |
| :--- | :--- |
| **Status** | `OPEN — NON-BLOCKING` (product and legal posture) |
| **Question** | Is the platform a neutral calculator, or may it advise on legal tax and insurance optimisation? |
| **Responsible role** | Product Manager + Legal Counsel |
| **Required approver** | Legal Counsel + CTO |
| **Blocking tasks** | `P1-T19`, `P3-T07` |

**Current evidence.** The Persian research §12.3 poses the question: *"whether the platform should merely be a neutral calculator, or is it permitted to advise the employer on how to manage and optimise the tax burden and total employment cost through legal capacity — for example by allocating part of the compensation package to tax-exempt non-cash benefits up to the statutory ceiling under Article 91 of the Direct Taxes Act, without reducing the candidate's net income."*

`REMEDIATED` §1.2 states that the platform *"Provides compliance evidentiary dossiers, **not legal counsel**"*.

**Available options:** (a) strict neutral calculator · (b) advisory, within an explicit legal boundary · (c) advisory without restriction.

**Recommendation: (a) for Phase 1 — a neutral calculator with full transparency.**

The platform already computes under two tax postures and shows the full breakdown; that is the "advantage" it offers. Making optimisation recommendations crosses from evidence into advice, which `REMEDIATED` §1.2 explicitly excludes and which creates a professional-liability exposure that no ADR in the corpus addresses. Option (b) may be reconsidered in Phase 2 with an Iranian tax attorney's opinion and a defined boundary.

**Risks:** (i) the dual-posture output could itself be read as implicit advice — mitigate with a prominent disclaimer that the output is a statutory computation, not advice, and that the employer remains responsible for its own tax position; (ii) a client integrating the API into its own advisory workflow — mitigate with API documentation stating the platform's role.

**Update (2026-11-16, ADR-009).** The compensation advisory module now proposes a salary **range** from a manager-entered profile. That is a recommendation, so the boundary question sharpens rather than closes. ADR-009 records the bounded reading actually implemented: the module is a neutral, published heuristic (`advisory: true`, `statutory: false`, weights echoed), the manager decides, the band comes from the manager, the statutory figures are the engine's, and **no tax or insurance optimisation is suggested**. This entry therefore stays `OPEN — NON-BLOCKING`: option (a) is implemented for the calculation surface, and any move to option (b) still needs an Iranian tax attorney's opinion and a defined advisory boundary.

---

## DEC-010 — Deployment Topology

| Field | Value |
| :--- | :--- |
| **Status** | `OPEN — BLOCKING` (for the Phase 4 pilot) |
| **Question** | What is the supported production topology, and what must the air-gapped installation path guarantee? |
| **Responsible role** | DevOps Lead |
| **Required approver** | CTO + DevOps Lead |
| **Blocking tasks** | `P0-T17`, `P2-T03`, `P4-T09`, `P4-T10` |

**Current evidence**

- ADR-001 names air-gapped and private-cloud Iranian enterprise intranets as the driving constraint for a static SPA with no Node.js runtime.
- `REMEDIATED` §3 adds Traefik, PgBouncer, Ceph, Celery and Redis to the topology.
- `ADR-002` selects Ceph/S3 `GOVERNANCE` with a 3650-day retention and an offline emergency key.
- Proposed topology and procedures: `docs/specs/DEPLOYMENT.md`.

**Available options**

| Axis | Options |
| :--- | :--- |
| Orchestration | Docker Compose on a single host · Docker Compose across 2–3 hosts · Kubernetes |
| Object storage | Ceph RADOS GW · a domestic managed S3 (ArvanCloud, Cloudware, MobinNet) · a managed international S3 |
| KMS | HashiCorp Vault · a local encrypted master config with an Argon2id-derived KEK |
| Proxy | Traefik · Nginx |

**Recommendation:** Docker Compose on one or a few hosts, with Ceph RADOS GW (or a domestic managed S3 where the client prefers it) · **Vault where the client already runs it, otherwise the local encrypted master config** · Nginx (simpler for an air-gapped client with no container platform).

**Not** Kubernetes: the target estate is a modest enterprise host and the operational burden is not justified.

**Risks**

| Risk | Mitigation |
| :--- | :--- |
| The local-KEK fallback path is untested in production because development uses Vault | The development stack must exercise the fallback path, or it is untested (`DEPLOYMENT.md` §2.5) |
| The air-gapped image mirror is incomplete at pilot time | A pre-pilot mirroring checklist (`DEPLOYMENT.md` §12) |
| Clock skew breaks the job lease mechanism and the audit timestamps | NTP is a mandatory pilot item; clock skew > 60 s is an alert |

---

## DEC-011 — Document Intelligence Acceptance Criteria

| Field | Value |
| :--- | :--- |
| **Status** | `OPEN — BLOCKING` |
| **Question** | What precisely constitutes acceptance for Module 3, given that the underlying OCR accuracy claim is unverified? |
| **Responsible role** | Document Forensics Engineer + QA Lead |
| **Required approver** | Product Manager + CTO |
| **Blocking tasks** | `P2-T05`, `P2-T16`, `P2-T17`, `P2-T18` |

**Current evidence**

- `REMEDIATED` §7 Phase 2 gate: *"Successful parsing of 500 authentic Social Security slips with > 95% field extraction accuracy."*
- `PHASE_1_RED_TEAM_AUDIT.md` List 3 item 1: the "98 %+ OCR accuracy" claim is **[UNVERIFIED — Requires Enterprise Pilot Dataset]**.
- The 500-slip authentic corpus **does not exist**; acquisition requires employer consent and a redaction pipeline.

**Available options**

| Option | Description |
| :--- | :--- |
| **A** | Accept on a synthetic corpus |
| **B** | Accept on the 500-slip authentic corpus, with per-field metrics |
| **C** | Accept on a smaller authentic corpus with a stated confidence interval |

**Recommendation: B, with C as a fallback if the corpus cannot be assembled at scale.**

Option A is not acceptable: synthetic documents do not exercise the failure modes that matter (wrinkles, phone-camera capture, scan artefacts) and would produce a meaningless gate.

**Risks**

| Risk | Mitigation |
| :--- | :--- |
| The corpus cannot be assembled in time, so Phase 2 slips | Acquisition starts in Week 1 alongside the engineering work; the corpus task is long-lead |
| The metric is gamed by counting easy fields | Per-field thresholds (≥ 90 % each) in addition to the aggregate |
| The gate is met on a corpus biased toward high-quality scans | The corpus composition must be recorded and reported with the result |

---

## DEC-011a — Shahkar Access Route

| Field | Value |
| :--- | :--- |
| **Status** | `OPEN — BLOCKING` (sub-decision of DEC-011) |
| **Question** | Does the platform obtain Shahkar access through PGSB/SITAD directly, or through a licensed third-party KYC aggregator? |
| **Responsible role** | Legal Counsel + Procurement |
| **Required approver** | Legal Counsel + Product Manager |
| **Blocking tasks** | `P2-T13`, `P2-T18` |

**Current evidence.** `RESEARCH_GAP` §2.2.2 establishes that Shahkar is available to legal entities via PGSB/SITAD (گذرگاه تعامل‌پذیری دولت / سیتاد) or through licensed third-party aggregators (UID, Vandar, Zibal, ApiEco), and that the API returns **only** a boolean. No commercial arrangement is in place. `FIND-ARCH-07` requires the interactive SMS OTP flow, which is a hard constraint regardless of the access route.

**Available options:** (a) direct PGSB/SITAD · (b) a licensed third-party aggregator · (c) both, with a failover.

**Recommendation: (a) as the primary, (b) as the documented fallback.**

Direct access removes an intermediary from a flow that handles National Codes and mobile numbers, which is the shortest path for legal review. The fallback matters because a third-party outage must not block the Phase 2 gate.

**Risks:** a single commercial counterparty creates a dependency with a long lead time; commercial terms may not be obtainable for a private Iranian entity → the aggregator fallback exists for exactly this reason, and the module sits behind an interface so the route is swappable. Any arrangement must include an explicit data-processing and locality clause.

---

## DEC-011b — Human Adjudication of Flagged Documents

| Field | Value |
| :--- | :--- |
| **Status** | `OPEN — NON-BLOCKING` (sub-decision of DEC-011) |
| **Question** | Which role adjudicates a document flagged `INVESTIGATION_REQUIRED`, and who may override a verification status? |
| **Responsible role** | Product Manager + Document Forensics Engineer |
| **Required approver** | Product Manager + CISO |
| **Blocking tasks** | `P2-T10`, `P2-T12` (implementation may proceed with the recommendation) |

**Current evidence.** `RESEARCH_GAP` §2.3 states that anomaly detection *"never issues a definitive verdict of fraud; it merely adjusts the status and routes the item for human adjudication"* — but does not name the role. The proposed role matrix in `SPEC-AUTH-001` §3 grants `document:verify_override` to `LEGAL_REVIEWER` and `SUPER_ADMIN` and explicitly denies it to `HR_MANAGER`.

**Available options:** (a) `HR_MANAGER` · (b) `LEGAL_REVIEWER` · (c) a two-person `LEGAL_REVIEWER` + `ADMIN` process for permanent rejections.

**Recommendation: (b) for status promotion; (c) for a permanent `REJECTED_FRAULENT` status.**

`HR_MANAGER` is the most frequent user of the platform and therefore the most exposed to social engineering; granting it the power to override a verification status would put a fraud-control decision in the hands of the party most likely to want a favourable answer. A permanent fraud rejection should never be a single-actor decision.

**Risks:** a `LEGAL_REVIEWER` bottleneck could slow the pipeline → the review queue must be measured, and the SLA must be agreed with each design partner during pilot onboarding.

---

## DEC-011c — Art. 86 720-Day Insured-Days Threshold

| Field | Value |
| :--- | :--- |
| **Status** | `OPEN — BLOCKING` (sub-decision of DEC-011) |
| **Question** | Is the 720-day (24-month) Social Security contribution threshold for the Art. 86 child allowance confirmed as a hard eligibility gate? |
| **Responsible role** | Labor Law Counsel |
| **Required approver** | Legal Counsel |
| **Blocking tasks** | `P2-T14`, `P2-T18` |

**Current evidence.** `RESEARCH_GAP` §3.1 states that the employer is *"legally prohibited"* from paying the child allowance unless the worker has accumulated at least 720 days of verified SSO contributions, and frames it as a statutory eligibility trigger. The figure is not sourced to a primary instrument in the corpus, and the corpus contains no Art. 86 determination.

**Available options:** (a) enforce 720 days as a hard gate · (b) warn but do not block · (c) make the threshold configurable and default to 720 days.

**Recommendation: (c), defaulting to 720 days.**

The rule as stated is legally significant — enforcing it wrongly causes either an unlawful denial or an unlawful payment — so it must be configurable pending confirmation, while the default reflects the best available reading. The configuration must be recorded in the rule set, not hard-coded, so that a verified determination can be applied without a code change.

**Risks:** if the threshold is wrong, the engine mis-states a statutory entitlement in either direction. Mitigation: a written SSO or Labour Counsel determination before `P2-T14` is finalised, and the simulated output must carry a provenance entry naming the legal source for the threshold.

---

## DEC-013 — Apply statutory allowance floors and the seniority base to net pay

| Field | Value |
| :--- | :--- |
| **Status** | `OPEN — NON-BLOCKING` for the delivered v1; **blocking** for any change that would apply the floors |
| **Question** | Must the gross-to-net calculation enforce the 1404 minimum wage, the housing/grocery/marriage/child allowance floors and the daily base-seniority increment, changing `net_rial` — or may they be published as reference-only? |
| **Responsible role** | Payroll Engineer (evidence); Certified Tax Accountant + Labour Counsel (legal meaning) |
| **Required approver** | Project Owner, with Labour Counsel and Certified Tax Accountant advice |
| **Blocking tasks** | None in the ADR-008 v1 scope (the engine publishes the values and does not apply them). Any future task that changes net pay is blocked until this entry is resolved. |

**Current evidence**

- The verified 1404 seed carries `monthly_housing_allowance_rial = 9,000,000`, `monthly_grocery_allowance_rial = 22,000,000`, `monthly_marriage_allowance_rial = 5,000,000`, `child_allowance_per_child_rial = 10,390,968` and `daily_seniority_base_rial = 94,000`.
- ADR-008 authorises the gross-to-net calculation only. It does not decide whether the employer's declared gross already satisfies the floors, whether an under-floor package is unlawful, or whether the seniority increment is a statutory entitlement for every worker.
- The engine therefore publishes `statutory_reference` with `applied_to_net = false`, the declared child allowance, a below-floor flag and the monthly seniority increment, and lists the floors as `reference_only` in `statutory_parameter_usage`.
- Holy Bible §2.3 distinguishes `مزد مبنا`, `مزد ثابت`, `حقوق`, `سنوات` and `پایه سنوات`; merging them without a legal ruling would violate AGENTS.md §10.

**Available options**

| Option | Description |
| :--- | :--- |
| **A** | Apply every floor and the seniority base to net; refuse or uplift an under-floor package |
| **B** | Keep them reference-only and disclose the comparison (current v1 behaviour) |
| **C** | Apply only the minimum-wage floor; leave allowances and seniority reference-only |

**Recommendation: B for the delivered v1**, with A or C considered only after a Labour Counsel/Tax Accountant ruling. The arithmetic is already published; the legal effect on a real contract is not established by the corpus, and inventing it would breach AGENTS.md §2 (unknown values stay unknown; no legal conclusion without a citation).

**Risks**

| Risk | Likelihood | Mitigation |
| :--- | :--- | :--- |
| A user treats the reference block as an entitlement and pays it | Medium | `applied_to_net=false` and `reference_only_reason` in the response; the UI labels the block as reference |
| An under-floor contract is processed without warning | Medium | `total_gross_below_minimum_wage` and `declared_child_allowance_below_floor` are published |
| Applying floors later changes historical net figures | Medium | Rule-set version, engine version and calculation hash are stored; historical simulations are never recomputed (invariant 6) |

## DEC-014 — Product scope for the requested "Batch 01" application modules (authentication, company management, accounting foundation, dashboard)

| Field | Value |
| :--- | :--- |
| **Status** | `OPEN — BLOCKING` for **Modules B–C only**; Modules **A (authentication)** and **D (dashboard)** are resolved for the manager prototype per ADR-010 (approved by the Project Owner, effective 2026-11-17). Does not block the engine, the security foundation or the documentation work |
| **Question** | Must the product boundary be re-expanded from the ADR-008 statutory payroll engine to a multi-tenant accounting application — authentication/RBAC, company and organisation management, chart of accounts and journal entries, and a data-backed dashboard — and if so, under which superseding ADR and schema? |
| **Responsible role** | Product Manager (scope); Security Architect (identity/session variant); Database Engineer (tenant schema) |
| **Required approver** | Project Owner, recorded as a superseding ADR under `AGENTS.md` §3 |
| **Blocking tasks** | Any implementation of those four modules. It does not block `P0-T07`, the engine, or documentation corrections |

**Current evidence**

- `AGENTS.md` §1 and ADR-008 (Accepted, 2026-11-15) fix the product boundary as the statutory payroll calculation engine: pure functions plus one minimal endpoint on the verified 1404 baseline, explicitly **"no frontend requirement"**. ADR-008 supersedes ADR-004's module list and implementation directives 2–3.
- The 2026-11-16 batch instruction asks for Modules A–D (authentication and authorization, company/organisation management, accounting foundation with chart of accounts and journal entries, dashboard with navigation). Those are the superseded ADR-004 platform scope plus an accounting module that **no ADR has ever authorised**; the corpus contains no chart-of-accounts, journal-entry or fiscal-period specification to build against.
- Implementing them would also encode decisions the register still holds open: the session variant and detailed session contract (`P0-T18`, DEC-004 resolved only for the opaque-session direction, not for timeouts/remember-me/recovery), the key hierarchy (`P0-T08`, DEC-004), and the RLS/tenant-context ordering (`P0-T09`, `P0-T05`). ADR-006/ADR-007 authorise the identity **schema**, not a running authentication feature.
- The existing frontend is a bounded demo (BOOTSTRAP_CHANGELOG §20) whose dashboard cards render synthetic fixture data. Wiring "summary cards backed by real API data" for accounting figures would publish financial numbers no engine computed, breaching AGENTS.md §2 invariants 4, 6 and 9.

**Available options**

| Option | Description |
| :--- | :--- |
| **A** | Keep the ADR-008 boundary; complete the in-scope foundation (`P0-T07`, `P0-T15`, engine review) and leave Modules A–D unbuilt |
| **B** | Expand scope formally: write the superseding ADR (boundary, roles/permissions, tenant schema, accounting model), then build A–D in dependency order with the open decisions recorded as assumptions |
| **C** | Build A–D as an explicitly labelled prototype outside the product boundary, with synthetic data and no completion claims |

**Partial update (2026-11-16).** The owner answered a different, narrower question: ADR-009 adds the **compensation advisory module** (manager-entered profile → band placement → statutory costing). That does **not** resolve this entry. Authentication/RBAC, company management, the accounting foundation and a data-backed dashboard all remain `NOT_STARTED` and blocked here.

**Resolution of Modules A and D (2026-11-17, ADR-010).** The Project Owner approved [ADR-010](adr/ADR-010-manager-mvp-product-scope.md) v2 **as written, prospectively, effective 2026-11-17**: the manager-only evaluation and compensation-advisory **prototype** — single manager sign-in (Argon2id, opaque session token) and the data-backed manager dashboard — is authorized as the current approved product direction, under a **preserved prototype boundary** (not production-ready; backend integration explicitly incomplete; loopback/dev-only; no production/pilot claim). `P0-T18` remains the completion gate for production-grade authentication; `P0-T10` the audit-hash-chain gate. **Modules B (company/organisation management beyond the one organisation bound at sign-in) and C (the accounting foundation) remain `OPEN — BLOCKING` in this entry** — no specification and no approved schema exists for them, and ADR-010 explicitly does not authorize them. PB-D03 (real criteria/weights), PB-D04 and PB-D05 remain `OPEN`. The original analysis above is retained unchanged.

**Recommendation: A until the owner records B or C as an ADR.** Option A is the only choice that neither contradicts an accepted ADR nor invents an accounting model. Option B is legitimate but is a product decision with legal and security consequences, and it needs a specification before code. Option C is acceptable only if every screen and endpoint is labelled a prototype.

**Risks**

| Risk | Likelihood | Mitigation |
| :--- | :--- | :--- |
| Modules are built piecemeal and the boundary erodes silently | High | This entry; ADR-008's out-of-scope list; the WBS annotations |
| An authentication feature ships ahead of `P0-T08`/`P0-T18` contracts | Medium | P0-T18 stays gated; the pepper registry stays an injected protocol with no production implementation |
| A dashboard publishes hypothetical financial figures as real | Medium | No accounting API exists; the demo remains labelled synthetic (§20) |

---

## Engine review ambiguity ledger (B-series)

**2026-11-17 — Night-work correction authorized and implemented:** [ADR-011](adr/ADR-011-night-work-supplement.md), Accepted on the owner's explicit instruction, supersedes ADR-008's night-factor application only: the additional non-shift night-work payment uses the loaded total multiplier minus one, giving 0.35 on the immutable 1404 seed. Engine `0.3.1-payroll-engine`, independent financial engineering review and numerical regression evidence are recorded in BOOTSTRAP_CHANGELOG §39. This resolves the implementation/decision conflict below prospectively; the historical observation is retained. No external legal certification, historic recomputation, rule-year activation or resolution of other B-series questions is implied.

**2026-11-17 — UI legal-source check, OPEN — BLOCKING for acceptance of night-work results:** the primary Labour Law text, Art. 58 ([reproduced instrument](https://shenasname.ir/wp-content/uploads/2025/02/قانون-کار-با-اصلاحات-بعدی.pdf), page 10), describes a 35% supplement for non-shift night work. `backend/app/engines/overtime.py` currently multiplies by the configured `night_shift_multiplier` (1.35) and adds that whole amount to contractual gross. This raises a potential duplicate ordinary-wage component when that wage is already in gross. The payroll skill/specification also prescribes 1.35. No formula, seed or accepted decision was changed during the UI task; the affected arithmetic is not certified. Owner / Labour Counsel / Payroll Engineering must resolve the interpretation and approve the required specification change, followed by independent monetary review and regression evidence. The form now discloses this limitation; zero-night-hour demo verification does not verify the affected path.

These are statutory/product ambiguities raised by the independent engine
review. None is a licence to invent a value: each records the assumption the
current implementation makes and the authority that must resolve it. The
numbering follows the review ledger; entries whose original text did not
survive in the repository are marked accordingly and are **not** treated as
decided.

| ID | Ambiguity | Current implementation / assumption | Status |
| :-- | :--- | :--- | :--- |
| B-1 | The Holy Bible Appendix A worked example mixes a full Art. 137 deduction with taxable welfare allowances — a posture ADR-008's binding cannot produce | Appendix A is used only for ladder arithmetic (A.4/A.5 tax figures); end-to-end vectors are not asserted | `OPEN` — Tax Accountant; DEC-002 |
| B-2 | Which Art. 137 reading has legal effect on a real payslip (the dual response publishes both, `conservative_inta` primary) | ADR-008/DEC-002a binding: both postures always computed, conservative primary | `OPEN` — Counsel; ADR-008 scope decision |
| B-3 | The SSO insurable base: total gross vs fixed wage (QB-04) | Total gross capped at `7 × daily minimum wage × days`; published as `insurable_base` with the conflict reference | `OPEN` — SSO/Counsel |
| B-4 | Whether overtime and night-shift premiums enter the Sanavat and Eydi bases | Excluded; `includes_overtime_premiums=false` is published in both blocks | `OPEN` — Labour Counsel |
| B-5 | The Eydi cap basis and whether the cap applies before or after tax | Cap = `max_annual_eydi_rial` (90 daily minimum wages); tax on the capped amount | `OPEN` — Tax Accountant |
| B-6 | Interaction between the annual Eydi tax exemption and the salary exemption | Eydi taxed progressively on the exempt excess through the same shifted ladder | `OPEN` — Tax Accountant |
| B-7 | Art. 71 leave-buyout daily wage: divisor and whether welfare allowances participate | `Mozd-e Saabet / 30`; divisor published as `daily_wage_divisor_days` | `OPEN` — Labour Counsel; implementation records 30 from the seed's documented 30-day convention |
| B-8 | Month-length convention for monthly statutory amounts (29/30/31 actual vs a fixed 30) | Monthly minimum/ceiling follow the actual month length; Art. 71 uses 30 | `OPEN` — Labour Counsel |
| B-9 | Precedence between the seed's `is_verified_and_active` flag and the loader's year gate | Seed status is read and published (`rule_set_status_source`); the loader still refuses any year outside `{1404}` | `RESOLVED — engineering` (fail-closed behaviour verified) |
| B-10 | Statutory parameters loaded but unused (allowance floors, child floor, seniority base, marriage allowance) | Published as `reference_only`; `applied_to_net=false`; see DEC-013 | `OPEN` — Project Owner; DEC-013 |
| B-11 | Refusal taxonomy: stable machine codes vs historical bare `ValueError`/`TypeError` | One `PayrollEngineError` hierarchy with stable codes; the API reads `code`; `ValueError` catch retained | `RESOLVED — engineering` (A-9/A-13) |

**No B-series item changes a statutory value or activates 1405.** B-1…B-8 and
B-10 require a human legal/tax ruling; B-9 and B-11 are engineering
resolutions and are recorded here for traceability only.

---

## Summary

### DEC-012 — Statutory provenance ownership and identity-FK ordering

**Current resolution:** Global FORCE-RLS tables, restricted DB reader/reviewer roles; deferred users FKs owned by P0-T05 with ON DELETE RESTRICT and all statutory writes blocked until enforcement. Owner explicitly accepted the concrete proposal; no human specialist signature is asserted. See ADR-007 and STATUTORY_DATABASE_CONTRACT revision 3. The original problem analysis below is retained as history.


**Status: RESOLVED — Project Owner, 2026-11-15, T-2 + F-1 (ADR-007).** Required approvers: CTO/DBA and Security Architect. Independent review of the draft `specs/STATUTORY_DATABASE_CONTRACT.md` found that declaring all five statutory tables global/no-RLS and deferring every user FK is not established by the omission of tenant columns in the draft ingestion schema. Holy Bible §5.3/§5.4 use different table-scope wording; users are linked to organizations through memberships (AUTH §2). This affects evidentiary attribution and isolation, not merely syntax.

Owner must confirm (1) which statutory/provenance/signature/change tables are global versus tenant-owned, and the approved DB access policy for global actor-linked evidence; (2) how user references are enforced despite P0-T04 preceding P0-T05, including migration ownership and deletion semantics. Deferred FKs and no-RLS are proposals, not accepted corrections under ADR-006. No migration implementation may proceed on those assumptions. Preserve full source evidence in BOOTSTRAP_CHANGELOG §17.4; the isolated draft contract is being corrected to BLOCKED. Other independent work may continue. This decision does not reopen or modify ADR-006's four accepted choices.

**Operational update (not a new architecture decision, 2026-11-15):** The previous P0-T03 HTTP 403 did not recur: official image pull/build and actual TLS/SCRAM/settings/pgAudit/privacy assertions PASS in §15; no new DB runtime check was performed in §19. P0-T03 is READY_FOR_REVIEW because P0-T01 CI remains incomplete. Historical root cause is unproven; no mirror, registry/proxy change or TLS relaxation was used. See BOOTSTRAP_CHANGELOG §15; §12 retains the prior failure. The census below includes DEC-012; no decision was resolved by the §19 milestone.

| ID | Title | Status | Blocking phase | Approver |
| :-- | :--- | :--- | :-- | :-- |
| DEC-001 | 1405 statutory baseline verification | OPEN — BLOCKING | Phase 1 | CTO + Legal Counsel |
| DEC-002 | Corrected worked example and golden corpus | OPEN — BLOCKING | Phase 1 | CTO + Tax Accountant |
| DEC-002a | Taxable-base definition | RESOLVED — ADR-008 | Phase 1 | Project Owner, ADR-008 |
| DEC-003 | Async execution strategy | OPEN — BLOCKING | Phase 2 | CTO |
| DEC-004 | Authentication and authorization model | RESOLVED | Phase 0 | Project Owner, ADR-006 |
| DEC-004a | MFA mandatory role set | RESOLVED | Phase 0 | Project Owner, ADR-006 |
| DEC-004b | Hash-chain scope for access events | RESOLVED | Phase 0 | Project Owner, ADR-006 |
| DEC-005 | Database schema corrections | RESOLVED | Phase 0 | Project Owner, ADR-006 |
| DEC-006 | Persian RTL / Jalali / PDF choices | OPEN — NON-BLOCKING | Phase 3 | CTO |
| DEC-007 | Market data ingestion and licensing | REJECTED — out of scope, ADR-008 | Phase 1 | Legal + Product |
| DEC-008 | Data-flywheel policy | REJECTED — out of scope, ADR-008 | Phase 1 | Legal + Product |
| DEC-009 | Tax-optimization advisory boundary | OPEN — NON-BLOCKING | Phase 3 | Legal + CTO |
| DEC-010 | Deployment topology | OPEN — BLOCKING | Phase 4 | CTO + DevOps |
| DEC-011 | Document intelligence acceptance criteria | OPEN — BLOCKING | Phase 2 | Product + CTO |
| DEC-011a | Shahkar access route | OPEN — BLOCKING | Phase 2 | Legal + Product |
| DEC-011b | Human adjudication of flagged documents | OPEN — NON-BLOCKING | Phase 2 | Product + CISO |
| DEC-011c | Art. 86 720-day insured-days threshold | OPEN — BLOCKING | Phase 2 | Legal Counsel |
| DEC-012 | Statutory provenance ownership and user-FK ordering | RESOLVED — ADR-007 | P0-T04 | CTO/DBA + Security Architect |
| DEC-013 | Apply allowance floors and seniority base to net | OPEN — NON-BLOCKING | v1 reference-only | Project Owner + Labour Counsel/Tax Accountant |
| DEC-014 | Product scope for the requested Batch-01 application modules | OPEN — BLOCKING (Modules B–C only; A/D resolved by ADR-010, 2026-11-17) | Modules B–C; nothing in ADR-008 scope | Project Owner (Modules B–C: superseding ADR) |
| DEC-015 | Which market-salary sources may be collected, under which licence, and who signs off a source before it is marked `connected`? Also reconciles DEC-007/DEC-008 (REJECTED) with ADR-013's market-data basis | OPEN — BLOCKING (data volume) | Every real estimate; ADR-014 acceptance | Project Owner + Legal Counsel |
| DEC-016 | Is estimation history tenant-scoped (RLS + `tenant_id`) or a single-tenant audit log, and what is its retention? | OPEN — BLOCKING (history feature) | History table/API only; estimation itself runs without it | Project Owner + Security Architect |
| DEC-017 | Accept ADR-014's cohort methodology (no monetary multiplier for city, experience, seniority, education or skill; median and p25/p75 of the cohort) as the published method | OPEN — NON-BLOCKING | ADR-014 Proposed → Accepted | Project Owner |

**22 entries: 14 open (10 blocking, 4 non-blocking), 6 resolved by owner approval (ADR-006/007/008), 2 rejected as out of product scope (ADR-008).** **ADR-014 (2026-11-18)**, the market-salary reference data and estimation engine, adds DEC-015/DEC-016/DEC-017. The engine is delivered and tested against the fail-closed rule: with no licensed source connected, every production estimate returns `insufficient_data` with its counts, which is the intended behaviour and not a defect. DEC-007/DEC-008 still record market-data ingestion as rejected, so DEC-015 is also the reconciliation entry between those records and ADR-013's market-data basis; no source is marked `connected` until it is answered. ADR-005 remains separately `PROPOSED`; no queue was approved. Notes (2026-11-15, ADR-008): DEC-001 and DEC-002 no longer gate the v1 engine path — the engine runs on the verified 1404.1 baseline only; they remain open for any future 1405 activation and external corpus certification, both of which are out of ADR-008 product scope. The B-series ambiguity ledger above records the engine-review questions separately from the DEC numbering; only DEC-013 is a new owner decision in the engine-remediation pass. **DEC-014 (2026-11-16)** records the Batch-01 scope conflict after ADR-008: authentication, company management, accounting foundation and the data-backed dashboard are outside the accepted product boundary and rest on decisions this register still holds open, so no implementation of them may proceed before the owner records an option as a superseding ADR. **ADR-010 (2026-11-17)** resolved Modules A and D for the manager prototype only; Modules B and C stay blocked here.

---

## Change Control

| Rule | Detail |
| :--- | :--- |
| Entry creation | Any new blocking issue discovered during implementation is added here within 1 working day, with the affected tasks listed |
| Entry resolution | Only the named approver may move an entry to `RESOLVED`; the resolution, the date and the approver are recorded in the entry |
| Recommendation escalation | If a recommendation has been implemented without approval for more than 5 working days, it is escalated to the CTO automatically |
| Cross-reference | Every entry lists the WBS tasks it blocks; `docs/IMPLEMENTATION_READINESS.md` is derived from this register |
