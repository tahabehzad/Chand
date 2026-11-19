import { describe, expect, it, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { DocumentVerificationPanel } from '../DocumentVerificationPanel';
import * as documentAnalysisApi from '@/api/document-analysis';

vi.mock('@/api/document-analysis', async () => {
  const actual = await vi.importActual<typeof import('@/api/document-analysis')>('@/api/document-analysis');
  return {
    ...actual,
    analyzeCareerDocument: vi.fn(),
  };
});

describe('DocumentVerificationPanel', () => {
  it('renders correctly with upload prompt and preset buttons', () => {
    render(<DocumentVerificationPanel />);
    expect(screen.getByText('احراز اصالت و سندیت مدارک شغلی')).toBeInTheDocument();
    expect(screen.getByText('📑 سابقه بیمه')).toBeInTheDocument();
    expect(screen.getByText('🧾 فیش حقوقی')).toBeInTheDocument();
    expect(screen.getByText('🎓 دانشنامه')).toBeInTheDocument();
  });

  it('selects preset sample and displays file information', () => {
    render(<DocumentVerificationPanel />);
    const ssoPreset = screen.getByText('📑 سابقه بیمه');
    fireEvent.click(ssoPreset);

    expect(screen.getByText('sso_record_tamin_official.png')).toBeInTheDocument();
    expect(screen.getByDisplayValue('برنامه‌نویس ارشد پایتون')).toBeInTheDocument();
  });

  it('analyzes document and displays authenticity verdict and indicators', async () => {
    const mockResponse: documentAnalysisApi.DocumentAnalysisResponse = {
      authenticity_score: 0.96,
      authenticity_verdict: 'verified',
      authenticity_verdict_fa: 'تأییدشده و رسمی',
      forensic_indicators: [
        {
          name: 'آرم و سربرگ رسمی',
          status: 'pass',
          detail: 'سربرگ رسمی با وضوح بالا احراز شد.',
        },
      ],
      extracted_facts: {
        document_type: 'sso_record',
        document_type_fa: 'سابقه پرداخت حق بیمه سازمان تأمین اجتماعی',
        issuing_organization: 'شعبه ۲۲ تهران',
        document_number: 'SSO-9912',
        issue_date_shamsi: '1403/07/20',
        verified_experience_years: 4,
        verified_last_salary_rial: 345000000,
        verified_education_level: null,
        verified_skills: ['پایتون'],
        employer_names: ['شرکت داده‌پردازی'],
      },
      salary_impact: {
        confidence_boost_percent: 20,
        market_quartile_recommendation: 'top_quartile',
        recommended_experience_years: 4,
        discrepancy_detected: false,
        discrepancy_message_fa: null,
        explanation_fa: '۴ سال سابقه قطعی احراز شد.',
      },
      analysis_timestamp: '2026-11-19T06:00:00Z',
    };

    vi.mocked(documentAnalysisApi.analyzeCareerDocument).mockResolvedValueOnce(mockResponse);

    const onApply = vi.fn();
    render(<DocumentVerificationPanel onApplyVerifiedFacts={onApply} />);

    // Select SSO preset
    fireEvent.click(screen.getByText('📑 سابقه بیمه'));

    // Click analyze button
    const analyzeButton = screen.getByText('سنجش اصالت و استخراج اثر بر حقوق');
    fireEvent.click(analyzeButton);

    await waitFor(() => {
      expect(screen.getByText('تأییدشده و رسمی')).toBeInTheDocument();
      expect(screen.getByText('شعبه ۲۲ تهران')).toBeInTheDocument();
      expect(screen.getByText('آرم و سربرگ رسمی')).toBeInTheDocument();
      expect(screen.getByText('۴ سال سابقه قطعی احراز شد.')).toBeInTheDocument();
    });

    // Click apply to form
    const applyButton = screen.getByText('اعمال سوابق و مهارت‌های مستند در فرم برآورد حقوق');
    fireEvent.click(applyButton);

    expect(onApply).toHaveBeenCalledWith({
      job_title: 'پایتون',
      experience_years: 4,
      education: undefined,
      confidence_boost_percent: 20,
      document_type_fa: 'سابقه پرداخت حق بیمه سازمان تأمین اجتماعی',
      authenticity_score: 0.96,
    });

    expect(screen.getByText('✓ اطلاعات مستند در فرم برآورد اعمال گردید')).toBeInTheDocument();
  });
});
