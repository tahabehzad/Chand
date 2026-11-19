/**
 * The API contract registry — WBS P3-T05.
 *
 * This file is deliberately a *truthful inventory*, not a wish list. An entry
 * marked `delivered` exists in `backend/` today; an entry marked
 * `awaiting-backend` is named by the specification but has **no implementation**,
 * so calling it would invent a working endpoint. Screens that need an
 * undelivered entry render a stated blocker instead of pretending to work.
 *
 * Authority: `docs/EXECUTION_PLAN.md` §7 (API design) and the WBS rows that own
 * each endpoint. `P1-T19` (simulation API) is the P3-T01 dependency and is
 * `NOT_STARTED`.
 */

import { ContractUnavailableError } from './errors';
import type { HttpMethod } from './client';

export type ContractAvailability = 'delivered' | 'awaiting-backend';

export type ContractDefinition = {
  id: string;
  method: HttpMethod;
  path: string;
  /** Persian purpose, for the "unavailable" explanation shown to a user. */
  purposeFa: string;
  availability: ContractAvailability;
  /** The WBS task that delivers this endpoint. */
  ownerTask: string;
};

function contract(definition: ContractDefinition): ContractDefinition {
  return definition;
}

export const CONTRACTS = {
  healthLive: contract({
    id: 'health.live',
    method: 'GET',
    path: '/health/live',
    purposeFa: 'بررسی زنده‌بودن سرویس',
    availability: 'delivered',
    ownerTask: 'P0-T02',
  }),

  sessionSignIn: contract({
    id: 'auth.session.create',
    method: 'POST',
    path: '/auth/login',
    purposeFa: 'ورود با شناسه و گذرواژه',
    availability: 'awaiting-backend',
    ownerTask: 'P0-T18',
  }),
  sessionMfaChallenge: contract({
    id: 'auth.mfa.verify',
    method: 'POST',
    path: '/auth/mfa/verify',
    purposeFa: 'تأیید دو‌مرحله‌ای',
    availability: 'awaiting-backend',
    ownerTask: 'P0-T18',
  }),
  sessionSignOut: contract({
    id: 'auth.session.delete',
    method: 'DELETE',
    path: '/auth/session',
    purposeFa: 'پایان دادن به نشست',
    availability: 'awaiting-backend',
    ownerTask: 'P0-T18',
  }),

  netToGross: contract({
    id: 'simulations.net-to-gross',
    method: 'POST',
    path: '/simulations/net-to-gross',
    purposeFa: 'شبیه‌سازی حقوق از خالص به ناخالص',
    availability: 'awaiting-backend',
    ownerTask: 'P1-T19',
  }),
  grossToNet: contract({
    id: 'simulations.gross-to-net',
    method: 'POST',
    path: '/api/v1/simulations/gross-to-net',
    purposeFa: 'شبیه‌سازی حقوق از ناخالص به خالص',
    availability: 'delivered',
    ownerTask: 'P1-T19',
  }),
  preHireCtc: contract({
    id: 'simulations.pre-hire-ctc',
    method: 'POST',
    path: '/simulations/pre-hire-ctc',
    purposeFa: 'هزینه کل کارفرما پیش از استخدام',
    availability: 'awaiting-backend',
    ownerTask: 'P1-T19',
  }),
  terminationLiability: contract({
    id: 'simulations.termination-liability',
    method: 'POST',
    path: '/simulations/termination-liability',
    purposeFa: 'تسویه و تعهد پایان خدمت',
    availability: 'awaiting-backend',
    ownerTask: 'P1-T19',
  }),

  documentUpload: contract({
    id: 'documents.upload',
    method: 'POST',
    path: '/documents/upload',
    purposeFa: 'بارگذاری سند برای اصالت‌سنجی',
    availability: 'awaiting-backend',
    ownerTask: 'P2-T02',
  }),
  documentStatus: contract({
    id: 'documents.status',
    method: 'GET',
    path: '/documents/{documentId}',
    purposeFa: 'وضعیت بازبینی سند',
    availability: 'awaiting-backend',
    ownerTask: 'P2-T10',
  }),
  salaryEstimation: contract({
    id: 'estimations.create',
    method: 'POST',
    path: '/api/v1/simulations/salary-estimation',
    purposeFa: 'برآورد حقوق بر اساس بازار کار ایران',
    availability: 'delivered',
    ownerTask: 'P4-T02',
  }),
  salaryCtcBreakdown: contract({
    id: 'simulations.salary-ctc-breakdown',
    method: 'POST',
    path: '/api/v1/simulations/salary-ctc-breakdown',
    purposeFa: 'تفکیک هزینه کل کارفرما (CTC) و خالص حقوق',
    availability: 'delivered',
    ownerTask: 'P4-T03',
  }),
  documentAnalysis: contract({
    id: 'simulations.document-analysis',
    method: 'POST',
    path: '/api/v1/simulations/document-analysis',
    purposeFa: 'تحلیل اصالت مدارک شغلی و محاسبه اثر بر حقوق',
    availability: 'delivered',
    ownerTask: 'P4-T05',
  }),

  benchmarkBand: contract({
    id: 'benchmarks.band',
    method: 'GET',
    path: '/benchmarks',
    purposeFa: 'بازه حقوق متعارف بازار',
    availability: 'awaiting-backend',
    ownerTask: 'P1-T18',
  }),
  statutoryRuleSets: contract({
    id: 'statutory.rule-sets',
    method: 'GET',
    path: '/statutory/rule-sets',
    purposeFa: 'فهرست نسخه‌های قوانین',
    availability: 'awaiting-backend',
    ownerTask: 'P1-T19',
  }),
  auditLog: contract({
    id: 'audit.log',
    method: 'GET',
    path: '/audit-logs',
    purposeFa: 'مشاهده دفتر حسابرسی',
    availability: 'awaiting-backend',
    ownerTask: 'P2-T10',
  }),
  regulatoryStatus: contract({
    id: 'regulatory.status',
    method: 'GET',
    path: '/api/v1/regulatory/status',
    purposeFa: 'وضعیت و نسخه قوانین جاری و همگام‌سازی مراجع رسمی',
    availability: 'delivered',
    ownerTask: 'P4-T04',
  }),
} as const satisfies Record<string, ContractDefinition>;

export type ContractKey = keyof typeof CONTRACTS;

export function isDelivered(definition: ContractDefinition): boolean {
  return definition.availability === 'delivered';
}

/**
 * Fail loudly, before any request, for a contract that does not exist.
 * This is what keeps an unavailable screen honest.
 */
export function requireDelivered(definition: ContractDefinition): void {
  if (!isDelivered(definition)) {
    throw new ContractUnavailableError(definition.id, definition.ownerTask);
  }
}
