import { Icon } from '@/components/icon';

/**
 * Persistent disclosure of the statutory baseline.
 *
 * 1404 is the **verified historical** baseline. 1405 is transcribed, unverified
 * and inactive. Neither may be described as newly verified current law, and the
 * two facts must not be merged into one label (see `src/api/provenance.ts`).
 */
export function StatutoryBaselineNotice({ compact = false }: { compact?: boolean }) {
  return (
    <p className="flex items-start gap-2 text-xs text-ink-muted">
      <Icon name="info" className="mt-0.5 size-4" />
      <span>
        مبنای قانونی این نسخه، مجموعه قواعد سال <bdi>۱۴۰۴</bdi> است که یک مبنای تاریخی
        تأییدشده محسوب می‌شود. مجموعه قواعد سال <bdi>۱۴۰۵</bdi> رونویسی‌شده، تأییدنشده و
        غیرفعال است و در هیچ محاسبه‌ای به کار نمی‌رود.
        {compact ? null : (
          <>
            {' '}هیچ مبلغی در این رابط بدون برچسب واحد و بدون ارجاع به نسخه قواعد نمایش داده
            نمی‌شود.
          </>
        )}
      </span>
    </p>
  );
}
