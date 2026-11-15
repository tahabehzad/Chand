/**
 * Jalali (Shamsi) calendar policy — SPEC-FE-001 §5, WBS P3-T03.
 *
 * **Status: policy only. No conversion is implemented, and none is chosen.**
 *
 * DEC-006 (`docs/DECISIONS_REGISTER.md`) is OPEN — NON-BLOCKING and names the
 * converter selection (`L-1`: `persiantools`, with `jdatetime` in tests) as an
 * unresolved choice for the CTO. Those are Python libraries; the browser-side
 * choice is not recorded anywhere. Hand-rolling the algorithm is explicitly
 * forbidden (`SPEC-FE-001` §5.1) because an off-by-one at Nowruz or Esfand is
 * silent and legally damaging. So this module exposes a *port*, formats
 * Jalali parts that a converter supplies, and reports the missing converter
 * instead of inventing a conversion.
 *
 * Storage policy, which is decidable today and is implemented by callers:
 * Gregorian UTC everywhere; convert to Jalali only at the render boundary;
 * never persist or sort on a Jalali string; anchor statutory years to the
 * rule-set version, never to the clock.
 */

export type JalaliParts = {
  year: number;
  /** 1 = Farvardin … 12 = Esfand */
  month: number;
  /** 1-based day within the month. */
  day: number;
};

/** Saturday-first weekday order, index 0 = شنبه (SPEC-FE-001 §5.2). */
export const WEEKDAYS_FA = [
  'شنبه',
  'یکشنبه',
  'دوشنبه',
  'سه‌شنبه',
  'چهارشنبه',
  'پنج‌شنبه',
  'جمعه',
] as const;

export const JALALI_MONTHS_FA = [
  'فروردین',
  'اردیبهشت',
  'خرداد',
  'تیر',
  'مرداد',
  'شهریور',
  'مهر',
  'آبان',
  'آذر',
  'دی',
  'بهمن',
  'اسفند',
] as const;

/**
 * A converter supplied by the approved library once DEC-006 lands.
 * `toJalali` receives an ISO-8601 calendar date or a UTC instant.
 */
export type JalaliConverter = {
  id: string;
  toJalali(iso: string): JalaliParts;
};

let registeredConverter: JalaliConverter | null = null;

/** Wiring point for the approved converter. Deliberately no default. */
export function registerJalaliConverter(converter: JalaliConverter | null): void {
  registeredConverter = converter;
}

export function getJalaliConverter(): JalaliConverter | null {
  return registeredConverter;
}

export class JalaliConverterUnavailable extends Error {
  constructor() {
    super(
      'No Jalali converter is registered: DEC-006 (converter selection) is unresolved and hand-rolling is forbidden.',
    );
    this.name = 'JalaliConverterUnavailable';
  }
}

export type JalaliStyle = 'full' | 'short' | 'month-year';

/**
 * Format Jalali *parts* that a converter produced. Formatting never performs
 * a conversion, so a caller cannot accidentally re-derive a date here.
 */
export function formatJalaliParts(
  parts: JalaliParts,
  style: JalaliStyle,
  toPersianDigits: (value: string) => string,
): string {
  const monthName = JALALI_MONTHS_FA[parts.month - 1] ?? '';
  const year = toPersianDigits(String(parts.year));
  if (style === 'month-year') return `${monthName} ${year}`;
  if (style === 'short') {
    const month = toPersianDigits(String(parts.month).padStart(2, '0'));
    const day = toPersianDigits(String(parts.day).padStart(2, '0'));
    return `${year}/${month}/${day}`;
  }
  const day = toPersianDigits(String(parts.day));
  return `${day} ${monthName} ${year}`;
}

/**
 * Convert for display, returning an explicit failure when no converter exists.
 * A caller must render the failure — never a guessed date.
 */
export function toJalali(iso: string): { ok: true; parts: JalaliParts } | { ok: false; reason: 'no-converter' } {
  if (registeredConverter === null) return { ok: false, reason: 'no-converter' };
  return { ok: true, parts: registeredConverter.toJalali(iso) };
}
