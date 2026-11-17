import { Icon } from '@/components/icon';

/**
 * The persistent honesty banner of the manager workspace.
 *
 * It states the four things a viewer must know before reading any number:
 * the data is synthetic, it is stored in PostgreSQL behind a real signed-in
 * manager, the evaluation weights are a provisional draft, and the statutory
 * costing comes from an engine that is READY_FOR_REVIEW — not an approved
 * legal authority.
 */
export function PrototypeNotice({ compact = false }: { compact?: boolean }) {
  return (
    <div
      role="note"
      className="flex items-start gap-3 rounded-xl border border-warning/30 bg-warning/10 px-4 py-3 text-sm text-warning"
    >
      <Icon name="alert" className="mt-1 shrink-0" />
      <div className="flex min-w-0 flex-col gap-1">
        <p className="font-semibold">ارزیابی نمونه — داده‌های ساختگی</p>
        {compact ? null : (
          <p className="text-xs leading-relaxed">
            جریان کامل روی سرور اجرا می‌شود: فرد ← دادهٔ عملکرد و شواهد ← امتیاز ← پیشنهاد ← تصمیم
            مدیر. داده‌ها در پایگاه‌داده و در محدودهٔ سازمانِ نشست ذخیره می‌شوند و تصمیم ثبت‌شده
            حذف یا بازنویسی نمی‌شود. وزن‌های مدل ارزیابی (۴۰/۳۰/۲۰/۱۰) پیش‌نویس و تأییدنشده‌اند؛
            مبالغ قانونی از موتور ۱۴۰۴ در وضعیت «آمادهٔ بازبینی» می‌آیند و قطعی یا مصوب نیستند.
          </p>
        )}
      </div>
    </div>
  );
}
