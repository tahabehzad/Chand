import { Outlet } from 'react-router-dom';
import { StatutoryBaselineNotice } from '@/components/layout/statutory-baseline-notice';

/**
 * Authentication screens sit outside the application shell: navigation must not
 * be presented before a session exists. No guard is implemented — there is no
 * session contract to guard with.
 */
export function AuthLayout() {
  return (
    <div className="flex min-h-screen flex-col bg-surface-muted">
      <main id="main-content" tabIndex={-1} className="flex-1 px-4 py-6 sm:px-6">
        <div className="mx-auto w-full max-w-xl">
          <Outlet />
        </div>
      </main>
      <footer className="border-t border-border-subtle bg-surface-raised px-4 py-4 sm:px-6">
        <div className="mx-auto w-full max-w-xl">
          <StatutoryBaselineNotice compact />
        </div>
      </footer>
    </div>
  );
}
