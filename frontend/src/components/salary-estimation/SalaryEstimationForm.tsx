/**
 * Salary estimation profile form — Persian RTL.
 *
 * Collects exactly what the estimation engine consumes. Nothing collected here is
 * turned into a number on the client: the backend decides the figure.
 *
 * Fields that do not change the published figure (education, skills) are still
 * collected because they drive the job-family match and the explanation — the
 * output says so explicitly instead of implying a hidden multiplier.
 */

import { useEffect, useState, useRef, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/cn';
import { toPersianDigits } from '@/lib/numerals';
import { CHAND_JOBS, type ChandJob } from '@/data/chandJobs';

function highlightAutofillMatch(text: string, query: string) {
  if (!query) return text;
  const idx = text.toLowerCase().indexOf(query.toLowerCase());
  if (idx === -1) return text;
  return (
    <>
      {text.slice(0, idx)}
      <mark>{text.slice(idx, idx + query.length)}</mark>
      {text.slice(idx + query.length)}
    </>
  );
}

const SKILL_OPTIONS = [
  'PHP',
  'Laravel',
  'React',
  'TypeScript',
  'Node.js',
  'Python',
  'Django',
  'AWS',
  'Docker',
  'SQL',
];

const CITY_OPTIONS = [
  { value: 'تهران', label: 'تهران' },
  { value: 'اصفهان', label: 'اصفهان' },
  { value: 'مشهد', label: 'مشهد' },
  { value: 'شیراز', label: 'شیراز' },
  { value: 'تبریز', label: 'تبریز' },
  { value: 'کرج', label: 'کرج' },
  { value: 'اهواز', label: 'اهواز' },
  { value: 'قم', label: 'قم' },
  { value: 'رشت', label: 'رشت' },
  { value: 'کرمانشاه', label: 'کرمانشاه' },
  { value: 'ارومیه', label: 'ارومیه' },
  { value: 'یزد', label: 'یزد' },
  { value: 'همدان', label: 'همدان' },
  { value: 'اراک', label: 'اراک' },
  { value: 'زنجان', label: 'زنجان' },
  { value: 'قزوین', label: 'قزوین' },
  { value: 'ساری', label: 'ساری' },
  { value: 'گرگان', label: 'گرگان' },
  { value: 'کرمان', label: 'کرمان' },
  { value: 'بندرعباس', label: 'بندرعباس' },
  { value: 'بوشهر', label: 'بوشهر' },
  { value: 'خرم‌آباد', label: 'خرم‌آباد' },
  { value: 'سنندج', label: 'سنندج' },
  { value: 'اردبیل', label: 'اردبیل' },
  { value: 'زاهدان', label: 'زاهدان' },
  { value: 'سمنان', label: 'سمنان' },
  { value: 'شهرکرد', label: 'شهرکرد' },
  { value: 'یاسوج', label: 'یاسوج' },
  { value: 'ایلام', label: 'ایلام' },
  { value: 'بیرجند', label: 'بیرجند' },
  { value: 'بجنورد', label: 'بجنورد' },
  { value: 'ساوه', label: 'ساوه' },
  { value: 'عسلویه', label: 'عسلویه' },
  { value: 'کیش', label: 'کیش' },
  { value: 'سایر', label: 'سایر شهرها…' },
];

const SENIORITY_OPTIONS = [
  { value: 'junior', label: 'جونیور' },
  { value: 'mid', label: 'میان‌رده' },
  { value: 'senior', label: 'ارشد' },
] as const;

const EMPLOYMENT_TYPE_OPTIONS = [
  { value: 'full_time', label: 'تمام‌وقت' },
  { value: 'part_time', label: 'نیمه‌وقت' },
  { value: 'contract', label: 'قراردادی' },
  { value: 'freelance', label: 'آزاد' },
] as const;

const WORK_CONDITION_OPTIONS = [
  { value: 'on_site', label: 'حضوری' },
  { value: 'remote', label: 'دورکاری' },
  { value: 'hybrid', label: 'ترکیبی' },
] as const;

const PRESET_PROFILES = [
  {
    label: 'فرانت‌اند React',
    icon: '⚛️',
    job_title: 'توسعه‌دهنده React',
    experience_years: 3,
    seniority_level: 'mid' as const,
    employment_type: 'full_time' as const,
    work_condition: 'hybrid' as const,
    city: 'تهران',
    province: 'تهران',
    job_description: 'توسعه اپلیکیشن‌های فرانت‌اند با React و Next.js',
    education: 'کارشناسی کامپیوتر',
    skills: ['React', 'TypeScript'],
  },
  {
    label: 'بک‌اند پایتون',
    icon: '🐍',
    job_title: 'برنامه‌نویس پایتون',
    experience_years: 4,
    seniority_level: 'mid' as const,
    employment_type: 'full_time' as const,
    work_condition: 'on_site' as const,
    city: 'تهران',
    province: 'تهران',
    job_description: 'توسعه وب‌سرویس و API با پایتون و جنگو',
    education: 'کارشناسی نرم‌افزار',
    skills: ['Python', 'Django', 'SQL'],
  },
  {
    label: 'مدیر محصول',
    icon: '📊',
    job_title: 'مدیر محصول',
    experience_years: 6,
    seniority_level: 'senior' as const,
    employment_type: 'full_time' as const,
    work_condition: 'on_site' as const,
    city: 'تهران',
    province: 'تهران',
    job_description: 'مدیریت چرخه عمر محصول و تدوین استراتژی محصول',
    education: 'کارشناسی ارشد MBA',
    skills: ['SQL'],
  },
] as const;

export type SalaryEstimationFormData = {
  job_title: string;
  experience_years: number;
  seniority_level: 'junior' | 'mid' | 'senior';
  employment_type: 'full_time' | 'part_time' | 'contract' | 'freelance';
  work_condition: 'on_site' | 'remote' | 'hybrid';
  city: string;
  province: string;
  job_description: string;
  education: string;
  skills: string[];
};

const selectClass =
  'min-h-12 h-12 w-full rounded-xl border border-border-subtle bg-surface-raised px-3.5 py-2.5 text-sm text-ink transition-all duration-200 focus-visible:border-brand focus-visible:ring-1 focus-visible:ring-brand';

export type SalaryEstimationFormProps = {
  onSubmit: (data: SalaryEstimationFormData) => void;
  isBusy?: boolean;
  initialValues?: Partial<SalaryEstimationFormData>;
  verifiedEvidenceBadge?: {
    documentTypeFa: string;
    confidenceBoostPercent: number;
    verifiedExperience: number | null;
  } | null;
};

export function SalaryEstimationForm({
  onSubmit,
  isBusy = false,
  initialValues,
  verifiedEvidenceBadge,
}: SalaryEstimationFormProps) {
  const [jobTitle, setJobTitle] = useState('');
  const [experienceYears, setExperienceYears] = useState(5);
  const [seniorityLevel, setSeniorityLevel] = useState<'junior' | 'mid' | 'senior'>('mid');
  const [employmentType, setEmploymentType] =
    useState<'full_time' | 'part_time' | 'contract' | 'freelance'>('full_time');
  const [workCondition, setWorkCondition] = useState<'on_site' | 'remote' | 'hybrid'>('on_site');
  const [city, setCity] = useState('تهران');
  const [customCity, setCustomCity] = useState('');
  const [province, setProvince] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [education, setEducation] = useState('');
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [isAutofillOpen, setIsAutofillOpen] = useState(false);
  const [autofillHighlightIdx, setAutofillHighlightIdx] = useState(-1);
  const autofillContainerRef = useRef<HTMLDivElement>(null);

  const filteredJobs = useMemo(() => {
    if (!isAutofillOpen) return [];
    const q = jobTitle.trim().toLowerCase();
    if (!q) return CHAND_JOBS.slice(0, 8);
    return CHAND_JOBS.filter(
      (j) => j.t.toLowerCase().includes(q) || j.c.toLowerCase().includes(q),
    ).slice(0, 8);
  }, [jobTitle, isAutofillOpen]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        autofillContainerRef.current &&
        !autofillContainerRef.current.contains(event.target as Node)
      ) {
        setIsAutofillOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const selectJob = (job: ChandJob) => {
    setJobTitle(job.t);
    setIsAutofillOpen(false);
    setAutofillHighlightIdx(-1);
    if (job.skills && job.skills.length > 0 && selectedSkills.length === 0) {
      setSelectedSkills(job.skills.slice(0, 3));
    }
  };

  useEffect(() => {
    if (initialValues) {
      if (initialValues.job_title !== undefined) setJobTitle(initialValues.job_title);
      if (initialValues.experience_years !== undefined) setExperienceYears(initialValues.experience_years);
      if (initialValues.education !== undefined) setEducation(initialValues.education || '');
      if (initialValues.seniority_level !== undefined) setSeniorityLevel(initialValues.seniority_level);
      if (initialValues.city !== undefined) setCity(initialValues.city);
      if (initialValues.skills && Array.isArray(initialValues.skills)) {
        setSelectedSkills(initialValues.skills);
      }
    }
  }, [initialValues]);

  const errors: Record<string, string> = {};
  if (!jobTitle.trim()) errors.job_title = 'عنوان شغل الزامی است';
  if (experienceYears < 0 || experienceYears > 60) {
    errors.experience_years = 'سابقه باید بین ۰ تا ۶۰ سال باشد';
  }
  const hasErrors = Object.keys(errors).length > 0;

  const toggleSkill = (skill: string) => {
    setSelectedSkills((previous) =>
      previous.includes(skill) ? previous.filter((item) => item !== skill) : [...previous, skill],
    );
  };

  const applyPreset = (preset: (typeof PRESET_PROFILES)[number]) => {
    setJobTitle(preset.job_title);
    setExperienceYears(preset.experience_years);
    setSeniorityLevel(preset.seniority_level);
    setEmploymentType(preset.employment_type);
    setWorkCondition(preset.work_condition);
    setCity(preset.city);
    setProvince(preset.province);
    setJobDescription(preset.job_description);
    setEducation(preset.education);
    setSelectedSkills([...preset.skills]);
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (hasErrors || isBusy) return;
    onSubmit({
      job_title: jobTitle.trim(),
      experience_years: experienceYears,
      seniority_level: seniorityLevel,
      employment_type: employmentType,
      work_condition: workCondition,
      city: city === 'سایر' ? (customCity.trim() || 'ایران') : city,
      province: province.trim(),
      job_description: jobDescription.trim(),
      education: education.trim(),
      skills: selectedSkills,
    });
  };

  return (
    <form onSubmit={handleSubmit} className='space-y-6' noValidate>
      <Card>
        <CardHeader>
          <CardTitle>پروفایل داوطلب</CardTitle>
          <p className='mt-1 text-xs text-ink-muted'>
            شهر، سطح تخصص و نوع استخدام، گروه مقایسهٔ بازار را تعیین می‌کنند؛ ضریب جداگانه‌ای روی
            نتیجه اعمال نمی‌شود.
          </p>
        </CardHeader>
        <CardContent className='space-y-6 pb-24 lg:pb-6'>
          {verifiedEvidenceBadge && (
            <div className='rounded-2xl border border-accent-emerald/40 bg-accent-emerald/10 p-3.5 flex flex-wrap items-center justify-between gap-2 text-xs animate-fade-up'>
              <div className='flex items-center gap-2'>
                <span className='text-base' aria-hidden='true'>🛡️</span>
                <div>
                  <p className='font-bold text-accent-emerald-dark dark:text-accent-emerald'>
                    اطلاعات سوابق شغلی مستند به «{verifiedEvidenceBadge.documentTypeFa}» اعمال شد
                  </p>
                  <p className='text-[11px] text-ink-muted mt-0.5'>
                    {verifiedEvidenceBadge.verifiedExperience !== null
                      ? `سابقهٔ قطعی احراز‌شده: ${toPersianDigits(String(verifiedEvidenceBadge.verifiedExperience))} سال · `
                      : ''}
                    افزایش ضریب اطمینان استخدامی: +{toPersianDigits(String(verifiedEvidenceBadge.confidenceBoostPercent))}٪
                  </p>
                </div>
              </div>
              <Badge tone='success' className='text-[11px] font-bold'>
                احراز رسمی ✓
              </Badge>
            </div>
          )}

          <div className='flex flex-wrap items-center gap-2 rounded-2xl bg-surface p-3.5 border border-border-subtle shadow-xs'>
            <span className='text-xs font-bold text-ink-muted flex items-center gap-1.5 shrink-0'>
              <span aria-hidden='true'>⚡</span>
              <span>نمونه‌های آماده:</span>
            </span>
            <div className='overflow-x-auto flex gap-2 snap-x pb-1 w-full sm:w-auto scrollbar-none'>
              {PRESET_PROFILES.map((preset) => (
                <button
                  key={preset.label}
                  type='button'
                  onClick={() => applyPreset(preset)}
                  className='min-h-[36px] snap-start shrink-0 cursor-pointer rounded-xl border border-border-subtle bg-surface-raised px-3.5 py-2 text-xs font-medium text-ink transition-all hover:border-brand hover:text-brand hover:shadow-xs active:scale-95 flex items-center gap-1.5'
                >
                  <span aria-hidden='true'>{preset.icon}</span>
                  <span>{preset.label}</span>
                </button>
              ))}
            </div>
          </div>

          <div className='grid gap-4 grid-cols-1 sm:grid-cols-2'>
            <div className='relative' ref={autofillContainerRef}>
              <Input
                label='عنوان شغلی'
                value={jobTitle}
                onChange={(event) => {
                  setJobTitle(event.target.value);
                  setIsAutofillOpen(true);
                  setAutofillHighlightIdx(-1);
                }}
                onFocus={() => {
                  setIsAutofillOpen(true);
                  setAutofillHighlightIdx(-1);
                }}
                onKeyDown={(e) => {
                  if (!isAutofillOpen || filteredJobs.length === 0) {
                    if (e.key === 'ArrowDown') {
                      setIsAutofillOpen(true);
                    }
                    return;
                  }
                  if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    setAutofillHighlightIdx((prev) => (prev + 1) % filteredJobs.length);
                  } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    setAutofillHighlightIdx(
                      (prev) => (prev - 1 + filteredJobs.length) % filteredJobs.length,
                    );
                  } else if (e.key === 'Enter') {
                    if (autofillHighlightIdx >= 0 && filteredJobs[autofillHighlightIdx]) {
                      e.preventDefault();
                      selectJob(filteredJobs[autofillHighlightIdx]);
                    }
                  } else if (e.key === 'Escape') {
                    setIsAutofillOpen(false);
                  }
                }}
                placeholder='مثلاً برنامه‌نویس پایتون، مدیر محصول، حسابدار...'
                error={errors.job_title}
                className='h-12 min-h-12'
                autoComplete='off'
              />
              {isAutofillOpen && filteredJobs.length > 0 && (
                <div
                  role='listbox'
                  className='chand-autofill absolute top-full inset-x-0 w-full z-50 shadow-2xl max-h-64 overflow-y-auto'
                  style={{ display: 'block' }}
                >
                  {filteredJobs.map((job, idx) => {
                    const isHighlight = idx === autofillHighlightIdx;
                    return (
                      <div
                        key={job.t}
                        role='option'
                        aria-selected={isHighlight}
                        className={cn('opt', isHighlight && 'active')}
                        onMouseDown={(e) => {
                          e.preventDefault();
                          selectJob(job);
                        }}
                      >
                        <span>{highlightAutofillMatch(job.t, jobTitle.trim())}</span>
                        <small>{job.c}</small>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
            <div className='flex flex-col'>
              <Input
                label='سابقهٔ کاری (سال)'
                type='number'
                inputMode='numeric'
                value={experienceYears}
                onChange={(event) => setExperienceYears(Number(event.target.value) || 0)}
                dir='ltr'
                min={0}
                max={60}
                error={errors.experience_years}
                className='h-12 min-h-12'
              />
              <div className='flex items-center justify-between gap-2 mt-2 px-0.5'>
                <div className='flex items-center gap-1.5'>
                  <button
                    type='button'
                    onClick={() => setExperienceYears((prev) => Math.max(0, prev - 1))}
                    disabled={experienceYears <= 0}
                    className='size-11 min-w-[44px] min-h-[44px] rounded-xl border border-border-subtle bg-surface hover:bg-surface-raised active:bg-surface-muted text-base font-bold text-ink flex items-center justify-center transition-all disabled:opacity-40 cursor-pointer shadow-xs'
                    title='کاهش یک سال'
                    aria-label='کاهش سابقه کاری'
                  >
                    -
                  </button>
                  <button
                    type='button'
                    onClick={() => setExperienceYears((prev) => Math.min(60, prev + 1))}
                    disabled={experienceYears >= 60}
                    className='size-11 min-w-[44px] min-h-[44px] rounded-xl border border-border-subtle bg-surface hover:bg-surface-raised active:bg-surface-muted text-base font-bold text-ink flex items-center justify-center transition-all disabled:opacity-40 cursor-pointer shadow-xs'
                    title='افزایش یک سال'
                    aria-label='افزایش سابقه کاری'
                  >
                    +
                  </button>
                </div>
                <span className='text-[11px] text-ink-muted font-medium'>
                  {experienceYears <= 2
                    ? 'کارآموز / تازه‌کار (Junior)'
                    : experienceYears <= 5
                      ? 'میان‌رده با تجربه (Mid-level)'
                      : experienceYears <= 9
                        ? 'ارشد و تخصصی (Senior)'
                        : 'راهبر فنی / سرپرست (Lead)'}
                </span>
              </div>
            </div>
          </div>

          <div className='grid gap-4 grid-cols-1 sm:grid-cols-3'>
            <div className='flex flex-col gap-2'>
              <label htmlFor='seniority' className='text-sm font-medium text-ink'>
                سطح تخصص
              </label>
              <select
                id='seniority'
                value={seniorityLevel}
                onChange={(event) =>
                  setSeniorityLevel(event.target.value as 'junior' | 'mid' | 'senior')
                }
                className={selectClass}
              >
                {SENIORITY_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div className='flex flex-col gap-2'>
              <label htmlFor='employment-type' className='text-sm font-medium text-ink'>
                نوع استخدام
              </label>
              <select
                id='employment-type'
                value={employmentType}
                onChange={(event) =>
                  setEmploymentType(
                    event.target.value as 'full_time' | 'part_time' | 'contract' | 'freelance',
                  )
                }
                className={selectClass}
              >
                {EMPLOYMENT_TYPE_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div className='flex flex-col gap-2'>
              <label htmlFor='work-condition' className='text-sm font-medium text-ink'>
                شرایط کاری
              </label>
              <select
                id='work-condition'
                value={workCondition}
                onChange={(event) =>
                  setWorkCondition(event.target.value as 'on_site' | 'remote' | 'hybrid')
                }
                className={selectClass}
              >
                {WORK_CONDITION_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className='grid gap-4 grid-cols-1 sm:grid-cols-3'>
            <div className='flex flex-col gap-2'>
              <label htmlFor='city' className='text-sm font-medium text-ink'>
                استان
              </label>
              <select
                id='city'
                value={city}
                onChange={(event) => setCity(event.target.value)}
                className={selectClass}
              >
                {CITY_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              {city === 'سایر' && (
                <div className='mt-2'>
                  <Input
                    label='نام شهر خود را بنویسید'
                    value={customCity}
                    onChange={(event) => setCustomCity(event.target.value)}
                    placeholder='مثلاً نیشابور، مراغه، ساوه...'
                    className='h-12 min-h-12'
                  />
                </div>
              )}
            </div>
            <Input
              label='استان (اختیاری)'
              value={province}
              onChange={(event) => setProvince(event.target.value)}
              placeholder='مثلاً تهران'
              className='h-12 min-h-12'
            />
            <Input
              label='تحصیلات (اختیاری)'
              value={education}
              onChange={(event) => setEducation(event.target.value)}
              placeholder='مثلاً کارشناسی نرم‌افزار'
              className='h-12 min-h-12'
            />
          </div>

          <div className='flex flex-col gap-2'>
            <label htmlFor='job-description' className='text-sm font-medium text-ink'>
              شرح وظایف (اختیاری)
            </label>
            <textarea
              id='job-description'
              value={jobDescription}
              onChange={(event) => setJobDescription(event.target.value)}
              rows={3}
              maxLength={4000}
              placeholder='مثلاً توسعه و نگهداری سرویس‌های PHP و Laravel'
              className='w-full rounded-xl border border-border-subtle bg-surface-raised px-3.5 py-2.5 text-sm text-ink transition-all duration-200 focus-visible:border-brand focus-visible:ring-1 focus-visible:ring-brand'
            />
            <p className='text-xs text-ink-muted'>
              شرح وظایف فقط برای تشخیص گروه شغلی استفاده می‌شود، نه برای تغییر عدد.
            </p>
          </div>

          <div className='border-t border-border-subtle pt-6'>
            <div className='flex items-center justify-between mb-3'>
              <h3 className='font-semibold text-ink flex items-center gap-2 text-sm'>
                <span aria-hidden='true'>⚡</span>
                <span>مهارت‌ها (اختیاری)</span>
              </h3>
              {selectedSkills.length > 0 && (
                <button
                  type='button'
                  onClick={() => setSelectedSkills([])}
                  className='text-[11px] text-ink-muted hover:text-danger transition-colors cursor-pointer'
                >
                  پاک کردن انتخاب‌ها
                </button>
              )}
            </div>
            <div className='overflow-x-auto flex gap-2 snap-x pb-2 pt-1 scrollbar-none sm:flex-wrap'>
              {SKILL_OPTIONS.map((skill) => {
                const isSelected = selectedSkills.includes(skill);
                return (
                  <button
                    key={skill}
                    type='button'
                    aria-pressed={isSelected}
                    onClick={() => toggleSkill(skill)}
                    className='min-h-[36px] snap-start shrink-0 cursor-pointer select-none rounded-xl transition-all duration-200 hover:scale-105 active:scale-95 flex items-center'
                  >
                    <Badge
                      tone={isSelected ? 'info' : 'neutral'}
                      className={cn(
                        'min-h-[36px] px-3.5 py-2 text-xs transition-all flex items-center gap-1.5 rounded-xl',
                        isSelected && 'border-brand/40 bg-brand/10 text-brand font-bold shadow-xs'
                      )}
                    >
                      {isSelected && <span className="text-[10px]" aria-hidden="true">✓</span>}
                      <span>{skill}</span>
                    </Badge>
                  </button>
                );
              })}
            </div>
          </div>

          {/* CTA Action Button: Responsive fixed bottom on mobile (<lg) / sticky within form on desktop (lg) */}
          <div className="fixed bottom-0 inset-x-0 z-30 border-t border-border-subtle bg-surface/95 p-3 backdrop-blur-md pb-[max(0.75rem,env(safe-area-inset-bottom))] shadow-lg lg:static lg:p-0 lg:bg-transparent lg:border-none lg:shadow-none lg:backdrop-blur-none lg:pt-4">
            <Button
              type='submit'
              variant='gradient'
              disabled={hasErrors || isBusy}
              size='lg'
              className='h-14 lg:h-12 min-h-12 w-full rounded-xl bg-brand hover:bg-brand-strong text-white font-bold text-base shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 cursor-pointer active:scale-[0.99]'
            >
              {isBusy ? (
                <>
                  <span className='size-4 rounded-full border-2 border-white/30 border-t-white animate-spin' aria-hidden='true' />
                  <span>در حال برآورد…</span>
                </>
              ) : (
                'برآورد حقوق بازار'
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </form>
  );
}
