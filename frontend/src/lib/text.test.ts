import { describe, expect, it } from 'vitest';
import { hasZwnj, normalisePersianText } from './text';

describe('normalisePersianText', () => {
  it('folds Arabic yeh to Persian yeh', () => {
    expect(normalisePersianText('ي')).toBe('ی');
  });

  it('folds Arabic kaf to Persian kaf', () => {
    expect(normalisePersianText('ك')).toBe('ک');
  });

  it('removes the tatweel artefact', () => {
    expect(normalisePersianText('می‌کـــن') === 'می‌کن').toBe(true);
  });

  it('preserves ZWNJ — it changes word meaning', () => {
    const input = 'می\u200Cشود';
    expect(normalisePersianText(input)).toBe(input);
    expect(hasZwnj(normalisePersianText(input))).toBe(true);
  });

  it('strips bidi control characters from pasted text', () => {
    expect(normalisePersianText('\u200Fحقوق\u200E')).toBe('حقوق');
  });

  it('does not use a regular space in place of ZWNJ', () => {
    expect(normalisePersianText('حقوق‌بگیر')).not.toContain(' ');
  });
});
