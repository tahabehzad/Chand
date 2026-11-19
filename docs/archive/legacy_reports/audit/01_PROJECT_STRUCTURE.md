# ساختار پروژه و نمای معماری

**تاریخ:** ۲۸ آبان ۱۴۰۵  
**شناسه:** AUDIT-01

---

## ۱. ساختار مخزن

```
C:\project\New project\
├── AGENTS.md                    # قوانین عملیاتی (payroll-era)
├── README.md                    # نقطه ورود (به‌روز شده برای salary estimation)
├── PROJECT_STATE.md             # وضعیت مشتق‌شده
├── REMEDIATED_TECHNICAL_SPEC... # مشخصات فنی اصلی (payroll-era)
├── RESEARCH_GAP_ANALYSIS...     # تحقیقات تاریخی
├── PHASE_1_RED_TEAM_AUDIT.md    # یافته‌های حسابرسی قبلی
├── PHASE_1_FINAL_AUDIT_BRIEF.md # خلاصه حسابرسی اولیه
├── PRODUCT_AUDIT_REPORT.md      # گزارش حسابرسی محصول
├── PROJECT_HANDOFF_SUMMARY.md   # خلاصه انتقال
├── AUTONOMOUS_PROGRESS.md       # پیشرفت خودکار
├── BLACK_VECTOR_PHASE0_PLAN.md  # طرح فاز ۰
├── LICENSE                      # مالکیت خصوصی
│
├── backend/                     # بک‌اند FastAPI (Python 3.12+)
│   ├── app/
│   │   ├── main.py              # نقطه ورود ASGI
│   │   ├── db.py                # اتصال دیتابیس
│   │   ├── core/
│   │   │   ├── config.py        # تنظیمات fail-closed
│   │   │   ├── logging.py       # لاگ ساختاریافته
│   │   │   ├── migration_lint.py
│   │   │   └── security/        # ماژول‌های امنیتی
│   │   │       ├── blind_index.py    # HMAC-SHA256 blind indexing
│   │   │       ├── pii_transformer.py # AES-256-GCM encryption
│   │   │       ├── tenant_context.py  # RLS context binding
│   │   │       ├── local_workspace.py
│   │   │       └── upload_limit.py
│   │   ├── api/v1/
│   │   │   ├── auth.py          # Login/Logout/Me
│   │   │   ├── payroll.py       # Gross-to-net simulation
│   │   │   ├── estimation/      # Salary estimation (جدید)
│   │   │   ├── valuation.py     # Compensation advisory
│   │   │   ├── manager.py       # Manager workspace
│   │   │   └── work_profile.py  # Work profile
│   │   ├── engines/             # موتور محاسبات حقوق (۱۴ ماژول)
│   │   │   ├── money.py         # Decimal money primitives
│   │   │   ├── rules.py         # Rule-set loader
│   │   │   ├── bases.py         # Base decomposition
│   │   │   ├── sso.py           # بیمه تأمین اجتماعی
│   │   │   ├── tax.py           # مالیات پلکانی
│   │   │   ├── overtime.py      # اضافه‌کاری و شب‌کاری
│   │   │   ├── eydi.py          # عیدی
│   │   │   ├── ctc.py           # هزینه کارفرما
│   │   │   ├── severance.py     # سنوات
│   │   │   ├── termination.py   # ماده ۱۱ فسخ
│   │   │   ├── valuation.py     # ارزیابی جبران خدمات
│   │   │   ├── work_schedule.py # برنامه کاری
│   │   │   ├── perf_v1.py       # Performance scoring
│   │   │   └── statutory_ref... # مراجع قانونی
│   │   ├── domain/              # دامنه تخمین حقوق (جدید)
│   │   │   └── salary_estimation/
│   │   │       ├── salary_estimator.py  # الگوریتم تخمین
│   │   │       ├── matcher.py           # Profile matching
│   │   │       ├── mock_data.py         # داده‌های mock
│   │   │       ├── money_validation.py  # اعتبارسنجی مالی
│   │   │       ├── adjuster.py          # تعدیل‌گر حقوق
│   │   │       └── schemas.py           # مدل‌های domain
│   │   ├── models/              # مدل‌های SQLAlchemy
│   │   ├── schemas/             # مدل‌های Pydantic
│   │   ├── services/            # لایه سرویس
│   │   ├── statutory/           # جمع‌آوری منابع قانونی
│   │   └── storage/             # S3 adapter
│   ├── alembic/versions/        # ۶ migration
│   ├── data/seeds/              # Rule sets (1404 verified, 1405 inactive)
│   ├── tests/                   # ~۳۵ فایل تست
│   ├── scripts/                 # اسکریپت‌های کمکی
│   ├── pyproject.toml           # وابستگی‌ها (uv)
│   └── .env                     # ⚠️ حاوی اطلاعات حساس
│
├── frontend/                    # فرانت‌اند React/Vite/TypeScript
│   ├── src/
│   │   ├── app/                 # Shell, Router, Auth
│   │   ├── api/                 # API client layer
│   │   ├── components/
│   │   │   ├── ui/              # Primitives (Button, Card, Input, etc.)
│   │   │   ├── salary-estimation/ # فرم و نتایج تخمین (جدید)
│   │   │   ├── salary-discovery/  # کاوش حقوق (جدید)
│   │   │   ├── dashboard/       # Dashboard components
│   │   │   ├── domain/          # Rule-set warning
│   │   │   └── layout/          # Layout components
│   │   ├── routes/              # صفحات
│   │   ├── lib/                 # Utilities (money, numerals, calendar)
│   │   ├── prototype/           # Session management
│   │   └── state/               # Zustand store
│   ├── package.json             # pnpm + React 19
│   └── vite.config.ts
│
├── docs/                        # ۴۰+ سند مستندات
│   ├── adr/                     # ۱۳ ADR (ADR-001 تا ADR-013)
│   ├── specs/                   # مشخصات فنی (۸ مورد)
│   ├── audit/                   # ماتریس حسابرسی مستندات
│   └── agent-reports/           # گزارشات agent
│
├── infra/                       # زیرساخت
│   ├── compose/                 # Docker Compose
│   └── postgres/                # PostgreSQL config, Dockerfile, roles
│
├── .agents/skills/              # ۱۱ قرارداد مهندسی agent
├── .github/workflows/ci.yml     # CI pipeline
├── .secrets/                    # ⚠️ گواهینامه‌ها و کلیدها
└── .freebuff/                   # داده‌های جمع‌آوری‌شده قانونی
```

---

## ۲. فناوری‌های استفاده‌شده

### بک‌اند
| فناوری | نسخه | کاربرد |
|:---|:---|:---|
| Python | ≥3.12, <3.14 | زبان اصلی |
| FastAPI | ≥0.110, <1.0 | Framework API |
| SQLAlchemy | ≥2.0.30, <3.0 | ORM (async) |
| Alembic | ≥1.13, <2.0 | Migrations |
| asyncpg | ≥0.29, <1.0 | PostgreSQL driver |
| Pydantic | ≥2.7, <3.0 | Validation |
| argon2-cffi | ≥23.1, <26.0 | Password hashing |
| cryptography | ≥42.0, <46.0 | AES-256-GCM |
| PyYAML | ≥6.0, <7.0 | Seed loading |
| ruff | ≥0.6, <1.0 | Linting |
| mypy | ≥1.11, <2.0 | Type checking (strict) |
| pytest | ≥8.2, <9.0 | Testing |
| hypothesis | ≥6.100, <7.0 | Property testing |

### فرانت‌اند
| فناوری | نسخه | کاربرد |
|:---|:---|:---|
| React | ^19.0.0 | UI framework |
| Vite | ^6.0.5 | Build tool |
| TypeScript | ^5.7.2 | Type safety |
| Tailwind CSS | ^4.0.0 | Styling |
| React Router | ^7.1.0 | Routing |
| TanStack Query | ^5.62.0 | Data fetching |
| Zustand | ^5.0.2 | State management |
| Vazirmatn | ^5.2.5 | Persian font |
| Vitest | ^2.1.8 | Testing |

### زیرساخت
| فناوری | کاربرد |
|:---|:---|
| PostgreSQL 16 | دیتابیس اصلی |
| Docker / Docker Compose | Containerization |
| GitHub Actions | CI/CD |
| uv | Python dependency manager |
| pnpm | Node dependency manager |

---

## ۳. معماری واقعی (نه مستند‌شده)

```
                    ┌──────────────────────────┐
                    │   React SPA (Vite)       │
                    │   RTL Persian Shell      │
                    │   Vazirmatn Font         │
                    │   SessionStorage Token   │
                    └────────────┬─────────────┘
                                 │ HTTP (localhost)
                    ┌────────────▼─────────────┐
                    │   FastAPI (uvicorn)       │
                    │   CORS Middleware         │
                    │   Correlation ID          │
                    │   Upload Limit            │
                    ├──────────────────────────┤
                    │  /api/v1/simulations/     │
                    │    gross-to-net ──────────┼── PayrollService → engines/*
                    │    salary-estimation ─────┼── EstimationService → domain/*
                    │  /api/v1/auth/            │      (MOCK DATA)
                    │    login/me/logout ───────┼── IdentityService → models/identity
                    │  /api/v1/valuation/ ──────┼── ValuationService → engines/valuation
                    │  /api/v1/manager/ ────────┼── ManagerService
                    │  /api/v1/work-profiles/ ──┼── WorkProfileService
                    │  /health/live             │
                    └────────────┬─────────────┘
                                 │ asyncpg (NOT CONNECTED)
                    ┌────────────▼─────────────┐
                    │   PostgreSQL 16           │
                    │   (Docker container)      │
                    │   6 migrations defined    │
                    │   NEVER EXECUTED          │
                    └──────────────────────────┘
```

**نکته مهم:** PostgreSQL container در محیط توسعه اجرا نمی‌شود — تست‌های integration خودکار skip می‌شوند. بنابراین تمام API endpointهایی که نیاز به دیتابیس دارند (auth, manager, work-profile) عملاً **اجرا نمی‌شوند**.

---

## ۴. فایل‌های مفقود یا غیرقابل‌دسترس

| مورد | وضعیت |
|:---|:---|
| PostgreSQL runtime | Container image در دسترس نیست؛ تست‌های integration skip می‌شوند |
| Production deployment | هیچ evidence از deployment وجود ندارد |
| Market data (real) | فقط mock data؛ هیچ اتصال به Jobinja/JobVision/survey |
| Golden corpus | تست‌های golden verification هنوز وجود ندارند |
| Independent review | هیچ review مستقل (non-author) انجام نشده |
| ADR-012 implementation | مدل persisted work profile تعریف شده ولی migration ندارد |
| Estimation migrations | مدل‌های `estimation.py` migration ندارند |

---

## ۵. پیوست بازبینی مستقل (ادامهٔ حسابرسی — ۲۸ آبان ۱۴۰۵)

### ۵.۱ تصحیح شمارش‌ها
| مورد | ادعای قبلی | واقعیت شمارش‌شده |
|:---|:--:|:--:|
| فایل تست بک‌اند | «~۳۵» | ۴۱ |
| اسناد Markdown | «۴۰+» | ۶۱ در `docs/` + ۱۱ در ریشه |
| ماژول‌های `engines/` | «۱۴» | ۱۴ فایل `.py` (شامل `errors.py`, `statutory_refs.py`) ✅ |
| LOC | ذکر نشده | بک‌اند ۱۰٬۹۵۵ / تست ۷٬۳۷۵ / فرانت ۹٬۴۰۲ |

### ۵.۲ وضعیت working tree در زمان حسابرسی (شاهد ساختاری)
- شاخه: `autonomous/project-completion`؛ HEAD: `f943634`.
- **۱۴ commit** در تاریخچه؛ هیچ تغییر staged وجود ندارد.
- **۱۴ فایل modified** (بدون commit) و **۴۵ ورودی untracked** — کل محصول جدید (ADR-013) در این دسته است: `backend/app/domain/`, `backend/app/services/estimation/`, `backend/app/api/v1/estimation/`, `backend/app/models/estimation.py`, `backend/app/schemas/estimation.py`, `frontend/src/components/salary-estimation/`, `frontend/src/components/salary-discovery/`, `frontend/src/lib/salary-benchmarks.ts`, `frontend/src/api/salary-estimation.ts` و ۱۳ سند.
- **پیامد معماری:** محصول اعلام‌شده هیچ‌گاه commit نشده و هیچ بازبینی مستقل (AGENTS.md §6) روی آن انجام نشده است. این یکی از ریشه‌های کیفیت پایین این ناحیه است.

### ۵.۳ ساختار واقعی درخت (تأییدشده)
```
backend/app/
├── api/v1/{auth,payroll,valuation,manager,work_profile}.py + estimation/__init__.py
├── engines/            14 ماژول (موتور حقوق، Decimal)
├── domain/salary_estimation/  7 فایل — ۲ فایل مرده (adjuster.py, mock_data.py)
├── services/estimation/service.py
├── models/{statutory,identity,manager,work_profile,audit,estimation}.py
└── core/security/{blind_index,pii_transformer,tenant_context,local_workspace,upload_limit}.py
backend/alembic/versions/   6 migration (هیچ‌کدام برای estimation)
backend/tests/              41 فایل / 835 تست collect
frontend/src/               15 فایل تست / 128 تست
```
**نکته:** ادعای گزارش قبلی که `domain/salary_estimation/` شامل «schemas.py و money_validation.py» است درست است، اما `adjuster.py` و `mock_data.py` **کد مرده** هستند (BE-16) و نباید در ارزیابی حجم قابلیت شمرده شوند.
