import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import {
  createPerson,
  decideRecommendation,
  getDashboard,
  getPerson,
  getRecommendation,
  importObservations,
  isPrototypeError,
  listPeople,
  login,
} from './api';
import { clearSession, readSession } from './session';

type Call = { url: string; init: RequestInit };

function jsonResponse(body: unknown, status = 200): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: {
      get: (name: string) => (name.toLowerCase() === 'content-type' ? 'application/json' : null),
    },
    json: async () => body,
  } as unknown as Response;
}

function mockFetch(handler: (call: Call) => Response): Call[] {
  const calls: Call[] = [];
  vi.stubGlobal(
    'fetch',
    vi.fn(async (input: string | URL | Request, init?: RequestInit) => {
      const call = { url: String(input), init: init ?? {} };
      calls.push(call);
      return handler(call);
    }),
  );
  return calls;
}

function bodyOf(call: Call): Record<string, unknown> {
  return JSON.parse(String(call.init.body)) as Record<string, unknown>;
}

function headersOf(call: Call): Record<string, string> {
  return (call.init.headers ?? {}) as Record<string, string>;
}

beforeEach(() => {
  clearSession();
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('session and transport', () => {
  it('signs in, stores the opaque token and attaches it to later calls', async () => {
    const calls = mockFetch(() =>
      jsonResponse({
        token: 'token-1',
        tokenType: 'Bearer',
        manager: { id: 'u1', displayName: 'مدیر', email: 'm@local.dev' },
        organization: { id: 'o1', nameFa: 'سازمان نمونه' },
      }),
    );

    const session = await login(' M@LOCAL.DEV ', 'secret');
    expect(session.manager.displayName).toBe('مدیر');
    expect(readSession()?.token).toBe('token-1');
    expect(calls[0]?.url).toContain('/api/v1/auth/login');
    expect(bodyOf(calls[0]!)).toEqual({ email: 'M@LOCAL.DEV', password: 'secret' });
    expect(headersOf(calls[0]!).Authorization).toBeUndefined();

    mockFetch(() => jsonResponse([]));
    await listPeople();
    const second = (globalThis.fetch as unknown as ReturnType<typeof vi.fn>).mock.calls[0];
    expect((second?.[1] as RequestInit).headers).toMatchObject({
      Authorization: 'Bearer token-1',
    });
  });

  it('keeps the server machine code and Persian detail on a refusal', async () => {
    mockFetch(() =>
      jsonResponse(
        { error: { code: 'EMPLOYEE_NAME_INVALID', detail: 'نام کارمند الزامی است.' } },
        422,
      ),
    );
    await expect(
      createPerson({ name: '', role: 'فروش', startDate: '2024-03-20' }),
    ).rejects.toSatisfy(
      (caught: unknown) =>
        isPrototypeError(caught) &&
        caught.code === 'EMPLOYEE_NAME_INVALID' &&
        caught.message === 'نام کارمند الزامی است.',
    );
  });

  it('returns null for a missing employee and keeps other errors fatal', async () => {
    mockFetch(() => jsonResponse({ error: { code: 'EMPLOYEE_NOT_FOUND' } }, 404));
    expect(await getPerson('missing')).toBeNull();

    mockFetch(() => jsonResponse({ error: { code: 'SERVER_ERROR' } }, 500));
    await expect(getPerson('missing')).rejects.toSatisfy(
      (caught: unknown) => isPrototypeError(caught) && caught.code === 'SERVER_ERROR',
    );
  });

  it('clears a dead session on 401', async () => {
    await loginWithToken();
    mockFetch(() => jsonResponse({ error: { code: 'AUTH_SESSION_INVALID' } }, 401));
    await expect(listPeople()).rejects.toSatisfy(
      (caught: unknown) => isPrototypeError(caught) && caught.code === 'AUTH_SESSION_INVALID',
    );
    expect(readSession()).toBeNull();
  });
});

async function loginWithToken(): Promise<void> {
  mockFetch(() =>
    jsonResponse({
      token: 'token-2',
      manager: { id: 'u1', displayName: 'مدیر', email: 'm@local.dev' },
      organization: { id: 'o1', nameFa: 'سازمان' },
    }),
  );
  await login('m@local.dev', 'secret');
}

describe('money at the boundary', () => {
  const serverRecommendation = {
    id: 'r1',
    personId: 'p1',
    personName: 'کارمند',
    period: '1404-Q2',
    ruleSetVersion: 'perf-v1',
    ruleSetStatus: 'PROVISIONAL_DRAFT',
    score100: 83,
    totalBp: 8343,
    contributions: [],
    missingCriteria: [],
    observationsUsed: [],
    band: { minRial: 80_000_000, maxRial: 140_000_000, currentRial: 100_000_000, positionBp: 8343 },
    suggestedGrossRial: 130_058_000,
    deltaRial: 30_058_000,
    statutory: { net_rial: 1 },
    currentStatutory: null,
    explanation: { reasons: [], warnings: [], dataQuality: [], advisory: true, statutoryStatus: 'x' },
    engineVersion: '0.3.0-payroll-engine',
    calculationHash: 'a'.repeat(64),
    advisory: true,
    status: 'pending',
    decision: null,
    createdAt: '2026-11-17T00:00:00Z',
  };

  it('turns server integers into digit strings and keeps the decision null', async () => {
    await loginWithToken();
    mockFetch(() => jsonResponse(serverRecommendation));
    const recommendation = await getRecommendation('r1');
    expect(recommendation?.suggestedGrossRial).toBe('130058000');
    expect(recommendation?.deltaRial).toBe('30058000');
    expect(recommendation?.band.currentRial).toBe('100000000');
    expect(recommendation?.decision).toBeNull();
    expect(recommendation?.advisory).toBe(true);
  });

  it('sends a decision amount as a digit string and normalises the answer', async () => {
    await loginWithToken();
    const calls = mockFetch(() =>
      jsonResponse({
        id: 'd1',
        recommendationId: 'r1',
        action: 'edit',
        editedGrossRial: 120_000_000,
        comment: 'بازبینی',
        decidedAt: '2026-11-17T01:00:00Z',
      }),
    );
    const decision = await decideRecommendation('r1', {
      action: 'edit',
      comment: 'بازبینی',
      editedGrossRial: '۱۲۰,۰۰۰,۰۰۰',
    });
    expect(decision.editedGrossRial).toBe('120000000');
    expect(bodyOf(calls[0]!)).toEqual({
      action: 'edit',
      comment: 'بازبینی',
      editedGrossRial: '120000000',
    });
  });
});

describe('dashboard and file upload', () => {
  it('normalises the recent decision amounts', async () => {
    await loginWithToken();
    mockFetch(() =>
      jsonResponse({
        peopleCount: 1,
        validObservationCount: 2,
        pendingCount: 1,
        decidedCount: 1,
        recentDecisions: [
          {
            id: 'd1',
            recommendationId: 'r1',
            action: 'approve',
            editedGrossRial: null,
            comment: 'تأیید',
            decidedAt: '2026-11-17T01:00:00Z',
            personName: 'کارمند',
            score100: 83,
          },
        ],
      }),
    );
    const dashboard = await getDashboard();
    expect(dashboard.recentDecisions[0]?.action).toBe('approve');
    expect(dashboard.recentDecisions[0]?.editedGrossRial).toBeNull();
  });

  it('uploads a CSV as multipart without a JSON content type', async () => {
    await loginWithToken();
    const calls = mockFetch(() => jsonResponse({ imported: 2, rejected: [] }));
    const file = new File(['metric_code,period,raw_value\n'], 'observations.csv', {
      type: 'text/csv',
    });
    const summary = await importObservations('p1', file);
    expect(summary.imported).toBe(2);
    expect(calls[0]?.url).toContain('/employees/p1/observations/import');
    expect(calls[0]?.init.body).toBeInstanceOf(FormData);
    expect(headersOf(calls[0]!).Authorization).toBe('Bearer token-2');
    expect(headersOf(calls[0]!)['Content-Type']).toBeUndefined();
  });
});
