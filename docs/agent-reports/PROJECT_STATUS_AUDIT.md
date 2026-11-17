# گزارش بررسی وضعیت پروژه پیش‌حسابداری

**شناسه:** DOC-AUDIT-001  
**تاریخ:** ۱۴۰۵/۰۸/۲۷ (۲۰۲۶-۱۱-۱۷)  
**روش:** بررسی مستقیمWorking Tree، است�ام‌های گیت، migrationها، مدل‌ها، تست‌ها و مستندات

---

## ۱. خلاصه وضعیت واقعی

محرك محاسبات حقوق و دستمزد قانونی (ADR-۰۰۸، پایه ۱۴۰۴ SH) پیاده شده و ۷۴۳ تست بک‌اند با موفقیت می‌گذرند (۲ تست در سی‌сіuite کامل درisyolasiedi به دلیل مشکلonial و ۲۱ تست skip). protectingها (PII، RLS، tenant context) کد شده و تست شده‌اند. Docker در حال اجرا است و تصویر postgres:۱۶.۱۶ موجود است. Verfahren CI روی گیت‌هاب اجرا نشده است.

تسک `market_sources` / `job_market_observations` در کدبرگ وجود ندارد و DEC-۰۰۷/ADR-۰۰۸ بازاریابی را خارج از دامنه محصول اعلام کرده‌اند.

---

## ۲. جدول وضعیت تسک‌ها

| تسک | وضعیت گزارش شده | وضعیت تاییدشده | شواهد (فایل / migration / تست) | ACهای fareful | وابستگی‌ها | اقدام مالک لازم |
|:---|:---|:---|:---|:---|:---|:---|
| P0-T01 | IN_PROGRESS | IN_PROGRESS | `backend/pyproject.toml`، `uv.lock`، `ruff` و `mypy` تایید شدند؛ VCS روی `autonomous/project-completion` | CI Runs both (درایو GitHub اجرا نشده) | — | تأیید DEC-F (CI provider) |
| P0-T02 | COMPLETED | COMPLETED | `app/main.py`، `app/core/config.py`؛ `/health/live` ۲۰۰ بازگرداند | App boots، health ۲۰۰ | P0-T01 | خیر |
| P0-T03 | READY_FOR_REVIEW | READY_FOR_REVIEW | `infra/postgres/Dockerfile`، `init.sql`، `pg_hba.conf`؛ image `postgres:16.16-bookworm` Pull شده؛ verify-local PASS | harden된 پستgréSQL، TLS، pgaudit | P0-T01 | خیر (CI clause در P0-T01) |
| P0-T04 | READY_FOR_REVIEW | READY_FOR_REVIEW | `0001_statutory_baseline.py` (۵ جدول statutory، FORCE RLS)؛ ۴۸ تست integration PASS | جداول statutory، write gate، نقشه Reader/Reviewer | P0-T01، P0-T03 | DEC-۰۰۱۲ تأییدشده؛ CI migration job در P0-T۱۹ |
| P0-T05 | NOT_STARTED | READY_FOR_REVIEW | `0002_identity_foundation.py` (۷ جدول، ۷ نقش، deferred actor FKs)؛ `models/identity.py`؛ تست ۳۳۲ PASS | ابزار کاتالوگ، adopt된 FKها | P0-T۰۴ | مالک باید وضعیت را ارتقا دهد (C-۶) |
| P0-T۰۶ | READY_FOR_REVIEW | READY_FOR_REVIEW | `pii_transformer.py`، AES-۲۵۶-GCM؛ ۶ تست PASS | Round-trip، tamper detection | P0-T۰۱ | CI clause در P0-T۰۱ |
| P0-T۰۷ | READY_FOR_REVIEW | READY_FOR_REVIEW | `blind_index.py`، HMAC-SHA۲۵۶؛ ۴۵ تست PASS | Determinism، جداسازی tenant/field | P0-T۰۶، P0-T۰۸ | ح resolvesesor P0-T۰۸ برای pepper custody |
| P0-T۰۸ | NOT_STARTED | NOT_STARTED | هیچ کدی وجود ندارد | Vault adapter، local KEK، rotación | P0-T۰۱ | تصمیم ordresgerired |
| P0-T۰۹ | IN_PROGRESS | IN_PROGRESS | `0003_tenant_context.py` (`set_tenant_context`، `current_tenant_id`fail-closed)؛ `0004_manager_workspace.py` (۶ جدول tenant با FORCE RLS) | Policies on tenant tables + FORCE RLS | P0-T۰۴، P0-T۰۵ | مالک برای P0-T۰۵/P0-T۱۴ |
| P0-T۱۰ | NOT_STARTED | NOT_STARTED | هیچ `audit_logs` 테이블/کاربر نیست | زنجیره هش، append-only trigger | P0-T۰۴، P0-T۰۶ | DEC-۰۰۴ب |
| P0-T۱۱ | READY_FOR_REVIEW | READY_FOR_REVIEW | `app/storage/` 어댑تر S3؛ تست واحد PASS | Upload under GOVERNANCE | P0-T۰۱ | integrate روش RGW محلی |
| P0-T۱۳ | NOT_STARTED | BLOCKED (DEC-۰۰۷) | هیچ seed شهری/شغلی نیست | cities، taxonomy seedها | P0-T۰۴ | مالک برای DEC-۰۰۷ |
| P0-T۱۴ | NOT_STARTED | NOT_STARTED | هیچ تست penetration نیست | ISO-۰۱…ISO-۱۲ | P0-T۰۵، P0-T۰۹ |无需 مالک (نیاز به PostgreSQL+table) |
| P0-T۱۸ | NOT_STARTED | PARTIALLY_IMPLEMENTED | `auth.py`، `identity_service.py` (Argon2id، session، tenant binding) | MFA، HttpOnly، CSRF، RBAC middleware | P0-T۰۵، P0-T۰۶، P0-T۰۸ | مالک برای production-grade auth |
| P0-T۱۹ | NOT_STARTED | PARTIALLY_IMPLEMENTED | `.github/workflows/ci.yml` وجود دارد؛ روی گیت‌هاب اجرا نشده | Stages ۰–۵ | P0-T۰۱، P0-T۰۳، P0-T۱۴، P0-T۱۵ | مالک برای DEC-F و راه‌اندازی |
| P0-T۲۰ | NOT_STARTED | NOT_STARTED | هیچ gate evidence pack نیست | Gate review + archive | P0-T۱۴…P0-T۱۹ | مالک برای تایید gate |
| P1-T۱۷ | NOT_STARTED | OUT_OF_SCOPE | ADR-۰۰۸/DEC-۰۰۷رفض خارج از دامنه | باند P۱۰–P۹۰ | P1-T۰۱ | مالک برای ADR جدید |
| P1-T۱۸ | NOT_STARTED | OUT_OF_SCOPE | ADR-۰۰۸/DEC-۰۰۷رفض خارج از دامنه | Seed loader، IQR/MAD فیلتر | P0-T۱۳، P1-T۱۷ | مالک برای ADR جدید |

**تعداد:** ۲۱ تسک بررسی‌شده؛ ۲ تسک کاملی، ۶ تسک READY_FOR_REVIEW، ۴ تسک IN_PROGRESS، ۶ تسک NOT_STARTED/BLOCKED، ۲ تسک خارج از دامنه.

---

## ۳. تناقض‌ها و خطاهای گزارش قبلی

| # | ادعاء گزارش قبلی | واقعیت تاییدشده | اثر | راه حل پیشنهادی |
|:---|:---|:---|:---|:---|
| C-۱ | WBS ۸۶ تسک، ۱/۸/۱۷/۵۶/۴ | ۸۸ ردیف، ۱/۸/۲۰/۵۵/۴ | شمارش‌ 틀恼 | PROJECT_STATUS را از WBS به‌روز کنید |
| C-۲ | ۶۷۸ پас / ۱۰۵ skip | ۷۴۳ پас / ۲ fail / ۲۱ skip | تضعیف پوشش | جدول را از V-۱ به‌روز کنید |
| C-۳ | PG suites "self-skip" | ۴۸ تست integration اجرا شده و PASS | ادعا أشیاء است | "اجرای حيث Docker موجود" بنویسید |
| C-۴ | engine ۰.۳.۰ | `__init__.py`: ۰.۳.۰، `payroll_service.py`: ۰.۳.۰ | دو ثابت متضاد | خودکارسازی و تست厳格 |
| C-۵ | "هیچ کد وجود ندارد" | ۲۹ تسک پیاده‌سازی، ۷۴۰۰+ خط است | گمراهی مشارکت‌کنندگان جدید | §۱۴.۲ را historical بنویسید |
| C-۶ | P0-T۰۵ NOT_STARTED | `000۲` + `models/identity.py` پیاده شده | وضعیت کمتر از reality | READY_FOR_REVIEW با شواhed |
| C-۷ | ۱۹ تصمیم، ۱۱ باز | ۲۰ ورودی، ۱۲ باز | ردیابی ناکامل | BACKUP_CHANGELOG را به‌روز کنید |
| C-۹ | P0-T۰۴ "۱۰۱ تست" | ۴۸ تست integration جمع‌آوری شده | 숫자 drift | WBS را جبران کنید |
| C-۱۱ | فایل `adr.md` ۰ بایت | فایل ۰ بایت در ریشه | فایل مرده | مالک حذف یا پر کند |

---

## ۴. وابستگی‌های واقعی

۱. **P0-T۰۱** وابستگی ندارد (شروع کنید)
۲. **P0-T۰۲** ← P0-T۰۱
۳. **P0-T۰۳** ← P0-T۰۱
۴. **P0-T۰۴** ← P0-T۰۱، P0-T۰۳
۵. **P0-T۰۵** ← P0-T۰۴ (FKهای actor، DEC-۰۰۱۲ تأییدشده)
۶. **P0-T۰۶** ← P0-T۰۱
۷. **P0-T۰۷** ← P0-T۰۶، P0-T۰۸ (pepper custody در P0-T۰۸)
۸. **P0-T۰۸** ← P0-T۰۱ (Vault/KEK تصمیم 소유)
۹. **P0-T۰۹** ← P0-T۰۴، P0-T۰۵ (RLS policies needs tenant tables)
۱۰. **P0-T۱۰** ← P0-T۰۴، P0-T۰۶ (actor model + digest contract)
۱۱. **P0-T۱۳** ← P0-T۰۴ (b국徳 به DEC-۰۰۷ برای بخش بازاریابی)
۱۲. **P0-T۱۴** ← P0-T۰۵، P0-T۰۹ (نیاز به جدول tenant + PostgreSQL)
۱۳. **P0-T۱۸** ← P0-T۰۵، P0-T۰۶، P0-T۰۸ (production-grade auth)
۱۴. **P0-T۱۹** ← P0-T۰۱، P0-T۰۳، P0-T۱۴، P0-T۱۵ (CI provider DEC-F)
۱۵. **P1-T۱۷/۱۸** ← P0-T۱۳ (DEC-۰۰۷ خارج از دامنه)

### تشریح تناقض P0-T۰۵
گزارش قبلی نوشته "P0-T۰۵ depends on P0-T۰۴/P0-T۰۵" — این تکرارِ الذات (circular) است. real chain: P0-T۰۵ ← P0-T۰۴.

### Alembic revision chain
`0001` → `0002` → `0003` → `0004` (0003 و 0004 staged، commit نشده‌اند)

---

## ۵. تصمیم‌های موردنیاز مالک (به ترتیب اولویت)

**P۰ — قبل از هر پیاده‌سازی فنی الأزمة:**

**Decision D-۱: CI Provider (DEC-F)**
- سوال: چه ارائه‌دهنده CI برای اجرا روی گیت‌هاب انتخاب شود؟
- گزینه‌ها: (a) GitHub Actions (فعال، فایل ci.yml وجود دارد، اجرا نشده)، (b) runner شخصی‌از سرور مشتری، (c) lokal CI
- توصیه: (a) — فایل وجود دارد، `contents: read`، بدون credential، بدون استقرار
- پیward: بدون این تصمیم P0-T۰۱ و P0-T۱۹ کامل نمی‌شوند و گیت ۰ گذر می‌کنند
- فعالیت بدون این تصمیم: جزئیاً (کد و تست lokal اجرا می‌شود، CI gate نمی‌oland)

**Decision D-۲: dec-۰۰۷ (Market data licensing)**
- سوال: چگونه دادهٔ nursuce بازاریابی трофей لایسنس شود؟
- گزینه‌ها: (A) scraping زنده (ToS نقض، رد شده)، (B) دیتاست 오фلاین curated از گزارش‌های لایسنس‌شده (JobVision، IranTalent، …)، (C) شبکه give-to-get Besitzerها
- توصیه: (B) برای فاز ۱، (C) برای فاز ۲
- پیward: P0-T۱۳، P1-T۱۷، P1-T۱۸ مسدود هستند بدون این تصمیم
- فعالیت بدون این تصمیم: 엔진 کار بر روی ۱۴۰۴ ادامه می‌یابد؛ benchmark کار مسدود

**Decision D-۳: Authentication production-grade (P0-T۱۸)**
- سوال: آیا P0-T۱۸ به صورت production-grade (HttpOnly، MFA، CSRF، rate limiting، run-time DB role) پیاده شود یا محید MVP sessionStorage باقی بماند؟
- گزینه‌ها: (a) پیاده‌سازی کامل P0-T۱۸، (b) ادامه با compromises MVP (sessionStorage، بدون MFA)
- توصیه: (a) قبل از هر تست penetrate/توليد
- پیward: P0-T۱۴، P0-T۲۰، و هر استートルپ یا تولید مسدود است بدون این تصمیم

**P۱ — مهم، اما موقتاً قابل تأخیر:**

**Decision D-۴: P0-T۰۸ Key management (Vault vs local KEK)**
- سوال: Vault adapter یا local encrypted master config؟
- گزینه‌ها: (a) Vault، (b) local KEK
- توصیه: (b) برای desarrollo / MVP، (a) برای تولید
- فعالیت بدون این تصمیم: P0-T۰۶ و P0-T۰۷ کد دارند، اما pepper custody gerçek نشده

**P۲ — قابل تأخیر:**

**Decision D-۵: Fich adr.md (۰ بایت)**
- سوال: فایل ریشه `adr.md` را حذف کنید یا پر کنید؟
- گزینه‌ها: (a) حذف، (b) پر کردن با محتوای historischen
- توصیه: (a) — فایل مرده، از git ls-files تضمین نشده
- فعالیت بدون این quyết: تاثیر روی کد ندارد

---

## ۶. ریسک‌های فنی و امنیتی

| # | ریسک | شدت | توضیح |
|:---|:---|:---|:---|
| R-۱ | RLS penetration suite نیست | بالا | P0-T۱۴ Not Started؛ هیچ تست cross-tenant روی پایگاه داده thực وجود ندارد |
| R-۲ | توکن در sessionStorage | بالا | MVP tooth-cookie نیست؛ XSS می‌تواند 토کن را 직면 کند |
| R-۳ | zwei ENGINE_VERSION constants | متوسط | `app/engines/__init__.py` (۰.۳.۰) و `payroll_service.py` (۰.۳.۰) — الدعوة справа contradictory |
| R-۴ | ۲ تست async درuite کامل Fail | متوسط | `test_apply_tenant_context_*` در suite کامل fail می‌شوند، جداگانه pass (test isolation issue) |
| R-۵ | migrations ۰۰۰۳/۰۰۰۴ staged، commit نشده | متوسط | rollback risco؛状態 ن明確 |
| R-۶ | P0-T۰۸ punch没有 | بالا | بدون pepper custody، PII encryption و blind index در تولید قابل اعتماد نیست |
| R-۷ | audit ledger نیست | بالا | P0-T۱۰ Not Started؛決ته‌ها append-only اما به‌درجة chaining نیستند |

---

## ۷. تخمین زمان باقی‌مانده (واقع‌بینانه)

انجام کارهای باقی‌مانده فاز ۰ (حذف خارج از دامنه):

| فاز | کارهای انجام‌شده باقی‌مانده | تلاش Engineer-Day | Calendar (مثلاً托 dispatcher) |
|:---|:---|---:|---:|
| ۰ | P0-T۰۱ (CI clause)، P0-T۰۳، P0-T۰۴، P0-T۰۵، P0-T۰۸، P0-T۰۹، P0-T۱۰، P0-T۱۱، P0-T۱۳، P0-T۱۴، P0-T۱۵، P0-T۱۶، P0-T۱۷، P0-T۱۸، P0-T۱۹، P0-T۲۰ | ~۳۰–۴۰ روز | ۴–۶ هفته (parallelize P0-T۰۶‖۰۷‖۱۱‖۱۳‖۱۶‖۱۷) |
| ۱ (فقط 엔진) | P1-T۰۱…P1-T۱۴، P1-T۱۶، P1-T۱۹ | ~۱۵–۲۰ روز | ۳–۵ هفته |

**مجموع davvero باقی‌مانده:** ۴۵–۶۰ Engineer-Day، تقویم تقریبی **۵–۸ هفته** باParallelization منطقی و شامل تست/بررسی/بازبینی مستقل. اینرقام假يت P0-T۰۱ CI clause و P0-T۱۸ production auth در مسیر filming قرار می‌گیرند.

**فرضیات:** Docker در دسترس است؛ PostgreSQL lokale اجرا می‌شود؛ مالک DEC-F، DEC-۰۰۷، P0-T۱۸ را در هفتهٔ اول決定 می‌کند؛ هیچ استقراری تولیدی در этапе حاضر geplant نیست.

---

## ۸. پیشنهاد دقیق برای گام بعدی

۱. مالک DEC-F (CI provider) را تأیید کند تا P0-T۰۱ و P0-T۱۹ کامل شوند و Workflow روی گیت‌هاب اجرا شود.
۲. مالک DEC-۰۰۷ (B) را تأیید کند تا P0-T۱۳ بخش cidade/taxonomy سراغ داشته باشد و benchmark مربوطه در خارج از دامنه بماند (ADR-۰۰۸).
۳. migration‌های ۰۰۰۳ و ۰۰۰۴ را commit کنید (حالیاً staged و commit نشده‌اند) و rollback را روی disposable PostgreSQL ۱۶ تست کنید.
۴. P0-T۰۵ را از NOT_STARTED به READY_FOR_REVIEW ارتقا دهید (ثابت شده است).
۵. ریسک R-۱ (P0-T۱۴ penetration suite) را در فاز بعد برنامه‌ریزی کنید بعد از وجود جدول tenant.

---

## ۹. شواهد تکنیکال (추가로)

- **Git:** شاخه `autonomous/project-completion`، HEAD `74685e7`؛ ۱۴۱ فایل staged، ۳ فایل unstaged Modified (EXECUTION_PLAN.md، PROJECT_STATUS.md، LATEST_REPORT.md)
- **Alembic:** ۴ migration (۰۰۰۱–۰۰۰۴)، chain linear
- **Docker:** نسخه ۲۹.۹.۲، سرور در حال اجرا، تصویر `postgres:16.16-bookworm` Pull شده
- **تست بک‌اند:** ۷۴۳ PASS، ۲ FAIL (test_tenant_context async isolation)، ۲۱ SKIP (40.۶۱s)
- **تست فرانت‌اند:** ۱۲۳ PASS، tsc clean، build ۲.۵۰s
- **ruff/mypy:** ruff `All checks passed!`؛ mypy `Success: no issues found in 50 source files`
- **Integration migration:** ۴۸ تست PASS (pish_statutory_migrations.py)، round-trip upgrade/downgrade/upgrade PASS
