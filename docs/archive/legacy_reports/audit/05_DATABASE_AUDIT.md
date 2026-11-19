# حسابرسی دیتابیس

**تاریخ:** ۲۸ آبان ۱۴۰۵  
**شناسه:** AUDIT-05

---

## ۱. خلاصه

۶ migration تعریف شده ولی **هیچ‌کدام در محیط واقعی اجرا نشده‌اند** (PostgreSQL container در دسترس نیست). مدل‌های estimation بدون migration تعریف شده‌اند.

---

## ۲. Migrations — Inventory

| Migration | موضوع | RLS | وضعیت |
|:---|:---|:--:|:--:|
| `0001_statutory_baseline.py` | Statutory rule sets, source artefacts, verification log | ✅ FORCE RLS | تعریف‌شده / اجرا نشده |
| `0002_identity_foundation.py` | Users, organizations, memberships, roles, sessions | ✅ FORCE RLS | تعریف‌شده / اجرا نشده |
| `0003_tenant_context.py` | Tenant context RLS policies | ✅ | تعریف‌شده / اجرا نشده |
| `0004_manager_workspace.py` | Manager proposals, candidates | ✅ | تعریف‌شده / اجرا نشده |
| `0005_audit_ledger.py` | Append-only audit log | ✅ | تعریف‌شده / اجرا نشده |
| `0006_work_profiles.py` | Work profiles, payroll snapshots | ✅ | تعریف‌شده / اجرا نشده |

### یافته‌ها

#### FIND-DB-01: مدل‌های estimation بدون migration
- **شدت:** بالا
- **مسئله:** `backend/app/models/estimation.py` ۴ جدول تعریف کرده:
  - `candidate_estimates`
  - `market_salary_data`
  - `resume_uploads`
  - `estimation_users`
- هیچ migration در `alembic/versions/` وجود ندارد
- **تأثیر:** این جداول هرگز ایجاد نمی‌شوند

#### FIND-DB-02: دو سیستم user متناقض
- **شدت:** بالا
- **مسئله:** 
  - `models/identity.py` → جدول `users` با Argon2id, organizations, memberships, RLS
  - `models/estimation.py` → جدول `estimation_users` بدون RLS، ساده‌تر
- **تأثیر:** مشخص نیست کدام سیستم auth باید استفاده شود

#### FIND-DB-03: estimation models بدون RLS/tenant_id
- **شدت:** اطلاع‌رسانی
- **مسئله:** ADR-013 صریحاً RLS و tenant_id را حذف کرده (single manager)
- ولی تمام migration‌های موجود (0001-0006) RLS دارند
- **تأثیر:** ناسازگاری معماری بین لایه‌های قدیم و جدید

---

## ۳. مدل‌های SQLAlchemy — Inventory

### ۳.۱ Payroll-era (با migration)
| مدل | فایل | جداول |
|:---|:---|:---|
| Statutory | `models/statutory.py` | `statutory_rule_set_versions`, `statutory_source_artefacts`, etc. |
| Identity | `models/identity.py` | `users`, `organizations`, `organization_memberships`, `roles`, `user_sessions` |
| Manager | `models/manager.py` | `manager_proposals`, `proposal_candidates` |
| WorkProfile | `models/work_profile.py` | `work_profiles`, `payroll_snapshots` |
| Audit | `models/audit.py` | `audit_entries` (append-only) |

### ۳.۲ Estimation (بدون migration)
| مدل | فایل | جداول |
|:---|:---|:---|
| CandidateEstimate | `models/estimation.py` | `candidate_estimates` |
| MarketSalaryData | `models/estimation.py` | `market_salary_data` |
| ResumeUpload | `models/estimation.py` | `resume_uploads` (v2 stub) |
| EstimationUser | `models/estimation.py` | `estimation_users` |

---

## ۴. PostgreSQL Infrastructure

| فایل | محتوا |
|:---|:---|
| `infra/postgres/Dockerfile` | Custom PostgreSQL image |
| `infra/postgres/init.sql` | Initial DB setup |
| `infra/postgres/statutory_roles.sql` | NOLOGIN roles for statutory access |
| `infra/postgres/pg_hba.conf` | Host-based access control |
| `infra/postgres/postgresql.conf` | Performance tuning |
| `infra/postgres/verify-hardening.sql` | Security verification queries |
| `infra/postgres/entrypoint.sh` | Container startup |
| `infra/postgres/backup/` | Backup/restore scripts |
| `infra/compose/compose.dev.yml` | Docker Compose for development |

**وضعیت واقعی:** تمام این زیرساخت تعریف شده ولی **container image در محیط توسعه فعلی pull نمی‌شود**. تست‌های integration خودکار skip می‌شوند.

---

## ۵. Data Integrity

### ۵.۱ Statutory Seeds — مثبت
| Seed | وضعیت |
|:---|:---|
| `statutory_rules_1404.yaml` | ✅ Verified, active, hash-pinned |
| `statutory_rules_1405.yaml` | ⚠️ Transcribed, unverified, inactive |

### ۵.۲ Seed Protection
- `.gitignore` explicitly allows `backend/data/seeds/*.yaml`
- CI verifies the 1404 hash
- 1405 fails closed on load attempt

---

## ۶. توصیه‌ها

1. **ایجاد migration برای مدل‌های estimation** — یا حذف مدل‌ها اگر persistence لازم نیست
2. **تعیین تکلیف سیستم auth** — identity.py یا estimation_users
3. **اجرای migration‌ها در یک محیط واقعی** — حداقل یک بار verify شوند
4. **تعیین تکلیف RLS** — آیا برای salary estimation لازم است یا نه

---

## ۷. پیوست بازبینی مستقل (ادامهٔ حسابرسی — ۲۸ آبان ۱۴۰۵)

### DB-04 — مدل‌های بدون migration در `Base.metadata` ثبت شده‌اند (ریسک drift)
- **شدت:** بالا
- **شرح:** `backend/app/models/__init__.py:24` ماژول `estimation` را import می‌کند تا جدول‌ها روی `Base` ثبت شوند. بنابراین `alembic revision --autogenerate` چهار جدول (`candidate_estimates`, `market_salary_data`, `resume_uploads`, `estimation_users`) را به‌عنوان «missing table» می‌بیند و `Base.metadata.create_all` نیز آن‌ها را می‌سازد. مسیر دوم عملاً استفاده شده است: `backend/create_first_user.py:30` با `Base.metadata.create_all` schema می‌سازد، نه Alembic.
- **مسیر و خط:** `backend/app/models/__init__.py:24`؛ `backend/app/models/estimation.py:45,90,131,158`؛ `backend/create_first_user.py:26-30`
- **تأثیر:** دو مسیر ساخت schema موازی (Alembic و create_all) با نسخهٔ مبهم؛ در محیطی که migration اجرا نشود، جدول‌ها یا ساخته نمی‌شوند یا با نسخهٔ دیگری ساخته می‌شوند. `estimation_users` هم با `users` موجود تداخل مفهومی دارد.
- **اقدام:** یا migration رسمی ۰۰۰۷، یا خارج‌کردن مدل‌ها از ثبت در `Base` تا autogenerate آن‌ها را نبیند؛ حذف `create_all` از هر مسیر.
- **وضعیت تأیید:** ✅ تأییدشده (مشاهدهٔ مستقیم کد).

### DB-05 — تأیید وضعیت اجرای migrationها (بازبینی)
- **شدت:** اطلاع‌رسانی
- **شرح:** در این محیط، اجرای تست‌های وابسته به migration با `ConfigurationError: Migration failed; inspect sanitized deployment checks.` (`alembic/env.py:147`) شکست می‌خورد؛ سرویس PostgreSQL در دسترس نیست. هیچ‌یک از ۶ migration در این audit اجرا نشد.
- **تأثیر:** ادعای «upgrade/downgrade/re-upgrade تأییدشدهٔ تاریخی» در `docs/PROJECT_STATUS.md` در این working tree بازتولید نشد.
- **اقدام:** راه‌اندازی محیط و اجرای واقعی؛ ثبت نتیجه (PASS/FAIL) در BOOTSTRAP_CHANGELOG.

