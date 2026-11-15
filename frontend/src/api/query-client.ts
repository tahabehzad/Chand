import { QueryClient } from '@tanstack/react-query';
import { ApiError } from './errors';

/**
 * A 4xx is a decision, not a blip: retrying it multiplies load and hides the
 * failure. Only transport and 5xx failures are retried, twice, with backoff.
 */
function shouldRetry(failureCount: number, error: unknown): boolean {
  if (error instanceof ApiError) {
    if (error.kind === 'contract-unavailable' || error.kind === 'aborted') return false;
    if (error.status !== undefined && error.status >= 400 && error.status < 500) return false;
  }
  return failureCount < 2;
}

export function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        // A monetary or statutory figure is never stale-by-assumption.
        staleTime: 30_000,
        retry: shouldRetry,
        refetchOnWindowFocus: false,
      },
      mutations: { retry: false },
    },
  });
}
