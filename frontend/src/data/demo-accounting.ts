/** Synthetic UI fixtures only. No candidate data, statutory rules or API results. */
export const DEMO_PERIOD = 'آبان ۱۴۰۵';
export const DEMO_NOTICE = 'تمام مبالغ و تراکنش‌ها ساختگی و صرفاً برای نمایش رابط هستند.';

export const demoSummary = [
  { id: 'income', title: 'کل درآمد', rial: '480000000', detail: 'دریافت‌های دوره نمونه', icon: 'income' },
  { id: 'expense', title: 'کل هزینه‌ها', rial: '185000000', detail: 'پرداخت‌های دوره نمونه', icon: 'expense' },
  { id: 'balance', title: 'مانده فعلی', rial: '295000000', detail: 'مانده ابتدای دوره: صفر ریال', icon: 'wallet' },
] as const;

// Predefined chart geometry is illustrative; it performs no financial calculation.
export const demoTrend = [
  { month: 'خرداد', income: '260000000', expense: '140000000', incomeHeight: 52, expenseHeight: 28 },
  { month: 'تیر', income: '320000000', expense: '180000000', incomeHeight: 64, expenseHeight: 36 },
  { month: 'مرداد', income: '290000000', expense: '160000000', incomeHeight: 58, expenseHeight: 32 },
  { month: 'شهریور', income: '410000000', expense: '220000000', incomeHeight: 82, expenseHeight: 44 },
  { month: 'مهر', income: '360000000', expense: '200000000', incomeHeight: 72, expenseHeight: 40 },
  { month: 'آبان', income: '480000000', expense: '185000000', incomeHeight: 96, expenseHeight: 37 },
] as const;

export const demoTransactions = [
  { id: 'demo-001', title: 'دریافت پروژه طراحی', category: 'خدمات', kind: 'income', rial: '300000000', date: '۲۴ آبان ۱۴۰۵' },
  { id: 'demo-002', title: 'خرید تجهیزات دفتر', category: 'تجهیزات', kind: 'expense', rial: '95000000', date: '۲۳ آبان ۱۴۰۵' },
  { id: 'demo-003', title: 'دریافت خدمات پشتیبانی', category: 'خدمات', kind: 'income', rial: '180000000', date: '۲۱ آبان ۱۴۰۵' },
  { id: 'demo-004', title: 'اجاره فضای کار', category: 'دفتر کار', kind: 'expense', rial: '70000000', date: '۲۰ آبان ۱۴۰۵' },
  { id: 'demo-005', title: 'اشتراک ابزارهای کاری', category: 'اشتراک', kind: 'expense', rial: '20000000', date: '۱۸ آبان ۱۴۰۵' },
] as const;
