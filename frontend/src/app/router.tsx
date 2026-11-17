import { lazy, Suspense, type ReactElement } from 'react';
import { createBrowserRouter, type RouteObject } from 'react-router-dom';
import { AppShell } from './app-shell';
import { AuthLayout } from './auth-layout';
import { RequireManager } from './require-manager';
import { RouteFallback } from './route-fallback';

/*
  Route-level code splitting via React.lazy is an ADR-001 trade-off, not an
  optimisation added later: the initial bundle must stay small in an air-gapped
  deployment.
*/
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
const ManagerLoginPage = lazy(() => import('@/routes/manager-login-page'));
const ProposalPage = lazy(() => import('@/routes/proposal-page'));
const MfaPage = lazy(() => import('@/routes/auth/mfa-page'));
const SessionExpiredPage = lazy(() => import('@/routes/auth/session-expired-page'));
const NotFoundPage = lazy(() => import('@/routes/not-found-page'));
const DevPreviewPage = lazy(() => import('@/routes/dev-preview-page'));
const PrototypeDashboardPage = lazy(() => import('@/routes/prototype/dashboard-page'));
const PrototypePeoplePage = lazy(() => import('@/routes/prototype/people-page'));
const PrototypePersonPage = lazy(() => import('@/routes/prototype/person-page'));
const PrototypeRecommendationPage = lazy(
  () => import('@/routes/prototype/recommendation-page'),
);

function withSuspense(element: ReactElement): ReactElement {
  return <Suspense fallback={<RouteFallback />}>{element}</Suspense>;
}

/** The manager screens render only when a real session token exists. */
function guarded(element: ReactElement): ReactElement {
  return withSuspense(<RequireManager>{element}</RequireManager>);
}

const appChildren: RouteObject[] = [
  { index: true, element: withSuspense(<SimulationPage />) },
  { path: 'transactions', element: withSuspense(<TransactionsPage />) },
  { path: 'settings', element: withSuspense(<SettingsPage />) },
  { path: 'system', element: withSuspense(<SystemPage />) },
  { path: 'prototype', element: guarded(<PrototypeDashboardPage />) },
  { path: 'prototype/people', element: guarded(<PrototypePeoplePage />) },
  { path: 'prototype/people/:personId', element: guarded(<PrototypePersonPage />) },
  {
    path: 'prototype/recommendations/:recommendationId',
    element: guarded(<PrototypeRecommendationPage />),
  },
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
    element: <RequireManager><AppShell /></RequireManager>,
    children: appChildren,
  },
  {
    path: '/proposal',
    element: withSuspense(<ProposalPage />),
  },
  {
    element: <AuthLayout />,
    children: [
      { path: '/login', element: withSuspense(<ManagerLoginPage />) },
      { path: '/login/mfa', element: withSuspense(<MfaPage />) },
      { path: '/session-expired', element: withSuspense(<SessionExpiredPage />) },
    ],
  },
]);
