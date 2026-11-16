import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Icon } from '@/components/icon';
import { CONTRACTS } from '@/api/contracts';
import { apiClient } from '@/api/instance';
import { formatMoney, formatPercentFromRate } from '@/lib/money';
import { toPersianDigits } from '@/lib/numerals';
import { isApiError } from '@/api/errors';
import type { GrossToNetRequest, PayrollResponse, TaxPosture } from '@/api/payroll-types';

/**
 * The optional liability inputs are genuinely optional: an empty field means
 * "not supplied", which the backend contract represents as `null`.  They must
 * never be seeded with `0`: the probation field's minimum is one month, so a
 * `0` would fail the browser's own constraint validation and silently block
 * every submission.
 */
const OPTIONAL_NUMERIC_FIELDS = [
  'probation_months',
  'tenure_months',
  'accumulated_unused_leave_days',
] as const;

/**
 * Render a whole-Rial amount with the project numeral policy (SPEC-FE-001
 * §4.2): Persian digits, the Persian thousands separator and no fractional
 * Rial.  A value that is not a safe integer is refused rather than rounded.
 */
function rialAmount(value: number): string {
  const formatted = formatMoney(value, 'rial');
  return formatted.ok ? formatted.value.amount : '—';
}

/** Render the Persian label of one tax band, with the rate the backend applied. */
function slabLabel(slab: number, rate: string): string {
  const percent = formatPercentFromRate(rate);
  const slabNumber = toPersianDigits(String(slab));
  return percent ? `پله ${slabNumber} (${percent})` : `پله ${slabNumber}`;
}

function PostureCard({ title, posture, netRial, taxRial, deductionRial, welfareTaxable, slabs }: {
  title: string;
  posture: TaxPosture;
  netRial: number;
  taxRial: number;
  deductionRial: number;
  welfareTaxable: boolean;
  slabs: { label: string; taxed: number; tax: number }[];
}) {
  const isConservative = posture === 'conservative_inta';
  return (
    <Card className='w-full'>
      <CardHeader className='flex-row items-center justify-between border-0 pb-2'>
        <CardTitle className='text-lg'>{title}</CardTitle>
        <Badge tone={isConservative ? 'info' : 'neutral'}>
          {isConservative ? 'محافظه‌کارانه (INTA)' : 'مرجع دیوان'}
        </Badge>
      </CardHeader>
      <CardContent className='space-y-3'>
        <div className='grid gap-3 sm:grid-cols-2'>
          <div className='rounded-lg border border-border-subtle bg-surface p-3'>
            <p className='text-xs text-ink-muted'>خالص دریافتی</p>
            <p className='text-2xl font-semibold tabular-nums'>{rialAmount(netRial)} <span className='text-sm font-normal text-ink-muted'>ریال</span></p>
          </div>
          <div className='rounded-lg border border-border-subtle bg-surface p-3'>
            <p className='text-xs text-ink-muted'>مالیات بر درآمد</p>
            <p className='text-xl font-semibold tabular-nums text-destructive'>{rialAmount(taxRial)} <span className='text-sm font-normal text-ink-muted'>ریال</span></p>
          </div>
          <div className='rounded-lg border border-border-subtle bg-surface p-3'>
            <p className='text-xs text-ink-muted'>کسر ماده ۱۳۷</p>
            <p className='text-xl font-semibold tabular-nums'>{rialAmount(deductionRial)} <span className='text-sm font-normal text-ink-muted'>ریال</span></p>
          </div>
          <div className='rounded-lg border border-border-subtle bg-surface p-3'>
            <p className='text-xs text-ink-muted'>حقوق رفاهی مشمول مالیات</p>
            <Badge tone={welfareTaxable ? 'danger' : 'neutral'} className='text-base'>
              {welfareTaxable ? 'بله' : 'خیر'}
            </Badge>
          </div>
        </div>
        <div className='rounded-lg border border-border-subtle bg-surface p-3'>
          <p className='mb-2 text-xs font-medium text-ink-muted'>ردیف‌های مالیات (اسلاب‌ها)</p>
          <div className='overflow-x-auto'>
            <table className='w-full text-sm text-start'>
              <thead>
                <tr className='border-b border-border-subtle'>
                  <th className='pb-2 text-ink-muted'>ردیف</th>
                  <th className='pb-2 text-ink-muted'>مبلغ مشمول (ریال)</th>
                  <th className='pb-2 text-ink-muted'>مالیات (ریال)</th>
                </tr>
              </thead>
              <tbody>
                {slabs.map((s, i) => (
                  <tr key={i} className='border-b border-border-subtle/50 last:border-0'>
                    <td className='py-1'>{s.label}</td>
                    <td className='py-1 tabular-nums'>{rialAmount(s.taxed)}</td>
                    <td className='py-1 tabular-nums'>{rialAmount(s.tax)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export function SimulationPage() {
  const [formData, setFormData] = useState<GrossToNetRequest>({
    /*
     * The seeded example is illustrative, not a market claim: it is chosen so
     * that the progressive ladder is actually engaged (the 1404 monthly
     * exemption is 240,000,000 Rial), so a first-time user sees both Article
     * 137 postures with a non-zero tax instead of an empty slab table.
     */
    gross_monthly_rial: 300000000,
    rule_year: 1404,
    days_in_month: 30,
    tax_posture: 'conservative_inta',
    allowances: {
      housing: 9000000,
      grocery: 4500000,
      marriage: 3000000,
      child: 6000000,
      continuous_attraction: 0,
    },
    overtime_hours: 0,
    night_hours: 0,
    continuous_attraction_taxable: false,
    probation_months: null,
    tenure_months: null,
    accumulated_unused_leave_days: null,
    probation_days_worked: null,
  });

  const [result, setResult] = useState<PayrollResponse | null>(null);
  const [error, setError] = useState<{ message: string; code: string } | null>(null);

  const mutation = useMutation({
    mutationFn: async (data: GrossToNetRequest) => {
      const response = await apiClient.request<PayrollResponse>({
        method: 'POST',
        path: CONTRACTS.grossToNet.path,
        body: data,
      });
      return response.data;
    },
    onSuccess: (data) => {
      setResult(data);
      setError(null);
    },
    onError: (err: Error) => {
      // The backend refusal keeps its categorical code: the Persian message
      // explains it and the machine code is shown so the refusal can be
      // traced to the statutory rule that stopped the calculation.
      setError(
        isApiError(err)
          ? { message: err.messageFa, code: err.code }
          : { message: 'خطای غیرمنتظره در ارتباط با سرویس محاسبه رخ داد.', code: 'UNKNOWN' },
      );
      setResult(null);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate(formData);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    let parsedValue: string | number | boolean | null = value;

    if (type === 'number' || type === 'range') {
      if (OPTIONAL_NUMERIC_FIELDS.includes(name as (typeof OPTIONAL_NUMERIC_FIELDS)[number])) {
        parsedValue = value === '' ? null : Number(value);
      } else {
        parsedValue = value === '' ? 0 : Number(value);
      }
    } else if (type === 'checkbox') {
      parsedValue = (e.target as HTMLInputElement).checked;
    }

    if (name.startsWith('allowances.')) {
      const field = name.replace('allowances.', '');
      setFormData((prev) => ({
        ...prev,
        allowances: {
          ...prev.allowances!,
          [field]: parsedValue as number,
        },
      }));
    } else {
      setFormData((prev) => ({
        ...prev,
        [name]: parsedValue,
      }));
    }
  };

  const primaryPosture = result?.tax_postures[result.primary_tax_posture];
  const alternatePosture = result?.tax_postures[
    result?.primary_tax_posture === 'conservative_inta' ? 'court_precedent' : 'conservative_inta'
  ];

  return (
    <div className='space-y-6'>
      <form onSubmit={handleSubmit} className='space-y-4'>
        <Card>
          <CardHeader>
            <CardTitle>ورودی‌های محاسبه</CardTitle>
            <CardDescription>مقادیر را وارد کنید و شبیه‌سازی را اجرا نمایید</CardDescription>
          </CardHeader>
          <CardContent className='space-y-4'>
            <div className='grid gap-4 sm:grid-cols-2 lg:grid-cols-3'>
              <Input
                name='gross_monthly_rial'
                type='number'
                label='حقوق ناخالص ماهانه (ریال) *'
                value={formData.gross_monthly_rial}
                onChange={handleChange}
                inputMode='numeric'
                min={1}
                step="any"
                dir='ltr'
                className='tabular-nums'
              />

              <Input
                name='rule_year'
                type='number'
                label='سال قانونی'
                value={formData.rule_year}
                onChange={handleChange}
                inputMode='numeric'
                min={1404}
                max={1404}
                dir='ltr'
                className='tabular-nums'
              />

              <div>
                <label htmlFor='days_in_month' className='text-sm font-medium text-ink mb-2 block'>روزهای ماه</label>
                <select
                  id='days_in_month'
                  name='days_in_month'
                  value={formData.days_in_month}
                  onChange={handleChange}
                  className='w-full rounded-lg border border-input bg-background px-3 py-2 text-sm dir-ltr'
                >
                  <option value={29}>۲۹</option>
                  <option value={30}>۳۰</option>
                  <option value={31}>۳۱</option>
                </select>
              </div>

              <div>
                <label htmlFor='tax_posture' className='text-sm font-medium text-ink mb-2 block'>حالت ماده ۱۳۷</label>
                <select
                  id='tax_posture'
                  name='tax_posture'
                  value={formData.tax_posture}
                  onChange={handleChange}
                  className='w-full rounded-lg border border-input bg-background px-3 py-2 text-sm dir-ltr'
                >
                  <option value='conservative_inta'>محافظه‌کارانه (INTA)</option>
                  <option value='court_precedent'>مرجع دیوان</option>
                </select>
              </div>

              <Input
                name='overtime_hours'
                type='number'
                label='ساعت اضافه‌کاری'
                value={formData.overtime_hours}
                onChange={handleChange}
                inputMode='numeric'
                min={0}
                dir='ltr'
                className='tabular-nums'
              />

              <Input
                name='night_hours'
                type='number'
                label='ساعت شب‌کاری'
                value={formData.night_hours}
                onChange={handleChange}
                inputMode='numeric'
                min={0}
                dir='ltr'
                className='tabular-nums'
              />
            </div>

            <div className='border-t border-border-subtle pt-4'>
              <h3 className='mb-3 font-medium'>حقوق و مزایا (ریال)</h3>
              <div className='grid gap-4 sm:grid-cols-2 lg:grid-cols-3'>
                {[
                  { key: 'housing', label: 'حق مسکن' },
                  { key: 'grocery', label: 'بن خواربار' },
                  { key: 'marriage', label: 'حق تاهل' },
                  { key: 'child', label: 'حق اولاد' },
                  { key: 'continuous_attraction', label: 'فوق‌العاده جذب' },
                ].map(({ key, label }) => (
                  <Input
                    key={key}
                    name={`allowances.${key}`}
                    type='number'
                    label={label}
                    value={formData.allowances?.[key as keyof typeof formData.allowances] ?? 0}
                    onChange={handleChange}
                    inputMode='numeric'
                    min={0}
                    step="any"
                    dir='ltr'
                    className='tabular-nums'
                  />
                ))}
              </div>
            </div>

            <div className='border-t border-border-subtle pt-4'>
              <h3 className='mb-3 font-medium'>تنظیمات پیشرفته (اختیاری)</h3>
              <div className='grid gap-4 sm:grid-cols-2 lg:grid-cols-4'>
                <div className='flex items-center gap-2'>
                  <input
                    type='checkbox'
                    id='continuous_attraction_taxable'
                    name='continuous_attraction_taxable'
                    checked={formData.continuous_attraction_taxable}
                    onChange={handleChange}
                    className='h-4 w-4 rounded border-input'
                  />
                  <label htmlFor='continuous_attraction_taxable' className='text-sm cursor-pointer'>
                    جذب مشمول مالیات
                  </label>
                </div>
                <Input
                  name='probation_months'
                  type='number'
                  label='ماه‌های آزمایشی'
                  value={formData.probation_months ?? ''}
                  onChange={handleChange}
                  inputMode='numeric'
                  min={1}
                  max={3}
                  dir='ltr'
                  className='tabular-nums'
                  placeholder='۱ تا ۳'
                />
                <Input
                  name='tenure_months'
                  type='number'
                  label='مُدّت خدمت (ماه)'
                  value={formData.tenure_months ?? ''}
                  onChange={handleChange}
                  inputMode='numeric'
                  min={0}
                  dir='ltr'
                  className='tabular-nums'
                  placeholder='۰'
                />
                <Input
                  name='accumulated_unused_leave_days'
                  type='number'
                  label='مرخصی انباشته'
                  value={formData.accumulated_unused_leave_days ?? ''}
                  onChange={handleChange}
                  inputMode='numeric'
                  min={0}
                  dir='ltr'
                  className='tabular-nums'
                  placeholder='۰'
                />
              </div>
            </div>

            <div className='flex justify-end pt-2'>
              <Button type='submit' disabled={mutation.isPending} className='min-w-[160px]'>
                {mutation.isPending ? (
                  <>
                    <Icon name='spinner' className='me-2 h-4 w-4 animate-spin' />
                    در حال محاسبه...
                  </>
                ) : (
                  <>
                    <Icon name='simulation' className='me-2 h-4 w-4' />
                    اجرای شبیه‌سازی
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {error && (
          <div className='rounded-lg border border-destructive bg-destructive/10 p-4 text-destructive' role='alert'>
            <Icon name='alert' className='inline-block h-5 w-5 align-middle ms-2' />
            <p>{error.message}</p>
            <p className='mt-1 text-xs font-mono' dir='ltr'>{error.code}</p>
          </div>
        )}
      </form>

      {result && (
        <section aria-label='نتایج شبیه‌سازی' className='space-y-6'>
          <div className='flex items-center justify-between'>
            <h2 className='text-xl font-semibold'>نتایج محاسبه</h2>
            <div className='flex items-center gap-2 text-sm text-ink-muted'>
              <Icon name='check' className='h-4 w-4' />
              <span>نسخه قوانین: {result.statutory_version} ({result.rule_set_status})</span>
              <span className='mx-1'>·</span>
              <span>هش محاسبه: {result.calculation_hash.slice(0, 16)}…</span>
            </div>
          </div>

          <div className='grid gap-4 lg:grid-cols-2'>
            <PostureCard
              title='حالت اصلی'
              posture={result.primary_tax_posture}
              netRial={result.net_rial}
              taxRial={primaryPosture?.income_tax_rial ?? 0}
              deductionRial={primaryPosture?.art137_deduction_rial ?? 0}
              welfareTaxable={primaryPosture?.welfare_allowances_taxable ?? false}
              slabs={primaryPosture?.slab_breakdown.map((s) => ({
                label: slabLabel(s.slab, s.rate),
                taxed: s.taxed_amount_rial,
                tax: s.tax_rial,
              })) ?? []}
            />
            <PostureCard
              title='حالت جایگزین'
              posture={result.primary_tax_posture === 'conservative_inta' ? 'court_precedent' : 'conservative_inta'}
              netRial={result.alternate_posture_net_rial}
              taxRial={alternatePosture?.income_tax_rial ?? 0}
              deductionRial={alternatePosture?.art137_deduction_rial ?? 0}
              welfareTaxable={alternatePosture?.welfare_allowances_taxable ?? false}
              slabs={alternatePosture?.slab_breakdown.map((s) => ({
                label: slabLabel(s.slab, s.rate),
                taxed: s.taxed_amount_rial,
                tax: s.tax_rial,
              })) ?? []}
            />
          </div>

          <Card>
            <CardHeader>
              <CardTitle>خلاصه کسرها و هزینه‌ها</CardTitle>
            </CardHeader>
            <CardContent className='space-y-3'>
              <div className='grid gap-3 sm:grid-cols-2 lg:grid-cols-4'>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>بیمه کارمند (۷٪)</p>
                  <p className='text-lg font-semibold tabular-nums'>{rialAmount(result.employee_deductions.employee_sso_7pct_rial)} ریال</p>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>مالیات درآمد</p>
                  <p className='text-lg font-semibold tabular-nums text-destructive'>{rialAmount(result.employee_deductions.income_tax_rial)} ریال</p>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>خالص دریافتی</p>
                  <p className='text-lg font-semibold tabular-nums'>{rialAmount(result.net_rial)} ریال</p>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>مانده گرد کردن</p>
                  <p className='text-lg font-semibold tabular-nums'>{rialAmount(result.rounding_residual_rial)} ریال</p>
                </div>
              </div>

              <div className='border-t border-border-subtle pt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-4'>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>سنوات (ماهانه)</p>
                  <p className='text-lg font-semibold tabular-nums'>{rialAmount(result.severance_sanavat.monthly_accrual_rial)} ریال</p>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>عیدی (ماهانه)</p>
                  <p className='text-lg font-semibold tabular-nums'>{rialAmount(result.eydi.monthly_accrual_rial)} ریال</p>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>هزینه کل کارفرما (ماه)</p>
                  <p className='text-lg font-semibold tabular-nums'>{rialAmount(result.employer_cost.total_monthly_employer_cost_rial)} ریال</p>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>بهای تمام‌شده سالانه</p>
                  <p className='text-lg font-semibold tabular-nums'>{rialAmount(result.employer_cost.annual_ctc_12month_rial)} ریال</p>
                </div>
              </div>

              {result.termination_liability && (
                <div className='border-t border-border-subtle pt-3'>
                  <h4 className='mb-3 font-medium'>تسویه و پایان خدمت (ماده ۱۱)</h4>
                  <div className='grid gap-3 sm:grid-cols-2 lg:grid-cols-4'>
                    <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                      <p className='text-xs text-ink-muted'>تعهد آزمایشی (کارفرما)</p>
                      <p className='text-lg font-semibold tabular-nums'>{rialAmount(result.termination_liability.employer_initiated_probation_liability_rial)} ریال</p>
                    </div>
                    <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                      <p className='text-xs text-ink-muted'>تعهد آزمایشی (کارمند)</p>
                      <p className='text-lg font-semibold tabular-nums'>{rialAmount(result.termination_liability.employee_initiated_probation_liability_rial ?? 0)} ریال</p>
                    </div>
                    <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                      <p className='text-xs text-ink-muted'>سنوات خروج</p>
                      <p className='text-lg font-semibold tabular-nums'>{rialAmount(result.termination_liability.exit_severance_rial)} ریال</p>
                    </div>
                    <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                      <p className='text-xs text-ink-muted'>خرید مرخصی</p>
                      <p className='text-lg font-semibold tabular-nums'>{rialAmount(result.termination_liability.leave_buyout_rial)} ریال</p>
                    </div>
                    <div className='rounded-lg border border-border-subtle bg-surface p-3 sm:col-span-2'>
                      <p className='text-xs text-ink-muted'>مجموع جداسازی</p>
                      <p className='text-xl font-semibold tabular-nums'>{rialAmount(result.termination_liability.total_separation_rial)} ریال</p>
                    </div>
                  </div>
                </div>
              )}

              <div className='border-t border-border-subtle pt-3 text-xs text-ink-muted'>
                <p>منشأ محاسبه: <code className='font-mono'>{result.engine_version}</code> · محاسبه در: {new Date(result.generated_at).toLocaleString('fa-IR', { timeZone: 'Asia/Tehran' })}</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>مبانی حقوقی و بیمه</CardTitle>
              <CardDescription>
                مبانی استخراج‌شده از حقوق ناخالص و سهم بیمهٔ تأمین اجتماعی؛ هر رقم بالا از همین مبانی محاسبه شده است.
              </CardDescription>
            </CardHeader>
            <CardContent className='space-y-3'>
              <div className='grid gap-3 sm:grid-cols-2 lg:grid-cols-4'>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>حقوق ناخالص ماهانه</p>
                  <p className='text-lg font-semibold tabular-nums'>{rialAmount(result.bases.total_gross_rial - result.bases.overtime_pay_rial - result.bases.night_shift_pay_rial)} ریال</p>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>جمع ناخالص با اضافه‌کاری و شب‌کاری</p>
                  <p className='text-lg font-semibold tabular-nums'>{rialAmount(result.bases.total_gross_rial)} ریال</p>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>مزایای رفاهی (خارج از مزد ثابت)</p>
                  <p className='text-lg font-semibold tabular-nums'>{rialAmount(result.bases.welfare_total_rial)} ریال</p>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>مزد ثابت (مبنای سنوات و عیدی)</p>
                  <p className='text-lg font-semibold tabular-nums'>{rialAmount(result.bases.mozd_e_saabet_rial)} ریال</p>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>اضافه‌کاری (مخرج {toPersianDigits(result.bases.overtime_divisor)} ساعت)</p>
                  <p className='text-lg font-semibold tabular-nums'>{rialAmount(result.bases.overtime_pay_rial)} ریال</p>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>شب‌کاری</p>
                  <p className='text-lg font-semibold tabular-nums'>{rialAmount(result.bases.night_shift_pay_rial)} ریال</p>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>سقف بیمهٔ ماهانه</p>
                  <p className='text-lg font-semibold tabular-nums'>{rialAmount(result.sso.insurable_ceiling_rial)} ریال</p>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>اعمال سقف بیمه</p>
                  <Badge tone={result.sso.sso_insurable_ceiling_applied ? 'danger' : 'neutral'} className='text-base'>
                    {result.sso.sso_insurable_ceiling_applied ? 'بله' : 'خیر'}
                  </Badge>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>حقوق مشمول بیمه</p>
                  <p className='text-lg font-semibold tabular-nums'>{rialAmount(result.sso.insurable_wage_rial)} ریال</p>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>بیمهٔ کارمند (۷٪)</p>
                  <p className='text-lg font-semibold tabular-nums'>{rialAmount(result.sso.employee_share_7pct_rial)} ریال</p>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>بیمهٔ کارفرما (۲۰٪)</p>
                  <p className='text-lg font-semibold tabular-nums'>{rialAmount(result.sso.employer_share_20pct_rial)} ریال</p>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>بیمهٔ بیکاری (۳٪)</p>
                  <p className='text-lg font-semibold tabular-nums'>{rialAmount(result.sso.unemployment_fund_3pct_rial)} ریال</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>منشأ هر رقم</CardTitle>
              <CardDescription>
                قاعدهٔ قانونی و فرمول هر رقم صادرشده؛ شناسهٔ قاعده و سال قانونی مستقیماً از پاسخ سرویس خوانده شده است.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className='overflow-x-auto'>
                <table className='w-full text-sm text-start'>
                  <thead>
                    <tr className='border-b border-border-subtle'>
                      <th className='pb-2 text-ink-muted'>رقم</th>
                      <th className='pb-2 text-ink-muted'>شناسهٔ قاعده</th>
                      <th className='pb-2 text-ink-muted'>سال قانونی</th>
                      <th className='pb-2 text-ink-muted'>فرمول</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(result.provenance).map(([figure, entry]) => (
                      <tr key={figure} className='border-b border-border-subtle/50 last:border-0'>
                        <td className='py-1 font-mono text-xs' dir='ltr'>{figure}</td>
                        <td className='py-1 font-mono text-xs' dir='ltr'>{entry.rule_id}</td>
                        <td className='py-1 tabular-nums'>{toPersianDigits(String(entry.rule_year_shamsi))}</td>
                        <td className='py-1 text-xs text-ink-muted' dir='ltr'>{entry.formula_ref}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </section>
      )}
    </div>
  );
}