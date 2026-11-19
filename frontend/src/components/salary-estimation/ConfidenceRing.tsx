/**
 * Confidence Ring / Radar Component — Persian RTL.
 *
 * Visualizes the statistical confidence score of the salary estimation using
 * pure CSS/SVG circular progress rings.
 *
 * Thresholds:
 *   score > 0.7  → Green / Success
 *   0.4 <= score <= 0.7 → Yellow / Warning
 *   score < 0.4  → Red / Danger
 *
 * Inner text: Rendered through `formatPercentFromRate()` from `lib/money.ts`.
 * Sub-rings: Visualizes data_confidence and prediction_confidence.
 */

import { formatPercentFromRate } from '@/lib/money';
import { toPersianDigits } from '@/lib/numerals';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export type ConfidenceRingProps = {
  score: string | number;
  dataConfidence: string;
  predictionConfidence: string;
  level?: 'high' | 'medium' | 'low' | 'insufficient_data';
  notes?: string[];
  className?: string;
};

function parseScore(val: string | number): number {
  const num = typeof val === 'number' ? val : parseFloat(val);
  if (isNaN(num)) return 0;
  return Math.min(1, Math.max(0, num));
}

function toRateString(val: string | number): string {
  if (typeof val === 'string') return val;
  return val.toFixed(2);
}

function getToneColor(score: number): {
  strokeClass: string;
  textClass: string;
  bgClass: string;
  badgeTone: 'success' | 'warning' | 'danger';
} {
  if (score > 0.7) {
    return {
      strokeClass: 'text-success',
      textClass: 'text-success',
      bgClass: 'bg-success/10',
      badgeTone: 'success',
    };
  }
  if (score >= 0.4) {
    return {
      strokeClass: 'text-warning',
      textClass: 'text-warning',
      bgClass: 'bg-warning/10',
      badgeTone: 'warning',
    };
  }
  return {
    strokeClass: 'text-danger',
    textClass: 'text-danger',
    bgClass: 'bg-danger/10',
    badgeTone: 'danger',
  };
}

const LEVEL_LABEL: Record<string, string> = {
  high: 'سطح بالا',
  medium: 'سطح متوسط',
  low: 'سطح پایین',
  insufficient_data: 'داده ناکافی',
};

function SubRing({
  label,
  rate,
  subtext,
}: {
  label: string;
  rate: string;
  subtext?: string;
}) {
  const num = parseScore(rate);
  const tone = getToneColor(num);
  const r = 22;
  const c = 2 * Math.PI * r; // ~138.23
  const offset = c * (1 - num);
  const percentText = formatPercentFromRate(rate) ?? `${toPersianDigits(String(Math.round(num * 100)))}٪`;

  return (
    <div className="flex flex-col items-center rounded-xl border border-border-subtle bg-surface p-3 text-center">
      <div className="relative size-16">
        <svg className="size-full -rotate-90" viewBox="0 0 54 54" aria-hidden="true">
          <circle
            cx="27"
            cy="27"
            r={r}
            className="stroke-surface-muted dark:stroke-border-subtle"
            strokeWidth="4"
            fill="none"
          />
          <circle
            cx="27"
            cy="27"
            r={r}
            className={`${tone.strokeClass} transition-all duration-1000 ease-out`}
            strokeWidth="4"
            strokeDasharray={c}
            strokeDashoffset={offset}
            strokeLinecap="round"
            fill="none"
          />
        </svg>
        <span className="absolute inset-0 flex items-center justify-center text-xs font-bold tabular-nums text-ink">
          {percentText}
        </span>
      </div>
      <p className="mt-2 text-xs font-medium text-ink">{label}</p>
      {subtext && <p className="text-[10px] text-ink-muted">{subtext}</p>}
    </div>
  );
}

export function ConfidenceRing({
  score,
  dataConfidence,
  predictionConfidence,
  level = 'medium',
  notes = [],
  className,
}: ConfidenceRingProps) {
  const scoreNum = parseScore(score);
  const rateStr = toRateString(score);
  const tone = getToneColor(scoreNum);

  // SVG radius 46, center 60, circumference = 2 * PI * 46 ≈ 289.026
  const r = 46;
  const c = 2 * Math.PI * r;
  const strokeOffset = c * (1 - scoreNum);
  const percentText = formatPercentFromRate(rateStr) ?? `${toPersianDigits(String(Math.round(scoreNum * 100)))}٪`;

  return (
    <Card className={className}>
      <CardContent className="space-y-6 p-6">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-ink">اطمینان و اعتبار آماری</h3>
          <Badge tone={tone.badgeTone}>{LEVEL_LABEL[level] ?? level}</Badge>
        </div>

        {/* Main Circular Ring */}
        <div className="flex flex-col items-center justify-center py-2">
          <div className="relative size-36 sm:size-40">
            <svg
              className="size-full -rotate-90"
              viewBox="0 0 120 120"
              role="img"
              aria-label={`شاخص اطمینان برآورد: ${percentText}`}
            >
              <circle
                cx="60"
                cy="60"
                r={r}
                className="stroke-surface-muted dark:stroke-border-subtle"
                strokeWidth="8"
                fill="none"
              />
              <circle
                cx="60"
                cy="60"
                r={r}
                className={`${tone.strokeClass} transition-all duration-1000 ease-out`}
                strokeWidth="8"
                strokeDasharray={c}
                strokeDashoffset={strokeOffset}
                strokeLinecap="round"
                fill="none"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
              <span className={`text-2xl font-black tabular-nums ${tone.textClass}`}>
                {percentText}
              </span>
              <span className="text-[11px] font-medium text-ink-muted">شاخص کل اطمینان</span>
            </div>
          </div>
        </div>

        {/* Sub-rings for data confidence & prediction confidence */}
        <div className="grid grid-cols-2 gap-3 pt-1">
          <SubRing
            label="اعتماد داده‌ها"
            rate={dataConfidence}
            subtext="حجم و اصالت شواهد"
          />
          <SubRing
            label="دقت پیش‌بینی"
            rate={predictionConfidence}
            subtext="انطباق مدل و ویژگی‌ها"
          />
        </div>

        {/* Notes if available */}
        {notes.length > 0 && (
          <div className="rounded-xl bg-surface p-3 border border-border-subtle text-xs text-ink-muted">
            <p className="font-semibold text-ink mb-1.5">ملاحظات تحلیل اطمینان:</p>
            <ul className="space-y-1 list-disc list-inside">
              {notes.map((note) => (
                <li key={note}>{note}</li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
