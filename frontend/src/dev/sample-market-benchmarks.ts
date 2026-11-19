// DEVELOPMENT SAMPLE ONLY — fabricated salary rows. Not imported by the application.
// Kept outside the product path so no screen can present a made-up figure as market data.

// Iranian salary benchmark data for salary discovery page
// This is SAMPLE data and should be replaced with real data when available

export interface SalaryBenchmark {
  id: string;
  jobTitle: string;
  city: string;
  cityCoefficient: number; // 1.0 = baseline (Tehran)
  experienceRange: {
    min: number; // years
    max: number; // years
  };
  salaryRange: {
    p25: number; // 25th percentile (minimum)
    p50: number; // 50th percentile (median)
    p75: number; // 75th percentile (maximum)
  };
  currencyUnit: 'rial' | 'toman';
  updatedAt: string;
  sampleSize: number;
}

export interface JobCityStats {
  jobTitle: string;
  city: string;
  totalSamples: number;
  avgSalary: number;
  medianSalary: number;
  minSalary: number;
  maxSalary: number;
  salaryTrend?: 'increasing' | 'decreasing' | 'stable';
}

// Sample salary data for 12 Iranian jobs across major cities
export const SALARY_BENCHMARKS: SalaryBenchmark[] = [
  // Tech jobs
  {
    id: 'developer-frontend-tehran',
    jobTitle: 'توسعه‌دهنده فرانت‌اند',
    city: 'تهران',
    cityCoefficient: 1.0,
    experienceRange: { min: 0, max: 1 },
    salaryRange: { p25: 18000000, p50: 28000000, p75: 42000000 },
    currencyUnit: 'rial',
    updatedAt: '2026-11-15',
    sampleSize: 145,
  },
  {
    id: 'developer-frontend-isfahan',
    jobTitle: 'توسعه‌دهنده فرانت‌اند',
    city: 'اصفهان',
    cityCoefficient: 0.85,
    experienceRange: { min: 0, max: 1 },
    salaryRange: { p25: 15300000, p50: 23800000, p75: 35700000 },
    currencyUnit: 'rial',
    updatedAt: '2026-11-15',
    sampleSize: 89,
  },
  {
    id: 'developer-backend-tehran',
    jobTitle: 'توسعه‌دهنده بک‌اند',
    city: 'تهران',
    cityCoefficient: 1.0,
    experienceRange: { min: 1, max: 3 },
    salaryRange: { p25: 25000000, p50: 38000000, p75: 56000000 },
    currencyUnit: 'rial',
    updatedAt: '2026-11-15',
    sampleSize: 203,
  },
  {
    id: 'developer-fullstack-tehran',
    jobTitle: 'توسعه‌دهنده فول‌استک',
    city: 'تهران',
    cityCoefficient: 1.0,
    experienceRange: { min: 3, max: 5 },
    salaryRange: { p25: 45000000, p50: 65000000, p75: 90000000 },
    currencyUnit: 'rial',
    updatedAt: '2026-11-15',
    sampleSize: 167,
  },

  // Business jobs
  {
    id: 'accountant-tehran',
    jobTitle: 'حسابدار',
    city: 'تهران',
    cityCoefficient: 1.0,
    experienceRange: { min: 1, max: 3 },
    salaryRange: { p25: 20000000, p50: 32000000, p75: 48000000 },
    currencyUnit: 'rial',
    updatedAt: '2026-11-15',
    sampleSize: 312,
  },
  {
    id: 'accountant-isfahan',
    jobTitle: 'حسابدار',
    city: 'اصفهان',
    cityCoefficient: 0.87,
    experienceRange: { min: 1, max: 3 },
    salaryRange: { p25: 16740000, p50: 26880000, p75: 40320000 },
    currencyUnit: 'rial',
    updatedAt: '2026-11-15',
    sampleSize: 134,
  },
  {
    id: 'manager-sales-tehran',
    jobTitle: 'مدیر فروش',
    city: 'تهران',
    cityCoefficient: 1.0,
    experienceRange: { min: 5, max: 10 },
    salaryRange: { p25: 55000000, p50: 85000000, p75: 120000000 },
    currencyUnit: 'rial',
    updatedAt: '2026-11-15',
    sampleSize: 98,
  },

  // Service jobs
  {
    id: 'nurse-tehran',
    jobTitle: 'پرستار',
    city: 'تهران',
    cityCoefficient: 1.0,
    experienceRange: { min: 0, max: 2 },
    salaryRange: { p25: 12000000, p50: 18000000, p75: 25000000 },
    currencyUnit: 'rial',
    updatedAt: '2026-11-15',
    sampleSize: 256,
  },
  {
    id: 'teacher-isfahan',
    jobTitle: 'معلم',
    city: 'اصفهان',
    cityCoefficient: 0.88,
    experienceRange: { min: 0, max: 5 },
    salaryRange: { p25: 10800000, p50: 16200000, p75: 22500000 },
    currencyUnit: 'rial',
    updatedAt: '2026-11-15',
    sampleSize: 189,
  },

  // Technical jobs
  {
    id: 'mechanical-engineer-tehran',
    jobTitle: 'مهندس مکانیک',
    city: 'تهران',
    cityCoefficient: 1.0,
    experienceRange: { min: 1, max: 4 },
    salaryRange: { p25: 22000000, p50: 35000000, p75: 50000000 },
    currencyUnit: 'rial',
    updatedAt: '2026-11-15',
    sampleSize: 167,
  },
  {
    id: 'electrician-karaj',
    jobTitle: 'برق‌کار',
    city: 'کرج',
    cityCoefficient: 0.92,
    experienceRange: { min: 0, max: 3 },
    salaryRange: { p25: 14000000, p50: 21000000, p75: 29000000 },
    currencyUnit: 'rial',
    updatedAt: '2026-11-15',
    sampleSize: 203,
  },

  // Sales and service
  {
    id: 'sales-representative-isfahan',
    jobTitle: 'نمایندۀ فروش',
    city: 'اصفهان',
    cityCoefficient: 0.89,
    experienceRange: { min: 0, max: 2 },
    salaryRange: { p25: 13000000, p50: 19500000, p75: 26800000 },
    currencyUnit: 'rial',
    updatedAt: '2026-11-15',
    sampleSize: 167,
  },
  {
    id: 'driver-tehran',
    jobTitle: 'راننده',
    city: 'تهران',
    cityCoefficient: 1.0,
    experienceRange: { min: 0, max: 2 },
    salaryRange: { p25: 8000000, p50: 12000000, p75: 16000000 },
    currencyUnit: 'rial',
    updatedAt: '2026-11-15',
    sampleSize: 412,
  },

  // Specialized roles
  {
    id: 'hr-manager-tehran',
    jobTitle: 'مدیر منابع انسانی',
    city: 'تهران',
    cityCoefficient: 1.0,
    experienceRange: { min: 3, max: 7 },
    salaryRange: { p25: 40000000, p50: 62000000, p75: 88000000 },
    currencyUnit: 'rial',
    updatedAt: '2026-11-15',
    sampleSize: 145,
  },
  {
    id: 'quality-engineer-karaj',
    jobTitle: 'مهندس کیفیت',
    city: 'کرج',
    cityCoefficient: 0.91,
    experienceRange: { min: 1, max: 4 },
    salaryRange: { p25: 24000000, p50: 35000000, p75: 48000000 },
    currencyUnit: 'rial',
    updatedAt: '2026-11-15',
    sampleSize: 123,
  },
];

// Helper functions for salary calculations
export function getSalaryForExperience(baseBenchmark: SalaryBenchmark, years: number): Partial<SalaryBenchmark> {
  const ratio = Math.min(Math.max((years - baseBenchmark.experienceRange.min) / (baseBenchmark.experienceRange.max - baseBenchmark.experienceRange.min), 0), 1);
  const p25 = baseBenchmark.salaryRange.p25 + (baseBenchmark.salaryRange.p75 - baseBenchmark.salaryRange.p25) * ratio;
  const p50 = baseBenchmark.salaryRange.p50 + (baseBenchmark.salaryRange.p75 - baseBenchmark.salaryRange.p50) * ratio;
  const p75 = baseBenchmark.salaryRange.p75 + (baseBenchmark.salaryRange.p75 - baseBenchmark.salaryRange.p25) * ratio;

  return {
    ...baseBenchmark,
    salaryRange: { p25, p50, p75 },
  };
}

export function getAllCities(): string[] {
  return Array.from(new Set(SALARY_BENCHMARKS.map(b => b.city)));
}

export function getAllJobTitles(): string[] {
  return Array.from(new Set(SALARY_BENCHMARKS.map(b => b.jobTitle)));
}

export function getBenchmarksByJob(jobTitle: string): SalaryBenchmark[] {
  return SALARY_BENCHMARKS.filter(b => b.jobTitle === jobTitle);
}

export function getBenchmarksByCity(city: string): SalaryBenchmark[] {
  return SALARY_BENCHMARKS.filter(b => b.city === city);
}

export function getSalaryStatsByCityAndJob(jobTitle: string, city: string): JobCityStats | null {
  const benchmarks = SALARY_BENCHMARKS.filter(b => b.jobTitle === jobTitle && b.city === city);
  if (benchmarks.length === 0) return null;

  const allP25 = benchmarks.flatMap(b => [
    b.salaryRange.p25 * b.cityCoefficient,
    b.salaryRange.p50 * b.cityCoefficient,
    b.salaryRange.p75 * b.cityCoefficient,
  ]);

  allP25.sort((a, b) => a - b);

  const medianIndex = Math.floor(allP25.length / 2);
  const median = allP25[medianIndex];

  return {
    jobTitle,
    city,
    totalSamples: benchmarks.reduce((sum, b) => sum + b.sampleSize, 0),
    avgSalary: allP25.reduce((sum, val) => sum + val, 0) / allP25.length,
    medianSalary: median ?? 0,
    minSalary: allP25[0] ?? 0,
    maxSalary: allP25[allP25.length - 1] ?? 0,
    salaryTrend: 'stable', // Would need historical data for this
  };
}