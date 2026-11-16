import { PageHeader } from '@/app/page-header';
import { Alert } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { EmptyState, ErrorState, LoadingSkeleton, LoadingState } from '@/components/ui/states';
import { Bdi, LtrRun } from '@/components/ui/bidi';
import { ProvenanceFooter, RuleSetWarning } from '@/components/domain/rule-set-warning';
import { formatMoney, formatMoneyPreferringToman, formatPercentFromRate } from '@/lib/money';
import { toAsciiDigits, toPersianDigits } from '@/lib/numerals';
import {
  SYNTHETIC_MONEY_SAMPLES,
  SYNTHETIC_PROVENANCE,
  SYNTHETIC_RATES,
  SYNTHETIC_VERIFIED_PROVENANCE,
} from '@/dev/fixtures';

/**
 * Development-only preview. Mounted only when `import.meta.env.DEV` is true.
 *
 * This is the **only** place synthetic values are rendered, and every block is
 * labelled as synthetic. It is not a feature surface and it must never be
 * deployed as one.
 */
export default function DevPreviewPage() {
  return (
    <>
      <PageHeader
        eyebrow="پیش‌نمایش توسعه"
        title="نمونه‌های سامانه طراحی (داده ساختگی)"
        description="این صفحه فقط برای بازبینی چشمی اجزای رابط در حالت راست‌به‌چپ است. همه مقادیر ساختگی و برچسب‌گذاری‌شده‌اند."
        actions={<Badge tone="danger">داده ساختگی</Badge>}
      />

      <Alert tone="danger" title="هیچ داده واقعی در این صفحه نیست">
        <p>
          این مسیر در ساخت تولیدی وجود ندارد. مقادیر آن از سرویس دریافت نشده‌اند، هیچ
          محاسبه‌ای را بازتولید نمی‌کنند و مبنای هیچ تصمیمی نیستند.
        </p>
      </Alert>

      <Card>
        <CardHeader>
          <CardTitle>قالب‌بندی مبلغ ریالی</CardTitle>
          <CardDescription>
            واحد همیشه صریح است. نمایش تومان فقط برای مبالغ بخش‌پذیر بر ۱۰ مجاز است و در
            غیر این صورت رد می‌شود (بدون گرد کردن).
          </CardDescription>
        </CardHeader>
        <CardContent>
          <table className="w-full border-collapse text-sm">
            <caption className="sr-only">نمونه‌های ساختگی قالب‌بندی مبلغ</caption>
            <thead>
              <tr className="border-b border-border-subtle text-start text-xs text-ink-muted">
                <th scope="col" className="py-2 text-start font-medium">ریال (ماشینی)</th>
                <th scope="col" className="py-2 text-start font-medium">نمایش ریالی</th>
                <th scope="col" className="py-2 text-start font-medium">نمایش تومانی</th>
                <th scope="col" className="py-2 text-start font-medium">توضیح</th>
              </tr>
            </thead>
            <tbody className="tabular">
              {SYNTHETIC_MONEY_SAMPLES.map((sample) => {
                const rial = formatMoney(sample.rial, 'rial');
                const toman = formatMoney(sample.rial, 'toman');
                return (
                  <tr key={sample.id} className="border-b border-border-subtle align-top">
                    <td className="py-2">
                      <LtrRun className="font-mono text-xs">{sample.rial}</LtrRun>
                    </td>
                    <td className="py-2">{rial.ok ? rial.value.text : rial.messageFa}</td>
                    <td className="py-2">
                      {toman.ok ? (
                        toman.value.text
                      ) : (
                        <span className="text-ink-muted">— نمایش تومان مجاز نیست</span>
                      )}
                    </td>
                    <td className="py-2 text-xs text-ink-muted">{sample.noteFa}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          <p className="mt-3 text-xs text-ink-muted">
            نمونه ترجیح واحد: {formatMoneyPreferringToman('123456785').text}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>درصد و نرخ</CardTitle>
          <CardDescription>نرخ به‌صورت رشته با مقیاس صریح می‌رسد؛ یک رقم اعشار.</CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="flex flex-wrap gap-3 text-sm">
            {SYNTHETIC_RATES.map((rate) => (
              <li key={rate} className="rounded-lg border border-border-subtle px-3 py-1.5">
                <Bdi className="font-mono text-xs text-ink-muted">{rate}</Bdi>
                <span className="mx-2">→</span>
                <span className="tabular">{formatPercentFromRate(rate) ?? 'نامعتبر'}</span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>سیاست ارقام</CardTitle>
          <CardDescription>نمایش فارسی، ورودی سه‌گانه، لایه ماشینی ASCII.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-2 text-sm">
          <p>
            نمایش: <span className="tabular">{toPersianDigits('1404')}</span>
          </p>
          <p>
            ورودی فارسی و عربی:{' '}
            <LtrRun className="font-mono">{toAsciiDigits('۱۲۳٤٥٦')}</LtrRun>
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>هشدار نسخه قوانین و منشأ رقم</CardTitle>
          <CardDescription>
            سه واقعیت جداگانه: نسخه، وضعیت تأیید و پرچم تأیید. هرگز در یک برچسب ادغام
            نمی‌شوند.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <RuleSetWarning provenance={SYNTHETIC_PROVENANCE} />
          <ProvenanceFooter provenance={SYNTHETIC_PROVENANCE} />
          <p className="text-xs text-ink-muted">
            نمونه نسخه تأییدشده (هشدار نمایش داده نمی‌شود):{' '}
            {SYNTHETIC_VERIFIED_PROVENANCE.rule_set_status}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>حالت‌های بارگذاری، خالی و خطا</CardTitle>
          <CardDescription>هر سه حالت دسترس‌پذیر و اعلام‌شده هستند.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <LoadingState />
          <LoadingSkeleton rows={2} />
          <EmptyState
            title="نمونه حالت خالی (ساختگی)"
            description="هیچ ردیفی برای نمایش وجود ندارد. این متن ساختگی است و به داده واقعی اشاره نمی‌کند."
          />
          <ErrorState
            title="نمونه حالت خطا (ساختگی)"
            description="در حالت واقعی، پیام از کاتالوگ خطا و شناسه پیگیری از سرور می‌آید."
            correlationId="synthetic-correlation-id"
          />
        </CardContent>
      </Card>
    </>
  );
}
