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

function renderMvp(initialEntry = '/') {
  render(<MemoryRouter initialEntries={[initialEntry]}><Routes><Route element={<AppShell />}><Route index element={<OverviewPage />} /><Route path="settings" element={<SettingsPage />} /><Route path="transactions" element={<TransactionsPage />} /></Route></Routes></MemoryRouter>);
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

  it('shows toman amounts on dashboard when unit preference is toman', () => {
    useUiStore.setState({ preferredUnit: 'toman' });
    renderMvp();
    const summary = screen.getByRole('region', { name: 'خلاصه مالی نمونه' });
    expect(within(summary).getByText('۴۸٬۰۰۰٬۰۰۰ تومان')).toBeInTheDocument();
    expect(within(summary).getByText('۱۸٬۵۰۰٬۰۰۰ تومان')).toBeInTheDocument();
    expect(within(summary).getByText('۲۹٬۵۰۰٬۰۰۰ تومان')).toBeInTheDocument();
  });

  it('closes the mobile navigation after choosing a page and on Escape', async () => {
    renderMvp('/settings');
    await userEvent.click(screen.getByRole('button', { name: 'باز کردن منو' }));
    await userEvent.click(within(screen.getByRole('navigation')).getByRole('link', { name: 'تراکنش‌ها' }));
    expect(screen.getByRole('button', { name: 'باز کردن منو' })).toHaveAttribute('aria-expanded', 'false');
    await userEvent.click(screen.getByRole('button', { name: 'باز کردن منو' }));
    await userEvent.keyboard('{Escape}');
    expect(screen.getByRole('button', { name: 'باز کردن منو' })).toHaveAttribute('aria-expanded', 'false');
  });
});
