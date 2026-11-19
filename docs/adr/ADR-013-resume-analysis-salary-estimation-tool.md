# ADR-013: Product Scope Change — Resume Analysis and Monthly Salary Estimation Tool

- **Status**: Accepted (recorded by Project Owner, effective date of this record)
- **Date**: 17 Aban 1405 SH (2026-11-17)
- **Decider**: Project Owner
- **Supersedes**:
  - ADR-008 **only as to** product-boundary clauses about the statutory payroll engine being the product; ADR-008's technical invariants (Decimal money, ROUND_HALF_UP, fail-closed loader, no float literals, per-field provenance) are **preserved** where applicable to the new scope.
  - ADR-010 **only as to** product-direction clauses about manager evaluation/compensation-advisory prototype; ADR-010's prototype guardrails (no production claims, loopback-only deployment, advisory labelling) are **preserved** as good practice but not binding.
  - ADR-009 is **unchanged** (its compensation-advisory module design remains out of scope for this product; no conflict).
- **Affected WBS**: all 88 tasks remain annotated, not deleted; new WBS for the salary estimation tool is to be defined by the owner in a future task.

---

## Context and Problem Statement

The owner has redefined the product. The previous product boundary was a **statutory payroll calculation engine** (SSO insurance, progressive income tax, net pay, overtime/night shift, severance, Eydi, employer CTC, Article 11 termination) serving employers who already have employees and need payslip calculations.

The new product boundary is a **resume analysis and monthly salary estimation tool**: one manager enters a candidate's career information (job title, experience, skills, education, city, employment type, seniority level) and the system returns a suggested monthly salary range with a primary estimate and the factors that influenced it.

This is not a payroll system. There are no employees to manage, no payslips to generate, no tax or insurance calculations, and no multi-tenant security foundation required.

---

## Decision Drivers

1. **Owner directive**: product is a salary estimation tool, not a statutory payroll engine. One manager only. No accounting, no HRIS, no attendance.
2. **Simplicity**: a multi-step form, an estimate result page, and optional history/PDF export. Security is simplified but not removed.
3. **Market data basis**: estimates come from real Iranian job-market data (Jobinja, JobVision, salary surveys), not from statutory minimum wage tables alone.
4. **AI boundary**: AI may analyze resumes and identify skills/experience, but must never invent salary figures or statistics; estimates must be grounded in real market data or clearly state insufficiency.
5. **Preserve what is still useful**: the frontend stack (React + Vite + TypeScript + Tailwind + RTL Persian), the testing and linting tooling, and the monetary discipline (Decimal precision, no float literals where money is touched) remain good practices.

---

## Decision Outcome

**The product boundary is now the resume analysis and monthly salary estimation tool**, effective immediately:

### Owner decisions (D-01 … D-07)

| ID | Decision | Chosen Option | Risks | Cost / Effort | Technical Dependencies |
|:--|:---|:---|:---|:---|:---|
| D-01 | Market data source | Licensed/manual salary reports + manual entry in MVP. Each data row must record: source, collection date, expiry date, job title, city/region, experience level, employment type, salary range (min–max), currency unit. Manual data without a valid source is **not** trusted for calculation. No automatic scraping in MVP; scraping only after ToS/legal review. | Data may be incomplete for some roles/cities; manual entry effort; risk of untrusted manual entries | Low for manual seeding; higher for licensed data acquisition | `market_salary_data` table; `LABOR_MARKET_DATA_SPEC.md` |
| D-02 | Authentication | Email + password (securely hashed, e.g., Argon2id/bcrypt). Single manager only. Session management with secure cookies. Rate limiting on login attempts. HTTPS enforced. Resume data protected at rest and in transit. API keys stored securely (environment variables or secret manager, never in code). Removal of RLS/tenant_id is justified because there is only one manager and no tenancy; impact is that data isolation beyond single-manager access is not enforced at database level. | Single point of access; no multi-user support in v1; database-level isolation not enforced | Low (simple auth); medium for session + rate limiting + secret management | `users` table; simplified security (no RLS, no tenant_id); HTTPS configuration |
| D-03 | Resume parsing AI | Provider-independent API for resume analysis. Manual entry always available; system works without AI. If AI API is unavailable, the manager enters data manually and estimation proceeds. Resume data sent to external AI service is minimized (skills, experience, education only) and transmitted over HTTPS; no National ID, mobile number, or Sheba number is ever sent. | API cost; privacy of resume data sent to external AI; dependency on external service; fallback UX complexity | Medium (API integration + fallback UI) | `AI_ANALYSIS_SPEC.md`; `resume_uploads` table (v2); HTTPS |
| D-04 | Database | PostgreSQL preserved. No migration to SQLite without serious technical reason. | Operational overhead of PostgreSQL for a simple tool | Low (existing infrastructure) | `DATA_MODEL_SPEC.md`; Alembic migrations |
| D-05 | PDF export | Browser print/save sufficient for MVP. Professional PDF generation deferred to v2. | Limited output quality in v1 | Low (no library needed) | Frontend print styles |
| D-06 | Estimation algorithm | Hybrid: rule-based adjustments (experience, skills, seniority, city, employment type) + real market data + AI for resume extraction/interpretation. Algorithm is explainable and evaluable: market median for matched profile is adjusted by documented rules; confidence level reflects data volume and recency; if market data is insufficient, the system returns `insufficient_data` with no numeric estimate. AI never generates salary numbers without real market data backing. | Algorithm complexity; need to validate against real market data; risk of over-reliance on AI | Medium (rule engine + market data integration) | `SALARY_ESTIMATION_SPEC.md`; `estimation_service.py` |
| D-07 | Legal minimum wage | Displayed as separate reference value only. Each value records: year, validity date, source. Not the basis of estimation; not a floor for the algorithm. | Users may confuse reference with estimate if UI unclear | Low (UI label separation) | `legal_minimum_wage_rial` field in `candidate_estimates` |

### Currency convention (applies to all layers)

- **Storage**: all monetary amounts stored in integer Rial.
- **Display**: amounts shown in Toman (Rial ÷ 10) with mandatory unit label.
- **Consistency**: this convention applies identically to database schema, API contracts, and frontend UI.

### In scope (v1)
- Single manager user type; no other roles.
- Multi-step Persian form collecting: job title, years of experience, previous jobs, skills and skill levels, education and field, certifications, city/location, employment type, seniority level (Junior/Mid/Senior).
- Resume file upload (PDF or text) for information extraction (nice-to-have for v1, prioritized for v2).
- Salary estimation service producing: (a) a suggested salary range (min–max in Iranian Rial/Toman), (b) a primary recommended estimate, (c) the factors that influenced the estimate, (d) a confidence level or "insufficient data" notice when market data is lacking.
- Clean result page showing the estimate and its reasoning.
- Save and view previous estimates (history).
- Legal minimum wage shown as a separate reference value (not mixed with market estimate).
- PDF export of estimate results (post-v1, optional).
- AI-assisted resume analysis: skill identification, experience extraction, comparison with market data — combined with calculation logic, never LLM-guesswork alone.

### Out of product scope (deferred, not cancelled)
- Statutory payroll engine (SSO, tax, net pay, overtime, severance, Eydi, CTC, Article 11).
- Employee management, payslip generation, attendance tracking.
- Accounting, financial reporting, journal entries.
- Document forensics, OCR, Shahkar verification.
- Market data scraping from job boards if it violates Terms of Service (manual or licensed data only).

---

### Preserved from previous ADRs (still useful)

| Item | Preserved? | Reason |
|:---|:---|:---|
| Frontend: React + Vite + TypeScript + Tailwind v4 + RTL Persian + Vazirmatn | Yes | Still the right UI stack for a Persian form-based tool |
| Testing: vitest, pytest, ruff, mypy --strict | Yes | Good engineering practice regardless of product scope |
| Monetary discipline: Decimal, ROUND_HALF_UP, integer Rial at boundaries | Yes | Applies wherever money figures are shown |
| Advisory labelling principle ("not legal payroll advice") | Yes | Protects against misrepresenting estimates as official |
| Logical CSS utilities only (no physical RTL overrides) | Yes | Already implemented in frontend |
| ADR-001 (frontend architecture) | Yes | React + Vite SPA remains valid |
| ADR-002 (object storage concept) | Partially | Concept valid; complexity reduced (no WORM needed for v1) |
| ADR-003 (encryption concept) | Partially | Concept valid; AES-256-GCM + blind indexing not needed for resume data in v1 |
| ADR-010 guardrails (no production claims, loopback-only, advisory labelling) | Yes | Good practice for prototype posture |

### Architectural decisions changed from previous ADRs

| Previous Decision | New Decision | Reason and Justification |
|:---|:---|:---|
| ADR-008: Product = statutory payroll engine | ADR-013: Product = salary estimation tool | Owner directive (2026-11-17); different product purpose |
| ADR-006/007: Multi-tenant RLS, tenant_id, FORCE ROW LEVEL SECURITY | Simplified: single manager, no tenant_id, no RLS | Justification: only one manager exists; no tenancy. Impact: database-level row isolation is not enforced; access control is application-level only. Not removed for simplicity alone — removed because it is unnecessary for the new scope. |
| ADR-003: AES-256-GCM + blind indexing for PII | Simplified: standard DB access controls + HTTPS + secure password hashing | Justification: resume data is not high-sensitivity PII (no National ID/mobile/Sheba). Impact: field-level encryption and blind indexing are not implemented in v1. Not removed for simplicity alone — removed because the threat model does not require it. |
| ADR-008: 1404/1405 statutory rule-set loader | Not used | Market data basis, not statutory rules |
| SPEC-STAT-001: Statutory parameter ingestion | LABOR_MARKET_DATA_SPEC: Market data acquisition | Different data domain |
| ADR-010: Manager evaluation + compensation advisory prototype | Salary estimation tool | Different product purpose |

### Superseded or set aside

| Item | What changes |
|:---|:---|
| ADR-008 product boundary (statutory payroll engine as product) | Superseded; engine remains as technical code but is no longer the product |
| ADR-010 manager prototype direction (evaluation + compensation advisory) | Superseded as product direction; its guardrails (no production claims, loopback-only) are kept as good practice |
| ADR-009 compensation advisory module | Unchanged; remains out of scope |
| All 88 WBS tasks | Annotated, not deleted; new task list for salary estimation tool defined separately |

---

## Positive Consequences

- Product matches the owner's stated mission: one manager, one form, one salary estimate.
- Much simpler implementation: no payroll calculations, no multi-role auth, no RLS, no tenant security.
- Faster time to value for the owner's actual decision need (job offer salary advice).

### Negative Consequences / Trade-offs

- Existing statutory payroll engine code remains in the repository but is no longer the product; it may be archived or removed in a future cleanup.
- Market data acquisition requires licensed or manual sources; scraping job boards may violate Terms of Service (DEC-007/008 rejection stands).
- No legal minimum wage enforcement; the tool estimates market rates, not statutory compliance.
- Database-level row isolation (RLS) is not enforced; access control is application-level only.

---

## Implementation Directives

1. **No code, database, migration, or behavior changes are made by this ADR.** It is a scope and decision record only.
2. A new WBS task list for the salary estimation tool must be defined by the owner (or delegated) before implementation begins.
3. Any reuse of the existing frontend components (UI primitives, money formatting, RTL layout) must be evaluated against the new scope on a case-by-case basis.
4. The existing statutory payroll engine (`backend/app/engines/`) and its seeds remain untouched; no deletion is authorized by this ADR.
5. Independent review by a non-author is required before any monetary or estimation logic moves beyond `READY_FOR_REVIEW` (AGENTS.md §6).

---

## Compatibility Check — Active Documents and Implementation Roadmap

All active documents and the implementation roadmap have been reviewed against decisions D-01 … D-07. The following confirms compatibility:

| Document | Compatible? | Notes |
|:---|:---|:---|
| `PRODUCT_VISION.md` | Yes | Matches single-manager, market-based salary estimation |
| `PRODUCT_SCOPE.md` | Yes | Reflects D-01 through D-07 choices |
| `FUNCTIONAL_REQUIREMENTS.md` | Yes | FR-01…FR-13 align with all decisions |
| `NON_FUNCTIONAL_REQUIREMENTS.md` | Yes | NF-01…NF-18 align with all decisions |
| `USER_WORKFLOWS.md` | Yes | Workflow matches D-02 (single manager), D-05 (browser print), D-07 (reference display) |
| `SALARY_ESTIMATION_SPEC.md` | Yes | Estimation methodology matches D-06 (hybrid rule-based + market data) |
| `LABOR_MARKET_DATA_SPEC.md` | Yes | Data model and acquisition rules match D-01 |
| `AI_ANALYSIS_SPEC.md` | Yes | AI boundaries match D-03 (provider-independent API, manual fallback) |
| `DATA_MODEL_SPEC.md` | Yes | Schema matches D-04 (PostgreSQL), D-02 (simplified users), D-07 (reference field) |
| `SECURITY_AND_PRIVACY.md` | Yes | Simplified security matches D-02, no RLS/encryption overreach |
| `ARCHITECTURE.md` | Yes | Simplified architecture matches all decisions |
| `IMPLEMENTATION_ROADMAP.md` | Yes | 12 tasks reflect D-01…D-07 priorities |
| `OPEN_DECISIONS.md` | Yes | All 7 decisions now resolved in this ADR |
| `README.md` | Yes | Updated to reflect new product direction |

**No active document contradicts decisions D-01 … D-07.**

---

## Next Step

This ADR records the scope change and all owner decisions (D-01 … D-07). No implementation occurs until the owner reviews and explicitly approves this ADR. After approval, a new implementation plan and WBS for the salary estimation tool can be created, and an implementation-capable agent can begin coding.
