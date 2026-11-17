# MVP Scope — Five-Hour Demonstration

- **Document ID:** `DOC-MVP-001`
- **Status:** Proposed plan — not started. Nothing in this document has been built at the time of writing.
- **Budget:** **300 minutes (5 h)**, owner-declared on 2026-11-16.
- **Nature:** a **labelled prototype**, not a product release. It completes no historical WBS task and passes no phase gate.
- **Depends on:** `PB-D01` (scope), `PB-D03` (criteria/weights), `PB-D06` (persistence). Until PB-D01 is recorded as an ADR, this is a demonstration of the direction, explicitly outside the accepted ADR-008 boundary.
- **Task plan:** `docs/MVP_WBS.md`

> **Superseded as planning history (2026-11-17, ADR-010).** [ADR-010](adr/ADR-010-manager-mvp-product-scope.md), approved by the Project Owner effective 2026-11-17, supersedes this plan's premises for the implemented manager prototype: persistence is PostgreSQL (not in-memory), a minimal real sign-in exists (PB-D09 superseded), and the prototype API is `/api/v1/auth` + `/api/v1/manager` under mandatory authentication (PB-D11 superseded). The five-hour budget, scenario and task plan are retained below for traceability; **no acceptance criterion of this plan is claimed as met**, and the prototype remains loopback/dev-only, synthetic-data-only and not production-ready (ADR-010 §3). Original text retained unchanged.

---

## 1. Goal in one sentence

Demonstrate, end to end and on one machine, that a manager can turn raw performance data about a person into a **score and a compensation recommendation whose every number can be explained**.

## 2. The exact demonstration scenario

Synthetic data only. Names and figures below are fixtures, not real people or real salaries.

| Step | Actor action | Expected system response |
| --: | :--- | :--- |
| 1 | Open `http://127.0.0.1:5273/` | Dashboard loads with the prototype banner ("نمونهٔ نمایشی — داده‌های ساختگی"), 0 people |
| 2 | Create person **«کارمند نمونهٔ ۱»**, role «فروش», start date 1403-01-01 | Person appears in list with a stable `person_id`; invalid input is refused with a typed error |
| 3 | Create a second person **«کارمند نمونهٔ ۲»** | Two people listed |
| 4 | Enter performance observations for person 1, period `1404-Q2`: sales = 1,200,000,000 Rial; quality score 82; attendance days 29/30; responsibility 4/5 | Observations listed with source `manual`, validation state `valid` |
| 5 | (Optional) Import a 5-row CSV for person 2 | Import batch recorded; 4 rows valid, 1 row rejected with a row-level reason |
| 6 | Open the review screen, correct one value, reject one row | Corrections and rejections recorded; rejected rows excluded from scoring |
| 7 | Run evaluation for person 1 | Score 0–100 with a per-criterion table: raw value, normalised value, weight, contribution |
| 8 | Generate recommendation with band 80,000,000 – 140,000,000 Rial and current pay 100,000,000 Rial | Suggested gross, delta, position in band, **plus** statutory net and employer cost from the existing engine, all labelled advisory |
| 9 | Open the explanation | Lists observations used (with source and period), weights, rule-set version (`perf-v1`), engine version, calculation hash |
| 10 | Approve with a comment | Decision stored; recommendation leaves the pending list; dashboard count updates |
| 11 | Generate a second recommendation for person 2 and **reject** it with a reason | Rejection stored; the approved one remains visible in history |
| 12 | Restart the server | Data is empty again — the prototype is in-memory (documented compromise) |

## 3. Included in the five hours

| Item | Notes |
| :--- | :--- |
| Person create + list + validation | In-memory, synthetic only |
| Manual observation entry | Metric, period, value, source tag |
| CSV import (single file, UTF-8) | **Optional** task MVP-07; dropped first if time runs out |
| Review / correct / reject observations | Excluded rows cannot be scored |
| Versioned evaluation rule set `perf-v1` | Criteria + weights + normalisation + missing-data policy |
| Deterministic scoring with per-criterion contributions | Decimal, 0–100, published weights |
| Recommendation generation | Band position, suggested gross, delta, explanation |
| Statutory costing of the suggestion | Reuses `compute_gross_to_net`; labelled advisory |
| Approve / edit / reject with comment | Stored in memory with timestamp |
| Basic dashboard | People count, pending recommendations, recent decisions |
| Prototype banner and environment gate | Loopback only; disabled outside `APP_ENV=local` |

## 4. Explicitly excluded

Document authenticity/OCR/forensics · Shahkar/OTP and any external identity check · bank transfers · employee portal · mobile app · multi-tenant/RBAC · real authentication (no fake login) · PostgreSQL persistence for the new entities · audit hash chain · key management · PII encryption of new fields · PDF export · advanced statistical/actuarial valuation · AI scoring · external connectors · duplicate/identity auto-matching · multi-period history comparison · load/performance testing · E2E automation framework · production deployment.

Each is mapped to a backlog entry in `docs/FUTURE_BACKLOG.md`.

## 5. MVP acceptance criteria

A criterion is met only when observed, not when coded.

| ID | Criterion | Verification |
| :--- | :--- | :--- |
| AC-01 | Server and SPA start locally on loopback; dashboard renders RTL with the prototype banner | Manual browser observation + HTTP 200 on `/health/live` |
| AC-02 | A person is created and listed; a malformed person is refused with `{error:{code,detail}}` and no echoed input | Scripted HTTP check + browser |
| AC-03 | An observation is attached to exactly one person; an unknown `person_id` is refused | Scripted HTTP check |
| AC-04 | A rejected observation is excluded from the evaluation input | API response shows `observations_used` without it |
| AC-05 | The rule set version is published and its weights sum to exactly 1 (`Decimal`) | Unit test + response field `rule_set_version` |
| AC-06 | The score is deterministic: same inputs and rule version ⇒ identical score and identical `calculation_hash` | Two consecutive calls compared |
| AC-07 | Every criterion shows raw value, normalised value, weight and contribution, and contributions sum to the score | Response inspection |
| AC-08 | Missing data is handled by the published policy and reported as `missing_criteria`, never silently zero | Unit test with one metric absent |
| AC-09 | The recommendation carries suggested gross, delta vs current pay, band position, and statutory net + employer cost from the existing engine, marked `advisory: true` / `statutory: false` | Response inspection; replay one costing through `/api/v1/simulations/gross-to-net` |
| AC-10 | Approve, edit and reject each persist a decision with comment and timestamp, and the decision appears in history | Browser + API read-back |
| AC-11 | No endpoint in the prototype namespace answers when `APP_ENV != local` (or the gate is absent from the router) | Start with `APP_ENV=production`; expect 404 |
| AC-12 | The existing regression suite still passes unchanged (backend + frontend) | Re-run the documented gates; record PASS/FAIL |

## 6. Dependencies

| Dependency | Status | Effect if missing |
| :--- | :--- | :--- |
| Owner records PB-D01 (scope) | OPEN | Prototype must stay explicitly labelled and outside the product boundary |
| Owner confirms criteria/weights (PB-D03) | OPEN | Use the provisional 40/30/20/10 example, labelled provisional in UI and response |
| Persistence choice (PB-D06) | PROVISIONAL: in-memory | A restart loses data — documented compromise |
| Existing statutory engine | Available, review-ready | If it fails, drop statutory costing from the demo, keep the score explanation |
| `python -m uvicorn` + Node/Vite toolchain | Available (verified) | Manual API checks only |
| `pnpm` on PATH | **Not available**; use `node_modules/.bin` | Build/test commands adjusted, no install |
| Docker (integration tests) | Available (29.9.2) | Unchanged; MVP does not require it |

## 7. Known compromises (must be stated in the demo)

1. **In-memory storage** — data disappears on restart; no concurrency control; not a database design.
2. **No authentication** — the prototype is loopback-only and must never be exposed on a LAN or the internet. The UI says so.
3. **Synthetic data only** — no national ID, mobile, Sheba or real salary may be entered.
4. **Provisional weights** — 40/30/20/10 are examples from the owner brief, not approved rules.
5. **Advisory only** — the statutory engine costs the proposal; it does not make it lawful, and 1404 is the only active baseline.
6. **No audit trail** — decisions are not hash-chained; tamper evidence is absent.
7. **No automated E2E** — the demonstration is a scripted HTTP sequence plus a manual browser walkthrough.
8. **No duplicate detection or person matching** — two similar names stay two people.
9. **Score normalisation is deliberately simple** — linear scaling with published caps; not an actuarial model.

## 8. Definition of "five hours done"

The session ends with either:

- **A)** all essential tasks complete, AC-01…AC-12 observed, and a short evidence note appended to `docs/CURRENT_STATE.md`; or
- **B)** an honest partial result: the last completed task, the first incomplete task, the observed failures, and no claim of a working demonstration.

Optional work (CSV import) is cut before any essential task is cut. No acceptance criterion may be weakened to make the demo pass.
