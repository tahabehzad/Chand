import { useCallback, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Icon } from '@/components/icon';
import { CONTRACTS } from '@/api/contracts';
import { apiClient } from '@/api/instance';
import { formatMoney, formatPercentFromRate } from '@/lib/money';
import { parseIntegerInput, toPersianDigits } from '@/lib/numerals';
import { useUiStore } from '@/state/ui-store';
import { isApiError } from '@/api/errors';
import type { GrossToNetRequest, PayrollResponse, TaxPosture } from '@/api/payroll-types';
import { WorkProfileFields } from './work-profile-fields';
import { calculateWorkProfile, type WorkResult } from './work-profile-api';
import { isPrototypeError } from '@/prototype/api';

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
 * Respects the display unit preference (rial/toman); a Toman rendering is
 * refused for a value not divisible by 10 and falls back to Rial.
 */
function rialAmount(value: number): { amount: string; unitLabel: string; unit: 'rial' | 'toman' } {
  const unit = useUiStore.getState().preferredUnit;
  const formatted = formatMoney(value, unit);
  if (formatted.ok) {
    return { amount: formatted.value.amount, unitLabel: formatted.value.unitLabel, unit: formatted.value.unit };
  }
  // Not divisible by 10 for Toman: fall back to Rial with a note.
  const rial = formatMoney(value, 'rial');
  return { amount: rial.ok ? rial.value.amount : '—', unitLabel: rial.ok ? rial.value.unitLabel : 'ریال', unit: 'rial' };
}

/** Render an amount followed by its unit label, respecting the preferred unit. */
function MoneyText({ value }: { value: number }) {
  const { amount, unitLabel } = rialAmount(value);
  return (
    <>
      {amount}
      <span className='text-sm font-normal text-ink-muted'>{unitLabel}</span>
    </>
  );
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
          {isConservative ? 'سناریوی محافظه‌کارانه' : 'سناریوی رویه قضایی'}
        </Badge>
      </CardHeader>
      <CardContent className='space-y-3'>
        <div className='grid gap-3 sm:grid-cols-2'>
          <div className='rounded-lg border border-border-subtle bg-surface p-3'>
            <p className='text-xs text-ink-muted'>خالص دریافتی</p>
            <p className='text-2xl font-semibold tabular-nums'><MoneyText value={netRial} /></p>
          </div>
          <div className='rounded-lg border border-border-subtle bg-surface p-3'>
            <p className='text-xs text-ink-muted'>مالیات بر درآمد</p>
            <p className='text-xl font-semibold tabular-nums text-destructive'><MoneyText value={taxRial} /></p>
          </div>
          <div className='rounded-lg border border-border-subtle bg-surface p-3'>
            <p className='text-xs text-ink-muted'>کسور از درآمد مشمول مالیات (ماده ۱۳۷)</p>
            <p className='text-xl font-semibold tabular-nums'><MoneyText value={deductionRial} /></p>
          </div>
          <div className='rounded-lg border border-border-subtle bg-surface p-3'>
            <p className='text-xs text-ink-muted'>شمول مالیات مزایای رفاهی در این سناریو</p>
            <Badge tone={welfareTaxable ? 'danger' : 'neutral'} className='text-base'>
              {welfareTaxable ? 'بله' : 'خیر'}
            </Badge>
          </div>
        </div>
        <div className='rounded-lg border border-border-subtle bg-surface p-3'>
          <p className='mb-2 text-xs font-medium text-ink-muted'>جزئیات پلکان‌های مالیات حقوق</p>
          <div className='overflow-x-auto'>
            <table className='w-full text-sm text-start'>
              <thead>
                <tr className='border-b border-border-subtle'>
                  <th className='pb-2 text-ink-muted'>ردیف</th>
                  <th className='pb-2 text-ink-muted'>مبلغ مشمول ({useUiStore.getState().preferredUnit === 'toman' ? 'تومان' : 'ریال'})</th>
                  <th className='pb-2 text-ink-muted'>مالیات ({useUiStore.getState().preferredUnit === 'toman' ? 'تومان' : 'ریال'})</th>
                </tr>
              </thead>
              <tbody>
                {slabs.map((s, i) => (
                  <tr key={i} className='border-b border-border-subtle/50 last:border-0'>
                    <td className='py-1'>{s.label}</td>
                    <td className='py-1 tabular-nums'><MoneyText value={s.taxed} /></td>
                    <td className='py-1 tabular-nums'><MoneyText value={s.tax} /></td>
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

const INITIAL_INPUTS: GrossToNetRequest = {
  gross_monthly_rial: 0,
  rule_year: 1404,
  days_in_month: 30,
  tax_posture: 'conservative_inta',
  allowances: {
    housing: 0,
    grocery: 0,
    marriage: 0,
    child: 0,
    continuous_attraction: 0,
  },
  overtime_hours: 0,
  night_hours: 0,
  continuous_attraction_taxable: false,
  probation_months: null,
  tenure_months: null,
  accumulated_unused_leave_days: null,
  probation_days_worked: null,
};

export function SimulationPage() {
  const [search, setSearch] = useSearchParams();
  const employeeId = search.get('employee') ?? '';
  const [workDirty, setWorkDirty] = useState(false);
  const [workContext, setWorkContext] = useState<WorkResult['work_context'] | null>(null);
  const [formData, setFormData] = useState(INITIAL_INPUTS);
  const [grossInput, setGrossInput] = useState('');
  const [grossError, setGrossError] = useState<string>();
  const parsedGross = parseIntegerInput(grossInput);
  const grossRial = parsedGross.ok && !parsedGross.negative ? Number(parsedGross.value) : 0;
  const validGross = Number.isSafeInteger(grossRial) && grossRial > 0;
  const grossHint = validGross ? formatMoney(grossRial, 'rial') : null;

  const [result, setResult] = useState<PayrollResponse | null>(null);
  const [error, setError] = useState<{ message: string; code: string } | null>(null);
  const restoreWork = useCallback((saved: WorkResult | null) => {
    if (saved?.full_time_inputs) {
      setFormData(saved.full_time_inputs);
      setGrossInput(toPersianDigits(String(saved.full_time_inputs.gross_monthly_rial)));
      setGrossError(undefined);
    }
    setResult(saved?.payroll ?? null);
    setWorkContext(saved?.work_context ?? null);
    setError(null);
  }, []);
  const selectEmployee = useCallback((id: string) => {
    setSearch(id ? { employee: id } : {}, { replace: true });
    setFormData(INITIAL_INPUTS);
    setGrossInput('');
    setGrossError(undefined);
    setResult(null); setWorkContext(null);
  }, [setSearch]);

  const mutation = useMutation({
    mutationFn: async (data: GrossToNetRequest) => {
      if (employeeId) {
        const saved = await calculateWorkProfile(employeeId, data);
        setWorkContext(saved.work_context);
        return saved.payroll;
      }
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
        isPrototypeError(err)
          ? { message: err.message, code: err.code }
          : isApiError(err)
          ? { message: err.messageFa, code: err.code }
          : { message: 'خطای غیرمنتظره در ارتباط با سرویس محاسبه رخ داد.', code: 'UNKNOWN' },
      );
      setResult(null);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validGross) {
      setGrossError('حقوق ناخالص ماهانه را به‌صورت عدد صحیح و مثبت به ریال وارد کنید.');
      return;
    }
    mutation.mutate({ ...formData, gross_monthly_rial: grossRial });
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setResult(null); setWorkContext(null);
    setError(null);
    const { name, value, type } = e.target;
    let parsedValue: string | number | boolean | null = value;

    if (name === 'days_in_month') {
      parsedValue = Number(value);
    } else if (type === 'number' || type === 'range') {
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
      <header className='flex flex-wrap items-start justify-between gap-4'>
        <div>
          <h1 className='text-2xl font-bold text-ink sm:text-3xl'>محاسبه حقوق و دستمزد</h1>
        </div>
      </header>
      <div className='grid items-start gap-5 lg:grid-cols-[minmax(0,1fr)_minmax(17rem,0.58fr)]'>
      <form onSubmit={handleSubmit} className='space-y-4'>
        <fieldset disabled={mutation.isPending} className='min-w-0 space-y-4'>
        <Card>
          <CardHeader className='bg-surface/50'>
            <CardTitle>اطلاعات حقوق و کارکرد</CardTitle>
          </CardHeader>
          <CardContent className='space-y-4'>
            <div className='grid gap-4 sm:grid-cols-2'>
              <Input
                name='gross_monthly_rial'
                type='text'
                label={employeeId ? 'حقوق ناخالص ماهانه تمام‌وقت، بدون پایه سنوات (ریال)' : 'حقوق ناخالص ماهانه با مزایا (ریال)'}
                hint={grossHint?.ok ? `${grossHint.value.amount} ${grossHint.value.unitLabel}` : 'جمع حقوق و مزایا پیش از کسر بیمه و مالیات'}
                error={grossError}
                value={grossInput}
                onChange={(event) => {
                  setGrossInput(toPersianDigits(event.target.value));
                  setGrossError(undefined);
                  setResult(null);
                  setWorkContext(null);
                  setError(null);
                }}
                inputMode='numeric'
                dir='ltr'
                className='tabular-nums'
              />

              <div>
                <label htmlFor='days_in_month' className='text-sm font-medium text-ink mb-2 block'>تعداد روزهای ماه</label>
                <select
                  id='days_in_month'
                  name='days_in_month'
                  value={formData.days_in_month}
                  onChange={handleChange}
                  className='min-h-11 w-full rounded-lg border border-border-subtle bg-surface-raised px-3 py-2 text-sm text-ink'
                >
                  <option value={29}>۲۹</option>
                  <option value={30}>۳۰</option>
                  <option value={31}>۳۱</option>
                </select>
              </div>

              <div>
                <label htmlFor='tax_posture' className='text-sm font-medium text-ink mb-2 block'>سناریوی اصلی مالیات</label>
                <select
                  id='tax_posture'
                  name='tax_posture'
                  value={formData.tax_posture}
                  onChange={handleChange}
                  className='min-h-11 w-full rounded-lg border border-border-subtle bg-surface-raised px-3 py-2 text-sm text-ink'
                >
                  <option value='conservative_inta'>سناریوی محافظه‌کارانه</option>
                  <option value='court_precedent'>سناریوی رویه قضایی</option>
                </select>
              </div>

              <Input
                name='overtime_hours'
                type='number'
                label='اضافه‌کاری ماهانه (ساعت)'
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
                label='شب‌کاری غیرنوبتی (ساعت)'
                value={formData.night_hours}
                onChange={handleChange}
                inputMode='numeric'
                min={0}
                dir='ltr'
                className='tabular-nums'
              />
            </div>

            <details className='rounded-xl border border-border-subtle p-4'>
              <summary className='cursor-pointer text-sm font-semibold text-ink'>ریز مزایای داخل ناخالص (اختیاری، ریال)</summary>
              <p className='mt-3 text-sm text-ink-muted'>مبالغی را وارد کنید که در حقوق ناخالص بالا حساب کرده‌اید.</p>
              <div className='mt-4 grid gap-4 sm:grid-cols-2'>
                {[
                  { key: 'housing', label: 'حق مسکن' },
                  { key: 'grocery', label: 'بن کارگری' },
                  { key: 'marriage', label: 'حق تأهل' },
                  { key: 'child', label: 'حق اولاد (جمع)' },
                  { key: 'continuous_attraction', label: 'فوق‌العاده جذب ثابت و مستمر' },
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
            </details>

            {!employeeId && <details className='rounded-xl border border-border-subtle bg-surface/50 p-4'>
              <summary className='cursor-pointer text-sm font-semibold text-ink'>تنظیمات تکمیلی و برآورد پایان همکاری (اختیاری)</summary>
              <div className='mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4'>
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
                    فوق‌العاده جذب در محاسبه مالیات منظور شود
                  </label>
                </div>
                <Input
                  name='probation_months'
                  type='number'
                  label='دوره آزمایشی ـ فسخ کارفرما (ماه)'
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
                  label='سابقه نزد کارفرمای فعلی (ماه)'
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
                  label='مانده مرخصی استفاده‌نشده (روز)'
                  value={formData.accumulated_unused_leave_days ?? ''}
                  onChange={handleChange}
                  inputMode='numeric'
                  min={0}
                  dir='ltr'
                  className='tabular-nums'
                  placeholder='۰'
                />
              </div>
            </details>}

            <div className='flex flex-col items-start justify-between gap-4 border-t border-border-subtle pt-5 sm:flex-row sm:items-center'>
              <Button type='submit' disabled={mutation.isPending || workDirty} size='lg' className='w-full sm:w-auto sm:min-w-48'>
                {mutation.isPending ? (
                  <>
                    <Icon name='spinner' className='me-2 h-4 w-4 animate-spin' />
                    در حال محاسبه...
                  </>
                ) : (
                  <>
                    <Icon name='simulation' className='me-2 h-4 w-4' />
                    محاسبه حقوق
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
        </fieldset>
      </form>
      <Card className='min-w-0 border-brand/30 lg:sticky lg:top-4'>
        <CardHeader className='bg-brand/5'>
          <CardTitle>خلاصهٔ حقوق ماهانه</CardTitle>
        </CardHeader>
        <CardContent role='status' className='space-y-4'>
          {mutation.isPending ? (
            <p className='text-sm text-ink-muted'>در حال محاسبهٔ حقوق…</p>
          ) : result ? (
            <>
              <div>
                <p className='text-sm text-ink-muted'>خالص پرداختی به کارمند</p>
                <p className='mt-1 break-words text-3xl font-bold tabular-nums text-brand'><MoneyText value={result.net_rial} /></p>
              </div>
              <dl className='space-y-3 border-t border-border-subtle pt-4 text-sm'>
                {([
                  ['سهم بیمهٔ کارمند', result.employee_deductions.employee_sso_7pct_rial],
                  ['مالیات حقوق', result.employee_deductions.income_tax_rial],
                  ['هزینهٔ ماهانهٔ کارفرما', result.employer_cost.total_monthly_employer_cost_rial],
                ] as const).map(([label, value]) => (
                  <div key={label} className='flex flex-wrap justify-between gap-x-3 gap-y-1'>
                    <dt className='text-ink-muted'>{label}</dt>
                    <dd className='font-semibold tabular-nums'><MoneyText value={value} /></dd>
                  </div>
                ))}
              </dl>
              <a href='#payroll-details' className='inline-block text-sm font-medium text-brand underline'>جزئیات محاسبه</a>
            </>
          ) : (
            <p className='text-sm leading-7 text-ink-muted'>حقوق ناخالص را وارد کنید و «محاسبه حقوق» را بزنید تا خالص پرداختی، کسورات و هزینهٔ کارفرما را ببینید.</p>
          )}
        </CardContent>
      </Card>
      </div>

      <details open={Boolean(employeeId)} className='rounded-xl border border-border-subtle bg-surface p-4'>
        <summary className='cursor-pointer text-sm font-semibold text-ink'>محاسبه با پروندهٔ کارمند (اختیاری)</summary>
        <div className='mt-4'>
          <WorkProfileFields employeeId={employeeId} onSelect={selectEmployee} onDirtyChange={setWorkDirty} onRestored={restoreWork} locked={mutation.isPending} />
        </div>
      </details>

      {result && (
        <section id='payroll-details' aria-label='نتایج شبیه‌سازی' className='scroll-mt-20 space-y-6'>
          {workContext && <Card><CardContent className='grid gap-4 sm:grid-cols-3'>
            <div><p className='text-xs text-ink-muted'>نسبت کارکرد</p><p className='mt-2 font-semibold'>{formatPercentFromRate(workContext.ratio) ?? '—'}</p></div>
            <div><p className='text-xs text-ink-muted'>ناخالص متناسب با کارکرد</p><p className='mt-2 font-semibold'><MoneyText value={workContext.gross_rial} /></p></div>
            <div><p className='text-xs text-ink-muted'>پایه سنوات این ماه</p><p className='mt-2 font-semibold'><MoneyText value={workContext.seniority_rial} /></p></div>
          </CardContent></Card>}
          <div className='flex flex-wrap items-center justify-between gap-3'>
            <h2 className='text-xl font-semibold'>نتایج محاسبه</h2>
            <details className='text-xs text-ink-muted'>
              <summary className='cursor-pointer'>شناسه محاسبه</summary>
              <div className='mt-2 flex flex-wrap items-center gap-2'>
              <Icon name='check' className='h-4 w-4' />
              <span>نسخه قوانین: {result.statutory_version} ({result.rule_set_status})</span>
              <span className='mx-1'>·</span>
              <span>هش محاسبه: {result.calculation_hash.slice(0, 16)}…</span>
              </div>
            </details>
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
                  <p className='text-lg font-semibold tabular-nums'><MoneyText value={result.employee_deductions.employee_sso_7pct_rial} /></p>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>مالیات درآمد</p>
                  <p className='text-lg font-semibold tabular-nums text-destructive'><MoneyText value={result.employee_deductions.income_tax_rial} /></p>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>خالص دریافتی</p>
                  <p className='text-lg font-semibold tabular-nums'><MoneyText value={result.net_rial} /></p>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>مانده گرد کردن</p>
                  <p className='text-lg font-semibold tabular-nums'><MoneyText value={result.rounding_residual_rial} /></p>
                </div>
              </div>

              <div className='border-t border-border-subtle pt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-4'>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>سنوات (ماهانه)</p>
                  <p className='text-lg font-semibold tabular-nums'><MoneyText value={result.severance_sanavat.monthly_accrual_rial} /></p>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>عیدی (ماهانه)</p>
                  <p className='text-lg font-semibold tabular-nums'><MoneyText value={result.eydi.monthly_accrual_rial} /></p>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>هزینه کل کارفرما (ماه)</p>
                  <p className='text-lg font-semibold tabular-nums'><MoneyText value={result.employer_cost.total_monthly_employer_cost_rial} /></p>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>بهای تمام‌شده سالانه</p>
                  <p className='text-lg font-semibold tabular-nums'><MoneyText value={result.employer_cost.annual_ctc_12month_rial} /></p>
                </div>
              </div>

              {result.termination_liability && (
                <div className='border-t border-border-subtle pt-3'>
                  <h4 className='mb-3 font-medium'>تسویه و پایان خدمت (ماده ۱۱)</h4>
                  <div className='grid gap-3 sm:grid-cols-2 lg:grid-cols-4'>
                    <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                      <p className='text-xs text-ink-muted'>تعهد آزمایشی (کارفرما)</p>
                      <p className='text-lg font-semibold tabular-nums'><MoneyText value={result.termination_liability.employer_initiated_probation_liability_rial} /></p>
                    </div>
                    <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                      <p className='text-xs text-ink-muted'>تعهد آزمایشی (کارمند)</p>
                      <p className='text-lg font-semibold tabular-nums'><MoneyText value={result.termination_liability.employee_initiated_probation_liability_rial ?? 0} /></p>
                    </div>
                    <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                      <p className='text-xs text-ink-muted'>سنوات خروج</p>
                      <p className='text-lg font-semibold tabular-nums'><MoneyText value={result.termination_liability.exit_severance_rial} /></p>
                    </div>
                    <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                      <p className='text-xs text-ink-muted'>خرید مرخصی</p>
                      <p className='text-lg font-semibold tabular-nums'><MoneyText value={result.termination_liability.leave_buyout_rial} /></p>
                    </div>
                    <div className='rounded-lg border border-border-subtle bg-surface p-3 sm:col-span-2'>
                      <p className='text-xs text-ink-muted'>مجموع جداسازی</p>
                      <p className='text-xl font-semibold tabular-nums'><MoneyText value={result.termination_liability.total_separation_rial} /></p>
                    </div>
                  </div>
                </div>
              )}

              <div className='border-t border-border-subtle pt-3 text-xs text-ink-muted'>
                <p>منشأ محاسبه: <code className='font-mono'>{result.engine_version}</code> · محاسبه در: {new Date(result.generated_at).toLocaleString('fa-IR', { timeZone: 'Asia/Tehran' })}</p>
              </div>
            </CardContent>
          </Card>

          <details className='space-y-3 rounded-xl border border-border-subtle bg-surface-raised p-4'>
            <summary className='cursor-pointer text-sm font-medium'>جزئیات مبالغ و بیمه</summary>
          <Card>
            <CardHeader>
              <CardTitle>مبانی حقوقی و بیمه</CardTitle>
            </CardHeader>
            <CardContent className='space-y-3'>
              <div className='grid gap-3 sm:grid-cols-2 lg:grid-cols-4'>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>حقوق ناخالص ماهانه</p>
                  <p className='text-lg font-semibold tabular-nums'><MoneyText value={result.bases.total_gross_rial - result.bases.overtime_pay_rial - result.bases.night_shift_pay_rial} /></p>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>جمع ناخالص با اضافه‌کاری و شب‌کاری</p>
                  <p className='text-lg font-semibold tabular-nums'><MoneyText value={result.bases.total_gross_rial} /></p>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>مزایای رفاهی (خارج از مزد ثابت)</p>
                  <p className='text-lg font-semibold tabular-nums'><MoneyText value={result.bases.welfare_total_rial} /></p>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>مزد ثابت (مبنای سنوات و عیدی)</p>
                  <p className='text-lg font-semibold tabular-nums'><MoneyText value={result.bases.mozd_e_saabet_rial} /></p>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>اضافه‌کاری (مخرج {toPersianDigits(result.bases.overtime_divisor)} ساعت)</p>
                  <p className='text-lg font-semibold tabular-nums'><MoneyText value={result.bases.overtime_pay_rial} /></p>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>شب‌کاری</p>
                  <p className='text-lg font-semibold tabular-nums'><MoneyText value={result.bases.night_shift_pay_rial} /></p>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>سقف بیمهٔ ماهانه</p>
                  <p className='text-lg font-semibold tabular-nums'><MoneyText value={result.sso.insurable_ceiling_rial} /></p>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>اعمال سقف بیمه</p>
                  <Badge tone={result.sso.sso_insurable_ceiling_applied ? 'danger' : 'neutral'} className='text-base'>
                    {result.sso.sso_insurable_ceiling_applied ? 'بله' : 'خیر'}
                  </Badge>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>حقوق مشمول بیمه</p>
                  <p className='text-lg font-semibold tabular-nums'><MoneyText value={result.sso.insurable_wage_rial} /></p>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>بیمهٔ کارمند (۷٪)</p>
                  <p className='text-lg font-semibold tabular-nums'><MoneyText value={result.sso.employee_share_7pct_rial} /></p>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>بیمهٔ کارفرما (۲۰٪)</p>
                  <p className='text-lg font-semibold tabular-nums'><MoneyText value={result.sso.employer_share_20pct_rial} /></p>
                </div>
                <div className='rounded-lg border border-border-subtle bg-surface p-3'>
                  <p className='text-xs text-ink-muted'>بیمهٔ بیکاری (۳٪)</p>
                  <p className='text-lg font-semibold tabular-nums'><MoneyText value={result.sso.unemployment_fund_3pct_rial} /></p>
                </div>
              </div>
            </CardContent>
          </Card>

          </details>
          <details className='space-y-3 rounded-xl border border-border-subtle bg-surface-raised p-4'>
            <summary className='cursor-pointer text-sm font-medium'>منشأ ارقام</summary>
          <Card>
            <CardHeader>
              <CardTitle>منشأ هر رقم</CardTitle>
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
          </details>
        </section>
      )}
    </div>
  );
}
