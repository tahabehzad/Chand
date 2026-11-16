import { afterEach, describe, expect, it } from 'vitest';
import { cleanup, render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { AppShell } from './app-shell';
import { NAV_ITEMS, PRIMARY_NAV_ITEMS } from './navigation';
import { useUiStore } from '@/state/ui-store';

function renderShell(path = '/') {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/" element={<AppShell />}>
          <Route index element={<h1>محتوای آزمون</h1>} />
          <Route path="*" element={<h1>محتوای آزمون</h1>} />
        </Route>
      </Routes>
    </MemoryRouter>,
  );
}

afterEach(() => {
  cleanup();
  useUiStore.setState({ mobileNavOpen: false, preferredUnit: 'rial', sessionExpired: false });
});

describe('AppShell', () => {
  it('provides the core RTL landmarks', () => {
    renderShell();
    expect(screen.getByRole('banner')).toBeInTheDocument();
    expect(screen.getByRole('navigation', { name: 'ناوبری اصلی' })).toBeInTheDocument();
    expect(screen.getByRole('main')).toBeInTheDocument();
    expect(screen.getByRole('contentinfo')).toBeInTheDocument();
  });

  it('offers a skip link to the main region', () => {
    renderShell();
    const skip = screen.getByRole('link', { name: 'پرش به محتوای اصلی' });
    expect(skip).toHaveAttribute('href', '#main-content');
    expect(screen.getByRole('main')).toHaveAttribute('id', 'main-content');
  });

  it('links every primary screen directly in the main navigation', () => {
    renderShell();
    const nav = screen.getByRole('navigation', { name: 'ناوبری اصلی' });
    for (const item of PRIMARY_NAV_ITEMS) {
      expect(within(nav).getByRole('link', { name: new RegExp(item.labelFa) })).toHaveAttribute(
        'href',
        item.path,
      );
    }
  });

  it('offers the delivered statutory simulation in the primary navigation', () => {
    renderShell();
    const nav = screen.getByRole('navigation', { name: 'ناوبری اصلی' });
    const link = within(nav).getByRole('link', { name: /شبیه‌سازی حقوق/ });
    expect(link).toHaveAttribute('href', '/simulation');
  });

  it('links every deferred module in the collapsed section', async () => {
    renderShell();
    await userEvent.click(screen.getByText('بخش‌های در انتظار قرارداد'));
    const nav = screen.getByRole('navigation', { name: 'ناوبری اصلی' });
    for (const item of NAV_ITEMS) {
      expect(within(nav).getByRole('link', { name: new RegExp(item.labelFa) })).toHaveAttribute(
        'href',
        item.path,
      );
    }
  });

  it('never links two navigation entries to the same path', () => {
    const paths = [...PRIMARY_NAV_ITEMS, ...NAV_ITEMS].map((item) => item.path);
    expect(new Set(paths).size).toBe(paths.length);
  });

  it('marks the active module with aria-current', () => {
    renderShell('/simulation');
    const nav = screen.getByRole('navigation', { name: 'ناوبری اصلی' });
    const link = within(nav).getByRole('link', { name: /شبیه‌سازی حقوق/ });
    expect(link).toHaveAttribute('aria-current', 'page');
  });

  it('labels the statutory screen with its baseline and the demo with its notice', () => {
    const { unmount } = renderShell('/simulation');
    expect(screen.getByRole('banner')).toHaveTextContent('پایه قانونی ۱۴۰۴');
    expect(screen.getByRole('banner')).not.toHaveTextContent('داده‌های نمایشی');
    unmount();
    renderShell('/');
    expect(screen.getByRole('banner')).toHaveTextContent('داده‌های نمایشی');
  });

  it('discloses the statutory baseline in the footer', () => {
    renderShell();
    const footer = screen.getByRole('contentinfo');
    expect(footer).toHaveTextContent('۱۴۰۴');
    expect(footer).toHaveTextContent('تأییدنشده');
  });

  it('toggles the mobile drawer through an announced control', async () => {
    renderShell();
    const toggle = screen.getByRole('button', { name: 'باز کردن منو' });
    expect(toggle).toHaveAttribute('aria-expanded', 'false');
    await userEvent.click(toggle);
    const close = screen.getByRole('button', { name: 'بستن منو' });
    expect(close).toHaveAttribute('aria-expanded', 'true');
    expect(screen.getByRole('navigation', { name: 'ناوبری اصلی' })).toBeInTheDocument();
  });

  it('does not render a sign-in or session surface inside the shell', () => {
    renderShell();
    expect(screen.queryByRole('form')).toBeNull();
    expect(screen.queryByText('گذرواژه')).toBeNull();
  });
});
