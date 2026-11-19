/**
 * Visual Salary Range Gauge / Thermometer — Persian RTL.
 *
 * Displays a horizontal gauge showing the P25–P50–P75 salary spread, with the
 * candidate's median estimate pinned on the track and the legal minimum wage
 * marked as a reference line if available.
 *
 * Pure CSS (Tailwind v4 gradients, logical properties, no chart libraries).
 * Invariant: Every monetary value is converted to Toman strictly through `formatMoney()`.
 */

import { useEffect, useState } from 'react';
import { formatMoney } from '@/lib/money';
import { toPersianDigits } from '@/lib/numerals';
import { Card, CardContent } from '@/components/ui/card';

export type SalaryRangeGaugeProps = {
  minSalaryRial: number; // P25
  medianSalaryRial: number; // P50 / Candidate primary estimate
  maxSalaryRial: number; // P75
  primaryEstimateRial?: number;
  legalMinimumWageRial?: number | null;
  className?: string;
};

function tomanText(rialValue: number): string {
  const roundedTo10 = Math.round(rialValue / 10) * 10;
  const toman = formatMoney(roundedTo10, 'toman');
  if (toman.ok) return toman.value.text;
  return `${toPersianDigits(String(Math.round(rialValue / 10)))} تومان`;
}

export function SalaryRangeGauge({
  minSalaryRial,
  medianSalaryRial,
  maxSalaryRial,
  primaryEstimateRial,
  legalMinimumWageRial,
  className,
}: SalaryRangeGaugeProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const handle = requestAnimationFrame(() => setMounted(true));
    return () => cancelAnimationFrame(handle);
  }, []);

  const estimateRial = primaryEstimateRial ?? medianSalaryRial;
  const hasLegalMin = legalMinimumWageRial !== null && legalMinimumWageRial !== undefined && legalMinimumWageRial > 0;

  // Compute a balanced scale that comfortably accommodates legal min and the P75 spread
  const scaleMin = hasLegalMin
    ? 0
    : Math.max(0, minSalaryRial - (maxSalaryRial - minSalaryRial) * 0.4);
  const scaleMax = maxSalaryRial * 1.15;

  const toPct = (val: number): number => {
    if (scaleMax <= scaleMin) return 50;
    const raw = ((val - scaleMin) / (scaleMax - scaleMin)) * 100;
    return Math.min(96, Math.max(4, raw));
  };

  const p25Pct = toPct(minSalaryRial);
  const p50Pct = toPct(estimateRial);
  const p75Pct = toPct(maxSalaryRial);
  const legalMinPct = hasLegalMin ? toPct(legalMinimumWageRial) : null;

  const rangeWidth = Math.max(2, p75Pct - p25Pct);

  return (
    <Card className={className}>
      <CardContent className="space-y-6 p-6">
        {/* Header summary */}
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-base font-bold text-ink">محدودهٔ حقوق بازار کار</h3>
            <p className="mt-0.5 text-xs text-ink-muted">
              دامنهٔ حقوق پیشنهادی بر اساس صدک‌های ۲۵ تا ۷۵ نمونه‌های معتبر
            </p>
          </div>
          <span className="inline-flex items-center gap-1.5 rounded-full border border-brand/20 bg-brand/5 px-3 py-1 text-xs font-semibold text-brand-strong">
            طیف صدک‌ها: {tomanText(minSalaryRial)} تا {tomanText(maxSalaryRial)}
          </span>
        </div>

        {/* The Gauge Component */}
        <div className="relative pt-12 pb-8">
          {/* Median Marker / Pin (Above the track) */}
          <div
            className="absolute top-0 z-20 flex flex-col items-center transition-all duration-1000 ease-out"
            style={{
              insetInlineStart: mounted ? `${p50Pct}%` : '50%',
              transform: 'translateX(50%)',
            }}
          >
            <div className="flex items-center gap-1.5 rounded-xl border border-brand/40 bg-surface-raised px-3 py-1.5 text-xs font-bold text-brand-strong shadow-lg shadow-brand/20 ring-2 ring-brand/10">
              <span className="size-2 rounded-full bg-brand animate-pulse" />
              <span>میانه: {tomanText(estimateRial)}</span>
            </div>
            {/* Arrow pointer down */}
            <div className="size-2 -mt-0.5 rotate-45 border-b border-e border-brand/40 bg-surface-raised" />
          </div>

          {/* Track Bar Container */}
          <div className="relative h-7 w-full rounded-full bg-surface-muted shadow-inner border border-border-subtle overflow-hidden">
            {/* Range highlight (P25 to P75) */}
            <div
              className="absolute top-0 bottom-0 rounded-full bg-gradient-to-r from-brand via-accent-teal to-accent-emerald transition-all duration-1000 ease-out"
              style={{
                insetInlineStart: mounted ? `${p25Pct}%` : `${p25Pct}%`,
                inlineSize: mounted ? `${rangeWidth}%` : '0%',
                opacity: mounted ? 1 : 0.2,
              }}
            >
              {/* Subtle inner highlight shimmer */}
              <div className="h-full w-full bg-white/10" />
            </div>

            {/* Median line on the track */}
            <div
              className="absolute top-0 bottom-0 w-1 bg-white shadow-sm transition-all duration-1000 ease-out z-10"
              style={{
                insetInlineStart: mounted ? `${p50Pct}%` : '50%',
                transform: 'translateX(50%)',
              }}
            />
          </div>

          {/* Legal Minimum Wage Reference Line (if available) */}
          {legalMinPct !== null && (
            <div
              className="absolute top-8 z-15 flex flex-col items-center pointer-events-none"
              style={{
                insetInlineStart: `${legalMinPct}%`,
                transform: 'translateX(50%)',
              }}
            >
              <div className="h-10 w-px border-s-2 border-dashed border-ink-muted/50" />
              <span className="mt-1 whitespace-nowrap rounded bg-surface-muted/90 px-1.5 py-0.5 text-[10px] text-ink-muted border border-border-subtle">
                کف قانون کار: {tomanText(legalMinimumWageRial!)}
              </span>
            </div>
          )}

          {/* Gauge Tick Markers Below the Track */}
          <div className="relative mt-2 h-4 text-xs">
            {/* P25 Tick */}
            <div
              className="absolute top-0 flex flex-col items-center"
              style={{
                insetInlineStart: `${p25Pct}%`,
                transform: 'translateX(50%)',
              }}
            >
              <div className="h-1.5 w-0.5 bg-border-subtle" />
              <span className="mt-0.5 text-[11px] text-ink-muted font-medium">حد پایین</span>
            </div>

            {/* P75 Tick */}
            <div
              className="absolute top-0 flex flex-col items-center"
              style={{
                insetInlineStart: `${p75Pct}%`,
                transform: 'translateX(50%)',
              }}
            >
              <div className="h-1.5 w-0.5 bg-border-subtle" />
              <span className="mt-0.5 text-[11px] text-ink-muted font-medium">حد بالا</span>
            </div>
          </div>
        </div>

        {/* 3 Percentile Figure Cards */}
        <div className="grid gap-3 pt-2 sm:grid-cols-3">
          <div className="rounded-2xl border border-border-subtle bg-surface p-4 text-start transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md hover:border-danger/40">
            <div className="flex items-center justify-between text-xs text-ink-muted">
              <span>حد پایین (صدک ۲۵)</span>
              <span className="rounded-md bg-danger/10 px-2 py-0.5 text-[10px] font-bold text-danger">P25</span>
            </div>
            <p className="mt-2 text-lg font-bold tabular-nums text-ink">
              {tomanText(minSalaryRial)}
            </p>
            <p className="mt-1 text-[11px] text-ink-muted leading-relaxed">
              ۲۵٪ شاغلین بازار در این جایگاه کمتر از این مبلغ دریافت می‌کنند.
            </p>
          </div>

          <div className="rounded-2xl border-2 border-brand/50 bg-gradient-to-b from-brand/5 via-surface to-surface-raised p-4 text-start shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lg hover:border-brand">
            <div className="flex items-center justify-between text-xs text-brand-strong font-semibold">
              <span>میانهٔ بازار (صدک ۵۰)</span>
              <span className="rounded-md bg-brand/15 px-2 py-0.5 text-[10px] font-black text-brand">P50</span>
            </div>
            <p className="mt-2 text-xl font-black tabular-nums text-brand-strong">
              {tomanText(estimateRial)}
            </p>
            <p className="mt-1 text-[11px] text-ink-muted leading-relaxed">
              نقطهٔ تعادل و برآورد پیشنهادی برای موقعیت شغلی متناظر.
            </p>
          </div>

          <div className="rounded-2xl border border-border-subtle bg-surface p-4 text-start transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md hover:border-success/40">
            <div className="flex items-center justify-between text-xs text-ink-muted">
              <span>حد بالا (صدک ۷۵)</span>
              <span className="rounded-md bg-success/10 px-2 py-0.5 text-[10px] font-bold text-success">P75</span>
            </div>
            <p className="mt-2 text-lg font-bold tabular-nums text-ink">
              {tomanText(maxSalaryRial)}
            </p>
            <p className="mt-1 text-[11px] text-ink-muted leading-relaxed">
              ۲۵٪ شاغلین برتر در این جایگاه بیش از این مبلغ دریافت می‌کنند.
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
