import { useEffect, useState } from 'react';
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { Icon } from '@/components/icon';
import { Badge } from '@/components/ui/badge';
import { StatutoryBaselineNotice } from '@/components/layout/statutory-baseline-notice';
import { ToastContainer } from '@/components/ui/toast';
import { NAV_ITEMS, PRIMARY_NAV_ITEMS, type NavItem } from '@/app/navigation';
import { SessionBridge } from '@/app/session-bridge';
import { logout } from '@/prototype/api';
import { readSession } from '@/prototype/session';
import { useUiStore } from '@/state/ui-store';
import { cn } from '@/lib/cn';

function NavItems({ onNavigate, items = NAV_ITEMS }: { onNavigate?: () => void; items?: readonly NavItem[] }) {
  return (
    <ul className="flex flex-col gap-1">
      {items.map((item) => (
        <li key={item.id}>
          <NavLink
            to={item.path}
            end={item.path === '/'}
            onClick={onNavigate}
            className={({ isActive }) =>
              cn(
                'flex items-start gap-3 rounded-xl px-3 py-2.5 text-sm transition-all duration-200',
                isActive
                  ? 'bg-brand/10 font-semibold text-brand-strong border border-brand/20'
                  : 'text-ink-muted hover:bg-surface hover:text-ink hover:border-border-subtle/50',
              )
            }
          >
            {({ isActive }) => (
              <>
                <Icon name={item.icon} className={cn('mt-0.5 shrink-0', isActive && 'text-brand')} />
                <span className="flex min-w-0 flex-col gap-0.5">
                  <span>{item.labelFa}</span>
                  {item.descriptionFa && <span className="text-xs font-normal text-ink-muted">{item.descriptionFa}</span>}
                </span>
              </>
            )}
          </NavLink>
        </li>
      ))}
    </ul>
  );
}

/**
 * The RTL application shell with FoodTrace-inspired premium styling:
 * glass header, dark mode toggle, emerald accent, hover-lift cards.
 */
export function AppShell() {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const isPrototypePage = pathname.startsWith('/prototype');
  const isCalculatorPage = pathname === '/' || pathname === '/simulation';
  const isDemoPage = ['/transactions', '/settings'].includes(pathname);
  const mobileNavOpen = useUiStore((state) => state.mobileNavOpen);
  const setMobileNavOpen = useUiStore((state) => state.setMobileNavOpen);
  const session = readSession();
  const [signingOut, setSigningOut] = useState(false);
  const [darkMode, setDarkMode] = useState(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('theme');
      if (stored) return stored === 'dark';
      if (typeof window.matchMedia === 'function') {
        return window.matchMedia('(prefers-color-scheme: dark)').matches;
      }
    }
    return false;
  });

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
      document.documentElement.classList.remove('light');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      document.documentElement.classList.add('light');
      localStorage.setItem('theme', 'light');
    }
  }, [darkMode]);

  async function onSignOut(): Promise<void> {
    setSigningOut(true);
    try {
      await logout();
    } finally {
      setSigningOut(false);
      navigate('/login', { replace: true });
    }
  }

  useEffect(() => {
    if (!mobileNavOpen) return undefined;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setMobileNavOpen(false);
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [mobileNavOpen, setMobileNavOpen]);

  return (
    <div className="flex min-h-screen flex-col bg-surface-muted transition-colors duration-300 overflow-x-hidden w-full max-w-full">
      <SessionBridge />
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:start-2 focus:z-50 focus:rounded-lg focus:bg-brand focus:px-4 focus:py-2 focus:text-white"
      >
        پرش به محتوای اصلی
      </a>

      <header className={cn('sticky top-0 z-40 h-14 border-b border-border-subtle header-glass flex items-center', darkMode ? 'dark border-border-subtle-dark' : '')}>
        <div className="flex h-full w-full items-center justify-between gap-3 px-4 sm:px-6">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setMobileNavOpen(!mobileNavOpen)}
              aria-expanded={mobileNavOpen}
              aria-controls="primary-navigation"
              aria-label={mobileNavOpen ? 'بستن منو' : 'باز کردن منو'}
              className={cn(
                'inline-flex min-h-10 min-w-10 items-center justify-center rounded-xl border border-border-subtle text-ink-muted hover:text-ink lg:hidden transition-colors',
                darkMode ? 'dark:border-border-subtle-dark dark:text-ink-muted-dark' : '',
              )}
            >
              <Icon name={mobileNavOpen ? 'close' : 'menu'} />
            </button>

            <div className="flex min-w-0 items-center gap-2.5">
              <img src="/chand-logo.jpg" alt="چند؟" className="h-8 w-8 rounded-lg object-contain border border-brand/30 shadow-sm shrink-0" />
              <div className="flex min-w-0 flex-col">
                <span className="truncate text-base font-black text-ink tracking-tight">چند؟</span>
                <span className="hidden truncate text-xs text-ink-muted sm:inline">
                  فضای ساده مدیریت مالی · نسخه نمونه
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setDarkMode((prev) => !prev)}
              aria-label={darkMode ? 'پوسته روشن' : 'پوسته تیره'}
              className={cn(
                'inline-flex min-h-10 min-w-10 items-center justify-center rounded-xl border border-border-subtle text-ink-muted transition-colors',
                darkMode
                  ? 'bg-surface-raised text-brand-strong border-brand/30'
                  : 'hover:bg-surface hover:text-ink',
              )}
            >
              <Icon name={darkMode ? 'sun' : 'moon'} />
            </button>

            {!isCalculatorPage && (isPrototypePage || isDemoPage) && (
              <Badge tone={isPrototypePage ? 'warning' : 'info'}>
                {isPrototypePage ? 'ارزیابی — مدل پیش‌نویس' : 'داده‌های نمایشی'}
              </Badge>
            )}

            {/* Desktop header controls */}
            <div className="hidden lg:flex lg:items-center lg:gap-3">
              {session !== null ? (
                <span className="flex flex-col text-end text-xs text-ink-muted">
                  <span className="font-medium text-ink">{session.manager.displayName}</span>
                  <span>{session.organization.nameFa}</span>
                </span>
              ) : null}

              <NavLink
                to="/chand"
                className="inline-flex min-h-10 items-center gap-1.5 rounded-xl border border-amber-500/30 bg-amber-500/10 px-3 py-1.5 text-xs font-bold text-amber-600 hover:bg-amber-500/20 transition-colors"
                title="مشاهده نسخه چند؟ با انیمیشن‌های اینترو"
              >
                <span>✨ نسخه «چند؟»</span>
              </NavLink>

              {session !== null ? (
                <button
                  type="button"
                  onClick={() => void onSignOut()}
                  disabled={signingOut}
                  className="min-h-10 rounded-xl border border-border-subtle px-3.5 py-1.5 text-xs font-semibold text-ink-muted hover:text-ink hover:bg-surface disabled:opacity-60 transition-colors"
                >
                  {signingOut ? 'در حال خروج…' : 'خروج'}
                </button>
              ) : null}
            </div>
          </div>
        </div>
      </header>

      <div className="flex flex-1 flex-col lg:flex-row">
        {mobileNavOpen && (
          <div
            className="fixed inset-0 z-20 bg-ink/40 backdrop-blur-sm lg:hidden transition-opacity duration-300"
            onClick={() => setMobileNavOpen(false)}
            aria-hidden="true"
          />
        )}
        <aside
          id="primary-navigation"
          className={cn(
            'border-border-subtle bg-surface-raised p-4 transition-colors duration-300',
            darkMode ? 'dark:border-border-subtle-dark dark:bg-surface-raised-dark' : '',
            isCalculatorPage
              ? (mobileNavOpen ? 'fixed inset-y-0 start-0 z-30 w-72 block border-e shadow-2xl lg:hidden' : 'hidden')
              : (mobileNavOpen ? 'block border-b lg:block lg:w-64 lg:shrink-0 lg:border-e' : 'hidden lg:block lg:w-64 lg:shrink-0 lg:border-e')
          )}
        >
          <nav aria-label="ناوبری اصلی" className="flex flex-col gap-4">
            <div className="flex items-center justify-between pb-2 border-b border-border-subtle lg:hidden">
              <span className="font-bold text-sm text-ink">منوی چند؟</span>
              <button
                type="button"
                onClick={() => setMobileNavOpen(false)}
                className="text-ink-muted hover:text-ink text-sm p-1 rounded-md"
                aria-label="بستن کشوی ناوبری"
              >
                ✕
              </button>
            </div>
            <p className="px-3 text-xs font-medium text-ink-muted">بخش‌های فعال</p>
            <NavItems items={PRIMARY_NAV_ITEMS} onNavigate={() => setMobileNavOpen(false)} />
            <details className="mt-2 border-t border-border-subtle pt-3">
              <summary className="cursor-pointer rounded-xl px-3 py-2 text-xs text-ink-muted transition-colors">
                بخش‌های در انتظار قرارداد
              </summary>
              <div className="pt-3"><NavItems onNavigate={() => setMobileNavOpen(false)} /></div>
            </details>

            {/* Mobile-only Unit Toggle & Logout */}
            <div className="mt-2 border-t border-border-subtle pt-4 lg:hidden space-y-4">
              <div>
                <p className="mb-2 px-3 text-xs font-medium text-ink-muted">واحد نمایش مبالغ</p>
                <div className="px-3">
                  <NavLink
                to="/chand"
                className="inline-flex min-h-10 items-center gap-1.5 rounded-xl border border-amber-500/30 bg-amber-500/10 px-3 py-1.5 text-xs font-bold text-amber-600 hover:bg-amber-500/20 transition-colors"
                title="مشاهده نسخه چند؟ با انیمیشن‌های اینترو"
              >
                <span>✨ نسخه «چند؟»</span>
              </NavLink>
                </div>
              </div>

              {session !== null ? (
                <div className="px-3 pt-2">
                  <div className="mb-2 text-xs text-ink-muted">
                    کاربر: <span className="font-semibold text-ink">{session.manager.displayName}</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => void onSignOut()}
                    disabled={signingOut}
                    className="w-full min-h-10 rounded-xl border border-border-subtle px-3.5 py-2 text-xs font-semibold text-danger hover:bg-danger/10 transition-colors flex items-center justify-center gap-2"
                  >
                    <span>{signingOut ? 'در حال خروج…' : 'خروج از حساب'}</span>
                  </button>
                </div>
              ) : null}
            </div>
          </nav>
        </aside>

        <main id="main-content" tabIndex={-1} className="min-w-0 flex-1 p-4 sm:p-6 lg:p-8">
          <div className="mx-auto flex w-full max-w-6xl flex-col gap-6">
            <Outlet />
          </div>
        </main>
      </div>
      <ToastContainer />

      <footer className={cn('border-t border-border-subtle bg-surface-raised px-4 py-4 sm:px-6 transition-colors duration-300', darkMode ? 'dark:border-border-subtle-dark dark:bg-surface-raised-dark' : '')}>
        <div className="mx-auto flex w-full max-w-6xl flex-wrap items-center justify-between gap-3">
          <div className="flex flex-col gap-1">
            {isCalculatorPage ? (
              <p className="text-xs text-ink-muted">نسخه آزمایشی · مبنای ۱۴۰۴ · قواعد ۱۴۰۵ تأییدنشده و غیرفعال</p>
            ) : isPrototypePage ? (
              <p className="text-xs text-ink-muted">ارزیابی کارکنان · دادهٔ ساختگی است · ذخیره‌سازی در پایگاه‌داده با جداسازی سازمان · تصمیم مدیر ثبت و تغییرناپذیر است · وزن‌های مدل و موتور قانونی ۱۴۰۴ پیش‌نویس/در حال بازبینی‌اند و نتیجه مشورتی است.</p>
            ) : isDemoPage ? (
              <p className="text-xs text-ink-muted">چند؟ · نسخه نمایشی ۰٫۱ · مبالغ ساختگی هستند و به قواعد قانونی متصل نیستند. مبنای قانونی بخش اصلی پروژه ۱۴۰۴ است؛ قواعد ۱۴۰۵ تأییدنشده و غیرفعال‌اند.</p>
            ) : <StatutoryBaselineNotice />}
            {!isDemoPage && !isCalculatorPage && <p className="text-xs text-ink-muted">
              این نسخه فقط لایه رابط کاربری است؛ محاسبات مالی در سرویس‌های بک‌اند انجام
              می‌شود و رابط هیچ محاسبه‌ای را بازتولید نمی‌کند.
            </p>}
          </div>
          <div className="flex items-center gap-2">
            <Badge tone="success" className="text-xs py-1 px-3">
              پایه قانونی ۱۴۰۴
            </Badge>
          </div>
        </div>
      </footer>
    </div>
  );
}
