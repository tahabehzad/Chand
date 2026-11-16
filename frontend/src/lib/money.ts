/**
 * Money formatting — SPEC-FE-001 §4.2, Holy Bible §6.5, skill rules 10–11.
 *
 * Hard rules implemented here:
 *  - Rial is the canonical unit and an *integer*: no fractional Rial is ever
 *    displayed, and rounding never happens in the display layer.
 *  - The unit label (`ریال` / `تومان`) is always rendered. A bare number in a
 *    salary interface is a defect.
 *  - Amounts are handled as exact digit strings or bigint. JavaScript `number`
 *    inputs are accepted only within the safe-integer range.
 *  - 1 Toman = 10 Rial. A Rial amount that is not divisible by 10 is legal and
 *    must not be truncated, so Toman rendering is refused for such a value.
 *
 * Input is a machine-layer value: ASCII digits only. A Persian-digit string is
 * rejected rather than guessed at, so the display layer can never disagree with
 * the bytes stored in the database (`numerals.ts` folds user input first).
 *
 * The backend is the authority: it supplies `rial` and `toman` strings
 * pre-computed (`formatting_boundary`). The helpers below exist for values the
 * frontend legitimately owns — counters, echoes of typed input, and a display
 * preference — and they never recompute an API figure.
 */

import { toPersianDigits } from './numerals';

export type CurrencyUnit = 'rial' | 'toman';

export const RIAL_PER_TOMAN = 10n;

export const UNIT_LABELS: Record<CurrencyUnit, string> = {
  rial: 'ریال',
  toman: 'تومان',
};

export type RialInput = string | bigint | number;

export type MoneyFormatFailure = 'not-an-integer' | 'not-divisible-by-ten';

export type MoneyText = {
  /** Persian-digit grouped amount, without the unit label. */
  amount: string;
  unit: CurrencyUnit;
  unitLabel: string;
  /** Amount and unit together, in logical RTL order. */
  text: string;
  /** ASCII machine form (`-120000`), suitable for `data-*` / `aria-label`. */
  machineValue: string;
};

export type MoneyResult =
  | { ok: true; value: MoneyText }
  | { ok: false; reason: MoneyFormatFailure; messageFa: string };

const MINUS = '-';
const GROUP_SEPARATOR = '\u066C'; // ٬ Persian thousands separator

const FAILURE_MESSAGES: Record<MoneyFormatFailure, string> = {
  'not-an-integer': 'مبلغ باید یک عدد صحیح دقیق باشد؛ ریال کوچک‌ترین واحد پول است.',
  'not-divisible-by-ten':
    'این مبلغ بر ۱۰ بخش‌پذیر نیست و نمایش تومان آن دقیق نخواهد بود.',
};

/** Normalise any accepted input to an ASCII signed digit string, or null. */
function toDigitString(input: RialInput): string | null {
  let raw: string;
  if (typeof input === 'bigint') {
    raw = input.toString();
  } else if (typeof input === 'number') {
    if (!Number.isSafeInteger(input)) return null;
    raw = BigInt(input).toString();
  } else {
    raw = input.trim();
  }
  return /^-?\d+$/.test(raw) ? raw : null;
}

function groupDigits(digits: string): string {
  let grouped = '';
  for (let index = 0; index < digits.length; index += 1) {
    const fromEnd = digits.length - index;
    grouped += digits[index] ?? '';
    if (fromEnd > 1 && (fromEnd - 1) % 3 === 0) {
      grouped += GROUP_SEPARATOR;
    }
  }
  return grouped;
}

function divideByTenExact(digits: string): string | null {
  if (!digits.endsWith('0')) return null;
  const cut = digits.slice(0, -1);
  return cut.length === 0 ? '0' : cut;
}

/**
 * Format a Rial-denominated integer for display.
 *
 * `unit: 'toman'` fails closed for a value that is not divisible by 10 rather
 * than truncating it: the caller decides whether to fall back to Rial.
 */
export function formatMoney(input: RialInput, unit: CurrencyUnit = 'rial'): MoneyResult {
  const digits = toDigitString(input);
  if (digits === null) {
    return {
      ok: false,
      reason: 'not-an-integer',
      messageFa: FAILURE_MESSAGES['not-an-integer'],
    };
  }

  const negative = digits.startsWith(MINUS);
  const magnitude = negative ? digits.slice(1) : digits;

  let displayDigits = magnitude;
  if (unit === 'toman') {
    const tornDown = divideByTenExact(magnitude);
    if (tornDown === null) {
      return {
        ok: false,
        reason: 'not-divisible-by-ten',
        messageFa: FAILURE_MESSAGES['not-divisible-by-ten'],
      };
    }
    displayDigits = tornDown;
  }

  const amount = toPersianDigits(groupDigits(displayDigits));
  const signedAmount = negative ? `\u2212${amount}` : amount;
  const unitLabel = UNIT_LABELS[unit];

  return {
    ok: true,
    value: {
      amount: signedAmount,
      unit,
      unitLabel,
      text: `${signedAmount} ${unitLabel}`,
      machineValue: digits,
    },
  };
}

/**
 * Render the unit a caller must use. A non-divisible-by-10 Rial amount is legal
 * and is shown in Rial, with the reason surfaced instead of a silent change of unit.
 */
export function formatMoneyPreferringToman(input: RialInput): {
  text: string;
  unit: CurrencyUnit;
  fallbackFromToman: boolean;
} {
  const toman = formatMoney(input, 'toman');
  if (toman.ok) {
    return { text: toman.value.text, unit: 'toman', fallbackFromToman: false };
  }
  const rial = formatMoney(input, 'rial');
  if (!rial.ok) {
    return { text: rial.messageFa, unit: 'rial', fallbackFromToman: false };
  }
  return { text: rial.value.text, unit: 'rial', fallbackFromToman: true };
}

/**
 * Percentage display — SPEC-FE-001 §4.3.
 *
 * Rates arrive from the API as strings with explicit scale (`"0.07"`), so they
 * can never be coerced to a binary float. One decimal place, Persian decimal
 * separator U+066B and Persian percent sign U+066A.
 */
export function formatPercentFromRate(rate: string): string | null {
  const match = /^(-?)(\d+)(?:\.(\d+))?$/.exec(rate.trim());
  if (!match) return null;
  const [, sign = '', whole = '0', fraction = ''] = match;

  // Shift the decimal point two places: rate × 100, exactly, in base 10.
  const combined = `${whole}${fraction}`;
  const pointIndex = whole.length + 2;
  const padded = combined.padEnd(pointIndex, '0');
  const rawWhole = padded.slice(0, pointIndex);
  const rawFraction = padded.slice(pointIndex);

  // One decimal place, half-up, computed on the decimal digits (never a float).
  let digits = rawWhole + (rawFraction.charAt(0) || '0');
  const nextDigit = rawFraction.charAt(1);
  if (nextDigit !== '' && nextDigit >= '5') {
    digits = (BigInt(digits) + 1n).toString();
  }

  const scale = digits.length === 1 ? '0' : digits.slice(0, -1);
  const decimals = digits.slice(-1);
  const trimmedWhole = scale.replace(/^0+(?=\d)/, '');

  return `${sign === '' ? '' : '\u2212'}${toPersianDigits(trimmedWhole)}\u066B${toPersianDigits(decimals)}\u066A`;
}
