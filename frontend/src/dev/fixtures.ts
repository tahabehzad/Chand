/**
 * **SYNTHETIC DEVELOPMENT FIXTURES — NOT REAL DATA.**
 *
 * These values exist so the design system can be inspected at 360 px without a
 * backend. They are reachable only from the development-only preview route.
 *
 * Rules this file follows deliberately:
 *  - No real candidate salary, name, National ID, mobile or Sheba number.
 *  - Values are obviously synthetic and labelled as such on screen.
 *  - The hash is a literal placeholder string, never a hash of anything.
 *  - A fixture is **never** substituted for a failed real API call.
 */

import type { FigureProvenance } from '@/api/provenance';

export const SYNTHETIC_MONEY_SAMPLES = [
  { id: 'four-digits', rial: '70000', noteFa: 'مبلغ کوچک، بخش‌پذیر بر ۱۰' },
  { id: 'seven-digits', rial: '1234560', noteFa: 'مبلغ هفت‌رقمی، بخش‌پذیر بر ۱۰' },
  { id: 'odd-rial', rial: '123456785', noteFa: 'مبلغ فرد: نمایش تومان باید رد شود' },
  { id: 'zero', rial: '0', noteFa: 'صفر' },
  { id: 'large', rial: '987654321000', noteFa: 'مبلغ بزرگ، بدون گرد کردن' },
] as const;

export const SYNTHETIC_RATES = ['0.07', '0.23', '0.0001', '1.5'] as const;

export const SYNTHETIC_PROVENANCE: FigureProvenance = {
  rule_version: '1404.1',
  rule_set_status: 'DRAFT',
  is_verified: false,
  engine_version: 'synthetic-preview',
  calculation_hash: 'SYNTHETIC-NOT-A-HASH',
  generated_at: '2026-01-01T00:00:00+03:30',
};

/** A provenance that represents a clean, verified rule set — for contrast only. */
export const SYNTHETIC_VERIFIED_PROVENANCE: FigureProvenance = {
  ...SYNTHETIC_PROVENANCE,
  rule_set_status: 'VERIFIED',
  is_verified: true,
};
