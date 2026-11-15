import type { ReactNode } from 'react';
import { Icon } from '@/components/icon';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/cn';

/** Loading is announced politely and never traps focus. */
export function LoadingState({
  label = 'در حال بارگذاری…',
  className,
}: {
  label?: string;
  className?: string;
}) {
  return (
    <div
      role="status"
      aria-live="polite"
      className={cn('flex items-center justify-center gap-3 p-8 text-sm text-ink-muted', className)}
    >
      <Icon name="spinner" className="size-5 motion-safe:animate-spin" />
      <span>{label}</span>
    </div>
  );
}

/** A content-shaped skeleton so the layout does not jump when data arrives. */
export function LoadingSkeleton({ rows = 3, className }: { rows?: number; className?: string }) {
  return (
    <div role="status" aria-live="polite" aria-label="در حال بارگذاری…" className={cn('flex flex-col gap-3', className)}>
      {Array.from({ length: rows }, (_, index) => (
        <div
          key={index}
          className="h-16 w-full animate-pulse rounded-lg border border-border-subtle bg-surface motion-reduce:animate-none"
        />
      ))}
      <span className="sr-only">در حال بارگذاری…</span>
    </div>
  );
}

export function EmptyState({
  title,
  description,
  action,
  className,
}: {
  title: string;
  description: ReactNode;
  action?: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        'flex flex-col items-center gap-3 rounded-[var(--radius-card)] border border-dashed border-border-subtle bg-surface p-8 text-center',
        className,
      )}
    >
      <Icon name="empty" className="size-8 text-ink-muted" />
      <h3 className="text-base font-semibold text-ink">{title}</h3>
      <p className="max-w-prose text-sm text-ink-muted">{description}</p>
      {action}
    </div>
  );
}

/**
 * An error state is a *rendered failure*, never a silent fallback to synthetic
 * data. The correlation id is shown so a support request can be traced to a
 * server log line (`X-Request-Id`).
 */
export function ErrorState({
  title = 'دریافت اطلاعات ناموفق بود',
  description,
  correlationId,
  onRetry,
  retryLabel = 'تلاش دوباره',
  className,
}: {
  title?: string;
  description: ReactNode;
  correlationId?: string;
  onRetry?: () => void;
  retryLabel?: string;
  className?: string;
}) {
  return (
    <div
      role="alert"
      className={cn(
        'flex flex-col items-start gap-3 rounded-[var(--radius-card)] border border-danger/40 bg-danger/5 p-6',
        className,
      )}
    >
      <div className="flex items-center gap-2 text-danger">
        <Icon name="alert" className="size-5" />
        <h3 className="text-base font-semibold">{title}</h3>
      </div>
      <div className="text-sm text-ink-muted">{description}</div>
      {correlationId ? (
        <p className="text-xs text-ink-muted">
          شناسه پیگیری:{' '}
          {/* A Latin identifier inside Persian text is isolated (§2.5). */}
          <bdi dir="ltr" className="font-mono">
            {correlationId}
          </bdi>
        </p>
      ) : null}
      {onRetry ? (
        <Button variant="secondary" size="sm" onClick={onRetry}>
          {retryLabel}
        </Button>
      ) : null}
    </div>
  );
}
