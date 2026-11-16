import { PageHeader } from '@/app/page-header';
import { Alert } from '@/components/ui/alert';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { Badge } from '@/components/ui/badge';
import { Bdi } from '@/components/ui/bidi';
import { useHealthLive } from '@/api/queries';
import { CONTRACTS } from '@/api/contracts';
import { isApiError } from '@/api/errors';
import { NAV_ITEMS } from '@/app/navigation';

function ServiceStatus() {
  const health = useHealthLive();

  if (health.isPending) {
    return <LoadingState label="در حال بررسی وضعیت سرویس…" />;
  }

  if (health.isError) {
    const error = health.error;
    return (
      <ErrorState
        title="سرویس در دسترس نیست"
        description={
          isApiError(error)
            ? error.messageFa
            : 'ارتباط با سرویس برقرار نشد. هیچ داده‌ای به‌جای پاسخ واقعی نمایش داده نمی‌شود.'
        }
        correlationId={isApiError(error) ? error.correlationId : undefined}
        onRetry={() => void health.refetch()}
      />
    );
  }

  return (
    <div className="flex flex-wrap items-center gap-3">
      <Badge tone="success">پاسخ سرویس: {health.data.status}</Badge>
      <span className="text-sm text-ink-muted">
        مسیر بررسی‌شده: <Bdi className="font-mono">{CONTRACTS.healthLive.path}</Bdi>
      </span>
    </div>
  );
}

export default function SystemPage() {
  const awaitingContracts = NAV_ITEMS.filter(
    (item) => item.contract !== undefined && item.contract.availability !== 'delivered',
  );

  return (
    <>
      <PageHeader
        eyebrow="لایه رابط کاربری"
        title="نمای کلی"
        description="این نسخه شامل پایه رابط فارسی، راست‌به‌چپ، مسیرها و مرز کلاینت API است. هیچ نتیجه مالی یا قانونی در آن تولید نمی‌شود."
      />

      <Alert tone="info" title="قرارداد محاسبه تحویل شده است">
        <p>
          قرارداد شبیه‌سازی حقوق (وظیفه <Bdi>P1-T19</Bdi>) پیاده‌سازی و تحویل شده
          است: <Bdi>POST /api/v1/simulations/gross-to-net</Bdi> روی مجموعه قواعد
          تأییدشده ۱۴۰۴ محاسبه می‌کند و هر دو حالت ماده ۱۳۷ را برمی‌گرداند. قرارداد
          احراز هویت (وظیفه <Bdi>P0-T18</Bdi>) هنوز تحویل نشده است، بنابراین
          صفحه‌های ورود فقط نمایشی می‌مانند.
        </p>
      </Alert>

      <Card>
        <CardHeader>
          <CardTitle>وضعیت اتصال</CardTitle>
          <CardDescription>
            بک‌اند دو مسیر ارائه می‌دهد: بررسی زنده‌بودن سرویس و محاسبه ناخالص به
            خالص. سایر بخش‌ها به‌صراحت به‌عنوان «بدون قرارداد» علامت‌گذاری شده‌اند.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ServiceStatus />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>بخش‌های در انتظار قرارداد</CardTitle>
          <CardDescription>
            هر بخش، وظیفه مالک قرارداد خود را نشان می‌دهد. هیچ درخواستی به این مسیرها ارسال
            نمی‌شود و داده ساختگی جای پاسخ واقعی نمی‌گذارد.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {awaitingContracts.length === 0 ? (
            <EmptyState
              title="همه بخش‌ها متصل هستند"
              description="در حال حاضر هیچ بخشی در انتظار قرارداد نیست."
            />
          ) : (
            <ul className="flex flex-col divide-y divide-border-subtle">
              {awaitingContracts.map((item) => (
                <li key={item.id} className="flex flex-wrap items-center justify-between gap-2 py-3">
                  <span className="text-sm font-medium text-ink">{item.labelFa}</span>
                  <span className="flex flex-wrap items-center gap-2 text-xs text-ink-muted">
                    <Bdi className="font-mono">{item.contract?.id}</Bdi>
                    <Badge tone="neutral">مالک: {item.ownerTask}</Badge>
                    <Badge tone="warning">قرارداد تحویل نشده</Badge>
                  </span>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>تصمیم‌ها و کارهای باقی‌مانده</CardTitle>
          <CardDescription>
            مواردی که آگاهانه پیاده‌سازی نشده‌اند، با دلیل ثبت شده‌اند:
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="flex list-disc flex-col gap-2 ps-5 text-sm text-ink-muted">
            <li>
              <Bdi>DEC-006</Bdi> باز است: هیچ کتابخانه تبدیل تقویم شمسی و هیچ خط لوله PDF
              انتخاب نشده است. تبدیل تاریخ در مرز نمایش به یک درگاه (<Bdi>JalaliConverter</Bdi>)
              سپرده شده و پیاده‌سازی نشده است؛ محاسبه دستی تقویم ممنوع است.
            </li>
            <li>
              صفحه‌های ورود و تأیید دو‌مرحله‌ای فقط نمایشی هستند: هیچ توکنی ذخیره نمی‌شود و
              هیچ معنای نشستی از فرض ساخته نمی‌شود.
            </li>
            <li>
              محافظ مسیر بر پایه مجوز پیاده‌سازی نشده است؛ اعمال مجوز سمت سرور انجام می‌شود و
              رابط فقط نمایشی است.
            </li>
            <li>
              کاتالوگ خطای رابط هم‌اکنون همان کدهای ماشینی خود بک‌اند را می‌خواند؛
              مسیرهای بدون قرارداد همچنان با کد وضعیت HTTP نگاشت می‌شوند.
            </li>
          </ul>
        </CardContent>
      </Card>
    </>
  );
}
