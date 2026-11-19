# حسابرسی تست و کیفیت

**تاریخ:** ۲۸ آبان ۱۴۰۵ (2026-11-18)
**شناسه:** AUDIT-07
**وضعیت:** تکمیل‌شده در ادامهٔ حسابرسی (پیش از این وجود نداشت)

---

## ۰. روش و مبنای شواهد

تمام نتایج این گزارش با اجرای واقعی ابزارها در همین working tree به دست آمده‌اند، نه از ادعای مستندات. هیچ فایلی از کد برنامه تغییر نکرد؛ فقط دستورهای read-only اجرا شد.

| # | دستور | نتیجه | حکم |
|:--:|:---|:---|:--:|
| ۱ | `npx tsc --noEmit -p tsconfig.app.json` (frontend) | ۹ خطای نحوی در ۳ فایل، exit 1 | **FAIL** |
| ۲ | `npx vitest run` (frontend) | ۴ تست شکست / ۱۲۴ موفق (۲ فایل شکست از ۱۵) | **FAIL** |
| ۳ | `python -m pytest -q` (backend) | ۷۶۱ موفق، ۴۹ skip، ۲۵ error | **FAIL** |
| ۴ | `python -m ruff check .` (backend) | ۲۵ خطا، exit 1 | **FAIL** |
| ۵ | `python -m mypy --strict` روی ماژول‌های تخمین | ۸ خطا در ۵ فایل | **FAIL** |
| ۶ | `vite build` | اجرا نشد (به‌دلیل FAIL بودن tsc) | **NOT RUN** |
| ۷ | تست اتصال PostgreSQL / migration | اجرا نشد (سرویس دیتابیس در دسترس نیست) | **NOT RUN** |
| ۸ | CI روی GitHub | هرگز اجرا نشده (طبق `docs/PROJECT_STATUS.md`) | **NOT RUN** |

**نتیجهٔ کلی:** «کد سبز» نیست. هر چهار دروازهٔ کیفیت (typecheck، test، lint، types) در وضعیت قرمز هستند.

---

## ۱. یافته‌ها

### TEST-01 — شکست typecheck فرانت‌اند (خطای نحوی)
- **شدت:** بحرانی
- **شرح:** `tsc --noEmit` با ۹ خطای نحوی در سه فایل شکست می‌خورد. build تولیدی (`tsc && vite build`) قطعاً شکست می‌خورد.
- **شواهد (خروجی واقعی):**
  - `src/components/salary-discovery/SalaryDiscoveryPage.tsx(351,70)` و `(352,23)`
  - `src/components/salary-estimation/SalaryEstimationPage.tsx(61,28)` و `(61,30)`
  - `src/lib/salary-benchmarks.ts(99,40)`, `(99,61)`, `(99,64)`, `(99,74)`, `(100,5)`
- **مسیر و خط:**
  - `frontend/src/components/salary-discovery/SalaryDiscoveryPage.tsx:351` → متن `class отч://selectedBenchmark.maxSalary}` (حروف سیریلیک و `://` داخل JSX)
  - `frontend/src/lib/salary-benchmarks.ts:99` → `experienceRange: { min: 1, max: man's experience range' to 'maximum' }`
  - `frontend/src/components/salary-estimation/SalaryEstimationPage.tsx:61` → `نسخه{v1.0}`
- **تأثیر:** محصول قابل build نیست؛ هیچ‌یک از صفحات تخمین/بازار حقوق قابل عرضه نیست.
- **اقدام:** حذف/بازنویسی سه قطعهٔ خراب، سپس اجرای مجدد `tsc` (پس از رفع، خطاهای پنهان بعدی — مانند TEST-02 — ظاهر می‌شوند).
- **وضعیت تأیید:** ✅ تأییدشده با اجرای ابزار.

### TEST-02 — وابستگی‌های import‌شده اما نصب‌نشده و اعلام‌نشده
- **شدت:** بحرانی
- **شرح:** `SalaryEstimationForm.tsx` سه ماژول را import می‌کند که نه در `package.json` هستند و نه در `node_modules`:
  `react-hook-form`، `@hookform/resolvers/zod`، `zod`.
- **شواهد:** `Test-Path frontend/node_modules/react-hook-form` → False؛ همان برای `zod` و `@hookform` → False؛ `frontend/package.json` این سه را ندارد.
- **مسیر و خط:** `frontend/src/components/salary-estimation/SalaryEstimationForm.tsx:9-11`
- **تأثیر:** پس از رفع خطاهای نحوی، `tsc` خطای «Cannot find module» می‌دهد و صفحهٔ تخمین هرگز رندر نمی‌شود. همچنین افزودن وابستگی جدید بدون تصویب، نقض AGENTS.md §13.11 است.
- **اقدام:** یا حذف react-hook-form/zod و بازنویسی فرم با state بومی (سازگار با قاعدهٔ «no new UI or state library»)، یا ثبت درخواست رسمی افزودن وابستگی.
- **وضعیت تأیید:** ✅ تأییدشده.

### TEST-03 — شکست تست‌های فرانت‌اند (ناوبری و قراردادها)
- **شدت:** بالا
- **شرح:** ۴ تست شکست می‌خورد:
  1. `src/api/contracts.test.ts > marks delivered contracts` — انتظار `['health.live','simulations.gross-to-net']`، دریافت مجموعه‌ای که `estimations.create` هم دارد.
  2. `src/app/app-shell.test.tsx > links every primary screen directly in the main navigation`
  3. `src/app/app-shell.test.tsx > links every deferred module in the collapsed section`
  4. `src/app/app-shell.test.tsx > never links two navigation entries to the same path` → `expected 13 to be 14` (یعنی یک مسیر تکراری وجود دارد).
- **شواهد:** خروجی vitest؛ علت ریشه‌ای: `navigation.ts` مسیر `/salaries` را هم در `PRIMARY_NAV_ITEMS` و هم در `NAV_ITEMS` دارد و `app-shell.tsx:158` فقط `PRIMARY_NAV_ITEMS` را در بخشی و `NAV_ITEMS` را در بخش دیگر رندر می‌کند.
- **مسیر و خط:** `frontend/src/app/navigation.ts:55-63` و `:82-91`؛ `frontend/src/app/app-shell.tsx:14,158`؛ `frontend/src/api/contracts.ts:119`
- **تأثیر:** رگرسیون واقعی در ناوبری (آیتم تکراری) و در فهرست «قراردادهای تحویل‌شده»؛ نشان می‌دهد تغییرات اخیر بدون اجرای تست ذخیره شده‌اند.
- **اقدام:** یکسان‌سازی مدل ناوبری (یک منبع حقیقت)، به‌روزرسانی تست قراردادها همراه با تغییر واقعی قرارداد.
- **وضعیت تأیید:** ✅ تأییدشده.

### TEST-04 — شکست lint بک‌اند
- **شدت:** بالا
- **شرح:** `ruff check .` ۲۵ خطا گزارش می‌کند؛ منبع آن‌ها سه فایل است: `create_first_user.py` (۱۸)، `debug_api.py` (۶)، `app/schemas/estimation.py` (۱: RUF022).
- **شواهد:** از جمله `S105 Possible hardcoded password assigned to: "password"` در `create_first_user.py:67` و `T201 print found` در چند خط.
- **تأثیر:** دروازهٔ lint در `ci.yml` قرمز است؛ همچنین S105 یک هشدار امنیتی واقعی است (نک. SEC-16).
- **اقدام:** حذف اسکریپت‌های موقت از مخزن یا انتقال به `scripts/` با مستندسازی؛ رفع RUF022.
- **وضعیت تأیید:** ✅ تأییدشده.

### TEST-05 — شکست mypy --strict در ماژول‌های تخمین
- **شدت:** بالا
- **شرح:** ۸ خطا در ۵ فایل، از جمله `no-any-return` در `matcher.py:155,179,191`، `[type-arg]` برای `dict` بدون پارامتر نوع در `schemas.py:132,137` و `app/schemas/estimation.py:60`، و `attr-defined` در `domain/salary_estimation/__init__.py:25`.
- **نکتهٔ مهم:** `adjuster.py:9` نیز `Cannot find implementation or library stub for module named "backend.app.engines.money"` می‌دهد — مسیر import اشتباه است (`backend.app...` به‌جای `app...`). این ماژول در هیچ‌جا import نمی‌شود؛ کد مرده است (BE-16).
- **تأثیر:** دروازهٔ `mypy --strict` (که در `docs/PROJECT_STATUS.md` برای ۸۶ فایل PASS ثبت شده) برای کد جدید برقرار نیست.
- **اقدام:** رفع خطاها یا حذف کد مرده (adjuster.py/mock_data.py).
- **وضعیت تأیید:** ✅ تأییدشده.

### TEST-06 — suite بک‌اند «سبز» نیست
- **شدت:** بالا
- **شرح:** ۷۶۱ PASS، ۴۹ skip، **۲۵ error**. خطاها همه از fixtureهای وابسته به PostgreSQL هستند و با `ConfigurationError: Migration failed; inspect sanitized deployment checks.` متوقف می‌شوند.
- **شواهد:** اجرای `tests/api/test_manager_workspace.py::test_rules_endpoint_publishes_provisional_contract` → خطا در `alembic/env.py:147` هنگام اتصال.
- **تأثیر:** حدود یک‌سوم مسیرهای persistence (auth، manager workspace، work profile، migration) در این محیط **قابل تأیید نیستند**. هر ادعای «PASS» دربارهٔ این مسیرها در مستندات، تاریخی است و در این audit بازتولید نشد.
- **اقدام:** راه‌اندازی PostgreSQL توسعه و اجرای مجدد؛ ثبت نتیجه در BOOTSTRAP_CHANGELOG.
- **وضعیت تأیید:** ✅ تأییدشده (شکست) — علت: محیط، نه لزوماً کد.

### TEST-07 — نبود تست برای مسیر پول تخمین
- **شدت:** بالا
- **شرح:** تنها فایل تست دامنه، `tests/domain/salary_estimation/test_money_validation.py` است که صرفاً `validate_estimation_money_path` را می‌سنجد؛ هیچ تستی:
  - ضرایب `SalaryAdjuster` را با `Decimal` بررسی نمی‌کند،
  - عدم استفاده از float در مسیر مبلغ را تضمین نمی‌کند (نقض BE-01 بی‌آزمون مانده)،
  - بردار طلایی (golden vector) برای تخمین ندارد،
  - تست property برای تخمین ندارد (تست‌های Hypothesis فقط برای موتور حقوق است).
- **تأثیر:** نقض invariant مالی می‌تواند بدون هیچ تستی وارد تولید شود — و شده است.
- **اقدام:** افزودن تست‌های واحد+property روی `estimate_salary` با ورودی‌های مرزی، و تست «هیچ float در مسیر مبلغ».
- **وضعیت تأیید:** ✅ تأییدشده (نبود تست).

### TEST-08 — تست‌های e2e قرارداد غلط را تثبیت می‌کنند
- **شدت:** بالا
- **شرح:** `backend/tests/e2e/*.py` سه مشکل دارد:
  1. برای شهر ناشناخته، `status_code == 200` و صفر بودن سه مبلغ را assert می‌کند؛ در حالی که ADR-013 (D-06)، FR-07 و `SALARY_ESTIMATION_SPEC.md §3` می‌گویند باید «امتناع» شود. تست، رفتار مغایر با تصمیم مصوب را قفل می‌کند.
  2. در همهٔ تست‌های موفق، فیلد `education` صریحاً ارسال می‌شود؛ به همین دلیل نقص BE-06 (که UI هرگز education نمی‌فرستد و پاسخ ۴۲۲ می‌گیرد) پنهان می‌ماند.
  3. assertهای تکراری (سه خط دو بار تکرار شده) نشانهٔ کپی بدون بازبینی است.
- **مسیر و خط:** `backend/tests/e2e/` (فایل تست تخمین)، بخش `test_estimate_salary_insufficient_data`.
- **تأثیر:** «تست سبز» گمراه‌کننده است: تست، نقص محصول را تأیید می‌کند.
- **اقدام:** بازنویسی تست بر اساس تصمیم مصوب (امتناع، نه صفر) و افزودن تست «payload واقعی UI».
- **وضعیت تأیید:** ✅ تأییدشده.

### TEST-09 — تستی که چیزی را assert نمی‌کند
- **شدت:** متوسط
- **شرح:** `test_invalid_range_consistency` (min > primary > max) فقط `isinstance(...)` را بررسی می‌کند و در کامنت می‌نویسد «Range still valid mathematically, just check validation logic». یعنی نبودِ بررسی بازه، در تست پذیرفته شده است.
- **مسیر و خط:** `backend/tests/domain/salary_estimation/test_money_validation.py:29-36`
- **تأثیر:** توهم پوشش تست؛ هم‌راستا با BE-13 (validation دور ریخته می‌شود).
- **اقدام:** تست باید شکست را انتظار ببرد و تابع باید واقعاً `min ≤ primary ≤ max` را بسنجد.
- **وضعیت تأیید:** ✅ تأییدشده.

### TEST-10 — صفر تست برای کامپوننت‌های تخمین/بازار حقوق
- **شدت:** متوسط
- **شرح:** از ۱۵ فایل تست فرانت‌اند، هیچ‌کدام `SalaryEstimationPage`، `SalaryEstimationForm`، `SalaryEstimationResults`، `SalaryDiscoveryPage` یا `salary-benchmarks.ts` را پوشش نمی‌دهد.
- **تأثیر:** خطاهای نحوی و متنی (TEST-01، FE-08) توسط CI گرفته نمی‌شوند.
- **اقدام:** تست render + تست snapshot متن فارسی + تست نبود اعداد float در نمایش پول.
- **وضعیت تأیید:** ✅ تأییدشده.

### TEST-11 — تست‌ها برای کد مرده وجود ندارد و کد مرده تست نشده رها شده
- **شدت:** پایین
- **شرح:** `app/domain/salary_estimation/adjuster.py` و `mock_data.py` در هیچ جایی import نمی‌شوند (جست‌وجوی سراسری: صفر ارجاع) و تستی هم ندارند.
- **تأثیر:** حجم کد فعال را بزرگ‌تر از واقع نشان می‌دهد و مسیر import شکسته (TEST-05) را پنهان می‌کند.
- **اقدام:** حذف یا ادغام.
- **وضعیت تأیید:** ✅ تأییدشده.

### TEST-12 — حجم واقعی مجموعهٔ تست (اطلاع‌رسانی)
- **شدت:** اطلاع‌رسانی
- **شرح:** بک‌اند: ۸۳۵ تست collect می‌شود (۲۶ فایل unit، ۶ api، ۵ integration، ۲ property، ۱ e2e، ۱ domain). فرانت‌اند: ۱۵ فایل / ۱۲۸ تست. LOC: بک‌اند ۱۰٬۹۵۵، تست بک‌اند ۷٬۳۷۵، فرانت‌اند ۹٬۴۰۲.
- **ارزیابی:** نسبت تست به کد در بک‌اند خوب است؛ مشکل در **کیفیت و صدق** تست‌های ناحیهٔ جدید است، نه کمیت کلی.

---

## ۲. ماتریس پوشش ناحیه‌ها

| ناحیه | تست واحد | تست API | تست property | تست e2e | حکم |
|:---|:--:|:--:|:--:|:--:|:--:|
| money primitives (`engines/money.py`) | ✅ | — | ✅ | — | خوب |
| SSO/مالیات/سنوات/عیدی/CTC | ✅ | ✅ | ✅ | — | خوب |
| rule-set loader (fail-closed) | ✅ | ✅ | — | — | خوب |
| PII encryption / blind index | ✅ | — | — | — | خوب |
| identity / auth | ✅ | ✅ (نیازمند DB) | — | — | تأییدنشده در این محیط |
| work profile / manager | ✅ | ✅ (نیازمند DB) | — | — | تأییدنشده در این محیط |
| **تخمین حقوق (دامنه)** | ⚠️ فقط money_validation | ⚠️ e2e غلط | ❌ | ⚠️ | **ضعیف** |
| **فرانت: تخمین/بازار حقوق** | ❌ | ❌ | ❌ | ❌ | **هیچ** |
| **فرانت: ناوبری/قرارداد** | ✅ | — | — | — | **شکست** |

---

## ۳. توصیه‌های اولویت‌دار

1. **P0:** رفع ۹ خطای نحوی و ۳ وابستگی گمشده تا build ممکن شود.
2. **P0:** افزودن تست «payload دقیق UI» به e2e — این تست همین امروز BE-06 را می‌گیرد.
3. **P1:** بازنویسی تست `insufficient_data` مطابق ADR-013 D-06 (امتناع).
4. **P1:** تست property روی `SalaryAdjuster` و ممنوعیت float در مسیر مبلغ.
5. **P1:** پاک‌سازی اسکریپت‌های موقت (`create_first_user.py`, `debug_api.py`) تا lint سبز شود.
6. **P2:** راه‌اندازی PostgreSQL توسعه و ثبت نتیجهٔ ۲۵ تست خطادار.
7. **P2:** تست قرارداد (`contracts.test.ts`) باید همراه تغییر قرارداد به‌روز شود، نه بعد از آن.

> **هشدار روش‌شناختی:** ادعای `docs/PROJECT_STATUS.md` مبنی بر «۷۶۵ PASS + ۱۲۳ تست فرانت PASS + typecheck/build PASS» در این working tree **بازتولید نشد**. آن اعداد مربوط به commit قبلی و پیش از افزودن کد تخمین هستند.
