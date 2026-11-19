import { useId, type ComponentProps } from 'react';
import { cn } from '@/lib/cn';

type CheckboxProps = Omit<ComponentProps<'input'>, 'type'> & {
  label: string;
  hint?: string;
  error?: string;
};

/**
 * Styled checkbox consistent with the form control system. The checkmark
 * is mirrored in RTL by the icon registry (`chevron-next` is directional,
 * but the check mark itself is not).
 */
export function Checkbox({ label, hint, error, className, ...props }: CheckboxProps) {
  const id = useId();
  const describedBy = [hint ? `${id}-hint` : null, error ? `${id}-error` : null]
    .filter(Boolean)
    .join(' ');

  return (
    <div className={cn('flex items-start gap-3', className)}>
      <input
        id={id}
        type="checkbox"
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy === '' ? undefined : describedBy}
        className={cn(
          'h-4 w-4 shrink-0 rounded border border-border-subtle bg-surface-raised text-brand',
          'focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2',
          'checked:bg-brand checked:border-brand',
          error && 'border-danger',
          className,
        )}
        {...props}
      />
      <div className="flex flex-col gap-1 leading-none">
        <label htmlFor={id} className="text-sm font-medium text-ink cursor-pointer select-none">
          {label}
        </label>
        {hint ? (
          <p id={`${id}-hint`} className="text-xs text-ink-muted">
            {hint}
          </p>
        ) : null}
        {error ? (
          <p id={`${id}-error`} className="text-xs font-medium text-danger">
            {error}
          </p>
        ) : null}
      </div>
    </div>
  );
}
