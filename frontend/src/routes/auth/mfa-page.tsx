import { Link } from 'react-router-dom';
import { PageHeader } from '@/app/page-header';
import { Alert } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Bdi } from '@/components/ui/bidi';

/**
 * Presentation only — `POST /auth/mfa/verify` is not implemented and the
 * mandatory MFA role set (DEC-004a) is only resolved in the register, not in
 * code. No verification is simulated.
 */
export default function MfaPage() {
  return (
    <div className="mx-auto flex w-full max-w-md flex-col gap-6 py-6">
      <PageHeader
        title="تأیید دو‌مرحله‌ای"
        description="کد یک‌بارمصرف برنامه احراز هویت خود را وارد کنید."
      />

      <Alert tone="info" title="این صفحه نمایشی است">
        <p>
          مسیر تأیید دو‌مرحله‌ای هنوز در بک‌اند وجود ندارد. هیچ کدی بررسی نمی‌شود و هیچ
          نشستی ایجاد نمی‌گردد.
        </p>
      </Alert>

      <Card>
        <CardHeader>
          <CardTitle>کد یک‌بارمصرف</CardTitle>
          <CardDescription>
            کد ۶ رقمی؛ ارقام فارسی، عربی و لاتین پذیرفته می‌شود و پیش از ارسال به شکل ماشینی
            (ASCII) تبدیل خواهد شد.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form noValidate onSubmit={(event) => event.preventDefault()} className="flex flex-col gap-4">
            <Input
              label="کد تأیید"
              dir="ltr"
              inputMode="numeric"
              autoComplete="one-time-code"
              maxLength={6}
              placeholder="۱۲۳۴۵۶"
              disabled
              hint="در این نسخه ورودی غیرفعال است."
            />
            <Button type="submit" size="lg" disabled>
              تأیید
            </Button>
          </form>
        </CardContent>
      </Card>

      <p className="text-xs text-ink-muted">
        <Link className="font-medium text-brand-strong underline underline-offset-4" to="/login">
          بازگشت به صفحه ورود
        </Link>{' '}
        — شناسه قرارداد مورد نیاز: <Bdi className="font-mono">auth.mfa.verify</Bdi>
      </p>
    </div>
  );
}
