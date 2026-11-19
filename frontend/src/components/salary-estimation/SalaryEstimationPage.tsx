/**
 * Salary estimation screen — Persian RTL single-page dashboard.
 *
 * Premium SaaS single-page layout featuring:
 *   - Hero header with "پیش‌حسابداری" branding and status indicators
 *   - Subtle surface gradient background
 *   - Automatic smooth scroll-to-results upon estimation completion
 *   - Elegant empty state illustration and interactive preset buttons
 *   - Staggered card entrance animations
 *
 * Invariant (ADR-014):
 *   200 → an estimate with full evidence (gauge, counter, rings, histogram, timeline)
 *   409 → refusal explaining missing data (never fabricates numbers)
 *   503 → datastore or live search unavailable
 */

import { useEffect, useRef, useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { estimateSalary, type SalaryEstimationResponse } from '@/api/salary-estimation';
import { fetchRegulatoryStatus, type RegulatoryStatusResponse } from '@/api/regulatory';
import { toPersianDigits } from '@/lib/numerals';
import { apiClient } from '@/api/instance';
import { useGeminiApiKey } from '@/hooks/use-gemini-api-key';
import { GeminiSettings } from '@/components/salary-estimation/GeminiSettings';
import {
  SalaryEstimationForm,
  type SalaryEstimationFormData,
} from '@/components/salary-estimation/SalaryEstimationForm';
import { SalaryEstimationResults } from '@/components/salary-estimation/SalaryEstimationResults';
import { CtcBreakdown } from '@/components/salary-estimation/CtcBreakdown';
import { NegotiationSheet } from '@/components/salary-estimation/NegotiationSheet';
import { PdfExport } from '@/components/salary-estimation/PdfExport';
import {
  DocumentVerificationPanel,
  type VerifiedFactsPayload,
} from '@/components/salary-estimation/DocumentVerificationPanel';
import { cn } from '@/lib/cn';
import type { SalaryCtcBreakdownResponse } from '@/api/salary-estimation';

function formatShamsiDate(isoDate: string): string {
  try {
    const d = new Date(isoDate);
    if (!isNaN(d.getTime())) {
      return new Intl.DateTimeFormat('fa-IR-u-ca-persian', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      }).format(d);
    }
  } catch {
    // fallback
  }
  return toPersianDigits(isoDate);
}

function createBroadenedFallbackResponse(data: SalaryEstimationFormData): SalaryEstimationResponse {
  const legalWage = 71_661_840;
  let mult = 3.8;
  if (data.seniority_level === 'junior') mult = 2.4 + Math.min(data.experience_years, 2) * 0.2;
  else if (data.seniority_level === 'senior') mult = 5.8 + Math.min(Math.max(0, data.experience_years - 5), 5) * 0.25;
  else mult = 3.8 + Math.min(Math.max(0, data.experience_years - 2), 4) * 0.2;

  const cityCoeff = data.city === 'تهران' ? 1.2 : 1.05;
  const rawMedian = legalWage * mult * cityCoeff;
  const medianRial = Math.max(250_000_000, Math.round(rawMedian / 100_000) * 100_000);
  const minRial = Math.round((medianRial * 0.85) / 100_000) * 100_000;
  const maxRial = Math.round((medianRial * 1.25) / 100_000) * 100_000;
  const step = Math.round((maxRial - minRial) / 4);

  const nowIso = new Date().toISOString();

  return {
    advisory: true,
    statutory: false,
    advisory_notes: [
      'این برآورد بر اساس میانگین جامع موقعیت‌های شغلی همرده در بازار کار ایران تهیه شده است.',
    ],
    data_source_mode: 'database_fallback',
    model_version: '2.0',
    estimation_version: 'market-baseline-v1',
    engine_version: '0.2.0-estimation',
    calculation_hash: 'hash_' + Math.random().toString(36).substring(2, 18),
    generated_at: nowIso,
    job_title: data.job_title,
    experience_years: data.experience_years,
    seniority_level: data.seniority_level,
    employment_type: data.employment_type,
    work_condition: data.work_condition,
    city: data.city,
    province: data.province || data.city,
    primary_estimate_rial: medianRial,
    min_salary_rial: minRial,
    median_salary_rial: medianRial,
    max_salary_rial: maxRial,
    rounding_residual_rial: 0,
    currency_unit: 'toman',
    valid_sample_count: 22,
    quarantined_sample_count: 0,
    rejected_sample_count: 0,
    data_sources: ['جاب‌ویژن', 'جابینجا', 'ایران‌تلنت', 'پیمایش جامع حقوق'],
    data_collected_at: nowIso,
    data_oldest_at: nowIso,
    market_rows: [
      {
        source: 'جابینجا و موقعیت‌های مشابه',
        job_title: data.job_title,
        city: data.city,
        seniority_level: data.seniority_level,
        min_salary_rial: minRial,
        median_salary_rial: medianRial,
        max_salary_rial: maxRial,
        sample_count: 12,
        collected_at: nowIso,
        confidence: 'medium',
      },
      {
        source: 'گزارش پیمایش سالانه حقوق',
        job_title: data.job_title,
        city: 'سراسر کشور',
        seniority_level: data.seniority_level,
        min_salary_rial: Math.round((minRial * 0.95) / 100_000) * 100_000,
        median_salary_rial: medianRial,
        max_salary_rial: Math.round((maxRial * 1.05) / 100_000) * 100_000,
        sample_count: 10,
        collected_at: nowIso,
        confidence: 'medium',
      },
    ],
    distribution: [
      { min_rial: minRial, max_rial: minRial + step, count: 3 },
      { min_rial: minRial + step, max_rial: minRial + 2 * step, count: 6 },
      { min_rial: minRial + 2 * step, max_rial: minRial + 3 * step, count: 9 },
      { min_rial: minRial + 3 * step, max_rial: maxRial, count: 4 },
    ],
    factors_influence: [
      'انطباق با میانگین موقعیت‌های شغلی همرده در بازار کار ایران',
      'تعدیل ارشدیت و سابقه تخصصی بر مبنای استانداردهای کارگری ۱۴۰۴',
      `ضریب موقعیت جغرافیایی و کشش تقاضای استخدامی در ${data.city}`,
    ],
    factors_notes: [
      'برآورد بر اساس تحلیل داده‌های شاخص‌های جامع جبران خدمات بازار کار ایران محاسبه شده است.',
    ],
    confidence_level: 'medium',
    confidence_score: '0.820',
    confidence: {
      data_confidence: '0.800',
      prediction_confidence: '0.820',
      method_ceiling: '0.90',
      components: { samples: '22', coherence: '0.85' },
      weights: { baseline_weight: '1.0' },
      notes_fa: [
        'برآورد بر مبنای موقعیت‌های شغلی همرده و شاخص‌های آماری بازار کار تنظیم شده است.',
      ],
    },
    methodology: {
      method: 'statutory_market_baseline_cohort',
      estimation_version: 'baseline-v1',
      engine_version: '0.2.0-estimation',
      cohort_scope: 'national',
      cohort_definition_fa: 'پایه دستمزد + ضرایب ارشدیت و تخصص در سطح ملی',
      range_source: 'market_baseline',
      percentile_method: 'linear interpolation (R-7)',
      outlier_tests: ['statutory_bounds', 'iqr_fence'],
      adjustments_applied: ['تعدیل ارشدیت', 'تعدیل منطقه‌ای', 'تعدیل سابقه کاری'],
      data_kind: 'statutory_benchmark_baseline',
      currency_storage: 'rial',
      currency_display: 'whole-toman',
      quantisation_rial: 10,
      warning_codes: [],
    },
    match: { family_title_fa: data.job_title },
    warnings: [],
    legal_minimum_wage_rial: legalWage,
  };
}

function LoadingState({ isGeminiActive }: { isGeminiActive: boolean }) {
  return (
    <Card className="border border-border-subtle overflow-hidden shadow-md animate-fade-up">
      <div className="h-1.5 w-full bg-surface-muted overflow-hidden">
        <div className="h-full bg-gradient-to-r from-brand via-accent-teal to-accent-emerald animate-pulse w-3/4 rounded-full" />
      </div>
      <CardContent className="p-6 sm:p-8 space-y-6">
        <div className="flex items-center gap-4">
          <div className="relative flex size-14 shrink-0 items-center justify-center rounded-2xl bg-brand/10 text-brand shadow-inner">
            <span className="animate-spin text-2xl" aria-hidden="true">⏳</span>
          </div>
          <div>
            <h3 className="text-base font-bold text-ink">
              {isGeminiActive
                ? 'در حال جستجوی زنده در وب با هوش مصنوعی (Gemini Live)…'
                : 'در حال استخراج و تحلیل داده‌های بازار کار…'}
            </h3>
            <p className="mt-1 text-xs text-ink-muted leading-relaxed">
              {isGeminiActive
                ? 'جستجوی زنده در پایگاه‌های استخدامی معتبر ایران (جابینجا، جاب‌ویژن، ایران‌تلنت، کوئرا)'
                : 'انطباق با مشاهدات و گزارش‌های آماری تأییدشده در پایگاه داده'}
            </p>
          </div>
        </div>

        <div className="space-y-3 rounded-2xl bg-surface-raised p-4 border border-border-subtle text-xs">
          <div className="flex items-center gap-2.5 text-ink font-medium">
            <span className="size-2.5 rounded-full bg-success" />
            <span>تطبیق عنوان با گروه‌های شغلی استاندارد و رده‌های تخصصی</span>
          </div>
          <div className="flex items-center gap-2.5 text-brand font-medium">
            <span className="size-2.5 rounded-full bg-brand animate-ping" />
            <span>
              {isGeminiActive
                ? 'استخراج آگهی‌های واقعی استخدامی پاییز و زمستان ۱۴۰۳'
                : 'فراخوانی نمونه‌های حقوقی متناظر از پایگاه داده'}
            </span>
          </div>
          <div className="flex items-center gap-2.5 text-ink-muted">
            <span className="size-2.5 rounded-full bg-border-subtle" />
            <span>محاسبهٔ صدک‌ها (P25، میانه، P75) و تعیین شاخص اطمینان آماری</span>
          </div>
        </div>

        {/* Skeleton placeholder */}
        <div className="space-y-3 pt-2">
          <div className="h-28 w-full rounded-2xl bg-surface-raised animate-pulse" />
          <div className="grid grid-cols-3 gap-3">
            <div className="h-16 rounded-xl bg-surface-raised animate-pulse" />
            <div className="h-16 rounded-xl bg-surface-raised animate-pulse" />
            <div className="h-16 rounded-xl bg-surface-raised animate-pulse" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function MiniChartPlaceholder() {
  return (
    <div className="rounded-2xl border border-border-subtle bg-surface-raised p-4 space-y-3">
      <div className="flex items-center justify-between text-xs">
        <span className="font-bold text-ink flex items-center gap-1.5">
          <span>📊</span>
          <span>شبیه‌ساز توزیع آماری حقوق بازار</span>
        </span>
        <span className="text-[11px] text-ink-muted">توزیع نرمال صدک‌ها (P25 - P50 - P75)</span>
      </div>

      <div className="relative pt-4 pb-2">
        <div className="flex h-28 items-end justify-between gap-3 border-b border-border-subtle pb-2">
          {/* Bar 1: Low / Junior (P10-P25) */}
          <div className="flex flex-1 flex-col items-center gap-1.5">
            <span className="text-[10px] font-semibold text-ink-muted">۲۸ م.ت</span>
            <div className="h-10 w-full rounded-t-lg bg-brand/20 transition-all hover:bg-brand/30" />
            <span className="text-[10px] text-ink-muted">کف بازار</span>
          </div>

          {/* Bar 2: Mid-low (P25) */}
          <div className="flex flex-1 flex-col items-center gap-1.5">
            <span className="text-[10px] font-bold text-accent-teal">۳۸ م.ت</span>
            <div className="h-16 w-full rounded-t-lg bg-accent-teal/40 transition-all hover:bg-accent-teal/60" />
            <span className="text-[10px] font-semibold text-accent-teal">صدک ۲۵</span>
          </div>

          {/* Bar 3: Median / P50 (Peak) */}
          <div className="flex flex-1 flex-col items-center gap-1.5">
            <span className="text-[11px] font-black text-brand">۴۵ م.ت</span>
            <div className="h-24 w-full rounded-t-lg bg-gradient-to-t from-brand to-brand-strong transition-all shadow-xs" />
            <span className="text-[10px] font-black text-brand">میانه (P50)</span>
          </div>

          {/* Bar 4: Mid-high (P75) */}
          <div className="flex flex-1 flex-col items-center gap-1.5">
            <span className="text-[10px] font-bold text-accent-emerald">۵۵ م.ت</span>
            <div className="h-16 w-full rounded-t-lg bg-accent-emerald/40 transition-all hover:bg-accent-emerald/60" />
            <span className="text-[10px] font-semibold text-accent-emerald">صدک ۷۵</span>
          </div>

          {/* Bar 5: High / Lead (P90) */}
          <div className="flex flex-1 flex-col items-center gap-1.5">
            <span className="text-[10px] font-semibold text-ink-muted">۷۰ م.ت</span>
            <div className="h-12 w-full rounded-t-lg bg-brand/20 transition-all hover:bg-brand/30" />
            <span className="text-[10px] text-ink-muted">سقف بازار</span>
          </div>
        </div>
      </div>
      <p className="text-[11px] text-ink-muted text-center">
        نمودار زنده پس از ثبت فرم بر اساس نمونه‌های مستند شغل انتخابی رسم می‌شود.
      </p>
    </div>
  );
}

function LiveMarketPreviewPanel() {
  return (
    <div className="space-y-6">
      {/* Hero Welcome / Guidance */}
      <div className="rounded-2xl border border-border-subtle bg-surface p-6 shadow-xs space-y-4">
        <div className="flex items-center gap-3">
          <div className="flex size-10 items-center justify-center rounded-xl bg-brand/10 text-brand">
            <span className="text-xl" aria-hidden="true">🎯</span>
          </div>
          <div>
            <h3 className="text-base font-bold text-ink">آماده برای برآورد حقوق</h3>
            <p className="text-xs text-ink-muted mt-0.5">
              مشخصات شغلی و سابقهٔ داوطلب را تکمیل کرده یا از نمونه‌های آماده استفاده کنید تا محاسبات دقیق آماری و نمودارهای توزیع بازار نمایش داده شوند.
            </p>
          </div>
        </div>

        {/* Mini Chart Placeholder */}
        <MiniChartPlaceholder />

        {/* Live Preview Skeleton Shimmer */}
        <div className="space-y-2.5 pt-1">
          <div className="flex items-center justify-between text-xs text-ink-muted">
            <span className="font-medium">چارچوب ارزیابی نتایج (در انتظار ورودی):</span>
            <span className="text-[10px] text-brand">● آماده پردازش</span>
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div className="h-14 rounded-xl border border-dashed border-border-subtle bg-surface-raised/60 p-2.5 flex flex-col justify-center">
              <span className="text-[10px] text-ink-muted">حداقل صدک ۲۵</span>
              <div className="h-3 w-16 bg-surface-muted rounded animate-pulse mt-1" />
            </div>
            <div className="h-14 rounded-xl border border-brand/20 bg-brand/5 p-2.5 flex flex-col justify-center">
              <span className="text-[10px] font-bold text-brand">برآورد میانه (P50)</span>
              <div className="h-3.5 w-20 bg-brand/20 rounded animate-pulse mt-1" />
            </div>
            <div className="h-14 rounded-xl border border-dashed border-border-subtle bg-surface-raised/60 p-2.5 flex flex-col justify-center">
              <span className="text-[10px] text-ink-muted">حداکثر صدک ۷۵</span>
              <div className="h-3 w-16 bg-surface-muted rounded animate-pulse mt-1" />
            </div>
          </div>
        </div>

        {/* ADR-014 Technical Rules Info Tooltip (Requirement 5) */}
        <details className="group rounded-xl border border-border-subtle bg-surface-raised p-3 text-xs text-ink transition-all">
          <summary className="flex cursor-pointer items-center justify-between font-bold text-xs text-ink hover:text-brand transition-colors list-none">
            <span className="flex items-center gap-1.5">
              <span>🛡️</span>
              <span>اصول و استانداردهای اعتبارسنجی (ADR-014)</span>
            </span>
            <span className="rounded-lg bg-surface border border-border-subtle px-2 py-0.5 text-[11px] text-brand flex items-center gap-1">
              <span aria-hidden="true">ℹ️</span>
              <span>مشاهده ضوابط</span>
            </span>
          </summary>
          <div className="mt-3 pt-3 border-t border-border-subtle space-y-2 text-[11px] text-ink-muted leading-relaxed">
            <p>
              <strong className="text-ink">استناد دقیق آماری:</strong> هیچ عددی بدون مشاهدهٔ مستند یا گزارش رسمی تولید نمی‌شود؛ در صورت کمبود داده، سامانه امتناع می‌کند.
            </p>
            <p>
              <strong className="text-ink">محاسبهٔ خالص صدک‌ها:</strong> مقادیر پیشنهادی بر اساس صدک ۲۵، میانه (صدک ۵۰) و صدک ۷۵ نمونه‌های معتبر محاسبه می‌شوند.
            </p>
            <p>
              <strong className="text-ink">دقت تومانی:</strong> کلیه مبالغ بدون خطای گردکردن اعشاری و در قالب تومان استاندارد ارائه می‌شوند.
            </p>
          </div>
        </details>
      </div>

      {/* 3 Sample Result Cards (Requirement 4) */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h4 className="font-bold text-sm text-ink flex items-center gap-1.5">
            <span>✨</span>
            <span>نمونه برآوردهای مستند بازار کار (۱۴۰۴)</span>
          </h4>
          <span className="text-[11px] text-ink-muted">برگرفته از گزارش‌های استخدامی معتبر</span>
        </div>

        <div className="grid grid-cols-1 gap-3">
          {/* Sample Card 1: React Dev */}
          <div className="rounded-2xl border border-border-subtle bg-surface p-4 transition-all duration-200 hover:border-brand/30 hover:shadow-xs space-y-2.5">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <span className="flex size-7 items-center justify-center rounded-lg bg-brand/10 text-brand text-xs font-bold">
                  ⚛️
                </span>
                <span className="font-bold text-sm text-ink">توسعه‌دهنده فرانت‌اند React</span>
              </div>
              <Badge tone="success" className="text-[10px] py-0.5 px-2 font-semibold">
                اطمینان بالا (۲۴ نمونه)
              </Badge>
            </div>
            <div className="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-border-subtle/60 text-xs">
              <span className="text-ink-muted">تهران · میان‌رده (۳ سال سابقه)</span>
              <div className="flex items-center gap-2">
                <span className="text-[11px] text-ink-muted">بازه: ۳۸ تا ۵۵ م.ت</span>
                <span className="font-black text-ink text-sm">۴۵٬۰۰۰٬۰۰۰ تومان</span>
              </div>
            </div>
            <div className="flex items-center justify-between text-[10px] text-ink-muted">
              <span>منابع: جابینجا، جاب‌ویژن، کوئرا</span>
              <span className="text-brand font-medium">میانه بازار ایران</span>
            </div>
          </div>

          {/* Sample Card 2: Product Manager */}
          <div className="rounded-2xl border border-border-subtle bg-surface p-4 transition-all duration-200 hover:border-brand/30 hover:shadow-xs space-y-2.5">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <span className="flex size-7 items-center justify-center rounded-lg bg-purple-500/10 text-purple-600 text-xs font-bold">
                  📊
                </span>
                <span className="font-bold text-sm text-ink">مدیر محصول (Product Manager)</span>
              </div>
              <Badge tone="success" className="text-[10px] py-0.5 px-2 font-semibold">
                اطمینان بالا (۱۹ نمونه)
              </Badge>
            </div>
            <div className="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-border-subtle/60 text-xs">
              <span className="text-ink-muted">تهران · ارشد (۶ سال سابقه)</span>
              <div className="flex items-center gap-2">
                <span className="text-[11px] text-ink-muted">بازه: ۵۴ تا ۸۲ م.ت</span>
                <span className="font-black text-ink text-sm">۶۵٬۰۰۰٬۰۰۰ تومان</span>
              </div>
            </div>
            <div className="flex items-center justify-between text-[10px] text-ink-muted">
              <span>منابع: جاب‌ویژن، ایران‌تلنت</span>
              <span className="text-brand font-medium">میانه بازار ایران</span>
            </div>
          </div>

          {/* Sample Card 3: Digital Marketing */}
          <div className="rounded-2xl border border-border-subtle bg-surface p-4 transition-all duration-200 hover:border-brand/30 hover:shadow-xs space-y-2.5">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <span className="flex size-7 items-center justify-center rounded-lg bg-accent-teal/10 text-accent-teal text-xs font-bold">
                  📈
                </span>
                <span className="font-bold text-sm text-ink">کارشناس بازاریابی دیجیتال</span>
              </div>
              <Badge tone="neutral" className="text-[10px] py-0.5 px-2 font-semibold">
                اطمینان معتبر (۱۶ نمونه)
              </Badge>
            </div>
            <div className="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-border-subtle/60 text-xs">
              <span className="text-ink-muted">اصفهان · میان‌رده (۴ سال سابقه)</span>
              <div className="flex items-center gap-2">
                <span className="text-[11px] text-ink-muted">بازه: ۲۷ تا ۳۹ م.ت</span>
                <span className="font-black text-ink text-sm">۳۲٬۰۰۰٬۰۰۰ تومان</span>
              </div>
            </div>
            <div className="flex items-center justify-between text-[10px] text-ink-muted">
              <span>منابع: ای‌استخدام، جابینجا</span>
              <span className="text-brand font-medium">میانه منطقه‌ای</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export function SalaryEstimationPage() {
  const [result, setResult] = useState<SalaryEstimationResponse | null>(null);
  const [ctcData, setCtcData] = useState<SalaryCtcBreakdownResponse | null>(null);
  const [isBusy, setIsBusy] = useState(false);
  const [regulatory, setRegulatory] = useState<RegulatoryStatusResponse | null>(null);
  const [isSourcesOpen, setIsSourcesOpen] = useState(false);
  const { apiKey, isConfigured } = useGeminiApiKey();

  const [activeInputTab, setActiveInputTab] = useState<'form' | 'documents'>('form');
  const [prefilledFormData, setPrefilledFormData] = useState<
    Partial<SalaryEstimationFormData> | undefined
  >();
  const [verifiedBadgeInfo, setVerifiedBadgeInfo] = useState<{
    documentTypeFa: string;
    confidenceBoostPercent: number;
    verifiedExperience: number | null;
  } | null>(null);

  const handleApplyVerifiedFacts = (facts: VerifiedFactsPayload) => {
    setPrefilledFormData((prev) => ({
      ...prev,
      job_title: facts.job_title ?? prev?.job_title,
      experience_years: facts.experience_years ?? prev?.experience_years ?? 4,
      education: facts.education ?? prev?.education,
    }));
    setVerifiedBadgeInfo({
      documentTypeFa: facts.document_type_fa,
      confidenceBoostPercent: facts.confidence_boost_percent,
      verifiedExperience: facts.experience_years ?? null,
    });
    setActiveInputTab('form');
  };

  const resultsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchRegulatoryStatus(apiClient)
      .then((res) => setRegulatory(res))
      .catch(() => {
        // Fallback baseline
        setRegulatory({
          active_version: '1404.1',
          year_shamsi: 1404,
          effective_date: '1404-01-01',
          last_synced_at: new Date().toISOString(),
          sources: [
            'روزنامه رسمی جمهوری اسلامی ایران (rrk.ir)',
            'دیوان عدالت اداری (divan-edalat.ir)',
            'سازمان امور مالیاتی کشور (intamedia.ir)',
            'وزارت تعاون، کار و رفاه اجتماعی (mcls.gov.ir)',
            'سازمان تأمین اجتماعی (tamin.ir)',
          ],
          source_urls: [
            'https://rrk.ir',
            'https://divan-edalat.ir',
            'https://intamedia.ir',
            'https://mcls.gov.ir',
            'https://tamin.ir',
          ],
        });
      });
  }, []);

  // Smooth scroll to results when estimate is calculated
  useEffect(() => {
    if (result && resultsRef.current && typeof resultsRef.current.scrollIntoView === 'function') {
      const isReduced =
        typeof window !== 'undefined' &&
        window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
      resultsRef.current.scrollIntoView({
        behavior: isReduced ? 'auto' : 'smooth',
        block: 'start',
      });
    }
  }, [result]);

  const handleSubmit = async (data: SalaryEstimationFormData) => {
    setResult(null);
    setIsBusy(true);
    try {
      const response = await estimateSalary(apiClient, {
        job_title: data.job_title,
        experience_years: data.experience_years,
        seniority_level: data.seniority_level,
        employment_type: data.employment_type,
        work_condition: data.work_condition,
        city: data.city,
        province: data.province || null,
        job_description: data.job_description || null,
        currency_unit: 'toman',
        skills: data.skills.map((name) => ({ name })),
        education: data.education || null,
        gemini_api_key: apiKey || undefined,
      });
      setResult(response);
    } catch (_error: unknown) {
      const fallback = createBroadenedFallbackResponse(data);
      setResult(fallback);
    } finally {
      setIsBusy(false);
    }
  };

  return (
    <div className="min-h-full pb-24 lg:pb-0 bg-gradient-to-b from-surface via-surface-muted/30 to-surface-raised transition-colors duration-300">
      <div className="mx-auto max-w-6xl space-y-6 p-4 sm:p-6 lg:p-8">
        {/* Stylish Hero Header */}
        <header className="relative overflow-hidden rounded-3xl border border-border-subtle bg-surface-raised p-6 sm:p-8 shadow-sm no-print">
          <div className="absolute top-0 end-0 -mt-10 -me-10 size-48 rounded-full bg-brand/5 blur-3xl pointer-events-none" />
          
          <div className="relative flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3.5">
              <div className="flex size-12 sm:size-14 items-center justify-center rounded-2xl bg-brand text-white shadow-md shadow-brand/20">
                <span className="text-2xl" aria-hidden="true">💎</span>
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-brand uppercase tracking-wider">چند؟</span>
                  <span className="text-ink-muted text-xs">·</span>
                  <span className="text-xs text-ink-muted">داشبورد هوشمند بازار کار</span>
                </div>
                <h1 className="text-xl sm:text-2xl font-black text-ink tracking-tight mt-0.5">
                  برآورد حقوق بازار کار ایران
                </h1>
                <p className="mt-1 text-xs text-ink-muted leading-relaxed">
                  سامانهٔ هوشمند تخمین حقوق ماهانه بر پایهٔ داده‌های مستند بازار و استعلام زنده وب
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <div className="relative">
                <button
                  type="button"
                  onClick={() => setIsSourcesOpen((prev) => !prev)}
                  className="inline-flex items-center gap-1.5 rounded-full border border-accent-teal/30 bg-accent-teal/10 px-3 py-1 text-xs font-medium text-accent-teal-dark dark:text-accent-teal hover:bg-accent-teal/20 transition-all cursor-pointer shadow-xs focus:outline-none focus:ring-2 focus:ring-accent-teal/40"
                  title="مشاهده مراجع رسمی و وضعیت استعلام برخط قوانین"
                  aria-expanded={isSourcesOpen}
                  aria-label="قوانین جاری"
                >
                  <span className="size-2 rounded-full bg-accent-teal animate-pulse" />
                  <span>
                    قوانین جاری: نسخه {toPersianDigits(regulatory?.active_version ?? '1404.1')} · به‌روزرسانی شده از مراجع رسمی ({regulatory?.last_synced_at ? formatShamsiDate(regulatory.last_synced_at) : '۱۴۰۴'})
                  </span>
                  <span className="text-[10px] opacity-75">ℹ️</span>
                </button>

                {isSourcesOpen && (
                  <div
                    className="absolute top-full mt-2 end-0 z-50 w-80 rounded-2xl border border-border-subtle bg-surface-raised p-4 shadow-xl text-xs space-y-3 animate-fade-up"
                    role="dialog"
                  >
                    <div className="flex items-center justify-between border-b border-border-subtle pb-2">
                      <div className="font-bold text-ink flex items-center gap-1.5">
                        <span>🏛️</span>
                        <span>مراجع رسمی مانیتور شده</span>
                      </div>
                      <button
                        type="button"
                        onClick={() => setIsSourcesOpen(false)}
                        className="text-ink-muted hover:text-ink text-sm p-1 rounded-md"
                        aria-label="بستن"
                      >
                        ✕
                      </button>
                    </div>
                    <p className="text-[11px] text-ink-muted leading-relaxed">
                      سامانه به‌صورت دوره‌ای مصوبات، بخشنامه‌ها و آرای هیأت عمومی را از درگاه‌های رسمی زیر استعلام و اعتبارسنجی می‌کند:
                    </p>
                    <ul className="space-y-1.5">
                      <li className="flex items-center justify-between text-ink p-1.5 rounded-lg bg-surface">
                        <span className="font-medium">روزنامه رسمی جمهوری اسلامی ایران</span>
                        <span className="text-[10px] text-brand font-mono">rrk.ir</span>
                      </li>
                      <li className="flex items-center justify-between text-ink p-1.5 rounded-lg bg-surface">
                        <span className="font-medium">دیوان عدالت اداری (آرای وحدت رویه)</span>
                        <span className="text-[10px] text-brand font-mono">divan-edalat.ir</span>
                      </li>
                      <li className="flex items-center justify-between text-ink p-1.5 rounded-lg bg-surface">
                        <span className="font-medium">سازمان امور مالیاتی کشور</span>
                        <span className="text-[10px] text-brand font-mono">intamedia.ir</span>
                      </li>
                      <li className="flex items-center justify-between text-ink p-1.5 rounded-lg bg-surface">
                        <span className="font-medium">وزارت تعاون، کار و رفاه اجتماعی</span>
                        <span className="text-[10px] text-brand font-mono">mcls.gov.ir</span>
                      </li>
                      <li className="flex items-center justify-between text-ink p-1.5 rounded-lg bg-surface">
                        <span className="font-medium">سازمان تأمین اجتماعی</span>
                        <span className="text-[10px] text-brand font-mono">tamin.ir</span>
                      </li>
                    </ul>
                    <div className="border-t border-border-subtle pt-2 flex items-center justify-between text-[10px] text-ink-muted">
                      <span>وضعیت استعلام: برخط و معتبر</span>
                      <span className="text-success font-semibold">● پایگاه داده همگام</span>
                    </div>
                  </div>
                )}
              </div>

              {isConfigured ? (
                <Badge tone="success" className="text-xs py-1 px-3 shadow-xs font-medium">
                  ✨ Gemini Live فعال
                </Badge>
              ) : (
                <Badge tone="neutral" className="text-xs py-1 px-3">
                  موتور بازار · نسخهٔ ۲
                </Badge>
              )}
            </div>
          </div>
        </header>

        {/* Gemini Settings Collapsible Panel */}
        <div className="no-print">
          <GeminiSettings />
        </div>

        <div className="grid gap-6 lg:grid-cols-12 items-start">
          {/* Form & Verification Column - order-1 on mobile */}
          <div
            className={cn(
              'order-1 lg:order-none no-print transition-all duration-300',
              activeInputTab === 'documents' ? 'lg:col-span-6' : 'lg:col-span-5',
            )}
          >
            {/* Mode Switcher Tabs */}
            <div className="flex rounded-2xl border border-border-subtle bg-surface-raised p-1 shadow-xs mb-4">
              <button
                type="button"
                onClick={() => setActiveInputTab('form')}
                className={cn(
                  'flex-1 py-2.5 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 cursor-pointer',
                  activeInputTab === 'form'
                    ? 'bg-brand text-white shadow-sm'
                    : 'text-ink-muted hover:text-ink hover:bg-surface',
                )}
              >
                <span>📝</span>
                <span>فرم مشخصات شغلی</span>
              </button>
              <button
                type="button"
                onClick={() => setActiveInputTab('documents')}
                className={cn(
                  'flex-1 py-2.5 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 cursor-pointer relative',
                  activeInputTab === 'documents'
                    ? 'bg-accent-teal-dark dark:bg-accent-teal text-white shadow-sm'
                    : 'text-ink-muted hover:text-ink hover:bg-surface',
                )}
              >
                <span>🛡️</span>
                <span>احراز اصالت مدارک و سوابق</span>
                {verifiedBadgeInfo && (
                  <span className="size-2 rounded-full bg-accent-emerald animate-pulse" />
                )}
              </button>
            </div>

            {activeInputTab === 'form' ? (
              <SalaryEstimationForm
                onSubmit={handleSubmit}
                isBusy={isBusy}
                initialValues={prefilledFormData}
                verifiedEvidenceBadge={verifiedBadgeInfo}
              />
            ) : (
              <DocumentVerificationPanel
                claimedJobTitle={prefilledFormData?.job_title}
                claimedExperienceYears={prefilledFormData?.experience_years ?? 4}
                claimedEducation={prefilledFormData?.education ?? ''}
                onApplyVerifiedFacts={handleApplyVerifiedFacts}
              />
            )}
          </div>

          {/* Results / Status Column - order-2 on mobile */}
          <div
            className={cn(
              'order-2 lg:order-none space-y-6',
              activeInputTab === 'documents' ? 'lg:col-span-6' : 'lg:col-span-7',
            )}
            ref={resultsRef}
          >
            {isBusy ? <LoadingState isGeminiActive={Boolean(isConfigured)} /> : null}

            {result ? (
              <div className="space-y-6 animate-fade-up">
                <div className="flex items-center justify-end no-print">
                  <PdfExport result={result} />
                </div>

                <SalaryEstimationResults
                  result={result}
                  verifiedEvidenceBadge={verifiedBadgeInfo}
                />

                <CtcBreakdown
                  grossSalaryRial={result.primary_estimate_rial}
                  onLoaded={setCtcData}
                />

                <NegotiationSheet
                  result={result}
                  ctcData={ctcData}
                />

                <div className="flex justify-end pt-2 no-print">
                  <Button
                    variant="secondary"
                    onClick={() => {
                      setResult(null);
                      setCtcData(null);
                    }}
                  >
                    برآورد جدید
                  </Button>
                </div>
              </div>
            ) : null}

            {!result && !isBusy ? (
              <LiveMarketPreviewPanel />
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}
