import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

/**
 * Minimal manager gate for the local preview.
 *
 * This is a **presentation-only** gate, not authentication: the backend has no
 * session or identity endpoint yet (`P0-T18`). It therefore accepts any name
 * and stores a local flag so the manager can reach the proposal screen. It must
 * never be described as a security control, and the notice on the card says so.
 */
export const MANAGER_SESSION_KEY = 'pish.manager.session';

export function ManagerLoginPage() {
  const navigate = useNavigate();
  const [name, setName] = useState('مدیر');

  function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = name.trim();
    if (!trimmed) return;
    window.sessionStorage.setItem(MANAGER_SESSION_KEY, trimmed);
    navigate('/proposal', { replace: true });
  }

  return (
    <main className="flex min-h-dvh items-center justify-center bg-surface px-4 py-10">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>ورود مدیر</CardTitle>
          <CardDescription>
            پیش‌حسابداری — پیشنهاد حقوق بر پایهٔ مهارت و سابقه
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form className="flex flex-col gap-4" onSubmit={submit}>
            <Input
              label="نام مدیر"
              value={name}
              onChange={(event) => setName(event.target.value)}
              autoComplete="username"
              required
            />
            <Button type="submit" size="lg">
              ورود
            </Button>
          </form>
          <p className="mt-4 text-xs leading-6 text-ink-muted">
            این ورود نمایشی است: سامانه هنوز شناسه و نشست واقعی ندارد، پس هیچ رمزی
            بررسی نمی‌شود و این صفحه کنترل امنیتی نیست.
          </p>
        </CardContent>
      </Card>
    </main>
  );
}

export default ManagerLoginPage;
