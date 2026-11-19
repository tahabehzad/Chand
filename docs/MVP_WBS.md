# MVP Work Breakdown Structure — 300 Minutes

- **Document ID:** `DOC-MVP-WBS-001`
- **Status:** Proposed plan. No task is started. Not a guarantee of completion.
- **Total budget:** **300 minutes** — essential **280** + optional **20** = **300**.
- **Rule:** an optional task is cut before any essential task is cut; the freed minutes go to the fix buffer (MVP-18), never to new scope.
- **Acceptance criteria** referenced as `AC-01…AC-12` are defined in `docs/MVP_SCOPE.md §5`.
- **Boundary:** prototype only, loopback only, synthetic data only, in-memory storage (PB-D06), labelled advisory.

> **Superseded as planning history (2026-11-17, ADR-010).** The in-memory and no-auth boundary premises above were superseded by [ADR-010](adr/ADR-010-manager-mvp-product-scope.md) (approved by the Project Owner, effective 2026-11-17): the implemented manager prototype persists in PostgreSQL with same-migration RLS and ships a minimal real sign-in under mandatory authentication. The task allocation and budget are retained for traceability; no MVP-xx task status is claimed from this plan. Original text retained unchanged.

---

## 1. Allocation

| Phase | Theme | Minutes | Share |
| :--- | :--- | --: | --: |
| A | Repository inspection and stabilisation | 30 | 10 % |
| B | Person management | 45 | 15 % |
| C | Data entry, import and review | 60 | 20 % |
| D | Evaluation, scoring and recommendation | 75 | 25 % |
| E | Manager interface | 45 | 15 % |
| F | End-to-end verification and fixes | 45 | 15 % |
| **Total** | | **300** | **100 %** |

The owner's provisional split (30 / 45 / 60 / 75 / 45 / 45) is preserved exactly. It is a planning hypothesis, not a promise.

---

## 2. Task list

Priority: **P1** = demo cannot happen without it · **P2** = needed for an honest demo · **P3** = optional.

| ID | Task, expected output | Pri | Min | Deps | Acceptance | Relevant existing files | Risk |
| :--- | :--- | :-: | --: | :--- | :--- | :--- | :--- |
| **MVP-01** | **Baseline re-check and prototype isolation.** Confirm the gates still pass, record the exact commits and versions, decide where prototype code lives (`backend/app/prototype/`, `frontend/src/routes/prototype/`), and confirm the working tree's uncommitted work is untouched. Output: a short evidence line in the session log. | P1 | 15 | — | Backend + frontend gates observed PASS/FAIL as-is (the baseline for AC-12); no pre-existing file modified; the prototype file boundary is written down before any code. | `backend/pyproject.toml`, `frontend/package.json`, `.github/workflows/ci.yml` | Low |
| **MVP-02** | **Prototype router and environment gate.** New `APIRouter(prefix="/api/v1/prototype")` registered in `app/main.py` **only** when the environment is local; a single in-memory store module with a reset hook for tests. Output: `/api/v1/prototype/_status` returning a prototype banner payload, 404 when the gate is off. | P1 | 15 | MVP-01 | AC-11 observed: with a non-local environment the namespace returns 404; with local it returns 200. Existing routes unchanged. | `backend/app/main.py`, `backend/app/core/config.py` | Medium — a mistake here exposes an unauthenticated prototype; the gate must default to off |
| **MVP-03** | **Person entity + validation.** Dataclass/model with `person_id` (UUID), display name, role label, start date, `created_at`; validation of required fields and maximum lengths; no national ID, mobile or bank fields. Output: pure validation module. | P1 | 20 | MVP-02 | AC-02 (validation half): invalid payloads raise the project's typed error; a valid person gets a stable id; unit test covers both paths. | `backend/app/engines/errors.py` (reuse error style), `backend/app/prototype/` | Low |
| **MVP-04** | **Person endpoints.** `POST` and `GET /api/v1/prototype/people`, one error envelope, no echo of rejected input. Output: two routes. | P1 | 15 | MVP-03 | AC-02 observed by scripted HTTP: create, list, malformed refused with `code`/`detail` only. | `backend/app/api/v1/payroll.py` (pattern), `backend/app/schemas/` | Low |
| **MVP-05** | **Person list + create UI.** RTL form and table using existing primitives and Persian numerals; loading/empty/error states. Output: `/prototype/people` route. | P2 | 10 | MVP-04 | AC-02 (UI half): person created in the browser appears in the list; validation error renders in Persian; no Latin digits in display. | `frontend/src/components/ui/*`, `src/lib/*`, `src/app/router.tsx` | Medium — 10 min is tight; if it slips, the API check stands in (state it) |
| **MVP-06** | **Observation entity + manual entry.** Observation = person, period label, metric code, raw value, source `manual`, validation state; typed refusals for unknown person, unknown metric, negative value. Output: model + `POST /api/v1/prototype/observations`. | P1 | 25 | MVP-03 | AC-03 observed; one person can hold several observations; an unknown `person_id` is refused. | `backend/app/prototype/`, `backend/app/schemas/payroll.py` (naming conventions) | Medium — metric semantics are provisional (PB-D03) |
| **MVP-07** | **(OPTIONAL) CSV import.** Single-file upload, UTF-8, fixed header contract, per-row validation with row-level errors, `import_batch` with source tag and row counts. Output: `POST /api/v1/prototype/imports`. | P3 | 20 | MVP-06 | AC-04 style: 5 rows → 4 valid + 1 rejected with a reason; batch recorded. Cut entirely if Phase C runs late. | — (new); no new dependency | High — file parsing and encoding edge cases consume the whole slot |
| **MVP-08** | **Review / correct / reject.** `PATCH` an observation value, `POST` a rejection; rejected rows are excluded from scoring input. Output: two routes + a review list in the UI (minimal table). | P1 | 15 | MVP-06 | AC-04 observed: a rejected observation never appears in `observations_used`. | `backend/app/prototype/` | Medium |
| **MVP-09** | **Versioned rule set `perf-v1`.** Declarative criteria (sales, quality, attendance, responsibility), normalisation bounds, weights (40/30/20/10), missing-data policy, published as an immutable object with a version string and a validation that weights sum to exactly `Decimal(1)`. Output: `rules.py` + docs note that the weights are **provisional**. | P1 | 25 | MVP-06 | AC-05: weights sum to 1 exactly; the version string is emitted; changing a weight without a version change is impossible by construction. | `backend/app/engines/valuation.py` (`ValuationWeights` pattern) | Medium — criteria are examples, must be labelled |
| **MVP-10** | **Scoring engine.** Deterministic Decimal scoring: per-criterion normalised value and contribution, total 0–100, missing criteria reported, no float, no clock, no environment read. Output: `score.py` + unit tests. | P1 | 25 | MVP-09 | AC-06 and AC-07 observed; AC-08 covered by a missing-metric test; an AST/grep check shows no float literal. | `backend/app/engines/money.py` (`round_half_up`) | Medium — normalisation choices are judgement calls; publish them |
| **MVP-11** | **Recommendation + statutory costing.** Score → band position → suggested gross → delta vs current pay; cost the suggestion with `compute_gross_to_net`; emit `advisory: true`, `statutory: false`, model/rule/engine versions and a SHA-256 over canonical JSON. Output: `recommendation.py` + `POST /api/v1/prototype/recommendations`. | P1 | 15 | MVP-10 | AC-09 observed; one costing replayable through the existing simulation endpoint. | `backend/app/services/payroll_service.py`, `app/services/valuation_service.py` | High — reuse must be a call, not a re-implementation |
| **MVP-12** | **Prototype unit/API tests.** One test per refusal code, the weight-sum invariant, determinism, rejection exclusion, and one end-to-end API test. Output: `backend/tests/unit/test_prototype_*.py`, `backend/tests/api/test_prototype_*.py`. | P1 | 10 | MVP-11 | AC-05…AC-09 (test half): `pytest` for the new files passes; the pre-existing suite still passes. | `backend/tests/unit/*`, `backend/tests/api/*` | Medium — 10 min only covers the critical paths |
| **MVP-13** | **Recommendation review screen.** Displays score, criterion table, observations used, weights, suggested gross + delta, statutory net/employer cost, explanation strings; approve / edit / reject controls. Output: `/prototype/recommendations/:id`. | P1 | 20 | MVP-11, MVP-05 | AC-10 (UI half) observed; every displayed figure equals the API response. | `frontend/src/routes/proposal-page.tsx` (structure), `src/components/ui/*`, `src/api/*` | Medium |
| **MVP-14** | **Dashboard.** Counts of people, pending recommendations, recent decisions; prototype banner; link into the flow. Output: `/prototype` landing page. | P2 | 15 | MVP-04, MVP-11 | AC-01 observed; banner text is explicit; no synthetic figure is presented as statutory. | `frontend/src/routes/overview-page.tsx` (pattern) | Low |
| **MVP-15** | **Decision persistence + history.** `POST /api/v1/prototype/recommendations/{id}/decision` storing approve/edit/reject, comment, timestamp; read-back list. Output: route + store + history panel. | P1 | 10 | MVP-11 | AC-10 observed by API read-back; an edited amount preserves the original suggestion and the reason. | `backend/app/prototype/` | Low |
| **MVP-16** | **End-to-end verification.** Scripted HTTP sequence covering steps 1–11 of the demo, then a manual browser walkthrough of the same steps; record PASS/FAIL per step. Output: verification log. | P1 | 25 | MVP-13, MVP-15 | AC-01…AC-11 each marked PASS/FAIL/NOT RUN with the command or observation that produced it. | `docs/MVP_SCOPE.md §2`, `§5` | High — this is where hidden integration breaks surface |
| **MVP-17** | **Evidence record.** Append the observed results, the cut optional task (if any) and the first incomplete item to `docs/CURRENT_STATE.md`. Output: a short, honest evidence block; no status inflation. | P1 | 10 | MVP-16 | AC-01…AC-12 evidence record: the block distinguishes verified from unverified and names the commands run. | `docs/CURRENT_STATE.md` | Low |
| **MVP-18** | **Fix buffer.** Repair regressions found by MVP-16, then re-run only the affected checks. Output: a green or explicitly red result. | P1 | 10 | MVP-16 | AC-12 (regression re-run): any money-path failure is fixed, never skipped; anything unfixed is reported as a limitation. | — | Medium — 10 minutes is a floor, not a guarantee |

---

## 3. Totals

| Phase | Tasks | Essential | Optional | Minutes |
| :--- | :--- | --: | --: | --: |
| A | MVP-01, MVP-02 | 2 | 0 | 30 |
| B | MVP-03, MVP-04, MVP-05 | 3 | 0 | 45 |
| C | MVP-06, MVP-07, MVP-08 | 2 | 1 | 60 |
| D | MVP-09, MVP-10, MVP-11, MVP-12 | 4 | 0 | 75 |
| E | MVP-13, MVP-14, MVP-15 | 3 | 0 | 45 |
| F | MVP-16, MVP-17, MVP-18 | 3 | 0 | 45 |
| **Total** | **18 tasks** | **17** | **1** | **300** |

Essential = **280 min** · Optional = **20 min** · Total = **300 min = 5 h**.

## 4. Critical path

```
MVP-01 → MVP-02 → MVP-03 → MVP-06 → MVP-09 → MVP-10 → MVP-11
        → MVP-13 → MVP-15 → MVP-16 → MVP-17 → MVP-18
```

`MVP-04`/`MVP-05` parallelise beside the path; `MVP-07` is a detached optional branch; `MVP-08` sits between `MVP-06` and `MVP-09`; `MVP-12` and `MVP-14` run beside the path.

## 5. Cut line and honesty rules

1. **Cut order if late:** `MVP-07` (CSV) → `MVP-14` (dashboard) → `MVP-05` (person UI, use the API/curl walkthrough and say so).
2. **Never cut:** determinism test, rejection exclusion, advisory labelling, environment gate, evidence record.
3. **No weakened assertion.** A failing money path is a defect (`AGENTS.md §11`).
4. **No hidden scope.** Anything not listed here is out; it goes to `docs/FUTURE_BACKLOG.md`.
5. **Report reality.** If the five hours end mid-phase, the final message states the last completed task, the first incomplete one, and the observed failures. A partial demo presented as complete is a defect.

## 6. Risks to the 300 minutes

| Risk | Likelihood | Effect | Mitigation |
| :--- | :--: | :--- | :--- |
| Front-end integration takes longer than the UI budget | High | Demo only via API | Keep `MVP-05`/`MVP-14` minimal; the review screen (MVP-13) is the one non-negotiable surface |
| Evaluation criteria are not yet approved | Certain | Score is provisional | Label `perf-v1` provisional in response and UI (PB-D03) |
| `pnpm` absence forces workarounds | Certain | Time lost on tooling | Use `node_modules/.bin` directly, as done in the audit |
| Prototype endpoint accidentally enabled outside local | Medium | Unauthenticated exposure | `MVP-02` gate plus AC-11 test |
| In-memory store surprises with ordering/ids | Low | Test flakiness | Deterministic ids, ordered reads |
| Scope creep into persistence/authentication | Medium | Budget overrun | `docs/MVP_SCOPE.md §4` is the exclusion list; no extension without owner instruction |
