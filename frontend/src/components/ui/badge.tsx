import type { ReactNode } from 'react';
import { cn } from '@/lib/cn';

type Tone = 'neutral' | 'info' | 'warning' | 'danger' | 'success';

const TONES: Record<Tone, string> = {
  neutral: 'border-border-subtle bg-surface text-ink-muted',
  info: 'border-brand/30 bg-brand/5 text-brand-strong',
  warning: 'border-warning/40 bg-warning/10 text-warning',
  danger: 'border-danger/40 bg-danger/10 text-danger',
  success: 'border-success/40 bg-success/10 text-success',
};

export function Badge({
  children,
  tone = 'neutral',
  className,
}: {
  children: ReactNode;
  tone?: Tone;
  className?: string;
}) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-medium',
        TONES[tone],
        className,
      )}
    >
      {children}
    </span>
  );
}
