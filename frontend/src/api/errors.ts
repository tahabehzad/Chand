/**
 * Frontend error model and catalogue mapping — WBS P3-T05.
 *
 * **Provisional.** The backend error catalogue is `backend/app/api/errors.py`
 * (`EXECUTION_PLAN` §7.1) and does not exist yet: `P0-T18`/`P1-T19` are not
 * delivered. The mapping below is therefore keyed on HTTP status and on the
 * conventional machine codes named by the specification
 * (Holy Bible M1/M8 error cases). When the real catalogue lands, this table is
 * replaced by it — it is not a second source of truth, and no endpoint is
 * invented to exercise it.
 */

export type ApiFailureKind =
  | 'network'
  | 'http'
  | 'malformed'
  | 'aborted'
  | 'session-expired'
  | 'contract-unavailable';

export type ErrorCode =
  | 'SESSION_EXPIRED'
  | 'MFA_REQUIRED'
  | 'FORBIDDEN'
  | 'NOT_FOUND'
  | 'CONFLICT'
  | 'VALIDATION_FAILED'
  | 'RATE_LIMITED'
  | 'STATUTORY_PARAMETER_UNAVAILABLE'
  | 'RULE_SET_NOT_VERIFIED'
  | 'SERVER_ERROR'
  | 'NETWORK_ERROR'
  | 'MALFORMED_RESPONSE'
  | 'CONTRACT_UNAVAILABLE'
  | 'UNKNOWN';

type CatalogueEntry = {
  messageFa: string;
  /** A 401 that means "go to sign-in" rather than "credentials rejected". */
  sessionExpiry: boolean;
};

const CATALOGUE: Record<ErrorCode, CatalogueEntry> = {
  SESSION_EXPIRED: { messageFa: 'نشست شما منقضی شده است. لطفاً دوباره وارد شوید.', sessionExpiry: true },
  MFA_REQUIRED: { messageFa: 'برای ادامه، تأیید دو‌مرحله‌ای لازم است.', sessionExpiry: false },
  FORBIDDEN: { messageFa: 'دسترسی شما به این بخش مجاز نیست.', sessionExpiry: false },
  NOT_FOUND: { messageFa: 'مورد درخواستی یافت نشد.', sessionExpiry: false },
  CONFLICT: { messageFa: 'این درخواست با وضعیت فعلی سامانه تعارض دارد.', sessionExpiry: false },
  VALIDATION_FAILED: { messageFa: 'اطلاعات ارسالی معتبر نیست. مقادیر را بررسی کنید.', sessionExpiry: false },
  RATE_LIMITED: { messageFa: 'تعداد درخواست‌ها بیش از حد مجاز است. کمی بعد تلاش کنید.', sessionExpiry: false },
  STATUTORY_PARAMETER_UNAVAILABLE: {
    messageFa: 'یک مقدار قانونی لازم در دسترس یا تأیید‌شده نیست؛ محاسبه متوقف شد.',
    sessionExpiry: false,
  },
  RULE_SET_NOT_VERIFIED: {
    messageFa: 'نسخه قوانین مورد استفاده در وضعیت تأیید‌شده نیست.',
    sessionExpiry: false,
  },
  SERVER_ERROR: { messageFa: 'خطای داخلی سامانه رخ داد. لطفاً بعداً تلاش کنید.', sessionExpiry: false },
  NETWORK_ERROR: {
    messageFa: 'ارتباط با سرور برقرار نشد. اتصال شبکه را بررسی کنید.',
    sessionExpiry: false,
  },
  MALFORMED_RESPONSE: {
    messageFa: 'پاسخ سرور قابل تفسیر نبود؛ قرارداد API با این نسخه از رابط هم‌خوان نیست.',
    sessionExpiry: false,
  },
  CONTRACT_UNAVAILABLE: {
    messageFa: 'قرارداد این بخش هنوز از سوی بک‌اند تحویل نشده است.',
    sessionExpiry: false,
  },
  UNKNOWN: { messageFa: 'خطای ناشناخته‌ای رخ داد.', sessionExpiry: false },
};

export function catalogueMessage(code: ErrorCode): string {
  return CATALOGUE[code].messageFa;
}

export function isSessionExpiryCode(code: ErrorCode): boolean {
  return CATALOGUE[code].sessionExpiry;
}

/** Map an HTTP status (plus an optional machine code from the body) to the catalogue. */
export function codeForStatus(status: number, machineCode?: string): ErrorCode {
  if (machineCode && machineCode in CATALOGUE) {
    return machineCode as ErrorCode;
  }
  if (status === 401) return 'SESSION_EXPIRED';
  if (status === 403) return 'FORBIDDEN';
  if (status === 404) return 'NOT_FOUND';
  if (status === 409) return 'CONFLICT';
  if (status === 422) return 'VALIDATION_FAILED';
  if (status === 429) return 'RATE_LIMITED';
  if (status >= 500) return 'SERVER_ERROR';
  return 'UNKNOWN';
}

export type ApiErrorInit = {
  kind: ApiFailureKind;
  code: ErrorCode;
  status?: number;
  correlationId?: string;
  /** Server-supplied machine warning, e.g. a `RuleSetNotActive` marker. */
  warning?: string;
  cause?: unknown;
};

/** A single error type for every failure crossing the API boundary. */
export class ApiError extends Error {
  readonly kind: ApiFailureKind;
  readonly code: ErrorCode;
  readonly status?: number;
  readonly correlationId?: string;
  readonly warning?: string;
  /** Persian message safe to render directly. */
  readonly messageFa: string;

  constructor(init: ApiErrorInit) {
    super(init.code, { cause: init.cause });
    this.name = 'ApiError';
    this.kind = init.kind;
    this.code = init.code;
    this.status = init.status;
    this.correlationId = init.correlationId;
    this.warning = init.warning;
    this.messageFa = catalogueMessage(init.code);
  }

  get isSessionExpiry(): boolean {
    return this.kind === 'session-expired' || isSessionExpiryCode(this.code);
  }
}

/**
 * Thrown *before any network call* for a route whose backend contract does not
 * exist yet. It exists so a placeholder screen can never be mistaken for a
 * working integration, and so a failed real call is never replaced with
 * fixture data.
 */
export class ContractUnavailableError extends ApiError {
  readonly contractId: string;

  constructor(contractId: string, requiredBy: string) {
    super({ kind: 'contract-unavailable', code: 'CONTRACT_UNAVAILABLE' });
    this.name = 'ContractUnavailableError';
    this.contractId = contractId;
    this.message = `${contractId} is not delivered (required by ${requiredBy})`;
  }
}

export function isApiError(value: unknown): value is ApiError {
  return value instanceof ApiError;
}
