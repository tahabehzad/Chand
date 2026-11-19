/**
 * Document Verification & Career Forensics Panel — Persian RTL.
 *
 * Authority: docs/AI_ANALYSIS_SPEC.md §2, §3; AGENTS.md §2 Domain invariants 1, 4, 7.
 *
 * Enables hiring managers to upload candidate documents (SSO insurance records,
 * payslips, academic degrees, certifications), inspect forensic authenticity
 * markers without judging fraud, and derive verified experience and confidence
 * adjustments to directly feed the salary estimation engine.
 */

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { apiClient } from '@/api/instance';
import { useGeminiApiKey } from '@/hooks/use-gemini-api-key';
import {
  analyzeCareerDocument,
  type DocumentAnalysisResponse,
  type ForensicStatus,
} from '@/api/document-analysis';
import { toPersianDigits } from '@/lib/numerals';
import { formatMoney } from '@/lib/money';

function formatSalaryToman(rialValue: number | null | undefined): string {
  if (rialValue === null || rialValue === undefined) return 'قید نشده';
  const roundedTo10 = Math.round(rialValue / 10) * 10;
  const toman = formatMoney(roundedTo10, 'toman');
  if (toman.ok) return toman.value.text;
  return `${toPersianDigits(String(Math.round(rialValue / 10)))} تومان`;
}

// Standard 1x1 transparent PNG fallback for presets
const PRESET_SAMPLE_PNG =
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';

export type VerifiedFactsPayload = {
  job_title?: string;
  experience_years?: number;
  education?: string;
  confidence_boost_percent: number;
  document_type_fa: string;
  authenticity_score: number;
};

interface DocumentVerificationPanelProps {
  claimedJobTitle?: string;
  claimedExperienceYears?: number;
  claimedEducation?: string;
  onApplyVerifiedFacts?: (payload: VerifiedFactsPayload) => void;
}

export function DocumentVerificationPanel({
  claimedJobTitle = '',
  claimedExperienceYears = 4,
  claimedEducation = '',
  onApplyVerifiedFacts,
}: DocumentVerificationPanelProps) {
  const { apiKey } = useGeminiApiKey();

  const [selectedFile, setSelectedFile] = useState<{
    name: string;
    sizeKb: number;
    mimeType: string;
    base64: string;
  } | null>(null);

  const [claimedTitleInput, setClaimedTitleInput] = useState(claimedJobTitle);
  const [claimedExpInput, setClaimedExpInput] = useState<number>(claimedExperienceYears);

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<DocumentAnalysisResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isApplied, setIsApplied] = useState(false);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setErrorMessage(null);
    setAnalysisResult(null);
    setIsApplied(false);

    if (file.size > 10 * 1024 * 1024) {
      setErrorMessage('حجم فایل انتخاب‌شده بیش از سقف مجاز ۱۰ مگابایت است.');
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string;
      setSelectedFile({
        name: file.name,
        sizeKb: Math.round(file.size / 1024),
        mimeType: file.type || 'image/jpeg',
        base64: result,
      });
    };
    reader.onerror = () => {
      setErrorMessage('خطا در خواندن فایل انتخاب‌شده.');
    };
    reader.readAsDataURL(file);
  };

  const handleSelectPreset = (presetType: 'sso' | 'payslip' | 'degree') => {
    setErrorMessage(null);
    setAnalysisResult(null);
    setIsApplied(false);

    if (presetType === 'sso') {
      setSelectedFile({
        name: 'sso_record_tamin_official.png',
        sizeKb: 342,
        mimeType: 'image/png',
        base64: `data:image/png;base64,${PRESET_SAMPLE_PNG}`,
      });
      setClaimedTitleInput('برنامه‌نویس ارشد پایتون');
      setClaimedExpInput(6);
    } else if (presetType === 'payslip') {
      setSelectedFile({
        name: 'payslip_verified_slip.pdf',
        sizeKb: 184,
        mimeType: 'application/pdf',
        base64: `data:application/pdf;base64,${PRESET_SAMPLE_PNG}`,
      });
      setClaimedTitleInput('توسعه‌دهنده React');
      setClaimedExpInput(3);
    } else {
      setSelectedFile({
        name: 'academic_degree_university.jpg',
        sizeKb: 512,
        mimeType: 'image/jpeg',
        base64: `data:image/jpeg;base64,${PRESET_SAMPLE_PNG}`,
      });
      setClaimedTitleInput('مهندس یادگیری ماشین');
      setClaimedExpInput(4);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setErrorMessage('لطفاً ابتدا فایل سند را بارگذاری کرده یا از نمونه‌های آماده استفاده کنید.');
      return;
    }

    setIsAnalyzing(true);
    setErrorMessage(null);
    try {
      const response = await analyzeCareerDocument(apiClient, {
        file_base64: selectedFile.base64,
        file_name: selectedFile.name,
        mime_type: selectedFile.mimeType,
        claimed_job_title: claimedTitleInput || undefined,
        claimed_experience_years: claimedExpInput,
        claimed_education: claimedEducation || undefined,
        gemini_api_key: apiKey || undefined,
      });
      setAnalysisResult(response);
    } catch (err) {
      setErrorMessage(
        err instanceof Error
          ? err.message
          : 'خطا در برقراری ارتباط با سرویس ارزیابی اصالت اسناد.',
      );
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleApplyToForm = () => {
    if (!analysisResult) return;
    const facts = analysisResult.extracted_facts;
    const impact = analysisResult.salary_impact;

    onApplyVerifiedFacts?.({
      job_title: facts.verified_skills[0] || claimedTitleInput || undefined,
      experience_years:
        impact.recommended_experience_years ?? facts.verified_experience_years ?? undefined,
      education: facts.verified_education_level ?? (claimedEducation || undefined),
      confidence_boost_percent: impact.confidence_boost_percent,
      document_type_fa: facts.document_type_fa,
      authenticity_score: analysisResult.authenticity_score,
    });
    setIsApplied(true);
  };

  const getStatusBadge = (status: ForensicStatus) => {
    switch (status) {
      case 'pass':
        return (
          <Badge tone="success" className="text-[10px] px-1.5 py-0.5">
            تأیید شد ✓
          </Badge>
        );
      case 'warning':
        return (
          <Badge tone="warning" className="text-[10px] px-1.5 py-0.5">
            هشدار ⚠️
          </Badge>
        );
      case 'info':
        return (
          <Badge tone="neutral" className="text-[10px] px-1.5 py-0.5">
            اطلاعات ℹ️
          </Badge>
        );
      case 'fail':
        return (
          <Badge tone="danger" className="text-[10px] px-1.5 py-0.5">
            عدم تطابق ✕
          </Badge>
        );
    }
  };

  return (
    <Card className="rounded-3xl border-border-subtle bg-surface shadow-sm overflow-hidden">
      <CardHeader className="p-6 border-b border-border-subtle bg-surface-raised/40">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="flex size-11 items-center justify-center rounded-2xl bg-accent-teal/15 text-accent-teal-dark dark:text-accent-teal shadow-xs">
              <span className="text-xl" aria-hidden="true">
                🛡️
              </span>
            </div>
            <div>
              <CardTitle className="text-base font-bold text-ink flex items-center gap-2">
                <span>احراز اصالت و سندیت مدارک شغلی</span>
                <span className="text-[11px] font-normal text-ink-muted">
                  (بیمه، فیش حقوقی، مدارک دانشگاهی)
                </span>
              </CardTitle>
              <p className="text-xs text-ink-muted mt-0.5">
                سنجش فورنزیک نشانه‌های اعتبار رسمی و محاسبهٔ اثر مستندات بر دقت و جایگاه حقوق
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="text-[11px] text-ink-muted">نمونه‌های آماده:</span>
            <button
              type="button"
              onClick={() => handleSelectPreset('sso')}
              className="px-2.5 py-1 text-xs font-medium rounded-lg border border-border-subtle bg-surface hover:bg-surface-raised hover:border-brand/40 text-ink transition-colors cursor-pointer"
            >
              📑 سابقه بیمه
            </button>
            <button
              type="button"
              onClick={() => handleSelectPreset('payslip')}
              className="px-2.5 py-1 text-xs font-medium rounded-lg border border-border-subtle bg-surface hover:bg-surface-raised hover:border-brand/40 text-ink transition-colors cursor-pointer"
            >
              🧾 فیش حقوقی
            </button>
            <button
              type="button"
              onClick={() => handleSelectPreset('degree')}
              className="px-2.5 py-1 text-xs font-medium rounded-lg border border-border-subtle bg-surface hover:bg-surface-raised hover:border-brand/40 text-ink transition-colors cursor-pointer"
            >
              🎓 دانشنامه
            </button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-6 space-y-6">
        {/* Upload Zone */}
        <div className="space-y-4">
          <label className="block text-xs font-bold text-ink">
            انتخاب یا کشیدن و رها کردن فایل سند (تصویر JPG/PNG یا PDF):
          </label>
          <div className="relative border-2 border-dashed border-border-subtle hover:border-brand/50 rounded-2xl p-6 text-center bg-surface-raised/30 transition-all cursor-pointer">
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp,application/pdf"
              onChange={handleFileUpload}
              className="absolute inset-0 size-full opacity-0 cursor-pointer"
              title="بارگذاری سند"
            />
            <div className="flex flex-col items-center justify-center space-y-2 pointer-events-none">
              <span className="text-3xl" aria-hidden="true">
                📁
              </span>
              <p className="text-xs font-semibold text-ink">
                برای بارگذاری کلیک کنید یا فایل را اینجا رها کنید
              </p>
              <p className="text-[11px] text-ink-muted">
                پشتیبانی از عکس واضح سوابق بیمه تأمین اجتماعی، حکم کارگزینی، فیش حقوقی رسمی یا دانشنامه (حداکثر ۱۰ مگابایت)
              </p>
            </div>
          </div>

          {selectedFile && (
            <div className="flex items-center justify-between p-3 rounded-xl border border-border-subtle bg-surface-raised text-xs">
              <div className="flex items-center gap-2.5">
                <span className="text-lg">
                  {selectedFile.mimeType.includes('pdf') ? '📄' : '🖼️'}
                </span>
                <div>
                  <p className="font-semibold text-ink">{selectedFile.name}</p>
                  <p className="text-[10px] text-ink-muted">
                    {toPersianDigits(String(selectedFile.sizeKb))} کیلوبایت · {selectedFile.mimeType}
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => {
                  setSelectedFile(null);
                  setAnalysisResult(null);
                }}
                className="text-ink-muted hover:text-danger text-xs px-2 py-1 rounded-md"
              >
                ✕ حذف
              </button>
            </div>
          )}
        </div>

        {/* Claimed Data Alignment */}
        <div className="rounded-2xl border border-border-subtle bg-surface-raised/40 p-4 space-y-3">
          <div className="flex items-center justify-between text-xs">
            <span className="font-bold text-ink flex items-center gap-1.5">
              <span>⚖️</span>
              <span>مشخصات ادعایی کارجو جهت سنجش انطباق</span>
            </span>
            <span className="text-[10px] text-ink-muted">جهت استخراج مغایرت‌های احتمالی سوابق</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <Input
                label="عنوان شغلی ادعایی"
                value={claimedTitleInput}
                onChange={(e) => setClaimedTitleInput(e.target.value)}
                placeholder="مثلاً توسعه‌دهنده React"
                className="text-xs h-9"
              />
            </div>
            <div>
              <Input
                label="سابقه کار ادعاشده (سال)"
                type="number"
                min={0}
                max={50}
                value={claimedExpInput}
                onChange={(e) => setClaimedExpInput(Number(e.target.value))}
                className="text-xs h-9"
              />
            </div>
          </div>
        </div>

        {/* Action Button */}
        <div>
          <Button
            type="button"
            onClick={handleAnalyze}
            disabled={!selectedFile || isAnalyzing}
            className="w-full h-11 text-sm font-bold shadow-md shadow-brand/15"
          >
            {isAnalyzing ? (
              <span className="flex items-center gap-2">
                <span className="size-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
                <span>در حال تحلیل فورنزیک و استخراج نشانه‌های سندیت...</span>
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <span>🔍</span>
                <span>سنجش اصالت و استخراج اثر بر حقوق</span>
              </span>
            )}
          </Button>
        </div>

        {errorMessage && (
          <div className="p-3 rounded-xl border border-danger/30 bg-danger/10 text-xs text-danger leading-relaxed">
            {errorMessage}
          </div>
        )}

        {/* Analysis Results */}
        {analysisResult && (
          <div className="space-y-6 pt-4 border-t border-border-subtle animate-fade-up">
            {/* Top Verdict Header */}
            <div className="rounded-2xl border border-border-subtle bg-surface-raised p-5 space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div
                    className={`flex size-14 items-center justify-center rounded-2xl font-black text-lg ${
                      analysisResult.authenticity_score >= 0.85
                        ? 'bg-accent-emerald/15 text-accent-emerald-dark dark:text-accent-emerald border border-accent-emerald/30'
                        : 'bg-accent-amber/15 text-accent-amber-dark dark:text-accent-amber border border-accent-amber/30'
                    }`}
                  >
                    <span>
                      {toPersianDigits(
                        String(Math.round(analysisResult.authenticity_score * 100)),
                      )}
                      ٪
                    </span>
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-ink">
                        شاخص اصالت و قابلیت استناد سند:
                      </span>
                      <Badge
                        tone={
                          analysisResult.authenticity_verdict === 'verified'
                            ? 'success'
                            : 'warning'
                        }
                        className="text-xs font-bold"
                      >
                        {analysisResult.authenticity_verdict_fa}
                      </Badge>
                    </div>
                    <p className="text-xs text-ink-muted mt-1">
                      نوع سند:{' '}
                      <strong className="text-ink">
                        {analysisResult.extracted_facts.document_type_fa}
                      </strong>{' '}
                      · سازمان صادرکننده:{' '}
                      <span className="text-ink font-medium">
                        {analysisResult.extracted_facts.issuing_organization ||
                          'مراجع ذیصلاح'}
                      </span>
                    </p>
                  </div>
                </div>

                <div className="text-end">
                  <span className="text-[11px] text-ink-muted block">
                    کد رهگیری / شماره سند:
                  </span>
                  <span className="font-mono text-xs font-bold text-brand" dir="ltr">
                    {analysisResult.extracted_facts.document_number || 'نشان‌دار'}
                  </span>
                </div>
              </div>

              {/* Forensic Indicators List */}
              <div className="space-y-2 pt-2 border-t border-border-subtle">
                <span className="text-[11px] font-bold text-ink block">
                  نشانه‌های بررسی‌شدهٔ فورنزیک و ضدتقلب:
                </span>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {analysisResult.forensic_indicators.map((indicator, index) => (
                    <div
                      key={index}
                      className="p-2.5 rounded-xl border border-border-subtle bg-surface flex items-start justify-between gap-2 text-xs"
                    >
                      <div className="space-y-0.5">
                        <span className="font-semibold text-ink">
                          {indicator.name}
                        </span>
                        <p className="text-[11px] text-ink-muted leading-relaxed">
                          {indicator.detail}
                        </p>
                      </div>
                      <div className="shrink-0">{getStatusBadge(indicator.status)}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Extracted Facts & Discrepancies */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="p-3.5 rounded-2xl border border-border-subtle bg-surface-raised space-y-1">
                <span className="text-[10px] text-ink-muted block">
                  سابقه بیمه رسمی قطعی:
                </span>
                <span className="text-base font-black text-brand">
                  {analysisResult.extracted_facts.verified_experience_years !== null
                    ? `${toPersianDigits(String(analysisResult.extracted_facts.verified_experience_years))} سال رسمی`
                    : 'نامشخص در سند'}
                </span>
              </div>

              <div className="p-3.5 rounded-2xl border border-border-subtle bg-surface-raised space-y-1">
                <span className="text-[10px] text-ink-muted block">
                  آخرین حقوق ناخالص احراز‌شده:
                </span>
                <span className="text-base font-black text-accent-emerald-dark dark:text-accent-emerald">
                  {formatSalaryToman(
                    analysisResult.extracted_facts.verified_last_salary_rial,
                  )}
                </span>
              </div>

              <div className="p-3.5 rounded-2xl border border-border-subtle bg-surface-raised space-y-1">
                <span className="text-[10px] text-ink-muted block">
                  مقطع تحصیلی / تخصص:
                </span>
                <span className="text-xs font-bold text-ink truncate block">
                  {analysisResult.extracted_facts.verified_education_level ||
                    (analysisResult.extracted_facts.verified_skills.length > 0
                      ? analysisResult.extracted_facts.verified_skills.join('، ')
                      : 'عمومی')}
                </span>
              </div>
            </div>

            {/* Salary Impact & Strategy Card */}
            <div className="rounded-2xl border border-brand/20 bg-brand/5 p-4 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-base" aria-hidden="true">
                    ⚡
                  </span>
                  <span className="font-bold text-xs text-brand">
                    اثر استناد بر استراتژی پیشنهاد دستمزد و مذاکره
                  </span>
                </div>
                <Badge tone="success" className="text-xs">
                  افزایش اطمینان:{' '}
                  {toPersianDigits(
                    String(analysisResult.salary_impact.confidence_boost_percent),
                  )}
                  ٪+
                </Badge>
              </div>

              <p className="text-xs text-ink leading-relaxed">
                {analysisResult.salary_impact.explanation_fa}
              </p>

              {analysisResult.salary_impact.discrepancy_detected && (
                <div className="p-3 rounded-xl border border-accent-amber/30 bg-accent-amber/10 text-xs text-accent-amber-dark dark:text-accent-amber leading-relaxed space-y-1">
                  <div className="font-bold flex items-center gap-1.5">
                    <span>⚠️</span>
                    <span>توصیهٔ بازبینی مدیر استخدام (عدم تطابق ادعا و مستندات):</span>
                  </div>
                  <p>{analysisResult.salary_impact.discrepancy_message_fa}</p>
                </div>
              )}
            </div>

            {/* Apply Button */}
            <div className="pt-2">
              <Button
                type="button"
                variant="primary"
                onClick={handleApplyToForm}
                disabled={isApplied}
                className="w-full h-11 text-xs font-bold flex items-center justify-center gap-2 shadow-md shadow-brand/20"
              >
                <span>⚡</span>
                <span>
                  {isApplied
                    ? '✓ اطلاعات مستند در فرم برآورد اعمال گردید'
                    : 'اعمال سوابق و مهارت‌های مستند در فرم برآورد حقوق'}
                </span>
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
