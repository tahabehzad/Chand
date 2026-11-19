# PRODUCT_WORKFLOW.md

Pish Hesabdari — Manager-to-Salary-Result Workflow

## Overview

Complete user journey for a company manager determining a monthly base salary for a new candidate.

## Step 1: Start a New Salary Assessment

**Entry point:** The application's main page (`/`).

**User action:** Manager navigates to the salary estimation page.

**UI:** A clear heading "برآورد حقوق بازار کار ایران" (Iran Market Salary Estimation) with a "برآورد حقوق را محاسبه کن" (Calculate Salary Estimate) call to action. An ADR-013 badge indicates specification version v1.0.

## Step 2: Enter Candidate Information

**Page:** `SalaryEstimationPage` → `SalaryEstimationForm`

**Form sections (Persian, RTL):**

### پروفایل داوطلب (Candidate Profile)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| عنوان شغل (Job title) | Text input | Yes | e.g. "توسعه‌دهنده نرم‌افزار" |
| سال‌های تجربه حرفه‌ای (Experience years) | Number input | Yes | 0–60, end-aligned LTR |
| سطح ارشدیت (Seniority level) | Select | Yes | جونیور / میان‌رده / ارشد |
| نوع استخدام (Employment type) | Select | Yes | تمام‌وقت / نیمه‌وقت / قراردادی / آزاد |
| شهر (City) | Select | Yes | تهران / اصفهان / شیراز / مشهد / اهواز / تبریز / ساوه / کرج |
| واحد پول (Currency unit) | Select | Yes | تومان / ریال |
| تحصیلات (Education) | Text input | Yes | e.g. "کارشناسی ارشد مهندسی کامپیوتر" |

### مهارت‌ها (Skills) — Optional

Badge-style selectable tags: React, TypeScript, Node.js, Python, AWS, Docker, Java, Go. Selected skills shown with `success` tone.

**Validation:**
- Job title: non-empty
- City: non-empty
- Education: non-empty
- Experience years: 0–60
- All errors shown inline in Persian beneath each field
- Submit disabled while errors exist or while submitting

## Step 3: Review Information

**Current implementation:** The form submits directly on validation pass. A separate review step (step 3 in the journey spec) is NOT yet implemented — this is a known gap. The manager reviews entered values in the form before clicking submit.

**Next stage:** Add a review/confirmation screen between form submission and calculation.

## Step 4: Calculate Salary

**API:** `POST /api/v1/simulations/salary-estimation`

**Request body:**
```json
{
  "job_title": "senior_react_developer",
  "experience_years": 5,
  "seniority_level": "senior",
  "employment_type": "full_time",
  "city": "tehran",
  "currency_unit": "toman",
  "skills": [{"name": "React", "level": "advanced"}],
  "education": "Bachelor's"
}
```

**Backend processing:**
1. Domain input validation (Pydantic v2 `field_validator`)
2. Market profile matching (deterministic: job_title + seniority + city)
3. Base salary = median of available market sources
4. Adjustments applied (Decimal multipliers): experience, skills, education, city, employment type
5. Confidence calculated from data volume, recency, experience, skill relevance
6. Range calculated (±15–40% based on confidence)
7. Legal minimum wage loaded from 1404 rule set (103,909,680 Rial)
8. Calculation hash generated (SHA-256)
9. Result assembled with provenance

**Refusal:** If no market profile matches → `ValueError("insufficient_data: ...")` → HTTP 409 with `ESTIMATION_INSUFFICIENT_DATA` error code.

## Step 5: Present Results

**Page:** `SalaryEstimationResults`

**Displayed (in order):**

1. **حقوق پیشنهادی اصلی (Primary estimate):** Large prominent figure in selected currency unit
2. **حد پایین / حد بالا (Range):** Min and max of suggested range
3. **سطح اطمینان (Confidence):** High/Medium/Low with visual bar
4. **عوامل تأثیرگذار (Influencing factors):** Persian tags (experience, skills, city, seniority)
5. **منابع داده (Data sources):** Actual sources used (Jobinja, JobVision, Salary Survey)
6. **مرجع دستمزد قانونی (Legal minimum wage reference):** Shown in danger-colored card, clearly labeled as reference only
7. **جزئیات محاسبه و منبع داده (Calculation details):** Collapsible section with calculation hash and timestamp

**Insufficient data state:** Danger-colored card with message "داده ناکافی برای برآورد حقوق" and guidance to try different role/city/seniority.

## Step 6: Manager Decision

**Current status:** NOT implemented in MVP. The system shows the recommendation but does not yet allow the manager to record Accept/Modify/Reject decisions.

**Next stage (P1):** Add agreed salary input and decision recording with append-only history.

## Navigation

The main navigation includes:
- صفحه اصلی (Home) — `/` — salary estimation entry
- بازار حقوق (Salary Market) — `/salaries` — salary discovery/comparison (separate feature)
- محاسبه حقوق (Salary Calculation) — `/simulation` — gross-to-net simulation

**Note:** The navigation has a pre-existing bug where "بازار حقوق" appears twice (in PRIMARY_NAV_ITEMS and NAV_ITEMS). This does not affect the core salary estimation workflow.
