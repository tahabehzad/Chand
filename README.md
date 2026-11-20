# چند؟ (Chand) — سامانه هوشمند برآورد حقوق و جبران خدمات بازار کار ایران

<div align="center">
  <img src="frontend/public/chand-logo.jpg" alt="لوگوی چند؟" width="120" style="border-radius: 24px; box-shadow: 0 8px 32px rgba(212,175,55,0.3);" />
  <h3>پلتفرم تخصصی تحلیل رزومه، برآورد حقوق منصفانه و تصمیم‌یاری استخدام در بازار کار ایران</h3>
  <p><strong>به‌روزرسانی: پاییز ۱۴۰۵ (آبان ۱۴۰۵) • مجهز به هوش مصنوعی Google Gemini Vision 2.0</strong></p>
  <p>
    <a href="https://github.com/tahabehzad/Chand/actions/workflows/ci.yml"><img src="https://github.com/tahabehzad/Chand/actions/workflows/ci.yml/badge.svg" alt="CI Status" /></a>
    <img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" alt="Python 3.12" />
    <img src="https://img.shields.io/badge/Node.js-22-339933?logo=node.js&logoColor=white" alt="Node.js 22" />
    <img src="https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white" alt="FastAPI" />
    <img src="https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black" alt="React 19" />
    <img src="https://img.shields.io/badge/Tests-1000%2B%20PASS-success?logo=pytest&logoColor=white" alt="Tests 1000+ PASS" />
    <img src="https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white" alt="Docker Ready" />
  </p>
</div>

---

## معرفی پروژه (Overview)

پلتفرم **«چند؟»** یک سامانه مدرن، داده‌محور و هوشمند برای مدیران منابع انسانی، کارفرمایان و کارجویان است که با تکیه بر داده‌های پایش‌شده بیش از **۱۹۴ ردیف شغلی** در بازار کار ایران (جابینجا، کوئرا، ایران‌تلنت و جاب‌ویژن)، محدوده دستمزد منصفانه را به همراه تفکیک قانونی کسورات و هزینه کل کارفرما (CTC) برآورد می‌کند.

این سامانه علاوه بر تحلیل پارامتریک سوابق و مهارت‌ها، به موتور بینایی ماشین **Google Gemini Vision** جهت سنجش اصالت و استخراج واقعیت از اسناد رسمی (سابقه بیمه تأمین اجتماعی، فیش حقوقی، حکم کارگزینی و مدارک دانشگاهی) مجهز است.

---

## قابلیت‌های کلیدی (Key Features)

### ۱. برآورد دقیق و زنده‌ی دستمزد (Market Salary Estimation)
- **بازه حقوقی صدک‌ها (P25 … P75) و میانه بازار (Median):** محاسبه چارک اول، میانه و چارک سوم بر مبنای توزیع آماری بازار.
- **پشتیبانی از ۱۹۴ ردیف شغلی:** پوشش کامل شاخه‌های نرم‌افزار، طراحی محصول، مدیریت محصول، داده و هوش مصنوعی، دواپس و زیرساخت، بازاریابی، مالی و حسابداری، منابع انسانی، فروش و توسعه بازار، و مدیریت اجرایی.
- **تأثیرپذیری زنده و چندبعدی:** محاسبه اثر سابقه کار (از ۰ سال / بدون سابقه تا ۱۵+ سال)، سطح ارشدیت (تازه‌کار، میان‌رده، ارشد، لید)، نوع استخدام (تمام‌وقت، پاره‌وقت)، شیوه کار (حضوری، هیبرید، دورکاری) و استان محل کار.
- **انتخاب‌پذیری تعاملی مهارت‌های تخصصی:** دکمه‌های فعال/غیرفعال مهارت‌ها با ۵٪ تأثیر مستقیم به ازای هر مهارت بر دستمزد و صدک‌های بازار.

### ۲. سنجش اصالت مدارک با هوش مصنوعی (AI Document Verification)
- **پشتیبانی از فرمت‌های تصویر و سند (PNG, JPG, WebP, PDF).**
- **قابلیت کشیدن و رها کردن (Drag & Drop):** آپلود آسان و بدون دردسر با افکت‌های نوری طلایی.
- **پیش‌نمایش زنده در صفحه:** نمایش فوری تصویر مدرک و مشخصات فایل درون داشبورد پیش از پردازش.
- **تشخیص و تفکیک هوشمند ماهیت سند:** استخراج نوع مدرک، درصد اصالت سند، سازمان صادرکننده، سوابق اثبات‌شده، مزد مبنا و کد رهگیری رهگیری استعلام.
- **تیکت کلید Google Gemini API:** امکان اتصال مستقیم کلید هوش مصنوعی با ذخیره‌سازی امن در کلاینت (BYOK).

### ۳. تفکیک دقیق هزینه‌های کارفرما و کسورات قانونی (CTC Breakdown)
- محاسبه خالص پرداختی به دستمزدبگیر (Net Pay).
- محاسبه کسورات حق بیمه سهم کارمند (۷٪).
- محاسبه مالیات پلکانی بر مبنای آخرین سقف معافیت ماده ۸۴ قانون مالیات‌های مستقیم.
- محاسبه سهم بیمه کارفرما (۲۳٪ شامل بیمه تأمین اجتماعی و بیمه بیکاری).
- محاسبه هزینه تمام‌شده واقعی سالانه و ماهانه جذب نیرو برای کارفرما (Cost to Company - CTC).

### ۴. طراحی بصری لوکس سازمانی (Executive Dark-Gold UI)
- رابط کاربری مدرن با رنگ‌بندی Obsidian Black و Gold Luxe.
- نمودار میله‌ای توزیع دستمزد با انیمیشن روان ارتفاع و اعداد.
- فونت استاندارد Vazirmatn و چیدمان کاملاً راست‌به‌چپ (RTL).
- خروجی رسمی PDF چاپی با قابلیت مهر دیجیتال و خروجی اکسل (Excel).

---

## پشته فناوری (Technology Stack)

```mermaid
graph TD
  User([کاربر / مدیر منابع انسانی]) --> WebUI[داشبورد رابط کاربری چند؟<br/>chand.html / React SPA]
  WebUI --> FastAPI[FastAPI Backend Server<br/>Python 3.12]
  FastAPI --> DomainEngine[موتور دامنه برآورد حقوق<br/>salary_estimation engine]
  FastAPI --> CtcEngine[موتور محاسبات هزینه کارفرما و مالیات<br/>CTC & Tax Engine]
  FastAPI --> DocAnalyzer[موتور تحلیل سندیت مدارک<br/>Career Document Analyzer]
  DocAnalyzer --> GeminiAI[Google Gemini 2.0 Flash Vision API]
  FastAPI --> Database[(PostgreSQL Database<br/>Alembic Migrations)]
```

- **فرانت‌اند:** HTML5, Tailwind CSS, Lucide Icons, React 18, TypeScript, Vite.
- **بک‌اند:** Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2, Alembic.
- **محاسبات مالی:** Decimal با دقت ۳۴ رقم اعشار و گردکردن بانکی `ROUND_HALF_UP` (بدون خطای اعشاری ممیز شناور).
- **هوش مصنوعی:** Google Gemini Vision 2.0 API با پرامپت‌های ساختاریافته استخراج واقعیت از اسناد اداری.
- **تست و کیفیت:** Pytest (بیش از ۸۰۰ تست بک‌اند)، Vitest (۱۷۰ تست فرانت‌اند)، Ruff و Strict Mypy.

---

## ساختار ریپازیتوری (Repository Layout)

```text
Chand/
├── frontend/                     # رابط کاربری و صفحات وب چند؟
│   ├── public/
│   │   ├── chand.html            # داشبورد کامل و یکپارچه اجرایی چند؟
│   │   ├── intro.html            # صفحه معرفی و اسلایدهای تعاملی
│   │   ├── chand_jobs.json       # دیتابیس ۱۹۴ شغل با مقادیر پاییز ۱۴۰۵
│   │   ├── chand-logo.jpg        # نشان رسمی پلتفرم چند؟
│   │   └── chand.ir/             # بسته مستقل پروداکشن وب‌سایت
│   └── src/                      # کامپوننت‌های مدرن React / Vite
│       ├── components/salary-estimation/  # کامپوننت‌های ماژولار استعلام
│       └── routes/               # روت‌های اختصاصی سامانه
│
├── backend/                      # سرویس‌های بک‌اند و موتورهای محاسباتی
│   ├── app/
│   │   ├── domain/salary_estimation/ # هسته ریاضی و آماری برآورد بازار
│   │   ├── api/v1/estimation/    # اندپوینت‌های FastAPI استعلام حقوق و CTC
│   │   ├── services/estimation/  # سرویس‌های تحلیل اسناد و ارتباط با Gemini
│   │   └── schemas/              # قراردادهای داده‌ای Pydantic
│   └── tests/                    # مجموعه جامع تست‌های دامنه، API و واحد
│
├── docs/                         # اسناد معماری، قراردادها و نیازمندی‌ها
│   ├── SALARY_ESTIMATION_SPEC.md # سند مشخصات فنی موتور برآورد
│   ├── LABOR_MARKET_DATA_SPEC.md # استاندارد داده‌های حقوق بازار ایران
│   ├── AI_ANALYSIS_SPEC.md       # مشخصات هوش مصنوعی تحلیل مدارک
│   ├── ARCHITECTURE.md           # معماری پلتفرم و لایه‌بندی سرویس‌ها
│   └── archive/                  # آرشیو گزارش‌ها و پژوهش‌های تاریخی
│
└── AGENTS.md                     # قوانین و تعهدات رفتاری توسعه‌دهندگان
```

---

## راهنمای راه‌اندازی و اجرا (Getting Started)

### پیش‌نیازها
- Python 3.12 یا بالاتر و ابزار **uv** (`pip install uv` یا نصب رسمی)
- Node.js 20 یا بالاتر
- pnpm

### روش سریع: اجرای یکپارچه با Docker Compose
برای بالا آوردن کل پشته (پایگاه داده PostgreSQL 16، سرور FastAPI و کلاینت فرانت‌اند) با یک دستور:

```bash
docker compose up --build
```
سپس داشبورد در آدرس `http://localhost:5273/chand.html` و مستندات API در `http://localhost:8000/docs` در دسترس خواهند بود.

---

### روش توسعه محلی (Local Development)

#### ۱. اجرای فرانت‌اند
```bash
cd frontend
pnpm install
pnpm dev
```
سپس داشبورد در آدرس زیر در دسترس خواهد بود:
`http://localhost:5273/chand.html`

### ۲. اجرای سرور بک‌اند
پروژه از پکیج منیجر مدرن **uv** برای قفل قطعی وابستگی‌ها استفاده می‌کند:

```bash
cd backend
# نصب سریع وابستگی‌ها و ایجاد محیط مجازی:
uv sync

# اجرای سرور در حالت توسعه لوکال (استفاده از داده‌های نمونه بازار بدون نیاز به پایگاه داده):
# در لینوکس و مک:
export APP_ESTIMATION_ALLOW_SAMPLE_DATA=true
uv run uvicorn app.main:create_app --factory --port 8000 --reload

# در ویندوز (PowerShell):
$env:APP_ESTIMATION_ALLOW_SAMPLE_DATA="true"
uv run uvicorn app.main:create_app --factory --port 8000 --reload
```

> **نکته برای محیط تولید یا اتصال به PostgreSQL:**
> در صورت راه‌اندازی پایگاه داده، کافی است متغیر `DATABASE_URL` را در فایل `backend/.env` وارد کرده و دستور `uv run alembic upgrade head` را اجرا نمایید.

---

## اجرای آزمون‌ها (Running Tests)

### تست‌های فرانت‌اند (Vitest)
```bash
cd frontend
pnpm test
```
*(تمامی ۱۷۰ تست فرانت‌اند PASS می‌شوند)*

### تست‌های بک‌اند (Pytest)
```bash
cd backend
uv run pytest -q tests/domain/salary_estimation tests/unit
```
*(تمامی تست‌های اعتبارسنجی ارزی، قوانین قانونی و آماری PASS می‌شوند)*

---

## مجوز (License)

توسعه‌یافته برای پلتفرم ارزیابی بازار کار و جبران خدمات ایران — پاییز ۱۴۰۵.
تمامی حقوق محفوظ است.
