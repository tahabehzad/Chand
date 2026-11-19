/**
 * Display helpers for the prototype screens.
 *
 * Money is formatted through `lib/money.ts` (exact integer Rial, mandatory unit
 * label, Persian digits). Scores and percentages are formatted from integer
 * basis points — no float is involved in producing a displayed figure.
 */

import { formatMoney } from '@/lib/money';
import { toPersianDigits } from '@/lib/numerals';

export function faDigits(value: string | number): string {
  return toPersianDigits(String(value));
}

export function rialText(digits: string): string {
  const result = formatMoney(digits, 'rial');
  return result.ok ? result.value.text : 'مبلغ نامعتبر';
}

/**
 * A difference rendered as a Persian word rather than a leading +/- sign.
 * A bare sign before a digit run is bidi-neutral and lands at the visual end
 * of an RTL line ("۳۰٬۰۰۰+"), which reads as the opposite of the intent.
 */
export function deltaText(digits: string): string {
  const negative = digits.startsWith('-');
  const magnitude = negative ? digits.slice(1) : digits;
  return `${negative ? 'کاهش' : 'افزایش'} ${rialText(magnitude)}`;
}

/**
 * Display helper: basis points rendered as one-decimal percent, ASCII digits.
 * Integer maths only; the caller converts to Persian digits for display.
 */
export function bpToPercentText(bp: number): string {
  const whole = Math.trunc(bp / 100);
  const tenth = Math.trunc((bp % 100) / 10);
  return `${whole}.${tenth}`;
}

export function percentText(basisPoints: number): string {
  return `${toPersianDigits(bpToPercentText(basisPoints))}\u066A`;
}

/** Gregorian ISO date, Persian digits. Jalali conversion waits on DEC-006. */
export function isoDateText(iso: string): string {
  return toPersianDigits(iso.slice(0, 10));
}
