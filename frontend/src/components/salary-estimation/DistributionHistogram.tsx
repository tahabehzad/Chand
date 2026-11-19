/**
 * Visual Salary Distribution Histogram — Persian RTL.
 *
 * Displays salary distribution buckets as smooth, rounded vertical bars with
 * gradient fills. Features:
 *   - Hover tooltip showing exact sample count, Toman range, and cohort share.
 *   - Prominent highlight on the bucket containing the median salary estimate.
 *   - Staggered upward growth animation on mount (50ms stagger per bar).
 *   - Pure CSS/Tailwind (no chart library).
 */

import { useEffect, useState } from 'react';
import { formatMoney } from '@/lib/money';
import { toPersianDigits } from '@/lib/numerals';
import type { DistributionBucket } from '@/api/salary-estimation';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export type DistributionHistogramProps = {
  distribution: DistributionBucket[];
  medianSalaryRial: number;
  className?: string;
};

function tomanText(rialValue: number): string {
  const roundedTo10 = Math.round(rialValue / 10) * 10;
  const toman = formatMoney(roundedTo10, 'toman');
  if (toman.ok) return toman.value.text;
  return `${toPersianDigits(String(Math.round(rialValue / 10)))} تومان`;
}

function shortToman(rialValue: number): string {
  const roundedTo10 = Math.round(rialValue / 10) * 10;
  const toman = formatMoney(roundedTo10, 'toman');
  if (toman.ok) return toman.value.amount;
  return toPersianDigits(String(Math.round(rialValue / 10)));
}

export function DistributionHistogram({
  distribution,
  medianSalaryRial,
  className,
}: DistributionHistogramProps) {
  const [mounted, setMounted] = useState(false);
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  useEffect(() => {
    const handle = requestAnimationFrame(() => setMounted(true));
    return () => cancelAnimationFrame(handle);
  }, []);

  if (!distribution || distribution.length === 0) {
    return null;
  }

  const maxCount = Math.max(1, ...distribution.map((b) => b.count));
  const totalCount = distribution.reduce((sum, b) => sum + b.count, 0);

  // Identify which bucket contains the median salary
  const medianBucketIndex = distribution.findIndex(
    (b) => medianSalaryRial >= b.min_rial && medianSalaryRial <= b.max_rial,
  );

  const activeIndex = hoveredIndex !== null ? hoveredIndex : medianBucketIndex >= 0 ? medianBucketIndex : 0;
  const activeBucket = distribution[activeIndex] ?? distribution[0];

  return (
    <Card className={className}>
      <CardContent className="space-y-6 p-6">
        {/* Title and interactive inspection banner */}
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-base font-bold text-ink">توزیع حقوق نمونه‌های معتبر بازار</h3>
            <p className="mt-0.5 text-xs text-ink-muted">
              فراوانی آماری نمونه‌های واقعی بر حسب بازه‌های حقوقی ماهانه
            </p>
          </div>
          <Badge tone="neutral" className="text-xs">
            مجموع شواهد: {toPersianDigits(String(totalCount))} نمونه
          </Badge>
        </div>

        {/* Hover / Active Inspector Card */}
        {activeBucket && (
          <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-brand/25 bg-gradient-to-r from-brand/5 via-surface to-surface-raised p-4 text-xs shadow-xs transition-colors">
            <div className="flex items-center gap-2.5">
              <span className="flex size-8 items-center justify-center rounded-xl bg-brand/10 text-brand font-bold text-sm">
                📊
              </span>
              <div>
                <p className="font-bold text-ink">
                  بازه: {tomanText(activeBucket.min_rial)} تا {tomanText(activeBucket.max_rial)}
                </p>
                <p className="text-[11px] text-ink-muted mt-0.5">
                  {toPersianDigits(String(activeBucket.count))} نمونه معتبر (
                  {toPersianDigits(String(Math.round((activeBucket.count / Math.max(1, totalCount)) * 100)))}٪ از کل مشاهدات)
                </p>
              </div>
            </div>

            {activeIndex === medianBucketIndex && (
              <Badge tone="success" className="text-xs font-semibold px-2.5 py-1">
                ★ دربرگیرندهٔ میانهٔ برآورد
              </Badge>
            )}
          </div>
        )}

        {/* Vertical Column Chart Canvas */}
        <div className="relative pt-6">
          <div className="flex h-52 items-end justify-between gap-2 sm:gap-3 border-b border-border-subtle pb-2">
            {distribution.map((bucket, idx) => {
              const isMedian = idx === medianBucketIndex;
              const isHovered = idx === hoveredIndex;
              const heightPct = Math.max(10, (bucket.count / maxCount) * 100);

              return (
                <div
                  key={`${bucket.min_rial}-${bucket.max_rial}`}
                  className="group relative flex flex-1 flex-col items-center justify-end h-full cursor-pointer focus:outline-none"
                  onMouseEnter={() => setHoveredIndex(idx)}
                  onMouseLeave={() => setHoveredIndex(null)}
                  onFocus={() => setHoveredIndex(idx)}
                  tabIndex={0}
                  role="button"
                  aria-label={`بازه ${tomanText(bucket.min_rial)} تا ${tomanText(bucket.max_rial)}: ${bucket.count} نمونه`}
                >
                  {/* Floating count label above bar */}
                  <span
                    className={`mb-1.5 text-[11px] font-bold tabular-nums transition-opacity duration-200 ${
                      isMedian || isHovered ? 'text-brand-strong opacity-100' : 'text-ink-muted opacity-80'
                    }`}
                  >
                    {toPersianDigits(String(bucket.count))}
                  </span>

                  {/* Median Marker Pill */}
                  {isMedian && (
                    <div className="absolute -top-3 z-10 rounded-full bg-brand px-2 py-0.5 text-[9px] font-bold text-white shadow-md animate-bounce">
                      میانه
                    </div>
                  )}

                  {/* Vertical Bar */}
                  <div className="relative w-full rounded-t-xl overflow-hidden bg-surface-muted h-full flex items-end">
                    <div
                      className={`w-full rounded-t-xl transition-all duration-500 ease-out ${
                        isMedian
                          ? 'bg-gradient-to-t from-brand via-accent-teal to-accent-emerald ring-2 ring-brand/50 shadow-md shadow-brand/20'
                          : isHovered
                            ? 'bg-gradient-to-t from-brand/90 to-accent-teal'
                            : 'bg-gradient-to-t from-brand/60 via-accent-teal/70 to-accent-emerald/80'
                      }`}
                      style={{
                        height: `${heightPct}%`,
                        transformOrigin: 'bottom',
                        transform: mounted ? 'scaleY(1)' : 'scaleY(0)',
                        transitionProperty: 'transform, height, background-color',
                        transitionDuration: '600ms',
                        transitionDelay: `${idx * 50}ms`,
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>

          {/* X-Axis Range Labels */}
          <div className="mt-2 flex justify-between gap-1 text-[10px] sm:text-xs text-ink-muted tabular-nums">
            {distribution.map((bucket, idx) => (
              <div
                key={`label-${bucket.min_rial}`}
                className={`flex-1 text-center truncate ${
                  idx === medianBucketIndex ? 'font-bold text-brand-strong' : ''
                }`}
                title={`${tomanText(bucket.min_rial)} – ${tomanText(bucket.max_rial)}`}
              >
                {shortToman(bucket.min_rial)}
              </div>
            ))}
          </div>
          <p className="mt-1 text-center text-[11px] text-ink-muted">
            مقادیر محور افقی بر حسب تومان می‌باشد.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
