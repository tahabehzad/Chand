import { useEffect } from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { Icon } from '@/components/icon';
import { Badge } from '@/components/ui/badge';
import { StatutoryBaselineNotice } from '@/components/layout/statutory-baseline-notice';
import { UnitToggle } from '@/components/layout/unit-toggle';
import { NAV_ITEMS, MVP_NAV_ITEMS, type NavItem } from '@/app/navigation';
import { SessionBridge } from '@/app/session-bridge';
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
                'flex items-start gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors',
                isActive
                  ? 'bg-brand/10 font-semibold text-brand-strong'
                  : 'text-ink-muted hover:bg-surface hover:text-ink',
              )
            }
          >
            {({ isActive }) => (
              <>
                <Icon name={item.icon} className={cn('mt-0.5', isActive && 'text-brand')} />
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
 * The RTL application shell.
 *
 * Direction is not set here: it is declared once in `index.html`. This component
 * uses logical utilities only (`ms-`, `ps-`, `text-start`, `inset-inline-*`), so
 * the sidebar sits at the *start* of the reading direction — the right-hand side
 * of an RTL document — without a single physical override.
 */
export function AppShell() {
  const { pathname } = useLocation();
  const isDemoPage = ['/', '/transactions', '/settings'].includes(pathname);
  const mobileNavOpen = useUiStore((state) => state.mobileNavOpen);
  const setMobileNavOpen = useUiStore((state) => state.setMobileNavOpen);

  useEffect(() => {
    if (!mobileNavOpen) return undefined;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setMobileNavOpen(false);
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [mobileNavOpen, setMobileNavOpen]);

  return (
    <div className="flex min-h-screen flex-col bg-surface-muted">
      <SessionBridge />
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:start-2 focus:z-50 focus:rounded-lg focus:bg-brand focus:px-4 focus:py-2 focus:text-white"
      >
        پرش به محتوای اصلی
      </a>

      <header className="sticky top-0 z-30 border-b border-border-subtle bg-surface-raised">
        <div className="flex items-center gap-3 px-4 py-3 sm:px-6">
          <button
            type="button"
            onClick={() => setMobileNavOpen(!mobileNavOpen)}
            aria-expanded={mobileNavOpen}
            aria-controls="primary-navigation"
            aria-label={mobileNavOpen ? 'بستن منو' : 'باز کردن منو'}
            className="inline-flex min-h-10 min-w-10 items-center justify-center rounded-lg border border-border-subtle text-ink-muted lg:hidden"
          >
            <Icon name={mobileNavOpen ? 'close' : 'menu'} />
          </button>

          <div className="flex min-w-0 flex-col">
            <span className="truncate text-base font-semibold text-ink">پیش‌حسابداری</span>
            <span className="truncate text-xs text-ink-muted">
              فضای ساده مدیریت مالی · نسخه نمونه
            </span>
          </div>

          <div className="ms-auto flex items-center gap-3">
            <Badge tone="info">
              داده‌های نمایشی
            </Badge>
            <div className="hidden sm:block">
              <UnitToggle />
            </div>
          </div>
        </div>
      </header>

      <div className="flex flex-1 flex-col lg:flex-row">
        <aside
          id="primary-navigation"
          className={cn(
            'border-border-subtle bg-surface-raised p-4 lg:block lg:w-60 lg:shrink-0 lg:border-e',
            // Below the desktop breakpoint the panel is a dialog-like drawer.
            mobileNavOpen ? 'block border-b' : 'hidden',
          )}
        >
          <nav aria-label="ناوبری اصلی" className="flex flex-col gap-4">
            <p className="px-3 text-xs font-medium text-ink-muted">فضای کاری نمونه</p>
            <NavItems items={MVP_NAV_ITEMS} onNavigate={() => setMobileNavOpen(false)} />
            <div className="mx-3 mt-6 rounded-xl border border-border-subtle bg-surface-muted p-3">
              <p className="text-sm font-medium">پیش‌حسابداری ۰٫۱</p>
              <p className="mt-2 text-xs text-ink-muted">یک شروع کوچک برای تصویری روشن از امور مالی.</p>
            </div>
            <details className="mt-4 border-t border-border-subtle pt-4">
              <summary className="cursor-pointer rounded px-3 py-2 text-xs text-ink-muted">بخش‌های پیشین پروژه</summary>
              <div className="pt-3"><NavItems onNavigate={() => setMobileNavOpen(false)} /></div>
            </details>
            <div className="mt-2 border-t border-border-subtle pt-4 lg:hidden">
              <p className="mb-2 px-3 text-xs font-medium text-ink-muted">واحد نمایش مبالغ</p>
              <div className="px-3">
                <UnitToggle />
              </div>
            </div>
          </nav>
        </aside>

        <main id="main-content" tabIndex={-1} className="min-w-0 flex-1 p-4 sm:p-6 lg:p-8">
          <div className="mx-auto flex w-full max-w-6xl flex-col gap-6">
            <Outlet />
          </div>
        </main>
      </div>

      <footer className="border-t border-border-subtle bg-surface-raised px-4 py-4 sm:px-6">
        <div className="mx-auto flex w-full max-w-6xl flex-col gap-2">
          {isDemoPage ? (
            <p className="text-xs text-ink-muted">پیش‌حسابداری · نسخه نمایشی ۰٫۱ · مبالغ ساختگی هستند و به قواعد قانونی متصل نیستند. مبنای قانونی بخش اصلی پروژه ۱۴۰۴ است؛ قواعد ۱۴۰۵ تأییدنشده و غیرفعال‌اند.</p>
          ) : <StatutoryBaselineNotice />}
          {!isDemoPage && <p className="text-xs text-ink-muted">
            این نسخه فقط لایه رابط کاربری است؛ محاسبات مالی در سرویس‌های بک‌اند انجام
            می‌شود و رابط هیچ محاسبه‌ای را بازتولید نمی‌کند.
          </p>}
        </div>
      </footer>
    </div>
  );
}
