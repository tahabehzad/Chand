---
name: persian-rtl-engineering
description: Builds native-quality Persian interfaces with correct RTL layout, Vazirmatn typography, Persian numerals, Jalali (Shamsi) calendar conversion, and print-ready bidirectional Persian PDF generation.
---

# Persian RTL Engineering Skill

## Purpose
Deliver a Persian-first enterprise experience: a genuinely right-to-left layout, correct Jalali calendar semantics, unambiguous money/number rendering, and legally presentable Persian PDFs — all without breaking the left-to-right assumptions baked into most UI and PDF tooling.

## RTL Layout
1. Set `<html dir="rtl" lang="fa">` at the document root. Direction is a document-level fact; never invert it per component.
2. Use **CSS logical properties exclusively**: `margin-inline-start`, `padding-inline`, `inset-inline-start`, `border-inline-end`, `text-align: start/end`. Never `margin-left`, `left`, `right`, `text-align: left`.
3. In Tailwind, prefer `ms-*` / `me-*` / `ps-*` / `pe-*` / `start-*` / `end-*`. The `left-*` / `right-*` utilities are physical and are a bug in RTL. When a physical utility is unavoidable (e.g. a third-party component), scope it with the `rtl:` / `ltr:` variants.
4. **Mirror directional icons**: back arrows, timeline connectors, progress steps, and "next/previous" chevrons must flip in RTL. Apply `rtl:-scale-x-100` to the glyph, never swap the asset — swapping breaks icon caching and licensing provenance.
5. **Isolate foreign runs**: Latin identifiers, code, URLs, and file names inside Persian sentences must be wrapped in `<bdi>` or `dir="ltr"` with `unicode-bidi: isolate`. Otherwise the surrounding Persian reorders around them and the run appears transposed.
6. **Bidi punctuation**: parentheses, brackets, quotes, and the Persian comma mirror automatically under the Unicode Bidirectional Algorithm. Do not hand-swap characters — hand-swapping corrupts copy/paste and search.
7. Numbers are bidi class EN/AN and stay left-to-right inside RTL text. Never reverse digits manually.

## Persian Typography & Numerals
8. **Self-host Vazirmatn** (SIL Open Font License — permits commercial embedding and redistribution). Air-gapped intranet deployments must not depend on a CDN. Ship `.woff2`, set `font-display: swap`, and preconnect nothing external.
9. **Numeral policy — three distinct layers, never conflated**:
   - *Display*: convert ASCII digits to Persian digits (U+06F0–U+06F9) for amounts, dates, percentages, and counters.
   - *Input*: accept ASCII digits, Persian digits, and Arabic-Indic digits (U+0660–U+0669); normalize all of them to ASCII **before** parsing. Reject anything else with a Persian validation message.
   - *Machine*: always ASCII in JSON payloads, database columns, audit payloads, hashes, and CSV exports. Never hash a Persian-digit string — it must be byte-identical to the value in the database.
10. **Money rendering**: Rial amounts are integers — never display decimals. Use the Persian thousands separator `٬` (U+066C) and decimal `٫` (U+066B) for display only. Always state the unit explicitly (`ریال` or `تومان`; 1 Toman = 10 Rial). A bare number in a salary interface is a defect.
11. **Character normalization**: Persian requires `ی` (U+06CC) and `ک` (U+06A9) — never Arabic `ي` (U+064A) / `ك` (U+0643). Normalize on input and in the PDF pipeline.
12. **ZWNJ**: insert U+200C in compounds (`می‌شود`, `نمی‌کند`, `۲۲ آبان`). Never use a regular space to join a prefix to a suffix.
13. Line height must be increased for Persian (≈1.8–2.0) and `text-align: justify` avoided in narrow columns where Persian letter joining is visually fragile.

## Jalali (Shamsi) Calendar
14. **Store Gregorian UTC internally.** Convert to Jalali only at the presentation boundary. Never persist a Jalali string in a date column, and never sort by a Jalali-formatted string.
15. **Use a battle-tested converter** (`persiantools`, `jdatetime`, or the standard *jalaali* algorithm). Never hand-roll the conversion — off-by-one errors around Nowruz and Esfand are silent and legally damaging.
16. **Calendar structure**: Farvardin 1 = 2026-03-21 for year 1405. Months 1–6 have 31 days, months 7–11 have 30 days, month 12 has 29 days (30 in a Jalali leap year). The leap cycle repeats every 33 years.
17. **Timezone**: `Asia/Tehran`, a fixed UTC+03:30. Iran abolished daylight saving in October 1401 / 2022, so no DST branch is needed. Store instants in UTC, render in Tehran local time.
18. **Statutory anchoring**: when a rule depends on "the 1405 tax year", pin it to the rule set version (`rule_year_shamsi` + `effective_date`) — never to "today". A simulation must be reproducible in 2030 without re-deriving which year applied.
19. Render Jalali dates in the canonical Persian form: `۲۲ آبان ۱۴۰۵` (day, month name, year) with Persian digits.

## Persian PDF Generation
20. **Preferred pipeline**: HTML/CSS → PDF via WeasyPrint or headless Chromium, so RTL layout, Vazirmatn embedding, table pagination, and page-break control all come from the same CSS as the application. Fall back to ReportLab only when the WeasyPrint/Chromium toolchain is unavailable on the target host.
21. **Mandatory text shaping for any PDF text engine**: `arabic_reshaper` (presentation-form shaping) → `python-bidi` (visual reordering) → font rendering. Omitting either stage yields disconnected and/or reversed Persian text — this is the single most common Persian PDF defect.
22. **Embed fonts** (subset when possible) and set `lang="fa"` / `dir="rtl"` / `text-align: right` on the PDF root. Rely on the PDF viewer, never on the OS, for text direction.
23. **Persian pagination and metadata**: page numbers as `صفحه ۳ از ۱۲`, document dates in Jalali, and any Latin technical identifier in an isolated LTR span.
24. **Legal exhibit rule**: the PDF is a document that may be shown to a *Heyat-e Tashkhis*. It MUST render byte-identical values to the API response and carry the `rule_version`, `engine_version`, `calculation_hash`, and generation timestamp. A PDF is a rendering of a snapshot, never a second computation.
25. **Print stylesheet**: `@page` margins sized for A4, `thead { display: table-header-group }` for repeating table headers across pages, and `break-inside: avoid` on monetary rows so a figure is never orphaned from its label.

## Accessibility & Input Behavior
26. All interactive elements keyboard-reachable with a visible focus ring; every `aria-label` in Persian.
27. Numeric inputs use `inputMode="numeric"`, `dir="ltr"`, and `text-align: right` so digits do not visually jump while typing.
28. Tables with monetary columns align digits consistently (`font-variant-numeric: tabular-nums`) — Persian digits in a proportional font make columns ragged and error-prone.

## Verification Checklist
29. Test all four corners: RTL and LTR embedding, long Persian strings without breaking layout, empty/error states, and 4-, 5-, and 6-digit magnitudes.
30. Snapshot-test the PDF output, and visually diff after any font or PDF-toolchain change — a font swap silently changes glyph metrics and page counts.
31. Verify the Persian numerals in the UI round-trip back to the exact ASCII integers stored in the database.
