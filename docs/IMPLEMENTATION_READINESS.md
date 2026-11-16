# Implementation Readiness Assessment

- **Document ID:** `DOC-READY-001`
- **Status:** Active — re-evaluated at every phase gate
- **Date:** 2026-11-14 (23 Aban 1405 SH); delivery census and evidence refreshed 2026-11-16 (BOOTSTRAP_CHANGELOG §24)
- **Related:** [`docs/EXECUTION_PLAN.md`](EXECUTION_PLAN.md) · [`docs/DECISIONS_REGISTER.md`](DECISIONS_REGISTER.md) · [`docs/specs/TESTING.md`](specs/TESTING.md)

---

## 1. Verdict

> **The project is NOT implementation-ready.**

The *architecture* is decided — seven Accepted ADRs (ADR-001…004, 006, 007, 008; ADR-005 remains proposed), a coherent technology stack and a coherent domain model. The *planning* is now complete — an 86-task WBS with dependencies, acceptance criteria and verification methods, against the unchanged 20-week roadmap.

What is missing is not architectural. It is:

1. **the active legal baseline** — the 1405 SH rule set is transcribed but not four-eyes verified, and the certified golden-vector corpus does not exist;
2. **one architectural decision** — the asynchronous execution strategy (ADR-005) is `PROPOSED`;
3. **three external acquisitions** — a Certified Tax Accountant, an Iranian labour attorney, and a consented corpus of 500 authentic Social Security slips.

Readiness is therefore assessed **per phase**, and two phases are `BLOCKED`.

---

## 2. Classification method

A phase is classified `READY` only when **all four** of the following are satisfied:

| # | Condition |
| :--: | :--- |
| 1 | Its **prerequisites** (the prior phases' outputs and the upstream specifications) are defined |
| 2 | Its **technical specifications** are complete enough to build against |
| 3 | Its **test requirements** are defined, including the gate's measurement method |
| 4 | The **decisions** it depends on are resolved |

If any condition fails but the failure is bounded and recoverable, the phase is `READY_WITH_CONDITIONS` and the conditions are listed. If a failure is unbounded — a required external artefact that does not exist, or a decision with no owner — the phase is `BLOCKED`.

**Documentation readiness is not implementation completion.** Current WBS: 1 `COMPLETED`, 6 `IN_PROGRESS`, 17 `READY_FOR_REVIEW`, 58 `NOT_STARTED`, 4 `BLOCKED`; 0 `APPROVED`. The ADR-008 statutory engine and its minimal endpoint are implemented and locally verified (§23, §24), but no engine task is `APPROVED`: independent review by a non-author and the PostgreSQL integration run remain outstanding. CI exists but has never executed on GitHub; the integrated tenant-security foundation and real authentication do not exist. ADR-006/007/008 resolve six register entries; 11 remain open (7 blocking, 4 non-blocking) and DEC-013 is proposed. Verification: BOOTSTRAP_CHANGELOG §24 (engine/application suite), §21 (isolated DB), §15 (recorded DB runtime). No accountant, labour counsel or licensed/consented datasets are available.

**Execution boundary.** Descriptions below of work with documented assumptions permit planning and proposals only when a decision is open. They do not authorize choosing authentication, key hierarchy or schema variants, or writing migrations that encode an unresolved decision. Obtain the recorded approvers' decision first; `AGENTS.md` §3 governs that boundary.

---

## 3. Per-phase classification

### Phase 0 — Security and Relational Foundation (Weeks 1–4)

**Classification: `READY_WITH_CONDITIONS`**

| # | Condition | Verification | Deadline |
| :--: | :--- | :--- | :--: |
| 1 | **DEC-004 and DEC-005 ratified** by the CISO/CTO and the CTO/DBA respectively | The register entries move to `RESOLVED` with a named approver (both are now resolved under ADR-006) | End of Week 1 |
| 2 | `P0-T05`, `P0-T12` and `P0-T18` proceed against the **proposed** schema in `SPEC-AUTH-001` §2 and the corrections in `EXECUTION_PLAN.md` §6.2, with the assumption recorded in each task's *Blocking issues* field | The assumption is visible in the task record and re-checked at the Phase 0 gate | On creation of each task |
| 3 | **Three external commissions started in Week 1**: the Certified Tax Accountant (`P1-T15`), the Labour Counsel (`P1-T02`, `P4-T07`), and the penetration-test vendor (`P4-T06`) | Engagement letters or recorded requests exist | End of Week 1 |
| 4 | `P0-T02` → `P0-T19` proceed without further decisions | — | — |

| Condition | Assessment |
| :-- | :--- |
| Prerequisites | **Met** — ADR-001…004, `REMEDIATED` §4, and `SPEC-AUTH-001` §2 define the domain model |
| Technical specifications | **Met** — `SPEC-AUTH-001`, `SPEC-STAT-001` §5–§7, `SPEC-OPS-001` §§2–5, `SPEC-QA-001` §§3–9 |
| Test requirements | **Met** — `SPEC-QA-001` §8 (the 12 isolation tests), §9 (the 13 crypto tests), §8.1 (the zero-plaintext-PII gate) |
| Decisions | **4 resolved by Project Owner, ADR-006** (DEC-004, DEC-004a, DEC-004b, DEC-005). CI/provider, topology and unapproved detailed contracts remain; no gate has passed |

**Verdict.** The phase can start on Monday. The two open decisions are recorded recommendations with complete specifications behind them; the condition is that they are ratified in Week 1 and that the assumption is visible on the three affected tasks. **The Phase 0 gate itself cannot be signed** until DEC-004 and DEC-005 are resolved, because `P0-T18` (8 days) and `P0-T12` implement them.

---

### Phase 1 — Deterministic Engine and Inverters (Weeks 5–8)

**Classification: `BLOCKED`**

| Blocking item | Why it is blocking | Owner | Unblock action |
| :-- | :--- | :-- | :--- |
| **`P1-T15` — the golden vector corpus does not exist** | The Phase 1 gate is defined as *"10,000-case automated test suite matching certified tax accountant test vectors"*. No corpus, no gate | Certified Tax Accountant (external, unengaged) | Appoint; agree the scope, the case taxonomy and the certification format; the corpus must be authored in parallel with the engine |
| **`P1-T02` — the 1405 rule set is not four-eyes verified** | No L1 primary PDF was retrievable from the build environment; O1–O5 remain open; the active baseline for the statutory year is unproven | Legal Counsel + Certified Tax Accountant | Obtain the primary PDFs through the official channels; complete the four-eyes protocol in `SPEC-STAT-001` §4 |
| **DEC-002a — the taxable-base definition is undecided** | The corrected gross for a given net depends on it; the engine cannot be specified deterministically without it | Certified Tax Accountant + Legal Counsel | Decide before `P1-T05` is finalised |
| **DEC-007 — the market-data source and licence** | `P1-T17` and `P1-T18` cannot load a licensed corpus | Legal Counsel + Product Manager | Decide the ingestion strategy |
| **DEC-001 — the 1405 activation** | The active rule set for the statutory year | CTO + Legal Counsel | Follows `P1-T02` and `P1-T03` |

| Condition | Assessment |
| :-- | :--- |
| Prerequisites | **Met** — the rule-set loader, the money primitives and the security foundation are defined |
| Technical specifications | **Partially met** — the engine's structure is fully specified, but the taxable-base definition (DEC-002a) is an input to it |
| Test requirements | **Defined but unexecutable** — the measurement method is specified; the measured artefact does not exist |
| Decisions | **4 open, all blocking** |

**Verdict.** The *engineering* of the tax, SSO, severance, Eydi, overtime, CTC and inverter engines can begin against the **verified 1404** rule set and the published 1404 brackets. The *phase* is nevertheless `BLOCKED`, because its gate cannot be met without the certified corpus, and because the statutory year that the platform must actually operate under is not yet proven.

**Mitigation.** The interim position in `EXECUTION_PLAN.md` §3.5 (operate on 1404, labelled as such) preserves the schedule for the engine work while the external items are procured.

---

### Phase 2 — Document Forensics and Identity (Weeks 9–14)

**Classification: `BLOCKED`**

| Blocking item | Why it is blocking | Owner | Unblock action |
| :-- | :--- | :-- | :--- |
| **`P2-T04` — the async execution strategy** | ADR-005 is `PROPOSED`; five downstream tasks (`P2-T05`–`P2-T09`) depend on the job interface. The `JobQueue` interface must be fixed before the pipeline is built | CTO | Approve ADR-005 (or reject it and re-plan `P2-T04` before `P2-T05`) |
| **`P2-T16` — the 500-slip authentic corpus does not exist** | The Phase 2 gate is *"parsing of 500 authentic Social Security slips with > 95% field extraction accuracy"*. A synthetic corpus is explicitly not admissible | Document Forensics Eng + QA Lead + employer consents | Begin the consent and redaction pipeline in Week 1 |
| **DEC-011, DEC-011a, DEC-011b, DEC-011c** | The acceptance criteria, the Shahkar aggregator arrangement, the adjudication role and the Art. 86 720-day threshold | Product Manager, Legal Counsel, CISO | Decide before `P2-T12` and `P2-T17` |

| Condition | Assessment |
| :-- | :--- |
| Prerequisites | **Met** — `SPEC-DOC-001` is complete, including the taxonomy, the status model, the consistency matrix, the disambiguation model and the acceptance criteria |
| Technical specifications | **Met** |
| Test requirements | **Defined** (`DF-01`…`DF-13`, `SPEC-QA-001` §10) but the corpus is unavailable |
| Decisions | **5 open**, of which 1 (ADR-005) is architectural and 4 are bounded |

**Verdict.** `P2-T01`, `P2-T02`, `P2-T03`, `P2-T07` and `P2-T08` have no dependency on ADR-005 and can proceed. Everything that needs the job pipeline waits on the CTO.

---

### Phase 3 — Pre-Hire Simulation and React SPA (Weeks 15–18)

**Classification: `READY_WITH_CONDITIONS`**

| Condition | Deadline | Verification |
| :-- | :-- | :-- |
| 1 | The Phase 1 API contract is frozen (`P1-T19`) and its contract tests are green | Week 15 |
| 2 | **DEC-006** is decided — the Jalali library, the PDF pipeline and the font subsetting strategy | Week 15 |
| 3 | ADR-005 is accepted, so the document-job status UI has a contract to render | Week 15 |
| 4 | `P2-T12` (Shahkar) and `P2-T13` (issuer orchestrators) have published their response shapes, so `P3-T09` can be built | Week 16 |

| Condition | Assessment |
| :-- | :--- |
| Prerequisites | **Partially met** — ADR-001 is Accepted; the API contract depends on Phase 1; the job-status contract depends on ADR-005 |
| Technical specifications | **Met** — `SPEC-FE-001` covers the layout, typography, numerals, calendar, currency, normalisation, PDF, browser rendering, accessibility and responsive behaviour |
| Test requirements | **Met** — `SPEC-QA-001` §§11.1–11.2 and the FE-01…FE-14 checks |
| Decisions | **1 open** (DEC-006, non-blocking) |

**Verdict.** The frontend has a complete, buildable specification and no legal or evidentiary dependency. The conditions are sequencing constraints rather than blockers.

---

### Phase 4 — Pilot Hardening and Compliance Sign-Off (Weeks 19–20)

**Classification: `READY_WITH_CONDITIONS`**

| Condition | Deadline | Verification |
| :-- | :-- | :-- |
| 1 | **DEC-010** is decided — the deployment topology and the air-gapped baseline | Week 18 |
| 2 | The external vendors are engaged with enough lead time to deliver inside a 2-week window: the penetration tester, the Iranian labour attorney, the Certified Tax Accountant | Week 16 |
| 3 | Phases 0–3 are green with archived evidence | Week 19 |
| 4 | The `SPEC-OPS-001` §12 air-gapped verification checklist has been executed at least once | Week 19 |

| Condition | Assessment |
| :-- | :--- |
| Prerequisites | **Not yet met** — depends on Phases 0–3 |
| Technical specifications | **Met** — `SPEC-OPS-001` §§7–12 |
| Test requirements | **Met** — `SPEC-QA-001` §12 and §18 |
| Decisions | **1 open** (DEC-010) plus the external lead times |

**Verdict.** The gate is a *legal and security* sign-off, not a build. It is entirely gated by the external parties and by Phases 0–3. **The 2-week Phase 4 window is unrealistic for an external penetration test and a legal review.** This is raised as schedule risk **R-6** in the execution plan; no schedule change has been applied.

---

## 4. Summary matrix

| Phase | Weeks | Classification | Blocking decisions | Blocking external artefacts | Can start? |
| :-- | :--: | :--- | :--: | :--: | :--- |
| 0 | 1–4 | **READY_WITH_CONDITIONS** | Four identity/audit/schema decisions resolved by ADR-006; CI, topology and detailed integration contracts remain | — | **Yes — within verified dependencies** |
| 1 | 5–8 | **BLOCKED** | DEC-001, DEC-002, DEC-002a, DEC-007 | The certified golden-vector corpus; the L1 primary circulars | Engine work only, on 1404 |
| 2 | 9–14 | **BLOCKED** | ADR-005, DEC-011, DEC-011a, DEC-011b, DEC-011c | The 500-slip authentic corpus | Partially (`P2-T01`, `T02`, `T03`, `T07`, `T08`) |
| 3 | 15–18 | **READY_WITH_CONDITIONS** | DEC-006 | — | Yes, from Week 15 |
| 4 | 19–20 | **READY_WITH_CONDITIONS** | DEC-010 | The pentest vendor; the labour attorney; the tax accountant | No — gated by Phases 0–3 |

**Overall: NOT implementation-ready.** Two of five phases are blocked; both blocks are external and legal, not architectural.

---

## 5. Tasks that can begin immediately

| Task | Why it can start |
| :-- | :--- |
| `P0-T01` | The only task with no predecessor. Everything else chains from it |
| `P1-T02` (commission) | The *activity* — obtaining the primary PDFs and engaging the Labour Counsel — can start now. The task cannot complete until O1–O5 close |
| `P1-T15` (commission) | The *activity* — appointing the Certified Tax Accountant — can start now. It is the longest lead item in the project |
| `P2-T16` (commission) | The *activity* — the employer-consent and redaction pipeline — can start now |
| `P4-T07` (commission) | The *activity* — engaging the Iranian labour attorney — can start now; the review itself needs the Phase 1 engine |
| `P4-T06` (commission) | Vendor engagement can start now; the test needs a deployed pilot |

**These five commissions are the highest-leverage actions available.** They are all externally gated, all long-lead, and all currently unowned.

---

## 6. Tasks that can begin with documented assumptions

Each of the following may proceed if the stated assumption is recorded in the task's *Blocking issues* field and re-checked at the phase gate.

| Task | Assumption | Assumption owner |
| :-- | :--- | :-- |
| `P0-T05` | The identity schema in `SPEC-AUTH-001` §2 is implemented as proposed | Security Architect |
| `P0-T09`, `P0-T12` | The ERD corrections in `EXECUTION_PLAN.md` §6.2 are applied as proposed | Database Engineer |
| `P0-T18` | The session model in `SPEC-AUTH-001` §5 is implemented as proposed | Security Architect |
| `P1-T01` | The 1404 rule set is the interim baseline; the loader stays fail-closed for 1405 | Backend Engineer |
| `P1-T05` | The tax engine supports both welfare treatments and both Art. 137 policies, with the active combination selected by DEC-002a when it lands | Payroll Engineer |
| `P1-T13` | The inverter is implemented against the two-region model in `SPEC-STAT-001` and the skill corpus, with the boundary check mandatory | Backend Engineer |
| `P2-T01`, `P2-T02`, `P2-T03`, `P2-T07`, `P2-T08` | The document storage and forensics layers are built behind the `JobQueue` interface, which is fixed by `P2-T04` | Document Forensics Engineer |
| `P3-T01`…`P3-T06` | The API contract shapes are taken from `REMEDIATED` §5 as amended by `P1-T19` | Lead Frontend Engineer |

---

## 7. Tasks blocked by missing legal or technical evidence

| Task | Evidence type | Missing evidence | Consequence if bypassed |
| :-- | :-- | :-- | :-- |
| `P1-T02` | **Legal** | The L1 primary circulars (wage circular, Cabinet Resolution 9234, SSO circular, Budget Law) and a four-eyes signature | Unlawful employment contracts; SSO and tax exposure (`FIND-TIME-01`) |
| `P1-T03` | **Legal** | The signed verification log | An unverified rule set activated |
| `P1-T15` | **Legal / actuarial** | The Certified Tax Accountant's signed corpus | The Phase 1 gate is unfalsifiable; the "certified accountant test vectors" claim is unsubstantiated |
| `P1-T22` | **Legal** | The gate evidence pack | The gate is asserted rather than demonstrated |
| `P2-T16` | **Legal / empirical** | 500 consented, redacted authentic slips | The OCR accuracy claim stays `[UNVERIFIED]`; the Phase 2 gate is unfalsifiable |
| `P2-T18` | **Legal** | The gate evidence pack and the corpus | The gate is asserted rather than demonstrated |
| `P4-T07` | **Legal** | The Iranian labour attorney's sign-off letter | The dispute-immunity claim is unsubstantiated |
| `P4-T06` | **Technical** | The external penetration-test report | An unknown Critical/High finding may reach the pilot |
| `P4-T11` | **Legal / technical** | All of the above | — |

---

## 8. The three highest-risk items

| Rank | Item | Why it is the top risk | Mitigation |
| :--: | :--- | :--- | :--- |
| **1** | **The golden vector corpus (`P1-T15`)** | It is the **only** evidence that the engine is legally correct, it is the definition of the Phase 1 gate, and it is produced by an external party that is not yet engaged. A 10,000-case corpus is not a small writing task. If it is commissioned in Week 8 instead of Week 1, Phase 1 cannot complete in 4 weeks | Appoint in Week 1; agree the case taxonomy, the case template and the certification format with the accountant **before** the engine is written, so the two proceed in parallel |
| **2** | **The 1405 four-eyes verification (`P1-T02`)** | The primary sources are unreachable from the engineering environment, so this is a legal-team task, not an engineering task. Until it completes, the platform must either run on 1404 or run on unverified values — and the second option is the one the red-team audit called out as `FIND-TIME-01` (Critical) | Start the Legal Counsel engagement in Week 1; use the interim 1404 position with explicit disclosure; close O1–O5 in parallel |
| **3** | **The 500-slip corpus (`P2-T16`)** | It requires employer consent and a redaction pipeline. Consent is an organisational process with a long tail and a large failure surface — one refusal or one late response can move the Phase 2 gate | Begin the consent process in Week 1, not Week 9; secure a fallback of a smaller authentic corpus with a stated confidence interval (DEC-011 Option C) |

---

## 9. Re-assessment triggers

This assessment is re-evaluated on any of the following:

| Trigger | Action |
| :--- | :--- |
| A register entry moves to `RESOLVED` | Re-classify the affected phase |
| A phase gate is signed | Re-classify the successor phase |
| A new blocking issue is discovered | Add it to the register within 1 working day and re-assess |
| The schedule changes | Re-check §4 and the execution plan §14.6 |
| A weekly cadence (from Phase 0) | Refresh the "can start" and "blocked" lists |

---

*Derived from `docs/EXECUTION_PLAN.md` §14 and `docs/DECISIONS_REGISTER.md`. The register is authoritative for the decision states; this document derives readiness from them.*
