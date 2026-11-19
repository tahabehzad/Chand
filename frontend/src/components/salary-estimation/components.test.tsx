import { describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AnimatedCounter } from './AnimatedCounter';
import { SalaryRangeGauge } from './SalaryRangeGauge';
import { ConfidenceRing } from './ConfidenceRing';
import { DistributionHistogram } from './DistributionHistogram';
import { FactorInfluenceCards } from './FactorInfluenceCards';
import { MarketSourcesTimeline } from './MarketSourcesTimeline';
import { CtcBreakdown } from './CtcBreakdown';
import { NegotiationSheet } from './NegotiationSheet';
import { PdfExport } from './PdfExport';
import type { SalaryEstimationResponse } from '@/api/salary-estimation';

const BASE_MOCK_ESTIMATE: SalaryEstimationResponse = {
  advisory: true,
  statutory: false,
  advisory_notes: [],
  model_version: '2.0',
  estimation_version: 'v1',
  engine_version: '0.2.0',
  calculation_hash: 'hash1234567890',
  generated_at: '2026-11-18T10:00:00Z',
  job_title: 'توسعه‌دهنده React',
  experience_years: 4,
  seniority_level: 'mid',
  employment_type: 'full_time',
  work_condition: 'on_site',
  city: 'تهران',
  province: 'تهران',
  primary_estimate_rial: 450_000_000,
  min_salary_rial: 380_000_000,
  median_salary_rial: 450_000_000,
  max_salary_rial: 550_000_000,
  rounding_residual_rial: 0,
  currency_unit: 'toman',
  valid_sample_count: 5,
  quarantined_sample_count: 0,
  rejected_sample_count: 0,
  data_sources: ['Jobinja'],
  data_collected_at: '2026-11-18T10:00:00Z',
  data_oldest_at: null,
  market_rows: [],
  distribution: [],
  factors_influence: [],
  factors_notes: [],
  confidence_level: 'high',
  confidence_score: '0.85',
  confidence: {
    data_confidence: '0.85',
    prediction_confidence: '0.85',
    method_ceiling: '0.90',
    components: {},
    weights: {},
    notes_fa: [],
  },
  methodology: {
    method: 'cohort',
    estimation_version: 'v1',
    engine_version: '0.2.0',
    cohort_scope: 'city_seniority',
    cohort_definition_fa: 'شهر + سطح تخصص',
    range_source: 'live',
    percentile_method: 'linear',
    outlier_tests: [],
    adjustments_applied: [],
    data_kind: 'live',
    currency_storage: 'rial',
    currency_display: 'toman',
    quantisation_rial: 10,
    warning_codes: [],
  },
  match: { family_title_fa: 'توسعه‌دهنده فرانت‌اند' },
  warnings: [],
  legal_minimum_wage_rial: 71_661_840,
};

describe('Salary Estimation UI Components', () => {
  describe('AnimatedCounter', () => {
    it('renders the formatted Toman amount with Persian digits', () => {
      render(<AnimatedCounter targetRial={450_000_000} durationMs={0} />);
      // 450,000,000 Rial is 45,000,000 Toman -> ۴۵٬۰۰۰٬۰۰۰ تومان
      expect(screen.getByText(/۴۵[٬,]۰۰۰[٬,]۰۰۰ تومان/)).toBeInTheDocument();
    });
  });

  describe('SalaryRangeGauge', () => {
    it('renders P25, P50, and P75 labels and amounts', () => {
      render(
        <SalaryRangeGauge
          minSalaryRial={380_000_000}
          medianSalaryRial={450_000_000}
          maxSalaryRial={550_000_000}
          primaryEstimateRial={450_000_000}
          legalMinimumWageRial={71_661_840}
        />,
      );

      expect(screen.getByText('محدودهٔ حقوق بازار کار')).toBeInTheDocument();
      expect(screen.getAllByText('حد پایین').length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText('حد بالا').length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText(/کف قانون کار:/)).toBeInTheDocument();
    });
  });

  describe('ConfidenceRing', () => {
    it('renders overall confidence score and sub-rings with Persian percentages', () => {
      render(
        <ConfidenceRing
          score="0.850"
          dataConfidence="0.880"
          predictionConfidence="0.850"
          level="high"
          notes={['نمونه‌های باکیفیت استخراج‌شده']}
        />,
      );

      expect(screen.getByText('اطمینان و اعتبار آماری')).toBeInTheDocument();
      expect(screen.getByText('سطح بالا')).toBeInTheDocument();
      expect(screen.getByText('اعتماد داده‌ها')).toBeInTheDocument();
      expect(screen.getByText('دقت پیش‌بینی')).toBeInTheDocument();
      expect(screen.getByText('نمونه‌های باکیفیت استخراج‌شده')).toBeInTheDocument();
    });
  });

  describe('DistributionHistogram', () => {
    it('renders histogram bars and identifies the median bucket', () => {
      render(
        <DistributionHistogram
          distribution={[
            { min_rial: 300_000_000, max_rial: 400_000_000, count: 4 },
            { min_rial: 400_000_000, max_rial: 500_000_000, count: 8 },
            { min_rial: 500_000_000, max_rial: 600_000_000, count: 3 },
          ]}
          medianSalaryRial={450_000_000}
        />,
      );

      expect(screen.getByText('توزیع حقوق نمونه‌های معتبر بازار')).toBeInTheDocument();
      expect(screen.getByText(/مجموع شواهد: ۱۵ نمونه/)).toBeInTheDocument();
      expect(screen.getByText('میانه')).toBeInTheDocument();
    });
  });

  describe('FactorInfluenceCards', () => {
    it('renders factor items with directional indicators and context', () => {
      render(
        <FactorInfluenceCards
          factors={['سابقه ۴ سال (+۱۵٪)', 'تسلط به React', 'جونیور']}
          notes={['تجربه بالا']}
        />,
      );

      expect(screen.getByText('عوامل تأثیرگذار بر برآورد')).toBeInTheDocument();
      expect(screen.getByText('سابقه ۴ سال (+۱۵٪)')).toBeInTheDocument();
      expect(screen.getByText('تسلط به React')).toBeInTheDocument();
      expect(screen.getByText('جونیور')).toBeInTheDocument();
    });
  });

  describe('MarketSourcesTimeline', () => {
    it('renders sorted timeline entries with Persian date and sample count', () => {
      render(
        <MarketSourcesTimeline
          dataSources={['Jobinja', 'Jobvision']}
          marketRows={[
            {
              source: 'Jobinja',
              job_title: 'React Dev',
              city: 'تهران',
              seniority_level: 'mid',
              min_salary_rial: 380_000_000,
              median_salary_rial: 450_000_000,
              max_salary_rial: 550_000_000,
              sample_count: 5,
              collected_at: '2026-11-18T10:00:00Z',
              confidence: 'high',
            },
          ]}
          dataCollectedAt="2026-11-18T10:00:00Z"
        />,
      );

      expect(screen.getByText('خط زمانی منابع دادهٔ بازار')).toBeInTheDocument();
      expect(screen.getByText('Jobinja')).toBeInTheDocument();
      expect(screen.getByText(/۵ نمونه/)).toBeInTheDocument();
    });
  });

  describe('CtcBreakdown', () => {
    it('renders the complete Iranian labor cost CTC panel and stacked bar chart', async () => {
      render(<CtcBreakdown grossSalaryRial={450_000_000} />);

      await waitFor(() => {
        expect(
          screen.getByText('تفکیک هزینه کل کارفرما (CTC) و خالص پرداختی'),
        ).toBeInTheDocument();
      });

      expect(screen.getByText('خالص دریافتی کارمند')).toBeInTheDocument();
      expect(screen.getAllByText('حقوق ناخالص توافقی').length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText('هزینه کل کارفرما (CTC)')).toBeInTheDocument();
      expect(screen.getByText('ترکیب هزینه کل (۱۰۰٪ CTC)')).toBeInTheDocument();
      expect(screen.getByText(/بیمه تأمین اجتماعی سهم کارمند/)).toBeInTheDocument();
      expect(screen.getByText(/حق بیمه تأمین اجتماعی سهم کارفرما/)).toBeInTheDocument();
      expect(screen.getByText(/ذخیره ماهانه سنوات خدمت/)).toBeInTheDocument();
      expect(screen.getByText(/ذخیره ماهانه عیدی و پاداش/)).toBeInTheDocument();
    });
  });

  describe('NegotiationSheet', () => {
    it('renders market percentile position statements correctly across cohorts', () => {
      // P25-P50 (primary 450M == median 450M)
      const { rerender } = render(<NegotiationSheet result={BASE_MOCK_ESTIMATE} />);
      expect(
        screen.getByText('در بازه رقابتی پایه — مناسب برای بودجه‌های کنترل‌شده'),
      ).toBeInTheDocument();

      // < P25 (300M < 380M)
      rerender(
        <NegotiationSheet
          result={{ ...BASE_MOCK_ESTIMATE, primary_estimate_rial: 300_000_000 }}
        />,
      );
      expect(
        screen.getByText('پایین‌تر از ۲۵٪ بازار — ریسک عدم جذب بسیار بالا'),
      ).toBeInTheDocument();

      // P50-P75 (500M between 450M and 550M)
      rerender(
        <NegotiationSheet
          result={{ ...BASE_MOCK_ESTIMATE, primary_estimate_rial: 500_000_000 }}
        />,
      );
      expect(
        screen.getByText('بالاتر از میانه بازار — مزیت رقابتی قوی در جذب'),
      ).toBeInTheDocument();

      // > P75 (600M > 550M)
      rerender(
        <NegotiationSheet
          result={{ ...BASE_MOCK_ESTIMATE, primary_estimate_rial: 600_000_000 }}
        />,
      );
      expect(
        screen.getByText('بالای ۷۵٪ بازار — مناسب برای جذب استعدادهای کلیدی و تخصصی'),
      ).toBeInTheDocument();
    });

    it('renders the 3 Iranian labor market talking points and the employer multiplier', () => {
      render(<NegotiationSheet result={BASE_MOCK_ESTIMATE} />);

      expect(screen.getByText('برگه تقلب مذاکره حقوق (ویژه مدیر استخدام)')).toBeInTheDocument();
      expect(screen.getByText('بهینه‌سازی با مزایای رفاهی')).toBeInTheDocument();
      expect(screen.getByText('ارزش سنوات و عیدی سالانه')).toBeInTheDocument();
      expect(screen.getByText('تطبیق با بازار تهران')).toBeInTheDocument();
      expect(screen.getByText(/هزینه واقعی ماهانه این استخدام برای شرکت/)).toBeInTheDocument();
      expect(screen.getByText('ضریب واقعی کارفرما')).toBeInTheDocument();
    });
  });

  describe('PdfExport', () => {
    it('renders print button and calls window.print when clicked', async () => {
      const user = userEvent.setup();
      const printSpy = vi.spyOn(window, 'print').mockImplementation(() => {});

      render(<PdfExport result={BASE_MOCK_ESTIMATE} />);

      const btn = screen.getByRole('button', { name: /دانلود گزارش PDF/ });
      expect(btn).toBeInTheDocument();

      await user.click(btn);
      expect(printSpy).toHaveBeenCalledTimes(1);

      expect(
        screen.getByText('چند؟ — گزارش برآورد حقوق و هزینه استخدام'),
      ).toBeInTheDocument();

      printSpy.mockRestore();
    });
  });
});
