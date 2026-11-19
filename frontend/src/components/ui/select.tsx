import { useId, type ComponentProps } from 'react';
import { Icon } from '@/components/icon';
import { cn } from '@/lib/cn';

type SelectProps = Omit<ComponentProps<'select'>, 'id'> & {
  label: string;
  hint?: string;
  error?: string;
};

/**
 * Styled select consistent with `Input`. Uses logical properties so the
 * chevron sits at the start in RTL (SPEC-FE-001 §7).
 */
export function Select({ label, hint, error, className, ...props }: SelectProps) {
  const id = useId();
  const describedBy = [hint ? `${id}-hint` : null, error ? `${id}-error` : null]
    .filter(Boolean)
    .join(' ');

  return (
    <div className="flex flex-col gap-2">
      <label htmlFor={id} className="text-sm font-medium text-ink">
        {label}
      </label>
      <select
        id={id}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy === '' ? undefined : describedBy}
        className={cn(
          'min-h-11 w-full rounded-xl border bg-surface-raised px-3 py-2 text-sm text-ink',
          'border-border-subtle focus-visible:border-brand focus-visible:ring-1 focus-visible:ring-brand',
          error && 'border-danger',
          className,
        )}
        {...props}
      >
        {props.children}
      </select>
      <div className="pointer-events-none absolute inset-y-0 start-0 flex items-center pe-3">
        <Icon name="chevron-next" className="size-4 text-ink-muted" />
      </div>
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
  );
}
