import { Link } from 'react-router-dom';
import { PageHeader } from '@/app/page-header';
import { EmptyState } from '@/components/ui/states';
import { Button } from '@/components/ui/button';
import { LtrRun } from '@/components/ui/bidi';
import { useLocation } from 'react-router-dom';

export default function NotFoundPage() {
  const location = useLocation();

  return (
    <>
      <PageHeader title="صفحه یافت نشد" description="نشانی وارد‌شده در این سامانه وجود ندارد." />
      <EmptyState
        title="مسیر نامعتبر"
        description={
          <>
            مسیر <LtrRun className="font-mono">{location.pathname}</LtrRun> شناسایی نشد. از منوی
            کنار صفحه یکی از بخش‌های موجود را انتخاب کنید.
          </>
        }
        action={
          <Button asChild variant="secondary">
            <Link to="/">بازگشت به نمای کلی</Link>
          </Button>
        }
      />
    </>
  );
}
