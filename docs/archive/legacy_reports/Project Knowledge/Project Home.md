---
title: "Pish Hesabdari — Project Home"
document_id: KNOW-HOME-001
status: Active navigation layer
as_of: 2026-11-16
authority: "Navigation only — the linked project documents remain authoritative"
---

# پیش حسابداری — Project Home

> **این صفحه فقط لایهٔ ناوبری است.** منبع حقیقت، اسناد اصلی پروژه در `docs/`، `AGENTS.md` و ADRهای پذیرفته‌شده است. هر عدد یا وضعیت زیر از سند مرجع نقل شده و پیوند آن ذکر شده است. هیچ درصد پیشرفت یا وضعیت ساختگی در این صفحه وجود ندارد.

**Vault:** `C:\project\New project` — خودِ ریشهٔ پروژه؛ هیچ سند اصلی کپی یا جابه‌جا نشده است.

---

## Project Overview

### Purpose

**Pish Hesabdari (پیش حسابداری)** یک موتور محاسباتی حقوق و دستمزد قانونی برای ایران است. دامنهٔ محصول طبق **ADR-008 (Accepted, 2026-11-15)** به موتور محاسبهٔ حقوق، مالیات و بیمهٔ قانونی محدود شده است: توابع خالص به‌همراه یک endpoint حداقلی FastAPI. دامنهٔ پیشین پیش از استخدام (pre-employment platform) طبق ADR-008 superseded شده است.

### Main objectives (ADR-008 v1)

- محاسبهٔ **SSO** (سهم کارمند/کارفرما، سقف بیمه‌ای، حالت‌های ۲۹/۳۰/۳۱ روز)
- **مالیات پیش‌روندهٔ حقوق** با هر دو posture مادهٔ ۱۳۷ (posture اصلی: `conservative_inta`)
- **خالص حقوق**، اضافه‌کاری/شب‌کاری، **سنوات**، **عیدی**، **CTC کارفرما**
- **بدترین حالت مادهٔ ۱۱** و تسویهٔ مرخصی مادهٔ ۶۶/۷۱
- اجرا روی baseline تأییدشدهٔ **۱۴۰۴ SH** (`1404.1`, `VERIFIED` / `ACTIVE`)؛ ۱۴۰۵ ترانویسی‌شده، تأییدنشده و **inactive** است.

### Current verified development stage

| Fact | Value | Source |
| :--- | :--- | :--- |
| Delivery snapshot | 2026-11-16, evidence `BOOTSTRAP_CHANGELOG §24` | [PROJECT_STATUS §2](../docs/PROJECT_STATUS.md) |
| Backend tests | **568 passed / 105 skipped** (skips: PostgreSQL integration + one contract-valid negative case) | [PROJECT_STATUS §2](../docs/PROJECT_STATUS.md) |
| Frontend tests | **110 passed** (last recorded §23 evidence) | [PROJECT_STATUS §2](../docs/PROJECT_STATUS.md) |
| WBS census | **86 tasks: 1 COMPLETED, 6 IN_PROGRESS, 17 READY_FOR_REVIEW, 58 NOT_STARTED, 4 BLOCKED; 0 APPROVED** | [PROJECT_STATUS §2](../docs/PROJECT_STATUS.md) · [EXECUTION_PLAN §14.3](../docs/EXECUTION_PLAN.md) |
| Phase gates | **0 of 5 passed** | [PROJECT_STATUS §2](../docs/PROJECT_STATUS.md) |
| Engine | Implemented; `ENGINE_VERSION = 0.3.0-payroll-engine`; rule-set SHA-256 fingerprint published | [PROJECT_STATUS §2](../docs/PROJECT_STATUS.md) · [BOOTSTRAP_CHANGELOG §24](../docs/BOOTSTRAP_CHANGELOG.md) |
| Git state | Branch `autonomous/project-completion`, HEAD `db27ed3`; §24 remediation is uncommitted | [PROJECT_STATUS §3](../docs/PROJECT_STATUS.md) |

> **این وضعیت «تکمیل محصول» نیست.** موتور روی baseline ۱۴۰۴ پیاده‌سازی و به‌صورت محلی آزمون شده است؛ اما هیچ phase gate و هیچ task با وضعیت `APPROVED` وجود ندارد. بازبینی مستقل و اجرای integration وابسته به PostgreSQL هنوز انجام نشده‌اند.

### Main system components

| Component | Location | Role |
| :--- | :--- | :--- |
| Calculation engines | `backend/app/engines/` | قواعد خالص: money, rules, bases, sso, tax, overtime, severance, eydi, ctc, termination |
| Composition service | [payroll_service.py](../backend/app/services/payroll_service.py) | ترکیب محاسبات، provenance، fingerprint و reconciliation |
| API | [payroll.py](../backend/app/api/v1/payroll.py) | `POST /api/v1/simulations/gross-to-net` و `/health/live` |
| Contracts | [schemas/payroll.py](../backend/app/schemas/payroll.py) | ورودی/خروجی Pydantic v2 |
| Database baseline | [0001_statutory_baseline.py](../backend/alembic/versions/0001_statutory_baseline.py) | پنج جدول statutory، FORCE RLS و write gate |
| Frontend | [frontend/README.md](../frontend/README.md) | React/Vite RTL، صفحهٔ شبیه‌سازی و client تایپ‌دار |
| Infrastructure | [infra/postgres/README.md](../infra/postgres/README.md) | PostgreSQL محلی، hardening و roleها |
| Governance | [AGENTS.md](../AGENTS.md), [docs/](../docs/) | قواعد کار، ADRها، WBS و شواهد |

---

## Documentation

> [!important] سلسله‌مراتب اعتبار
> 1. مشخصات تأییدشده و Holy Bible → 2. ADRهای Accepted → 3. Execution Plan تأییدشده → 4. مستندات پیاده‌سازی → 5. یادداشت‌های توسعه و گزارش‌های agent.
> این داشبورد در سطح ۵ است و جای سطح ۱–۴ را نمی‌گیرد. در تعارض، هر دو سند پیوند داده می‌شوند و تعارض حل‌نشده باقی می‌ماند.

### Authority and navigation

| Document | Role | Status |
| :--- | :--- | :--- |
| [PISH_HESABDARI_HOLY_BIBLE.md](../docs/PISH_HESABDARI_HOLY_BIBLE.md) | سند مرجع اصلی پروژه (`DOC-HOLY-001`, v1.0.7) | Active |
| [DOCUMENTATION_INDEX.md](../docs/DOCUMENTATION_INDEX.md) | مسیر انتخاب context و supersession map | Active |
| [ADR_INDEX.md](../docs/ADR_INDEX.md) | فهرست ADRها و فناوری‌های ردشده | Active — **ADR-007 در آن فهرست نشده؛ تعارض ثبت شد** |
| [AGENTS.md](../AGENTS.md) | قرارداد رفتاری عامل‌ها و invariants | Active |
| [AGENT_OPERATING_MODEL.md](../docs/AGENT_OPERATING_MODEL.md) | نقش‌ها، delegation و محدودیت‌ها | Active |

### Status, planning and decisions

| Document | Role |
| :--- | :--- |
| [PROJECT_STATUS.md](../docs/PROJECT_STATUS.md) | وضعیت تحویل فعلی؛ **مرجع آمار و blockers** |
| [EXECUTION_PLAN.md](../docs/EXECUTION_PLAN.md) | WBS، وابستگی‌ها، acceptance criteria و phase gates |
| [DECISIONS_REGISTER.md](../docs/DECISIONS_REGISTER.md) | ۱۹ تصمیم DEC و ledger ابهامات B-1…B-11 |
| [DECISION_REQUIRED_FROM_OWNER.md](../docs/DECISION_REQUIRED_FROM_OWNER.md) | تصمیم‌های نیازمند مالک |
| [IMPLEMENTATION_READINESS.md](../docs/IMPLEMENTATION_READINESS.md) | ارزیابی آمادگی هر فاز |
| [BOOTSTRAP_CHANGELOG.md](../docs/BOOTSTRAP_CHANGELOG.md) | شواهد اجرایی؛ §24 جدیدترین remediation |
| [AUTONOMOUS_PROGRESS.md](../AUTONOMOUS_PROGRESS.md) | پیگیری remediation خودکار |
| [PROJECT_HANDOFF_SUMMARY.md](../PROJECT_HANDOFF_SUMMARY.md) | خلاصهٔ handoff — **snapshot قدیمی؛ آمار آن superseded است** |

### ADRs

| ADR | Title | Status |
| :--- | :--- | :--- |
| [ADR-001](../docs/adr/ADR-001-frontend-architecture-react-vite-spa.md) | React + Vite SPA | **Accepted** |
| [ADR-002](../docs/adr/ADR-002-object-storage-worm-ceph-s3-governance.md) | Ceph / S3-compatible WORM storage | **Accepted** |
| [ADR-003](../docs/adr/ADR-003-sensitive-data-encryption-alee-blind-indexing.md) | ALEE encryption and blind indexing | **Accepted** |
| [ADR-004](../docs/adr/ADR-004-phase-1-product-boundary-prehire-scope.md) | Phase 1 pre-hire boundary | **Accepted** — module list/directives 2–3 superseded by ADR-008; text retained |
| [ADR-005](../docs/adr/ADR-005-async-execution-strategy.md) | Async execution strategy | **PROPOSED** — not binding; `P2-T04` blocked |
| [ADR-006](../docs/adr/ADR-006-phase-0-owner-approved-security-and-schema.md) | Phase 0 security and schema | **Accepted** |
| [ADR-007](../docs/adr/ADR-007-statutory-global-access-and-deferred-identity.md) | Global statutory access and deferred identity | **Accepted** — missing from ADR_INDEX and DOCUMENTATION_INDEX (**CONFLICT**) |
| [ADR-008](../docs/adr/ADR-008-product-scope-statutory-payroll-engine.md) | Product scope refocus on statutory payroll engine | **Accepted** |

### Architecture and specifications

| Document | Scope |
| :--- | :--- |
| [REMEDIATED_TECHNICAL_SPECIFICATION_V2.md](../REMEDIATED_TECHNICAL_SPECIFICATION_V2.md) | مشخصات فنی/محصولی مبنا (rank 2) |
| [AUTH.md](../docs/specs/AUTH.md) | identity، session، MFA، tenant isolation و audit |
| [DEPLOYMENT.md](../docs/specs/DEPLOYMENT.md) | topology، configuration، TLS، observability، backup، rollback؛ §7.1 API |
| [STATUTORY_INGESTION.md](../docs/specs/STATUTORY_INGESTION.md) | acquisition، transcription، four-eyes verification و activation |
| [STATUTORY_DATABASE_CONTRACT.md](../docs/specs/STATUTORY_DATABASE_CONTRACT.md) | قرارداد پنج جدول statutory و RLS |
| [DOCUMENT_FORENSICS.md](../docs/specs/DOCUMENT_FORENSICS.md) | forensics سند — **خارج از دامنهٔ ADR-008** |
| [FRONTEND_PERSIAN.md](../docs/specs/FRONTEND_PERSIAN.md) | RTL، Vazirmatn، تقویم جلالی و PDF فارسی |
| [TESTING.md](../docs/specs/TESTING.md) | ۱۳ لایهٔ آزمون، CI stages و release criteria |

### Backend, frontend, API and database

| Area | Entry point |
| :--- | :--- |
| Backend service | [payroll_service.py](../backend/app/services/payroll_service.py) |
| Rule-set loader | [rules.py](../backend/app/engines/rules.py) |
| Tax engine | [tax.py](../backend/app/engines/tax.py) |
| Termination engine | [termination.py](../backend/app/engines/termination.py) |
| API endpoint | [payroll.py](../backend/app/api/v1/payroll.py) |
| API contract tests | [test_payroll_simulation.py](../backend/tests/api/test_payroll_simulation.py) · [test_openapi_contract.py](../backend/tests/api/test_openapi_contract.py) |
| Backend tests | `backend/tests/{unit,api,property,integration}/` |
| Frontend | [frontend/README.md](../frontend/README.md) · [simulation-page.tsx](../frontend/src/routes/simulation-page.tsx) · [client.ts](../frontend/src/api/client.ts) |
| Database migration | [0001_statutory_baseline.py](../backend/alembic/versions/0001_statutory_baseline.py) |
| Database operations | [infra/postgres/README.md](../infra/postgres/README.md) |

---

## Development Status

### Completed milestones

- **`P0-T02` — FastAPI skeleton and configuration:** the only task recorded as `COMPLETED`; `/health/live` answers 200. Source: [PROJECT_STATUS §7](../docs/PROJECT_STATUS.md).
- **Engine implementation and local verification:** the ADR-008 engine tasks are `READY_FOR_REVIEW`, **not** `APPROVED`. Local evidence: 568 backend tests pass, ruff and strict mypy pass. Source: [BOOTSTRAP_CHANGELOG §24](../docs/BOOTSTRAP_CHANGELOG.md).
- **P0-T04 migration:** five-table baseline verified on an isolated PostgreSQL instance; `READY_FOR_REVIEW`. No production or `pish_dev` migration was run. Source: [PROJECT_STATUS §2](../docs/PROJECT_STATUS.md).

### Current milestone

هیچ phase gateای باز نشده است. وضعیت فعلی طبق [PROJECT_STATUS §2](../docs/PROJECT_STATUS.md): موتور پیاده‌سازی‌شده در انتظار **بازبینی مستقل** و **اجرای integration وابسته به PostgreSQL** است. وظایف مالی جدید تا تعیین‌تکلیف `DEC-013` و ابهامات B-series نباید وضعیت `APPROVED` بگیرند.

### Remaining milestones

- **58 task** در وضعیت `NOT_STARTED` و **4 task** در وضعیت `BLOCKED` (WBS کامل: [EXECUTION_PLAN §14.3](../docs/EXECUTION_PLAN.md)).
- **5 phase gate** هنوز عبور نکرده‌اند؛ هیچ gate evidence pack وجود ندارد.
- فازهای ۱ و ۲ در [IMPLEMENTATION_READINESS](../docs/IMPLEMENTATION_READINESS.md) به‌دلیل وابستگی‌های خارجی/حقوقی `BLOCKED` هستند.

### Known blockers

| Blocker | Current evidence | Source |
| :--- | :--- | :--- |
| PostgreSQL integration suites | **NOT RUN** — Docker daemon unavailable; 104 suites self-skip | [BOOTSTRAP_CHANGELOG §24](../docs/BOOTSTRAP_CHANGELOG.md) |
| Independent review by a non-author | **NOT RUN** — unavailable in this environment; no engine task may move to `APPROVED` | [PROJECT_STATUS §2](../docs/PROJECT_STATUS.md) · [AGENTS.md §6](../AGENTS.md) |
| CI execution | Workflow exists, but it has never run on GitHub; `gh` token recorded invalid | [PROJECT_STATUS §2](../docs/PROJECT_STATUS.md) |
| External legal/tax verification | 1405 four-eyes verification and the certified golden corpus do not exist; accountant/counsel not engaged | [DECISIONS_REGISTER](../docs/DECISIONS_REGISTER.md) · [EXECUTION_PLAN §14.3](../docs/EXECUTION_PLAN.md) |
| Async execution | ADR-005 remains `PROPOSED`; `P2-T04` is blocked | [ADR-005](../docs/adr/ADR-005-async-execution-strategy.md) |
| Statutory ambiguities | B-1…B-8 and B-10 need a human legal/tax ruling; `DEC-013` is open | [DECISIONS_REGISTER](../docs/DECISIONS_REGISTER.md) |

### Verified progress (no invented percentages)

- **0 of 5** phase gates; **0 APPROVED** tasks.
- **568** backend tests passed, **105** skipped; **110** frontend tests recorded as passing.
- `ruff check .` and `mypy --strict app tests` pass on **64** source files.
- CI has **never executed** on GitHub; local verification is not CI or production acceptance.

---

## Architecture Navigation

- [Architecture Map](Architecture/Architecture%20Map.md) — نقشهٔ لایه‌ها و پیوند به کد
- [Holy Bible §4 — Architecture and Technology](../docs/PISH_HESABDARI_HOLY_BIBLE.md) (بخش ۴)
- [ADR-001 — frontend architecture](../docs/adr/ADR-001-frontend-architecture-react-vite-spa.md)
- [ADR-003 — encryption and blind indexing](../docs/adr/ADR-003-sensitive-data-encryption-alee-blind-indexing.md)
- [ADR-006 — Phase 0 security/schema](../docs/adr/ADR-006-phase-0-owner-approved-security-and-schema.md)
- [ADR-007 — global statutory access](../docs/adr/ADR-007-statutory-global-access-and-deferred-identity.md)
- [ADR-008 — product scope](../docs/adr/ADR-008-product-scope-statutory-payroll-engine.md)
- [STATUTORY_DATABASE_CONTRACT](../docs/specs/STATUTORY_DATABASE_CONTRACT.md)
- [AUTH specification](../docs/specs/AUTH.md)
- [DEPLOYMENT specification](../docs/specs/DEPLOYMENT.md)

**Code map (directories are shown as code paths; files are linked):**

| Layer | Path |
| :--- | :--- |
| Pure engines | `backend/app/engines/` — [money.py](../backend/app/engines/money.py), [rules.py](../backend/app/engines/rules.py), [tax.py](../backend/app/engines/tax.py), [termination.py](../backend/app/engines/termination.py) |
| Composition | [payroll_service.py](../backend/app/services/payroll_service.py) |
| HTTP/API | [payroll.py](../backend/app/api/v1/payroll.py) · [main.py](../backend/app/main.py) |
| Persistence | [statutory.py](../backend/app/models/statutory.py) · [0001_statutory_baseline.py](../backend/alembic/versions/0001_statutory_baseline.py) |
| Frontend | [simulation-page.tsx](../frontend/src/routes/simulation-page.tsx) · [contracts.ts](../frontend/src/api/contracts.ts) |
| Tests | `backend/tests/unit/`, `backend/tests/api/`, `backend/tests/property/`, `backend/tests/integration/` |

---

## Decision Register

### Accepted decisions (binding)

- **ADR-001, ADR-002, ADR-003, ADR-004, ADR-006, ADR-007, ADR-008** — Accepted. ADR-004's module list and directives 2–3 are superseded by ADR-008; its text remains.
- **DEC-002a, DEC-004, DEC-004a, DEC-004b, DEC-005, DEC-012** — resolved by ADR-006/007/008 per [DECISIONS_REGISTER](../docs/DECISIONS_REGISTER.md).

### Proposed decision (not binding)

- **ADR-005 — Asynchronous execution strategy:** `PROPOSED`. It must not be cited as a binding constraint; `P2-T04` remains blocked.

### Unresolved decisions

**19 entries total: 11 open (7 blocking, 4 non-blocking), 6 resolved, 2 rejected.** Source: [DECISIONS_REGISTER summary](../docs/DECISIONS_REGISTER.md).

| Decision | Status | Blocking phase |
| :--- | :--- | :--- |
| `DEC-001` — 1405 statutory baseline verification | `OPEN — BLOCKING` | Phase 1 |
| `DEC-002` — corrected worked example and golden corpus | `OPEN — BLOCKING` | Phase 1 |
| `DEC-003` — async execution strategy | `OPEN — BLOCKING` | Phase 2 |
| `DEC-006` — Persian RTL / Jalali / PDF choices | `OPEN — NON-BLOCKING` | Phase 3 |
| `DEC-009` — tax-optimization advisory boundary | `OPEN — NON-BLOCKING` | Phase 3 |
| `DEC-010` — deployment topology | `OPEN — BLOCKING` | Phase 4 |
| `DEC-011` — document intelligence acceptance criteria | `OPEN — BLOCKING` | Phase 2 |
| `DEC-011a` — Shahkar access route | `OPEN — BLOCKING` | Phase 2 |
| `DEC-011b` — human adjudication of flagged documents | `OPEN — NON-BLOCKING` | Phase 2 |
| `DEC-011c` — Art. 86 720-day threshold | `OPEN — BLOCKING` | Phase 2 |
| `DEC-013` — apply allowance floors and seniority base to net | `OPEN — NON-BLOCKING` | v1 reference-only |

**Rejected as out of product scope:** `DEC-007`, `DEC-008` (ADR-008). They remain rejected; do not reintroduce without a superseding ADR.

**B-series ambiguity ledger:** B-1…B-8 and B-10 `OPEN` (human legal/tax ruling); B-9 and B-11 `RESOLVED — engineering`. Source: [DECISIONS_REGISTER B-series](../docs/DECISIONS_REGISTER.md).

### Conflicts and documentation gaps

> [!warning] تعارض ثبت‌شده — حل‌نشده
> - **ADR-007 در `ADR_INDEX.md` و `DOCUMENTATION_INDEX.md` فهرست نشده است**، در حالی که فایل ADR-007 وضعیت `Accepted` دارد و `DECISIONS_REGISTER` نیز آن را تأیید می‌کند. منابع: [ADR-007](../docs/adr/ADR-007-statutory-global-access-and-deferred-identity.md) · [ADR_INDEX](../docs/ADR_INDEX.md) · [DOCUMENTATION_INDEX](../docs/DOCUMENTATION_INDEX.md). وضعیت: **CONFLICT / MISSING** — بدون حدس و بدون تغییر سند مرجع.
> - **آمار README، PROJECT_HANDOFF_SUMMARY و metadata Holy Bible با `PROJECT_STATUS §2` (2026-11-16) هم‌راستا نیست.** به‌عنوان مثال README و handoff آمار ۵۴۸/۱۰۴ و «CI: None» را حفظ کرده‌اند؛ Holy Bible v1.0.7 آمار ۵ READY_FOR_REVIEW / ۷۰ NOT_STARTED را در metadata دارد. وضعیت جاری فقط از [PROJECT_STATUS](../docs/PROJECT_STATUS.md) و [EXECUTION_PLAN §14.3](../docs/EXECUTION_PLAN.md) خوانده می‌شود. وضعیت: **CONFLICT / stale snapshot** — اسناد قدیمی بازنویسی نشدند.

---

## Risk Register

> رجیستر کامل ریسک در [Holy Bible Appendix C](../docs/PISH_HESABDARI_HOLY_BIBLE.md) و [Risk Register](Risks/Risk%20Register.md) است. جدول زیر ریسک‌های فعالِ مرتبط با وضعیت فعلی را نشان می‌دهد؛ شدت و مالک از منبع اصلی نقل شده است.

| Risk | Category | Status / source |
| :--- | :--- | :--- |
| `HB-RISK-01` — 1405 baseline never verified; platform ships 1404 law in a 1405 year | Legal / regulatory | **CRITICAL** — Holy Bible Appendix C; `DEC-001` open |
| `HB-RISK-02` — Phase 1 gate cannot be met without a Certified Tax Accountant | Schedule | **CRITICAL** — Holy Bible Appendix C |
| `HB-RISK-07` — flat-10% Eydi rule in the seed causes under-withholding | Legal / financial | **CRITICAL** — mitigated in engine by progressive taxation; seed remains immutable (HB-GAP-005) |
| `HB-RISK-08` — SSO insurable base mis-modelled | Legal / financial | **HIGH** — B-3 open |
| `HB-RISK-09` — tenant-isolation escape in production | Security | **HIGH** — ADR-003/006; integration tests NOT RUN |
| `HB-RISK-10` — host compromise yields ciphertext and DEK | Security | **HIGH** — ADR-003/006; key registry not implemented |
| `HB-RISK-13` — OCR worker saturates the API | Operational | **HIGH if ADR-005 not accepted** — ADR-005 `PROPOSED` |
| `HB-RISK-16` — Phase 2 schedule with 5 blocked tasks | Schedule | **HIGH** — EXECUTION_PLAN §14.6 R-1 |
| `RISK-OBS-01` — PostgreSQL integration suites not executed here | Verification / database | **NOT RUN** — Docker unavailable; [§24](../docs/BOOTSTRAP_CHANGELOG.md) |
| `RISK-OBS-02` — CI workflow never executed on GitHub | Delivery / quality | **OPEN** — [PROJECT_STATUS §2](../docs/PROJECT_STATUS.md) |
| `RISK-OBS-03` — independent review by a non-author unavailable | Governance | **OPEN** — engine tasks stay `READY_FOR_REVIEW` |
| `RISK-DOC-01` — ADR-007 omitted from the two indexes | Documentation | **CONFLICT / MISSING** — see above |

**Top three readiness risks:** golden-vector corpus, 1405 four-eyes verification, 500-slip corpus. Source: [IMPLEMENTATION_READINESS §8](../docs/IMPLEMENTATION_READINESS.md).

**Schedule risks (recorded, not applied):** R-1…R-6 in [EXECUTION_PLAN §14.6](../docs/EXECUTION_PLAN.md). No schedule change is approved.

---

## Knowledge Layer

این لایه با Obsidian 1.15.1 باز می‌شود، اما محتوای آن Markdown استاندارد و قابل‌حمل است و به Obsidian وابسته نیست. صفحات زیر فقط ناوبری‌اند و سند مرجع نیستند.

| Page | Purpose |
| :--- | :--- |
| [Project Home](Project%20Home.md) | داشبورد مرکزی (همین صفحه) |
| [Documentation Inventory](Overview/Documentation%20Inventory.md) | فهرست کامل اسناد موجود و وضعیت هر گروه |
| [Architecture Map](Architecture/Architecture%20Map.md) | نقشهٔ لایه‌ها، ماژول‌ها و آزمون‌ها با پیوند به کد |
| [Decision Status](Decisions/Decision%20Status.md) | ADRها، ۱۹ تصمیم DEC و ledger ابهامات B-series |
| [Development Log Index](Development%20Log/Development%20Log%20Index.md) | گاه‌شمار شواهد اجرایی |
| [Risk Register](Risks/Risk%20Register.md) | تلفیق ریسک‌های قانونی، امنیتی و زمانی |
| [Agent Guide](Agent%20Knowledge/Agent%20Guide.md) | نحوهٔ استفادهٔ عامل‌ها و سلسله‌مراتب اعتبار |
| [Project Map](Project%20Map.canvas) | نقشهٔ بصری (Canvas) از همین صفحات |

**Templates:** [ADR](Templates/ADR%20Template.md) · [Technical Research](Templates/Technical%20Research.md) · [Development Log](Templates/Development%20Log.md) · [Risk Report](Templates/Risk%20Report.md) · [Module Documentation](Templates/Module%20Documentation.md)

## استفاده توسط Agentها

- ابتدا [AGENTS.md](../AGENTS.md)، سپس [DOCUMENTATION_INDEX §0](../docs/DOCUMENTATION_INDEX.md) و [Agent Guide](Agent%20Knowledge/Agent%20Guide.md).
- برای وضعیت جاری فقط [PROJECT_STATUS](../docs/PROJECT_STATUS.md) و WBS؛ برای تصمیم‌ها فقط [DECISIONS_REGISTER](../docs/DECISIONS_REGISTER.md) و ADRهای Accepted.
- فایل‌های Markdown استاندارد و قابل‌حمل باقی می‌مانند؛ لینک‌ها relative هستند. هیچ plugin اجتماعی نصب نشده و هیچ sync ابری فعال نیست.
- **هرگز** secret، API key، محتوای `.env`، National ID، شمارهٔ تماس، Sheba یا حقوق واقعی را در noteها قرار ندهید. این Vault شامل `.secrets/` و فایل‌های محلی است؛ آن‌ها را باز نکنید و به سرویس بیرونی نفرستید.

---

*Navigation layer created 2026-11-16. Re-verify links and statuses at every phase gate or when `PROJECT_STATUS` changes.*
