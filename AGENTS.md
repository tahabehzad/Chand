# AGENTS.md — Operating Rules for Pish Hesabdari

Behaviour contract for every contributor and agent. Accepted ADRs and the Holy Bible govern product decisions; report conflicts rather than silently choosing an implementation.

## 0. Language

Persian (Farsi) for all user-facing prose; English for code, identifiers, paths, commands and API strings. See §12.

## 1. Start with the task

The active product is the **resume analysis and monthly salary estimation tool** (ADR-013, accepted 2026-11-17; ADR-014, accepted 2026-11-18): one manager enters a candidate's career information (job title, experience, skills, education, city, employment type, seniority level), and the system returns a suggested monthly salary range (P25…P75) with a primary estimate (median), contributing factors, and confidence level based on verified Iranian labor market data. The prior statutory payroll calculation engine scope (ADR-008) remains implemented in code but is superseded as the active product direction. The earlier pre-employment platform scope (ADR-004) is historical.

Read this file, then use **docs/DOCUMENTATION_INDEX.md §0** to select context. For the active salary estimation product, refer to **docs/PRODUCT_VISION.md**, **docs/PRODUCT_SCOPE.md**, **docs/SALARY_ESTIMATION_SPEC.md**, **docs/LABOR_MARKET_DATA_SPEC.md**, **docs/DATA_MODEL_SPEC.md**, and **docs/ARCHITECTURE.md**.

- Current delivery status: **docs/PROJECT_STATUS.md §2**; task dependencies/acceptance: **docs/EXECUTION_PLAN.md**.
- Derived snapshot (no independent facts): **PROJECT_STATE.md**. If it disagrees with an owner above, the owner wins and the snapshot is wrong.
- Latest recorded application and UI evidence: **docs/BOOTSTRAP_CHANGELOG.md §28**; engine verification: §23–§24; market salary engine verification: ADR-014 (82 domain tests + 13 E2E tests PASS; 129 frontend tests PASS).
- Decisions: **docs/DECISIONS_REGISTER.md**, **docs/OPEN_DECISIONS.md**, and **docs/ADR_INDEX.md**. Accepted ADRs: 001–004, 006, 007, 008, 009, 010, 011, 012, 013, and 014; ADR-005 remains proposed.
- Research Markdown/DOCX is historical and contains rejected recommendations. Consult only for a specific evidence question after checking the supersession index.

## 2. Non-negotiable invariants

Violating any invariant is a defect regardless of tests.

### Domain
1. Keep **total professional experience**, **relevant occupational experience**, **Social Security contribution history**, and **current-employer tenure / legally recognised base seniority** separate.
2. Never double-count overlapping employment periods.
3. Statutory requirements are hard constraints, never scoring bonuses.
4. A forensic anomaly is not a fraud verdict; route it to a human.
5. Human review/adjudication remains mandatory where specified.
6. Historical simulations retain their original rule-set reference; never recompute or rewrite them.
7. **Refuse instead of fabricate (ADR-014):** When no verified market observation covers a profile cohort, the engine must return `insufficient_data` with the measured counts and reasons; it must **never** invent salary numbers, interpolate blindly, or fall back to an unmeasured national average. AI is restricted to resume text parsing and must never generate salary figures.

### Financial
8. Decimal only: no float literal in `backend/app/engines/**` or `backend/app/domain/salary_estimation/**`; `getcontext().prec = 34`; `ROUND_HALF_UP` only; no Python `round()` on money.
9. Round once at the line-item boundary. Surface a signed `rounding_residual_rial` for rounded-line/rounded-total differences (≤ 1 Rial per line).
10. Every emitted figure carries `rule_version` / `estimation_version`, `engine_version`, `calculation_hash`, `generated_at` and per-field provenance.
11. Unknown statutory values stay unknown: never coerce null to zero; raise `StatutoryParameterUnavailable`.
12. Calculation is a pure function of `(inputs, rule_set_version / market_observations)`: no clock, randomness, network or environment reads in the calculation path.

### Security
13. Tenant tables get `tenant_id`, an RLS policy and `FORCE ROW LEVEL SECURITY`. Global reference tables (e.g. `market_salary_observations`, `market_salary_aggregates`, `market_data_sources`) hold no tenant data and require no RLS per ADR-007 / ADR-014.
14. Encrypt PII in the application layer with AES-256-GCM when high-sensitivity personal data is stored; keys never enter the database. Exact lookup uses HMAC-SHA256 blind indexing with an isolated pepper.
15. The audit ledger is append-only; the database rejects UPDATE/DELETE.
16. Never print, log, commit or transmit secrets, National IDs, mobile numbers, Sheba numbers or real candidate salaries.

## 3. Authority and change control

Work only within an approved task's ownership and decisions. Code, tests, docs, migrations and configuration templates must conform to those decisions. Factual corrections to rank-4 documents require a changelog entry.

**Never modify ADR-001…004, `backend/data/seeds/statutory_rules_1404.yaml`, or the roadmap in REMEDIATED §7.** Accepted decisions, including ADR-006, require a superseding ADR to change. Do not approve ADR-005, activate 1405, select an unresolved authentication/schema variant, implement an unresolved production migration, or write financial logic from an unverified assumption without explicit owner approval.

Do not commit/push without explicit instruction. Do not delete or rewrite historical research. Propose product changes through **docs/DECISION_REQUIRED_FROM_OWNER.md**; propose unresolved decisions through **docs/DECISIONS_REGISTER.md**.

## 4. Before implementation

Find the exact WBS ID (§14.3), read its specification, check dependencies (D) and decisions (B), confirm measurable acceptance criteria (AC), assign one accountable owner, define file ownership/integration boundaries and verification, then record actual status.

Documentation, a plan or a scaffold does not make a task complete. Mark `COMPLETED` only after implementation and acceptance criteria are verified; never change status to bypass a blocker.

## 5. Task status vocabulary

Tasks: NOT_STARTED · IN_PROGRESS · BLOCKED · READY_FOR_REVIEW · APPROVED · COMPLETED. Decisions: OPEN · OPEN — BLOCKING · OPEN — NON-BLOCKING · RESOLVED · REJECTED. ADRs: Accepted · Proposed · Superseded · Deprecated · Rejected. Rule sets: DRAFT · UNDER_REVIEW · VERIFIED · ACTIVE · RETIRED · REJECTED.

## 6. Working with agents and subagents

One owner per task. Give agents the actual required documents, not substitute summaries; required specifications must be read. Never let two agents edit the same file: partition ownership or use separate Git worktrees. A security-sensitive or financial change requires independent review by someone who did not write it. Record actual delegation, decisions and verification in BOOTSTRAP_CHANGELOG; never claim planned roles are active. See **docs/AGENT_OPERATING_MODEL.md** when delegating.

## 7. Behaviour contracts

Load only applicable `.agents/skills/*/SKILL.md` contracts:
- Monetary change: **financial-data-integrity**; engine change: also **iranian-payroll-engineering**.
- Database/security: **database-engineering**, **security-threat-model**.
- Persian UI/PDF: **persian-rtl-engineering**.
- LLM search/grounding: **llm-market-grounding**.
- Architecture/specification/review/modeling/discovery/ADR work: the matching existing skill.

Skills constrain how to work, not product scope. **Slow-path execution remains undecided**: software-architecture and REMEDIATED §3.1 name BackgroundTasks, but ADR-005 is proposed and P2-T04 remains blocked. Keep the JobQueue interface boundary; do not treat a proposed queue, cloud fallback or unresolved PDF preference as approved. See Holy Bible §4.8 and §13.5.

## 8. Security and operational safety

Use least privilege; do not assume administrator access. Before destructive/irreversible action, state the exact action, affected files/services and rollback, then obtain explicit approval. Never weaken controls/invariants, run untrusted elevated scripts, send candidate/personal data to unapproved services, connect to production or deploy publicly. Secrets must never enter images, compose files, logs, errors or tracebacks.

## 9. Verification discipline

Run and observe verification yourself; an agent's claim is insufficient. Record exact commands/results as **PASS / FAIL / NOT RUN** in BOOTSTRAP_CHANGELOG. Record assumptions in the task's Blocking issues and recheck at the phase gate. For documentation-only changes, check links, factual consistency and scope; do not run write-producing application tests unnecessarily.

## 10. Domain terminology

Use statutory Persian terms in user-facing strings. For vocabulary, read Holy Bible §2 and the payroll skill only when relevant; never merge مزد مبنا, مزد ثابت, حقوق, سنوات or پایه سنوات.

## 11. Escalation

- Specification versus accepted ADR: stop the affected work; raise the conflict in DECISIONS_REGISTER.
- Unavailable statutory value: stop; fail closed, never estimate.
- Failed money-path test: stop and treat as a defect; never quarantine it.
- Security defect: stop the affected path, preserve evidence and follow DEPLOYMENT §9.3.
- Legal conclusion: cite the instrument/article or label it UNVERIFIED.

Changes to this file are recorded in **docs/BOOTSTRAP_CHANGELOG.md**.

## 12. Language and communication
- Answer in the shortest form that is correct: no preamble, no restating of the request, no summary of what the user already has in context.
- Do not use Persian numerals inside code, commands, identifiers or test data; use them only in Persian UI text where the frontend policy requires it (SPEC-FE-001).

## 13. Context and token discipline

1. Never scan the whole repository for a small task; open only task-relevant files.
2. Prefer targeted search (`rg`), `git diff` and explicit paths over directory listings or reading many files "to be safe".
3. Never walk or dump `node_modules/`, `backend/.venv/`, `__pycache__/`, caches or build output.
4. Read an unchanged file once per session; rely on the current context instead of rereading.
5. Run the narrowest test/lint/type scope that answers the question; widen only when the result demands it.
6. Do not repeat an identical command, and do not print full tracebacks, secrets or whole logs — filter to the relevant lines.
7. Do not delegate to a subagent what you can do directly; one owner per task (§6).
8. Do not create a document, table or summary that already has an owner; link to it (DOCUMENTATION_INDEX §1).
9. Load a skill body or a specification only when the task matches, and read the referenced sections rather than whole large documents.
10. Prefer deterministic local tools (`rg`, `ruff`, `mypy`, `pytest`, `tsc`, `git`) over model reasoning for search, formatting, static analysis and routine checks.
11. Install no dependency or tool without a stated, task-specific need; no paid API or service (§8).

## 14. Documentation set

Only three documents carry standing instructions; everything else is owned elsewhere.

| Path | Role |
| :--- | :--- |
| `AGENTS.md` | This file: operating rules and context discipline. |
| `README.md` | Human entry point: scope, repository layout, run and verify commands. |
| `PROJECT_STATE.md` | Derived snapshot. **No independent facts** — delivery state stays in `docs/PROJECT_STATUS.md`, tasks in `docs/EXECUTION_PLAN.md §14.3`, decisions in `docs/DECISIONS_REGISTER.md` and `docs/adr/`, verification in `docs/BOOTSTRAP_CHANGELOG.md`. |

Do not add a top-level Markdown document, or duplicate an existing table, without owner approval. Corrections to an owned document go to that document, not into a new one.

## 15. Coding conventions

- **Python:** ruff (line length 100, target `py312`) and `mypy --strict`; type hints on every signature; `from __future__ import annotations` in new modules; module docstrings follow the existing **Authority / Related / Scope** header pattern; Decimal for money (§2 Financial).
- **TypeScript/React:** function components, `import type` for types, existing Tailwind design tokens and `frontend/src/components/ui/*` primitives; no new UI or state library.
- **Tests:** colocated `*.test.ts(x)` on the frontend, `backend/tests/{unit,api,property,integration}` on the backend; a money-path test failure is a defect (§11), never a skipped test.
- **Money paths:** the rules in §2 (Financial) override any stylistic preference, including in tests and fixtures.

## 16. Git safety

- Do not commit, push, amend, reset, force-push, clean or rewrite history without an explicit owner instruction.
- Never stage or commit secrets, `.env*` files, `.secrets/`, key material, National IDs, mobile numbers, Sheba numbers or real salary data.
- Preserve existing uncommitted work; never overwrite or revert another contributor's changes.
- Keep changes reviewable and scoped to the approved task; configuration and generated files are not a place to hide behaviour change.
