import type { IconName } from '@/lib/icons';
import { CONTRACTS, type ContractDefinition } from '@/api/contracts';

/**
 * Navigation for the approved product modules (`EXECUTION_PLAN` §6, WBS
 * `P3-T07`…`P3-T10`). Every entry names the contract it needs, so the shell can
 * show which modules are waiting on the backend rather than implying a working
 * feature.
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

/** Local-only MVP demo navigation; approved product modules remain separate. */
export const MVP_NAV_ITEMS: readonly NavItem[] = [
  { id: 'dashboard', path: '/', labelFa: 'داشبورد', descriptionFa: '', icon: 'overview' },
  { id: 'transactions', path: '/transactions', labelFa: 'تراکنش‌ها', descriptionFa: '', icon: 'wallet' },
  { id: 'settings', path: '/settings', labelFa: 'تنظیمات', descriptionFa: '', icon: 'settings' },
];

export const NAV_ITEMS: readonly NavItem[] = [
  {
    id: 'overview',
    path: '/',
    labelFa: 'نمای کلی',
    descriptionFa: 'وضعیت سامانه و آمادگی بخش‌ها',
    icon: 'overview',
  },
  {
    id: 'simulation',
    path: '/simulation',
    labelFa: 'شبیه‌سازی حقوق',
    descriptionFa: 'محاسبه خالص و ناخالص با دو سناریو',
    icon: 'simulation',
    contract: CONTRACTS.netToGross,
    ownerTask: 'P3-T07',
  },
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
