import { useId, type ComponentProps } from 'react';
import { cn } from '@/lib/cn';

type InputProps = Omit<ComponentProps<'input'>, 'id'> & {
  label: string;
  hint?: string;
  error?: string;
};

/**
 * Every control carries a programmatic label (§8).
 *
 * Numeric entry uses `inputMode="numeric"`, `dir="ltr"` and end-aligned text so
 * digits do not visually jump while typing, while the field still behaves
 * correctly inside the RTL form (SPEC-FE-001 §7).
 */
export function Input({ label, hint, error, className, dir, ...props }: InputProps) {
  const id = useId();
  const describedBy = [hint ? `${id}-hint` : null, error ? `${id}-error` : null]
    .filter(Boolean)
    .join(' ');

  return (
    <div className="flex flex-col gap-2">
      <label htmlFor={id} className="text-sm font-medium text-ink">
        {label}
      </label>
      <input
        id={id}
        dir={dir}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy === '' ? undefined : describedBy}
        className={cn(
          'min-h-11 w-full rounded-xl border bg-surface-raised px-3 py-2 text-sm text-ink',
          'border-border-subtle focus-visible:border-brand focus-visible:ring-1 focus-visible:ring-brand',
          // Numeric fields are end-aligned, not right-aligned: `text-end`
          // follows the document direction logically.
          dir === 'ltr' && 'text-end tabular',
          error && 'border-danger',
          className,
        )}
        {...props}
      />
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
