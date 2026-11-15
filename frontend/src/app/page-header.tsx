import type { ReactNode } from 'react';

/**
 * One `h1` per page, no skipped heading levels (`SPEC-FE-001` §8).
 * `actions` sit at the logical end of the header row.
 */
export function PageHeader({
  title,
  description,
  actions,
  eyebrow,
}: {
  title: string;
  description?: ReactNode;
  actions?: ReactNode;
  eyebrow?: string;
}) {
  return (
    <header className="flex flex-wrap items-end justify-between gap-4">
      <div className="flex min-w-0 flex-col gap-1">
        {eyebrow ? (
          <p className="text-xs font-medium tracking-wide text-ink-muted">{eyebrow}</p>
        ) : null}
        <h1 className="text-2xl font-semibold text-ink">{title}</h1>
        {description ? <p className="max-w-prose text-sm text-ink-muted">{description}</p> : null}
      </div>
      {actions ? <div className="flex items-center gap-3">{actions}</div> : null}
    </header>
  );
}
