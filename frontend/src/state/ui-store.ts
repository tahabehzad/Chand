import { create } from 'zustand';
import type { CurrencyUnit } from '@/lib/money';

/**
 * Lightweight UI state only (ADR-001 directive 3). Server data is owned by
 * TanStack Query; nothing here is a source of truth for a monetary figure.
 *
 * The currency unit is a *display* preference. It never changes a value: the
 * API supplies Rial, and a Toman rendering is refused unless the amount is
 * exactly divisible by 10 (`src/lib/money.ts`).
 */
type UiState = {
  preferredUnit: CurrencyUnit;
  setPreferredUnit: (unit: CurrencyUnit) => void;
  mobileNavOpen: boolean;
  setMobileNavOpen: (open: boolean) => void;
  /** Set when a 401 has been observed, so the shell can explain the redirect. */
  sessionExpired: boolean;
  markSessionExpired: () => void;
  clearSessionExpired: () => void;
};

export const useUiStore = create<UiState>((set) => ({
  preferredUnit: 'rial',
  setPreferredUnit: (unit) => set({ preferredUnit: unit }),
  mobileNavOpen: false,
  setMobileNavOpen: (open) => set({ mobileNavOpen: open }),
  sessionExpired: false,
  markSessionExpired: () => set({ sessionExpired: true }),
  clearSessionExpired: () => set({ sessionExpired: false }),
}));
