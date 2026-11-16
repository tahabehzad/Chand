import { PageHeader } from '@/app/page-header';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { UnitToggle } from '@/components/layout/unit-toggle';
import { Link } from 'react-router-dom';

export default function SettingsPage() {
  return (
    <>
      <PageHeader eyebrow="مطابق با سلیقه شما" title="تنظیمات" description="تنظیمات ساده نمایش در نسخه نمایشی پیش‌حسابداری." />
      <Card><CardHeader><CardTitle>نمایش مبالغ</CardTitle><CardDescription>این انتخاب فقط نحوه نمایش داده‌های نمونه را تغییر می‌دهد.</CardDescription></CardHeader><CardContent className="flex flex-wrap items-center justify-between gap-4"><div><p className="text-sm font-medium">واحد پول</p><p className="mt-1 text-xs text-ink-muted">در همین نشست حفظ می‌شود؛ با بارگذاری دوباره صفحه به ریال برمی‌گردد.</p></div><UnitToggle /></CardContent></Card>
      <Card><CardHeader><CardTitle>زبان و ظاهر</CardTitle><CardDescription>رابط این نسخه با تنظیمات ثابت زیر ارائه می‌شود.</CardDescription></CardHeader><CardContent><dl className="grid gap-5 text-sm sm:grid-cols-3"><div><dt className="text-ink-muted">زبان و جهت</dt><dd className="mt-1 font-medium">فارسی · راست‌به‌چپ</dd></div><div><dt className="text-ink-muted">پوسته</dt><dd className="mt-1 font-medium">روشن</dd></div><div><dt className="text-ink-muted">قلم</dt><dd className="mt-1 font-medium">وزیرمتن · میزبانی محلی</dd></div></dl></CardContent></Card>
      <p className="text-sm text-ink-muted">نسخه نمایشی ۰٫۱ · داده‌ها ساختگی هستند. <Link className="font-medium text-brand underline underline-offset-4" to="/system">مشاهده وضعیت اتصال سرویس</Link></p>
    </>
  );
}
