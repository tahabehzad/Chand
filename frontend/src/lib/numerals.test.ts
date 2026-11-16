import { describe, expect, it } from 'vitest';
import {
  normaliseNumericInput,
  parseIntegerInput,
  persianNumberLabel,
  toAsciiDigits,
  toPersianDigits,
} from './numerals';

describe('toPersianDigits (display layer)', () => {
  it('converts ASCII digits to U+06F0–U+06F9', () => {
    const persian = toPersianDigits('1404');
    expect(persian).toBe('\u06F1\u06F4\u06F0\u06F4');
    expect([...persian].every((c) => c.charCodeAt(0) >= 0x06f0 && c.charCodeAt(0) <= 0x06f9)).toBe(true);
  });

  it('leaves non-digits untouched', () => {
    expect(toPersianDigits('-٬ / :')).toBe('-٬ / :');
  });
});

describe('toAsciiDigits (machine layer)', () => {
  it('converts Persian digits', () => {
    expect(toAsciiDigits('۱۲۳۴۵۶۷۸۹۰')).toBe('1234567890');
  });

  it('converts Arabic-Indic digits', () => {
    expect(toAsciiDigits('٠١٢٣٤٥٦٧٨٩')).toBe('0123456789');
  });

  it('leaves ASCII digits unchanged', () => {
    expect(toAsciiDigits('2026')).toBe('2026');
  });
});

describe('normaliseNumericInput (input layer)', () => {
  it('folds mixed digit sets and Persian separators in one pass', () => {
    expect(normaliseNumericInput('۱۲۳٬۴٥٦٫۷۸')).toBe('123,456.78');
  });

  it('folds the Persian percent sign and removes the tatweel artefact', () => {
    expect(normaliseNumericInput('۷٪ـ')).toBe('7%');
  });
});

describe('parseIntegerInput', () => {
  it('accepts ASCII, Persian and Arabic-Indic input', () => {
    for (const raw of ['123', '۱۲۳', '١٢٣']) {
      expect(parseIntegerInput(raw)).toEqual({ ok: true, value: '123', negative: false });
    }
  });

  it('keeps a negative sign separate from the magnitude', () => {
    expect(parseIntegerInput('-۱۲۳')).toEqual({ ok: true, value: '123', negative: true });
  });

  it('rejects a fractional amount: Rial has no sub-unit', () => {
    const result = parseIntegerInput('۱۲۳٫۴');
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.reason).toBe('non-numeric');
  });

  it('rejects an empty or whitespace-only value', () => {
    expect(parseIntegerInput('   ')).toEqual({ ok: false, reason: 'empty' });
  });
});

describe('FE-02 Persian digit round-trip', () => {
  it('a displayed amount converts back to the exact ASCII integer', () => {
    const machine = '280000000';
    const displayed = persianNumberLabel(machine);
    expect(toAsciiDigits(displayed)).toBe(machine);
  });
});
