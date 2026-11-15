import { afterEach, describe, expect, it } from 'vitest';
import {
  formatJalaliParts,
  getJalaliConverter,
  JALALI_MONTHS_FA,
  registerJalaliConverter,
  toJalali,
  WEEKDAYS_FA,
} from './calendar';
import { toPersianDigits } from './numerals';

afterEach(() => {
  registerJalaliConverter(null);
});

describe('calendar names', () => {
  it('lists the twelve Jalali months in order', () => {
    expect(JALALI_MONTHS_FA).toHaveLength(12);
    expect(JALALI_MONTHS_FA[0]).toBe('فروردین');
    expect(JALALI_MONTHS_FA[11]).toBe('اسفند');
  });

  it('starts the week on Saturday, not Sunday or Monday', () => {
    expect(WEEKDAYS_FA[0]).toBe('شنبه');
    expect(WEEKDAYS_FA).toHaveLength(7);
  });
});

describe('formatJalaliParts', () => {
  const parts = { year: 1405, month: 8, day: 23 };

  it('renders the canonical full form', () => {
    expect(formatJalaliParts(parts, 'full', toPersianDigits)).toBe('۲۳ آبان ۱۴۰۵');
  });

  it('renders the short form with Persian digits', () => {
    expect(formatJalaliParts(parts, 'short', toPersianDigits)).toBe('۱۴۰۵/۰۸/۲۳');
  });

  it('renders month and year', () => {
    expect(formatJalaliParts(parts, 'month-year', toPersianDigits)).toBe('آبان ۱۴۰۵');
  });
});

describe('the converter port (DEC-006)', () => {
  it('refuses to convert when no converter is registered', () => {
    expect(getJalaliConverter()).toBeNull();
    expect(toJalali('2026-11-14')).toEqual({ ok: false, reason: 'no-converter' });
  });

  it('uses a registered converter as-is and never re-derives a date', () => {
    registerJalaliConverter({ id: 'test-double', toJalali: () => ({ year: 1405, month: 8, day: 23 }) });
    expect(toJalali('2026-11-14')).toEqual({
      ok: true,
      parts: { year: 1405, month: 8, day: 23 },
    });
  });
});
