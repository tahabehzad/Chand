import { afterEach, describe, expect, it } from 'vitest';
import { cleanup, render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { AppShell } from './app-shell';
import OverviewPage from '@/routes/overview-page';
import SettingsPage from '@/routes/settings-page';
import TransactionsPage from '@/routes/transactions-page';
import { useUiStore } from '@/state/ui-store';

afterEach(() => {
  cleanup();
  useUiStore.setState({ mobileNavOpen: false, preferredUnit: 'rial' });
});

function renderMvp() {
  render(<MemoryRouter><Routes><Route element={<AppShell />}><Route index element={<OverviewPage />} /><Route path="settings" element={<SettingsPage />} /><Route path="transactions" element={<TransactionsPage />} /></Route></Routes></MemoryRouter>);
}

describe('MVP demo', () => {
  it('shows explicitly synthetic summary, chart and matching transaction amounts', () => {
    renderMvp();
    expect(screen.getByRole('heading', { name: 'داشبورد مالی' })).toBeInTheDocument();
    expect(screen.getByText(/تمام مبالغ و تراکنش‌ها ساختگی/)).toBeInTheDocument();
    const summary = screen.getByRole('region', { name: 'خلاصه مالی نمونه' });
    expect(within(summary).getByText('۴۸۰٬۰۰۰٬۰۰۰ ریال')).toBeInTheDocument();
    expect(within(summary).getByText('۱۸۵٬۰۰۰٬۰۰۰ ریال')).toBeInTheDocument();
    expect(within(summary).getByText('۲۹۵٬۰۰۰٬۰۰۰ ریال')).toBeInTheDocument();
    expect(screen.getByRole('img', { name: /مقایسه درآمد و هزینه نمونه/ })).toBeInTheDocument();
    expect(screen.getByRole('table', { name: /تراکنش‌های ساختگی/ }).querySelectorAll('tbody tr')).toHaveLength(5);
  });

  it('navigates to settings and changes the display unit across pages', async () => {
    renderMvp();
    const nav = screen.getByRole('navigation', { name: 'ناوبری اصلی' });
    await userEvent.click(within(nav).getByRole('link', { name: 'تنظیمات' }));
    expect(screen.getByRole('heading', { level: 1, name: 'تنظیمات' })).toBeInTheDocument();
    const main = screen.getByRole('main');
    await userEvent.click(within(main).getByRole('button', { name: 'تومان' }));
    await userEvent.click(within(nav).getByRole('link', { name: 'تراکنش‌ها' }));
    expect(screen.getByRole('heading', { name: 'تراکنش‌های نمونه' })).toBeInTheDocument();
    expect(screen.getByText('۳۰٬۰۰۰٬۰۰۰ تومان')).toBeInTheDocument();
    await userEvent.click(within(nav).getByRole('link', { name: 'داشبورد' }));
    expect(within(screen.getByRole('region', { name: 'خلاصه مالی نمونه' })).getByText('۴۸٬۰۰۰٬۰۰۰ تومان')).toBeInTheDocument();
  });

  it('closes the mobile navigation after choosing a page and on Escape', async () => {
    renderMvp();
    await userEvent.click(screen.getByRole('button', { name: 'باز کردن منو' }));
    await userEvent.click(within(screen.getByRole('navigation')).getByRole('link', { name: 'تراکنش‌ها' }));
    expect(screen.getByRole('button', { name: 'باز کردن منو' })).toHaveAttribute('aria-expanded', 'false');
    await userEvent.click(screen.getByRole('button', { name: 'باز کردن منو' }));
    await userEvent.keyboard('{Escape}');
    expect(screen.getByRole('button', { name: 'باز کردن منو' })).toHaveAttribute('aria-expanded', 'false');
  });
});
