import { useCallback, useEffect, useState, type FormEvent } from 'react';
import { Link, useParams } from 'react-router-dom';
import { PageHeader } from '@/app/page-header';
import { Icon } from '@/components/icon';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { EmptyState, ErrorState, LoadingSkeleton } from '@/components/ui/states';
import {
  decideRecommendation,
  getRecommendation,
  isPrototypeError,
} from '@/prototype/api';
import type { DecisionAction, Recommendation } from '@/prototype/types';
import { PrototypeNotice } from './prototype-notice';
import { deltaText, faDigits, isoDateText, percentText, rialText } from './format';

const ACTIONS: Array<{ value: DecisionAction; labelFa: string }> = [
  { value: 'approve', labelFa: 'تأیید پیشنهاد' },
  { value: 'edit', labelFa: 'ویرایش مبلغ و تأیید' },
  { value: 'reject', labelFa: 'رد پیشنهاد' },
];

const DECISION_LABELS: Record<DecisionAction, string> = {
  approve: 'تأیید‌شده',
  edit: 'ویرایش‌شده',
  reject: 'رد‌شده',
};

const DECISION_TONES: Record<DecisionAction, 'success' | 'info' | 'danger'> = {
  approve: 'success',
  edit: 'info',
  reject: 'danger',
};

function rialNumber(value: number): string {
  return rialText(String(value));
}

export default function PrototypeRecommendationPage() {
  const { recommendationId } = useParams<{ recommendationId: string }>();
  const [recommendation, setRecommendation] = useState<Recommendation | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [action, setAction] = useState<DecisionAction>('approve');
  const [comment, setComment] = useState('');
  const [editedGross, setEditedGross] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async (): Promise<void> => {
    if (recommendationId === undefined) {
      setLoaded(true);
      return;
    }
    try {
      setLoadError(null);
      setRecommendation(await getRecommendation(recommendationId));
    } catch (caught) {
      setLoadError(
        isPrototypeError(caught) ? caught.message : 'دریافت پیشنهاد ناموفق بود.',
      );
    } finally {
      setLoaded(true);
    }
  }, [recommendationId]);

  useEffect(() => {
    void load();
  }, [load]);

  async function onDecide(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (recommendationId === undefined) return;
    setBusy(true);
    setError(null);
    try {
      await decideRecommendation(recommendationId, {
        action,
        comment,
        editedGrossRial: editedGross,
      });
      await load();
    } catch (caught) {
      setError(
        isPrototypeError(caught) ? caught.message : 'ثبت تصمیم ناموفق بود.',
      );
    } finally {
      setBusy(false);
    }
  }

  if (!loaded) {
    return <LoadingSkeleton rows={5} />;
  }

  if (recommendation === null) {
    return (
      <EmptyState
        title="این پیشنهاد یافت نشد"
        description={
          loadError ??
          'شناسهٔ درخواستی در سازمانِ نشست شما وجود ندارد؛ از فهرست کارکنان دوباره محاسبه کنید.'
        }
        action={
          <Button asChild variant="secondary">
            <Link to="/prototype/people">بازگشت به فهرست کارکنان</Link>
          </Button>
        }
      />
    );
  }

  const decision = recommendation.decision;
  const statutory = recommendation.statutory;
  const currentStatutory = recommendation.currentStatutory;

  return (
    <>
      <PageHeader
        eyebrow="گام ۳ از ۴ · پیشنهاد مشورتی"
        title={`پیشنهاد جبران خدمت برای ${recommendation.personName}`}
        description={`دورهٔ ${recommendation.period || '—'} · مدل ${recommendation.ruleSetVersion} · شناسهٔ ${recommendation.id}`}
        actions={
          <Button asChild variant="secondary">
            <Link to={`/prototype/people/${recommendation.personId}`}>
              <Icon name="arrow-back" />
              بازگشت به کارمند
            </Link>
          </Button>
        }
      />

      <PrototypeNotice compact />

      {loadError ? <ErrorState description={loadError} onRetry={() => void load()} /> : null}

      <div className="flex flex-wrap items-center gap-2">
        <Badge tone="warning">مشورتی — نه حقوق قانونی</Badge>
        <Badge tone="info">مدل {recommendation.ruleSetVersion}</Badge>
        <Badge tone="neutral">وضعیت مدل: {recommendation.ruleSetStatus}</Badge>
        <Badge tone="neutral">موتور: {recommendation.engineVersion}</Badge>
        {decision ? (
          <Badge tone={DECISION_TONES[decision.action]}>{DECISION_LABELS[decision.action]}</Badge>
        ) : (
          <Badge tone="warning">در انتظار تصمیم مدیر</Badge>
        )}
      </div>

      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_minmax(0,1.6fr)]">
        <Card className="min-w-0">
          <CardHeader>
            <CardTitle>امتیاز کل</CardTitle>
            <CardDescription>۰ تا ۱۰۰ بر پایهٔ وزن‌های منتشرشدهٔ مدل</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            <p className="text-5xl font-semibold tabular text-brand-strong">
              {faDigits(recommendation.score100)}
              <span className="ms-2 text-base font-normal text-ink-muted">از ۱۰۰</span>
            </p>
            <dl className="flex flex-col gap-2 text-sm">
              <div className="flex items-center justify-between gap-3">
                <dt className="text-ink-muted">حداقل بازه</dt>
                <dd className="tabular">{rialText(recommendation.band.minRial)}</dd>
              </div>
              <div className="flex items-center justify-between gap-3">
                <dt className="text-ink-muted">حداکثر بازه</dt>
                <dd className="tabular">{rialText(recommendation.band.maxRial)}</dd>
              </div>
              <div className="flex items-center justify-between gap-3">
                <dt className="text-ink-muted">جایگاه در بازه</dt>
                <dd className="tabular">{percentText(recommendation.band.positionBp)}</dd>
              </div>
              <div className="flex items-center justify-between gap-3 border-t border-border-subtle pt-2">
                <dt className="font-medium">پیشنهاد ماهانه</dt>
                <dd className="font-semibold tabular">
                  {rialText(recommendation.suggestedGrossRial)}
                </dd>
              </div>
              {recommendation.band.currentRial !== null ? (
                <>
                  <div className="flex items-center justify-between gap-3">
                    <dt className="text-ink-muted">حقوق فعلی</dt>
                    <dd className="tabular">{rialText(recommendation.band.currentRial)}</dd>
                  </div>
                  <div className="flex items-center justify-between gap-3">
                    <dt className="text-ink-muted">اختلاف</dt>
                    <dd className="tabular">
                      {recommendation.deltaRial === null
                        ? '—'
                        : deltaText(recommendation.deltaRial)}
                    </dd>
                  </div>
                </>
              ) : null}
            </dl>
          </CardContent>
        </Card>

        <Card className="min-w-0">
          <CardHeader>
            <CardTitle>تفکیک امتیاز</CardTitle>
            <CardDescription>
              هر سهم از ضرب مقدار نرمال‌شده در وزن همان معیار به دست آمده است؛ جمع سهم‌ها امتیاز
              کل است.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[36rem] text-sm">
                <thead>
                  <tr className="text-xs text-ink-muted">
                    <th className="px-2 py-2 text-start font-medium">معیار</th>
                    <th className="px-2 py-2 text-start font-medium">مقدار</th>
                    <th className="px-2 py-2 text-start font-medium">نرمال‌شده</th>
                    <th className="px-2 py-2 text-start font-medium">وزن</th>
                    <th className="px-2 py-2 text-start font-medium">سهم</th>
                  </tr>
                </thead>
                <tbody>
                  {recommendation.contributions.map((criterion) => (
                    <tr key={criterion.code} className="border-t border-border-subtle">
                      <td className="px-2 py-2">{criterion.labelFa}</td>
                      <td className="px-2 py-2 tabular">
                        {criterion.raw === null ? (
                          <span className="text-ink-muted">ثبت نشده</span>
                        ) : (
                          faDigits(criterion.raw)
                        )}
                      </td>
                      <td className="px-2 py-2 tabular">{percentText(criterion.normalisedBp)}</td>
                      <td className="px-2 py-2 tabular">{percentText(criterion.weightBp)}</td>
                      <td className="px-2 py-2 tabular">{percentText(criterion.contributionBp)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <Card className="min-w-0">
          <CardHeader>
            <CardTitle>داده‌های استفاده‌شده</CardTitle>
            <CardDescription>
              هر مشاهده با شناسه، منبع و دورهٔ خودش؛ این فهرست قابل ردیابی است.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-3 text-sm">
            <ul className="flex flex-col gap-2">
              {recommendation.observationsUsed.map((observation) => (
                <li
                  key={observation.id}
                  className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-border-subtle bg-surface px-3 py-2"
                >
                  <span>{observation.code}</span>
                  <span className="text-xs text-ink-muted">
                    دورهٔ {observation.period} · مقدار {faDigits(observation.raw)}
                  </span>
                </li>
              ))}
            </ul>
            {recommendation.missingCriteria.length > 0 ? (
              <p className="rounded-lg border border-warning/30 bg-warning/10 px-3 py-2 text-xs text-warning">
                این امتیاز با {faDigits(recommendation.missingCriteria.length)} معیار ثبت‌نشده
                محاسبه شده است؛ آن معیارها صفر گرفته‌اند و وزن‌ها بازمحاسبه نشده‌اند.
              </p>
            ) : (
              <p className="text-xs text-ink-muted">هر چهار معیار در این امتیاز استفاده شده‌اند.</p>
            )}
            <p className="break-all text-xs text-ink-muted">
              هش محاسبه:{' '}
              <bdi dir="ltr" className="font-mono">
                {recommendation.calculationHash}
              </bdi>
            </p>
          </CardContent>
        </Card>

        <Card className="min-w-0">
          <CardHeader>
            <CardTitle>هزینهٔ قانونی</CardTitle>
            <CardDescription>
              محاسبه در سرور با موتور ۱۴۰۴ در وضعیت «آمادهٔ بازبینی» انجام شده است؛ نتیجه قطعی و
              مصوب نیست.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-2 text-sm">
            <dl className="flex flex-col gap-2">
              <div className="flex items-center justify-between gap-3">
                <dt className="text-ink-muted">حقوق ماهانهٔ ناخالص</dt>
                <dd className="tabular">{rialNumber(statutory.gross_monthly_rial)}</dd>
              </div>
              <div className="flex items-center justify-between gap-3">
                <dt className="text-ink-muted">بیمهٔ سهم کارمند (۷٪)</dt>
                <dd className="tabular">{rialNumber(statutory.employee_sso_7pct_rial)}</dd>
              </div>
              <div className="flex items-center justify-between gap-3">
                <dt className="text-ink-muted">مالیات بر درآمد</dt>
                <dd className="tabular">{rialNumber(statutory.income_tax_rial)}</dd>
              </div>
              <div className="flex items-center justify-between gap-3 border-t border-border-subtle pt-2">
                <dt className="font-medium">خالص پرداختی ماهانه</dt>
                <dd className="font-semibold tabular">{rialNumber(statutory.net_rial)}</dd>
              </div>
              <div className="flex items-center justify-between gap-3">
                <dt className="text-ink-muted">هزینهٔ کل ماهانهٔ کارفرما</dt>
                <dd className="tabular">
                  {rialNumber(statutory.total_monthly_employer_cost_rial)}
                </dd>
              </div>
              <div className="flex items-center justify-between gap-3">
                <dt className="text-ink-muted">هزینهٔ کل سالانه (۱۲ ماه)</dt>
                <dd className="tabular">{rialNumber(statutory.annual_ctc_12month_rial)}</dd>
              </div>
              <div className="flex items-center justify-between gap-3">
                <dt className="text-ink-muted">ذخیرهٔ ماهانهٔ سنوات / عیدی</dt>
                <dd className="tabular">
                  {rialNumber(statutory.monthly_sanavat_accrual_rial)} /{' '}
                  {rialNumber(statutory.monthly_eydi_accrual_rial)}
                </dd>
              </div>
            </dl>
            {currentStatutory !== null ? (
              <p className="rounded-lg border border-border-subtle bg-surface px-3 py-2 text-xs text-ink-muted">
                حقوق فعلی هم هزینه شده است: خالص {rialNumber(currentStatutory.net_rial)} · هزینهٔ
                کارفرما {rialNumber(currentStatutory.total_monthly_employer_cost_rial)}
              </p>
            ) : null}
            <p className="text-xs text-ink-muted">
              نسخهٔ قانونی: <bdi dir="ltr">{statutory.statutory_version}</bdi> · وضعیت قاعده:{' '}
              {statutory.rule_set_status} · تأییدشده: {statutory.is_verified ? 'بله' : 'خیر'} ·
              ماندهٔ گرد کردن: {rialNumber(statutory.rounding_residual_rial)}
            </p>
            <p className="break-all text-xs text-ink-muted">
              هش موتور:{' '}
              <bdi dir="ltr" className="font-mono">
                {statutory.calculation_hash}
              </bdi>
            </p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>توضیح و محدودیت‌ها</CardTitle>
          <CardDescription>دلیل تولید پیشنهاد و آنچه این پیشنهاد نمی‌داند.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-3 text-sm">
          <ul className="list-inside list-disc text-ink-muted">
            {recommendation.explanation.reasons.map((reason) => (
              <li key={reason}>{reason}</li>
            ))}
          </ul>
          {recommendation.explanation.warnings.map((warning) => (
            <p
              key={warning}
              className="rounded-lg border border-warning/30 bg-warning/10 px-3 py-2 text-xs text-warning"
            >
              {warning}
            </p>
          ))}
          {recommendation.explanation.dataQuality.length > 0 ? (
            <div className="rounded-lg border border-border-subtle bg-surface px-3 py-2 text-xs text-ink-muted">
              <p className="font-medium text-ink">محدودیت کیفیت داده</p>
              <ul className="mt-1 list-inside list-disc">
                {recommendation.explanation.dataQuality.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          ) : null}
        </CardContent>
      </Card>

      <Card className="min-w-0">
        <CardHeader>
          <CardTitle>تصمیم مدیر</CardTitle>
          <CardDescription>
            تصمیم نهایی با مدیر است. مبلغ ویرایش‌شده در کنار پیشنهاد اصلی و دلیل ذخیره می‌شود و
            رکورد تصمیم قابل تغییر نیست.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {decision ? (
            <div className="flex flex-col gap-3 text-sm">
              <div className="flex flex-wrap items-center gap-2">
                <Badge tone={DECISION_TONES[decision.action]}>
                  {DECISION_LABELS[decision.action]}
                </Badge>
                <span className="text-xs text-ink-muted">
                  ثبت در {isoDateText(decision.decidedAt)}
                </span>
              </div>
              {decision.editedGrossRial !== null ? (
                <p>
                  مبلغ ویرایش‌شده:{' '}
                  <span className="font-medium tabular">{rialText(decision.editedGrossRial)}</span>{' '}
                  <span className="text-xs text-ink-muted">
                    (پیشنهاد اصلی: {rialText(recommendation.suggestedGrossRial)})
                  </span>
                </p>
              ) : null}
              <p className="rounded-lg border border-border-subtle bg-surface px-3 py-2">
                {decision.comment === '' ? 'بدون توضیح' : decision.comment}
              </p>
              <p className="text-xs text-ink-muted">
                این تصمیم در پایگاه‌داده ذخیره شده است و در سطح پایگاه‌داده اجازهٔ ویرایش یا حذف
                ندارد. زنجیرهٔ هش کامل حسابرسی (`P0-T10`) هنوز پیاده نشده است.
              </p>
              <div className="flex flex-wrap gap-2">
                <Button asChild variant="secondary">
                  <Link to="/prototype">بازگشت به داشبورد</Link>
                </Button>
                <Button asChild variant="ghost">
                  <Link to={`/prototype/people/${recommendation.personId}`}>
                    مشاهدهٔ کارمند
                  </Link>
                </Button>
              </div>
            </div>
          ) : (
            <form className="flex flex-col gap-4" onSubmit={(event) => void onDecide(event)}>
              <fieldset className="flex flex-col gap-2">
                <legend className="mb-1 text-sm font-medium text-ink">نوع تصمیم</legend>
                {ACTIONS.map((option) => (
                  <label
                    key={option.value}
                    className="flex cursor-pointer items-center gap-3 rounded-lg border border-border-subtle bg-surface px-3 py-2 text-sm"
                  >
                    <input
                      type="radio"
                      name="decision-action"
                      value={option.value}
                      checked={action === option.value}
                      onChange={() => setAction(option.value)}
                    />
                    <span>{option.labelFa}</span>
                  </label>
                ))}
              </fieldset>

              {action === 'edit' ? (
                <Input
                  label="مبلغ ویرایش‌شده (ریال)"
                  value={editedGross}
                  onChange={(event) => setEditedGross(event.target.value)}
                  dir="ltr"
                  inputMode="numeric"
                  hint={`پیشنهاد اصلی: ${rialText(recommendation.suggestedGrossRial)}`}
                  required
                />
              ) : null}

              <div className="flex flex-col gap-2">
                <label htmlFor="decision-comment" className="text-sm font-medium text-ink">
                  توضیح مدیر
                </label>
                <textarea
                  id="decision-comment"
                  value={comment}
                  onChange={(event) => setComment(event.target.value)}
                  rows={3}
                  maxLength={500}
                  className="w-full rounded-lg border border-border-subtle bg-surface-raised px-3 py-2 text-sm text-ink"
                  placeholder="مثلاً: با توجه به کیفیت کار و حضور، پیشنهاد تأیید می‌شود."
                />
                <p className="text-xs text-ink-muted">برای ویرایش و رد، نوشتن دلیل الزامی است.</p>
              </div>

              {error ? (
                <p
                  role="alert"
                  className="rounded-lg border border-danger/40 bg-danger/5 px-3 py-2 text-sm text-danger"
                >
                  {error}
                </p>
              ) : null}

              <Button type="submit" size="lg" disabled={busy}>
                {busy ? 'در حال ثبت…' : 'ثبت تصمیم'}
              </Button>
            </form>
          )}
        </CardContent>
      </Card>
    </>
  );
}
