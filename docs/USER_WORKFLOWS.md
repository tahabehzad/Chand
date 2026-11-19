# User Workflows — Salary Estimation Tool

**Document ID:** `DOC-USER-WORKFLOWS-001`  
**Status:** Draft — pending owner approval  
**Date:** 17 Aban 1405 SH (2026-11-17)  
**Related:** `DOC-FUNC-REQ-001`, `DOC-PRODUCT-SCOPE.md`

---

## 1. Primary User

**One manager** — the only user type. Employees are subjects of estimation, not system users.

---

## 2. Main Workflow: Estimate a Salary

```
1. Manager opens the application.
   └─ Landing page shows: "تخمین حقوق بر اساس رزومه" + "شروع تخمین جدید" button.

2. Manager clicks "شروع تخمین جدید".
   └─ Multi-step Persian form begins.

3. Step 1 — اطلاعات شغلی (Job Information):
   - عنوان شغلی موردنظر (e.g., "فروشندۀ نرم‌افزار")
   - سطح شغلی (Junior / Mid-level / Senior)
   - نوع همکاری (Full-time / Part-time /契約ی / Freelance)
   - شهر و محل فعالیت (e.g., "تهران")

4. Step 2 — سابقه و تجربه (Experience):
   - تعداد سال تجربه حرفه‌ای
   - سوابق شغلی قبلی (عنوان، شرکت، مدت زمان)

5. Step 3 — مهارت‌ها و تحصیلات (Skills & Education):
   - مهارت‌ها و سطح هر مهارت (مبتدی / میان‌فला / پیشرفته)
   - رشته و سطح تحصیلی
   - دوره‌ها و مدارک تخصصی

6. Step 4 — رزومه (اختیاری):
   - آپلود فایل PDF یا متن رزومه برای استخراج خودکار اطلاعات (v2)

7. Manager clicks "تخمین حقوق".
   └─ System analyzes profile against Iranian labor market data.

8. Result page displays:
   - عدد تخمین اصلی (مثلاً ۲۵,۰۰۰,۰۰۰ تومان)
   - بازه حقوق (حداقل–حداکثر) (مثلاً ۲۰,۰۰۰,۰۰۰ – ۳۰,۰۰۰,۰۰۰ تومان)
   - دلایل تخمین (تجربه ۵ سال، مهارت React، شهر تهران، سطح Senior)
   - میزان اطمینان (بالاتا / متوسط / پایین / داده ناکافی)
   - منبع داده‌ها (جابینجا، جاب‌ویژن، گزارش حقوقی)
   - حداقل حقوق قانونی به عنوان مرجع جدا

9. Manager clicks "ذخیره".
   └─ Estimate saved to history.

10. Manager can view "تخمین‌های قبلی" to compare candidates.
```

---

## 3. Alternative Workflow: View Estimate History

```
1. Manager navigates to "تخمین‌های قبلی".
2. System lists saved estimates with: date, job title, city, primary estimate, confidence.
3. Manager clicks on an estimate to view its full details.
4. Manager can export to PDF (v2).
```

---

## 4. Edge Cases

| Situation | System Behavior |
|:---|:---|
| Insufficient market data for role/city | Shows "داده کافی برای این شغل در این شهر وجود ندارد" — no fabricated estimate |
| Resume upload fails (invalid PDF) | Shows error: "فایل رزومه قابل پردازش نیست" — falls back to manual form |
| Manager enters no experience | Uses market data for entry-level roles with lower confidence |
| Salary range too wide | Confidence level set to "میان" or "پایین" with explanation |

---

## 5. Screen Map (v1)

| Screen | Purpose |
|:---|:---|
| `/` (landing) | "شروع تخمین جدید" + kurze説明 |
| `/estimate/new` | Multi-step form (Steps 1–4) |
| `/estimate/result` | Result: range, primary, factors, confidence, sources |
| `/estimate/history` | List of saved estimates |
| `/estimate/history/[id]` | Detail view of one saved estimate |
| `/settings` (optional) | Display unit (rial/toman), preferences |

---

## 6. What Is NOT in the Workflow

- No employee onboarding
- No payslip generation
- No tax/insurance calculation
- No attendance tracking
- No multi-user permission management
- No statutory minimum wage enforcement (only reference display)
