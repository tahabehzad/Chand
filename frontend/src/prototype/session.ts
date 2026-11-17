/**
 * The manager session: one opaque bearer token plus the identity the API bound
 * to it at sign-in.
 *
 * Authority
 * ---------
 * `docs/specs/AUTH.md` §6 (the tenant is decided server-side, never by the
 * client), `backend/app/api/v1/auth.py` (the login contract).
 *
 * Storage
 * -------
 * `sessionStorage`, not `localStorage`: the token dies with the tab, so a
 * shared machine does not keep a live session. It is still readable by any
 * script on this origin, which is why the backend uses an opaque revocable
 * token rather than a self-contained JWT. A future HttpOnly cookie
 * (`SPEC-AUTH-001` §6) is the production target; this is the MVP boundary.
 */

export type ManagerIdentity = {
  id: string;
  displayName: string;
  email: string;
};

export type OrganizationIdentity = {
  id: string;
  nameFa: string;
};

export type ManagerSession = {
  token: string;
  manager: ManagerIdentity;
  organization: OrganizationIdentity;
};

const SESSION_KEY = 'pish.manager.session.v1';

function storage(): Storage | null {
  try {
    return typeof window === 'undefined' ? null : window.sessionStorage;
  } catch {
    return null;
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

/** Tolerant reader: a damaged or unknown snapshot is treated as no session. */
export function readSession(): ManagerSession | null {
  const store = storage();
  if (store === null) return null;
  const raw = store.getItem(SESSION_KEY);
  if (raw === null) return null;
  let parsed: unknown;
  try {
    parsed = JSON.parse(raw);
  } catch {
    return null;
  }
  if (!isRecord(parsed) || typeof parsed.token !== 'string' || parsed.token.length === 0) {
    return null;
  }
  const manager = parsed.manager;
  const organization = parsed.organization;
  if (!isRecord(manager) || !isRecord(organization)) return null;
  if (typeof manager.displayName !== 'string' || typeof organization.id !== 'string') return null;
  return {
    token: parsed.token,
    manager: {
      id: typeof manager.id === 'string' ? manager.id : '',
      displayName: manager.displayName,
      email: typeof manager.email === 'string' ? manager.email : '',
    },
    organization: {
      id: organization.id,
      nameFa: typeof organization.nameFa === 'string' ? organization.nameFa : '',
    },
  };
}

export function writeSession(session: ManagerSession): void {
  const store = storage();
  if (store === null) return;
  try {
    store.setItem(SESSION_KEY, JSON.stringify(session));
  } catch {
    // A blocked or full store must not break sign-in; the caller still holds
    // the value it just received.
  }
}

export function clearSession(): void {
  const store = storage();
  if (store === null) return;
  try {
    store.removeItem(SESSION_KEY);
  } catch {
    // ignore: clearing is best-effort
  }
}

/** The `Authorization` header for one request, or an empty object. */
export function authHeaders(): Record<string, string> {
  const session = readSession();
  return session === null ? {} : { Authorization: `Bearer ${session.token}` };
}
