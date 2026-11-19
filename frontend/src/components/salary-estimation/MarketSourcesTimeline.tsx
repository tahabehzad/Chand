/**
 * Market Sources Timeline — Persian RTL.
 *
 * Renders verified labor market sources on an interactive vertical timeline
 * sorted by date (most recent first).
 *
 * Displays:
 *   - Source name and verified badge
 *   - Sample count in Persian numerals
 *   - Median salary in Toman via `formatMoney()`
 *   - Collection date formatted with Intl.DateTimeFormat('fa-IR', { timeZone: 'Asia/Tehran' })
 */

import { formatMoney } from '@/lib/money';
import { toPersianDigits } from '@/lib/numerals';
import type { MarketDataRow } from '@/api/salary-estimation';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export type MarketSourcesTimelineProps = {
  dataSources: string[];
  marketRows: MarketDataRow[];
  dataCollectedAt?: string | null;
  className?: string;
};

function tomanText(rialValue: number): string {
  const toman = formatMoney(rialValue, 'toman');
  if (toman.ok) return toman.value.text;
  const rial = formatMoney(rialValue, 'rial');
  return rial.ok ? rial.value.text : '—';
}

function faDate(isoValue: string | null): string {
  if (!isoValue) return 'نامشخص';
  try {
    return new Intl.DateTimeFormat('fa-IR', {
      dateStyle: 'medium',
      timeZone: 'Asia/Tehran',
    }).format(new Date(isoValue));
  } catch {
    return isoValue.slice(0, 10);
  }
}

export function MarketSourcesTimeline({
  dataSources,
  marketRows,
  dataCollectedAt,
  className,
}: MarketSourcesTimelineProps) {
  // Sort most recent first
  const sortedRows = [...marketRows].sort((a, b) => {
    const timeA = a.collected_at ? new Date(a.collected_at).getTime() : 0;
    const timeB = b.collected_at ? new Date(b.collected_at).getTime() : 0;
    return timeB - timeA;
  });

  return (
    <Card className={className}>
      <CardContent className="space-y-6 p-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-base font-bold text-ink">خط زمانی منابع دادهٔ بازار</h3>
            <p className="mt-0.5 text-xs text-ink-muted">
              استعلام‌های معتبر و پایگاه‌های استخدامی مبنای محاسبه به ترتیب تاریخ استخراج
            </p>
          </div>
          {dataCollectedAt && (
            <Badge tone="neutral" className="text-xs">
              آخرین به‌روزرسانی: {faDate(dataCollectedAt)}
            </Badge>
          )}
        </div>

        {/* Source overview pills */}
        {dataSources && dataSources.length > 0 && (
          <div className="flex flex-wrap items-center gap-1.5 pt-1">
            <span className="text-xs font-medium text-ink-muted me-1">پایگاه‌های فعال:</span>
            {dataSources.map((src) => (
              <Badge key={src} tone="neutral" className="text-xs">
                🌐 {src}
              </Badge>
            ))}
          </div>
        )}

        {sortedRows.length === 0 ? (
          <div className="rounded-xl border border-border-subtle bg-surface p-4 text-center text-sm text-ink-muted">
            منبع مشاهده‌ای مستقیمی ثبت نشده است (استناد به داده‌های کلان تجمیعی).
          </div>
        ) : (
          <div className="relative ps-7 space-y-4 before:absolute before:top-3 before:bottom-3 before:start-2.5 before:w-0.5 before:bg-border-subtle">
            {sortedRows.map((row, idx) => (
              <div
                key={`${row.source}-${row.collected_at}-${idx}`}
                className="relative group transition-all duration-200"
                style={{
                  animation: 'fadeUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) both',
                  animationDelay: `${idx * 60}ms`,
                }}
              >
                {/* Timeline node icon */}
                <div className="absolute -start-7 top-3 flex size-5 items-center justify-center rounded-full border-2 border-brand bg-surface-raised shadow-sm ring-4 ring-surface">
                  <span className="size-1.5 rounded-full bg-brand group-hover:scale-125 transition-transform" />
                </div>

                {/* Timeline Card */}
                <div className="rounded-xl border border-border-subtle bg-surface p-4 transition-all hover:border-brand/30 hover:shadow-sm">
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border-subtle/60 pb-2.5">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-sm text-ink">{row.source}</span>
                      <span className="rounded bg-surface-muted px-2 py-0.5 text-[11px] text-ink-muted border border-border-subtle">
                        {row.city} · {row.seniority_level}
                      </span>
                    </div>
                    <time className="text-xs tabular-nums text-ink-muted font-medium">
                      📅 {faDate(row.collected_at)}
                    </time>
                  </div>

                  <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-3 text-xs">
                    <div>
                      <span className="text-ink-muted block text-[11px]">حجم نمونه:</span>
                      <span className="font-bold tabular-nums text-ink text-sm">
                        {toPersianDigits(String(row.sample_count))} نمونه
                      </span>
                    </div>

                    <div>
                      <span className="text-ink-muted block text-[11px]">میانهٔ حقوق منبع:</span>
                      <span className="font-bold tabular-nums text-brand-strong text-sm">
                        {tomanText(row.median_salary_rial)}
                      </span>
                    </div>

                    <div className="col-span-2 sm:col-span-1">
                      <span className="text-ink-muted block text-[11px]">دامنهٔ گزارش‌شده:</span>
                      <span className="tabular-nums text-ink text-xs">
                        {tomanText(row.min_salary_rial)} – {tomanText(row.max_salary_rial)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
