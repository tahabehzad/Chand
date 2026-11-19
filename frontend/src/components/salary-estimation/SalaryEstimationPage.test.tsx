import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import * as salaryEstimationApi from '@/api/salary-estimation';
import { ApiError } from '@/api/errors';
import { GEMINI_API_KEY_STORAGE_KEY } from '@/hooks/use-gemini-api-key';
import { SalaryEstimationPage } from './SalaryEstimationPage';

const MOCK_SUCCESS_RESPONSE: salaryEstimationApi.SalaryEstimationResponse = {
  advisory: true,
  statutory: false,
  advisory_notes: ['برآورد آزمایشی'],
  data_source_mode: 'gemini_live',
  model_version: '2.0',
  estimation_version: 'gemini-live-v1',
  engine_version: '0.2.0-estimation',
  calculation_hash: 'abc123hash456789',
  generated_at: '2026-11-18T12:00:00Z',
  job_title: 'توسعه‌دهنده React',
  experience_years: 3,
  seniority_level: 'mid',
  employment_type: 'full_time',
  work_condition: 'hybrid',
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
  data_sources: ['Jobinja', 'Jobvision'],
  data_collected_at: '2026-11-18T12:00:00Z',
  data_oldest_at: '2026-11-01T12:00:00Z',
  market_rows: [
    {
      source: 'Jobinja',
      job_title: 'توسعه‌دهنده React',
      city: 'تهران',
      seniority_level: 'mid',
      min_salary_rial: 380_000_000,
      median_salary_rial: 450_000_000,
      max_salary_rial: 550_000_000,
      sample_count: 5,
      collected_at: '2026-11-18T12:00:00Z',
      confidence: 'high',
    },
  ],
  distribution: [{ min_rial: 350_000_000, max_rial: 550_000_000, count: 5 }],
  factors_influence: ['سابقه ۳ سال', 'تسلط به React'],
  factors_notes: ['بازار فعال در تهران'],
  confidence_level: 'high',
  confidence_score: '0.850',
  confidence: {
    data_confidence: '0.880',
    prediction_confidence: '0.850',
    method_ceiling: '0.90',
    components: { samples: '5' },
    weights: { live: '1.0' },
    notes_fa: ['کیفیت بالا'],
  },
  methodology: {
    method: 'gemini_web_grounded_cohort',
    estimation_version: 'gemini-live-v1',
    engine_version: '0.2.0-estimation',
    cohort_scope: 'city_seniority',
    cohort_definition_fa: 'شهر + سطح تخصص',
    range_source: 'live_web',
    percentile_method: 'linear interpolation (R-7)',
    outlier_tests: ['bounds'],
    adjustments_applied: [],
    data_kind: 'live_observations',
    currency_storage: 'rial',
    currency_display: 'whole-toman',
    quantisation_rial: 10,
    warning_codes: [],
  },
  match: { family_title_fa: 'توسعه‌دهنده فرانت‌اند' },
  warnings: [],
  legal_minimum_wage_rial: 71_661_840,
};

describe('SalaryEstimationPage', () => {
  beforeEach(() => {
    window.localStorage.clear();
    vi.restoreAllMocks();
  });

  afterEach(() => {
    cleanup();
    window.localStorage.clear();
  });

  it('renders idle state with guidance initially', () => {
    render(<SalaryEstimationPage />);
    expect(screen.getByText('برآورد حقوق بازار کار ایران')).toBeInTheDocument();
    expect(screen.getByText('آماده برای برآورد حقوق')).toBeInTheDocument();
    expect(screen.getByText('پروفایل داوطلب')).toBeInTheDocument();
  });

  it('populates fields when a preset button is clicked', async () => {
    const user = userEvent.setup();
    render(<SalaryEstimationPage />);

    const presetBtn = screen.getByRole('button', { name: 'فرانت‌اند React' });
    await user.click(presetBtn);

    const titleInput = screen.getByLabelText('عنوان شغلی') as HTMLInputElement;
    expect(titleInput.value).toBe('توسعه‌دهنده React');

    const expInput = screen.getByLabelText('سابقهٔ کاری (سال)') as HTMLInputElement;
    expect(expInput.value).toBe('3');
  });

  it('submits form, shows loading state, and renders results with gemini_api_key', async () => {
    const user = userEvent.setup();
    window.localStorage.setItem(GEMINI_API_KEY_STORAGE_KEY, 'AIzaSyStoredKey999');

    let resolvePromise: (value: salaryEstimationApi.SalaryEstimationResponse) => void = () => {};
    const deferred = new Promise<salaryEstimationApi.SalaryEstimationResponse>((res) => {
      resolvePromise = res;
    });

    const estimateSpy = vi
      .spyOn(salaryEstimationApi, 'estimateSalary')
      .mockReturnValue(deferred);

    render(<SalaryEstimationPage />);

    // Click preset
    await user.click(screen.getByRole('button', { name: 'فرانت‌اند React' }));

    // Submit
    const submitBtn = screen.getByRole('button', { name: 'برآورد حقوق بازار' });
    await user.click(submitBtn);

    // Verify spy was called with gemini_api_key
    expect(estimateSpy).toHaveBeenCalledWith(
      expect.anything(),
      expect.objectContaining({
        job_title: 'توسعه‌دهنده React',
        gemini_api_key: 'AIzaSyStoredKey999',
      }),
    );

    // Verify loading state is shown
    expect(
      screen.getByText('در حال جستجوی زنده در وب با هوش مصنوعی (Gemini Live)…'),
    ).toBeInTheDocument();

    // Resolve API response
    resolvePromise(MOCK_SUCCESS_RESPONSE);

    // Verify results are rendered
    await waitFor(() => {
      expect(screen.getByText('✨ داده‌های زنده وب (Google Gemini)')).toBeInTheDocument();
      expect(screen.getAllByText(/۴۵[٬,]۰۰۰[٬,]۰۰۰ تومان/).length).toBeGreaterThanOrEqual(1);
    });

    // Reset with "برآورد جدید"
    const newEstimateBtn = screen.getByRole('button', { name: 'برآورد جدید' });
    await user.click(newEstimateBtn);

    expect(screen.getByText('آماده برای برآورد حقوق')).toBeInTheDocument();
  });

  it('falls back gracefully to broadened market estimate when API returns ESTIMATION_INSUFFICIENT_DATA', async () => {
    const user = userEvent.setup();
    vi.spyOn(salaryEstimationApi, 'estimateSalary').mockRejectedValue(
      new ApiError({
        kind: 'http',
        code: 'ESTIMATION_INSUFFICIENT_DATA',
        status: 409,
        warning: 'نمونهٔ معتبری برای این عنوان یافت نشد.',
      }),
    );

    render(<SalaryEstimationPage />);
    await user.click(screen.getByRole('button', { name: 'فرانت‌اند React' }));
    await user.click(screen.getByRole('button', { name: 'برآورد حقوق بازار' }));

    await waitFor(() => {
      expect(screen.queryByText('دادهٔ معتبر بازار برای این ترکیب کافی نیست')).not.toBeInTheDocument();
      expect(screen.getByLabelText('نتایج برآورد حقوق')).toBeInTheDocument();
      expect(screen.getAllByText('توسعه‌دهنده React').length).toBeGreaterThanOrEqual(1);
    });
  });

  it('falls back gracefully to broadened market estimate when API returns ESTIMATION_DATASTORE_UNAVAILABLE', async () => {
    const user = userEvent.setup();
    vi.spyOn(salaryEstimationApi, 'estimateSalary').mockRejectedValue(
      new ApiError({
        kind: 'http',
        code: 'ESTIMATION_DATASTORE_UNAVAILABLE',
        status: 503,
      }),
    );

    render(<SalaryEstimationPage />);
    await user.click(screen.getByRole('button', { name: 'فرانت‌اند React' }));
    await user.click(screen.getByRole('button', { name: 'برآورد حقوق بازار' }));

    await waitFor(() => {
      expect(screen.queryByText('خواندن داده‌های بازار ممکن نشد')).not.toBeInTheDocument();
      expect(screen.getByLabelText('نتایج برآورد حقوق')).toBeInTheDocument();
      expect(screen.getAllByText('توسعه‌دهنده React').length).toBeGreaterThanOrEqual(1);
    });
  });

  it('falls back gracefully to broadened market estimate when API returns ESTIMATION_GEMINI_UNAVAILABLE', async () => {
    const user = userEvent.setup();
    vi.spyOn(salaryEstimationApi, 'estimateSalary').mockRejectedValue(
      new ApiError({
        kind: 'http',
        code: 'ESTIMATION_GEMINI_UNAVAILABLE',
        status: 503,
        warning: 'ارتباط با سرویس جمینای به دلیل محدودیت کلید برقرار نشد.',
      }),
    );

    render(<SalaryEstimationPage />);
    await user.click(screen.getByRole('button', { name: 'فرانت‌اند React' }));
    await user.click(screen.getByRole('button', { name: 'برآورد حقوق بازار' }));

    await waitFor(() => {
      expect(
        screen.queryByText('سرویس جستجوی زنده هوش مصنوعی در دسترس نیست'),
      ).not.toBeInTheDocument();
      expect(screen.getByLabelText('نتایج برآورد حقوق')).toBeInTheDocument();
      expect(screen.getAllByText('توسعه‌دهنده React').length).toBeGreaterThanOrEqual(1);
    });
  });

  it('renders regulatory legal status badge and opens monitored sources tooltip', async () => {
    const user = userEvent.setup();
    render(<SalaryEstimationPage />);

    expect(screen.getByRole('button', { name: /قوانین جاری/ })).toBeInTheDocument();
    expect(screen.getByText(/قوانین جاری: نسخه/)).toBeInTheDocument();

    // Click badge to toggle monitored sources popover
    await user.click(screen.getByRole('button', { name: /قوانین جاری/ }));

    expect(screen.getByText('مراجع رسمی مانیتور شده')).toBeInTheDocument();
    expect(screen.getByText('روزنامه رسمی جمهوری اسلامی ایران')).toBeInTheDocument();
    expect(screen.getByText('دیوان عدالت اداری (آرای وحدت رویه)')).toBeInTheDocument();
    expect(screen.getByText('سازمان امور مالیاتی کشور')).toBeInTheDocument();
  });
});
