import { Link } from 'react-router-dom';
import { PageHeader } from '@/app/page-header';
import { Icon } from '@/components/icon';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { DemoMoney } from '@/components/dashboard/demo-money';
import { IncomeExpenseChart } from '@/components/dashboard/income-expense-chart';
import { TransactionsTable } from '@/components/dashboard/transactions-table';
import { DEMO_NOTICE, DEMO_PERIOD, demoSummary } from '@/data/demo-accounting';

export default function OverviewPage() {
  return (
    <>
      <PageHeader eyebrow='یک نگاه، تصویر روشن‌تر' title='داشبورد مالی' description='نمایی ساده از درآمد، هزینه و مانده شما در محیط نمونه.' actions={<span className='flex items-center gap-2 rounded-lg border border-border-subtle bg-white px-4 py-2 text-sm'><Icon name='calendar' />{DEMO_PERIOD}</span>} />
      <div className='flex items-start gap-3 rounded-xl border border-brand/15 bg-brand/5 px-4 py-3 text-sm text-brand-strong'><Icon name='info' className='mt-1 shrink-0' /><p><span className='font-semibold'>نسخه نمایشی ۰٫۱</span><span className='mx-2'>·</span>{DEMO_NOTICE}</p></div>
      <section aria-label='خلاصه مالی نمونه' className='grid gap-4 md:grid-cols-3'>
        {demoSummary.map((item) => (
          <Card key={item.id} className={item.id === 'balance' ? 'border-brand/25 bg-brand/5' : ''}>
            <CardContent>
              <div className='mb-5 flex items-center justify-between gap-2'><h2 className='text-sm font-medium text-ink-muted'>{item.title}</h2><span className='summary-icon'><Icon name={item.icon} /></span></div>
              <p className='text-xl font-semibold sm:text-2xl'><DemoMoney rial={item.rial} /></p>
              <p className='mt-3 text-xs text-ink-muted'>{item.detail}</p>
            </CardContent>
          </Card>
        ))}
      </section>
      <section aria-label='روند مالی نمونه' className='grid items-start gap-5 xl:grid-cols-[minmax(0,2.4fr)_minmax(0,1fr)]'>
        <Card><CardHeader className='border-0'><CardTitle>درآمد و هزینه</CardTitle><CardDescription>مقایسه شش ماه نمونه · خرداد تا آبان ۱۴۰۵</CardDescription></CardHeader><CardContent className='pt-0'><IncomeExpenseChart /></CardContent></Card>
        <Card><CardHeader className='border-0'><p className='text-xs text-brand'>محیط آزمایشی</p><CardTitle className='mt-3'>شروعی ساده و شفاف</CardTitle><CardDescription>اطلاعات این صفحه فقط برای آشنایی با رابط نمایش داده می‌شوند.</CardDescription></CardHeader><CardContent className='flex flex-col gap-4 pt-0'><p className='text-sm text-ink-muted'>واحد نمایش را در تنظیمات تغییر دهید و نتیجه را در کارت‌ها، نمودار و جدول ببینید.</p><Link to='/settings' className='flex items-center justify-between rounded-lg border border-border-subtle bg-surface px-3 py-2.5 text-sm font-medium text-brand'>تنظیمات نمایش<Icon name='chevron-next' /></Link><p className='border-t border-border-subtle pt-4 text-xs text-ink-muted'>ثبت، ویرایش و پرداخت واقعی در این نسخه ارائه نمی‌شود.</p></CardContent></Card>
      </section>
      <Card className='min-w-0 overflow-hidden'><CardHeader className='flex-row flex-wrap items-center justify-between gap-3 border-0'><div><CardTitle>تراکنش‌های اخیر</CardTitle><CardDescription>آخرین دریافت‌ها و پرداخت‌های ساختگی</CardDescription></div><Link to='/transactions' className='flex items-center gap-2 text-sm font-medium text-brand'>مشاهده تراکنش‌ها<Icon name='chevron-next' /></Link></CardHeader><TransactionsTable /></Card>
    </>
  );
}
