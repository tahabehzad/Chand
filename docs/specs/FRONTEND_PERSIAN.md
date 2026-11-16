# Specification: Persian Frontend, RTL, Jalali Calendar & Persian PDF

- **Document ID:** `SPEC-FE-001`
- **Status:** Draft — proposed implementation specification
- **Author:** Documentation Engineering (Frontend workstream)
- **Date:** 2026-11-14 (23 Aban 1405 SH)
- **Related:** [`docs/EXECUTION_PLAN.md`](../EXECUTION_PLAN.md) §8 · [`docs/adr/ADR-001-frontend-architecture-react-vite-spa.md`](../adr/ADR-001-frontend-architecture-react-vite-spa.md) · `.agents/skills/persian-rtl-engineering/SKILL.md`

> **Why this document exists.** ADR-001 directive 2 specifies "Shadcn/UI (Radix UI primitives) styled with Tailwind CSS **and RTL support for Persian typography (Vazirmatn font)**". That is one line. It is not a localisation strategy. Persian is not a left-to-right language with a translated string table: it is a right-to-left, cursive, context-sensitive script with its own calendar, its own numeral sets, its own currency conventions, its own bidi interaction rules, and a PDF pipeline that silently corrupts text unless a shaping stage is present. This document specifies the whole of it.

---

## 1. Scope

### 1.1 In scope

Document root direction and layout · typography and font delivery · numeral and currency presentation · Jalali calendar and date handling · Persian text normalisation · accessibility · responsive behaviour · Persian PDF generation (client- and server-side) · browser-rendering correctness.

### 1.2 Out of scope

Backend statutory calculations (see `SPEC-STAT-001`) · candidate-facing portals (excluded by ADR-004) · English-language product surfaces beyond the machine-readable API contract.

---

## 2. Document and Layout Direction

### 2.1 Root attributes

```html
<html lang="fa" dir="rtl">
```

Set once, at the document root, in `index.html`. Direction is a document-level fact; it is never inverted per component.

### 2.2 Logical properties only

| Never use | Use instead |
| :--- | :--- |
| `margin-left` / `margin-right` | `margin-inline-start` / `margin-inline-end` |
| `padding-left` / `padding-right` | `padding-inline-start` / `padding-inline-end` |
| `left` / `right` (positioning) | `inset-inline-start` / `inset-inline-end` |
| `border-left` / `border-right` | `border-inline-start` / `border-inline-end` |
| `text-align: left` / `right` | `text-align: start` / `end` |
| `float: left` / `right` | `float: inline-start` / `inline-end` |

### 2.3 Tailwind CSS

- Prefer the logical utilities: `ms-*`, `me-*`, `ps-*`, `pe-*`, `start-*`, `end-*`, `text-start`, `text-end`, `border-s`, `border-e`.
- The physical utilities `left-*`, `right-*`, `ml-*`, `mr-*`, `pl-*`, `pr-*`, `text-left`, `text-right` are **physical** and are a defect in an RTL document.
- Where a third-party component forces a physical utility, scope it with the `rtl:` / `ltr:` variants rather than removing it globally.
- **Lint gate:** a CI rule rejects `left-`, `right-`, `ml-`, `mr-`, `pl-`, `pr-`, `text-left`, `text-right` in application source (Shadcn/UI vendor code is exempt but must not be edited in place — override at the call site).

### 2.4 Directional icon mirroring

Icons that encode direction — back/forward arrows, chevrons, timeline connectors, progress steps, "next"/"previous" — must be mirrored in RTL:

```tsx
<ChevronRight className="rtl:-scale-x-100" />
```

The **asset is not swapped**. Swapping breaks icon caching, breaks any future RTL-neutral asset pipeline, and breaks the licensing provenance of the icon set.

Icons that do **not** encode direction (a clock, a person, a document, a currency symbol) are not mirrored. Persian convention also commonly mirrors the *clock face* in digital media, but this is a per-asset decision recorded in the icon inventory.

### 2.5 Bidirectional isolation

Latin identifiers, code, URLs, file names and email addresses inside Persian sentences must be isolated:

```tsx
<bdi>SalarySimulator</bdi>
<span dir="ltr">2026-11-14</span>
```

Without isolation, the surrounding Persian reorders around the run and the Latin text appears transposed. `unicode-bidi: isolate` is the CSS equivalent.

**Never hand-swap bidi punctuation.** Parentheses, brackets and quotes mirror automatically under the Unicode Bidirectional Algorithm. Hand-swapping corrupts copy/paste and full-text search.

### 2.6 Numbers inside RTL text

Digits are bidi class `EN`/`AN` and stay left-to-right inside an RTL paragraph. **Never reverse digits manually.** A numeric run such as `۲۸۰,۰۰۰,۰۰۰ ریال` renders correctly without intervention.

---

## 3. Typography

### 3.1 Font: Vazirmatn

| Property | Requirement |
| :--- | :--- |
| Family | **Vazirmatn** |
| Licence | SIL Open Font License 1.1 — permits commercial embedding, bundling and redistribution with the software |
| Delivery | **Self-hosted**, subset, `.woff2` — no CDN, no Google Fonts |
| Weights | 400 (regular), 500 (medium), 600 (semibold), 700 (bold). Persian text needs fewer weights than Latin; 700 is used sparingly |
| `font-display` | `swap` |
| Preload | preload the 400 and 600 `.woff2` files (`<link rel="preload" as="font" type="font/woff2" crossorigin>`) |
| Fallback stack | `Vazirmatn, "IRANSans", Tahoma, "Segoe UI", system-ui, sans-serif` — Tahoma is the pragmatic Windows fallback for Persian |

**Self-hosting is mandatory**, not an optimisation: ADR-001 names air-gapped Iranian enterprise intranets as a driving constraint, and a CDN font reference would fail silently in exactly those deployments.

### 3.2 Metrics and line height

| Property | Value | Rationale |
| :--- | :--- | :--- |
| Base font size | 16 px | — |
| Line height | **1.85 – 2.0** | Persian descenders and diacritic-free cursive forms need more vertical room than Latin; 1.5 clips |
| Paragraph measure | 60–75 characters | Persian is denser in visual width than Latin at the same character count |
| Letter spacing | `0` (do not add) | Persian is cursive; positive tracking breaks the visual joining rhythm |
| `word-spacing` | `0` | — |
| Heading scale | 1.25 (h3→h2), 1.5 (h2→h1) | More compressed than the Latin 1.2/1.25 default |

### 3.3 Persian character normalisation

Persian requires `ی` (U+06CC) and `ک` (U+06A9), **not** Arabic `ي` (U+064A) and `ك` (U+0643). Input arriving from Arabic-keyboard systems, legacy databases or pasted documents must be normalised.

| Transformation | From | To | Applied |
| :--- | :--- | :--- | :--- |
| Yeh | `ي` U+064A | `ی` U+06CC | On input and on display normalisation |
| Kaf | `ك` U+0643 | `ک` U+06A9 | On input and on display normalisation |
| Arabic-Indic digits | `٠١٢٣٤٥٦٧٨٩` U+0660–0669 | ASCII `0123456789` | On input, before parsing |
| Persian digits | `۰۱۲۳۴۵۶۷۸۹` U+06F0–06F9 | ASCII `0123456789` | On input, before parsing |
| Tatweel | `ـ` U+0640 | removed | On display normalisation (a frequent artefact of copy/paste) |
| Zero-width non-joiner | `‌` U+200C | preserved | **Never stripped** — it changes word meaning (`می‌شود` vs `میشود`) |
| Arabic-Indic percent/decimal/thousands | `٪` `٫` `٬` | `%` `.` `,` | On input, before parsing |

**Normalisation is for input and display. Machine-layer data is always ASCII** (§4.2).

### 3.4 ZWNJ

U+200C joins a prefix to a suffix: `می‌شود`, `نمی‌کند`, `پیش‌حسابداری`, `حقوق‌بگیر`. A regular space is **never** used for this purpose — it produces a visible gap that reads as a spelling error to a Persian reader.

### 3.5 Persian text in the product

All user-facing strings are authored in Persian directly, not translated from English. The statutory Persian terms must be used rather than English loanwords, because the output may be read by a *Heyat-e Tashkhis* reviewer:

| Use | Not |
| :--- | :--- |
| حقوق | salary |
| مزد مبنا / مزد ثابت | base wage |
| سنوات / حق سنوات پایان خدمت | severance pay |
| عیدی و پاداش پایان سال | annual bonus |
| حق مسکن / بن خواربار / حق اولاد / حق تأهل | welfare allowance |
| فوق‌العاده جذب | attraction allowance |
| بیمه تأمین اجتماعی | social security |
| مالیات بر درآمد حقوق | income tax |
| هزینه کل کارفرما (CTC) | total cost to employer |
| حقوق کارگر / نرخ کارگر | worker rate |
| اضافه‌کاری / شب‌کاری / تعطیل‌کاری | overtime / night shift / holiday work |
| مرخصی / ذخیره مرخصی | leave / leave reserve |

---

## 4. Numerals, Currency and Formatting

### 4.1 The three-layer numeral policy

This is the single most common source of Persian localisation defects. The layers must never be conflated.

| Layer | Form | Rule |
| :--- | :--- | :--- |
| **Display** | Persian digits (U+06F0–U+06F9) | Amounts, dates, percentages, counters, table cells, axis labels |
| **Input** | Accept ASCII, Persian (U+06F0–06F9) and Arabic-Indic (U+0660–0669) | Normalise **all three to ASCII before parsing**. Reject anything else with a Persian validation message |
| **Machine** | Always **ASCII** | JSON payloads, database columns, audit payloads, hashes, CSV exports, URLs, `data-*` attributes, `aria-label` numeric values |

**A Persian-digit string must never be hashed.** The hash must be byte-identical to the value stored in the database. This is the reason the machine layer is ASCII.

```ts
// utils/numerals.ts
const PERSIAN = ['۰','۱','۲','۳','۴','۵','۶','۷','۸','۹'];
export const toPersianDigits = (s: string) =>
  s.replace(/[0-9]/g, (d) => PERSIAN[Number(d)]);

const ARABIC_INDIC = /[٠-٩۰-۹]/g;
export const toAsciiDigits = (s: string) =>
  s.replace(ARABIC_INDIC, (d) => {
    const code = d.charCodeAt(0);
    const base = code >= 0x06f0 ? 0x06f0 : 0x0660;
    return String(code - base);
  });
```

### 4.2 Currency

| Rule | Value |
| :--- | :--- |
| Canonical unit | **Rial (ریال)** — the unit of Labour Law, Social Security and the tax law |
| Display unit | Rial **and** Toman. 1 Toman = 10 Rial |
| Decimal places | **None.** Rial is the smallest unit; a fractional Rial is not a legal amount |
| Display separator | Persian thousands separator `٬` (U+066C) |
| Machine separator | Plain ASCII in JSON; the database stores an integer `BIGINT` |
| Label | The unit is **always** stated: `ریال` or `تومان`. A bare number in a salary interface is a defect |

```ts
export const formatRial = (rial: number, unit: 'rial' | 'toman' = 'rial') =>
  toPersianDigits(
    new Intl.NumberFormat('fa-IR', { maximumFractionDigits: 0 }).format(
      unit === 'toman' ? rial / 10 : rial
    )
  ) + (unit === 'toman' ? ' تومان' : ' ریال');
```

> **Precision note.** `rial / 10` must be computed as `Decimal` in the backend; the display layer may only divide by 10 when the source value is guaranteed divisible by 10. Rial amounts that are not divisible by 10 are legal (tax bracket edges are round, but SSO on an odd base is not) and must not be silently truncated. The backend supplies both Rial and Toman strings, pre-computed.

### 4.3 Percentages and rates

Rates are percentages of a statutory base, not of a free amount. They are displayed with **one decimal place** (e.g. `۷٫۰٪`) using the Persian decimal separator `٫` (U+066B) and the Persian percent sign `٪`. The **machine layer carries rates as strings** with explicit scale (e.g. `"0.07"`) so a JavaScript client cannot coerce them to binary float.

---

## 5. Jalali Calendar

### 5.1 Storage and conversion policy

| Concern | Policy |
| :--- | :--- |
| Storage | **Gregorian UTC** (`TIMESTAMPTZ`) — always. Never a Jalali string in a date column |
| Sorting | Always on the Gregorian column. Never on a Jalali-formatted string |
| Presentation | Convert to Jalali **only at the render boundary** |
| Conversion library | A battle-tested implementation — `persiantools`, `jdatetime`, or the standard *jalaali* algorithm. **Never hand-rolled**: an off-by-one around Nowruz or Esfand is silent and legally damaging |
| Timezone | `Asia/Tehran`, a fixed **UTC+03:30**. Iran abolished daylight saving in October 1401 / 2022, so there is no DST branch |
| Instants | Stored as UTC instants; rendered in Tehran local time |

### 5.2 Calendar structure

| Property | Value |
| :--- | :--- |
| Jalali year 1405 begins | 2026-03-21 (1 Farvardin 1405) |
| Months 1–6 (Farvardin–Shahrivar) | 31 days |
| Months 7–11 (Mehr–Bahman) | 30 days |
| Month 12 (Esfand) | 29 days, **30 in a leap year** |
| Leap rule | The 33-year cycle (`Jalaali` algorithm) |
| Week start | Saturday (شنبه) — Iranian convention, **not** Sunday or Monday |

### 5.3 Canonical display formats

| Context | Format | Example |
| :--- | :--- | :--- |
| Full date | `D MonthName YYYY` | `۲۳ آبان ۱۴۰۵` |
| Short date | `YYYY/MM/DD` | `۱۴۰۵/۰۸/۲۳` |
| Month + year | `MonthName YYYY` | `آبان ۱۴۰۵` |
| Month names | `فروردین، اردیبهشت، خرداد، تیر، مرداد، شهریور، مهر، آبان، آذر، دی، بهمن، اسفند` | — |
| Weekday names | `شنبه، یکشنبه، دوشنبه، سه‌شنبه، چهارشنبه، پنج‌شنبه، جمعه` | — |
| Date + time | `۲۳ آبان ۱۴۰۵، ۱۴:۳۰` | — |

### 5.4 Statutory-year anchoring — a critical rule

A rule that depends on "the 1405 tax year" must be anchored to the **rule set version** (`rule_year_shamsi` + `effective_from`), never to "today". A simulation executed in 2030 must reproduce exactly.

```ts
// WRONG — the result changes with the wall clock
if (new Date().getFullYear() === 1405) { ... }

// RIGHT — the result is anchored to the rule set
const ruleSet = await loadRuleSet(simulation.ruleSetVersionId);
```

The 1405 rule year spans **1405-01-01 … 1405-12-29** in Jalali terms; note that Jalali year 1405 has **365 days** (2026-03-21 → 2027-03-20), so Farvardin 1 of 1406 is 2027-03-21.

### 5.5 Calendar UI

- The Jalali picker must offer **both** a Jalali calendar grid and a Gregorian text input, with the two kept in sync. Iranian enterprise users are equally likely to know a Gregorian ISO date (system logs, contracts, bank documents).
- The Jalali month grid is **Saturday-first**.
- Selecting a date yields a `Date` at Tehran local midnight; it is serialised to the API as an ISO-8601 date string or as a Julian day number — **never** as a Jalali string.
- The picker must handle the 29/30-day Esfand distinction and the leap year correctly.

---

## 6. Persian PDF Generation

A PDF is a **legal exhibit**. It may be shown to a *Heyat-e Tashkhis*. It must render byte-identical values to the API response and carry the rule-set version, the engine version and the calculation hash.

### 6.1 Pipeline selection

| Option | When to use | Notes |
| :--- | :--- | :--- |
| **HTML/CSS → PDF** (WeasyPrint, or headless Chromium) | **Preferred** | RTL layout, Vazirmatn embedding, table pagination and page-break control all come from the same CSS as the application — one stylesheet, one source of truth |
| ReportLab + `arabic_reshaper` + `python-bidi` | Fallback only, when the WeasyPrint/Chromium toolchain is unavailable on the target host | Requires explicit shaping (§6.2) |
| Client-side `window.print()` | Allowed for a quick internal print | Must go through the same stylesheet with `@media print` |

### 6.2 Mandatory text shaping

For any PDF engine that does not implement the Unicode Arabic shaping algorithm, the pipeline **must** be:

```
normalise → arabic_reshaper (presentation forms) → python-bidi (visual reordering) → render
```

Omitting either stage yields **disconnected** (unjoined) and/or **reversed** Persian text. This is the single most common Persian PDF defect and it is invisible to a developer who reads only Latin.

### 6.3 Font embedding

| Requirement | Value |
| :--- | :--- |
| Embedding | **Mandatory** — the PDF must render identically on a machine without Vazirmatn installed |
| Format | `.ttf`/`.otf` for ReportLab; `.woff2`/`.ttf` for WeasyPrint/Chromium |
| Subsetting | Permitted, but the subset must retain all Persian glyphs and the ZWNJ behaviour |
| PDF root attributes | `lang="fa"`, `dir="rtl"`, `text-align: right` |
| Direction | Rely on the PDF viewer, never on the operating system |

### 6.4 Page furniture

| Element | Format |
| :--- | :--- |
| Page numbers | `صفحه ۳ از ۱۲` (Persian digits) |
| Document date | Jalali — `۲۳ آبان ۱۴۰۵` |
| Document reference | `شناسه شبیه‌سازی: SIM-2026-000123` (Latin identifier in an isolated LTR span) |
| Rule set | `نسخه قوانین: ۱۴۰۵.۱ — VERIFIED` |
| Calculation hash | `هش محاسبه: 3f9a…c21` (LTR, isolated) |
| Generation timestamp | Jalali + timezone `Asia/Tehran` |

### 6.5 Print stylesheet

```css
@page { size: A4; margin: 18mm 16mm 20mm; }
thead { display: table-header-group; }        /* repeat headers across pages */
tr, .figure-block { break-inside: avoid; }    /* never orphan a figure from its label */
tfoot { display: table-footer-group; }
table { width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; }
```

**A monetary figure must never be separated from its label.** `break-inside: avoid` on the row is a correctness requirement, not a cosmetic preference, on a document that may be used as evidence.

### 6.6 Determinism

The PDF is a **rendering of a stored snapshot**, never a second computation. It must be reproducible: same snapshot + same engine version + same template version ⇒ byte-identical PDF (modulo the generation timestamp, which is itself a field of the snapshot). The timestamp is rendered from the snapshot, not from the render clock.

---

## 7. Browser Rendering

| Concern | Requirement |
| :--- | :--- |
| Direction in the DOM | `dir` attributes are set on the `<html>` root only. Nested `dir` is used only for genuinely foreign runs |
| Form controls | Numeric inputs: `inputMode="numeric"`, `dir="ltr"`, `text-align: right` — so digits do not visually jump while typing, while the field still behaves correctly inside an RTL form |
| Selects and dropdowns | Radix/Shadcn popovers must render in the correct physical side. Test explicitly; Radix's positioning is direction-aware but third-party wrappers are not |
| Tables | `font-variant-numeric: tabular-nums` and consistent digit alignment. Persian digits in a proportional font produce ragged, error-prone columns |
| Scrollbars | RTL scroll containers scroll in the opposite physical direction — verify explicitly |
| Selection & copy | Copying a Persian selection must yield correct logical order; `dir="rtl"` on the container is what makes this work. Never use `direction: rtl` as a CSS-only hack on a container whose logical content is LTR |
| Print | `@media print` must produce the §6.5 layout with the font embedded or substituted correctly |

---

## 8. Accessibility

| Requirement | Target | Verification |
| :--- | :--- | :--- |
| Keyboard operability | Every interactive element reachable and operable by keyboard | Automated axe scan + manual keyboard pass |
| Focus visibility | Visible focus ring that survives the dark/light theme, ≥ 3:1 contrast against the adjacent colour | Visual review |
| Labels | Every control has a programmatic label; `aria-label` in Persian | Automated |
| Headings | One `h1` per page, no skipped levels | Automated |
| Contrast | WCAG 2.1 AA (4.5:1 text, 3:1 large text and UI) | Automated + manual |
| Motion | `prefers-reduced-motion` honoured | Manual |
| Landmarks | `<header>`, `<nav>`, `<main>`, `<aside>`, `<footer>` present | Automated |
| Screen-reader language | `lang="fa"` set; numbers announced correctly — prefer `aria-label` with a Persian-numeral string where a screen reader would otherwise read a bare digit string | Manual |
| Colour is not the only signal | Status, verification and error states carry an icon and text as well as colour | Manual |
| Persian numerals in `aria-label` | Announced as Persian, not as an unpronounceable digit run | Manual |

---

## 9. Responsive Behaviour

| Breakpoint | Target | Layout |
| :--- | :--- | :--- |
| `< 640 px` | Mobile | Single column; the dual-state input form collapses to the Simple mode; the simulation result panel becomes a stacked summary |
| `640–1024 px` | Tablet | Single column with wider measure; tables become horizontally scrollable with a sticky first column |
| `> 1024 px` | Desktop | Two-column: input form left / result panel right **in logical terms** — the input is `inline-start`, the result is `inline-end`. In an RTL document the input therefore appears on the **right** |

Breakpoints are defined in `rem` against a 16 px root, never in `px`, so the user's browser font-size preference is honoured.

**Mobile is not optional.** Iranian enterprise executives read offers on mobile. The Simple/Advanced mode split (from the historical Persian SRS, `گزارش جامع پژوهشی.docx` §8.2) exists precisely so the mobile path stays short.

---

## 10. Component and Library Decisions

| Concern | Decision | Status |
| :--- | :--- | :--- |
| Framework | React 18/19 + Vite + TypeScript | **[CONFIRMED]** ADR-001 |
| Styling | Tailwind CSS with logical utilities | **[CONFIRMED]** ADR-001 |
| Components | Shadcn/UI (Radix primitives) | **[CONFIRMED]** ADR-001 |
| State / server cache | TanStack Query v5 + Zustand | **[CONFIRMED]** ADR-001 |
| Font | Vazirmatn, self-hosted, OFL | **[PROPOSED]** §3.1 |
| Jalali library | `persiantools` (or `jdatetime`) | **[PROPOSED]** §5.1 |
| Numeral helpers | Local `utils/numerals.ts` | **[PROPOSED]** §4.1 |
| PDF (server) | WeasyPrint preferred; headless Chromium alternative | **[PROPOSED]** §6.1 |
| PDF (client print) | `@media print` stylesheet | **[PROPOSED]** §6.1 |
| Charts | A library that supports RTL axis labels and Persian digit formatting — verify before adoption; a chart that renders its own axis labels in Latin numerals is a defect | **[PROPOSED]** — to be confirmed |

**Note on Shadcn/UI:** Radix primitives are direction-aware, but Shadcn's *examples* are not Persian. Porting a component means checking every margin, every icon direction, and every text alignment — not adding `dir="rtl"` to the root and assuming the result is correct.

---

## 11. Verification Checklist

### 11.1 Automated

| ID | Check |
| :-- | :--- |
| FE-01 | No physical direction utilities in application source (lint gate) |
| FE-02 | Persian digit round-trip: a displayed value converts back to the exact ASCII integer stored in the database |
| FE-03 | Input accepts ASCII, Persian and Arabic-Indic digits and rejects all other digit-like characters |
| FE-04 | Jalali ↔ Gregorian conversion is verified for 1900–2100 against a reference implementation |
| FE-05 | Jalali month lengths correct for every month, including Esfand in leap and non-leap years |
| FE-06 | Every monetary cell renders with a unit label |
| FE-07 | axe scan clean on every route |
| FE-08 | PDF snapshot: page count, page furniture and a monetary row match the expected baseline |
| FE-09 | Snapshot test of the RTL layout at three viewport widths |

### 11.2 Manual

| ID | Check |
| :-- | :--- |
| FE-10 | A Persian paragraph containing a Latin identifier, an email, a URL and a parenthetical renders with correct ordering |
| FE-11 | A PDF opened on a machine with no Persian font installed renders correctly (embedding verified) |
| FE-12 | Copy-paste from the UI preserves Persian logical order |
| FE-13 | Long Persian strings do not overflow their containers |
| FE-14 | The Simple/Advanced form is operable on a 360 px viewport |

---

## 12. Known Risks

| Risk | Impact | Mitigation |
| :--- | :--- | :--- |
| Vazirmatn subset drops ZWNJ-contextual glyph forms | Broken joining in the PDF and in the browser | Subset test that renders a ZWNJ corpus and compares glyph counts |
| The Jalali library treats `Esfand 30` as invalid | Off-by-one at the year boundary | Explicit leap-year tests (FE-05) |
| A charting library renders its own axis labels | Mixed-script chart | Evaluate during `P3-T10` before adoption |
| The PDF pipeline is assembled without a shaping stage | Disconnected Persian in the PDF | Shaping is a mandatory, separately-tested stage (§6.2) |
| Radix popover positioning is not direction-aware in a nested component | Misplaced dropdown | Explicit manual test per component in `P3-T07`–`P3-T09` |
| Persian digits leak into the machine layer | Broken hashes, broken API contracts | FE-02 and the numeric layer unit tests |

---

## 13. Related Tasks

| Task | Phase | Title | Status |
| :--- | :--- | :--- | :--- |
| `P3-T01` | 3 | Frontend scaffold (Vite + React + TS + Tailwind + Shadcn) | NOT_STARTED |
| `P3-T02` | 3 | Persian design system: Vazirmatn, RTL logical properties, numeral policy | NOT_STARTED |
| `P3-T03` | 3 | Jalali calendar library integration and date policy | NOT_STARTED |
| `P3-T04` | 3 | Currency and money formatting layer | NOT_STARTED |
| `P3-T07` | 3 | Net-to-gross simulation form (dual scenario) | NOT_STARTED |
| `P3-T11` | 3 | Persian PDF report generation (shaping + embedding) | NOT_STARTED |
| `P3-T12` | 3 | Frontend component tests and accessibility audit | NOT_STARTED |
| `P3-T13` | 3 | End-to-end tests with the < 3 s budget | NOT_STARTED |
