import type { ComponentProps } from 'react';
import { Icon } from '@/components/icon';
import { cn } from '@/lib/cn';

type Tone = 'info' | 'warning' | 'danger' | 'success';

const TONE_STYLES: Record<Tone, string> = {
  info: 'border-brand/30 bg-brand/5 text-ink',
  warning: 'border-warning/40 bg-warning/10 text-ink',
  danger: 'border-danger/40 bg-danger/10 text-ink',
  success: 'border-success/40 bg-success/10 text-ink',
};

const TONE_ICONS: Record<Tone, 'info' | 'alert' | 'check'> = {
  info: 'info',
  warning: 'alert',
  danger: 'alert',
  success: 'check',
};

type AlertProps = ComponentProps<'div'> & {
  tone?: Tone;
  title?: string;
};

/**
 * Colour is never the only signal (§8): every alert carries an icon and text
 * as well as its border colour. `role` is `alert` only for the danger tone.
 */
export function Alert({ tone = 'info', title, className, children, ...props }: AlertProps) {
  return (
    <div
      role={tone === 'danger' ? 'alert' : 'status'}
      className={cn(
        'flex items-start gap-3 rounded-lg border p-4 text-sm',
        TONE_STYLES[tone],
        className,
      )}
      {...props}
    >
      <Icon name={TONE_ICONS[tone]} className="mt-1 size-5" />
      <div className="flex flex-col gap-1">
        {title ? <p className="font-semibold">{title}</p> : null}
        {children ? <div className="text-ink-muted">{children}</div> : null}
      </div>
    </div>
  );
}
