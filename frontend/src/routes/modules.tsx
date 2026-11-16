import { Link } from 'react-router-dom';
import { ModulePendingPage } from './module-pending-page';
import { CONTRACTS } from '@/api/contracts';
import { Icon } from '@/components/icon';

export function CtcPage() {
  return (
    <ModulePendingPage
      title="هزینه کل کارفرما"
      description="تفکیک هزینه کارفرما، بیمه سهم کارفرما و تعهدات آینده."
      contract={CONTRACTS.preHireCtc}
      frontendTask="P3-T08"
      planned={['تفکیک هزینه به قلم‌های قابل بازبینی', 'نمودار سهم هر مؤلفه']}
      note={
        <p className="text-sm">
          <span className="font-medium">ارقام این بخش هم‌اکنون محاسبه می‌شوند.</span> هزینه
          کل کارفرما و بهای تمام‌شده سالانه در پاسخ قرارداد محاسبه حقوق موجود است؛{' '}
          <Link
            to="/simulation"
            className="inline-flex items-center gap-1 font-medium text-brand underline"
          >
            شبیه‌سازی حقوق
            <Icon name="chevron-next" className="size-4" />
          </Link>
          {' '}را باز کنید.
        </p>
      }
    />
  );
}

export function TerminationPage() {
  return (
    <ModulePendingPage
      title="تسویه و پایان خدمت"
      description="سنوات، ذخیره مرخصی و نمایش حالت ماده ۱۱."
      contract={CONTRACTS.terminationLiability}
      frontendTask="P3-T08"
      planned={['ریز اقلام تسویه', 'نمایش صریح حالت آزمایشی ماده ۱۱']}
      note={
        <p className="text-sm">
          <span className="font-medium">تعهد پایان خدمت هم‌اکنون محاسبه می‌شود.</span> تعهد
          آزمایشی ماده ۱۱، سنوات خروج و خرید مرخصی در پاسخ قرارداد محاسبه حقوق موجود
          است؛{' '}
          <Link
            to="/simulation"
            className="inline-flex items-center gap-1 font-medium text-brand underline"
          >
            شبیه‌سازی حقوق
            <Icon name="chevron-next" className="size-4" />
          </Link>
          {' '}را باز کنید.
        </p>
      }
    />
  );
}

export function DocumentsPage() {
  return (
    <ModulePendingPage
      title="اسناد و اصالت‌سنجی"
      description="بارگذاری سند، وضعیت بررسی، نشانه‌های ناهنجاری و صف بازبینی انسانی."
      contract={CONTRACTS.documentUpload}
      frontendTask="P3-T09"
      planned={[
        'بارگذاری سند و پیگیری وضعیت',
        'نمایش ناهنجاری به‌عنوان نشانه، نه حکم تقلب',
        'ارجاع به بازبینی انسانی',
      ]}
    />
  );
}

export function BenchmarksPage() {
  return (
    <ModulePendingPage
      title="بازار و حقوق متعارف"
      description="بازه P10–P90 با برچسب‌های فارسی و نمایش نسبت به میانه."
      contract={CONTRACTS.benchmarkBand}
      frontendTask="P3-T10"
      planned={['نمودار بازه با محورهای فارسی', 'نمایش نسبت به میانه و نفوذ در بازه']}
    />
  );
}

export function RuleSetsPage() {
  return (
    <ModulePendingPage
      title="نسخه‌های قوانین"
      description="نسخه، سال قانونی و وضعیت تأیید مجموعه قواعد به‌صورت سه فیلد جداگانه."
      contract={CONTRACTS.statutoryRuleSets}
      frontendTask="P3-T05"
      planned={[
        'نمایش جداگانه نسخه، سال و وضعیت تأیید',
        'نمایش صریح اینکه ۱۴۰۵ غیرفعال است',
      ]}
    />
  );
}

export function AuditPage() {
  return (
    <ModulePendingPage
      title="دفتر حسابرسی"
      description="رویدادهای ثبت‌شده، بازیگر هر رویداد و صحت زنجیره هش."
      contract={CONTRACTS.auditLog}
      frontendTask="P3-T05"
      planned={['فهرست فقط‌خواندنی رویدادها', 'نمایش نتیجه بررسی زنجیره']}
    />
  );
}
