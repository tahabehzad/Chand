import { describe, expect, it } from 'vitest';
import {
  needsRuleSetWarning,
  statutoryYearState,
  RULE_SET_STATUS_LABELS_FA,
  type RuleSetStatus,
} from './provenance';

describe('needsRuleSetWarning — the P3-T05 acceptance criterion', () => {
  it('surfaces a warning for a non-VERIFIED rule set', () => {
    expect(needsRuleSetWarning({ rule_set_status: 'DRAFT', is_verified: false })).toBe(true);
    expect(needsRuleSetWarning({ rule_set_status: 'UNDER_REVIEW', is_verified: false })).toBe(true);
    expect(needsRuleSetWarning({ rule_set_status: 'RETIRED', is_verified: true })).toBe(true);
    expect(needsRuleSetWarning({ rule_set_status: 'REJECTED', is_verified: false })).toBe(true);
  });

  it('stays silent only for a verified, ACTIVE rule set', () => {
    expect(needsRuleSetWarning({ rule_set_status: 'VERIFIED', is_verified: true })).toBe(false);
    expect(needsRuleSetWarning({ rule_set_status: 'ACTIVE', is_verified: true })).toBe(false);
  });

  it('warns when the server contradicts itself', () => {
    expect(needsRuleSetWarning({ rule_set_status: 'VERIFIED', is_verified: false })).toBe(true);
  });
});

describe('statutory year states', () => {
  it('treats 1404 as a verified historical baseline', () => {
    expect(statutoryYearState('1404.1')).toBe('verified-historical');
  });

  it('treats 1405 as transcribed, unverified and inactive', () => {
    expect(statutoryYearState('1405.1')).toBe('unverified-inactive');
  });

  it('labels every status in Persian', () => {
    const statuses: RuleSetStatus[] = [
      'DRAFT',
      'UNDER_REVIEW',
      'VERIFIED',
      'ACTIVE',
      'RETIRED',
      'REJECTED',
    ];
    for (const status of statuses) {
      expect(RULE_SET_STATUS_LABELS_FA[status].length).toBeGreaterThan(0);
    }
  });
});
