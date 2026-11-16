import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { setUnauthorizedHandler } from '@/api/instance';
import { useUiStore } from '@/state/ui-store';

/**
 * Connects the API layer's 401 signal to the router. This is a *reaction* to a
 * real server decision, not a client-side session model: the expiry policy lives
 * in `SPEC-AUTH-001` §5.2 and is not implemented in the browser.
 */
export function SessionBridge() {
  const navigate = useNavigate();
  const markSessionExpired = useUiStore((state) => state.markSessionExpired);

  useEffect(() => {
    setUnauthorizedHandler(() => {
      markSessionExpired();
      navigate('/session-expired', { replace: true });
    });
    return () => setUnauthorizedHandler(null);
  }, [markSessionExpired, navigate]);

  return null;
}
