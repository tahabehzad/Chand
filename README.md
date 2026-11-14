# Pish Hesabdari (پیش‌حسابداری)

> **Pre-employment compensation intelligence and evidentiary verification for the Iranian labour market.**

An enterprise platform that turns a candidate's *verified* records into a legally defensible employment offer: exact Iranian statutory wage, tax and Social Security computation; Total Cost to Employer; severance and termination-liability modelling; document forensics; four-way experience disambiguation; and market benchmarking — every figure reproducible, provenance-tagged and admissible before a labour dispute board.

**It is not** an accounting package, a payroll execution system, an HRIS, or a recruitment marketplace. See [ADR-004](docs/adr/ADR-004-phase-1-product-boundary-prehire-scope.md).

---

## Start here

| If you are… | Read |
| :--- | :--- |
| **A new engineer or agent** | [`docs/PISH_HESABDARI_HOLY_BIBLE.md`](docs/PISH_HESABDARI_HOLY_BIBLE.md) — the master knowledge base. Then [`AGENTS.md`](AGENTS.md). |
| **Deciding something** | [`docs/DECISION_REQUIRED_FROM_OWNER.md`](docs/DECISION_REQUIRED_FROM_OWNER.md) — what is waiting on the owner. |
| **Picking up Phase 0 work** | [`docs/PHASE_0_BOOTSTRAP_PLAN.md`](docs/PHASE_0_BOOTSTRAP_PLAN.md) — the task sequence and the exact next task. |
| **Checking the current state** | [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md) — verified status, not aspiration. |
| **Setting up a machine** | [`docs/ENVIRONMENT_INVENTORY.md`](docs/ENVIRONMENT_INVENTORY.md) — verified tools, versions and gaps. |

**The Holy Bible is authoritative for project knowledge.** This README is only an entry point; it deliberately does not restate it.

---

## Document authority

Binding order — when two documents conflict, the higher wins and the lower must be corrected.

| Rank | Class | Where |
| :--: | :--- | :--- |
| 1 | Accepted ADRs | `docs/adr/ADR-001` … `ADR-004` |
| 2 | Authoritative product & technical specification | `REMEDIATED_TECHNICAL_SPECIFICATION_V2.md` |
| 3 | Red-team findings and dispositions | `PHASE_1_RED_TEAM_AUDIT.md` |
| 4 | Execution package | `docs/EXECUTION_PLAN.md`, `docs/specs/*`, `docs/DECISIONS_REGISTER.md` |
| 5 | Historical research (not superseded content only) | `RESEARCH_GAP…md`, the three `.docx` files |
| 6 | Superseded | `PHASE_1_FINAL_AUDIT_BRIEF.md` |

`ADR-005` is **PROPOSED** and binds nothing.

---

## Current state — read before you plan anything

| | |
| :--- | :--- |
| Implementation | **0 %.** 86 of 86 WBS tasks are `NOT_STARTED` (82) or `BLOCKED` (4). No application source code exists. |
| Active statutory baseline | **1404 SH** (`1404.1`, `VERIFIED`). 1405 is transcribed but **not** four-eyes verified and **must not** be activated. |
| Roadmap | Five phases over 20 weeks. **Do not rewrite it.** |
| Phase readiness | Phase 0 `READY WITH CONDITIONS`; Phases 1 and 2 `BLOCKED`; Phases 3 and 4 `READY WITH CONDITIONS`. |
| Open decisions | 17 register entries (14 blocking) + 1 proposed ADR. |

---

## Repository layout

Current state of the tree (target layout is `docs/specs/DEPLOYMENT.md` §2.2):

```
.
├── AGENTS.md                     agent operating rules
├── README.md                     this file
├── .editorconfig  .gitattributes  .gitignore
├── .agents/skills/*/SKILL.md     11 engineering behaviour contracts
├── backend/
│   ├── pyproject.toml            PEP 621 / uv project definition
│   ├── uv.lock                   committed, exact pins
│   ├── ruff.toml  mypy.ini       lint / strict typing
│   ├── .env.example              environment KEYS only, no values
│   ├── app/                      application package (scaffolded, empty)
│   │   ├── api/v1/  core/  engines/  models/  schemas/  services/
│   ├── tests/                    (scaffolded, empty)
│   └── data/seeds/               statutory rule sets
│       ├── statutory_rules_1404.yaml   VERIFIED, active, immutable
│       └── statutory_rules_1405.yaml   placeholder, all null, INACTIVE
├── docs/
│   ├── PISH_HESABDARI_HOLY_BIBLE.md    ← master knowledge base
│   ├── adr/  specs/                   accepted ADRs, subordinate specifications
│   ├── EXECUTION_PLAN.md              the 86-task WBS
│   ├── DECISIONS_REGISTER.md          open decisions and blockers
│   ├── IMPLEMENTATION_READINESS.md    per-phase readiness
│   └── …control files (see below)
├── infra/                        (not yet created — WBS P0-T17)
├── frontend/                     (not yet created — WBS P3-T01)
└── <historical .docx and .md research corpus>
```

---

## Development setup (proposed — not yet executed)

> The environment was **verified** but **dependencies are not installed**. `uv sync` has deliberately not been run: it installs ~166 packages and creates `backend/.venv`. See [`docs/DECISION_REQUIRED_FROM_OWNER.md`](docs/DECISION_REQUIRED_FROM_OWNER.md) (DEC-A).

```powershell
# one-time, from the repository root
cd backend
uv python install 3.12        # uv already has a managed CPython 3.12.9 present
uv sync --frozen --all-groups # installs from the committed uv.lock
uv run ruff check .
uv run ruff format --check .
uv run mypy app
uv run pytest -q
```

Local services (PostgreSQL 16 + an S3-compatible object store) are described in `docs/specs/DEPLOYMENT.md` §2.5 and §5. **The Docker daemon is not currently running.**

---

## Hard rules for every contributor and every agent

1. **Never activate the 1405 rule set.** The loader must fail closed. `backend/data/seeds/statutory_rules_1405.yaml` stays inert until activation conditions A1–A8 are met (`docs/specs/STATUTORY_INGESTION.md` §7).
2. **Never modify `backend/data/seeds/statutory_rules_1404.yaml`.** It is an immutable legal artefact, hash-pinned by invariant `R-10`. Corrections create a new revision.
3. **Never use `float` for money.** `Decimal` only, `prec=34`, `ROUND_HALF_UP`, round once at the line-item boundary, surface the residual.
4. **Never hard-code a statutory rate.** Read it from the rule set; the engine never falls back silently.
5. **Never modify an accepted ADR.** Raise a superseding ADR.
6. **Never introduce a rejected technology** (`pgcrypto`, MinIO `COMPLIANCE`, bisection inversion, Next.js SSR, Redis/Celery as a mandatory broker, live job-board scraping, automated Shahkar).
7. **Never send candidate data to an external AI provider.**
8. **Never commit a secret.** `.env` is ignored; only `.env.example` (keys, no values) is tracked.

The full set, with sources, is in [`AGENTS.md`](AGENTS.md) §"Non-negotiable invariants" and the Holy Bible §3.3–§3.4.

---

## Licence and ownership

**The repository licence is undecided and is an owner decision** (`docs/DECISION_REQUIRED_FROM_OWNER.md`, DEC-E). Until it is set, treat the code as proprietary and do not redistribute it externally.
