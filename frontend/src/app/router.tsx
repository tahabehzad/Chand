import { lazy, Suspense, type ReactElement } from 'react';
import { createBrowserRouter, type RouteObject } from 'react-router-dom';
import { AppShell } from './app-shell';
import { AuthLayout } from './auth-layout';
import { RouteFallback } from './route-fallback';

/*
  Route-level code splitting via React.lazy is an ADR-001 trade-off, not an
  optimisation added later: the initial bundle must stay small in an air-gapped
  deployment.
*/
const OverviewPage = lazy(() => import('@/routes/overview-page'));
const TransactionsPage = lazy(() => import('@/routes/transactions-page'));
const SettingsPage = lazy(() => import('@/routes/settings-page'));
const SystemPage = lazy(() => import('@/routes/system-page'));
const SimulationPage = lazy(() =>
  import('@/routes/simulation-page').then((m) => ({ default: m.SimulationPage })),
);
const CtcPage = lazy(() =>
  import('@/routes/modules').then((module) => ({ default: module.CtcPage })),
);
const TerminationPage = lazy(() =>
  import('@/routes/modules').then((module) => ({ default: module.TerminationPage })),
);
const DocumentsPage = lazy(() =>
  import('@/routes/modules').then((module) => ({ default: module.DocumentsPage })),
);
const BenchmarksPage = lazy(() =>
  import('@/routes/modules').then((module) => ({ default: module.BenchmarksPage })),
);
const RuleSetsPage = lazy(() =>
  import('@/routes/modules').then((module) => ({ default: module.RuleSetsPage })),
);
const AuditPage = lazy(() =>
  import('@/routes/modules').then((module) => ({ default: module.AuditPage })),
);
const SignInPage = lazy(() => import('@/routes/auth/sign-in-page'));
const MfaPage = lazy(() => import('@/routes/auth/mfa-page'));
const SessionExpiredPage = lazy(() => import('@/routes/auth/session-expired-page'));
const NotFoundPage = lazy(() => import('@/routes/not-found-page'));
const DevPreviewPage = lazy(() => import('@/routes/dev-preview-page'));

function withSuspense(element: ReactElement): ReactElement {
  return <Suspense fallback={<RouteFallback />}>{element}</Suspense>;
}

const appChildren: RouteObject[] = [
  { index: true, element: withSuspense(<OverviewPage />) },
  { path: 'transactions', element: withSuspense(<TransactionsPage />) },
  { path: 'settings', element: withSuspense(<SettingsPage />) },
  { path: 'system', element: withSuspense(<SystemPage />) },
  { path: 'simulation', element: withSuspense(<SimulationPage />) },
  { path: 'ctc', element: withSuspense(<CtcPage />) },
  { path: 'termination', element: withSuspense(<TerminationPage />) },
  { path: 'documents', element: withSuspense(<DocumentsPage />) },
  { path: 'benchmarks', element: withSuspense(<BenchmarksPage />) },
  { path: 'rule-sets', element: withSuspense(<RuleSetsPage />) },
  { path: 'audit', element: withSuspense(<AuditPage />) },
  { path: '*', element: withSuspense(<NotFoundPage />) },
];

/*
  The synthetic preview route is registered only in a development build.
  The lazy import above can still emit an orphan fixture chunk in production;
  absence of a route does not prove the module is absent from dist/.
*/
if (import.meta.env.DEV) {
  appChildren.splice(appChildren.length - 1, 0, {
    path: 'dev/preview',
    element: withSuspense(<DevPreviewPage />),
  });
}

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppShell />,
    children: appChildren,
  },
  {
    element: <AuthLayout />,
    children: [
      { path: '/login', element: withSuspense(<SignInPage />) },
      { path: '/login/mfa', element: withSuspense(<MfaPage />) },
      { path: '/session-expired', element: withSuspense(<SessionExpiredPage />) },
    ],
  },
]);
