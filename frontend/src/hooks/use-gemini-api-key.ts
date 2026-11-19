/**
 * Gemini API Key management hook and validation helpers.
 *
 * Stores the Google Gemini API key in `localStorage` under `pish_gemini_api_key`
 * for live web-grounded market salary searches.
 *
 * Supports both traditional AIza standard keys and new AQ format keys.
 */

import { useCallback, useEffect, useState } from 'react';

export const GEMINI_API_KEY_STORAGE_KEY = 'pish_gemini_api_key';

/**
 * Sanitizes a Gemini API key:
 * Trims leading/trailing whitespace, strips zero-width joiners/spaces,
 * directional formatting markers, and surrounding/internal quotes.
 */
export function sanitizeGeminiKey(k: string | null | undefined): string {
  if (!k) return '';
  return k
    .replace(/[\u200B-\u200D\uFEFF\u200E\u200F\u202A-\u202E]/g, '')
    .replace(/["'«»“”‘’`]/g, '')
    .trim();
}

/**
 * Validates Google Gemini API key format:
 * - AIza standard key: 'AIza' followed by 35+ base64/url-safe chars (total >= 39 chars)
 * - AQ auth key: 'AQ.' followed by 10+ characters (A-Za-z0-9_.-)
 */
export function isValidGeminiKey(k: string | null | undefined): boolean {
  if (!k) return false;
  const cleaned = sanitizeGeminiKey(k);
  return /^(AIza[0-9A-Za-z_-]{35,}|AQ\.[A-Za-z0-9_.-]{10,})$/.test(cleaned);
}

function readStoredKey(): string | null {
  if (typeof window === 'undefined') return null;
  try {
    const raw = window.localStorage.getItem(GEMINI_API_KEY_STORAGE_KEY);
    if (!raw) return null;
    const sanitized = sanitizeGeminiKey(raw);
    return sanitized.length > 0 ? sanitized : null;
  } catch {
    return null;
  }
}

export function useGeminiApiKey(): {
  apiKey: string | null;
  setApiKey: (key: string | null) => void;
  isConfigured: boolean;
} {
  const [apiKey, setApiKeyState] = useState<string | null>(readStoredKey);

  const setApiKey = useCallback((key: string | null) => {
    const cleaned = key ? sanitizeGeminiKey(key) : null;
    try {
      if (cleaned && cleaned.length > 0) {
        window.localStorage.setItem(GEMINI_API_KEY_STORAGE_KEY, cleaned);
      } else {
        window.localStorage.removeItem(GEMINI_API_KEY_STORAGE_KEY);
      }
    } catch {
      // Ignore storage errors in restricted contexts
    }
    setApiKeyState(cleaned && cleaned.length > 0 ? cleaned : null);
  }, []);

  useEffect(() => {
    const handleStorageChange = (event: StorageEvent) => {
      if (event.key === GEMINI_API_KEY_STORAGE_KEY) {
        const val = event.newValue ? sanitizeGeminiKey(event.newValue) : null;
        setApiKeyState(val && val.length > 0 ? val : null);
      }
    };
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  return {
    apiKey,
    setApiKey,
    isConfigured: Boolean(apiKey && apiKey.length > 0),
  };
}
