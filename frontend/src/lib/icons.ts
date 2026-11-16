/**
 * Icon inventory — SPEC-FE-001 §2.4.
 *
 * Icons that encode direction (arrows, chevrons, "next"/"previous") are
 * mirrored with the Tailwind `rtl:-scale-x-100` utility. The *asset is never
 * swapped*: swapping breaks icon caching, any future RTL-neutral asset
 * pipeline, and the licensing provenance of the set.
 *
 * `directional: false` is a deliberate, recorded decision — not an omission.
 * Every icon in the app must appear in this registry, so an unreviewed icon
 * cannot reach the UI silently.
 */

export type IconName =
  | 'income'
  | 'expense'
  | 'wallet'
  | 'settings'
  | 'calendar'
  | 'overview'
  | 'simulation'
  | 'ctc'
  | 'termination'
  | 'documents'
  | 'benchmarks'
  | 'rule-sets'
  | 'audit'
  | 'menu'
  | 'close'
  | 'chevron-next'
  | 'chevron-previous'
  | 'arrow-back'
  | 'alert'
  | 'info'
  | 'check'
  | 'spinner'
  | 'empty'
  | 'lock'
  | 'external';

type IconDefinition = {
  /** Persian accessible label, used when the icon is not aria-hidden. */
  labelFa: string;
  /** True when the glyph encodes reading/logical direction and must mirror in RTL. */
  directional: boolean;
  /** SVG path data on a 24×24 viewBox, stroke-based. */
  path: string;
};

export const ICON_REGISTRY: Record<IconName, IconDefinition> = {
  income: { labelFa: 'درآمد', directional: false, path: 'M12 3v12M7 10l5 5 5-5M4 16v5h16v-5' },
  expense: { labelFa: 'هزینه', directional: false, path: 'M12 15V3M7 8l5-5 5 5M4 16v5h16v-5' },
  wallet: { labelFa: 'کیف پول', directional: false, path: 'M4 6h15v15H4zM4 6V3h12v3M15 11h6v6h-6zM17 14h1' },
  settings: { labelFa: 'تنظیمات', directional: false, path: 'M4 6h16M4 12h16M4 18h16M8 3v6M16 9v6M10 15v6' },
  calendar: { labelFa: 'تقویم', directional: false, path: 'M4 5h16v16H4zM8 3v4M16 3v4M4 10h16M8 14h2M14 14h2' },
  overview: {
    labelFa: 'نمای کلی',
    directional: false,
    path: 'M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 14h6v6h-6z',
  },
  simulation: {
    labelFa: 'شبیه‌سازی حقوق و دستمزد',
    directional: false,
    path: 'M6 3h12v18H6zM9 7h6M9 11h6M9 15h3',
  },
  ctc: {
    labelFa: 'هزینه کل کارفرما',
    directional: false,
    path: 'M3 9h18v10H3zM7 9V5h10v4M7 14h3',
  },
  termination: {
    labelFa: 'محاسبه تسویه و پایان خدمت',
    directional: false,
    path: 'M4 7h9l6 5-6 5H4zM4 4v16',
  },
  documents: {
    labelFa: 'اسناد و اصالت‌سنجی',
    directional: false,
    path: 'M7 3h7l5 5v13H7zM14 3v5h5M10 13h7M10 17h5',
  },
  benchmarks: {
    labelFa: 'نمودار بازار و حقوق متعارف',
    directional: false,
    path: 'M4 20V10M10 20V4M16 20v-7M22 20H2',
  },
  'rule-sets': {
    labelFa: 'نسخه‌های قوانین',
    directional: false,
    path: 'M5 4h9a3 3 0 0 1 3 3v13H8a3 3 0 0 1-3-3zM17 7h2v13h-2M9 8h5M9 12h5',
  },
  audit: {
    labelFa: 'دفتر حسابرسی',
    directional: false,
    path: 'M12 3l8 3v6c0 4.5-3.2 7.6-8 9-4.8-1.4-8-4.5-8-9V6zM9 12l2 2 4-4',
  },
  menu: { labelFa: 'منو', directional: false, path: 'M4 7h16M4 12h16M4 17h16' },
  close: { labelFa: 'بستن', directional: false, path: 'M6 6l12 12M18 6L6 18' },
  'chevron-next': {
    labelFa: 'بعدی',
    directional: true,
    path: 'M9 5l7 7-7 7',
  },
  'chevron-previous': {
    labelFa: 'قبلی',
    directional: true,
    path: 'M15 5l-7 7 7 7',
  },
  'arrow-back': {
    labelFa: 'بازگشت',
    directional: true,
    path: 'M20 12H5M11 6l-6 6 6 6',
  },
  alert: {
    labelFa: 'هشدار',
    directional: false,
    path: 'M12 3l9 17H3zM12 9v5M12 17h.01',
  },
  info: { labelFa: 'اطلاعات', directional: false, path: 'M12 3a9 9 0 1 1 0 18 9 9 0 0 1 0-18M12 11v6M12 8h.01' },
  check: { labelFa: 'تأیید', directional: false, path: 'M4 13l5 5L20 7' },
  spinner: {
    labelFa: 'در حال بارگذاری',
    directional: false,
    path: 'M12 3a9 9 0 1 0 9 9',
  },
  empty: {
    labelFa: 'خالی',
    directional: false,
    path: 'M3 13h5l1 3h6l1-3h5M3 13l3-8h12l3 8v6H3z',
  },
  lock: {
    labelFa: 'قفل',
    directional: false,
    path: 'M6 10h12v10H6zM9 10V7a3 3 0 0 1 6 0v3',
  },
  external: {
    labelFa: 'پیوند بیرونی',
    directional: false,
    path: 'M14 4h6v6M20 4l-9 9M18 14v6H4V6h6',
  },
};

/** Names whose glyph must be mirrored in an RTL document, derived from the registry. */
export const MIRRORED_ICONS: readonly IconName[] = (
  Object.entries(ICON_REGISTRY) as Array<[IconName, IconDefinition]>
)
  .filter(([, definition]) => definition.directional)
  .map(([name]) => name);

/** The class applied to a directional glyph. The asset itself never changes. */
export const RTL_MIRROR_CLASS = 'rtl:-scale-x-100';
