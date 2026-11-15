/**
 * Provenance model shared by every emitted figure — AGENTS.md invariant 9,
 * Holy Bible §6.6, `EXECUTION_PLAN` §7.2 r4.
 *
 * The three facts are separate fields and must never be concatenated into a
 * single label. `"1405.1-VERIFIED"` is the exact defect this separation exists
 * to prevent: it asserts a verification that did not occur.
 *
 * 1404 is the verified *historical* statutory baseline. 1405 is transcribed,
 * unverified and inactive — the UI must never present either as newly verified
 * current law.
 */

export type RuleSetStatus =
  | 'DRAFT'
  | 'UNDER_REVIEW'
  | 'VERIFIED'
  | 'ACTIVE'
  | 'RETIRED'
  | 'REJECTED';

export type FieldProvenance = {
  rule_id: string;
  rule_year: number;
  formula_ref: string;
};

export type FigureProvenance = {
  /** e.g. `1404.1` — the rule-set version actually used. */
  rule_version: string;
  rule_set_status: RuleSetStatus;
  is_verified: boolean;
  engine_version: string;
  calculation_hash: string;
  /** ISO-8601 UTC instant rendered from the snapshot, never re-derived. */
  generated_at: string;
  provenance?: Record<string, FieldProvenance>;
};

/** The statutory years the product may discuss, with their verified state. */
export type StatutoryYearState = 'verified-historical' | 'unverified-inactive';

export const STATUTORY_YEAR_STATE: Record<string, StatutoryYearState> = {
  '1404': 'verified-historical',
  '1405': 'unverified-inactive',
};

export function statutoryYearState(version: string): StatutoryYearState | undefined {
  return STATUTORY_YEAR_STATE[version.split('.')[0] ?? ''];
}

/**
 * A response is only "clean" when its rule set is verified *and* the server
 * says so. Anything else surfaces the warning banner (`P3-T05` AC).
 */
export function needsRuleSetWarning(provenance: Pick<FigureProvenance, 'rule_set_status' | 'is_verified'>): boolean {
  const statusOk = provenance.rule_set_status === 'VERIFIED' || provenance.rule_set_status === 'ACTIVE';
  return !statusOk || !provenance.is_verified;
}

export const RULE_SET_STATUS_LABELS_FA: Record<RuleSetStatus, string> = {
  DRAFT: 'پیش‌نویس',
  UNDER_REVIEW: 'در حال بازبینی',
  VERIFIED: 'تأییدشده',
  ACTIVE: 'فعال',
  RETIRED: 'بازنشسته',
  REJECTED: 'ردشده',
};

export const STATUTORY_YEAR_LABELS_FA: Record<StatutoryYearState, string> = {
  'verified-historical': 'مبنای تاریخی تأییدشده',
  'unverified-inactive': 'رونویسی‌شده، تأییدنشده و غیرفعال',
};
