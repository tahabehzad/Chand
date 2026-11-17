# گزارش Phase 4، Stage 4.3 — اصلاح مستندات تناقض‌دار (X-4 / C-4)

**تاریخ:** 2026-11-17  
**شاخه:** `autonomous/project-completion`  
**HEAD:** `74685e7608c3ed43c72bc520b76dee2d7e85746d`  
**وضعیت:** تکمیل‌شده

---

## ۱. هدف و حوزه

اصلاح سه فایل مستندات که همچنان به نسخه قدیمی `ENGINE_VERSION` (`0.2.0-payroll-engine`) یا تضاد حل‌نشده ارجاع می‌دادند، مطابق با:
- تسویه Stage 4.2 (نسخه قانونمند `0.3.0-payroll-engine` در `app/engines/__init__.py`)
- دستور ADR-010 directive 1 ("Reconcile the two ENGINE_VERSION constants...")
- کامنت بسته موتور: "Bumped only with a changelog entry"

**محدوده:** فقط اصلاح ارجاع‌های نسخه در مستندات؛ بدون تغییر کد، تست، یا منطق تجاری.

---

## ۲. فایل‌های اصلاح‌شده (۳)

| فایل | خط | تغییر |
|------|-----|--------|
| `docs/CURRENT_STATE.md` | ۶۳ | `0.2.0-payroll-engine` → `0.3.0-payroll-engine` با یادداشت "reconciled per ADR-010 directive 1" |
| `docs/PROJECT_BIBLE.md` | ۲۰۳ | `0.2.0-payroll-engine` → `0.3.0-payroll-engine` با یادداشت "reconciled per ADR-010 directive 1" |
| `docs/BOOTSTRAP_CHANGELOG.md` | ۱۸۱۳ | متن تضاد → "ENGINE_VERSION conflict resolved" با توضیح منبع واحد |
| `docs/BOOTSTRAP_CHANGELOG.md` | انتها | افزوده شدن بخش **۳۵. ENGINE_VERSION reconciliation (X-4)** — ورودی changelog کامل با پیش‌زمینه، حل، تأیید، نتایج تست، و تضادهای باقی‌مانده |

---

## ۳. جزئیات ورودی Changelog (بخش ۳۵)

**پیش‌زمینه:** کامیت `f31e01e` (۲۰۲۶-۱۱-۱۶) نسخه `0.3.0` را در `payroll_service.py` معرفی کرد اما بسته موتور در `0.2.0` ماند.

**حل:** نسخه قانونمند `0.3.0-payroll-engine` در `app/engines/__init__.py:80`؛ حذف تعریف تکراری در سرویس‌ها؛ import مستقیم از موتور.

**فایل‌های کد تغییر یافته (از Stage 4.2):**
1. `backend/app/engines/__init__.py:80`
2. `backend/app/services/payroll_service.py:79`
3. `backend/app/services/__init__.py:7`
4. `backend/tests/unit/test_payroll_service.py` (۲ تست رگرسیونی)

**مستندات به‌روزرسانی‌شده (این مرحله):**
- `CURRENT_STATE.md:63`، `PROJECT_BIBLE.md:203`، `BOOTSTRAP_CHANGELOG.md:1813`

**تأیید مصرف‌کنندگان:** تمام مسیرهای import و پاسخ‌های API هم‌اکنون `0.3.0-payroll-engine` برمی‌گردانند.

**نتایج تست:** ۴۸ تست واحد payroll (شامل ۲ جدید)، ۷۶۵ بک‌اند، ۱۲۳ فرانت‌اند — همه پاس.

**تضادهای باقی‌مانده (C-1…C-11):** جداگانه پیگیری می‌شوند؛ این ورودی فقط X-4 را پوشش می‌دهد.

---

## ۴. تأیید تست‌ها (پس از اصلاح مستندات)

| مجموعه | دستور | نتیجه |
|--------|--------|--------|
| سرویس payroll (unit) | `pytest tests/unit/test_payroll_service.py -q` | **۴۸ passed** |
| کل بک‌اند | `pytest -q` | **۷۶۵ passed، ۱ skipped** |
| لنیت بک‌اند | `ruff check .` | **All checks passed** |
| تایپ‌چک بک‌اند | `mypy --strict app tests` | **Success (۸۶ فایل)** |
| تست‌های فرانت‌اند | `npm test` | **۱۲۳ passed** |
| تایپ‌چک فرانت‌اند | `npm run typecheck` | **Clean** |
| لنیت فرانت‌اند | `npm run lint` | **۰ violation** |

---

## ۵. وضعیت نهایی Git

**تغییرکرده در این مرحله (مستندات):**
- `docs/CURRENT_STATE.md`
- `docs/PROJECT_BIBLE.md`
- `docs/BOOTSTRAP_CHANGELOG.md`

**تغییرات پیشین (Stage 4.2 کد + تست):**
- `backend/app/engines/__init__.py`
- `backend/app/services/__init__.py`
- `backend/app/services/payroll_service.py`
- `backend/tests/unit/test_payroll_service.py`

**سایر تغییرات مخزن (از پیش موجود، بدون تغییر):**
- ۱۵ فایل tracked دیگر، ۱ حذف‌شده، ۳۴ untracked
- دایرکتوری جدید `docs/agent-reports/` (untracked)

---

## ۶. محدودیت‌ها و موارد باقی‌مانده

| مورد | وضعیت |
|------|--------|
| **تضادهای مستندات C-1…C-11** (شمارش تسک‌ها، تعداد تست‌ها، ارجاع‌های قدیمی در `PROJECT_STATUS.md`، `EXECUTION_PLAN.md` و غیره) | **رفع نشده** — جداگانه در `CURRENT_STATE.md` §۴ لیست شده؛ نیاز به Stage 4.4 یا مجوز جداگانه |
| **ورود changelog برای ارتقای نسخه** | **انجام شده** — بخش ۳۵ اضافه شد |
| **کامیت/پوش Git** | **انجام نشده** — در انتظار دستور صریح مالک |
| **بازبینی مستقل غیرنویسنده** | **انجام نشده** — AGENTS.md §۶ الزامی برای READY_FOR_REVIEW → APPROVED |

---

## ۷. اقدام پیشنهادی بعدی

**Stage 4.4 (اختیاری) — اصلاح تضادهای C-1…C-11:** به‌روزرسانی `PROJECT_STATUS.md`، `EXECUTION_PLAN.md`، `ADR_INDEX.md` و سایر مستندات برای حذف ۱۱ تضاد شناسایی‌شده در Stage 4.1.

**یا اولویتدهی بر اساس ریسک Critical:** R1 (tenant isolation pentest)، R2 (sessionStorage token)، R3 (authorization boundaries) — مطابق `LATEST_REPORT.md`.

**نیاز به تأیید مالک:** بله — برای Stage 4.4 یا شروع کار روی ریسک‌های Critical.

---

**توقف — در انتظار دستور مالک برای مرحله بعد.**