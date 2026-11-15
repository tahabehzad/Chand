import { PageHeader } from '@/app/page-header';
import { Alert } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { useUiStore } from '@/state/ui-store';
import { useNavigate } from 'react-router-dom';

/**
 * Where a 401 lands. Session policy is server-side; detailed timeouts remain
 * undecided under ADR-006. This route only renders the client consequence of a 401
 * response and never assumes a session state of its own.
 */
export default function SessionExpiredPage() {
  const sessionExpired = useUiStore((state) => state.sessionExpired);
  const clearSessionExpired = useUiStore((state) => state.clearSessionExpired);
  const navigate = useNavigate();

  return (
    <div className="mx-auto flex w-full max-w-lg flex-col gap-6 py-6">
      <PageHeader title="نشست پایان یافت" description="برای ادامه، دوباره وارد شوید." />

      <Card>
        <CardContent className="flex flex-col gap-4">
          <Alert tone={sessionExpired ? 'warning' : 'info'} title={sessionExpired ? 'پاسخ ۴۰۱ از سرویس دریافت شد' : 'این صفحه فقط نمایشی است'}>
            <p>
              {sessionExpired
                ? 'پاسخ ۴۰۱ از سرویس دریافت شد. برای ورود دوباره به صفحه ورود بروید.'
                : 'هیچ پاسخ ۴۰۱ واقعی ثبت نشده است؛ این صفحه بدون نشست واقعی قابل آزمون نیست.'}
            </p>
          </Alert>
          <Button
            size="lg"
            onClick={() => {
              clearSessionExpired();
              navigate('/login');
            }}
          >
            رفتن به صفحه ورود
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
