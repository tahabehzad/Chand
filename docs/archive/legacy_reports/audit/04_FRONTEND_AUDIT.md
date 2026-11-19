# حسابرسی فرانت‌اند

**تاریخ:** ۲۸ آبان ۱۴۰۵  
**شناسه:** AUDIT-04

---

## ۱. خلاصه

فرانت‌اند یک SPA فارسی RTL با کیفیت متوسط است. Shell، routing و UI primitives خوب هستند ولی صفحات salary estimation حاوی خطاهای واضح هستند.

---

## ۲. Component Inventory

### ۲.۱ واقعی و فعال
| کامپوننت | فایل | وضعیت |
|:---|:---|:--:|
| App Shell | `app-shell.tsx` | ✅ RTL, Vazirmatn, navigation |
| Router | `router.tsx` | ✅ ۲۰+ route با code splitting |
| Session Management | `prototype/session.ts` | ✅ sessionStorage, tolerant reader |
| RequireManager guard | `require-manager.tsx` | ✅ navigation guard (نه security) |
| SessionBridge | `session-bridge.tsx` | ✅ 401 → redirect |
| Button, Card, Input, Badge | `components/ui/` | ✅ Tailwind primitives |
| Money formatting | `lib/money.ts` | ✅ Rial/Toman با separators فارسی |
| Persian numerals | `lib/numerals.ts` | ✅ تبدیل اعداد فارسی |
| Calendar | `lib/calendar.ts` | ✅ تبدیل شمسی/میلادی |
| API client | `api/client.ts` | ✅ Typed, error handling |
| Contracts | `api/contracts.ts` | ✅ Endpoint registry |

### ۲.۲ جدید (salary estimation) — ناقص
| کامپوننت | فایل | وضعیت |
|:---|:---|:--:|
| SalaryEstimationPage | `salary-estimation/SalaryEstimationPage.tsx` | ❌ خطای syntax (Badge import نشده) |
| SalaryEstimationForm | `salary-estimation/SalaryEstimationForm.tsx` | ⚠️ باید بررسی شود |
| SalaryEstimationResults | `salary-estimation/SalaryEstimationResults.tsx` | ⚠️ باید بررسی شود |
| SalaryDiscoveryPage | `salary-discovery/SalaryDiscoveryPage.tsx` | ⚠️ بدون مستندات |
| SalaryResultCard | `salary-discovery/SalaryResultCard.tsx` | ⚠️ بدون مستندات |
| salary-estimation API | `api/salary-estimation.ts` | ✅ Typed client |
| salary-benchmarks | `lib/salary-benchmarks.ts` | ⚠️ بدون مستندات |

### ۲.۳ Prototype/Demo — قدیمی
| کامپوننت | فایل | وضعیت |
|:---|:---|:--:|
| Prototype Dashboard | `routes/prototype/dashboard-page.tsx` | ⚠️ Demo |
| Prototype People | `routes/prototype/people-page.tsx` | ⚠️ Demo |
| Prototype Person | `routes/prototype/person-page.tsx` | ⚠️ Demo |
| Prototype Recommendation | `routes/prototype/recommendation-page.tsx` | ⚠️ Demo |
| Demo Accounting Data | `data/demo-accounting.ts` | ⚠️ Static demo data |

### ۲.۴ Payroll-era — preserved ولی نه محصول فعال
| کامپوننت | فایل | وضعیت |
|:---|:---|:--:|
| SimulationPage | `routes/simulation-page.tsx` | ✅ Gross-to-net form (کار می‌کند) |
| ProposalPage | `routes/proposal-page.tsx` | ⚠️ Manager proposal |
| WorkProfile fields | `routes/work-profile-fields.tsx` | ⚠️ نیاز به DB |
| Manager login | `routes/manager-login-page.tsx` | ⚠️ نیاز به DB |
| Module pending pages | `routes/modules.tsx` | ⚠️ Placeholder |

---

## ۳. یافته‌های بحرانی

### FIND-FE-01: خطای syntax در SalaryEstimationPage
- **شدت:** بالا
- **فایل:** `frontend/src/components/salary-estimation/SalaryEstimationPage.tsx` خط ۶۰-۶۲
```tsx
<Badge variant='outline' className='text-xs'>
  ADR-013 · نسخه{v1.0}
</Badge>
```
- **مسئله:** `Badge` هیچ‌جا import نشده؛ `{v1.0}` یک expression نامعتبر JSX است (باید `{'v1.0'}` باشد)
- **تأثیر:** این صفحه در runtime خطا می‌دهد و render نمی‌شود

### FIND-FE-02: window.apiClient استفاده نامتعارف
- **شدت:** متوسط
- **فایل:** `SalaryEstimationPage.tsx` خط ۲۹
```tsx
const response = await estimateSalary(window.apiClient, data);
```
- **مسئله:** `window.apiClient` type-safe نیست و ممکن است undefined باشد. فایل `instance.ts` یک `apiClient` export می‌کند که باید مستقیماً import شود

### FIND-FE-03: Routing بدون حفاظت
- **شدت:** متوسط
- **فایل:** `router.tsx` خط ۸۴-۸۶
- **مسئله:** مسیرهای `salary-estimation` و `salaries` با `withSuspense` محافظت شده‌اند ولی نه با `guarded` — یعنی بدون session هم قابل دسترسی هستند
- **توجه:** این ممکن است عمدی باشد (ADR-013 single manager بدون auth complex)

---

## ۴. RTL و فارسی — ارزیابی مثبت

| معیار | وضعیت |
|:---|:--:|
| `dir="rtl"` روی HTML | ✅ |
| Vazirmatn font loaded | ✅ |
| Logical CSS properties (not physical) | ✅ |
| Persian numerals helper | ✅ |
| Jalali calendar conversion | ✅ |
| Rial/Toman formatting | ✅ |
| Money separator (فارسی) | ✅ |
| BiDi text component | ✅ |

---

## ۵. تست‌ها

| فایل تست | موضوع | وضعیت |
|:---|:---|:--:|
| `app-shell.test.tsx` | Shell rendering | ✅ |
| `mvp-navigation.test.tsx` | Navigation items | ✅ |
| `client.test.ts` | API client | ✅ |
| `contracts.test.ts` | Contract validation | ✅ |
| `provenance.test.ts` | Provenance types | ✅ |
| `states.test.tsx` | UI states | ✅ |
| `icon.test.tsx` | Icon component | ✅ |
| `money.test.ts` | Money formatting | ✅ |
| `numerals.test.ts` | Persian numerals | ✅ |
| `calendar.test.ts` | Jalali calendar | ✅ |
| `text.test.ts` | Text utilities | ✅ |
| `simulation-page.test.tsx` | Payroll simulation | ✅ |
| `work-profile-fields.test.tsx` | Work profile | ✅ |
| `api.test.ts` | Prototype API | ✅ |
| `logical-utilities-gate.test.ts` | CSS gate | ✅ |

**مشاهده:** ۱۵ فایل تست — خوب برای utilities و payroll-era، ولی **هیچ تستی برای salary estimation components** نیست.

---

## ۶. وابستگی‌ها — ارزیابی

- **React 19:** جدیدترین نسخه، مناسب
- **Vite 6:** مناسب
- **Tailwind 4:** مناسب با `@tailwindcss/vite`
- **React Router 7:** مناسب
- **TanStack Query 5:** import شده ولی **در salary estimation استفاده نشده** — فقط در payroll-era
- **Zustand 5:** برای UI store (theme, session-expired flag)
- **هیچ وابستگی اضافی غیرضروری وجود ندارد**

---

## ۷. Build Configuration

- `vite.config.ts`: Path aliases, React plugin
- `tsconfig.app.json`: Strict mode
- Build script: `tsc --noEmit && vite build`
- **⚠️ خطای FIND-FE-01 احتمالاً باعث شکست build می‌شود** (Badge import missing → type error)

---

## ۸. پیوست بازبینی مستقل (ادامهٔ حسابرسی — ۲۸ آبان ۱۴۰۵)

یافته‌های این بخش با اجرای واقعی `npx tsc --noEmit -p tsconfig.app.json`، `npx vitest run` و خواندن UTF-8 فایل‌ها تأیید شده‌اند. متن بخش‌های ۱–۷ بازنویسی نشده است.

### FE-04 — build فرانت‌اند با ۹ خطای نحوی شکست می‌خورد
- **شدت:** بحرانی
- **شرح:** خروجی واقعی `tsc` (exit 1):
  ```
  src/components/salary-discovery/SalaryDiscoveryPage.tsx(351,70): TS1381
  src/components/salary-discovery/SalaryDiscoveryPage.tsx(352,23): TS1003
  src/components/salary-estimation/SalaryEstimationPage.tsx(61,28): TS1005
  src/components/salary-estimation/SalaryEstimationPage.tsx(61,30): TS1381
  src/lib/salary-benchmarks.ts(99,40): TS1005
  src/lib/salary-benchmarks.ts(99,61): TS1005
  src/lib/salary-benchmarks.ts(99,64): TS1005
  src/lib/salary-benchmarks.ts(99,74): TS1005
  src/lib/salary-benchmarks.ts(100,5): TS1005
  ```
- **مسیر و خط:**
  - `SalaryDiscoveryPage.tsx:351` → `<span class отч://selectedBenchmark.maxSalary} ...` (سیریلیک + `://` داخل JSX)
  - `salary-benchmarks.ts:99` → `experienceRange: { min: 1, max: man's experience range' to 'maximum' }` (یک دستور متنی/ویرایشی داخل کد)
  - `SalaryEstimationPage.tsx:61` → `نسخه{v1.0}`
- **تأثیر:** FIND-FE-01 فقط یکی از سه محل خرابی بود؛ build در سه فایل شکسته است. این خطاها نشانهٔ کد تولیدشده و ذخیره‌شده بدون اجرای ابزار است.
- **اقدام:** بازنویسی سه قطعه و اجرای مجدد `tsc` تا exit 0.

### FE-05 — سه وابستگی import‌شده اما نصب/اعلام‌نشده
- **شدت:** بحرانی
- **شرح:** `react-hook-form`، `@hookform/resolvers/zod` و `zod` نه در `package.json` هستند نه در `node_modules`.
- **مسیر و خط:** `SalaryEstimationForm.tsx:9-11`
- **تأثیر:** پس از رفع FE-04، `tsc` خطای «Cannot find module» می‌دهد؛ فرم هرگز اجرا نمی‌شود. افزودن آن‌ها هم خلاف AGENTS.md §15 است (بدون تصویب).
- **اقدام:** DEC-11.

### FE-06 — `window.apiClient` وجود ندارد
- **شدت:** بالا
- **شرح:** `estimateSalary(window.apiClient, data)` فراخوانی می‌شود، اما در سراسر `src` هیچ تعریف global برای `window.apiClient` نیست؛ تنها صادرکننده، `apiClient` در `@/api/instance` است.
- **مسیر و خط:** `SalaryEstimationPage.tsx:29`؛ مقایسه با `simulation-page.tsx:10,188` که همان الگوی صحیح import را دارد.
- **تأثیر:** پس از رفع خطاهای نحوی، خطای type (و در runtime، `undefined`) رخ می‌دهد.
- **اقدام:** import مستقیم از `@/api/instance`.

### FE-07 — مدل ناوبری تکراری و مسیر یتیم
- **شدت:** بالا
- **شرح:** `/salaries` هم در `PRIMARY_NAV_ITEMS` (`navigation.ts:55-63`) و هم در `NAV_ITEMS` (`:82-91`) وجود دارد؛ سه تست ناوبری (`app-shell.test.tsx`) شکست می‌خورند، از جمله `expected 13 to be 14`. در مقابل، `/salary-estimation` در router ثبت شده (`router.tsx:84`) اما در هیچ منوی کاربری نیست.
- **تأثیر:** آیتم تکراری در منو و صفحه‌ای که کاربر نمی‌تواند پیدا کند.
- **اقدام:** ARCH-08.

### FE-08 — متن فارسی خراب و واژگان نادرست در UI
- **شدت:** بالا
- **شرح (خوانده‌شده با UTF-8 صحیح):**

  | مکان | متن | مشکل |
  |:---|:---|:---|
  | `SalaryEstimationResults.tsx:157` | «شناسه محاسبه و로부터ی» | حروف کره‌ای |
  | `SalaryEstimationForm.tsx:132` | `<option value='saveh'>سSave</option>` | ترکیب فارسی/لاتین |
  | `SalaryEstimationForm.tsx:64` | placeholder «توسعه‌دهنده پیرایش» | واژهٔ بی‌معنا |
  | `SalaryEstimationForm.tsx:95-97` | «میان‌جستجو (Junior)»، «کارساز (Mid)»، «سطح کارشناسی» | ترجمهٔ نادرست؛ معادل: جونیور/میان‌رده/ارشد، سطح ارشدیت |
  | `contracts.ts:123` | «برآ즈ۀ حقوق» | ترکیب «ز»/«ژ» |
  | چند صفحه | «برآزۀ»، «برآزه» | صورت صحیح: «برآورد» |

- **تأثیر:** نقض AGENTS.md §10 و قرارداد `persian-rtl-engineering`؛ متن با نویسهٔ غیرفارسی در محصول فارسی، اعتماد را از بین می‌برد.
- **اقدام:** بازنویسی رشته‌ها + گیت CI نویسه (ARCH-09).

### FE-09 — دادهٔ بنچمارک ساختگی با ابراز نمونه و تاریخ جعلی
- **شدت:** بالا
- **شرح:** `salary-benchmarks.ts` رکوردهایی با `sampleSize: 312/134/98`، `updatedAt: '2026-11-15'` و `cityCoefficient` اعشاری دارد، بدون هیچ منبع یا مسیر جمع‌آوری. صفحهٔ `SalaryDiscoveryPage` با `medianSalary * 0.65` و `* 0.35` مبلغ را با float می‌شکند.
- **مسیر و خط:** `frontend/src/lib/salary-benchmarks.ts`؛ `SalaryDiscoveryPage.tsx:369`
- **تأثیر:** «۵۰٪ میانه»، «حقوق پایه = ۶۵٪ میانه» و «حجم نمونه» همه ساختگی‌اند؛ FR-13 نقض می‌شود و مبالغ با float محاسبه می‌شوند.
- **اقدام:** حذف از محصول تا وجود دادهٔ منبع‌دار (DEC-01).

### FE-10 — انتخاب مهارت بی‌اثر است
- **شدت:** متوسط
- **شرح:** چیپ‌های مهارت `onClick={() => {}}` دارند و `skills` در schema فرم نیست؛ بنابراین هرگز ارسال نمی‌شود.
- **مسیر و خط:** `SalaryEstimationForm.tsx:17-24, 155-173`
- **تأثیر:** کاربر انتخابی انجام می‌دهد که نتیجه ندارد؛ «پرمیوم مهارت» در مسیر UI صفر است.
- **اقدام:** افزودن فیلد مهارت به state فرم و به payload.

### FE-11 — تبدیل پول با تقسیم float و نمایش مرجع غلط
- **شدت:** متوسط
- **شرح:** `formatRial` مقدار را با `value / 10` تقسیم می‌کند (float) و `toLocaleString('fa-IR')` را روی float اجرا می‌کند؛ عدد ریالی به تومان تبدیل می‌شود که با قرارداد ADR-013 (ذخیره ریال، نمایش تومان) هم‌خوان است، اما محاسبهٔ پول با float انجام می‌شود. هم‌زمان مرجع حداقل دستمزد (۳۶٬۰۰۰٬۰۰۰ ریال، نادرست) در یک کارت قرمز برجسته نمایش داده می‌شود.
- **مسیر و خط:** `SalaryEstimationResults.tsx:24-27, 136-152`
- **تأثیر:** نقض مسیر پول در لایهٔ نمایش + نمایش عدد قانونی نادرست.
- **اقدام:** `lib/money.ts` موجود بازاستفاده شود (که همین کار را با صحت انجام می‌دهد) و مرجع از rule set بیاید.

### FE-12 — قرارداد «delivered» برای قابلیتی که build نمی‌شود
- **شدت:** پایین
- **شرح:** `contracts.ts:119-126` ورودی تخمین را `availability: 'delivered'` علامت زده، در حالی که فایل خودش را «truthful inventory» می‌نامد و تست قرارداد همین را نقض می‌کند (TEST-03).
- **تأثیر:** ادعای تحویل نادرست در منبع حقیقتِ قراردادها.
- **اقدام:** بازگرداندن به `awaiting-backend` تا سبز شدن مسیر واقعی.

