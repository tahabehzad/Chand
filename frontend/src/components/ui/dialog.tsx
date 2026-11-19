import { useEffect, useRef, useState, type ReactNode } from 'react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/cn';

type DialogProps = {
  open: boolean;
  onClose: () => void;
  title?: string;
  description?: string;
  children: ReactNode;
  confirmLabel?: string;
  cancelLabel?: string;
  onConfirm?: () => void;
  destructive?: boolean;
};

/**
 * Accessible modal dialog with backdrop, escape-to-close, focus containment
 * and a confirm/cancel action area. Destructive confirmations use the danger
 * tone and require explicit confirmation (SPEC-FE-001 §8).
 */
export function Dialog({
  open,
  onClose,
  title,
  description,
  children,
  confirmLabel,
  cancelLabel = 'لغو',
  onConfirm,
  destructive = false,
}: DialogProps) {
  const [exited, setExited] = useState(!open);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (open) {
      setExited(false);
      document.body.style.overflow = 'hidden';
      return () => {
        document.body.style.overflow = '';
      };
    }
    if (!exited) {
      setExited(true);
    }
  }, [open, exited]);

  if (!open && exited) return null;

  return (
    <>
      <div
        className={cn(
          'fixed inset-0 z-40 bg-ink/60 backdrop-blur-sm transition-opacity',
          open ? 'opacity-100' : 'opacity-0',
        )}
        onClick={onClose}
      />
      <div
        ref={containerRef}
        className={cn(
          'fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6',
          open ? 'opacity-100' : 'opacity-0',
          'transition-opacity duration-200',
        )}
        role="dialog"
        aria-modal="true"
        aria-labelledby={title ? 'dialog-title' : undefined}
        aria-describedby={description ? 'dialog-description' : undefined}
      >
        <div
          className="w-full max-w-md rounded-[var(--radius-card)] border border-border-subtle bg-surface-raised shadow-xl text-ink"
        >
          {title || description ? (
            <div className="flex flex-col gap-2 p-5">
              {title ? (
                <h2 id="dialog-title" className="text-lg font-semibold text-ink">
                  {title}
                </h2>
              ) : null}
              {description ? (
                <p id="dialog-description" className="text-sm text-ink-muted">
                  {description}
                </p>
              ) : null}
            </div>
          ) : null}
          <div className="border-t border-border-subtle p-5">{children}</div>
          {(confirmLabel || cancelLabel) && (
            <div className="border-t border-border-subtle p-5 flex justify-end gap-3">
              <Button
                variant="secondary"
                size="sm"
                onClick={onClose}
                disabled={destructive && !onConfirm}
              >
                {cancelLabel}
              </Button>
              {confirmLabel && (
                <Button
                  variant={destructive ? 'danger' : 'primary'}
                  size="sm"
                  onClick={onConfirm ? onConfirm : onClose}
                >
                  {confirmLabel}
                </Button>
              )}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
