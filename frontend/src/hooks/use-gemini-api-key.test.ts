import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { act, renderHook } from '@testing-library/react';
import {
  GEMINI_API_KEY_STORAGE_KEY,
  isValidGeminiKey,
  sanitizeGeminiKey,
  useGeminiApiKey,
} from './use-gemini-api-key';

describe('useGeminiApiKey', () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  afterEach(() => {
    window.localStorage.clear();
  });

  it('returns null and isConfigured=false when storage is empty', () => {
    const { result } = renderHook(() => useGeminiApiKey());
    expect(result.current.apiKey).toBeNull();
    expect(result.current.isConfigured).toBe(false);
  });

  it('reads pre-existing key from localStorage', () => {
    window.localStorage.setItem(GEMINI_API_KEY_STORAGE_KEY, 'AIzaSyExistingKey');
    const { result } = renderHook(() => useGeminiApiKey());
    expect(result.current.apiKey).toBe('AIzaSyExistingKey');
    expect(result.current.isConfigured).toBe(true);
  });

  it('saves new key and updates localStorage', () => {
    const { result } = renderHook(() => useGeminiApiKey());

    act(() => {
      result.current.setApiKey('  AIzaSyNewKey123  ');
    });

    expect(result.current.apiKey).toBe('AIzaSyNewKey123');
    expect(result.current.isConfigured).toBe(true);
    expect(window.localStorage.getItem(GEMINI_API_KEY_STORAGE_KEY)).toBe('AIzaSyNewKey123');
  });

  it('removes key when set to null or empty string', () => {
    window.localStorage.setItem(GEMINI_API_KEY_STORAGE_KEY, 'AIzaSyExistingKey');
    const { result } = renderHook(() => useGeminiApiKey());

    act(() => {
      result.current.setApiKey(null);
    });

    expect(result.current.apiKey).toBeNull();
    expect(result.current.isConfigured).toBe(false);
    expect(window.localStorage.getItem(GEMINI_API_KEY_STORAGE_KEY)).toBeNull();

    act(() => {
      result.current.setApiKey('   ');
    });

    expect(result.current.apiKey).toBeNull();
    expect(result.current.isConfigured).toBe(false);
  });
});

describe('isValidGeminiKey and sanitizeGeminiKey', () => {
  it('validates traditional AIza format keys', () => {
    expect(isValidGeminiKey('AIzaSyA1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7')).toBe(true);
    // Too short (less than 35 chars after AIza)
    expect(isValidGeminiKey('AIzaShort')).toBe(false);
  });

  it('validates new AQ format auth keys', () => {
    expect(isValidGeminiKey('AQ.Ab12345678cdefgh')).toBe(true);
    expect(isValidGeminiKey('AQ.AbCdEf12345678_.-Key')).toBe(true);
    // Too short (less than 10 chars after AQ.)
    expect(isValidGeminiKey('AQ.short')).toBe(false);
    // Missing dot
    expect(isValidGeminiKey('AQAb12345678cdefgh')).toBe(false);
  });

  it('sanitizes quotes and zero-width characters', () => {
    const raw = '\u200D"AQ.Ab12345678cdefgh"\u200E';
    expect(sanitizeGeminiKey(raw)).toBe('AQ.Ab12345678cdefgh');
    expect(isValidGeminiKey(raw)).toBe(true);

    const rawAIza = "'AIzaSyA1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7'";
    expect(sanitizeGeminiKey(rawAIza)).toBe('AIzaSyA1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7');
    expect(isValidGeminiKey(rawAIza)).toBe(true);
  });

  it('rejects invalid prefixes or empty inputs', () => {
    expect(isValidGeminiKey(null)).toBe(false);
    expect(isValidGeminiKey(undefined)).toBe(false);
    expect(isValidGeminiKey('')).toBe(false);
    expect(isValidGeminiKey('   ')).toBe(false);
    expect(isValidGeminiKey('sk-1234567890abcdefghijklmnop')).toBe(false);
  });
});
