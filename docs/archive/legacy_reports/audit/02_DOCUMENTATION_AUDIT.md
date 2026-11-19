# حسابرسی مستندات

**تاریخ:** ۲۸ آبان ۱۴۰۵  
**شناسه:** AUDIT-02

---

## ۱. حجم و پیچیدگی مستندات

پروژه شامل **۴۰+ سند Markdown** و **۳ فایل DOCX** است. این حجم برای یک محصول که هنوز MVP هم نرسیده، **بسیار غیرعادی** است و خود یکی از مشکلات اصلی پروژه است.

| دسته | تعداد | نمونه |
|:---|:--:|:---|
| ADR | ۱۳ | ADR-001 تا ADR-013 |
| Specification | ۸ | AUTH, DEPLOYMENT, TESTING, etc. |
| Product vision/scope (new) | ۱۲ | PRODUCT_VISION, FUNCTIONAL_REQUIREMENTS, etc. |
| Planning/execution | ۸ | EXECUTION_PLAN, WBS, ROADMAP, etc. |
| Status/state | ۵ | PROJECT_STATUS, PROJECT_STATE, CURRENT_STATE, etc. |
| Audit/reports | ۸ | DOCUMENTATION_AUDIT, agent-reports, etc. |
| Historical/research | ۶ | RESEARCH_GAP_ANALYSIS, DOCX files, etc. |
| Agent/skill contracts | ۱۱ | .agents/skills/*/SKILL.md |
| Root-level documents | ۸ | AGENTS.md, README.md, etc. |

---

## ۲. تناقضات بحرانی

### FIND-DOC-01: تعارض محصول بین AGENTS.md و README.md
- **شدت:** بحرانی
- **AGENTS.md §1:** «محصول موتور محاسبات حقوق قانونی (ADR-008) است»
- **README.md خط ۳:** «Smart salary estimation platform for the Iranian labor market»
- **ADR-013:** «Product boundary is now the resume analysis and monthly salary estimation tool»
- **تأثیر:** هر agent یا توسعه‌دهنده‌ای که AGENTS.md را بخواند، محصول اشتباه را پیاده‌سازی می‌کند
- **اقدام:** AGENTS.md باید برای انعکاس ADR-013 به‌روز شود

### FIND-DOC-02: OPEN_DECISIONS.md با ADR-013 تناقض دارد
- **شدت:** بالا
- **OPEN_DECISIONS.md:** D-01 (market data)، D-02 (auth)، D-06 (algorithm) هنوز `OPEN — BLOCKING`
- **ADR-013:** همان تصمیمات را resolved اعلام کرده (D-01 تا D-07)
- **تأثیر:** مشخص نیست آیا تصمیمات واقعاً گرفته شده‌اند یا نه
- **اقدام:** OPEN_DECISIONS.md باید به‌روز شود یا حذف شود

### FIND-DOC-03: سه سند وضعیت متناقض
- **شدت:** بالا
- **PROJECT_STATE.md:** «statutory payroll engine is implemented... Persian RTL simulation screen consumes it»
- **docs/PROJECT_STATUS.md:** از WBS حقوق قانونی صحبت می‌کند
- **docs/CURRENT_STATE.md:** سند سومی با وضعیت متفاوت
- **تأثیر:** هیچ‌کس نمی‌داند وضعیت واقعی پروژه چیست
- **اقدام:** باید یک سند واحد وضعیت وجود داشته باشد

### FIND-DOC-04: ADR-008 و ADR-013 عملاً متناقض هستند
- **شدت:** بالا
- **ADR-008:** «Product scope: statutory payroll calculation engine» — Status: Accepted
- **ADR-013:** «Product boundary is now the resume analysis and monthly salary estimation tool» — Status: Accepted
- **ADR-013 ادعا می‌کند ADR-008 را "partially supersede" کرده ولی ADR-008 هنوز Accepted است**
- **تأثیر:** دو ADR accepted با product scope متناقض
- **اقدام:** ADR-008 باید صریحاً status خود را به «Partially Superseded» تغییر دهد

---

## ۳. مستندات بدون پیاده‌سازی

| سند | وضعیت پیاده‌سازی |
|:---|:---|
| `FUNCTIONAL_REQUIREMENTS.md` (FR-01…FR-13) | ❌ فقط FR-01 (ورود اطلاعات) به صورت partial scaffold شده |
| `USER_WORKFLOWS.md` | ❌ فقط workflow ورود ابتدایی |
| `SALARY_ESTIMATION_SPEC.md` | ⚠️ الگوریتم ناقص با mock data |
| `LABOR_MARKET_DATA_SPEC.md` | ❌ هیچ پیاده‌سازی واقعی |
| `AI_ANALYSIS_SPEC.md` | ❌ هیچ پیاده‌سازی |
| `DATA_MODEL_SPEC.md` | ⚠️ مدل‌ها تعریف شده ولی migration ندارند |
| `SECURITY_AND_PRIVACY.md` | ⚠️ ساده‌شده ولی salary estimation بدون auth |
| `IMPLEMENTATION_ROADMAP.md` | ❌ هنوز WBS تعریف نشده |
| `docs/specs/AUTH.md` | ⚠️ پیاده‌سازی auth موجود ولی برای payroll-era |
| `docs/specs/DEPLOYMENT.md` | ❌ هیچ deployment evidence |

---

## ۴. پیاده‌سازی بدون مستندات

| پیاده‌سازی | سند متناظر |
|:---|:---|
| `SalaryDiscoveryPage.tsx` | ❌ هیچ سندی این صفحه را تعریف نکرده |
| `salary-benchmarks.ts` | ❌ benchmark data بدون مشخصات |
| `BLACK_VECTOR_PHASE0_PLAN.md` | ❌ طرحی خارج از WBS رسمی |
| `create_first_user.py` | ❌ اسکریپت بدون مستندات |
| `debug_api.py` | ❌ ابزار debug بدون مستندات |

---

## ۵. ADRها — وضعیت واقعی

| ADR | Status رسمی | وضعیت واقعی |
|:---|:---|:---|
| ADR-001 (React/Vite SPA) | Accepted | ✅ هنوز معتبر |
| ADR-002 (Object Storage WORM) | Accepted | ⚠️ تقریباً irrelevant برای salary estimation |
| ADR-003 (AES-256-GCM + Blind Index) | Accepted | ⚠️ ADR-013 آن را simplified اعلام کرده |
| ADR-004 (Pre-hire Scope) | Accepted (superseded) | 🔴 مرده — superseded by ADR-008 |
| ADR-005 (Async Strategy) | Proposed | ⚠️ هنوز proposed، irrelevant برای scope جدید |
| ADR-006 (Security & Schema) | Accepted | ⚠️ چهار تصمیم Phase 0 — بخشی irrelevant |
| ADR-007 (Statutory Global Access) | Accepted | ⚠️ مربوط به payroll، نه salary estimation |
| ADR-008 (Payroll Engine Scope) | Accepted | 🔴 Product scope superseded by ADR-013 |
| ADR-009 (Compensation Advisory) | Accepted | 🔴 Out of scope per ADR-013 |
| ADR-010 (Manager MVP) | Accepted | 🔴 Product direction superseded by ADR-013 |
| ADR-011 (Night Work) | Accepted | ⚠️ مربوط به payroll engine |
| ADR-012 (Persisted Work Profile) | — | ⚠️ وجود فیزیکی دارد ولی status نامشخص |
| ADR-013 (Salary Estimation) | Accepted | ✅ تصمیم جاری محصول |

**نتیجه:** از ۱۳ ADR، فقط ۲ مورد (ADR-001 و ADR-013) به طور کامل برای محصول فعلی معتبر هستند.

---

## ۶. تصمیمات حل‌نشده

| تصمیم | وضعیت | تأثیر |
|:---|:---|:---|
| D-01: منبع داده بازار | BLOCKING (ADR-013 resolve کرده ولی OPEN_DECISIONS هنوز open) | بدون داده واقعی، محصول کار نمی‌کند |
| D-02: Authentication | BLOCKING | بدون تصمیم، endpoint بدون حفاظت است |
| D-06: الگوریتم تخمین | BLOCKING | الگوریتم فعلی mock است |
| ADR-005: Async strategy | Proposed | تا salary estimation به queue نیاز ندارد، irrelevant |
| DEC-006: PDF generation | Open | به v2 موکول شده |

---

## ۷. توصیه‌ها

1. **حذف یا archive مستندات مرده:** حداقل ۱۵ سند دیگر معتبر نیستند
2. **یکپارچه‌سازی وضعیت:** فقط یک سند وضعیت (PROJECT_STATE.md)
3. **به‌روزرسانی AGENTS.md:** انعکاس محصول جدید (ADR-013)
4. **تعیین تکلیف ADRها:** Superseded/Deprecated ADRها باید صریحاً علامت‌گذاری شوند
5. **حل OPEN_DECISIONS:** همسو‌سازی با ADR-013

---

## ۸. پیوست بازبینی مستقل (ادامهٔ حسابرسی — ۲۸ آبان ۱۴۰۵)

### ۸.۱ تصحیح یافتهٔ FIND-DOC-04 — **نادرست در متن فعلی**
- **ادعای قبلی:** «ADR-008 هنوز Accepted است و هیچ نشانه‌ای از supersession ندارد؛ ADR-013 ادعا می‌کند partially supersede کرده ولی ADR-008 تغییر نکرده.»
- **واقعیت working tree:** `docs/adr/ADR-008-...md:10` صریحاً می‌نویسد:
  «**Partially superseded (2026-11-17):** the product-boundary clause ... is superseded **for the resume analysis and salary estimation tool** by [ADR-013] ...»
  و `docs/ADR_INDEX.md:23,25,33` همین را ثبت کرده است. ADR-010 نیز در خط وضعیت خود supersession جزئی توسط ADR-013 را ثبت کرده است.
- **حکم:** ❌ ادعای FIND-DOC-04 با شواهد فایل ناسازگار است. **تصحیح:** ADR-008 و ADR-010 supersession را ثبت کرده‌اند؛ مشکل باقی‌مانده این است که **AGENTS.md** (سند دارای اقتدار عملیاتی) به‌روز نشده است — که همان FIND-DOC-01 است و معتبر می‌ماند.
- **درس روش‌شناختی:** این خطا نشان می‌دهد گزارش قبلی حداقل در یک مورد بدون خواندن نسخهٔ working tree قضاوت کرده است.

### ۸.۲ تصحیح ادعای «IMPLEMENTATION_ROADMAP بدون WBS»
- **ادعای قبلی (بخش ۳):** «`IMPLEMENTATION_ROADMAP.md` — ❌ هنوز WBS تعریف نشده».
- **واقعیت:** این سند ۱۲ task با شناسهٔ T-01..T-12، وابستگی، تلاش و دروازهٔ فاز تعریف کرده است (خطوط ۱۶–۳۱). وضعیت سند `Draft — pending owner approval` است و ستون وضعیت اجرا ندارد.
- **حکم:** ❌ ادعا نادرست؛ **تصحیح:** WBS وجود دارد اما تصویب‌نشده و بدون ردیابی وضعیت است (نک. DEC-08).

### ۸.۳ تصحیح شمارش اسناد
| سنجه | ادعای قبلی | شمارش واقعی |
|:---|:--:|:--:|
| اسناد Markdown | «۴۰+» | ۶۱ فایل در `docs/` (بازگشتی) + ۱۱ در ریشه = ۷۲ |
| اسناد سطح اول `docs/` | — | ۳۴ |
| ADR | ۱۳ | ۱۳ ✅ |
| فایل تست بک‌اند | «~۳۵» | ۴۱ فایل `.py` |

### ۸.۴ یافته‌های جدید مستندات

#### DOC-05 — AGENTS.md هنوز محصول قدیم را تعریف می‌کند (تأیید FIND-DOC-01)
- **شدت:** بحرانی
- **شاهد:** `AGENTS.md §1`: «The product is the **statutory payroll calculation engine** (ADR-008, accepted 2026-11-15)» در برابر ADR-013 (Accepted) و `README.md:3` («Smart salary estimation platform»). تاریخ آخرین تغییر AGENTS.md: 2026-11-17 20:42.
- **تأثیر:** هر agent/توسعه‌دهنده‌ای که طبق AGENTS.md کار کند، محصول اشتباه را می‌سازد؛ همین گزارش‌های حسابرسی نیز تحت همان قاعده نوشته شده‌اند.
- **اقدام:** به‌روزرسانی §1 (و بخش‌های وابستهٔ §2، §14) یا ثبت ADR جایگزین؛ تصمیم مالک.

#### DOC-06 — دوازده سند محصولی جدید، «Active» ولی تصویب‌نشده
- **شدت:** بالا
- **شاهد:** `PRODUCT_VISION.md`, `PRODUCT_SCOPE.md`, `FUNCTIONAL_REQUIREMENTS.md`, `NON_FUNCTIONAL_REQUIREMENTS.md`, `USER_WORKFLOWS.md`, `DATA_MODEL_SPEC.md`, `SECURITY_AND_PRIVACY.md`, `LABOR_MARKET_DATA_SPEC.md`, `SALARY_ESTIMATION_SPEC.md`, `AI_ANALYSIS_SPEC.md`, `IMPLEMENTATION_ROADMAP.md` (Draft), `OPEN_DECISIONS.md` (Active) — همه untracked.
- **تأثیر:** این اسناد در عمل «مشخصات» شده‌اند و کد بر اساس آن‌ها نوشته شده، بدون آنکه هیچ‌کدام تصویب یا در فهرست اسناد رسمی ثبت شده باشند. `docs/DOCUMENTATION_INDEX.md` هم آن‌ها را فهرست نکرده است (بررسی‌شده).
- **اقدام:** ثبت در `DOCUMENTATION_INDEX.md` و اعلام وضعیت (Draft/Approved) توسط مالک.

#### DOC-07 — سند وضعیت پروژه کهنه است و ادعای کیفیتِ نادرست دارد
- **شدت:** بالا
- **شاهد:** `docs/PROJECT_STATUS.md` تاریخ 2026-11-16 دارد و می‌گوید «765 backend PASS و 123 frontend tests PASS ... frontend typecheck/build PASS». اجرای واقعی امروز: ۷۶۱ PASS + ۴۹ skip + ۲۵ error؛ ۱۲۴ PASS + ۴ fail؛ tsc FAIL. همچنین می‌گوید «no authenticated workflow» ولی `api/v1/auth.py` و migrationهای identity موجودند — یعنی سند حتی نسبت به گذشته هم دقیق نیست.
- **تأثیر:** «سند حقیقت» پروژه، حقیقت را گزارش نمی‌کند؛ سه سند وضعیت (`PROJECT_STATE.md`, `docs/PROJECT_STATUS.md`, `docs/CURRENT_STATE.md`) با تاریخ‌های مختلف وجود دارند.
- **اقدام:** یک سند وضعیت، تولیدشده از اجرای واقعی ابزارها (نه از سند قبلی).

#### DOC-08 — اسناد حسابرسی موازی
- **شدت:** پایین
- **شاهد:** `docs/audit/DOCUMENTATION_AUDIT.md` (2026-11-17) و مجموعهٔ `audit/` (2026-11-18) هر دو دربارهٔ مستندات‌اند. اولی ماتریس طبقه‌بندی است، دومی گزارش داوری. هیچ‌کدام به دیگری ارجاع نمی‌دهد.
- **تأثیر:** دو منبع حقیقت برای همان موضوع.
- **اقدام:** ارجاع متقابل یا ادغام با تصمیم مالک.

### ۸.۵ جمع‌بندی بازبینی مستندات
- از چهار یافتهٔ اصلی گزارش قبلی: **DOC-01 معتبر و بحرانی**، **DOC-02 معتبر**، **DOC-03 معتبر**، **DOC-04 نادرست**.
- یافتهٔ «۱۳ ADR که ۵ مورد مرده‌اند» نیازمند تعدیل است: ADR-008/009/010 همگی supersession جزئی یا out-of-scope بودن را ثبت کرده‌اند؛ مشکل در **وضعیت حقوقی محصول** است، نه در نبود یادداشت supersession.
- مشکل اصلی مستندات، **حجم** نیست؛ **نبود یک منبع حقیقت مصوب** است: AGENTS.md، README، ADR-013 و OPEN_DECISIONS چهار روایت متفاوت از یک محصول می‌دهند.
