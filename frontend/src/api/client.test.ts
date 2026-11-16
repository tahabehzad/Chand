import { describe, expect, it, vi } from 'vitest';
import { createApiClient, readApiBaseUrl } from './client';
import { ApiError } from './errors';

type FakeResponseInit = {
  status?: number;
  body?: unknown;
  headers?: Record<string, string>;
  brokenJson?: boolean;
};

function fakeResponse({ status = 200, body, headers = {}, brokenJson = false }: FakeResponseInit) {
  const headerMap: Record<string, string> = {
    'content-type': 'application/json',
    ...Object.fromEntries(Object.entries(headers).map(([key, value]) => [key.toLowerCase(), value])),
  };
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: { get: (name: string) => headerMap[name.toLowerCase()] ?? null },
    json: async () => {
      if (brokenJson) throw new Error('unexpected end of JSON');
      return body;
    },
  } as unknown as Response;
}

type FetchMock = ReturnType<typeof vi.fn<(input: RequestInfo | URL, init?: RequestInit) => Promise<Response>>>;

function client(response: Response, overrides: { onUnauthorized?: () => void } = {}) {
  const fetchMock: FetchMock = vi.fn(async () => response);
  const api = createApiClient({
    // A trailing slash is stripped, so a configured origin is safe to paste.
    baseUrl: 'http://api.test/',
    fetchImpl: fetchMock as unknown as typeof fetch,
    requestIdFactory: () => 'req-fixed-1234',
    onUnauthorized: overrides.onUnauthorized,
  });
  return { fetchMock, api };
}

function requestInit(fetchMock: FetchMock): RequestInit {
  return (fetchMock.mock.calls[0]?.[1] ?? {}) as RequestInit;
}

describe('readApiBaseUrl', () => {
  it('defaults to the same origin when unset', () => {
    expect(readApiBaseUrl({})).toBe('');
  });

  it('honours VITE_API_BASE_URL as a service origin', () => {
    expect(readApiBaseUrl({ VITE_API_BASE_URL: 'http://localhost:8000' })).toBe(
      'http://localhost:8000',
    );
  });
});

describe('createApiClient', () => {
  it('calls the configured base URL with the request path', async () => {
    const { api, fetchMock } = client(fakeResponse({ body: { status: 'alive' } }));
    await api.request({ path: '/health/live' });
    expect(fetchMock.mock.calls[0]?.[0]).toBe('http://api.test/health/live');
    expect(requestInit(fetchMock).method).toBe('GET');
  });

  it('propagates a correlation id on every request and returns the echoed value', async () => {
    const { api, fetchMock } = client(
      fakeResponse({ body: { status: 'alive' }, headers: { 'X-Request-Id': 'server-echoed' } }),
    );
    const result = await api.request<{ status: string }>({ path: '/health/live' });

    const headers = requestInit(fetchMock).headers as Record<string, string>;
    expect(headers['X-Request-Id']).toBe('req-fixed-1234');
    expect(result.correlationId).toBe('server-echoed');
    expect(result.data.status).toBe('alive');
  });

  it('serialises a JSON body and sets the content type', async () => {
    const { api, fetchMock } = client(fakeResponse({ body: { ok: true } }));
    await api.request({ method: 'POST', path: '/simulations/net-to-gross', body: { gross: '1' } });
    const init = requestInit(fetchMock);
    expect(init.method).toBe('POST');
    expect(init.body).toBe('{"gross":"1"}');
    expect((init.headers as Record<string, string>)['Content-Type']).toBe('application/json');
  });

  it('maps a 401 to a session-expiry error and invokes the unauthorized handler', async () => {
    const onUnauthorized = vi.fn();
    const { api } = client(fakeResponse({ status: 401, body: {} }), { onUnauthorized });

    await expect(api.request({ path: '/simulations/net-to-gross' })).rejects.toBeInstanceOf(ApiError);
    expect(onUnauthorized).toHaveBeenCalledTimes(1);

    try {
      await api.request({ path: '/simulations/net-to-gross' });
    } catch (error) {
      const apiError = error as ApiError;
      expect(apiError.kind).toBe('session-expired');
      expect(apiError.code).toBe('SESSION_EXPIRED');
      expect(apiError.isSessionExpiry).toBe(true);
      expect(apiError.messageFa).toContain('نشست');
    }
  });

  it('maps 403, 404, 409, 422, 429 and 5xx to catalogue codes', async () => {
    const cases: Array<[number, string]> = [
      [403, 'FORBIDDEN'],
      [404, 'NOT_FOUND'],
      [409, 'CONFLICT'],
      [422, 'VALIDATION_FAILED'],
      [429, 'RATE_LIMITED'],
      [503, 'SERVER_ERROR'],
    ];
    for (const [status, code] of cases) {
      const { api } = client(fakeResponse({ status, body: {} }));
      await expect(api.request({ path: '/x' })).rejects.toMatchObject({ code });
    }
  });

  it('prefers a machine code supplied by the server', async () => {
    const { api } = client(
      fakeResponse({ status: 422, body: { code: 'STATUTORY_PARAMETER_UNAVAILABLE' } }),
    );
    await expect(api.request({ path: '/x' })).rejects.toMatchObject({
      code: 'STATUTORY_PARAMETER_UNAVAILABLE',
    });
  });

  it('keeps a server warning on the error', async () => {
    const { api } = client(fakeResponse({ status: 409, body: { warning: 'RuleSetNotActive' } }));
    try {
      await api.request({ path: '/x' });
    } catch (error) {
      expect((error as ApiError).warning).toBe('RuleSetNotActive');
    }
  });

  it('maps a transport failure to NETWORK_ERROR and keeps the correlation id', async () => {
    const fetchMock: FetchMock = vi.fn(async () => {
      throw new TypeError('Failed to fetch');
    });
    const api = createApiClient({
      baseUrl: '',
      fetchImpl: fetchMock as unknown as typeof fetch,
      requestIdFactory: () => 'req-network',
    });

    try {
      await api.request({ path: '/health/live' });
      throw new Error('expected a rejection');
    } catch (error) {
      const apiError = error as ApiError;
      expect(apiError.kind).toBe('network');
      expect(apiError.code).toBe('NETWORK_ERROR');
      expect(apiError.correlationId).toBe('req-network');
    }
  });

  it('reports an unparsable success payload as MALFORMED_RESPONSE', async () => {
    const { api } = client(fakeResponse({ body: undefined, brokenJson: true }));
    await expect(api.request({ path: '/health/live' })).rejects.toMatchObject({
      code: 'MALFORMED_RESPONSE',
      kind: 'malformed',
    });
  });

  it('never falls back to fixture data on failure', async () => {
    const { api } = client(fakeResponse({ status: 500, body: {} }));
    await expect(api.request({ path: '/health/live' })).rejects.toBeInstanceOf(ApiError);
  });
});
