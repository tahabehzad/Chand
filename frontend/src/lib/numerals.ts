/**
 * The three-layer numeral policy — SPEC-FE-001 §4.1, Holy Bible §6.4.
 *
 * | Layer   | Form                                                    |
 * | Display | Persian digits U+06F0–U+06F9                              |
 * | Input   | ASCII + Persian + Arabic-Indic, normalised to ASCII first |
 * | Machine | ASCII only — JSON, hashes, `data-*`, `aria-label` values  |
 *
 * A Persian-digit string must never reach the machine layer: the hash must be
 * byte-identical to the value stored in the database.
 */

const PERSIAN_ZERO = 0x06f0;
const ARABIC_INDIC_ZERO = 0x0660;

const PERSIAN_DIGITS = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'] as const;

/** Display layer: ASCII digit characters become Persian digits. */
export function toPersianDigits(input: string): string {
  return input.replace(/[0-9]/g, (digit) => PERSIAN_DIGITS[Number(digit)] ?? digit);
}

/** Machine layer: any supported digit set becomes ASCII digits. */
export function toAsciiDigits(input: string): string {
  return input.replace(/[\u0660-\u0669\u06F0-\u06F9]/g, (digit) => {
    const code = digit.charCodeAt(0);
    const base = code >= PERSIAN_ZERO ? PERSIAN_ZERO : ARABIC_INDIC_ZERO;
    return String(code - base);
  });
}

/**
 * Input layer: fold Arabic-Indic and Persian digits, separator variants and
 * the tatweel artefact to their ASCII equivalents before any parsing.
 * ZWNJ (U+200C) is *not* touched here — it changes word meaning.
 */
export function normaliseNumericInput(input: string): string {
  return toAsciiDigits(input)
    .replace(/\u066B/g, '.') // Arabic decimal separator
    .replace(/\u066C/g, ',') // Arabic thousands separator
    .replace(/\u066A/g, '%') // Arabic percent sign
    .replace(/\u0640/g, '') // tatweel
    .replace(/\u200F|\u200E/g, ''); // RLM / LRM bidi marks
}

export type IntegerParseResult =
  | { ok: true; value: string; negative: boolean }
  | { ok: false; reason: 'empty' | 'non-numeric' };

const INTEGER_INPUT = /^-?\d+$/;

/**
 * Parse a user-entered integer for the machine layer.
 *
 * Amounts are integers in Rial: there is no fractional Rial (SPEC-FE-001 §4.2),
 * so a decimal separator is rejected rather than rounded. The result is a
 * digit *string*, never a JavaScript `number`, so a large amount is never
 * silently coerced to a binary float.
 */
export function parseIntegerInput(raw: string): IntegerParseResult {
  const folded = normaliseNumericInput(raw).replace(/\s/g, '');
  if (folded.length === 0) {
    return { ok: false, reason: 'empty' };
  }
  if (!INTEGER_INPUT.test(folded)) {
    return { ok: false, reason: 'non-numeric' };
  }
  const negative = folded.startsWith('-');
  return {
    ok: true,
    value: negative ? folded.slice(1) : folded,
    negative,
  };
}

/** Persian digits grouped for screen readers so a digit run is not misread. */
export function persianNumberLabel(asciiDigits: string): string {
  return toPersianDigits(asciiDigits);
}
