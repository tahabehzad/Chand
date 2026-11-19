import { PageHeader } from '@/app/page-header';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { UnitToggle } from '@/components/layout/unit-toggle';
import { Select } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Link } from 'react-router-dom';

const DENSITY_OPTIONS = [
  { value: 'comfortable', label: 'راحت' },
  { value: 'compact', label: 'چگال' },
] as const;

export default function SettingsPage() {

  return (
    <>
      <PageHeader
        eyebrow="مطابق با سلیقه شما"
        title="تنظیمات"
        description="تنظیمات نمایش و رفتار در نسخه نمایشی چند؟."
      />

      <Card>
        <CardHeader>
          <CardTitle>واحد نمایش مبالغ</CardTitle>
          <CardDescription>
            این انتخاب فقط نحوه نمایش مبالغ را تغییر می‌دهد؛ Amountها در پایگاه‌داده به‌صورت ریال
            ذخیره می‌شوند. نمایش تومان برای مبالغی که بر ۱۰ بخش‌پذیر نیستند، رد می‌شود.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-sm font-medium">واحد پول</p>
            <p className="mt-1 text-xs text-ink-muted">
              در همین نشست حفظ می‌شود؛ با بارگذاری دوباره صفحه به ریال برمی‌گردد.
            </p>
          </div>
          <UnitToggle />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>نمایش و چگالی</CardTitle>
          <CardDescription>
            چگالی تراکم displayed محتوای صفحات و کارت‌ها را تغییر می‌دهد.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-sm font-medium">چگالی نمایش</p>
            <p className="mt-1 text-xs text-ink-muted">فاصله‌های داخلی کارت‌ها و جداول</p>
          </div>
          <Select
            label="چگالی"
            value="comfortable"
            onChange={() => {}}
            hint="راحت برای خواندن بهتر، چگال برای نمایش بیشتری در صفحه"
          >
            {DENSITY_OPTIONS.map((d) => (
              <option key={d.value} value={d.value}>
                {d.label}
              </option>
            ))}
          </Select>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>زبان و ظاهر</CardTitle>
          <CardDescription>
            رابط این نسخه با تنظیمات ثابت زیر ارائه می‌شود.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <dl className="grid gap-5 text-sm sm:grid-cols-3">
            <div>
              <dt className="text-ink-muted">زبان و جهت</dt>
              <dd className="mt-1 font-medium">فارسی · راست‌به‌چپ</dd>
            </div>
            <div>
              <dt className="text-ink-muted">پوسته</dt>
              <dd className="mt-1 font-medium">روشن</dd>
            </div>
            <div>
              <dt className="text-ink-muted">قلم</dt>
              <dd className="mt-1 font-medium">وزیرمتن · میزبانی محلی</dd>
            </div>
          </dl>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>اعلان‌ها</CardTitle>
          <CardDescription>
            نحوه دریافت اعلان‌های سامانه در همین نشست.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <Checkbox
            label="اعلان محاسبه تکمیل‌شده"
            hint="هنگام تکمیل محاسبه حقوق، اعلان نمایش داده شود"
            defaultChecked
          />
          <Checkbox
            label="اعلان خطای سرویس"
            hint="هنگام قطع ارتباط با بک‌اند، خطا را نمایش دهد"
            defaultChecked
          />
        </CardContent>
      </Card>

      <p className="text-sm text-ink-muted">
        نسخه نمایشی ۰٫۱ · داده‌ها ساختگی هستند{' '}
        <Link className="font-medium text-brand underline underline-offset-4" to="/system">
          مشاهده وضعیت اتصال سرویس
        </Link>
      </p>
    </>
  );
}
