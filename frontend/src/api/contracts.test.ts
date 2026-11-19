import { describe, expect, it } from 'vitest';
import { CONTRACTS, isDelivered, requireDelivered, type ContractDefinition } from './contracts';
import { ContractUnavailableError, isApiError } from './errors';

const entries = Object.values(CONTRACTS) as ContractDefinition[];

describe('the contract registry', () => {
  it('marks delivered contracts', () => {
    const delivered = entries.filter(isDelivered).map((entry) => entry.id);
    expect(delivered).toEqual([
      'health.live',
      'simulations.gross-to-net',
      'estimations.create',
      'simulations.salary-ctc-breakdown',
      'simulations.document-analysis',
      'regulatory.status',
    ]);
  });

  it('names an owning WBS task for every contract', () => {
    for (const entry of entries) {
      expect(entry.ownerTask).toMatch(/^P\d-T\d+$/);
    }
  });

  it('uses a unique id for every contract', () => {
    const ids = entries.map((entry) => entry.id);
    expect(new Set(ids).size).toBe(ids.length);
  });

  it('states that the P3-T01 dependency is not delivered', () => {
    expect(CONTRACTS.netToGross.availability).toBe('awaiting-backend');
    expect(CONTRACTS.netToGross.ownerTask).toBe('P1-T19');
  });

  it('accepts a delivered contract', () => {
    expect(() => requireDelivered(CONTRACTS.healthLive)).not.toThrow();
  });

  it('refuses an undelivered contract before any request is made', () => {
    expect(() => requireDelivered(CONTRACTS.netToGross)).toThrow(ContractUnavailableError);
    try {
      requireDelivered(CONTRACTS.documentUpload);
    } catch (error) {
      expect(isApiError(error)).toBe(true);
      if (isApiError(error)) {
        expect(error.kind).toBe('contract-unavailable');
        expect(error.message).toContain('P2-T02');
      }
    }
  });
});
