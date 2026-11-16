import { useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { apiClient } from '@/api/instance';
import { isApiError } from '@/api/errors';
import { toPersianDigits } from '@/lib/numerals';
import { MANAGER_SESSION_KEY } from '@/routes/manager-login-page';

/**
 * The manager's proposal screen (ADR-009, `P5-T02`).
 *
 * One form, one request, one result table. The manager supplies the monthly
 * gross band in Toman; the engine scores the profile, places it inside that
 * band and returns the statutory cost of both ends. Nothing here calculates
 * money: every figure comes from the backend response.
 */
const ENDPOINT = '/api/v1/valuations/compensation-proposal';

type Education = 'below_diploma' | 'diploma' | 'associate' | 'bachelor' | 'master' | 'doctorate';

const EDUCATION_LABELS: Record<Education, string> = {
  below_diploma: 'زیر دیپلم',
  diploma: 'دیپلم',
  associate: 'کاردانی',
  bachelor: 'کارشناسی',
  master: 'کارشناسی ارشد',
  doctorate: 'دکترا',
};

type CostBlock = {
  gross_monthly_rial: number;
  employee_sso_7pct_rial: number;
  income_tax_rial: number;
  net_rial: number;
  total_monthly_employer_cost_rial: number;
};

type ProposalResponse = {
  model_version: string;
  score: { score_100: number; weights: Record<string, string> };
  band: { min_gross_rial: number; max_gross_rial: number };
  proposed: {
    gross_point_rial: number;
    range_low_rial: number;
    range_high_rial: number;
    position_in_band: string;
  };
  statutory_costing: {
    lower_bound: CostBlock;
    point: CostBlock;
    upper_bound: CostBlock;
  };
  statutory_context: {
    monthly_minimum_wage_rial: number;
    range_low_below_statutory_minimum: boolean;
  };
  calculation_hash: string;
  advisory_notes: string[];
};

function rial(value: number): string {
  return `${toPersianDigits(value.toLocaleString('en-US'))} ریال`;
}

function toman(value: string): number | null {
  const digits = value.replace(/[^\d]/g, '');
  return digits ? Number(digits) : null;
}

export function ProposalPage() {
  const navigate = useNavigate();
  const manager = window.sessionStorage.getItem(MANAGER_SESSION_KEY);

  const [totalYears, setTotalYears] = useState('5');
  const [relevantYears, setRelevantYears] = useState('3');
  const [skillLevel, setSkillLevel] = useState('3');
  const [education, setEducation] = useState<Education>('bachelor');
  const [bandMinToman, setBandMinToman] = useState('10,000,000');
  const [bandMaxToman, setBandMaxToman] = useState('20,000,000');

  const [result, setResult] = useState<ProposalResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  if (!manager) return <Navigate to="/login" replace />;

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    const min = toman(bandMinToman);
    const max = toman(bandMaxToman);
    if (min === null || max === null) {
      setError('کف و سقف بازه را به تومان وارد کنید.');
      return;
    }
    setPending(true);
    try {
      const response = await apiClient.request<ProposalResponse>({
        method: 'POST',
        path: ENDPOINT,
        body: {
          total_experience_months: Math.round(Number(totalYears) * 12),
          relevant_experience_months: Math.round(Number(relevantYears) * 12),
          skill_level: Number(skillLevel),
          education_level: education,
          band_min_gross_rial: min * 10,
          band_max_gross_rial: max * 10,
        },
      });
      setResult(response.data);
    } catch (caught) {
      if (isApiError(caught)) {
        setError(caught.messageFa);
      } else {
        setError('ارتباط با سرور برقرار نشد.');
      }
      setResult(null);
    } finally {
      setPending(false);
    }
  }

  const rows: Array<{ key: string; label: string; block: CostBlock }> = result
    ? [
        { key: 'low', label: 'کف بازه', block: result.statutory_costing.lower_bound },
        { key: 'point', label: 'پیشنهاد', block: result.statutory_costing.point },
        { key: 'high', label: 'سقف بازه', block: result.statutory_costing.upper_bound },
      ]
    : [];

  return (
    <main className="mx-auto flex min-h-dvh w-full max-w-5xl flex-col gap-6 bg-surface px-4 py-8">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-semibold text-ink">پیشنهاد حقوق</h1>
          <p className="mt-1 text-sm text-ink-muted">
            {manager} — بازه را شما تعیین می‌کنید؛ سامانه جایگاه فرد و هزینهٔ قانونی آن را حساب می‌کند.
          </p>
        </div>
        <Button
          variant="secondary"
          size="sm"
          onClick={() => {
            window.sessionStorage.removeItem(MANAGER_SESSION_KEY);
            navigate('/login', { replace: true });
          }}
        >
          خروج
        </Button>
      </header>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.1fr)]">
        <Card>
          <CardHeader>
            <CardTitle>مشخصات فرد</CardTitle>
            <CardDescription>سابقهٔ کل و سابقهٔ مرتبط جدا وارد می‌شوند.</CardDescription>
          </CardHeader>
          <CardContent>
            <form className="flex flex-col gap-4" onSubmit={submit}>
              <Input
                label="سابقهٔ کل (سال)"
                inputMode="numeric"
                dir="ltr"
                value={totalYears}
                onChange={(event) => setTotalYears(event.target.value)}
              />
              <Input
                label="سابقهٔ مرتبط (سال)"
                inputMode="numeric"
                dir="ltr"
                value={relevantYears}
                onChange={(event) => setRelevantYears(event.target.value)}
              />
              <label className="flex flex-col gap-2 text-sm font-medium text-ink">
                سطح مهارت (۱ تا ۵)
                <select
                  className="min-h-11 rounded-lg border border-border-subtle bg-surface-raised px-3 text-ink"
                  value={skillLevel}
                  onChange={(event) => setSkillLevel(event.target.value)}
                >
                  {[1, 2, 3, 4, 5].map((level) => (
                    <option key={level} value={level}>
                      {toPersianDigits(String(level))}
                    </option>
                  ))}
                </select>
              </label>
              <label className="flex flex-col gap-2 text-sm font-medium text-ink">
                تحصیلات
                <select
                  className="min-h-11 rounded-lg border border-border-subtle bg-surface-raised px-3 text-ink"
                  value={education}
                  onChange={(event) => setEducation(event.target.value as Education)}
                >
                  {(Object.keys(EDUCATION_LABELS) as Education[]).map((key) => (
                    <option key={key} value={key}>
                      {EDUCATION_LABELS[key]}
                    </option>
                  ))}
                </select>
              </label>
              <Input
                label="کف بازهٔ ماهانه (تومان)"
                inputMode="numeric"
                dir="ltr"
                value={bandMinToman}
                onChange={(event) => setBandMinToman(event.target.value)}
                hint="مثلاً 10,000,000 تومان"
              />
              <Input
                label="سقف بازهٔ ماهانه (تومان)"
                inputMode="numeric"
                dir="ltr"
                value={bandMaxToman}
                onChange={(event) => setBandMaxToman(event.target.value)}
                hint="مثلاً 20,000,000 تومان"
              />
              <Button type="submit" size="lg" disabled={pending}>
                {pending ? 'در حال محاسبه…' : 'محاسبهٔ پیشنهاد'}
              </Button>
            </form>
          </CardContent>
        </Card>

        <div className="flex flex-col gap-4">
          {error ? (
            <div className="rounded-lg border border-danger/40 bg-danger/5 p-4 text-sm text-danger">
              {error}
            </div>
          ) : null}

          {!result && !error ? (
            <Card>
              <CardContent>
                <p className="py-10 text-center text-sm text-ink-muted">
                  فرم را پر کنید؛ نتیجه همراه با هزینهٔ کارفرما اینجا نمایش داده می‌شود.
                </p>
              </CardContent>
            </Card>
          ) : null}

          {result ? (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>امتیاز و بازهٔ پیشنهادی</CardTitle>
                  <CardDescription>
                    مدل {result.model_version} — بازهٔ پیشنهادی{' '}
                    {rial(result.proposed.range_low_rial)} تا {rial(result.proposed.range_high_rial)}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap items-center gap-3">
                    <Badge>امتیاز {toPersianDigits(String(result.score.score_100))}</Badge>
                    <Badge>پیشنهاد {rial(result.proposed.gross_point_rial)}</Badge>
                    {result.statutory_context.range_low_below_statutory_minimum ? (
                      <Badge>کف بازه زیر حداقل قانونی است</Badge>
                    ) : null}
                  </div>
                  <table className="mt-4 w-full text-sm">
                    <thead>
                      <tr className="text-ink-muted">
                        <th className="py-2 text-start font-medium"> </th>
                        {rows.map((row) => (
                          <th key={row.key} className="py-2 text-start font-medium">
                            {row.label}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {[
                        ['ناخالص', 'gross_monthly_rial'],
                        ['بیمهٔ کارگر', 'employee_sso_7pct_rial'],
                        ['مالیات', 'income_tax_rial'],
                        ['خالص', 'net_rial'],
                        ['هزینهٔ کارفرما', 'total_monthly_employer_cost_rial'],
                      ].map(([label, field]) => (
                        <tr key={field} className="border-t border-border-subtle">
                          <td className="py-2 text-ink-muted">{label}</td>
                          {rows.map((row) => (
                            <td key={row.key} className="py-2 text-ink">
                              {rial(row.block[field as keyof CostBlock])}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  <p className="mt-4 text-xs leading-6 text-ink-muted">
                    این پیشنهاد توصیه‌ای است و تصمیم نهایی با مدیر است. کف قانونی ماهانه:{' '}
                    {rial(result.statutory_context.monthly_minimum_wage_rial)} — فقط برای مقایسه، اعمال نمی‌شود.
                  </p>
                </CardContent>
              </Card>
            </>
          ) : null}
        </div>
      </div>
    </main>
  );
}

export default ProposalPage;
