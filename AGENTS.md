# AGENTS.md — Operating Rules for Pish Hesabdari

Behaviour contract for every contributor and agent. Accepted ADRs and the Holy Bible govern product decisions; report conflicts rather than silently choosing an implementation.

## 1. Start with the task

The product is the **statutory payroll calculation engine** (ADR-008, accepted 2026-11-15): SSO, progressive income tax, net pay, overtime/night shift, Sanavat, Eydi, employer CTC and the Article 11 worst case — pure functions plus one minimal API endpoint on the verified **1404 SH** baseline. The prior pre-employment platform scope (ADR-004's module list) is superseded; the five-phase/20-week roadmap table is retained for traceability. 1405 is transcribed, unverified and inactive.

Read this file, then use **docs/DOCUMENTATION_INDEX.md §0** to select context. Before your first change, read the Holy Bible **§0.3, §13.1 and §13.8**, the relevant §3 requirements and the applicable primary sources. Read §0.4 only when source provenance is relevant; it is a historical inventory. Do not load the entire Holy Bible, WBS, changelog or research corpus by default.

- Current delivery status: **docs/PROJECT_STATUS.md §2**; task dependencies/acceptance: **docs/EXECUTION_PLAN.md §14.3**.
- Latest recorded application/collector evidence: **docs/BOOTSTRAP_CHANGELOG.md §16**; PostgreSQL runtime: §15; documentation maintenance: §13. Historical test results are not a fresh runtime check.
- Decisions: **docs/DECISIONS_REGISTER.md** and **docs/ADR_INDEX.md**. ADR-006, ADR-007 and ADR-008 are accepted; ADR-005 remains proposed.
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

### Financial
7. Decimal only: no float literal in `backend/app/engines/**`; `getcontext().prec = 34`; `ROUND_HALF_UP` only; no Python `round()` on money.
8. Round once at the line-item boundary. Surface a signed `rounding_residual_rial` for rounded-line/rounded-total differences (≤ 1 Rial per line).
9. Every emitted figure carries `rule_version`, `rule_set_status`, `engine_version`, `calculation_hash`, `generated_at` and per-field provenance.
10. Unknown statutory values stay unknown: never coerce null to zero; raise `StatutoryParameterUnavailable`.
11. Calculation is a pure function of `(inputs, rule_set_version)`: no clock, randomness, network or environment reads in the calculation path.

### Security
12. Every tenant table gets `tenant_id`, an RLS policy and `FORCE ROW LEVEL SECURITY` in the same migration.
13. Encrypt PII in the application layer with AES-256-GCM; keys never enter the database. Exact lookup uses HMAC-SHA256 blind indexing with an isolated pepper; no `pgcrypto`.
14. The audit ledger is append-only; the database rejects UPDATE/DELETE.
15. Never print, log, commit or transmit secrets, National IDs, mobile numbers, Sheba numbers or real candidate salaries.

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
