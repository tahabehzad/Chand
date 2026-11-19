/**
 * Total Cost to Employer (CTC) & Net Pay Breakdown Panel — Persian RTL.
 *
 * Visualizes the complete financial journey of a monthly salary under Iranian labor law:
 *   1. Gross -> minus employee SSO (7%) and income tax -> Net take-home pay.
 *   2. Plus employer SSO (20%), unemployment (3%), monthly severance, and monthly bonus -> Total Cost to Employer (CTC).
 *   3. Stacked horizontal bar chart showing % Net vs % Deductions vs % Employer overhead.
 *   4. All numbers formatted in Toman via `formatMoney()` from `@/lib/money.ts`.
 *
 * Authority: ADR-014, WBS P4-T03.
 */

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatMoney } from '@/lib/money';
import { toPersianDigits } from '@/lib/numerals';
import { apiClient } from '@/api/instance';
import {
  getSalaryCtcBreakdown,
  type SalaryCtcBreakdownResponse,
} from '@/api/salary-estimation';

export type CtcBreakdownProps = {
  grossSalaryRial: number;
  onLoaded?: (data: SalaryCtcBreakdownResponse) => void;
  className?: string;
};

function formatToman(rialValue: number): string {
  const roundedTo10 = Math.round(rialValue / 10) * 10;
  const toman = formatMoney(roundedTo10, 'toman');
  if (toman.ok) return toman.value.text;
  return `${toPersianDigits(String(Math.round(rialValue / 10)))} تومان`;
}

/**
 * Fallback computation for offline demo or mock states when backend simulation is uncontactable.
 * Follows exact statutory formulas for 1404.
 */
function computeOfflineFallback(grossRial: number): SalaryCtcBreakdownResponse {
  // 1404 daily minimum: 2,388,728 Rial -> 30-day ceiling: 7 * 2388728 * 30 = 501,632,880 Rial
  const ceiling = 501_632_880;
  const insurable = Math.min(grossRial, ceiling);

  const employeeSso = Math.round(insurable * 0.07);
  const employerSso = Math.round(insurable * 0.20);
  const unemployment = Math.round(insurable * 0.03);

  // Article 137: 2/7 of employee SSO is tax-deductible
  const art137 = Math.round(employeeSso * (2 / 7));
  const taxable = Math.max(0, grossRial - art137);
  // Monthly exemption: 200,000,000 Rial
  const taxExemption = 200_000_000;
  let tax = 0;
  if (taxable > taxExemption) {
    const excess = taxable - taxExemption;
    // 10% slab up to 100M excess
    if (excess <= 100_000_000) {
      tax = Math.round(excess * 0.10);
    } else {
      tax = Math.round(100_000_000 * 0.10 + (excess - 100_000_000) * 0.15);
    }
  }

  const monthlySeverance = Math.round(grossRial / 12);
  // Eydi: min(2 * gross, 3 * monthly min)
  const maxEydi = 71_661_840 * 3;
  const annualEydi = Math.min(grossRial * 2, maxEydi);
  const monthlyEydi = Math.round(annualEydi / 12);

  const totalDeductions = employeeSso + tax;
  const netSalary = Math.max(0, grossRial - totalDeductions);
  const totalEmployerCosts = employerSso + unemployment + monthlySeverance + monthlyEydi;
  const totalCtc = grossRial + totalEmployerCosts;

  return {
    gross_salary_rial: grossRial,
    net_salary_rial: netSalary,
    deductions: {
      employee_sso_rial: employeeSso,
      income_tax_rial: tax,
      total_deductions_rial: totalDeductions,
    },
    employer_costs: {
      employer_sso_rial: employerSso,
      unemployment_rial: unemployment,
      monthly_severance_rial: monthlySeverance,
      monthly_eydi_rial: monthlyEydi,
      total_employer_costs_rial: totalEmployerCosts,
    },
    total_cost_to_employer_rial: totalCtc,
    annual_cost_to_employer_rial: totalCtc * 12,
    rule_version: '1404.1',
    engine_version: '0.1.0-ctc',
    calculation_hash: 'ctc_fallback_' + Math.abs(grossRial).toString(16),
    generated_at: new Date().toISOString(),
  };
}

export function CtcBreakdown({ grossSalaryRial, onLoaded, className = '' }: CtcBreakdownProps) {
  const [data, setData] = useState<SalaryCtcBreakdownResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!grossSalaryRial || grossSalaryRial <= 0) {
      setData(null);
      return;
    }

    let isMounted = true;
    setIsLoading(true);
    setError(null);

    getSalaryCtcBreakdown(apiClient, {
      gross_salary_rial: grossSalaryRial,
      year: 1404,
      month_days: 30,
    })
      .then((res) => {
        if (!isMounted) return;
        setData(res);
        onLoaded?.(res);
      })
      .catch((err) => {
        if (!isMounted) return;
        // Graceful fallback to pure statutory calculation if network/mock API unavailable
        const fallback = computeOfflineFallback(grossSalaryRial);
        setData(fallback);
        onLoaded?.(fallback);
        if (err instanceof Error && err.name !== 'ContractUnavailableError') {
          setError(err.message);
        }
      })
      .finally(() => {
        if (isMounted) setIsLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [grossSalaryRial, onLoaded]);

  if (!grossSalaryRial || grossSalaryRial <= 0) {
    return null;
  }

  if (error && !data) {
    return (
      <Card className={`border border-danger/20 bg-danger/5 p-4 text-xs text-danger ${className}`}>
        خطا در دریافت محاسبه هزینه کارفرما: {error}
      </Card>
    );
  }

  if (isLoading && !data) {
    return (
      <Card className={`border border-border-subtle bg-surface animate-pulse p-6 ${className}`}>
        <div className="h-6 w-48 bg-surface-muted rounded mb-4" />
        <div className="h-24 bg-surface-muted rounded" />
      </Card>
    );
  }

  if (!data) return null;

  // Percentage calculations relative to Total Cost to Employer (CTC)
  const totalCtc = data.total_cost_to_employer_rial || 1;
  const net = data.net_salary_rial;
  const deductions = data.deductions.total_deductions_rial;
  const overhead = data.employer_costs.total_employer_costs_rial;

  const netPercent = totalCtc > 0 ? Math.round((net / totalCtc) * 100) : 0;
  const deductionsPercent = totalCtc > 0 ? Math.round((deductions / totalCtc) * 100) : 0;
  const overheadPercent = totalCtc > 0 ? Math.max(0, 100 - netPercent - deductionsPercent) : 0;

  return (
    <Card className={`overflow-hidden border border-border-subtle bg-surface shadow-md print-avoid-break ${className}`}>
      {/* Top Gradient Banner */}
      <div className="h-1.5 w-full bg-gradient-to-r from-brand via-accent-teal to-purple-600" />

      <CardHeader className="pb-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <span className="flex size-9 items-center justify-center rounded-xl bg-purple-500/10 text-purple-600 font-bold text-base" aria-hidden="true">
              🏢
            </span>
            <div>
              <CardTitle className="text-lg font-bold text-ink">
                تفکیک هزینه کل کارفرما (CTC) و خالص پرداختی
              </CardTitle>
              <p className="text-xs text-ink-muted mt-0.5">
                محاسبهٔ دقیق بیمه، مالیات، سنوات و عیدی بر پایهٔ قوانین کار و تأمین اجتماعی ۱۴۰۴
              </p>
            </div>
          </div>
          <Badge tone="neutral" className="text-xs font-mono">
            مبنا: قانون کار ۱۴۰۴
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Top 3 KPI Hero Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {/* Net Take-Home */}
          <div className="rounded-2xl border border-accent-emerald/20 bg-accent-emerald/5 p-4 text-center transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md hover:border-accent-emerald/40">
            <span className="text-xs font-semibold text-accent-emerald-dark dark:text-accent-emerald flex items-center justify-center gap-1.5">
              <span aria-hidden="true">💳</span>
              <span>خالص دریافتی کارمند</span>
            </span>
            <div className="mt-1.5 text-lg sm:text-xl font-black text-ink">
              {formatToman(data.net_salary_rial)}
            </div>
            <span className="text-[11px] text-ink-muted block mt-0.5">
              واریزی ماهانه به حساب
            </span>
          </div>

          {/* Gross Agreed Salary */}
          <div className="rounded-2xl border border-brand/20 bg-brand/5 p-4 text-center transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md hover:border-brand/40">
            <span className="text-xs font-semibold text-brand flex items-center justify-center gap-1.5">
              <span aria-hidden="true">📝</span>
              <span>حقوق ناخالص توافقی</span>
            </span>
            <div className="mt-1.5 text-lg sm:text-xl font-black text-ink">
              {formatToman(data.gross_salary_rial)}
            </div>
            <span className="text-[11px] text-ink-muted block mt-0.5">
              مبلغ مندرج در قرارداد
            </span>
          </div>

          {/* Total CTC */}
          <div className="rounded-2xl border border-purple-500/20 bg-purple-500/5 p-4 text-center transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md hover:border-purple-500/40">
            <span className="text-xs font-semibold text-purple-700 dark:text-purple-400 flex items-center justify-center gap-1.5">
              <span aria-hidden="true">🏢</span>
              <span>هزینه کل کارفرما (CTC)</span>
            </span>
            <div className="mt-1.5 text-lg sm:text-xl font-black text-purple-950 dark:text-purple-200">
              {formatToman(data.total_cost_to_employer_rial)}
            </div>
            <span className="text-[11px] text-ink-muted block mt-0.5">
              مجموع تعهد ماهانه شرکت
            </span>
          </div>
        </div>

        {/* Stacked Horizontal Bar Chart (% Net vs % Deductions vs % Employer Overhead) */}
        <div className="space-y-2 rounded-2xl bg-surface-raised p-4 border border-border-subtle">
          <div className="flex items-center justify-between text-xs">
            <span className="font-bold text-ink">ترکیب هزینه کل (۱۰۰٪ CTC)</span>
            <span className="text-ink-muted text-[11px]">
              سالانه: {formatToman(data.annual_cost_to_employer_rial)}
            </span>
          </div>

          {/* Pure CSS/Tailwind Horizontal Bar */}
          <div className="flex h-5 w-full overflow-hidden rounded-xl bg-surface-muted p-0.5 gap-0.5">
            {/* Net Share (Emerald) */}
            <div
              style={{ width: `${netPercent}%` }}
              className="h-full bg-accent-emerald rounded-s-lg transition-all duration-500 flex items-center justify-center text-[10px] font-bold text-white overflow-hidden"
              title={`خالص کارمند: ${toPersianDigits(String(netPercent))}٪`}
            >
              {netPercent > 12 ? `${toPersianDigits(String(netPercent))}٪` : ''}
            </div>

            {/* Deductions Share (Amber) */}
            <div
              style={{ width: `${deductionsPercent}%` }}
              className="h-full bg-amber-500 transition-all duration-500 flex items-center justify-center text-[10px] font-bold text-white overflow-hidden"
              title={`کسورات کارمند: ${toPersianDigits(String(deductionsPercent))}٪`}
            >
              {deductionsPercent > 12 ? `${toPersianDigits(String(deductionsPercent))}٪` : ''}
            </div>

            {/* Employer Overhead Share (Purple) */}
            <div
              style={{ width: `${overheadPercent}%` }}
              className="h-full bg-purple-600 rounded-e-lg transition-all duration-500 flex items-center justify-center text-[10px] font-bold text-white overflow-hidden"
              title={`بالاسری کارفرما: ${toPersianDigits(String(overheadPercent))}٪`}
            >
              {overheadPercent > 12 ? `${toPersianDigits(String(overheadPercent))}٪` : ''}
            </div>
          </div>

          {/* Bar Chart Legend */}
          <div className="flex flex-wrap items-center justify-between gap-2 pt-1 text-xs">
            <div className="flex items-center gap-1.5">
              <span className="size-2.5 rounded-full bg-accent-emerald" />
              <span className="text-ink font-medium">خالص پرداختی:</span>
              <span className="text-ink-muted">{toPersianDigits(String(netPercent))}٪ ({formatToman(net)})</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="size-2.5 rounded-full bg-amber-500" />
              <span className="text-ink font-medium">کسورات قانونی کارمند:</span>
              <span className="text-ink-muted">{toPersianDigits(String(deductionsPercent))}٪ ({formatToman(deductions)})</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="size-2.5 rounded-full bg-purple-600" />
              <span className="text-ink font-medium">بالاسری کارفرما:</span>
              <span className="text-ink-muted">{toPersianDigits(String(overheadPercent))}٪ ({formatToman(overhead)})</span>
            </div>
          </div>
        </div>

        {/* Detailed 2-Column Itemized Breakdown */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Column 1: Gross -> Deductions -> Net */}
          <div className="rounded-2xl border border-border-subtle bg-surface-raised p-4 space-y-3">
            <div className="flex items-center gap-2 border-b border-border-subtle pb-2.5">
              <span className="size-2 rounded-full bg-amber-500" />
              <h4 className="text-sm font-bold text-ink">
                ۱. کسورات قانونی از حقوق ناخالص
              </h4>
            </div>

            <dl className="space-y-2 text-xs">
              <div className="flex justify-between py-1">
                <dt className="text-ink-muted">حقوق ناخالص توافقی</dt>
                <dd className="font-semibold text-ink">{formatToman(data.gross_salary_rial)}</dd>
              </div>

              <div className="flex justify-between py-1 text-danger">
                <dt className="flex items-center gap-1">
                  <span>➖ بیمه تأمین اجتماعی سهم کارمند (۷٪)</span>
                </dt>
                <dd className="font-mono font-semibold">
                  {formatToman(data.deductions.employee_sso_rial)}
                </dd>
              </div>

              <div className="flex justify-between py-1 text-danger">
                <dt className="flex items-center gap-1">
                  <span>➖ مالیات بر درآمد حقوق (ماده ۸۴ و ۱۳۷)</span>
                </dt>
                <dd className="font-mono font-semibold">
                  {formatToman(data.deductions.income_tax_rial)}
                </dd>
              </div>

              <div className="border-t border-dashed border-border-subtle pt-2 flex justify-between font-bold text-ink">
                <dt>مجموع کسورات ماهانه</dt>
                <dd className="text-danger font-mono">
                  {formatToman(data.deductions.total_deductions_rial)}
                </dd>
              </div>

              <div className="rounded-xl bg-accent-emerald/10 border border-accent-emerald/20 p-2.5 mt-2 flex justify-between items-center text-accent-emerald-dark dark:text-accent-emerald font-bold">
                <dt className="text-xs">خالص واریزی ماهانه به کارمند</dt>
                <dd className="text-sm font-black">{formatToman(data.net_salary_rial)}</dd>
              </div>
            </dl>
          </div>

          {/* Column 2: Gross + Employer Overhead -> Total CTC */}
          <div className="rounded-2xl border border-border-subtle bg-surface-raised p-4 space-y-3">
            <div className="flex items-center gap-2 border-b border-border-subtle pb-2.5">
              <span className="size-2 rounded-full bg-purple-600" />
              <h4 className="text-sm font-bold text-ink">
                ۲. تعهدات و بالاسری کارفرما (مازاد بر ناخالص)
              </h4>
            </div>

            <dl className="space-y-2 text-xs">
              <div className="flex justify-between py-1 text-purple-700 dark:text-purple-400">
                <dt className="flex items-center gap-1">
                  <span>➕ حق بیمه تأمین اجتماعی سهم کارفرما (۲۰٪)</span>
                </dt>
                <dd className="font-mono font-semibold">
                  {formatToman(data.employer_costs.employer_sso_rial)}
                </dd>
              </div>

              <div className="flex justify-between py-1 text-purple-700 dark:text-purple-400">
                <dt className="flex items-center gap-1">
                  <span>➕ بیمه بیکاری سهم کارفرما (۳٪)</span>
                </dt>
                <dd className="font-mono font-semibold">
                  {formatToman(data.employer_costs.unemployment_rial)}
                </dd>
              </div>

              <div className="flex justify-between py-1 text-purple-700 dark:text-purple-400">
                <dt className="flex items-center gap-1">
                  <span>➕ ذخیره ماهانه سنوات خدمت (۱/۱۲ ناخالص)</span>
                </dt>
                <dd className="font-mono font-semibold">
                  {formatToman(data.employer_costs.monthly_severance_rial)}
                </dd>
              </div>

              <div className="flex justify-between py-1 text-purple-700 dark:text-purple-400">
                <dt className="flex items-center gap-1">
                  <span>➕ ذخیره ماهانه عیدی و پاداش (۱/۱۲ سالانه)</span>
                </dt>
                <dd className="font-mono font-semibold">
                  {formatToman(data.employer_costs.monthly_eydi_rial)}
                </dd>
              </div>

              <div className="border-t border-dashed border-border-subtle pt-2 flex justify-between font-bold text-ink">
                <dt>مجموع بالاسری ماهانه کارفرما</dt>
                <dd className="text-purple-700 dark:text-purple-400 font-mono">
                  {formatToman(data.employer_costs.total_employer_costs_rial)}
                </dd>
              </div>

              <div className="rounded-xl bg-purple-600/10 border border-purple-600/20 p-2.5 mt-2 flex justify-between items-center text-purple-950 dark:text-purple-200 font-bold">
                <dt className="text-xs">هزینه کل ماهانه کارفرما (CTC)</dt>
                <dd className="text-sm font-black">{formatToman(data.total_cost_to_employer_rial)}</dd>
              </div>
            </dl>
          </div>
        </div>

        {/* Verification and Audit metadata */}
        <div className="flex flex-wrap items-center justify-between gap-2 border-t border-border-subtle pt-3 text-[11px] text-ink-muted">
          <div className="flex items-center gap-2">
            <span>نسخه قانون: {data.rule_version}</span>
            <span>·</span>
            <span>موتور محاسباتی: {data.engine_version}</span>
          </div>
          <div className="font-mono text-[10px] bg-surface-muted px-2 py-0.5 rounded border border-border-subtle">
            هش محاسبه: {data.calculation_hash.slice(0, 16)}...
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
