import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { PageHeader } from '@/app/page-header';
import { Icon } from '@/components/icon';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { EmptyState, ErrorState } from '@/components/ui/states';
import { getDashboard, isPrototypeError, listPendingRecommendations } from '@/prototype/api';
import type {
  DashboardSummary,
  DecisionAction,
  RecommendationSummary,
} from '@/prototype/types';
import type { IconName } from '@/lib/icons';
import { PrototypeNotice } from './prototype-notice';
import { faDigits, isoDateText, rialText } from './format';

const ACTION_LABELS: Record<DecisionAction, string> = {
  approve: 'تأیید',
  edit: 'ویرایش',
  reject: 'رد',
};

const ACTION_TONES: Record<DecisionAction, 'success' | 'info' | 'danger'> = {
  approve: 'success',
  edit: 'info',
  reject: 'danger',
};

export default function PrototypeDashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [pending, setPending] = useState<RecommendationSummary[]>([]);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (): Promise<void> => {
    try {
      setError(null);
      const [dashboard, queue] = await Promise.all([
        getDashboard(),
        listPendingRecommendations(),
      ]);
      setSummary(dashboard);
      setPending(queue);
    } catch (caught) {
      setError(
        isPrototypeError(caught) ? caught.message : 'دریافت خلاصهٔ وضعیت ناموفق بود.',
      );
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const stats: Array<{ id: string; labelFa: string; value: number; icon: IconName }> =
    summary === null
      ? []
      : [
          { id: 'people', labelFa: 'افراد ثبت‌شده', value: summary.peopleCount, icon: 'overview' },
          {
            id: 'observations',
            labelFa: 'مشاهدات معتبر',
            value: summary.validObservationCount,
            icon: 'check',
          },
          {
            id: 'pending',
            labelFa: 'پیشنهادهای در انتظار تصمیم',
            value: summary.pendingCount,
            icon: 'alert',
          },
          {
            id: 'decided',
            labelFa: 'تصمیم‌های ثبت‌شده',
            value: summary.decidedCount,
            icon: 'audit',
          },
        ];

  return (
    <>
      <PageHeader
        eyebrow="فضای مدیر · ارزیابی و جبران خدمت"
        title="ارزیابی و پیشنهاد جبران خدمت"
        description="یک جریان کامل: ثبت کارمند، ورود دادهٔ عملکرد و شواهد، امتیاز قابل توضیح، پیشنهاد مشورتی و تصمیم ماندگار مدیر."
        actions={
          <Button asChild>
            <Link to="/prototype/people">مدیریت کارکنان</Link>
          </Button>
        }
      />

      <PrototypeNotice />

      {error ? (
        <ErrorState description={error} onRetry={() => void load()} />
      ) : null}

      <section aria-label="خلاصهٔ وضعیت" className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.id}>
            <CardContent>
              <div className="mb-4 flex items-center justify-between gap-2">
                <h2 className="text-sm font-medium text-ink-muted">{stat.labelFa}</h2>
                <span className="summary-icon">
                  <Icon name={stat.icon} />
                </span>
              </div>
              <p className="text-2xl font-semibold tabular">{faDigits(stat.value)}</p>
            </CardContent>
          </Card>
        ))}
        {summary === null && error === null
          ? [0, 1, 2, 3].map((index) => (
              <Card key={`skeleton-${index}`}>
                <CardContent>
                  <div className="h-16 animate-pulse rounded bg-surface-muted motion-reduce:animate-none" />
                </CardContent>
              </Card>
            ))
          : null}
      </section>

      <div className="grid gap-5 xl:grid-cols-[minmax(0,1.6fr)_minmax(0,1fr)]">
        <Card>
          <CardHeader>
            <CardTitle>پیشنهادهای در انتظار تصمیم</CardTitle>
            <CardDescription>
              پیشنهادهای محاسبه‌شده در سرور که هنوز تأیید، ویرایش یا رد نشده‌اند.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {summary !== null && pending.length === 0 ? (
              <EmptyState
                title="صف تصمیم خالی است"
                description="برای یک کارمند دادهٔ عملکرد ثبت کنید و از صفحهٔ او «محاسبهٔ امتیاز و پیشنهاد» را بزنید."
                action={
                  <Button asChild variant="secondary" size="sm">
                    <Link to="/prototype/people">رفتن به کارکنان</Link>
                  </Button>
                }
              />
            ) : (
              <ul className="flex flex-col gap-3">
                {pending.map((recommendation) => (
                  <li key={recommendation.id}>
                    <Link
                      to={`/prototype/recommendations/${recommendation.id}`}
                      className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-border-subtle bg-surface px-3 py-2.5 text-sm hover:border-brand/30"
                    >
                      <span className="flex flex-col gap-0.5">
                        <span className="font-medium text-ink">{recommendation.personName}</span>
                        <span className="text-xs text-ink-muted">
                          دورهٔ {recommendation.period || '—'} · {isoDateText(recommendation.createdAt)}
                        </span>
                      </span>
                      <span className="flex items-center gap-2">
                        <span className="text-xs text-ink-muted">
                          امتیاز {faDigits(recommendation.score100)} · پیشنهاد{' '}
                          {rialText(recommendation.suggestedGrossRial)}
                        </span>
                        <Icon name="chevron-next" />
                      </span>
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>آخرین تصمیم‌ها</CardTitle>
            <CardDescription>تأیید، ویرایش یا ردِ ثبت‌شده توسط مدیر</CardDescription>
          </CardHeader>
          <CardContent>
            {summary !== null && summary.recentDecisions.length === 0 ? (
              <EmptyState
                title="هنوز تصمیمی ثبت نشده"
                description="پس از بررسی یک پیشنهاد، تصمیم شما با زمان و توضیح در همین فهرست ثبت می‌شود."
              />
            ) : (
              <ul className="flex flex-col gap-3">
                {summary?.recentDecisions.map((decision) => (
                  <li
                    key={decision.id}
                    className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-border-subtle bg-surface px-3 py-2.5 text-sm"
                  >
                    <Link
                      to={`/prototype/recommendations/${decision.recommendationId}`}
                      className="font-medium text-brand"
                    >
                      {decision.personName}
                    </Link>
                    <span className="text-xs text-ink-muted">
                      امتیاز {faDigits(decision.score100)} · {isoDateText(decision.decidedAt)}
                    </span>
                    <Badge tone={ACTION_TONES[decision.action]}>{ACTION_LABELS[decision.action]}</Badge>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>مسیر کار</CardTitle>
          <CardDescription>گام‌های واقعی همین سامانه؛ هر گام روی سرور ثبت می‌شود</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-3 text-sm sm:grid-cols-2 xl:grid-cols-4">
          <Link
            to="/prototype/people"
            className="flex items-center justify-between rounded-lg border border-border-subtle bg-surface px-3 py-2.5 text-brand"
          >
            <span>۱. ثبت یا انتخاب کارمند</span>
            <Icon name="chevron-next" />
          </Link>
          <div className="flex items-center justify-between rounded-lg border border-border-subtle bg-surface px-3 py-2.5 text-ink-muted">
            <span>۲. دادهٔ عملکرد و شواهد</span>
            <Icon name="chevron-next" />
          </div>
          <div className="flex items-center justify-between rounded-lg border border-border-subtle bg-surface px-3 py-2.5 text-ink-muted">
            <span>۳. امتیاز و پیشنهاد</span>
            <Icon name="chevron-next" />
          </div>
          <div className="flex items-center justify-between rounded-lg border border-border-subtle bg-surface px-3 py-2.5 text-ink-muted">
            <span>۴. تصمیم مدیر</span>
            <Icon name="check" />
          </div>
        </CardContent>
      </Card>
    </>
  );
}
