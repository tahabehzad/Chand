import { describe, expect, it } from 'vitest';
import { formatMoney, formatMoneyPreferringToman, formatPercentFromRate } from './money';
import { normaliseNumericInput } from './numerals';

const THOUSANDS = '\u066C';
const DECIMAL = '\u066B';
const PERCENT = '\u066A';

function ok(result: ReturnType<typeof formatMoney>) {
  if (!result.ok) throw new Error(`expected success, received ${result.reason}`);
  return result.value;
}

describe('formatMoney — Rial', () => {
  it('always states the unit', () => {
    expect(ok(formatMoney('120000', 'rial')).text.endsWith(' ریال')).toBe(true);
  });

  it('groups with the Persian thousands separator U+066C and Persian digits', () => {
    const value = ok(formatMoney('987654321000'));
    expect(value.amount).toBe(`۹۸۷${THOUSANDS}۶۵۴${THOUSANDS}۳۲۱${THOUSANDS}۰۰۰`);
  });

  it('never renders a fractional Rial', () => {
    const value = ok(formatMoney('70000'));
    expect(value.text).not.toContain(DECIMAL);
    expect(value.text).not.toContain('.');
  });

  it('refuses a non-integer amount instead of rounding it', () => {
    const result = formatMoney('70000.5');
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.reason).toBe('not-an-integer');
  });

  it('accepts bigint and integer number inputs', () => {
    expect(ok(formatMoney(10n)).machineValue).toBe('10');
    expect(ok(formatMoney(10)).machineValue).toBe('10');
    expect(formatMoney(10.5).ok).toBe(false);
  });

  it('rejects unsafe number amounts but preserves exact bigint and string amounts', () => {
    expect(formatMoney(Number.MAX_SAFE_INTEGER + 1).ok).toBe(false);
    expect(formatMoney(Number.MIN_SAFE_INTEGER - 1).ok).toBe(false);
    expect(ok(formatMoney(Number.MAX_SAFE_INTEGER)).machineValue).toBe('9007199254740991');
    expect(ok(formatMoney(Number.MIN_SAFE_INTEGER)).machineValue).toBe('-9007199254740991');
    expect(ok(formatMoney('9007199254740993')).machineValue).toBe('9007199254740993');
    expect(ok(formatMoney(9007199254740993n)).machineValue).toBe('9007199254740993');
  });

  it('keeps the machine value ASCII and rejects Persian digits instead of guessing', () => {
    expect(formatMoney('۱۲۳۰۰۰').ok).toBe(false);
    // The input layer folds Persian digits before this function is reached.
    const folded = normaliseNumericInput('۱۲۳۰۰۰');
    expect(ok(formatMoney(folded)).machineValue).toBe('123000');
  });
});

describe('formatMoney — Toman', () => {
  it('divides exactly by 10 when the Rial amount is divisible', () => {
    const value = ok(formatMoney('1234560', 'toman'));
    expect(value.text).toBe(`۱۲۳${THOUSANDS}۴۵۶ تومان`);
  });

  it('refuses Toman for a Rial amount that is not divisible by 10', () => {
    const result = formatMoney('123456785', 'toman');
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.reason).toBe('not-divisible-by-ten');
  });

  it('falls back to Rial rather than truncating', () => {
    const preferred = formatMoneyPreferringToman('123456785');
    expect(preferred.unit).toBe('rial');
    expect(preferred.fallbackFromToman).toBe(true);
    expect(preferred.text).toContain('ریال');
  });

  it('shows Toman when the amount allows it', () => {
    expect(formatMoneyPreferringToman('1234560').unit).toBe('toman');
  });
});

describe('formatPercentFromRate', () => {
  it('renders one decimal place with U+066B and U+066A', () => {
    expect(formatPercentFromRate('0.07')).toBe(`۷${DECIMAL}۰${PERCENT}`);
  });

  it('accepts a value above one', () => {
    expect(formatPercentFromRate('1.5')).toBe(`۱۵۰${DECIMAL}۰${PERCENT}`);
  });

  it.each([
    ['0', '۰٫۰٪'],
    ['1', '۱۰۰٫۰٪'],
    ['0.7', '۷۰٫۰٪'],
    ['12', '۱۲۰۰٫۰٪'],
    ['-1.5', '−۱۵۰٫۰٪'],
    ['1.005', '۱۰۰٫۵٪'],
    ['0.0005', '۰٫۱٪'],
    ['0.9995', '۱۰۰٫۰٪'],
  ])('converts exact rate %s into percentage %s', (rate, expected) => {
    expect(formatPercentFromRate(rate)).toBe(expected);
  });

  it('rounds half up on the decimal digits, not on a float', () => {
    expect(formatPercentFromRate('0.2345')).toBe(`۲۳${DECIMAL}۵${PERCENT}`);
    expect(formatPercentFromRate('0.2344')).toBe(`۲۳${DECIMAL}۴${PERCENT}`);
  });

  it('rejects a non-numeric rate', () => {
    expect(formatPercentFromRate('seven')).toBeNull();
  });
});
