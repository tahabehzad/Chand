import { useUiStore } from '@/state/ui-store';
import { UNIT_LABELS, type CurrencyUnit } from '@/lib/money';
import { cn } from '@/lib/cn';

const UNITS: CurrencyUnit[] = ['rial', 'toman'];

/**
 * A display preference, not a conversion. A Toman rendering is refused for a
 * Rial amount that is not divisible by 10 (`formatMoney`), so selecting Toman
 * here can never silently truncate a figure.
 */
export function UnitToggle() {
  const preferredUnit = useUiStore((state) => state.preferredUnit);
  const setPreferredUnit = useUiStore((state) => state.setPreferredUnit);

  return (
    <div
      role="group"
      aria-label="واحد نمایش مبالغ"
      className="inline-flex items-center gap-1 rounded-lg border border-border-subtle bg-surface-raised p-1"
    >
      {UNITS.map((unit) => (
        <button
          key={unit}
          type="button"
          onClick={() => setPreferredUnit(unit)}
          aria-pressed={preferredUnit === unit}
          className={cn(
            'min-h-8 rounded-md px-3 text-xs font-medium transition-colors',
            preferredUnit === unit ? 'bg-brand text-white' : 'text-ink-muted hover:text-ink',
          )}
        >
          {UNIT_LABELS[unit]}
        </button>
      ))}
    </div>
  );
}
