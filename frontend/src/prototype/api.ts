/**
 * The prototype data layer — real HTTP against the manager API.
 *
 * Authority
 * ---------
 * `backend/app/api/v1/manager.py` and `backend/app/schemas/manager.py` are the
 * contract; `docs/ARCHITECTURE.md` §6–§8 and `docs/MVP_SCOPE.md`. Every figure
 * this module returns was computed and persisted by the backend. The browser
 * performs no scoring and no statutory arithmetic.
 *
 * Boundary rules
 * --------------
 * * Server integer Rial is converted to a digit **string** here, so a component
 *   never holds money as a JavaScript number (`SPEC-FE-001` §4.2).
 * * A refusal keeps the server's machine code and its Persian detail, so a
 *   screen can say exactly which rule rejected the input.
 * * A 401 clears the stored session and returns the manager to sign-in; no
 *   request silently falls back to fixture data.
 */

import { readApiBaseUrl } from '@/api/client';
import { normaliseNumericInput, parseIntegerInput } from '@/lib/numerals';
import type {
  DashboardSummary,
  Decision,
  DecisionAction,
  EvaluationRules,
  Evidence,
  ImportSummary,
  MetricCode,
  Observation,
  Person,
  Recommendation,
  RecommendationSummary,
  StatutoryCost,
} from './types';
import {
  authHeaders,
  clearSession,
  readSession,
  writeSession,
  type ManagerSession,
} from './session';

const BASE_URL = readApiBaseUrl();

export class PrototypeError extends Error {
  readonly code: string;

  constructor(code: string, messageFa: string) {
    super(messageFa);
    this.name = 'PrototypeError';
    this.code = code;
  }
}

export function isPrototypeError(value: unknown): value is PrototypeError {
  return value instanceof PrototypeError;
}

function fail(code: string, messageFa: string): never {
  throw new PrototypeError(code, messageFa);
}

function correlationId(): string {
  const cryptoApi = globalThis.crypto;
  if (cryptoApi && typeof cryptoApi.randomUUID === 'function') {
    return cryptoApi.randomUUID().replace(/-/g, '');
  }
  return Math.random().toString(16).slice(2).padEnd(32, '0');
}

/** Leave a dead session behind and route to sign-in, outside the test runner. */
function handleUnauthorized(): void {
  clearSession();
  if (typeof window === 'undefined') return;
  if (import.meta.env.MODE === 'test') return;
  if (window.location.pathname.startsWith('/login')) return;
  window.location.assign('/login');
}

type ErrorBody = { error?: { code?: unknown; detail?: unknown } };

function readError(payload: unknown, status: number): PrototypeError {
  const body = (typeof payload === 'object' && payload !== null ? payload : {}) as ErrorBody;
  const code =
    typeof body.error?.code === 'string' ? body.error.code : `HTTP_${String(status)}`;
  const detail =
    typeof body.error?.detail === 'string'
      ? body.error.detail
      : 'درخواست از سوی سرور پذیرفته نشد؛ مقادیر را بررسی کنید.';
  return new PrototypeError(code, detail);
}

type RequestOptions = {
  method?: 'GET' | 'POST' | 'PATCH' | 'PUT';
  body?: unknown;
  form?: FormData;
  auth?: boolean;
  query?: Record<string, string | undefined>;
};

export async function managerRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const search =
    options.query === undefined
      ? ''
      : '?' +
        new URLSearchParams(
          Object.entries(options.query).filter(
            (entry): entry is [string, string] => entry[1] !== undefined,
          ),
        ).toString();

  const headers: Record<string, string> = {
    Accept: 'application/json',
    'X-Request-Id': correlationId(),
  };
  if (options.auth !== false) Object.assign(headers, authHeaders());
  let body: BodyInit | undefined;
  if (options.form !== undefined) {
    body = options.form;
  } else if (options.body !== undefined) {
    headers['Content-Type'] = 'application/json';
    body = JSON.stringify(options.body);
  }

  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}${search}`, {
      method: options.method ?? 'GET',
      credentials: 'same-origin',
      headers,
      body,
    });
  } catch {
    fail('NETWORK_ERROR', 'ارتباط با سرور برقرار نشد. اتصال سرویس را بررسی کنید.');
  }

  const contentType = response.headers.get('Content-Type') ?? '';
  let payload: unknown = undefined;
  if (contentType.includes('application/json')) {
    try {
      payload = await response.json();
    } catch {
      payload = undefined;
    }
  }

  if (!response.ok) {
    if (response.status === 401) {
      handleUnauthorized();
      const parsed = readError(payload, response.status);
      fail('AUTH_SESSION_INVALID', parsed.message);
    }
    throw readError(payload, response.status);
  }
  return payload as T;
}

/** Send a user-entered integer in the machine layer's ASCII digit form. */
function machineInteger(raw: string): string {
  const cleaned = normaliseNumericInput(raw).replace(/[\s,]/g, '');
  const parsed = parseIntegerInput(cleaned);
  return parsed.ok && !parsed.negative ? parsed.value : cleaned;
}

function money(value: unknown): string {
  if (typeof value === 'number' && Number.isInteger(value)) return String(value);
  if (typeof value === 'string' && /^-?\d+$/.test(value)) return value;
  return '0';
}

function optionalMoney(value: unknown): string | null {
  return value === null || value === undefined ? null : money(value);
}

// ------------------------------------------------------------ server rows ---

type ServerDecision = {
  id: string;
  recommendationId: string;
  action: string;
  editedGrossRial: number | null;
  comment: string;
  decidedAt: string;
};

type ServerRecommendation = {
  id: string;
  personId: string;
  personName: string;
  period: string;
  ruleSetVersion: string;
  ruleSetStatus: string;
  score100: number;
  totalBp: number;
  contributions: Recommendation['contributions'];
  missingCriteria: MetricCode[];
  observationsUsed: Recommendation['observationsUsed'];
  band: {
    minRial: number;
    maxRial: number;
    currentRial: number | null;
    positionBp: number;
  };
  suggestedGrossRial: number;
  deltaRial: number | null;
  statutory: StatutoryCost;
  currentStatutory: StatutoryCost | null;
  explanation: Recommendation['explanation'];
  engineVersion: string;
  calculationHash: string;
  advisory: true;
  status: 'pending' | 'decided';
  decision: ServerDecision | null;
  createdAt: string;
};

type ServerSummary = {
  id: string;
  personId: string;
  personName: string;
  period: string;
  score100: number;
  suggestedGrossRial: number;
  deltaRial: number | null;
  status: 'pending' | 'decided';
  decisionAction: DecisionAction | null;
  createdAt: string;
};

type ServerObservation = {
  id: string;
  personId: string;
  code: MetricCode;
  period: string;
  raw: string;
  state: Observation['state'];
  source: Observation['source'];
  createdAt: string;
};

type ServerDashboard = {
  peopleCount: number;
  validObservationCount: number;
  pendingCount: number;
  decidedCount: number;
  recentDecisions: Array<ServerDecision & { personName: string; score100: number }>;
};

function normalizeDecision(row: ServerDecision): Decision {
  return {
    id: row.id,
    recommendationId: row.recommendationId,
    action: row.action as DecisionAction,
    editedGrossRial: optionalMoney(row.editedGrossRial),
    comment: row.comment,
    decidedAt: row.decidedAt,
  };
}

function normalizeRecommendation(row: ServerRecommendation): Recommendation {
  return {
    ...row,
    band: {
      minRial: money(row.band.minRial),
      maxRial: money(row.band.maxRial),
      currentRial: optionalMoney(row.band.currentRial),
      positionBp: row.band.positionBp,
    },
    suggestedGrossRial: money(row.suggestedGrossRial),
    deltaRial: optionalMoney(row.deltaRial),
    decision: row.decision === null ? null : normalizeDecision(row.decision),
  };
}

function normalizeSummary(row: ServerSummary): RecommendationSummary {
  return {
    ...row,
    suggestedGrossRial: money(row.suggestedGrossRial),
    deltaRial: optionalMoney(row.deltaRial),
  };
}

// ------------------------------------------------------------------- auth ---

export async function login(email: string, password: string): Promise<ManagerSession> {
  const payload = await request<{
    token: string;
    manager: ManagerSession['manager'];
    organization: ManagerSession['organization'];
  }>('/api/v1/auth/login', {
    method: 'POST',
    auth: false,
    body: { email: email.trim(), password },
  });
  const session: ManagerSession = {
    token: payload.token,
    manager: payload.manager,
    organization: payload.organization,
  };
  writeSession(session);
  return session;
}

export async function logout(): Promise<void> {
  try {
    if (readSession() !== null) {
      await request<{ status: string }>('/api/v1/auth/logout', { method: 'POST' });
    }
  } catch {
    // A refused logout must still clear the local session; the token expires
    // server-side on its own.
  } finally {
    clearSession();
  }
}

export { readSession };

// ----------------------------------------------------------------- people ---

const request = managerRequest;

export async function listPeople(): Promise<Person[]> {
  return request<Person[]>('/api/v1/manager/employees');
}

export async function getPerson(personId: string): Promise<Person | null> {
  try {
    return await request<Person>(`/api/v1/manager/employees/${personId}`);
  } catch (caught) {
    if (isPrototypeError(caught) && caught.code === 'EMPLOYEE_NOT_FOUND') return null;
    throw caught;
  }
}

export type PersonDraft = { name: string; role: string; startDate: string };

export async function createPerson(draft: PersonDraft): Promise<Person> {
  return request<Person>('/api/v1/manager/employees', {
    method: 'POST',
    body: {
      name: draft.name.trim(),
      role: draft.role.trim(),
      startDate: draft.startDate.trim(),
    },
  });
}

export async function updatePerson(personId: string, draft: PersonDraft): Promise<Person> {
  return request<Person>(`/api/v1/manager/employees/${personId}`, {
    method: 'PATCH',
    body: {
      name: draft.name.trim(),
      role: draft.role.trim(),
      startDate: draft.startDate.trim(),
    },
  });
}

// ----------------------------------------------------------- observations ---

export async function listObservations(personId: string): Promise<Observation[]> {
  return request<Observation[]>(`/api/v1/manager/employees/${personId}/observations`);
}

export type ObservationDraft = {
  personId: string;
  code: MetricCode;
  period: string;
  raw: string;
};

export async function addObservation(draft: ObservationDraft): Promise<Observation> {
  return request<ServerObservation>(
    `/api/v1/manager/employees/${draft.personId}/observations`,
    {
      method: 'POST',
      body: {
        code: draft.code,
        period: draft.period.trim(),
        raw: machineInteger(draft.raw),
      },
    },
  );
}

export async function correctObservation(
  observationId: string,
  raw: string,
): Promise<Observation> {
  return request<Observation>(`/api/v1/manager/observations/${observationId}`, {
    method: 'PATCH',
    body: { raw: machineInteger(raw) },
  });
}

export async function rejectObservation(observationId: string): Promise<Observation> {
  return request<Observation>(`/api/v1/manager/observations/${observationId}/reject`, {
    method: 'POST',
  });
}

export async function importObservations(
  personId: string,
  file: File,
): Promise<ImportSummary> {
  const form = new FormData();
  form.append('file', file, file.name);
  return request<ImportSummary>(
    `/api/v1/manager/employees/${personId}/observations/import`,
    { method: 'POST', form },
  );
}

// --------------------------------------------------------------- evidence ---

export async function listEvidence(personId: string): Promise<Evidence[]> {
  return request<Evidence[]>(`/api/v1/manager/employees/${personId}/evidence`);
}

export async function uploadEvidence(
  personId: string,
  file: File,
  note: string,
): Promise<Evidence> {
  const form = new FormData();
  form.append('file', file, file.name);
  if (note.trim().length > 0) form.append('note', note.trim());
  return request<Evidence>(`/api/v1/manager/employees/${personId}/evidence`, {
    method: 'POST',
    form,
  });
}

// ------------------------------------------------------------------ rules ---

export async function getRules(): Promise<EvaluationRules> {
  return request<EvaluationRules>('/api/v1/manager/rules');
}

// ------------------------------------------------------------- evaluation ---

export type BandDraft = {
  bandMinRial: string;
  bandMaxRial: string;
  currentRial?: string;
};

export async function evaluatePerson(
  personId: string,
  draft: BandDraft,
): Promise<Recommendation> {
  const current = draft.currentRial?.trim() ?? '';
  const row = await request<ServerRecommendation>(
    `/api/v1/manager/employees/${personId}/evaluations`,
    {
      method: 'POST',
      body: {
        bandMinRial: machineInteger(draft.bandMinRial),
        bandMaxRial: machineInteger(draft.bandMaxRial),
        currentRial: current === '' ? null : machineInteger(current),
      },
    },
  );
  return normalizeRecommendation(row);
}

// ---------------------------------------------------- recommendations/queue --

export async function getRecommendation(
  recommendationId: string,
): Promise<Recommendation | null> {
  try {
    const row = await request<ServerRecommendation>(
      `/api/v1/manager/recommendations/${recommendationId}`,
    );
    return normalizeRecommendation(row);
  } catch (caught) {
    if (isPrototypeError(caught) && caught.code === 'RECOMMENDATION_NOT_FOUND') return null;
    throw caught;
  }
}

export async function listRecommendations(personId: string): Promise<RecommendationSummary[]> {
  const rows = await request<ServerSummary[]>(
    `/api/v1/manager/employees/${personId}/recommendations`,
  );
  return rows.map(normalizeSummary);
}

export async function listPendingRecommendations(): Promise<RecommendationSummary[]> {
  const rows = await request<ServerSummary[]>('/api/v1/manager/recommendations', {
    query: { status: 'pending' },
  });
  return rows.map(normalizeSummary);
}

export type DecisionDraft = {
  action: DecisionAction;
  editedGrossRial?: string;
  comment?: string;
};

export async function decideRecommendation(
  recommendationId: string,
  draft: DecisionDraft,
): Promise<Decision> {
  const edited = draft.editedGrossRial?.trim() ?? '';
  const row = await request<ServerDecision>(
    `/api/v1/manager/recommendations/${recommendationId}/decision`,
    {
      method: 'POST',
      body: {
        action: draft.action,
        comment: (draft.comment ?? '').trim(),
        editedGrossRial:
          draft.action === 'edit' && edited !== '' ? machineInteger(edited) : null,
      },
    },
  );
  return normalizeDecision(row);
}

// -------------------------------------------------------------- dashboard ---

export async function getDashboard(): Promise<DashboardSummary> {
  const row = await request<ServerDashboard>('/api/v1/manager/dashboard');
  return {
    ...row,
    recentDecisions: row.recentDecisions.map((decision) => ({
      ...normalizeDecision(decision),
      personName: decision.personName,
      score100: decision.score100,
    })),
  };
}

export { PrototypeError as ApiErrorForManager };
