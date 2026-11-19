/**
 * Factor Influence Cards — Persian RTL.
 *
 * Renders each candidate factor (experience, skills, location, seniority, education)
 * as a horizontal card with an icon, Persian name, impact indicator (↑, →, ↓),
 * and contextual explanation.
 *
 * Entrance: Staggered fade-in animation on mount.
 */

import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export type FactorInfluenceCardsProps = {
  factors: string[];
  notes?: string[];
  className?: string;
};

type FactorAnalysis = {
  name: string;
  icon: string;
  impact: 'positive' | 'negative' | 'neutral';
  impactSymbol: string;
  impactText: string;
  explanation: string;
};

function analyzeFactor(raw: string, index: number, notes: string[]): FactorAnalysis {
  const text = raw.trim();

  // Determine topic and icon
  let icon = '📊';
  if (text.includes('سابقه') || text.includes('سال') || text.includes('تجربه')) {
    icon = '⏱️';
  } else if (
    text.includes('React') ||
    text.includes('Python') ||
    text.includes('TypeScript') ||
    text.includes('مهارت') ||
    text.includes('تسلط') ||
    text.includes('تخصص')
  ) {
    icon = '⚡';
  } else if (text.includes('تهران') || text.includes('شهر') || text.includes('استان')) {
    icon = '📍';
  } else if (
    text.includes('ارشد') ||
    text.includes('جونیور') ||
    text.includes('سطح') ||
    text.includes('رده')
  ) {
    icon = '🎖️';
  } else if (text.includes('تحصیلات') || text.includes('دانشگاه') || text.includes('مدرک')) {
    icon = '🎓';
  } else if (text.includes('تمام‌وقت') || text.includes('قرارداد') || text.includes('استخدام')) {
    icon = '💼';
  }

  // Determine impact direction
  let impact: 'positive' | 'negative' | 'neutral' = 'neutral';
  let impactSymbol = '→';
  let impactText = 'خنثی / پایه';

  const isPositive =
    text.includes('+') ||
    text.includes('افزایش') ||
    text.includes('ارشد') ||
    text.includes('تسلط') ||
    text.includes('پیشرفته') ||
    text.includes('بالا') ||
    text.includes('تهران') ||
    text.includes('مزیت') ||
    /\d+\s*سال/.test(text);

  const isNegative =
    text.includes('-') ||
    text.includes('کاهش') ||
    text.includes('پایین') ||
    text.includes('مبتدی') ||
    text.includes('جونیور') ||
    text.includes('فاقد') ||
    text.includes('کسر');

  if (isNegative) {
    impact = 'negative';
    impactSymbol = '↓';
    impactText = 'کاهنده';
  } else if (isPositive) {
    impact = 'positive';
    impactSymbol = '↑';
    impactText = 'افزاینده';
  }

  // Explanation: use corresponding note if available, else informative default
  const noteExplanation = notes[index];
  let explanation = noteExplanation ?? 'تأثیر مستقیم بر تعیین بازه و صدک‌های حقوقی';
  if (!noteExplanation) {
    if (icon === '⏱️') explanation = 'تجربهٔ کاری مؤثر در ارتقای ردهٔ حقوقی متناظر';
    else if (icon === '⚡') explanation = 'مهارت فنی کلیدی و مورد تقاضا در گزارش‌های استخدامی';
    else if (icon === '📍') explanation = 'ضریب هزینهٔ زندگی و پویایی بازار کار منطقه';
    else if (icon === '🎖️') explanation = 'تعیین‌کنندهٔ افق مسئولیت‌پذیری و چارک استخدامی';
    else if (icon === '🎓') explanation = 'پشتوانهٔ آکادمیک داوطلب و تطابق با رده‌های سازمانی';
  }

  return {
    name: text,
    icon,
    impact,
    impactSymbol,
    impactText,
    explanation,
  };
}

export function FactorInfluenceCards({
  factors,
  notes = [],
  className,
}: FactorInfluenceCardsProps) {
  if (!factors || factors.length === 0) {
    return null;
  }

  const analyzed = factors.map((f, i) => analyzeFactor(f, i, notes));

  return (
    <Card className={className}>
      <CardContent className="space-y-4 p-6">
        <div>
          <h3 className="text-base font-bold text-ink">عوامل تأثیرگذار بر برآورد</h3>
          <p className="mt-0.5 text-xs text-ink-muted">
            عناصر کلیدی شناسایی‌شده در رزومه داوطلب و وزن اثرگذاری آن‌ها بر حقوق
          </p>
        </div>

        <div className="grid gap-3 sm:grid-cols-2">
          {analyzed.map((item, idx) => {
            const badgeTone =
              item.impact === 'positive'
                ? 'success'
                : item.impact === 'negative'
                  ? 'danger'
                  : 'neutral';

            return (
              <div
                key={`${item.name}-${idx}`}
                className="group flex items-start gap-3 rounded-xl border border-border-subtle bg-surface p-4 transition-all duration-200 hover:border-brand/40 hover:shadow-sm"
                style={{
                  animation: 'fadeUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) both',
                  animationDelay: `${idx * 70}ms`,
                }}
              >
                {/* Topic Icon */}
                <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-surface-muted border border-border-subtle text-lg">
                  <span aria-hidden="true">{item.icon}</span>
                </div>

                {/* Factor Details */}
                <div className="flex flex-1 flex-col justify-between min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <p className="font-semibold text-sm text-ink truncate">{item.name}</p>
                    <Badge tone={badgeTone} className="text-[11px] shrink-0 font-medium">
                      <span className="font-bold">{item.impactSymbol}</span> {item.impactText}
                    </Badge>
                  </div>
                  <p className="mt-1 text-xs text-ink-muted leading-relaxed line-clamp-2">
                    {item.explanation}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Any extra notes from model */}
        {notes.length > analyzed.length && (
          <div className="rounded-xl bg-surface-raised p-3 border border-border-subtle text-xs text-ink-muted">
            <p className="font-semibold text-ink mb-1">سایر نکات تحلیلی:</p>
            <ul className="space-y-1 list-disc list-inside">
              {notes.slice(analyzed.length).map((note) => (
                <li key={note}>{note}</li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
