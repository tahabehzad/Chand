import { useState, type FormEvent } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Icon } from '@/components/icon';
import { isPrototypeError, login } from '@/prototype/api';
import { readSession } from '@/prototype/session';

/**
 * Manager sign-in against `POST /api/v1/auth/login`.
 *
 * The backend verifies an Argon2id password and issues one opaque token bound
 * to exactly one organisation; the token is held for this tab only. There is
 * no client-side authorization decision here — the tenant and the role are
 * decided server-side.
 */
export function ManagerLoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
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

  return (
    <div className="grid min-h-dvh bg-surface-raised lg:grid-cols-2">
      <section className="relative flex flex-col justify-between overflow-hidden bg-brand-strong px-7 py-8 text-white sm:px-12 lg:px-16 lg:py-12" aria-label="پیش‌حسابداری">
        <div aria-hidden="true" className="pointer-events-none absolute -end-32 top-1/4 size-96 rounded-full border border-white/10" />
        <div aria-hidden="true" className="pointer-events-none absolute -end-16 top-1/3 size-64 rounded-full border border-white/10" />
        <div className="relative flex items-center gap-3">
          <span className="flex size-12 items-center justify-center rounded-2xl border border-white/20 bg-white/10"><Icon name="simulation" className="size-7" /></span>
          <div><p className="text-xl font-bold">پیش‌حسابداری</p><p className="mt-1 text-xs text-white/70">همراه شما در محاسبه حقوق و دستمزد</p></div>
        </div>
        <div className="relative max-w-md py-10 lg:py-20">
          <p className="mb-5 text-xs font-medium tracking-wide text-white/70">شفافیت در هر محاسبه</p>
          <h1 className="text-3xl font-bold leading-relaxed sm:text-4xl sm:leading-relaxed">از حقوق ناخالص،<br />تا تصویری روشن از پرداخت.</h1>
          <p className="mt-5 max-w-sm text-sm leading-8 text-white/75">محاسبه حقوق، بیمه، مالیات و هزینه کارفرما را در یک فضای ساده و منظم بررسی کنید.</p>
          <div className="mt-9 hidden gap-3 sm:flex">
            {['حقوق و دستمزد', 'بیمه و مالیات', 'هزینه کارفرما'].map((label) => <span key={label} className="rounded-full border border-white/20 px-3 py-2 text-xs text-white/90">{label}</span>)}
          </div>
        </div>
        <p className="relative hidden text-xs leading-6 text-white/60 lg:block">نسخه آزمایشی محلی · مبنای محاسبات ۱۴۰۴<br />قواعد سال ۱۴۰۵ هنوز فعال نشده‌اند.</p>
      </section>
      <section className="flex flex-col justify-center px-6 py-10 sm:px-12 lg:px-16" aria-labelledby="login-title">
        <div className="mx-auto w-full max-w-sm">
          <span className="mb-6 inline-flex size-12 items-center justify-center rounded-2xl bg-brand/10 text-brand"><Icon name="lock" className="size-6" /></span>
          <p className="mb-2 text-sm text-ink-muted">خوش آمدید</p>
          <h2 id="login-title" className="text-2xl font-bold text-ink">ورود به حساب مدیریت</h2>
          <p className="mb-8 mt-3 text-sm leading-7 text-ink-muted">برای شروع محاسبه حقوق، وارد حساب خود شوید.</p>
          <form className="flex flex-col gap-5" aria-busy={busy} onSubmit={(event) => void submit(event)}>
            <Input
              label="نشانی رایانامه"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              autoComplete="username"
              placeholder="name@example.com"
              disabled={busy}
              className="min-h-12 text-start"
              dir="ltr"
              required
            />
            <div className="relative">
              <Input
              label="گذرواژه"
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              autoComplete="current-password"
              placeholder="گذرواژه خود را وارد کنید"
              disabled={busy}
              className="min-h-12 ps-20 text-start"
              dir="ltr"
              required
              />
              <button type="button" aria-pressed={showPassword} aria-label={showPassword ? 'پنهان کردن گذرواژه' : 'نمایش گذرواژه'} onClick={() => setShowPassword(!showPassword)} className="absolute bottom-0 start-0 flex min-h-12 items-center rounded-lg px-3 text-xs font-medium text-brand focus-visible:outline-2 focus-visible:outline-brand">{showPassword ? 'پنهان کن' : 'نمایش'}</button>
            </div>
            {error ? (
              <p
                role="alert"
                className="rounded-lg border border-danger/40 bg-danger/5 px-3 py-2 text-sm text-danger"
              >
                {error}
              </p>
            ) : null}
            <Button type="submit" size="lg" disabled={busy} className="mt-1 w-full">
              {busy && <Icon name="spinner" className="animate-spin" />}
              {busy ? 'در حال ورود…' : 'ورود به محاسبه حقوق'}
              {!busy && <Icon name="arrow-back" />}
            </Button>
          </form>
          <p className="mt-6 border-t border-border-subtle pt-5 text-xs leading-7 text-ink-muted">
            نشست شما به همین زبانهٔ مرورگر محدود است. پس از پایان کار، از حساب خارج شوید.
          </p>
          <p className="mt-8 text-xs text-ink-muted">پیش‌حسابداری · نسخه آزمایشی محلی</p>
        </div>
      </section>
    </div>
  );
}

export default ManagerLoginPage;
