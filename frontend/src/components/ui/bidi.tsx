import type { ReactNode } from 'react';

/**
 * Latin identifiers, code, URLs, e-mail addresses and file names inside a
 * Persian sentence must be isolated, otherwise the surrounding RTL text
 * reorders around the run and the run appears transposed (SPEC-FE-001 §2.5).
 */
export function Bdi({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <bdi className={className} style={{ unicodeBidi: 'isolate' }}>
      {children}
    </bdi>
  );
}

/** A visibly left-to-right technical run, e.g. an ISO date or a hash. */
export function LtrRun({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <span dir="ltr" className={className} style={{ unicodeBidi: 'isolate', display: 'inline-block' }}>
      {children}
    </span>
  );
}
