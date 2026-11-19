# حسابرسی امنیت

**تاریخ:** ۲۸ آبان ۱۴۰۵  
**شناسه:** AUDIT-06

---

## ۱. خلاصه یافته‌ها

| شدت | تعداد |
|:---|:--:|
| بحرانی | ۲ |
| بالا | ۴ |
| متوسط | ۳ |
| پایین | ۲ |
| اطلاع‌رسانی | ۳ |

---

## ۲. یافته‌ها

### SEC-01: اطلاعات حساس در working tree
- **شدت:** بحرانی
- **فایل:** `backend/.env` خط ۶
- **شواهد:** `DATABASE_URL=postgresql://postgres:<REDACTED-DB-PASSWORD>@127.0.0.1:55432/pish_dev`
- **وضعیت `.gitignore`:** `.env` exclude شده — فایل tracked نیست
- **ریسک:** اگر `.gitignore` اشتباهی تغییر کند، رمز عبور commit می‌شود. همچنین `BLIND_INDEX_PEPPER` و `MASTER_KEK` هم در `.env` هستند
- **اقدام:** استفاده از secret manager یا حداقل git pre-commit hook برای بررسی

### SEC-02: دایرکتوری .secrets/ در مخزن
- **شدت:** بحرانی
- **فایل:** `.secrets/postgres/` حاوی `ca.key`, `server.key`, `password`, `ca.crt`, `server.crt`
- **وضعیت `.gitignore`:** `.secrets/` exclude شده
- **ریسک:** کلیدهای خصوصی TLS و رمز عبور PostgreSQL در working tree
- **اقدام:** انتقال به secret manager؛ حداقل اطمینان از عدم commit

### SEC-03: Salary estimation بدون authentication
- **شدت:** بالا
- **فایل:** `backend/app/api/v1/estimation/__init__.py` خط ۴۶
- **شواهد:** `async def salary_estimation(payload: EstimateRequest)` — هیچ `ManagerRequired` dependency
- **تأثیر:** هر کسی می‌تواند estimate بگیرد بدون login
- **اقدام:** افزودن auth dependency یا rate limiting

### SEC-04: عدم وجود rate limiting
- **شدت:** بالا
- **شواهد:** هیچ rate limiter middleware در `main.py`
- **تأثیر:** API در برابر brute-force و DoS آسیب‌پذیر
- **اقدام:** افزودن rate limiting (slowapi یا مشابه)

### SEC-05: CORS فقط برای localhost
- **شدت:** بالا (مثبت ولی ناقص)
- **فایل:** `backend/app/core/config.py` خط ۹۸-۱۰۱
- **شواهد:** فقط `localhost:5173`, `localhost:5273`, `127.0.0.1:5173`, `127.0.0.1:5273`
- **مثبت:** restrictive است
- **ریسک:** اگر production deploy شود بدون تنظیم جدید، frontend روی domain دیگر کار نمی‌کند
- **اقدام:** environment-specific CORS origins

### SEC-06: Session token در sessionStorage
- **شدت:** بالا
- **فایل:** `frontend/src/prototype/session.ts` خط ۳۶
- **شواهد:** `const SESSION_KEY = 'pish.manager.session.v1'` → sessionStorage
- **ریسک:** XSS می‌تواند token را بخواند. مستندات خودش می‌گوید «HttpOnly cookie is the production target»
- **اقدام:** انتقال به HttpOnly cookie در production

### SEC-07: Argon2id password hashing — مثبت
- **شدت:** اطلاع‌رسانی (مثبت)
- **فایل:** `backend/app/services/identity_service.py` خط ۴۳
- **شواهد:** `PasswordHasher()` با پارامترهای default argon2-cffi
- **ارزیابی:** ✅ خوب — Argon2id استاندارد صنعت

### SEC-08: Account lockout — مثبت
- **شدت:** اطلاع‌رسانی (مثبت)
- **فایل:** `identity_service.py` خطوط ۷۸-۸۴
- **شواهد:** ۵ تلاش ناموفق → قفل ۱۵ دقیقه‌ای
- **ارزیابی:** ✅ خوب

### SEC-09: AES-256-GCM PII encryption — مثبت
- **شدت:** اطلاع‌رسانی (مثبت)
- **فایل:** `backend/app/core/security/pii_transformer.py`
- **شواهد:** Fresh 96-bit nonce, context authentication, tenant/record/field binding
- **ارزیابی:** ✅ عالی — ولی در salary estimation scope استفاده نمی‌شود (ADR-013: simplified)

### SEC-10: Blind indexing — مثبت
- **شدت:** اطلاع‌رسانی
- **فایل:** `backend/app/core/security/blind_index.py`
- **ارزیابی:** ✅ HMAC-SHA256 با pepper جداگانه

### SEC-11: Error responses بدون اطلاعات حساس
- **شدت:** پایین (مثبت)
- **فایل:** `main.py` خطوط ۱۳۵-۱۵۸
- **شواهد:** Validation errors فقط field path و type گزارش می‌کنند — مقادیر مالی echo نمی‌شوند
- **ارزیابی:** ✅ خوب

### SEC-12: OpenAPI docs در production غیرفعال
- **شدت:** پایین (مثبت)
- **فایل:** `main.py` خطوط ۷۷-۷۹
- **شواهد:** `docs_url=None, redoc_url=None, openapi_url=None` وقتی `app_debug=False`
- **ارزیابی:** ✅ خوب

### SEC-13: Tenant context binding — مثبت (payroll-era)
- **شدت:** متوسط
- **فایل:** `backend/app/api/deps.py` خطوط ۱۰۸-۱۵۶
- **شواهد:** `require_manager` tenant را از session می‌خواند نه از client
- **ارزیابی:** ✅ خوب — ولی ADR-013 tenancy را حذف کرده

### SEC-14: CI permissions minimal
- **شدت:** متوسط (مثبت)
- **فایل:** `.github/workflows/ci.yml` خط ۳۵
- **شواهد:** `permissions: contents: read`
- **ارزیابی:** ✅ least privilege

### SEC-15: `create_first_user.py` بدون بررسی
- **شدت:** متوسط
- **فایل:** `backend/create_first_user.py`
- **ریسک:** اسکریپت ایجاد کاربر بدون audit trail
- **اقدام:** بررسی محتوا و محدودسازی

---

## ۳. ماتریس امنیتی

| کنترل | Payroll-era | Salary Estimation |
|:---|:--:|:--:|
| Authentication | ✅ Argon2id + Bearer | ❌ هیچ |
| Authorization (roles) | ✅ OWNER/ADMIN/HR_MANAGER | ❌ هیچ |
| Tenant isolation (RLS) | ✅ FORCE RLS | ❌ حذف شده (ADR-013) |
| PII encryption | ✅ AES-256-GCM | ❌ حذف شده (ADR-013) |
| Blind indexing | ✅ HMAC-SHA256 | ❌ حذف شده |
| Rate limiting | ❌ ندارد | ❌ ندارد |
| CSRF protection | ⚠️ Bearer token (implicit) | ❌ ندارد |
| Input validation | ✅ Pydantic | ✅ Pydantic |
| Error sanitization | ✅ No monetary echo | ✅ |
| Audit trail | ✅ Append-only | ❌ ندارد |
| Session management | ✅ Server-side, revocable | ❌ ندارد |

---

## ۴. توصیه‌ها (به ترتیب اولویت)

1. **افزودن auth به salary estimation endpoint** — حتی ساده (API key یا shared secret)
2. **افزودن rate limiting** — به خصوص برای login و estimation
3. **انتقال secrets از .env به secret manager** — یا حداقل pre-commit hook
4. **حذف .secrets/ از working tree** — یا اطمینان از exclude بودن
5. **انتقال token به HttpOnly cookie** — برای production

---

## ۵. پیوست بازبینی مستقل (ادامهٔ حسابرسی — ۲۸ آبان ۱۴۰۵)

### SEC-00 — تصحیح وضعیت git برای SEC-01 و SEC-02 (بازبینی)
- **شدت:** اطلاع‌رسانی
- **شرح:** با `git ls-files` تأیید شد که هیچ‌یک از `backend/.env` و `.secrets/` **tracked نیستند**؛ `git check-ignore -v` صریحاً آن‌ها را به `.gitignore:16` و `.gitignore:21` نسبت می‌دهد. تنها فایل‌های tracked مرتبط، `backend/.env.example` و `frontend/.env.example` هستند.
- **تأثیر:** ریسک «ورود رمز به تاریخچهٔ git» فعلاً محقق نشده است؛ اما ریسک باقی‌مانده (تغییر تصادفی `.gitignore`، کپی شدن فایل، پشتیبان‌گیری بدون exclude) واقعی است.
- **اقدام:** pre-commit hook با `gitleaks`/`detect-secrets` (پیشنهاد؛ نیازمند تصویب نصب ابزار).

### SEC-16 — رمز پیش‌فرض مدیر با دسترسی platform admin در مخزن
- **شدت:** بالا
- **شرح:** `backend/create_first_user.py` یک کاربر با `is_platform_admin=True`، ایمیل ثابت `manager@example.com` و رمز **hardcoded** می‌سازد و رمز را در stdout چاپ می‌کند. این اسکریپت همچنین با `Base.metadata.create_all` schema می‌سازد و Alembic را دور می‌زند.
- **شواهد:** `create_first_user.py:67` (`password = "<REDACTED-DEFAULT-PASSWORD>"`)؛ `:78` (`is_platform_admin=True`)؛ `:104` (چاپ رمز)؛ `:26-30` (`create_all`). `ruff` نیز همین را با `S105` علامت زده است.
- **تأثیر:** اگر اجرا شود، یک حساب مدیر با رمز شناخته‌شده ساخته می‌شود؛ لاگ‌های CI/ترمینال رمز را نگه می‌دارند. نقض AGENTS.md §2.15 و §8.
- **اقدام:** حذف فایل از مخزن یا تبدیل به اسکریپت با رمز اجباری از متغیر محیط، بدون چاپ رمز، بدون `create_all`، و بدون `is_platform_admin` پیش‌فرض (DEC-15).

### SEC-17 — رمز واقعی دیتابیس در متن گزارش حسابرسی قبلی
- **شدت:** بالا
- **شرح:** بخش SEC-01 همین گزارش، مقدار کامل `DATABASE_URL` شامل رمز PostgreSQL را **به‌صورت متن ساده** درج کرده است. این نقض AGENTS.md §8/§15 است («هرگز رمز را چاپ/ثبت نکن») و خود گزارش را به یک artifact حاوی راز تبدیل می‌کند.
- **تأثیر:** هر کسی که `audit/` را بخواند یا به اشتراک بگذارد، رمز را می‌بیند. حتی با gitignored بودن `.env`، گزارش در working tree است.
- **اقدام:** (۱) خط مذکور در SEC-01 سانسور شد (ادامهٔ حسابرسی، ۲۸ آبان ۱۴۰۵: مقدار با `<REDACTED-DB-PASSWORD>` جایگزین شد؛ یافته و ساختار حفظ شده‌اند)؛ (۲) **rotate کردن رمز دیتابیس همچنان لازم است**، چون مقدار واقعی در یک فایل متنی در working tree قرار داشته است؛ (۳) قاعدهٔ «هیچ مقدار SecretStr در گزارش» در روش‌شناسی audit.
- **توجه:** این سانسیور فقط حذف مقدار محرمانه است، نه تغییر یافته؛ متن اصلی یافته در SEC-01 دست‌نخورده باقی مانده است.

### SEC-18 — نشت متن استثنا به کاربر در endpoint تخمین
- **شدت:** متوسط
- **شرح:** `except Exception as exc: return _error_response(422, "ESTIMATION_ENGINE_ERROR", str(exc))` متن خام خطا را در پاسخ API می‌گذارد، در حالی که طراحی سراسری (`main.py:135-159`) عمداً مقادیر را از خطاها حذف می‌کند.
- **مسیر و خط:** `backend/app/api/v1/estimation/__init__.py:61-62`
- **تأثیر:** نشت جزئیات پیاده‌سازی/پیکربندی به مهاجم.
- **اقدام:** کد خطای ثابت + لاگ داخلی با correlation id.

### SEC-19 — اسکریپت‌های موقت و اثرانگشت محیط
- **شدت:** پایین
- **شرح:** `backend/debug_api.py` (untracked) و `backend/create_first_user.py` (untracked) در ریشهٔ بک‌اند هستند، نه در `scripts/`، و هیچ سندی آن‌ها را تعریف نکرده است. `debug_api.py` پاسخ خام API را چاپ می‌کند.
- **تأثیر:** سطح حمله و ابهام عملیاتی؛ شکست lint (TEST-04).
- **اقدام:** حذف یا انتقال به `scripts/` با مستندسازی (DEC-13).

### بازبینی ماتریس امنیتی
ماتریس بخش ۳ همچنان معتبر است. افزودهٔ این بازبینی:

| کنترل | وضعیت واقعی (تأییدشده) |
|:---|:---|
| Secret در تاریخچهٔ git | ✅ پاک (`.env` و `.secrets/` tracked نیستند) |
| Secret در artifactهای working tree | ❌ **موجود** (SEC-17 و SEC-16) |
| کنترل ورودی دامنهٔ تخمین | ❌ **بی‌اثر** (BE-07) — کنترل ادعاشده وجود ندارد |
| قرارداد خطای یکسان | ⚠️ نقض موضعی (SEC-18) |
| rate limiting | ❌ (SEC-04 تأیید شد: هیچ middleware‌ای در `main.py` نیست) |

