import { useState, type FormEvent } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { Icon } from '@/components/icon';
import { isPrototypeError, login } from '@/prototype/api';
import { readSession, writeSession } from '@/prototype/session';

/**
 * Manager sign-in against `POST /api/v1/auth/login`.
 *
 * Redesigned SaaS login UI:
 * - Right column: Clean, high-contrast light form on `#F8FAFC`
 * - Left column: Branded advertisement showcase panel on `#0A2540`
 * - Responsive: Mobile single column with form first
 * - Zero physical utility violations (logical CSS only)
 */
export function ManagerLoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  if (readSession() !== null) {
    return <Navigate to="/" replace />;
  }

  async function submit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await login(email, password);
      navigate('/', { replace: true });
    } catch (caught) {
      setError(
        isPrototypeError(caught)
          ? caught.message
          : 'ورود ناموفق بود؛ دوباره تلاش کنید.',
      );
    } finally {
      setBusy(false);
    }
  }

  function handleDemoAccess(): void {
    writeSession({
      token: 'demo-token',
      manager: { id: 'demo-1', displayName: 'مدیر دمو', email: 'demo@pish.ir' },
      organization: { id: 'org-demo', nameFa: 'سازمان پیش‌نمایش' },
    });
    navigate('/', { replace: true });
  }

  return (
    <div className="grid min-h-dvh bg-[#F8FAFC] lg:grid-cols-2">
      {/* 1. Right Column Form (Mobile first, desktop right column in RTL) */}
      <section
        className="flex flex-col items-center justify-center p-6 sm:p-10 lg:p-12 bg-[#F8FAFC]"
        aria-labelledby="login-title"
      >
        <div className="w-full max-w-[400px] rounded-3xl bg-white p-8 sm:p-12 shadow-sm border border-slate-200/80">
          <div className="mb-6">
            <p className="text-xs font-semibold text-slate-500 mb-1">خوش برگشتی</p>
            <h2 id="login-title" className="text-2xl font-black text-slate-900 tracking-tight">
              ورود به حساب مدیریت
            </h2>
            <p className="mt-2 text-xs leading-relaxed text-slate-500">
              برای ادامه محاسبه حقوق ۱۴۰۴ وارد شوید.
            </p>
          </div>

          <form className="flex flex-col gap-4" aria-busy={busy} onSubmit={(event) => void submit(event)}>
            {/* Email Input */}
            <div className="space-y-1.5">
              <label htmlFor="email-input" className="text-xs font-bold text-slate-700">
                نشانی ایمیل
              </label>
              <input
                id="email-input"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                autoComplete="username"
                placeholder="name@company.com"
                disabled={busy}
                required
                dir="ltr"
                className="h-14 w-full rounded-[14px] border border-slate-200 bg-white px-4 text-start text-sm text-slate-800 placeholder:text-slate-400 focus:border-[#0B2B4F] focus:outline-none focus:ring-2 focus:ring-[#0B2B4F]/20 transition-all"
              />
            </div>

            {/* Password Input */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label htmlFor="password-input" className="text-xs font-bold text-slate-700">
                  گذرواژه
                </label>
                <a
                  href="#forgot"
                  onClick={(event) => {
                    event.preventDefault();
                    setError('برای بازیابی گذرواژه با پشتیبانی سیستم تماس بگیرید.');
                  }}
                  className="text-xs font-semibold text-[#0B2B4F] hover:underline"
                >
                  فراموش کردم؟
                </a>
              </div>
              <div className="relative">
                <input
                  id="password-input"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  autoComplete="current-password"
                  placeholder="گذرواژه خود را وارد کنید"
                  disabled={busy}
                  required
                  dir="ltr"
                  className="h-14 w-full rounded-[14px] border border-slate-200 bg-white px-4 pe-11 text-start text-sm text-slate-800 placeholder:text-slate-400 focus:border-[#0B2B4F] focus:outline-none focus:ring-2 focus:ring-[#0B2B4F]/20 transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((prev) => !prev)}
                  className="absolute inset-y-0 end-0 flex items-center pe-3.5 text-slate-400 hover:text-slate-600 transition-colors cursor-pointer"
                  aria-label={showPassword ? 'پنهان کردن گذرواژه' : 'نمایش گذرواژه'}
                >
                  {showPassword ? (
                    <svg
                      className="size-5"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.8"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      aria-hidden="true"
                    >
                      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
                      <line x1="1" y1="1" x2="23" y2="23" />
                    </svg>
                  ) : (
                    <svg
                      className="size-5"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.8"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      aria-hidden="true"
                    >
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                      <circle cx="12" cy="12" r="3" />
                    </svg>
                  )}
                </button>
              </div>
            </div>

            {/* Checkbox "مرا به خاطر بسپار" */}
            <div className="flex items-center gap-2 pt-1">
              <input
                id="remember-me"
                type="checkbox"
                checked={rememberMe}
                onChange={(event) => setRememberMe(event.target.checked)}
                className="size-4 rounded-[5px] border border-slate-300 text-[#0B2B4F] focus:ring-[#0B2B4F] focus:ring-offset-0 cursor-pointer accent-[#0B2B4F]"
              />
              <label htmlFor="remember-me" className="text-xs font-medium text-slate-600 cursor-pointer select-none">
                مرا به خاطر بسپار
              </label>
            </div>

            {/* Error Message */}
            {error ? (
              <p
                role="alert"
                className="rounded-xl border border-red-200 bg-red-50 p-3 text-xs font-medium text-red-600"
              >
                {error}
              </p>
            ) : null}

            {/* ONE Primary Button */}
            <button
              type="submit"
              disabled={busy}
              className="mt-2 h-14 w-full rounded-[14px] bg-[#0B2B4F] hover:bg-[#08203a] active:bg-[#06182c] text-white font-bold text-base transition-all duration-200 shadow-md shadow-[#0B2B4F]/15 flex items-center justify-center gap-2 cursor-pointer focus:outline-none focus:ring-2 focus:ring-[#0B2B4F] focus:ring-offset-2 disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {busy ? (
                <>
                  <Icon name="spinner" className="size-5 animate-spin" />
                  <span>در حال ورود…</span>
                </>
              ) : (
                <span>ورود به محاسبه حقوق ←</span>
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="relative my-5 flex items-center justify-center">
            <div className="absolute inset-0 flex items-center" aria-hidden="true">
              <div className="w-full border-t border-slate-200" />
            </div>
            <span className="relative bg-white px-3 text-xs font-medium text-slate-400">یا</span>
          </div>

          {/* Ghost Button: مشاهده دمو بدون ورود */}
          <button
            type="button"
            onClick={handleDemoAccess}
            className="h-12 w-full rounded-[14px] border border-slate-200 hover:border-slate-300 bg-transparent hover:bg-slate-50 text-slate-700 font-bold text-sm transition-all duration-200 flex items-center justify-center gap-2 cursor-pointer focus:outline-none focus:ring-2 focus:ring-slate-300"
          >
            مشاهده دمو بدون ورود
          </button>

          {/* New Button: مشاهده اینترو و سامانه «چند؟» */}
          <button
            type="button"
            onClick={() => navigate('/chand')}
            className="h-12 w-full rounded-[14px] bg-gradient-to-r from-amber-500/10 via-amber-400/20 to-amber-500/10 border border-amber-400/40 hover:border-amber-400 text-amber-900 font-bold text-xs sm:text-sm transition-all duration-200 flex items-center justify-center gap-2 cursor-pointer shadow-sm hover:shadow"
          >
            <span>✨ مشاهده اینترو سینمایی و نسخه «چند؟»</span>
            <span className="text-xs">←</span>
          </button>

          {/* Footer */}
          <p className="mt-8 text-center text-[11px] font-medium text-slate-400 leading-relaxed border-t border-slate-100 pt-5">
            🔒 اطلاعات شما رمزنگاری میشود | مبنای محاسبات: قانون کار ۱۴۰۴
          </p>
        </div>
      </section>

      {/* 2. Left Column Ad Panel (bg #0A2540, subtle circles) */}
      <section
        className="relative flex flex-col justify-between overflow-hidden bg-[#0A2540] p-8 sm:p-12 lg:p-16 text-white"
        aria-label="چند؟"
      >
        {/* Subtle geometric circles */}
        <div
          aria-hidden="true"
          className="pointer-events-none absolute -top-24 -end-24 size-96 rounded-full border border-white/5 bg-gradient-to-br from-white/5 to-transparent blur-xs"
        />
        <div
          aria-hidden="true"
          className="pointer-events-none absolute top-1/2 -start-32 size-[440px] rounded-full border border-white/5"
        />
        <div
          aria-hidden="true"
          className="pointer-events-none absolute -bottom-20 -end-16 size-80 rounded-full border border-white/5"
        />

        <div className="relative z-10">
          {/* Header branding */}
          <div className="flex items-center gap-3">
            <span className="flex size-11 items-center justify-center rounded-2xl border border-white/20 bg-white/10 shadow-inner">
              <Icon name="simulation" className="size-6 text-white" />
            </span>
            <div>
              <p className="text-lg font-bold text-white">چند؟</p>
              <p className="text-[11px] text-white/60">سامانه هوشمند برآورد حقوق و جبران خدمات</p>
            </div>
          </div>

          {/* Main Ad Copy */}
          <div className="mt-10 lg:mt-14 max-w-lg">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3.5 py-1 text-xs font-semibold text-emerald-400 backdrop-blur-md shadow-inner">
              <span className="size-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span>شفافیت در هر محاسبه • نسخه ۰٫۱</span>
            </div>

            {/* H1 */}
            <h1 className="mt-6 text-[32px] sm:text-[36px] lg:text-[40px] font-black text-white leading-[1.9] tracking-tight">
              از حقوق ناخالص تا فیش شفاف
            </h1>

            {/* Sub */}
            <p className="mt-3 text-sm sm:text-base text-slate-300 leading-relaxed max-w-md">
              حقوق، بیمه، مالیات و هزینه کارفرما رو در ۳۰ ثانیه ببین.
            </p>

            {/* 3 Checks */}
            <ul className="mt-7 space-y-3">
              {[
                'محاسبه دقیق بیمه سهم کارگر و کارفرما ۱۴۰۴',
                'مالیات پلکانی حقوق + خروجی فیش قابل چاپ',
                'بدون اکسل، بدون خطا',
              ].map((item) => (
                <li key={item} className="flex items-center gap-3 text-sm text-slate-200 font-medium">
                  <span className="flex size-5 shrink-0 items-center justify-center rounded-full bg-[#0E9F6E]/20 text-[#0E9F6E] border border-[#0E9F6E]/40 text-xs font-bold">
                    ✓
                  </span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>

            {/* Glass Preview Card */}
            <div className="mt-8 rounded-2xl border border-white/15 bg-white/10 p-5 backdrop-blur-xl shadow-2xl space-y-3 max-w-md">
              <div className="flex items-center justify-between text-xs text-slate-300 border-b border-white/10 pb-2.5">
                <span>حقوق ناخالص ماهانه</span>
                <span className="font-mono text-sm font-bold tabular-nums text-white">۴۵,۰۰۰,۰۰۰ ریال</span>
              </div>
              <div className="flex items-center justify-between text-xs text-rose-300">
                <span>بیمه سهم کارگر (۷٪)</span>
                <span className="font-mono tabular-nums text-rose-300">-۳,۱۵۰,۰۰۰ ریال</span>
              </div>
              <div className="flex items-center justify-between text-xs text-rose-300">
                <span>مالیات بر حقوق</span>
                <span className="font-mono tabular-nums text-rose-300">-۱,۲۰۰,۰۰۰ ریال</span>
              </div>
              <div className="border-t border-white/10 pt-2.5 flex items-center justify-between">
                <span className="text-xs font-bold text-slate-200">خالص دریافتی</span>
                <span className="font-mono text-base font-black tabular-nums text-[#0E9F6E]">
                  ۴۰,۶۵۰,۰۰۰ ریال
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Trust Footer */}
        <div className="relative z-10 mt-10 pt-6 border-t border-white/10 flex items-center gap-2 text-xs text-slate-400 font-medium">
          <span className="size-2 rounded-full bg-emerald-400" />
          <span>مبنای ۱۴۰۴ • بهروزرسانی خودکار برای ۱۴۰۵</span>
        </div>
      </section>
    </div>
  );
}

export default ManagerLoginPage;
