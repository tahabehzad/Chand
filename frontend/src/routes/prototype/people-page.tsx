import { useCallback, useEffect, useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { PageHeader } from '@/app/page-header';
import { Icon } from '@/components/icon';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { EmptyState, ErrorState, LoadingSkeleton } from '@/components/ui/states';
import { createPerson, isPrototypeError, listPeople } from '@/prototype/api';
import type { Person } from '@/prototype/types';
import { PrototypeNotice } from './prototype-notice';
import { faDigits, isoDateText } from './format';

export default function PrototypePeoplePage() {
  const [people, setPeople] = useState<Person[]>([]);
  const [name, setName] = useState('');
  const [role, setRole] = useState('');
  const [startDate, setStartDate] = useState('2024-03-20');
  const [error, setError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async (): Promise<void> => {
    try {
      setError(null);
      setPeople(await listPeople());
    } catch (caught) {
      setError(isPrototypeError(caught) ? caught.message : 'دریافت فهرست کارکنان ناموفق بود.');
    } finally {
      setLoaded(true);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  async function onSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setBusy(true);
    setFormError(null);
    try {
      await createPerson({ name, role, startDate });
      setName('');
      setRole('');
      await load();
    } catch (caught) {
      setFormError(
        isPrototypeError(caught) ? caught.message : 'ثبت کارمند ناموفق بود.',
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <PageHeader
        eyebrow="گام ۱ از ۴ · کارکنان"
        title="کارکنان تحت ارزیابی"
        description="هر کارمند یک شناسهٔ داخلی، نام نمایشی، عنوان شغلی و تاریخ شروع دارد. کارمند کاربر سامانه نیست."
      />

      <PrototypeNotice compact />

      <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)]">
        <Card>
          <CardHeader>
            <CardTitle>ثبت کارمند تازه</CardTitle>
            <CardDescription>
              داده‌های شناسایی حساس (کد ملی، موبایل، شبا) در این سامانه پذیرفته نمی‌شود.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form className="flex flex-col gap-4" onSubmit={(event) => void onSubmit(event)}>
              <Input
                label="نام نمایشی"
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="مثلاً کارمند نمونهٔ ۳"
                maxLength={120}
                required
              />
              <Input
                label="عنوان شغلی"
                value={role}
                onChange={(event) => setRole(event.target.value)}
                placeholder="مثلاً فروش"
                maxLength={60}
                required
              />
              <Input
                label="تاریخ شروع (میلادی)"
                value={startDate}
                onChange={(event) => setStartDate(event.target.value)}
                hint="قالب YYYY-MM-DD؛ تبدیل شمسی پس از تصمیم DEC-006 اضافه می‌شود."
                dir="ltr"
                maxLength={10}
                required
              />
              {formError ? (
                <p
                  role="alert"
                  className="rounded-lg border border-danger/40 bg-danger/5 px-3 py-2 text-sm text-danger"
                >
                  {formError}
                </p>
              ) : null}
              <Button type="submit" disabled={busy}>
                {busy ? 'در حال ثبت…' : 'ثبت کارمند'}
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>فهرست کارکنان</CardTitle>
            <CardDescription>
              برای ورود دادهٔ عملکرد، شواهد و محاسبهٔ امتیاز، یک نفر را انتخاب کنید.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {error ? (
              <ErrorState description={error} onRetry={() => void load()} />
            ) : !loaded ? (
              <LoadingSkeleton rows={3} />
            ) : people.length === 0 ? (
              <EmptyState
                title="هنوز کسی ثبت نشده"
                description="از فرم کنار یک کارمند بسازید. داده‌ها روی سرور و در سازمانِ نشست شما ذخیره می‌شوند."
              />
            ) : (
              <ul className="flex flex-col gap-3">
                {people.map((person) => (
                  <li key={person.id}>
                    <Link
                      to={`/prototype/people/${person.id}`}
                      className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-border-subtle bg-surface px-3 py-3 text-sm hover:border-brand/30"
                    >
                      <span className="flex flex-col gap-0.5">
                        <span className="font-medium text-ink">{person.name}</span>
                        <span className="text-xs text-ink-muted">
                          {person.role} · شروع {isoDateText(person.startDate)}
                        </span>
                      </span>
                      <span className="flex items-center gap-2">
                        <Badge tone="info">فعال</Badge>
                        <span className="text-xs text-ink-muted">
                          شناسهٔ {faDigits(person.id.slice(0, 8))}
                        </span>
                        <Icon name="chevron-next" />
                      </span>
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>
    </>
  );
}
