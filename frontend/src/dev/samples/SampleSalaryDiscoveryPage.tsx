import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { SALARY_BENCHMARKS, getSalaryStatsByCityAndJob, getAllCities, getAllJobTitles, type SalaryBenchmark, type JobCityStats } from '@/dev/sample-market-benchmarks';
import { formatMoney } from '@/lib/money';

const POPULAR_JOBS = ['توسعه‌دهنده فرانت‌اند', 'حسابدار', 'منشی', 'راننده', 'فروشنده', 'برنامه‌نویس'];
const POPULAR_CITIES = ['تهران', 'اصفهان', 'کرج', 'مشهد', 'شیراز', 'اهواز', 'تبریز', 'ساوه'];
const EXPERIENCE_LEVELS = [
  { value: '0-1', label: '۰-۱ سال' },
  { value: '1-3', label: '۱-۳ سال' },
  { value: '3-5', label: '۳-۵ سال' },
  { value: '5+', label: '۵+ سال' },
];

function moneyText(value: number, unit: 'rial' | 'toman' = 'rial'): string {
  const result = formatMoney(value, unit);
  if (result.ok) {
    return result.value.text;
  }
  return `${value} ${unit === 'toman' ? 'تومان' : 'ریال'}`;
}

export function SalaryDiscoveryPage() {
  const [searchParams, setSearchParams] = useState({
    jobTitle: '',
    city: '',
    experience: '',
  });

  const [results, setResults] = useState<JobCityStats[]>([]);
  const [selectedBenchmark, setSelectedBenchmark] = useState<JobCityStats | null>(null);

  const handleSearch = () => {
    const { jobTitle, city, experience } = searchParams;

    let filtered = SALARY_BENCHMARKS;

    if (jobTitle) {
      filtered = filtered.filter(b => b.jobTitle === jobTitle);
    }

    if (city) {
      filtered = filtered.filter(b => b.city === city);
    }

    if (experience) {
      const parts = experience.split('-');
      const minStr = parts[0] ?? '0';
      const maxStr = parts[1];
      const minYears = minStr === '5+' ? 5 : parseInt(minStr, 10) || 0;
      const maxYears = maxStr === undefined || maxStr === '5+' ? 99 : parseInt(maxStr, 10) || 99;
      filtered = filtered.filter((b): b is SalaryBenchmark => {
        return b.experienceRange.min >= minYears && b.experienceRange.max <= maxYears;
      });
    }

    const statsMap = new Map<string, JobCityStats>();

    filtered.forEach((benchmark) => {
      const key = `${benchmark.jobTitle}-${benchmark.city}`;
      if (!statsMap.has(key)) {
        const stats = getSalaryStatsByCityAndJob(benchmark.jobTitle, benchmark.city);
        if (stats) {
          statsMap.set(key, stats);
        }
      }
    });

    setResults(Array.from(statsMap.values()));
  };

  return (
    <div className='space-y-8 max-w-7xl mx-auto p-4'>
      <section className='text-center space-y-6 py-12 rounded-2xl p-8'>
        <h1 className='text-4xl font-bold text-ink'>حقوق مشاغل در ایران را شفاف مقایسه کنید</h1>
        <p className='text-lg text-ink-muted max-w-2xl mx-auto'>
          با استفاده از داده‌های بازار کار ایران، حقوق را بر اساس شغل، شهر و سابقه کار مقایسه کنید.
        </p>

        <Card className='max-w-4xl mx-auto border border-border-subtle'>
          <CardContent className='p-8'>
            <div className='grid gap-6 md:grid-cols-2 lg:grid-cols-4'>
              <div className='space-y-2'>
                <label className='text-sm font-medium text-ink'>عنوان شغلی</label>
                <select
                  value={searchParams.jobTitle}
                  onChange={(e) => setSearchParams({ ...searchParams, jobTitle: e.target.value })}
                  className='min-h-11 w-full rounded-lg border border-border-subtle bg-surface-raised px-3 py-2 text-sm text-ink'
                >
                  <option value=''>انتخاب شغل...</option>
                  {POPULAR_JOBS.map((job) => (
                    <option key={job} value={job}>
                      {job}
                    </option>
                  ))}
                  {getAllJobTitles().filter((job) => !POPULAR_JOBS.includes(job)).map((job) => (
                    <option key={job} value={job}>
                      {job}
                    </option>
                  ))}
                </select>
              </div>

              <div className='space-y-2'>
                <label className='text-sm font-medium text-ink'>شهر</label>
                <select
                  value={searchParams.city}
                  onChange={(e) => setSearchParams({ ...searchParams, city: e.target.value })}
                  className='min-h-11 w-full rounded-lg border border-border-subtle bg-surface-raised px-3 py-2 text-sm text-ink'
                >
                  <option value=''>انتخاب شهر...</option>
                  {POPULAR_CITIES.map((city) => (
                    <option key={city} value={city}>
                      {city}
                    </option>
                  ))}
                  {getAllCities().filter((city) => !POPULAR_CITIES.includes(city)).map((city) => (
                    <option key={city} value={city}>
                      {city}
                    </option>
                  ))}
                </select>
              </div>

              <div className='space-y-2'>
                <label className='text-sm font-medium text-ink'>سابقه</label>
                <select
                  value={searchParams.experience}
                  onChange={(e) => setSearchParams({ ...searchParams, experience: e.target.value })}
                  className='min-h-11 w-full rounded-lg border border-border-subtle bg-surface-raised px-3 py-2 text-sm text-ink'
                >
                  <option value=''>انتخاب سابقه...</option>
                  {EXPERIENCE_LEVELS.map((level) => (
                    <option key={level.value} value={level.value}>
                      {level.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className='flex items-end'>
                <Button onClick={handleSearch} size='lg' className='w-full'>
                  جستجوی حقوق
                </Button>
              </div>
            </div>

            {results.length > 0 && (
              <div className='mt-8 p-4 bg-surface-raised rounded-lg'>
                <p className='text-sm text-ink-muted'>
                  {results.length} نتیجه یافت شد
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        <div className='flex flex-wrap justify-center gap-3'>
          {POPULAR_JOBS.map((job) => (
            <span
              key={job}
              className='cursor-pointer select-none transition-colors'
              onClick={() => setSearchParams({ ...searchParams, jobTitle: job })}
            >
              <Badge tone='neutral' className='hover:bg-brand/10'>
                {job}
              </Badge>
            </span>
          ))}
          {POPULAR_CITIES.map((city) => (
            <span
              key={city}
              className='cursor-pointer select-none transition-colors'
              onClick={() => setSearchParams({ ...searchParams, city })}
            >
              <Badge tone='neutral' className='hover:bg-brand/10'>
                {city}
              </Badge>
            </span>
          ))}
        </div>
      </section>

      {results.length > 0 && (
        <section className='space-y-6'>
          <h2 className='text-2xl font-semibold text-ink'>نتایج جستجو</h2>

          <div className='grid gap-6 md:grid-cols-2 lg:grid-cols-3'>
            {results.map((result, index) => (
              <Card
                key={index}
                className='cursor-pointer hover:shadow-lg transition-shadow border border-border-subtle'
                onClick={() => setSelectedBenchmark(result)}
              >
                <CardHeader className='pb-3'>
                  <CardTitle className='text-lg'>{result.jobTitle}</CardTitle>
                  <div className='flex items-center justify-between text-sm text-ink-muted'>
                    <span>{result.city}</span>
                    <span>{result.totalSamples} نمونه</span>
                  </div>
                </CardHeader>

                <CardContent className='space-y-4'>
                  <div className='text-center p-4 bg-surface-raised rounded-lg'>
                    <p className='text-xs text-ink-muted mb-1'>میانگین حقوق</p>
                    <p className='text-xl font-bold tabular-nums text-brand-strong'>
                      {moneyText(result.medianSalary, 'rial')}
                    </p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
      )}

      {selectedBenchmark && (
        <section className='space-y-6'>
          <Button
            variant='secondary'
            onClick={() => setSelectedBenchmark(null)}
            className='mb-6'
          >
            بازگشت به نتایج
          </Button>

          <Card>
            <CardHeader>
              <CardTitle className='text-2xl'>
                جزئیات حقوق: {selectedBenchmark.jobTitle} در {selectedBenchmark.city}
              </CardTitle>
            </CardHeader>

            <CardContent className='space-y-8'>
              <div className='text-center p-6 bg-surface-raised rounded-xl'>
                <p className='text-sm text-ink-muted mb-2'>میانگین حقوق</p>
                <p className='text-3xl font-bold tabular-nums text-brand-strong'>
                  {moneyText(selectedBenchmark.medianSalary, 'rial')}
                </p>
              </div>
            </CardContent>
          </Card>
        </section>
      )}
    </div>
  );
}
