import type { IconName } from '@/lib/icons';
import { CONTRACTS, type ContractDefinition } from '@/api/contracts';

/**
 * Navigation for the delivered product and the deferred sections.
 *
 * ADR-008 fixed the product boundary on the statutory payroll calculation
 * engine, so the navigation follows the same truth: the working screens are
 * the primary navigation, and the sections whose backend contract does not
 * exist yet stay in a clearly labelled, collapsed group where each item
 * names the contract it waits for.
 *
 * Every entry names the contract it needs, so the shell can show which
 * modules are waiting on the backend rather than implying a working feature.
 *
 * Route-level permission guards (`SPEC-AUTH-001` §3) are **not** implemented:
 * the session contract does not exist, and a client-side guard that "passes"
 * against an invented session would imply a security control that is not there.
 * Authorization is enforced server-side; this navigation is presentational.
 */
export type NavItem = {
  id: string;
  path: string;
  labelFa: string;
  descriptionFa: string;
  icon: IconName;
  /** The contract the module's data depends on. */
  contract?: ContractDefinition;
  ownerTask?: string;
};

/**
 * The statutory simulation — the delivered ADR-008 screen. It calls the
 * gross-to-net contract, which exists; the net-to-gross inverter is out of
 * product scope, so it is not named here.
 */
export const SIMULATION_NAV_ITEM: NavItem = {
  id: 'simulation',
  path: '/simulation',
  labelFa: 'شبیه‌سازی حقوق',
  descriptionFa: 'محاسبه ناخالص به خالص با دو حالت ماده ۱۳۷',
  icon: 'simulation',
  contract: CONTRACTS.grossToNet,
  ownerTask: 'P1-T19',
};

/**
 * The primary navigation: the screens that work today.
 *
 * The dashboard, the transactions table and the settings are the local
 * synthetic demo; the simulation is the statutory screen backed by the
 * verified 1404 rule set; the system page reports the delivered contracts
 * and the service status.
 */
export const PRIMARY_NAV_ITEMS: readonly NavItem[] = [
  { id: 'dashboard', path: '/', labelFa: 'صفحه اصلی', descriptionFa: 'محاسبه حقوق', icon: 'simulation' },
  {
    // The previous "بازار حقوق" entry served a fabricated table bundled in the
    // SPA. It was replaced by this screen, which asks the backend and refuses
    // when the market data is insufficient (ADR-014 §1.4).
    id: 'salary-estimation',
    path: '/salary-estimation',
    labelFa: 'برآورد حقوق بازار',
    descriptionFa: 'تخمین حقوق پایه بر پایهٔ داده‌های معتبر بازار',
    icon: 'benchmarks',
    contract: CONTRACTS.salaryEstimation,
    ownerTask: 'P4-T02',
  },
  {
    id: 'prototype',
    path: '/prototype',
    labelFa: 'ارزیابی نمونه',
    descriptionFa: 'امتیاز و پیشنهاد مشورتی (دادهٔ ساختگی)',
    icon: 'overview',
  },
  SIMULATION_NAV_ITEM,
  { id: 'transactions', path: '/transactions', labelFa: 'تراکنش‌ها', descriptionFa: '', icon: 'wallet' },
  { id: 'settings', path: '/settings', labelFa: 'تنظیمات', descriptionFa: '', icon: 'settings' },
  { id: 'system', path: '/system', labelFa: 'وضعیت سامانه', descriptionFa: '', icon: 'rule-sets' },
];

/**
 * The sections whose backend contract does not exist yet. They are grouped
 * and collapsed so that a deferred module can never be mistaken for a
 * working one.
 */
export const NAV_ITEMS: readonly NavItem[] = [
  {
    id: 'ctc',
    path: '/ctc',
    labelFa: 'هزینه کل کارفرما',
    descriptionFa: 'تفکیک هزینه کارفرما و پیش‌بینی تعهدات',
    icon: 'ctc',
    contract: CONTRACTS.preHireCtc,
    ownerTask: 'P3-T08',
  },
  {
    id: 'termination',
    path: '/termination',
    labelFa: 'تسویه و پایان خدمت',
    descriptionFa: 'سنوات، مرخصی ذخیره‌شده و ماده ۱۱',
    icon: 'termination',
    contract: CONTRACTS.terminationLiability,
    ownerTask: 'P3-T08',
  },
  {
    id: 'documents',
    path: '/documents',
    labelFa: 'اسناد و اصالت‌سنجی',
    descriptionFa: 'بارگذاری، وضعیت بررسی و نشانه‌های ناهنجاری',
    icon: 'documents',
    contract: CONTRACTS.documentUpload,
    ownerTask: 'P3-T09',
  },
  {
    id: 'benchmarks',
    path: '/benchmarks',
    labelFa: 'بازار و حقوق متعارف',
    descriptionFa: 'بازه P10–P90 و نسبت به میانه',
    icon: 'benchmarks',
    contract: CONTRACTS.benchmarkBand,
    ownerTask: 'P3-T10',
  },
  {
    id: 'rule-sets',
    path: '/rule-sets',
    labelFa: 'نسخه‌های قوانین',
    descriptionFa: 'نسخه، سال قانونی و وضعیت تأیید',
    icon: 'rule-sets',
    contract: CONTRACTS.statutoryRuleSets,
    ownerTask: 'P1-T19',
  },
  {
    id: 'audit',
    path: '/audit',
    labelFa: 'دفتر حسابرسی',
    descriptionFa: 'رویدادهای ثبت‌شده و زنجیره هش',
    icon: 'audit',
    contract: CONTRACTS.auditLog,
    ownerTask: 'P2-T10',
  },
];
