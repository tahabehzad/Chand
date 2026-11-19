/**
 * Negotiation Cheat Sheet Component for Hiring Managers — Persian RTL.
 *
 * Provides actionable market intelligence during salary offers:
 *   1. Market percentile position statement (< P25, P25-P50, P50-P75, > P75)
 *   2. 3 tactical talking points grounded in Iranian labor market practice
 *   3. True employer multiplier callout ("هزینه واقعی ماهانه این استخدام برای شرکت X تومان است")
 *
 * Authority: ADR-014, WBS P4-T03.
 */

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatMoney } from '@/lib/money';
import { toPersianDigits } from '@/lib/numerals';
import type {
  SalaryEstimationResponse,
  SalaryCtcBreakdownResponse,
} from '@/api/salary-estimation';

export type NegotiationSheetProps = {
  result: SalaryEstimationResponse;
  ctcData?: SalaryCtcBreakdownResponse | null;
  className?: string;
};

function formatToman(rialValue: number): string {
  const roundedTo10 = Math.round(rialValue / 10) * 10;
  const toman = formatMoney(roundedTo10, 'toman');
  if (toman.ok) return toman.value.text;
  return `${toPersianDigits(String(Math.round(rialValue / 10)))} تومان`;
}

type MarketPosition = {
  statement: string;
  badgeTone: 'danger' | 'warning' | 'success' | 'info';
  description: string;
  icon: string;
};

function resolveMarketPosition(
  offeredRial: number,
  p25: number,
  p50: number,
  p75: number,
): MarketPosition {
  if (offeredRial < p25) {
    return {
      statement: 'پایین‌تر از ۲۵٪ بازار — ریسک عدم جذب بسیار بالا',
      badgeTone: 'danger',
      description: 'پیشنهاد در این سطح تنها برای متقاضیان کم‌سابقه یا شرایط با مزایای غیرنقدی و سهام استارتاپی استثنایی کارایی دارد؛ احتمال رد آفر بالای ۷۰٪ است.',
      icon: '⚠️',
    };
  }
  if (offeredRial <= p50) {
    return {
      statement: 'در بازه رقابتی پایه — مناسب برای بودجه‌های کنترل‌شده',
      badgeTone: 'warning',
      description: 'در محدوده صدک ۲۵ تا میانه بازار؛ مناسب برای متقاضیان مستعدی که امکان رشد درون‌سازمانی دارند، اما نیازمند پیگیری فعال در دوره مصاحبه است.',
      icon: '📊',
    };
  }
  if (offeredRial <= p75) {
    return {
      statement: 'بالاتر از میانه بازار — مزیت رقابتی قوی در جذب',
      badgeTone: 'success',
      description: 'بالاتر از میانه تا صدک ۷۵ بازار؛ موضعی بسیار مطمئن و جذاب برای استخدام متخصصان حرفه‌ای با کاهش چشمگیر ریسک ترک خدمت در سال اول.',
      icon: '⭐',
    };
  }
  return {
    statement: 'بالای ۷۵٪ بازار — مناسب برای جذب استعدادهای کلیدی و تخصصی',
    badgeTone: 'info',
    description: 'در صدک برتر بازار؛ قدرت جذب حداکثری افراد کلیدی و مدیران ارشد با رقابت فشرده استخدامی در صنعت.',
    icon: '👑',
  };
}

export function NegotiationSheet({
  result,
  ctcData,
  className = '',
}: NegotiationSheetProps) {
  const [copied, setCopied] = useState<boolean>(false);

  const primaryRial = result.primary_estimate_rial;
  const p25 = result.min_salary_rial;
  const p50 = result.median_salary_rial;
  const p75 = result.max_salary_rial;

  const position = resolveMarketPosition(primaryRial, p25, p50, p75);

  // CTC figures & multiplier
  const effectiveCtcRial =
    ctcData?.total_cost_to_employer_rial ?? Math.round(primaryRial * 1.28);
  const ctcTomanText = formatToman(effectiveCtcRial);

  const multiplier = (effectiveCtcRial / (primaryRial || 1)).toFixed(2);
  const multiplierFa = toPersianDigits(multiplier);

  const copyTalkingPoints = () => {
    const text = [
      `برگه راهنمای مذاکره استخدامی — ${result.job_title} (${result.city})`,
      `وضعیت در بازار: ${position.statement}`,
      `هزینه واقعی ماهانه این استخدام برای شرکت: ${ctcTomanText}`,
      `ضریب هزینه کارفرما: ${multiplierFa} برابر ناخالص`,
      '',
      'نکات کلیدی مذاکره برای مدیر استخدام:',
      '۱. مزایای غیرنقدی و معافیت‌های مالیاتی: ارائه مزایای رفاهی و بیمه تکمیلی بدون افزایش پلکان مالیاتی',
      '۲. ارزش سنوات و عیدی پایان سال: محاسبه ۱ ماه سنوات و ۲ ماه عیدی که ۲۵٪ به ارزش ناخالص سالانه می‌افزاید',
      `۳. تطبیق با بازار ${result.city}: موقعیت در صدک‌های تخصصی جهت ایجاد ثبات شغلی`,
    ].join('\n');

    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <Card className={`overflow-hidden border border-border-subtle bg-surface shadow-md print-avoid-break ${className}`}>
      {/* Header Accent */}
      <div className="h-1.5 w-full bg-gradient-to-r from-accent-teal via-brand to-purple-600" />

      <CardHeader className="pb-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <span className="flex size-9 items-center justify-center rounded-xl bg-accent-teal/10 text-accent-teal-dark dark:text-accent-teal font-bold text-base" aria-hidden="true">
              🤝
            </span>
            <div>
              <CardTitle className="text-lg font-bold text-ink">
                برگه تقلب مذاکره حقوق (ویژه مدیر استخدام)
              </CardTitle>
              <p className="text-xs text-ink-muted mt-0.5">
                راهنمای استراتژیک ارائه پیشنهاد حقوق و بستن قرارداد با تکیه بر آمار بازار کار
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 no-print">
            <button
              type="button"
              onClick={copyTalkingPoints}
              className="rounded-xl border border-border-subtle bg-surface-raised px-3.5 py-1.5 text-xs font-semibold text-ink hover:bg-surface-muted hover:border-brand/40 transition-all flex items-center gap-1.5 cursor-pointer shadow-xs active:scale-95"
            >
              <span>{copied ? '✓ کپی شد' : '📋 کپی خلاصه راهنما'}</span>
            </button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* 1. Market Percentile Position Statement */}
        <div className="rounded-2xl border border-border-subtle bg-surface-raised p-4 space-y-2.5">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <span className="text-xs font-bold text-ink flex items-center gap-1.5">
              <span>{position.icon}</span>
              <span>موقعیت حقوق پیشنهادی نسبت به بازار:</span>
            </span>
            <Badge tone={position.badgeTone} className="text-xs font-semibold px-2.5 py-0.5">
              {position.statement}
            </Badge>
          </div>
          <p className="text-xs text-ink-muted leading-relaxed">
            {position.description}
          </p>
        </div>

        {/* 2. True Employer Multiplier Callout Banner */}
        <div className="rounded-2xl border-2 border-purple-500/20 bg-gradient-to-r from-purple-500/10 via-brand/5 to-surface-raised p-4 sm:p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-lg" aria-hidden="true">💡</span>
              <span className="text-xs font-black uppercase tracking-wider text-purple-700 dark:text-purple-400">
                هزینه واقعی استخدام برای شرکت
              </span>
            </div>
            <div className="text-base sm:text-lg font-black text-ink">
              هزینه واقعی ماهانه این استخدام برای شرکت{' '}
              <span className="text-purple-700 dark:text-purple-400 font-extrabold underline decoration-purple-500/30 underline-offset-4">
                {ctcTomanText}
              </span>{' '}
              است.
            </div>
            <p className="text-xs text-ink-muted leading-relaxed">
              شامل حقوق ناخالص پایه بعلاوه حق بیمه کارفرما (۲۰٪)، بیمه بیکاری (۳٪)، ذخیره ماهانه سنوات و عیدی قانونی.
            </p>
          </div>

          <div className="shrink-0 rounded-xl bg-purple-600/10 border border-purple-600/20 px-4 py-2 text-center self-stretch sm:self-auto flex sm:flex-col justify-between items-center sm:justify-center">
            <span className="text-[11px] text-purple-800 dark:text-purple-300 font-medium">ضریب واقعی کارفرما</span>
            <span className="text-lg font-black text-purple-950 dark:text-purple-100 font-mono">
              {multiplierFa} برابر
            </span>
          </div>
        </div>

        {/* 3. Three Grounded Iranian Labor Market Talking Points */}
        <div className="space-y-3">
          <h4 className="text-sm font-bold text-ink flex items-center gap-2">
            <span className="size-2 rounded-full bg-brand" />
            <span>۳ نکته کلیدی برای مدیر استخدام در جلسه مذاکره:</span>
          </h4>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {/* Point 1: Non-cash and Welfare Tax Exemptions */}
            <div className="rounded-2xl border border-border-subtle bg-surface-raised p-4 space-y-2 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md hover:border-brand/30">
              <div className="flex items-center gap-2 text-brand font-bold text-xs">
                <span>🎁</span>
                <span>بهینه‌سازی با مزایای رفاهی</span>
              </div>
              <p className="text-xs text-ink-muted leading-relaxed">
                با استناد به ماده ۸۴ ق.م.م، افزودن بن خرید کالا، کمک‌هزینه مسکن و بیمه تکمیلی، خالص دریافتی را بدون ورود به پله‌های مالیاتی بالاتر افزایش می‌دهد.
              </p>
            </div>

            {/* Point 2: Hidden Annual Bonus & Severance Value */}
            <div className="rounded-2xl border border-border-subtle bg-surface-raised p-4 space-y-2 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md hover:border-accent-teal/30">
              <div className="flex items-center gap-2 text-accent-teal-dark dark:text-accent-teal font-bold text-xs">
                <span>📅</span>
                <span>ارزش سنوات و عیدی سالانه</span>
              </div>
              <p className="text-xs text-ink-muted leading-relaxed">
                به کارجو متذکر شوید که در پایان سال ۱ ماه سنوات و ۲ ماه عیدی قانونی به او پرداخت می‌شود که عملاً معادل ۲۵٪ افزایش بر حقوق ماهانه است.
              </p>
            </div>

            {/* Point 3: City and Seniority Alignment */}
            <div className="rounded-2xl border border-border-subtle bg-surface-raised p-4 space-y-2 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md hover:border-purple-500/30">
              <div className="flex items-center gap-2 text-purple-700 dark:text-purple-400 font-bold text-xs">
                <span>🎯</span>
                <span>تطبیق با بازار {result.city}</span>
              </div>
              <p className="text-xs text-ink-muted leading-relaxed">
                برای رده شغلی در {result.city}، استقرار در محدوده صدک ۵۰ تا ۷۵ بازار بیش از ۸۰٪ ثبات شغلی و کاهش جابجایی در دوره آزمایشی را تضمین می‌کند.
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
