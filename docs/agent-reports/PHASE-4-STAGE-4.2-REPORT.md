# گزارشPhase 4، Stage 4.2 — تسویه ENGINE_VERSION (X-4)

**تاریخ:** 2026-11-17  
**شاخه:** `autonomous/project-completion`  
**HEAD:** `74685e7608c3ed43c72bc520b76dee2d7e85746d`  
**وضعیت:** تکمیل‌شده — در انتظار تأیید مالک برای مستندسازی

---

## ۱. هدف و حوزه

حل تضاد `ENGINE_VERSION` (معرفی شده به عنوان X-4 در بازبینی Phase 4، Stage 4.1) با:
- برقراری یک منبع حقیقت واحد (Single Source of Truth)
- حذف تعریف‌های تکراری
- اطمینان از اینکه تمام مصرف‌کنندگان نسخه یکسان را برمی‌گردانند
- اضافه کردن تست‌های رگرسیونی
- **بدون** تغییر منطق محاسبه، معیارهای ارزیابی، یا سیاست‌های تجاری

محدوده: فقط فایل‌های مربوط به `ENGINE_VERSION` و تست‌های مستقیم آن.

---

## ۲. وضعیت اولیه مخزن

| مورد | مقدار |
|------|-------|
| شاخه | `autonomous/project-completion` |
| HEAD | `74685e7` (یک کامیت جلوتر از origin) |
| فایل‌های tracked تغییرکرده | ۱۹ |
| فایل tracked حذف‌شده | ۱ (`backend/debug_downgrade.py`) |
| فایل‌های untracked | ۳۴ |
| تغییرات staged | ۰ |

---

## ۳. تعریف‌ها و مصرف‌های موجود (پیش از اصلاح)

| فایل | خط | مقدار | نقش |
|------|-----|-------|------|
| `backend/app/engines/__init__.py` | ۸۰ | `0.2.0-payroll-engine` | **بسته موتور قانون‌مند** (کامنت: "Engine identity carried by every response; also re-exported from the composition service") |
| `backend/app/services/payroll_service.py` | ۷۹ | `0.3.0-payroll-engine` | **تعریف سایه** در سرویس ترکیب (اضافه شده در کامیت `f31e01e`) |
| `backend/app/services/__init__.py` | ۸ | صادرکننده از `payroll_service` | API عمومی لایه سرویس → `0.3.0` |
| `backend/app/services/manager_service.py` | ۶۲ | واردکننده از `app.services` | دریافت `0.3.0` |
| `backend/app/services/valuation_service.py` | ۴۴ | واردکننده از `payroll_service` | دریافت `0.3.0` |
| `backend/tests/unit/test_payroll_service.py` | ۲۹، ۷۸ | واردکننده از `app.services` | تست در برابر `0.3.0` |

**ریشه علت:** کامیت `f31e01e` ("fix(backend): close the payroll engine review findings and contract gaps") نسخه سرویس را به `0.3.0` ارتقا داد اما بسته موتور در `0.2.0` مانده بود. بسته موتور منبع قانون‌مند докуменتی است.

---

## ۴. مستندات برای انتخابنسخه رسمی `0.3.0-payroll-engine`

- کامیت `f31e01e` به طور دقیق نسخه سرویس را به `0.3.0` ارتقا داد همراه با اصلاح قرارداد بزرگ (فیلدهای provenance، رفع residual rounding، سناریو termination، بلوک statutory reference)
- کامنت بسته موتور: "Engine identity carried by every response; also re-exported from the composition service. Bumped only with a changelog entry."
- تمام مصرف‌کنندگان در runtime (پاسخ‌های API، توصیه‌های manager، پیشنهادهای valuation) قبلاً `0.3.0` بازمی‌گرداندند
- مجموعه تست در برابر `0.3.0` утверждng داشت

---

## ۵. جزئیات پیاده‌سازی

### فایل‌های تغییرکرده (۴)

| فایل | تغییر |
|------|--------|
| `backend/app/engines/__init__.py:80` | ارتقای نسخه قانونمند به `0.3.0-payroll-engine` |
| `backend/app/services/payroll_service.py:79` | حذف تعریف تکراری؛ اکنون `from app.engines import ENGINE_VERSION` |
| `backend/app/services/__init__.py:7` | وارد کردن مستقیم از `app.engines` (منبع واحد) |
| `backend/tests/unit/test_payroll_service.py` | اضافه شدن دو تست رگرسیونی |

### تست‌های رگرسیونی اضافه‌شده

```python
def test_engine_version_single_source_of_truth() -> None:
    """Engine and service layer must expose the same ENGINE_VERSION."""
    from app.engines import ENGINE_VERSION as ENGINE_ENGINE_VERSION
    from app.services import ENGINE_VERSION as SERVICE_ENGINE_VERSION
    from app.services.payroll_service import ENGINE_VERSION as PAYROLL_ENGINE_VERSION
    assert ENGINE_ENGINE_VERSION == SERVICE_ENGINE_VERSION == PAYROLL_ENGINE_VERSION
    assert ENGINE_ENGINE_VERSION == "0.3.0-payroll-engine"


def test_api_response_carries_canonical_engine_version() -> None:
    """The gross-to-net response must carry the canonical engine version."""
    from app.engines import ENGINE_VERSION as CANONICAL_VERSION
    calculation = compute_gross_to_net(PayrollInput(gross_monthly_rial=100_000_000))
    assert calculation.payload["engine_version"] == CANONICAL_VERSION
    assert calculation.payload["engine_version"] == "0.3.0-payroll-engine"
```

---

## ۶. نتایج اجرای تست

| مجموعه | دستور | نتیجه |
|--------|--------|--------|
| سرویس payroll (unit) | `pytest tests/unit/test_payroll_service.py -v` | **۴۸ passed** (شامل ۲ جدید) |
| کل بک‌اند | `pytest -q` | **۷۶۵ passed، ۱ skipped** |
| لنیت بک‌اند | `ruff check .` | **All checks passed** |
| تایپ‌چک بک‌اند | `mypy --strict app tests` | **Success (۸۶ فایل)** |
| تست‌های فرانت‌اند | `npm test` | **۱۲۳ passed** |
| تایپ‌چک فرانت‌اند | `npm run typecheck` | **Clean** |
| لنیت فرانت‌اند | `npm run lint` | **۰ violoation** |

---

## ۷. تأیید مصرف‌کنندگان

```python
# تمام مسیرهای import هم‌اکنون به یکسان resolve می‌شوند:
app.engines.ENGINE_VERSION                    → "0.3.0-payroll-engine"
app.services.ENGINE_VERSION                   → "0.3.0-payroll-engine"
app.services.payroll_service.ENGINE_VERSION   → "0.3.0-payroll-engine"
app.services.manager_service.ENGINE_VERSION   → "0.3.0-payroll-engine"
app.services.valuation_service.ENGINE_VERSION → "0.3.0-payroll-engine"

# پاسخ‌های API تأیید شده:
POST /api/v1/simulations/gross-to-net         → engine_version: "0.3.0-payroll-engine"
POST /api/v1/manager/employees/{id}/evaluations → engine_version: "0.3.0-payroll-engine"
POST /api/v1/valuations/compensation-proposal   → engine_version: "0.3.0-payroll-engine"
                                              → proposal_version: "valuation-v1+0.3.0-payroll-engine"
```

---

## ۸. وضعیت نهایی Git

**تغییرکرده در این مرحله:**
- `backend/app/engines/__init__.py`
- `backend/app/services/__init__.py`
- `backend/app/services/payroll_service.py`
- `backend/tests/unit/test_payroll_service.py`

**تغییرات از پیش موجود حفظ شده (بدون تغییر):**
- ۱۵ فایل tracked تغییرکرده دیگر، ۱ حذف‌شده، ۳۴ untracked

---

## ۹. محدودیت‌ها و ریسک‌های باقی‌مانده

| ریسک | وضعیت |
|------|--------|
| **ارزیابی‌های تاریخی** — رکوردهای `SalaryRecommendation` ذخیره‌شده قبل از اصلاح `engine_version: "0.3.0-payroll-engine"` حمل می‌کنند (در runtime درست بود) اما بسته موتور قبلاً `0.2.0` اعلام می‌کرد. اکنون همسو شده. | **حل شده** |
| **انحراف مستندات** — `docs/CURRENT_STATE.md:63`، `docs/PROJECT_BIBLE.md:203`، `docs/BOOTSTRAP_CHANGELOG.md:1400/1813` همچنان به مقدار قدیمی `0.2.0` یا تضاد ارجاع می‌دهند. | **رفع نشده** (خارج از حوزه Stage 4.2) |
| **ورود changelog** — طبق کامنت موتور ("Bumped only with a changelog entry")، یک ورودی BOOTSTRAP_CHANGELOG باید ارتقای نسخه را ثبت کند. | **انجام نشده** (نیاز به تأیید مالک برای تغییر مستندات) |

---

## ۱۰. تصمیم‌های مورد نیاز مالک

1. **تأیید اصلاح مستندات (Stage 4.3):** به‌روزرسانی `CURRENT_STATE.md`، `PROJECT_BIBLE.md`، `BOOTSTRAP_CHANGELOG.md` برای بازتاب `0.3.0-payroll-engine` قانونمند و حذف ارجاع‌های تضاد.
2. **ورود changelog:** ثبت ارتقای نسخه در `BOOTSTRAP_CHANGELOG.md` با تاریخ و استناد به ADR-010 directive 1.
3. **گزارش‌دهی:** ایجاد/به‌روزرسانی `docs/agent-reports/LATEST_REPORT.md` (تأیید شده در پیام قبلی).

---

## ۱۱. اقدام پیشنهادی بعدی

**Stage 4.3 — اصلاح مستندات:** با تأیید مالک، اصلاح ۳ فایل مستندات برای حذف تضاد و ثبت نسخه قانونمند واحد. سپس به کار اولویت بالاتر (مثلاً Stage 4.4 یا رفع ریسک Critical در ثباتtenant isolation) ادامه دهید.

---

**توقف — در انتظار تأیید صریح مالک برای هرگونه تغییر بیشتر.**