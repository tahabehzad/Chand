import type { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { readSession } from '@/prototype/session';

/**
 * Client-side gate in front of the manager screens.
 *
 * It is a *navigation* guard, not a security control: authorization and tenant
 * isolation are enforced by the API on every request. The guard only avoids
 * rendering an empty shell when no token exists and remembers the requested
 * path so sign-in can return to it.
 */
export function RequireManager({ children }: { children: ReactNode }) {
  const location = useLocation();
  if (readSession() === null) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }
  return <>{children}</>;
}
