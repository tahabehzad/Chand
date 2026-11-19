# حسابرسی بک‌اند

**تاریخ:** ۲۸ آبان ۱۴۰۵  
**شناسه:** AUDIT-03

---

## ۱. خلاصه

بک‌اند شامل دو سیستم کاملاً متفاوت است:

| سیستم | کیفیت | وضعیت |
|:---|:--:|:---|
| موتور حقوق قانونی (`engines/`) | ⭐⭐⭐⭐⭐ | مهندسی عالی، Decimal money، تست جامع |
| تخمین حقوق بازار (`domain/salary_estimation/`) | ⭐⭐ | Mock data، float violations، scaffold |

---

## ۲. موتور حقوق قانونی (engines/) — ارزیابی مثبت

### ۲.۱ money.py — کیفیت عالی
- `prec=34`, `ROUND_HALF_UP` فقط
- هیچ `float` یا `round()` استفاده نشده
- `RoundingReport` با residual tracking
- `RialAllocation` با largest-remainder method
- Internal context مستقل از ambient context
- تست‌های property-based جامع

### ۲.۲ rules.py — Fail-closed loader
- YAML floats به `Decimal` تبدیل می‌شوند (نه float)
- `is_verified_and_active: false` → exception
- ۱۱ invariant (R-01 تا R-11) بررسی می‌شوند
- SHA-256 fingerprint برای reproducibility
- 1405 صریحاً reject می‌شود

### ۲.۳ سایر engines
| ماژول | عملکرد | وضعیت |
|:---|:---|:--:|
| `bases.py` | Base decomposition (مزد مبنا، مزد ثابت) | ✅ |
| `sso.py` | بیمه تأمین اجتماعی (سقف قابل بیمه) | ✅ |
| `tax.py` | مالیات پلکانی + دو posture ماده ۱۳۷ | ✅ |
| `overtime.py` | اضافه‌کاری و شب‌کاری (ADR-011) | ✅ |
| `eydi.py` | عیدی (حداقل ۲ ماه، حداکثر ۳ ماه) | ✅ |
| `ctc.py` | هزینه کارفرما (CTC) | ✅ |
| `severance.py` | سنوات خدمت | ✅ |
| `termination.py` | ماده ۱۱ فسخ قرارداد | ✅ |
| `valuation.py` | ارزیابی جبران خدمات (ADR-009) | ✅ |
| `work_schedule.py` | برنامه کاری | ✅ |
| `perf_v1.py` | Performance scoring | ✅ |

---

## ۳. تخمین حقوق بازار (domain/salary_estimation/) — یافته‌های بحرانی

### FIND-BE-01: استفاده از float در مسیر مالی
- **شدت:** بحرانی
- **فایل:** `backend/app/domain/salary_estimation/salary_estimator.py`
- **خطوط:** ۸۲-۸۶
```python
experience_multiplier: float = 1.0
skills_premium: float = 1.0
education_bonus: float = 1.0
city_cost_factor: float = 1.0
employment_type_factor: float = 1.0
```
- **نقض:** AGENTS.md §2 Financial invariant 7: «Decimal only: no float literal in `backend/app/engines/**`»
- **توجه:** این ماژول در `domain/` است نه `engines/`، ولی نتیجه محاسبه مبلغ مالی است و روح invariant نقض شده
- **اقدام:** تبدیل تمام multipliers به `Decimal`

### FIND-BE-02: داده‌های Mock بدون هیچ مسیر واقعی
- **شدت:** بحرانی
- **فایل:** `salary_estimator.py` خط ۳۰-۷۰, `mock_data.py` خط ۲۲-۷۱
- **مسئله:** `MOCK_MARKET_DATA` hardcoded — فقط ۳ شهر (tehran, saveh, isfahan)، فقط ۵ نقش شغلی
- **تأثیر:** محصول برای هیچ ورودی واقعی دیگری پاسخ معنادار نمی‌دهد
- **اقدام:** باید جدول `market_salary_data` با داده واقعی پر شود

### FIND-BE-03: حداقل دستمزد قانونی hardcoded
- **شدت:** متوسط
- **فایل:** `salary_estimator.py` خط ۲۸۸-۲۸۹
```python
return 36000000  # hardcoded "approximate"
```
- **مسئله:** عدد approximate بدون مرجع قانونی، بدون ورود سال
- **اقدام:** اتصال به rule-set loader موجود (1404 verified) یا حذف

### FIND-BE-04: مدل‌های estimation بدون migration
- **شدت:** بالا
- **فایل:** `backend/app/models/estimation.py`
- **مسئله:** ۴ جدول تعریف شده (`candidate_estimates`, `market_salary_data`, `resume_uploads`, `estimation_users`) ولی هیچ migration در `alembic/versions/` وجود ندارد
- **تأثیر:** جداول هرگز ایجاد نمی‌شوند؛ هیچ persistence واقعی وجود ندارد

### FIND-BE-05: estimation endpoint بدون authentication
- **شدت:** بالا
- **فایل:** `backend/app/api/v1/estimation/__init__.py` خط ۴۶
- **مسئله:** `salary_estimation()` هیچ dependency بر `ManagerRequired` ندارد — هر کسی می‌تواند estimate بگیرد
- **تأثیر:** اگر deploy شود، API عمومی و بدون محدودیت است

---

## ۴. API Endpoints — وضعیت واقعی

| Endpoint | نوع | Auth | DB نیاز | کار می‌کند؟ |
|:---|:--:|:--:|:--:|:--:|
| `GET /health/live` | Health | ❌ | ❌ | ✅ |
| `POST /api/v1/simulations/gross-to-net` | Payroll | ❌ | ❌ | ✅ (pure function) |
| `POST /api/v1/simulations/salary-estimation` | Estimation | ❌ | ❌ | ⚠️ (mock data) |
| `POST /api/v1/auth/login` | Auth | ❌ | ✅ | ❌ (نیاز به DB) |
| `GET /api/v1/auth/me` | Auth | ✅ | ✅ | ❌ (نیاز به DB) |
| `POST /api/v1/auth/logout` | Auth | ✅ | ✅ | ❌ (نیاز به DB) |
| `POST /api/v1/valuation/score` | Valuation | ❌ | ❌ | ✅ (pure function) |
| `POST /api/v1/manager/proposals` | Manager | ✅ | ✅ | ❌ (نیاز به DB) |
| `POST /api/v1/work-profiles` | WorkProfile | ✅ | ✅ | ❌ (نیاز به DB) |

**نتیجه:** فقط ۳ endpoint از ۹ مورد بدون PostgreSQL کار می‌کنند.

---

## ۵. Services — ارزیابی

| سرویس | عملکرد | وضعیت |
|:---|:---|:--:|
| `payroll_service.py` | Gross-to-net orchestration | ✅ خوب |
| `estimation/service.py` | Salary estimation bridge | ⚠️ Mock data |
| `identity_service.py` | Auth (Argon2id, session) | ✅ خوب (نیاز به DB) |
| `valuation_service.py` | Compensation advisory | ✅ خوب |
| `audit_service.py` | Audit hash chain | ✅ خوب (نیاز به DB) |
| `manager_service.py` | Manager workspace | ✅ خوب (نیاز به DB) |
| `work_profile.py` | Work profile CRUD | ✅ خوب (نیاز به DB) |

---

## ۶. تست‌ها — خلاصه

| پوشه | تعداد فایل | موضوع |
|:---|:--:|:---|
| `tests/unit/` | ۲۵ | Money, engines, security, config, logging |
| `tests/api/` | ۵ | Health, payroll simulation, OpenAPI contract |
| `tests/property/` | ۱ | Engine properties (Hypothesis) |
| `tests/integration/` | ۴ | Statutory migrations, fail-closed, backup (skip without DB) |
| `tests/domain/` | ۱ | Money validation for estimation |
| `tests/e2e/` | ۱ | Salary estimation API |

**مشاهده مهم:** تست‌های integration بدون PostgreSQL container اجرا نمی‌شوند (self-skip). تست‌های unit engines جامع هستند ولی تست‌های salary estimation حداقلی‌اند.

---

## ۷. وابستگی‌ها — نکات

- **numpy و scipy** در dependencies هستند ولی در هیچ کد فعلی استفاده نمی‌شوند (برای "statistical engine M5" رزرو شده)
- **boto3** برای object storage — در salary estimation scope مورد نیاز نیست
- **Phase 2 optional deps** (PaddleOCR, pyHanko, pikepdf, OpenCV) — out of scope

---

## ۸. Configuration (`config.py`) — مثبت

- Fail-closed validators
- SecretStr برای اطلاعات حساس
- Production policy enforcement
- 1405 activation guard
- خوب طراحی شده و robust

---

## ۹. پیوست بازبینی مستقل (ادامهٔ حسابرسی — ۲۸ آبان ۱۴۰۵)

این بخش در ادامهٔ حسابرسی و پس از اجرای واقعی endpointها و ابزارهای کیفیت اضافه شده است. یافته‌های بخش‌های ۱–۸ بازنویسی نشده‌اند. هر یافتهٔ این پیوست با اجرای واقعی کد تأیید شده است مگر آنکه صریحاً «فرضیه» علامت خورده باشد.

**روش:** فراخوانی مستقیم `compute_estimate` و `TestClient` روی `create_app(Settings(_env_file=None))`، با payloadهایی که دقیقاً معادل ورودی رابط کاربری هستند.

### BE-06 — endpoint تخمین برای ورودی واقعی UI همیشه ۴۲۲ می‌دهد
- **شدت:** بحرانی
- **شرح:** `EstimateRequest.education` اختیاری است (`str | None = None`) و فرم UI هیچ فیلد تحصیلات ندارد؛ اما `map_request_to_domain` مقدار `request.education or ""` را می‌فرستد و `EstimationInput.education` در دامنه `min_length=1` اجباری است. نتیجه: هر درخواست بدون تحصیلات با `ValidationError` رد می‌شود.
- **شواهد (اجرا):**
  ```
  {"job_title":"توسعه‌دهنده وب","experience_years":5,"seniority_level":"mid",
   "employment_type":"full_time","city":"tehran","currency_unit":"toman"}
  → 422 ESTIMATION_INPUT_INVALID
    "1 validation error for EstimationInput / education / String should have at least 1 character"
  ```
  همان درخواست با `education="Bachelor"` → ۲۰۰.
- **مسیر و خط:** `backend/app/schemas/estimation.py:58`؛ `backend/app/domain/salary_estimation/schemas.py:31`؛ `backend/app/services/estimation/service.py:63`
- **تأثیر:** تنها مسیر end-to-end محصول جدید کار نمی‌کند. این یافته در حسابرسی قبلی دیده نشده بود و تست e2e آن را پنهان می‌کرد (TEST-08).
- **اقدام:** یکسان‌سازی اجباری‌بودن تحصیلات در هر دو schema؛ یا افزودن فیلد به UI. تست e2e باید بدنهٔ واقعی فرم را ارسال کند.

### BE-07 — اعتبارسنجی دامنه بی‌اثر است (Pydantic v1 API در محیط v2)
- **شدت:** بالا
- **شرح:** سه validator با الگوی `@classmethod` + `@validator` نوشته شده‌اند که در Pydantic 2.14 اجرا نمی‌شوند. نتیجه: `city`، `employment_type` و `seniority_level` هیچ اعتبارسنجی‌ای ندارند.
- **شواهد (اجرا):**
  ```
  EstimationInput(job_title='X', experience_years=3, education='Bachelor',
                  city='Berlin', employment_type='nonsense', seniority_level='Overlord')
  → ACCEPTED INVALID INPUT: Berlin nonsense Overlord
  ```
- **مسیر و خط:** `backend/app/domain/salary_estimation/schemas.py:37-60` و `:102-124`
- **تأثیر:** کنترل ورودی که وجودش ادعا شده، وجود ندارد؛ هم‌زمان schema مرز API (`EstimateRequest`) شهر را آزاد می‌پذیرد، پس ورودی نامحدود به منطق کسب‌وکار می‌رسد.
- **اقدام:** `field_validator` / `Literal` در Pydantic v2؛ حذف schema میانی تکراری.

### BE-08 — تمایز نقش شغلی از بین رفته است
- **شدت:** بالا
- **شرح:** `_find_fuzzy_match` بر اساس کلمات عنوان تطبیق می‌دهد و «developer» در همهٔ کلیدها مشترک است، پس اولین پروفایل شهر برگردانده می‌شود. تطبیق قطعی هم به‌دلیل ساخت نادرست `_process_job_title` (تولید کلیدی مثل `senior_senior react`) هرگز موفق نمی‌شود.
- **شواهد (اجرا، تهران، ۵ سال، mid):**
  ```
  senior_react_developer     → 30,000,000
  senior_backend_developer   → 30,000,000
  senior_fullstack_developer → 30,000,000
  ```
- **مسیر و خط:** `backend/app/domain/salary_estimation/matcher.py:139-180`
- **تأثیر:** محصول نمی‌تواند نقش‌ها را تفکیک کند؛ عدد خروجی مستقل از عنوان شغل است.
- **اقدام:** کلید نرمال‌شدهٔ صریح + امتناع در نبود تطبیق؛ تست تفکیک نقش.

### BE-09 — ضریب هزینهٔ شهر هرگز اعمال نمی‌شود
- **شدت:** بالا
- **شرح:** مقایسه با `["Tehran", "Isfahan"]` حساس به حروف است، در حالی که UI و API نام شهر را کوچک می‌فرستند.
- **شواهد (اجرا):** ورودی `tehran` → ۳۰٬۰۰۰٬۰۰۰؛ ورودی `Tehran` (همان شرایط) → ۴۵٬۰۰۰٬۰۰۰.
- **مسیر و خط:** `backend/app/domain/salary_estimation/salary_estimator.py:247-250`
- **تأثیر:** یکی از عوامل مصوب D-06 در مسیر واقعی حذف شده است.
- **اقدام:** نرمال‌سازی موردی ورودی در یک نقطه.

### BE-10 — «داده ناکافی» به‌جای امتناع، سه عدد صفر برمی‌گرداند
- **شدت:** بالا
- **شرح:** اگر پروفایلی پیدا نشود، دامنه `EstimationResult(primary=0, min=0, max=0, confidence="insufficient_data")` می‌سازد و سرویس آن را با HTTP 200 برمی‌گرداند. UI همان صفر را به‌عنوان رقم نمایش می‌دهد.
- **شواهد (اجرا):** برای شش شهر از هشت شهر فرم (اصفهان، شیراز، مشهد، اهواز، تبریز، کرج) پاسخ `200` با `primary_estimate_rial=0`.
- **مسیر و خط:** `backend/app/domain/salary_estimation/salary_estimator.py:137-155`؛ `backend/app/services/estimation/service.py:106-120`
- **تأثیر:** نقض ADR-013 D-06 («no numeric estimate»)، FR-07 و `SALARY_ESTIMATION_SPEC.md §3`. همچنین `_error_response` که برای همین حالت نوشته شده، هرگز فراخوانی نمی‌شود.
- **اقدام:** قرارداد امتناع بدون فیلد عددی (ARCH-03).

### BE-11 — provenance ساختگی روی هر پاسخ
- **شدت:** بحرانی
- **شرح:** فیلدهایی که باید از داده و rule set واقعی بیایند، رشتهٔ ثابت‌اند: `data_sources=["Jobinja","JobVision","Salary Survey"]`، `rule_version="v1.0"`، `rule_set_status="ACTIVE"`، `engine_version="0.1.0"`، `estimation_version="v1.0"`؛ همچنین `market_data_used=bool(data_sources)` که چون `data_sources` ثابت و ناتهی است، همیشه `True` است. در `service.py:85` همان `ACTIVE` دوباره تثبیت می‌شود.
- **مسیر و خط:** `salary_estimator.py:176, 190-194, 199-202`؛ `service.py:83-85, 100`
- **تأثیر:** نقض invariant ۹ (AGENTS.md §2.9) و FR-13. کاربر «ACTIVE» را به‌معنای قانون تأییدشده می‌خواند، در حالی که هیچ rule set تخمینی وجود ندارد. نام سه منبع واقعی بدون استفاده از آن‌ها، ادعای منبع کاذب است.
- **اقدام:** ساخت provenance از دادهٔ واقعی؛ حذف فیلد تا وجود واقعی rule set.

### BE-12 — سطح اطمینان از دادهٔ ساختگی محاسبه می‌شود
- **شدت:** بالا
- **شرح:** `calculate_confidence` امتیاز را از `data_volume` و `recency_days` می‌سازد که هر دو دستی در دیکشنری mock نوشته شده‌اند؛ نتیجه برای تهران همیشه `high` است.
- **مسیر و خط:** `matcher.py:194-244`؛ `salary_estimator.py:30-70`
- **تأثیر:** «اطمینان بالا» به کاربر، اطمینان کاذب می‌دهد.
- **اقدام:** تا دادهٔ واقعی، مقدار ثابت `insufficient_data`.

### BE-13 — اعتبارسنجی بازه محاسبه و سپس دور ریخته می‌شود
- **شدت:** متوسط
- **شرح:** `compute_estimate` نتیجهٔ `validate_range_consistency` را در `money_report` می‌گذارد و به تابع نگاشت می‌دهد که آن را با نام `_money_report` نادیده می‌گیرد. خود تابع نیز (برخلاف داک‌استرینگ) ترتیب `min ≤ primary ≤ max` را نمی‌سنجد و فقط باقیماندهٔ گرد کردن را بررسی می‌کند.
- **مسیر و خط:** `service.py:115-120`؛ `money_validation.py:69-87`
- **تأثیر:** کنترل مالی نمایشی است؛ تست مربوطه هم چیزی را assert نمی‌کند (TEST-09).
- **اقدام:** بررسی واقعی ترتیب + شکست صریح در نقض.

### BE-14 — ضرب float و بریدن با `int()` در محاسبهٔ بازه
- **شدت:** بالا
- **شرح:** `min_rial = int(base_salary * (1 - variance))` و `max_rial = int(base_salary * (1 + variance))` با `variance` از جنس float؛ `int()` به‌جای گرد کردن نیم‌بالا، به سمت صفر می‌برد.
- **شواهد (اجرا):** برای برآورد ۴۵٬۰۰۰٬۰۰۰، سقف `51,749,999` ریال برگشت — اثر دقیق بریدن (۱ ریال کم).
- **مسیر و خط:** `salary_estimator.py:261-282`
- **تأثیر:** نقض AGENTS.md §2.7/§2.8 (Decimal-only، ROUND_HALF_UP، بدون اثر ۱ ریالی) در مسیر مبلغ.
- **اقدام:** Decimal با `ROUND_HALF_UP` و quantum ریال (ARCH-01).

### BE-15 — متن فارسی خراب در پاسخ API
- **شدت:** بالا
- **شرح:** `advisory_notes` شامل «برآوزۀ»، «نمونۀ شبكاسازی» (ک عربی) و در خط ۸۱ **حروف کره‌ای**: «برآوزه 벆뿠انه است و تعهد پولی نیست».
- **مسیر و خط:** `backend/app/services/estimation/service.py:78-82`
- **تأثیر:** نقض AGENTS.md §10؛ متن با نویسهٔ غیرفارسی در پاسخ رسمی API به کاربر می‌رسد.
- **اقدام:** بازنویسی رشته‌ها + گیت نویسه در CI (ARCH-09).

### BE-16 — دو ماژول مرده و سه مجموعهٔ دادهٔ موازی
- **شدت:** متوسط
- **شرح:** `adjuster.py` در هیچ‌جا import نمی‌شود و import داخلی آن مسیر غلط `backend.app.engines.money` دارد (در mypy خطا می‌دهد)؛ `mock_data.py` هیچ ارجاعی ندارد. هم‌زمان سه دیکشنری مستقل وجود دارد: `MOCK_MARKET_DATA` (salary_estimator)، `EXTENDED_MOCK_MARKET_DATA` (matcher)، `MOCK_MARKET_ROWS` (service) که با هم هم‌خوان نیستند.
- **مسیر و خط:** `adjuster.py:9`؛ `mock_data.py`؛ `service.py:33-54`
- **تأثیر:** حجم کد فعال را بزرگ‌تر نشان می‌دهد، منبع حقیقت داده مشخص نیست و مسیر import شکسته در سکوت می‌ماند.
- **اقدام:** حذف/ادغام (ARCH-12).

### BE-17 — جامع‌ترین `except` متن خطای داخلی را به کاربر می‌فرستد
- **شدت:** پایین
- **شرح:** `except Exception as exc: return _error_response(422, "ESTIMATION_ENGINE_ERROR", str(exc))` متن خام استثنا را در پاسخ می‌گذارد؛ در مقابل، handler سراسری `RequestValidationError` در `main.py:135-159` عمداً مقادیر را پنهان می‌کند. همچنین importهای بی‌استفاده (`UTC`, `datetime`, `Any`) در همان فایل باقی مانده‌اند.
- **مسیر و خط:** `backend/app/api/v1/estimation/__init__.py:15, 61-62`
- **تأثیر:** نشت اطلاعات پیاده‌سازی و ناسازگاری با قرارداد خطای واحد.
- **اقدام:** کد خطای ثابت + لاگ داخلی؛ حذف importهای بی‌استفاده.

### ارزیابی نهایی بک‌اند (بازبینی‌شده)
بخش موتور حقوق (بخش ۲) همچنان ارزیابی مثبت دارد و در این بازبینی نقض float/round در `engines/**` یافت نشد. اما بخش تخمین **از «scaffold» فراتر نمی‌رود**: نه ورودی معتبر می‌پذیرد، نه نقش را تفکیک می‌کند، نه در حالت نبود داده امتناع می‌کند و نه provenance صادق دارد. بنابراین ارزیابی «⭐⭐» در بخش ۱ این گزارش با شواهد جدید سازگار نیست؛ ارزیابی واقعی: **«نمونهٔ اولیهٔ ناتمام و غیرقابل استفاده»**.
