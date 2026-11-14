# AGENTS.md — Operating Rules for Every Agent Working on Pish Hesabdari

> **Scope.** This file binds every human and every automated agent touching this repository. It is a **behaviour contract**, subordinate to the accepted ADRs and to `docs/PISH_HESABDARI_HOLY_BIBLE.md`. Where an agent instruction conflicts with a product decision, the product decision wins — and the conflict is reported, not silently resolved.

**Read before your first change:** `docs/PISH_HESABDARI_HOLY_BIBLE.md` (§0.3 authority, §0.4 sources, §3 requirements, §13 knowledge governance).

---

## 1. The one-minute orientation

1. The project is a **pre-employment compensation intelligence and evidentiary verification platform** for Iran.
2. The authoritative knowledge is the **Holy Bible**. Do not start from the research `.md`/`.docx` corpus — it contains rejected technologies in the present tense.
3. **0 % implemented.** 86 WBS tasks; 82 `NOT_STARTED`, 4 `BLOCKED`. No application source code exists.
4. The **only verified statutory baseline is 1404 SH**. 1405 is transcribed, unverified and **inactive**.
5. The roadmap is **five phases / 20 weeks**. It is approved. Do not rewrite, re-time or re-scope it.

---

## 2. Non-negotiable invariants

Violating any of these is a defect regardless of test results.

### Domain
1. **Total professional experience**, **relevant occupational experience**, **Social Security contribution history** and **current-employer tenure / legally recognised base seniority** are four separate dimensions. Never merge them into one "years of experience" figure.
2. **Never double-count overlapping employment periods.**
3. Statutory requirements are **hard constraints**, never scoring bonuses.
4. A forensic anomaly is **not** an automatic fraud verdict. It routes to a human.
5. Human review and adjudication remain **mandatory** where the specifications require it.
6. Historical financial simulations retain their **original** rule-set reference. Never recompute or rewrite them.

### Financial
7. **Decimal only.** No `float` literal in `backend/app/engines/**`. `getcontext().prec = 34`; `ROUND_HALF_UP` only; Python's `round()` is banned on money.
8. **Round once**, at the line-item boundary. Any difference between the sum of rounded lines and the rounded total is surfaced as a signed `rounding_residual_rial` (≤ 1 Rial per line).
9. Every emitted figure carries `rule_version`, `rule_set_status`, `engine_version`, `calculation_hash`, `generated_at` and a per-field provenance map.
10. **Unknown legal values stay unknown.** Never coerce a null statutory parameter to zero; raise `StatutoryParameterUnavailable`.
11. The engine is a **pure function** of `(inputs, rule_set_version)`. No clock, no randomness, no network, no environment reads inside a calculation path.

### Security
12. **Tenant isolation and sensitive-data protection are foundational.** `tenant_id` on every tenant table, an RLS policy, and `FORCE ROW LEVEL SECURITY` — created in the same migration.
13. PII is encrypted **in the application layer** (AES-256-GCM). Keys never enter the database. Exact-match lookup uses an HMAC-SHA256 blind index with an isolated pepper.
14. The audit ledger is **append-only**; `UPDATE`/`DELETE` are rejected by the database.
15. **Never** print, log, commit or transmit a secret, a National ID, a mobile number, a Sheba number or a real candidate's salary.

---

## 3. Authority and change control

| You may do this | You may **not** do this without explicit owner approval |
| :--- | :--- |
| Add code inside an approved task's file ownership | Modify an accepted ADR |
| Add a test, a doc, a migration consistent with an approved decision | Activate the 1405 statutory baseline |
| Correct a factual error in a rank-4 document, with a changelog entry | Modify `backend/data/seeds/statutory_rules_1404.yaml` |
| Propose a decision in `docs/DECISIONS_REGISTER.md` | Approve ADR-005 |
| Create `.gitignore`/`.editorconfig`/config templates | Choose an unresolved authentication or schema variant |
| Run local, non-destructive verification commands | Write production financial logic from an unverified assumption |
| Prepare a plan | Write production migrations that encode an unresolved decision |
| | Commit or push to a remote repository |
| | Delete or rewrite historical research documents |
| | Change the five-phase, 20-week roadmap |

**Never** modify: `docs/adr/ADR-001`…`ADR-004`, `backend/data/seeds/statutory_rules_1404.yaml`, or the roadmap in `REMEDIATED_TECHNICAL_SPECIFICATION_V2.md` §7.

---

## 4. Before you implement anything

```
1. Find the exact WBS ID              (docs/EXECUTION_PLAN.md §14.3)
2. Read its specification             (docs/specs/*, REMEDIATED)
3. Check its dependencies             (the D column)
4. Check whether its decisions are approved   (the B column; docs/DECISIONS_REGISTER.md)
5. Confirm its acceptance criteria are measurable   (the AC column)
6. Identify its file ownership and integration boundaries
7. Assign one accountable owner
8. Define the verification command or evidence
9. Record the ACTUAL task status
```

**A task may only be marked `COMPLETED` when the implementation and its acceptance criteria have actually been verified.** A document, a plan or a scaffold is not an implementation. **Never change a status to work around a blocker.**

**The current Phase 0 dependency chain is:**
`P0-T01 → P0-T02 → P0-T06 → P0-T07 → P0-T08 → P1-T04 → …`

---

## 5. Task status vocabulary

`NOT_STARTED` · `IN_PROGRESS` · `BLOCKED` · `READY_FOR_REVIEW` · `APPROVED` · `COMPLETED`

Decision status: `OPEN` · `OPEN — BLOCKING` · `OPEN — NON-BLOCKING` · `RESOLVED` · `REJECTED`
ADR status: `Accepted` · `Proposed` · `Superseded` · `Deprecated` · `Rejected`
Rule-set status: `DRAFT` · `UNDER_REVIEW` · `VERIFIED` · `ACTIVE` · `RETIRED` · `REJECTED`

---

## 6. Working with agents and subagents

- **One accountable owner per task.** Shared ownership means no ownership.
- **Give an agent the documents, not a summary of them.** An agent that has not read `SPEC-AUTH-001` must not write `P0-T05`.
- **An agent must not redefine product scope** or resolve an open decision to keep moving. If blocked, it stops and reports the blocker.
- **Never let two agents edit the same file.** Partition by file ownership, or use a Git worktree per agent.
- **Security-sensitive and financial code requires independent review** — a second agent or a red-team pass that did not write the code.
- **Keep an auditable record** of what was delegated, what was decided, and what was verified. `docs/BOOTSTRAP_CHANGELOG.md` is the running instance.
- **Do not create agents the platform cannot actually run.** Report which roles are genuinely active and which are planned. See `docs/AGENT_OPERATING_MODEL.md`.

---

## 7. Behaviour contracts

Eleven engineering contracts live in `.agents/skills/`. They are **how** to work, not **what** to build. The binding ones for this phase:

| Skill | Binding rules |
| :--- | :--- |
| `financial-data-integrity` | 31 rules — Decimal discipline, 5 reconciliation invariants, rule versioning, field-level provenance, the verification harness. **Binding on every monetary change.** |
| `iranian-payroll-engineering` | 19 rules — the statutory bases, the fail-closed loader, the two-region inverter with a mandatory boundary check, CTC and leave rules. **Binding on every engine change.** |
| `database-engineering` | `FORCE RLS` on every tenant table; ALEE + blind index; append-only audit ledger. |
| `security-threat-model` | STRIDE framing; multi-tenant isolation mandate; no `pgcrypto`. |
| `persian-rtl-engineering` | 31 rules — logical properties only, three-layer numeral policy, Jalali semantics, PDF shaping and font embedding. |
| `software-architecture` | Modular monolith; strict fast/slow path separation; fail-closed tenant queries. |
| `spec-driven-development` | No code before a complete, verifiable specification. |
| `doubt-driven-development` | Temporal reality check; statutory cross-examination; mathematical first principles. |
| `adr-authoring` | The MADR 3.0 / Nygard ADR template. |
| `actuarial-risk-modeling` | CTC without the 26-day double count; Bühlmann-Kish with the `K` clamp. |
| `product-discovery` | The boundary matrix; no feature without a validated problem statement. |

> ⚠️ **Known conflict.** The `software-architecture` skill mandates FastAPI `BackgroundTasks` for the slow path. That is the same position as `REMEDIATED` §3.1, and it is **not** the settled decision — `ADR-005` (a PostgreSQL-backed job queue) is `PROPOSED` and Phase 2's job pipeline is `BLOCKED` on it. Treat the slow-path mechanism as **undecided** and build behind a `JobQueue` interface. See the Holy Bible §4.8 and §13.5 CONF-02.

---

## 8. Security and operational safety

- **Least privilege.** Do not assume administrator access; request it.
- Before any destructive or irreversible action: state the exact action, the affected files or services, and the rollback — then get explicit approval.
- **Do not** disable a security control to make a test pass. **Do not** weaken an invariant to make CI green.
- **Do not** send candidate or personal data to an external AI provider or any unapproved service.
- **Do not** connect to production systems or deploy publicly.
- **Do not** run untrusted scripts with elevated privileges.
- **Do not** delete or rewrite historical research.
- Secrets never enter the repository, an image layer, a compose file, a log line, an error message or a traceback.

---

## 9. Verification discipline

- **Never report success based on an agent's claim.** Run the command, read the output, record both.
- Separate results into **PASS**, **FAIL** and **NOT RUN**. "Not run" is a legitimate and important answer.
- Record the exact command and the exact result in `docs/BOOTSTRAP_CHANGELOG.md`.
- Identify unverified assumptions explicitly. An assumption recorded in a task's *Blocking issues* field and re-checked at the phase gate is acceptable; an assumption made silently is not.

---

## 10. The ten-second glossary

| Persian | English | Never confuse with |
| :--- | :--- | :--- |
| مزد مبنا (*Mozd-e Mabna*) | base wage subject to SSO insurance | *Mozd-e Saabet* |
| مزد ثابت (*Mozd-e Saabet*) | fixed wage = base + continuous fixed attraction allowances | *Mozd-e Mabna* |
| حقوق (*Hoghoogh*) | total contractual entitlement | either base |
| فوق‌العاده جذب (*Fogholadeh Jazb*) | fixed, continuous attraction allowance | a variable bonus |
| حق مسکن / بن خواربار / حق اولاد | housing / grocery / child allowance | part of *Mozd-e Saabet* |
| حق سنوات (*Sanavat*) | severance — 1 month per year of service | a bonus |
| عیدی (*Eydi*) | annual bonus — 60 days base, 90 days min-wage cap | severance |
| پایه سنوات (*Payeh Sanavat*) | base-seniority daily increment | *Sanavat* |
| حکم کارگزینی (*Hokm-e Kargozini*) | appointment decree / offer letter | a contract |
| سابقه بیمه تأمین اجتماعی | Social Security contribution history | total professional experience |

User-facing Persian strings use the statutory Persian term, never an English loanword.

---

## 11. Escalation

| Situation | Action |
| :--- | :--- |
| A specification contradicts an accepted ADR | Stop; raise the conflict in `docs/DECISIONS_REGISTER.md`; do not pick a side. |
| A statutory value is unavailable | Stop; the engine must fail closed. Never estimate. |
| A test fails on a money path | Stop; treat as a defect, never as a flaky test to be quarantined. |
| An agent proposes a product change | Route to the Product Manager via `docs/DECISION_REQUIRED_FROM_OWNER.md`. |
| You find a security defect | Stop the affected path; preserve evidence; follow the SEV-1 runbook in `docs/specs/DEPLOYMENT.md` §9.3. |

---

*Maintained alongside `docs/PISH_HESABDARI_HOLY_BIBLE.md`. Any change to this file is recorded in `docs/BOOTSTRAP_CHANGELOG.md`.*
