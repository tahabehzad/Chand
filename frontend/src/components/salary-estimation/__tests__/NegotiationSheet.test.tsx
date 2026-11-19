import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { NegotiationSheet } from '../NegotiationSheet';
import type { SalaryEstimationResponse } from '@/api/salary-estimation';

const BASE_RESPONSE: SalaryEstimationResponse = {
  advisory: true,
  statutory: false,
  advisory_notes: [],
  model_version: '2.0',
  estimation_version: 'v1',
  engine_version: '0.2.0',
  calculation_hash: 'test-hash-1234',
  generated_at: '2026-11-18T12:00:00Z',
  job_title: 'توسعه‌دهنده React',
  experience_years: 3,
  seniority_level: 'mid',
  employment_type: 'full_time',
  work_condition: 'on_site',
  city: 'تهران',
  province: 'تهران',
  primary_estimate_rial: 450_000_000,
  min_salary_rial: 350_000_000,
  median_salary_rial: 450_000_000,
  max_salary_rial: 550_000_000,
  rounding_residual_rial: 0,
  currency_unit: 'toman',
  valid_sample_count: 6,
  quarantined_sample_count: 0,
  rejected_sample_count: 0,
  data_sources: ['Jobinja', 'Jobvision'],
  data_collected_at: '2026-11-18T12:00:00Z',
  data_oldest_at: null,
  market_rows: [],
  distribution: [],
  factors_influence: [],
  factors_notes: [],
  confidence_level: 'high',
  confidence_score: '0.85',
  confidence: {
    data_confidence: '0.88',
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

describe('NegotiationSheet', () => {
  it('renders correct percentile badges and advice logic for all 4 market tiers', () => {
    // 1. Below P25 (< 350M Rial)
    const { rerender } = render(
      <NegotiationSheet
        result={{ ...BASE_RESPONSE, primary_estimate_rial: 300_000_000 }}
      />,
    );
    expect(
      screen.getByText('پایین‌تر از ۲۵٪ بازار — ریسک عدم جذب بسیار بالا'),
    ).toBeInTheDocument();

    // 2. In P25 - P50 (between 350M and 450M Rial)
    rerender(
      <NegotiationSheet
        result={{ ...BASE_RESPONSE, primary_estimate_rial: 400_000_000 }}
      />,
    );
    expect(
      screen.getByText('در بازه رقابتی پایه — مناسب برای بودجه‌های کنترل‌شده'),
    ).toBeInTheDocument();

    // 3. In P50 - P75 (between 450M and 550M Rial)
    rerender(
      <NegotiationSheet
        result={{ ...BASE_RESPONSE, primary_estimate_rial: 500_000_000 }}
      />,
    );
    expect(
      screen.getByText('بالاتر از میانه بازار — مزیت رقابتی قوی در جذب'),
    ).toBeInTheDocument();

    // 4. Above P75 (> 550M Rial)
    rerender(
      <NegotiationSheet
        result={{ ...BASE_RESPONSE, primary_estimate_rial: 650_000_000 }}
      />,
    );
    expect(
      screen.getByText('بالای ۷۵٪ بازار — مناسب برای جذب استعدادهای کلیدی و تخصصی'),
    ).toBeInTheDocument();
  });

  it('renders tactical Iranian labor market talking points and true employer multiplier', () => {
    render(<NegotiationSheet result={BASE_RESPONSE} />);

    expect(screen.getByText('برگه تقلب مذاکره حقوق (ویژه مدیر استخدام)')).toBeInTheDocument();
    expect(screen.getByText('بهینه‌سازی با مزایای رفاهی')).toBeInTheDocument();
    expect(screen.getByText('ارزش سنوات و عیدی سالانه')).toBeInTheDocument();
    expect(screen.getByText('تطبیق با بازار تهران')).toBeInTheDocument();
    expect(screen.getByText('ضریب واقعی کارفرما')).toBeInTheDocument();
    expect(screen.getByText(/هزینه واقعی ماهانه این استخدام برای شرکت/)).toBeInTheDocument();
  });
});
