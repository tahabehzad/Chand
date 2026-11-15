/**
 * The typed API boundary — WBS P3-T05.
 *
 * ADR-001 requires strict REST/JSON contract separation with the FastAPI
 * backend. Every call goes through this module; components never call `fetch`.
 *
 * Delivered API surface at the time of writing: `GET /health/live` only
 * (`backend/app/main.py`). No other endpoint is assumed to exist.
 *
 * Correlation id: the backend accepts and echoes `X-Request-Id`
 * (`docs/specs/DEPLOYMENT.md` §7.2, implemented in `backend/app/main.py`), so
 * the client generates one per request and keeps the echoed value on the error
 * for support.
 */

import { ApiError, codeForStatus, isApiError } from './errors';

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

export type ApiResponse<T> = {
  data: T;
  correlationId: string;
};

export type RequestOptions = {
  method?: HttpMethod;
  /** Path relative to the configured API base URL, e.g. `/health/live`. */
  path: string;
  body?: unknown;
  signal?: AbortSignal;
  /** Extra headers. Never used for credentials in this phase. */
  headers?: Record<string, string>;
};

export type ApiClient = {
  readonly baseUrl: string;
  request<T>(options: RequestOptions): Promise<ApiResponse<T>>;
};

export type ApiClientOptions = {
  baseUrl: string;
  fetchImpl?: typeof fetch;
  /** Injected so tests are deterministic. */
  requestIdFactory?: () => string;
  /** Invoked on a 401 so the app layer can route to the sign-in screen. */
  onUnauthorized?: (error: ApiError) => void;
};

/**
 * The service origin, not a route prefix. Defaults to the same origin, because
 * the reverse proxy that would co-host the SPA and the API is not part of this
 * delivery; `VITE_API_BASE_URL` is set per deployment (e.g. `http://localhost:8000`).
 * Each contract carries its own full path.
 */
const DEFAULT_BASE_URL = '';

function defaultRequestId(): string {
  const cryptoApi = globalThis.crypto;
  if (cryptoApi && typeof cryptoApi.randomUUID === 'function') {
    return cryptoApi.randomUUID().replace(/-/g, '');
  }
  return Math.random().toString(16).slice(2).padEnd(32, '0');
}

function readMachineCode(payload: unknown): string | undefined {
  if (typeof payload !== 'object' || payload === null) return undefined;
  const record = payload as Record<string, unknown>;
  const candidate = record.code ?? record.error_code ?? record.error;
  return typeof candidate === 'string' ? candidate : undefined;
}

function readWarning(payload: unknown): string | undefined {
  if (typeof payload !== 'object' || payload === null) return undefined;
  const warning = (payload as Record<string, unknown>).warning;
  return typeof warning === 'string' ? warning : undefined;
}

export function readApiBaseUrl(env: Record<string, string | undefined> = import.meta.env): string {
  const configured = env.VITE_API_BASE_URL?.trim();
  return configured && configured.length > 0 ? configured : DEFAULT_BASE_URL;
}

export function createApiClient(options: ApiClientOptions): ApiClient {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  const requestIdFactory = options.requestIdFactory ?? defaultRequestId;
  const baseUrl = options.baseUrl.replace(/\/$/, '');

  return {
    baseUrl,
    async request<T>(requestOptions: RequestOptions): Promise<ApiResponse<T>> {
      const method = requestOptions.method ?? 'GET';
      const correlationId = requestIdFactory();

      let response: Response;
      try {
        response = await fetchImpl(`${baseUrl}${requestOptions.path}`, {
          method,
          // Cookies are only meaningful once the session contract exists; the
          // browser default is left untouched so no credential is invented here.
          credentials: 'same-origin',
          headers: {
            Accept: 'application/json',
            'X-Request-Id': correlationId,
            ...(requestOptions.body === undefined
              ? {}
              : { 'Content-Type': 'application/json' }),
            ...requestOptions.headers,
          },
          body: requestOptions.body === undefined ? undefined : JSON.stringify(requestOptions.body),
          signal: requestOptions.signal,
        });
      } catch (cause) {
        if (cause instanceof DOMException && cause.name === 'AbortError') {
          throw new ApiError({ kind: 'aborted', code: 'UNKNOWN', correlationId, cause });
        }
        throw new ApiError({ kind: 'network', code: 'NETWORK_ERROR', correlationId, cause });
      }

      const echoedId = response.headers.get('X-Request-Id') ?? correlationId;

      let payload: unknown = undefined;
      const contentType = response.headers.get('Content-Type') ?? '';
      if (contentType.includes('application/json')) {
        try {
          payload = await response.json();
        } catch (cause) {
          if (response.ok) {
            throw new ApiError({
              kind: 'malformed',
              code: 'MALFORMED_RESPONSE',
              status: response.status,
              correlationId: echoedId,
              cause,
            });
          }
          payload = undefined;
        }
      }

      if (!response.ok) {
        const code = codeForStatus(response.status, readMachineCode(payload));
        const error = new ApiError({
          kind: response.status === 401 ? 'session-expired' : 'http',
          code,
          status: response.status,
          correlationId: echoedId,
          warning: readWarning(payload),
        });
        if (error.isSessionExpiry) {
          options.onUnauthorized?.(error);
        }
        throw error;
      }

      return { data: payload as T, correlationId: echoedId };
    },
  };
}

export { isApiError };
export type { ApiError };
