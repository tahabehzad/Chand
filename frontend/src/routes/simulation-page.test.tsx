import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { cleanup, render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import { SimulationPage } from '@/routes/simulation-page';
import type { PayrollResponse } from '@/api/payroll-types';

/**
 * The simulation screen is the product's only screen (ADR-008 v1), so it is
 * tested against the real backend contract: the request it sends, the
 * envelope it reads and the refusal it renders.
 */

const RESPONSE: PayrollResponse = {
  statutory_version: '1404.1',
  rule_set_status: 'VERIFIED',
  is_verified: true,
  engine_version: '0.2.0-payroll-engine',
  calculation_hash: 'a'.repeat(64),
  generated_at: '2026-11-16T08:00:00+00:00',
  rule_year_shamsi: 1404,
  days_in_month: 30,
  primary_tax_posture: 'conservative_inta',
  inputs: {
    gross_monthly_rial: 341_850_120,
    allowances_rial: {
      housing: 9_000_000,
      grocery: 22_000_000,
      marriage: 5_000_000,
      child: 10_390_968,
      continuous_attraction: 40_000_000,
    },
    overtime_hours: 0,
    night_hours: 0,
    continuous_attraction_taxable: false,
  },
  bases: {
    welfare_total_rial: 46_390_968,
    mozd_e_saabet_rial: 295_459_152,
    overtime_divisor: '220.00',
    overtime_pay_rial: 0,
    night_shift_pay_rial: 0,
    total_gross_rial: 341_850_120,
  },
  sso: {
    insurable_wage_rial: 341_850_120,
    insurable_ceiling_rial: 727_367_760,
    sso_insurable_ceiling_applied: false,
    employee_share_7pct_rial: 23_929_508,
    employer_share_20pct_rial: 68_370_024,
    unemployment_fund_3pct_rial: 10_255_504,
  },
  tax_postures: {
    conservative_inta: {
      posture: 'conservative_inta',
      art137_deduction_rial: 6_837_002,
      welfare_allowances_taxable: true,
      taxable_income_rial: 295_013_118,
      income_tax_rial: 5_501_312,
      tax_slabs_applied: ['Slab 2 (10%)'],
      slab_breakdown: [
        { slab: 2, rate: '0.10', taxed_amount_rial: 55_013_118, tax_rial: 5_501_312 },
      ],
      net_rial: 312_419_300,
    },
    court_precedent: {
      posture: 'court_precedent',
      art137_deduction_rial: 23_929_508,
      welfare_allowances_taxable: false,
      taxable_income_rial: 231_529_644,
      income_tax_rial: 0,
      tax_slabs_applied: ['Slab 1 (0%)'],
      slab_breakdown: [],
      net_rial: 317_920_612,
    },
  },
  net_rial: 312_419_300,
  alternate_posture_net_rial: 317_920_612,
  employee_deductions: { employee_sso_7pct_rial: 23_929_508, income_tax_rial: 5_501_312 },
  severance_sanavat: { monthly_accrual_rial: 24_621_596 },
  eydi: {
    annual_gross_rial: 311_729_040,
    at_cap: true,
    monthly_accrual_rial: 25_977_420,
    annual_tax_rial: 7_759_356,
    annual_net_rial: 303_969_684,
  },
  employer_cost: {
    total_monthly_employer_cost_rial: 471_074_664,
    annual_ctc_12month_rial: 5_652_895_968,
    includes_26day_leave_reserve: false,
  },
  rounding_residual_rial: 0,
  provenance: {
    mozd_e_saabet_rial: {
      rule_id: 'LABOUR_LAW_ART_36_NOTE_3_PRECEDENT_3328',
      rule_year_shamsi: 1404,
      formula_ref: 'gross - welfare_allowances (attraction retained)',
    },
    income_tax_rial: {
      rule_id: 'DTA_ART_82_92_137',
      rule_year_shamsi: 1404,
      formula_ref: 'progressive slabs on (gross - art137_deduction - exempt)',
    },
  },
  termination_liability: null,
};

let fetchMock: ReturnType<typeof vi.fn>;

function jsonResponse(body: unknown, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: new Headers({ 'Content-Type': 'application/json', 'X-Request-Id': 'req-test' }),
    json: async () => body,
  };
}

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <SimulationPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

beforeEach(() => {
  fetchMock = vi.fn(async () => jsonResponse(RESPONSE));
  vi.stubGlobal('fetch', fetchMock);
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe('Simulation screen', () => {
  it('sends the documented request to the gross-to-net endpoint', async () => {
    renderPage();
    await userEvent.click(screen.getByRole('button', { name: /اجرای شبیه‌سازی/ }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toContain('/api/v1/simulations/gross-to-net');
    expect(init.method).toBe('POST');
    expect(init.headers).toMatchObject({ 'Content-Type': 'application/json' });

    const body = JSON.parse(String(init.body)) as Record<string, unknown>;
    expect(body.gross_monthly_rial).toBe(300_000_000);
    expect(body.rule_year).toBe(1404);
    expect(body.days_in_month).toBe(30);
    expect(body.tax_posture).toBe('conservative_inta');
  });

  it('sends the edited gross to the backend', async () => {
    renderPage();
    const gross = screen.getByLabelText(/حقوق ناخالص ماهانه/);
    await userEvent.clear(gross);
    await userEvent.type(gross, '123456789');
    await userEvent.click(screen.getByRole('button', { name: /اجرای شبیه‌سازی/ }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    const body = JSON.parse(String(init.body)) as Record<string, unknown>;
    expect(body.gross_monthly_rial).toBe(123_456_789);
  });

  it('renders the net pay, the tax and the rule-set provenance', async () => {
    renderPage();
    await userEvent.click(screen.getByRole('button', { name: /اجرای شبیه‌سازی/ }));

    const results = await screen.findByRole('region', { name: 'نتایج شبیه‌سازی' });
    expect(within(results).getByText(/نسخه قوانین/)).toHaveTextContent('1404.1 (VERIFIED)');
    expect(within(results).getByText(/هش محاسبه/)).toHaveTextContent('aaaaaaaaaaaaaaaa');
    expect(within(results).getAllByText(/۳۱۲٬۴۱۹٬۳۰۰/).length).toBeGreaterThan(0);
    expect(within(results).getAllByText(/۵٬۵۰۱٬۳۱۲/).length).toBeGreaterThan(0);
    expect(within(results).getAllByText(/۲۳٬۹۲۹٬۵۰۸/).length).toBeGreaterThan(0);
    expect(within(results).getAllByText(/۴۷۱٬۰۷۴٬۶۶۴/).length).toBeGreaterThan(0);
    expect(within(results).getAllByText(/۲۴٬۶۲۱٬۵۹۶/).length).toBeGreaterThan(0);
    expect(within(results).getAllByText(/۲۵٬۹۷۷٬۴۲۰/).length).toBeGreaterThan(0);
  });

  it('shows both Article 137 postures side by side', async () => {
    renderPage();
    await userEvent.click(screen.getByRole('button', { name: /اجرای شبیه‌سازی/ }));

    const results = await screen.findByRole('region', { name: 'نتایج شبیه‌سازی' });
    expect(within(results).getByText('محافظه‌کارانه (INTA)')).toBeInTheDocument();
    expect(within(results).getByText('مرجع دیوان')).toBeInTheDocument();
    expect(within(results).getAllByText(/۳۱۷٬۹۲۰٬۶۱۲/).length).toBeGreaterThan(0);
  });

  it('renders the slab breakdown of the primary posture', async () => {
    renderPage();
    await userEvent.click(screen.getByRole('button', { name: /اجرای شبیه‌سازی/ }));

    const results = await screen.findByRole('region', { name: 'نتایج شبیه‌سازی' });
    const tables = within(results).getAllByRole('table');
    const firstTable = tables[0];
    expect(firstTable).toBeDefined();
    expect(firstTable?.querySelectorAll('tbody tr')).toHaveLength(1);
    expect(within(firstTable as HTMLElement).getByText(/پله ۲/)).toBeInTheDocument();
  });

  it('renders the termination block when the response carries one', async () => {
    fetchMock.mockResolvedValue(
      jsonResponse({
        ...RESPONSE,
        termination_liability: {
          probation_months: 3,
          employer_initiated_probation_liability_rial: 150_000_000,
          employee_initiated_probation_liability_rial: null,
          tenure_months: 24,
          exit_severance_rial: 590_918_304,
          leave_carryover_cap_days: 18,
          effective_buyout_days: 12,
          leave_buyout_rial: 118_183_656,
          total_separation_rial: 709_101_960,
        },
      }),
    );
    renderPage();
    await userEvent.click(screen.getByRole('button', { name: /اجرای شبیه‌سازی/ }));

    const results = await screen.findByRole('region', { name: 'نتایج شبیه‌سازی' });
    expect(within(results).getByText('تسویه و پایان خدمت (ماده ۱۱)')).toBeInTheDocument();
    expect(within(results).getAllByText(/۱۵۰٬۰۰۰٬۰۰۰/).length).toBeGreaterThan(0);
    expect(within(results).getAllByText(/۷۰۹٬۱۰۱٬۹۶۰/).length).toBeGreaterThan(0);
  });

  it('surfaces the refusal of the backend instead of a stale result', async () => {
    fetchMock.mockResolvedValue(
      jsonResponse(
        {
          error: {
            code: 'STATUTORY_PARAMETER_UNAVAILABLE',
            detail: 'the rule set is not verified and active',
          },
        },
        422,
      ),
    );
    renderPage();
    await userEvent.click(screen.getByRole('button', { name: /اجرای شبیه‌سازی/ }));

    const alert = await screen.findByRole('alert');
    expect(alert).toHaveTextContent('STATUTORY_PARAMETER_UNAVAILABLE');
    expect(alert).toHaveTextContent('یک مقدار قانونی لازم در دسترس یا تأیید‌شده نیست');
    expect(screen.queryByRole('region', { name: 'نتایج شبیه‌سازی' })).not.toBeInTheDocument();
  });

  it('renders the statutory bases, the insurance block and the field provenance', async () => {
    renderPage();
    await userEvent.click(screen.getByRole('button', { name: /اجرای شبیه‌سازی/ }));

    const results = await screen.findByRole('region', { name: 'نتایج شبیه‌سازی' });
    // The statutory base of severance, Eydi and overtime must be visible:
    // a net pay figure without its base is not auditable.
    expect(within(results).getByText('مزد ثابت (مبنای سنوات و عیدی)')).toBeInTheDocument();
    expect(within(results).getAllByText(/۲۹۵٬۴۵۹٬۱۵۲/).length).toBeGreaterThan(0);
    expect(within(results).getByText('سقف بیمهٔ ماهانه')).toBeInTheDocument();
    expect(within(results).getAllByText(/۷۲۷٬۳۶۷٬۷۶۰/).length).toBeGreaterThan(0);
    expect(within(results).getByText('منشأ هر رقم')).toBeInTheDocument();
    expect(within(results).getByText('DTA_ART_82_92_137')).toBeInTheDocument();
  });

  it('never renders a float as a monetary amount', async () => {
    renderPage();
    await userEvent.click(screen.getByRole('button', { name: /اجرای شبیه‌سازی/ }));
    await screen.findByRole('region', { name: 'نتایج شبیه‌سازی' });
    // A decimal separator in a rendered Rial amount would mean a float
    // reached the screen.
    const text = document.body.textContent ?? '';
    expect(text).not.toMatch(/\d\.\d{2,}\s*ریال/);
  });
});
