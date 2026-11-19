/**
 * Print & PDF Export Component — Persian RTL.
 *
 * Provides a one-click "دانلود گزارش PDF" button calling `window.print()`,
 * and embeds the clean branded header that renders exclusively in print mode.
 *
 * Authority: ADR-014, WBS P4-T03.
 */

import { Button } from '@/components/ui/button';
import { toPersianDigits } from '@/lib/numerals';
import type { SalaryEstimationResponse } from '@/api/salary-estimation';

export type PdfExportProps = {
  result?: SalaryEstimationResponse | null;
  className?: string;
};

export function PdfExport({ result, className = '' }: PdfExportProps) {
  const handlePrint = () => {
    window.print();
  };

  const currentDateFa = new Intl.DateTimeFormat('fa-IR', {
    dateStyle: 'long',
    timeZone: 'Asia/Tehran',
  }).format(new Date());

  return (
    <>
      {/* Interactive PDF Download Button (Hidden in Print) */}
      <div className={`no-print ${className}`}>
        <Button
          type="button"
          variant="secondary"
          onClick={handlePrint}
          className="flex items-center gap-2 font-medium text-xs sm:text-sm py-2 px-3.5 rounded-xl border border-border-subtle bg-surface hover:bg-surface-raised shadow-xs transition-all cursor-pointer"
          title="چاپ یا ذخیره به صورت فایل PDF"
        >
          <span className="text-base" aria-hidden="true">🖨️</span>
          <span>دانلود گزارش PDF</span>
        </Button>
      </div>

      {/* Print-Only Branded Report Header */}
      {result ? (
        <div className="print-only print-header border-b-2 border-slate-900 pb-4 mb-6">
          <div className="flex items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-black text-slate-900 tracking-tight">چند؟</span>
                <span className="text-xs text-slate-500">| سامانه هوشمند جبران خدمات</span>
              </div>
              <h1 className="text-lg font-bold text-slate-900 mt-1">
                چند؟ — گزارش برآورد حقوق و هزینه استخدام
              </h1>
            </div>
            <div className="text-end text-xs text-slate-600 space-y-0.5">
              <p>تاریخ صدور: {currentDateFa}</p>
              <p>مبنای قانونی: سال ۱۴۰۴</p>
            </div>
          </div>

          <div className="mt-3 grid grid-cols-4 gap-2 rounded-lg bg-slate-50 p-2 text-xs border border-slate-200">
            <div>
              <span className="font-semibold text-slate-700">عنوان شغلی: </span>
              <span>{result.match.family_title_fa ?? result.job_title}</span>
            </div>
            <div>
              <span className="font-semibold text-slate-700">سابقه کار: </span>
              <span>{toPersianDigits(String(result.experience_years))} سال</span>
            </div>
            <div>
              <span className="font-semibold text-slate-700">سطح تخصص: </span>
              <span>{result.seniority_level}</span>
            </div>
            <div>
              <span className="font-semibold text-slate-700">شهر: </span>
              <span>{result.city}</span>
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}
