/**
 * Salary Estimation Result Dashboard — Persian RTL.
 *
 * Implements a world-class SaaS estimation dashboard with:
 *   - AnimatedCounter for the primary estimate (median salary in Toman)
 *   - SalaryRangeGauge (horizontal thermometer with P25, P50, P75 and legal minimum wage)
 *   - ConfidenceRing (SVG circular chart with data & prediction sub-rings)
 *   - DistributionHistogram (interactive vertical histogram with hover tooltips)
 *   - FactorInfluenceCards (horizontal factor cards with icons and impact indicators)
 *   - MarketSourcesTimeline (vertical chronological evidence timeline)
 *
 * Invariant: Every monetary amount comes from the API as an integer Rial that is
 * an exact multiple of 10 Rial and is formatted through `lib/money.ts`.
 */

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatMoney } from '@/lib/money';
import { toPersianDigits } from '@/lib/numerals';
import type { SalaryEstimationResponse } from '@/api/salary-estimation';
import { AnimatedCounter } from './AnimatedCounter';
import { SalaryRangeGauge } from './SalaryRangeGauge';
import { ConfidenceRing } from './ConfidenceRing';
import { DistributionHistogram } from './DistributionHistogram';
import { FactorInfluenceCards } from './FactorInfluenceCards';
import { MarketSourcesTimeline } from './MarketSourcesTimeline';

function tomanText(rialValue: number): string {
  const roundedTo10 = Math.round(rialValue / 10) * 10;
  const toman = formatMoney(roundedTo10, 'toman');
  if (toman.ok) return toman.value.text;
  return `${toPersianDigits(String(Math.round(rialValue / 10)))} تومان`;
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

const COHORT_LABEL: Record<string, string> = {
  city_seniority_employment: 'شهر + سطح تخصص + نوع استخدام',
  city_seniority: 'شهر + سطح تخصص',
  city: 'شهر (بدون تفکیک سطح)',
  province: 'استان',
  national: 'میانگین کشوری (سراسر کشور)',
  live_web_search: 'جستجوی زنده وب',
  live_web_grounded: 'جستجوی زنده وب',
  published_report: 'گزارش تجمیعی منتشرشده',
};

export function SalaryEstimationResults({
  result,
  verifiedEvidenceBadge,
}: {
  result: SalaryEstimationResponse;
  verifiedEvidenceBadge?: {
    documentTypeFa: string;
    confidenceBoostPercent: number;
    verifiedExperience: number | null;
  } | null;
}) {
  const [copiedHash, setCopiedHash] = useState(false);

  const rialFmt = formatMoney(result.primary_estimate_rial, 'rial');
  const rialText = rialFmt.ok ? rialFmt.value.text : '—';

  const hourlyRial = Math.round(result.primary_estimate_rial / 176 / 10) * 10;
  const hourlyFmt = formatMoney(hourlyRial, 'toman');
  const hourlyTomanText = hourlyFmt.ok ? hourlyFmt.value.text : '—';

  return (
    <section className="space-y-6" aria-label="نتایج برآورد حقوق">
      {/* Primary Estimate Hero Card */}
      <Card className="overflow-hidden border border-border-subtle bg-gradient-to-b from-surface via-surface to-surface-raised shadow-lg relative">
        <div className="h-1.5 w-full bg-gradient-to-r from-brand via-accent-teal to-accent-emerald" />
        <CardHeader className="flex flex-row flex-wrap items-center justify-between gap-4 pb-2">
          <div>
            <div className="flex items-center gap-2">
              <span className="flex size-8 items-center justify-center rounded-xl bg-brand/10 text-brand font-bold text-sm">
                💼
              </span>
              <CardTitle className="text-xl">
                {result.match.family_title_fa ?? result.job_title}
              </CardTitle>
            </div>
            <p className="mt-1 text-xs text-ink-muted">
              پوشش نمونه‌ها:{' '}
              {COHORT_LABEL[result.methodology.cohort_scope] ?? result.methodology.cohort_scope}
              {' · '}
              سابقه: {toPersianDigits(String(result.experience_years))} سال
              {' · '}
              شهر: {result.city}
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2 shrink-0">
            {verifiedEvidenceBadge && (
              <Badge tone="success" className="text-xs font-semibold py-1 px-3 shadow-xs flex items-center gap-1.5 border border-accent-emerald/40 bg-accent-emerald/15 text-accent-emerald-dark dark:text-accent-emerald">
                <span>🛡️</span>
                <span>مستند به {verifiedEvidenceBadge.documentTypeFa} (+{toPersianDigits(String(verifiedEvidenceBadge.confidenceBoostPercent))}٪)</span>
              </Badge>
            )}
            {result.data_source_mode === 'gemini_live' ? (
              <Badge tone="success" className="text-xs font-semibold py-1 px-3 shadow-xs">
                ✨ داده‌های زنده وب (Google Gemini)
              </Badge>
            ) : (
              <Badge tone="neutral" className="text-xs py-1 px-3">
                📚 پایگاه دادهٔ پشتیبان
              </Badge>
            )}
          </div>
        </CardHeader>

        <CardContent className="space-y-6 pt-2">
          {/* Main Primary Estimate Callout with Animated Counter */}
          <div className="relative overflow-hidden rounded-2xl border border-brand/20 bg-gradient-to-b from-brand/5 via-surface to-surface-raised p-6 sm:p-8 text-center shadow-xs">
            <div className="absolute top-0 end-0 size-48 bg-brand/5 rounded-full blur-2xl pointer-events-none" />

            <span className="inline-flex items-center gap-1.5 rounded-full border border-brand/20 bg-surface px-3 py-1 text-xs font-medium text-ink-muted mb-2 shadow-2xs">
              <span className="size-2 rounded-full bg-success animate-ping" />
              حقوق پایهٔ ماهانهٔ پیشنهادی (میانهٔ بازار)
            </span>

            <div className="mt-2 text-3xl sm:text-5xl font-black tabular-nums text-brand-strong tracking-tight">
              <AnimatedCounter targetRial={result.primary_estimate_rial} />
            </div>

            <div className="mt-3 flex flex-wrap items-center justify-center gap-2 text-xs text-ink-muted">
              <span className="rounded-lg bg-surface px-2.5 py-1 border border-border-subtle shadow-2xs font-medium">
                معادل: {toPersianDigits(rialText)}
              </span>
              <span className="text-border-subtle">·</span>
              <span className="rounded-lg bg-surface px-2.5 py-1 border border-border-subtle shadow-2xs font-medium">
                حدود {hourlyTomanText} به ازای هر ساعت کاری (مبنای ۱۷۶ ساعت)
              </span>
            </div>

            <p className="mt-3 text-xs text-ink-muted max-w-lg mx-auto leading-relaxed">
              این رقم نقطهٔ میانه (P50) بازار کار ایران بر اساس انطباق با شواهد مستند استخدامی برای این ردهٔ تخصصی است.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Visual Salary Range Gauge Component */}
      <SalaryRangeGauge
        minSalaryRial={result.min_salary_rial}
        medianSalaryRial={result.median_salary_rial}
        maxSalaryRial={result.max_salary_rial}
        primaryEstimateRial={result.primary_estimate_rial}
        legalMinimumWageRial={result.legal_minimum_wage_rial}
      />

      {/* Confidence Ring & Evidence Stats in 2 Columns */}
      <div className="grid gap-6 md:grid-cols-12">
        <div className="md:col-span-6">
          <ConfidenceRing
            score={result.confidence_score}
            dataConfidence={result.confidence.data_confidence}
            predictionConfidence={result.confidence.prediction_confidence}
            level={result.confidence_level}
            notes={result.confidence.notes_fa}
            className="h-full"
          />
        </div>

        <div className="md:col-span-6">
          <Card className="h-full">
            <CardContent className="space-y-6 p-6">
              <div className="flex items-center justify-between">
                <h3 className="text-base font-bold text-ink">حجم و اصالت شواهد</h3>
                <Badge tone="neutral" className="text-xs">
                  {toPersianDigits(String(result.valid_sample_count))} مشاهدهٔ خالص
                </Badge>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-xl border border-border-subtle bg-surface p-4">
                  <span className="text-[11px] text-ink-muted block">نمونه‌های معتبر:</span>
                  <span className="mt-1 text-2xl font-black tabular-nums text-success">
                    {toPersianDigits(String(result.valid_sample_count))}
                  </span>
                  <span className="text-[10px] text-ink-muted block mt-0.5">در محاسبات صدک‌ها</span>
                </div>

                <div className="rounded-xl border border-border-subtle bg-surface p-4">
                  <span className="text-[11px] text-ink-muted block">قرنطینه و رد:</span>
                  <span className="mt-1 text-2xl font-black tabular-nums text-ink-muted">
                    {toPersianDigits(String(result.quarantined_sample_count + result.rejected_sample_count))}
                  </span>
                  <span className="text-[10px] text-ink-muted block mt-0.5">غربال داده‌های پرت</span>
                </div>
              </div>

              <div className="space-y-2 rounded-xl bg-surface-muted/60 p-4 border border-border-subtle text-xs text-ink-muted">
                <div className="flex justify-between items-center">
                  <span>جدیدترین تاریخ داده:</span>
                  <span className="font-semibold text-ink tabular-nums">
                    {faDate(result.data_collected_at)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span>قدیمی‌ترین دادهٔ لحاظ‌شده:</span>
                  <span className="font-semibold text-ink tabular-nums">
                    {faDate(result.data_oldest_at)}
                  </span>
                </div>
                <div className="flex justify-between items-center pt-1 border-t border-border-subtle/60">
                  <span>پوشش زمانی تحلیل:</span>
                  <span className="font-medium text-ink">۶ ماه اخیر (معتبر و استنادپذیر)</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Distribution Histogram Enhancement */}
      {result.distribution.length > 0 && (
        <DistributionHistogram
          distribution={result.distribution}
          medianSalaryRial={result.median_salary_rial}
        />
      )}

      {/* Factor Influence Cards */}
      {result.factors_influence.length > 0 && (
        <FactorInfluenceCards
          factors={result.factors_influence}
          notes={result.factors_notes}
        />
      )}

      {/* Market Sources Timeline */}
      <MarketSourcesTimeline
        dataSources={result.data_sources}
        marketRows={result.market_rows}
        dataCollectedAt={result.data_collected_at}
      />

      {/* Legal Minimum Wage Reference Card */}
      {result.legal_minimum_wage_rial !== null && result.legal_minimum_wage_rial > 0 && (
        <Card className="border-s-4 border-border-subtle bg-surface">
          <CardContent className="p-6">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <h4 className="text-sm font-bold text-ink">مرجع حداقل دستمزد قانونی (شورای عالی کار)</h4>
                <p className="mt-1 text-xs text-ink-muted max-w-xl">
                  این رقم صرفاً جهت تطبیق حقوق با قوانین بالادستی کار نمایش داده می‌شود و به عنوان کفِ بازار یا ضریب تحلیلی در برآورد آماری دخالت ندارد.
                </p>
              </div>
              <div className="text-end">
                <span className="text-xs text-ink-muted block">حداقل قانونی ماهانه</span>
                <span className="text-lg font-bold tabular-nums text-ink">
                  {tomanText(result.legal_minimum_wage_rial)}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Methodology and Reproducibility Collapsible */}
      <details className="rounded-2xl border border-border-subtle bg-surface/50 p-5 transition-all">
        <summary className="cursor-pointer text-sm font-semibold text-ink flex items-center justify-between">
          <span className="flex items-center gap-2">
            <span>🔬</span>
            <span>روش‌شناسی محاسبه و ردپای بازتولیدپذیری (ADR-014)</span>
          </span>
          <span className="text-xs text-ink-muted font-normal">برای مشاهده جزئیات کلیک کنید</span>
        </summary>
        <dl className="mt-4 grid gap-3 text-xs text-ink-muted sm:grid-cols-2 border-t border-border-subtle pt-4">
          <div>
            <dt className="inline font-medium text-ink">الگوریتم برآورد: </dt>
            <dd className="inline">{result.methodology.method}</dd>
          </div>
          <div>
            <dt className="inline font-medium text-ink">دامنهٔ بازه: </dt>
            <dd className="inline">{result.methodology.range_source}</dd>
          </div>
          <div>
            <dt className="inline font-medium text-ink">محاسبه صدک‌ها: </dt>
            <dd className="inline">{result.methodology.percentile_method}</dd>
          </div>
          <div>
            <dt className="inline font-medium text-ink">آزمون‌های غربال پرت: </dt>
            <dd className="inline">{result.methodology.outlier_tests.join('، ')}</dd>
          </div>
          <div>
            <dt className="inline font-medium text-ink">تعدیل‌های اعمال‌شده: </dt>
            <dd className="inline">
              {result.methodology.adjustments_applied.length === 0
                ? 'هیچ (بدون دستکاری داده)'
                : result.methodology.adjustments_applied.join('، ')}
            </dd>
          </div>
          <div>
            <dt className="inline font-medium text-ink">واحد مبنا و نمایش: </dt>
            <dd className="inline">
              ذخیره در {result.methodology.currency_storage} · نمایش در تومان استاندارد
            </dd>
          </div>
          <div className="sm:col-span-2 flex flex-wrap items-center justify-between gap-2 rounded-xl bg-surface-muted/60 p-2.5 border border-border-subtle">
            <div>
              <dt className="inline font-medium text-ink">شناسه و هش یکتای محاسبه: </dt>
              <dd className="inline font-mono text-[11px] text-ink-muted">
                {result.calculation_hash}
              </dd>
            </div>
            <button
              type="button"
              onClick={() => {
                navigator.clipboard.writeText(result.calculation_hash);
                setCopiedHash(true);
                setTimeout(() => setCopiedHash(false), 2000);
              }}
              className="rounded-lg border border-border-subtle bg-surface px-2.5 py-1 text-[11px] font-medium text-ink hover:text-brand hover:border-brand/40 transition-colors cursor-pointer shrink-0"
              title="کپی هش محاسبه"
            >
              {copiedHash ? '✓ کپی شد' : '📋 کپی هش'}
            </button>
          </div>
          <div className="sm:col-span-2">
            <dt className="inline font-medium text-ink">زمان صدور برآورد: </dt>
            <dd className="inline">{faDate(result.generated_at)}</dd>
          </div>
        </dl>
        <p className="mt-3 text-xs text-ink-muted border-t border-border-subtle/50 pt-2">
          باقیماندهٔ رندکردن در مرز انتشار: {result.rounding_residual_rial} ریال
        </p>
      </details>

      {/* Advisory Notes */}
      {result.advisory_notes.length > 0 && (
        <p className="text-xs text-ink-muted leading-relaxed text-center">
          {result.advisory_notes.join(' ')}
        </p>
      )}
    </section>
  );
}
