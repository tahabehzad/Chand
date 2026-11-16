import { useState } from 'react';
import { Link } from 'react-router-dom';
import { PageHeader } from '@/app/page-header';
import { Alert } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Bdi } from '@/components/ui/bidi';
import { CONTRACTS } from '@/api/contracts';

/**
 * **Presentation only.** The session contract (`POST /auth/login`, `P0-T18`)
 * does not exist, the token format is decided by ADR-006 but not implemented,
 * and P3-T06's own blocker (`DEC-004`) must not be resolved by assumption.
 *
 * Therefore this screen stores **no** token, sets **no** cookie, implements
 * **no** session semantics and sends **no** request. The submit control is
 * disabled and explains why, so a stakeholder cannot read a rendered form as a
 * working sign-in.
 */
export default function SignInPage() {
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const contract = CONTRACTS.sessionSignIn;
  const disabled = true;

  return (
    <div className="mx-auto flex w-full max-w-md flex-col gap-6 py-6">
      <PageHeader
        title="ورود به سامانه"
        description="دسترسی به این سامانه فقط برای کاربران سازمانی مجاز است."
      />

      <Alert tone="info" title="این صفحه نمایشی است و هنوز کار نمی‌کند">
        <p>
          قرارداد ورود (<Bdi className="font-mono">{contract.method} {contract.path}</Bdi>) هنوز
          پیاده‌سازی نشده است. در این نسخه هیچ توکنی ذخیره نمی‌شود، هیچ کوکی نشستی تنظیم
          نمی‌شود و هیچ درخواست ورودی ارسال نمی‌گردد.
        </p>
      </Alert>

      <Card>
        <CardHeader>
          <CardTitle>شناسه سازمانی</CardTitle>
          <CardDescription>شناسه کاربری و گذرواژه خود را وارد کنید.</CardDescription>
        </CardHeader>
        <CardContent>
          <form
            className="flex flex-col gap-4"
            noValidate
            onSubmit={(event) => event.preventDefault()}
            aria-describedby="sign-in-disabled-note"
          >
            <Input
              label="شناسه کاربری"
              type="email"
              dir="ltr"
              autoComplete="username"
              value={identifier}
              onChange={(event) => setIdentifier(event.target.value)}
              hint="نشانی ایمیل سازمانی"
              disabled={disabled}
            />
            <Input
              label="گذرواژه"
              type="password"
              dir="ltr"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              disabled={disabled}
            />
            <p id="sign-in-disabled-note" className="text-xs text-ink-muted">
              ورود تا تحویل قرارداد نشست غیرفعال است.
            </p>
            <Button type="submit" size="lg" disabled={disabled} aria-describedby="sign-in-disabled-note">
              ورود
            </Button>
          </form>
        </CardContent>
        <CardFooter className="justify-between text-xs text-ink-muted">
          <span>تأیید دو‌مرحله‌ای پس از ورود لازم است.</span>
          <Link className="font-medium text-brand-strong underline underline-offset-4" to="/login/mfa">
            صفحه تأیید دو‌مرحله‌ای
          </Link>
        </CardFooter>
      </Card>
    </div>
  );
}
