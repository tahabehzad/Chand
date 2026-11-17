# Product Decisions — Pish-Hesabdari

- **Document ID:** `DOC-DEC-002`
- **Status:** Living register for the **product/architecture direction**. Statutory and legal decisions stay in `docs/DECISIONS_REGISTER.md` (DEC-001…DEC-014) and accepted architecture decisions in `docs/adr/`.
- **Rule:** an entry is binding only when `CONFIRMED`. `PROVISIONAL` means "in force for the prototype only". `OPEN` means nobody may implement it. Examples in any document are **not** decisions.
- **As at:** 2026-11-17 (ADR-010 approved by the Project Owner, effective 2026-11-17)

**Status vocabulary:** `CONFIRMED` · `PROVISIONAL` · `OPEN` · `REJECTED`

---

## 1. Register

### PB-D01 — Product scope: management evaluation and compensation advisory

| Field | Value |
| :--- | :--- |
| **Status** | `CONFIRMED — ADR-010` (approved by the Project Owner as written, prospective, **effective 2026-11-17**) |
| **Decision** | Should the product boundary expand from the ADR-008 statutory payroll engine to a management system that registers people, evaluates performance and recommends compensation? |
| **Reason** | The owner stated this direction on 2026-11-16. `AGENTS.md §3` requires a **superseding ADR** to change an accepted decision; ADR-008 limits the product to pure functions + one minimal endpoint, and `DEC-014` holds exactly these modules `OPEN — BLOCKING`. |
| **Consequences** | Until recorded: the five-hour MVP is a **labelled prototype**, loopback-only, no production/pilot claim, and the statutory engine remains the only accepted product surface. If rejected: prototype is deleted or stays a demo; the payroll engine remains the product. If confirmed: a new ADR (recommend `ADR-010`) plus ADR-008 amendment and `DEC-014` resolution. |
| **Resolution (2026-11-17)** | Confirmed per [ADR-010](adr/ADR-010-manager-mvp-product-scope.md) v2: the **manager-only evaluation and compensation-advisory prototype** is the current approved product direction, effective 2026-11-17, under a **preserved prototype boundary** (not production-ready; backend integration not complete; no scope expansion beyond ADR-010 §2/§3). The consequences row above describes the pre-approval posture and is retained as history. |
| **Date** | 2026-11-16 (opened) · 2026-11-17 (confirmed) |

### PB-D02 — Initial user type

| Field | Value |
| :--- | :--- |
| **Status** | `CONFIRMED — ADR-010` (effective 2026-11-17) |
| **Decision** | Exactly one user type in the MVP: Manager / organisation owner. Employees are evaluation subjects, not users. |
| **Reason** | Owner brief. Keeps the first release small and avoids an employee-facing security surface. |
| **Consequences** | No employee portal, no self-service, no per-employee login. The existing 7-role identity schema (`0002`) is **not** exercised by the MVP; it stays a foundation for later phases. Any future employee access requires a new decision and real authentication. |
| **Resolution (2026-11-17)** | Confirmed per ADR-010 §4.1 (text unchanged; X-2 resolved the same way — the 7 roles remain an unexercised foundation). |
| **Date** | 2026-11-16 |

### PB-D03 — Evaluation criteria and weights

| Field | Value |
| :--- | :--- |
| **Status** | `OPEN` |
| **Decision** | Which real criteria, metrics, normalisation and weights define contribution? |
| **Reason** | The brief offers **examples only** (sales 40 %, quality 30 %, attendance 20 %, responsibility 10 %) and states they are not approved rules. No source system, unit or period has been named. |
| **Consequences** | The prototype may ship `perf-v1` with those illustrative weights **only** if the API and UI label them `provisional` and the rule set is versioned. No real pay decision may cite them. Changing them later requires a new rule-set version and re-running historical evaluations — never rewriting them. |
| **Date** | 2026-11-16 |

### PB-D04 — Data sources and integrations

| Field | Value |
| :--- | :--- |
| **Status** | `OPEN` |
| **Decision** | Which external systems supply performance data, in what priority, and under which access method (export file, API, manual)? |
| **Reason** | The brief explicitly leaves integrations unidentified. |
| **Consequences** | The MVP must be source-agnostic: every channel produces the same observation DTO. No connector, credential or scraping may be designed yet. A later decision must also settle rate limits, consent and data-processing terms. |
| **Date** | 2026-11-16 |

### PB-D05 — Person identity matching

| Field | Value |
| :--- | :--- |
| **Status** | `OPEN` |
| **Decision** | How are records from different sources established as the same person? |
| **Reason** | Name similarity is not identity. A wrong merge attaches one person's performance and pay to another — a severe, hard-to-reverse harm. |
| **Consequences** | The MVP never auto-merges; a candidate match is displayed for human confirmation. Any future automatic rule needs a precision/recall argument, an audit trail and an undo path. No national-ID-based matching is authorised (no PII custody yet). |
| **Date** | 2026-11-16 |

### PB-D06 — Persistence for the MVP and beyond

| Field | Value |
| :--- | :--- |
| **Status** | `SUPERSEDED — ADR-010` (effective 2026-11-17; original text retained as history) |
| **Decision** | MVP uses an in-memory store behind a `Repository` protocol; PostgreSQL persistence is the next step. |
| **Reason** | Five hours cannot deliver schema, migration, RLS, session wiring and UI together. An in-memory store with a narrow interface keeps the domain code portable. |
| **Consequences** | Data is lost on restart; no concurrency guarantees; not a database design. The prototype stores **no** national ID, mobile, Sheba or real salary data. Moving to PostgreSQL requires tenant tables with `tenant_id`, policy and `FORCE ROW LEVEL SECURITY` in the same migration. |
| **Supersession (2026-11-17)** | Per ADR-010 §4.2: the prototype persists in **PostgreSQL** tenant tables with `tenant_id`, RLS policy and `FORCE ROW LEVEL SECURITY` in the same migration (`0003`/`0004`), exactly as the consequence row above required. The in-memory premise (incl. `MVP_SCOPE` §7.1 and step 12) no longer describes the tree. The no-PII consequence stands. |
| **Date** | 2026-11-16 |

### PB-D07 — Recommendation vs statutory payroll

| Field | Value |
| :--- | :--- |
| **Status** | `CONFIRMED` (separation) · later use `OPEN` |
| **Decision** | A management recommendation is **advisory** and must be labelled `advisory: true`, `statutory: false`. It is never described as legally compliant payroll. The statutory engine may only *cost* a proposed gross. |
| **Reason** | `AGENTS.md §2` invariants 4, 5, 9; ADR-008; DEC-009; DEC-013 open; 1404 is the only active, unverified-by-counsel baseline. |
| **Consequences** | No automatic payment, no payslip claim, no compliance statement. Whether a recommendation may ever feed a real payroll run stays `OPEN` and requires Labour Counsel plus the accountant's sign-off. |
| **Date** | 2026-11-16 |

### PB-D08 — AI boundary

| Field | Value |
| :--- | :--- |
| **Status** | `CONFIRMED` (principle) |
| **Decision** | AI may later assist extraction, summarisation and anomaly detection. It must never silently make a financial decision or produce an unexplained score. |
| **Reason** | Owner brief; `AGENTS.md` invariants 4 and 5 (forensic anomaly ≠ verdict; human review mandatory). |
| **Consequences** | The MVP uses a deterministic rule engine only. Any future AI feature needs a published model version, an explanation path, a human confirmation step and no outbound PII transfer to unapproved services. |
| **Date** | 2026-11-16 |

### PB-D09 — Authentication for the MVP

| Field | Value |
| :--- | :--- |
| **Status** | `SUPERSEDED — ADR-010` (effective 2026-11-17; original text and recommendation retained as history) |
| **Decision** | Does the MVP ship without authentication, or is a minimal local login required first? |
| **Reason** | Real authentication (`P0-T18`) needs sessions, hashing, CSRF, rate limiting and a database — far beyond five hours. A fake login screen would be a security claim without a control. |
| **Recommendation** | Ship **no login**: bind to `127.0.0.1`, environment-gate the prototype routes, show a persistent banner, and state in the demo that anyone with local access can read the data. |
| **Supersession (2026-11-17)** | Per ADR-010 §4.2 the owner approved the prototype **with a minimal real sign-in** (Argon2id verification, opaque session token) instead of the no-login recommendation; `P0-T18` remains the completion gate for production-grade authentication (HttpOnly cookie, MFA, CSRF, rate limiting, runtime DB role). The prototype remains loopback/dev-only and must never be exposed on a LAN, a tunnel or the internet. The recommendation above is preserved as the recorded position it superseded — a fake login was never shipped (`R-6` still holds). |
| **Consequences** | The prototype must never be exposed on a LAN, a tunnel or the internet. `docs/MVP_SCOPE.md` records this as a known compromise. |
| **Date** | 2026-11-16 |

### PB-D10 — Money and precision

| Field | Value |
| :--- | :--- |
| **Status** | `CONFIRMED` |
| **Decision** | Money is integer Rial in JSON; computation uses `Decimal` with `prec = 34` and `ROUND_HALF_UP`; no float literal or `round()` on money; one rounding boundary per line. |
| **Reason** | `AGENTS.md §2` Financial invariants 7–9; already enforced in `app/engines/money.py`. |
| **Consequences** | New modules inherit the rule, including scores and deltas. Rates/scores are published as strings so a JavaScript client cannot silently convert them to binary floats. |
| **Date** | 2026-11-16 |

### PB-D11 — Prototype namespace and environment gate

| Field | Value |
| :--- | :--- |
| **Status** | `SUPERSEDED — ADR-010` (effective 2026-11-17; original text retained as history) |
| **Decision** | Prototype endpoints live under `/api/v1/prototype/*` and are registered only when `APP_ENV` is local; the default is **off**. |
| **Reason** | Keeps the labelled prototype out of any real deployment and makes accidental exposure a 404, not an unauthenticated API. |
| **Consequences** | Extra wiring in `app/main.py`; a test must prove 404 outside local (AC-11). A later authenticated product does not reuse this namespace. |
| **Supersession (2026-11-17)** | Per ADR-010 §4.2: the prototype publishes real authenticated routes (`/api/v1/auth`, `/api/v1/manager`) instead of the environment-gated namespace; every manager route requires an authenticated manager session and the tenant bound at sign-in. The protective intent is preserved by mandatory authentication + tenant binding, and the loopback-only deployment discipline stands. The "404 outside local" acceptance criterion no longer applies to these routes. |
| **Date** | 2026-11-16 |

### PB-D12 — Import formats in the MVP

| Field | Value |
| :--- | :--- |
| **Status** | `PROVISIONAL` |
| **Decision** | Manual entry is essential; a single UTF-8 CSV is optional; XLSX is out. |
| **Reason** | Parsing spreadsheets needs a new dependency and edge-case work that does not fit the budget (`AGENTS.md §13.11`: no dependency without a stated need). |
| **Consequences** | The demo can run entirely on manual entry. CSV import is the first task cut. XLSX returns only with a real ingestion requirement. |
| **Date** | 2026-11-16 |

### PB-D13 — No new dependencies for the MVP

| Field | Value |
| :--- | :--- |
| **Status** | `CONFIRMED` |
| **Decision** | The five-hour MVP adds no runtime dependency to backend or frontend. |
| **Reason** | `AGENTS.md §13.11`; the toolchain already provides pydantic, Decimal, React, TanStack Query and Vitest. |
| **Consequences** | No charting library, no XLSX parser, no Playwright, no new UI kit. Anything needing them moves to `docs/FUTURE_BACKLOG.md`. |
| **Date** | 2026-11-16 |

### PB-D14 — Human decision is mandatory

| Field | Value |
| :--- | :--- |
| **Status** | `CONFIRMED` |
| **Decision** | Every recommendation requires an explicit manager decision (approve / edit / reject) with a comment; the system never applies a recommendation by itself. |
| **Reason** | `AGENTS.md §2` invariant 5; owner brief §4–§5. |
| **Consequences** | A recommendation without a decision remains `pending`. Rejections preserve the score and the reason for audit and later analysis. |
| **Date** | 2026-11-16 |

---

## 2. Rejected approaches

| ID | Approach | Status | Reason | Consequence |
| :--- | :--- | :--- | :--- | :--- |
| R-1 | Automatic fuzzy name matching / auto-merge of person records | `REJECTED` (for the product, not just the MVP) | Wrong merge misattributes pay and performance; irreversible harm | Candidate matches are human-confirmed only |
| R-2 | ML/AI scoring model as the MVP scoring engine | `REJECTED` | Unexplainable, unverifiable, no training data, violates explainability | Deterministic versioned rule engine |
| R-3 | Automatic bank transfer of a recommendation | `REJECTED` | Out of scope; payment execution is a regulated operation | Manager decision only; disbursement stays external |
| R-4 | Storing real national IDs, mobiles, Sheba or real salaries in the prototype | `REJECTED` | No key management, no tenant isolation, no audit ledger, no consent basis | Synthetic data only; PII fields appear only in the future PostgreSQL design |
| R-5 | Writing performance/evaluation data into `statutory_*` tables | `REJECTED` | Those tables are global, evidence-grade and append-only (ADR-007); mixing domains destroys provenance | Separate entities, separate migrations |
| R-6 | A "presentation-only" login kept in the flow as if it were authentication | `REJECTED` | A security claim without a control is worse than none (`frontend/src/routes/manager-login-page.tsx` already says so) | No login in the MVP; real auth only via `P0-T18` |
| R-7 | XLSX import inside the five hours | `REJECTED` (for the MVP) | New dependency + encoding/number-format edge cases | Backlog BL-06 |
| R-8 | Introducing Playwright/axe inside the five hours | `REJECTED` (for the MVP) | Toolchain install + first-test cost exceeds the budget | Backlog BL-12 |
| R-9 | Re-implementing tax/SSO inside the new module "for isolation" | `REJECTED` | Two sources of financial truth; the engine is tested | Mandatory reuse of `compute_gross_to_net` |

---

## 3. Conflicts that require an owner decision

| # | Conflict | Documents | What is needed |
| --: | :--- | :--- | :--- |
| X-1 | The new product direction vs the accepted minimal boundary | Owner brief 2026-11-16 ↔ ADR-008 ↔ `DEC-014` (`OPEN — BLOCKING`) | Record PB-D01 as a superseding ADR (recommend `ADR-010`), amend ADR-008's scope clause, resolve DEC-014 |
| X-2 | "One user type (manager)" vs the 7-role identity schema | PB-D02 ↔ ADR-006 / `0002_identity_foundation.py` | Confirm that Phase 1 uses one operator role and the 7 roles remain an unexercised foundation |
| X-3 | Examples presented as weights | Owner brief §4 ↔ PB-D03 | Owner confirms real criteria/weights before any non-demo use |
| X-4 | Statutory engine version | `PROJECT_STATUS §2` says `0.3.0-payroll-engine`; code says `0.2.0-payroll-engine` (`app/engines/__init__.py:80`) | Correct the document or bump deliberately with a changelog entry |
| X-5 | WBS `P0-T05 = NOT_STARTED` vs `0002` + `identity.py` implementation | `EXECUTION_PLAN §14.3` ↔ code | Advance the status with evidence and a recorded explanation |
| X-6 | Documentation counts (86 vs 88 tasks; 678/105 vs 735/1 tests; "self-skip" integration suites) | `PROJECT_STATUS`, `PROJECT_STATE`, `README` ↔ observed runs in `docs/CURRENT_STATE.md §1` | Refresh from the evidence register |

**Resolution note (2026-11-17, ADR-010 approved):** **X-1 is resolved** (ADR-010 accepted as written, prospective, effective 2026-11-17; ADR-008/009 notes and the DEC-014 Modules-A/D resolution recorded in their owning documents). **X-2 is resolved** (PB-D02 confirmed; the 7 roles remain an unexercised foundation). **X-3…X-6 remain unresolved** and are untouched pending owner authorization of the reconciliation edits. The statement that none of these conflicts was resolved by editing an existing document was true when written on 2026-11-16 and is superseded by this dated note only.

---

## 4. Change control

| Rule | Detail |
| :--- | :--- |
| New entry | Any product/architecture question discovered during work is added within one working day, with status and consequences |
| Promotion | Only the Project Owner may move `PROVISIONAL` → `CONFIRMED`; `OPEN` → `CONFIRMED` for scope matters also requires an ADR |
| Rejection | A rejected approach stays listed; re-proposing it requires a new entry referencing the rejection |
| Cross-reference | Entries that block historical tasks name the task IDs; entries that block MVP tasks name `MVP-xx` |
| Non-duplication | Statutory/legal questions belong in `docs/DECISIONS_REGISTER.md`, not here |
