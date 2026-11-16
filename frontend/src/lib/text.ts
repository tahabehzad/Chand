/**
 * Persian text normalisation — SPEC-FE-001 §3.3.
 *
 * Arabic `ي`/`ك` are folded to Persian `ی`/`ک` on input and in display
 * normalisation so downstream matching is stable. ZWNJ (U+200C) is always
 * preserved: `می‌شود` and `میشود` are different strings, and stripping the
 * joiner produces a visible gap that reads as a spelling error.
 */

const TATWEEL = /\u0640/g;
const ARABIC_YEH = /\u064A/g;
const ARABIC_KAF = /\u0643/g;
const BIDI_CONTROLS = /[\u200E\u200F\u202A-\u202E\u2066-\u2069]/g;

/** Fold Arabic letter forms and copy/paste artefacts without touching ZWNJ. */
export function normalisePersianText(input: string): string {
  return input
    .replace(ARABIC_YEH, '\u06CC')
    .replace(ARABIC_KAF, '\u06A9')
    .replace(TATWEEL, '')
    .replace(BIDI_CONTROLS, '');
}

/** True when the string contains a ZWNJ, used by the ZWNJ regression tests. */
export function hasZwnj(input: string): boolean {
  return input.includes('\u200C');
}

/**
 * Copy is stable only when the logical order is correct in the DOM, which is
 * why direction lives on the document root. This helper exists for the
 * clipboard-facing tests rather than for hand-swapping punctuation: bidi
 * punctuation mirrors automatically and must never be swapped by hand.
 */
export function logicalCopyText(input: string): string {
  return input.normalize('NFC');
}
