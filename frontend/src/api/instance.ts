import { createApiClient, readApiBaseUrl, type ApiClient } from './client';
import type { ApiError } from './errors';

/**
 * The app-wide client. The base URL comes from `VITE_API_BASE_URL` and defaults
 * to the same origin; each delivered contract carries its own full path.
 */
let unauthorizedHandler: ((error: ApiError) => void) | null = null;

/** Registered once by the router so a 401 can route to the sign-in screen. */
export function setUnauthorizedHandler(handler: ((error: ApiError) => void) | null): void {
  unauthorizedHandler = handler;
}

export const apiClient: ApiClient = createApiClient({
  baseUrl: readApiBaseUrl(),
  onUnauthorized: (error) => unauthorizedHandler?.(error),
});
